from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone,timedelta
import json,runpy
ROOT=Path(__file__).resolve().parents[1]
def read(n):return json.loads((ROOT/n).read_bytes())
def sha(n):return sha256((ROOT/n).read_bytes()).hexdigest()
def enc(v):return (json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode('utf8')
def pin(n):return {'receipt':n,'sha256':sha(n)}
title='事件附注区分出现前条件与选择后结果'
change='固定事件目录的16条选项附注现在按4条出现前条件、12条选择后结果分别阅读；新增十条结果的来源核对与分类，在玩家说明、资料页及原选项目的地中分别标明可能战斗、紧急难度、后续奖励与暂离再访，避免将选择后的说明误读为选项出现条件。原4条条件、既有2条结果与作战/奖励/再访入口保留。来源失效时清除旧分类、保留原文并提示类型待核对，恢复后重新核对；同事件刷新保留阅读位置。'
limits='本节是资料分类与阅读能力，不是新增十种机制或奖励池。原资格判断、资源数量、实际可选未知与299兼容原接口不改。安眠一隅两处原注均写2种、分别只列1种和列3种的矛盾继续明确提示；完整候选池、概率、实际触发/领取、25个原场景与57个原选项入口及当前服务器适用性均未补齐，不据文献推断本局已发生。P3/P2/P1均未全部完成，识别优化最后。'
necessary_name='verification/sections/307-necessary-attempt2/process.json';native_name='verification/sections/307-window-attempt2/actual/window.json';process_name='verification/sections/307-window-attempt2/process.json';visual_name='verification/sections/307-root-visual.json';main_name='verification/sections/307-main-window.json'
n=read(necessary_name);w=read(native_name);p=read(process_name);v=read(visual_name);m=read(main_name)
assert n['passed'] and n['exit_code']==0 and n['methods_ran']==87
assert w['passed'] and w['qpa']=='windows' and w['qt_exit_code']==0 and w['verification_window_closed'] and w['unique_checks']==23
assert len(w['actual_event_readings'])==9
assert p['passed'] and p['exit_code']==0 and p['window_receipt_sha256']==sha(native_name)
assert v['section']==307 and v['all_reviewed'] and len(v['images'])==len(w['screenshots'])==5
for image in v['images']:assert image['root_viewed'] and sha(image['file'])==image['sha256']
assert m['passed'] and m['window_visible_and_responsive'] and m['private_state_five_paths_unchanged']
for data in(n,w):
 assert data['source_sha256_before']==data['source_sha256_after']
 for name,h in data['source_sha256_after'].items():assert sha(name)==h,name
assert sha('rouge/event_planning.py')=='00490a20281c00a54113c69db8fd97635ac191db781ecffde29c907aab6f7249'
registration=read('verification/sections/307-preparation/maintained-registration.json')
assert registration['before_count']==471 and registration['after_count']==474 and registration['original_ordered_prefix_unchanged'] and registration['source_sha256']==sha('scripts/verify_full_available.py')
cp=read('DEVELOPMENT_CHECKPOINT.json');assert cp['completed_sections']==306 and cp['next_section']==307
assert cp['policy']['wrap_up_below_usage_percent']==15 and cp['policy']['development_paused_by_latest_user_request']is False
now=datetime.now(timezone(timedelta(hours=8))).isoformat()
usage={'observed_Beijing':now,'tool':'mcp__codex_app.get_usage_limits','used_percent':5,'remaining_percent':95,'window_duration_minutes':10080,'other_window':'unavailable, not inferred','strict_below15_triggered':False,'account_identifier_published':False}
(ROOT/'verification/sections/307-preparation/usage-threshold.json').write_bytes(enc(usage))
# Preserve the actual failed preparation observation, not a fabricated test receipt.
(ROOT/'verification/sections/307-preparation/preparation-tool-error.json').write_bytes(enc({'operation':'maintained registry registration preparation','observed_first_exit':1,'exception':'ModuleNotFoundError: No module named verify_cloud','cause':'Root import helper omitted scripts directory from sys.path','production_modified_before_error':False,'repair':'Add explicit scripts path only in root helper; unchanged complete ordered prefix then checked successfully','final_receipt':'verification/sections/307-preparation/maintained-registration.json','original_full_stdout_retained':False}))
pending='<!-- section307-publication-pending -->当前为本地验收完成，普通推送与真实远端核对尚待完成。'
receipt={'section':307,'kind':'functional_section','title':title,'new_capability':change,'limitations':[limits],'at_Beijing':now,'branch':'codex/p2-development','necessary_validation':{**pin(necessary_name),'methods_run':87,'actual_exit':0},'native_windows_validation':{**pin(native_name),'process':pin(process_name),'unique_checks':23,'actual_Qt_exit':0,'events_read':9,'new_result_notes':10,'true_prior_requirements':4},'root_visual_review':pin(visual_name),'original_project_window':pin(main_name),'source_sha256':n['source_sha256_after'],'validated_source_sha256':w['source_sha256_after'],'maintained_registry':pin('verification/sections/307-preparation/maintained-registration.json'),'complete_current_player_comparison':{'events':38,'contexts_each':2,'pairs':76,'only_changed_events':7,'other_events_full_text_unchanged':31,'approved_literal_changes_only':True},'raw_event_planning_source_unchanged_sha256':sha('rouge/event_planning.py'),'classification':{'all_nonempty_annotations':16,'preselection':4,'selection_result':12,'new_result_reading_classifications':10,'new_mechanisms':0},'failure_history':pin('verification/sections/307-preparation/failure-and-repair-history.json'),'full_suite_rerun':False,'last_full_receipt':'verification/full-305/summary.json','last_full_source_is_historical305':True,'next_periodic_full_section':320,'P3_complete':False,'P2_complete':False,'private_state_read_copied_or_restored':False,'game_operated':False,'chat_sent':False,'cloud_publication_binding':'enclosing_commit','cloud_published':False}
(ROOT/'verification/sections/307.json').write_bytes(enc(receipt))
details=change+'\n\n实际87项必要检查、23项原生唯一检查、五张实际截图核对通过；38事件的默认与自然入口上下文共76组成对全文对照，原190场景资源及299兼容范围保留。新增三模块进入下次完整验收，原471选择器顺序不减、现474。原项目测试窗口已更新且可见响应，正常关闭至启动的私人五路径不变。未重跑全量；305完整回执只保留其历史适用范围，下一定期全量320。符号链接权限、历史私样本、Linux/Wine及游戏聊天不冒称本节通过。\n\n'+limits+'\n\n'+pending
for name in('PROJECT_COMPLETED.md','WORK_IN_PROGRESS.md'):
 path=ROOT/name;path.write_text('## 第307节 + '+title+'\n\n'+now+'。'+details+'\n\n以下为历史记录；当前断点以上述307为准。\n\n'+path.read_text('utf8'),encoding='utf8')
path=ROOT/'PROJECT_PROGRESS.md';s=path.read_text('utf8');old='10条未解析附注的结果/条件分类与来源核验；';assert s.count(old)==1;s=s.replace(old,'',1);path.write_text(s,encoding='utf8')
path=ROOT/'AGENTS.md';s=path.read_text('utf8');end=s.index('\n## ',3);s='## 当前续接 · 第307节 + '+title+'\n\n'+details+'\n\n用户已恢复，继续P3；编号与实际改动配对，严格低于15%规则保留；305后暂停为历史，308未启动。\n'+s[end:]
old='## 当前用量收尾规则及本节后暂停（2026-10-18）';assert s.count(old)==1;s=s.replace(old,'## 当前用量收尾规则（2026-10-18）',1)
old='用户同时明确要求完成当前第305节后暂停，306不得启动；完整收尾后等待用户恢复。';assert s.count(old)==1;s=s.replace(old,'305后暂停已被后续“继续”明确解除；该暂停要求仅保留为历史。',1);path.write_text(s,encoding='utf8')
path=ROOT/'PROJECT_REQUIREMENTS.md';s=path.read_text('utf8');start=s.index('<!-- current-delivery:start -->');end=s.index('<!-- current-delivery:end -->')+len('<!-- current-delivery:end -->');s=s[:start]+'<!-- current-delivery:start -->\n## 第307节 + '+title+'\n\n'+details+'\n<!-- current-delivery:end -->'+s[end:];path.write_text(s,encoding='utf8')
for key in('current_section_validation','latest_section_environment','cloud_publication_closeout','active_section'):
 if key in cp:cp['historical_before307_'+key]=cp.pop(key)
cp.update(completed_sections=307,next_section=308,batch_status='P3_SECTION307_LOCAL_ACCEPTED_PUBLICATION_PENDING',next_action='第307节 + '+title+'已本地验收；普通推送及真实远端核对后继续P3。下一定期全量320。')
assert not any(s['number']==307 for s in cp['sections'])
cp['sections'].append({'number':307,'completion_ref':'p3-section-307','topic':title,'verification':'verification/sections/307.json'})
cp['functional_sections_since_latest_requirement'].append(307)
cp['current_section_save']={'section':307,'verification':'verification/sections/307.json','scope':'current_functional_section','binding':'enclosing_commit'}
cp['last_verified_cloud_save']['scope']='previous_functional_section'
cp['current_section_validation']={'section':307,'receipt':'verification/sections/307.json','necessary_methods_passed':87,'native_isolated_window_checks':23,'full_suite_rerun':False,'last_full_receipt':'verification/full-305/summary.json','full_source_is_historical305':True}
cp['latest_section_environment']={'section':307,'receipt':'verification/sections/307.json','native_windows':'87 necessary; nine-event isolated actual Windows reader; original app startup separately verified','native_game_or_chat_verified':False,'current_section_full_rerun':False,'last_full_receipt':'verification/full-305/summary.json'}
cp['current_batch'].update(status=cp['batch_status'],completed_sections=307,next_section=308,next_section_started=False,receipt='verification/sections/307.json',batch_closed=False)
cp['policy'].update(current_usage_remaining_percent=95,current_usage_receipt='verification/sections/307-preparation/usage-threshold.json')
cp['policy']['usage_monitoring']='Use verified available account windows only. Strictly below15 percent triggers wrap-up, exactly15 does not. Finish the entire active section, necessary checks, records, requirements/index, ordinary push and actual remote verification before stopping. Never reduce scope or infer unavailable windows. The prior305 pause was completed and explicitly revoked by subsequent user continuation.'
(ROOT/'DEVELOPMENT_CHECKPOINT.json').write_bytes(enc(cp))
path=ROOT/'CLOUD_HANDOFF.md';path.write_text(path.read_text('utf8')+'\n<!-- section307-handoff:start -->\n## 第307节 + '+title+'\n\n'+details+'\n<!-- section307-handoff:end -->\n',encoding='utf8')
runpy.run_path(str(ROOT/'scripts/update_cloud_index.py'))['update'](ROOT)
out=ROOT/'verification/sections/307-closeout';out.mkdir();(out/'execution-closeout.py').write_bytes(Path(__file__).read_bytes())
(out/'applied.json').write_bytes(enc({'section':307,'local_accepted':True,'ordinary_cloud_publication_verified':False,'at_Beijing':now,'next308_started':False,'section_label':read('CLOUD_INDEX.json')['current_section_label']}))
for src,target in(('.cache/open_test_window_307.py','verification/sections/307-preparation/execution-main-window.py'),('.cache/prepare307_close.py','verification/sections/307-preparation/execution-preparation.py'),('.cache/repair307_native.py','verification/sections/307-preparation/execution-native-fixture-repair.py')):
 (ROOT/target).write_bytes((ROOT/src).read_bytes())
print(json.dumps({'completed_section_label':read('CLOUD_INDEX.json')['current_section_label'],'cloud_publication_pending':True},ensure_ascii=False))
