"""Read saved bytes and named source; no product imports, recomputation, or texts."""
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

def sha(value):
    return hashlib.sha256(value).hexdigest()

def typed(value):
    if type(value) is dict:
        return {'type': 'dict', 'items': [[typed(k), typed(v)] for k, v in value.items()]}
    if type(value) in (list, tuple):
        return {'type': type(value).__name__, 'items': [typed(v) for v in value]}
    assert type(value) in (str, int, float, bool, type(None))
    return {'type': 'float', 'hex': value.hex()} if type(value) is float else {'type': type(value).__name__, 'value': value}

def write(filename, value):
    (HERE / filename).write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n')

failure_path = BASE / 'api-ui090-section088-new8-failure.json.gz'
failure_bytes = failure_path.read_bytes()
failure = json.loads(gzip.decompress(failure_bytes))
assert failure['actual_root089_commit'] == COMMIT
assert failure['error_type'] == 'AssertionError' and failure['error'] == 'timing'
assert len(failure['saved_records']) == 3
assert failure['source_hashes_before'] == failure['source_hashes_after']
proof_path = BASE / 'actual-root089-ui090-source-proof.json'
proof_bytes = proof_path.read_bytes()
proof = json.loads(proof_bytes)
assert proof['actual_root089_commit'] == COMMIT
assert proof['public_source_sha256'] == failure['source_hashes_before']
assert len(failure['source_hashes_before']) == 126
plan_path = BASE / 'original-approved-additional8-input-plan090.json'
plan_bytes = plan_path.read_bytes()
assert sha(plan_bytes) == '31beb7f95a256172591226127562324be6625317fd1ad406baa84851130dd521'
plan = json.loads(plan_bytes)
assert len(plan['cases']) == 8

source_rows = []
source_texts = {}
for name in ('operator_engine', 'timing'):
    relative = 'rouge/' + name + '.py'
    blob = subprocess.check_output(['git', 'show', COMMIT + ':' + relative], cwd='/workspace/rougezhushou')
    assert sha(blob) == proof['public_source_sha256'][relative]
    ast.parse(blob)
    (HERE / ('actual089-' + name + '.py')).write_bytes(blob)
    source_texts[name] = blob.decode()
    source_rows.append({'git_commit': COMMIT, 'path': relative, 'bytes': len(blob), 'sha256': sha(blob)})

engine = source_texts['operator_engine']
assert "resume=max((s.get('resume_frame',0) for s in full['timing']['streams']),default=0)" in engine
assert "self.s['timing']={**self.s.get('timing',{}),'_resume_frames':resume}" in engine
tree = ast.parse(source_texts['timing'])
timeline = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'AttackTimeline')
attacks = next(n for n in timeline.body if isinstance(n, ast.FunctionDef) and n.name == 'attacks')
continuous = next(n for n in attacks.body if isinstance(n, ast.If)
                  and ast.unparse(n.test) == "self.mode == 'continuous'")
stream_assignment = next(n for n in continuous.body if isinstance(n, ast.Assign)
                         and isinstance(n.targets[0], ast.Name) and n.targets[0].id == 'stream')
stream_keys = [k.value for k in stream_assignment.value.keys]
assert 'resume_frame' in stream_keys
append_gate = next(n for n in continuous.body if isinstance(n, ast.If)
                   and isinstance(n.test, ast.Name) and n.test.id == 'deployment_speed'
                   and any(isinstance(v, ast.Call) and ast.unparse(v.func) == 'self.streams.append'
                           for v in ast.walk(n)))
assert not append_gate.orelse
assert isinstance(continuous.body[-1], ast.Return)
assert ast.unparse(continuous.body[-1].value) == 'stream'
outside_gate_calls = [v for n in continuous.body if n is not append_gate
                      for v in ast.walk(n) if isinstance(v, ast.Call)
                      and ast.unparse(v.func) == 'self.streams.append']
assert outside_gate_calls == []

def expected_prepared_requested_fields(case):
    """Only these exact frozen8 inputs; compare entire expected timing, never drop keys."""
    expected = deepcopy(case['input'])
    pair = case['pair_id']
    if pair == '088-native-checkbox-mechanist-S1':
        assert expected['operator'] == 'mechanist' and expected['timing_mode'] == 'frames'
        assert 'timing' not in expected
    elif pair in ('088-hidden-checkbox-amiya-E2-S1-bounded-reference',
                  '088-hidden-checkbox-amiya-E0-S1-empty-target-reference'):
        assert expected['operator'] == 'char_002_amiya' and expected['skill'] == 1
        assert expected['timing_mode'] == 'continuous'
        assert expected['relic_ids'] == [] and type(expected['timing']) is dict
        if expected['elite'] == 2:
            assert typed(expected['timing']) == typed({'target_disappears_seconds': 5.75})
        else:
            assert expected['elite'] == 0
            assert typed(expected['timing']) == typed({'target_windows': []})
        expected['timing'] = {**expected['timing'], '_resume_frames': 0}
    elif pair == '088-hidden-checkbox-chen3-S3-active-warrior67':
        assert expected['operator'] == 'char_1050_chen3' and expected['skill'] == 3
        assert expected['timing_mode'] == 'continuous'
        assert expected['relic_ids'] == ['rogue_6_relic_legacy_67']
        assert 'timing' not in expected
        expected['timing'] = {'_resume_frames': 0}
    else:
        raise AssertionError('No widening beyond fixed eight-input plan')
    return expected

expected_rows = []
for sequence, case in enumerate(plan['cases'], 1):
    expected = expected_prepared_requested_fields(case)
    expected_rows.append({'sequence': sequence, 'pair_id': case['pair_id'],
                         'widget_checked': case['widget_checked'],
                         'expected_timing_present': 'timing' in expected,
                         'expected_timing': expected['timing'] if 'timing' in expected else None,
                         'remaining_unique_API_request': sequence > 3})

records_proof = []
for index, record in enumerate(failure['saved_records']):
    case = plan['cases'][index]
    assert record['sequence'] == index + 1
    assert record['pair_id'] == case['pair_id']
    assert record['widget_checked'] is case['widget_checked']
    assert typed(record['input']) == typed(case['input'])
    assert record['caller_native_before'] == record['caller_native_after'] == typed(case['input'])
    assert typed(record['result']) == record['result_native']
    assert len(record['same_call_processed_report_scenarios']) == 1
    prepared = record['same_call_processed_report_scenarios'][0]
    assert typed(prepared['scenario']) == prepared['scenario_native']
    expected = expected_prepared_requested_fields(case)
    for key in expected:
        assert typed(prepared['scenario'][key]) == typed(expected[key]), key
    for name, report in record['reports'].items():
        assert type(report) is str
        assert sha(report.encode()) == record['reports_sha256'][name]
    assert record['reports']['estimate'] == record['reports']['default']
    result = record['result']
    assert result['report']['schema_version'] == 2
    assert result['report']['operator']['id'] == case['input']['operator']
    assert result['report']['skill_number'] == 1
    skill = result['estimate']['skill']
    if index < 2:
        assert 'total_healing' not in result
        assert skill['total_healing'] == 0 and skill['window_healing'] == 0
        for key in ('initial_seconds', 'recharge_seconds', 'cycle_seconds'):
            if index == 0:
                assert skill[key] is None
            else:
                assert type(skill[key]) is float and math.isfinite(skill[key]) and skill[key] > 0
    else:
        ref = result['amiya_continuous_reference']
        assert ref['attack_sp_per_attack_parameter'] == 2
        assert ref['attack_sp_enabled_in_reference'] is False
        assert ref['enemy_source_excluded'] is False
        assert ref['declared_target_lifetime_seconds'] == 5.75
        assert ref['declared_target_windows_seconds'] is None
        assert ref['native_clock_binding_verified'] is False
        for key in ('actual_acquisition_times_seconds', 'actual_impact_times_seconds',
                    'actual_recharge_seconds', 'actual_cycle_seconds'):
            assert ref[key] is None
        for key in ('recharge_seconds', 'cycle_seconds', 'cycle_damage', 'cycle_dps', 'cycle_healing', 'cycle_hps'):
            assert skill[key] is None
        assert result['total_damage'] is None
        assert result['timing']['phase_clock_unbound'] is True
        assert result['timing']['resource_and_damage_shared_clock'] is False
        assert result['complete'] is False and result['estimate']['complete'] is False
    records_proof.append({'sequence': index + 1, 'pair_id': record['pair_id'],
        'whole_public_result_native_sha256': sha(json.dumps(record['result_native'], separators=(',', ':'), ensure_ascii=False).encode()),
        'caller_unchanged': True, 'same_call_prepared_requested_fields_strict': True,
        'complete_result_native_and_all_three_report_hashes_verified': True})

assert failure['current_case'] == plan['cases'][2]
assert typed(failure['current_result']) == failure['current_result_native']
assert typed(failure['current_result']) == typed(failure['saved_records'][2]['result'])
ledger = failure['ledger']
assert ledger['actual_public_calculation_requests'] == ledger['unique_requested_calculation_inputs'] == 3
assert ledger['formatter_text_requests'] == 9 and ledger['formatter_actual_entries'] == 12
write('expected-prepared-timing8.json', {'status': 'EXACT_FROZEN_INPUT_PLAN_PRODUCER_BOUNDARY', 'rows': expected_rows})
write('receipt.json', {
    'status': 'SAVED3_NARROW_PREPARED_TIMING_CONTRACT_PASS_READY_TO_RESUME_REMAINING5',
    'failure_archive': {'path': str(failure_path), 'sha256': sha(failure_bytes), 'bytes': len(failure_bytes)},
    'source_proof': {'path': str(proof_path), 'sha256': sha(proof_bytes)},
    'actual_named_commit': COMMIT, 'source_blobs': source_rows,
    'plan_sha256': sha(plan_bytes), 'saved_records_verified': 3,
    'source126_before_after_same_and_equal_transport_proof': True,
    'parent_execution_ledger': ledger,
    'classification': 'harness requested-timing identity assertion omitted actual private producer addition; no product failure observed',
    'exact_producer': 'operator_engine1468 reads full timing streams;1469 adds _resume_frames to original timing dict',
    'continuous_source_correction': 'continuous returned stream HAS resume_frame; it is appended to self.streams only with deployment_attack_speed. These fixed inputs have no such rule, so full timing streams is empty and max default gives integer0',
    'normalizer_boundary': 'only fixed plan8; preserve all caller timing keys plus sole integer _resume_frames0; compare whole typed dict, no ignored unknown keys or fallback on missing required Amiya timing',
    'normalizer_producer_expectations_for_unexecuted_inputs': 'source-derived, not an API or GUI result',
    'remaining_unique_API_requests': 5, 'reexecute_completed3': False,
    'strict_readback': records_proof,
    'previous_sealed_contract11_unchanged': True,
    'new_calls_by_reviewer': {'API': 0, 'product_helper': 0, 'formatter': 0, 'RunState_constructor_apply': 0, 'Qt': 0, 'Wine': 0, 'tests': 0},
    'gui_executed': False, 'wine_executed': False,
})
print('PASS: all three saved records/native outputs/reports; exact named continuous-stream append gate; original timing plus sole integer _resume_frames0; 0 product calls.')
