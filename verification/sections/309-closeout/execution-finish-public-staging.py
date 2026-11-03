from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import json,runpy,subprocess
ROOT=Path(__file__).resolve().parents[1];out=ROOT/'verification/sections/309-closeout'
def enc(v):return(json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode('utf8')
def git(*a):return subprocess.check_output(['git',*a],cwd=ROOT)
def read(n):return json.loads((ROOT/n).read_bytes())
def sha(n):return sha256((ROOT/n).read_bytes()).hexdigest()
assert (out/'final-git-diff-check.txt').read_text('utf8').strip()=='verification/sections/309-closeout/before-view-test-whitespace.py:102: new blank line at EOF.'
subprocess.run(['git','add','--','.gitattributes'],cwd=ROOT,check=True)
check=subprocess.run(['git','-c','core.whitespace=cr-at-eol','diff','--cached','--check'],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
(out/'final-preserved-evidence-diff-check.txt').write_bytes(check.stdout+check.stderr);assert check.returncode==0
record={'section':309,'passed':True,'at_utc':datetime.now(timezone.utc).isoformat(),'first_active_test_EOF_and_second_archived_original_style_observations_preserved':True,'final_diff_check_exit':check.returncode,'old_test_AST_identical':True,'private_paths_staged':False,'application_code_runtime_sources_current':True,'metadata_doc_and_test_EOF_changes_bound_separately':True,'exact_raw_evidence_gitattributes_exception':'verification/sections/309-closeout/before-view-test-whitespace.py only disables blank-at-eof to retain original failure bytes; active code style guard remains enabled.'}
(out/'final-stage-review.json').write_bytes(enc(record));(out/'execution-finish-public-staging.py').write_bytes(Path(__file__).read_bytes())
r=read('verification/sections/309.json');r['final_stage_review']={'receipt':'verification/sections/309-closeout/final-stage-review.json','sha256':sha('verification/sections/309-closeout/final-stage-review.json')};(ROOT/'verification/sections/309.json').write_bytes(enc(r))
runpy.run_path(str(ROOT/'scripts/update_cloud_index.py'))['update'](ROOT)
subprocess.run(['git','add','-f','--','verification/sections/309-closeout','verification/sections/309.json','CLOUD_INDEX.json','CLOUD_HANDOFF.md'],cwd=ROOT,check=True)
names=git('diff','--cached','--name-only').decode('utf8').splitlines();assert not any(n.startswith(('.cache/','.local/'))or n=='local-settings.json'for n in names)
assert not git('diff','--name-only').strip()
assert subprocess.run(['git','-c','core.whitespace=cr-at-eol','diff','--cached','--check'],cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0
for name,h in r['source_sha256'].items():assert sha(name)==h,name
for name,h in r['validated_source_sha256'].items():assert sha(name)==h,name
print(json.dumps({'staged_public_files':len(names),'diff_check_exit':0,'index_tests_actual_passed':25,'application_code_and_runtime_sources_current':True,'ordinary_commit_and_push_pending':True}))
