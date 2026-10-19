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
title='当前关卡按层数、作战来源与同名配置分类预览'
change='版本与更新的关卡目录新增独立层数和作战来源筛选，并与新增改动范围、中文搜索求交集；普通、紧急、险路恶敌、追猎、鸭爵与雇员、狭路相逢、特殊挑战、流窜居民及坎诺特挑战分别选择。固定441984关卡总表77个具名入口与bee3当前184份完整关卡配置逐项核对，保留同名变体及稳定编号，不把目录当本局生成池。第一至第六层可查；第六层明确区分源流交汇处与盲目者所见，不把原编号7当第七层。22份特殊来源配置的层数保留未知，追猎明示属于节点外事件。选择精确配置可直接打开当前固定原图、敌人、出怪与条件奖励。新增独立分类来源页，原技术页完整契约保留；刷新保留筛选、条目、三个页签的滚动选区，坏源清旧并关闭预览，恢复后手动重选。修正旧的未接入出怪提示，不将部分资料说成全量计算。'
limits='层数与来源是固定社区目录参考，不是当前服务器生成脚本、全体强化版本池或实际进入资格。按精确中文名称和关卡代码关联资料，不按ID后缀推测层数或版本；普通/紧急再依据当前完整原表的isElite标志分开。全部184配置能找到目录入口，不代表每份配置都会自然生成或属于同一关卡实例。22份特殊来源配置缺准确层数，条件脚本、同名版本选择、当前热更新、特殊区域布局和完整奖励池仍未完成。原图完整坐标校准和出怪的全局时钟、完整预计面板及数值模型缺口保留；不把固定原图上的目标外观当新投影能力。本局资源和旧计算均未修改，不操作游戏、不发送聊天。小八界及制图桌另行查询仍缺可用数量/完整前置，保留未知。P3/P2/P1未完成，识别优化最后。'

necessary='verification/sections/317-necessary-attempt3/process.json';native='verification/sections/317-native-attempt2/actual/window.json';process='verification/sections/317-native-attempt2/process.json';source='verification/sections/317-source-attempt2/process.json';visual='verification/sections/317-root-visual.json';main='verification/sections/317-main-window.json';reg='verification/sections/317-preparation/maintained-registration.json'
n,w,p,s,v,m=(read(x)for x in(necessary,native,process,source,visual,main))
assert n['passed']and n['exit_code']==0 and n['methods_ran']==53
assert w['passed']and w['unique_checks']==25 and w['qpa']=='windows'and w['qt_exit_code']==0 and w['verification_window_closed']
assert len(w['actual_readings'])==6 and len(w['same_identity_refresh_observations'])==3
assert all(x==0 for x in w['external_operation_attempts'].values())and p['passed']and p['window_receipt_sha256']==sha(native)
assert s['passed']and s['exit_code']==0
for value in(n,w,s):
 assert value['source_sha256_before']==value['source_sha256_after']
 for name,digest in value['source_sha256_after'].items():assert sha(name)==digest,name
assert v['all_reviewed']and len(v['images'])==5
for image in v['images']:assert image['root_viewed']and sha(image['file'])==image['sha256']
assert m['passed']and m['private_entire_normal_close_and_start_interval_unchanged']and m['window_visible_and_responsive']
rr=read(reg);assert rr['before_count']==498 and rr['after_count']==501 and rr['original_ordered_prefix_unchanged']and rr['source_sha256']==sha('scripts/verify_full_available.py')
from rouge import current_stage_directory as model
ref=model.packet();assert ref is not None
scope={'game_commit':model.version.NEW_COMMIT,'community_revision':'441984','source_transport':'previous actual Windows-mcp Scrape use_dom=false/use_sampling=false; new exact selected excerpts','stage_refs':184,'documented_named_entries':77,'documented_layer_refs':162,'unknown_layer_special_refs':22,'all_stage_originals_checked_against_whole_current_source_in_necessary_run':True,'regions_in_layer6':['源流交汇处','盲目者所见'],'complete_actual_generation_pool_verified':False,'actual_current_server_verified':False,'actual_run_memory_updated':False}
out=ROOT/'verification/sections/317-preparation';shutil.copyfile(ROOT/'.cache/open_test_window_317.py',out/'execution-main-window.py');(out/'source-scope.json').write_bytes(enc(scope))
usage=read('verification/sections/317-preparation/usage-final.json');assert usage['remainingPercent']>=15
now=datetime.now(timezone(timedelta(hours=8))).isoformat();pending='<!-- section317-publication-pending -->本地验收完成，普通推送及真实远端核对待完成。'
r={'section':317,'kind':'functional_section','title':title,'new_capability':change,'limitations':[limits],'at_Beijing':now,'branch':'codex/p2-development',
 'necessary_validation':{**pin(necessary),'methods_run':53,'actual_exit':0},'native_windows_validation':{**pin(native),'process':pin(process),'unique_checks':25,'actual_Qt_exit':0,'actual_source_readings_and_jumps':6,'real_nonzero_refresh_states':3,'actual_MainWindow_compact_viewport':True,'actual_MainWindow_entry_exercised':True,'all_seven_real_external_operations_zero':True},
 'source_build':pin(source),'root_visual_review':pin(visual),'original_project_window':pin(main),'maintained_registry':pin(reg),'source_manifest':pin(model.MANIFEST),
 'source_sha256':n['source_sha256_after'],'validated_source_sha256':w['source_sha256_after'],'source_scope':scope,
 'failed_product_validation_attempts':[pin('verification/sections/317-necessary-attempt1/process.json')],
 'failure_explanation':'First necessary run had two wrong test expectations: Counter(dict) treats values as counts, and sixth-layer boss configurations are3 not7. Corrected actual key cardinality and independently read current filters, preserving complete directory and intersection assertions. Prior passing necessary2/native1 retained before correcting the stale no-spawn-information UI notice.',
 'full_suite_rerun':False,'last_full_receipt':'verification/full-305/summary.json','last_full_source_is_historical305':True,'next_periodic_full_section':320,'P3_complete':False,'P2_complete':False,'P1_complete':False,
 'private_state_contents_parsed_copied_or_restored':False,'private_state_hashed_locally_for_preservation_only':True,'private_hashes_published':False,'game_operated':False,'chat_sent':False,'cloud_publication_binding':'enclosing_commit','cloud_published':False}
(ROOT/'verification/sections/317.json').write_bytes(enc(r))
validation='实际53项必要检查、25项Windows原生唯一检查通过；实际MainWindow按层数/来源筛选，6项精确资料阅读（含普通/紧急、两份熄日、追猎和未知层数灰坑）、三组非零滚动选区保留、真实公开文件副本损坏清旧关闭预览及手动恢复通过；五张最终实际截图均已查看，七类游戏采样/聊天/凭证调用零次，临时本局与旧计算上下文不变。498维护选择器原序保持，现501；原测试窗口正常更新并可见响应，正常关闭至启动期间私人五路径未变。首轮两项测试前提错误及原失败完整保留。未重跑全量，305仅历史范围，下次定期全量320；符号链接1314、历史私样本、Linux/Wine及游戏聊天未计通过。'
details=change+'\n\n'+validation+'\n\n'+limits+'\n\n'+pending
for name in('PROJECT_COMPLETED.md','WORK_IN_PROGRESS.md'):
 text=(ROOT/name).read_text('utf8')
 if name=='WORK_IN_PROGRESS.md':assert text.startswith('## 正在进行第317节');text=text[text.index('## 第316节'):]
 doc(name,'## 第317节 + '+title+'\n\n'+now+'。'+details+'\n\n以下为历史记录；当前断点以上述317为准。\n\n'+text)
text=(ROOT/'AGENTS.md').read_text('utf8');end=text.index('\n## ',3);doc('AGENTS.md','## 当前续接 · 第317节 + '+title+'\n\n'+details+'\n\n继续P3，后续318优先新事件前置/作战与地图入口、完整奖励池和原图映射的剩余缺口。严格低于15%才开始完整收尾，下次定期全量320。\n'+text[end:])
text=(ROOT/'PROJECT_REQUIREMENTS.md').read_text('utf8');a=text.index('<!-- current-delivery:start -->');marker='<!-- current-delivery:end -->';b=text.index(marker)+len(marker)
doc('PROJECT_REQUIREMENTS.md',text[:a]+'<!-- current-delivery:start -->\n## 第317节 + '+title+'\n\n'+details+'\n'+marker+text[b:])
text=(ROOT/'PROJECT_PROGRESS.md').read_text('utf8');text=text.replace('新区域布局与准确层数分类','新区域布局、22份特殊来源关卡的准确层数和实际生成/强化版本选择依据',1).replace('15个事件/特殊关卡的层数适用依据','旧基准15个事件/特殊关卡的层数适用依据',1);doc('PROJECT_PROGRESS.md',text)
cp=read('DEVELOPMENT_CHECKPOINT.json');assert cp['completed_sections']==316 and cp['next_section']==317
for key in('current_section_validation','latest_section_environment','cloud_publication_closeout','active_section'):
 if key in cp:cp['historical_before317_'+key]=cp.pop(key)
cp.update(completed_sections=317,latest_functional_section=317,next_section=318,batch_status='P3_SECTION317_LOCAL_ACCEPTED_PUBLICATION_PENDING',next_action='第317节 + '+title+'已本地验收。普通推送核对后接续事件前置/作战入口、完整奖励池和原图映射；318未启动，下一定期全量320。')
cp['sections'].append({'number':317,'completion_ref':'p3-section-317','topic':title,'verification':'verification/sections/317.json'});cp['functional_sections_since_latest_requirement'].append(317)
cp['current_section_save']={'section':317,'verification':'verification/sections/317.json','scope':'current_functional_section','binding':'enclosing_commit'};cp['last_verified_cloud_save']['scope']='previous_functional_section'
cp['current_section_validation']={'section':317,'receipt':'verification/sections/317.json','necessary_methods_passed':53,'native_isolated_window_checks':25,'actual_source_readings_and_jumps':6,'real_nonzero_refresh_states':3,'full_suite_rerun':False,'last_full_receipt':'verification/full-305/summary.json','full_source_is_historical305':True}
cp['latest_section_environment']={'section':317,'receipt':'verification/sections/317.json','native_windows':'53 necessary;25 native actual MainWindow directory/current preview checks;6 readings and3 nonzero states;original app/private5 preservation verified','native_game_or_chat_verified':False,'current_section_full_rerun':False,'last_full_receipt':'verification/full-305/summary.json'}
cp['windows_native_validation']=validation;cp['current_batch'].update(status=cp['batch_status'],completed_sections=317,next_section=318,next_section_started=False,receipt='verification/sections/317.json',batch_closed=False)
cp['policy'].update(current_usage_remaining_percent=usage['remainingPercent'],current_usage_receipt='verification/sections/317-preparation/usage-final.json')
cp['current_data_versions'].update(current_stage_directory_commit=model.version.NEW_COMMIT,current_stage_directory_source_manifest=model.MANIFEST,current_stage_directory_community_revision='441984',current_stage_directory_unknown_layer_refs=22,current_stage_directory_actual_server_verified=False)
(ROOT/'DEVELOPMENT_CHECKPOINT.json').write_bytes(enc(cp))
doc('CLOUD_HANDOFF.md',(ROOT/'CLOUD_HANDOFF.md').read_text('utf8')+'\n<!-- section317-handoff:start -->\n## 第317节 + '+title+'\n\n'+details+'\n<!-- section317-handoff:end -->\n')
runpy.run_path(str(ROOT/'scripts/update_cloud_index.py'))['update'](ROOT)
out=ROOT/'verification/sections/317-closeout';out.mkdir();(out/'execution-closeout.py').write_bytes(Path(__file__).read_bytes());(out/'applied.json').write_bytes(enc({'section':317,'local_accepted':True,'ordinary_cloud_publication_verified':False,'next318_started':False,'at_Beijing':now}))
print(json.dumps({'section_label':read('CLOUD_INDEX.json')['current_section_label'],'scope':scope,'publication_pending':True},ensure_ascii=False))
