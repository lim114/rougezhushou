import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).parent
before = json.loads((ROOT / 'baseline-matrix.json').read_text())
after = json.loads((ROOT / 'draft-matrix.json').read_text())
assert len(before['records']) == len(after['records']) == 1876
changed = []
unchanged = []
groups = {}
for original, revised in zip(before['records'], after['records']):
    assert original['scenario'] == revised['scenario'] and original['kind'] == revised['kind']
    groups[original['kind']] = groups.get(original['kind'], 0) + 1
    if original['kind'] == 'active_bool':
        assert original['accepted'] and not revised['accepted']
        assert original['outcome_sha256'] == original['integer_control_sha256']
        assert revised['integer_control_sha256'] == original['integer_control_sha256']
        assert revised['omitted_control_sha256'] == original['omitted_control_sha256']
        assert revised['outcome']['error_type'] == 'ValueError'
        changed.append(revised['scenario'])
    else:
        assert original == revised
        unchanged.append(original['outcome_sha256'])
assert len(changed) == 16
receipt = {'case_pairs': len(before['records']), 'changed_only_active_raw_bool': len(changed),
           'unchanged_full_outcomes': len(unchanged), 'kind_counts': groups,
           'public_calls_per_package': before['total_public_calls'],
           'matrix_public_calls_baseline_plus_draft': before['total_public_calls'] + after['total_public_calls'],
           'shared_unchanged_outcome_hashes_sha256': hashlib.sha256(json.dumps(unchanged).encode()).hexdigest(),
           'new_native_rule': False, 'caller_inputs_and_catalog_unchanged': True,
           'changed_scenarios': changed}
(ROOT / 'matrix-comparison.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({key: value for key, value in receipt.items() if key != 'changed_scenarios'}))
