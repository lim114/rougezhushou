"""Small stdlib-only native evidence helpers; this file imports no project code."""
import gzip
import hashlib
import io
import os
import pickle
import struct
from pathlib import Path


def sha256(data):
    if type(data) is not bytes:
        raise TypeError('Hash input must be bytes')
    return hashlib.sha256(data).hexdigest()


def validate_native(value):
    """Admit only exact builtins, including container cycles and shared references."""
    todo = [value]
    seen = set()
    while todo:
        current = todo.pop()
        kind = type(current)
        if current is None or kind in (bool, int, float, str, bytes):
            continue
        if kind not in (dict, list, tuple):
            raise TypeError('Unsupported evidence type: ' + kind.__name__)
        if id(current) in seen:
            continue
        seen.add(id(current))
        if kind is dict:
            for key, item in current.items():
                todo.extend((key, item))
        else:
            todo.extend(current)


def assert_native_equal(actual, expected, label=''):
    """Compare types, float bits, dict order, and bidirectional container aliases."""
    todo = [(actual, expected, '$')]
    left_to_right = {}
    right_to_left = {}
    visited = set()
    while todo:
        left, right, coordinate = todo.pop()
        kind = type(left)
        if kind is not type(right):
            raise AssertionError((label, coordinate, 'type', kind.__name__, type(right).__name__))
        if left is None:
            continue
        if kind is float:
            if struct.pack('>d', left) != struct.pack('>d', right):
                raise AssertionError((label, coordinate, 'float bits', left.hex(), right.hex()))
            continue
        if kind in (bool, int, str, bytes):
            if left != right:
                raise AssertionError((label, coordinate, 'scalar value'))
            continue
        if kind not in (dict, list, tuple):
            raise TypeError('Unsupported evidence type: ' + kind.__name__)
        left_id, right_id = id(left), id(right)
        if left_id in left_to_right and left_to_right[left_id] != right_id:
            raise AssertionError((label, coordinate, 'left container alias differs'))
        if right_id in right_to_left and right_to_left[right_id] != left_id:
            raise AssertionError((label, coordinate, 'right container alias differs'))
        left_to_right[left_id] = right_id
        right_to_left[right_id] = left_id
        if (left_id, right_id) in visited:
            continue
        visited.add((left_id, right_id))
        if len(left) != len(right):
            raise AssertionError((label, coordinate, 'container length', len(left), len(right)))
        if kind is dict:
            pairs = list(zip(left.items(), right.items()))
            for index in range(len(pairs) - 1, -1, -1):
                (left_key, left_value), (right_key, right_value) = pairs[index]
                todo.append((left_value, right_value, coordinate + '/value[' + str(index) + ']'))
                todo.append((left_key, right_key, coordinate + '/key[' + str(index) + ']'))
        else:
            for index in range(len(left) - 1, -1, -1):
                todo.append((left[index], right[index], coordinate + '/' + str(index)))


def freeze(value):
    validate_native(value)
    restored = pickle.loads(pickle.dumps(value, protocol=4))
    assert_native_equal(restored, value, 'pickle protocol 4 roundtrip')
    return restored


class _NativeUnpickler(pickle.Unpickler):
    def find_class(self, module, name):
        raise ValueError('Evidence pickle may not load globals')

    def persistent_load(self, identifier):
        raise ValueError('Evidence pickle may not load external references')


def write_record(directory, sequence, value):
    directory = Path(directory)
    if type(sequence) is not int or sequence < 1:
        raise ValueError('Sequence must be a positive integer')
    validate_native(value)
    raw = pickle.dumps(value, protocol=4)
    restored = _NativeUnpickler(io.BytesIO(raw)).load()
    assert_native_equal(restored, value, 'saved native record roundtrip')
    compressed = gzip.compress(raw, compresslevel=1, mtime=0)
    name = '%06d.pickle.gz' % sequence
    with (directory / name).open('xb') as stream:
        stream.write(compressed)
        stream.flush()
        os.fsync(stream.fileno())
    return {'path': name, 'bytes': len(compressed), 'sha256': sha256(compressed),
            'decoded_bytes': len(raw), 'decoded_sha256': sha256(raw), 'pickle_protocol': 4}


def read_record(directory, row):
    directory = Path(directory)
    name = row['path']
    if type(name) is not str or Path(name).name != name or not name.endswith('.pickle.gz'):
        raise ValueError('Record must have a single safe relative filename')
    path = directory / name
    if path.is_symlink():
        raise ValueError('Evidence records may not be symlinks')
    compressed = path.read_bytes()
    if len(compressed) != row['bytes'] or sha256(compressed) != row['sha256']:
        raise AssertionError('Saved compressed record length/hash mismatch: ' + name)
    raw = gzip.decompress(compressed)
    if len(raw) != row['decoded_bytes'] or sha256(raw) != row['decoded_sha256']:
        raise AssertionError('Saved native record length/hash mismatch: ' + name)
    if row['pickle_protocol'] != 4 or not raw.startswith(b'\x80\x04'):
        raise AssertionError('Expected pickle protocol 4: ' + name)
    stream = io.BytesIO(raw)
    value = _NativeUnpickler(stream).load()
    if stream.read():
        raise AssertionError('Trailing bytes after native record: ' + name)
    validate_native(value)
    return value


def source_map(root, folders=('rouge', 'tests', 'scripts')):
    root = Path(root).resolve()
    result = {}
    for folder_name in folders:
        folder = root / folder_name
        if not folder.is_dir():
            raise ValueError('Missing maintained source directory: ' + str(folder))
        for path in sorted(folder.rglob('*')):
            relative = path.relative_to(root)
            if '__pycache__' in relative.parts or path.suffix not in ('.py', '.json'):
                continue
            if path.is_symlink():
                raise ValueError('Maintained source may not be a symlink: ' + str(relative))
            if path.is_file():
                result[relative.as_posix()] = sha256(path.read_bytes())
    return dict(sorted(result.items()))
