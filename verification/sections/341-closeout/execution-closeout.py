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
parent='fb1e0c2e68e145a7327383238e9d91a11bf24949';assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()==parent
assert subprocess.check_output(['git','branch','--show-current'],cwd=ROOT).decode().strip()=='codex/p2-development'
title='溯源六色雾气、加工品条件与准确原文入口'
change='新增溯源完整资料阅读：六色雾气分别显示对话，三处使用加工品后的结果与确认、两种离开对话及无加工品变体分别查阅。有加工品与无加工品按完整文献表分组，三条使用选项各消耗1件的文献说明分别保留，不相加；进入黑潭的确认不重复扣费，不按雾色虚构地图目的地。绿雾同时出现在两组离开标签，明确保留冲突，不替玩家认定实际变体；红雾特殊无法发动选项单列。保留76段原对话和114份完整原选项，其中95份有明确后续对话，19份仅为同文确认候选，不能据此认定游戏中属于该事件。190处版本条目各有准确原文入口；原对话不猜后续，原选项只跟随其明确下一对话。节点接入44条准确后续情景并保留未绑定旧入口，共33目录组、31事件标题、15类阅读器。本页加工品数量默认未知，仅用于资料条件对照；确认、终段及不适用分支不出现数量控件。实际父刷新保留两组非零阅读、选区、页签及本页条件；来源失效清旧，手动恢复，重复打开/换条目/父页和主窗关闭清理所属窗口。'
limits='复用321真实下载的BWIKI352356完整HTTP中的溯源整表，逐项核对固定bee3国服原件及baseline；保留完整文献、原文及19份同文确认候选的关联边界，不按编号猜服务器归属。完整表的合并单元格证明资料中有加工品/无加工品分组，不证明实际可选加工品池、消耗顺序或服务器完整资格；绿雾双标签未解决。实际雾色、候选归属、消耗/传送时点与目的地、行动力及当前本局状态未知；旧初始情景仍未绑定，25场景/57选项旧缺口未缩减。只局外资料查阅，不操作游戏、不发聊天或改私人状态、地图及计算，不给路线建议/排序/概率。P3/P2/P1未完成，识别最后。'
validation='本机最终39项相关检查通过，完整资料构建字节一致；原生Windows临时MainWindow共47项唯一检查通过，实际打开190处原文条目，核对六雾、绿雾冲突、红雾变体、加工品0/1边界、确认不重复付费、准确后续与无据不拼接、19候选警示、两组真实非零阅读/选区/页签和条件刷新保留、坏源清旧及手动恢复、目录兼容与主窗关闭整树。最终确认页直接查看，其余8张完整PNG与上次逐张查看的图片字节相同，复用视觉验收。七类真实外部操作计数零，临时本局与旧计算上下文不变；实际项目测试窗正常更新，可见响应未最小化，正常重启期间私人五路径一致，未确认置前台。549旧维护选择器原序保留，现551。原检查已通过后进一步区分95明确关联与19同文候选、修改玩家措辞，并按最终源码重跑；保留此前源码/回执。三个启动观察调用超时，但各原任务实际Popen及Qt均退出0，未因观察超时重复启动。只本机必要与原生检查，不云端重复；335全量属历史，下一全量350。索引实现未变，复用原25项单测，当前文档/要求/来源和索引实际校验。'
nname='verification/sections/341-necessary-attempt4/process.json';wname='verification/sections/341-native-attempt3/actual/window.json';pname='verification/sections/341-native-attempt3/process.json'
n,w,p=map(read,(nname,wname,pname));m=read('verification/sections/341-main-window-final.json');a=read('verification/sections/341-source-audit.json');v=read('verification/sections/341-root-visual.json')
assert n['passed']and n['methods_ran']==39 and w['passed']and w['qpa']=='windows'and w['qt_exit_code']==0 and w['unique_checks']==47 and w['verification_window_closed']
assert len(w['same_identity_refresh_observations'])==2 and len(w['screenshots'])==9 and len(w['actual_readings'])==190 and all(x==0 for x in w['external_operation_attempts'].values())
assert p['passed']and p['window_receipt_sha256']==sha(wname)
for result in(n,w):
 assert result['source_sha256_before']==result['source_sha256_after']
 for name,h in result['source_sha256_after'].items():assert sha(name)==h,name
assert v['passed']and len(v['final_screenshot_reviews'])==9 and a['ordered_previous549_preserved']and len(a['current_selectors'])==551
assert m['passed']and m['private_entire_normal_close_and_start_interval_unchanged']and m['window_visible_and_responsive']
now=datetime.now(timezone(timedelta(hours=8))).isoformat();pending='<!-- section341-publication-pending -->本地验收完成，普通推送及真实远端核对待完成。'
r={'section':341,'kind':'functional_section','title':title,'new_capability':change,'limitations':[limits],'at_Beijing':now,'branch':'codex/p2-development','necessary_validation':{**pin(nname),'methods_run':39,'actual_exit':0},'native_windows_validation':{**pin(wname),'process':pin(pname),'unique_checks':47,'actual_Qt_exit':0,'original_scenes':76,'original_choices_preserved':114,'explicit_destination_choices':95,'full_literal_teleport_candidates':19,'fog_tabs':6,'document_contexts':13,'document_choice_groups':10,'exact_original_version_entries':190,'catalogue_groups':33,'catalogue_titles':31,'reader_kinds':15,'real_nonzero_refresh_states':2,'actual_MainWindow_entry_and_close_exercised':True,'all_seven_real_external_operations_zero':True},'root_visual_review':pin('verification/sections/341-root-visual.json'),'source_audit':pin('verification/sections/341-source-audit.json'),'original_project_window':pin('verification/sections/341-main-window-final.json'),'source_sha256':n['source_sha256_after'],'validated_source_sha256':w['source_sha256_after'],'full_suite_rerun':False,'last_full_receipt':'verification/full-335/summary.json','last_full_receipt_is_historical_for_this_changed_source':True,'last_full_validation_sha256':sha('verification/full-335/summary.json'),'next_periodic_full_section':350,'P3_complete':False,'P2_complete':False,'P1_complete':False,'private_state_contents_parsed_copied_or_restored':False,'private_state_hashed_locally_for_preservation_only':True,'private_hashes_published':False,'game_operated':False,'chat_sent':False,'cloud_publication_binding':'enclosing_commit','cloud_published':False,'execution_environment':'local_original_windows_project_venv','local_source_parity_required_for_cloud_publication':True}
(ROOT/'verification/sections/341.json').write_bytes(enc(r));details=change+'\n\n'+validation+'\n\n'+limits+'\n\n'+pending
old_wip=subprocess.check_output(['git','show',parent+':WORK_IN_PROGRESS.md'],cwd=ROOT);(ROOT/'WORK_IN_PROGRESS.md').write_bytes(('## 第341节 + '+title+'\n\n'+now+'。'+details+'\n\n以下为历史记录；当前断点以上述341为准。\n\n').replace('\n','\r\n').encode()+old_wip)
doc('PROJECT_COMPLETED.md','## 第341节 + '+title+'\n\n'+now+'。'+details+'\n\n'+(ROOT/'PROJECT_COMPLETED.md').read_text('utf8'))
s=(ROOT/'AGENTS.md').read_text('utf8');end=s.index('\n## 项目级最高优先要求');note='下一到期完整检查须给304/305两份full320验证脚本显式传入--source-freeze及当轮根声明冻结文件；默认320仅供历史绑定。335原失败与绑定维护/复验见verification/full-335/summary.json。'
doc('AGENTS.md','## 当前续接 · 第341节 + '+title+'\n\n'+details+'\n\n继续P3；342从实际剩余节点/事件条件、掉落和固定地图缺口接续，未启动。文献条件与同文确认候选不替代服务器资格、实际消耗或传送。只跑本机必要检查；下一全量350，严格低于15%才开始当前完整小节收尾。\n\n'+note+'\n'+s[end:])
s=(ROOT/'PROJECT_REQUIREMENTS.md').read_text('utf8');start=s.index('<!-- current-delivery:start -->');end=s.index('<!-- current-delivery:end -->')+len('<!-- current-delivery:end -->');doc('PROJECT_REQUIREMENTS.md',s[:start]+'<!-- current-delivery:start -->\n## 第341节 + '+title+'\n\n'+details+'\n<!-- current-delivery:end -->'+s[end:])
s=(ROOT/'PROJECT_PROGRESS.md').read_text('utf8');assert s.count('其余未覆盖完整事件表及其奖励条件')==1;s=s.replace('其余未覆盖完整事件表及其奖励条件','溯源19份同文确认候选的实际归属、绿雾两组离开标签的实际选择、可消耗加工品完整池与消耗/传送时点、实际目的地及原入口服务器资格，其余未覆盖完整事件表及其奖励条件');doc('PROJECT_PROGRESS.md',s)
cp=read('DEVELOPMENT_CHECKPOINT.json');assert cp['completed_sections']==340 and cp['next_section']==341
for key in('current_section_validation','latest_section_environment','cloud_publication_closeout'):
 if key in cp:cp['historical_before341_'+key]=cp.pop(key)
cp.update(completed_sections=341,latest_functional_section=341,next_section=342,batch_status='P3_SECTION341_LOCAL_ACCEPTED_PUBLICATION_PENDING',next_action='第341节 + '+title+'已本机必要验收；普通推送核对后342接续P3实际剩余缺口，未启动。下次350。',full_validation_due=False)
cp['sections'].append({'number':341,'completion_ref':'p3-section-341','topic':title,'verification':'verification/sections/341.json'});cp['functional_sections_since_latest_requirement'].append(341)
cp['current_section_save']={'section':341,'verification':'verification/sections/341.json','scope':'current_functional_section','binding':'enclosing_commit'};cp['last_verified_cloud_save']['scope']='previous_functional_section'
cp['current_section_validation']={'section':341,'receipt':'verification/sections/341.json','methods_run':39,'native_isolated_window_checks':47,'original_scenes':76,'original_choices_preserved':114,'explicit_destination_choices':95,'full_literal_teleport_candidates':19,'fog_tabs':6,'document_contexts':13,'document_choice_groups':10,'exact_original_version_entries':190,'catalogue_groups':33,'catalogue_titles':31,'reader_kinds':15,'real_nonzero_refresh_states':2,'full_suite_rerun':False,'last_full_receipt':'verification/full-335/summary.json','last_full_receipt_is_historical_for_current_changes':True}
cp['latest_section_environment']={'section':341,'receipt':'verification/sections/341.json','native_windows':validation,'native_game_or_chat_verified':False,'current_section_full_rerun':False,'last_full_receipt':'verification/full-335/summary.json'}
cp['windows_native_validation']=validation;cp['current_batch'].update(status=cp['batch_status'],completed_sections=341,next_section=342,next_section_started=False,receipt='verification/sections/341.json',batch_closed=False)
cp['policy'].update(verification_execution_preference='local_project_environment',avoid_duplicate_cloud_tests=True)
cp['current_data_versions'].update(current_portal_game_commit='bee3f83c5d60590b5e1cd42b8d09d00ce32ab10d',current_portal_original_scenes=76,current_portal_original_choices_preserved=114,current_portal_explicit_destination_choices=95,current_portal_full_literal_confirmation_candidates=19,current_portal_original_entry_views=190,current_node_reader_groups=33,current_node_reader_titles=31,current_node_reader_kinds=15,current_portal_actual_server_parent_or_teleport_verified=False)
(ROOT/'DEVELOPMENT_CHECKPOINT.json').write_bytes(enc(cp))
doc('CLOUD_HANDOFF.md',(ROOT/'CLOUD_HANDOFF.md').read_text('utf8')+'\n<!-- section341-handoff:start -->\n## 第341节 + '+title+'\n\n'+details+'\n<!-- section341-handoff:end -->\n')
out=ROOT/'verification/sections/341-closeout';out.mkdir();shutil.copyfile(ROOT/'.cache/open_test_window_341_final.py',out/'execution-main-window.py')
runpy.run_path(str(ROOT/'scripts/update_cloud_index.py'))['update'](ROOT)
(out/'execution-closeout.py').write_bytes(Path(__file__).read_bytes());(out/'applied.json').write_bytes(enc({'section':341,'local_accepted':True,'ordinary_cloud_publication_verified':False,'next342_started':False,'at_Beijing':now}))
print(json.dumps({'section':341,'local_accepted':True,'ordinary_publication_pending':True},ensure_ascii=False))
