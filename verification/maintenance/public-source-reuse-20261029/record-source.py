from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import json,runpy,sys,subprocess
R=Path(__file__).resolve().parents[1];sys.path[:0]=[str(R),str(R/'scripts')]
from player_ui_verification import source_hashes
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R).decode().strip()
assert head=='9534fba280ef999630b96891a0f131c07a27298d'
cp=json.loads((R/'DEVELOPMENT_CHECKPOINT.json').read_bytes());assert cp['completed_sections']==412 and not cp['current_batch']['next_section_started']
cp['policy'].update(public_source_reuse_preferred=True,public_source_reuse_requires_local_adaptation=True,
    public_source_reuse_guidance='AGENTS.md#公开源码优先复用与本机适配2026-10-29',dlc1_missing_content_audit_pending=True)
cp['next_action']='按新要求优先参考相关公开源码，核实可复用范围并适配本机；继续核对DLC1遗漏内容与界面入口。参考程序源码未取得，不把空发布仓库或视频称为源码。当前仍完成412，413未启动；下一到期全量425。'
(R/'DEVELOPMENT_CHECKPOINT.json').write_bytes((json.dumps(cp,ensure_ascii=False,indent=2)+'\n').encode())
p=R/'PROJECT_PROGRESS.md';text=p.read_text('utf8')
needle='| P3 | 视频效果对齐剩余交互 | '
assert text.count(needle)==1
text=text.replace(needle,needle+'核对并补齐DLC1目录、节点事件、物品池及入口的遗漏；',1);p.write_bytes(text.encode())
p=R/'WORK_IN_PROGRESS.md';text=p.read_text('utf8');marker='<!-- source-reuse-current:start -->'
assert marker not in text
note='''<!-- source-reuse-current:start -->
## 后续执行要求 · 公开源码优先复用与DLC1补漏

2026-10-29：用户明确要求参考相关公开项目，能复用就优先复用并适配本机，且将此规则写入AGENTS.md。规则已同步PROJECT_REQUIREMENTS.md。参考程序源码仍未确认；用户说明此前以为已经找到，并未提供额外源码位置。不得把视频、空发布仓库和公开资料包当作原程序源码。

DLC1漏项核对同时继续：已实际读取授权的路标公开资料进行初查，接下来核对版本化成员、现有归一化目录和界面入口，不因来源标为DLC1就断言已完整收录。此处只记录要求与调查断点，没有修改实现或计为完成；功能仍412，413未启动，下一到期全量425。隐私、只读、不自动选路和实际交付要求保持。
<!-- source-reuse-current:end -->

'''
end='<!-- player-batch-current:end -->';assert text.count(end)==1
text=text.replace(end,end+'\n\n'+note,1);p.write_bytes(text.encode())
tool=runpy.run_path(str(R/'scripts/update_cloud_index.py'));tool['update'](R);valid=tool['validate_delivery'](R,cp)
source=source_hashes();previous=json.loads((R/'verification/sections/412-source-audit.json').read_bytes())['source_sha256'];assert source==previous
out=R/'verification/maintenance/public-source-reuse-20261029';out.mkdir(exist_ok=False)
record={'kind':'requirements_maintenance','completed_sections':412,'next_section':413,'next_section_started':False,
    'functional_section_increment':0,'implementation_changed':False,'source_equals_412_audit':True,
    'index_validation':valid,'highest_five_project_requirements_retained':True,
    'user_clarified_no_reference_source_link_available':True,'dlc1_gap_audit_pending':True,
    'reference_source_acquired_or_reused_claimed':False,'full_suite_rerun':False,
    'private_data_included':False,'game_operated':False,'chat_sent':False,
    'requirements_sha256':sha256((R/'PROJECT_REQUIREMENTS.md').read_bytes()).hexdigest(),
    'agents_sha256':sha256((R/'AGENTS.md').read_bytes()).hexdigest(),'at_UTC':datetime.now(timezone.utc).isoformat()}
(out/'review.json').write_bytes((json.dumps(record,ensure_ascii=False,indent=2)+'\n').encode());(out/'record-source.py').write_bytes(Path(__file__).read_bytes())
publisher=(R/'.cache/publish_video_strategy_20261029.py').read_text('utf8')
publisher=publisher.replace('.cache/video-strategy-20261029-publication','.cache/public-source-reuse-20261029-publication')
publisher=publisher.replace('verification/maintenance/video-strategy-20261029/','verification/maintenance/public-source-reuse-20261029/')
publisher=publisher.replace("'IMPLEMENTATION_STRATEGY.md'in names","'AGENTS.md'in names and 'PROJECT_REQUIREMENTS.md'in names")
publisher=publisher.replace('记录视频完整效果目标与简化实现路线，恢复P3续接','将公开源码优先复用与本机适配写入项目要求')
publisher=publisher.replace("'completed_sections':410","'completed_sections':412")
(R/'.cache/publish_reuse_guidance_20261029.py').write_bytes(publisher.encode())
print('AGENTS and requirements updated; actual index validates; implementation unchanged; still412, not413.')
