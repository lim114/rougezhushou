from pathlib import Path
from hashlib import sha256
from datetime import datetime, timezone
import json,runpy,subprocess,sys
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'verification/sections/312-index-validation';OUT.mkdir()
def enc(v):return(json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode('utf8')
def read(n):return json.loads((ROOT/n).read_bytes())
def sha(n):return sha256((ROOT/n).read_bytes()).hexdigest()
def git(*a):return subprocess.check_output(['git',*a],cwd=ROOT)
parent='b46edb97bcae897414a4179d26cc5d7bd17acbef'
assert git('branch','--show-current').decode().strip()=='codex/p2-development'
assert git('rev-parse','HEAD').decode().strip()==parent==git('ls-remote','origin','refs/heads/codex/p2-development').decode().split()[0]
argv=[sys.executable,'-B','-X','utf8','-m','unittest','tests.test_cloud_index_sync','-q']
with(OUT/'stdout.txt').open('xb')as stdout,(OUT/'stderr.txt').open('xb')as stderr:
 p=subprocess.Popen(argv,cwd=ROOT,stdin=subprocess.DEVNULL,stdout=stdout,stderr=stderr);code=p.wait()
log=(OUT/'stderr.txt').read_text('utf8');passed=code==0 and 'Ran 25 tests'in log and'OK'in log
(OUT/'process.json').write_bytes(enc({'section':312,'passed':passed,'argv':argv,'retained_popen_pid':p.pid,'actual_exit':code,'tests_run':25 if'Ran 25 tests'in log else None,'observed_utc':datetime.now(timezone.utc).isoformat(),'script_sha256':sha('scripts/update_cloud_index.py'),'full_rerun':False}));(OUT/'process.exit').write_text(str(code)+'\n',encoding='ascii');(OUT/'execution-runner.py').write_bytes(Path(__file__).read_bytes())
assert passed,log[-4000:]
r=read('verification/sections/312.json');r['index_validation']={'receipt':'verification/sections/312-index-validation/process.json','sha256':sha('verification/sections/312-index-validation/process.json'),'tests_run':25}
(ROOT/'verification/sections/312.json').write_bytes(enc(r));runpy.run_path(str(ROOT/'scripts/update_cloud_index.py'))['update'](ROOT)
for mapping in('source_sha256','validated_source_sha256'):
 for name,h in r[mapping].items():assert sha(name)==h,name
index=read('CLOUD_INDEX.json');cp=read('DEVELOPMENT_CHECKPOINT.json')
assert cp['completed_sections']==cp['latest_functional_section']==312 and cp['next_section']==313
assert index['current_section_label']=='第312节 + '+r['title']
assert index['current_completed_change']==r['new_capability']
assert cp['policy']['wrap_up_below_usage_percent']==15 and cp['policy']['development_paused_by_latest_user_request']is False
for name,h in index['public_pointers'].items():assert sha(name)==h,name
allowed=['AGENTS.md','CLOUD_HANDOFF.md','CLOUD_INDEX.json','DEVELOPMENT_CHECKPOINT.json','PROJECT_COMPLETED.md','PROJECT_PROGRESS.md','PROJECT_REQUIREMENTS.md','WORK_IN_PROGRESS.md','rouge/battle_view.py','rouge/gold_boss_reference.py','rouge/gold_boss_view.py','rouge/data/gold-boss-reference.json','scripts/build_gold_boss_reference_312.py','scripts/verify_gold_boss_window_312.py','scripts/verify_full_available.py','tests/test_gold_boss_reference_312.py','tests/test_gold_boss_view_312.py','tests/test_gold_boss_integration_312.py','research/p3-gold-boss-312','research/p3-map-attempt-312']
allowed.extend(p.relative_to(ROOT).as_posix()for p in(ROOT/'verification/sections').glob('312*'))
subprocess.run(['git','add','-f','--',*allowed],cwd=ROOT,check=True)
check=subprocess.run(['git','-c','core.whitespace=cr-at-eol','diff','--cached','--check'],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
(OUT/'git-diff-check.txt').write_bytes(check.stdout+check.stderr)
assert check.returncode==0,(check.stdout+check.stderr).decode('utf8',errors='replace')[-5000:]
(OUT/'public-stage-review.json').write_bytes(enc({'section':312,'root_reviewed':True,'code_and_runtime_sources_current':True,'index_actual_exit':code,'diff_check_exit':check.returncode,'parent_commit':parent,'private_or_cache_inclusion_allowed':False,'full_validation_repeated':False,'current_section_label':index['current_section_label']}))
subprocess.run(['git','add','-f','--',OUT.relative_to(ROOT).as_posix()],cwd=ROOT,check=True)
staged=git('diff','--cached','--name-only').decode('utf8').splitlines()
assert not any(n.startswith(('.cache/','.local/'))or n=='local-settings.json'for n in staged)
assert not git('diff','--name-only').strip()and not git('ls-files','--others','--exclude-standard').strip()
subprocess.run(['git','-c','core.whitespace=cr-at-eol','diff','--cached','--check'],cwd=ROOT,check=True)
print(json.dumps({'section':312,'staged_public_files':len(staged),'index_checks':25,'actual_index_exit':code,'diff_check_exit':0,'current_sources_verified':True,'commit_ready_not_published':True},ensure_ascii=False))
