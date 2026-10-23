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
parent='97b34a5a62158e71e5198e78b8ee0e6a9c83f840';assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()==parent
assert subprocess.check_output(['git','branch','--show-current'],cwd=ROOT).decode().strip()=='codex/p2-development'
title='开局配置与招募职业组合的准确双向查询'
change='通用探索设置新增开局招募目录，21份配置与14份组合的106条明确关联可在同一窗口双向查阅，并分别按常规、实践者列表和未关联分支筛选。普通开局条目使用完整四字段身份进入，不按等级0或同名合并；五份固定职业组成、八份支援随机券和随心所欲保证范围分开。仅随心所欲显示“曾用其它组合探索”的本页声明，主题5星与通用文献4星说明各自适用范围。父刷新保持搜索、关联选中、本页声明和两阅读，失效清旧并手选恢复，切条目/主页面/关闭清除所属内容。'
limits='14组定义与旧原表相同，不称新增14种组合；新能力是完整配置关联、准确普通入口和主题保证范围说明。四个未关联支援组不推未来月份或可选资格；不会三张同职业不等于三张全不同。第一张完整职业池未知，不借支援组或通用旧文献补齐；使用其它组合探索不等于通关。固定职业列示顺序不当作真实出券顺序，5星保证不证明全部候选只有5星。当前解锁、真实菜单、人选/培养、完整初始资源/加成及服务器执行未知，不写本局、不招募、不推荐路线或给概率。P3/P2/P1未完成，识别最后。'
validation='本机27项必要测试和62项原生窗口唯一检查通过，21四字段配置/14组合/106明确关联逐次真实前进返回、17常规/4实践者与6/4/4分支、固定职业范围/五星彩别/不继承保证、仅相关控件、两个同等级0不同实践者准确普通入口、伪造关联拒绝、旧事件guard保持、父刷新两非零阅读/文字选择/关联/搜索/声明保留、真实成员损坏清旧手选恢复及所属关闭。七类真实外部操作零、临时本局与旧计算保持。独立子代理逐张实际看最终七图，不把截图当106关联证明；本机原测试窗正常更新可见响应，完整正常重启期间私人五路径保持。594旧选择器原序保留，新2个共596；350全量仅历史，下一节365到期全量范围不缩。当前要求/索引实际验证、未变25索引单测复用；私样本/1314/实机游戏聊天不计通过。继续至370后暂停。'
nname='verification/sections/364-necessary-attempt1/process.json';wname='verification/sections/364-native-attempt1/actual/window.json';pname='verification/sections/364-native-attempt1/process.json'
n,w,p=map(read,(nname,wname,pname));m=read('verification/sections/364-main-window.json');a=read('verification/sections/364-source-audit.json');v=read('verification/sections/364-root-visual.json')
assert n['passed']and n['methods_ran']==27 and w['passed']and w['qpa']=='windows'and w['qt_exit_code']==0 and w['unique_checks']==62 and w['verification_window_closed']
assert len(w['same_identity_refresh_observations'])==2 and len(w['screenshots'])==7 and len(w['actual_readings'])==144 and all(x==0 for x in w['external_operation_attempts'].values())
assert p['passed']and p['window_receipt_sha256']==sha(wname)
for result in(n,w):
 assert result['source_sha256_before']==result['source_sha256_after']
 for name,h in result['source_sha256_after'].items():assert sha(name)==h,name
assert v['passed']and len(v['final_screenshot_reviews'])==7 and a['ordered_previous594_preserved']and len(a['current_selectors'])==596
assert m['passed']and m['private_entire_normal_close_and_start_interval_unchanged']and m['window_visible_and_responsive']
now=datetime.now(timezone(timedelta(hours=8))).isoformat();pending='<!-- section364-publication-pending -->本地验收完成，普通推送及真实远端核对待完成。'
r={'section':364,'kind':'functional_section','title':title,'new_capability':change,'limitations':[limits],'at_Beijing':now,'branch':'codex/p2-development','necessary_validation':{**pin(nname),'methods_run':n['methods_ran'],'actual_exit':0},'native_windows_validation':{**pin(wname),'process':pin(pname),'unique_checks':w['unique_checks'],'actual_Qt_exit':0,'real_nonzero_refresh_states':2,'actual_MainWindow_entry_and_close_exercised':True,'all_seven_real_external_operations_zero':True},'root_visual_review':pin('verification/sections/364-root-visual.json'),'source_audit':pin('verification/sections/364-source-audit.json'),'original_project_window':pin('verification/sections/364-main-window.json'),'source_sha256':n['source_sha256_after'],'validated_source_sha256':w['source_sha256_after'],'full_suite_rerun':False,'last_full_receipt':'verification/full-350/summary.json','last_full_receipt_is_historical_for_this_changed_source':True,'last_full_validation_sha256':sha('verification/full-350/summary.json'),'next_periodic_full_section':365,'P3_complete':False,'P2_complete':False,'P1_complete':False,'private_state_contents_parsed_copied_or_restored':False,'private_state_hashed_locally_for_preservation_only':True,'private_hashes_published':False,'game_operated':False,'chat_sent':False,'cloud_publication_binding':'enclosing_commit','cloud_published':False,'execution_environment':'local_original_windows_project_venv','local_source_parity_required_for_cloud_publication':True}
(ROOT/'verification/sections/364.json').write_bytes(enc(r));details=change+'\n\n'+validation+'\n\n'+limits+'\n\n'+pending
old_wip=(ROOT/'WORK_IN_PROGRESS.md').read_bytes();(ROOT/'WORK_IN_PROGRESS.md').write_bytes(('## 第364节 + '+title+'\n\n'+now+'。'+details+'\n\n以下为历史记录；当前断点以上述364为准。\n\n').replace('\n','\r\n').encode()+old_wip)
doc('PROJECT_COMPLETED.md','## 第364节 + '+title+'\n\n'+now+'。'+details+'\n\n'+(ROOT/'PROJECT_COMPLETED.md').read_text('utf8'))
s=(ROOT/'AGENTS.md').read_text('utf8');end=s.index('\n## 项目级最高优先要求');note='下一到期完整检查须给304/305两份full320验证脚本显式传入--source-freeze及当轮根声明冻结文件；默认320仅供历史绑定。350原失败与组合复验见verification/full-350/summary.json。312补充窗口采用既有120秒默认，304/305显式传入当轮source-freeze。'
doc('AGENTS.md','## 当前续接 · 第364节 + '+title+'\n\n'+details+'\n\n继续P3；365从实际剩余节点/事件条件、掉落和固定地图缺口接续，未启动。资料条件对照不替代本局实际状态、生成、生效或结算。通用页面不恢复独立版本栏目。用户当前授权继续至370，完整收尾后暂停。只跑本机必要检查；下一全量365，严格低于15%才开始当前完整小节收尾。\n\n'+note+'\n'+s[end:])
s=(ROOT/'PROJECT_REQUIREMENTS.md').read_text('utf8');start=s.index('<!-- current-delivery:start -->');end=s.index('<!-- current-delivery:end -->')+len('<!-- current-delivery:end -->');doc('PROJECT_REQUIREMENTS.md',s[:start]+'<!-- current-delivery:start -->\n## 第364节 + '+title+'\n\n'+details+'\n<!-- current-delivery:end -->'+s[end:])
s=(ROOT/'PROJECT_PROGRESS.md').read_text('utf8')
old='补齐难度、结局前置和动态状态对具体节点/事件资格的影响';assert s.count(old)==1;s=s.replace(old,'开局招募组合的实际账户解锁、真实菜单、人选/培养与完整初始资源修正；补齐难度、结局前置和动态状态对具体节点/事件资格的影响')
doc('PROJECT_PROGRESS.md',s)
cp=read('DEVELOPMENT_CHECKPOINT.json');assert cp['completed_sections']==363 and cp['next_section']==364
for key in('current_section_validation','latest_section_environment','cloud_publication_closeout'):
 if key in cp:cp['historical_before364_'+key]=cp.pop(key)
cp.update(completed_sections=364,latest_functional_section=364,next_section=365,batch_status='P3_SECTION364_LOCAL_ACCEPTED_PUBLICATION_PENDING',next_action='第364节 + '+title+'已本机必要验收；普通推送核对后365接续P3实际剩余缺口，未启动。下次365。',full_validation_due=False)
cp['sections'].append({'number':364,'completion_ref':'p3-section-364','topic':title,'verification':'verification/sections/364.json'});cp['functional_sections_since_latest_requirement'].append(364)
cp['current_section_save']={'section':364,'verification':'verification/sections/364.json','scope':'current_functional_section','binding':'enclosing_commit'};cp['last_verified_cloud_save']['scope']='previous_functional_section'
cp['current_section_validation']={'section':364,'receipt':'verification/sections/364.json','methods_run':n['methods_ran'],'native_isolated_window_checks':w['unique_checks'],'real_nonzero_refresh_states':2,'full_suite_rerun':False,'last_full_receipt':'verification/full-350/summary.json','last_full_receipt_is_historical_for_current_changes':True}
cp['latest_section_environment']={'section':364,'receipt':'verification/sections/364.json','native_windows':validation,'native_game_or_chat_verified':False,'current_section_full_rerun':False,'last_full_receipt':'verification/full-350/summary.json'}
cp['windows_native_validation']=validation;cp['current_batch'].update(status=cp['batch_status'],completed_sections=364,next_section=365,next_section_started=False,receipt='verification/sections/364.json',batch_closed=False)
cp['policy'].update(verification_execution_preference='local_project_environment',avoid_duplicate_cloud_tests=True)
cp['current_data_versions'].update({'current_initial_recruit_groups': 14, 'current_initial_configurations': 21, 'current_initial_recruit_links': 106, 'current_initial_account_eligibility_verified': False})
cp['current_available_full_validation']['historical_for_current_changed_source']=True
cp['current_available_full_validation']['current_worktree_validation_authority']=False
cp['last_full_validation']['historical_for_current_changed_source']=True
(ROOT/'DEVELOPMENT_CHECKPOINT.json').write_bytes(enc(cp))
doc('CLOUD_HANDOFF.md',(ROOT/'CLOUD_HANDOFF.md').read_text('utf8')+'\n<!-- section364-handoff:start -->\n## 第364节 + '+title+'\n\n'+details+'\n<!-- section364-handoff:end -->\n')
out=ROOT/'verification/sections/364-closeout';out.mkdir();shutil.copyfile(ROOT/'.cache/open_test_window_364.py',out/'execution-main-window.py')
runpy.run_path(str(ROOT/'scripts/update_cloud_index.py'))['update'](ROOT)
(out/'execution-closeout.py').write_bytes(Path(__file__).read_bytes());(out/'applied.json').write_bytes(enc({'section':364,'local_accepted':True,'ordinary_cloud_publication_verified':False,'next365_started':False,'at_Beijing':now}))
print(json.dumps({'section':364,'local_accepted':True,'ordinary_publication_pending':True},ensure_ascii=False))
