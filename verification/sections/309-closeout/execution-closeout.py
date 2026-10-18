from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone,timedelta
import json,runpy
ROOT=Path(__file__).resolve().parents[1]
def read(n):return json.loads((ROOT/n).read_bytes())
def sha(n):return sha256((ROOT/n).read_bytes()).hexdigest()
def enc(v):return(json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode('utf8')
def pin(n):return{'receipt':n,'sha256':sha(n)}
title='畸症首领按形态查看招式与转换条件'
change='畸症作战的玻利瓦尔，症结之核新增专属资料入口，可按六个文献名称条目查看招式归属、七条进入/离开/返回条件、灾厄共同影响与第三形态的循环和飞行分支。飞行招式直接展开对应未熄之地效果，避免来回查找；未明确另列技能不说成没有技能。玩家中文说明与完整技术来源分开，同资料刷新保留形态、页签及阅读位置；切换敌人或资料失效清旧，恢复后需手动重开。其他敌人隐藏此入口，原伪装/现身、调谐削弱及出场资料保持独立。'
limits='六项是文献阅读条目，不等于六条血或六次击倒；飞行是第三形态子过程，主目标退场打断灾厄之口不等于进入下一形态。不经重生的循环保留说明明确注明来自文献说明注。重生加成、延长时长、索敌措辞及同名原招式的对应口径分别保留，不能认定数值互斥、擅自10+1或按数组顺序恢复引擎绑定。当前服务器、实际形态/转换/时刻、阶段完整面板/伤害与第三或飞行形态的完整终止流程仍未知；不修改预计数值、地图或本局记忆。其余首领、节点/事件/掉落与完整地图校准及P2/P1缺口均保留。'
necessary='verification/sections/309-necessary-attempt2/process.json';native='verification/sections/309-native-attempt2/actual/window.json';process='verification/sections/309-native-attempt2/process.json';visual='verification/sections/309-root-visual.json';main='verification/sections/309-main-window.json';build='verification/sections/309-source-attempt2/process.json'
n,w,p,v,m,b=(read(x)for x in(necessary,native,process,visual,main,build))
assert n['passed'] and n['exit_code']==0 and n['methods_ran']==83
assert w['passed'] and w['qpa']=='windows' and w['qt_exit_code']==0 and w['verification_window_closed'] and w['unique_checks']==27
assert len(w['actual_phase_readings'])==6 and len(w['same_identity_refresh_observations'])==2
assert all(value==0 for value in w['external_operation_attempts'].values())
assert p['passed'] and p['exit_code']==0 and p['window_receipt_sha256']==sha(native)
assert v['all_reviewed'] and len(v['images'])==len(w['screenshots'])==5 and v['actual_flight_inline_effect_readable']
for img in v['images']:assert img['root_viewed'] and sha(img['file'])==img['sha256']
assert m['passed'] and m['window_visible_and_responsive'] and m['private_state_five_paths_unchanged'] and m['private_entire_normal_close_and_start_interval_unchanged']
assert b['passed'] and b['exit_code']==0
for data in(n,w,b):
    assert data['source_sha256_before']==data['source_sha256_after']
    for name,h in data['source_sha256_after'].items():assert sha(name)==h,name
registration='verification/sections/309-preparation/maintained-registration.json';reg=read(registration)
assert reg['after_count']==478 and reg['before_count']==475 and reg['original_ordered_prefix_unchanged'] and reg['source_sha256']==sha('scripts/verify_full_available.py')
usage=read('verification/sections/309-preparation/usage-threshold.json');assert usage['remaining_percent']==90 and usage['strict_below15_triggered'] is False
cp=read('DEVELOPMENT_CHECKPOINT.json');assert cp['completed_sections']==308 and cp['next_section']==309 and cp['batch_start_section']==309
assert cp['policy']['wrap_up_below_usage_percent']==15 and cp['policy']['development_paused_by_latest_user_request'] is False
now=datetime.now(timezone(timedelta(hours=8))).isoformat();pending='<!-- section309-publication-pending -->当前为本地验收完成，普通推送与真实远端核对尚待完成。'
r={'section':309,'kind':'functional_section','title':title,'new_capability':change,'limitations':[limits],'at_Beijing':now,'branch':'codex/p2-development','necessary_validation':{**pin(necessary),'methods_run':83,'actual_exit':0},'native_windows_validation':{**pin(native),'process':pin(process),'unique_checks':27,'actual_Qt_exit':0,'documentary_phase_readings':6,'actual_refresh_reading_states':2,'eight_external_operation_attempts_zero':True},'root_visual_review':pin(visual),'original_project_window':pin(main),'source_build':pin(build),'source_sha256':n['source_sha256_after'],'validated_source_sha256':w['source_sha256_after'],'maintained_registry':pin(registration),'source_manifest':pin('research/p3-boss-phase-309/source-manifest.json'),'source_scope':{'exact_target':['ro6_b_6','enemy_2150_shchmr',0],'complete_document_revisions':['435612','420841'],'documentary_entries':6,'complete_skills':6,'transitions':7,'unresolved_source_differences':4,'per_target_fresh_small_public_runtime_members':8,'full_database_and_level_hashing_at_build_only':True,'entire_selected_current_stage_enemy_skill_objects_compared':True,'current_server_or_actual_phase_proven':False,'numerical_phase_model_added':False},'first_actual_readability_refinement':pin('verification/sections/309-preparation/first-rendering/root-visual.json'),'source_mode_extraction_correction_preserves_original_freeze':True,'full_suite_rerun':False,'last_full_receipt':'verification/full-305/summary.json','last_full_source_is_historical305':True,'next_periodic_full_section':320,'P3_complete':False,'P2_complete':False,'private_state_contents_parsed_copied_or_restored':False,'private_state_hashed_locally_for_preservation_only':True,'private_hashes_published':False,'game_operated':False,'chat_sent':False,'cloud_publication_binding':'enclosing_commit','cloud_published':False}
(ROOT/'verification/sections/309.json').write_bytes(enc(r))
details=change+'\n\n实际83项必要检查、27项原生唯一检查通过，六条文献形态逐项手动选择，两类阅读状态非零滚动保留与真实公开源副本损坏/恢复核对通过，五张实际截图由根代理核对；原测试窗口已更新可见响应，正常关闭至启动的私人五路径不变。原475维护选择器顺序不减，现478；未重跑全量，305回执只保留其原历史范围，下次定期全量320。权限1314、历史私样本、Linux/Wine及游戏聊天仍不计通过。\n\n'+limits+'\n\n'+pending
for name in('PROJECT_COMPLETED.md','WORK_IN_PROGRESS.md'):
    path=ROOT/name;s=path.read_text('utf8')
    if name=='WORK_IN_PROGRESS.md':
        marker='以下为已交付历史。\n\n';assert s.startswith('## 当前进行第309节') and s.count(marker)==1;s=s.split(marker,1)[1]
    path.write_text('## 第309节 + '+title+'\n\n'+now+'。'+details+'\n\n以下为历史记录；当前断点以上述309为准。\n\n'+s,encoding='utf8')
path=ROOT/'PROJECT_PROGRESS.md';s=path.read_text('utf8');old='、首领阶段、已绑定22正费用技能';assert s.count(old)==1;s=s.replace(old,'、首领阶段的实际数值/转换/执行与其余首领的完整文献流程、已绑定22正费用技能',1);path.write_text(s,encoding='utf8')
path=ROOT/'AGENTS.md';s=path.read_text('utf8');end=s.index('\n## ',3);s='## 当前续接 · 第309节 + '+title+'\n\n'+details+'\n\n继续P3，310未启动；编号仅配实际完成改动，严格低于15%规则保留。\n'+s[end:];path.write_text(s,encoding='utf8')
path=ROOT/'PROJECT_REQUIREMENTS.md';s=path.read_text('utf8');start=s.index('<!-- current-delivery:start -->');end=s.index('<!-- current-delivery:end -->')+len('<!-- current-delivery:end -->');s=s[:start]+'<!-- current-delivery:start -->\n## 第309节 + '+title+'\n\n'+details+'\n<!-- current-delivery:end -->'+s[end:];path.write_text(s,encoding='utf8')
for key in('current_section_validation','latest_section_environment','cloud_publication_closeout','active_section'):
    if key in cp:cp['historical_before309_'+key]=cp.pop(key)
cp.update(completed_sections=309,latest_functional_section=309,next_section=310,batch_status='P3_SECTION309_LOCAL_ACCEPTED_PUBLICATION_PENDING',next_action='第309节 + '+title+'已本地验收，普通推送并真实远端核对后继续P3；当前阶段数值与其余缺口保留，下次定期全量320。')
assert not any(s['number']==309 for s in cp['sections'])
cp['sections'].append({'number':309,'completion_ref':'p3-section-309','topic':title,'verification':'verification/sections/309.json'});cp['functional_sections_since_latest_requirement'].append(309)
cp['current_section_save']={'section':309,'verification':'verification/sections/309.json','scope':'current_functional_section','binding':'enclosing_commit'}
cp['last_verified_cloud_save']['scope']='previous_functional_section'
cp['current_section_validation']={'section':309,'receipt':'verification/sections/309.json','necessary_methods_passed':83,'native_isolated_window_checks':27,'documentary_phase_readings':6,'full_suite_rerun':False,'last_full_receipt':'verification/full-305/summary.json','full_source_is_historical305':True}
cp['latest_section_environment']={'section':309,'receipt':'verification/sections/309.json','native_windows':'83 necessary; exact target six documentary readings / two actual reading refresh states / real temporary public clone failure and manual recovery; original app startup separately verified','native_game_or_chat_verified':False,'current_section_full_rerun':False,'last_full_receipt':'verification/full-305/summary.json'}
cp['current_batch'].update(status=cp['batch_status'],completed_sections=309,next_section=310,next_section_started=False,receipt='verification/sections/309.json',batch_closed=False)
cp['policy'].update(current_usage_remaining_percent=usage['remaining_percent'],current_usage_receipt='verification/sections/309-preparation/usage-threshold.json')
(ROOT/'DEVELOPMENT_CHECKPOINT.json').write_bytes(enc(cp))
path=ROOT/'CLOUD_HANDOFF.md';path.write_text(path.read_text('utf8')+'\n<!-- section309-handoff:start -->\n## 第309节 + '+title+'\n\n'+details+'\n<!-- section309-handoff:end -->\n',encoding='utf8')
runpy.run_path(str(ROOT/'scripts/update_cloud_index.py'))['update'](ROOT)
out=ROOT/'verification/sections/309-closeout';out.mkdir();(out/'execution-closeout.py').write_bytes(Path(__file__).read_bytes())
(out/'applied.json').write_bytes(enc({'section':309,'local_accepted':True,'ordinary_cloud_publication_verified':False,'at_Beijing':now,'next310_started':False,'section_label':read('CLOUD_INDEX.json')['current_section_label']}))
(ROOT/'verification/sections/309-preparation/execution-main-window.py').write_bytes((ROOT/'.cache/open_test_window_309.py').read_bytes())
(ROOT/'verification/sections/309-preparation/registration-runner-observation.json').write_bytes(enc({'section':309,'kind':'tool_observed_preparation_runner_error_not_product_test_failure','first_execution_exit':1,'observed_error':'ModuleNotFoundError: No module named verify_cloud','cause':'Root registration runner omitted scripts/ on sys.path; registry invocation stopped before any write.','repair':'Added scripts/ to runner sys.path, then actual registry475 ordered prefix preserved and3new added; production gate unchanged.','retry_exit':0,'original_tool_output_is_session_transcript_not_claimed_raw_log_file':True}))
print(json.dumps({'completed_section_label':read('CLOUD_INDEX.json')['current_section_label'],'cloud_publication_pending':True},ensure_ascii=False))
