from pathlib import Path
import json,hashlib,difflib,datetime,subprocess

base=Path(__file__).parent
root=Path('/workspace/rougezhushou')
name='rouge/operator_engine.py'
old=(base/'baseline'/name).read_bytes().decode()
new=(base/'draft068'/name).read_bytes().decode()
patch=f'diff --git a/{name} b/{name}\n'+''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/'+name,tofile='b/'+name))
name='tests/test_shu_profession_text_input.py'
source=(base/'test_shu_profession_text_input.py').read_text()
patch+=f'diff --git a/{name} b/{name}\nnew file mode 100644\n'+''.join(difflib.unified_diff([],source.splitlines(True),fromfile='/dev/null',tofile='b/'+name))
path=base/'section68.patch';path.write_bytes(patch.encode())
freeze=json.loads((base/'baseline-freeze068.json').read_bytes())
drift=[name for name,receipt in freeze['files'].items() if hashlib.sha256((base/'baseline'/name).read_bytes()).hexdigest()!=receipt['sha256']]
assert not drift
check=subprocess.run(['git','apply','--check',str(path)],cwd=root,capture_output=True,text=True)
related=json.loads((base/'related-tests068.json').read_bytes())
matrix=json.loads((base/'matrix-comparison068.json').read_bytes())
assert not matrix['mismatches']
assert related['available_checks_passed'] and not related['errors'] and not related['failures']
assert matrix['source_sha256']==hashlib.sha256((base/'draft068/rouge/operator_engine.py').read_bytes()).hexdigest()
artifacts=['section68.patch','baseline-freeze068.json','freeze068.py','source_audit068.py','source-receipt068.json',
           'build_draft068.py','draft-receipt068.json','public_probe068.py','public-probe068.log','public-results068.json',
           'public-comparison068.json','compare_saved068.py','compare-saved068.log','public-comparison068-final.json',
           'evaluate_matrix068.py','draft-results068.json','matrix-comparison068.json','matrix068.log',
           'matrix-comparison068-initial-native-json-key-error.json','matrix068-initial-native-json-key-error.log',
           'matrix068-runtime-import-error.log','new-tests068-runtime-import-error.log','compare_draft_saved068.py',
           'test_shu_profession_text_input.py','new-tests068.log','run_related068.py','related-tests068.json',
           'related-tests068.log','author-end-source068.json','NOTE068.md','package068.py']
for artifact in sorted(base.glob('independent-*068*')):
    if artifact.is_file():artifacts.append(artifact.name)
files={name:{'sha256':hashlib.sha256((base/name).read_bytes()).hexdigest(),'bytes':(base/name).stat().st_size} for name in artifacts}
manifest={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':files,
          'scope':'public static sources and API outcomes only; excludes frozen packages and private/live state'}
(base/'manifest068.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
reviewfile=base/'independent-review068.json'
review=json.loads(reviewfile.read_bytes()) if reviewfile.exists() else None
if review:
    assert review['status']=='independent_review_passed' and not review['blockers']
    assert review['patch_sha256']==files['section68.patch']['sha256']
    assert review['draft_engine_sha256']==matrix['source_sha256']
receipt={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'section':68,
         'baseline_commit':freeze['frozen_commit'],'baseline_intact':True,'baseline_public_files':freeze['file_count'],
         'observed_root_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),
         'root_apply_check':{'exit_code':check.returncode,'stderr':check.stderr},
         'patch_sha256':files['section68.patch']['sha256'],'draft_source_sha256':matrix['source_sha256'],
         'changed_files':['rouge/operator_engine.py','tests/test_shu_profession_text_input.py'],
         'register_new_test_required':'scripts/verify_cloud.py MODULES test_shu_profession_text_input; no outdated runner hunk',
         'new_test_methods':8,'related_run':related['run'],'related_passed':related['passed'],'related_skipped':len(related['skipped']),
         'original_public_calls':matrix['original_public_calls_reused'],'paired_scenarios':matrix['paired_scenarios'],
         'public_calls':matrix['public_calls'],'matrix_counts':matrix['counts'],'all_full_json_and_error_outcomes_retained_in_archive':True,
         'source_values_and_formulas_unchanged':True,'strings_not_interpreted_as_bool':True,
         'existing_training_and_four_sui_error_priority_preserved':True,'inactive_fields_and_nontext_inputs_unchanged':True,
         'selected_shu_only_no_native_squad_count_or_global_effect_inference':True,'periodic_unknown_clock_preserved':True,
         'native_or_gui_or_wine_execution':False,'independent_review_status':'passed' if review else 'source_design_passed; final draft pending',
         'independent_paired_cases':review['independent_paired_cases'] if review else None,
         'independent_public_calls':review['independent_public_calls'] if review else None,
         'independent_new_tests_passed':review['new_test_methods_passed'] if review else None,
         'independent_saved_author_pairs_strictly_recompared':review['author_saved_outcome_pairs_strictly_recompared'] if review else None,
         'independent_review_sha256':hashlib.sha256(reviewfile.read_bytes()).hexdigest() if review else None,
         'manifest_sha256':hashlib.sha256((base/'manifest068.json').read_bytes()).hexdigest()}
(base/'handoff-receipt068.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(receipt,ensure_ascii=False))
assert check.returncode==0
