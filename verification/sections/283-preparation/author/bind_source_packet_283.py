"""Prepare public file-backed panel evidence. No native loading or execution."""
from pathlib import Path
import hashlib
import json
import shutil
import struct

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]
PACKET = BASE / 'research/p2-panel-native-finalization-283'
PACKET.mkdir(parents=True, exist_ok=True)
reader = ROOT / '.cache/research/p2-native-current-263/read_metadata_static.py'
ns = {'__file__': str(reader)}
exec(compile(reader.read_text(encoding='utf8').split('selected=[]\n')[0], str(reader), 'exec'), ns)
sha = lambda raw: hashlib.sha256(raw).hexdigest()
expected = ('583b04ff4d1b1a4b35eaf09d77d936408c25447c9e345ef0463d814b6a123fc5',
            'd3fede171f92740a6f5dc053c58c7013d3c962db764ad1f05cbe977c074fcd1f')
assert (sha(ns['binary']), sha(ns['meta'])) == expected
spans, methods, seen_instructions = [], [], set()


def span(source, offset, raw):
    data = ns['binary'] if source == 'dll' else ns['meta']
    assert data[offset:offset + len(raw)] == raw
    spans.append({'source': source, 'physical_offset': offset, 'raw_hex': raw.hex()})


def take(record, provenance):
    for ins in record['instructions']:
        address = int(ins['address'], 16)
        if address not in seen_instructions:
            span('dll', int(ins['physical_offset'], 16), bytes.fromhex(ins['bytes']))
            seen_instructions.add(address)
        for ref in ins.get('rip_data', []):
            span('dll', ns['offset'](int(ref['address'], 16)), bytes.fromhex(ref['bytes8']))
    method = record['method']
    methods.append({'name': method['Name'], 'index': method.get('metadata_method_index'),
                    'address': hex(method['Address']),
                    'selected_instruction_count': record['instruction_count'],
                    'selected_code_sha256': record['reachable_bytes_sha256'],
                    'provenance': provenance, 'whole_dynamic_callgraph_closed': False})


for name in ('common-panel-native-candidate.json', 'panel-writer-helper-candidate.json', 'reflection-read-helper-283.json'):
    obj = json.loads((BASE / name).read_bytes())
    assert (obj['dll_sha256'], obj['metadata_sha256']) == expected
    for record in obj['methods']:
        take(record, name)
support = json.loads((BASE / 'type-routing-support-283.json').read_bytes())
wanted = {0x185e8b590, 0x185eded20, 0x184625350, 0x185f1fc70, 0x185d96c00,
          0x185de8ee0, 0x18660a830, 0x18660a860, 0x18660b950, 0x18660ba40,
          0x182319960}
for record in support['methods']:
    if record['method']['Address'] in wanted:
        take(record, 'type-routing-support-283.json')

# Literal identities are bound by both the metadata registration type table and
# the raw Il2CppType record. Kinds1/2 are sourced from pinned Dumper metadata
# enums rather than guessed from a native symbol alias.
literals = json.loads((BASE / 'runtime-type-literal-candidates-283.json').read_bytes())
for item in literals:
    span('dll', int(item['offset'], 16), bytes.fromhex(item['bytes8']))
    index = item['type_index']
    pointer = ns['reg']['types'][index]
    span('dll', ns['offset'](ns['reg']['values'][7]) + index * 8, struct.pack('<Q', pointer))
    span('dll', ns['offset'](pointer), ns['binary'][ns['offset'](pointer):ns['offset'](pointer) + 12])
    definition = ns['native_type'](index)['data']
    off = ns['header']['typeDefinitions'][0] + definition * 92
    span('metadata', off, ns['meta'][off:off + 92])

attribute_data = json.loads((BASE / 'common-panel-field-attributes-283.json').read_bytes())
for item in attribute_data['fields']:
    span('metadata', item['physical_offset'], bytes.fromhex(item['raw_hex']))

method_map = json.loads((BASE / 'mscorlib-map.json').read_bytes())['ScriptMethod']
map_receipt = json.loads((BASE / 'mscorlib-mapping-verification.json').read_bytes())
assert (map_receipt['game_dll_sha256'], map_receipt['metadata_sha256']) == expected
selected_map = [item for item in method_map if item['metadata_method_index'] in (239694, 241329, 241343, 242639, 247894, 248554)]
for item in selected_map:
    index = item['metadata_method_index']
    off = ns['header']['methods'][0] + index * 32
    span('metadata', off, ns['meta'][off:off + 32])
    po = map_receipt['codegen_module']['array_offset'] + ((int(item['token'], 16) & 0xffffff) - 1) * 8
    span('dll', po, struct.pack('<Q', item['Address']))

layouts = []
for ti, td in enumerate(ns['types']):
    name = ns['type_def_name'](ti)
    if name not in ('Torappu.AttributesData', 'Torappu.AttributeMetaAttribute', 'Torappu.Battle.Roguelike.RoguelikeBattleManager', 'Torappu.AttributesData+FieldMeta'):
        continue
    fp = ns['reg']['fields'][ti]
    offsets = struct.unpack_from('<' + str(td[19]) + 'i', ns['binary'], ns['offset'](fp)) if fp and td[19] else []
    fields = []
    for j, fi in enumerate(range(td[8], td[8] + td[19])):
        field = ns['fields'][fi]
        fn = ns['string'](field[0])
        if name == 'Torappu.Battle.Roguelike.RoguelikeBattleManager' and fn not in ('m_attributeAdditions', 'm_attributeMultipliers', 'm_attributeFinalScalers'):
            continue
        if name == 'Torappu.AttributesData' and fn not in ('maxHp', 'atk', 'def', 'magicResistance', 'attackSpeed'):
            continue
        fields.append({'name': fn, 'index': fi, 'type': ns['typename'](field[1]), 'offset': offsets[j]})
        off = ns['header']['fields'][0] + fi * 12
        span('metadata', off, ns['meta'][off:off + 12])
        span('dll', ns['offset'](fp) + j * 4, struct.pack('<i', offsets[j]))
    layouts.append({'name': name, 'type_index': ti, 'fields': fields})

method_metadata = []
parameters = ns['records']('parameters', 'Iii')
for index in sorted({item['index'] for item in methods if item['index'] is not None} | {30778, 247881, 241156}):
    row = ns['methods'][index]
    off = ns['header']['methods'][0] + index * 32
    span('metadata', off, ns['meta'][off:off + 32])
    method_metadata.append({'index': index,
        'name': ns['type_def_name'](row[1]) + '::' + ns['string'](row[0]),
        'return_type': ns['typename'](row[2]), 'slot': row[8], 'token': hex(row[5]),
        'parameters': [{'name': ns['string'](p[0]), 'type': ns['typename'](p[2])}
                       for p in parameters[row[3]:row[3] + row[9]]]})

proof = {
    'kind': 'file-backed conditional panel finalizer/source identity proof',
    'source_game_dll': str(ns['GAME']), 'source_metadata': str(ns['META']),
    'dll_sha256': expected[0], 'metadata_sha256': expected[1],
    'file_only': True, 'game_dll_executed': False, 'process_memory_read': False,
    'current_hotfix_equivalence_proven': False, 'actual_inventory_or_game_value_proven': False,
    'protected_encode_decode_roundtrip_proven': False,
    'methods': methods, 'unique_selected_instructions': len(seen_instructions),
    'byte_span_count': len(spans), 'byte_spans': spans,
    'fresh_original_byte_guards_passed': True,
    'fresh_counts_include_rechecks_of_existing_candidate_spans': True,
    'new_whole_method_mechanism_credit_claimed': False,
    'layouts': layouts, 'runtime_type_literals': literals,
    'method_metadata': method_metadata,
    'mscorlib_selected_method_mapping': selected_map,
    'mscorlib_code_generation_module': map_receipt['codegen_module'],
    'metadata_layout_reader_sha256': sha(reader.read_bytes()),
    'upstream_layout_source': {
        name: sha((ROOT / '.cache/research/p2-native-current-263/upstream-source' / name).read_bytes())
        for name in ('Metadata.cs', 'MetadataClass.cs')
    },
    'facts': {
        'read_null_returns_single_zero': True,
        'fp_writer_asfloat_before_field_null_guard': True,
        'manager_formula': '(raw + ADD) * (ONE + MULT) * FS',
        'manager_multiplier_max_zero_proven': False,
        'ordinary_recompute_formula_reused_from_273': '((raw+ADD)*max(0,ONE+MULT)+FINALADD)*FS',
        'writer_return_type': 'System.Boolean', 'manager_return_type': 'System.Void',
        'manager_tests_writer_boolean': False,
        'range_meta_null_skips_before_fieldinfo_null_guard': True,
        'primitive_int32_selector_boxes_rounded_double': True,
        'five_primary_fields_use_primitive_int32_route': False,
        'normal_reflection_setvalue_proves_later_decoder_value': False,
        'metadata_default_upper_raw': 9223372036854775806,
        'signed64_input_domain_upper_raw': 9223372036854775807,
        'fp_maxvalue_is_not_uppercase_width_max_value': True,
    },
}
target = PACKET / 'source-proof.json'
if target.exists() and not (BASE / 'source-proof-initial-283.json').exists():
    shutil.copyfile(target, BASE / 'source-proof-initial-283.json')
(PACKET / 'source-proof.json').write_text(json.dumps(proof, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
for src, dst in (
    (BASE / 'common-panel-field-attributes-283.json', PACKET / 'field-custom-attributes.json'),
    (BASE / 'routing-metadata-283.json', PACKET / 'routing-metadata.json'),
    (BASE / 'ROUTING_CORRECTION.md', PACKET / 'preparation-correction.md'),
    (BASE / 'SCHEMA.md', PACKET / 'SCHEMA.md'),
):
    shutil.copyfile(src, dst)
print(json.dumps({'methods': len(methods), 'unique_instructions': len(seen_instructions),
                  'spans': len(spans), 'proof_sha256': sha((PACKET / 'source-proof.json').read_bytes())}))
