from pathlib import Path
from hashlib import sha256,sha1
from datetime import datetime,timezone
import argparse,json,subprocess
ROOT=Path(__file__).resolve().parents[1]
def git(*a):return subprocess.check_output(['git',*a],cwd=ROOT)
def read(n):return json.loads((ROOT/n).read_bytes())
def enc(v):return(json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode()
def sha(n):return sha256((ROOT/n).read_bytes()).hexdigest()
parser=argparse.ArgumentParser();parser.add_argument('--phase',choices=['functional','metadata'],required=True);parser.add_argument('--attempt',type=int,default=1);args=parser.parse_args();phase=args.phase
assert git('branch','--show-current').decode().strip()=='codex/p2-development'and not git('status','--porcelain').strip()
head=git('rev-parse','HEAD').decode().strip();cp=read('DEVELOPMENT_CHECKPOINT.json');r=read('verification/sections/363.json');index=read('CLOUD_INDEX.json')
assert cp['completed_sections']==363 and cp['next_section']==364 and cp['policy']['wrap_up_below_usage_percent']==15
assert cp['policy']['new_functional_sections_paused']is False and cp['policy']['stop_after_section']==370
assert index['current_section_label']=='第363节 + '+r['title']and index['current_completed_change']==r['new_capability']
assert index['requirements']['sha256']==sha('PROJECT_REQUIREMENTS.md')
for n,h in index['public_pointers'].items():assert sha(n)==h,n
assert r['full_suite_rerun']is False and r['last_full_validation_sha256']==sha('verification/full-350/summary.json')
if phase=='functional':assert git('rev-parse','HEAD^').decode().strip()=='356b809a63feb400967057d56d4f166d5c2e9d92'
else:
 proof=read('verification/sections/363-publication.json');assert proof['passed']and proof['ordinary_push']and proof['push_primary_exit']==0
 assert git('rev-parse','HEAD^').decode().strip()==proof['commit']==cp['last_verified_cloud_save']['commit']
 assert cp['last_verified_cloud_save']['proof_sha256']==sha('verification/sections/363-publication.json')
for group in ('source_sha256','validated_source_sha256'):
 for n,h in r[group].items():assert sha(n)==h,n
out=ROOT/(f'.cache/section363-{phase}-publication'+(f'-attempt{args.attempt}'if args.attempt>1 else''));out.mkdir()
argv=['git','push','origin','HEAD:refs/heads/codex/p2-development'];start=datetime.now(timezone.utc).isoformat()
with(out/'stdout.txt').open('xb')as stdout,(out/'stderr.txt').open('xb')as stderr:
 p=subprocess.Popen(argv,cwd=ROOT,stdin=subprocess.DEVNULL,stdout=stdout,stderr=stderr);code=p.wait()
actual={'argv':argv,'actual_retained_popen_pid':p.pid,'actual_observed_exit':code,'started_at':start,'finished_at':datetime.now(timezone.utc).isoformat(),'commit':head,'ordinary_push':True,'force_push':False}
(out/'process.json').write_bytes(enc(actual));(out/'process.exit').write_text(str(code)+'\n',encoding='ascii')
print(json.dumps({'phase':phase,'actual_push_exit':code,'stderr':(out/'stderr.txt').read_text('utf8',errors='replace')},ensure_ascii=False),flush=True);assert code==0
remote=git('ls-remote','origin','refs/heads/codex/p2-development');assert remote.decode().split()[0]==head;(out/'ls-remote.txt').write_bytes(remote)
fetch=subprocess.run(['git','fetch','origin','codex/p2-development'],cwd=ROOT,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
(out/'fetch-stdout.txt').write_bytes(fetch.stdout);(out/'fetch-stderr.txt').write_bytes(fetch.stderr)
assert fetch.returncode==0 and git('rev-parse','FETCH_HEAD').decode().strip()==head==git('rev-parse','origin/codex/p2-development').decode().strip()
tree={}
for row in git('ls-tree','-rz',head).split(b'\0'):
 if row:
  meta,name=row.split(b'\t',1);tree[name.decode('utf8')]=meta.decode().split()
assert not any(n.startswith('.local/')or n=='local-settings.json'for n in tree)
changed=set([n.decode('utf8') for n in git('diff-tree','--no-commit-id','--name-only','-z','-r',head).split(b'\0') if n]);assert not any(n.startswith(('.cache/','.local/'))or n=='local-settings.json'for n in changed)
names=changed|set(r['source_sha256'])|set(r['validated_source_sha256']);verified={}
for name in sorted(names):
 raw=(ROOT/name).read_bytes();mode,kind,blob=tree[name];digest=sha256(raw).hexdigest()
 assert mode=='100644'and kind=='blob'and sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==blob,name
 for key in('source_sha256','validated_source_sha256'):
  if name in r[key]:assert r[key][name]==digest,name
 verified[name]={'sha256':digest,'bytes':len(raw),'git_blob_sha1':blob}
assert git('rev-parse','HEAD').decode().strip()==head and not git('status','--porcelain').strip()
report={'section':363,'passed':True,'branch':'codex/p2-development','phase':phase,'commit':head,'local_HEAD':head,'remote_HEAD':head,'remote_branch':'origin/codex/p2-development','push_primary_exit':code,'push_evidence':actual,'fetch_exit':fetch.returncode,'ordinary_push':True,'force_push':False,'at_utc':datetime.now(timezone.utc).isoformat(),'verified_commit_tree_and_local_public_bytes':verified,'private_state_included':False,'next_section':364,'next_section_started':False,'source_drift':[],'full_validation_rerun':False,'last_full_receipt':'verification/full-350/summary.json','last_full_is_historical_for_current_changes':True,'current_section_label':index['current_section_label'],'worktree_clean_at_verification':True}
(out/'remote-proof.json').write_bytes(enc(report));(out/'execution-publisher.py').write_bytes(Path(__file__).read_bytes())
if phase=='functional':
 target=ROOT/'verification/sections/363-publication.json';assert not target.exists();target.write_bytes(enc(report))
 logs=ROOT/'verification/sections/363-publication-execution';logs.mkdir()
 for name in('stdout.txt','stderr.txt','process.json','process.exit','execution-publisher.py'):(logs/name).write_bytes((out/name).read_bytes())
print(json.dumps({'phase':phase,'actual_local_and_remote_commit':head,'verified_public_files':len(verified),'publication_passed':True},ensure_ascii=False))
