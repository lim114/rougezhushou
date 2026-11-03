from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone,timedelta
import json,runpy
ROOT=Path(__file__).resolve().parents[1]
def read(n):return json.loads((ROOT/n).read_bytes())
def sha(n):return sha256((ROOT/n).read_bytes()).hexdigest()
def enc(v):return(json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode('utf8')
def pin(n):return{'receipt':n,'sha256':sha(n)}
title='一步之遥与彼处水如酒的格子位置预览'
change='两张新固定原图新增16个可点选的低地近似位置：一步之遥5格、彼处水如酒11格，各自覆盖普通与紧急入口。点击左侧已核对格，可在右侧原图看到对应标记；四个入口在三种窗口尺寸下实际点遍历、缩放与刷新保留通过。完整67个首次双读数在比较前冻结，其余51格保留未知、不显示未经核对的原图位置。原有107格完整保留，逐格参考合计14图、25关、123格；原12图24关整面资料保持原字节。'
limits='16格是两个隔离代理上下文对同一原图的读数一致结果，不是两位真人或游戏采样，不证明绝对位置精度。严格4原像素门槛，不平均、不修点、不重读求通过、不拟合、插值或外推。完整81关59图校准、其余格、高台顶面、立体入口脚点、出生偏移、随机范围、反向定位、整段路线及实际敌人位置仍未闭合。旧303/294原生脚本保留，适配当前123数据的full308变体只完成来源合同和静态流程核对，完整窗口执行留到320；不能记成本节额外原生通过。节点事件、掉落及P3/P2/P1其余待办保留。'
necessary='verification/sections/308-necessary-attempt2/process.json';native='verification/sections/308-window-attempt1/actual/window.json';process='verification/sections/308-window-attempt1/process.json';visual='verification/sections/308-root-visual.json';main='verification/sections/308-main-window.json'
n,w,p,v,m=(read(x)for x in(necessary,native,process,visual,main))
assert n['passed']and n['exit_code']==0 and n['methods_ran']==99
assert w['passed']and w['qpa']=='windows'and w['qt_exit_code']==0 and w['verification_window_closed']and w['unique_checks']==57
assert w['actual_accepted_source_points']==16 and w['source_requested_points']==67 and w['rejected_or_unknown_source_points']==51 and w['total_partial_scope_from_current_data']==[14,25,123]
assert len(w['stage_observations'])==4 and all(len(row['sizes'])==3 for row in w['stage_observations'])
assert sum(len(size['actually_clicked_accepted_points'])for row in w['stage_observations']for size in row['sizes'])==96
assert p['passed']and p['exit_code']==0 and p['window_receipt_sha256']==sha(native)
assert v['section']==308 and v['all_reviewed']and len(v['images'])==len(w['screenshots'])==5
for img in v['images']:assert img['root_viewed']and sha(img['file'])==img['sha256']
assert m['passed']and m['window_visible_and_responsive']and m['private_state_five_paths_unchanged']
for data in(n,w):
 assert data['source_sha256_before']==data['source_sha256_after']
 for name,h in data['source_sha256_after'].items():assert sha(name)==h,name
registration='verification/sections/308-preparation/maintained-registration.json';reg=read(registration)
assert reg['after_count']==475 and reg['original_ordered_prefix_unchanged']and reg['source_sha256']==sha('scripts/verify_full_available.py')
cp=read('DEVELOPMENT_CHECKPOINT.json');assert cp['completed_sections']==307 and cp['next_section']==308
assert cp['policy']['wrap_up_below_usage_percent']==15 and cp['policy']['development_paused_by_latest_user_request']is False
usage=read('verification/sections/308-preparation/usage-threshold.json');assert usage['remaining_percent']==92 and usage['strict_below15_triggered']is False
now=datetime.now(timezone(timedelta(hours=8))).isoformat();pending='<!-- section308-publication-pending -->当前为本地验收完成，普通推送与真实远端核对尚待完成。'
r={'section':308,'kind':'functional_section','title':title,'new_capability':change,'limitations':[limits],'at_Beijing':now,'branch':'codex/p2-development','necessary_validation':{**pin(necessary),'methods_run':99,'actual_exit':0},'native_windows_validation':{**pin(native),'process':pin(process),'unique_checks':57,'actual_Qt_exit':0,'exact_aliases':4,'actual_sizes_each':3,'all_accepted_cell_actual_clicks_across_alias_and_size':96,'new_distinct_source_acceptance':16},'root_visual_review':pin(visual),'original_project_window':pin(main),'source_build':pin('verification/sections/308-source-build-attempt1/process.json'),'source_sha256':n['source_sha256_after'],'validated_source_sha256':w['source_sha256_after'],'maintained_registry':pin(registration),'first_complete_frozen_comparison':pin('verification/sections/308-preparation/first-frozen-comparison.json'),'source_manifest':pin('research/p3-map-direct-ground-308/source-manifest.json'),'comparison_receipt':pin('research/p3-map-direct-ground-308/build-receipt.json'),'source_scope':{'requests':67,'new_accepted':16,'unknown_or_disagreed':51,'original_direct_points_preserved':107,'current_partial_images':14,'current_partial_stage_bindings':25,'current_partial_points':123,'regular_images_preserved':12,'regular_stages_preserved':24,'whole_map_stage_gap':81,'whole_map_bitmap_gap':59,'absolute_accuracy_verified':False},'failure_history':pin('verification/sections/308-preparation/necessary-failure-repair.json'),'legacy_current_native_variants_source_only':pin('verification/sections/308-preparation/current-legacy-source-contract-observation.json'),'full_suite_rerun':False,'last_full_receipt':'verification/full-305/summary.json','last_full_source_is_historical305':True,'next_periodic_full_section':320,'P3_complete':False,'P2_complete':False,'private_state_contents_parsed_copied_or_restored':False,'private_state_hashed_locally_for_preservation_only':True,'private_hashes_published':False,'game_operated':False,'chat_sent':False,'cloud_publication_binding':'enclosing_commit','cloud_published':False}
(ROOT/'verification/sections/308.json').write_bytes(enc(r))
details=change+'\n\n实际99项必要检查、57项原生唯一检查、四入口各三尺寸共12状态/96次接受格实际点击及五张截图核对通过；原测试窗口已更新可见响应，正常关闭至启动的私人五路径不变。475维护选择器保留原474有序范围。未重跑全量，305回执仅为其原历史范围，下一定期全量320；权限1314、历史私样本、Linux/Wine与游戏聊天仍不计通过。\n\n'+limits+'\n\n'+pending
for name in('PROJECT_COMPLETED.md','WORK_IN_PROGRESS.md'):
 path=ROOT/name;s=path.read_text('utf8')
 if name=='WORK_IN_PROGRESS.md':
  marker='以下为已交付历史。\n\n';assert s.startswith('## 当前进行第308节')and s.count(marker)==1;s=s.split(marker,1)[1]
 path.write_text('## 第308节 + '+title+'\n\n'+now+'。'+details+'\n\n以下为历史记录；当前断点以上述308为准。\n\n'+s,encoding='utf8')
path=ROOT/'PROJECT_PROGRESS.md';s=path.read_text('utf8');old='（其中12图/21关已有107格直接参考，整图仍未校准）';assert s.count(old)==1;s=s.replace(old,'',1);s=s.replace('；补齐单列/部分格校准的侧向外推验证','；补齐局部直接参考的其余格与单列/部分格校准的侧向外推验证',1);path.write_bytes(s.encode('utf8'))
path=ROOT/'AGENTS.md';s=path.read_text('utf8');end=s.index('\n## ',3);s='## 当前续接 · 第308节 + '+title+'\n\n'+details+'\n\n继续P3，309未启动；编号仅配实际完成改动，严格低于15%规则保留。\n'+s[end:];path.write_text(s,encoding='utf8')
path=ROOT/'PROJECT_REQUIREMENTS.md';s=path.read_text('utf8');start=s.index('<!-- current-delivery:start -->');end=s.index('<!-- current-delivery:end -->')+len('<!-- current-delivery:end -->');s=s[:start]+'<!-- current-delivery:start -->\n## 第308节 + '+title+'\n\n'+details+'\n<!-- current-delivery:end -->'+s[end:];path.write_text(s,encoding='utf8')
for key in('current_section_validation','latest_section_environment','cloud_publication_closeout','active_section'):
 if key in cp:cp['historical_before308_'+key]=cp.pop(key)
cp.update(completed_sections=308,latest_functional_section=308,next_section=309,batch_status='P3_SECTION308_LOCAL_ACCEPTED_PUBLICATION_PENDING',next_action='第308节 + '+title+'已本地验收，普通推送并真实远端核对后继续P3，下一定期全量320；完整校准81关59图仍保留。')
assert not any(s['number']==308 for s in cp['sections'])
cp['sections'].append({'number':308,'completion_ref':'p3-section-308','topic':title,'verification':'verification/sections/308.json'});cp['functional_sections_since_latest_requirement'].append(308)
cp['current_section_save']={'section':308,'verification':'verification/sections/308.json','scope':'current_functional_section','binding':'enclosing_commit'}
cp['last_verified_cloud_save']['scope']='previous_functional_section'
cp['current_section_validation']={'section':308,'receipt':'verification/sections/308.json','necessary_methods_passed':99,'native_isolated_window_checks':57,'native_exact_stage_and_size_states':12,'full_suite_rerun':False,'last_full_receipt':'verification/full-305/summary.json','full_source_is_historical305':True}
cp['latest_section_environment']={'section':308,'receipt':'verification/sections/308.json','native_windows':'99 necessary; 4 exact aliases / 3 actual sizes / 96 accepted-cell clicks; original app startup separately verified','native_game_or_chat_verified':False,'current_section_full_rerun':False,'last_full_receipt':'verification/full-305/summary.json','future_full_legacy_native_variants':reg['current_native_full_scope_variants']}
cp['current_batch'].update(status=cp['batch_status'],completed_sections=308,next_section=309,next_section_started=False,receipt='verification/sections/308.json',batch_closed=False)
cp['policy'].update(current_usage_remaining_percent=usage['remaining_percent'],current_usage_receipt='verification/sections/308-preparation/usage-threshold.json')
(ROOT/'DEVELOPMENT_CHECKPOINT.json').write_bytes(enc(cp))
path=ROOT/'CLOUD_HANDOFF.md';path.write_text(path.read_text('utf8')+'\n<!-- section308-handoff:start -->\n## 第308节 + '+title+'\n\n'+details+'\n<!-- section308-handoff:end -->\n',encoding='utf8')
runpy.run_path(str(ROOT/'scripts/update_cloud_index.py'))['update'](ROOT)
out=ROOT/'verification/sections/308-closeout';out.mkdir();(out/'execution-closeout.py').write_bytes(Path(__file__).read_bytes())
(out/'applied.json').write_bytes(enc({'section':308,'local_accepted':True,'ordinary_cloud_publication_verified':False,'at_Beijing':now,'next309_started':False,'section_label':read('CLOUD_INDEX.json')['current_section_label']}))
(ROOT/'verification/sections/308-preparation/execution-main-window.py').write_bytes((ROOT/'.cache/open_test_window_308.py').read_bytes())
print(json.dumps({'completed_section_label':read('CLOUD_INDEX.json')['current_section_label'],'cloud_publication_pending':True},ensure_ascii=False))
