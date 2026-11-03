from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone,timedelta
import json,runpy,sys,shutil
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
def read(n):return json.loads((ROOT/n).read_bytes())
def enc(v):return(json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode('utf8')
def sha(n):return sha256((ROOT/n).read_bytes()).hexdigest()
def pin(n):return {'receipt':n,'sha256':sha(n)}
def doc(n,s):
 p=ROOT/n;style='\r\n'if b'\r\n'in p.read_bytes()else'\n';p.write_bytes(s.replace('\r\n','\n').replace('\n',style).encode('utf8'))
title='旧日重燃事件前置、特殊区域和当前作战入口'
change='版本与更新新增独立结局条件入口，按线索与区域、命运所指、不期而遇、出现类型未确认四类查看7组信息、12个完整原选项及相关藏品。费用与探险家存活只核对对应选项，不误排除整个事件；救援每局一次，后续生成条件不删除当前或历史节点；未知与条件不符分别显示，矛盾声明提示且不擅自修正。熄日余径普通作战的额外1件随机收藏品按条件说明，不扩大到所有战斗或记为实际领取。灰坑与隐藏区域的7份当前关卡提供手动固定预览入口，普通、紧急和首领配置分别标明，两份同名熄日不按后缀或藏品擅选。刷新保留分类、事件、条件、相关作战、页签与非零阅读状态；来源损坏清旧、恢复手动重选。本页只用于对照，不保存输入为本局状态。'
limits='当前结局社区资料固定441984修订，实际来自Windows-mcp轻量Scrape返回的连续原文节选，不冒称原始HTTP字节或服务器脚本。已与bee3固定原表核对选项、明确nextSceneId、藏品与精确关卡引用；没有恢复场景到选项的完整脚本。制图桌完整出现前置与节点类型、隐藏层实际进入过程、两份同名熄日的实际选择、当前服务器资格及完整奖励池仍未知。文献节点数量标待补充，不作为模板上限；半目标生命上限的实际整数处理、实际触发/可选/领取/库存均不推算。声明条件不等于自动读取到的实际状态，也不计算生成概率或提供路线建议。新旧数值模型不混用。P3/P2/P1均未完成，识别优化最后；地图完整投影、其余节点和掉落与旧计算缺口继续保留。'
necessary='verification/sections/316-necessary-attempt4/process.json';native='verification/sections/316-native-attempt2/actual/window.json';process='verification/sections/316-native-attempt2/process.json';source='verification/sections/316-source-attempt3/process.json';visual='verification/sections/316-root-visual.json';main='verification/sections/316-main-window.json';reg='verification/sections/316-preparation/maintained-registration.json'
n,w,p,s,v,m=(read(x)for x in(necessary,native,process,source,visual,main))
assert n['passed']and n['exit_code']==0 and n['methods_ran']==51
assert w['passed']and w['unique_checks']==24 and w['qpa']=='windows'and w['qt_exit_code']==0 and w['verification_window_closed']
assert len(w['actual_readings'])==8 and len(w['same_identity_refresh_observations'])==2
assert all(x==0 for x in w['external_operation_attempts'].values())and p['passed']and p['window_receipt_sha256']==sha(native)
assert s['passed']and s['exit_code']==0
for value in(n,w,s):
 assert value['source_sha256_before']==value['source_sha256_after']
 for name,digest in value['source_sha256_after'].items():assert sha(name)==digest,name
assert v['all_reviewed']and len(v['images'])==5
for image in v['images']:assert image['root_viewed']and sha(image['file'])==image['sha256']
assert m['passed']and m['private_entire_normal_close_and_start_interval_unchanged']and m['window_visible_and_responsive']
rr=read(reg);assert rr['before_count']==496 and rr['after_count']==498 and rr['original_ordered_prefix_unchanged']and rr['source_sha256']==sha('scripts/verify_full_available.py')
from rouge import ending_event_reference as model
ref=model.packet();assert ref is not None
scope={'game_commit':model.battle.version.NEW_COMMIT,'community_revision':'441984','source_transport':'Windows-mcp Scrape use_dom=false/use_sampling=false','records':7,'complete_choices':12,'related_items':4,'stage_refs':7,'explicit_next_scenes':len(ref['data']['selected_originals']['scenes']),'entire_scene_choice_script_restored':False,'actual_current_server_verified':False,'actual_rewards':None,'actual_run_memory_updated':False}
out=ROOT/'verification/sections/316-preparation';shutil.copyfile(ROOT/'.cache/open_test_window_316.py',out/'execution-main-window.py');(out/'source-scope.json').write_bytes(enc(scope))
usage=read('verification/sections/316-preparation/usage-final.json');assert usage['remainingPercent']>=15
now=datetime.now(timezone(timedelta(hours=8))).isoformat();pending='<!-- section316-publication-pending -->本地验收完成，普通推送及真实远端核对待完成。'
r={'section':316,'kind':'functional_section','title':title,'new_capability':change,'limitations':[limits],'at_Beijing':now,'branch':'codex/p2-development',
 'necessary_validation':{**pin(necessary),'methods_run':51,'actual_exit':0},'native_windows_validation':{**pin(native),'process':pin(process),'unique_checks':24,'actual_Qt_exit':0,'actual_source_readings_and_jumps':8,'real_nonzero_refresh_states':2,'owned_event_dialog_compact_viewport':True,'actual_MainWindow_entry_exercised':True,'all_seven_real_external_operations_zero':True},
 'source_build':pin(source),'root_visual_review':pin(visual),'original_project_window':pin(main),'maintained_registry':pin(reg),'source_manifest':pin(model.MANIFEST),
 'source_sha256':n['source_sha256_after'],'validated_source_sha256':w['source_sha256_after'],'source_scope':scope,
 'failed_product_validation_attempts':[pin('verification/sections/316-necessary-attempt2/process.json'),pin('verification/sections/316-native-attempt1/process.json')],
 'failure_explanation':'Initial offscreen reader viewport had no scrollbar; used actual compact viewport retaining nonzero assertion. Initial native fixture forgot to change branch before selecting button; fixed fixture to use real branch, no automatic product selection. Preparation runner first failed before tests because fixture not yet written; no passing claim. Prior passing necessary attempt3 retained before fixture correction.',
 'full_suite_rerun':False,'last_full_receipt':'verification/full-305/summary.json','last_full_source_is_historical305':True,'next_periodic_full_section':320,'P3_complete':False,'P2_complete':False,'P1_complete':False,
 'private_state_contents_parsed_copied_or_restored':False,'private_state_hashed_locally_for_preservation_only':True,'private_hashes_published':False,'game_operated':False,'chat_sent':False,'cloud_publication_binding':'enclosing_commit','cloud_published':False}
(ROOT/'verification/sections/316.json').write_bytes(enc(r))
validation='实际51项必要检查、24项Windows原生唯一检查通过；主窗口实际打开结局条件入口，5组事件阅读与3次精确关卡跳转、两组非零滚动选区保留、真实公开文件副本损坏清旧和手动恢复通过；五张最终截图均已查看，七类游戏采样/聊天/凭证调用零次，临时本局与旧计算上下文不变。496维护选择器原序不减，现498；原测试窗口正常更新，可见响应，关闭至启动期间私人五路径未变。首轮视口及测试分类操作前提错误与失败回执保留。未重跑全量，305仅历史范围，下次定期全量320；符号链接1314、历史私样本、Linux/Wine与实际游戏聊天未计通过。'
details=change+'\n\n'+validation+'\n\n'+limits+'\n\n'+pending
for name in('PROJECT_COMPLETED.md','WORK_IN_PROGRESS.md'):
 text=(ROOT/name).read_text('utf8')
 if name=='WORK_IN_PROGRESS.md':assert text.startswith('## 正在进行第316节');text=text[text.index('## 第315节'):]
 doc(name,'## 第316节 + '+title+'\n\n'+now+'。'+details+'\n\n以下为历史记录；当前断点以上述316为准。\n\n'+text)
text=(ROOT/'AGENTS.md').read_text('utf8');end=text.index('\n## ',3);doc('AGENTS.md','## 当前续接 · 第316节 + '+title+'\n\n'+details+'\n\n继续P3，后续317优先新事件前置/作战与地图入口、完整奖励池和原图映射的剩余缺口。严格低于15%才开始完整收尾，下次定期全量320。\n'+text[end:])
text=(ROOT/'PROJECT_REQUIREMENTS.md').read_text('utf8');a=text.index('<!-- current-delivery:start -->');marker='<!-- current-delivery:end -->';b=text.index(marker)+len(marker)
doc('PROJECT_REQUIREMENTS.md',text[:a]+'<!-- current-delivery:start -->\n## 第316节 + '+title+'\n\n'+details+'\n'+marker+text[b:])
text=(ROOT/'PROJECT_PROGRESS.md').read_text('utf8');text=text.replace('新增事件完整前置与具体作战绑定、','制图桌完整出现前置/节点类型、其余新增事件完整前置、隐藏层实际进入脚本与同名熄日精确版本绑定、',1);doc('PROJECT_PROGRESS.md',text)
cp=read('DEVELOPMENT_CHECKPOINT.json');assert cp['completed_sections']==315 and cp['next_section']==316
for key in('current_section_validation','latest_section_environment','cloud_publication_closeout','active_section'):
 if key in cp:cp['historical_before316_'+key]=cp.pop(key)
cp.update(completed_sections=316,latest_functional_section=316,next_section=317,batch_status='P3_SECTION316_LOCAL_ACCEPTED_PUBLICATION_PENDING',next_action='第316节 + '+title+'已本地验收。普通推送核对后接续事件前置/作战入口、完整奖励池和原图映射；317未启动，下一定期全量320。')
cp['sections'].append({'number':316,'completion_ref':'p3-section-316','topic':title,'verification':'verification/sections/316.json'});cp['functional_sections_since_latest_requirement'].append(316)
cp['current_section_save']={'section':316,'verification':'verification/sections/316.json','scope':'current_functional_section','binding':'enclosing_commit'};cp['last_verified_cloud_save']['scope']='previous_functional_section'
cp['current_section_validation']={'section':316,'receipt':'verification/sections/316.json','necessary_methods_passed':51,'native_isolated_window_checks':24,'actual_source_readings_and_jumps':8,'real_nonzero_refresh_states':2,'full_suite_rerun':False,'last_full_receipt':'verification/full-305/summary.json','full_source_is_historical305':True}
cp['latest_section_environment']={'section':316,'receipt':'verification/sections/316.json','native_windows':'51 necessary;24 native actual MainWindow/event dialog checks;8 readings/jumps and2 nonzero states;original app/private5 preservation verified','native_game_or_chat_verified':False,'current_section_full_rerun':False,'last_full_receipt':'verification/full-305/summary.json'}
cp['windows_native_validation']=validation;cp['current_batch'].update(status=cp['batch_status'],completed_sections=316,next_section=317,next_section_started=False,receipt='verification/sections/316.json',batch_closed=False)
cp['policy'].update(current_usage_remaining_percent=usage['remainingPercent'],current_usage_receipt='verification/sections/316-preparation/usage-final.json')
cp['current_data_versions'].update(current_ending_game_commit=model.battle.version.NEW_COMMIT,current_ending_source_manifest=model.MANIFEST,current_ending_community_revision='441984',current_ending_actual_server_verified=False)
(ROOT/'DEVELOPMENT_CHECKPOINT.json').write_bytes(enc(cp))
doc('CLOUD_HANDOFF.md',(ROOT/'CLOUD_HANDOFF.md').read_text('utf8')+'\n<!-- section316-handoff:start -->\n## 第316节 + '+title+'\n\n'+details+'\n<!-- section316-handoff:end -->\n')
runpy.run_path(str(ROOT/'scripts/update_cloud_index.py'))['update'](ROOT)
out=ROOT/'verification/sections/316-closeout';out.mkdir();(out/'execution-closeout.py').write_bytes(Path(__file__).read_bytes());(out/'applied.json').write_bytes(enc({'section':316,'local_accepted':True,'ordinary_cloud_publication_verified':False,'next317_started':False,'at_Beijing':now}))
print(json.dumps({'section_label':read('CLOUD_INDEX.json')['current_section_label'],'scope':scope,'publication_pending':True},ensure_ascii=False))
