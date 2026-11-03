from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone,timedelta
import json,runpy
ROOT=Path(__file__).resolve().parents[1]
def read(n):return json.loads((ROOT/n).read_bytes())
def sha(n):return sha256((ROOT/n).read_bytes()).hexdigest()
def enc(v):return(json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode('utf8')
def pin(n):return{'receipt':n,'sha256':sha(n)}
title='洛伦茨与源阶方的交替激活及模块条件'
change='混沌源阶理论新增两个首领专属入口，均可查看交替激活、首次半血变化、终点退场和模块两类结果，七条资料流程按四组条件阅读，不当作必经时间表。补齐原摘录遗漏的全域信息失真技能，区分技能完成的少量我方法伤与对源阶方8%最大生命值伤害、致命伤害的另一爆炸条款；不擅自合并。七张首领技能卡、两张能力卡和模块独立技能/机制表完整保留；玩家说明直接展开相应招式，用普通说法解释限制，模块基础面板只留技术资料。两个确切首领原图独立显示，其他敌人隐藏入口；同源刷新保留主题、页签和阅读位置，换入口或来源失效清旧、恢复后手动重开。'
limits='文献参数不是当前对局预测。两主体按各自触发条件与技能结束返回，未验证同时切换或实际时点；首次半血不能只凭当前血量反推，25技力不能当25秒，预设九个模块不能当实际出现数。源阶方零值默认项不证明本局零伤害或必非零，也不补难度倍率；扣30目标生命不推定所有对局必败。模块完成后的强制击杀与致命伤害触发关系未恢复，不额外叠加爆炸；当前服务器、模式、模块数量/分组/位置/面板、具体伤害/时钟、首次半血实际留存与通关结算仍未知。不改数值模型、地图或本局记忆，原306/309阅读与299出场资料保持独立。P3/P2/P1其余缺口继续保留。'
necessary='verification/sections/310-necessary-attempt4/process.json';native='verification/sections/310-native-attempt4/actual/window.json';process='verification/sections/310-native-attempt4/process.json';visual='verification/sections/310-root-visual.json';main='verification/sections/310-main-window.json';build='verification/sections/310-source-attempt4/process.json'
n,w,p,v,m,b=(read(x)for x in(necessary,native,process,visual,main,build))
assert n['passed']and n['exit_code']==0 and n['methods_ran']==75
assert w['passed']and w['qpa']=='windows'and w['qt_exit_code']==0 and w['verification_window_closed']and w['unique_checks']==28
assert len(w['actual_entry_overviews'])==2 and len(w['actual_topic_readings'])==8 and len(w['same_identity_refresh_observations'])==4
assert all(value==0 for value in w['external_operation_attempts'].values())
assert p['passed']and p['exit_code']==0 and p['window_receipt_sha256']==sha(native)
assert v['all_reviewed']and len(v['images'])==len(w['screenshots'])==5
for img in v['images']:assert img['root_viewed']and sha(img['file'])==img['sha256']
assert m['passed']and m['window_visible_and_responsive']and m['private_state_five_paths_unchanged']and m['private_entire_normal_close_and_start_interval_unchanged']
assert b['passed']and b['exit_code']==0
for data in(n,w,b):
    assert data['source_sha256_before']==data['source_sha256_after']
    for name,h in data['source_sha256_after'].items():assert sha(name)==h,name
registration='verification/sections/310-preparation/maintained-registration.json';reg=read(registration)
assert reg['after_count']==481 and reg['before_count']==478 and reg['original_ordered_prefix_unchanged']and reg['source_sha256']==sha('scripts/verify_full_available.py')
usage=read('verification/sections/310-preparation/usage-threshold.json');assert usage['remaining_percent']==88 and usage['strict_below15_triggered']is False
cp=read('DEVELOPMENT_CHECKPOINT.json');assert cp['completed_sections']==309 and cp['next_section']==310 and cp['batch_start_section']==310
assert cp['policy']['wrap_up_below_usage_percent']==15 and cp['policy']['development_paused_by_latest_user_request']is False
now=datetime.now(timezone(timedelta(hours=8))).isoformat();pending='<!-- section310-publication-pending -->当前为本地验收完成，普通推送与真实远端核对尚待完成。'
r={'section':310,'kind':'functional_section','title':title,'new_capability':change,'limitations':[limits],'at_Beijing':now,'branch':'codex/p2-development','necessary_validation':{**pin(necessary),'methods_run':75,'actual_exit':0},'native_windows_validation':{**pin(native),'process':pin(process),'unique_checks':28,'actual_Qt_exit':0,'exact_entries':2,'actual_topic_readings':8,'actual_nonzero_refresh_reading_states':4,'eight_external_operation_attempts_zero':True},'root_visual_review':pin(visual),'original_project_window':pin(main),'source_build':pin(build),'source_sha256':n['source_sha256_after'],'validated_source_sha256':w['source_sha256_after'],'maintained_registry':pin(registration),'source_manifest':pin('research/p3-boss-cycle-310/source-manifest.json'),'source_scope':{'exact_targets':[['ro6_b_5','enemy_2147_shophm',0],['ro6_b_5','enemy_2148_shorbb',0]],'complete_public_revisions':['441767','436997','440218','427939'],'boss_skill_cards':7,'boss_ability_cards':2,'independent_module_skill_tables':1,'documentary_flow_records':7,'conditional_flow_groups':4,'per_target_fresh_public_runtime_members':12,'whole_database_and_level_hashing_at_build_only':True,'entire_selected_current_stage_and_three_related_skill_objects_compared':True,'current_server_or_actual_modes_verified':False,'numerical_phase_model_added':False},'original_failure_history':[pin('verification/sections/310-native-attempt1/actual/window.json'),pin('verification/sections/310-native-attempt2/actual/window.json')],'harness_repairs':[pin('verification/sections/310-preparation/native-path-repair/repair.json'),pin('verification/sections/310-preparation/native-name-repair/applied.json')],'independent_static_review':pin('verification/sections/310-preparation/native-name-repair/independent-static-review/static-review.json'),'first_actual_visual_readability_review':pin('verification/sections/310-preparation/player-wording-before/root-visual.json'),'player_wording_changes':pin('verification/sections/310-preparation/player-wording-refinement/correction-final.json'),'full_suite_rerun':False,'last_full_receipt':'verification/full-305/summary.json','last_full_source_is_historical305':True,'next_periodic_full_section':320,'P3_complete':False,'P2_complete':False,'private_state_contents_parsed_copied_or_restored':False,'private_state_hashed_locally_for_preservation_only':True,'private_hashes_published':False,'game_operated':False,'chat_sent':False,'cloud_publication_binding':'enclosing_commit','cloud_published':False}
(ROOT/'verification/sections/310.json').write_bytes(enc(r))
details=change+'\n\n实际75项必要检查、28项原生唯一检查通过；两个入口各四主题共8次实际阅读、四组非零滚动阅读位置保留及真实公开源副本损坏/恢复核对通过，根代理查看全部五张实际截图。原测试窗口已更新可见响应，正常关闭至启动的私人五路径不变。首次两次原生脚本分别因路径与变量名错误在窗口构造前失败，原件和修复/独立审核均保留；第三窗口通过后的玩家措辞进一步简化，末轮完整重验通过。原478维护选择器顺序不减，现481；未重跑全量，305回执只保留历史适用范围，下次定期全量320。权限1314、历史私样本、Linux/Wine和游戏聊天仍不计通过。\n\n'+limits+'\n\n'+pending
for name in('PROJECT_COMPLETED.md','WORK_IN_PROGRESS.md'):
    path=ROOT/name;s=path.read_text('utf8')
    if name=='WORK_IN_PROGRESS.md':
        marker='以下为已交付历史。\n\n';assert s.startswith('## 当前进行第310节')and s.count(marker)==1;s=s.split(marker,1)[1]
    path.write_text('## 第310节 + '+title+'\n\n'+now+'。'+details+'\n\n以下为历史记录；当前断点以上述310为准。\n\n'+s,encoding='utf8')
path=ROOT/'PROJECT_PROGRESS.md';s=path.read_text('utf8');old='首领阶段的实际数值/转换/执行与其余首领的完整文献流程';assert s.count(old)==1;s=s.replace(old,'首领阶段的实际数值/转换/执行、未覆盖首领及其关联装置的完整文献条件流程',1);path.write_text(s,encoding='utf8')
path=ROOT/'AGENTS.md';s=path.read_text('utf8');end=s.index('\n## ',3);path.write_text('## 当前续接 · 第310节 + '+title+'\n\n'+details+'\n\n继续P3，311未启动；编号仅配实际完成改动，严格低于15%规则保留。\n'+s[end:],encoding='utf8')
path=ROOT/'PROJECT_REQUIREMENTS.md';s=path.read_text('utf8');start=s.index('<!-- current-delivery:start -->');end=s.index('<!-- current-delivery:end -->')+len('<!-- current-delivery:end -->');path.write_text(s[:start]+'<!-- current-delivery:start -->\n## 第310节 + '+title+'\n\n'+details+'\n<!-- current-delivery:end -->'+s[end:],encoding='utf8')
for key in('current_section_validation','latest_section_environment','cloud_publication_closeout','active_section'):
    if key in cp:cp['historical_before310_'+key]=cp.pop(key)
cp.update(completed_sections=310,latest_functional_section=310,next_section=311,batch_status='P3_SECTION310_LOCAL_ACCEPTED_PUBLICATION_PENDING',next_action='第310节 + '+title+'已本地验收，普通推送并真实远端核对后继续P3；条件说明不等于本局实际，剩余缺口保留，下次定期全量320。')
assert not any(s['number']==310 for s in cp['sections']);cp['sections'].append({'number':310,'completion_ref':'p3-section-310','topic':title,'verification':'verification/sections/310.json'});cp['functional_sections_since_latest_requirement'].append(310)
cp['current_section_save']={'section':310,'verification':'verification/sections/310.json','scope':'current_functional_section','binding':'enclosing_commit'};cp['last_verified_cloud_save']['scope']='previous_functional_section'
cp['current_section_validation']={'section':310,'receipt':'verification/sections/310.json','necessary_methods_passed':75,'native_isolated_window_checks':28,'exact_entries':2,'actual_topic_readings':8,'actual_nonzero_refresh_states':4,'full_suite_rerun':False,'last_full_receipt':'verification/full-305/summary.json','full_source_is_historical305':True}
cp['latest_section_environment']={'section':310,'receipt':'verification/sections/310.json','native_windows':'75 necessary; exact two entries / eight actual topic readings / four actual refresh states / real temporary public source failure and manual recovery; original app startup separately verified','native_game_or_chat_verified':False,'current_section_full_rerun':False,'last_full_receipt':'verification/full-305/summary.json'}
cp['current_batch'].update(status=cp['batch_status'],completed_sections=310,next_section=311,next_section_started=False,receipt='verification/sections/310.json',batch_closed=False);cp['policy'].update(current_usage_remaining_percent=usage['remaining_percent'],current_usage_receipt='verification/sections/310-preparation/usage-threshold.json');(ROOT/'DEVELOPMENT_CHECKPOINT.json').write_bytes(enc(cp))
path=ROOT/'CLOUD_HANDOFF.md';path.write_text(path.read_text('utf8')+'\n<!-- section310-handoff:start -->\n## 第310节 + '+title+'\n\n'+details+'\n<!-- section310-handoff:end -->\n',encoding='utf8')
runpy.run_path(str(ROOT/'scripts/update_cloud_index.py'))['update'](ROOT)
out=ROOT/'verification/sections/310-closeout';out.mkdir();(out/'execution-closeout.py').write_bytes(Path(__file__).read_bytes());(out/'applied.json').write_bytes(enc({'section':310,'local_accepted':True,'ordinary_cloud_publication_verified':False,'at_Beijing':now,'next311_started':False,'section_label':read('CLOUD_INDEX.json')['current_section_label']}));(ROOT/'verification/sections/310-preparation/execution-main-window.py').write_bytes((ROOT/'.cache/open_test_window_310.py').read_bytes())
print(json.dumps({'completed_section_label':read('CLOUD_INDEX.json')['current_section_label'],'cloud_publication_pending':True},ensure_ascii=False))
