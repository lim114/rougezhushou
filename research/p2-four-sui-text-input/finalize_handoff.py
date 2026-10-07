"""Seal only public artifacts; large external packages are never archive inputs."""
import hashlib
import json
from pathlib import Path
import shutil

ROOT=Path(__file__).resolve().parent
AUDIT=ROOT.parent/'p2-boolean-option-audit-062'
BASE=ROOT/'baseline060'
DRAFT=ROOT/'draft062'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def write(name,value):
    (ROOT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
freeze=json.loads((ROOT/'freeze-receipt060.json').read_text())
drift=[rel for rel,digest in freeze['files'].items()
       if not (BASE/rel).is_file() or sha(BASE/rel)!=digest]
assert not drift,drift
write('baseline-integrity.json',{'baseline_head':freeze['baseline_head'],
    'files_checked':len(freeze['files']),'baseline_intact':True,'source_drift':drift})
prior=ROOT/'prior-readonly-audit'
prior.mkdir(exist_ok=True)
for file in AUDIT.iterdir():
    if file.is_file():shutil.copyfile(file,prior/file.name)
source=json.loads((AUDIT/'source-receipt.json').read_text())
source['section']=62
source['draft_baseline_head']=freeze['baseline_head']
source['scope']='Qualified Shu Four-Sui raw text input rejection only'
source['prior_readonly_audit_implemented_policy']=source.pop('implemented_policy',False)
source['external_draft_implemented_policy']='Qualified Four-Sui raw str rejection only; no tracked integration'
source['changed_policy']={
    'operator':'char_2025_shu','actual_query_seam':'Combat.apply_self_talents',
    'talent_qualification':'Existing selected_talents yields 天有四时 from the pinned PHASE_2 / level1 candidate.',
    'rejected_type':'raw str only; no parsing/trimming/normalization',
    'unchanged_types':'bool, numeric0/1/null and every other previous nonstr outcome',
    'unchanged_inactive':'Other owners, ineligible Shu E0/E1 and prior validation errors',
    'exact_error_literal':freeze['declared_error_literal'],
    'global_bool_helper':False,'fragile_fixed_in_this_section':False}
source['supports'].append('Qualification uses the same named selected talent that supplies the existing Four-Sui parameters; the gate does not use a guessed report/reference flag.')
source['does_not_support'].append('Declaring older numeric0/1/null or container compatibility to be a new documented global API domain.')
for name,record in source['sources'].items():
    assert sha(Path(record['path']))==record['sha256'],name
    record['fresh_hash_check_for_final_draft']=True
write('source-receipt062.json',source)
comparison=json.loads((ROOT/'matrix-comparison.json').read_text())
new=json.loads((ROOT/'draft-new-tests.json').read_text())
red=json.loads((ROOT/'baseline-new-tests.json').read_text())
assert new['passed'] and new['tests_run']==7
related=(ROOT/'related-tests.log').read_text()
combined=(ROOT/'combined-61-62-tests.log').read_text()
assert 'Ran 71 tests' in related and related.rstrip().endswith('OK')
assert 'Ran 39 tests' in combined and combined.rstrip().endswith('OK')
write('test-receipt.json',{'passed':True,'new_tests':new,'related':{
    'tests_run':71,'failures':0,'errors':0,'skipped':0,'console_sha256':sha(ROOT/'related-tests.log')},
    'baseline_new_tests_expected_failures':red,
    'paired_complete_outputs':comparison['public_pairs'],
    'paired_public_calls':comparison['public_calls_both_packages'],
    'qualified_texts_to_exact_errors':comparison['qualified_text_changed_to_explicit_errors'],
    'unchanged_whole_JSON_or_errors':comparison['unchanged_complete_JSON_or_errors'],
    'no_reference_flag_error_oracle':True,'Wine_GUI_native_windows_executed':False})
write('integration-61-62.json',{'base_head':freeze['baseline_head'],
    'external_package':'combined061062','section61_patch_sha256':sha(ROOT.parent/'p2-integer-option-audit-061/section61.patch'),
    'section62_patch_sha256':sha(ROOT/'section62.patch'),
    'section61_apply_check_and_apply_passed':True,
    'combined_engine_sha256':sha(ROOT/'combined061062/rouge/operator_engine.py'),
    'combined_public_tests_run':39,'failures':0,'errors':0,'skipped':0,
    'tracked_repo_changed_by_agent':False,'fresh_root_integration_still_required':True})
write('handoff-receipt.json',{'section':62,'baseline_head':freeze['baseline_head'],
    'patch_path':'section62.patch','patch_sha256':sha(ROOT/'section62.patch'),
    'patch_bytes':(ROOT/'section62.patch').stat().st_size,
    'patch_files':['rouge/operator_engine.py','tests/test_four_sui_text_input.py'],
    'source_added_lines':2,'new_tests':7,'related_tests':71,
    'public_pairs':comparison['public_pairs'],'public_calls':comparison['public_calls_both_packages'],
    'qualified_text_to_errors':comparison['qualified_text_changed_to_explicit_errors'],
    'unchanged_whole_outputs_or_old_errors':comparison['unchanged_complete_JSON_or_errors'],
    'baseline_intact':True,'tracked_changes':False,
    'selected_runner_registration_required':'tests.test_four_sui_text_input',
    'section61_external_compatibility':True,'independent_review':'pending',
    'full_and_actual_ui_validation':'Root current branch integration and batch checks required; no native claim.'})
print(json.dumps({'patch_sha256':sha(ROOT/'section62.patch'),'baseline_checked_files':len(freeze['files']),
                  'public_pairs':comparison['public_pairs'],'new_tests':new['tests_run']},ensure_ascii=False))
