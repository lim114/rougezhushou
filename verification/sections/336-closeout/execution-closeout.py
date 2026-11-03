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
parent='6a70f55e14967be00210d59517587c575efdf9be';assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()==parent
assert subprocess.check_output(['git','branch','--show-current'],cwd=ROOT).decode().strip()=='codex/p2-development'
title='愈创之心的五种选项、独立条件与追忆区域说明'
change='新增愈创之心完整事件阅读，保留6段对话、5个独立选项、11份精确国服原始入口和4份物品原件。三种取得追忆的分支分别对照3行动力、随机2件加工品和消耗源私钥，不合并代价、不重复领取、不猜独立件数；源私钥的原物品99源石锭说明不变成消费后的新奖励。持有笼控器获得5行动力与闭眼休息获得1行动力分开显示，持有条件不改成消耗，零件总数不当加工品数量，也不能指定随机损失成员。只在本事件显示行动力、加工品数量、源私钥和笼控器四类对照，默认未知，不自动代入本局；已知不足只阻断对应分支后续，所有文献对话仍可直接查阅。追忆资料说明第四层取得、随后进入另一张第四层地图、失效及进入误入奇境不触发；不推断整事件其它选项也只在第四层出现、不执行移动或伪造目的地。原调查中标记保留，不将完整表冒充完整服务器资格。节点目录新增1个准入、6个ID和完整正文对应（3份完全一致、3份仅明确省略号写法转换，双方全文保留），合计30目录组/28事件/12类阅读器。父页刷新保持两组真实非零阅读、情景选择和本页条件；坏源清旧、手动恢复、重复开窗以及父页/主窗关闭清理所属阅读窗口。'
limits='复用321真实下载的BWIKI352356原HTTP；选取完整标题段落，保留调查中标记和随后完整5选项表，记录原字符范围、字节与摘要。本轮独立复读BWIKI和PRTS追忆、源私钥与引擎配件说明，不冒称重新下载HTML或当前服务器实机核验。6原情景、5原选项与4物品完整记录逐项比较固定bee3/a550；只允许旧目录……与原件六个英文句点的明确转换，不能靠同名、近似匹配或ID猜剧情。当前所有选项是否同时展示、完整资格、随机加工品成员/抽取顺序/实际库存、源私钥消耗件数、追忆实际领取件数、行动力上限及完整当前服务器区域触发脚本仍未知。固定资料中的进入新第四层不是还原已走地图；误入奇境不触发也不推出所有特殊区域的其它规则。四类值只是本页条件对照，不写回本局、数值、库存或地图，不操作游戏或发送聊天，不给路线建议、排序或概率。P3/P2/P1未完成，识别最后。'
validation='本机36项相关必要测试全部通过，完整源码字节守卫前后相同；完整资料可重复构建字节一致。Windows原生临时MainWindow共42项唯一检查通过，实际遍历11个原始入口、5种独立结果、行动力2/3与加工品1/2边界、源私钥/笼控器缺少和持有边界，独立消耗/持有与1/5行动力收益、无二次99收入/无猜件数/无假区域移动，两个阅读区真实非零滚动和选区经父页刷新保留。源实际损坏清旧、恢复后手动重选、重复开窗及父源失效和实际主窗关闭清理子窗；节点入口默认四条件未知，新增源失效保留旧目录文字。7张实际PNG均由主代理直接查看，含外层版本提示。七类真实外部操作计数零，临时本局及旧计算上下文不变；原项目测试窗正常更新，可见响应且未最小化（本次未确认置前台），正常关闭到启动私人五路径一致。539旧选择器原序保留，现541。准备阶段首表只得到调查中、严格全文对应遇3份省略号差异及选择器声明结构断言，均在正式验收前按实际原件处理，未冒称测试失败或通过。只跑本机必要与原生验证，不重复全量；335完整可用验收及原失败/两份验证脚本绑定维护后的复验仍为历史，下次350。索引实现未变，25单测按原证据复用，当前要求/断点/索引仍实际校验。'
nname='verification/sections/336-necessary-attempt1/process.json';wname='verification/sections/336-native-attempt1/actual/window.json';pname='verification/sections/336-native-attempt1/process.json'
n,w,p=map(read,(nname,wname,pname));m=read('verification/sections/336-main-window.json');a=read('verification/sections/336-source-audit.json');v=read('verification/sections/336-root-visual.json')
assert n['passed']and n['methods_ran']==36 and w['passed']and w['qpa']=='windows'and w['qt_exit_code']==0 and w['unique_checks']==42 and w['verification_window_closed']
assert len(w['same_identity_refresh_observations'])==2 and len(w['screenshots'])==7 and len(w['actual_readings'])==5 and all(x==0 for x in w['external_operation_attempts'].values())
assert p['passed']and p['window_receipt_sha256']==sha(wname)
for result in(n,w):
 assert result['source_sha256_before']==result['source_sha256_after']
 for name,h in result['source_sha256_after'].items():assert sha(name)==h,name
assert v['passed']and len(v['final_screenshot_reviews'])==7 and a['ordered_previous539_preserved']and len(a['current_selectors'])==541
assert m['passed']and m['private_entire_normal_close_and_start_interval_unchanged']and m['window_visible_and_responsive']
now=datetime.now(timezone(timedelta(hours=8))).isoformat();pending='<!-- section336-publication-pending -->本地验收完成，普通推送及真实远端核对待完成。'
r={'section':336,'kind':'functional_section','title':title,'new_capability':change,'limitations':[limits],'at_Beijing':now,'branch':'codex/p2-development','necessary_validation':{**pin(nname),'methods_run':36,'actual_exit':0},'native_windows_validation':{**pin(wname),'process':pin(pname),'unique_checks':42,'actual_Qt_exit':0,'documented_events':1,'document_scenes':6,'document_choices':5,'original_source_entries':11,'new_catalogue_groups':1,'scene_identity_links':6,'exact_full_text_links':3,'explicit_document_ellipsis_links':3,'real_nonzero_refresh_states':2,'actual_MainWindow_entry_and_close_exercised':True,'all_seven_real_external_operations_zero':True},'root_visual_review':pin('verification/sections/336-root-visual.json'),'source_audit':pin('verification/sections/336-source-audit.json'),'original_project_window':pin('verification/sections/336-main-window.json'),'source_sha256':n['source_sha256_after'],'validated_source_sha256':w['source_sha256_after'],'full_suite_rerun':False,'last_full_receipt':'verification/full-335/summary.json','last_full_receipt_is_historical_for_this_changed_source':True,'last_full_validation_sha256':sha('verification/full-335/summary.json'),'next_periodic_full_section':350,'P3_complete':False,'P2_complete':False,'P1_complete':False,'private_state_contents_parsed_copied_or_restored':False,'private_state_hashed_locally_for_preservation_only':True,'private_hashes_published':False,'game_operated':False,'chat_sent':False,'cloud_publication_binding':'enclosing_commit','cloud_published':False,'execution_environment':'local_original_windows_project_venv','local_source_parity_required_for_cloud_publication':True}
(ROOT/'verification/sections/336.json').write_bytes(enc(r));details=change+'\n\n'+validation+'\n\n'+limits+'\n\n'+pending
old_wip=subprocess.check_output(['git','show',parent+':WORK_IN_PROGRESS.md'],cwd=ROOT);(ROOT/'WORK_IN_PROGRESS.md').write_bytes(('## 第336节 + '+title+'\n\n'+now+'。'+details+'\n\n以下为历史记录；当前断点以上述336为准。\n\n').replace('\n','\r\n').encode()+old_wip)
doc('PROJECT_COMPLETED.md','## 第336节 + '+title+'\n\n'+now+'。'+details+'\n\n'+(ROOT/'PROJECT_COMPLETED.md').read_text('utf8'))
s=(ROOT/'AGENTS.md').read_text('utf8');end=s.index('\n## 项目级最高优先要求');note='下一到期完整检查须给304/305两份full320验证脚本显式传入--source-freeze及当轮根声明冻结文件；默认320仅供历史绑定。335原失败与绑定维护/复验见verification/full-335/summary.json。'
doc('AGENTS.md','## 当前续接 · 第336节 + '+title+'\n\n'+details+'\n\n继续P3；337从实际未完成节点事件条件、奖励与固定地图缺口接续，未启动。本节只跑本机必要检查；下一全量350，严格低于15%才开始当前完整小节收尾。\n\n'+note+'\n'+s[end:])
s=(ROOT/'PROJECT_REQUIREMENTS.md').read_text('utf8');start=s.index('<!-- current-delivery:start -->');end=s.index('<!-- current-delivery:end -->')+len('<!-- current-delivery:end -->');doc('PROJECT_REQUIREMENTS.md',s[:start]+'<!-- current-delivery:start -->\n## 第336节 + '+title+'\n\n'+details+'\n<!-- current-delivery:end -->'+s[end:])
s=(ROOT/'PROJECT_PROGRESS.md').read_text('utf8');old='其余未覆盖完整事件表及其奖励条件';new='愈创之心完整资格、随机加工品实际消耗成员/顺序、源私钥消耗与追忆领取件数及当前本局/服务器区域触发，其余未覆盖完整事件表及其奖励条件';assert s.count(old)==1;doc('PROJECT_PROGRESS.md',s.replace(old,new,1))
cp=read('DEVELOPMENT_CHECKPOINT.json');assert cp['completed_sections']==335 and cp['next_section']==336
for key in('current_section_validation','latest_section_environment','cloud_publication_closeout'):
 if key in cp:cp['historical_before336_'+key]=cp.pop(key)
cp.update(completed_sections=336,latest_functional_section=336,next_section=337,batch_status='P3_SECTION336_LOCAL_ACCEPTED_PUBLICATION_PENDING',next_action='第336节 + '+title+'已本机必要验收；普通推送核对后337接续P3实际剩余缺口，未启动。下次350。',full_validation_due=False)
cp['sections'].append({'number':336,'completion_ref':'p3-section-336','topic':title,'verification':'verification/sections/336.json'});cp['functional_sections_since_latest_requirement'].append(336)
cp['current_section_save']={'section':336,'verification':'verification/sections/336.json','scope':'current_functional_section','binding':'enclosing_commit'};cp['last_verified_cloud_save']['scope']='previous_functional_section'
cp['current_section_validation']={'section':336,'receipt':'verification/sections/336.json','methods_run':36,'native_isolated_window_checks':42,'documented_events':1,'document_scenes':6,'document_choices':5,'original_source_entries':11,'new_catalogue_groups':1,'scene_identity_links':6,'exact_full_text_links':3,'explicit_document_ellipsis_links':3,'real_nonzero_refresh_states':2,'full_suite_rerun':False,'last_full_receipt':'verification/full-335/summary.json','last_full_receipt_is_historical_for_current_changes':True}
cp['latest_section_environment']={'section':336,'receipt':'verification/sections/336.json','native_windows':validation,'native_game_or_chat_verified':False,'current_section_full_rerun':False,'last_full_receipt':'verification/full-335/summary.json'}
cp['windows_native_validation']=validation;cp['current_batch'].update(status=cp['batch_status'],completed_sections=336,next_section=337,next_section_started=False,receipt='verification/sections/336.json',batch_closed=False)
cp['policy'].update(current_usage_remaining_percent=95,current_usage_receipt='verification/sections/336-preparation/usage-final.json',verification_execution_preference='local_project_environment',avoid_duplicate_cloud_tests=True)
cp['current_data_versions'].update(current_memory_tree_game_commit='bee3f83c5d60590b5e1cd42b8d09d00ce32ab10d',current_memory_tree_document_revision=352356,current_memory_tree_events=1,current_memory_tree_scenes=6,current_memory_tree_choices=5,current_memory_tree_items=4,current_memory_tree_declared_resource_controls=4,current_node_reader_aggregate_catalogue_groups=30,current_node_reader_aggregate_event_titles=28,current_node_reader_aggregate_types=12,current_node_actual_version_or_phase_verified=False)
(ROOT/'DEVELOPMENT_CHECKPOINT.json').write_bytes(enc(cp))
doc('CLOUD_HANDOFF.md',(ROOT/'CLOUD_HANDOFF.md').read_text('utf8')+'\n<!-- section336-handoff:start -->\n## 第336节 + '+title+'\n\n'+details+'\n<!-- section336-handoff:end -->\n')
out=ROOT/'verification/sections/336-preparation';shutil.copyfile(ROOT/'.cache/open_test_window_336.py',out/'execution-main-window.py')
runpy.run_path(str(ROOT/'scripts/update_cloud_index.py'))['update'](ROOT)
out=ROOT/'verification/sections/336-closeout';out.mkdir();(out/'execution-closeout.py').write_bytes(Path(__file__).read_bytes());(out/'applied.json').write_bytes(enc({'section':336,'local_accepted':True,'ordinary_cloud_publication_verified':False,'next337_started':False,'at_Beijing':now}))
print(json.dumps({'section':336,'local_accepted':True,'ordinary_publication_pending':True},ensure_ascii=False))
