"""One independent complete saved8 readback, stdlib only, no product imports/calls."""
import gzip
import hashlib
import json
import math
from copy import deepcopy
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
PACKAGE = BASE / 'public-schema-actual-root089'
COMMIT = '3a59aa0c3d09199caea14de3c5fe89781225a8d6'

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def typed(value):
    if type(value) is dict:
        return {'type': 'dict', 'items': [[typed(k), typed(v)] for k, v in value.items()]}
    if type(value) in (list, tuple):
        return {'type': type(value).__name__, 'items': [typed(v) for v in value]}
    assert type(value) in (str, int, float, bool, type(None))
    return {'type': 'float', 'hex': value.hex()} if type(value) is float else {'type': type(value).__name__, 'value': value}

def decode(tree):
    tag = tree['type']
    if tag == 'dict':
        return {decode(k): decode(v) for k, v in tree['items']}
    if tag == 'list':
        return [decode(v) for v in tree['items']]
    if tag == 'tuple':
        return tuple(decode(v) for v in tree['items'])
    if tag == 'float':
        return float.fromhex(tree['hex'])
    assert tag in ('str', 'int', 'bool', 'NoneType')
    value = tree['value']
    assert type(value).__name__ == tag
    return value

def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)

def write(name, value):
    (HERE / name).write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n')

archive = BASE / 'api-ui090-section088-new8.json.gz'
compressed = archive.read_bytes()
assert len(compressed) == 61135
assert sha(compressed) == '39d4b4ac331ce3ddc7bd4745ac1c915f5f18d8fde6bcdf4bc20c314027c2e0bc'
raw = gzip.decompress(compressed)
assert len(raw) == 491521
assert sha(raw) == '6bada344443afbacdb8427543791acbd5056314df0d87b81f0a942976813d8e9'
final = json.loads(raw)
assert final['status'] == 'PASS_ACTUAL_ROOT089_NEW8_PUBLIC_API_NATIVE_JSON_THREE_TEXT_PREFLIGHT_ONLY'
assert final['actual_root089_commit'] == COMMIT
assert final['record_count'] == len(final['records']) == 8
assert final['same_harness_issue_failed_attempts'] == 2
assert final['same_call_trace_not_invented_public_result_scenario'] is True
assert final['old44_1154_4217_source16_author60_reexecuted'] is False
assert final['future_actual_root090_source_freeze_complete'] is False

plan_path = BASE / 'original-approved-additional8-input-plan090.json'
plan_bytes = plan_path.read_bytes()
assert sha(plan_bytes) == final['approved_original_plan_sha256'] == '31beb7f95a256172591226127562324be6625317fd1ad406baa84851130dd521'
plan = json.loads(plan_bytes)
assert len(plan['cases']) == 8
assert len({canonical(c['input']) for c in plan['cases']}) == 8
proof_path = BASE / 'actual-root089-ui090-source-proof.json'
proof_bytes = proof_path.read_bytes()
proof = json.loads(proof_bytes)
assert proof['actual_root089_commit'] == COMMIT
assert final['source_hashes_before'] == final['source_hashes_after'] == proof['public_source_sha256']
assert len(proof['public_source_sha256']) == 126
current_package = {p.relative_to(PACKAGE).as_posix(): sha(p.read_bytes())
                   for p in sorted((PACKAGE / 'rouge').rglob('*'))
                   if p.is_file() and p.suffix in ('.py', '.json')}
assert current_package == proof['public_source_sha256']

prefix_proof = []
for filename, count in [('api-ui090-section088-new8-failure.json.gz', 3),
                        ('api-ui090-section088-new8-resume-failure.json.gz', 5)]:
    path = BASE / filename
    data = path.read_bytes()
    before = json.loads(gzip.decompress(data))
    assert len(before['saved_records']) == count
    assert typed(final['records'][:count]) == typed(before['saved_records'])
    assert canonical(final['records'][:count]) == canonical(before['saved_records'])
    assert before['source_hashes_before'] == before['source_hashes_after'] == proof['public_source_sha256']
    prefix_proof.append({'archive': str(path), 'sha256': sha(data), 'count': count,
                         'whole_native_and_JSON_prefix_exact': True, 'reexecuted': False})

ledger = final['ledger']
assert ledger['actual_public_calculation_requests'] == 8
assert ledger['profile_observed_calculate_damage_function_entries'] == 8
assert ledger['unique_requested_calculation_inputs'] == 8
assert ledger['formatter_text_requests'] == 24 and ledger['formatter_actual_entries'] == 32
assert ledger['formatter_function_entry_counts'] == {'format_estimate': 8, 'format_report_default': 16, 'format_report_technical': 8}
assert ledger['external_production_helper_calls'] == ledger['RunState_constructor_apply_calls'] == ledger['Qt_Wine_tests_network_calls'] == 0
assert [(s['actual_API_calls'], s['explicit_text_requests'], s['actual_formatter_entries'])
        for s in final['execution_segments']] == [(3, 9, 12), (2, 6, 8), (3, 9, 12)]

mechanics = json.loads((PACKAGE / 'rouge/data/relic-mechanics.json').read_bytes())
catalog = json.loads((PACKAGE / 'rouge/data/catalog.json').read_bytes())
relic67 = mechanics['relics']['rogue_6_relic_legacy_67']
assert len(relic67['effects']) == 1
effect67 = relic67['effects'][0]
assert effect67['kind'] == 'attack_sp' and effect67['profession'] == 'warrior' and effect67['value'] == 2.0
assert catalog['operators']['char_1050_chen3']['profession'] == 'warrior'
rule67 = {**effect67, 'value': effect67['value'], 'relic_id': 'rogue_6_relic_legacy_67', '_verified_rule': True}
amiya_talents = catalog['operators']['char_002_amiya']['talents'][0]
qualified = [t for t in amiya_talents if t['phase'] <= 2 and t['potential_rank'] <= 0
             and (t['phase'] < 2 or t['level'] <= 80)]
assert qualified[-1]['name'] == '情绪吸收' and qualified[-1]['values']['amiya_t_1[atk].sp'] == 2.0
e0 = [t for t in amiya_talents if t['phase'] <= 0 and t['potential_rank'] <= 0 and t['level'] <= 50]
assert all(t['name'] != '情绪吸收' for t in e0)

def expected_fields(case):
    fields = deepcopy(case['input'])
    assert type(fields['continuous_attacks']) is bool and fields['continuous_attacks'] is case['widget_checked']
    assert 'base_attack' not in fields and fields['window_seconds'] == 12.75
    assert type(fields['window_seconds']) is float
    if case['pair_id'] == '088-native-checkbox-mechanist-S1':
        assert fields['operator'] == 'mechanist' and fields['skill'] == 1 and fields['timing_mode'] == 'frames'
        assert fields['relic_ids'] == [] and 'timing' not in fields
    elif case['pair_id'] in ('088-hidden-checkbox-amiya-E2-S1-bounded-reference',
                            '088-hidden-checkbox-amiya-E0-S1-empty-target-reference'):
        assert fields['operator'] == 'char_002_amiya' and fields['skill'] == 1 and fields['timing_mode'] == 'continuous'
        assert fields['relic_ids'] == []
        if fields['elite'] == 2:
            assert typed(fields['timing']) == typed({'target_disappears_seconds': 5.75})
        else:
            assert fields['elite'] == 0 and typed(fields['timing']) == typed({'target_windows': []})
        fields['timing'] = {**fields['timing'], '_resume_frames': 0}
    else:
        assert case['pair_id'] == '088-hidden-checkbox-chen3-S3-active-warrior67'
        assert fields['operator'] == 'char_1050_chen3' and fields['skill'] == 3 and fields['timing_mode'] == 'continuous'
        assert fields['relic_ids'] == ['rogue_6_relic_legacy_67'] and 'timing' not in fields
        fields['timing'] = {'_resume_frames': 0}
    fields['relic_ids'] = []
    return fields

extras = {'base_attack', 'effects', '_token_relic_effects', '_relic_rules', '_relic_enemy_effects',
          '_attribute_runes', '_attribute_attack_speed'}
rows = []
pairs = {}
text_count = 0
for index, (case, record) in enumerate(zip(plan['cases'], final['records']), 1):
    assert record['sequence'] == index and record['pair_id'] == case['pair_id']
    assert record['widget_checked'] is case['widget_checked']
    assert typed(record['input']) == typed(case['input'])
    assert record['caller_native_before'] == record['caller_native_after'] == typed(case['input'])
    result = record['result']
    native_result = decode(record['result_native'])
    assert typed(result) == record['result_native'] == typed(native_result)
    assert canonical(result) == canonical(native_result)
    assert set(record['reports']) == {'estimate', 'default', 'technical'}
    for name, report in record['reports'].items():
        assert type(report) is str and sha(report.encode()) == record['reports_sha256'][name]
        text_count += 1
    assert record['reports']['estimate'] == record['reports']['default']
    report = result['report']
    assert report['schema_version'] == 2 and report['operator']['id'] == case['input']['operator']
    assert report['skill_number'] == case['input']['skill']
    skill = result['estimate']['skill']
    training = {k: case['input'][k] for k in ('elite', 'level', 'trust', 'potential', 'module_id', 'module_level')}
    assert typed(result['estimate']['training']) == typed(training)
    assert len(record['same_call_processed_report_scenarios']) == 1
    obs = record['same_call_processed_report_scenarios'][0]
    scenario = obs['scenario']
    assert typed(scenario) == obs['scenario_native']
    expected = expected_fields(case)
    for key in expected:
        assert typed(scenario[key]) == typed(expected[key]), key
    wanted_extra = extras | ({'_timeline_offset_seconds', '_first_damage_consumed_in_skill'}
                            if case['input']['operator'] != 'mechanist' else set())
    assert set(scenario) == set(expected) | wanted_extra
    assert scenario['effects'] == scenario['_attribute_runes'] == scenario['_token_relic_effects'] == []
    rules = [rule67] if case['input']['relic_ids'] else []
    resolution = result['relic_resolution']
    assert typed(scenario['_relic_rules']) == typed(resolution['rules']) == typed(rules)
    assert [r['id'] for r in resolution['records']] == case['input']['relic_ids']
    if rules:
        assert len(resolution['records']) == 1
        rr = resolution['records'][0]
        assert rr['status'] == 'applied' and rr['source'] == relic67['source']
        assert typed(rr['applied']) == typed(rules)
        assert rr['pending'] == rr['missing_conditions'] == rr['reference_effects'] == []
    operator = case['input']['operator']
    boundaries = {}
    if operator == 'mechanist':
        assert 'total_healing' not in result
        assert skill['total_healing'] == skill['window_healing'] == 0
        assert skill['sp_type'] == 'INCREASE_WHEN_ATTACK'
        for key in ('initial_seconds', 'recharge_seconds', 'cycle_seconds'):
            if case['widget_checked']:
                assert type(skill[key]) is float and math.isfinite(skill[key]) and skill[key] > 0
            else:
                assert skill[key] is None
        boundaries = {'initial_recharge_cycle': {k: skill[k] for k in ('initial_seconds', 'recharge_seconds', 'cycle_seconds')},
                      'top_healing_absent': True, 'estimate_total_window_healing_zero': True}
    elif operator == 'char_002_amiya':
        ref = result['amiya_continuous_reference']
        excluded = case['input']['elite'] == 0
        assert ref['operator_id'] == 'char_002_amiya' and ref['skill_number'] == 1
        assert ref['attack_sp_enabled_in_reference'] is case['widget_checked']
        assert ref['enemy_source_excluded'] is excluded
        if excluded:
            assert type(ref['attack_sp_per_attack_parameter']) is int and ref['attack_sp_per_attack_parameter'] == 0
            assert ref['declared_target_windows_seconds'] == [] and ref['declared_target_lifetime_seconds'] is None
            assert type(result['total_damage']) in (int, float) and result['total_damage'] == 0
            assert ref['cast_reference']['enemy_source_excluded'] is True
            assert ref['window_reference']['enemy_source_excluded'] is True
            for component in result['components']:
                if component['damage_type'] not in ('healing', 'regeneration', 'buildup'):
                    assert component['total'] == 0 and component['hits'] == 0 and 'actual_total' not in component
        else:
            assert type(ref['attack_sp_per_attack_parameter']) is float and ref['attack_sp_per_attack_parameter'] == 2.0
            assert ref['declared_target_lifetime_seconds'] == 5.75 and ref['declared_target_windows_seconds'] is None
            assert result['total_damage'] is None
            assert skill['total_damage'] is None and skill['phase_damage'] is None
        assert ref['native_clock_binding_verified'] is False
        for key in ('actual_acquisition_times_seconds', 'actual_impact_times_seconds', 'actual_recharge_seconds', 'actual_cycle_seconds'):
            assert ref[key] is None
        for key in ('recharge_seconds', 'cycle_seconds', 'cycle_damage', 'cycle_dps', 'cycle_healing', 'cycle_hps'):
            assert skill[key] is None
        assert result['timing']['phase_clock_unbound'] is True
        assert result['timing']['resource_and_damage_shared_clock'] is False
        assert result['complete'] is False and result['estimate']['complete'] is False
        boundaries = {'enemy_source_excluded': excluded, 'attack_credit': ref['attack_sp_per_attack_parameter'],
                      'attack_reference_enabled': ref['attack_sp_enabled_in_reference'],
                      'actual_four_None_and_cycle_six_None': True, 'top_damage': result['total_damage'],
                      'own_regeneration_numeric_inference_made': False}
    else:
        assert operator == 'char_1050_chen3'
        assert type(skill['initial_seconds']) is float and math.isfinite(skill['initial_seconds'])
        wave = result['chen_phase_reference']
        assert wave['kind'] == 'swordwave' and wave['actual_collision_times_seconds'] is None
        assert wave['collision_clock_verified'] is False
        boundaries = {'active_warrior67_rule_bound': True, 'initial_seconds': skill['initial_seconds'],
                      'actual_collision_None': True, 'masked_damage_or_cycle_difference_required': False}
    direct_return_trace = False
    if index >= 4:
        internal = record['same_call_internal_resume_proof']
        assert len(internal) == 1
        rp = internal[0]
        assert rp['full_timing_streams'] == [] and rp['full_timing_streams_native'] == typed([])
        assert type(rp['calculated_internal_resume']) is int and rp['calculated_internal_resume'] == 0
        assert typed(rp['actual_internal_prepared_timing']) == typed(expected['timing'])
        assert rp['actual_rules_include_deployment_attack_speed'] is False
        assert rp['private_reference_arithmetic_not_native_frame_proof'] is True
        direct_return_trace = True
    pairs.setdefault(case['pair_id'], []).append(record)
    rows.append({'sequence': index, 'pair_id': case['pair_id'], 'widget_checked': case['widget_checked'],
                 'caller_full_native_unchanged': True, 'result_full_native_and_JSON_projection_exact': True,
                 'all_three_original_text_hashes_verified': True, 'whole_transformed_requested_fields_and_prepared_keyset_exact': True,
                 'public_rules_records_bound_to_actual_prepared_rules_and_requestedIDs': True,
                 'actual_calculate_return_trace_observed': direct_return_trace,
                 'boundaries': boundaries})
assert text_count == 24 and len(pairs) == 4
for pair_id, records in pairs.items():
    assert len(records) == 2 and [r['widget_checked'] for r in records] == [False, True]
    assert records[0]['result_native'] != records[1]['result_native']
    if pair_id == '088-hidden-checkbox-chen3-S3-active-warrior67':
        f, t = [r['result']['estimate']['skill']['initial_seconds'] for r in records]
        assert f > t >= 0

adapter_path = BASE / 'resume_ui090_section088_remaining3.py'
adapter_bytes = adapter_path.read_bytes()
assert sha(adapter_bytes) == '384712959c98d11e456c91f96d91f0d05d1a9d79e0e04224bdc4383b558e4fcf'
ordering_path = BASE / 'remaining3-preassert-checkpoint-ordering-proof090.json'
ordering_bytes = ordering_path.read_bytes()
freeze_path = BASE / 'new8-final3-execution-freeze090.json'
freeze_bytes = freeze_path.read_bytes()
freeze = json.loads(freeze_bytes)
for item in freeze['files']:
    frozen = Path(item['source_path']).read_bytes()
    assert len(frozen) == item['bytes'] and sha(frozen) == item['sha256']

receipt = {
 'status': 'FINAL_SAVED8_STRICT_READBACK_PASS_READY_FOR_ROOT090_ACTUAL_GUI',
 'actual_calculation_source_commit': COMMIT, 'approved_input_plan_sha256': sha(plan_bytes),
 'formal_archive': {'path': str(archive), 'bytes': len(compressed), 'sha256': sha(compressed),
                    'decoded_bytes': len(raw), 'decoded_sha256': sha(raw)},
 'actual_source_proof': {'path': str(proof_path), 'sha256': sha(proof_bytes)},
 'all126_current_package_files_and_saved_before_after_equal_final_transport_proof': True,
 'unique_requested_input_count': 8, 'pair_count': 4, 'saved_text_count': 24,
 'parent_actual_execution_ledger': ledger, 'execution_segments': final['execution_segments'],
 'original_saved_prefixes': prefix_proof, 'same_prepared_identity_problem_failed_attempts': 2,
 'third_failure_policy_not_triggered': True,
 'original_3_and_5_whole_records_neither_mutated_nor_reexecuted': True,
 'record_readback': rows,
 'calculate_return_trace_coverage': {'actual_saved_sequences': [4, 5, 6, 7, 8],
    'sequence3': 'actual processed report timing captured; earlier independent source proof explains private0; no return trace backfilled',
    'legacy_sequences1_2': 'legacy pipeline, no Combat.calculate return trace'},
 'source_data_qualification': {'67_effect': effect67, 'Chen_profession': 'warrior',
    'Amiya_E2P1_selected_talent': qualified[-1], 'Amiya_E0_absent_qualified_emotional_absorption': True},
 'actual_reference_scope': 'unknown actual clocks remain None; empty target excludes only current enemy mathematical source; no own regeneration value or native frame observation inferred',
 'final_adapter': {'path': str(adapter_path), 'sha256': sha(adapter_bytes)},
 'final_adapter_ordering_proof': {'path': str(ordering_path), 'sha256': sha(ordering_bytes)},
 'final_execution_freeze': {'path': str(freeze_path), 'sha256': sha(freeze_bytes), 'all_frozen_files_exact': True},
 'prior_sealed_directories_modified': False,
 'reviewer_new_calls': {'API': 0, 'product_helpers': 0, 'formatter': 0, 'RunState_constructor_apply': 0,
                       'Qt': 0, 'Wine': 0, 'tests': 0, 'passed_checker_reruns': 0},
 'gui_executed': False, 'wine_executed': False,
 'remaining': 'root090 actual source transport and Qt/Wine execution owned by root; reuse saved8, do not recalculate',
}
write('receipt.json', receipt)
(HERE / 'HANDOFF.md').write_text(
    '# Formal saved8 readback\n\n'
    'All 8 distinct saved public results, all caller/native and JSON projections, 24 saved texts, '
    'original whole3/whole5 prefixes, and 126 frozen public-source hashes passed independent readback. '
    'Actual API execution occurred in 3 + 2 + 3 segments, with 24 explicit text requests and 32 formatter entries.\n\n'
    'Requested input fields remain exact after the two qualified preparation conversions: '
    'relic IDs consumed to [], and extended continuous timing gets the sole private integer _resume_frames0. '
    'Active warrior67 effects remain bound to the public resolution. Amiya E2 qualified attack credit2.0, '
    'E0 credit0 and native False/True reference flags, actual clock unknowns, and enemy-only empty-target exclusion passed. '
    'Chen first charge changed; no difference in masked damage or cycle was required.\n\n'
    'Actual calculate-return evidence exists for sequences4–8. Sequence3 has its original report-scenario trace '
    'and independent source qualification; no missing return trace was invented. '
    'Private resume0 is internal reference arithmetic, not native battle frame verification.\n\n'
    'Reviewer executed 0 product APIs/helpers/formatters/RunState/Qt/Wine/tests and reran no passed checker. '
    'Prior sealed directories remain unchanged. Root090 actual source transport and GUI work may reuse these outputs.\n')
print('PASS: formal saved8 full native/JSON/caller, all24 texts, unchanged whole3/5 prefixes, actual rules/reference boundaries, observed5 return traces, frozen126 source hashes; 0 product calls.')
