from pathlib import Path
from hashlib import sha256
import json,runpy,subprocess
ROOT=Path(__file__).resolve().parents[1]
def git(*a):return subprocess.check_output(['git',*a],cwd=ROOT)
def enc(v):return (json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode('utf8')
path=ROOT/'verification/sections/309-publication.json';proof=json.loads(path.read_bytes());commit=proof['commit']
assert proof['passed'] and proof['push_primary_exit']==0 and proof['ordinary_push'] and not proof['force_push']
assert git('rev-parse','HEAD').decode().strip()==commit==git('ls-remote','origin','refs/heads/codex/p2-development').decode().split()[0]
assert not git('diff','--name-only').strip() and not git('diff','--cached','--name-only').strip()
cp_path=ROOT/'DEVELOPMENT_CHECKPOINT.json';cp=json.loads(cp_path.read_bytes())
assert cp['completed_sections']==309 and cp['next_section']==310 and cp['last_verified_cloud_save']['section']==308
cp['historical_before309_publication']=cp['last_verified_cloud_save']
cp['last_verified_cloud_save']={'section':309,'scope':'current_functional_section','binding':'verified_remote_commit','commit':commit,'proof':'verification/sections/309-publication.json','proof_sha256':sha256(path.read_bytes()).hexdigest()}
cp['batch_status']='P3_SECTION309_PUBLISHED'
cp['current_batch'].update(status=cp['batch_status'],batch_closed=True,next_section=310,next_section_started=False)
cp['next_action']='第309节 + 畸症首领按形态查看招式与转换条件，已验收并普通推送核对。继续P3剩余节点/敌人/固定地图事项；下一定期全量320，310未启动。'
cp['cloud_publication_closeout']={'section':309,'functional_commit':commit,'proof':'verification/sections/309-publication.json','current_commit_kind':'publication metadata only','next_section_started':False,'development_paused':False}
cp_path.write_bytes(enc(cp))
old='<!-- section309-publication-pending -->当前为本地验收完成，普通推送与真实远端核对尚待完成。'
new='第309节功能提交'+commit+'已普通推送并核对真实远端及公开文件字节，证明verification/sections/309-publication.json。本次仅保存发布元数据，不增加功能节数；继续P3，310未启动，下一定期全量320。'
for name in ('AGENTS.md','PROJECT_COMPLETED.md','WORK_IN_PROGRESS.md','PROJECT_REQUIREMENTS.md','CLOUD_HANDOFF.md'):
 p=ROOT/name;s=p.read_text('utf8');assert s.count(old)==1,(name,s.count(old));p.write_text(s.replace(old,new,1),encoding='utf8')
runpy.run_path(str(ROOT/'scripts/update_cloud_index.py'))['update'](ROOT)
out=ROOT/'verification/sections/309-publication-execution';(out/'execution-metadata.py').write_bytes(Path(__file__).read_bytes())
print(json.dumps({'section':309,'functional_commit':commit,'metadata_ready_not_yet_pushed':True,'development_paused':False}))
