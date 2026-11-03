from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone,timedelta
from collections import Counter
from unittest.mock import patch
import json,runpy,sys,shutil
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
def read(n):return json.loads((ROOT/n).read_bytes())
def enc(v):return(json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode()
def sha(n):return sha256((ROOT/n).read_bytes()).hexdigest()
def pin(n):return {'receipt':n,'sha256':sha(n)}
def doc(n,s):
 p=ROOT/n;style='\r\n'if b'\r\n'in p.read_bytes()else'\n';p.write_bytes(s.replace('\r\n','\n').replace('\n',style).encode())
title='当前关卡条件奖励、同组候选与出现条件跳转'
change='当前版本关卡预览新增“奖励与条件”页，按宝箱与装置、移动恶笼草、稀有敌人独立分支阅读；按精确原引用核对184关卡/113份原件中的1056条装置、256条移动恶笼草、543条稀有敌人来源，1855是跨关卡引用条数而非实际数量。当前同bee3原角色/技能表的五类奖励装置明确区分2/5/10源石锭、50点部署费用换战后1零件，以及保险柜偷取1–2件商店物品和再部署限制。保留完整同队列候选、空条目、明确额外分支与别名冲突，不把候选相加、空奖励池当不会掉落、装置与派生敌人重复计奖；独立参数或培养/技能不匹配时数量未知。选择明确出现条件后跳到本关精确出怪条目，不进入旧关卡或操作游戏；移动与稀有敌人配对应图片。刷新保留分支、奖励项、条件入口、页签、滚动和选区；来源失效清旧，恢复手动选择。'
limits='这是固定来源的条件奖励预览，不是实际领奖或完整掉落计算。五类装置数量来自当前原表；移动恶笼草和四类稀有敌人数量沿用已固定的分级社区文献，并对当前关卡精确ID、等级、useDb和覆盖单独核验；不把旧文献改称新服务器结果。六个社区页面本地TLS下载各三次失败，全部保留并停止重试；实际web工具只重看了移动恶笼草级别0、鸭爵级别1的奖励条件和主题丰饶树冢随机零件说明，未重验其它所有等级或刷新修订号。小八界只保留当前五类名单身份，未取得新的奖励数量依据且当前固定关卡没有对应出怪行；不得用名单证明会生成。原图上的奖励位置、完整物品候选池、修正后的全部基础/额外奖励、实际激活/派生/击破/偷取/胜利/领取、完整服务器结算仍未知。无证参数不作默认计算，无实际总奖励，不改本局库存。P3/P2/P1均未完成，识别优化最后；314的原图完整校准、预计面板与时钟及其余事件前置缺口继续保留。'
necessary='verification/sections/315-necessary-attempt2/process.json';native='verification/sections/315-native-attempt2/actual/window.json';process='verification/sections/315-native-attempt2/process.json';source='verification/sections/315-source-attempt2/process.json';visual='verification/sections/315-root-visual.json';main='verification/sections/315-main-window.json';reg='verification/sections/315-preparation/maintained-registration.json'
n,w,p,s,v,m=(read(x)for x in(necessary,native,process,source,visual,main))
assert n['passed']and n['exit_code']==0 and n['methods_ran']==56
assert w['passed']and w['unique_checks']==26 and w['qpa']=='windows'and w['qt_exit_code']==0 and w['verification_window_closed']
assert len(w['actual_readings'])==13 and len(w['same_identity_refresh_observations'])==2
assert all(x==0 for x in w['external_operation_attempts'].values())and p['passed']and p['window_receipt_sha256']==sha(native)
assert s['passed']and s['exit_code']==0
for value in(n,w,s):
 assert value['source_sha256_before']==value['source_sha256_after']
 for name,digest in value['source_sha256_after'].items():assert sha(name)==digest,name
assert v['all_reviewed']and len(v['images'])==6
for image in v['images']:assert image['root_viewed']and sha(image['file'])==image['sha256']
assert m['passed']and m['private_entire_normal_close_and_start_interval_unchanged']and m['window_visible_and_responsive']
rr=read(reg);assert rr['before_count']==493 and rr['after_count']==496 and rr['original_ordered_prefix_unchanged']and rr['source_sha256']==sha('scripts/verify_full_available.py')
from rouge import current_reward_reference as model
ref=model.packet();assert ref is not None
counts=Counter();unqualified=0;stage_count=0
with patch.object(model,'packet',return_value=ref):
 for sid in ref['current']['version']['current']['details']['stages']:
  result=model.stage_rewards(sid);stage_count+=1
  for row in result['rows']:
   counts[row['kind']]+=1
   if row['kind']=='device'and not row['rule']['quantity_qualified']:unqualified+=1
assert dict(counts)=={'device':1056,'rare':543,'moving':256}and stage_count==184
scope={'game_commit':model.battle.version.NEW_COMMIT,'stage_refs':184,'unique_level_files':113,'reward_source_refs_by_kind':dict(counts),'total_source_refs_not_actual_reward_or_entity_total':sum(counts.values()),'current_primary_device_rule_count':5,'current_primary_character_and_skill_objects_checked_against_whole_downloads_in_necessary_run':True,'unqualified_device_source_rows_keep_quantities_unknown':unqualified,'community_grade_docs_reused_not_refreshed':True,'new_community_downloads_success':0,'six_local_TLS_sources_deferred_after_three_attempts_each':True,'reward_pool_complete':False,'actual_current_server_verified':False}
out=ROOT/'verification/sections/315-preparation';shutil.copyfile(ROOT/'.cache/open_test_window_315.py',out/'execution-main-window.py');(out/'source-scope.json').write_bytes(enc(scope))
usage=read('verification/sections/315-preparation/usage-final.json');assert usage['remainingPercent']>=15
now=datetime.now(timezone(timedelta(hours=8))).isoformat();pending='<!-- section315-publication-pending -->本地验收完成，普通推送及真实远端核对待完成。'
r={'section':315,'kind':'functional_section','title':title,'new_capability':change,'limitations':[limits],'at_Beijing':now,'branch':'codex/p2-development',
 'necessary_validation':{**pin(necessary),'methods_run':56,'actual_exit':0},'native_windows_validation':{**pin(native),'process':pin(process),'unique_checks':26,'actual_Qt_exit':0,'actual_source_readings_and_jumps':13,'real_nonzero_refresh_states':2,'owned_current_dialog_not_default_MainWindow_compact_viewport':True,'actual_MainWindow_entry_exercised':True,'all_seven_real_external_operations_zero':True},
 'source_build':pin(source),'root_visual_review':pin(visual),'original_project_window':pin(main),'maintained_registry':pin(reg),'source_manifest':pin(model.MANIFEST),
 'source_sha256':n['source_sha256_after'],'validated_source_sha256':w['source_sha256_after'],'source_scope':scope,
 'source_failure_history':[pin('research/p3-current-rewards-315/new-document-download-failures.json')],'failed_product_validation_attempts':[],'prior_passing_sources_retained':['verification/sections/315-necessary-attempt1/process.json','verification/sections/315-native-attempt1/process.json'],
 'full_suite_rerun':False,'last_full_receipt':'verification/full-305/summary.json','last_full_source_is_historical305':True,'next_periodic_full_section':320,'P3_complete':False,'P2_complete':False,'P1_complete':False,
 'private_state_contents_parsed_copied_or_restored':False,'private_state_hashed_locally_for_preservation_only':True,'private_hashes_published':False,'game_operated':False,'chat_sent':False,'cloud_publication_binding':'enclosing_commit','cloud_published':False}
(ROOT/'verification/sections/315.json').write_bytes(enc(r))
validation='实际56项必要检查、26项Windows原生唯一检查通过；主窗口真实打开三关奖励页，13次分类阅读/精确条件跳转、两组非零滚动选区保持、实际临时公开原件字节损坏与手动恢复通过，六张最终截图均已查看，七类游戏采样/聊天/凭证调用零次，临时本局与旧计算上下文不变。493维护选择器原序不减，现496；原测试窗口正常更新并可见响应，整个关闭/启动期间私人五路径未变。未重跑全量，305为历史可用范围，下次定期全量320；符号链接1314、历史私样本、Linux/Wine及实际游戏聊天未计通过。'
details=change+'\n\n'+validation+'\n\n'+limits+'\n\n'+pending
for name in('PROJECT_COMPLETED.md','WORK_IN_PROGRESS.md'):
 text=(ROOT/name).read_text('utf8')
 if name=='WORK_IN_PROGRESS.md':assert text.startswith('## 正在进行第315节');text=text[text.index('## 第314节'):]
 doc(name,'## 第315节 + '+title+'\n\n'+now+'。'+details+'\n\n以下为历史记录；当前断点以上述315为准。\n\n'+text)
text=(ROOT/'AGENTS.md').read_text('utf8');end=text.index('\n## ',3);doc('AGENTS.md','## 当前续接 · 第315节 + '+title+'\n\n'+details+'\n\n继续P3，后续316优先新事件前置/作战与地图入口、完整奖励池和原图映射的剩余缺口。严格低于15%才开始完整收尾，下次定期全量320。\n'+text[end:])
text=(ROOT/'PROJECT_REQUIREMENTS.md').read_text('utf8');a=text.index('<!-- current-delivery:start -->');marker='<!-- current-delivery:end -->';b=text.index(marker)+len(marker)
doc('PROJECT_REQUIREMENTS.md',text[:a]+'<!-- current-delivery:start -->\n## 第315节 + '+title+'\n\n'+details+'\n'+marker+text[b:])
text=(ROOT/'PROJECT_PROGRESS.md').read_text('utf8');text=text.replace('完整奖励池与发放条件、新区域布局与准确层数分类','完整奖励池与发放条件（含动态宝箱/派生实体与结算、小八界数量及当前社区文献修订缺口）、新区域布局与准确层数分类',1);doc('PROJECT_PROGRESS.md',text)
cp=read('DEVELOPMENT_CHECKPOINT.json');assert cp['completed_sections']==314 and cp['next_section']==315
for key in('current_section_validation','latest_section_environment','cloud_publication_closeout','active_section'):
 if key in cp:cp['historical_before315_'+key]=cp.pop(key)
cp.update(completed_sections=315,latest_functional_section=315,next_section=316,batch_status='P3_SECTION315_LOCAL_ACCEPTED_PUBLICATION_PENDING',next_action='第315节 + '+title+'已本地验收。普通推送核对后接续事件前置/作战入口、完整奖励池和原图映射；316未启动，下一定期全量320。')
cp['sections'].append({'number':315,'completion_ref':'p3-section-315','topic':title,'verification':'verification/sections/315.json'});cp['functional_sections_since_latest_requirement'].append(315)
cp['current_section_save']={'section':315,'verification':'verification/sections/315.json','scope':'current_functional_section','binding':'enclosing_commit'};cp['last_verified_cloud_save']['scope']='previous_functional_section'
cp['current_section_validation']={'section':315,'receipt':'verification/sections/315.json','necessary_methods_passed':56,'native_isolated_window_checks':26,'actual_source_readings_and_jumps':13,'real_nonzero_refresh_states':2,'full_suite_rerun':False,'last_full_receipt':'verification/full-305/summary.json','full_source_is_historical305':True}
cp['latest_section_environment']={'section':315,'receipt':'verification/sections/315.json','native_windows':'56 necessary;26 native actual MainWindow/current dialog checks;13 readings/jumps and2 nonzero states;original app/private5 preservation verified','native_game_or_chat_verified':False,'current_section_full_rerun':False,'last_full_receipt':'verification/full-305/summary.json'}
cp['windows_native_validation']=validation;cp['current_batch'].update(status=cp['batch_status'],completed_sections=315,next_section=316,next_section_started=False,receipt='verification/sections/315.json',batch_closed=False)
cp['policy'].update(current_usage_remaining_percent=usage['remainingPercent'],current_usage_receipt='verification/sections/315-preparation/usage-final.json')
cp['current_data_versions'].update(current_reward_primary_commit=model.battle.version.NEW_COMMIT,current_reward_source_manifest=model.MANIFEST,reward_grade_documentation_is_prior_pinned_community=True,current_reward_complete_pool_verified=False)
(ROOT/'DEVELOPMENT_CHECKPOINT.json').write_bytes(enc(cp))
doc('CLOUD_HANDOFF.md',(ROOT/'CLOUD_HANDOFF.md').read_text('utf8')+'\n<!-- section315-handoff:start -->\n## 第315节 + '+title+'\n\n'+details+'\n<!-- section315-handoff:end -->\n')
runpy.run_path(str(ROOT/'scripts/update_cloud_index.py'))['update'](ROOT)
out=ROOT/'verification/sections/315-closeout';out.mkdir();(out/'execution-closeout.py').write_bytes(Path(__file__).read_bytes());(out/'applied.json').write_bytes(enc({'section':315,'local_accepted':True,'ordinary_cloud_publication_verified':False,'next316_started':False,'at_Beijing':now}))
print(json.dumps({'section_label':read('CLOUD_INDEX.json')['current_section_label'],'scope':scope,'publication_pending':True},ensure_ascii=False))
