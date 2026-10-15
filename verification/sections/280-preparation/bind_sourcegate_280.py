"""Fresh original byte/metadata and official CPU file binding; no DLL execution."""
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
artifacts, spans, methods, instructions = {}, [], [], {}


def read(path):
    raw = path.read_bytes()
    artifacts[path.relative_to(ROOT).as_posix()] = sha(raw)
    return json.loads(raw)


def bind(source, position, raw, label):
    position = int(position, 0) if isinstance(position, str) else position
    actual = ns['binary'] if source == 'dll' else ns['meta']
    assert actual[position:position + len(raw)] == raw, label
    spans.append({'source': source, 'physical_offset': position, 'raw_hex': raw.hex(), 'label': label})


previous = read(HERE.parent / 'p2-skill-data-modifiers-278/source-proof-preparation-278.json')
assert sha((HERE.parent / 'p2-skill-data-modifiers-278/source-proof-preparation-278.json').read_bytes()) == '823f5e9fca98291bba30336b2836f9167bbc4242c774c1fb93695cd0d17c7f30'
selected = {85326, 85329, 85835, 237419, 237420}
raw_addresses = {0x18059e290, 0x1804d57f0, 0x1804d3200, 0x1804d58c0}
for method in previous['methods']:
    index = method['method'].get('metadata_method_index')
    if index not in selected and method['method']['Address'] not in raw_addresses:
        continue
    assert method['cfg_bounded_traversal_finished'] and not method['limits']
    methods.append(method)
    for ins in method['instructions']:
        raw = bytes.fromhex(ins['bytes'])
        assert instructions.setdefault(ins['address'], raw) == raw
        bind('dll', ins['physical_offset'], raw, method['method']['Name'] + '@' + ins['address'])
        for rip in ins.get('rip_data', []):
            bind('dll', ns['offset'](int(rip['address'], 16)), bytes.fromhex(rip['bytes8']), 'RIP ' + rip['address'])
assert len(methods) == 9
params = ns['records']('parameters', 'Iii')
metadata = []
for index in sorted(selected):
    row = ns['methods'][index]
    name = ns['type_def_name'](row[1]) + '$$' + ns['string'](row[0])
    bind('metadata', ns['header']['methods'][0] + index * 32, struct.pack('<IiiiiI4H', *row), name + ' method')
    position = ns['offset'](ns['reg']['types'][row[2]])
    bind('dll', position, ns['binary'][position:position + 12], name + ' return type')
    arguments = []
    for pi in range(row[3], row[3] + row[9]):
        p = params[pi]
        bind('metadata', ns['header']['parameters'][0] + pi * 12, struct.pack('<Iii', *p), name + ' parameter')
        position = ns['offset'](ns['reg']['types'][p[2]])
        bind('dll', position, ns['binary'][position:position + 12], name + ' parameter type')
        arguments.append({'name': ns['string'](p[0]), 'type': ns['typename'](p[2])})
    metadata.append({'index': index, 'name': name, 'return_type': ns['typename'](row[2]), 'parameters': arguments})
layouts = []
wanted = {'Torappu.SpData', 'Torappu.SkillData', 'CodeStage.AntiCheat.ObscuredTypes.ObscuredInt'}
for index, td in enumerate(ns['types']):
    name = ns['type_def_name'](index)
    if name not in wanted:
        continue
    bind('metadata', ns['header']['typeDefinitions'][0] + index * 92,
         struct.pack('<IIiiiiiIiiiiiiiii8HII', *td), name + ' type')
    fields = []
    pointer = ns['reg']['fields'][index]
    for ordinal, fi in enumerate(range(td[8], td[8] + td[19])):
        row = ns['fields'][fi]
        field = ns['string'](row[0])
        bind('metadata', ns['header']['fields'][0] + fi * 12, struct.pack('<IiI', *row), name + '.' + field)
        position = ns['offset'](ns['reg']['types'][row[1]])
        bind('dll', position, ns['binary'][position:position + 12], name + '.' + field + ' type')
        offset = None
        if pointer:
            position = ns['offset'](pointer) + ordinal * 4
            raw = ns['binary'][position:position + 4]
            bind('dll', position, raw, name + '.' + field + ' offset')
            offset = struct.unpack('<I', raw)[0]
        fields.append({'index': fi, 'name': field, 'type': ns['typename'](row[1]), 'offset': offset})
    layouts.append({'name': name, 'index': index, 'fields': fields})
protected = read(HERE.parent / 'p2-sp-sourcegate-276/common-mapping-verification.json')
module = protected['codegen_module']
bind('dll', module['module_offset'], ns['binary'][module['module_offset']:module['module_offset'] + 24], 'protected codegen module')
for row in methods:
    if row['method'].get('metadata_method_index') not in (237419, 237420):
        continue
    position = module['array_offset'] + ((int(row['method']['token'], 16) & 0xffffff) - 1) * 8
    raw = ns['binary'][position:position + 8]
    assert struct.unpack('<Q', raw)[0] == row['method']['Address']
    bind('dll', position, raw, row['method']['Name'] + ' actual codegen pointer')
cpu1 = read(HERE.parent / 'p2-skill-data-modifiers-278/intel-arithmetic-source.json')
cpu2 = read(HERE / 'intel-rounding-source-inspection-v2-280.json')
assert sha((HERE.parent / 'p2-skill-data-modifiers-278/intel-sdm-vol1-dec2024.pdf').read_bytes()) == cpu1['sha256']
assert sha((HERE / 'intel-sdm-volume2abcd-280.pdf').read_bytes()) == cpu2['file_sha256']
independent = read(ROOT / '.cache/section278-independent-cost-source/cost-source-review.json')
assert independent['fresh_primary_bytes_matched'] is True
for path in (reader, Path(__file__), BASE / 'mapping-verification.json', HERE / 'inspect_intel_rounding_280.py',
             HERE / 'inspect_intel_rounding_280_v2.py', HERE / 'SOURCE_INSPECTION_CORRECTION.md'):
    artifacts[path.relative_to(ROOT).as_posix()] = sha(path.read_bytes())
packet = {'kind': 'SECTION280_FILE_ONLY_COST_ROUNDING_CONSENSUS_PREPARATION_NOT_IMPLEMENTED',
          'source_game_dll': primary['source_game_dll'], 'source_metadata': str(ns['META']),
          'dll_sha256': primary['game_dll_sha256'], 'metadata_sha256': primary['metadata_sha256'],
          'file_only': True, 'game_dll_executed': False, 'process_memory_read': False, 'production_or_tests_modified': False,
          'method_count': len(methods), 'unique_instruction_count': len(instructions), 'byte_span_count': len(spans),
          'methods': methods, 'method_metadata': metadata, 'layouts': layouts, 'byte_spans': spans,
          'source_artifacts_sha256': artifacts, 'all_spans_rechecked_against_fresh_primary_files': True,
          'official_cpu_sources': [cpu1, cpu2], 'game_current_MXCSR_proven': False,
          'normal_exception_handler_result_preservation_proven': False,
          'rc_pair_scope': 'all16_independent_RC_pairs_conservative_superset',
          'ordinary_cost_instruction_pairs': [
              {'kind': 'rune_mul', 'conversion': '0x180cf70c6', 'operation': '0x180cf70c9', 'round': '0x18059e290'},
              {'kind': 'rune_add', 'conversion': '0x180cf6e95', 'operation': '0x180cf6e98', 'round': '0x18059e290'},
              {'kind': 'relic_mul', 'conversion': '0x180d0f2a6', 'operation': '0x180d0f2a9', 'round': 'inline half-even'}],
          'unmapped_round_helper_metadata_identity_proven': False,
          'numeric_scope': 'Conditional ordinary hardware normal finite/zero results; all16 qualifying signed32 rounded integers must agree',
          'protected_roundtrip_or_actual_cost_sp_complete_cycle_proven': False,
          'unknown': ['real RC/coupling/FTZ/DAZ/exception masks/handler result overrides',
                      'actual activation/order/decoded values/BB/hotfix/current instances',
                      'subnormal/nonfinite/overflow/rounded Int32 domain outside supported scope',
                      'actual cost/SP/clock/full skill cycle']}
target = HERE / 'source-proof-preparation-280.json'
assert not target.exists(), 'preserve original source gate receipt'
raw = (json.dumps(packet, ensure_ascii=False, indent=2) + '\n').encode('utf8')
target.write_bytes(raw)
print(json.dumps({'path': str(target.relative_to(ROOT)), 'sha256': sha(raw), 'methods': len(methods),
                  'instructions': len(instructions), 'spans': len(spans)}, ensure_ascii=False))
