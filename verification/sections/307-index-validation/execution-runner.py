from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import json,subprocess,sys,runpy
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'verification/sections/307-index-validation';OUT.mkdir()
def enc(v):return (json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode('utf8')
def git(*a):return subprocess.check_output(['git',*a],cwd=ROOT)
def read(n):return json.loads((ROOT/n).read_bytes())
def sha(n):return sha256((ROOT/n).read_bytes()).hexdigest()
assert git('rev-parse','HEAD').decode().strip()=='c45ffb00f1932a27919885440b98a52094b087e0'
assert git('ls-remote','origin','refs/heads/codex/p2-development').decode().split()[0]==git('rev-parse','HEAD').decode().strip()
argv=[sys.executable,'-B','-X','utf8','-m','unittest','tests.test_cloud_index_sync','-q']
with(OUT/'stdout.txt').open('xb')as stdout,(OUT/'stderr.txt').open('xb')as stderr:
 p=subprocess.Popen(argv,cwd=ROOT,stdin=subprocess.DEVNULL,stdout=stdout,stderr=stderr);code=p.wait()
log=(OUT/'stderr.txt').read_text('utf8');assert code==0 and 'Ran 25 tests'in log and 'OK'in log
check=subprocess.run(['git','-c','core.whitespace=cr-at-eol','diff','--check'],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
(OUT/'git-diff-check.txt').write_bytes(check.stdout+check.stderr);assert check.returncode==0
record={'section':307,'passed':True,'argv':argv,'retained_popen_pid':p.pid,'actual_exit':code,'tests_run':25,'observed_utc':datetime.now(timezone.utc).isoformat(),'script_sha256':sha('scripts/update_cloud_index.py'),'checks':'Current index/requirements/content guards; CRLF treated as original repo line endings; no full validation rerun','diff_check_actual_exit':check.returncode}
(OUT/'process.json').write_bytes(enc(record));(OUT/'process.exit').write_text(str(code)+'\n',encoding='ascii');(OUT/'execution-runner.py').write_bytes(Path(__file__).read_bytes())
p=ROOT/'verification/sections/307.json';r=read(p.relative_to(ROOT));r['index_validation']={'receipt':'verification/sections/307-index-validation/process.json','sha256':sha('verification/sections/307-index-validation/process.json'),'tests_run':25};p.write_bytes(enc(r))
runpy.run_path(str(ROOT/'scripts/update_cloud_index.py'))['update'](ROOT)
for result in (read('verification/sections/307-necessary-attempt2/process.json'),read('verification/sections/307-window-attempt2/actual/window.json')):
 assert result['passed'] and result['source_sha256_before']==result['source_sha256_after']
 for n,h in result['source_sha256_after'].items():assert sha(n)==h,n
cp=read('DEVELOPMENT_CHECKPOINT.json');index=read('CLOUD_INDEX.json')
assert cp['completed_sections']==cp['latest_functional_section']==307 and cp['next_section']==308
assert index['current_section_label']=='第307节 + '+r['title'] and index['current_completed_change']==r['new_capability']
for n,h in index['public_pointers'].items():assert sha(n)==h,n
assert index['requirements']['sha256']==sha('PROJECT_REQUIREMENTS.md')
allowed=['AGENTS.md','CLOUD_HANDOFF.md','CLOUD_INDEX.json','DEVELOPMENT_CHECKPOINT.json','PROJECT_COMPLETED.md','PROJECT_PROGRESS.md','PROJECT_REQUIREMENTS.md','WORK_IN_PROGRESS.md','rouge/node_catalog_view.py','rouge/original_destinations.py','rouge/player_node_information.py','rouge/choice_annotations.py','rouge/data/choice-annotations.json','scripts/build_choice_annotations_307.py','scripts/verify_choice_annotations_window_307.py','scripts/verify_full_available.py','tests/test_documented_item_integration_295.py','tests/test_event_node_requirements_integration_298.py','tests/test_expedition_integration_297.py','tests/player_presentation_legacy_307.py','tests/test_annotation_presentation_pairs_307.py','tests/test_choice_annotation_view_307.py','tests/test_choice_annotations_307.py','research/p3-choice-annotations-307']
allowed.extend(p.relative_to(ROOT).as_posix()for p in(ROOT/'verification/sections').glob('307*'))
assert not any(n.startswith(('.local/','.cache/'))or n=='local-settings.json'for n in allowed)
subprocess.run(['git','add','-f','--',*allowed],cwd=ROOT,check=True)
staged=git('diff','--cached','--name-only').decode('utf8').splitlines()
assert not any(n.startswith(('.local/','.cache/'))or n=='local-settings.json'for n in staged)
assert not git('diff','--name-only').strip(),'Unstaged edits require review before commit'
print(enc({'section':307,'index_checks_actual_exit':code,'staged_public_files':len(staged),'sources_current':True,'commit_ready_not_pushed':True}))
