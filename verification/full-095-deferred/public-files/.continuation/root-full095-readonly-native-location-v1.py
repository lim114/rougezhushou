"""Briefly sample only registers; detach without changing memory or registers."""
import ctypes
import hashlib
import json
import os
import struct
import time
from datetime import datetime, timezone
from pathlib import Path

PID = 38556
FIELDS = ('r15 r14 r13 r12 rbp rbx r11 r10 r9 r8 rax rcx rdx rsi rdi '
          'orig_rax rip cs eflags rsp ss fs_base gs_base ds es fs gs').split()


class Registers(ctypes.Structure):
    _fields_ = [(name, ctypes.c_ulonglong) for name in FIELDS]


libc = ctypes.CDLL(None, use_errno=True)
libc.ptrace.restype = ctypes.c_long
libc.ptrace.argtypes = (ctypes.c_uint, ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p)


def call(request, data=None):
    result = libc.ptrace(request, PID, None, data)
    if result == -1:
        error = ctypes.get_errno()
        raise OSError(error, os.strerror(error))


report = {'status': 'READ_ONLY_NATIVE_LOCATION_DIAGNOSTIC',
          'observed_at': datetime.now(timezone.utc).isoformat(), 'pid': PID,
          'project_calls': 0, 'new_wine_executions': 0,
          'memory_or_register_writes': 0, 'UI_primary_exit_observed': False,
          'UI_PASS_claimed': False, 'samples': []}
for number in range(2):
    seized = False
    try:
        call(0x4206)  # PTRACE_SEIZE, verified local sys/ptrace.h.
        seized = True
        before = time.monotonic()
        call(0x4207)  # PTRACE_INTERRUPT; no signal delivery or group stop change.
        deadline = before + 3
        while True:
            waited, status = os.waitpid(PID, os.WNOHANG)
            if waited:
                assert os.WIFSTOPPED(status)
                break
            if time.monotonic() >= deadline:
                raise TimeoutError('Register sample stop was not observed')
            time.sleep(0.01)
        registers = Registers()
        call(12, ctypes.byref(registers))  # PTRACE_GETREGS only.
        rip = registers.rip
        call(17)  # PTRACE_DETACH, signal 0, no memory/register changes.
        seized = False
        elapsed = time.monotonic() - before
        mappings = Path(f'/proc/{PID}/maps').read_text().splitlines()
        current = None
        images = []
        for row in mappings:
            pieces = row.split(maxsplit=5)
            lower, upper = [int(x, 16) for x in pieces[0].split('-')]
            if lower <= rip < upper:
                current = row
            if len(pieces) == 6 and pieces[2] == '00000000' and pieces[5].endswith(('.dll', '.pyd', '.exe')):
                path = Path(pieces[5])
                header = path.read_bytes()
                if header[:2] != b'MZ':
                    continue
                pe = struct.unpack_from('<I', header, 0x3c)[0]
                if header[pe:pe+4] != b'PE\0\0':
                    continue
                size = struct.unpack_from('<I', header, pe + 24 + 56)[0]
                if lower <= rip < lower + size:
                    images.append({'path': str(path), 'image_base': hex(lower),
                                   'relative_virtual_address': hex(rip-lower),
                                   'bytes': len(header), 'sha256': hashlib.sha256(header).hexdigest()})
        report['samples'].append({'sample': number + 1, 'instruction_pointer': hex(rip),
                                  'interruption_seconds': elapsed,
                                  'matching_mapping': current, 'matching_PE_images': images})
    except (OSError, TimeoutError) as error:
        report['diagnostic_error'] = {'type': type(error).__name__, 'message': str(error)}
        break
    finally:
        if seized:
            call(17)
    if number == 0:
        time.sleep(0.2)
report['process_not_left_traced'] = 'TracerPid:\t0\n' in Path(f'/proc/{PID}/status').read_text()
assert report['process_not_left_traced']
print(json.dumps(report, ensure_ascii=True, indent=2))
