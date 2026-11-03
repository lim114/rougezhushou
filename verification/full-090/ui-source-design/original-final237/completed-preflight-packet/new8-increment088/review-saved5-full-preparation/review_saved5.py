"""Full frozen-input preparation audit and saved-byte readback; no product code runs."""
import ast
import gzip
import hashlib
import json
import math
import subprocess
from copy import deepcopy
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
COMMIT = '3a59aa0c3d09199caea14de3c5fe89781225a8d6'
PRODUCT_ROOT = Path('/workspace/rougezhushou')

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def typed(value):
    if type(value) is dict:
        return {'type': 'dict', 'items': [[typed(k), typed(v)] for k, v in value.items()]}
    if type(value) in (list, tuple):
        return {'type': type(value).__name__, 'items': [typed(v) for v in value]}
    assert type(value) in (str, int, float, bool, type(None))
    return {'type': 'float', 'hex': value.hex()} if type(value) is float else {'type': type(value).__name__, 'value': value}

def write(name, value):
    (HERE / name).write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n')

proof_path = BASE / 'actual-root089-ui090-source-proof.json'
proof_bytes = proof_path.read_bytes()
proof = json.loads(proof_bytes)
assert proof['actual_root089_commit'] == COMMIT
plan_path = BASE / 'original-approved-additional8-input-plan090.json'
plan_bytes = plan_path.read_bytes()
assert sha(plan_bytes) == '31beb7f95a256172591226127562324be6625317fd1ad406baa84851130dd521'
plan = json.loads(plan_bytes)
assert len(plan['cases']) == 8
failure_path = BASE / 'api-ui090-section088-new8-resume-failure.json.gz'
failure_bytes = failure_path.read_bytes()
failure = json.loads(gzip.decompress(failure_bytes))
assert failure['actual_root089_commit'] == COMMIT
assert failure['error_type'] == 'AssertionError' and failure['error'] == 'relic_ids'
assert failure['source_hashes_before'] == failure['source_hashes_after'] == proof['public_source_sha256']
assert len(failure['source_hashes_before']) == 126
assert len(failure['saved_records']) == 5
ledger = failure['ledger']
assert ledger['actual_public_calculation_requests'] == ledger['unique_requested_calculation_inputs'] == 5
assert ledger['formatter_text_requests'] == 15 and ledger['formatter_actual_entries'] == 20

names = ('damage', 'run_modifiers', 'relics', 'relic_attributes', 'operator_engine', 'estimate',
         'reporting', 'timing', 'condition_inputs', 'catalog', 'offline_scope',
         'charge_reference', 'shield_break_reference', 'summons')
sources = []
texts = {}
trees = {}
mutation_inventory = []
for name in names:
    relative = 'rouge/' + name + '.py'
    raw = subprocess.check_output(['git', 'show', COMMIT + ':' + relative], cwd=PRODUCT_ROOT)
    assert sha(raw) == proof['public_source_sha256'][relative]
    texts[name] = raw.decode()
    trees[name] = ast.parse(raw)
    sources.append({'commit': COMMIT, 'path': relative, 'bytes': len(raw), 'sha256': sha(raw)})
    for node in ast.walk(trees[name]):
        targets = node.targets if isinstance(node, (ast.Assign, ast.Delete)) else [node.target] if isinstance(node, (ast.AugAssign, ast.AnnAssign)) else []
        writes = any(any(isinstance(v, ast.Subscript) and ast.unparse(v.value) in ('scenario', 'self.s')
                         for v in ast.walk(target)) for target in targets)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            writes = writes or (ast.unparse(node.func.value) in ('scenario', 'self.s')
                                and node.func.attr in ('pop', 'update', 'setdefault', 'clear'))
        if writes:
            mutation_inventory.append({'source': relative, 'line': node.lineno, 'statement': ast.unparse(node)})

leaf_sources = []
leaves = {}
for relative in ('rouge/data/relic-mechanics.json', 'rouge/data/catalog.json'):
    raw = subprocess.check_output(['git', 'show', COMMIT + ':' + relative], cwd=PRODUCT_ROOT)
    assert sha(raw) == proof['public_source_sha256'][relative]
    leaves[relative] = json.loads(raw)
    leaf_sources.append({'commit': COMMIT, 'path': relative, 'bytes': len(raw), 'sha256': sha(raw),
                         'snapshot': 'selected-data-leaves.json with exact selectors; whole source recoverable from fixed git blob'})
relic67 = leaves['rouge/data/relic-mechanics.json']['relics']['rogue_6_relic_legacy_67']
profiles = leaves['rouge/data/catalog.json']['operators']
assert len(relic67['effects']) == 1 and relic67['effects'][0]['kind'] == 'attack_sp'
assert relic67['effects'][0]['value'] == 2.0 and relic67['effects'][0]['profession'] == 'warrior'
assert profiles['char_1050_chen3']['profession'] == 'warrior'
assert relic67['pending'] == [] and 'recipient_binding' not in relic67
expected67 = {**relic67['effects'][0], 'value': relic67['effects'][0]['value'],
              'relic_id': 'rogue_6_relic_legacy_67', '_verified_rule': True}
assert "'attack_sp'" not in ast.unparse(next(n.value for n in trees['offline_scope'].body
    if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name) and n.targets[0].id == 'REFERENCE_KINDS'))
assert "(36, 37, 51, 65, 79, 114" in texts['offline_scope']
assert "scenario['relic_ids']=[]" in texts['relics']
assert "scenario['_relic_rules']=rules" in texts['relics']
assert "result['relic_resolution']=resolution" in texts['relics']
assert "scenario.setdefault('base_attack',attributes['attack'])" in texts['damage']
assert "scenario,run_resolution=prepare_run(scenario)" in texts['damage']
assert "scenario,resolution=prepare(scenario,profile)" in texts['damage']
assert "scenario,attributes=prepare_attribute_runes(scenario,attributes)" in texts['damage']
assert "if not deployment_clock:return _evaluate_damage_once(prepared,wine_phase)" in texts['damage']
assert "result['report']=build_report(scenario,result)" in texts['damage']
write('selected-data-leaves.json', {'sources': leaf_sources,
    'selectors': {'relic-mechanics.relics.rogue_6_relic_legacy_67': relic67,
                  'catalog.operators.char_1050_chen3.profession': profiles['char_1050_chen3']['profession'],
                  'catalog.operators.char_002_amiya.talents[0]': profiles['char_002_amiya']['talents'][0]}})

def expected_prepared_requested_fields(case):
    """Exact plan8 only, complete transformed values rather than key filtering."""
    expected = deepcopy(case['input'])
    assert 'base_attack' not in expected and 'run_config' not in expected and 'effects' not in expected
    assert type(expected['continuous_attacks']) is bool
    assert type(expected['window_seconds']) is float and expected['window_seconds'] == 12.75
    requested_relics = expected['relic_ids']
    if case['pair_id'] == '088-native-checkbox-mechanist-S1':
        assert expected['operator'] == 'mechanist' and expected['skill'] == 1
        assert expected['timing_mode'] == 'frames' and requested_relics == []
        assert 'timing' not in expected
    elif case['pair_id'] in ('088-hidden-checkbox-amiya-E2-S1-bounded-reference',
                            '088-hidden-checkbox-amiya-E0-S1-empty-target-reference'):
        assert expected['operator'] == 'char_002_amiya' and expected['skill'] == 1
        assert expected['timing_mode'] == 'continuous' and requested_relics == []
        assert type(expected['timing']) is dict
        if expected['elite'] == 2:
            assert typed(expected['timing']) == typed({'target_disappears_seconds': 5.75})
        else:
            assert expected['elite'] == 0 and typed(expected['timing']) == typed({'target_windows': []})
        expected['timing'] = {**expected['timing'], '_resume_frames': 0}
    elif case['pair_id'] == '088-hidden-checkbox-chen3-S3-active-warrior67':
        assert expected['operator'] == 'char_1050_chen3' and expected['skill'] == 3
        assert expected['timing_mode'] == 'continuous'
        assert requested_relics == ['rogue_6_relic_legacy_67'] and 'timing' not in expected
        expected['timing'] = {'_resume_frames': 0}
    else:
        raise AssertionError('No broad preparation exceptions')
    expected['relic_ids'] = []
    return expected

all_keys = sorted({key for case in plan['cases'] for key in case['input']})
unchanged_keys = [k for k in all_keys if k not in ('timing', 'relic_ids')]
key_matrix = [{'key': key, 'prepared_conversion': 'consume IDs to exact [] and bind selected public resolution' if key == 'relic_ids'
               else 'exact original dict plus sole integer _resume_frames0 for these Amiya S1 continuous inputs' if key == 'timing'
               else 'unchanged value and native type for these fixed inputs',
               'requested_sequences': [n for n, c in enumerate(plan['cases'], 1) if key in c['input']]} for key in all_keys]
expected_rows = []
for n, case in enumerate(plan['cases'], 1):
    expected = expected_prepared_requested_fields(case)
    expected_rows.append({'sequence': n, 'pair_id': case['pair_id'],
                         'expected_transformed_requested_fields': expected,
                         'expected_resolved_rules': [expected67] if case['input']['relic_ids'] else [],
                         'result_verified_from_saved': n <= 5, 'remaining_unique_API_call': n > 5})

extras = {'base_attack', 'effects', '_token_relic_effects', '_relic_rules', '_relic_enemy_effects',
          '_attribute_runes', '_attribute_attack_speed'}
record_receipts = []
for index, record in enumerate(failure['saved_records']):
    case = plan['cases'][index]
    assert record['sequence'] == index + 1 and record['pair_id'] == case['pair_id']
    assert record['widget_checked'] is case['widget_checked']
    assert typed(record['input']) == typed(case['input'])
    assert record['caller_native_before'] == record['caller_native_after'] == typed(case['input'])
    assert typed(record['result']) == record['result_native']
    assert set(record['reports']) == {'estimate', 'default', 'technical'}
    for key in record['reports']:
        assert type(record['reports'][key]) is str
        assert sha(record['reports'][key].encode()) == record['reports_sha256'][key]
    assert record['reports']['estimate'] == record['reports']['default']
    result = record['result']
    assert result['report']['schema_version'] == 2
    assert result['report']['operator']['id'] == case['input']['operator']
    assert result['report']['skill_number'] == case['input']['skill']
    training = {k: case['input'][k] for k in ('elite', 'level', 'trust', 'potential', 'module_id', 'module_level')}
    assert typed(result['estimate']['training']) == typed(training)
    assert len(record['same_call_processed_report_scenarios']) == 1
    observed = record['same_call_processed_report_scenarios'][0]
    scenario = observed['scenario']
    assert typed(scenario) == observed['scenario_native']
    expected = expected_prepared_requested_fields(case)
    for key in expected:
        assert typed(scenario[key]) == typed(expected[key]), key
    wanted_extra = extras | ({'_timeline_offset_seconds', '_first_damage_consumed_in_skill'}
                            if case['input']['operator'] != 'mechanist' else set())
    assert set(scenario) == set(expected) | wanted_extra
    assert type(scenario['base_attack']) in (int, float) and math.isfinite(scenario['base_attack']) and scenario['base_attack'] > 0
    assert scenario['effects'] == scenario['_attribute_runes'] == scenario['_token_relic_effects'] == []
    expected_rules = [expected67] if case['input']['relic_ids'] else []
    assert typed(scenario['_relic_rules']) == typed(expected_rules)
    resolution = result['relic_resolution']
    assert typed(resolution['rules']) == typed(expected_rules)
    assert [r['id'] for r in resolution['records']] == case['input']['relic_ids']
    if expected_rules:
        assert len(resolution['records']) == 1
        rr = resolution['records'][0]
        assert rr['status'] == 'applied' and rr['source'] == relic67['source']
        assert typed(rr['applied']) == typed(expected_rules)
        assert rr['pending'] == rr['missing_conditions'] == rr['reference_effects'] == []
    skill = result['estimate']['skill']
    if case['input']['operator'] == 'mechanist':
        assert 'total_healing' not in result
        assert skill['total_healing'] == skill['window_healing'] == 0
        assert skill['sp_type'] == 'INCREASE_WHEN_ATTACK'
        for key in ('initial_seconds', 'recharge_seconds', 'cycle_seconds'):
            if not case['widget_checked']:
                assert skill[key] is None
            else:
                assert type(skill[key]) is float and math.isfinite(skill[key]) and skill[key] > 0
    elif case['input']['operator'] == 'char_002_amiya':
        ref = result['amiya_continuous_reference']
        assert type(ref['attack_sp_per_attack_parameter']) is float and ref['attack_sp_per_attack_parameter'] == 2.0
        assert ref['attack_sp_enabled_in_reference'] is case['widget_checked']
        assert ref['enemy_source_excluded'] is False and ref['declared_target_lifetime_seconds'] == 5.75
        assert ref['declared_target_windows_seconds'] is None and ref['native_clock_binding_verified'] is False
        for key in ('actual_acquisition_times_seconds', 'actual_impact_times_seconds', 'actual_recharge_seconds', 'actual_cycle_seconds'):
            assert ref[key] is None
        for key in ('recharge_seconds', 'cycle_seconds', 'cycle_damage', 'cycle_dps', 'cycle_healing', 'cycle_hps'):
            assert skill[key] is None
        assert result['total_damage'] is None
        assert result['timing']['phase_clock_unbound'] is True and result['timing']['resource_and_damage_shared_clock'] is False
    else:
        assert type(skill['initial_seconds']) is float and math.isfinite(skill['initial_seconds'])
        wave = result['chen_phase_reference']
        assert wave['kind'] == 'swordwave' and wave['actual_collision_times_seconds'] is None
        assert wave['collision_clock_verified'] is False
    if index >= 3:
        internal = record['same_call_internal_resume_proof']
        assert len(internal) == 1
        rp = internal[0]
        assert rp['full_timing_streams'] == [] and rp['full_timing_streams_native'] == typed([])
        assert type(rp['calculated_internal_resume']) is int and rp['calculated_internal_resume'] == 0
        assert typed(rp['actual_internal_prepared_timing']) == typed(expected['timing'])
        assert rp['actual_rules_include_deployment_attack_speed'] is False
        assert rp['private_reference_arithmetic_not_native_frame_proof'] is True
    record_receipts.append({'sequence': index + 1, 'pair_id': record['pair_id'],
        'requested_field_count': len(case['input']), 'complete_prepared_key_set': sorted(scenario),
        'all_requested_fields_transformed_exactly': True, 'caller_full_native_unchanged': True,
        'public_result_full_native_unchanged': True, 'all_three_text_hashes_verified': True,
        'public_relic_resolution_bound_to_actual_prepared_rules': True,
        'whole_public_native_sha256': sha(json.dumps(record['result_native'], ensure_ascii=False, separators=(',', ':')).encode())})

first_path = BASE / 'api-ui090-section088-new8-failure.json.gz'
first_bytes = first_path.read_bytes()
first = json.loads(gzip.decompress(first_bytes))
assert typed(failure['saved_records'][:3]) == typed(first['saved_records'])
assert typed(failure['current_result']) == failure['current_result_native']
assert typed(failure['current_result']) == typed(failure['saved_records'][4]['result'])
assert failure['current_case'] == plan['cases'][4]
write('full-preparation-contract8.json', {
    'status': 'EXACT_FROZEN8_SOURCE_QUALIFIED_PREPARED_FIELDS', 'input_field_union_count': len(all_keys),
    'all_requested_key_matrix': key_matrix, 'unchanged_requested_keys': unchanged_keys,
    'expected_rows': expected_rows, 'scenario_mutation_source_inventory': mutation_inventory,
    'pipeline': ['calculate_damage→_prepare_damage shallow copy', 'operator_attributes→auto base_attack',
        'prepare_run (no run_config input, no squad/difficulty rules)', 'relics.prepare (consume relic_ids, preserve active rules/resolution)',
        'prepare_attribute_runes (empty attribute effects, only derived fields)', '_evaluate_damage direct (no periodic_sp/deployment_attack_speed)',
        '_evaluate_damage_once→legacy local copy or Combat.calculate', 'finishers→public resolution and result annotations',
        'build_report receives actual processed scenario'],
    'inactive_mutation_paths': [
        'damage285: raw string lifetime numerically0 only; fixed lifetime5.75 float / empty windows do not enter',
        'relics306/309: final_attack_factor/enemy_def_delta rules absent; only67attack_sp or no rules',
        'operator_engine1471: AmiyaS2frames only, while fixed AmiyaS1continuous',
        'damage_base43/49: converts numbers on its own local dict copy; requested window/defense/resistance already floats/rank int',
        'operator_engine115: window→float but fixed12.75 already float; no skill_duration_seconds requested',
        'run_modifiers35: no run_config/squad input; no requested fields modified',
        'condition_inputs: bool returned unchanged; text rejection path is inactive'],
    'added_auto_or_private_fields_excluded_from_manual_input_claim': sorted(extras | {'_timeline_offset_seconds', '_first_damage_consumed_in_skill'}),
    'no_unknown_timing_key_filtering_or_missing_required_key_fallback': True,
    'relic_ids_empty_does_not_mean_effect_absent': True,
})
write('receipt.json', {
    'status': 'SAVED5_COMPLETE_FROZEN_INPUT_PREPARATION_CONTRACT_PASS_PENDING_REMAINING3',
    'actual_named_commit': COMMIT, 'plan_sha256': sha(plan_bytes),
    'failure_archive': {'path': str(failure_path), 'bytes': len(failure_bytes), 'sha256': sha(failure_bytes)},
    'first_failure_archive': {'path': str(first_path), 'sha256': sha(first_bytes), 'first3_saved_records_unchanged': True},
    'source_proof': {'path': str(proof_path), 'sha256': sha(proof_bytes)},
    'readonly_named_source_blob_proof': sources, 'selected_data_blob_proof': leaf_sources,
    'source126_before_after_unchanged_and_equal_transport': True,
    'prepared_identity_problem_failed_attempts': 2,
    'both_failures_one_problem': True,
    'classification': 'harness incorrectly compared caller inputs to downstream consumed/transformed fields; all5 product API/text results saved successfully',
    'next_same_preparation_problem_failure_policy': 'third failure must defer; do not split field names into different issues',
    'parent_execution_ledger': ledger, 'saved_records_completely_read_back': 5,
    'readback_records': record_receipts,
    'remaining_unique_API_requests': 3, 'reexecute_completed5': False,
    'static_expectations_for_unexecuted3_are_not_product_results': True,
    'prior_sealed11_7_3_directories_unchanged': True,
    'reviewer_new_calls': {'API': 0, 'product_helpers': 0, 'formatter': 0, 'RunState_constructor_apply': 0, 'Qt': 0, 'Wine': 0, 'tests': 0},
    'gui_executed': False, 'wine_executed': False,
})
print('PASS: entire frozen8 requested-key preparation pipeline; all5 saved native/caller/texts; exact consumed relicIDs plus active67 rule/resolution; one problem/two attempts; 0 product calls.')
