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
parent='79d72235054913bcc948e75877a21ba750de5e4d';assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()==parent
assert subprocess.check_output(['git','branch','--show-current'],cwd=ROOT).decode().strip()=='codex/p2-development'
title='洞中宝的四类结果、原记录后续分歧与阶段查阅'
change='新增洞中宝完整固定事件表的逐步查阅，保留46段原情景、44份完整原选项、10个文献阶段和8个可读选项组。四类文献随机结果各有独立入口，不指定本局结果或概率；取得源石锭后低鸣、空手后低鸣分开阅读，继续探索的文献说明不变成无限循环。两组同文案的8份原记录各有6份低鸣后续、2份结束后续，普通合读时分别提供文献后续与原记录结束入口、不默认其一；从版本页指定原件时准确跟随该份原记录的明确后续，原件没有下一段则保留未知。5源石锭与1件收藏品仅列各自分支，不相加、不按重复记录多领，完整收藏品池未知。90个原始情景/选项入口均保留精确来源；低鸣对话及继续/离开选项跨两个文献阶段时先选阶段，不靠文字或编号猜实际轮次。战斗原文没有具体关卡，明确说明并禁用未核对地图，不能将艰难当紧急。节点目录新增1个准入、46处原情景ID及全文对应，合计28目录组/26事件/10类阅读器；不自动代入资源或实际进度。刷新保留两组真实非零阅读、阶段、选择和精确来源；坏源清旧/手选恢复、重复开窗、父页和实际主窗关闭均清理新阅读窗。'
limits='复用321真实下载的BWIKI352356完整原HTTP，洞中宝整表保留原字符位置、字节与摘要；本轮独立网页文字复读四类结果及继续随机组说明，针对具体作战身份检索仍未获得精确关卡依据，不冒称重新下载HTML或服务器验证。46情景/44选项及1份物品完整记录逐项比较bee3与a550；资料成员由完整事件正文、旧目录明列原ID和原件明确后续共同限定，不用编号或前缀恢复父脚本。两条低鸣阶段只是原表分别写在取得源石锭及空手之后的文献上下文，同文原件全部保留，不认定实际阶段、次数、内外奇境实例或当前可选池。原记录还列有直接结束的选择，不能把文献重复说明当无限继续，也不合算5源石锭与1件收藏品。当前完整出现资格、各阶段候选和随机脚本、最大次数、奖励完整池与实际发放、具体战斗身份和版本仍未知。仅局外查阅，不操作游戏或聊天，不改本局/地图/资源/计算及私人配置，不给路线建议或概率。P3/P2/P1未完成、识别最后。'
validation='本机首轮41项必要检查中40项通过、1项因测试笔误失败：原应检查篡改副本，却调用了未改原件。只修正该测试的一处参数，保留首版完整测试字节与原失败日志，确认该方法以外AST及原生验证导入的clone辅助函数未变；最终定向1项复验通过，其余40项按未变范围复用，不声称最终重跑41项。产品代码和原生验证代码始终未改，原生Windows49项唯一检查复用，已遍历全部90个精确原始入口、10文献阶段/10阶段选项关系、四类结果单独查看无默认、两个同文后续分歧、指定原件继续或结束、两条低鸣阶段及来源保持、5源石锭与1件收藏品不相加、无精确关卡不开图、两组真实非零阅读经父页刷新保持、实际坏源清旧/手选恢复、重复开窗及父页/主窗关闭。10张实际PNG全部直接查看，含节点外层版本提示；七类真实外部调用零，临时本局与旧计算上下文不变。原测试窗正常更新、可见响应且前台，正常关闭到启动私人五路径不变。535旧维护选择器原序保留，现537。本节只跑本机必要检查，不重复已通过窗口/全量及未变索引25单测；320全量、原失败和不可用范围仍属历史，下一完整335。'
nname='verification/sections/334-necessary-attempt2/process.json';wname='verification/sections/334-native-attempt1/actual/window.json';pname='verification/sections/334-native-attempt1/process.json'
n,w,p=map(read,(nname,wname,pname));m=read('verification/sections/334-main-window.json');a=read('verification/sections/334-source-audit.json');v=read('verification/sections/334-root-visual.json')
assert n['passed']and n['methods_ran']==1 and w['passed']and w['qpa']=='windows'and w['qt_exit_code']==0 and w['unique_checks']==49 and w['verification_window_closed']
assert len(w['same_identity_refresh_observations'])==2 and len(w['screenshots'])==10 and len(w['actual_readings'])==10 and all(x==0 for x in w['external_operation_attempts'].values())
assert p['passed']and p['window_receipt_sha256']==sha(wname)
scope=read('verification/sections/334-check-scope/scope.json')
assert scope['outside_changed_method_AST_identical']and scope['native_imported_clone_helper_AST_unchanged']
for result in(n,w):
 assert result['source_sha256_before']==result['source_sha256_after']
 for name,h in result['source_sha256_after'].items():
  if result is w and name==scope['changed_file']:assert h==scope['original_sha256']and sha(name)==scope['current_sha256']
  else:assert sha(name)==h,name
assert v['passed']and len(v['final_screenshot_reviews'])==10 and a['ordered_previous535_preserved']and len(a['current_selectors'])==537
assert m['passed']and m['private_entire_normal_close_and_start_interval_unchanged']and m['window_visible_and_responsive']
now=datetime.now(timezone(timedelta(hours=8))).isoformat();pending='<!-- section334-publication-pending -->本地验收完成，普通推送及真实远端核对待完成。'
r={'section':334,'kind':'functional_section','title':title,'new_capability':change,'limitations':[limits],'at_Beijing':now,'branch':'codex/p2-development','necessary_validation':{**pin(nname),'final_targeted_method_run':1,'initial40_passed_methods_reused':True,'actual_exit':0},'native_windows_validation':{**pin(wname),'process':pin(pname),'unique_checks':49,'actual_Qt_exit':0,'documented_events':1,'document_scene_contexts':10,'document_choices':8,'original_scenes':46,'original_choices':44,'original_source_entries':90,'new_catalogue_groups':1,'exact_scene_links':46,'real_nonzero_refresh_states':2,'actual_MainWindow_entry_and_close_exercised':True,'all_seven_real_external_operations_zero':True},'root_visual_review':pin('verification/sections/334-root-visual.json'),'source_audit':pin('verification/sections/334-source-audit.json'),'original_project_window':pin('verification/sections/334-main-window.json'),'source_sha256':n['source_sha256_after'],'validated_source_sha256':{k:h for k,h in w['source_sha256_after'].items()if k!=scope['changed_file']},'native_test_only_fix_scope':pin('verification/sections/334-check-scope/scope.json'),'native_test_file_original_guard_retained_in_original_receipt':True,'initial_failure_retained':'verification/sections/334-necessary-attempt1/process.json','full_suite_rerun':False,'last_full_receipt':'verification/full-320/summary.json','last_full_receipt_is_historical_for_this_changed_source':True,'last_full_validation_sha256':sha('verification/full-320/summary.json'),'next_periodic_full_section':335,'P3_complete':False,'P2_complete':False,'P1_complete':False,'private_state_contents_parsed_copied_or_restored':False,'private_state_hashed_locally_for_preservation_only':True,'private_hashes_published':False,'game_operated':False,'chat_sent':False,'cloud_publication_binding':'enclosing_commit','cloud_published':False,'execution_environment':'local_original_windows_project_venv','local_source_parity_required_for_cloud_publication':True}
(ROOT/'verification/sections/334.json').write_bytes(enc(r));details=change+'\n\n'+validation+'\n\n'+limits+'\n\n'+pending
old_wip=subprocess.check_output(['git','show',parent+':WORK_IN_PROGRESS.md'],cwd=ROOT);(ROOT/'WORK_IN_PROGRESS.md').write_bytes(('## 第334节 + '+title+'\n\n'+now+'。'+details+'\n\n以下为历史记录；当前断点以上述334为准。\n\n').replace('\n','\r\n').encode()+old_wip)
doc('PROJECT_COMPLETED.md','## 第334节 + '+title+'\n\n'+now+'。'+details+'\n\n'+(ROOT/'PROJECT_COMPLETED.md').read_text('utf8'))
s=(ROOT/'AGENTS.md').read_text('utf8');end=s.index('\n## ',3);doc('AGENTS.md','## 当前续接 · 第334节 + '+title+'\n\n'+details+'\n\n继续P3；335从当前事件前置、完整奖励池、未有目录的新事件与固定地图实际剩余缺口接续，未启动。测试优先本机；保留到期完整范围，下次335；严格低于15%才开始完整收尾。\n'+s[end:])
s=(ROOT/'PROJECT_REQUIREMENTS.md').read_text('utf8');start=s.index('<!-- current-delivery:start -->');end=s.index('<!-- current-delivery:end -->')+len('<!-- current-delivery:end -->');doc('PROJECT_REQUIREMENTS.md',s[:start]+'<!-- current-delivery:start -->\n## 第334节 + '+title+'\n\n'+details+'\n<!-- current-delivery:end -->'+s[end:])
s=(ROOT/'PROJECT_PROGRESS.md').read_text('utf8').replace('更新：2026-10-20。','更新：2026-10-21。');old='其余未覆盖完整事件表及其奖励条件';new='洞中宝完整资格/原记录实际阶段/各阶段随机候选与最大次数/奖励池和发放/具体作战身份及版本，其余未覆盖完整事件表及其奖励条件';assert s.count(old)==1;doc('PROJECT_PROGRESS.md',s.replace(old,new,1))
cp=read('DEVELOPMENT_CHECKPOINT.json');assert cp['completed_sections']==333 and cp['next_section']==334
for key in('current_section_validation','latest_section_environment','cloud_publication_closeout'):
 if key in cp:cp['historical_before334_'+key]=cp.pop(key)
cp.update(completed_sections=334,latest_functional_section=334,next_section=335,batch_status='P3_SECTION334_LOCAL_ACCEPTED_PUBLICATION_PENDING',next_action='第334节 + '+title+'已本机必要验收；普通推送核对后335接续P3实际剩余缺口，未启动。下次335。',full_validation_due=False)
cp['sections'].append({'number':334,'completion_ref':'p3-section-334','topic':title,'verification':'verification/sections/334.json'});cp['functional_sections_since_latest_requirement'].append(334)
cp['current_section_save']={'section':334,'verification':'verification/sections/334.json','scope':'current_functional_section','binding':'enclosing_commit'};cp['last_verified_cloud_save']['scope']='previous_functional_section'
cp['current_section_validation']={'section':334,'receipt':'verification/sections/334.json','final_targeted_method_run':1,'initial40_passed_methods_reused':True,'native_isolated_window_checks':49,'documented_events':1,'document_scene_contexts':10,'document_choices':8,'original_scenes':46,'original_choices':44,'original_source_entries':90,'new_catalogue_groups':1,'exact_scene_links':46,'real_nonzero_refresh_states':2,'full_suite_rerun':False,'last_full_receipt':'verification/full-320/summary.json','last_full_receipt_is_historical_for_current_changes':True}
cp['latest_section_environment']={'section':334,'receipt':'verification/sections/334.json','native_windows':validation,'native_game_or_chat_verified':False,'current_section_full_rerun':False,'last_full_receipt':'verification/full-320/summary.json'}
cp['windows_native_validation']=validation;cp['current_batch'].update(status=cp['batch_status'],completed_sections=334,next_section=335,next_section_started=False,receipt='verification/sections/334.json',batch_closed=False)
cp['policy'].update(current_usage_remaining_percent=97,current_usage_receipt='verification/sections/334-preparation/usage-final.json',verification_execution_preference='local_project_environment',avoid_duplicate_cloud_tests=True)
cp['current_data_versions'].update(current_cave_game_commit='bee3f83c5d60590b5e1cd42b8d09d00ce32ab10d',current_cave_document_revision=352356,current_cave_document_scenes=10,current_cave_document_choices=8,current_cave_original_scenes=46,current_cave_original_choices=44,current_cave_original_source_entries=90,current_cave_exact_stage_verified=False,current_cave_max_attempts_verified=False,current_node_reader_aggregate_catalogue_groups=28,current_node_reader_aggregate_event_titles=26,current_node_reader_aggregate_types=10,current_node_actual_version_or_phase_verified=False)
(ROOT/'DEVELOPMENT_CHECKPOINT.json').write_bytes(enc(cp))
doc('CLOUD_HANDOFF.md',(ROOT/'CLOUD_HANDOFF.md').read_text('utf8')+'\n<!-- section334-handoff:start -->\n## 第334节 + '+title+'\n\n'+details+'\n<!-- section334-handoff:end -->\n')
out=ROOT/'verification/sections/334-preparation';shutil.copyfile(ROOT/'.cache/open_test_window_334.py',out/'execution-main-window.py')
runpy.run_path(str(ROOT/'scripts/update_cloud_index.py'))['update'](ROOT)
out=ROOT/'verification/sections/334-closeout';out.mkdir();(out/'execution-closeout.py').write_bytes(Path(__file__).read_bytes());(out/'applied.json').write_bytes(enc({'section':334,'local_accepted':True,'ordinary_cloud_publication_verified':False,'next335_started':False,'at_Beijing':now}))
print(json.dumps({'section':334,'local_accepted':True,'ordinary_publication_pending':True},ensure_ascii=False))
