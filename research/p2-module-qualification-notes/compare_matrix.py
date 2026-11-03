import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).parent
before = json.loads((ROOT / 'baseline-matrix.json').read_text())
after = json.loads((ROOT / 'draft-matrix.json').read_text())
assert len(before['records']) == len(after['records']) == 1020
changed = eligible = locked = 0
for original, revised in zip(before['records'], after['records']):
    assert original['scenario'] == revised['scenario']
    assert original['without_notes_sha256'] == revised['without_notes_sha256']
    assert original['no_module_full_result_sha256'] == revised['no_module_full_result_sha256']
    assert revised['training_request_preserved']
    if original['eligible_under_existing_gate']:
        eligible += 1
        assert original == revised
    else:
        locked += 1
        assert revised['numeric_result_and_clock_equal_to_no_module']
        assert revised['selected_module_parts'] == 0
        assert not revised['false_applied_claim']
        assert '所选模组未满足当前精英阶段或等级门槛，本次未计模组基础属性与能力覆盖。' in revised['notes']
        assert original['full_result_sha256'] != revised['full_result_sha256']
        changed += 1
assert before['false_applied_claim_cases'] == 18 and after['false_applied_claim_cases'] == 0
shared = [row['without_notes_sha256'] for row in before['records']]
receipt = {
    'calculation_pairs': len(shared),
    'public_calls_per_package': before['full_public_calls'],
    'matrix_public_calls_baseline_plus_draft': before['full_public_calls'] + after['full_public_calls'],
    'all_result_fields_except_notes_identical': True,
    'all_no_module_full_results_identical': True,
    'all_training_requests_preserved': True,
    'eligible_full_results_identical': eligible,
    'locked_results_changed_only_notes': locked,
    'changed_full_results': changed,
    'locked_module_parts_empty': True,
    'false_applied_claim_before': before['false_applied_claim_cases'],
    'false_applied_claim_after': after['false_applied_claim_cases'],
    'shared_non_note_result_hashes_sha256': hashlib.sha256(json.dumps(shared).encode()).hexdigest(),
    'baseline_matrix_sha256': hashlib.sha256((ROOT / 'baseline-matrix.json').read_bytes()).hexdigest(),
    'draft_matrix_sha256': hashlib.sha256((ROOT / 'draft-matrix.json').read_bytes()).hexdigest(),
}
(ROOT / 'matrix-comparison.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(receipt, ensure_ascii=False))
