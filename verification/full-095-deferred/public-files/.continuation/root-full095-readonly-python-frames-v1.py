"""Read public code/frame metadata from Win CPython 3.12.10, then detach."""
import ctypes
import json
import os
import struct
import time
from datetime import datetime, timezone
from pathlib import Path

PID = 38556
BASE = 0x6ffffad30000
libc = ctypes.CDLL(None, use_errno=True)
libc.ptrace.restype = ctypes.c_long
libc.ptrace.argtypes = (ctypes.c_uint, ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p)


def call(request):
    if libc.ptrace(request, PID, None, None) == -1:
        error = ctypes.get_errno()
        raise OSError(error, os.strerror(error))


def line_at(table, first, offset):
    start = 0
    line = first
    cursor = 0
    while cursor < len(table):
        entry = table[cursor]
        assert entry & 0x80
        kind = (entry >> 3) & 15
        end = start + ((entry & 7) + 1) * 2
        cursor += 1
        if 10 <= kind <= 12:
            line += kind - 10
        elif kind in (13, 14):
            position, shift, value = cursor, 0, 0
            while True:
                part = table[position]
                value |= (part & 63) << shift
                position += 1
                if not part & 64:
                    break
                shift += 6
            line += -(value >> 1) if value & 1 else value >> 1
        if offset < end:
            return None if kind == 15 else line
        while cursor < len(table) and not table[cursor] & 128:
            cursor += 1
        start = end
    return None


seized = False
report = {'status': 'READ_ONLY_ACTUAL_PYTHON_FRAME_METADATA_NOT_UI_PASS',
          'observed_at': datetime.now(timezone.utc).isoformat(), 'pid': PID,
          'memory_register_writes': 0, 'target_API_calls': 0,
          'project_calls': 0, 'new_Wine_runs': 0, 'threads': []}
try:
    call(0x4206)
    seized = True
    began = time.monotonic()
    call(0x4207)
    deadline = began + 3
    while True:
        waited, status = os.waitpid(PID, os.WNOHANG)
        if waited:
            assert os.WIFSTOPPED(status)
            break
        if time.monotonic() > deadline:
            raise TimeoutError('No sample stop observed')
        time.sleep(0.01)
    fd = os.open(f'/proc/{PID}/mem', os.O_RDONLY)
    try:
        def read(address, size):
            assert 0 < address < 2**63 and 0 <= size <= 2**20
            data = os.pread(fd, size, address)
            assert len(data) == size
            return data

        def pointer(address):
            return struct.unpack('<Q', read(address, 8))[0]

        def text(address):
            raw = read(address, 40)
            length = struct.unpack_from('<q', raw, 16)[0]
            flags = struct.unpack_from('<I', raw, 32)[0]
            assert 0 <= length <= 4096 and flags & 32
            kind = (flags >> 2) & 7
            if flags & 64:
                return read(address + 40, length).decode('ascii')
            assert kind in (1, 2, 4)
            return read(address + 56, length * kind).decode({1: 'latin1', 2: 'utf-16-le', 4: 'utf-32-le'}[kind])

        interpreter = pointer(BASE + 0x624028)
        thread = pointer(interpreter + 0x48)
        seen_threads = set()
        while thread and len(seen_threads) < 8:
            assert thread not in seen_threads
            seen_threads.add(thread)
            cframe = pointer(thread + 0x38)
            frame = pointer(cframe) if cframe else 0
            frames = []
            seen_frames = set()
            while frame and len(frames) < 40:
                assert frame not in seen_frames
                seen_frames.add(frame)
                code = pointer(frame)
                instruction = pointer(frame + 56)
                offset = instruction - (code + 192)
                first = struct.unpack('<i', read(code + 68, 4))[0]
                table = pointer(code + 136)
                length = struct.unpack('<q', read(table + 16, 8))[0]
                assert 0 <= length <= 2**20
                frames.append({'filename': text(pointer(code + 112)),
                               'function': text(pointer(code + 120)),
                               'bytecode_offset': offset, 'first_line': first,
                               'line_from_actual_linetable': line_at(read(table + 32, length), first, offset),
                               'actual_linetable_bytes': length})
                frame = pointer(frame + 8)
            report['threads'].append({'frames': frames})
            thread = pointer(thread + 8)
    finally:
        os.close(fd)
    call(17)
    seized = False
    report['interruption_seconds'] = time.monotonic() - began
finally:
    if seized:
        call(17)
report['process_not_left_traced'] = 'TracerPid:\t0\n' in Path(f'/proc/{PID}/status').read_text()
assert report['process_not_left_traced']
print(json.dumps(report, ensure_ascii=True, indent=2))
