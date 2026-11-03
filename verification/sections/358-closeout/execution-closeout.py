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
parent='e8c842b4f20146a794a067ee12cf439f4ccd2fa0';assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()==parent
assert subprocess.check_output(['git','branch','--show-current'],cwd=ROOT).decode().strip()=='codex/p2-development'
title='秘境雾色、九种区域规则与原节点刷新表的准确入口'
change='通用节点事件页加入秘境规则目录：可分别查看六种雾色、九份规则、十九份准确区域和三份原节点刷新表。红雾保持四个候选，不按编号推断规则；只有相关规则显示主层、移动/通过与商店完成条件。蓝雾已完成商店例外和橙雾社区补充与原文分开显示。准确场景、区域和地图标志可反向进入对应资料，原雾色对话及地图标志说明可直接打开；刷新保持阅读与本页声明，失效清旧内容并要求手动重选，换页/换项关闭所属原文窗口。'
limits='依据固定国服原表及已保存的PRTS442947/433770原文核对。十九份区域不推定为当前同时存在的秘境；同名或编号不证明主层、雾色、规则与刷新表的对应。原表只列节点类型，不是具体事件全集，不能把同类型的所有事件都列为本区可发生。条件对照不证明当前进入、刷新、消耗、奖励或资格，地图标志不冒充藏品。P3/P2/P1仍未完成，无生成概率、路线建议或数值/本局状态写入；游戏和聊天未操作。'
validation='最终本机32项必要测试及60项原生窗口唯一检查通过，实际逐项查看6雾色、9规则、19区域，验证准确原文/反向入口、相关控件、两组非零阅读经父刷新保持、真实成员损坏与手动恢复、全部所属窗口树关闭；七类真实外部操作为零，临时本局和旧计算上下文保持。首轮32项中一项因提示语未使用断言要求的“具体事件”用词失败；保留首轮原回执，在明确提示语后完整重验32/60，没有改机制。最终七张截图由独立子代理实际逐张查看并据实记录审阅者。原项目测试窗口更新且可见响应，完整关闭/启动期间私人五路径保持。582旧选择器原序保留，新增2个共584；350全量仅为改前历史，下一定期365。索引25项未变旧单测复用，当前要求和索引实际校验；不可用私样本/1314/游戏聊天不计通过。按授权继续至370后暂停。'
nname='verification/sections/358-necessary-attempt2/process.json';wname='verification/sections/358-native-attempt2/actual/window.json';pname='verification/sections/358-native-attempt2/process.json'
n,w,p=map(read,(nname,wname,pname));m=read('verification/sections/358-main-window.json');a=read('verification/sections/358-source-audit.json');v=read('verification/sections/358-root-visual.json')
assert n['passed']and n['methods_ran']==32 and w['passed']and w['qpa']=='windows'and w['qt_exit_code']==0 and w['unique_checks']==60 and w['verification_window_closed']
assert len(w['same_identity_refresh_observations'])==2 and len(w['screenshots'])==7 and len(w['actual_readings'])==34 and all(x==0 for x in w['external_operation_attempts'].values())
assert p['passed']and p['window_receipt_sha256']==sha(wname)
for result in(n,w):
 assert result['source_sha256_before']==result['source_sha256_after']
 for name,h in result['source_sha256_after'].items():assert sha(name)==h,name
assert v['passed']and len(v['final_screenshot_reviews'])==7 and a['ordered_previous582_preserved']and len(a['current_selectors'])==584
assert m['passed']and m['private_entire_normal_close_and_start_interval_unchanged']and m['window_visible_and_responsive']
now=datetime.now(timezone(timedelta(hours=8))).isoformat();pending='<!-- section358-publication-pending -->本地验收完成，普通推送及真实远端核对待完成。'
r={'section':358,'kind':'functional_section','title':title,'new_capability':change,'limitations':[limits],'at_Beijing':now,'branch':'codex/p2-development','necessary_validation':{**pin(nname),'methods_run':n['methods_ran'],'actual_exit':0},'native_windows_validation':{**pin(wname),'process':pin(pname),'unique_checks':w['unique_checks'],'actual_Qt_exit':0,'real_nonzero_refresh_states':2,'actual_MainWindow_entry_and_close_exercised':True,'all_seven_real_external_operations_zero':True},'root_visual_review':pin('verification/sections/358-root-visual.json'),'source_audit':pin('verification/sections/358-source-audit.json'),'original_project_window':pin('verification/sections/358-main-window.json'),'source_sha256':n['source_sha256_after'],'validated_source_sha256':w['source_sha256_after'],'full_suite_rerun':False,'last_full_receipt':'verification/full-350/summary.json','last_full_receipt_is_historical_for_this_changed_source':True,'last_full_validation_sha256':sha('verification/full-350/summary.json'),'next_periodic_full_section':365,'P3_complete':False,'P2_complete':False,'P1_complete':False,'private_state_contents_parsed_copied_or_restored':False,'private_state_hashed_locally_for_preservation_only':True,'private_hashes_published':False,'game_operated':False,'chat_sent':False,'cloud_publication_binding':'enclosing_commit','cloud_published':False,'execution_environment':'local_original_windows_project_venv','local_source_parity_required_for_cloud_publication':True}
(ROOT/'verification/sections/358.json').write_bytes(enc(r));details=change+'\n\n'+validation+'\n\n'+limits+'\n\n'+pending
old_wip=(ROOT/'WORK_IN_PROGRESS.md').read_bytes();(ROOT/'WORK_IN_PROGRESS.md').write_bytes(('## 第358节 + '+title+'\n\n'+now+'。'+details+'\n\n以下为历史记录；当前断点以上述358为准。\n\n').replace('\n','\r\n').encode()+old_wip)
doc('PROJECT_COMPLETED.md','## 第358节 + '+title+'\n\n'+now+'。'+details+'\n\n'+(ROOT/'PROJECT_COMPLETED.md').read_text('utf8'))
s=(ROOT/'AGENTS.md').read_text('utf8');end=s.index('\n## 项目级最高优先要求');note='下一到期完整检查须给304/305两份full320验证脚本显式传入--source-freeze及当轮根声明冻结文件；默认320仅供历史绑定。350原失败与组合复验见verification/full-350/summary.json。312补充窗口采用既有120秒默认，304/305显式传入当轮source-freeze。'
doc('AGENTS.md','## 当前续接 · 第358节 + '+title+'\n\n'+details+'\n\n继续P3；359从实际剩余节点/事件条件、掉落和固定地图缺口接续，未启动。资料条件对照不替代本局实际状态、生成、生效或结算。通用页面不恢复独立版本栏目。用户当前授权继续至370，完整收尾后暂停。只跑本机必要检查；下一全量365，严格低于15%才开始当前完整小节收尾。\n\n'+note+'\n'+s[end:])
s=(ROOT/'PROJECT_REQUIREMENTS.md').read_text('utf8');start=s.index('<!-- current-delivery:start -->');end=s.index('<!-- current-delivery:end -->')+len('<!-- current-delivery:end -->');doc('PROJECT_REQUIREMENTS.md',s[:start]+'<!-- current-delivery:start -->\n## 第358节 + '+title+'\n\n'+details+'\n<!-- current-delivery:end -->'+s[end:])
s=(ROOT/'PROJECT_PROGRESS.md').read_text('utf8')
old='同步完成标志、住民/迷雾、行动力与加工品的实际节点状态规则';assert s.count(old)==1;s=s.replace(old,'九规则/六雾色与十九秘境原区域的真实实例绑定、当前刷新结果及具体事件成员；同步完成标志、住民/迷雾、行动力与加工品的实际节点状态规则')
doc('PROJECT_PROGRESS.md',s)
cp=read('DEVELOPMENT_CHECKPOINT.json');assert cp['completed_sections']==357 and cp['next_section']==358
for key in('current_section_validation','latest_section_environment','cloud_publication_closeout'):
 if key in cp:cp['historical_before358_'+key]=cp.pop(key)
cp.update(completed_sections=358,latest_functional_section=358,next_section=359,batch_status='P3_SECTION358_LOCAL_ACCEPTED_PUBLICATION_PENDING',next_action='第358节 + '+title+'已本机必要验收；普通推送核对后359接续P3实际剩余缺口，未启动。下次365。',full_validation_due=False)
cp['sections'].append({'number':358,'completion_ref':'p3-section-358','topic':title,'verification':'verification/sections/358.json'});cp['functional_sections_since_latest_requirement'].append(358)
cp['current_section_save']={'section':358,'verification':'verification/sections/358.json','scope':'current_functional_section','binding':'enclosing_commit'};cp['last_verified_cloud_save']['scope']='previous_functional_section'
cp['current_section_validation']={'section':358,'receipt':'verification/sections/358.json','methods_run':n['methods_ran'],'native_isolated_window_checks':w['unique_checks'],'real_nonzero_refresh_states':2,'full_suite_rerun':False,'last_full_receipt':'verification/full-350/summary.json','last_full_receipt_is_historical_for_current_changes':True}
cp['latest_section_environment']={'section':358,'receipt':'verification/sections/358.json','native_windows':validation,'native_game_or_chat_verified':False,'current_section_full_rerun':False,'last_full_receipt':'verification/full-350/summary.json'}
cp['windows_native_validation']=validation;cp['current_batch'].update(status=cp['batch_status'],completed_sections=358,next_section=359,next_section_started=False,receipt='verification/sections/358.json',batch_closed=False)
cp['policy'].update(verification_execution_preference='local_project_environment',avoid_duplicate_cloud_tests=True)
cp['current_data_versions'].update({'current_portal_rules': 9, 'current_portal_fogs': 6, 'current_portal_regions': 19, 'current_portal_refresh_tables': 3, 'current_portal_actual_instance_verified': False})
cp['current_available_full_validation']['historical_for_current_changed_source']=True
cp['current_available_full_validation']['current_worktree_validation_authority']=False
cp['last_full_validation']['historical_for_current_changed_source']=True
(ROOT/'DEVELOPMENT_CHECKPOINT.json').write_bytes(enc(cp))
doc('CLOUD_HANDOFF.md',(ROOT/'CLOUD_HANDOFF.md').read_text('utf8')+'\n<!-- section358-handoff:start -->\n## 第358节 + '+title+'\n\n'+details+'\n<!-- section358-handoff:end -->\n')
out=ROOT/'verification/sections/358-closeout';out.mkdir();shutil.copyfile(ROOT/'.cache/open_test_window_358.py',out/'execution-main-window.py')
runpy.run_path(str(ROOT/'scripts/update_cloud_index.py'))['update'](ROOT)
(out/'execution-closeout.py').write_bytes(Path(__file__).read_bytes());(out/'applied.json').write_bytes(enc({'section':358,'local_accepted':True,'ordinary_cloud_publication_verified':False,'next359_started':False,'at_Beijing':now}))
print(json.dumps({'section':358,'local_accepted':True,'ordinary_publication_pending':True},ensure_ascii=False))
