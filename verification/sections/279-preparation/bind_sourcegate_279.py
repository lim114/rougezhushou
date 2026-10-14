"""Fresh file-only binding of selected increment/init native bytes and metadata."""
import hashlib
import json
from pathlib import Path
import struct

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = HERE.parent / 'p2-native-current-263'
reader = BASE / 'read_metadata_static.py'
ns = {'__file__': str(reader)}
exec(compile(reader.read_text(encoding='utf8').split('selected=[]\n')[0], str(reader), 'exec'), ns)
sha = lambda raw: hashlib.sha256(raw).hexdigest()
primary = json.loads((BASE / 'mapping-verification.json').read_bytes())
assert sha(ns['binary']) == primary['game_dll_sha256']
assert sha(ns['meta']) == primary['metadata_sha256']
methods, instructions, spans, artifacts = {}, {}, [], {}


def read(path):
    raw = path.read_bytes()
    artifacts[path.relative_to(ROOT).as_posix()] = sha(raw)
    return json.loads(raw)


def bind(source, position, raw, label):
    position = int(position, 0) if isinstance(position, str) else position
    current = ns['binary'] if source == 'dll' else ns['meta']
    assert current[position:position + len(raw)] == raw, label
    spans.append({'source': source, 'physical_offset': position, 'raw_hex': raw.hex(), 'label': label})


selected = {32850, 32851, 32852, 32863, 66748, 66749, 66751, 66752,
            220359, 220498, 220503, 30809, 30824, 70957, 237393}
for path in (HERE / 'increments-source-279.json', HERE / 'increments-consumers-279.json',
             HERE / 'increments-read-callees-279.json', HERE / 'channel-index-helper-279.json',
             HERE.parent / 'p2-skill-data-modifiers-278/protected-float-signatures-278.json',
             HERE.parent / 'p2-skill-data-modifiers-278/init-key-renderer-278.json'):
    packet = read(path)
    assert packet['dll_sha256'] == primary['game_dll_sha256']
    assert packet['metadata_sha256'] == primary['metadata_sha256']
    for row in packet['methods']:
        method = row['method']
        index = method.get('metadata_method_index')
        if index not in selected and method['Address'] not in (0x1844dc660, 0x185efd730):
            continue
        key = (method['Address'], index)
        if key in methods:
            assert methods[key]['reachable_bytes_sha256'] == row['reachable_bytes_sha256']
        methods[key] = row
assert {index for _, index in methods if index is not None} == selected
assert len(methods) == 17
for row in methods.values():
    assert row['cfg_bounded_traversal_finished'] and not row['limits']
    for instruction in row['instructions']:
        raw = bytes.fromhex(instruction['bytes'])
        assert instructions.setdefault(instruction['address'], raw) == raw
        bind('dll', instruction['physical_offset'], raw, row['method']['Name'] + '@' + instruction['address'])
        for rip in instruction.get('rip_data', []):
            bind('dll', ns['offset'](int(rip['address'], 16)), bytes.fromhex(rip['bytes8']), 'RIP ' + rip['address'])

parameters = ns['records']('parameters', 'Iii')
metadata = []
for index in sorted(selected):
    row = ns['methods'][index]
    name = ns['type_def_name'](row[1]) + '$$' + ns['string'](row[0])
    bind('metadata', ns['header']['methods'][0] + index * 32, struct.pack('<IiiiiI4H', *row), name + ' method row')
    position = ns['offset'](ns['reg']['types'][row[2]])
    bind('dll', position, ns['binary'][position:position + 12], name + ' return native type')
    params = []
    for pi in range(row[3], row[3] + row[9]):
        p = parameters[pi]
        bind('metadata', ns['header']['parameters'][0] + pi * 12, struct.pack('<Iii', *p), name + ' parameter')
        position = ns['offset'](ns['reg']['types'][p[2]])
        bind('dll', position, ns['binary'][position:position + 12], name + ' parameter native type')
        params.append({'name': ns['string'](p[0]), 'type': ns['typename'](p[2])})
    metadata.append({'index': index, 'name': name, 'return_type': ns['typename'](row[2]),
                     'parameters': params, 'slot': row[8]})

wanted = {'Torappu.SpData', 'Torappu.SkillData', 'Torappu.SpType', 'Torappu.SpTypeIndex',
          'Torappu.Battle.Entity+SpController', 'Torappu.Battle.SpController',
          'Torappu.Battle.Modifier', 'CodeStage.AntiCheat.ObscuredTypes.ObscuredFloat'}
wanted.add(ns['type_def_name'](ns['methods'][66751][1]))
layouts, enum_defaults = [], []
defaults = ns['records']('fieldDefaultValues', 'iii')
for index, td in enumerate(ns['types']):
    name = ns['type_def_name'](index)
    if name not in wanted:
        continue
    bind('metadata', ns['header']['typeDefinitions'][0] + index * 92,
         struct.pack('<IIiiiiiIiiiiiiiii8HII', *td), name + ' type')
    pointer = ns['reg']['fields'][index]
    fields = []
    for ordinal, fi in enumerate(range(td[8], td[8] + td[19])):
        row = ns['fields'][fi]
        field_name = ns['string'](row[0])
        bind('metadata', ns['header']['fields'][0] + fi * 12, struct.pack('<IiI', *row), name + '.' + field_name)
        position = ns['offset'](ns['reg']['types'][row[1]])
        bind('dll', position, ns['binary'][position:position + 12], name + '.' + field_name + ' native type')
        offset = None
        if pointer:
            position = ns['offset'](pointer) + ordinal * 4
            raw = ns['binary'][position:position + 4]
            bind('dll', position, raw, name + '.' + field_name + ' offset')
            offset = struct.unpack('<I', raw)[0]
        item = {'index': fi, 'name': field_name, 'type': ns['typename'](row[1]), 'offset': offset}
        if td[25] & 2 and fi in ns['defaults']:
            default = ns['defaults'][fi]
            default_index = defaults.index(default)
            bind('metadata', ns['header']['fieldDefaultValues'][0] + default_index * 12,
                 struct.pack('<iii', *default), name + '.' + field_name + ' default row')
            value = ns['default_value'](fi)
            bind('metadata', ns['header']['fieldAndParameterDefaultValueData'][0] + default[2],
                 bytes.fromhex(value['raw']), name + '.' + field_name + ' compressed default')
            item['enum_default'] = value
            enum_defaults.append({'type': name, 'field': field_name, 'value': value})
        fields.append(item)
    layouts.append({'name': name, 'index': index, 'fields': fields})

protected = read(HERE.parent / 'p2-sp-sourcegate-276/common-mapping-verification.json')
module = protected['codegen_module']
bind('dll', module['module_offset'], ns['binary'][module['module_offset']:module['module_offset'] + 24],
     'exact protected codegen module registration')
wrapper = next(row for row in methods.values() if row['method'].get('metadata_method_index') == 237393)
position = module['array_offset'] + ((int(wrapper['method']['token'], 16) & 0xffffff) - 1) * 8
raw = ns['binary'][position:position + 8]
assert struct.unpack('<Q', raw)[0] == wrapper['method']['Address']
bind('dll', position, raw, 'protected Float decoder exact codegen pointer')
cpu = read(HERE.parent / 'p2-skill-data-modifiers-278/intel-arithmetic-source.json')
read(BASE / 'mapping-verification.json')
for path in (reader, HERE / 'extract_sp_increments_279.py', HERE / 'helper-map-with-protected.json', Path(__file__)):
    artifacts[path.relative_to(ROOT).as_posix()] = sha(path.read_bytes())

packet = {'kind': 'SECTION279_PURE_FILE_SP_INCREMENT_SOURCE_GATE_PREPARATION_NOT_IMPLEMENTED',
          'source_game_dll': primary['source_game_dll'], 'source_metadata': str(ns['META']),
          'dll_sha256': primary['game_dll_sha256'], 'metadata_sha256': primary['metadata_sha256'],
          'file_only': True, 'game_dll_executed': False, 'process_memory_read': False,
          'production_or_tests_modified': False, 'current_hotfix_equivalence_proven': False,
          'method_count': len(methods), 'unique_instruction_count': len(instructions), 'byte_span_count': len(spans),
          'methods': list(methods.values()), 'method_metadata': metadata, 'layouts': layouts,
          'enum_defaults': enum_defaults, 'byte_spans': spans, 'source_artifacts_sha256': artifacts,
          'all_spans_rechecked_against_fresh_primary_files': True,
          'single_ge_rhs_zero': {'epsilon_bits': 0x3727c5ac, 'adjusted_rhs_bits': 0xb727c5ac,
                                 'ordered_inclusive_ge': True, 'fixed_fp_comparison_reused': False},
          'captured_blackboard_pointer': {'capture_instruction': '0x18252b311', 'loop_test_instruction': '0x18252b440',
                                         'pointer_read_count': 1, 'lookup_results_independent': True},
          'unmapped_index_helper': {'address': '0x1844dc660', 'metadata_identity_proven': False,
                                    'ordinary_result': 'unchanged low32 ECX', 'consumer_indices': [1, 2]},
          'single_to_fp': {'method_index': 220498, 'scale_q': 4294967296, 'scale_bits': 0x4f800000,
                           'multiplication_precision': 'Single', 'conversion': 'CVTTSS2SI Int64 toward zero'},
          'on_tick_direct_slot_zero_multiplier_proven': False,
          'controller_spdata_array_alias_proven': False,
          'actual_array_or_sp_or_complete_cycle_proven': False,
          'protected_encode_decode_roundtrip_proven': False,
          'official_cpu_source': cpu,
          'unknown': ['dynamic BB key strings and current lookup contents', 'current XLua/hotfix and actual instances',
                      'decoder returns/array alias/content', 'MXCSR/exception masks outside exact safe domains',
                      'actual SP/events/timers/full skill cycle']}
target = HERE / 'source-proof-preparation-279.json'
assert not target.exists(), 'preserve existing proof; use a new attempt name instead'
raw = (json.dumps(packet, ensure_ascii=False, indent=2) + '\n').encode('utf8')
target.write_bytes(raw)
print(json.dumps({'path': str(target.relative_to(ROOT)), 'sha256': sha(raw), 'methods': len(methods),
                  'instructions': len(instructions), 'spans': len(spans),
                  'layout_names': [row['name'] for row in layouts]}, ensure_ascii=False))
