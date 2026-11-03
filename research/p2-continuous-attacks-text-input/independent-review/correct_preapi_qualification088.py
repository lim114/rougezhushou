"""Correct qualification from actual retirement policy before zero fresh calls."""
import gzip
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = Path('/workspace/rougezhushou')
AUTHOR = Path('/workspace/.continuation/p2-continuous-attacks-text-088-draft')
path = ROOT / 'formal-risk-plan088.json'
original = path.read_bytes()
assert hashlib.sha256(original).hexdigest() == 'd854efa8b2e287584b1e9b8c21da42bbc04d85a98e410f786738f766c84869f4'
assert not (ROOT / 'baseline-risks088.jsonl.gz').exists()
assert not (ROOT / 'draft-risks088.jsonl.gz').exists()
(ROOT / 'formal-risk-plan088-original-before-retirement-check.json').write_bytes(original)
plan = json.loads(original)
plan['cases'][0]['label'] = 'retired event reference ignores empty text at zero observation'
plan['cases'][0]['expected'] = 'whole_unchanged'
args = {'operator': 'char_002_amiya', 'skill': 1, 'elite': 0, 'level': 20,
        'skill_rank': 3, 'potential': 2, 'base_attack': 911, 'window_seconds': 0,
        'timing_mode': 'continuous', 'timing': {'target_windows': []},
        'continuous_attacks': 'false'}


def typed(v):
    if isinstance(v, dict):
        return {'type': 'dict', 'items': [[typed(k), typed(x)] for k, x in v.items()]}
    if isinstance(v, (list, tuple)):
        return {'type': type(v).__name__, 'items': [typed(x) for x in v]}
    if isinstance(v, float):
        return {'type': 'float', 'hex': v.hex()}
    return {'type': type(v).__name__, 'value': v}


def fp(v):
    return hashlib.sha256(json.dumps(typed(v), ensure_ascii=False, sort_keys=True,
                                    separators=(',', ':'), allow_nan=False).encode()).hexdigest()


plan['cases'][2] = {'case': 3, 'label': 'E0 Amiya zero observation empty target still has actual reference condition',
                     'expected': 'new_text_error', 'input': args, 'input_typed': typed(args),
                     'native_input_sha256': fp(args)}
source = Path('/workspace/.continuation/p2-section088-candidate-audit/public-source16.jsonl.gz')
source_rows = [json.loads(x) for x in gzip.decompress(source.read_bytes()).splitlines()]
author_plan = json.loads((AUTHOR / 'matrix-plan088.json').read_bytes())
prior = {fp(r['input']) for r in source_rows + author_plan}
assert all(r['native_input_sha256'] not in prior for r in plan['cases'])
assert len({r['native_input_sha256'] for r in plan['cases']}) == 8
saved = [json.loads(x) for x in gzip.decompress((AUTHOR / 'draft-public60.jsonl.gz').read_bytes()).splitlines()]
for index in (18, 19, 20, 21, 40, 41, 42, 43):
    row = saved[index]
    assert row['outcome'] == 'accepted'
    records = row['result']['relic_resolution']['records']
    assert records and all(r['status'] == 'reference_only' and r['applied'] == [] for r in records)
    assert 'sp_events' not in row['result']['estimate']
bindings = []
for rel in ('rouge/offline_scope.py', 'rouge/relics.py'):
    data = (REPO / rel).read_bytes()
    copy = ROOT / 'preapi-bound-current87' / rel
    copy.parent.mkdir(parents=True, exist_ok=True)
    copy.write_bytes(data)
    bindings.append({'source_path': str(REPO / rel), 'copied_path': str(copy),
                     'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()})
receipt = {'format_version': 1, 'status': 'PRE_API_QUALIFICATION_PREPARATION_CORRECTED_FROM_SOURCES',
           'original_plan_sha256': hashlib.sha256(original).hexdigest(), 'source_bindings': bindings,
           'saved_author_receipt_path': str(AUTHOR / 'draft-public60.jsonl.gz'),
           'saved_author_receipt_sha256': hashlib.sha256((AUTHOR / 'draft-public60.jsonl.gz').read_bytes()).hexdigest(),
           'saved_reference_only_rows_verified': [19, 20, 21, 22, 41, 42, 43, 44],
           'original_incorrect_expectation': 'Gummy received-SP rule would enable public native0 event tail.',
           'actual_source': 'offline_scope.REFERENCE_KINDS excludes received_sp/event_sp; relics.prepare partitions them and overwrites _relic_rules with active rules. Public records show reference_only/applied=[] and no event estimate.',
           'correction': 'Case1 now tests reference-only unchanged; case3 is replaced by genuine E0 Amiya reference-condition consumer at empty target/zero observation. Native0 tail remains actual scoped standalone helper test only.',
           'first_get_missing_phase_test_limit': 'Public Gummy has retired rules, so case2 does not itself prove helper early-return reachability. Source/helper tests establish that separate boundary.',
           'preparation_qualification_failures': 1, 'actual_API_or_product_failures': 0,
           'fresh_API_helper_formatter_tests': 0, 'budget_unchanged_8pairs16API': True,
           'all_original_plans_and_frozen_source_preparation_preserved': True}
plan['preapi_qualification_correction'] = {'source_path': str(ROOT / 'preapi-qualification-correction088.json'),
                                         'reason': 'Actual current offline retirement policy, not guessed source attachment.'}
path.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + '\n')
(ROOT / 'preapi-qualification-correction088.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'status': receipt['status'], 'risk_pairs': 8, 'fresh_calls': 0,
                  'corrected_plan_sha256': hashlib.sha256(path.read_bytes()).hexdigest()}))
