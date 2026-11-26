"""Windows OpenCL 1.2 calls used by the optional held-icon filter."""
import ctypes as ct
from contextlib import ExitStack

Handle = ct.c_void_p
UInt = ct.c_uint
Int = ct.c_int
Size = ct.c_size_t
Flags = ct.c_ulonglong
Pointer = ct.POINTER

class OpenCLUnavailable(RuntimeError):
    """The requested device, program or kernel could not be initialized."""

def _check(status, operation, error=RuntimeError):
    if status:
        raise error(f'{operation} (OpenCL {status})')

class IconDevice:
    def __init__(self, source):
        try:
            self.lib = ct.WinDLL('OpenCL.dll', winmode=0x800)
        except OSError as exc:
            raise OpenCLUnavailable(str(exc)) from exc
        self._declare_calls()
        with ExitStack() as owned:
            device = self._intel_gpu()
            status = Int()
            def own(handle, release, operation):
                _check(status.value, operation, OpenCLUnavailable)
                owned.callback(release, handle)
                return handle

            lib = self.lib
            self.context = own(lib.clCreateContext(None, 1, ct.byref(device), None, None, ct.byref(status)),
                               lib.clReleaseContext, 'clCreateContext')
            self.queue = own(lib.clCreateCommandQueue(self.context, device, 0, ct.byref(status)),
                             lib.clReleaseCommandQueue, 'clCreateCommandQueue')
            code = ct.c_char_p(source.encode('ascii'))
            program = own(lib.clCreateProgramWithSource(self.context, 1, ct.byref(code), None, ct.byref(status)),
                          lib.clReleaseProgram, 'clCreateProgramWithSource')
            result = lib.clBuildProgram(program, 1, ct.byref(device), b'', None, None)
            if result:
                length = Size()
                lib.clGetProgramBuildInfo(program, device, 0x1183, 0, None, ct.byref(length))
                detail = ct.create_string_buffer(max(1, length.value))
                lib.clGetProgramBuildInfo(program, device, 0x1183, len(detail), detail, None)
                raise OpenCLUnavailable(f'clBuildProgram (OpenCL {result}): {detail.value.decode(errors="replace")}')
            self.kernel = own(lib.clCreateKernel(program, b'screen', ct.byref(status)),
                              lib.clReleaseKernel, 'clCreateKernel')
            self._owned = owned.pop_all()

    def _declare_calls(self):
        specs = {
            'clGetPlatformIDs': (Int, UInt, Pointer(Handle), Pointer(UInt)),
            'clGetDeviceIDs': (Int, Handle, Flags, UInt, Pointer(Handle), Pointer(UInt)),
            'clGetDeviceInfo': (Int, Handle, UInt, Size, Handle, Pointer(Size)),
            'clCreateContext': (Handle, Handle, UInt, Pointer(Handle), Handle, Handle, Pointer(Int)),
            'clCreateCommandQueue': (Handle, Handle, Handle, Flags, Pointer(Int)),
            'clCreateProgramWithSource': (Handle, Handle, UInt, Pointer(ct.c_char_p), Pointer(Size), Pointer(Int)),
            'clBuildProgram': (Int, Handle, UInt, Pointer(Handle), ct.c_char_p, Handle, Handle),
            'clGetProgramBuildInfo': (Int, Handle, Handle, UInt, Size, Handle, Pointer(Size)),
            'clCreateKernel': (Handle, Handle, ct.c_char_p, Pointer(Int)),
            'clCreateBuffer': (Handle, Handle, Flags, Size, Handle, Pointer(Int)),
            'clSetKernelArg': (Int, Handle, UInt, Size, Handle),
            'clEnqueueNDRangeKernel': (Int, Handle, Handle, UInt, Handle, Pointer(Size), Pointer(Size), UInt, Pointer(Handle), Pointer(Handle)),
            'clEnqueueReadBuffer': (Int, Handle, Handle, UInt, Size, Size, Handle, UInt, Pointer(Handle), Pointer(Handle)),
        }
        for name in ('Context', 'CommandQueue', 'Program', 'Kernel', 'MemObject'):
            specs['clRelease' + name] = (Int, Handle)
        for name, (result, *arguments) in specs.items():
            try:
                fn = getattr(self.lib, name)
            except AttributeError as exc:
                raise OpenCLUnavailable(f"OpenCL.dll 缺少 {name}") from exc
            fn.restype, fn.argtypes = result, arguments

    def _intel_gpu(self):
        count = UInt()
        _check(self.lib.clGetPlatformIDs(0, None, ct.byref(count)), 'clGetPlatformIDs', OpenCLUnavailable)
        platforms = (Handle * count.value)()
        if count.value:
            _check(self.lib.clGetPlatformIDs(count, platforms, None), 'clGetPlatformIDs', OpenCLUnavailable)
        for platform in platforms:
            devices_count = UInt()
            status = self.lib.clGetDeviceIDs(platform, 4, 0, None, ct.byref(devices_count))
            if status == -1:  # CL_DEVICE_NOT_FOUND on this platform
                continue
            _check(status, 'clGetDeviceIDs', OpenCLUnavailable)
            devices = (Handle * devices_count.value)()
            _check(self.lib.clGetDeviceIDs(platform, 4, devices_count, devices, None), 'clGetDeviceIDs', OpenCLUnavailable)
            for raw in devices:
                vendor_id = UInt()
                _check(self.lib.clGetDeviceInfo(raw, 0x1001, ct.sizeof(vendor_id), ct.byref(vendor_id), None),
                       'clGetDeviceInfo(CL_DEVICE_VENDOR_ID)', OpenCLUnavailable)
                if vendor_id.value != 0x8086:
                    continue
                unified = UInt()
                _check(self.lib.clGetDeviceInfo(raw, 0x1035, ct.sizeof(unified), ct.byref(unified), None),
                       'clGetDeviceInfo(CL_DEVICE_HOST_UNIFIED_MEMORY)', OpenCLUnavailable)
                if unified.value:
                    return Handle(raw)
        raise OpenCLUnavailable('未找到 Intel OpenCL 核显计算设备')

    def upload(self, array, owner):
        status = Int()
        raw = self.lib.clCreateBuffer(self.context, 1 | 32, array.nbytes, array.ctypes.data, ct.byref(status))
        _check(status.value, 'clCreateBuffer')
        handle = Handle(raw)
        owner.callback(self.lib.clReleaseMemObject, handle)
        return handle

    def execute(self, inputs, width, height, flags):
        with ExitStack() as call:
            out = self.upload(flags, call)
            for start in range(0, len(flags), 32):
                arguments = (*inputs, Int(width), Int(height), Int(start), out)
                for index, arg in enumerate(arguments):
                    _check(self.lib.clSetKernelArg(self.kernel, index, ct.sizeof(arg), ct.byref(arg)), 'clSetKernelArg')
                grid = (Size * 3)(width, height, min(32, len(flags) - start))
                _check(self.lib.clEnqueueNDRangeKernel(self.queue, self.kernel, 3, None, grid, None, 0, None, None),
                       'clEnqueueNDRangeKernel')
            _check(self.lib.clEnqueueReadBuffer(self.queue, out, 1, 0, flags.nbytes,
                                                flags.ctypes.data, 0, None, None), 'clEnqueueReadBuffer')

    def close(self):
        self._owned.close()
