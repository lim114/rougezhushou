from pathlib import Path
from hashlib import sha256
import json,runpy,subprocess
ROOT=Path(__file__).resolve().parents[1]
def git(*a):return subprocess.check_output(['git',*a],cwd=ROOT)
def enc(v):return(json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode('utf8')
path=ROOT/'verification/sections/371-publication.json';proof=json.loads(path.read_bytes());commit=proof['commit']
assert proof['passed']and proof['push_primary_exit']==0 and proof['ordinary_push']and not proof['force_push']
assert git('rev-parse','HEAD').decode().strip()==commit==git('ls-remote','origin','refs/heads/codex/p2-development').decode().split()[0]
assert not git('diff','--name-only').strip()and not git('diff','--cached','--name-only').strip()
cp_path=ROOT/'DEVELOPMENT_CHECKPOINT.json';cp=json.loads(cp_path.read_bytes())
assert cp['completed_sections']==371 and cp['next_section']==372 and cp['last_verified_cloud_save']['section']==370
cp['historical_before371_publication']=cp['last_verified_cloud_save']
cp['last_verified_cloud_save']={'section':371,'scope':'current_functional_section','binding':'verified_remote_commit','commit':commit,'proof':'verification/sections/371-publication.json','proof_sha256':sha256(path.read_bytes()).hexdigest()}
cp['batch_status']='P3_SECTION371_PUBLISHED';cp['current_batch'].update(status=cp['batch_status'],batch_closed=False,next_section=372,next_section_started=False)
assert cp['policy']['new_functional_sections_paused']is False and cp['policy']['stop_after_section']==380
cp['next_action']='第371节 + 从敌人反查准确出怪记录与条件分支，已本机必要验收并普通推送核对。后续372接续P3当前事件条件、完整奖励池与固定地图实际剩余缺口，未启动；P3/P2/P1均未完成，识别优化最后，下次定期全量380。'
cp['cloud_publication_closeout']={'section':371,'functional_commit':commit,'proof':'verification/sections/371-publication.json','current_commit_kind':'publication metadata only','next_section_started':False,'development_paused':False}
cp_path.write_bytes(enc(cp))
old='<!-- section371-publication-pending -->本地验收完成，普通推送及真实远端核对待完成。'
new='第371节功能提交'+commit+'已普通推送并核对真实远端及'+str(len(proof['verified_commit_tree_and_local_public_bytes']))+'份相关公开文件字节，证明verification/sections/371-publication.json。本次仅保存发布元数据，不增加功能节数；后续372尚未启动；按本次授权继续至380并完整收尾后暂停，下一定期全量380。P3/P2/P1未完成，资料对照不冒充本局实际状态/生成/生效/结算；私人状态及实机游戏/聊天未纳入云端。'
for name in('AGENTS.md','PROJECT_COMPLETED.md','WORK_IN_PROGRESS.md','PROJECT_REQUIREMENTS.md','CLOUD_HANDOFF.md'):
 p=ROOT/name;raw=p.read_bytes();s=raw.decode('utf8');assert s.count(old)==1,(name,s.count(old));p.write_bytes(s.replace(old,new,1).encode('utf8'))
runpy.run_path(str(ROOT/'scripts/update_cloud_index.py'))['update'](ROOT)
out=ROOT/'verification/sections/371-publication-execution';(out/'execution-metadata.py').write_bytes(Path(__file__).read_bytes())
print(json.dumps({'section':371,'functional_commit':commit,'metadata_ready_not_yet_pushed':True,'development_paused':False},ensure_ascii=False))
