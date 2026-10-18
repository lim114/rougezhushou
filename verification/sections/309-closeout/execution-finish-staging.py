from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import ast,json,runpy,subprocess
ROOT=Path(__file__).resolve().parents[1]
def enc(v):return(json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode('utf8')
def read(n):return json.loads((ROOT/n).read_bytes())
def sha(n):return sha256((ROOT/n).read_bytes()).hexdigest()
def git(*a):return subprocess.check_output(['git',*a],cwd=ROOT)
name='tests/test_boss_phase_view_309.py';p=ROOT/name;old=p.read_bytes();new=old.rstrip(b'\r\n')+b'\r\n'
assert old!=new and ast.dump(ast.parse(old),include_attributes=True)==ast.dump(ast.parse(new),include_attributes=True)
out=ROOT/'verification/sections/309-closeout';(out/'before-view-test-whitespace.py').write_bytes(old);p.write_bytes(new)
style={'section':309,'kind':'post_validation_test_EOF_whitespace_only_no_behavior_change','file':name,'before_sha256':sha256(old).hexdigest(),'after_sha256':sha(name),'entire_AST_including_line_and_column_attributes_equal':True,'actual_failure':'git diff --cached --check: tests/test_boss_phase_view_309.py:102 new blank line at EOF','first_diff_check_exit':1,'original_diff_check_log':'verification/sections/309-index-validation/git-diff-check.txt','change':'Remove one empty EOF line only. No assertion, import, identifier, application source, runtime authority or native script changed.','necessary_or_Qt_repeat_needed':False,'not_claimed_new_test_bytes_were_the_native_bound_bytes':True}
(out/'test-whitespace-only-review.json').write_bytes(enc(style))
receipt='verification/sections/309.json';r=read(receipt)
assert r['source_sha256'][name]==r['validated_source_sha256'][name]==style['before_sha256']
r['source_sha256'][name]=style['after_sha256'];r['validated_source_sha256'].pop(name)
r['post_validation_whitespace_only_test_change']={'receipt':'verification/sections/309-closeout/test-whitespace-only-review.json','sha256':sha('verification/sections/309-closeout/test-whitespace-only-review.json'),'exclusion_from_current_native_source_map':name,'entire_test_AST_equal':True,'all_application_code_and_runtime_bytes_unchanged':True}
doc=read('verification/sections/309-preparation/schema-current-doc/correction.json')
overrides={name:style,doc['file']:doc}
for value in(read('verification/sections/309-necessary-attempt2/process.json'),read('verification/sections/309-native-attempt2/actual/window.json')):
    assert value['passed'] and value['source_sha256_before']==value['source_sha256_after']
    for filename,h in value['source_sha256_after'].items():
        if filename in overrides:
            item=overrides[filename];assert h==item['before_sha256'] and sha(filename)==item['after_sha256']
        else:assert sha(filename)==h,filename
(ROOT/receipt).write_bytes(enc(r));runpy.run_path(str(ROOT/'scripts/update_cloud_index.py'))['update'](ROOT)
(out/'execution-first-finalizer.py').write_bytes((ROOT/'.cache/finalize309.py').read_bytes());(out/'execution-finish-staging.py').write_bytes(Path(__file__).read_bytes())
subprocess.run(['git','add','-f','--',name,receipt,'CLOUD_INDEX.json','CLOUD_HANDOFF.md','verification/sections/309-closeout'],cwd=ROOT,check=True)
check=subprocess.run(['git','-c','core.whitespace=cr-at-eol','diff','--cached','--check'],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
(out/'final-git-diff-check.txt').write_bytes(check.stdout+check.stderr);assert check.returncode==0
record={'section':309,'passed':True,'at_utc':datetime.now(timezone.utc).isoformat(),'first_staging_whitespace_failure_preserved':True,'final_diff_check_exit':check.returncode,'old_test_AST_identical':True,'private_paths_staged':False,'code_runtime_sources_current':True,'metadata_doc_and_test_EOF_changes_bound_separately':True}
(out/'final-stage-review.json').write_bytes(enc(record));r['final_stage_review']={'receipt':'verification/sections/309-closeout/final-stage-review.json','sha256':sha('verification/sections/309-closeout/final-stage-review.json')};(ROOT/receipt).write_bytes(enc(r))
runpy.run_path(str(ROOT/'scripts/update_cloud_index.py'))['update'](ROOT)
subprocess.run(['git','add','-f','--',receipt,'CLOUD_INDEX.json','CLOUD_HANDOFF.md','verification/sections/309-closeout'],cwd=ROOT,check=True)
staged=git('diff','--cached','--name-only').decode('utf8').splitlines();assert not any(n.startswith(('.cache/','.local/'))or n=='local-settings.json'for n in staged)
assert not git('diff','--name-only').strip()
assert subprocess.run(['git','-c','core.whitespace=cr-at-eol','diff','--cached','--check'],cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0
print(json.dumps({'staged_files':len(staged),'diff_check_exit':0,'index_tests_actual_passed':25,'code_data_and_assertions_changed_after_final_83_or27':False,'metadata_only_corrections_separately_proven':True,'ordinary_commit_and_push_pending':True}))
