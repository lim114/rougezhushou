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
parent='0f13838819baffd193f03d2454d2d88462cbbf8e';assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()==parent
assert subprocess.check_output(['git','branch','--show-current'],cwd=ROOT).decode().strip()=='codex/p2-development'
title='准确区域的入区行动力分项与耗尽条件'
change='通用节点事件页加入区域行动力与离开条件目录，27份准确区域可按抵达险路尽头、击败险路恶敌和秘境返回分支查阅。逐项绑定入区发放参数、目标和耗尽说明，保留六个中文区域文献及同名变体限制。只有第一层显示翅膀加成声明，5+1仅资料小计；其它区域和秘境隐藏无关选项。从普通区域条目准确反向定位，父刷新保持本页声明和两种阅读，失效清空并要求手动重选。'
limits='旧189区域目标/预算和196秘境返回不重复记新机制；新增为当前27份明确入区发放参数与文献适用范围，其中zone7不按编号推成第七层。六名文献未区分同名变体，秘境和新区域缺独立数量文献，只列参数。基础与翅膀分项不是完整实际入区行动力；耗尽条件相符不证明已经触发，不推实际返回节点/区域、结算顺序、当前资格或服务器执行，不替换旧预算和本局状态。P3/P2/P1未完成，无游戏/聊天操作、概率和路线建议。'
validation='本机26项必要测试及53项原生窗口唯一检查通过，实际查看27准确区域、4/4/19目标分支、翅膀未知/否/是与行动力未知/0/1边界、同名变体/新区域/秘境区别、准确普通入口、两非零阅读与声明经父刷新保持、真实成员损坏清旧和手动恢复、所属窗口关闭。七类外部实际操作零，临时本局与旧计算上下文保持。独立子代理实际查看最终六张图，无可见阻断；本机原项目测试窗更新且可见响应，完整正常重启期间私人五路径保持。584旧选择器原序保留，新增2个共586；350全量仅改前历史，下一定期365。索引25旧单测未变复用，当前索引/要求实际校验。缺原Windows私样本/1314及实机游戏聊天未计通过；继续至370后暂停。'
nname='verification/sections/359-necessary-attempt1/process.json';wname='verification/sections/359-native-attempt1/actual/window.json';pname='verification/sections/359-native-attempt1/process.json'
n,w,p=map(read,(nname,wname,pname));m=read('verification/sections/359-main-window.json');a=read('verification/sections/359-source-audit.json');v=read('verification/sections/359-root-visual.json')
assert n['passed']and n['methods_ran']==26 and w['passed']and w['qpa']=='windows'and w['qt_exit_code']==0 and w['unique_checks']==53 and w['verification_window_closed']
assert len(w['same_identity_refresh_observations'])==2 and len(w['screenshots'])==6 and len(w['actual_region_readings'])==27 and all(x==0 for x in w['external_operation_attempts'].values())
assert p['passed']and p['window_receipt_sha256']==sha(wname)
for result in(n,w):
 assert result['source_sha256_before']==result['source_sha256_after']
 for name,h in result['source_sha256_after'].items():assert sha(name)==h,name
assert v['passed']and len(v['final_screenshot_reviews'])==6 and a['ordered_previous584_preserved']and len(a['current_selectors'])==586
assert m['passed']and m['private_entire_normal_close_and_start_interval_unchanged']and m['window_visible_and_responsive']
now=datetime.now(timezone(timedelta(hours=8))).isoformat();pending='<!-- section359-publication-pending -->本地验收完成，普通推送及真实远端核对待完成。'
r={'section':359,'kind':'functional_section','title':title,'new_capability':change,'limitations':[limits],'at_Beijing':now,'branch':'codex/p2-development','necessary_validation':{**pin(nname),'methods_run':n['methods_ran'],'actual_exit':0},'native_windows_validation':{**pin(wname),'process':pin(pname),'unique_checks':w['unique_checks'],'actual_Qt_exit':0,'real_nonzero_refresh_states':2,'actual_MainWindow_entry_and_close_exercised':True,'all_seven_real_external_operations_zero':True},'root_visual_review':pin('verification/sections/359-root-visual.json'),'source_audit':pin('verification/sections/359-source-audit.json'),'original_project_window':pin('verification/sections/359-main-window.json'),'source_sha256':n['source_sha256_after'],'validated_source_sha256':w['source_sha256_after'],'full_suite_rerun':False,'last_full_receipt':'verification/full-350/summary.json','last_full_receipt_is_historical_for_this_changed_source':True,'last_full_validation_sha256':sha('verification/full-350/summary.json'),'next_periodic_full_section':365,'P3_complete':False,'P2_complete':False,'P1_complete':False,'private_state_contents_parsed_copied_or_restored':False,'private_state_hashed_locally_for_preservation_only':True,'private_hashes_published':False,'game_operated':False,'chat_sent':False,'cloud_publication_binding':'enclosing_commit','cloud_published':False,'execution_environment':'local_original_windows_project_venv','local_source_parity_required_for_cloud_publication':True}
(ROOT/'verification/sections/359.json').write_bytes(enc(r));details=change+'\n\n'+validation+'\n\n'+limits+'\n\n'+pending
old_wip=(ROOT/'WORK_IN_PROGRESS.md').read_bytes();(ROOT/'WORK_IN_PROGRESS.md').write_bytes(('## 第359节 + '+title+'\n\n'+now+'。'+details+'\n\n以下为历史记录；当前断点以上述359为准。\n\n').replace('\n','\r\n').encode()+old_wip)
doc('PROJECT_COMPLETED.md','## 第359节 + '+title+'\n\n'+now+'。'+details+'\n\n'+(ROOT/'PROJECT_COMPLETED.md').read_text('utf8'))
s=(ROOT/'AGENTS.md').read_text('utf8');end=s.index('\n## 项目级最高优先要求');note='下一到期完整检查须给304/305两份full320验证脚本显式传入--source-freeze及当轮根声明冻结文件；默认320仅供历史绑定。350原失败与组合复验见verification/full-350/summary.json。312补充窗口采用既有120秒默认，304/305显式传入当轮source-freeze。'
doc('AGENTS.md','## 当前续接 · 第359节 + '+title+'\n\n'+details+'\n\n继续P3；360从实际剩余节点/事件条件、掉落和固定地图缺口接续，未启动。资料条件对照不替代本局实际状态、生成、生效或结算。通用页面不恢复独立版本栏目。用户当前授权继续至370，完整收尾后暂停。只跑本机必要检查；下一全量365，严格低于15%才开始当前完整小节收尾。\n\n'+note+'\n'+s[end:])
s=(ROOT/'PROJECT_REQUIREMENTS.md').read_text('utf8');start=s.index('<!-- current-delivery:start -->');end=s.index('<!-- current-delivery:end -->')+len('<!-- current-delivery:end -->');doc('PROJECT_REQUIREMENTS.md',s[:start]+'<!-- current-delivery:start -->\n## 第359节 + '+title+'\n\n'+details+'\n<!-- current-delivery:end -->'+s[end:])
s=(ROOT/'PROJECT_PROGRESS.md').read_text('utf8')
old='同步完成标志、住民/迷雾、行动力与加工品的实际节点状态规则';assert s.count(old)==1;s=s.replace(old,'入区发放参数与本次实际挂载/执行的绑定、完整最终行动力与特殊区域真实返回；同步完成标志、住民/迷雾、行动力与加工品的实际节点状态规则')
doc('PROJECT_PROGRESS.md',s)
cp=read('DEVELOPMENT_CHECKPOINT.json');assert cp['completed_sections']==358 and cp['next_section']==359
for key in('current_section_validation','latest_section_environment','cloud_publication_closeout'):
 if key in cp:cp['historical_before359_'+key]=cp.pop(key)
cp.update(completed_sections=359,latest_functional_section=359,next_section=360,batch_status='P3_SECTION359_LOCAL_ACCEPTED_PUBLICATION_PENDING',next_action='第359节 + '+title+'已本机必要验收；普通推送核对后360接续P3实际剩余缺口，未启动。下次365。',full_validation_due=False)
cp['sections'].append({'number':359,'completion_ref':'p3-section-359','topic':title,'verification':'verification/sections/359.json'});cp['functional_sections_since_latest_requirement'].append(359)
cp['current_section_save']={'section':359,'verification':'verification/sections/359.json','scope':'current_functional_section','binding':'enclosing_commit'};cp['last_verified_cloud_save']['scope']='previous_functional_section'
cp['current_section_validation']={'section':359,'receipt':'verification/sections/359.json','methods_run':n['methods_ran'],'native_isolated_window_checks':w['unique_checks'],'real_nonzero_refresh_states':2,'full_suite_rerun':False,'last_full_receipt':'verification/full-350/summary.json','last_full_receipt_is_historical_for_current_changes':True}
cp['latest_section_environment']={'section':359,'receipt':'verification/sections/359.json','native_windows':validation,'native_game_or_chat_verified':False,'current_section_full_rerun':False,'last_full_receipt':'verification/full-350/summary.json'}
cp['windows_native_validation']=validation;cp['current_batch'].update(status=cp['batch_status'],completed_sections=359,next_section=360,next_section_started=False,receipt='verification/sections/359.json',batch_closed=False)
cp['policy'].update(verification_execution_preference='local_project_environment',avoid_duplicate_cloud_tests=True)
cp['current_data_versions'].update({'current_exact_regions': 27, 'current_entry_grant_records': 27, 'current_region_parameter_actual_execution_verified': False})
cp['current_available_full_validation']['historical_for_current_changed_source']=True
cp['current_available_full_validation']['current_worktree_validation_authority']=False
cp['last_full_validation']['historical_for_current_changed_source']=True
(ROOT/'DEVELOPMENT_CHECKPOINT.json').write_bytes(enc(cp))
doc('CLOUD_HANDOFF.md',(ROOT/'CLOUD_HANDOFF.md').read_text('utf8')+'\n<!-- section359-handoff:start -->\n## 第359节 + '+title+'\n\n'+details+'\n<!-- section359-handoff:end -->\n')
out=ROOT/'verification/sections/359-closeout';out.mkdir();shutil.copyfile(ROOT/'.cache/open_test_window_359.py',out/'execution-main-window.py')
runpy.run_path(str(ROOT/'scripts/update_cloud_index.py'))['update'](ROOT)
(out/'execution-closeout.py').write_bytes(Path(__file__).read_bytes());(out/'applied.json').write_bytes(enc({'section':359,'local_accepted':True,'ordinary_cloud_publication_verified':False,'next360_started':False,'at_Beijing':now}))
print(json.dumps({'section':359,'local_accepted':True,'ordinary_publication_pending':True},ensure_ascii=False))
