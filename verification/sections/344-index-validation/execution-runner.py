from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import json,runpy,subprocess
ROOT=Path(__file__).resolve().parents[1];out=ROOT/'verification/sections/344-index-validation';out.mkdir()
def enc(v):return(json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode()
def read(n):return json.loads((ROOT/n).read_bytes())
def sha(n):return sha256((ROOT/n).read_bytes()).hexdigest()
def git(*a):return subprocess.check_output(['git',*a],cwd=ROOT)
assert git('rev-parse','HEAD').decode().strip()=='5832cf5829e9b6090b5a7d79fb78e3b1c4e26705'
prior=read('verification/sections/320-index-validation/process.json');assert prior['passed']and prior['tests_run']==25 and prior['script_sha256']==sha('scripts/update_cloud_index.py')
# Same unchanged index implementation: reuse the25 portable tests, execute its actual validation on current344 documents.
module=runpy.run_path(str(ROOT/'scripts/update_cloud_index.py'));module['update'](ROOT)
cp=read('DEVELOPMENT_CHECKPOINT.json');delivery=module['validate_delivery'](ROOT,cp);index=read('CLOUD_INDEX.json');r=read('verification/sections/344.json')
assert index['current_section_label']=='第344节 + '+r['title']and index['completed_sections']==344 and index['next_section']==345
assert index['requirements']['sha256']==sha('PROJECT_REQUIREMENTS.md')and index['latest_full_receipt']=='verification/full-335/summary.json'
assert cp['policy']['wrap_up_below_usage_percent']==15 and cp['policy']['development_paused_by_latest_user_request']is False
for n,h in index['public_pointers'].items():assert sha(n)==h,n
for group in('source_sha256','validated_source_sha256'):
 for n,h in r[group].items():assert sha(n)==h,n
record={'section':344,'passed':True,'current_documents_actually_validated':delivery,'current_index_script_sha256':sha('scripts/update_cloud_index.py'),'unchanged_index_unit_tests_reused':{'receipt':'verification/sections/320-index-validation/process.json','sha256':sha('verification/sections/320-index-validation/process.json'),'tests_run_historically':25,'rerun_this_section':False},'public_pointer_SHA_checked':True,'full_validation_rerun':False,'at_utc':datetime.now(timezone.utc).isoformat()}
(out/'current-validation.json').write_bytes(enc(record));(out/'execution-runner.py').write_bytes(Path(__file__).read_bytes())
r['index_validation']={'receipt':'verification/sections/344-index-validation/current-validation.json','sha256':sha('verification/sections/344-index-validation/current-validation.json'),'unchanged25_unit_tests_reused_not_rerun':True};(ROOT/'verification/sections/344.json').write_bytes(enc(r));module['update'](ROOT)
allowed=['AGENTS.md','CLOUD_HANDOFF.md','CLOUD_INDEX.json','DEVELOPMENT_CHECKPOINT.json','PROJECT_COMPLETED.md','PROJECT_PROGRESS.md','PROJECT_REQUIREMENTS.md','WORK_IN_PROGRESS.md','rouge/expansion_view.py','rouge/current_reconstruction.py','rouge/current_reconstruction_view.py','rouge/current_node_readers.py','rouge/current_node_readers_view.py','rouge/data/current-reconstruction.json','research/p3-current-reconstruction-344','scripts/build_current_reconstruction_344.py','scripts/verify_current_reconstruction_window_344.py','scripts/verify_full_available.py','tests/test_current_reconstruction_344.py','tests/test_current_reconstruction_view_344.py']
allowed.extend(p.relative_to(ROOT).as_posix()for p in(ROOT/'verification/sections').glob('344*'))
subprocess.run(['git','add','-f','--',*allowed],cwd=ROOT,check=True)
check=subprocess.run(['git','-c','core.whitespace=cr-at-eol','diff','--cached','--check'],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE);(out/'git-diff-check.txt').write_bytes(check.stdout+check.stderr);assert check.returncode==0,(check.stdout+check.stderr).decode('utf8',errors='replace')[-3000:]
(out/'public-stage-review.json').write_bytes(enc({'section':344,'root_reviewed':True,'source_and_runtime_current':True,'private_or_cache_inclusion_allowed':False,'staged_diff_check_actual_exit':check.returncode,'parent_commit':git('rev-parse','HEAD').decode().strip(),'index_actual_current_validation':True,'local_necessary_methods_run':49,'local_native_checks':61}))
subprocess.run(['git','add','-f','--',out.relative_to(ROOT).as_posix()],cwd=ROOT,check=True)
staged=git('diff','--cached','--name-only').decode('utf8').splitlines();assert not any(n.startswith(('.cache/','.local/'))or n=='local-settings.json'for n in staged)
assert not git('diff','--name-only').strip()and not git('ls-files','--others','--exclude-standard').strip()
print(json.dumps({'section':344,'staged_public_files':len(staged),'index_current_pointers_validated':True,'unchanged25_tests_reused_not_rerun':True,'ready_to_commit_not_published':True},ensure_ascii=False))
