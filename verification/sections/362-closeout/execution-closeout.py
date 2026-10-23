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
parent='e2215b38bd109e2f3bce80558b65603f3ddac8e2';assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()==parent
assert subprocess.check_output(['git','branch','--show-current'],cwd=ROOT).decode().strip()=='codex/p2-development'
title='战斗奖励中的基础与满科技经验分别展示'
change='直接更新通用战斗预览的通关基础奖励页，分别列出基础指挥经验、满级生命游戏经验参考和源石锭，不新建版本栏目。完整HTML的明确显示标签和类支持36组独立非零数值；晶矿惊蝗两个同名配置保留各自身份，事件30/39/3与通常追猎0/0/0分开，隐藏第六层/余径基础未知与余径额外随机藏品单列。同源父刷新复用页并保持声明、页签和两非零阅读；换关卡、来源失效及关闭清除旧数值。同步将独立版本更新待办按节点、地图、敌人、本局环境和图片归入通用项目，未知缺口不销项。'
limits='新增依据为后续实际保存PRTS442954完整HTML，不能补冒旧318下载失败原件，也不从合并文本猜拆1013。基础与满科技是两种参考不能相加，玩家实际科技、完整奖励修正、结算次序、事件真实入口/版本选择和实际领取仍未知。conditional_current_experience仍未知，不代用户选择模式。保留318独立模型/reader、原失败和全部旧检查范围；旧依赖损坏仍使新页不可用。没有指挥等级升级算法、实际奖励/库存写入、游戏聊天操作、概率或路线建议；P3/P2/P1未完成。'
validation='本机30项必要测试及49项新原生窗口唯一检查通过；额外执行适配后的318原生29项通过，原参数/源损坏等原场景未删。旧318独立模型/reader测试原语义保留，仅当前生产入口补充362实例与10/13两个分项；旧native当前追猎断言改为两个分项0且实际科技未知，新增资料源全部绑定，技术JSON按标准序列化结构比较不忽略字段。新native准确普通/紧急/源流、两晶矿/入口边界、范围/隐藏层/余径、旧318/新362/当前battle三种真实来源损坏、父刷新两非零阅读及关闭清旧通过。七类真实外部操作零、临时本局与旧计算保持。独立子代理实际查看新native最终七图；318适配原生截图未在本节另逐张视觉复查，不据此声称完整视觉覆盖。原项目测试窗口可见响应，重启全程私人五路径保持。590旧选择器原序保留，新增2个共592；350全量仅改前历史，下次365。当前索引/要求实际校验，未变25索引单测复用；不可用私样本/1314/实机游戏聊天未计通过。继续至370后暂停。'
nname='verification/sections/362-necessary-attempt1/process.json';wname='verification/sections/362-native-attempt1/actual/window.json';pname='verification/sections/362-native-attempt1/process.json'
n,w,p=map(read,(nname,wname,pname));m=read('verification/sections/362-main-window.json');a=read('verification/sections/362-source-audit.json');v=read('verification/sections/362-root-visual.json')
assert n['passed']and n['methods_ran']==30 and w['passed']and w['qpa']=='windows'and w['qt_exit_code']==0 and w['unique_checks']==49 and w['verification_window_closed']
assert len(w['same_identity_refresh_observations'])==2 and len(w['screenshots'])==7 and len(w['actual_readings'])==18 and all(x==0 for x in w['external_operation_attempts'].values())
assert p['passed']and p['window_receipt_sha256']==sha(wname)
for result in(n,w):
 assert result['source_sha256_before']==result['source_sha256_after']
 for name,h in result['source_sha256_after'].items():assert sha(name)==h,name
assert v['passed']and len(v['final_screenshot_reviews'])==7 and a['ordered_previous590_preserved']and len(a['current_selectors'])==592
assert m['passed']and m['private_entire_normal_close_and_start_interval_unchanged']and m['window_visible_and_responsive']
now=datetime.now(timezone(timedelta(hours=8))).isoformat();pending='<!-- section362-publication-pending -->本地验收完成，普通推送及真实远端核对待完成。'
r={'section':362,'kind':'functional_section','title':title,'new_capability':change,'limitations':[limits],'at_Beijing':now,'branch':'codex/p2-development','necessary_validation':{**pin(nname),'methods_run':n['methods_ran'],'actual_exit':0},'native_windows_validation':{**pin(wname),'process':pin(pname),'unique_checks':w['unique_checks'],'actual_Qt_exit':0,'real_nonzero_refresh_states':2,'actual_MainWindow_entry_and_close_exercised':True,'all_seven_real_external_operations_zero':True},'root_visual_review':pin('verification/sections/362-root-visual.json'),'source_audit':pin('verification/sections/362-source-audit.json'),'original_project_window':pin('verification/sections/362-main-window.json'),'source_sha256':n['source_sha256_after'],'validated_source_sha256':w['source_sha256_after'],'full_suite_rerun':False,'last_full_receipt':'verification/full-350/summary.json','last_full_receipt_is_historical_for_this_changed_source':True,'last_full_validation_sha256':sha('verification/full-350/summary.json'),'next_periodic_full_section':365,'P3_complete':False,'P2_complete':False,'P1_complete':False,'private_state_contents_parsed_copied_or_restored':False,'private_state_hashed_locally_for_preservation_only':True,'private_hashes_published':False,'game_operated':False,'chat_sent':False,'cloud_publication_binding':'enclosing_commit','cloud_published':False,'execution_environment':'local_original_windows_project_venv','local_source_parity_required_for_cloud_publication':True}
(ROOT/'verification/sections/362.json').write_bytes(enc(r));details=change+'\n\n'+validation+'\n\n'+limits+'\n\n'+pending
old_wip=(ROOT/'WORK_IN_PROGRESS.md').read_bytes();(ROOT/'WORK_IN_PROGRESS.md').write_bytes(('## 第362节 + '+title+'\n\n'+now+'。'+details+'\n\n以下为历史记录；当前断点以上述362为准。\n\n').replace('\n','\r\n').encode()+old_wip)
doc('PROJECT_COMPLETED.md','## 第362节 + '+title+'\n\n'+now+'。'+details+'\n\n'+(ROOT/'PROJECT_COMPLETED.md').read_text('utf8'))
s=(ROOT/'AGENTS.md').read_text('utf8');end=s.index('\n## 项目级最高优先要求');note='下一到期完整检查须给304/305两份full320验证脚本显式传入--source-freeze及当轮根声明冻结文件；默认320仅供历史绑定。350原失败与组合复验见verification/full-350/summary.json。312补充窗口采用既有120秒默认，304/305显式传入当轮source-freeze。'
doc('AGENTS.md','## 当前续接 · 第362节 + '+title+'\n\n'+details+'\n\n继续P3；363从实际剩余节点/事件条件、掉落和固定地图缺口接续，未启动。资料条件对照不替代本局实际状态、生成、生效或结算。通用页面不恢复独立版本栏目。用户当前授权继续至370，完整收尾后暂停。只跑本机必要检查；下一全量365，严格低于15%才开始当前完整小节收尾。\n\n'+note+'\n'+s[end:])
s=(ROOT/'PROJECT_REQUIREMENTS.md').read_text('utf8');start=s.index('<!-- current-delivery:start -->');end=s.index('<!-- current-delivery:end -->')+len('<!-- current-delivery:end -->');doc('PROJECT_REQUIREMENTS.md',s[:start]+'<!-- current-delivery:start -->\n## 第362节 + '+title+'\n\n'+details+'\n<!-- current-delivery:end -->'+s[end:])
s=(ROOT/'PROJECT_PROGRESS.md').read_text('utf8')
old='当前非零经验两种显示模式的原始依据、';assert s.count(old)==1;s=s.replace(old,'')
oldrow=next(row for row in s.splitlines() if row.startswith('| 3 | 国服10月拓展的功能迁移 |'))
parts=oldrow.split('|')[3].strip().split('；');assert len(parts)==6
scopes={'固定战斗地图映射':'；'.join(parts[:2]),'敌人面板与机制':parts[2],'节点事件与掉落':parts[3],'本局环境':parts[4],'图片与分类资料缺口':parts[5].replace('。旧计算继续明示旧版本范围','')}
s=s.replace(oldrow+'\n','')
for subject,scope in scopes.items():
 row=next(row for row in s.splitlines() if row.startswith('|') and len(row.split('|'))>3 and row.split('|')[2].strip()==subject)
 fields=row.split('|');fields[3]=' '+scope+'；'+fields[3].strip()+' ';s=s.replace(row,'|'.join(fields))
(ROOT/'verification/sections/362-todo-merge.json').write_bytes(enc({'section':362,'documentation_maintenance_only':True,'original_remaining_row':oldrow,'remaining_scopes_rehomed_to':scopes,'mechanisms_marked_complete_by_reorganization':False,'old_calculation_version_boundary_retained_in_requirements':True}))
doc('PROJECT_PROGRESS.md',s)
cp=read('DEVELOPMENT_CHECKPOINT.json');assert cp['completed_sections']==361 and cp['next_section']==362
for key in('current_section_validation','latest_section_environment','cloud_publication_closeout'):
 if key in cp:cp['historical_before362_'+key]=cp.pop(key)
cp.update(completed_sections=362,latest_functional_section=362,next_section=363,batch_status='P3_SECTION362_LOCAL_ACCEPTED_PUBLICATION_PENDING',next_action='第362节 + '+title+'已本机必要验收；普通推送核对后363接续P3实际剩余缺口，未启动。下次365。',full_validation_due=False)
cp['sections'].append({'number':362,'completion_ref':'p3-section-362','topic':title,'verification':'verification/sections/362.json'});cp['functional_sections_since_latest_requirement'].append(362)
cp['current_section_save']={'section':362,'verification':'verification/sections/362.json','scope':'current_functional_section','binding':'enclosing_commit'};cp['last_verified_cloud_save']['scope']='previous_functional_section'
cp['current_section_validation']={'section':362,'receipt':'verification/sections/362.json','methods_run':n['methods_ran'],'native_isolated_window_checks':w['unique_checks'],'real_nonzero_refresh_states':2,'full_suite_rerun':False,'last_full_receipt':'verification/full-350/summary.json','last_full_receipt_is_historical_for_current_changes':True}
cp['latest_section_environment']={'section':362,'receipt':'verification/sections/362.json','native_windows':validation,'native_game_or_chat_verified':False,'current_section_full_rerun':False,'last_full_receipt':'verification/full-350/summary.json'}
cp['windows_native_validation']=validation;cp['current_batch'].update(status=cp['batch_status'],completed_sections=362,next_section=363,next_section_started=False,receipt='verification/sections/362.json',batch_closed=False)
cp['policy'].update(verification_execution_preference='local_project_environment',avoid_duplicate_cloud_tests=True)
cp['current_data_versions'].update({'current_settlement_mode_pairs': 36, 'current_settlement_named_special_rows': 18, 'current_settlement_docs_revision': 442954, 'current_actual_player_technology_verified': False, 'current_actual_reward_total_verified': False})
cp['current_available_full_validation']['historical_for_current_changed_source']=True
cp['current_available_full_validation']['current_worktree_validation_authority']=False
cp['last_full_validation']['historical_for_current_changed_source']=True
(ROOT/'DEVELOPMENT_CHECKPOINT.json').write_bytes(enc(cp))
doc('CLOUD_HANDOFF.md',(ROOT/'CLOUD_HANDOFF.md').read_text('utf8')+'\n<!-- section362-handoff:start -->\n## 第362节 + '+title+'\n\n'+details+'\n<!-- section362-handoff:end -->\n')
out=ROOT/'verification/sections/362-closeout';out.mkdir();shutil.copyfile(ROOT/'.cache/open_test_window_362.py',out/'execution-main-window.py')
runpy.run_path(str(ROOT/'scripts/update_cloud_index.py'))['update'](ROOT)
(out/'execution-closeout.py').write_bytes(Path(__file__).read_bytes());(out/'applied.json').write_bytes(enc({'section':362,'local_accepted':True,'ordinary_cloud_publication_verified':False,'next363_started':False,'at_Beijing':now}))
print(json.dumps({'section':362,'local_accepted':True,'ordinary_publication_pending':True},ensure_ascii=False))
