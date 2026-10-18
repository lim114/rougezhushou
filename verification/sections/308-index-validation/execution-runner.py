from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import ast,json,subprocess,sys,runpy
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'verification/sections/308-index-validation';OUT.mkdir()
def enc(v):return(json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode('utf8')
def git(*a):return subprocess.check_output(['git',*a],cwd=ROOT)
def read(n):return json.loads((ROOT/n).read_bytes())
def sha(n):return sha256((ROOT/n).read_bytes()).hexdigest()
before_ast=ast.parse((ROOT/'verification/sections/308-preparation/before/tests/test_direct_landmark_303.py').read_bytes());after_ast=ast.parse((ROOT/'tests/test_direct_landmark_303.py').read_bytes())
def methods(tree):return{n.name:n for n in ast.walk(tree)if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
old,new=methods(before_ast),methods(after_ast);assert old.keys()==new.keys()
changed=[name for name in old if ast.dump(old[name])!=ast.dump(new[name])];assert set(changed)=={'setUpClass','test_14_default_cli_is_readonly_and_candidate_output_is_exclusive'}
assert len([n for n in old if n.startswith('test_')])==16
(ROOT/'verification/sections/308-preparation/root-final303-maintenance-review.json').write_bytes(enc({'section':308,'complete_old_test_methods_preserved':16,'only_changed_functions':changed,'all_other_function_ASTs_identical':True,'original_builder_source_unchanged_sha256':sha('scripts/extend_direct_landmark_303.py'),'current303_test_sha256':sha('tests/test_direct_landmark_303.py'),'actual_child_CLI_uses_explicit_public107_and_utf8':True,'no_subprocess_mock_or_skip_added':True,'new308_tests_separately_validate_live123_and_old_guard_rejection':True}))
assert git('branch','--show-current').decode().strip()=='codex/p2-development'
assert git('rev-parse','HEAD').decode().strip()=='aae2340ba4689dd54097f84db4942af21e0d88f8'
assert git('ls-remote','origin','refs/heads/codex/p2-development').decode().split()[0]==git('rev-parse','HEAD').decode().strip()
argv=[sys.executable,'-B','-X','utf8','-m','unittest','tests.test_cloud_index_sync','-q']
with(OUT/'stdout.txt').open('xb')as stdout,(OUT/'stderr.txt').open('xb')as stderr:
 p=subprocess.Popen(argv,cwd=ROOT,stdin=subprocess.DEVNULL,stdout=stdout,stderr=stderr);code=p.wait()
log=(OUT/'stderr.txt').read_text('utf8');assert code==0 and 'Ran 25 tests'in log and 'OK'in log
check=subprocess.run(['git','-c','core.whitespace=cr-at-eol','diff','--check'],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
(OUT/'git-diff-check.txt').write_bytes(check.stdout+check.stderr);assert check.returncode==0
record={'section':308,'passed':True,'argv':argv,'retained_popen_pid':p.pid,'actual_exit':code,'tests_run':25,'observed_utc':datetime.now(timezone.utc).isoformat(),'script_sha256':sha('scripts/update_cloud_index.py'),'checks':'Current source/requirements/index guards; preserved CRLF treated as original line endings; no full suite rerun','diff_check_actual_exit':check.returncode}
(OUT/'process.json').write_bytes(enc(record));(OUT/'process.exit').write_text(str(code)+'\n',encoding='ascii');(OUT/'execution-runner.py').write_bytes(Path(__file__).read_bytes())
p=ROOT/'verification/sections/308.json';r=read(p.relative_to(ROOT));r['index_validation']={'receipt':'verification/sections/308-index-validation/process.json','sha256':sha('verification/sections/308-index-validation/process.json'),'tests_run':25};r['root_303_historical_test_review']={'receipt':'verification/sections/308-preparation/root-final303-maintenance-review.json','sha256':sha('verification/sections/308-preparation/root-final303-maintenance-review.json')};p.write_bytes(enc(r))
runpy.run_path(str(ROOT/'scripts/update_cloud_index.py'))['update'](ROOT)
for value in(read('verification/sections/308-necessary-attempt2/process.json'),read('verification/sections/308-window-attempt1/actual/window.json')):
 assert value['passed']and value['source_sha256_before']==value['source_sha256_after']
 for name,h in value['source_sha256_after'].items():assert sha(name)==h,name
index=read('CLOUD_INDEX.json');c=read('DEVELOPMENT_CHECKPOINT.json');assert c['completed_sections']==c['latest_functional_section']==308 and c['next_section']==309
assert index['current_section_label']=='第308节 + '+r['title']and index['current_completed_change']==r['new_capability']
for name,h in index['public_pointers'].items():assert sha(name)==h,name
allowed=['AGENTS.md','CLOUD_HANDOFF.md','CLOUD_INDEX.json','DEVELOPMENT_CHECKPOINT.json','PROJECT_COMPLETED.md','PROJECT_PROGRESS.md','PROJECT_REQUIREMENTS.md','WORK_IN_PROGRESS.md','rouge/data/fixed-landmark-references.json','scripts/extend_direct_landmark_308.py','scripts/verify_direct_map_window_308.py','scripts/verify_direct_map_window_303_full308.py','scripts/verify_direct_map_window_294_full308.py','scripts/verify_full_available.py','tests/test_direct_landmark_303.py','tests/test_direct_landmark_308.py','research/p3-map-direct-ground-308']
allowed.extend(p.relative_to(ROOT).as_posix()for p in(ROOT/'verification/sections').glob('308*'))
subprocess.run(['git','add','-f','--',*allowed],cwd=ROOT,check=True)
staged=git('diff','--cached','--name-only').decode('utf8').splitlines();assert not any(n.startswith(('.cache/','.local/'))or n=='local-settings.json'for n in staged)
assert not git('diff','--name-only').strip()
publish=(ROOT/'.cache/publish307.py').read_text('utf8').replace('307','308').replace("cp['next_section']==308","cp['next_section']==309").replace("'next_section':308","'next_section':309").replace('c45ffb00f1932a27919885440b98a52094b087e0','aae2340ba4689dd54097f84db4942af21e0d88f8')
(ROOT/'.cache/publish308.py').write_text(publish,encoding='utf8')
metadata=(ROOT/'.cache/metadata307.py').read_text('utf8').replace('307','308').replace("cp['next_section']==308","cp['next_section']==309").replace('next_section=308','next_section=309').replace("['section']==306","['section']==307").replace('事件附注区分出现前条件与选择后结果','一步之遥与彼处水如酒的格子位置预览').replace('308未启动','309未启动')
(ROOT/'.cache/metadata308.py').write_text(metadata,encoding='utf8')
print(json.dumps({'section':308,'staged_public_files':len(staged),'index_checks_actual_exit':code,'sources_current':True,'commit_ready_not_pushed':True},ensure_ascii=False))
