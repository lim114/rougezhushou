from pathlib import Path
from hashlib import sha256
from copy import deepcopy
from datetime import datetime,timezone,timedelta
import json,runpy
ROOT=Path(__file__).resolve().parents[1]
def read(n):return json.loads((ROOT/n).read_bytes())
def sha(n):return sha256((ROOT/n).read_bytes()).hexdigest()
def enc(v):return (json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode('utf8')
def pin(n):return {'receipt':n,'sha256':sha(n)}
title='本性难移伪装与现身资料、进度标题显示实际改动'
change='本性难移普通和紧急作战的四类空值体，可手动查看伪装对象、对应敌人的独立能力，以及文献记载的出场、退场与本体现身条件；八个精确引用才显示专属入口，其他敌人隐藏。玩家说明与技术资料分开，同一条目刷新保留阅读位置，切换或资料失效清旧内容，恢复后手动重开。云端索引和交接标题采用“第N节 + 实际完成的改动”，只取同号完成回执，规划不混入，历史编号不重排。'
limits='固定原记录“空植体”与文献“空值体”、“受攻击”与“受到伤害”的差异明确保留。本体与对应敌人分开，不推定实际召唤等级、能力继承、档次、生成成功、现身时刻、位置或当前服务器行为；本体图片缺失时不借用伪装对象图片。未补齐首领阶段、四派生分类或缺失头像，不改数值、地图或本局。P3/P2/P1剩余项保留。'
necessary_name='verification/sections/306-necessary-attempt1/process.json';native_name='verification/sections/306-window-attempt1/actual/window.json';process_name='verification/sections/306-window-attempt1/process.json';visual_name='verification/sections/306-root-visual.json';main_name='verification/sections/306-main-window.json'
n=read(necessary_name);w=read(native_name);p=read(process_name);v=read(visual_name);m=read(main_name)
assert n['passed'] and n['exit_code']==0 and n['methods_ran']==75
assert w['passed'] and w['qpa']=='windows' and w['qt_exit_code']==0 and w['verification_window_closed'] and len(w['actual_tuple_readings'])==8
assert p['passed'] and p['exit_code']==0 and p['window_receipt_sha256']==sha(native_name)
assert v['section']==306 and v['all_reviewed'] and len(v['images'])==len(w['screenshots'])==5
for image in v['images']:assert image['root_viewed'] and sha(image['file'])==image['sha256']
assert m['passed'] and m['window_visible_and_responsive'] and m['private_state_five_paths_unchanged']
for data in (n,w):
 assert data['source_sha256_before']==data['source_sha256_after']
 for name,h in data['source_sha256_after'].items():assert sha(name)==h,name
cp=read('DEVELOPMENT_CHECKPOINT.json');assert cp['completed_sections']==305 and cp['next_section']==306
assert cp['policy']['wrap_up_below_usage_percent']==15 and cp['policy']['development_paused_by_latest_user_request'] is False
now=datetime.now(timezone(timedelta(hours=8))).isoformat();pending='<!-- section306-publication-pending -->当前为本地验收完成，普通推送与真实远端核对尚待完成。'
receipt={'section':306,'kind':'functional_section','title':title,'new_capability':change,'limitations':[limits],'at_Beijing':now,'branch':'codex/p2-development','necessary_validation':{**pin(necessary_name),'methods_run':75,'actual_exit':0},'native_windows_validation':{**pin(native_name),'process':pin(process_name),'unique_checks':w['unique_checks'],'actual_Qt_exit':0,'actual_tuple_readings':w['actual_tuple_readings']},'root_visual_review':pin(visual_name),'original_project_window':pin(main_name),'source_sha256':n['source_sha256_after'],'validated_source_sha256':w['source_sha256_after'],'full_suite_rerun':False,'last_full_receipt':'verification/full-305/summary.json','last_full_source_is_historical305':True,'next_periodic_full_section':320,'P3_complete':False,'P2_complete':False,'private_state_read_copied_or_restored':False,'game_operated':False,'chat_sent':False,'actual_game_form_or_level_verified':False,'cloud_publication_binding':'enclosing_commit','cloud_published':False}
(ROOT/'verification/sections/306.json').write_bytes(enc(receipt))
details=change+'\n\n实际75项必要检查、原生'+str(w['unique_checks'])+'项唯一检查及五张代表截图通过，原测试窗口已更新并确认响应，启动前后私人五路径不变。此次未重跑全量；305全量保留原适用范围，下一定期全量320。符号链接权限、历史私样本及游戏聊天仍未计通过。\n\n'+limits+'\n\n'+pending
for name in ('PROJECT_COMPLETED.md','WORK_IN_PROGRESS.md'):
 path=ROOT/name;path.write_text('## 第306节 + '+title+'\n\n'+now+'。'+details+'\n\n以下保留历史记录；当前断点以上述306为准。\n\n'+path.read_text('utf8'),encoding='utf8')
path=ROOT/'AGENTS.md';s=path.read_text('utf8');end=s.index('\n## ',3);s='## 当前续接 · 第306节 + '+title+'\n\n'+details+'\n\n用户已恢复，继续P3；编号与实际改动配对，15%规则保留；305后暂停为历史，未启动307。\n'+s[end:];path.write_text(s,encoding='utf8')
path=ROOT/'PROJECT_REQUIREMENTS.md';s=path.read_text('utf8');start=s.index('<!-- current-delivery:start -->');end=s.index('<!-- current-delivery:end -->')+len('<!-- current-delivery:end -->');s=s[:start]+'<!-- current-delivery:start -->\n## 第306节 + '+title+'\n\n'+details+'\n<!-- current-delivery:end -->'+s[end:];path.write_text(s,encoding='utf8')
for key in ('current_section_validation','latest_section_environment','cloud_publication_closeout','active_section'):
 if key in cp:cp['historical_before306_'+key]=cp.pop(key)
cp.update(completed_sections=306,next_section=307,batch_status='P3_SECTION306_LOCAL_ACCEPTED_PUBLICATION_PENDING',next_action='第306节 + '+title+'已本地验收；普通推送并核对远端后继续P3剩余项目。下次定期全量320。')
cp['sections'].append({'number':306,'completion_ref':'p3-section-306','topic':title,'verification':'verification/sections/306.json'})
cp['functional_sections_since_latest_requirement'].append(306)
cp['current_section_save']={'section':306,'verification':'verification/sections/306.json','scope':'current_functional_section','binding':'enclosing_commit'}
cp['last_verified_cloud_save']['scope']='previous_functional_section'
cp['current_section_validation']={'section':306,'receipt':'verification/sections/306.json','necessary_methods_passed':75,'native_isolated_window_checks':w['unique_checks'],'full_suite_rerun':False,'last_full_receipt':'verification/full-305/summary.json','full_source_is_historical305':True}
cp['latest_section_environment']={'section':306,'receipt':'verification/sections/306.json','native_windows':'75 necessary; panel-only actual Windows reader; original app startup verified separately','native_game_or_chat_verified':False,'current_section_full_rerun':False,'last_full_receipt':'verification/full-305/summary.json'}
cp['current_batch'].update(status=cp['batch_status'],completed_sections=306,next_section=307,next_section_started=False,receipt='verification/sections/306.json',batch_closed=False)
for key in ('pause_after_active_section','pause_request_date','usage_wrap_up_after_active_section','usage_remaining_percent_at_trigger','usage_threshold_receipt','latest_usage_and_pause_instruction_receipt'):
 cp['policy'].pop(key,None)
cp['policy']['latest_user_instruction_receipt']='verification/sections/306-preparation/resume-and-numbering.json'
(ROOT/'DEVELOPMENT_CHECKPOINT.json').write_bytes(enc(cp))
path=ROOT/'CLOUD_HANDOFF.md';path.write_text(path.read_text('utf8')+'\n<!-- section306-handoff:start -->\n## 第306节 + '+title+'\n\n'+details+'\n<!-- section306-handoff:end -->\n',encoding='utf8')
runpy.run_path(str(ROOT/'scripts/update_cloud_index.py'))['update'](ROOT)
out=ROOT/'verification/sections/306-closeout';out.mkdir();(out/'execution-closeout.py').write_bytes(Path(__file__).read_bytes())
(out/'applied.json').write_bytes(enc({'section':306,'local_accepted':True,'ordinary_cloud_publication_verified':False,'at_Beijing':now,'next307_started':False,'section_label':read('CLOUD_INDEX.json')['current_section_label']}))
print(json.dumps({'completed_section_label':read('CLOUD_INDEX.json')['current_section_label'],'cloud_publication_pending':True},ensure_ascii=False))
