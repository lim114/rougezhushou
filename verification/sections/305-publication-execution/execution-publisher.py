"""Root explicit ordinary publication, only after complete305 acceptance."""
from pathlib import Path
from datetime import datetime,timezone
from hashlib import sha256,sha1
import argparse,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)
def encode(v):return(json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode('utf8')
def digest(p):return sha256(p.read_bytes()).hexdigest()
def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--ordinary-push-and-verify',action='store_true');parser.add_argument('--functional-commit',required=True);args=parser.parse_args()
 assert args.ordinary_push_and_verify
 assert git('branch','--show-current').decode().strip()=='codex/p2-development'
 commit=git('rev-parse','HEAD').decode().strip();assert commit==args.functional_commit and len(commit)==40
 assert not git('status','--porcelain').strip(),'Complete functional snapshot must be clean before actual push.'
 section=json.loads((ROOT/'verification/sections/305.json').read_bytes());full=json.loads((ROOT/'verification/full-305/summary.json').read_bytes())
 assert section['section']==305 and full['available_checks_passed']is True and full['after_section']==305
 assert full['scope_not_reduced']is True and full['actual_validation_attempt']==2
 cp=json.loads((ROOT/'DEVELOPMENT_CHECKPOINT.json').read_bytes());assert cp['completed_sections']==305 and cp['next_section']==306
 folder=ROOT/'.cache/section305-functional-publication';folder.mkdir()
 argv=['git','push','origin','HEAD:refs/heads/codex/p2-development']
 started=datetime.now(timezone.utc).isoformat()
 with(folder/'stdout.log').open('xb')as out,(folder/'stderr.log').open('xb')as err:
  process=subprocess.Popen(argv,cwd=ROOT,stdin=subprocess.DEVNULL,stdout=out,stderr=err)
  code=process.wait()
 push={'kind':'actual_retained_subprocess_ordinary_git_push','argv':argv,'started_at':started,'finished_at':datetime.now(timezone.utc).isoformat(),'exit_code':code,'owned_popen_retained':True,'pid':process.pid,'force_push':False,'commit':commit}
 (folder/'process.json').write_bytes(encode(push));(folder/'process.exit').write_text(str(code)+'\n',encoding='ascii')
 print(json.dumps({'actual_push_exit':code,'stdout':(folder/'stdout.log').read_text('utf8',errors='replace'),'stderr':(folder/'stderr.log').read_text('utf8',errors='replace')},ensure_ascii=False),flush=True)
 if code:raise SystemExit(code)
 remote=git('ls-remote','origin','refs/heads/codex/p2-development').decode().split()[0];assert remote==commit
 fetch=subprocess.run(['git','fetch','origin','codex/p2-development'],cwd=ROOT,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 assert fetch.returncode==0,fetch.stderr.decode('utf8',errors='replace')
 assert git('rev-parse','FETCH_HEAD').decode().strip()==commit
 assert git('rev-parse','HEAD').decode().strip()==commit and not git('status','--porcelain').strip()
 tree={}
 for row in git('ls-tree','-rz',commit).split(b'\0'):
  if row:
   meta,name=row.split(b'\t',1);tree[name.decode('utf8')]=meta.decode().split()
 changed=git('diff-tree','--no-commit-id','--name-only','-r',commit).decode('utf8').splitlines()
 freeze=json.loads((ROOT/full['source_freeze']).read_bytes())
 frozen_source={**freeze['source_sha256'],**freeze['supplemental_public_inputs_sha256']}
 names=set(changed)|set(frozen_source)
 for field in('source_sha256','validated_source_sha256'):names.update(section[field])
 verified={}
 for name in sorted(names):
  assert not name.startswith(('.cache/','.local/'))and name!='local-settings.json'
  p=ROOT/name;assert p.is_file()and not p.is_symlink();raw=p.read_bytes()
  mode,kind,blob=tree[name];assert mode=='100644'and kind=='blob'
  assert sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==blob,name
  h=sha256(raw).hexdigest()
  if name in frozen_source:assert h==frozen_source[name],name
  for field in('source_sha256','validated_source_sha256'):
   if name in section[field]:assert section[field][name]==h,name
  verified[name]={'sha256':h,'bytes':len(raw),'git_blob_sha1':blob}
 proof={'section':305,'passed':True,'branch':'codex/p2-development','commit':commit,'local_HEAD':commit,'remote_HEAD':remote,'remote_branch':'origin/codex/p2-development','push_primary_exit':code,'push_evidence':push,'push_stdout':(folder/'stdout.log').read_text('utf8',errors='replace'),'push_stderr':(folder/'stderr.log').read_text('utf8',errors='replace'),'fetch_exit':fetch.returncode,'actual_remote_verified_via':'git ls-remote plus ordinary fetch and FETCH_HEAD','at_utc':datetime.now(timezone.utc).isoformat(),'ordinary_push':True,'force_push':False,'changed_public_files':changed,'verified_commit_tree_and_local_public_bytes':verified,'private_state_included':False,'functional_section_count':305,'next_section':306,'next_section_started':False,'full_validation_rerun':True,'full_summary_sha256':digest(ROOT/'verification/full-305/summary.json')}
 destination=ROOT/'verification/sections/305-publication.json';assert not destination.exists();destination.write_bytes(encode(proof))
 logs=ROOT/'verification/sections/305-publication-execution';logs.mkdir()
 for name in('stdout.log','stderr.log','process.json','process.exit'):(logs/name).write_bytes((folder/name).read_bytes())
 (logs/'execution-publisher.py').write_bytes(Path(__file__).read_bytes())
 print(json.dumps({'functional_commit':commit,'actual_remote':remote,'verified_public_files':len(verified),'changed_public_files':len(changed),'proof':destination.relative_to(ROOT).as_posix(),'proof_sha256':digest(destination),'metadata_still_pending':True},ensure_ascii=False))
if __name__=='__main__':main()
