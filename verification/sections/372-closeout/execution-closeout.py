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
parent='4942843cf5c2d809c42856a28db19b9467a1dcb6';assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()==parent
assert subprocess.check_output(['git','branch','--show-current'],cwd=ROOT).decode().strip()=='codex/p2-development'
title='当前节点事件合流目录、条件原文检索与准确对话入口'
change='在通用节点事件页面按事件、选项原文、奖励文字和关联物品提示检索39份已证当前文献；8类文字内容与固定节点分类独立筛选，277个准确对话选项或结果位置回到21种既有完整reader。38旧目录组和三重身三CG来源保留，4未分类事件不强行归入不期而遇。目录默认未选，不写本局资格。'
limits='39份是已核对文献目录而非完整服务器事件池；文字分类不证明必要/充分资格，缺字段不当无条件或不可能。关联图标提示不单独当领取/消耗。实际阶段、隐藏条件、随机菜单/奖励池与当前服务器执行仍未知；P3/P2/P1均未完成。'
validation='本机31项必要检查和45项原生窗口唯一检查通过，真实退出与当前源码摘要一致。主代理逐张实际查看7张最终图，外观不替代交互证明；七类真实外部操作均零，隔离临时状态不作为本局或游戏验证。原项目测试窗正常更新可见响应，正常关闭启动区间私人五路径仅摘要核对保持，不复制或发布内容。新选择器追加且既有次序保持。365全量仅历史来源，本节不称重跑全量；到期完整验收380另行执行。当前要求/索引实际验证，未变25索引测试复用；缺权限、私样本、实机游戏/聊天不冒称通过。按授权继续至380，完整当前小节和最终发布后暂停。第一轮原生失败保留；修复测试将子页恢复误当父页恢复的前提，真实点击父重核后恢复。补充真实Esc清资料检查，并修复371选择器在CLI退出后不可达的缺陷，612项顺序在真实main入口与快照相符；没有因此冒称全量运行。'
nname='verification/sections/372-necessary-attempt3/process.json';wname='verification/sections/372-native-attempt2/actual/window.json';pname='verification/sections/372-native-attempt2/process.json'
n,w,p=map(read,(nname,wname,pname));m=read('verification/sections/372-main-window.json');a=read('verification/sections/372-source-audit.json');v=read('verification/sections/372-root-visual.json')
assert n['passed']and n['methods_ran']==31 and w['passed']and w['qpa']=='windows'and w['qt_exit_code']==0 and w['unique_checks']==45 and w['verification_window_closed']
assert len(w['same_identity_refresh_observations'])==2 and len(w['screenshots'])==7 and len(w['actual_readings'])==21 and all(x==0 for x in w['external_operation_attempts'].values())
assert p['passed']and p['window_receipt_sha256']==sha(wname)
for result in(n,w):
 assert result['source_sha256_before']==result['source_sha256_after']
 for name,h in result['source_sha256_after'].items():assert sha(name)==h,name
assert v['passed']and len(v['final_screenshot_reviews'])==7 and a['ordered_previous610_preserved']and len(a['current_selectors'])==612
assert m['passed']and m['private_entire_normal_close_and_start_interval_unchanged']and m['window_visible_and_responsive']
now=datetime.now(timezone(timedelta(hours=8))).isoformat();pending='<!-- section372-publication-pending -->本地验收完成，普通推送及真实远端核对待完成。'
r={'section':372,'kind':'functional_section','title':title,'new_capability':change,'limitations':[limits],'at_Beijing':now,'branch':'codex/p2-development','necessary_validation':{**pin(nname),'methods_run':n['methods_ran'],'actual_exit':0},'native_windows_validation':{**pin(wname),'process':pin(pname),'unique_checks':w['unique_checks'],'actual_Qt_exit':0,'real_nonzero_refresh_states':2,'actual_MainWindow_entry_and_close_exercised':True,'all_seven_real_external_operations_zero':True},'root_visual_review':pin('verification/sections/372-root-visual.json'),'source_audit':pin('verification/sections/372-source-audit.json'),'original_project_window':pin('verification/sections/372-main-window.json'),'source_sha256':n['source_sha256_after'],'validated_source_sha256':w['source_sha256_after'],'full_suite_rerun':False,'last_full_receipt':'verification/full-365/summary.json','last_full_receipt_is_historical_for_this_changed_source':True,'last_full_validation_sha256':sha('verification/full-365/summary.json'),'next_periodic_full_section':380,'P3_complete':False,'P2_complete':False,'P1_complete':False,'private_state_contents_parsed_copied_or_restored':False,'private_state_hashed_locally_for_preservation_only':True,'private_hashes_published':False,'game_operated':False,'chat_sent':False,'cloud_publication_binding':'enclosing_commit','cloud_published':False,'execution_environment':'local_original_windows_project_venv','local_source_parity_required_for_cloud_publication':True}
(ROOT/'verification/sections/372.json').write_bytes(enc(r));details=change+'\n\n'+validation+'\n\n'+limits+'\n\n'+pending
old_wip=(ROOT/'WORK_IN_PROGRESS.md').read_bytes();(ROOT/'WORK_IN_PROGRESS.md').write_bytes(('## 第372节 + '+title+'\n\n'+now+'。'+details+'\n\n以下为历史记录；当前断点以上述372为准。\n\n').replace('\n','\r\n').encode()+old_wip)
doc('PROJECT_COMPLETED.md','## 第372节 + '+title+'\n\n'+now+'。'+details+'\n\n'+(ROOT/'PROJECT_COMPLETED.md').read_text('utf8'))
s=(ROOT/'AGENTS.md').read_text('utf8');end=s.index('\n## 项目级最高优先要求');note='下一到期完整检查须给304/305两份full320验证脚本显式传入--source-freeze及当轮根声明冻结文件；默认320仅供历史绑定。350原失败与组合复验见verification/full-350/summary.json。312补充窗口采用既有120秒默认，304/305显式传入当轮source-freeze。'
doc('AGENTS.md','## 当前续接 · 第372节 + '+title+'\n\n'+details+'\n\n继续P3；373从实际剩余节点/事件条件、掉落和固定地图缺口接续，未启动。资料条件对照不替代本局实际状态、生成、生效或结算。通用页面不恢复独立版本栏目。用户当前授权继续至380，完整收尾后暂停。只跑本机必要检查；下一全量380，严格低于15%才开始当前完整小节收尾。\n\n'+note+'\n'+s[end:])
s=(ROOT/'PROJECT_REQUIREMENTS.md').read_text('utf8');start=s.index('<!-- current-delivery:start -->');end=s.index('<!-- current-delivery:end -->')+len('<!-- current-delivery:end -->');doc('PROJECT_REQUIREMENTS.md',s[:start]+'<!-- current-delivery:start -->\n## 第372节 + '+title+'\n\n'+details+'\n<!-- current-delivery:end -->'+s[end:])
s=(ROOT/'PROJECT_PROGRESS.md').read_text('utf8')
doc('PROJECT_PROGRESS.md',s)
cp=read('DEVELOPMENT_CHECKPOINT.json');assert cp['completed_sections']==371 and cp['next_section']==372

if 372==371:
 cp['historical_before371_batch']={k:cp.get(k) for k in ('batch_start_section','batch_target_section','current_batch','batch_status')}
 cp['batch_start_section']=371;cp['batch_target_section']=380
 cp['current_batch']={'start':371,'end':380,'status':cp['batch_status'],'completed_sections':370,'next_section':371,'next_section_started':False,'batch_closed':False,'target_origin':'direct_user_request_2026-10-26_continue_to380','next_full_validation_after':380}
 cp['policy'].update(development_paused_by_latest_user_request=False,new_functional_sections_paused=False,stop_after_section=380,current_user_batch_target_section=380,batch_target_section=380,current_user_batch_completed=False,latest_user_instruction_receipt='verification/sections/371-preparation/resume-and-scope.json')
 cp['policy'].pop('paused_after_completed_section',None)

for key in('current_section_validation','latest_section_environment','cloud_publication_closeout'):
 if key in cp:cp['historical_before372_'+key]=cp.pop(key)
cp.update(completed_sections=372,latest_functional_section=372,next_section=373,batch_status='P3_SECTION372_LOCAL_ACCEPTED_PUBLICATION_PENDING',next_action='第372节 + '+title+'已本机必要验收；普通推送核对后373接续P3实际剩余缺口，未启动。下次380。',full_validation_due=False)
cp['sections'].append({'number':372,'completion_ref':'p3-section-372','topic':title,'verification':'verification/sections/372.json'});cp['functional_sections_since_latest_requirement'].append(372)
cp['current_section_save']={'section':372,'verification':'verification/sections/372.json','scope':'current_functional_section','binding':'enclosing_commit'};cp['last_verified_cloud_save']['scope']='previous_functional_section'
cp['current_section_validation']={'section':372,'receipt':'verification/sections/372.json','methods_run':n['methods_ran'],'native_isolated_window_checks':w['unique_checks'],'real_nonzero_refresh_states':2,'full_suite_rerun':False,'last_full_receipt':'verification/full-365/summary.json','last_full_receipt_is_historical_for_current_changes':True}
cp['latest_section_environment']={'section':372,'receipt':'verification/sections/372.json','native_windows':validation,'native_game_or_chat_verified':False,'current_section_full_rerun':False,'last_full_receipt':'verification/full-365/summary.json'}
cp['windows_native_validation']=validation;cp['current_batch'].update(status=cp['batch_status'],completed_sections=372,next_section=373,next_section_started=False,receipt='verification/sections/372.json',batch_closed=False)
cp['policy'].update(verification_execution_preference='local_project_environment',avoid_duplicate_cloud_tests=True)
cp['current_data_versions'].update({'game_commit': 'bee3f83c5d60590b5e1cd42b8d09d00ce32ab10d', 'data': 'rouge/data/current-event-directory.json', 'manifest': 'research/p3-current-event-directory-372/runtime-manifest.json', 'schema': 'current_event_directory_372_v1'})

f=read('verification/full-365/summary.json');assert f['available_checks_passed']and f['scope_not_reduced']
cp['current_available_full_validation']={
 'section':365,'receipt':'verification/full-365/summary.json','available_scope_passed':True,
 'actual_validation_attempt':f['actual_validation_attempt'],
 'single_available_scope_execution_all_green':f['single_available_scope_execution_all_green'],
 'actual_root_controller_exit':f['actual_root_controller_exit'],
 'validation_composition':f['validation_composition'],
 'source_freeze':f['source_freeze'],'source_freeze_sha256':f['source_freeze_sha256'],
 'native_windows_game_chat_verified':False,
 'historical_for_current_changed_source':True,
 'current_worktree_validation_authority':not True}
cp['last_full_validation']={'after_section':365,'receipt':'verification/full-365/summary.json',
 'available_checks_passed':True,'complete_repository_validation':False,'scope_not_reduced':True,
 'source_freeze':f['source_freeze'],'source_freeze_sha256':f['source_freeze_sha256'],
 'historical_for_current_changed_source':True}
cp['next_full_validation_after']=380
for key in ('validation_cadence','policy','current_batch','current_batch_commit_policy'):
 if isinstance(cp.get(key),dict):cp[key]['next_full_validation_after']=380
cp['current_batch']['next_full_validation_after']=380
cp['current_section_validation']['full_suite_rerun']=not True
cp['latest_section_environment']['current_section_full_rerun']=not True

(ROOT/'DEVELOPMENT_CHECKPOINT.json').write_bytes(enc(cp))
doc('CLOUD_HANDOFF.md',(ROOT/'CLOUD_HANDOFF.md').read_text('utf8')+'\n<!-- section372-handoff:start -->\n## 第372节 + '+title+'\n\n'+details+'\n<!-- section372-handoff:end -->\n')
out=ROOT/'verification/sections/372-closeout';out.mkdir();shutil.copyfile(ROOT/'.cache/open_test_window_372.py',out/'execution-main-window.py')
runpy.run_path(str(ROOT/'scripts/update_cloud_index.py'))['update'](ROOT)
(out/'execution-closeout.py').write_bytes(Path(__file__).read_bytes());(out/'applied.json').write_bytes(enc({'section':372,'local_accepted':True,'ordinary_cloud_publication_verified':False,'next373_started':False,'at_Beijing':now}))
print(json.dumps({'section':372,'local_accepted':True,'ordinary_publication_pending':True},ensure_ascii=False))
