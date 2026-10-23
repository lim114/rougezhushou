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
parent='87b3f79683d0a406ae2d544502323e9239003a70';assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()==parent
assert subprocess.check_output(['git','branch','--show-current'],cwd=ROOT).decode().strip()=='codex/p2-development'
title='行动奖励的当前版本候选、继承来源与专门条件'
change='行动奖励页面可分别查看常规支援候选和继承的额外支援，收录当前固定资料中的十二条准确选项、六件继承收藏品及行动奖励原文。总览明确说明它是资料目录，不把十二项当成本次菜单或同时奖励。仅显示所选支援所需的模式、上次完成区域、源石锭或继承来源；默认未知，核对一/二区域和五/六源石锭边界。同名继承记录按明确原件分别对应，当前持有不反推上次继承。金乌的奖励时点为进入喋血区域，九头蛇成长等未证数值仍保留未知。父页刷新保留选项、手动条件及两组非零阅读位置；坏源清空旧内容并可手动恢复，主窗关闭清理所属窗口。本节同时修正节点页面按钮多占一行导致小窗口阅读区缩小的问题，保留所有入口。'
limits='采用固定bee3国服2026-10-16资料，十二条选项、六件收藏品与一个场景共十九个准确原项分别核对。六个常规候选与六份独立继承来源不等于当前菜单；资料所述三项常规选项和一项额外继承仍受实际资格、抽取和账户状态限制。实际出现菜单、完整服务器资格、费用和奖励结算、生命及编制容量底限、九头蛇区域成长/重复获取/丢失数值均未由本节证明。手动条件仅供本页资料对照，不写本局或修改计算，不生成路线建议、概率或虚构作战入口；P3/P2/P1未完成，识别最后。'
validation='最终本机22项相关测试、33项原生窗口检查通过，五张功能截图已逐张复查；修复另有38项相关测试、142项节点窗口检查及44项取得入口检查。到期350完整范围仍在本机执行，只有完整终态摘要通过后本脚本才允许记录验收：保留569个维护选择器、52份旧状态与独立完整审核、原30项及其可用29项、65组P3补充窗口。首轮原始失败、改前源码和修复回执全部保留；修正一个实际布局问题、两处过时断言及304/305审核器的参数比较，未削减原验收范围。第二轮根进程实际退出1，312在完整检查强制60秒时超时；相同源码按该脚本原有120秒默认上限完整复验31项通过，合并证据支持可用范围通过，不宣称单次全绿、原60秒通过或性能已改善。原生截图使用主代理直接查看或逐字节相同的已审阅原图；具体数量和不可用项以本节完整摘要为准。符号链接1314、历史Windows/私有样本、Linux/Wine与实际游戏聊天范围不计通过。原项目测试窗首次启动响应断言失败且未保留私人前后哈希；随后确认该窗健康并完成第二次正常重启，可见响应，第二次完整关闭/启动区间私人五路径保持，首次区间不补称通过；云端不重复跑测试。索引实现未改，复用历史25项单测，仍实际校验本节文档和索引绑定。下一定期全量365。'
nname='verification/sections/350-necessary-attempt2/process.json';wname='verification/sections/350-native-attempt2/actual/window.json';pname='verification/sections/350-native-attempt2/process.json'
n,w,p=map(read,(nname,wname,pname));m=read('verification/sections/350-main-window.json');a=read('verification/sections/350-final-source-audit.json');v=read('verification/sections/350-root-visual-attempt2.json')
assert n['passed']and n['methods_ran']==22 and w['passed']and w['qpa']=='windows'and w['qt_exit_code']==0 and w['unique_checks']==33 and w['verification_window_closed']
assert len(w['same_identity_refresh_observations'])==2 and len(w['screenshots'])==5 and len(w['actual_readings'])==19 and all(x==0 for x in w['external_operation_attempts'].values())
assert p['passed']and p['window_receipt_sha256']==sha(wname)
for result in(n,w):
 assert result['source_sha256_before']==result['source_sha256_after']
 for name,h in result['source_sha256_after'].items():assert sha(name)==h,name
assert v['all_reviewed']and len(v['images'])==5 and a['ordered_previous567_preserved']and len(a['current_selectors'])==569
assert m['passed']and m['private_entire_normal_close_and_start_interval_unchanged']and m['window_visible_and_responsive']
full=read('verification/full-350/summary.json');assert full['after_section']==350 and full['available_checks_passed']is True and full['actual_validation_attempt']==2 and full['maintained_selectors']==569 and full['scope_not_reduced']
validation=validation.replace('到期350完整范围仍在本机执行，只有完整终态摘要通过后本脚本才允许记录验收：','到期350完整可用范围已在本机通过：')
now=datetime.now(timezone(timedelta(hours=8))).isoformat();pending='<!-- section350-publication-pending -->本地验收完成，普通推送及真实远端核对待完成。'
r={'section':350,'kind':'functional_section','title':title,'new_capability':change,'limitations':[limits],'at_Beijing':now,'branch':'codex/p2-development','necessary_validation':{**pin(nname),'methods_run':n['methods_ran'],'actual_exit':0},'native_windows_validation':{**pin(wname),'process':pin(pname),'unique_checks':w['unique_checks'],'actual_Qt_exit':0,'current_startup_choices':12,'regular_candidates':6,'independent_inherited_sources':6,'current_original_entries':19,'actual_menu_verified':False,'real_nonzero_refresh_states':2,'actual_MainWindow_entry_and_close_exercised':True,'all_seven_real_external_operations_zero':True},'root_visual_review':pin('verification/sections/350-root-visual-attempt2.json'),'source_audit':pin('verification/sections/350-final-source-audit.json'),'original_project_window':pin('verification/sections/350-main-window.json'),'source_sha256':n['source_sha256_after'],'validated_source_sha256':w['source_sha256_after'],'full_suite_rerun':True,'last_full_receipt':'verification/full-350/summary.json','last_full_receipt_is_historical_for_this_changed_source':False,'last_full_validation_sha256':sha('verification/full-350/summary.json'),'next_periodic_full_section':365,'P3_complete':False,'P2_complete':False,'P1_complete':False,'private_state_contents_parsed_copied_or_restored':False,'private_state_hashed_locally_for_preservation_only':True,'private_hashes_published':False,'game_operated':False,'chat_sent':False,'cloud_publication_binding':'enclosing_commit','cloud_published':False,'execution_environment':'local_original_windows_project_venv','local_source_parity_required_for_cloud_publication':True}
(ROOT/'verification/sections/350.json').write_bytes(enc(r));details=change+'\n\n'+validation+'\n\n'+limits+'\n\n用户最新要求：第350节完整收尾后暂停，不启动351；完成本节普通发布、远端核对及暂停断点后等待明确继续。\n\n'+pending
old_wip=subprocess.check_output(['git','show',parent+':WORK_IN_PROGRESS.md'],cwd=ROOT);(ROOT/'WORK_IN_PROGRESS.md').write_bytes(('## 第350节 + '+title+'\n\n'+now+'。'+details+'\n\n以下为历史记录；当前断点以上述350为准。\n\n').replace('\n','\r\n').encode()+old_wip)
doc('PROJECT_COMPLETED.md','## 第350节 + '+title+'\n\n'+now+'。'+details+'\n\n'+(ROOT/'PROJECT_COMPLETED.md').read_text('utf8'))
s=(ROOT/'AGENTS.md').read_text('utf8');end=s.index('\n## 项目级最高优先要求');note='下一到期完整检查须给304/305两份full320验证脚本显式传入--source-freeze及当轮根声明冻结文件；默认320仅供历史绑定。后续312补充窗口沿用脚本原有120秒默认上限，不再强制60秒；旧60秒失败仍保留且不宣称性能改进。350原失败、完整修复复验与本机范围见verification/full-350/summary.json。'
doc('AGENTS.md','## 当前续接 · 第350节 + '+title+'\n\n'+details+'\n\n完成350后暂停；351只是将来获准恢复后的编号，尚未启动，等待用户明确继续。行动奖励资料目录不替代实际菜单、服务器资格或真实领取。只跑本机必要检查；下一全量365，严格低于15%才开始当前完整小节收尾。\n\n'+note+'\n'+s[end:])
s=(ROOT/'PROJECT_REQUIREMENTS.md').read_text('utf8');start=s.index('<!-- current-delivery:start -->');end=s.index('<!-- current-delivery:end -->')+len('<!-- current-delivery:end -->');doc('PROJECT_REQUIREMENTS.md',s[:start]+'<!-- current-delivery:start -->\n## 第350节 + '+title+'\n\n'+details+'\n<!-- current-delivery:end -->'+s[end:])
s=(ROOT/'PROJECT_PROGRESS.md').read_text('utf8');old='行动奖励的实际出现与原入口';assert s.count(old)==1;s=s.replace(old,'行动奖励的实际菜单/出现资格、上次继承状态、实际结算及未证数值');doc('PROJECT_PROGRESS.md',s)
cp=read('DEVELOPMENT_CHECKPOINT.json');assert cp['completed_sections']==349 and cp['next_section']==350
for key in('current_section_validation','latest_section_environment','cloud_publication_closeout'):
 if key in cp:cp['historical_before350_'+key]=cp.pop(key)
cp.update(completed_sections=350,latest_functional_section=350,next_section=351,batch_status='P3_SECTION350_LOCAL_ACCEPTED_PUBLICATION_PENDING',next_action='第350节 + '+title+'已本机必要验收；完成本节普通推送、真实远端核对与暂停元数据后停止；351未启动，等待明确继续。恢复后下次全量365。',full_validation_due=False)
cp['sections'].append({'number':350,'completion_ref':'p3-section-350','topic':title,'verification':'verification/sections/350.json'});cp['functional_sections_since_latest_requirement'].append(350)
cp['current_section_save']={'section':350,'verification':'verification/sections/350.json','scope':'current_functional_section','binding':'enclosing_commit'};cp['last_verified_cloud_save']['scope']='previous_functional_section'
cp['current_section_validation']={'section':350,'receipt':'verification/sections/350.json','methods_run':n['methods_ran'],'native_isolated_window_checks':w['unique_checks'],'current_startup_choices':12,'regular_candidates':6,'independent_inherited_sources':6,'current_original_entries':19,'actual_menu_verified':False,'real_nonzero_refresh_states':2,'full_suite_rerun':True,'last_full_receipt':'verification/full-350/summary.json','last_full_receipt_is_historical_for_current_changes':False}
cp['latest_section_environment']={'section':350,'receipt':'verification/sections/350.json','native_windows':validation,'native_game_or_chat_verified':False,'current_section_full_rerun':True,'last_full_receipt':'verification/full-350/summary.json'}
cp['windows_native_validation']=validation;cp['current_batch'].update(status=cp['batch_status'],completed_sections=350,next_section=351,next_section_started=False,receipt='verification/sections/350.json',batch_closed=False)
cp['policy'].update(verification_execution_preference='local_project_environment',avoid_duplicate_cloud_tests=True,pause_after_active_section_requested=True,stop_after_section=350,development_paused_by_latest_user_request=True,new_functional_sections_paused=False,latest_user_instruction_receipt='verification/sections/350-pause-request.json',latest_pause_instruction_receipt='verification/sections/350-pause-request.json')
# Publication-complete pause flag is set only after actual current350 remote proof, as required by the unchanged index guard.
(ROOT/'verification/sections/350-pause-request.json').write_bytes(enc({'section':350,'request':'完成本节后暂停','source':'direct user request in current task','observed_at_Beijing':now,'finish_active_section_and_publication_before_pause':True,'start351_authorized':False}))
cp['current_data_versions'].update(current_startup_game_commit='bee3f83c5d60590b5e1cd42b8d09d00ce32ab10d',current_startup_choices=12,current_startup_regular_candidates=6,current_startup_inherited_sources=6,current_startup_original_entries=19,current_startup_actual_menu_verified=False)
for key in ('current_available_full_validation','last_full_validation'):
 cp['historical_before350_'+key]=cp.get(key)
cp['current_available_full_validation']={'section':350,'receipt':'verification/full-350/summary.json','available_scope_passed':True,'actual_validation_attempt':2,'single_available_scope_execution_all_green':full['single_available_scope_execution_all_green'],'actual_root_controller_exit':full['actual_root_controller_exit'],'validation_composition':full['validation_composition'],'source_freeze':full['source_freeze'],'source_freeze_sha256':full['source_freeze_sha256'],'native_windows_game_chat_verified':False}
cp['last_full_validation']={'after_section':350,'receipt':'verification/full-350/summary.json','available_checks_passed':True,'complete_repository_validation':False,'scope_not_reduced':True,'source_freeze':full['source_freeze'],'source_freeze_sha256':full['source_freeze_sha256']}
cp['next_full_validation_after']=365
for key in ('policy','current_batch_commit_policy','current_batch'):cp[key]['next_full_validation_after']=365
(ROOT/'DEVELOPMENT_CHECKPOINT.json').write_bytes(enc(cp))
doc('CLOUD_HANDOFF.md',(ROOT/'CLOUD_HANDOFF.md').read_text('utf8')+'\n<!-- section350-handoff:start -->\n## 第350节 + '+title+'\n\n'+details+'\n<!-- section350-handoff:end -->\n')
out=ROOT/'verification/sections/350-closeout';out.mkdir();shutil.copyfile(ROOT/'.cache/open_test_window_350.py',out/'execution-main-window.py')
runpy.run_path(str(ROOT/'scripts/update_cloud_index.py'))['update'](ROOT)
(out/'execution-closeout.py').write_bytes(Path(__file__).read_bytes());(out/'applied.json').write_bytes(enc({'section':350,'local_accepted':True,'ordinary_cloud_publication_verified':False,'next351_started':False,'at_Beijing':now}))
print(json.dumps({'section':350,'local_accepted':True,'ordinary_publication_pending':True},ensure_ascii=False))
