from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone,timedelta
import json,subprocess,runpy,shutil
ROOT=Path(__file__).resolve().parents[1]
def read(n):return json.loads((ROOT/n).read_bytes())
def enc(v):return(json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode('utf8')
def sha(n):return sha256((ROOT/n).read_bytes()).hexdigest()
def pin(n):return{'receipt':n,'sha256':sha(n)}
def doc(n,s):
 p=ROOT/n;style='\r\n'if b'\r\n'in p.read_bytes()else'\n';p.write_bytes(s.replace('\r\n','\n').replace('\n',style).encode('utf8'))
parent='d423b9bcee95745b4d360b8dc0e1295e7c87741b';assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()==parent
assert subprocess.check_output(['git','branch','--show-current'],cwd=ROOT).decode().strip()=='codex/p2-development'
title='节点目录直达完整事件资料，并保留阅读状态'
change='节点目录新增统一的“查看当前版本的完整事件资料”入口，把25个已有目录分组连接到23个事件、8类已核对的完整阅读器。逐项比对固定旧目录完整记录、原始情景ID、标题和完整正文，保留116处精确对应，不能仅凭同名连接；三重身三个目录分组分别保留。普通目录和已记住的历史节点均可查对话、选项、条件、奖励及既有作战配置/固定地图入口，明确这是固定版本参考，不确定本局版本、阶段、实际选项或领取结果。打开时不自动代入本局源石锭、化石、笼控器或其他条件；本页对照仍从未知开始。相同来源和节点的刷新保留两个阅读区的真实滚动与选区、手动条件、情景选项、配置和嵌套地图；换节点、换本局身份或来源失效时关闭旧阅读树。实际桥接资料损坏不影响原目录文字，恢复后由玩家手动重开；重复打开及实际主窗口关闭均清理整棵新阅读器和嵌套战斗窗口。'
limits='本节为现有资料的产品入口整合，复用321–331已核对的固定国服记录和完整文献包，无新机制或数值改动，不冒称重新下载或核对当前服务器。116个原情景ID及全文对应只证明资料可相互参照，不能证明实际节点使用同一版本、同一阶段或当前可选；旧目录没有条目的大红按钮、制图桌、手术祭坛仍留在版本资料页，不伪造节点入口。回滚文明等尚无当前完整阅读器的事件不冒充已接入。完整服务器出现资格、奖励池、真实发放和跨版本本局身份仍未知。固定地图只供查阅，条件与库存不回写本局、计算、地图或私人配置；不操作游戏、不发送聊天、不推荐路线或给出概率。P3/P2/P1仍未完成，识别最后。'
validation='本机41项必要测试全部通过，包含6项来源/构建检查、5项新入口界面检查、7项原节点目录和23项刷新相关检查；另有首轮11项探索检查通过但不代替带源码字节守卫的正式41项。构建输出逐字节一致。Windows原生临时MainWindow共41项唯一检查通过，遍历25组入口/23事件/8类阅读器、默认条件未知、历史节点和本局身份变化、两组真实非零阅读状态、选项/条件/配置及嵌套地图刷新保留、重复开窗/换条目/坏源和实际主窗口关闭的整树清理。九张实际PNG全部直接查看：八张阅读面板、一张坏源时仍可用的旧目录；新增版本提示通过真实Qt控件断言，内面板截图不冒称拍到外层提示。七类真实外部调用零，临时本局和旧计算上下文不变。原项目测试窗正常更新，可见、响应且前台，正常关闭到启动私人五路径保持一致。531旧维护选择器原序保留，现533。准备阶段CRLF插入断言和索引读取缺scripts导入路径均如实记录，不记为功能失败或测试通过。仅本机必要测试，不重复全量或未变索引25单测；320全量、原失败与不可用范围仍为历史，下一全量335。'
nname='verification/sections/332-necessary-attempt1/process.json';wname='verification/sections/332-native-attempt1/actual/window.json';pname='verification/sections/332-native-attempt1/process.json'
n,w,p=map(read,(nname,wname,pname));m=read('verification/sections/332-main-window.json');a=read('verification/sections/332-source-audit.json');v=read('verification/sections/332-root-visual.json')
assert n['passed']and n['methods_ran']==41 and w['passed']and w['qpa']=='windows'and w['qt_exit_code']==0 and w['unique_checks']==41 and w['verification_window_closed']
assert len(w['same_identity_refresh_observations'])==2 and len(w['screenshots'])==9 and len(w['actual_readings'])==25 and all(x==0 for x in w['external_operation_attempts'].values())
assert p['passed']and p['window_receipt_sha256']==sha(wname)
for result in(n,w):
 assert result['source_sha256_before']==result['source_sha256_after']
 for name,h in result['source_sha256_after'].items():assert sha(name)==h,name
assert v['passed']and len(v['final_screenshot_reviews'])==9 and a['ordered_previous531_preserved']and len(a['current_selectors'])==533
assert m['passed']and m['private_entire_normal_close_and_start_interval_unchanged']and m['window_visible_and_responsive']
now=datetime.now(timezone(timedelta(hours=8))).isoformat();pending='<!-- section332-publication-pending -->本地验收完成，普通推送及真实远端核对待完成。'
r={'section':332,'kind':'functional_section','title':title,'new_capability':change,'limitations':[limits],'at_Beijing':now,'branch':'codex/p2-development','necessary_validation':{**pin(nname),'methods_run':41,'actual_exit':0,'exploratory11_not_substitute_for_guarded41':'verification/sections/332-preparation/notes.json'},'native_windows_validation':{**pin(wname),'process':pin(pname),'unique_checks':41,'actual_Qt_exit':0,'catalogue_groups':25,'event_titles':23,'reader_types':8,'exact_scene_links':116,'real_nonzero_refresh_states':2,'actual_MainWindow_entry_and_close_exercised':True,'all_seven_real_external_operations_zero':True},'root_visual_review':pin('verification/sections/332-root-visual.json'),'source_audit':pin('verification/sections/332-source-audit.json'),'original_project_window':pin('verification/sections/332-main-window.json'),'source_sha256':n['source_sha256_after'],'validated_source_sha256':w['source_sha256_after'],'full_suite_rerun':False,'last_full_receipt':'verification/full-320/summary.json','last_full_receipt_is_historical_for_this_changed_source':True,'last_full_validation_sha256':sha('verification/full-320/summary.json'),'next_periodic_full_section':335,'P3_complete':False,'P2_complete':False,'P1_complete':False,'private_state_contents_parsed_copied_or_restored':False,'private_state_hashed_locally_for_preservation_only':True,'private_hashes_published':False,'game_operated':False,'chat_sent':False,'cloud_publication_binding':'enclosing_commit','cloud_published':False,'execution_environment':'local_original_windows_project_venv','local_source_parity_required_for_cloud_publication':True}
(ROOT/'verification/sections/332.json').write_bytes(enc(r));details=change+'\n\n'+validation+'\n\n'+limits+'\n\n'+pending
old_wip=subprocess.check_output(['git','show',parent+':WORK_IN_PROGRESS.md'],cwd=ROOT);(ROOT/'WORK_IN_PROGRESS.md').write_bytes(('## 第332节 + '+title+'\n\n'+now+'。'+details+'\n\n以下为历史记录；当前断点以上述332为准。\n\n').replace('\n','\r\n').encode()+old_wip)
doc('PROJECT_COMPLETED.md','## 第332节 + '+title+'\n\n'+now+'。'+details+'\n\n'+(ROOT/'PROJECT_COMPLETED.md').read_text('utf8'))
s=(ROOT/'AGENTS.md').read_text('utf8');end=s.index('\n## ',3);doc('AGENTS.md','## 当前续接 · 第332节 + '+title+'\n\n'+details+'\n\n继续P3；333从当前事件前置、完整奖励池、未有目录的新事件与固定地图实际剩余缺口接续，未启动。测试优先本机；保留到期完整范围，下次335；严格低于15%才开始完整收尾。\n'+s[end:])
s=(ROOT/'PROJECT_REQUIREMENTS.md').read_text('utf8');start=s.index('<!-- current-delivery:start -->');end=s.index('<!-- current-delivery:end -->')+len('<!-- current-delivery:end -->');doc('PROJECT_REQUIREMENTS.md',s[:start]+'<!-- current-delivery:start -->\n## 第332节 + '+title+'\n\n'+details+'\n<!-- current-delivery:end -->'+s[end:])
s=(ROOT/'PROJECT_PROGRESS.md').read_text('utf8');old='其余未覆盖完整事件表及其奖励条件';new='跨版本本局事件身份/阶段、尚无旧目录条目的新增事件入口与其余未适配的完整阅读器，其余未覆盖完整事件表及其奖励条件';assert s.count(old)==1;doc('PROJECT_PROGRESS.md',s.replace(old,new,1))
cp=read('DEVELOPMENT_CHECKPOINT.json');assert cp['completed_sections']==331 and cp['next_section']==332
for key in('current_section_validation','latest_section_environment','cloud_publication_closeout'):
 if key in cp:cp['historical_before332_'+key]=cp.pop(key)
cp.update(completed_sections=332,latest_functional_section=332,next_section=333,batch_status='P3_SECTION332_LOCAL_ACCEPTED_PUBLICATION_PENDING',next_action='第332节 + '+title+'已本机必要验收；普通推送核对后333接续P3实际剩余缺口，未启动。下次335。',full_validation_due=False)
cp['sections'].append({'number':332,'completion_ref':'p3-section-332','topic':title,'verification':'verification/sections/332.json'});cp['functional_sections_since_latest_requirement'].append(332)
cp['current_section_save']={'section':332,'verification':'verification/sections/332.json','scope':'current_functional_section','binding':'enclosing_commit'};cp['last_verified_cloud_save']['scope']='previous_functional_section'
cp['current_section_validation']={'section':332,'receipt':'verification/sections/332.json','methods_run':41,'native_isolated_window_checks':41,'catalogue_groups':25,'event_titles':23,'reader_types':8,'exact_scene_links':116,'real_nonzero_refresh_states':2,'full_suite_rerun':False,'last_full_receipt':'verification/full-320/summary.json','last_full_receipt_is_historical_for_current_changes':True}
cp['latest_section_environment']={'section':332,'receipt':'verification/sections/332.json','native_windows':validation,'native_game_or_chat_verified':False,'current_section_full_rerun':False,'last_full_receipt':'verification/full-320/summary.json'}
cp['windows_native_validation']=validation;cp['current_batch'].update(status=cp['batch_status'],completed_sections=332,next_section=333,next_section_started=False,receipt='verification/sections/332.json',batch_closed=False)
cp['policy'].update(current_usage_remaining_percent=98,current_usage_receipt='verification/sections/332-preparation/usage-final.json',verification_execution_preference='local_project_environment',avoid_duplicate_cloud_tests=True)
cp['current_data_versions'].update(current_node_readers_game_commit='bee3f83c5d60590b5e1cd42b8d09d00ce32ab10d',current_node_readers_catalogue_groups=25,current_node_readers_event_titles=23,current_node_readers_types=8,current_node_readers_exact_scene_links=116,current_node_actual_version_or_phase_verified=False)
(ROOT/'DEVELOPMENT_CHECKPOINT.json').write_bytes(enc(cp))
doc('CLOUD_HANDOFF.md',(ROOT/'CLOUD_HANDOFF.md').read_text('utf8')+'\n<!-- section332-handoff:start -->\n## 第332节 + '+title+'\n\n'+details+'\n<!-- section332-handoff:end -->\n')
out=ROOT/'verification/sections/332-preparation';shutil.copyfile(ROOT/'.cache/open_test_window_332.py',out/'execution-main-window.py')
runpy.run_path(str(ROOT/'scripts/update_cloud_index.py'))['update'](ROOT)
out=ROOT/'verification/sections/332-closeout';out.mkdir();(out/'execution-closeout.py').write_bytes(Path(__file__).read_bytes());(out/'applied.json').write_bytes(enc({'section':332,'local_accepted':True,'ordinary_cloud_publication_verified':False,'next333_started':False,'at_Beijing':now}))
print(json.dumps({'section':332,'local_accepted':True,'ordinary_publication_pending':True},ensure_ascii=False))
