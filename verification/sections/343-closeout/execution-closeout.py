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
parent='df8ae2b00751a64907d4b4ee506ac5be6df1174f';assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()==parent
assert subprocess.check_output(['git','branch','--show-current'],cwd=ROOT).decode().strip()=='codex/p2-development'
title='和平守卫者完整流程、移动例外与悬赏生效时点'
change='新增固定bee3国服和平守卫者完整事件阅读：3段对话、4份完整原选项及7处准确版本入口。接取悬赏与离开分别阅读，接取后仅有立即前往及仅标记两种分支；按完整文献明确父关系，不把标记当移动、作战或胜利。旧291已核对的本层已完成则不移动例外纳入当前流程，保持单向语义，未完成不保证移动；只有立即前往分支显示默认未知的仅本页完成情况对照，接取/离开/标记与终段完全隐藏。对照不改变本局完成状态或实际目的地，原件未给下一对话/战斗地图就不造跳转。接取及接取后情景显示当前厄运火杆的准确图片与完整效果；区分与居民作战的敌人减生命和胜利后永久10攻速，持有/接取/移动/标记不记胜利，+10不作+10%。离开清除图片与移动控件，坏图回退文字但保留资料，整源坏清旧并手选恢复。刷新保留两组真实非零阅读/选区、页签、选项和本页对照；重复打开/父页失效及主窗关闭清理所属窗口。节点新增完整当前入口与3条准确情景对照，共35目录组、33标题、17类阅读器。'
limits='复用321实际下载的BWIKI352356完整和平守卫者表、291已归档PRTS两版完整事件文献及原件、固定bee3与baseline完整记录；再次读取当前BWIKI与PRTS厄运火杆说明。旧291单向例外与原服务器/来源边界不变，不重新登记成新机制发现。本节新增当前完整流程与精确入口，不称已恢复服务器移动脚本。仅原件明确收藏品指针和准确图片，不按名称猜节点或地图。完整出现资格、本层实际完成、最近目标判定/真实目的地、实际移动/标记/作战和胜利次数、领取/持有/累计层数未知；未完成不反推移动成功。战斗触发仅作资料，未新增数值模型或改旧计算；不操作游戏、不发聊天、不改本局及私人设置，不给路线建议/排序/概率。P3/P2/P1未完成，识别最后。'
validation='最终本机36项相关检查与Windows原生临时MainWindow45项唯一检查通过，完整资料构建字节一致。7处准确版本入口、接取/离开及前往/标记分支、三种完成对照保持单向逻辑且不写实际状态、不虚构地图/后续、胜利时点及非百分比攻速、控件只出现在对应分支、准确藏品图片与坏图文字回退、两组非零阅读/选区和条件/页签经真实父刷新保留、来源损坏清旧/手选恢复、节点版本提示、重复打开/父页失效及实际主窗同时关闭两入口子窗均通过。7张最终实际PNG主代理逐张查看。七类真实外部操作计数零，临时本局及旧计算上下文不变；原项目测试窗正常更新，可见响应且未最小化，正常重启全过程私人五路径不变，未确认置前台。首轮36与45已通过；视觉复查后将开发过程用语改为玩家核对提示，按最终源码重跑，保留初始源码/回执，不伪称旧测试失败。553旧维护选择器原序保留，现555。只跑本机必要及原生检查，云端不重复；335全量属历史，下次350。索引实现未变，复用既有25项单测，当前要求/断点/来源和索引实际校验。'
nname='verification/sections/343-necessary-attempt2/process.json';wname='verification/sections/343-native-attempt2/actual/window.json';pname='verification/sections/343-native-attempt2/process.json'
n,w,p=map(read,(nname,wname,pname));m=read('verification/sections/343-main-window.json');a=read('verification/sections/343-source-audit.json');v=read('verification/sections/343-root-visual.json')
assert n['passed']and n['methods_ran']==36 and w['passed']and w['qpa']=='windows'and w['qt_exit_code']==0 and w['unique_checks']==45 and w['verification_window_closed']
assert len(w['same_identity_refresh_observations'])==2 and len(w['screenshots'])==7 and len(w['actual_readings'])==7 and all(x==0 for x in w['external_operation_attempts'].values())
assert p['passed']and p['window_receipt_sha256']==sha(wname)
for result in(n,w):
 assert result['source_sha256_before']==result['source_sha256_after']
 for name,h in result['source_sha256_after'].items():assert sha(name)==h,name
assert v['passed']and len(v['final_screenshot_reviews'])==7 and a['ordered_previous553_preserved']and len(a['current_selectors'])==555
assert m['passed']and m['private_entire_normal_close_and_start_interval_unchanged']and m['window_visible_and_responsive']
now=datetime.now(timezone(timedelta(hours=8))).isoformat();pending='<!-- section343-publication-pending -->本地验收完成，普通推送及真实远端核对待完成。'
r={'section':343,'kind':'functional_section','title':title,'new_capability':change,'limitations':[limits],'at_Beijing':now,'branch':'codex/p2-development','necessary_validation':{**pin(nname),'methods_run':36,'actual_exit':0},'native_windows_validation':{**pin(wname),'process':pin(pname),'unique_checks':45,'actual_Qt_exit':0,'original_scenes':3,'original_choices':4,'current_named_item':1,'exact_original_version_entries':7,'catalogue_groups':35,'catalogue_titles':33,'reader_kinds':17,'real_nonzero_refresh_states':2,'actual_MainWindow_entry_and_close_exercised':True,'all_seven_real_external_operations_zero':True},'root_visual_review':pin('verification/sections/343-root-visual.json'),'source_audit':pin('verification/sections/343-source-audit.json'),'original_project_window':pin('verification/sections/343-main-window.json'),'source_sha256':n['source_sha256_after'],'validated_source_sha256':w['source_sha256_after'],'full_suite_rerun':False,'last_full_receipt':'verification/full-335/summary.json','last_full_receipt_is_historical_for_this_changed_source':True,'last_full_validation_sha256':sha('verification/full-335/summary.json'),'next_periodic_full_section':350,'P3_complete':False,'P2_complete':False,'P1_complete':False,'private_state_contents_parsed_copied_or_restored':False,'private_state_hashed_locally_for_preservation_only':True,'private_hashes_published':False,'game_operated':False,'chat_sent':False,'cloud_publication_binding':'enclosing_commit','cloud_published':False,'execution_environment':'local_original_windows_project_venv','local_source_parity_required_for_cloud_publication':True}
(ROOT/'verification/sections/343.json').write_bytes(enc(r));details=change+'\n\n'+validation+'\n\n'+limits+'\n\n'+pending
old_wip=subprocess.check_output(['git','show',parent+':WORK_IN_PROGRESS.md'],cwd=ROOT);(ROOT/'WORK_IN_PROGRESS.md').write_bytes(('## 第343节 + '+title+'\n\n'+now+'。'+details+'\n\n以下为历史记录；当前断点以上述343为准。\n\n').replace('\n','\r\n').encode()+old_wip)
doc('PROJECT_COMPLETED.md','## 第343节 + '+title+'\n\n'+now+'。'+details+'\n\n'+(ROOT/'PROJECT_COMPLETED.md').read_text('utf8'))
s=(ROOT/'AGENTS.md').read_text('utf8');end=s.index('\n## 项目级最高优先要求');note='下一到期完整检查须给304/305两份full320验证脚本显式传入--source-freeze及当轮根声明冻结文件；默认320仅供历史绑定。335原失败与绑定维护/复验见verification/full-335/summary.json。'
doc('AGENTS.md','## 当前续接 · 第343节 + '+title+'\n\n'+details+'\n\n继续P3；344从实际剩余节点/事件条件、掉落和固定地图缺口接续，未启动。完整事件与单向移动例外不替代实际完成、目的地、移动或胜利核对。只跑本机必要检查；下一全量350，严格低于15%才开始当前完整小节收尾。\n\n'+note+'\n'+s[end:])
s=(ROOT/'PROJECT_REQUIREMENTS.md').read_text('utf8');start=s.index('<!-- current-delivery:start -->');end=s.index('<!-- current-delivery:end -->')+len('<!-- current-delivery:end -->');doc('PROJECT_REQUIREMENTS.md',s[:start]+'<!-- current-delivery:start -->\n## 第343节 + '+title+'\n\n'+details+'\n<!-- current-delivery:end -->'+s[end:])
s=(ROOT/'PROJECT_PROGRESS.md').read_text('utf8');old='和平守卫者本层实际完成、真实目的地、实际移动/作战与当前服务器适用性';assert s.count(old)==1;s=s.replace(old,'和平守卫者本层实际完成、最近目标判定与真实目的地、实际移动/标记/作战及胜利次数、领取状态与当前服务器完整资格');doc('PROJECT_PROGRESS.md',s)
cp=read('DEVELOPMENT_CHECKPOINT.json');assert cp['completed_sections']==342 and cp['next_section']==343
for key in('current_section_validation','latest_section_environment','cloud_publication_closeout'):
 if key in cp:cp['historical_before343_'+key]=cp.pop(key)
cp.update(completed_sections=343,latest_functional_section=343,next_section=344,batch_status='P3_SECTION343_LOCAL_ACCEPTED_PUBLICATION_PENDING',next_action='第343节 + '+title+'已本机必要验收；普通推送核对后344接续P3实际剩余缺口，未启动。下次350。',full_validation_due=False)
cp['sections'].append({'number':343,'completion_ref':'p3-section-343','topic':title,'verification':'verification/sections/343.json'});cp['functional_sections_since_latest_requirement'].append(343)
cp['current_section_save']={'section':343,'verification':'verification/sections/343.json','scope':'current_functional_section','binding':'enclosing_commit'};cp['last_verified_cloud_save']['scope']='previous_functional_section'
cp['current_section_validation']={'section':343,'receipt':'verification/sections/343.json','methods_run':36,'native_isolated_window_checks':45,'original_scenes':3,'original_choices':4,'current_named_item':1,'exact_original_version_entries':7,'catalogue_groups':35,'catalogue_titles':33,'reader_kinds':17,'real_nonzero_refresh_states':2,'full_suite_rerun':False,'last_full_receipt':'verification/full-335/summary.json','last_full_receipt_is_historical_for_current_changes':True}
cp['latest_section_environment']={'section':343,'receipt':'verification/sections/343.json','native_windows':validation,'native_game_or_chat_verified':False,'current_section_full_rerun':False,'last_full_receipt':'verification/full-335/summary.json'}
cp['windows_native_validation']=validation;cp['current_batch'].update(status=cp['batch_status'],completed_sections=343,next_section=344,next_section_started=False,receipt='verification/sections/343.json',batch_closed=False)
cp['policy'].update(verification_execution_preference='local_project_environment',avoid_duplicate_cloud_tests=True)
cp['current_data_versions'].update(current_peace_game_commit='bee3f83c5d60590b5e1cd42b8d09d00ce32ab10d',current_peace_original_scenes=3,current_peace_original_choices=4,current_peace_original_entry_views=7,current_peace_named_item=1,current_node_reader_groups=35,current_node_reader_titles=33,current_node_reader_kinds=17,current_peace_actual_target_movement_or_server_verified=False)
(ROOT/'DEVELOPMENT_CHECKPOINT.json').write_bytes(enc(cp))
doc('CLOUD_HANDOFF.md',(ROOT/'CLOUD_HANDOFF.md').read_text('utf8')+'\n<!-- section343-handoff:start -->\n## 第343节 + '+title+'\n\n'+details+'\n<!-- section343-handoff:end -->\n')
out=ROOT/'verification/sections/343-closeout';out.mkdir();shutil.copyfile(ROOT/'.cache/open_test_window_343.py',out/'execution-main-window.py')
runpy.run_path(str(ROOT/'scripts/update_cloud_index.py'))['update'](ROOT)
(out/'execution-closeout.py').write_bytes(Path(__file__).read_bytes());(out/'applied.json').write_bytes(enc({'section':343,'local_accepted':True,'ordinary_cloud_publication_verified':False,'next344_started':False,'at_Beijing':now}))
print(json.dumps({'section':343,'local_accepted':True,'ordinary_publication_pending':True},ensure_ascii=False))
