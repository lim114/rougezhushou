"""Recheck only original AsFloat bytes and RIP data; no DLL execution."""
from pathlib import Path
import hashlib
import json
import struct

HERE = Path(__file__).resolve().parent
source = HERE.parent / 'section283-preparation/panel-writer-helper-candidate.json'
source_raw = source.read_bytes()
candidate = json.loads(source_raw)
dll = Path(candidate['source_game_dll'])
raw = dll.read_bytes()
assert hashlib.sha256(raw).hexdigest() == candidate['dll_sha256']
pe = struct.unpack_from('<I', raw, 0x3c)[0]
assert raw[pe:pe + 4] == b'PE\0\0'
section_count, optional_size = struct.unpack_from('<H', raw, pe + 6)[0], struct.unpack_from('<H', raw, pe + 20)[0]
optional = pe + 24
assert struct.unpack_from('<H', raw, optional)[0] == 0x20b
base = struct.unpack_from('<Q', raw, optional + 24)[0]
table = optional + optional_size
sections = [struct.unpack_from('<IIII', raw, table + n * 40 + 8) for n in range(section_count)]

def offset(address):
    rva = address - base
    for virtual_size, virtual_address, raw_size, raw_offset in sections:
        if virtual_address <= rva < virtual_address + raw_size:
            return raw_offset + rva - virtual_address
    raise AssertionError('not file-backed RVA')

method = next(m for m in candidate['methods'] if m['method']['Address'] == 0x1866fae20)
assert method['instruction_count'] == 19 and method['cfg_bounded_traversal_finished'] is True
instructions, refs = [], {}
for row in method['instructions']:
    wanted = bytes.fromhex(row['bytes'])
    at = offset(int(row['address'], 16))
    assert at == int(row['physical_offset'], 16)
    assert raw[at:at + len(wanted)] == wanted
    instructions.append({'address': row['address'], 'physical_offset': at, 'bytes': row['bytes']})
    for ref in row.get('rip_data', []):
        target = int(ref['address'], 16)
        at = offset(target)
        assert raw[at:at + 8] == bytes.fromhex(ref['bytes8'])
        refs[target] = {'address': ref['address'], 'physical_offset': at, 'bytes8': ref['bytes8']}
convert = next(r for r in method['instructions'] if r['mnemonic'] == 'cvtsi2ss')
assert convert['bytes'] == 'f3480f2ac3' and convert['operands'] == 'xmm0, rbx'
multiply = next(r for r in method['instructions'] if r['mnemonic'] == 'mulss')
assert multiply['rip_data'][0]['uint32'] == 0x2f800000
assert instructions[-1]['bytes'] == 'c3'
result = {'kind': 'SECTION283_FP_ASFLOAT_ORIGINAL_FILE_FRESH_READBACK',
          'candidate_sha256': hashlib.sha256(source_raw).hexdigest(),
          'dll_sha256': hashlib.sha256(raw).hexdigest(),
          'method_address': '0x1866fae20', 'instruction_count': len(instructions),
          'instructions': instructions, 'rip_spans': list(refs.values()),
          'fresh_byte_spans': len(instructions) + len(refs),
          'signed64_cvtsi2ss_rex_w': True, 'scale_single_bits': 0x2f800000,
          'facts': ['Signed64 raw is loaded as a qword before conversion.',
                    'Legacy CVTSI2SS uses the signed64 RBX operand.',
                    'MULSS uses Single2^-32 from original file-backed RIP data.'],
          'source_reuse_not_new_mechanism_count': True,
          'actual_mxcsr_or_masks_proven': False, 'actual_hotfix_equivalence_proven': False,
          'game_dll_executed': False, 'process_memory_read': False}
target = HERE / 'fp-asfloat-primary-readback-283.json'
assert not target.exists(), 'preserve first original-file readback'
target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
print(json.dumps({'output': str(target), 'sha256': hashlib.sha256(target.read_bytes()).hexdigest(),
                  'instructions': len(instructions), 'rip_spans': len(refs)}, ensure_ascii=False))
