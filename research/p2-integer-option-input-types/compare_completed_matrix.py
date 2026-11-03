"""Strict comparison of already completed public JSON outcomes; no recalculation."""
import hashlib
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
before = json.loads((OUT / 'baseline-public-results.json').read_text())['complete_public_cases']
after = json.loads((OUT / 'draft-public-results.json').read_text())['complete_public_cases']
assert len(before) == len(after) == 1354
canonical = lambda value: json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))
changed = []
preserved = []
failures = []
for index, (original, actual) in enumerate(zip(before, after)):
    assert canonical(original['scenario']) == canonical(actual['scenario'])
    reject = (original['group'] == 'active_integer'
        and original['identity'] in ('false', 'true')
        and original['field_queried_as_integer'] and original['outcome']['accepted'])
    expected = {'accepted': False, 'error_type': 'ValueError',
                'error': original['field'] + '需要范围内的有限非负整数。'} if reject else original['outcome']
    if canonical(actual['outcome']) != canonical(expected):
        failures.append(index)
    (changed if reject else preserved).append(index)
old = json.loads((OUT / 'matrix-comparison-v1-preparation-failure.json').read_text())
summary = {**old, 'queried_raw_bool_rejections': len(changed),
           'full_outcomes_preserved': len(preserved), 'changed_indices': changed,
           'preserved_indices': preserved, 'failures': failures,
           'whole_outcome_comparison': 'strict canonical complete public JSON, preserving numeric and Boolean serialization',
           'preparation_issue': {'old_runtime_comparison_failures': len(old['failures']),
               'diagnosis': 'Current Python result tuples were compared with saved JSON lists. Stored full draft JSON and baseline JSON show no preserved-outcome change.',
               'correction': 'Canonical complete public JSON comparison; no production code change or repeated calculations.',
               'original_failed_receipt': 'matrix-comparison-v1-preparation-failure.json',
               'resolved': True},
           'completed_public_calls_reused_no_rerun': True,
           'verified_complete_artifacts': {name: hashlib.sha256((OUT / name).read_bytes()).hexdigest()
                                          for name in ('baseline-public-results.json',
                                                       'draft-public-results.json')}}
(OUT / 'matrix-comparison.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({key: summary[key] for key in ('pairs', 'queried_raw_bool_rejections',
                                               'full_outcomes_preserved', 'failures')}))
assert not failures
