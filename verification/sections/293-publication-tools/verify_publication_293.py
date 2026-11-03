from datetime import datetime,timezone,timedelta
from pathlib import Path
from hashlib import sha256
import json,subprocess
ROOT=Path(__file__).resolve().parents[1]
def git(args,**kw):return subprocess.check_output(['git',*args],cwd=ROOT,**kw)
def sha(raw):return sha256(raw).hexdigest()
def load(p):return json.loads((ROOT/p).read_bytes())
def write(name,value):(ROOT/name).write_bytes((json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
head=git(['rev-parse','HEAD']).decode().strip()
assert head=='6b59ad14e30226fab12d1f3447da96b80208ff63'
assert git(['branch','--show-current']).decode().strip()=='codex/p2-development'
assert not git(['status','--porcelain'])
push=load('.cache/section293-functional-push.json')
assert push['exit_code']==0 and push['commit']==head and push['ordinary_push'] is True
remote=git(['ls-remote','origin','refs/heads/codex/p2-development']).decode().strip()
assert remote.split()[0]==head
changed=git(['diff-tree','--no-commit-id','--name-only','-r',head]).decode().splitlines()
stage=load('.cache/section293-stage-readback.json')
assert set(changed)==set(stage['staged_and_disk_sha256'])
section=load('verification/sections/293.json')
necessary=load(section['necessary_validation']['receipt'])
window=load(section['native_windows_validation']['receipt'])
expected=dict(stage['staged_and_disk_sha256'])
for mapping in (section['source_sha256'],necessary['source_sha256_after'],window['source_sha256_after']):
    for name,value in mapping.items():
        assert not name.startswith(('.cache/','.local/')) and name!='local-settings.json'
        assert name not in expected or expected[name]==value
        expected[name]=value
names=sorted(expected)
blobs=git(['cat-file','--batch'],input=(''.join(head+':'+p+'\n' for p in names)).encode('utf8'))
offset=0
for name in names:
    end=blobs.index(b'\n',offset);header=blobs[offset:end].split();assert header[1]==b'blob'
    size=int(header[2]);offset=end+1;raw=blobs[offset:offset+size];offset+=size
    assert blobs[offset:offset+1]==b'\n';offset+=1
    assert sha(raw)==expected[name] and raw==(ROOT/name).read_bytes(),name
assert offset==len(blobs)
public_push='verification/sections/293-publication-push.json'
proof_path='verification/sections/293-publication.json'
assert not (ROOT/public_push).exists() and not (ROOT/proof_path).exists()
(ROOT/public_push).write_bytes((ROOT/'.cache/section293-functional-push.json').read_bytes())
proof={'section':293,'passed':True,'branch':'codex/p2-development','commit':head,'functional_commit':head,
 'local_HEAD':head,'remote_HEAD':head,'remote_branch':'origin/codex/p2-development','push_primary_exit':push['exit_code'],
 'actual_push_receipt':public_push,'actual_push_receipt_sha256':sha((ROOT/public_push).read_bytes()),
 'verified_at_Beijing':datetime.now(timezone(timedelta(hours=8))).isoformat(),
 'actual_remote_ref_command':['git','ls-remote','origin','refs/heads/codex/p2-development'],
 'actual_remote_ref_stdout':remote,'verified_public_files':{p:expected[p] for p in changed},
 'verified_necessary_and_window_public_source_files':len(expected),
 'all_changed_public_files_and_current_validated_sources_match_commit':True,
 'private_files_included':False,'source_receipt_matches_verified_git_bytes':True,
 'full290_is_historical_not_relabelled_for293':True,
 'scope':'Functional293 one-hop future result and scene reader, actual80 necessary and54 unique native checks; both source-builder failures retained. Metadata adds no functional section.'}
write(proof_path,proof)
cp=load('DEVELOPMENT_CHECKPOINT.json');cp['historical_before293_publication']=cp['last_verified_cloud_save']
cp['last_verified_cloud_save']={'section':293,'scope':'current_functional_section','binding':'verified_remote_commit',
 'commit':head,'proof':proof_path,'proof_sha256':sha((ROOT/proof_path).read_bytes())}
cp['batch_status']='P3_SECTION293_PUBLISHED_CONTINUATION_READY';cp['current_batch']['status']=cp['batch_status']
cp['cloud_publication_closeout']={'section':293,'functional_commit':head,'functional_source_bytes_unchanged':True,
 'proof':proof_path,'current_commit_kind':'publication metadata; no additional functional section',
 'next_section':294,'batch_closed':False,'next_section_started':False,'numeric_continuation_target':None}
write('DEVELOPMENT_CHECKPOINT.json',cp)
note=('发布核对：功能提交'+head+'已普通推送并核对实际远端；'+str(len(changed))+
 '份变更公开文件及最终必要/窗口来源与提交逐字节一致，证明'+proof_path+'。仅追加发布元数据，不增加功能节数。\n\n')
for name in ('WORK_IN_PROGRESS.md','PROJECT_COMPLETED.md'):
    p=ROOT/name;text=p.read_text(encoding='utf8');idx=text.index('## 功能第292节')
    current=text[:idx];assert current.count('待普通推送核对。')==1
    current=current.replace('待普通推送核对。','已普通推送并核对实际远端，详见下方发布证明。',1)
    p.write_bytes((current+note+text[idx:]).encode('utf8'))
updates={'PROJECT_REQUIREMENTS.md':('待普通推送核对，源码/要求/回执/索引同提交。',
 '293功能提交'+head+'已普通推送并核对实际远端，公开证明'+proof_path+'；源码/要求/回执/索引一并保存。'),
 'AGENTS.md':('本节待普通推送并核对真实远端，源码/要求/验收/索引同提交。',
 '293功能提交'+head+'已普通推送并核对实际远端，发布证明'+proof_path+'；源码/要求/验收/索引一并保存。')}
for name,(old,new) in updates.items():
    p=ROOT/name;text=p.read_text(encoding='utf8');assert text.count(old)==1
    p.write_bytes(text.replace(old,new,1).encode('utf8'))
print(json.dumps({'section':293,'verified_functional_commit':head,'actual_remote_matches':True,
 'changed_public_files':len(changed),'all_verified_public_files':len(expected),'next_section_started':False}))
