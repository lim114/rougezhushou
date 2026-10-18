from pathlib import Path
from hashlib import sha256,sha1
from datetime import datetime,timezone
import argparse,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)
def read(n):return json.loads((ROOT/n).read_bytes())
def enc(v):return (json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode('utf8')
def sha(n):return sha256((ROOT/n).read_bytes()).hexdigest()
args=argparse.ArgumentParser();args.add_argument('--phase',choices=['functional','metadata'],required=True);phase=args.parse_args().phase
assert git('branch','--show-current').decode().strip()=='codex/p2-development' and not git('status','--porcelain').strip()
head=git('rev-parse','HEAD').decode().strip();cp=read('DEVELOPMENT_CHECKPOINT.json');r=read('verification/sections/306.json');index=read('CLOUD_INDEX.json')
assert cp['completed_sections']==306 and cp['next_section']==307 and cp['policy']['wrap_up_below_usage_percent']==15
assert cp['policy']['development_paused_by_latest_user_request'] is False
assert index['current_section_label']=='第306节 + '+r['title'] and index['current_completed_change']==r['new_capability']
assert index['requirements']['sha256']==sha('PROJECT_REQUIREMENTS.md')
for name,h in index['public_pointers'].items():assert sha(name)==h,name
if phase=='functional':assert git('rev-parse','HEAD^').decode().strip()=='603e1700c3ae4523ac2ff3d5495f127dc30556df'
else:
 proof=read('verification/sections/306-publication.json');assert proof['passed'] and proof['push_primary_exit']==0 and proof['ordinary_push']
 assert git('rev-parse','HEAD^').decode().strip()==proof['commit']==cp['last_verified_cloud_save']['commit']
 assert cp['last_verified_cloud_save']['proof_sha256']==sha('verification/sections/306-publication.json')
folder=ROOT/('.cache/section306-'+phase+'-publication');folder.mkdir()
argv=['git','push','origin','HEAD:refs/heads/codex/p2-development'];started=datetime.now(timezone.utc).isoformat()
with (folder/'stdout.txt').open('xb') as stdout,(folder/'stderr.txt').open('xb') as stderr:
 p=subprocess.Popen(argv,cwd=ROOT,stdin=subprocess.DEVNULL,stdout=stdout,stderr=stderr);code=p.wait()
actual={'argv':argv,'actual_retained_popen_pid':p.pid,'actual_observed_exit':code,'started_at':started,'finished_at':datetime.now(timezone.utc).isoformat(),'commit':head,'ordinary_push':True,'force_push':False}
(folder/'process.json').write_bytes(enc(actual));(folder/'process.exit').write_text(str(code)+'\n',encoding='ascii')
print(json.dumps({'phase':phase,'actual_push_exit':code,'stderr':(folder/'stderr.txt').read_text('utf8',errors='replace')},ensure_ascii=False),flush=True)
assert code==0,'Actual ordinary push failed.'
remote=git('ls-remote','origin','refs/heads/codex/p2-development');assert remote.decode().split()[0]==head
(folder/'ls-remote.txt').write_bytes(remote)
fetch=subprocess.run(['git','fetch','origin','codex/p2-development'],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE,stdin=subprocess.DEVNULL)
(folder/'fetch-stdout.txt').write_bytes(fetch.stdout);(folder/'fetch-stderr.txt').write_bytes(fetch.stderr)
assert fetch.returncode==0 and git('rev-parse','FETCH_HEAD').decode().strip()==head==git('rev-parse','origin/codex/p2-development').decode().strip()
tree={}
for row in git('ls-tree','-rz',head).split(b'\0'):
 if row:
  meta,name=row.split(b'\t',1);tree[name.decode('utf8')]=meta.decode().split()
assert not any(n.startswith('.local/') or n=='local-settings.json' for n in tree)
changed=set(git('diff-tree','--no-commit-id','--name-only','-r',head).decode('utf8').splitlines())
assert not any(n.startswith(('.cache/','.local/')) or n=='local-settings.json' for n in changed)
names=changed|set(r['source_sha256'])|set(r['validated_source_sha256']);verified={}
for name in sorted(names):
 raw=(ROOT/name).read_bytes();mode,kind,blob=tree[name];h=sha256(raw).hexdigest()
 assert mode=='100644' and kind=='blob' and sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==blob,name
 for key in ('source_sha256','validated_source_sha256'):
  if name in r[key]:assert r[key][name]==h,name
 verified[name]={'sha256':h,'bytes':len(raw),'git_blob_sha1':blob}
assert git('rev-parse','HEAD').decode().strip()==head and not git('status','--porcelain').strip()
report={'section':306,'passed':True,'branch':'codex/p2-development','phase':phase,'commit':head,'local_HEAD':head,'remote_HEAD':head,'remote_branch':'origin/codex/p2-development','push_primary_exit':code,'push_evidence':actual,'fetch_exit':fetch.returncode,'ordinary_push':True,'force_push':False,'at_utc':datetime.now(timezone.utc).isoformat(),'verified_commit_tree_and_local_public_bytes':verified,'private_state_included':False,'next_section':307,'next_section_started':False,'source_drift':[],'full_validation_rerun':False,'last_full_receipt':'verification/full-305/summary.json','current_section_label':index['current_section_label'],'worktree_clean_at_verification':True}
(folder/'remote-proof.json').write_bytes(enc(report));(folder/'execution-publisher.py').write_bytes(Path(__file__).read_bytes())
if phase=='functional':
 target=ROOT/'verification/sections/306-publication.json';assert not target.exists();target.write_bytes(enc(report))
 logs=ROOT/'verification/sections/306-publication-execution';logs.mkdir()
 for name in ('stdout.txt','stderr.txt','process.json','process.exit','execution-publisher.py'):(logs/name).write_bytes((folder/name).read_bytes())
print(json.dumps({'phase':phase,'actual_local_and_remote_commit':head,'verified_public_files':len(verified),'section_label':index['current_section_label'],'publication_passed':True},ensure_ascii=False))
