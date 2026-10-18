from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone,timedelta
from copy import deepcopy
import json
ROOT=Path(__file__).resolve().parents[1]
def enc(v):return (json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode('utf8')
now=datetime.now(timezone(timedelta(hours=8))).isoformat()
cp_path=ROOT/'DEVELOPMENT_CHECKPOINT.json';cp=json.loads(cp_path.read_bytes())
assert cp['completed_sections']==305 and cp['next_section']==306
cp['historical_before_resume306_policy']={k:deepcopy(v) for k,v in cp['policy'].items() if 'usage' in k or 'pause' in k}
cp['historical_before_resume306_batch']=deepcopy(cp.get('current_batch'))
cp['policy'].update(development_paused_by_latest_user_request=False,new_functional_sections_paused=False,pause_after_active_section_requested=False,usage_wrap_up_triggered=False,usage_wrap_up_completed=False,current_usage_remaining_percent=98,current_usage_receipt='verification/sections/306-preparation/resume-and-numbering.json',section_display_format='第N节 + 实际完成的改动；N保留稳定历史标识，未验收规划不计完成')
cp['active_section']={'number':306,'status':'implementation_not_completed','planned_change':'本性难移四类空值体的伪装与现身资料；进度标题显示当前节加实际改动','acceptance':'普通/紧急8个精确引用；无关敌人不显示专属入口；来源失效清旧内容；同身份刷新保留阅读；不改分类/数值/本局；必要检查与实际Qt窗口验证'}
cp['batch_start_section']=306;cp['batch_target_section']=None;cp['batch_status']='P3_SECTION306_IN_PROGRESS'
cp['current_batch'].update(start=306,end=None,status=cp['batch_status'],completed_sections=305,next_section=306,next_section_started=True,batch_closed=False,next_full_validation_after=320)
cp['next_action']='继续P3第306节开发；验收后以第306节 + 实际完成的改动发布，不把当前规划记作完成。下次定期全量320。'
cp_path.write_bytes(enc(cp))
record={'section':306,'kind':'user_resume_and_section_label_requirement_not_functional_completion','at_Beijing':now,'user_request':'继续，项目编号方式改为当前节+实际完成的改动','completed_sections_unchanged':305,'active_section':306,'naming_rule':'第N节 + 实际完成的改动','history_receipt_ids_renumbered':False,'usage_query_actual':{'usedPercent':2,'remainingPercent':98,'windowDurationMins':10080,'secondary_window_available':False},'threshold_percent':15,'below_threshold':False,'previous_pause_revoked_by_user_resume':True,'game_chat_private_state_modified':False}
out=ROOT/'verification/sections/306-preparation';out.mkdir(parents=True,exist_ok=True)
(out/'resume-and-numbering.json').write_bytes(enc(record));(out/'execution-resume.py').write_bytes(Path(__file__).read_bytes())
notice='## 当前要求 · 恢复开发，编号附实际改动（2026-10-18）\n\n用户已明确继续，原305后暂停已解除。当前开发第306节，尚未完成；拟补齐本性难移四类空值体的伪装与现身资料。交付统一采用“第N节 + 实际完成的改动”，编号保留稳定引用，不重排历史回执，不将规划、测试数量或节数当作功能完成。当前已交付仍为305；每节源码、验收、要求和索引普通推送并核对远端。15%收尾规则保留，当前实际可用窗口剩余98%，其它窗口不可用不推定。P3优先，识别最后。\n\n'
for name in ('AGENTS.md','WORK_IN_PROGRESS.md'):
 p=ROOT/name;p.write_text(notice+p.read_text('utf8'),encoding='utf8')
p=ROOT/'PROJECT_REQUIREMENTS.md';text=p.read_text('utf8');anchor='## 当前优先顺序与输出可读性（2026-10-15最新更正）';assert anchor in text
rule='## 进度编号与恢复要求（2026-10-18）\n\n当前已恢复开发，305后的暂停为历史。进度标题与云端索引使用“第N节 + 实际完成的改动”：保留稳定整数编号和原回执路径，不重排历史；改动必须来自同节已验收交付，不以计划、测试条数或编号代替成果。进行中的工作明确标注未完成。普通推送后核对真实远端；收尾阈值仍为严格低于15%。\n\n'
p.write_text(text.replace(anchor,rule+anchor,1),encoding='utf8')
print(json.dumps({'active_section':306,'completed_sections':305,'resume_record':str(out/'resume-and-numbering.json'),'current_threshold_percent':15},ensure_ascii=False))
