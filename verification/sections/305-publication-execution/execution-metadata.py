"""Root metadata only, after actual functional push and independent remote proof."""
from pathlib import Path
from hashlib import sha256
import json,subprocess,runpy
ROOT=Path(__file__).resolve().parents[1]
def git(*a):return subprocess.check_output(['git',*a],cwd=ROOT)
def encode(v):return(json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode('utf8')
proof_path=ROOT/'verification/sections/305-publication.json';proof=json.loads(proof_path.read_bytes());commit=proof['commit']
assert proof['passed']and proof['section']==305 and proof['push_primary_exit']==0 and proof['ordinary_push']and not proof['force_push']
assert git('branch','--show-current').decode().strip()=='codex/p2-development'
assert git('rev-parse','HEAD').decode().strip()==commit==proof['local_HEAD']==proof['remote_HEAD']
assert git('ls-remote','origin','refs/heads/codex/p2-development').decode().split()[0]==commit
assert not git('diff','--name-only').strip()and not git('diff','--cached','--name-only').strip(),'Unexpected changes after functional commit.'
cp_path=ROOT/'DEVELOPMENT_CHECKPOINT.json';cp=json.loads(cp_path.read_bytes())
assert cp['completed_sections']==305 and cp['next_section']==306 and cp['last_verified_cloud_save']['section']==304
assert cp['policy']['usage_wrap_up_triggered']is True and cp['policy']['usage_wrap_up_after_active_section']==305
cp['historical_before305_publication']=cp['last_verified_cloud_save']
cp['last_verified_cloud_save']={'section':305,'scope':'current_functional_section','binding':'verified_remote_commit','commit':commit,'proof':'verification/sections/305-publication.json','proof_sha256':sha256(proof_path.read_bytes()).hexdigest()}
cp['batch_status']='P3_SECTION305_PUBLISHED_USAGE_WRAPUP_COMPLETE'
cp['next_action']='第305节完整验收、索引与要求、普通发布及实际远端核对已完成。收尾阈值已恢复严格低于15%；按用户明确要求在305后暂停，306未启动，等待用户恢复。后续优先P3，下一定期全量320；P2/P1与识别剩余项保留。'
cp['policy']['new_functional_sections_paused']=True
cp['policy']['usage_wrap_up_completed']=True
cp['policy']['development_paused_by_latest_user_request']=True
cp['current_batch'].update(status=cp['batch_status'],batch_closed=True,next_section_started=False,next_section=306,completed_sections=305)
cp['current_section_save']['commit_reference']='enclosing publication metadata snapshot; separately bound actual305 functional source/acceptance/requirements/index commit verified remotely'
cp['cloud_publication_closeout']={'section':305,'functional_commit':commit,'functional_source_bytes_unchanged':True,'proof':'verification/sections/305-publication.json','current_commit_kind':'publication metadata only; no new functional section','next_section':306,'batch_closed':True,'next_section_started':False,'usage_wrap_up_completed':True,'numeric_continuation_target':None}
pending='<!-- section305-publication-pending -->当前为本地完整验收完成，普通推送与实际远端核对尚待完成。'
published='305功能提交'+commit+'已普通推送并核对真实远端及公开文件字节，证明verification/sections/305-publication.json。本次仅保存发布元数据，不增加功能节数；阈值已恢复15%，完整收尾后按用户明确要求暂停，306未启动，等待用户恢复。'
for name in('AGENTS.md','PROJECT_REQUIREMENTS.md','PROJECT_COMPLETED.md','WORK_IN_PROGRESS.md','CLOUD_HANDOFF.md'):
 p=ROOT/name;text=p.read_text('utf8');assert text.count(pending)==1,(name,text.count(pending));p.write_bytes(text.replace(pending,published,1).encode('utf8'))
cp_path.write_bytes(encode(cp));runpy.run_path(str(ROOT/'scripts/update_cloud_index.py'))['update'](ROOT)
folder=ROOT/'verification/sections/305-publication-execution';(folder/'execution-metadata.py').write_bytes(Path(__file__).read_bytes())
print(json.dumps({'section':305,'actual_functional_commit':commit,'metadata_generated':True,'new306_started':False,'usage_wrap_up_completed':True,'private_state_or_source_changed':False}))
