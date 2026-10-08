import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OFFICIAL = Path('/workspace/.continuation/p2-gummy-back-parser-source087-official-reader/official-source/spine-ts/core/src/SkeletonBinary.ts')

def read_positive_varint(data, offset):
    # Source: official SkeletonBinary.ts:815-835, optimizePositive=true.
    result = 0
    for shift in range(0, 35, 7):
        b = data[offset]
        offset += 1
        result |= (b & 0x7f) << shift
        if not b & 0x80:
            return result, offset
    raise ValueError('Unexpected header varint continuation')

def read_ascii_header_string(data, offset):
    # Source: official readString():842-871. These two actual headers are ASCII;
    # stop rather than claim this extraction implements a full UTF-8 reader.
    start = offset
    count, offset = read_positive_varint(data, offset)
    if count == 0:
        return None, offset, {'start': start, 'end': offset, 'encoded_count': count}
    if count == 1:
        return '', offset, {'start': start, 'end': offset, 'encoded_count': count}
    raw = data[offset:offset + count - 1]
    assert len(raw) == count - 1 and all(b < 128 for b in raw)
    offset += len(raw)
    return raw.decode('ascii'), offset, {'start': start, 'end': offset, 'encoded_count': count}

receipt = {'version': 1, 'operation': 'header-only extraction of the first two documented official strings', 'full_skeleton_parser_calls': 0, 'application_calls': 0, 'official_reader_source_path': str(OFFICIAL), 'official_reader_sha256': hashlib.sha256(OFFICIAL.read_bytes()).hexdigest(), 'official_commit': '8b4844bd4b193ba9e54487ed397a777993cbad56', 'resources': []}
for orientation in ('Front', 'Back'):
    path = ROOT / 'reacquired' / orientation / 'char_196_sunbr.skel'
    data = path.read_bytes()
    skeleton_hash, offset, first = read_ascii_header_string(data, 0)
    version, offset, second = read_ascii_header_string(data, offset)
    receipt['resources'].append({'orientation': orientation, 'source_path': str(path), 'resource_bytes': len(data), 'resource_sha256': hashlib.sha256(data).hexdigest(), 'skeleton_hash_string': skeleton_hash, 'spine_version_string': version, 'hash_field': first, 'version_field': second, 'header_end_offset': offset, 'raw_header_hex': data[:offset].hex()})
out = ROOT / 'header-only-receipt.json'
out.write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps(receipt, indent=2))
