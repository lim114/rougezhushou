"""Resume read verification of one genuinely successful push; never push or commit."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,subprocess,json,runpy,hashlib
R=Path(__file__).resolve().parents[1];base=runpy.run_path(str(R/'.cache/player_batch_pipeline.py'))
p=argparse.ArgumentParser();p.add_argument('--phase',choices=('functional','metadata'),required=True);p.add_argument('--push-output',required=True);p.add_argument('--expected-commit',required=True);args=p.parse_args()
git=base['git'];head=git('rev-parse','HEAD').decode().strip();assert head==args.expected_commit
assert git('branch','--show-current').decode().strip()=='codex/p2-development'
folder=R/args.push_output;push=json.loads((folder/'process.json').read_bytes())
assert push['actual_observed_exit']==0 and push['ordinary_push']is True and push['force_push']is False
assert push['argv']==['git','push','origin','HEAD:refs/heads/codex/p2-development']
source_before=base['source']();assert source_before==base['read']('verification/sections/410-source-audit.json')['source_sha256']
index=1
while(folder/f'read-recovery-{index}').exists():index+=1
out=folder/f'read-recovery-{index}';out.mkdir()
(out/'source.py').write_bytes(Path(__file__).read_bytes())
def read_observed(label,arguments):
    for attempt in range(1,4):
        target=out/f'{label}-{attempt}';target.mkdir();argv=['git',*arguments]
        with(target/'stdout.txt').open('xb')as stdout,(target/'stderr.txt').open('xb')as stderr:
            child=subprocess.Popen(argv,cwd=R,stdout=stdout,stderr=stderr);code=child.wait()
        record={'argv':argv,'actual_retained_Popen_pid':child.pid,'actual_observed_exit':code,'read_or_local_fetch_only':True,'push_or_commit_performed':False}
        (target/'process.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n','utf8')
        if code==0:return(target/'stdout.txt').read_bytes()
        print(json.dumps({'read_stage':label,'attempt':attempt,'actual_exit':code,'failed_original_preserved':True}),flush=True)
    raise RuntimeError('Read verification remained unavailable; no publication success invented.')
remote=read_observed('ls-remote',['ls-remote','origin','refs/heads/codex/p2-development']).decode().split()[0];assert remote==head
read_observed('fetch',['fetch','origin','codex/p2-development'])
assert git('rev-parse','origin/codex/p2-development').decode().strip()==head
names={v.decode('utf8')for v in git('diff-tree','--no-commit-id','--name-only','-r','-z',head).split(b'\0')if v}|set(source_before)
tree={}
for row in git('ls-tree','-rz',head).split(b'\0'):
    if row:
        meta,name=row.split(b'\t',1);tree[name.decode()]=meta.decode().split()
proofs={}
for name in sorted(names):
    assert not name.startswith(('.local/','.cache/'))and name!='local-settings.json'
    raw=(R/name).read_bytes();mode,kind,blob=tree[name]
    assert mode=='100644'and kind=='blob'and hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==blob,name
    proofs[name]={'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'git_blob_sha1':blob}
assert base['source']()==source_before and git('rev-parse','HEAD').decode().strip()==head
report={'section':410,'passed':True,'branch':'codex/p2-development','commit':head,'local_HEAD':head,'remote_HEAD':remote,'remote_branch':'origin/codex/p2-development','push_primary_exit':push['actual_observed_exit'],'ordinary_push':True,'force_push':False,'phase':args.phase,'verified_commit_tree_and_local_public_bytes':proofs,'private_state_included':False,'full_validation_rerun':True,'last_full_is_historical_for_current_changes':False,'publication_itself_reexecuted_tests':False,'at_UTC':datetime.now(timezone.utc).isoformat()}
base['write']((out/'remote-proof.json').relative_to(R).as_posix(),report)
base['write']((out/'recovery-binding.json').relative_to(R).as_posix(),{'original_successful_push':base['pin']((folder/'process.json').relative_to(R).as_posix()),'expected_commit_checked_against_actual_HEAD':head,'source_unchanged':True,'new_push_or_commit_performed':False,'recovery_source':base['pin']((out/'source.py').relative_to(R).as_posix())})
if args.phase=='functional':base['write']('verification/sections/410-publication.json',report)
print(json.dumps({'phase':args.phase,'section':410,'actual_verified_remote_commit':head,'public_files_compared':len(proofs),'new_pushes':0,'read_recovery':out.relative_to(R).as_posix()}),flush=True)
