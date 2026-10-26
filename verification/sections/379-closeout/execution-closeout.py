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
parent='6da5f66c180ab610fabc3534b1246acc6b60203e';assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()==parent
assert subprocess.check_output(['git','branch','--show-current'],cwd=ROOT).decode().strip()=='codex/p2-development'
title='晶矿惊蝗 · 双晶兽的护盾与捕杀'
change='晶矿惊蝗的两份准确来源分别接入晶玲兽和晶珑兽完整条件阅读。区分晶玲每次60层与最多80层、晶珑捕杀后的80层护盾、半血连击与模式变化；图鉴概述与详细文献不同口径分别保留。捕杀条件、固定技能准备与实际相遇分开，同关另一晶兽和固定地图准确关联。生息演算通用追踪不当作肉鸽本关既成行为。父刷新保留首领、主题、页签和两处阅读，坏源清旧、恢复手选、所属关闭清图。'
limits='完整页面含有生息演算的通用追踪说明。本页只把双兽核心条件作为文献参考，不把生息演算通用追踪、逃窜和缴械规则认作肉鸽本关已生效；完整原文放在来源详情。 护盾周期、层数、捕杀条件与模式均不表示本局已生效；当前精确引用与完整文献分别绑定，不追加预计面板或实时站位。 只作局外资料查阅，不操作游戏、发送聊天或改变本局；P3/P2/P1仍未完成，识别最后。'
validation='本机30项必要检查和53项原生窗口唯一检查通过，真实退出与当前源码摘要一致。主代理逐张实际查看7张最终图，外观不替代交互证明；七类真实外部操作均零，隔离临时状态不作为本局或游戏验证。原项目测试窗正常更新可见响应，正常关闭启动区间私人五路径仅摘要核对保持，不复制或发布内容。新选择器追加且既有次序保持。365全量仅历史来源，本节不称重跑全量；到期完整验收380另行执行。当前要求/索引实际验证，未变25索引测试复用；缺权限、私样本、实机游戏/聊天不冒称通过。按授权继续至380，完整当前小节和最终发布后暂停。双兽50%阈值的图鉴/完整文献冲突逐个保留；只有追踪来源明确属生息演算通用规则，不把逃窜缴械一并断言专用。基础减防-100不能线性外推，本页不计算叠加后的实际防御。2份配置4条准确引用与3张完整原卡分别核对，固定资料不表示当前触发。'
nname='verification/sections/379-necessary-attempt1/process.json';wname='verification/sections/379-native-attempt1/actual/window.json';pname='verification/sections/379-native-attempt1/process.json'
n,w,p=map(read,(nname,wname,pname));m=read('verification/sections/379-main-window.json');a=read('verification/sections/379-source-audit.json');v=read('verification/sections/379-root-visual.json')
assert n['passed']and n['methods_ran']==30 and w['passed']and w['qpa']=='windows'and w['qt_exit_code']==0 and w['unique_checks']==53 and w['verification_window_closed']
assert len(w['same_identity_refresh_observations'])==2 and len(w['screenshots'])==7 and len(w['actual_readings'])==8 and all(x==0 for x in w['external_operation_attempts'].values())
assert p['passed']and p['window_receipt_sha256']==sha(wname)
for result in(n,w):
 assert result['source_sha256_before']==result['source_sha256_after']
 for name,h in result['source_sha256_after'].items():assert sha(name)==h,name
assert v['passed']and len(v['final_screenshot_reviews'])==7 and a['ordered_previous623_preserved']and len(a['current_selectors'])==625
assert m['passed']and m['private_entire_normal_close_and_start_interval_unchanged']and m['window_visible_and_responsive']
now=datetime.now(timezone(timedelta(hours=8))).isoformat();pending='<!-- section379-publication-pending -->本地验收完成，普通推送及真实远端核对待完成。'
r={'section':379,'kind':'functional_section','title':title,'new_capability':change,'limitations':[limits],'at_Beijing':now,'branch':'codex/p2-development','necessary_validation':{**pin(nname),'methods_run':n['methods_ran'],'actual_exit':0},'native_windows_validation':{**pin(wname),'process':pin(pname),'unique_checks':w['unique_checks'],'actual_Qt_exit':0,'real_nonzero_refresh_states':2,'actual_MainWindow_entry_and_close_exercised':True,'all_seven_real_external_operations_zero':True},'root_visual_review':pin('verification/sections/379-root-visual.json'),'source_audit':pin('verification/sections/379-source-audit.json'),'original_project_window':pin('verification/sections/379-main-window.json'),'source_sha256':n['source_sha256_after'],'validated_source_sha256':w['source_sha256_after'],'full_suite_rerun':False,'last_full_receipt':'verification/full-365/summary.json','last_full_receipt_is_historical_for_this_changed_source':True,'last_full_validation_sha256':sha('verification/full-365/summary.json'),'next_periodic_full_section':380,'P3_complete':False,'P2_complete':False,'P1_complete':False,'private_state_contents_parsed_copied_or_restored':False,'private_state_hashed_locally_for_preservation_only':True,'private_hashes_published':False,'game_operated':False,'chat_sent':False,'cloud_publication_binding':'enclosing_commit','cloud_published':False,'execution_environment':'local_original_windows_project_venv','local_source_parity_required_for_cloud_publication':True}
(ROOT/'verification/sections/379.json').write_bytes(enc(r));details=change+'\n\n'+validation+'\n\n'+limits+'\n\n'+pending
old_wip=(ROOT/'WORK_IN_PROGRESS.md').read_bytes();(ROOT/'WORK_IN_PROGRESS.md').write_bytes(('## 第379节 + '+title+'\n\n'+now+'。'+details+'\n\n以下为历史记录；当前断点以上述379为准。\n\n').replace('\n','\r\n').encode()+old_wip)
doc('PROJECT_COMPLETED.md','## 第379节 + '+title+'\n\n'+now+'。'+details+'\n\n'+(ROOT/'PROJECT_COMPLETED.md').read_text('utf8'))
s=(ROOT/'AGENTS.md').read_text('utf8');end=s.index('\n## 项目级最高优先要求');note='下一到期完整检查须给304/305两份full320验证脚本显式传入--source-freeze及当轮根声明冻结文件；默认320仅供历史绑定。350原失败与组合复验见verification/full-350/summary.json。312补充窗口采用既有120秒默认，304/305显式传入当轮source-freeze。'
doc('AGENTS.md','## 当前续接 · 第379节 + '+title+'\n\n'+details+'\n\n继续P3；380从实际剩余节点/事件条件、掉落和固定地图缺口接续，未启动。资料条件对照不替代本局实际状态、生成、生效或结算。通用页面不恢复独立版本栏目。用户当前授权继续至380，完整收尾后暂停。只跑本机必要检查；下一全量380，严格低于15%才开始当前完整小节收尾。\n\n'+note+'\n'+s[end:])
s=(ROOT/'PROJECT_REQUIREMENTS.md').read_text('utf8');start=s.index('<!-- current-delivery:start -->');end=s.index('<!-- current-delivery:end -->')+len('<!-- current-delivery:end -->');doc('PROJECT_REQUIREMENTS.md',s[:start]+'<!-- current-delivery:start -->\n## 第379节 + '+title+'\n\n'+details+'\n<!-- current-delivery:end -->'+s[end:])
s=(ROOT/'PROJECT_PROGRESS.md').read_text('utf8')
doc('PROJECT_PROGRESS.md',s)
cp=read('DEVELOPMENT_CHECKPOINT.json');assert cp['completed_sections']==378 and cp['next_section']==379

if 379==371:
 cp['historical_before371_batch']={k:cp.get(k) for k in ('batch_start_section','batch_target_section','current_batch','batch_status')}
 cp['batch_start_section']=371;cp['batch_target_section']=380
 cp['current_batch']={'start':371,'end':380,'status':cp['batch_status'],'completed_sections':370,'next_section':371,'next_section_started':False,'batch_closed':False,'target_origin':'direct_user_request_2026-10-26_continue_to380','next_full_validation_after':380}
 cp['policy'].update(development_paused_by_latest_user_request=False,new_functional_sections_paused=False,stop_after_section=380,current_user_batch_target_section=380,batch_target_section=380,current_user_batch_completed=False,latest_user_instruction_receipt='verification/sections/371-preparation/resume-and-scope.json')
 cp['policy'].pop('paused_after_completed_section',None)

for key in('current_section_validation','latest_section_environment','cloud_publication_closeout'):
 if key in cp:cp['historical_before379_'+key]=cp.pop(key)
cp.update(completed_sections=379,latest_functional_section=379,next_section=380,batch_status='P3_SECTION379_LOCAL_ACCEPTED_PUBLICATION_PENDING',next_action='第379节 + '+title+'已本机必要验收；普通推送核对后380接续P3实际剩余缺口，未启动。下次380。',full_validation_due=False)
cp['sections'].append({'number':379,'completion_ref':'p3-section-379','topic':title,'verification':'verification/sections/379.json'});cp['functional_sections_since_latest_requirement'].append(379)
cp['current_section_save']={'section':379,'verification':'verification/sections/379.json','scope':'current_functional_section','binding':'enclosing_commit'};cp['last_verified_cloud_save']['scope']='previous_functional_section'
cp['current_section_validation']={'section':379,'receipt':'verification/sections/379.json','methods_run':n['methods_ran'],'native_isolated_window_checks':w['unique_checks'],'real_nonzero_refresh_states':2,'full_suite_rerun':False,'last_full_receipt':'verification/full-365/summary.json','last_full_receipt_is_historical_for_current_changes':True}
cp['latest_section_environment']={'section':379,'receipt':'verification/sections/379.json','native_windows':validation,'native_game_or_chat_verified':False,'current_section_full_rerun':False,'last_full_receipt':'verification/full-365/summary.json'}
cp['windows_native_validation']=validation;cp['current_batch'].update(status=cp['batch_status'],completed_sections=379,next_section=380,next_section_started=False,receipt='verification/sections/379.json',batch_closed=False)
cp['policy'].update(verification_execution_preference='local_project_environment',avoid_duplicate_cloud_tests=True)
cp['current_data_versions'].update({'guest_crystals_manifest': '015433e4fc028b4d29c7e32750d064b7a129b808371ecf06571541a4709f449d', 'guest_crystals_current_server_verified': False, 'guest_crystals_numeric_model_added': False})

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
doc('CLOUD_HANDOFF.md',(ROOT/'CLOUD_HANDOFF.md').read_text('utf8')+'\n<!-- section379-handoff:start -->\n## 第379节 + '+title+'\n\n'+details+'\n<!-- section379-handoff:end -->\n')
out=ROOT/'verification/sections/379-closeout';out.mkdir();shutil.copyfile(ROOT/'.cache/open_test_window_379.py',out/'execution-main-window.py')
runpy.run_path(str(ROOT/'scripts/update_cloud_index.py'))['update'](ROOT)
(out/'execution-closeout.py').write_bytes(Path(__file__).read_bytes());(out/'applied.json').write_bytes(enc({'section':379,'local_accepted':True,'ordinary_cloud_publication_verified':False,'next380_started':False,'at_Beijing':now}))
print(json.dumps({'section':379,'local_accepted':True,'ordinary_publication_pending':True},ensure_ascii=False))
