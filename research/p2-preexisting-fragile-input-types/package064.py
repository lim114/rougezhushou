from pathlib import Path
import json,hashlib,difflib,datetime,subprocess
base=Path(__file__).parent;root=Path('/workspace/rougezhushou')
name='rouge/damage.py';old=(base/'baseline'/name).read_bytes().decode();new=(base/'draft064'/name).read_bytes().decode()
patch=f'diff --git a/{name} b/{name}\n'+''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/'+name,tofile='b/'+name))
name='tests/test_preexisting_fragile_input_types.py';source=(base/'test_preexisting_fragile_input_types.py').read_text()
patch+=f'diff --git a/{name} b/{name}\nnew file mode 100644\n'+''.join(difflib.unified_diff([],source.splitlines(True),fromfile='/dev/null',tofile='b/'+name))
p=base/'section64.patch';p.write_bytes(patch.encode())
freeze=json.loads((base/'baseline-freeze064.json').read_bytes());drift=[]
for name,receipt in freeze['files'].items():
 if hashlib.sha256((base/'baseline'/name).read_bytes()).hexdigest()!=receipt['sha256']:drift.append(name)
assert not drift
check=subprocess.run(['git','apply','--check',str(p)],cwd=root,capture_output=True,text=True)
related=json.loads((base/'related-tests064.json').read_bytes());matrix=json.loads((base/'matrix-comparison064.json').read_bytes());assert not matrix['mismatches'];assert related['available_checks_passed'] and not related['errors'] and not related['failures']
artifacts=['section64.patch','baseline-freeze064.json','freeze064.py','source_audit064.py','source-receipt064.json','gamedata_const.json','constant-download064.json','build_draft064.py','draft-receipt064.json','public_probe064.py','public-probe064.log','public-results064.json','public-comparison064.json','evaluate_matrix064.py','draft-results064.json','matrix-comparison064.json','matrix064.log','test_preexisting_fragile_input_types.py','new-tests064.log','new-tests064-initial.log','baseline-red064.log','run_related064.py','related-tests064.json','related-tests064.log','package064.py']
if (base/'NOTE064.md').exists():artifacts.append('NOTE064.md')
files={name:{'sha256':hashlib.sha256((base/name).read_bytes()).hexdigest(),'bytes':(base/name).stat().st_size} for name in artifacts}
manifest={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':files,'scope':'public static sources/API outcomes only; excludes 121MB frozen packages and any private/live state'}
(base/'manifest064.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
receipt={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'section':64,'baseline_commit':freeze['head'],'baseline_intact':not drift,'baseline_public_files':freeze['file_count'],
 'observed_root_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),'root_apply_check':{'exit_code':check.returncode,'stderr':check.stderr},
 'patch_sha256':files['section64.patch']['sha256'],'draft_source_sha256':matrix['source_sha256'],'changed_files':['rouge/damage.py','tests/test_preexisting_fragile_input_types.py'],
 'register_new_test_required':'scripts/verify_cloud.py MODULES test_preexisting_fragile_input_types; no outdated runner hunk',
 'new_test_methods':7,'related_run':related['run'],'related_passed':related['passed'],'related_skipped':len(related['skipped']),
 'paired_scenarios':matrix['paired_scenarios'],'public_calls':matrix['public_calls'],'matrix_counts':matrix['counts'],
 'source_values_and_formulas_unchanged':True,'strings_not_interpreted_as_bool':True,'inactive_fields_and_nontext_inputs_unchanged':True,
 'fragile_same_name_term_known_but_actual_multi_source_identity_and_attachment_unverified':True,'native_or_gui_or_wine_execution':False,
 'independent_review_status':'pending platform slot, followup review_shu60 rejected at seven active agents; author complete',
 'manifest_sha256':hashlib.sha256((base/'manifest064.json').read_bytes()).hexdigest()}
(base/'handoff-receipt064.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n');print(json.dumps(receipt,ensure_ascii=False));assert check.returncode==0
