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
parent='23215171e35900a1b75aebb44e66d4bf657f267a';assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()==parent
assert subprocess.check_output(['git','branch','--show-current'],cwd=ROOT).decode().strip()=='codex/p2-development'
title='汉科、相关敌人与烟雾弹的完整机制查阅'
change='普通敌人页可直接查阅汉科、大总统和烟雾弹的完整机制，并在准确关联实体之间跳转；六份配置、五个原始关卡的12个准确敌人引用分别保留身份。七份机制卡和四份图鉴原文/社区修正说明分开显示，照明弹解除范围的修正明确可见；哀悼铁腕的本关覆写不借用通用说明。相同目标刷新保留主题和两处阅读，来源失效清旧并提示手选恢复，切换敌人或页面时清理所属窗口。'
limits='原始图鉴与社区修正分别保存，不把照明弹视为清除全场所有隐匿/迷彩。当前实际触发时刻、持续时间、解除状态、烟雾位置及数量和最终敌人面板仍未知；关卡原参数仅按已证范围说明，不把未解析参数翻译成实际时钟。关卡中的未定义覆写不替换真实敌人身份，相关实体也不冒充同时登场。只提供固定资料与局外查阅，不加入伤害公式、不操作游戏或发聊天、不更改本局。P3/P2/P1仍未完成，识别最后。'
validation='本机28项必要测试、46项原生窗口检查与6图独立实际审阅通过，含12准确敌人引用、36次实体/主题读取、父刷新两非零阅读、真实来源失效清旧与手选恢复、所属窗口清理。首轮313旧提示断言失败原件完整保留；修正为分别核对通用资料范围和旧计算限制，不删除边界断言、不增加功能节。修正后的第2轮到期365完整可用范围真实运行：6441项离线测试，6362项通过，历史/声明跳过73；原52保存状态与完整4283项读回、862修订断言及156文本请求保留，80组P3窗口与85必需位置完整终止。原当前窗口可用29项通过，符号链接操作是否通过依据真实原30项结果单列；不可用不冒充通过。全量截图逐路径核对，并仅对相同字节复用实际视觉审阅，其余实际看图；外观不替代语义测试。598有序选择器与完整来源无缩减。普通测试窗正常更新可见响应，正常重启期间私人五路径只校验摘要保持；不声称整个全量期间五路径都已比较。当前要求/索引实际校验，原未变25索引单测复用。实际运行与图像证明见全量摘要；游戏/聊天、私有历史样本和缺失平台不计通过。继续至370后暂停，下一周期全量380。 外观检查另发现既有干员页的无关灰色专属工具按钮，正式源码也只对这些按钮设可用性而未隐藏；已保留为界面未完成项，不因本批资料整合而销项。 原30项中的符号链接操作因实际WinError1314缺少权限不可执行，其余29项与独立29项分别保留，不叠加计数，也不声称完整30项通过。'
nname='verification/sections/365-necessary-attempt2/process.json';wname='verification/sections/365-native-attempt2/actual/window.json';pname='verification/sections/365-native-attempt2/process.json'
n,w,p=map(read,(nname,wname,pname));m=read('verification/sections/365-main-window.json');a=read('verification/sections/365-source-audit.json');v=read('verification/sections/365-root-visual.json')
assert n['passed']and n['methods_ran']==28 and w['passed']and w['qpa']=='windows'and w['qt_exit_code']==0 and w['unique_checks']==46 and w['verification_window_closed']
assert len(w['same_identity_refresh_observations'])==2 and len(w['screenshots'])==6 and len(w['actual_readings'])==36 and all(x==0 for x in w['external_operation_attempts'].values())
assert p['passed']and p['window_receipt_sha256']==sha(wname)
for result in(n,w):
 assert result['source_sha256_before']==result['source_sha256_after']
 for name,h in result['source_sha256_after'].items():assert sha(name)==h,name
assert v['passed']and len(v['final_screenshot_reviews'])==6 and a['ordered_previous596_preserved']and len(a['current_selectors'])==598
assert m['passed']and m['private_entire_normal_close_and_start_interval_unchanged']and m['window_visible_and_responsive']
now=datetime.now(timezone(timedelta(hours=8))).isoformat();pending='<!-- section365-publication-pending -->本地验收完成，普通推送及真实远端核对待完成。'
r={'section':365,'kind':'functional_section','title':title,'new_capability':change,'limitations':[limits],'at_Beijing':now,'branch':'codex/p2-development','necessary_validation':{**pin(nname),'methods_run':n['methods_ran'],'actual_exit':0},'native_windows_validation':{**pin(wname),'process':pin(pname),'unique_checks':w['unique_checks'],'actual_Qt_exit':0,'real_nonzero_refresh_states':2,'actual_MainWindow_entry_and_close_exercised':True,'all_seven_real_external_operations_zero':True},'root_visual_review':pin('verification/sections/365-root-visual.json'),'source_audit':pin('verification/sections/365-source-audit.json'),'original_project_window':pin('verification/sections/365-main-window.json'),'source_sha256':n['source_sha256_after'],'validated_source_sha256':w['source_sha256_after'],'full_suite_rerun':True,'last_full_receipt':'verification/full-365/summary.json','last_full_receipt_is_historical_for_this_changed_source':False,'last_full_validation_sha256':sha('verification/full-365/summary.json'),'next_periodic_full_section':380,'P3_complete':False,'P2_complete':False,'P1_complete':False,'private_state_contents_parsed_copied_or_restored':False,'private_state_hashed_locally_for_preservation_only':True,'private_hashes_published':False,'game_operated':False,'chat_sent':False,'cloud_publication_binding':'enclosing_commit','cloud_published':False,'execution_environment':'local_original_windows_project_venv','local_source_parity_required_for_cloud_publication':True}
(ROOT/'verification/sections/365.json').write_bytes(enc(r));details=change+'\n\n'+validation+'\n\n'+limits+'\n\n'+pending
old_wip=(ROOT/'WORK_IN_PROGRESS.md').read_bytes();(ROOT/'WORK_IN_PROGRESS.md').write_bytes(('## 第365节 + '+title+'\n\n'+now+'。'+details+'\n\n以下为历史记录；当前断点以上述365为准。\n\n').replace('\n','\r\n').encode()+old_wip)
doc('PROJECT_COMPLETED.md','## 第365节 + '+title+'\n\n'+now+'。'+details+'\n\n'+(ROOT/'PROJECT_COMPLETED.md').read_text('utf8'))
s=(ROOT/'AGENTS.md').read_text('utf8');end=s.index('\n## 项目级最高优先要求');note='后续到期完整检查仍须给304/305两份full320验证脚本显式传入--source-freeze及当轮根声明冻结文件；默认320仅供历史绑定。350原失败与组合复验见verification/full-350/summary.json。312补充窗口采用既有120秒默认，304/305显式传入当轮source-freeze。'
doc('AGENTS.md','## 当前续接 · 第365节 + '+title+'\n\n'+details+'\n\n继续P3；366从实际剩余节点/事件条件、掉落和固定地图缺口接续，未启动。资料条件对照不替代本局实际状态、生成、生效或结算。通用页面不恢复独立版本栏目。用户当前授权继续至370，完整收尾后暂停。只跑本机必要检查；下一全量380，严格低于15%才开始当前完整小节收尾。\n\n'+note+'\n'+s[end:])
s=(ROOT/'PROJECT_REQUIREMENTS.md').read_text('utf8');start=s.index('<!-- current-delivery:start -->');end=s.index('<!-- current-delivery:end -->')+len('<!-- current-delivery:end -->');doc('PROJECT_REQUIREMENTS.md',s[:start]+'<!-- current-delivery:start -->\n## 第365节 + '+title+'\n\n'+details+'\n<!-- current-delivery:end -->'+s[end:])
s=(ROOT/'PROJECT_PROGRESS.md').read_text('utf8')
old='功能跑通后统一优化界面；';assert s.count(old)==1;s=s.replace(old,'功能跑通后统一优化界面；移除其他干员仍能看到的灰色机械师时序等专属工具按钮，保留已正确隐藏的培养/技能条件表单；')
doc('PROJECT_PROGRESS.md',s)
cp=read('DEVELOPMENT_CHECKPOINT.json');assert cp['completed_sections']==364 and cp['next_section']==365
for key in('current_section_validation','latest_section_environment','cloud_publication_closeout'):
 if key in cp:cp['historical_before365_'+key]=cp.pop(key)
cp.update(completed_sections=365,latest_functional_section=365,next_section=366,batch_status='P3_SECTION365_LOCAL_ACCEPTED_PUBLICATION_PENDING',next_action='第365节 + '+title+'已本机必要验收；普通推送核对后366接续P3实际剩余缺口，未启动。下次380。',full_validation_due=False)
cp['sections'].append({'number':365,'completion_ref':'p3-section-365','topic':title,'verification':'verification/sections/365.json'});cp['functional_sections_since_latest_requirement'].append(365)
cp['current_section_save']={'section':365,'verification':'verification/sections/365.json','scope':'current_functional_section','binding':'enclosing_commit'};cp['last_verified_cloud_save']['scope']='previous_functional_section'
cp['current_section_validation']={'section':365,'receipt':'verification/sections/365.json','methods_run':n['methods_ran'],'native_isolated_window_checks':w['unique_checks'],'real_nonzero_refresh_states':2,'full_suite_rerun':True,'last_full_receipt':'verification/full-365/summary.json','last_full_receipt_is_historical_for_current_changes':False}
cp['latest_section_environment']={'section':365,'receipt':'verification/sections/365.json','native_windows':validation,'native_game_or_chat_verified':False,'current_section_full_rerun':True,'last_full_receipt':'verification/full-365/summary.json'}
cp['windows_native_validation']=validation;cp['current_batch'].update(status=cp['batch_status'],completed_sections=365,next_section=366,next_section_started=False,receipt='verification/sections/365.json',batch_closed=False)
cp['policy'].update(verification_execution_preference='local_project_environment',avoid_duplicate_cloud_tests=True)
u=read('verification/sections/365-usage-closeout.json');cp['policy'].update(current_usage_remaining_percent=u['remaining_percent'],current_usage_receipt='verification/sections/365-usage-closeout.json',usage_percent_available=True,usage_wrap_up_triggered=u['triggered'])
cp['current_data_versions'].update({'current_hanko_configurations': 6, 'current_hanko_exact_enemy_references': 12, 'current_hanko_full_document_cards': 7, 'current_hanko_actual_battle_state_verified': False})

f=read('verification/full-365/summary.json');assert f['available_checks_passed']and f['scope_not_reduced']
cp['current_available_full_validation']={
 'section':365,'receipt':'verification/full-365/summary.json','available_scope_passed':True,
 'actual_validation_attempt':f['actual_validation_attempt'],
 'single_available_scope_execution_all_green':f['single_available_scope_execution_all_green'],
 'actual_root_controller_exit':f['actual_root_controller_exit'],
 'validation_composition':f['validation_composition'],
 'source_freeze':f['source_freeze'],'source_freeze_sha256':f['source_freeze_sha256'],
 'native_windows_game_chat_verified':False,
 'historical_for_current_changed_source':False,
 'current_worktree_validation_authority':not False}
cp['last_full_validation']={'after_section':365,'receipt':'verification/full-365/summary.json',
 'available_checks_passed':True,'complete_repository_validation':False,'scope_not_reduced':True,
 'source_freeze':f['source_freeze'],'source_freeze_sha256':f['source_freeze_sha256'],
 'historical_for_current_changed_source':False}
cp['next_full_validation_after']=380
for key in ('validation_cadence','policy','current_batch','current_batch_commit_policy'):
 if isinstance(cp.get(key),dict):cp[key]['next_full_validation_after']=380
cp['current_batch']['next_full_validation_after']=380
cp['current_section_validation']['full_suite_rerun']=not False
cp['latest_section_environment']['current_section_full_rerun']=not False

(ROOT/'DEVELOPMENT_CHECKPOINT.json').write_bytes(enc(cp))
doc('CLOUD_HANDOFF.md',(ROOT/'CLOUD_HANDOFF.md').read_text('utf8')+'\n<!-- section365-handoff:start -->\n## 第365节 + '+title+'\n\n'+details+'\n<!-- section365-handoff:end -->\n')
out=ROOT/'verification/sections/365-closeout';out.mkdir();shutil.copyfile(ROOT/'.cache/open_test_window_365.py',out/'execution-main-window.py')
runpy.run_path(str(ROOT/'scripts/update_cloud_index.py'))['update'](ROOT)
(out/'execution-closeout.py').write_bytes(Path(__file__).read_bytes());(out/'applied.json').write_bytes(enc({'section':365,'local_accepted':True,'ordinary_cloud_publication_verified':False,'next366_started':False,'at_Beijing':now}))
print(json.dumps({'section':365,'local_accepted':True,'ordinary_publication_pending':True},ensure_ascii=False))
