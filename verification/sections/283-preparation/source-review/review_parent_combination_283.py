"""Limited independent 536875 composition review; not the author/full QA suite."""
from copy import deepcopy
from pathlib import Path
import hashlib
import importlib.util
import json
import shutil
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PREP = ROOT / '.cache/section283-preparation'
CORE = PREP / 'rouge/panel_native_finalization.py'
CORE_SHA = '536875942fe6222f7ab3d995fffc4d2ae31f043a6f67e3616cc5c39a1cd68190'
OUT = HERE / 'limited-parent-review-283.json'
assert not OUT.exists()
assert hashlib.sha256(CORE.read_bytes()).hexdigest() == CORE_SHA
SNAPSHOT = HERE / 'core-reviewed-53687594.py'
assert not SNAPSHOT.exists()
SNAPSHOT.write_bytes(CORE.read_bytes())
sys.path.insert(0, str(ROOT))
import rouge
rouge.__path__.insert(0, str(PREP / 'rouge'))
spec = importlib.util.spec_from_file_location('rouge._independent_parent_283', CORE)
core = importlib.util.module_from_spec(spec)
spec.loader.exec_module(core)
assert core.source_data() is not None
Q = 4294967296
MAX = 9223372036854775807
checks, probes = [], []


def check(name, ok):
    checks.append({'name': name, 'passed': bool(ok)})


def run(name, fn, payload):
    original = deepcopy(payload)
    result = fn(payload)
    probes.append({'name': name, 'input': original, 'actual_output': deepcopy(result)})
    check(name + '/input_unchanged', payload == original)
    return result


def field(field='attack', phase='normal', raw=100 * Q, **kw):
    row = {'id': phase + '-' + field, 'field': field, 'phase': phase, 'model_value': None,
           'basis_kind': 'nominal_fp', 'basis_single_bits': None, 'basis_fp_raw': raw,
           'addition_raw': 0, 'multiplier_delta_raw': 0,
           'final_addition_raw': 0, 'final_scaler_raw': Q}
    row.update(kw)
    return row


def read(**kw):
    row = {'value_exists': True, 'object_type_normal': True, 'int_type_normal': True,
           'int_assignable': {'normal': True, 'value': True}, 'float_type_normal': True,
           'float_assignable': {'normal': True, 'value': False}, 'unbox_normal': True,
           'decode_normal': True, 'int_to_single_normal': True, 'decoded_int32': 123,
           'decoded_single_bits': None, 'fallback_normal': True, 'fallback_bits': None}
    row.update(kw)
    return row


def writer(kind='ObscuredInt', raw=3 * Q // 2, **kw):
    row = {'fp_raw': raw, 'field_exists': True, 'as_float_normal': True,
           'field_type_read': {'normal': True, 'value': kind}, 'type_route_normal': True,
           'round_normal': True, 'encode_normal': True, 'copy_normal': True,
           'box_normal': True, 'set_value_normal': True}
    row.update(kw)
    return row


def iteration(identity='first'):
    w = writer()
    del w['fp_raw']; del w['field_exists']
    return {'id': identity,
            'first_meta': {'get_normal': True, 'exists': True, 'item_normal': True,
                           'item_exists': True, 'field_read_normal': True, 'field_exists': True},
            'second_meta': {'get_normal': True, 'exists': True, 'item_normal': True,
                            'item_exists': True, 'range_read_normal': True, 'range_exists': True,
                            'attribute_read_normal': True, 'attribute': 1},
            'reflection_get_normal': True, 'read_field': read(decoded_int32=2),
            'single_to_fp_normal': True,
            'arrays': {name: {'read_normal': True, 'exists': True, 'length': 8,
                              'element_normal': True, 'raw': raw}
                       for name, raw in [('addition', 0), ('multiplier', 0), ('scaler', Q)]},
            'range_read': {'normal': True, 'lower_raw': 0, 'upper_raw': MAX - 1},
            'clamp_normal': True, 'writer': w}


def manager(*rows):
    return {'ordinary_native_path': True,
            'initial_metas': {'get_normal': True, 'exists': True, 'count_normal': True, 'count': len(rows)},
            'iterations': list(rows)}


def stages(result):
    return {r['name']: r for r in result['stages']}


# Same JSON input as the sealed, actual old3e331 counterexample: no schema migration.
old = json.loads((HERE / 'max-range-original-counterexample-283.json').read_bytes())
r = run('same_original_MAX_input_after_repair', core.panel_native_finalization, old['input'])
check('same_MAX_input/source_valid', r['source_valid'] is True)
check('same_MAX_input/new_bound', r['fields'][0]['metadata_range']['upper_raw'] == MAX - 1)
check('same_MAX_input/new_getter', r['fields'][0]['references']['getter_result_raw'] == MAX - 1)
check('same_MAX_input/input_domain_retained', r['fields'][0]['references']['input_fp_raw'] == MAX)

rows = [field(f, raw=MAX) for f in ('hp', 'attack', 'defense', 'attack_speed')]
rows += [field('resistance', raw=101 * Q), field('attack_speed', raw=700 * Q, id='as-700'),
         field('hp', raw=-Q, id='hp-negative'), field('attack_speed', raw=-Q, id='as-negative')]
r = run('five_metadata_ranges_and_no_600_attribute_cap', core.panel_native_finalization, {'fields': rows})
values = [row['references']['getter_result_raw'] for row in r['fields']]
check('five_ranges/gold', values == [MAX-1]*4 + [100*Q, 700*Q, Q, 20*Q])
check('five_ranges/all_actual_unknown', all(row['actual_getter_raw'] is None and row['actual_decoded_value'] is None and row['complete_native_value'] is False for row in r['fields']))
check('five_ranges/whole_unknown', r['complete_native_panel'] is False and r['actual_panel'] is None)

rows = [field(phase=p, raw=2*Q, multiplier_delta_raw=-2*Q, final_scaler_raw=-Q) for p in ('rune', 'normal')]
r = run('rune_three_buckets_vs_ordinary_max_zero', core.panel_native_finalization, {'fields': rows})
check('three_vs_four/rune_gold', r['fields'][0]['references']['clamped_raw'] == 2*Q)
check('three_vs_four/ordinary_gold', r['fields'][1]['references']['getter_result_raw'] == 0)
check('three_vs_four/rune_writer', r['fields'][0]['references']['writer']['encoder_argument_reference'] == 2)
check('three_vs_four/normal_no_writer', r['fields'][1]['references']['writer'] is None)

rows = [field(phase=p, raw=3*Q//2) for p in ('cultivation', 'rune', 'normal', 'skill')]
r = run('four_phases_not_a_protected_roundtrip', core.panel_native_finalization, {'fields': rows})
check('four_phases/cultivation_no_finalizer', r['fields'][0]['references']['writer'] is None and r['fields'][0]['references']['getter_result_raw'] is None)
check('four_phases/rune_half_even', r['fields'][1]['references']['writer']['encoder_argument_reference'] == 2)
check('four_phases/fractional_getters', [row['references']['getter_result_raw'] for row in r['fields'][2:]] == [3*Q//2]*2)

r = run('read_null_normal_zero', core.read_field_reference, read(value_exists=False, int_to_single_normal=False))
check('read_null/normal_zero', r['normal'] is True and r['single_bits_candidates'] == [0])
check('read_null/no_decoder', stages(r)['decode']['called'] is False and stages(r)['int_to_single']['called'] is False)

for normal in (False, None):
    r = run('read_conversion_separate_' + str(normal), core.read_field_reference,
            read(decoded_int32=16777217, int_to_single_normal=normal))
    s = stages(r)
    check('read_conversion/' + str(normal) + '/normal', r['normal'] is normal)
    check('read_conversion/' + str(normal) + '/no_completed_value', r['single_bits_candidates'] == [])
    check('read_conversion/' + str(normal) + '/decoded_past', s['decode']['called'] is True and s['decode']['normal'] is True)
    check('read_conversion/' + str(normal) + '/conditional_bits_retained', s['int_to_single']['reference']['normal_result_bits_candidates'] == [0x4b800000, 0x4b800001])
    check('read_conversion/' + str(normal) + '/known_exclusions', all(s[n]['called'] is False for n in ('float_target_type', 'float_assignability', 'fallback_convert')))

r = run('read_independent_decoded_integer', core.read_field_reference, read(decoded_int32=17))
check('read_independent/value17', r['normal'] is True and r['single_bits_candidates'] == [0x41880000])
check('read_independent/actual_unknown', r['actual_decoded_value'] is None)

r = run('fallback_unknown_preserves_excluded_decode', core.read_field_reference,
        read(int_assignable={'normal': True, 'value': False}, float_assignable={'normal': True, 'value': False}, fallback_normal=None))
s = stages(r)
check('fallback/normal_unknown', r['normal'] is None)
check('fallback/known_excluded', all(s[n]['called'] is False for n in ('unbox_and_copy', 'decode', 'int_to_single')))
check('fallback/call_known', s['fallback_convert']['called'] is True and s['fallback_convert']['normal'] is None)

for normal in (False, None):
    r = run('write_type_routing_normal_' + str(normal), core.write_field_reference,
            writer(type_route_normal=normal))
    s = stages(r)
    check('write_route/' + str(normal) + '/normal', r['normal'] is normal)
    check('write_route/' + str(normal) + '/type_read_past', s['field_type_read']['normal'] is True)
    check('write_route/' + str(normal) + '/future', all(s[n]['called'] is (False if normal is False else None) for n in ('round', 'encode', 'struct_copy', 'box', 'set_value')))

r = run('writer_fp_AsFloat_before_null_field', core.write_field_reference, writer(field_exists=False))
s = stages(r)
check('writer_null/asfloat_past', s['as_float']['called'] is True and s['as_float']['normal'] is True)
check('writer_null/failed_guard', r['normal'] is False and s['field_type_read']['called'] is False)

r = run('primitive_int_selector_boxes_Double', core.write_field_reference, writer('Int32'))
s = stages(r)
check('primitive_int/Double_box', r['normal'] is True and r['boxed_type_reference'] == 'Double')
check('primitive_int/no_protected_encoder', s['encode']['called'] is False and s['struct_copy']['called'] is False and r['stored_prefix'] is None)
check('primitive_int/reflection_called', s['set_value']['called'] is True and r['actual_decoded_value'] is None)

r = run('protected_integer_unknown_argument_but_opaque_normal', core.write_field_reference, writer(raw=None))
check('opaque_unknown/normal', r['normal'] is True and r['return_boolean'] is True)
check('opaque_unknown/20byte_prefix', r['stored_prefix'] == {'kind': 'protected_struct_copy', 'byte_count': 20, 'encoder_argument_reference': None})
check('opaque_unknown/no_fabricated_argument', r['encoder_argument_reference'] is None and r['actual_decoded_value'] is None)

r = run('protected_float24_copy_prefix_survives_setter_throw', core.write_field_reference,
        writer('ObscuredFloat', raw=Q//2, set_value_normal=False))
check('float_copy/24bytes', r['stored_prefix']['byte_count'] == 24 and r['encoder_argument_bits_reference'] == 0x3f000000)
check('float_copy/no_normal_return_or_actual', r['normal'] is False and r['return_boolean'] is None and r['actual_decoded_value'] is None)

row = iteration()
row['first_meta']['field_exists'] = False
row['second_meta']['range_exists'] = False
r = run('manager_null_range_skips_before_field_null', core.manager_flow_reference, manager(row))
first = r['rows'][0]
check('null_range/normal_skip', r['normal'] is True and first['normal'] is True and first['loop_continues_reference'] is True)
check('null_range/no_field_guard', stages(first)['field_null_check']['called'] is False and first['read_reference'] is None)

row = iteration()
row['arrays']['multiplier']['raw'] = -2*Q
row['arrays']['scaler']['raw'] = -Q
row['writer']['field_type_read']['value'] = 'unsupported'
r = run('manager_formula_and_false_writer_continues', core.manager_flow_reference, manager(row, iteration('second')))
first, second = r['rows']
check('manager_formula/no_max_zero', first['arithmetic_reference']['clamped_raw'] == 2*Q)
check('manager_false/Boolean_false_normal', first['writer_reference']['normal'] is True and first['writer_reference']['return_boolean'] is False)
check('manager_false/continues_second', r['normal'] is True and stages(second)['first_metas_get']['called'] is True)

for normal in (False, None):
    row = iteration()
    row['clamp_normal'] = normal
    r = run('manager_clamp_normal_' + str(normal), core.manager_flow_reference, manager(row, iteration('second')))
    first, second = r['rows']
    s = stages(first)
    check('manager_clamp/' + str(normal) + '/normal', r['normal'] is normal)
    check('manager_clamp/' + str(normal) + '/range_and_math_prefix', s['range_get']['normal'] is True and first['arithmetic_reference']['after_scaler_raw'] == 2*Q)
    check('manager_clamp/' + str(normal) + '/no_completed_clamp', first['arithmetic_reference']['clamped_raw'] is None)
    check('manager_clamp/' + str(normal) + '/writer_and_next', s['write_attributes_field']['called'] is (False if normal is False else None) and stages(second)['first_metas_get']['called'] is (False if normal is False else None))

for normal in (False, None):
    row = iteration()
    row['writer']['set_value_normal'] = normal
    r = run('manager_setter_normal_' + str(normal), core.manager_flow_reference, manager(row, iteration('second')))
    first, second = r['rows']
    check('manager_setter/' + str(normal) + '/temporary_copy_retained', first['writer_reference']['stored_prefix']['byte_count'] == 20)
    check('manager_setter/' + str(normal) + '/no_increment', stages(first)['loop_increment']['called'] is (False if normal is False else None))
    check('manager_setter/' + str(normal) + '/next', stages(second)['first_metas_get']['called'] is (False if normal is False else None))

row = iteration()
row['second_meta']['attribute'] = -1
r = run('manager_unsigned_negative_attribute_not_python_index', core.manager_flow_reference, manager(row))
s = stages(r['rows'][0])
check('unsigned_index/rejected_before_element', s['addition_bounds']['normal'] is False and s['addition_bounds']['reference']['unsigned_index'] == 4294967295 and s['addition_element']['called'] is False)

# An independently obtained range can differ from captured first FieldInfo.
row = iteration()
row['second_meta']['attribute'] = 3
row['range_read'] = {'normal': True, 'lower_raw': 10*Q, 'upper_raw': 5*Q}
r = run('manager_second_metadata_independent_reversed_clamp', core.manager_flow_reference, manager(row))
check('independent_range/second_attribute', stages(r['rows'][0])['attribute_read']['reference']['attribute'] == 3)
check('independent_range/reversed_range_lower', r['rows'][0]['arithmetic_reference']['clamped_raw'] == 10*Q)

rejections = []
for name, fn, payload in [
    ('source_injection', core.panel_native_finalization, {'fields': [], 'source_data': {}}),
    ('evaluator_injection', core.panel_native_finalization, {'fields': [], 'evaluator': 'caller'}),
    ('wrong_skill_field', core.panel_native_finalization, {'fields': [field('hp', 'skill')]}),
    ('writer_pointer_rebind', core.manager_flow_reference, manager(iteration())),
]:
    if name == 'writer_pointer_rebind':
        payload['iterations'][0]['writer']['field_exists'] = True
    try:
        fn(payload)
        rejected = False
    except ValueError:
        rejected = True
    rejections.append({'name': name, 'rejected': rejected})
    check('schema/' + name, rejected)

# Clone the complete pinned manifest into this review's own cache; warm then
# alter one clone byte. This touches no shared author or production file.
clone = HERE / 'fresh-guard-clone'
assert not clone.exists()
manifest_path = PREP / core.SOURCE
manifest = json.loads(manifest_path.read_bytes())
for name in list(manifest['files']) + [core.SOURCE, 'rouge/panel_native_finalization.py']:
    target = clone / name
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(PREP / name, target)
spec = importlib.util.spec_from_file_location('rouge._independent_parent_guard_283', clone / 'rouge/panel_native_finalization.py')
guard = importlib.util.module_from_spec(spec); spec.loader.exec_module(guard)
check('clone_guard/warm_valid', guard.source_data() is not None)
clone_dep = clone / 'rouge/panel_native_precision.py'
clone_dep.write_bytes(clone_dep.read_bytes() + b'\n# own-cache source guard tamper\n')
r = run('fresh_guard_after_warmed_dependency', guard.panel_native_finalization, {'fields': [field()]})
check('clone_guard/current_invalid', r['source_valid'] is False)
check('clone_guard/derived_blank', r['fields'][0]['metadata_range'] is None and all(v is None for v in r['fields'][0]['references'].values()))

report = {'kind': 'LIMITED_INDEPENDENT_283_PARENT_COMPOSITION_REVIEW',
          'reviewed_core_sha256': CORE_SHA, 'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
          'source_manifest_sha256': hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
          'source_gate_receipt_sha256': hashlib.sha256((HERE/'source-gates-283.json').read_bytes()).hexdigest(),
          'numeric_review_reused_unchanged': {'core_sha256': '878347f7f5d69d09535f1bf0aec409068c68a3cdcf54812091c7deb96be838fc', 'probes': 36, 'checks': 145},
          'old_counterexample_preserved': 'max-range-original-counterexample-283.json',
          'same_input_not_schema_migration': True,
          'probe_count': len(probes), 'check_count': len(checks), 'failed': [c for c in checks if not c['passed']],
          'checks': checks, 'probes': probes, 'rejections': rejections,
          'new_fresh_native_instruction_spans': 0,
          'scope': 'Only composition and normal/unknown/throw prefixes against independently reviewed source; not full QA, real native calls, current RC, protected decode roundtrip or a Windows UI test.',
          'game_or_chat_operation': False, 'production_or_author_cache_modified': False}
OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf8')
print(json.dumps({'probes': len(probes), 'checks': len(checks), 'failed': report['failed'], 'receipt_sha256': hashlib.sha256(OUT.read_bytes()).hexdigest()}))
raise SystemExit(bool(report['failed']))
