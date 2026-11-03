from pathlib import Path
from hashlib import sha256,sha1
from datetime import datetime,timezone
import subprocess,json,runpy
R=Path.cwd();branch='codex/p2-development';proof=json.loads((R/'.cache/current-enemy448-functional-publication.json').read_bytes());BASE=proof['commit']
def git(*a):return subprocess.check_output(['git',*a],cwd=R)
assert git('branch','--show-current').decode().strip()==branch
assert git('rev-parse','HEAD').decode().strip()==BASE
assert git('ls-remote','origin','refs/heads/'+branch).decode().split()[0]==BASE
out=R/'.cache/current-enemy448-publication-metadata';out.mkdir(exist_ok=False)
checkpoint=json.loads((R/'DEVELOPMENT_CHECKPOINT.json').read_bytes());assert checkpoint['completed_sections']==448 and checkpoint['next_section']==448
idx=runpy.run_path(str(R/'scripts/update_cloud_index.py'));assert idx['validate_delivery'](R,checkpoint)['verified_remote_section']==448
source=json.loads((R/'verification/sections/448-current-enemy-component/source-review.json').read_bytes())
for n,v in source['changed_or_new_sources'].items():assert sha256((R/n).read_bytes()).hexdigest()==v['sha256']==proof['verified_commit_tree_and_local_public_bytes'][n]['sha256']
assert json.loads((R/'verification/sections/448-publication-index-checks/process.json').read_bytes())['actual_observed_exit']==0
allowed={'DEVELOPMENT_CHECKPOINT.json','CLOUD_INDEX.json','CLOUD_HANDOFF.md','verification/sections/448-publication.json'}
names={n.decode('utf8')for n in git('diff','--name-only','-z').split(b'\0')if n}|{n.decode('utf8')for n in git('ls-files','--others','--exclude-standard','-z').split(b'\0')if n}
names.update(p.relative_to(R).as_posix()for p in(R/'verification/sections/448-publication-index-checks').iterdir()if p.is_file())
assert all(n in allowed or n.startswith('verification/sections/448-publication-index-checks/')for n in names)
assert not git('diff','--cached','--name-only').strip()
subprocess.run(['git','--literal-pathspecs','add','-f','--',*sorted(names)],cwd=R,check=True)
assert {n.decode('utf8')for n in git('diff','--cached','--name-only','-z').split(b'\0')if n}==names
subprocess.run(['git','-c','core.whitespace=cr-at-eol,-blank-at-eof','diff','--cached','--check'],cwd=R,check=True)
subprocess.run(['git','-c','maintenance.auto=false','commit','-m','核对第448节发布证明并同步云端入口'],cwd=R,check=True,stdout=subprocess.PIPE)
head=git('rev-parse','HEAD').decode().strip()
with(out/'stdout.txt').open('xb')as a,(out/'stderr.txt').open('xb')as b:
    p=subprocess.Popen(['git','push','origin','HEAD:refs/heads/'+branch],cwd=R,stdout=a,stderr=b);(out/'start.json').write_text(json.dumps({'actual_retained_PID':p.pid},indent=2)+'\n','utf8');code=p.wait()
(out/'process.json').write_text(json.dumps({'actual_retained_PID':p.pid,'actual_observed_exit':code},indent=2)+'\n','utf8')
remote=git('ls-remote','origin','refs/heads/'+branch).decode().split()[0];assert remote==head
subprocess.run(['git','fetch','origin',branch],cwd=R,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE);assert git('rev-parse','origin/'+branch).decode().strip()==head
raw_proofs={}
for n in sorted(names|set(proof['verified_commit_tree_and_local_public_bytes'])):
    raw=(R/n).read_bytes();blob=git('rev-parse',head+':'+n).decode().strip();assert blob==sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
    raw_proofs[n]={'sha256':sha256(raw).hexdigest(),'bytes':len(raw),'git_blob_sha1':blob}
assert not git('status','--porcelain').strip()
value={'passed':True,'branch':branch,'section':448,'functional_commit':BASE,'actual_current_commit':head,'actual_remote_HEAD':remote,'ordinary_push':True,'actual_push_exit':code,'force_push':False,'verified_public_files':raw_proofs,'product_code_unchanged_since_verified_functional_commit':True,'new_functional_section_added':False,'git_clean':True,'goal_active':True,'whole_program_or_video_complete':False,'at_UTC':datetime.now(timezone.utc).isoformat()}
(R/'.cache/current-enemy448-metadata-publication.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n','utf8')
print(json.dumps({'passed':True,'section':448,'actual_remote_HEAD':remote,'public_files_verified':len(raw_proofs),'git_clean':True,'whole_goal_complete':False}))
