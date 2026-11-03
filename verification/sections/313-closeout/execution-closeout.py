from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone,timedelta
import json,runpy,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
def read(n):return json.loads((ROOT/n).read_bytes())
def enc(v):return(json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode('utf8')
def sha(n):return sha256((ROOT/n).read_bytes()).hexdigest()
def pin(n):return{'receipt':n,'sha256':sha(n)}
def doc(n,s):
 p=ROOT/n;style='\r\n'if b'\r\n'in p.read_bytes()else'\n';p.write_bytes(s.replace('\r\n','\n').replace('\n',style).encode('utf8'))
title='国服10月拓展目录、固定原图与选项后续场景'
change='新增“版本与更新”页面，按十类中文分支查看10月16日内容拓展一的新增/改动或完整固定目录。当前镜像184条关卡引用均绑定精确原图，85份不同图像逐字节核验，其中80条关卡资料相对旧基准有变化，不能当作80张新地图。当前355场景、418选项等原资料分别阅读，17个新增场景和22个新增选项可筛选；只按明确nextSceneId手动跳转后续场景，并显示原物品提示，不猜选项前置和实际领取。保密等级16直接显示数字；同名条目在筛选前后保留稳定编号，四份月度小队初始状态不再被同等级合并。旧伤害与战斗页明确显示未整体迁移的新旧版本边界，原计算不被静默替换。'
limits='这是版本隔离的资料阅读与固定原图接入，不是完整更新适配。新关卡原始level、敌人图片/面板/机制、出怪/分支时钟、掉落池、事件前置和具体作战绑定、区域布局、层数分类、保密等级16及新分队/藏品/科技的实际计算仍须迁移核验。旧基准的81关59图校准缺口保留其旧范围，新184引用85原图不能借旧矩阵自动获得位置；本节未增加坐标、脚点或出生偏移映射。游戏原表的scene到choice入口链未提供时保持未知，不按编号或同名拼接，也不将当前完整目录当每种节点均可发生的候选。资料存在、物品提示或解锁文案不等于本局已持有、可选、触发或领取。当前服务器/安装版本与固定镜像相同仍未证明；当前计算页继续旧基准并明确提示，不能声称全新内容已算准。官方官网使用“内容拓展一”，用户称DLC2的官方编号未获印证；转帖与官网、镜像和社区来源区分。P3/P2/P1均未完成，识别优化最后。'
necessary='verification/sections/313-necessary-attempt4/process.json';native='verification/sections/313-native-attempt3/actual/window.json';process='verification/sections/313-native-attempt3/process.json';source='verification/sections/313-source-attempt3/process.json';visual='verification/sections/313-root-visual.json';main='verification/sections/313-main-window.json'
n,w,p,s,v,m=(read(x)for x in(necessary,native,process,source,visual,main))
assert n['passed']and n['exit_code']==0 and n['methods_ran']==31
assert w['passed']and w['unique_checks']==22 and w['qpa']=='windows'and w['qt_exit_code']==0 and w['verification_window_closed']
assert len(w['actual_readings'])==13 and len(w['same_identity_refresh_observations'])==2 and all(x['not_MainWindow_default_viewport']for x in w['same_identity_refresh_observations'])
assert all(x==0 for x in w['external_operation_attempts'].values())and p['passed']and p['window_receipt_sha256']==sha(native)
assert s['passed']and s['exit_code']==0
for value in(n,w,s):
 assert value['source_sha256_before']==value['source_sha256_after']
 for name,digest in value['source_sha256_after'].items():assert sha(name)==digest,name
assert v['all_reviewed']and len(v['images'])==5
for image in v['images']:assert image['root_viewed']and sha(image['file'])==image['sha256']
assert m['passed']and m['private_entire_normal_close_and_start_interval_unchanged']and m['window_visible_and_responsive']
reg='verification/sections/313-preparation/maintained-registration.json';rr=read(reg);assert rr['before_count']==487 and rr['after_count']==490 and rr['original_ordered_prefix_unchanged']and rr['source_sha256']==sha('scripts/verify_full_available.py')
from rouge.expansion_reference import packet,rows,CATEGORIES
reference=packet();assert reference is not None
counts={key:{'current':len(rows(key,changes_only=False,reference=reference)),'new_or_changed':len(rows(key,reference=reference))}for key,_ in CATEGORIES}
assert counts['stages']=={'current':184,'new_or_changed':80}and len(reference['images']['images'])==184
now=datetime.now(timezone(timedelta(hours=8))).isoformat();pending='<!-- section313-publication-pending -->本地验收完成，普通推送及真实远端核对待完成。'
r={'section':313,'kind':'functional_section','title':title,'new_capability':change,'limitations':[limits],'at_Beijing':now,'branch':'codex/p2-development',
 'necessary_validation':{**pin(necessary),'methods_run':31,'actual_exit':0},'native_windows_validation':{**pin(native),'process':pin(process),'unique_checks':22,'actual_Qt_exit':0,'actual_source_readings':13,'compact_owned_reader_nonzero_refresh_states':2,'default_MainWindow_nonzero_scroll_claimed':False,'actual_MainWindow_tab_exercised':True,'all_seven_real_external_operations_zero':True},
 'source_build':pin(source),'root_visual_review':pin(visual),'original_project_window':pin(main),'maintained_registry':pin(reg),'source_manifest':pin('research/p3-expansion-313/runtime-manifest.json'),
 'source_sha256':n['source_sha256_after'],'validated_source_sha256':w['source_sha256_after'],
 'source_scope':{'baseline_game_commit':'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add','current_game_commit':'bee3f83c5d60590b5e1cd42b8d09d00ce32ab10d','resource_commit':'de6cfb30ed1d41d9102d93e8ea400fc0cefc8ff7','full_original_two_topic_inputs_checked_in_actual_necessary_run':True,'complete_selected_rogue6_branches':['topics','details','modules','customizeData'],'global_constant_not_migrated':True,'category_counts':counts,'current_map_references':184,'distinct_map_blobs':85,'changed_stage_refs':80,'distinct_changed_map_blobs':41,'no_level_enemy_clock_pool_or_numeric_migration_claimed':True,'current_server_verified':False},
 'original_failure_history':[pin('verification/sections/313-necessary-attempt1/process.json'),pin('verification/sections/313-diagnostic-attempt1/process.json'),pin('verification/sections/313-native-attempt1/process.json')],
 'repair_evidence':pin('verification/sections/313-preparation/repair-evidence.json'),'failure_scope':'First necessary process terminated by actual Qt access violation after two assertion failures; isolated faulthandler reproduced clear(). Signals blocked during item destruction and explicit clear follows; two assertions resolved with stable whole-source labels and correct null-pixmap check. Original sources and failures kept. Native first attempt had an unmet nonzero viewport assertion, not product crash; separate actual compact reader now exercises that scope. Final grade16 title made explicit and final sources revalidated.',
 'full_suite_rerun':False,'last_full_receipt':'verification/full-305/summary.json','last_full_source_is_historical305':True,'next_periodic_full_section':320,'P3_complete':False,'P2_complete':False,'P1_complete':False,
 'private_state_contents_parsed_copied_or_restored':False,'private_state_hashed_locally_for_preservation_only':True,'private_hashes_published':False,'game_operated':False,'chat_sent':False,'cloud_publication_binding':'enclosing_commit','cloud_published':False}
(ROOT/'verification/sections/313.json').write_bytes(enc(r))
validation='实际31项必要检查、22项原生唯一检查通过；真实MainWindow的更新页、13次条目阅读、明确后续按钮、七类外部操作零调用及临时本局不变通过。两组非零滚动/选区保留在额外真实紧凑阅读窗口完成，不冒称主窗口默认小尺寸；五张最终实际截图均已查看。首轮Qt访问违规、独立诊断与原断言失败保留，阻断清空中的条目变更回调后通过；原生首轮视口条件未满足也保留，未加假文字或移除滚动断言。原十个机制阅读处理方法AST保持，维护选择器487原序不减，现490。原测试窗口正常更新并可见响应，整个关闭/启动期间私人五路径未变。未重跑全量，305只为历史范围，下次定期全量320；权限1314、历史私样本、Linux/Wine和游戏聊天不计通过。'
details=change+'\n\n'+validation+'\n\n'+limits+'\n\n'+pending
for name in('PROJECT_COMPLETED.md','WORK_IN_PROGRESS.md'):
 text=(ROOT/name).read_text('utf8')
 if name=='WORK_IN_PROGRESS.md':
  marker='以下为已交付历史。\n\n';assert text.startswith('## 当前进行第313节')and text.count(marker)==1;text=text.split(marker,1)[1]
 doc(name,'## 第313节 + '+title+'\n\n'+now+'。'+details+'\n\n以下为历史记录；当前断点以上述313为准。\n\n'+text)
text=(ROOT/'AGENTS.md').read_text('utf8');end=text.index('\n## ',3);doc('AGENTS.md','## 当前续接 · 第313节 + '+title+'\n\n'+details+'\n\n继续P3，后续314从当前国服新关卡/事件机制迁移接续；历史基准不冒称当前适用。严格低于15%才开始完整收尾，下次定期全量320。\n'+text[end:])
text=(ROOT/'PROJECT_REQUIREMENTS.md').read_text('utf8');a=text.index('<!-- current-delivery:start -->');marker='<!-- current-delivery:end -->';b=text.index(marker)+len(marker)
addition='## 国服内容更新与版本范围（2026-10-19）\n\n用户提醒“dlc2已经更新”。执行时先核实名称和来源：目前核实的为国服2026-10-16内容拓展一；不能把未经印证的DLC2编号写成官方事实。固定当前资料为游戏镜像bee3f83c5d60590b5e1cd42b8d09d00ce32ab10d及资源镜像de6cfb30ed1d41d9102d93e8ea400fc0cefc8ff7。旧a550基准、历史回执与私人本局记忆保留，不静默混算；新目录、原图已接入不等于新敌人/关卡/藏品数值已适配。新增关卡、变体、事件前置、作战绑定、奖励、等级16与分队/科技效果逐项按证迁移；完整来源条目数不等于全部可选事件、可获得收藏品、新地图或新分队数量。官方原帖、转载和解包镜像区分，不将未成功下载记作HTTP通过；当前服务器适用性仍单独核验。\n\n'
doc('PROJECT_REQUIREMENTS.md',text[:a]+'<!-- current-delivery:start -->\n## 第313节 + '+title+'\n\n'+details+'\n'+marker+'\n\n'+addition+text[b:])
text=(ROOT/'PROJECT_PROGRESS.md').read_text('utf8').replace('更新：2026-10-18。','更新：2026-10-19。',1)
head='| --- | --- | --- |';assert text.count(head)==1
newtodo='| 3 | 国服10月拓展的功能迁移 | 已固定的bee3资料中184条关卡引用的原始关卡几何、敌人图片/面板/机制与出怪/分支时钟迁移；新增事件的完整前置、场景选项入口与具体作战绑定，完整奖励池与发放条件；新区域布局与准确层数分类；等级16及新增/变更分队、收藏品、零件与长期科技的当前实际效果和计算迁移。当前目录/文本/原图阅读不能替代这些验收，旧计算继续明示旧版本范围 |'
text=text.replace(head,head+'\n'+newtodo,1)
text=text.replace('81个关卡、59张独立原图的完整坐标校准与独立地标核验','旧基准81个关卡、59张独立原图的完整坐标校准与独立地标核验；新184引用/85原图需按新关卡几何独立确认适用范围，不能仅凭同名或同图沿用旧矩阵',1)
doc('PROJECT_PROGRESS.md',text)
cp=read('DEVELOPMENT_CHECKPOINT.json');assert cp['completed_sections']==312 and cp['next_section']==313
for key in('current_section_validation','latest_section_environment','cloud_publication_closeout','active_section'):
 if key in cp:cp['historical_before313_'+key]=cp.pop(key)
cp.update(completed_sections=313,latest_functional_section=313,next_section=314,batch_status='P3_SECTION313_LOCAL_ACCEPTED_PUBLICATION_PENDING',next_action='第313节 + '+title+'已本地验收。普通推送核对后继续迁移bee3当前国服P3关卡几何/敌人/事件前置与作战绑定；314未启动，下一定期全量320。')
cp['sections'].append({'number':313,'completion_ref':'p3-section-313','topic':title,'verification':'verification/sections/313.json'});cp['functional_sections_since_latest_requirement'].append(313)
cp['current_section_save']={'section':313,'verification':'verification/sections/313.json','scope':'current_functional_section','binding':'enclosing_commit'};cp['last_verified_cloud_save']['scope']='previous_functional_section'
cp['current_section_validation']={'section':313,'receipt':'verification/sections/313.json','necessary_methods_passed':31,'native_isolated_window_checks':22,'actual_source_readings':13,'compact_real_reader_nonzero_refresh_states':2,'full_suite_rerun':False,'last_full_receipt':'verification/full-305/summary.json','full_source_is_historical305':True}
cp['latest_section_environment']={'section':313,'receipt':'verification/sections/313.json','native_windows':'31 necessary;22 native checks in actual MainWindow plus separate compact reader; source damage and recovery; exact original app startup/private5 preservation verified','native_game_or_chat_verified':False,'current_section_full_rerun':False,'last_full_receipt':'verification/full-305/summary.json'}
cp['current_batch'].update(status=cp['batch_status'],completed_sections=313,next_section=314,next_section_started=False,receipt='verification/sections/313.json',batch_closed=False)
cp['policy'].update(current_usage_remaining_percent=79,current_usage_receipt='verification/sections/313-preparation/usage-final.json',latest_data_update_instruction_receipt='verification/sections/313-preparation/scope.json')
cp['current_data_versions']={'reference_catalog_commit':'bee3f83c5d60590b5e1cd42b8d09d00ce32ab10d','reference_resource_commit':'de6cfb30ed1d41d9102d93e8ea400fc0cefc8ff7','calculation_and_original_battle_commit':'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add','legacy_calculation_boundary_visible':True,'whole_functional_migration_completed':False,'current_server_verified':False}
(ROOT/'DEVELOPMENT_CHECKPOINT.json').write_bytes(enc(cp))
doc('CLOUD_HANDOFF.md',(ROOT/'CLOUD_HANDOFF.md').read_text('utf8')+'\n<!-- section313-handoff:start -->\n## 第313节 + '+title+'\n\n'+details+'\n<!-- section313-handoff:end -->\n')
runpy.run_path(str(ROOT/'scripts/update_cloud_index.py'))['update'](ROOT)
out=ROOT/'verification/sections/313-closeout';out.mkdir();(out/'execution-closeout.py').write_bytes(Path(__file__).read_bytes());(out/'applied.json').write_bytes(enc({'section':313,'local_accepted':True,'ordinary_cloud_publication_verified':False,'next314_started':False,'at_Beijing':now}))
print(json.dumps({'section_label':read('CLOUD_INDEX.json')['current_section_label'],'current_catalog_stages':184,'current_images':85,'publication_pending':True},ensure_ascii=False))
