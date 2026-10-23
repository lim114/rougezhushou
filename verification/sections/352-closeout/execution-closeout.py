from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone,timedelta
import json,runpy,subprocess,shutil
ROOT=Path(__file__).resolve().parents[1]
def read(n):return json.loads((ROOT/n).read_bytes())
def enc(v):return(json.dumps(v,ensure_ascii=False,indent=2)+chr(10)).encode('utf8')
def sha(n):return sha256((ROOT/n).read_bytes()).hexdigest()
def pin(n):return{'receipt':n,'sha256':sha(n)}
def doc(n,s):
 p=ROOT/n;style='\r\n'if b'\r\n'in p.read_bytes()else'\n';p.write_bytes(s.replace('\r\n','\n').replace('\n',style).encode('utf8'))
parent='df45ec99b83b7189aeb4eaf0f526b9a9b4897dba';assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()==parent
assert subprocess.check_output(['git','branch','--show-current'],cwd=ROOT).decode().strip()=='codex/p2-development'
title='版本资料并入通用页面，按真实物品类型分类'
change='取消独立的版本与更新栏目，将原有十类资料整合进战斗预览、节点事件、藏品与零件、探索设置四个常用页面，直接列出完整固定目录。关卡保留层数与作战来源，事件/选项/区域/结局在事件页，收藏品与零件及其他效果按原始物品类型分别选择，默认只列284条真实收藏品，395条原效果记录仍可按类型或明确总览查看，不把分队等条目冒称持有藏品。既有精确作战、事件流程、取得方式和后续原文入口保留；各页搜索、选择和阅读分别保持，真实鼠标切页与显式导航统一关闭不再对应的子窗。旧基准计算保留清楚适用范围，版本信息置于资料/结果旁，不静默混用新旧数值。'
limits='这是资料入口及分类的真实整合，不代表新版本计算、完整服务器资格、事件脚本、掉落池、实际领取或当前游戏状态已完成迁移。38份既有原生脚本和4份集成测试已按真实常用页迁移并做语法/检查保留核对；本节实际重跑6份代表原生流程，不宣称38份全部重跑或本节全量通过。固定来源仍为bee3国服10月16日；未知与新旧数值边界继续在对应页面说明，不增加游戏操作、聊天、路线建议或生成概率。P3/P2/P1仍未完成，识别最后；353地形等缓存预备不计完成或发布。'
validation='最终本机21项必要测试、29项新原生唯一检查通过，真实鼠标验证四个页面与全部十类资料、物品类型默认/总览、精确关卡/事件/取得方式入口、切页保留状态、损坏源清空四页与恢复手选、主窗关闭作战子窗。两种非零阅读的选区/滚动/页签保持在同一真实通用组件的紧凑独立窗口验证，未冒称主窗口默认视口有滚动条；原始非零前提失败与改前来源保留。首次原生27项通过后视觉发现原效果表混有分队等条目，增加真实类型分支后最终29通过，旧成功记录不充当前源码通过。6份迁移代表313/316/317/349/350/351原生分别23/24/26/45/34/24项通过；七类真实外部操作均零，临时本局/旧计算不变。最终8张功能截图主代理直接或逐字节相同的已审图复查；迁移代表29张由独立子代理逐张实际看图并按真实审阅者记录，不冒称主代理直接查看。原项目测试窗口已更新可见响应，整个正常关闭/启动期间私人五路径保持。571旧选择器原序保留，新加1个共572；350全量为本节改动前历史证据，下一定期365。索引实现未改，复用25项历史单测并实际校验当前要求/索引绑定。按用户授权继续至370，完整收尾后暂停。'
nname='verification/sections/352-necessary-attempt3/process.json';wname='verification/sections/352-native-attempt3/actual/window.json';pname='verification/sections/352-native-attempt3/process.json'
n,w,p=map(read,(nname,wname,pname));m=read('verification/sections/352-main-window.json');a=read('verification/sections/352-source-audit.json');v=read('verification/sections/352-root-visual.json')
assert n['passed']and n['methods_ran']==21 and w['passed']and w['qpa']=='windows'and w['qt_exit_code']==0 and w['unique_checks']==29 and w['verification_window_closed']
assert len(w['same_identity_refresh_observations'])==2 and len(w['screenshots'])==8 and len(w['actual_readings'])==10 and all(x==0 for x in w['external_operation_attempts'].values())
assert p['passed']and p['window_receipt_sha256']==sha(wname)
for result in(n,w):
 assert result['source_sha256_before']==result['source_sha256_after']
 for name,h in result['source_sha256_after'].items():assert sha(name)==h,name
assert v['passed']and len(v['final_screenshot_reviews'])==8 and a['ordered_previous571_preserved']and len(a['current_selectors'])==572
assert m['passed']and m['private_entire_normal_close_and_start_interval_unchanged']and m['window_visible_and_responsive']
now=datetime.now(timezone(timedelta(hours=8))).isoformat();pending='<!-- section352-publication-pending -->本地验收完成，普通推送及真实远端核对待完成。'
r={'section':352,'kind':'functional_section','title':title,'new_capability':change,'limitations':[limits],'at_Beijing':now,'branch':'codex/p2-development','necessary_validation':{**pin(nname),'methods_run':n['methods_ran'],'actual_exit':0},'native_windows_validation':{**pin(wname),'process':pin(pname),'unique_checks':w['unique_checks'],'actual_Qt_exit':0,'ordinary_pages':4,'reference_categories':10,'actual_collectibles_default':284,'complete_effect_rows_selectable':395,'real_nonzero_refresh_states':2,'actual_MainWindow_entry_and_close_exercised':True,'all_seven_real_external_operations_zero':True},'root_visual_review':pin('verification/sections/352-root-visual.json'),'source_audit':pin('verification/sections/352-source-audit.json'),'original_project_window':pin('verification/sections/352-main-window.json'),'source_sha256':n['source_sha256_after'],'validated_source_sha256':w['source_sha256_after'],'full_suite_rerun':False,'last_full_receipt':'verification/full-350/summary.json','last_full_receipt_is_historical_for_this_changed_source':True,'last_full_validation_sha256':sha('verification/full-350/summary.json'),'next_periodic_full_section':365,'P3_complete':False,'P2_complete':False,'P1_complete':False,'private_state_contents_parsed_copied_or_restored':False,'private_state_hashed_locally_for_preservation_only':True,'private_hashes_published':False,'game_operated':False,'chat_sent':False,'cloud_publication_binding':'enclosing_commit','cloud_published':False,'execution_environment':'local_original_windows_project_venv','local_source_parity_required_for_cloud_publication':True}
(ROOT/'verification/sections/352.json').write_bytes(enc(r));details=change+'\n\n'+validation+'\n\n'+limits+'\n\n'+pending
old_wip=(ROOT/'WORK_IN_PROGRESS.md').read_bytes();(ROOT/'WORK_IN_PROGRESS.md').write_bytes(('## 第352节 + '+title+'\n\n'+now+'。'+details+'\n\n以下为历史记录；当前断点以上述352为准。\n\n').replace('\n','\r\n').encode()+old_wip)
doc('PROJECT_COMPLETED.md','## 第352节 + '+title+'\n\n'+now+'。'+details+'\n\n'+(ROOT/'PROJECT_COMPLETED.md').read_text('utf8'))
s=(ROOT/'AGENTS.md').read_text('utf8');end=s.index('\n## 项目级最高优先要求');note='下一到期完整检查须给304/305两份full320验证脚本显式传入--source-freeze及当轮根声明冻结文件；默认320仅供历史绑定。351原失败与组合复验见verification/full-350/summary.json。312补充窗口采用既有120秒默认，304/305显式传入当轮source-freeze。'
doc('AGENTS.md','## 当前续接 · 第352节 + '+title+'\n\n'+details+'\n\n继续P3；353从实际剩余节点/事件条件、掉落和固定地图缺口接续，未启动。资料按通用内容分类；不得恢复单独版本栏目，版本范围在对应资料/结果旁标注。用户当前授权继续至370，完整收尾后暂停。只跑本机必要检查；下一全量365，严格低于15%才开始当前完整小节收尾。\n\n'+note+'\n'+s[end:])
s=(ROOT/'PROJECT_REQUIREMENTS.md').read_text('utf8');start=s.index('<!-- current-delivery:start -->');end=s.index('<!-- current-delivery:end -->')+len('<!-- current-delivery:end -->');doc('PROJECT_REQUIREMENTS.md',s[:start]+'<!-- current-delivery:start -->\n## 第352节 + '+title+'\n\n'+details+'\n<!-- current-delivery:end -->'+s[end:])
instruction='## 通用资料的统一入口（2026-10-23）\n\n用户要求将版本与更新中的内容整合到通用内容，不再设置独立版本栏目。关卡、事件、物品、分队与难度应在各自常用页面直接提供完整资料、分类和既有准确入口；版本来源与尚未迁移的计算范围在对应资料或结果旁说明，不能仅改栏目名称或静默混用数值。\n\n'
p=ROOT/'PROJECT_REQUIREMENTS.md';text=p.read_text('utf8');assert '## 通用资料的统一入口（2026-10-23）'not in text;marker='<!-- current-delivery:end -->';text=text.replace(marker,marker+'\n\n'+instruction,1);doc('PROJECT_REQUIREMENTS.md',text)
s=(ROOT/'PROJECT_PROGRESS.md').read_text('utf8');s=s.replace('更新：2026-10-22。','更新：2026-10-23。');doc('PROJECT_PROGRESS.md',s)
cp=read('DEVELOPMENT_CHECKPOINT.json');assert cp['completed_sections']==351 and cp['next_section']==352
for key in('current_section_validation','latest_section_environment','cloud_publication_closeout'):
 if key in cp:cp['historical_before352_'+key]=cp.pop(key)
cp.update(completed_sections=352,latest_functional_section=352,next_section=353,batch_status='P3_SECTION352_LOCAL_ACCEPTED_PUBLICATION_PENDING',next_action='第352节 + '+title+'已本机必要验收；普通推送核对后353接续P3实际剩余缺口，未启动。下次365。',full_validation_due=False)
cp['sections'].append({'number':352,'completion_ref':'p3-section-352','topic':title,'verification':'verification/sections/352.json'});cp['functional_sections_since_latest_requirement'].append(352)
cp['current_section_save']={'section':352,'verification':'verification/sections/352.json','scope':'current_functional_section','binding':'enclosing_commit'};cp['last_verified_cloud_save']['scope']='previous_functional_section'
cp['current_section_validation']={'section':352,'receipt':'verification/sections/352.json','methods_run':n['methods_ran'],'native_isolated_window_checks':w['unique_checks'],'ordinary_pages':4,'reference_categories':10,'actual_collectibles_default':284,'complete_effect_rows_selectable':395,'real_nonzero_refresh_states':2,'full_suite_rerun':False,'last_full_receipt':'verification/full-350/summary.json','last_full_receipt_is_historical_for_current_changes':True}
cp['latest_section_environment']={'section':352,'receipt':'verification/sections/352.json','native_windows':validation,'native_game_or_chat_verified':False,'current_section_full_rerun':False,'last_full_receipt':'verification/full-350/summary.json'}
cp['windows_native_validation']=validation;cp['current_batch'].update(status=cp['batch_status'],completed_sections=352,next_section=353,next_section_started=False,receipt='verification/sections/352.json',batch_closed=False)
cp['policy'].update(verification_execution_preference='local_project_environment',avoid_duplicate_cloud_tests=True)
cp['current_data_versions'].update(common_reference_pages=4,common_reference_categories=10,separate_update_tab=False,collectible_default_true_relics=284,full_effect_records_separately_selectable=395)
cp['policy']['latest_product_instruction_receipt']='verification/sections/352-preparation/scope.json'
cp['current_available_full_validation']['historical_for_current_changed_source']=True
cp['current_available_full_validation']['current_worktree_validation_authority']=False
cp['last_full_validation']['historical_for_current_changed_source']=True
(ROOT/'DEVELOPMENT_CHECKPOINT.json').write_bytes(enc(cp))
doc('CLOUD_HANDOFF.md',(ROOT/'CLOUD_HANDOFF.md').read_text('utf8')+'\n<!-- section352-handoff:start -->\n## 第352节 + '+title+'\n\n'+details+'\n<!-- section352-handoff:end -->\n')
out=ROOT/'verification/sections/352-closeout';out.mkdir();shutil.copyfile(ROOT/'.cache/open_test_window_352.py',out/'execution-main-window.py')
runpy.run_path(str(ROOT/'scripts/update_cloud_index.py'))['update'](ROOT)
(out/'execution-closeout.py').write_bytes(Path(__file__).read_bytes());(out/'applied.json').write_bytes(enc({'section':352,'local_accepted':True,'ordinary_cloud_publication_verified':False,'next353_started':False,'at_Beijing':now}))
print(json.dumps({'section':352,'local_accepted':True,'ordinary_publication_pending':True},ensure_ascii=False))
