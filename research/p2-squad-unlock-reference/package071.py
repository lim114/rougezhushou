from pathlib import Path
import json,hashlib,difflib,datetime,subprocess
base=Path(__file__).parent;root=Path('/workspace/rougezhushou')
changed=('rouge/run_modifiers.py','rouge/reporting.py')
added={'rouge/squad_unlock_reference.py':'squad_unlock_reference.py','tests/test_squad_unlock_reference.py':'test_squad_unlock_reference.py'}
patch=''
for name in changed:
    old=(base/'baseline'/name).read_bytes().decode();new=(base/'draft071'/name).read_bytes().decode()
    patch+=f'diff --git a/{name} b/{name}\n'+''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/'+name,tofile='b/'+name))
for name,local in added.items():
    text=(base/local).read_text()
    patch+=f'diff --git a/{name} b/{name}\nnew file mode 100644\n'+''.join(difflib.unified_diff([],text.splitlines(True),fromfile='/dev/null',tofile='b/'+name))
path=base/'section71.patch';path.write_bytes(patch.encode())
freeze=json.loads((base/'baseline-freeze.json').read_bytes())
assert not [name for name,r in freeze['files'].items() if hashlib.sha256((base/'baseline'/name).read_bytes()).hexdigest()!=r['sha256']]
matrix=json.loads((base/'matrix-comparison071.json').read_bytes());related=json.loads((base/'related-tests071.json').read_bytes())
assert not matrix['mismatches'] and related['available_checks_passed'] and not related['failures'] and not related['errors']
raw=(base/'roguelike_topic_table.json').read_bytes()
assert hashlib.sha256(raw).hexdigest()=='f5867e55d09472253083486174aa47bd94dd48b07684b74b60a5b29ca00eda86'
end={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'raw_topic_sha256':hashlib.sha256(raw).hexdigest(),
     'raw_topic_bytes':len(raw),'draft_source_sha256':{name:hashlib.sha256((base/'draft071'/name).read_bytes()).hexdigest() for name in (*changed,'rouge/squad_unlock_reference.py')}}
(base/'author-end-source071.json').write_text(json.dumps(end,ensure_ascii=False,indent=2)+'\n')
assert end['draft_source_sha256']==related['source_start_sha256']==related['source_end_sha256']
check=subprocess.run(['git','apply','--check',str(path)],cwd=root,capture_output=True,text=True)
already_applied=False
reverse_check=None
if check.returncode:
    reverse_check=subprocess.run(['git','apply','--reverse','--check',str(path)],cwd=root,capture_output=True,text=True)
    already_applied=reverse_check.returncode==0
names=['section71.patch','baseline-freeze.json','baseline-freeze-earlier-b4428de.json','freeze_environment.py',
       'source_audit071.py','source-receipt071.json','source-audit071.log','roguelike_topic_table.json','reused-source-copy071.json',
       'squad_unlock_reference.py','build_draft071.py','draft-receipt071.json',
       'public_probe071.py','baseline-results071.json','draft-results071.json','baseline-probe071.log','draft-probe071.log',
       'compare_matrix071.py','matrix-comparison071.json','matrix071.log','test_squad_unlock_reference.py','new-tests071.log',
       'run_related071.py','related-tests071.json','related-tests071.log','related-tests071-initial-missing-public-fixture.json',
       'related-tests071-initial-missing-public-fixture.log','author-end-source071.json','NOTE071.md','package071.py']
for p in sorted(base.glob('independent*071*')):
    if p.is_file():names.append(p.name)
files={name:{'sha256':hashlib.sha256((base/name).read_bytes()).hexdigest(),'bytes':(base/name).stat().st_size} for name in names}
manifest={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':files,
          'scope':'public source and whole JSON/error results; excludes package copies, private state and live data'}
(base/'manifest071.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
reviewfile=base/'independent-review071.json';review=json.loads(reviewfile.read_bytes()) if reviewfile.exists() else None
if review:
    assert review['status']=='independent_review_passed' and not review['blockers']
    assert review['patch_sha256']==files['section71.patch']['sha256']
    assert review['changed_source_hashes']==end['draft_source_sha256']
out={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'section':71,'baseline_commit':freeze['frozen_commit'],
     'baseline_public_files':freeze['file_count'],'baseline_intact':True,
     'observed_root_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),
     'root_apply_check':{'exit_code':check.returncode,'stderr':check.stderr},
     'root_patch_already_applied':already_applied,
     'root_reverse_apply_check':None if reverse_check is None else {'exit_code':reverse_check.returncode,'stderr':reverse_check.stderr},
     'patch_sha256':files['section71.patch']['sha256'],'draft_source_sha256':end['draft_source_sha256'],
     'changed_files':[*changed,*added],
     'register_new_test_required':'scripts/verify_cloud.py MODULES tests.test_squad_unlock_reference; no outdated runner hunk',
     'new_test_methods':9,'related_run':related['run'],'related_passed':related['passed'],'related_skipped':related['skipped'],
     'paired_scenarios':matrix['paired_scenarios'],'public_calls':matrix['public_calls'],'matrix_counts':matrix['counts'],
     'only_reference_and_report_added':True,'numerics_training_existing_flags_and_errors_unchanged':True,
     'account_unlock_actual_activation_and_buff_binding_remain_unknown':True,
     'no_private_state_reads_or_resets':True,'no_native_binaries_or_gui_or_wine':True,
     'independent_review_status':'passed' if review else 'source_passed; final patch pending',
     'independent_paired_scenarios':review['fresh_independent_paired_scenarios'] if review else None,
     'independent_public_calls':review['fresh_independent_public_calls'] if review else None,
     'independent_new_tests_passed':review['independent_new_tests_passed'] if review else None,
     'independent_author_saved_pairs_strictly_recompared':review['author_saved_pairs_strictly_recompared'] if review else None,
     'independent_review_sha256':hashlib.sha256(reviewfile.read_bytes()).hexdigest() if review else None,
     'manifest_sha256':hashlib.sha256((base/'manifest071.json').read_bytes()).hexdigest()}
(base/'handoff-receipt071.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(out)
assert check.returncode==0 or already_applied
