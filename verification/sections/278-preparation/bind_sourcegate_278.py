"""Bind selected original native/metadata bytes, only under cache; no DLL execution."""
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
sha = lambda data: hashlib.sha256(data).hexdigest()
primary = json.loads((BASE / 'mapping-verification.json').read_bytes())
assert sha(ns['binary']) == primary['game_dll_sha256']
assert sha(ns['meta']) == primary['metadata_sha256']
artifacts, methods, instructions = {}, {}, {}
spans = []


def read(path):
    raw = path.read_bytes()
    artifacts[path.relative_to(ROOT).as_posix()] = sha(raw)
    return json.loads(raw)


def bind(source, position, raw, label):
    position = int(position, 0) if isinstance(position, str) else position
    actual = ns['binary'] if source == 'dll' else ns['meta']
    assert actual[position:position + len(raw)] == raw, label
    spans.append({'source': source, 'physical_offset': position, 'raw_hex': raw.hex(), 'label': label})


old = read(HERE.parent / 'p2-sp-sourcegate-276/source-proof-preparation-276.json')
selected = {32849, 32863, 66606, 66747, 72708, 72662, 76055, 76057, 237419, 237420, 220359, 220360}
for row in old['methods']:
    if row['method'].get('metadata_method_index') in selected:
        methods[(row['method']['Address'], row['method']['metadata_method_index'])] = row
for filename in ('skill-data-modifier-first-278.json', 'skill-data-modifier-dependencies-278.json',
                 'rounding-native-helpers-278.json', 'roundtoint-method-278.json',
                 'protected-float-signatures-278.json', 'init-key-renderer-278.json'):
    report = read(HERE / filename)
    assert report['dll_sha256'] == primary['game_dll_sha256']
    assert report['metadata_sha256'] == primary['metadata_sha256']
    for row in report['methods']:
        key = (row['method']['Address'], row['method'].get('metadata_method_index'))
        if key in methods:
            assert methods[key]['reachable_bytes_sha256'] == row['reachable_bytes_sha256']
        methods[key] = row
for row in methods.values():
    assert row['cfg_bounded_traversal_finished'] and not row['limits']
    for ins in row['instructions']:
        raw = bytes.fromhex(ins['bytes'])
        assert instructions.setdefault(ins['address'], raw) == raw
        bind('dll', ins['physical_offset'], raw, row['method']['Name'] + '@' + ins['address'])
        for rip in ins.get('rip_data', []):
            bind('dll', ns['offset'](int(rip['address'], 16)), bytes.fromhex(rip['bytes8']), 'RIP ' + rip['address'])

metadata = []
params = ns['records']('parameters', 'Iii')
for index in sorted({key[1] for key in methods if key[1] is not None}):
    row = ns['methods'][index]
    name = ns['type_def_name'](row[1]) + '$$' + ns['string'](row[0])
    bind('metadata', ns['header']['methods'][0] + index * 32, struct.pack('<IiiiiI4H', *row), name + ' method row')
    position = ns['offset'](ns['reg']['types'][row[2]])
    bind('dll', position, ns['binary'][position:position + 12], name + ' return native type')
    parameters = []
    for pi in range(row[3], row[3] + row[9]):
        p = params[pi]
        bind('metadata', ns['header']['parameters'][0] + pi * 12, struct.pack('<Iii', *p), name + ' parameter')
        position = ns['offset'](ns['reg']['types'][p[2]])
        bind('dll', position, ns['binary'][position:position + 12], name + ' parameter native type')
        parameters.append({'name': ns['string'](p[0]), 'type': ns['typename'](p[2])})
    metadata.append({'index': index, 'name': name, 'return_type': ns['typename'](row[2]),
                     'parameters': parameters, 'slot': row[8]})

wanted = {'Torappu.SpData', 'Torappu.SkillData', 'Torappu.SpType', 'Torappu.SpTypeIndex',
          'Torappu.Battle.BattleCharacterData', 'Torappu.Battle.UnitDataFlowConfig',
          'Torappu.Battle.UnitDataFlowConfig+Delta', 'Torappu.Battle.UnitDataFlowConfig+Modifier',
          'Torappu.Battle.UnitDataFlowConfig+FormulaType', 'Torappu.Battle.UnitDataFlowConfig+ModifyType',
          'Torappu.Battle.UnitDataFlowConfig+DataType', 'Torappu.Battle.Skills.SpScaleAfterSkillCast',
          'Torappu.Battle.Skills.ModifySpDataAfterSkillCast',
          'CodeStage.AntiCheat.ObscuredTypes.ObscuredFloat', 'CodeStage.AntiCheat.ObscuredTypes.ObscuredInt'}
layouts = []
enum_defaults = []
defaults = ns['records']('fieldDefaultValues', 'iii')
for index, td in enumerate(ns['types']):
    name = ns['type_def_name'](index)
    if name not in wanted:
        continue
    bind('metadata', ns['header']['typeDefinitions'][0] + index * 92, struct.pack('<IIiiiiiIiiiiiiiii8HII', *td), name)
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
            bind('dll', position, ns['binary'][position:position + 4], name + '.' + field_name + ' offset')
            offset = struct.unpack_from('<I', ns['binary'], position)[0]
        field = {'index': fi, 'name': field_name, 'type': ns['typename'](row[1]), 'offset': offset}
        if td[25] & 2 and fi in ns['defaults']:
            default = ns['defaults'][fi]
            default_index = defaults.index(default)
            bind('metadata', ns['header']['fieldDefaultValues'][0] + default_index * 12, struct.pack('<iii', *default), name + '.' + field_name + ' default row')
            value = ns['default_value'](fi)
            bind('metadata', ns['header']['fieldAndParameterDefaultValueData'][0] + default[2], bytes.fromhex(value['raw']), name + '.' + field_name + ' compressed default')
            field['enum_default'] = value
            enum_defaults.append({'type': name, 'field': field_name, 'value': value})
        fields.append(field)
    layouts.append({'name': name, 'index': index, 'fields': fields})

unity = read(HERE / 'common-mapping-verification.json')
third = read(HERE.parent / 'p2-sp-sourcegate-276/common-mapping-verification.json')
for receipt, indices in ((unity, {282369}), (third, {237392, 237393, 237419, 237420})):
    module = receipt['codegen_module']
    assert receipt['game_dll_sha256'] == primary['game_dll_sha256']
    assert receipt['metadata_sha256'] == primary['metadata_sha256']
    bind('dll', module['module_offset'], ns['binary'][module['module_offset']:module['module_offset'] + 24], 'exact codegen module registration')
    for (address, index), row in methods.items():
        if index not in indices:
            continue
        position = module['array_offset'] + ((int(row['method']['token'], 16) & 0xffffff) - 1) * 8
        raw = ns['binary'][position:position + 8]
        assert struct.unpack('<Q', raw)[0] == address
        bind('dll', position, raw, row['method']['Name'] + ' exact codegen pointer')

for filename in ('targeted-type-metadata-278.json', 'signature-and-return-layouts-278.json',
                 'sp-type-index-metadata-278.json', 'intel-arithmetic-source.json'):
    read(HERE / filename)
for path in (reader, BASE / 'mapping-verification.json', HERE / 'extract_skill_data_278.py',
             HERE / 'extract_protected_float_278.py', HERE / 'map_unity_source_278.py', Path(__file__)):
    artifacts[path.relative_to(ROOT).as_posix()] = sha(path.read_bytes())
result = {'kind': 'SECTION278_PURE_FILE_SKILL_DATA_SOURCE_GATE_PREPARATION_NOT_IMPLEMENTED',
          'dll_sha256': primary['game_dll_sha256'], 'metadata_sha256': primary['metadata_sha256'],
          'source_game_dll': primary['source_game_dll'], 'source_metadata': str(ns['META']),
          'file_only': True, 'game_dll_executed': False, 'process_memory_read': False,
          'production_or_tests_modified': False, 'current_hotfix_equivalence_proven': False,
          'method_count': len(methods), 'unique_instruction_count': len(instructions), 'byte_span_count': len(spans),
          'methods': list(methods.values()), 'method_metadata': metadata, 'layouts': layouts,
          'enum_defaults': enum_defaults, 'byte_spans': spans, 'source_artifacts_sha256': artifacts,
          'all_spans_rechecked_against_fresh_primary_files': True,
          'numeric_scope': 'Independent decoded cost/Single BB operands, source arithmetic/encoder parameters and known write prefixes only',
          'helper_metadata_identity_proven': False,
          'actual_cost_or_sp_or_clock_or_complete_cycle_proven': False,
          'protected_value_encode_decode_roundtrip_proven': False,
          'unknown': ['current activation/order/BB/hotfix/derived instances', 'actual MXCSR/FTZ/DAZ/exception masks',
                      'post-encoding decoded dataCost and capacities', 'actual4 formattedBB keys and decoder output',
                      'actual actor SP and actual clocks/full skill cycle']}
raw = (json.dumps(result, ensure_ascii=False, indent=2) + '\n').encode('utf8')
target = HERE / 'source-proof-preparation-278.json'
target.write_bytes(raw)
print(json.dumps({'path': str(target.relative_to(ROOT)), 'sha256': sha(raw), 'methods': len(methods),
                  'instructions': len(instructions), 'spans': len(spans)}, ensure_ascii=False))
