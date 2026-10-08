"""Correct public qualification before calls without changing frozen first plan."""
import gzip
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
AUTHOR = Path('/workspace/.continuation/p2-continuous-attacks-text-088-draft')
SOURCE = Path('/workspace/.continuation/p2-section088-candidate-audit')


def typed(v):
    if isinstance(v, dict):
        return {'type': 'dict', 'items': [[typed(k), typed(x)] for k, x in v.items()]}
    if isinstance(v, (list, tuple)):
        return {'type': type(v).__name__, 'items': [typed(x) for x in v]}
    if isinstance(v, float):
        return {'type': 'float', 'hex': v.hex()}
    return {'type': type(v).__name__, 'value': v}


def digest(v):
    return hashlib.sha256(json.dumps(typed(v), ensure_ascii=False, sort_keys=True,
                                    separators=(',', ':'), allow_nan=False).encode()).hexdigest()


old_path = ROOT / 'formal-risk-plan088.json'
assert hashlib.sha256(old_path.read_bytes()).hexdigest() == 'd854efa8b2e287584b1e9b8c21da42bbc04d85a98e410f786738f766c84869f4'
old = json.loads(old_path.read_bytes())
plan = json.loads(old_path.read_bytes())
plan['cases'][0]['label'] = 'retired event rule stays reference-only with zero observation'
plan['cases'][0]['expected'] = 'whole_unchanged'
plan['cases'][1].update(label='actual natural attack-SP source with zero observation', expected='new_text_error',
    input={'operator': 'char_1050_chen3', 'skill': 3, 'elite': 2, 'level': 65,
           'skill_rank': 9, 'base_attack': 911, 'window_seconds': 0,
           'timing_mode': 'frames', 'relic_ids': ['rogue_6_relic_legacy_67'], 'continuous_attacks': 'false'})
plan['cases'][2].update(label='E0 restricted Amiya condition reference with excluded enemy scope', expected='new_text_error',
    input={'operator': 'char_002_amiya', 'skill': 1, 'elite': 0, 'level': 20,
           'skill_rank': 3, 'base_attack': 911, 'window_seconds': .125,
           'timing_mode': 'continuous', 'timing': {'target_windows': []}, 'continuous_attacks': ''})
for row in plan['cases']:
    if row['case'] == 6:
        # The original JSON display loses tuple; keep its frozen native tree exactly.
        continue
    row['input_typed'] = typed(row['input'])
    row['native_input_sha256'] = digest(row['input'])
old_rows = [json.loads(line) for line in gzip.decompress((SOURCE / 'public-source16.jsonl.gz').read_bytes()).splitlines()]
author_rows = json.loads((AUTHOR / 'matrix-plan088.json').read_bytes())
existing = {digest(row['input']) for row in old_rows + author_rows}
assert len({row['native_input_sha256'] for row in plan['cases']}) == 8
assert all(row['native_input_sha256'] not in existing for row in plan['cases'])
plan.update(status='FROZEN_CORRECTED_INDEPENDENT_RISKS_BEFORE_NEW_CALLS',
            current_root_archive_closure_commit='6191cc76ecf2a907493dd8347dcecb7b0d6bc4d0',
            original_plan_sha256=hashlib.sha256(old_path.read_bytes()).hexdigest(),
            qualification_correction='Current offline scope strips received/event SP into reference_only; Gummy public tail not active. Test final eighth method validates internal ready/wait and readyNone helper boundary instead.',
            calls_before_or_during_revision=0,
            current_author_plan_sha256=hashlib.sha256((AUTHOR / 'matrix-plan088.json').read_bytes()).hexdigest())
new_path = ROOT / 'formal-risk-plan-final088.json'
diag_path = ROOT / 'risk-plan-precall-qualification-diagnostics088.json'
assert not new_path.exists() and not diag_path.exists()
new_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + '\n')
diag_path.write_text(json.dumps({
    'format_version': 1, 'status': 'SOURCE_QUALIFICATION_CORRECTED_BEFORE_ANY_PROJECT_CALL',
    'original_plan_path': str(old_path), 'original_plan_sha256': hashlib.sha256(old_path.read_bytes()).hexdigest(),
    'corrected_plan_path': str(new_path), 'corrected_plan_sha256': hashlib.sha256(new_path.read_bytes()).hexdigest(),
    'source': str(AUTHOR / 'EVIDENCE_BOUNDARY.md'),
    'source_sha256': hashlib.sha256((AUTHOR / 'EVIDENCE_BOUNDARY.md').read_bytes()).hexdigest(),
    'original_plan_executed': False, 'project_API_helper_tests_calls': 0,
    'public_event_rules_not_reactivated': True,
    'corrected_case_ids': [1, 2, 3], 'unchanged_native_tuple_case': 6,
    'actual_tail_validation_scope': 'Frozen final eighth test only, standalone scoped helper; no claim of current public event-path reachability.',
    'product_or_numerical_test_failure': False
}, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'status': plan['status'], 'risk_pairs': 8,
                  'plan_sha256': hashlib.sha256(new_path.read_bytes()).hexdigest(), 'new_calls': 0}))
