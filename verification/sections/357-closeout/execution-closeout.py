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
parent='9e0de06c761033123daa9dcb018c2a24b83d1608';assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()==parent
assert subprocess.check_output(['git','branch','--show-current'],cwd=ROOT).decode().strip()=='codex/p2-development'
title='实托邦理念与方针的完整条件、组合限制和原文入口'
change='通用节点事件页加入实托邦理念与方针目录，分别查看10种理念的30份早中晚期原项及4方针，可按名称/类型筛选，并仅展示对应条目所需的主层、配对或分队条件。进入与途经可以独立或同时声明，不互相推定已结算；希望沃土与增益互限，文明开化免疫例外、储藏室社区补文及节点自身揭示例外分别保留。准确打开两条红苔原文与安眠原场景，从原场景/选项反向只筛相关理念、不自动选档。父刷新保留阅读和本页条件，源失效清旧内容，所属事件随换项/关闭清理。'
limits='固定bee3国服资料与实际下载PRTS442947/442954全文核对；旧希望沃土三档不重计新机制，新覆盖为其余27理念原项、4方针及完整当前条件关联。自然生成的2/6/12门槛不证明事件强制来源、其它模式或当前节点已存在/生效；其它组合、实际生成/覆盖/阶段/结算和奖励完整数量仍未知。原追忆与希望沃土当前来源关系未证，不推已生成。猎犬proto已用两份受跟踪公开原件核对为正式名字，不改成其它猎犬。没有将理念/方针写入本局或数值计算，不操作游戏/发聊天/给路线建议或概率；P3/P2/P1未完成，识别最后。'
validation='最终本机31项必要测试、42项原生窗口唯一检查通过：34原项、三阶段边界、组合限制、文明开化例外、两种行为不互斥、专属控件、原说明与社区补文、准确三原文及反向入口、两组非零阅读/条件/搜索/页签经父刷新保持、坏源清除手选恢复、所属树关闭。七类真实外部操作均零，临时本局与旧计算不变。首轮31/42通过后仅清理玩家正文中的开发进度与源码缩写，保留改前文本并在最终相同来源重验31/42；没有改机制。最终六张图由独立子代理逐张实际查看并按真实审阅者保存，主代理此前查看首轮六图，不冒称最终直接看图。原项目测试窗更新可见响应、完整关闭/启动区间私人五路径保持。580旧选择器原序保留，新加2个共582；350全量仅改前历史，下一定期365。未变索引25旧单测复用并实际验证要求/索引；不可用私样本/1314/实机游戏聊天未冒称通过。按授权继续至370后暂停。'
nname='verification/sections/357-necessary-attempt2/process.json';wname='verification/sections/357-native-attempt2/actual/window.json';pname='verification/sections/357-native-attempt2/process.json'
n,w,p=map(read,(nname,wname,pname));m=read('verification/sections/357-main-window.json');a=read('verification/sections/357-source-audit.json');v=read('verification/sections/357-root-visual.json')
assert n['passed']and n['methods_ran']==31 and w['passed']and w['qpa']=='windows'and w['qt_exit_code']==0 and w['unique_checks']==42 and w['verification_window_closed']
assert len(w['same_identity_refresh_observations'])==2 and len(w['screenshots'])==6 and len(w['actual_readings'])==6 and all(x==0 for x in w['external_operation_attempts'].values())
assert p['passed']and p['window_receipt_sha256']==sha(wname)
for result in(n,w):
 assert result['source_sha256_before']==result['source_sha256_after']
 for name,h in result['source_sha256_after'].items():assert sha(name)==h,name
assert v['passed']and len(v['final_screenshot_reviews'])==6 and a['ordered_previous580_preserved']and len(a['current_selectors'])==582
assert m['passed']and m['private_entire_normal_close_and_start_interval_unchanged']and m['window_visible_and_responsive']
now=datetime.now(timezone(timedelta(hours=8))).isoformat();pending='<!-- section357-publication-pending -->本地验收完成，普通推送及真实远端核对待完成。'
r={'section':357,'kind':'functional_section','title':title,'new_capability':change,'limitations':[limits],'at_Beijing':now,'branch':'codex/p2-development','necessary_validation':{**pin(nname),'methods_run':n['methods_ran'],'actual_exit':0},'native_windows_validation':{**pin(wname),'process':pin(pname),'unique_checks':w['unique_checks'],'actual_Qt_exit':0,'current_idea_records':30,'current_policy_records':4,'exact_related_originals':3,'real_nonzero_refresh_states':2,'actual_MainWindow_entry_and_close_exercised':True,'all_seven_real_external_operations_zero':True},'root_visual_review':pin('verification/sections/357-root-visual.json'),'source_audit':pin('verification/sections/357-source-audit.json'),'original_project_window':pin('verification/sections/357-main-window.json'),'source_sha256':n['source_sha256_after'],'validated_source_sha256':w['source_sha256_after'],'full_suite_rerun':False,'last_full_receipt':'verification/full-350/summary.json','last_full_receipt_is_historical_for_this_changed_source':True,'last_full_validation_sha256':sha('verification/full-350/summary.json'),'next_periodic_full_section':365,'P3_complete':False,'P2_complete':False,'P1_complete':False,'private_state_contents_parsed_copied_or_restored':False,'private_state_hashed_locally_for_preservation_only':True,'private_hashes_published':False,'game_operated':False,'chat_sent':False,'cloud_publication_binding':'enclosing_commit','cloud_published':False,'execution_environment':'local_original_windows_project_venv','local_source_parity_required_for_cloud_publication':True}
(ROOT/'verification/sections/357.json').write_bytes(enc(r));details=change+'\n\n'+validation+'\n\n'+limits+'\n\n'+pending
old_wip=(ROOT/'WORK_IN_PROGRESS.md').read_bytes();(ROOT/'WORK_IN_PROGRESS.md').write_bytes(('## 第357节 + '+title+'\n\n'+now+'。'+details+'\n\n以下为历史记录；当前断点以上述357为准。\n\n').replace('\n','\r\n').encode()+old_wip)
doc('PROJECT_COMPLETED.md','## 第357节 + '+title+'\n\n'+now+'。'+details+'\n\n'+(ROOT/'PROJECT_COMPLETED.md').read_text('utf8'))
s=(ROOT/'AGENTS.md').read_text('utf8');end=s.index('\n## 项目级最高优先要求');note='下一到期完整检查须给304/305两份full320验证脚本显式传入--source-freeze及当轮根声明冻结文件；默认320仅供历史绑定。350原失败与组合复验见verification/full-350/summary.json。312补充窗口采用既有120秒默认，304/305显式传入当轮source-freeze。'
doc('AGENTS.md','## 当前续接 · 第357节 + '+title+'\n\n'+details+'\n\n继续P3；358从实际剩余节点/事件条件、掉落和固定地图缺口接续，未启动。实托邦条件对照不替代本局生成、生效或结算。通用页面不恢复独立版本栏目。用户当前授权继续至370，完整收尾后暂停。只跑本机必要检查；下一全量365，严格低于15%才开始当前完整小节收尾。\n\n'+note+'\n'+s[end:])
s=(ROOT/'PROJECT_REQUIREMENTS.md').read_text('utf8');start=s.index('<!-- current-delivery:start -->');end=s.index('<!-- current-delivery:end -->')+len('<!-- current-delivery:end -->');doc('PROJECT_REQUIREMENTS.md',s[:start]+'<!-- current-delivery:start -->\n## 第357节 + '+title+'\n\n'+details+'\n<!-- current-delivery:end -->'+s[end:])
s=(ROOT/'PROJECT_PROGRESS.md').read_text('utf8');old='同步完成标志、住民/迷雾、行动力与加工品的节点状态规则';assert s.count(old)==1;s=s.replace(old,'实托邦理念/方针的实际生成、覆盖、阶段组合、当前资格及真实结算；同步完成标志、住民/迷雾、行动力与加工品的实际节点状态规则');doc('PROJECT_PROGRESS.md',s)
cp=read('DEVELOPMENT_CHECKPOINT.json');assert cp['completed_sections']==356 and cp['next_section']==357
for key in('current_section_validation','latest_section_environment','cloud_publication_closeout'):
 if key in cp:cp['historical_before357_'+key]=cp.pop(key)
cp.update(completed_sections=357,latest_functional_section=357,next_section=358,batch_status='P3_SECTION357_LOCAL_ACCEPTED_PUBLICATION_PENDING',next_action='第357节 + '+title+'已本机必要验收；普通推送核对后358接续P3实际剩余缺口，未启动。下次365。',full_validation_due=False)
cp['sections'].append({'number':357,'completion_ref':'p3-section-357','topic':title,'verification':'verification/sections/357.json'});cp['functional_sections_since_latest_requirement'].append(357)
cp['current_section_save']={'section':357,'verification':'verification/sections/357.json','scope':'current_functional_section','binding':'enclosing_commit'};cp['last_verified_cloud_save']['scope']='previous_functional_section'
cp['current_section_validation']={'section':357,'receipt':'verification/sections/357.json','methods_run':n['methods_ran'],'native_isolated_window_checks':w['unique_checks'],'current_idea_records':30,'current_policy_records':4,'exact_related_originals':3,'real_nonzero_refresh_states':2,'full_suite_rerun':False,'last_full_receipt':'verification/full-350/summary.json','last_full_receipt_is_historical_for_current_changes':True}
cp['latest_section_environment']={'section':357,'receipt':'verification/sections/357.json','native_windows':validation,'native_game_or_chat_verified':False,'current_section_full_rerun':False,'last_full_receipt':'verification/full-350/summary.json'}
cp['windows_native_validation']=validation;cp['current_batch'].update(status=cp['batch_status'],completed_sections=357,next_section=358,next_section_started=False,receipt='verification/sections/357.json',batch_closed=False)
cp['policy'].update(verification_execution_preference='local_project_environment',avoid_duplicate_cloud_tests=True)
cp['current_data_versions'].update(current_real_domain_idea_records=30,current_real_domain_policy_records=4,current_real_domain_docs_revision=[442947,442954],current_real_domain_actual_applied_verified=False)
cp['current_available_full_validation']['historical_for_current_changed_source']=True
cp['current_available_full_validation']['current_worktree_validation_authority']=False
cp['last_full_validation']['historical_for_current_changed_source']=True
(ROOT/'DEVELOPMENT_CHECKPOINT.json').write_bytes(enc(cp))
doc('CLOUD_HANDOFF.md',(ROOT/'CLOUD_HANDOFF.md').read_text('utf8')+'\n<!-- section357-handoff:start -->\n## 第357节 + '+title+'\n\n'+details+'\n<!-- section357-handoff:end -->\n')
out=ROOT/'verification/sections/357-closeout';out.mkdir();shutil.copyfile(ROOT/'.cache/open_test_window_357.py',out/'execution-main-window.py')
runpy.run_path(str(ROOT/'scripts/update_cloud_index.py'))['update'](ROOT)
(out/'execution-closeout.py').write_bytes(Path(__file__).read_bytes());(out/'applied.json').write_bytes(enc({'section':357,'local_accepted':True,'ordinary_cloud_publication_verified':False,'next358_started':False,'at_Beijing':now}))
print(json.dumps({'section':357,'local_accepted':True,'ordinary_publication_pending':True},ensure_ascii=False))
