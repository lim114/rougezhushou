from pathlib import Path
from hashlib import sha256
import json,subprocess
ROOT=Path.cwd();OUT=ROOT/'verification/sections/313-index-validation'
def enc(v):return(json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode('utf8')
def read(n):return json.loads((ROOT/n).read_bytes())
def sha(n):return sha256((ROOT/n).read_bytes()).hexdigest()
def git(*a):return subprocess.check_output(['git',*a],cwd=ROOT)
parent='cc0b53683b37dae5273065986c989e5f783105d2'
r=read('verification/sections/313.json');code=read('verification/sections/313-index-validation/process.json')['actual_exit']
assert code==0 and git('rev-parse','HEAD').decode().strip()==parent
original=OUT/'git-diff-check.txt';archived=OUT/'git-diff-check-first-attempt.txt'
assert archived.exists()
for mapping in('source_sha256','validated_source_sha256'):
 for name,h in r[mapping].items():assert sha(name)==h,name
index=read('CLOUD_INDEX.json');cp=read('DEVELOPMENT_CHECKPOINT.json')
assert cp['completed_sections']==cp['latest_functional_section']==313 and cp['next_section']==314
assert index['current_section_label']=='第313节 + '+r['title']
assert index['current_completed_change']==r['new_capability']
assert cp['policy']['wrap_up_below_usage_percent']==15 and cp['policy']['development_paused_by_latest_user_request']is False
for name,h in index['public_pointers'].items():assert sha(name)==h,name
allowed=['.gitattributes','AGENTS.md','CLOUD_HANDOFF.md','CLOUD_INDEX.json','DEVELOPMENT_CHECKPOINT.json','PROJECT_COMPLETED.md','PROJECT_PROGRESS.md','PROJECT_REQUIREMENTS.md','WORK_IN_PROGRESS.md','rouge/app.py','rouge/battle_view.py','rouge/expansion_reference.py','rouge/expansion_view.py','rouge/data/expansion-maps','scripts/build_expansion_reference_313.py','scripts/verify_expansion_window_313.py','scripts/verify_full_available.py','tests/test_expansion_reference_313.py','tests/test_expansion_view_313.py','tests/test_expansion_integration_313.py','research/p3-expansion-313']
allowed.extend(p.relative_to(ROOT).as_posix()for p in(ROOT/'verification/sections').glob('313*'))
subprocess.run(['git','add','-f','--',*allowed],cwd=ROOT,check=True)
(OUT/'git-diff-check.txt').write_bytes(b'')
subprocess.run(['git','add','-f','--','verification/sections/313-index-validation/git-diff-check.txt'],cwd=ROOT,check=True)
check=subprocess.run(['git','-c','core.whitespace=cr-at-eol','diff','--cached','--check'],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
(OUT/'git-diff-check.txt').write_bytes(check.stdout+check.stderr)
assert check.returncode==0,(check.stdout+check.stderr).decode('utf8',errors='replace')[-5000:]
(OUT/'public-stage-review.json').write_bytes(enc({'section':313,'root_reviewed':True,'code_and_runtime_sources_current':True,'index_actual_exit':code,'diff_check_exit':check.returncode,'parent_commit':parent,'private_or_cache_inclusion_allowed':False,'full_validation_repeated':False,'current_section_label':index['current_section_label']}))
subprocess.run(['git','add','-f','--',OUT.relative_to(ROOT).as_posix()],cwd=ROOT,check=True)
staged=git('diff','--cached','--name-only').decode('utf8').splitlines()
assert not any(n.startswith(('.cache/','.local/'))or n=='local-settings.json'for n in staged)
assert not git('diff','--name-only').strip()and not git('ls-files','--others','--exclude-standard').strip()
subprocess.run(['git','-c','core.whitespace=cr-at-eol','diff','--cached','--check'],cwd=ROOT,check=True)
(OUT/'execution-stage-resume.py').write_bytes(Path(__file__).read_bytes())
subprocess.run(['git','add','-f','--',OUT.relative_to(ROOT).as_posix()],cwd=ROOT,check=True)
print(json.dumps({'section':313,'staged_public_files':len(staged),'index_checks':25,'actual_index_exit':code,'diff_check_exit':0,'current_sources_verified':True,'commit_ready_not_published':True},ensure_ascii=False))
