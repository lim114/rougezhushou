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
parent='9fd2e496d0007a1e4e89f4ef948af900497a1ef5';assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()==parent
assert subprocess.check_output(['git','branch','--show-current'],cwd=ROOT).decode().strip()=='codex/p2-development'
title='从敌人反查准确出怪记录与条件分支'
change='通用关卡的准确敌人页面新增出怪反查，可按主波次和条件分支查看该引用对应的直接出怪条目，准确返回原条目及已有地图位置参考。184份配置、2060条敌人引用逐项核对；无直接记录的110条保留技能、装置等动态来源的可能，不据此判断不会出现。同名多引用保留候选，不强选等级。真实父刷新保留所选条目、分类、页签和两处阅读，坏源清旧并手选恢复，切换敌人或关闭所属窗口清理地图。'
limits='这里只反查7696条固定直接SPAWN声明，不是实际出场清单、出场数量或完整动态生成来源。配置等待不能相加当开场后准确时刻；分支名称不证明触发条件或次数，地图只用既有名义格和已核对的原图中心。当前服务器执行、实际路径与完整敌人面板仍未知。仅局外查阅，不操作游戏、不发送聊天、不改变本局；P3/P2/P1均未完成，识别最后。'
validation='本机30项必要检查与43项原生窗口唯一检查通过；准确主波次/分支跳转、两处非零阅读的真实父刷新、坏源清除/手选恢复、直接关闭/拒绝和父窗口关闭均按实际回执核对。首轮原生因测试视口过高而没有非零滚动范围失败，原脚本和失败原件保留；只缩小验证窗口，43处原断言保持，最终必要与原生均为attempt2，不改生产机制。根代理实际逐张查看7张最终图，截图外观不替代交互证明。七类外部操作零，临时本局/旧计算不变。原项目窗口正常更新可见响应，正常关闭启动区间私人五路径仅摘要核对保持。365全量只作历史，下次到期380；当前索引和要求实际验证，未变25索引测试复用；不可用私样本、1314、实机游戏/聊天不计通过。按本次恢复授权继续至380并完整收尾后暂停。'
nname='verification/sections/371-necessary-attempt2/process.json';wname='verification/sections/371-native-attempt2/actual/window.json';pname='verification/sections/371-native-attempt2/process.json'
n,w,p=map(read,(nname,wname,pname));m=read('verification/sections/371-main-window.json');a=read('verification/sections/371-source-audit.json');v=read('verification/sections/371-root-visual.json')
assert n['passed']and n['methods_ran']==30 and w['passed']and w['qpa']=='windows'and w['qt_exit_code']==0 and w['unique_checks']==43 and w['verification_window_closed']
assert len(w['same_identity_refresh_observations'])==2 and len(w['screenshots'])==7 and len(w['representative_exact_window_jumps'])==2 and all(x==0 for x in w['external_operation_attempts'].values())
assert p['passed']and p['window_receipt_sha256']==sha(wname)
for result in(n,w):
 assert result['source_sha256_before']==result['source_sha256_after']
 for name,h in result['source_sha256_after'].items():assert sha(name)==h,name
assert v['passed']and len(v['final_screenshot_reviews'])==7 and a['ordered_previous608_preserved']and len(a['current_selectors'])==610
assert m['passed']and m['private_entire_normal_close_and_start_interval_unchanged']and m['window_visible_and_responsive']
now=datetime.now(timezone(timedelta(hours=8))).isoformat();pending='<!-- section371-publication-pending -->本地验收完成，普通推送及真实远端核对待完成。'
r={'section':371,'kind':'functional_section','title':title,'new_capability':change,'limitations':[limits],'at_Beijing':now,'branch':'codex/p2-development','necessary_validation':{**pin(nname),'methods_run':n['methods_ran'],'actual_exit':0},'native_windows_validation':{**pin(wname),'process':pin(pname),'unique_checks':w['unique_checks'],'actual_Qt_exit':0,'real_nonzero_refresh_states':2,'actual_MainWindow_entry_and_close_exercised':True,'all_seven_real_external_operations_zero':True},'root_visual_review':pin('verification/sections/371-root-visual.json'),'source_audit':pin('verification/sections/371-source-audit.json'),'original_project_window':pin('verification/sections/371-main-window.json'),'source_sha256':n['source_sha256_after'],'validated_source_sha256':w['source_sha256_after'],'full_suite_rerun':False,'last_full_receipt':'verification/full-365/summary.json','last_full_receipt_is_historical_for_this_changed_source':True,'last_full_validation_sha256':sha('verification/full-365/summary.json'),'next_periodic_full_section':380,'P3_complete':False,'P2_complete':False,'P1_complete':False,'private_state_contents_parsed_copied_or_restored':False,'private_state_hashed_locally_for_preservation_only':True,'private_hashes_published':False,'game_operated':False,'chat_sent':False,'cloud_publication_binding':'enclosing_commit','cloud_published':False,'execution_environment':'local_original_windows_project_venv','local_source_parity_required_for_cloud_publication':True}
(ROOT/'verification/sections/371.json').write_bytes(enc(r));details=change+'\n\n'+validation+'\n\n'+limits+'\n\n'+pending
old_wip=(ROOT/'WORK_IN_PROGRESS.md').read_bytes();(ROOT/'WORK_IN_PROGRESS.md').write_bytes(('## 第371节 + '+title+'\n\n'+now+'。'+details+'\n\n以下为历史记录；当前断点以上述371为准。\n\n').replace('\n','\r\n').encode()+old_wip)
doc('PROJECT_COMPLETED.md','## 第371节 + '+title+'\n\n'+now+'。'+details+'\n\n'+(ROOT/'PROJECT_COMPLETED.md').read_text('utf8'))
s=(ROOT/'AGENTS.md').read_text('utf8');end=s.index('\n## 项目级最高优先要求');note='下一到期完整检查须给304/305两份full320验证脚本显式传入--source-freeze及当轮根声明冻结文件；默认320仅供历史绑定。350原失败与组合复验见verification/full-350/summary.json。312补充窗口采用既有120秒默认，304/305显式传入当轮source-freeze。'
doc('AGENTS.md','## 当前续接 · 第371节 + '+title+'\n\n'+details+'\n\n继续P3；372从实际剩余节点/事件条件、掉落和固定地图缺口接续，未启动。资料条件对照不替代本局实际状态、生成、生效或结算。通用页面不恢复独立版本栏目。用户当前授权继续至380，完整收尾后暂停。只跑本机必要检查；下一全量380，严格低于15%才开始当前完整小节收尾。\n\n'+note+'\n'+s[end:])
s=(ROOT/'PROJECT_REQUIREMENTS.md').read_text('utf8');start=s.index('<!-- current-delivery:start -->');end=s.index('<!-- current-delivery:end -->')+len('<!-- current-delivery:end -->');doc('PROJECT_REQUIREMENTS.md',s[:start]+'<!-- current-delivery:start -->\n## 第371节 + '+title+'\n\n'+details+'\n<!-- current-delivery:end -->'+s[end:])
s=(ROOT/'PROJECT_REQUIREMENTS.md').read_text('utf8');marker='## 当前批次与云端同步';assert s.count(marker)==1;doc('PROJECT_REQUIREMENTS.md',s.replace(marker,marker+'\n\n- 2026-10-26用户明确恢复：从真实370断点继续371–380；每节实际功能、必要验收、当前要求和索引同提交普通推送并核真实远端。380完成到期完整可用范围验收与最终发布后暂停，不启动381。370后的暂停已被本次恢复解除，仅保留为历史。\n',1))
s=(ROOT/'PROJECT_PROGRESS.md').read_text('utf8')
doc('PROJECT_PROGRESS.md',s)
cp=read('DEVELOPMENT_CHECKPOINT.json');assert cp['completed_sections']==370 and cp['next_section']==371

if 371==371:
 cp['historical_before371_batch']={k:cp.get(k) for k in ('batch_start_section','batch_target_section','current_batch','batch_status')}
 cp['batch_start_section']=371;cp['batch_target_section']=380
 cp['current_batch']={'start':371,'end':380,'status':cp['batch_status'],'completed_sections':370,'next_section':371,'next_section_started':False,'batch_closed':False,'target_origin':'direct_user_request_2026-10-26_continue_to380','next_full_validation_after':380}
 cp['policy'].update(development_paused_by_latest_user_request=False,new_functional_sections_paused=False,stop_after_section=380,current_user_batch_target_section=380,batch_target_section=380,current_user_batch_completed=False,latest_user_instruction_receipt='verification/sections/371-preparation/resume-and-scope.json')
 cp['policy'].pop('paused_after_completed_section',None)

for key in('current_section_validation','latest_section_environment','cloud_publication_closeout'):
 if key in cp:cp['historical_before371_'+key]=cp.pop(key)
cp.update(completed_sections=371,latest_functional_section=371,next_section=372,batch_status='P3_SECTION371_LOCAL_ACCEPTED_PUBLICATION_PENDING',next_action='第371节 + '+title+'已本机必要验收；普通推送核对后372接续P3实际剩余缺口，未启动。下次380。',full_validation_due=False)
cp['sections'].append({'number':371,'completion_ref':'p3-section-371','topic':title,'verification':'verification/sections/371.json'});cp['functional_sections_since_latest_requirement'].append(371)
cp['current_section_save']={'section':371,'verification':'verification/sections/371.json','scope':'current_functional_section','binding':'enclosing_commit'};cp['last_verified_cloud_save']['scope']='previous_functional_section'
cp['current_section_validation']={'section':371,'receipt':'verification/sections/371.json','methods_run':n['methods_ran'],'native_isolated_window_checks':w['unique_checks'],'real_nonzero_refresh_states':2,'full_suite_rerun':False,'last_full_receipt':'verification/full-365/summary.json','last_full_receipt_is_historical_for_current_changes':True}
cp['latest_section_environment']={'section':371,'receipt':'verification/sections/371.json','native_windows':validation,'native_game_or_chat_verified':False,'current_section_full_rerun':False,'last_full_receipt':'verification/full-365/summary.json'}
cp['windows_native_validation']=validation;cp['current_batch'].update(status=cp['batch_status'],completed_sections=371,next_section=372,next_section_started=False,receipt='verification/sections/371.json',batch_closed=False)
cp['policy'].update(verification_execution_preference='local_project_environment',avoid_duplicate_cloud_tests=True)
u=read('verification/sections/371-usage.json');cp['policy'].update(current_usage_remaining_percent=u['remaining_percent'],current_usage_receipt='verification/sections/371-usage.json',usage_percent_available=True,usage_wrap_up_triggered=u['triggered'])
cp['current_data_versions'].update({'current_direct_spawn_declarations': 7696, 'current_enemy_references_without_direct_spawn': 110, 'current_enemy_direct_spawn_actual_occurrence_verified': False})

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
doc('CLOUD_HANDOFF.md',(ROOT/'CLOUD_HANDOFF.md').read_text('utf8')+'\n<!-- section371-handoff:start -->\n## 第371节 + '+title+'\n\n'+details+'\n<!-- section371-handoff:end -->\n')
out=ROOT/'verification/sections/371-closeout';out.mkdir();shutil.copyfile(ROOT/'.cache/open_test_window_371.py',out/'execution-main-window.py')
runpy.run_path(str(ROOT/'scripts/update_cloud_index.py'))['update'](ROOT)
(out/'execution-closeout.py').write_bytes(Path(__file__).read_bytes());(out/'applied.json').write_bytes(enc({'section':371,'local_accepted':True,'ordinary_cloud_publication_verified':False,'next372_started':False,'at_Beijing':now}))
print(json.dumps({'section':371,'local_accepted':True,'ordinary_publication_pending':True},ensure_ascii=False))
