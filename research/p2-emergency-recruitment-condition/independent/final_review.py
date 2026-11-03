"""Freeze independent conclusions and the reviewed final patch."""
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
AUDIT=Path('/workspace/.continuation/p2-after-055-audit/relic-scope')
DRAFT=AUDIT/'draft'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
freeze=json.loads((AUDIT/'freeze.json').read_text())
draft_creation=json.loads((AUDIT/'draft-creation.json').read_text())
changes=[rel for rel,expected in freeze['public_source_hashes'].items() if sha(DRAFT/rel)!=expected]
assert changes==['rouge/relics.py'],changes
assert sha(DRAFT/'rouge/relics.py')==draft_creation['draft_relics_sha256']
patch=AUDIT/'section58.patch'
assert sha(patch)=='16234cd506a350baed74e6b30adc613baaf5298c3fe1d7bb935fd3bb6606ca39'
patch_text=patch.read_text()
assert patch_text.count('diff --git')==2
assert 'diff --git a/rouge/relics.py b/rouge/relics.py' in patch_text
assert 'diff --git a/tests/test_emergency_recruitment_condition.py b/tests/test_emergency_recruitment_condition.py' in patch_text
source=json.loads((HERE/'source-review.json').read_text())
controls=json.loads((HERE/'control-comparison.json').read_text())
tests=json.loads((HERE/'independent-tests.json').read_text())
assert source['source_review_passed'] and controls['passed'] and tests['successful']
receipt={
    'review_scope':'Final section 58 external frozen public source, patch, new tests, paired full-return controls',
    'reviewed_baseline_head':freeze['baseline_head'],
    'reviewed_patch':str(patch),'reviewed_patch_sha256':sha(patch),'patch_bytes':patch.stat().st_size,
    'draft_production_source_changes':changes,'draft_relics_sha256':sha(DRAFT/'rouge/relics.py'),
    'new_test_sha256':sha(DRAFT/'tests/test_emergency_recruitment_condition.py'),
    'source_closure_passed':True,'source_manifest_files_checked':source['frozen_public_files_checked'],
    'public_paired_cases':controls['public_paired_cases'], 'public_calls_both_packages':controls['public_calls_both_packages'],
    'complete_public_outputs_unchanged':controls['unchanged_complete_public_outputs'],
    'invalid_applicable_cases_equal_existing_pending':controls['invalid_applicable_cases_equal_existing_pending'],
    'python_sentinel_controls_pending':controls['direct_python_controls_pending'],
    'tests_run':tests['tests_run'],'tests_passed':tests['passed'],'historical_skips':len(tests['skipped']),
    'findings':[], 'blockers':[], 'independent_review_passed':True,
    'reviewer_script_preparation_issue':'Source assertion initially used atk_pct/def_pct spellings; actual parsed attack_pct/defense_pct inspected and corrected before receipt success. No source or draft edit.',
    'reviewer_root_tracked_edits':0,'reviewer_draft_edits':0,'private_state_read':False,'game_actions':0,
    'native_attachment_proven':False,'hotfix_equivalence_proven':False,'new_stacking_or_timing_claim':False,
    'remaining_limit':'Root integration after section 57 and any required full Linux/Wine/actual GUI validation are owned by root, outside this frozen HEAD55 draft review.',
    'artifacts':{p.name:sha(p) for p in sorted(HERE.iterdir()) if p.is_file() and p.name not in {'final-review.json','final_review.py'}},
}
(HERE/'final-review.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'passed':True,'patch_sha256':sha(patch),'public_calls':receipt['public_calls_both_packages'],'preserved':receipt['complete_public_outputs_unchanged'],'pending':receipt['invalid_applicable_cases_equal_existing_pending'],'tests_passed':tests['passed'],'historical_skips':len(tests['skipped']),'blockers':[]},ensure_ascii=False))
