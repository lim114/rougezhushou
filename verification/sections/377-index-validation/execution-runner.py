from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import json,runpy,subprocess
ROOT=Path(__file__).resolve().parents[1];out=ROOT/'verification/sections/377-index-validation';out.mkdir(exist_ok=True)
def enc(v):return(json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode()
def read(n):return json.loads((ROOT/n).read_bytes())
def sha(n):return sha256((ROOT/n).read_bytes()).hexdigest()
def git(*a):return subprocess.check_output(['git',*a],cwd=ROOT)
assert git('rev-parse','HEAD').decode().strip()=='cb892adc6f1f0e37c25d45b46d8321b3550612f6'
prior=read('verification/sections/320-index-validation/process.json');assert prior['passed']and prior['tests_run']==25 and prior['script_sha256']==sha('scripts/update_cloud_index.py')
# Same unchanged index implementation: reuse the25 portable tests, execute its actual validation on current377 documents.
module=runpy.run_path(str(ROOT/'scripts/update_cloud_index.py'));module['update'](ROOT)
cp=read('DEVELOPMENT_CHECKPOINT.json');delivery=module['validate_delivery'](ROOT,cp);index=read('CLOUD_INDEX.json');r=read('verification/sections/377.json')
assert index['current_section_label']=='第377节 + '+r['title']and index['completed_sections']==377 and index['next_section']==378
assert index['requirements']['sha256']==sha('PROJECT_REQUIREMENTS.md')and index['latest_full_receipt']=='verification/full-365/summary.json'
assert cp['policy']['wrap_up_below_usage_percent']==15 and cp['policy']['development_paused_by_latest_user_request']is False
for n,h in index['public_pointers'].items():assert sha(n)==h,n
for group in('source_sha256','validated_source_sha256'):
 for n,h in r[group].items():assert sha(n)==h,n
record={'section':377,'passed':True,'current_documents_actually_validated':delivery,'current_index_script_sha256':sha('scripts/update_cloud_index.py'),'unchanged_index_unit_tests_reused':{'receipt':'verification/sections/320-index-validation/process.json','sha256':sha('verification/sections/320-index-validation/process.json'),'tests_run_historically':25,'rerun_this_section':False},'public_pointer_SHA_checked':True,'full_validation_rerun':False,'at_utc':datetime.now(timezone.utc).isoformat()}
(out/'current-validation.json').write_bytes(enc(record));(out/'execution-runner.py').write_bytes(Path(__file__).read_bytes())
r['index_validation']={'receipt':'verification/sections/377-index-validation/current-validation.json','sha256':sha('verification/sections/377-index-validation/current-validation.json'),'unchanged25_unit_tests_reused_not_rerun':True};(ROOT/'verification/sections/377.json').write_bytes(enc(r));module['update'](ROOT)
allowed=['AGENTS.md', 'CLOUD_HANDOFF.md', 'CLOUD_INDEX.json', 'DEVELOPMENT_CHECKPOINT.json', 'PROJECT_COMPLETED.md', 'PROJECT_PROGRESS.md', 'PROJECT_REQUIREMENTS.md', 'WORK_IN_PROGRESS.md', 'rouge/current_guest_knights.py', 'rouge/current_guest_knights_view.py', 'research/p3-current-guest-knights-377/corrupt-knight-complete.html', 'research/p3-current-guest-knights-377/http-source-records.json', 'research/p3-current-guest-knights-377/reference-data.json', 'research/p3-current-guest-knights-377/runtime-manifest.json', 'research/p3-current-guest-knights-377/source-notes.json', 'research/p3-current-guest-knights-377/wither-knight-complete.html', 'scripts/build_current_guest_knights_377.py', 'scripts/verify_current_guest_knights_window_377.py', 'tests/test_current_guest_knights_377.py', 'tests/test_current_guest_knights_view_377.py', 'rouge/current_battle_view.py', 'scripts/verify_full_available.py']
allowed.extend(p.relative_to(ROOT).as_posix()for p in(ROOT/'verification/sections').glob('377*'))
subprocess.run(['git','add','-f','--',*allowed],cwd=ROOT,check=True)
check=subprocess.run(['git','-c','core.whitespace=cr-at-eol,-blank-at-eof','diff','--cached','--check','--','.',':(exclude)research/p3-current-guest-knights-377/*.html'],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE);(out/'git-diff-check.txt').write_bytes(check.stdout+check.stderr);assert check.returncode==0,(check.stdout+check.stderr).decode('utf8',errors='replace')[-3000:]
(out/'public-stage-review.json').write_bytes(enc({'section':377,'root_reviewed':True,'source_and_runtime_current':True,'private_or_cache_inclusion_allowed':False,'staged_diff_check_actual_exit':check.returncode,'parent_commit':git('rev-parse','HEAD').decode().strip(),'index_actual_current_validation':True,'local_necessary_methods_run':r['necessary_validation']['methods_run'],'local_native_checks':r['native_windows_validation']['unique_checks']}))
subprocess.run(['git','add','-f','--',out.relative_to(ROOT).as_posix()],cwd=ROOT,check=True)
staged=git('diff','--cached','--name-only').decode('utf8').splitlines();assert not any(n.startswith(('.cache/','.local/'))or n=='local-settings.json'for n in staged)
assert not git('diff','--name-only').strip()and not git('ls-files','--others','--exclude-standard').strip()
print(json.dumps({'section':377,'staged_public_files':len(staged),'index_current_pointers_validated':True,'unchanged25_tests_reused_not_rerun':True,'ready_to_commit_not_published':True},ensure_ascii=False))
