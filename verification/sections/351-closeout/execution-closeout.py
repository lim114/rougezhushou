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
parent='9cdda91f070e030eed1d7b9f655585868138c4fd';assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()==parent
assert subprocess.check_output(['git','branch','--show-current'],cwd=ROOT).decode().strip()=='codex/p2-development'
title='敌人行动方式、漏敌影响与控制抗性的中文预览'
change='当前版本全部固定关卡的敌人资料加入行动方式、普通攻击途径、图鉴攻击类型、抵达终点的生命扣除声明、是否计入敌人数及明确的控制免疫。仅按精确等级的明确赋值逐级继承并叠加关卡覆盖；独立构造只读自身声明，未定义占位值不补成可控或地面。地面行动与不可阻挡机制并列，普通攻击途径为空仍保留技能行为。战栗、诱导与缚地采用文献准确名称，显式免疫为否不宣称所有阶段可控制。沿用实际普通/精英/领袖分支、图片与中文阅读页，刷新保留已选敌人、两组非零阅读和页签；资料损坏清空旧内容，恢复后重新选择。'
limits='采用bee3国服10月16日原关卡和敌人资料及固定PRTS异常效果文献。固定声明不能证明当前服务器、阶段、技能、实际控制结果、最终漏敌扣点或总敌人数。当前保密等级/分队/阶段的完整数值修正仍待迁移，生命攻击防御法抗继续标未知，不显示白值替代。独立构造不借数据库图鉴或同名原型；未取得精确数据库等级时仅采用本关明确覆盖。没有加入游戏操作、聊天、实时战斗分析、路线推荐或生成概率；P3/P2/P1均未完成，识别最后。'
validation='本机24项必要测试及23项原生窗口唯一检查通过，验证四份真实关卡的独立构造、未定义占位、无普通攻击但有特殊行为、零扣点与不计总数、地面但不可阻挡等边界。通过真实MainWindow版本页打开关卡，核对两组非零阅读状态经父刷新保持、原源字节损坏清除、恢复手选和主窗关闭整树；七类真实外部操作零，临时本局及旧计算上下文不变。五张实际截图主代理逐张复查；原项目测试窗已正常更新并可见响应，完整正常关闭/启动区间私人五路径保持。569个旧选择器顺序保留，新加2个，当前571。350完整可用验收保留为本节改动前的历史证据，本节未重复跑全量，下一定期365；符号链接1314、历史Windows/私有样本与实机游戏聊天未冒称通过。索引实现未改，复用25项历史单测，实际校验本节要求/索引绑定。用户本次继续至370，完整收尾后暂停。'
nname='verification/sections/351-necessary-attempt1/process.json';wname='verification/sections/351-native-attempt1/actual/window.json';pname='verification/sections/351-native-attempt1/process.json'
n,w,p=map(read,(nname,wname,pname));m=read('verification/sections/351-main-window.json');a=read('verification/sections/351-source-audit.json');v=read('verification/sections/351-root-visual.json')
assert n['passed']and n['methods_ran']==24 and w['passed']and w['qpa']=='windows'and w['qt_exit_code']==0 and w['unique_checks']==23 and w['verification_window_closed']
assert len(w['same_identity_refresh_observations'])==2 and len(w['screenshots'])==5 and len(w['actual_readings'])==4 and all(x==0 for x in w['external_operation_attempts'].values())
assert p['passed']and p['window_receipt_sha256']==sha(wname)
for result in(n,w):
 assert result['source_sha256_before']==result['source_sha256_after']
 for name,h in result['source_sha256_after'].items():assert sha(name)==h,name
assert v['passed']and len(v['final_screenshot_reviews'])==5 and a['ordered_previous569_preserved']and len(a['current_selectors'])==571
assert m['passed']and m['private_entire_normal_close_and_start_interval_unchanged']and m['window_visible_and_responsive']
now=datetime.now(timezone(timedelta(hours=8))).isoformat();pending='<!-- section351-publication-pending -->本地验收完成，普通推送及真实远端核对待完成。'
r={'section':351,'kind':'functional_section','title':title,'new_capability':change,'limitations':[limits],'at_Beijing':now,'branch':'codex/p2-development','necessary_validation':{**pin(nname),'methods_run':n['methods_ran'],'actual_exit':0},'native_windows_validation':{**pin(wname),'process':pin(pname),'unique_checks':w['unique_checks'],'actual_Qt_exit':0,'enemy_boundary_subjects':4,'explicit_immunity_fields':11,'real_nonzero_refresh_states':2,'actual_MainWindow_entry_and_close_exercised':True,'all_seven_real_external_operations_zero':True},'root_visual_review':pin('verification/sections/351-root-visual.json'),'source_audit':pin('verification/sections/351-source-audit.json'),'original_project_window':pin('verification/sections/351-main-window.json'),'source_sha256':n['source_sha256_after'],'validated_source_sha256':w['source_sha256_after'],'full_suite_rerun':False,'last_full_receipt':'verification/full-350/summary.json','last_full_receipt_is_historical_for_this_changed_source':True,'last_full_validation_sha256':sha('verification/full-350/summary.json'),'next_periodic_full_section':365,'P3_complete':False,'P2_complete':False,'P1_complete':False,'private_state_contents_parsed_copied_or_restored':False,'private_state_hashed_locally_for_preservation_only':True,'private_hashes_published':False,'game_operated':False,'chat_sent':False,'cloud_publication_binding':'enclosing_commit','cloud_published':False,'execution_environment':'local_original_windows_project_venv','local_source_parity_required_for_cloud_publication':True}
(ROOT/'verification/sections/351.json').write_bytes(enc(r));details=change+'\n\n'+validation+'\n\n'+limits+'\n\n'+pending
old_wip=(ROOT/'WORK_IN_PROGRESS.md').read_bytes();(ROOT/'WORK_IN_PROGRESS.md').write_bytes(('## 第351节 + '+title+'\n\n'+now+'。'+details+'\n\n以下为历史记录；当前断点以上述351为准。\n\n').replace('\n','\r\n').encode()+old_wip)
doc('PROJECT_COMPLETED.md','## 第351节 + '+title+'\n\n'+now+'。'+details+'\n\n'+(ROOT/'PROJECT_COMPLETED.md').read_text('utf8'))
s=(ROOT/'AGENTS.md').read_text('utf8');end=s.index('\n## 项目级最高优先要求');note='下一到期完整检查须给304/305两份full320验证脚本显式传入--source-freeze及当轮根声明冻结文件；默认320仅供历史绑定。350原失败与组合复验见verification/full-350/summary.json。312补充窗口采用既有120秒默认，304/305显式传入当轮source-freeze。'
doc('AGENTS.md','## 当前续接 · 第351节 + '+title+'\n\n'+details+'\n\n继续P3；352从实际剩余节点/事件条件、掉落和固定地图缺口接续，未启动。固定敌人声明不替代本局最终面板与阶段行为。用户当前授权继续至370，完整收尾后暂停。只跑本机必要检查；下一全量365，严格低于15%才开始当前完整小节收尾。\n\n'+note+'\n'+s[end:])
s=(ROOT/'PROJECT_REQUIREMENTS.md').read_text('utf8');start=s.index('<!-- current-delivery:start -->');end=s.index('<!-- current-delivery:end -->')+len('<!-- current-delivery:end -->');doc('PROJECT_REQUIREMENTS.md',s[:start]+'<!-- current-delivery:start -->\n## 第351节 + '+title+'\n\n'+details+'\n<!-- current-delivery:end -->'+s[end:])
s=(ROOT/'PROJECT_PROGRESS.md').read_text('utf8');old='扩展属性的技能/藏品/阶段修正';assert s.count(old)==1;s=s.replace(old,'行动方式/普通攻击/目标生命扣除/计数与控制抗性的动态阶段及当前服务器核对；扩展属性的技能/藏品/阶段修正');doc('PROJECT_PROGRESS.md',s)
cp=read('DEVELOPMENT_CHECKPOINT.json');assert cp['completed_sections']==350 and cp['next_section']==351
for key in('current_section_validation','latest_section_environment','cloud_publication_closeout'):
 if key in cp:cp['historical_before351_'+key]=cp.pop(key)
cp.update(completed_sections=351,latest_functional_section=351,next_section=352,batch_status='P3_SECTION351_LOCAL_ACCEPTED_PUBLICATION_PENDING',next_action='第351节 + '+title+'已本机必要验收；普通推送核对后352接续P3实际剩余缺口，未启动。下次365。',full_validation_due=False)
cp['sections'].append({'number':351,'completion_ref':'p3-section-351','topic':title,'verification':'verification/sections/351.json'});cp['functional_sections_since_latest_requirement'].append(351)
cp['current_section_save']={'section':351,'verification':'verification/sections/351.json','scope':'current_functional_section','binding':'enclosing_commit'};cp['last_verified_cloud_save']['scope']='previous_functional_section'
cp['current_section_validation']={'section':351,'receipt':'verification/sections/351.json','methods_run':n['methods_ran'],'native_isolated_window_checks':w['unique_checks'],'enemy_boundary_subjects':4,'explicit_immunity_fields':11,'real_nonzero_refresh_states':2,'full_suite_rerun':False,'last_full_receipt':'verification/full-350/summary.json','last_full_receipt_is_historical_for_current_changes':True}
cp['latest_section_environment']={'section':351,'receipt':'verification/sections/351.json','native_windows':validation,'native_game_or_chat_verified':False,'current_section_full_rerun':False,'last_full_receipt':'verification/full-350/summary.json'}
cp['windows_native_validation']=validation;cp['current_batch'].update(status=cp['batch_status'],completed_sections=351,next_section=352,next_section_started=False,receipt='verification/sections/351.json',batch_closed=False)
cp['policy'].update(verification_execution_preference='local_project_environment',avoid_duplicate_cloud_tests=True)
cp['current_data_versions'].update(current_enemy_traits_game_commit='bee3f83c5d60590b5e1cd42b8d09d00ce32ab10d',current_enemy_trait_immunities=11,current_enemy_dynamic_control_verified=False)
cp['current_available_full_validation']['historical_for_current_changed_source']=True
cp['current_available_full_validation']['current_worktree_validation_authority']=False
cp['last_full_validation']['historical_for_current_changed_source']=True
(ROOT/'DEVELOPMENT_CHECKPOINT.json').write_bytes(enc(cp))
doc('CLOUD_HANDOFF.md',(ROOT/'CLOUD_HANDOFF.md').read_text('utf8')+'\n<!-- section351-handoff:start -->\n## 第351节 + '+title+'\n\n'+details+'\n<!-- section351-handoff:end -->\n')
out=ROOT/'verification/sections/351-closeout';out.mkdir();shutil.copyfile(ROOT/'.cache/open_test_window_351.py',out/'execution-main-window.py')
runpy.run_path(str(ROOT/'scripts/update_cloud_index.py'))['update'](ROOT)
(out/'execution-closeout.py').write_bytes(Path(__file__).read_bytes());(out/'applied.json').write_bytes(enc({'section':351,'local_accepted':True,'ordinary_cloud_publication_verified':False,'next352_started':False,'at_Beijing':now}))
print(json.dumps({'section':351,'local_accepted':True,'ordinary_publication_pending':True},ensure_ascii=False))
