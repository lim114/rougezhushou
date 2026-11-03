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
parent='3908c7a40146e673ffcbeac7b0668b97a36aeb77';assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()==parent
assert subprocess.check_output(['git','branch','--show-current'],cwd=ROOT).decode().strip()=='codex/p2-development'
title='前瞻性投资五档解锁、计数口径与收藏品反向说明'
change='通用探索设置可打开投资五档解锁资料，以本页独立累计投资额对照15、50、125、250、500源石锭门槛及差额；250档另外展示金酒之杯原解锁文案的历史最高余额，两输入互不补值，默认未知。仅对应档位显示专属控件及有图物品说明，准确金酒之杯可反向打开250档。解锁与取得、实际账户状态分别说明，不把50档作战猜成特定关卡，也不合并125/500为当前最终商店栏位。父刷新保留两阅读器、输入和物品子窗，换物品/页面或源损坏关闭所属旧内容。'
limits='固定bee3五档原表与已保存PRTS修订433770完整投资表相互核对；没有冒称新下载或当前服务器实测。累计计数与金酒之杯最高余额原文存在差异，双方原文保留；250档绑定是明确命名加当前唯一同名收藏品，原奖励表没有物品指针，不能写成明确itemId。实际解锁、领取、完整取得来源、最终商店栏位及当前服务器口径仍未知。本页输入不写本局/账户或干员计算，没有游戏操作、聊天、路线建议或概率；P3/P2/P1未完成，识别最后。'
validation='本机26项必要测试与30项原生窗口唯一检查通过，核对五档共15组上下界、累计与最高余额双向冲突、缺值保持未知、专属控件只在250档出现、准确原物品图片与解锁文案、普通探索设置及唯一收藏品反向入口、两组非零阅读/输入/所属物品经父刷新保持、坏源清除及手选恢复、换页换物品及主窗整树关闭。七类真实外部操作均零，本局与旧计算不变。六张最终截图主代理逐张查看；原项目测试窗正常更新可见响应，完整关闭/启动区间私人五路径保持。578旧选择器原序保留，新加2个共580；350完整检查仅改前历史证据，下一定期365。未变索引25项旧单测复用并实际验证本节要求/索引；不可用私样本/符号链接1314/实机游戏聊天不冒称通过。实际账户工具显示唯一可读窗口已用24%、剩余76%，其它窗口不可用，不触发低于15%收尾；已脱敏保存，继续至370后暂停。'
nname='verification/sections/356-necessary-attempt1/process.json';wname='verification/sections/356-native-attempt1/actual/window.json';pname='verification/sections/356-native-attempt1/process.json'
n,w,p=map(read,(nname,wname,pname));m=read('verification/sections/356-main-window.json');a=read('verification/sections/356-source-audit.json');v=read('verification/sections/356-root-visual.json')
assert n['passed']and n['methods_ran']==26 and w['passed']and w['qpa']=='windows'and w['qt_exit_code']==0 and w['unique_checks']==30 and w['verification_window_closed']
assert len(w['same_identity_refresh_observations'])==2 and len(w['screenshots'])==6 and len(w['actual_readings'])==15 and all(x==0 for x in w['external_operation_attempts'].values())
assert p['passed']and p['window_receipt_sha256']==sha(wname)
for result in(n,w):
 assert result['source_sha256_before']==result['source_sha256_after']
 for name,h in result['source_sha256_after'].items():assert sha(name)==h,name
assert v['passed']and len(v['final_screenshot_reviews'])==6 and a['ordered_previous578_preserved']and len(a['current_selectors'])==580
assert m['passed']and m['private_entire_normal_close_and_start_interval_unchanged']and m['window_visible_and_responsive']
now=datetime.now(timezone(timedelta(hours=8))).isoformat();pending='<!-- section356-publication-pending -->本地验收完成，普通推送及真实远端核对待完成。'
r={'section':356,'kind':'functional_section','title':title,'new_capability':change,'limitations':[limits],'at_Beijing':now,'branch':'codex/p2-development','necessary_validation':{**pin(nname),'methods_run':n['methods_ran'],'actual_exit':0},'native_windows_validation':{**pin(wname),'process':pin(pname),'unique_checks':w['unique_checks'],'actual_Qt_exit':0,'investment_thresholds':[15,50,125,250,500],'threshold_boundary_observations':15,'counter_conflict_retained':True,'real_nonzero_refresh_states':2,'actual_MainWindow_entry_and_close_exercised':True,'all_seven_real_external_operations_zero':True},'root_visual_review':pin('verification/sections/356-root-visual.json'),'source_audit':pin('verification/sections/356-source-audit.json'),'original_project_window':pin('verification/sections/356-main-window.json'),'source_sha256':n['source_sha256_after'],'validated_source_sha256':w['source_sha256_after'],'full_suite_rerun':False,'last_full_receipt':'verification/full-350/summary.json','last_full_receipt_is_historical_for_this_changed_source':True,'last_full_validation_sha256':sha('verification/full-350/summary.json'),'next_periodic_full_section':365,'P3_complete':False,'P2_complete':False,'P1_complete':False,'private_state_contents_parsed_copied_or_restored':False,'private_state_hashed_locally_for_preservation_only':True,'private_hashes_published':False,'game_operated':False,'chat_sent':False,'cloud_publication_binding':'enclosing_commit','cloud_published':False,'execution_environment':'local_original_windows_project_venv','local_source_parity_required_for_cloud_publication':True}
(ROOT/'verification/sections/356.json').write_bytes(enc(r));details=change+'\n\n'+validation+'\n\n'+limits+'\n\n'+pending
old_wip=(ROOT/'WORK_IN_PROGRESS.md').read_bytes();(ROOT/'WORK_IN_PROGRESS.md').write_bytes(('## 第356节 + '+title+'\n\n'+now+'。'+details+'\n\n以下为历史记录；当前断点以上述356为准。\n\n').replace('\n','\r\n').encode()+old_wip)
doc('PROJECT_COMPLETED.md','## 第356节 + '+title+'\n\n'+now+'。'+details+'\n\n'+(ROOT/'PROJECT_COMPLETED.md').read_text('utf8'))
s=(ROOT/'AGENTS.md').read_text('utf8');end=s.index('\n## 项目级最高优先要求');note='下一到期完整检查须给304/305两份full320验证脚本显式传入--source-freeze及当轮根声明冻结文件；默认320仅供历史绑定。350原失败与组合复验见verification/full-350/summary.json。312补充窗口采用既有120秒默认，304/305显式传入当轮source-freeze。'
doc('AGENTS.md','## 当前续接 · 第356节 + '+title+'\n\n'+details+'\n\n继续P3；357从实际剩余节点/事件条件、掉落和固定地图缺口接续，未启动。投资解锁说明不替代真实账户状态或取得来源。通用页面不恢复独立版本栏目。用户当前授权继续至370，完整收尾后暂停。只跑本机必要检查；下一全量365，严格低于15%才开始当前完整小节收尾。\n\n'+note+'\n'+s[end:])
s=(ROOT/'PROJECT_REQUIREMENTS.md').read_text('utf8');start=s.index('<!-- current-delivery:start -->');end=s.index('<!-- current-delivery:end -->')+len('<!-- current-delivery:end -->');doc('PROJECT_REQUIREMENTS.md',s[:start]+'<!-- current-delivery:start -->\n## 第356节 + '+title+'\n\n'+details+'\n<!-- current-delivery:end -->'+s[end:])
s=(ROOT/'PROJECT_PROGRESS.md').read_text('utf8');old='全部具名物品的其余取得来源';assert s.count(old)==1;s=s.replace(old,'投资累计/最高余额冲突的当前服务器口径与真实解锁/领取、最终商店栏位；全部具名物品的其余取得来源');doc('PROJECT_PROGRESS.md',s)
cp=read('DEVELOPMENT_CHECKPOINT.json');assert cp['completed_sections']==355 and cp['next_section']==356
for key in('current_section_validation','latest_section_environment','cloud_publication_closeout'):
 if key in cp:cp['historical_before356_'+key]=cp.pop(key)
cp.update(completed_sections=356,latest_functional_section=356,next_section=357,batch_status='P3_SECTION356_LOCAL_ACCEPTED_PUBLICATION_PENDING',next_action='第356节 + '+title+'已本机必要验收；普通推送核对后357接续P3实际剩余缺口，未启动。下次365。',full_validation_due=False)
cp['sections'].append({'number':356,'completion_ref':'p3-section-356','topic':title,'verification':'verification/sections/356.json'});cp['functional_sections_since_latest_requirement'].append(356)
cp['current_section_save']={'section':356,'verification':'verification/sections/356.json','scope':'current_functional_section','binding':'enclosing_commit'};cp['last_verified_cloud_save']['scope']='previous_functional_section'
cp['current_section_validation']={'section':356,'receipt':'verification/sections/356.json','methods_run':n['methods_ran'],'native_isolated_window_checks':w['unique_checks'],'investment_thresholds':[15,50,125,250,500],'threshold_boundary_observations':15,'counter_conflict_retained':True,'real_nonzero_refresh_states':2,'full_suite_rerun':False,'last_full_receipt':'verification/full-350/summary.json','last_full_receipt_is_historical_for_current_changes':True}
cp['latest_section_environment']={'section':356,'receipt':'verification/sections/356.json','native_windows':validation,'native_game_or_chat_verified':False,'current_section_full_rerun':False,'last_full_receipt':'verification/full-350/summary.json'}
cp['windows_native_validation']=validation;cp['current_batch'].update(status=cp['batch_status'],completed_sections=356,next_section=357,next_section_started=False,receipt='verification/sections/356.json',batch_closed=False)
cp['policy'].update(verification_execution_preference='local_project_environment',avoid_duplicate_cloud_tests=True)
cp['current_data_versions'].update(current_bank_thresholds=[15,50,125,250,500],current_bank_counter_conflict_retained=True,current_bank_actual_account_verified=False)
cp['policy'].update(current_usage_remaining_percent=76,current_usage_receipt='verification/sections/356-usage.json')
cp['current_available_full_validation']['historical_for_current_changed_source']=True
cp['current_available_full_validation']['current_worktree_validation_authority']=False
cp['last_full_validation']['historical_for_current_changed_source']=True
(ROOT/'DEVELOPMENT_CHECKPOINT.json').write_bytes(enc(cp))
doc('CLOUD_HANDOFF.md',(ROOT/'CLOUD_HANDOFF.md').read_text('utf8')+'\n<!-- section356-handoff:start -->\n## 第356节 + '+title+'\n\n'+details+'\n<!-- section356-handoff:end -->\n')
out=ROOT/'verification/sections/356-closeout';out.mkdir();shutil.copyfile(ROOT/'.cache/open_test_window_356.py',out/'execution-main-window.py')
runpy.run_path(str(ROOT/'scripts/update_cloud_index.py'))['update'](ROOT)
(out/'execution-closeout.py').write_bytes(Path(__file__).read_bytes());(out/'applied.json').write_bytes(enc({'section':356,'local_accepted':True,'ordinary_cloud_publication_verified':False,'next357_started':False,'at_Beijing':now}))
print(json.dumps({'section':356,'local_accepted':True,'ordinary_publication_pending':True},ensure_ascii=False))
