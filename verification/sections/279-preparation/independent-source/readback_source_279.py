"""Original-file byte audit only; no native execution or process-memory access."""
from fractions import Fraction
from pathlib import Path
import hashlib
import json
import mmap
import struct

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
RESEARCH = ROOT / '.cache/research/p2-sp-increments-279'
INPUTS = [RESEARCH / 'increments-source-279.json', RESEARCH / 'increments-consumers-279.json']
documents = [json.loads(p.read_bytes()) for p in INPUTS]
mapping = json.loads((ROOT / '.cache/research/p2-native-current-263/mapping-verification.json').read_bytes())


def physical(address):
    rva = int(address, 16) - mapping['image_base']
    for section in mapping['sections']:
        if section['rva'] <= rva < section['rva'] + section['raw_size']:
            return section['offset'] + rva - section['rva']
    raise AssertionError('Not a file-backed address')


instructions, spans, methods = {}, 0, []
with Path(mapping['source_game_dll']).open('rb') as handle, mmap.mmap(handle.fileno(), 0, access=mmap.ACCESS_READ) as binary:
    dll_sha = hashlib.sha256(binary).hexdigest()
    assert dll_sha == mapping['game_dll_sha256']
    for document in documents:
        assert document['dll_sha256'] == dll_sha
        for method in document['methods']:
            assert method['cfg_bounded_traversal_finished'] is True and method['limits'] == []
            methods.append({'index': method['method']['metadata_method_index'], 'name': method['method']['Name'],
                            'instruction_count': len(method['instructions'])})
            for instruction in method['instructions']:
                raw = bytes.fromhex(instruction['bytes'])
                offset = int(instruction['physical_offset'], 16)
                assert binary[offset:offset + len(raw)] == raw
                assert instructions.setdefault(instruction['address'], instruction)['bytes'] == instruction['bytes']
                spans += 1
                for rip in instruction.get('rip_data', []):
                    raw = bytes.fromhex(rip['bytes8'])
                    offset = physical(rip['address'])
                    assert binary[offset:offset + len(raw)] == raw
                    spans += 1
    epsilon = instructions['0x1866e4b90']['rip_data'][0]
    assert epsilon['address'] == '0x186e3fd88' and epsilon['uint32'] == 0x3727C5AC
    epsilon_value = Fraction.from_float(struct.unpack('<f', bytes.fromhex(epsilon['bytes8'])[:4])[0])
    assert epsilon_value == Fraction(2748779, 274877906944)
    one = instructions['0x18252b426']['rip_data'][0]
    assert one['bytes8'] == '0000803f00000000'
    tick = next(m for m in documents[1]['methods'] if m['method']['metadata_method_index'] == 66751)
    assert not any('[rdi + 0x38]' in i['operands'] for i in tick['instructions'])
    int_fp = next(m for m in documents[1]['methods'] if m['method']['Address'] == 0x1866FDAC0)
    assert [(i['mnemonic'], i['operands']) for i in int_fp['instructions']] == [('movsxd', 'rax, ecx'), ('shl', 'rax, 0x20'), ('ret', '')]
metadata_file = Path(mapping['source_game_dll']).parent / 'Arknights_Data/il2cpp_data/Metadata/global-metadata.dat'
metadata_sha = hashlib.sha256(metadata_file.read_bytes()).hexdigest()
assert metadata_sha == mapping['metadata_sha256'] == documents[0]['metadata_sha256'] == documents[1]['metadata_sha256']
result = {
    'kind': 'SECTION279_INDEPENDENT_INITIALIZER_AND_CONSUMER_FILE_READBACK',
    'preparation_only': True, 'game_dll_executed': False, 'process_memory_read': False,
    'game_or_chat_actions': 0, 'production_or_tests_modified': False,
    'other_agent_cache_modified': False,
    'dll_sha256': dll_sha, 'metadata_sha256': metadata_sha,
    'methods': methods, 'method_count': len(methods),
    'unique_instruction_addresses': len(instructions), 'fresh_instruction_and_RIP_spans': spans,
    'source_artifacts_sha256': {str(p.relative_to(ROOT)).replace('\\', '/'): hashlib.sha256(p.read_bytes()).hexdigest() for p in INPUTS},
    'Single_GE': {'method_index': 220359, 'epsilon_bits': 0x3727C5AC,
                  'epsilon_ratio': [2748779, 274877906944], 'operator_after_SUBSS': 'ordered >=',
                  'zero_rhs_exact_threshold_bits': 0xB727C5AC,
                  'general_SUBSS_MXCSR_proven': False, 'FP_EPS_42950_reused': False},
    'inactive_increment_default': {'single_bits': 0x3F800000, 'value': 1.0, 'spType_bit_enabled': False},
    'natural_tick_caller': {'direct_slot0_array_read': False, 'direct_slot0_multiply': False,
                           'delta_from_positive_update_count': 'signed Int32 shifted left32',
                           'indirect_timer_initialization_or_callback_effects_closed': False},
    'unclosed': ['Current hotfix/instances/BB key strings and per-slot values',
                 'Consumer field +0x38 alias with an initialized SpData array',
                 'Raw index helper0x1844dc660 numerical identity/result before claiming fixed event slots',
                 'Actual recovery rate/time/current actor SP/full skill cycle'],
}
output = HERE / 'source-readback-279.json'
with output.open('x', encoding='utf-8') as handle:
    json.dump(result, handle, ensure_ascii=False, indent=2)
    handle.write('\n')
print(json.dumps({'output': str(output), 'methods': len(methods), 'unique_instructions': len(instructions),
                  'fresh_spans': spans, 'Single_GE_inclusive': True, 'native_executed': False}, ensure_ascii=False))
