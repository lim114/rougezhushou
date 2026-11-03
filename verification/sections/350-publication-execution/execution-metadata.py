from pathlib import Path
from hashlib import sha256
import json,runpy,subprocess
ROOT=Path(__file__).resolve().parents[1]
def git(*a):return subprocess.check_output(['git',*a],cwd=ROOT)
def enc(v):return(json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode('utf8')
path=ROOT/'verification/sections/350-publication.json';proof=json.loads(path.read_bytes());commit=proof['commit']
assert proof['passed']and proof['push_primary_exit']==0 and proof['ordinary_push']and not proof['force_push']
assert git('rev-parse','HEAD').decode().strip()==commit==git('ls-remote','origin','refs/heads/codex/p2-development').decode().split()[0]
assert not git('diff','--name-only').strip()and not git('diff','--cached','--name-only').strip()
cp_path=ROOT/'DEVELOPMENT_CHECKPOINT.json';cp=json.loads(cp_path.read_bytes())
assert cp['completed_sections']==350 and cp['next_section']==351 and cp['last_verified_cloud_save']['section']==349
cp['historical_before350_publication']=cp['last_verified_cloud_save']
cp['last_verified_cloud_save']={'section':350,'scope':'current_functional_section','binding':'verified_remote_commit','commit':commit,'proof':'verification/sections/350-publication.json','proof_sha256':sha256(path.read_bytes()).hexdigest()}
cp['batch_status']='P3_SECTION350_PUBLISHED_PAUSED';cp['current_batch'].update(status=cp['batch_status'],batch_closed=True,next_section=351,next_section_started=False)
assert cp['policy']['new_functional_sections_paused']is False and cp['policy']['stop_after_section']==350
cp['policy'].update(new_functional_sections_paused=True,development_paused_by_latest_user_request=True,pause_after_active_section_requested=True,current_user_batch_completed=True)
cp['next_action']='第350节 + 行动奖励的当前版本候选、继承来源与专门条件，已本机必要验收并普通推送核对。按用户要求完成本节后暂停，351未启动；等待明确继续后才恢复P3实际剩余缺口；P3/P2/P1均未完成，识别优化最后，下次定期全量365。'
cp['cloud_publication_closeout']={'section':350,'functional_commit':commit,'proof':'verification/sections/350-publication.json','current_commit_kind':'publication metadata only','next_section_started':False,'development_paused':True}
cp_path.write_bytes(enc(cp))
old='<!-- section350-publication-pending -->本地验收完成，普通推送及真实远端核对待完成。'
new='第350节功能提交'+commit+'已普通推送并核对真实远端及'+str(len(proof['verified_commit_tree_and_local_public_bytes']))+'份相关公开文件字节，证明verification/sections/350-publication.json。本次仅保存发布元数据，不增加功能节数；本批完成后已暂停，351尚未启动，等待用户明确继续；恢复后下一定期全量365。P3/P2/P1未完成，资料目录不冒充实际菜单、服务器资格或实际领取；私人状态及实机游戏/聊天未纳入云端。'
for name in('AGENTS.md','PROJECT_COMPLETED.md','WORK_IN_PROGRESS.md','PROJECT_REQUIREMENTS.md','CLOUD_HANDOFF.md'):
 p=ROOT/name;raw=p.read_bytes();s=raw.decode('utf8');assert s.count(old)==1,(name,s.count(old));p.write_bytes(s.replace(old,new,1).encode('utf8'))
runpy.run_path(str(ROOT/'scripts/update_cloud_index.py'))['update'](ROOT)
out=ROOT/'verification/sections/350-publication-execution';(out/'execution-metadata.py').write_bytes(Path(__file__).read_bytes())
print(json.dumps({'section':350,'functional_commit':commit,'metadata_ready_not_yet_pushed':True,'development_paused':True},ensure_ascii=False))
