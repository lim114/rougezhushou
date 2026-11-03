from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone,timedelta
import json,runpy,sys,shutil
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
def read(n):return json.loads((ROOT/n).read_bytes())
def enc(v):return(json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode()
def sha(n):return sha256((ROOT/n).read_bytes()).hexdigest()
def pin(n):return {'receipt':n,'sha256':sha(n)}
def doc(n,s):
 p=ROOT/n;style='\r\n'if b'\r\n'in p.read_bytes()else'\n';p.write_bytes(s.replace('\r\n','\n').replace('\n',style).encode())
title='当前版本关卡的敌人、原图与出怪条件预览'
change='“版本与更新”的关卡新增独立预览入口，按精确ID接入184条关卡引用共用的113份完整关卡配置，覆盖387类敌人或关联实体的原始引用。按普通、精英、领袖及类别未确认提供独立选择分支；按主波次、条件分支筛选出怪、装置与演出条目，每个条件分支有独立编号。展示精确固定原图、关卡特点、设置和可取得的当前中文图鉴机制，354条图片资源引用逐字节核验，新增50份本地公开PNG；图鉴链接标记转为中文文字，完整原值保留技术页。等待、间隔、数量与随机/隐藏条件分别展示，不把候选相加为实际总数，也不将等待相加为绝对时刻。同版本刷新保留敌人、出怪条目、分类、页签及阅读状态；来源损坏清旧、恢复后重选敌人/条目，重复打开关闭旧预览，父页清空也关闭旧子窗。'
limits='本节恢复固定关卡配置与图鉴参考，不是当前全部机制或完整预计面板。当前保密等级、分队、藏品、技能/阶段与关卡符文修正后面板、实际生成/清场/分支时钟、原图坐标投影、完整掉落池与结算、具体事件到作战绑定及准确层数仍未完成。旧计算和旧战斗页继续原固定基准，不混用。387类引用不等于387种必出敌人；31个引用无独立图鉴，按各自明确配置保留未知，不借同名/去后缀机制。资源树有33个精确图片键缺失（含别名，不能直接算33种缺图敌人）；另enemy_1250_lyengs_2的原图初取及三次重试均失败，已搁置为缺图，取得稳定的同SHA原件或新来源后恢复，不能反复无条件重试。354为成功资源键数，不冒称354张不同图片或全部图片齐全。113个关卡树blob与完整当前原件选择核对通过；镜像固定版本与当前服务器/游戏安装版本一致仍未证明。P3/P2/P1均未完成，识别优化最后。'
necessary='verification/sections/314-necessary-attempt3/process.json';native='verification/sections/314-native-attempt2/actual/window.json';process='verification/sections/314-native-attempt2/process.json';source='verification/sections/314-source-attempt2/process.json';visual='verification/sections/314-root-visual.json';main='verification/sections/314-main-window.json'
n,w,p,s,v,m=(read(x)for x in(necessary,native,process,source,visual,main))
assert n['passed']and n['exit_code']==0 and n['methods_ran']==31
assert w['passed']and w['unique_checks']==22 and w['qpa']=='windows'and w['qt_exit_code']==0 and w['verification_window_closed']
assert len(w['actual_readings'])==15 and len(w['same_identity_refresh_observations'])==4
assert all(x==0 for x in w['external_operation_attempts'].values())and p['passed']and p['window_receipt_sha256']==sha(native)
assert s['passed']and s['exit_code']==0
for value in(n,w,s):
 assert value['source_sha256_before']==value['source_sha256_after']
 for name,digest in value['source_sha256_after'].items():assert sha(name)==digest,name
assert v['all_reviewed']and len(v['images'])==6
for image in v['images']:assert image['root_viewed']and sha(image['file'])==image['sha256']
assert m['passed']and m['private_entire_normal_close_and_start_interval_unchanged']and m['window_visible_and_responsive']
reg='verification/sections/314-preparation/maintained-registration.json';rr=read(reg);rr['source_sha256']=sha('scripts/verify_full_available.py');(ROOT/reg).write_bytes(enc(rr));assert rr['before_count']==490 and rr['after_count']==493 and rr['original_ordered_prefix_unchanged']
from rouge import current_battle_reference as model
ref=model.packet();assert ref is not None
levels=ref['inputs']['levels'];images=ref['portraits'];assert len(levels)==113 and len(ref['selection']['selected_enemy_ids'])==387 and len(images['images'])==354
usage=read('verification/sections/314-preparation/usage-final.json');assert usage['remainingPercent']>=15
stats={'stage_refs':184,'unique_level_files':113,'distinct_enemy_reference_ids':387,'enemyDbRefs_in_unique_levels':sum(len(l['enemyDbRefs'])for l in levels.values()),'all_action_rows_in_unique_levels':sum(len(q['actions'])for l in levels.values()for q in model.queues(l)),'image_resource_keys':354,'new_png_files':len(list((ROOT/'rouge/data/current-enemies').glob('*.png'))),'original_cache_equality_checked_in_necessary_run':True,'level_tree_blob_checks':113,'missing_handbook_ids':len(ref['selection']['handbook_missing']),'tree_missing_image_keys_including_aliases':33,'failed_image_keys':[x['identity']for x in images['failures']]}
repair={'section':314,'original_necessary_failure':pin('verification/sections/314-necessary-attempt1/process.json'),'original_sources':'verification/sections/314-necessary-attempt1/before-fix','facts':['First assertion incorrectly assumed a different level must have a different PNG: exact current tree proves the same PNG for ro6_n_4_1 and its dlc1 variant. Strict independent level-object inequality remains checked.','Short action text fitted the original wide reader: actual measured viewport302px and scrollbar maximum0. Resizable splitter narrowed the real reader, producing real wrapping and nonzero scrolling; no padding or assertion removal.','Final branch ordinal and old-child-window fixes were accepted by necessary attempt3 and native attempt2.'],'image_download_failures_retained':True,'one_image_deferred_after_initial_plus_three_retries':True,'retry_limit_note':'Collector used three retries after initial, exceeding the intended three total attempts for that image. No further request made; future retries count initial attempt.','restart_condition':'A new independently usable same-SHA image source or stable GitHub blob payload; no silent raw-URL repetition.'}
(ROOT/'verification/sections/314-preparation/repair-evidence.json').write_bytes(enc(repair));shutil.copyfile(ROOT/'.cache/open_test_window_314.py',ROOT/'verification/sections/314-preparation/execution-main-window.py')
now=datetime.now(timezone(timedelta(hours=8))).isoformat();pending='<!-- section314-publication-pending -->本地验收完成，普通推送及真实远端核对待完成。'
r={'section':314,'kind':'functional_section','title':title,'new_capability':change,'limitations':[limits],'at_Beijing':now,'branch':'codex/p2-development',
 'necessary_validation':{**pin(necessary),'methods_run':31,'actual_exit':0},'native_windows_validation':{**pin(native),'process':pin(process),'unique_checks':22,'actual_Qt_exit':0,'actual_source_readings':15,'real_nonzero_refresh_states':4,'owned_current_dialog_not_default_MainWindow_compact_viewport':True,'actual_MainWindow_entry_exercised':True,'all_seven_real_external_operations_zero':True},
 'source_build':pin(source),'root_visual_review':pin(visual),'original_project_window':pin(main),'maintained_registry':pin(reg),'source_manifest':pin(model.MANIFEST),
 'source_sha256':n['source_sha256_after'],'validated_source_sha256':w['source_sha256_after'],'source_scope':stats,
 'original_failure_history':[pin('verification/sections/314-necessary-attempt1/process.json')],'repair_evidence':pin('verification/sections/314-preparation/repair-evidence.json'),
 'full_suite_rerun':False,'last_full_receipt':'verification/full-305/summary.json','last_full_source_is_historical305':True,'next_periodic_full_section':320,'P3_complete':False,'P2_complete':False,'P1_complete':False,
 'private_state_contents_parsed_copied_or_restored':False,'private_state_hashed_locally_for_preservation_only':True,'private_hashes_published':False,'game_operated':False,'chat_sent':False,'cloud_publication_binding':'enclosing_commit','cloud_published':False}
(ROOT/'verification/sections/314.json').write_bytes(enc(r))
validation='实际31项必要检查、22项Windows原生唯一检查通过；MainWindow真实点击三个关卡预览入口、15次原图/敌人/条目阅读、四组真实非零滚动与选区保持通过。实际临时公开来源字节损坏清旧、恢复后重选验证，六张最终实际截图均已查看，七类采样/聊天/凭证调用零次，临时本局与旧计算上下文未变。首轮两项错误测试前提与原件均保留，改为同图不同配置与真实分栏视口核对；没有填充假文字或删除滚动断言。490个维护选择器原序保持，现493；未重跑全量，305仅历史范围，下次定期全量320。原测试窗口正常更新，可见响应，整个关闭/启动期间私人五路径未变。符号链接1314、历史私样本、Linux/Wine与实际游戏聊天未计通过。'
details=change+'\n\n'+validation+'\n\n'+limits+'\n\n'+pending
for name in('PROJECT_COMPLETED.md','WORK_IN_PROGRESS.md'):
 text=(ROOT/name).read_text('utf8')
 if name=='WORK_IN_PROGRESS.md':assert text.startswith('## 正在进行第314节');text=text[text.index('## 第313节'):]
 doc(name,'## 第314节 + '+title+'\n\n'+now+'。'+details+'\n\n以下为历史记录；当前断点以上述314为准。\n\n'+text)
text=(ROOT/'AGENTS.md').read_text('utf8');end=text.index('\n## ',3);doc('AGENTS.md','## 当前续接 · 第314节 + '+title+'\n\n'+details+'\n\n继续P3，后续315优先当前国服事件条件/奖励与原图映射的剩余缺口。严格低于15%才开始完整收尾，下次定期全量320。\n'+text[end:])
text=(ROOT/'PROJECT_REQUIREMENTS.md').read_text('utf8');a=text.index('<!-- current-delivery:start -->');marker='<!-- current-delivery:end -->';b=text.index(marker)+len(marker)
doc('PROJECT_REQUIREMENTS.md',text[:a]+'<!-- current-delivery:start -->\n## 第314节 + '+title+'\n\n'+details+'\n'+marker+text[b:])
text=(ROOT/'PROJECT_PROGRESS.md').read_text('utf8');a=text.index('| 3 | 国服10月拓展的功能迁移 |');b=text.index('\n',a)
todo='| 3 | 国服10月拓展的功能迁移 | 新184引用/85原图的位置校准与独立地标核验；难度/分队/关卡符文及技能阶段修正后的敌人面板，图鉴以外的关卡与阶段脚本、条件分支实际入口和完整时钟；新增事件完整前置与具体作战绑定、完整奖励池与发放条件、新区域布局与准确层数分类；等级16及新增/变更分队、收藏品、零件与长期科技实际效果和计算；精确图片缺键与enemy_1250_lyengs_2下载失败（原初取+三次重试保留，取得稳定同SHA新来源才恢复）。旧计算继续明示旧版本范围 |'
doc('PROJECT_PROGRESS.md',text[:a]+todo+text[b:])
cp=read('DEVELOPMENT_CHECKPOINT.json');assert cp['completed_sections']==313 and cp['next_section']==314
for key in('current_section_validation','latest_section_environment','cloud_publication_closeout','active_section'):
 if key in cp:cp['historical_before314_'+key]=cp.pop(key)
cp.update(completed_sections=314,latest_functional_section=314,next_section=315,batch_status='P3_SECTION314_LOCAL_ACCEPTED_PUBLICATION_PENDING',next_action='第314节 + '+title+'已本地验收。普通推送核对后接续当前国服事件前置/奖励与原图映射；315未启动，下一定期全量320。')
cp['sections'].append({'number':314,'completion_ref':'p3-section-314','topic':title,'verification':'verification/sections/314.json'});cp['functional_sections_since_latest_requirement'].append(314)
cp['current_section_save']={'section':314,'verification':'verification/sections/314.json','scope':'current_functional_section','binding':'enclosing_commit'};cp['last_verified_cloud_save']['scope']='previous_functional_section'
cp['current_section_validation']={'section':314,'receipt':'verification/sections/314.json','necessary_methods_passed':31,'native_isolated_window_checks':22,'actual_source_readings':15,'real_nonzero_refresh_states':4,'full_suite_rerun':False,'last_full_receipt':'verification/full-305/summary.json','full_source_is_historical305':True}
cp['latest_section_environment']={'section':314,'receipt':'verification/sections/314.json','native_windows':'31 necessary;22 native actual MainWindow and current dialog checks;15 readings and4 nonzero states;original app/private5 preservation verified','native_game_or_chat_verified':False,'current_section_full_rerun':False,'last_full_receipt':'verification/full-305/summary.json'}
cp['windows_native_validation']=validation;cp['current_batch'].update(status=cp['batch_status'],completed_sections=314,next_section=315,next_section_started=False,receipt='verification/sections/314.json',batch_closed=False)
cp['policy'].update(current_usage_remaining_percent=usage['remainingPercent'],current_usage_receipt='verification/sections/314-preparation/usage-final.json')
cp['current_data_versions'].update(current_battle_reference_commit=model.version.NEW_COMMIT,current_battle_reference_source_manifest=model.MANIFEST,current_battle_numeric_environment_migrated=False,current_battle_original_map_projection_verified=False)
(ROOT/'DEVELOPMENT_CHECKPOINT.json').write_bytes(enc(cp))
doc('CLOUD_HANDOFF.md',(ROOT/'CLOUD_HANDOFF.md').read_text('utf8')+'\n<!-- section314-handoff:start -->\n## 第314节 + '+title+'\n\n'+details+'\n<!-- section314-handoff:end -->\n')
runpy.run_path(str(ROOT/'scripts/update_cloud_index.py'))['update'](ROOT)
out=ROOT/'verification/sections/314-closeout';out.mkdir();(out/'execution-closeout.py').write_bytes(Path(__file__).read_bytes());(out/'applied.json').write_bytes(enc({'section':314,'local_accepted':True,'ordinary_cloud_publication_verified':False,'next315_started':False,'at_Beijing':now}))
print(json.dumps({'section_label':read('CLOUD_INDEX.json')['current_section_label'],'scope':stats,'publication_pending':True},ensure_ascii=False))
