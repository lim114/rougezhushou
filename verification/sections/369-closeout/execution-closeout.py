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
parent='2535030d489a8abf939b97aaa34226c9205bd0fc';assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()==parent
assert subprocess.check_output(['git','branch','--show-current'],cwd=ROOT).decode().strip()=='codex/p2-development'
title='已有首领文献接入当前关卡与关联敌人'
change='将已核对的四组首领文献接入当前五份关卡配置与九个准确敌人引用，普通敌人页按相关对象显示完整说明和固定地图入口。三十八个主题保留各自来源；同关关联敌人准确返回普通敌人条目，是否提供完整文献由该目标的来源依据决定。同源刷新保留两处阅读和选择，坏源与错源清旧，直接关闭、拒绝和父页离开清理地图树。'
limits='四组旧文献不是四套新机制。当前赤金厄运未配置旧两项关卡修正，旧倍率与面板不能套用；只提供守卫后的文献说明，完整当前敌人预测数值仍未知。未支持的变体、DLC配置或同名狗不借用已支持条目。两份独立痛楚实体只在追猎变体ro6_b_4_b的准确普通敌人条目保留，该变体尚无本节完整机制入口；不把它们放入普通关ro6_b_4的关联列表，不伪造完整图鉴、实际出现或位置。 只作局外查阅，不操作游戏、发送聊天或改变本局；P3/P2/P1均未完成，识别最后。'
validation='本机36项必要测试和78项原生窗口唯一检查通过，完整准确引用与来源边界、两处非零阅读的真实父刷新、坏源清旧/手选恢复、关联跳转及所属关闭按实际回执验收；7张最终图由记录中的真实审阅者逐张查看，不把图片当未显示语义的证明。七类真实外部操作零，临时本局及旧计算保持。原项目测试窗正常更新后可见响应，正常关闭重启期间私人五路径只校验摘要保持；不复制或发布内容。新选择器追加且既有顺序保持。365全量只作历史来源，本节不称重跑全量或365证明当前改动；下一周期380。当前要求和索引实际验证，未变25索引单测复用；未取得的私样本、1314与实机游戏/聊天不计通过。至370完整收尾后暂停。 首次包装在测试开始前因旧清单无files字段退出1；原代码与真实工具报错转录均保留。必要attempt2曾通过；原生attempt1发现验证脚本误用关联索引2，依据原关卡改为6，并将同一真实旧清单格式用于隔离源复制，该次修复保留70处require语法。必要attempt3曾通过，原生attempt2又查出将追猎变体的独立实体误当普通关关联实体的错误前提；改为核对普通关准确的痛楚化身与猎犬proto跳转，另增加真实追猎关7/8两份独立实体的普通选择、原覆写、无数据库替代及无借用文献入口检查。两轮原生失败、原脚本和来源事实均保留；最终必要attempt4与原生attempt3才是当前字节验收。不把预检当执行过测试，不修改游戏机制，不沿用错误关卡前提，也不以删掉整个边界场景来过验收。'
nname='verification/sections/369-necessary-attempt4/process.json';wname='verification/sections/369-native-attempt3/actual/window.json';pname='verification/sections/369-native-attempt3/process.json'
n,w,p=map(read,(nname,wname,pname));m=read('verification/sections/369-main-window.json');a=read('verification/sections/369-source-audit.json');v=read('verification/sections/369-root-visual.json')
assert n['passed']and n['methods_ran']==36 and w['passed']and w['qpa']=='windows'and w['qt_exit_code']==0 and w['unique_checks']==78 and w['verification_window_closed']
assert len(w['same_identity_refresh_observations'])==2 and len(w['screenshots'])==7 and len(w['actual_readings'])==9 and all(x==0 for x in w['external_operation_attempts'].values())
assert p['passed']and p['window_receipt_sha256']==sha(wname)
for result in(n,w):
 assert result['source_sha256_before']==result['source_sha256_after']
 for name,h in result['source_sha256_after'].items():assert sha(name)==h,name
assert v['passed']and len(v['final_screenshot_reviews'])==7 and a['ordered_previous604_preserved']and len(a['current_selectors'])==606
assert m['passed']and m['private_entire_normal_close_and_start_interval_unchanged']and m['window_visible_and_responsive']
now=datetime.now(timezone(timedelta(hours=8))).isoformat();pending='<!-- section369-publication-pending -->本地验收完成，普通推送及真实远端核对待完成。'
r={'section':369,'kind':'functional_section','title':title,'new_capability':change,'limitations':[limits],'at_Beijing':now,'branch':'codex/p2-development','necessary_validation':{**pin(nname),'methods_run':n['methods_ran'],'actual_exit':0},'native_windows_validation':{**pin(wname),'process':pin(pname),'unique_checks':w['unique_checks'],'actual_Qt_exit':0,'real_nonzero_refresh_states':2,'actual_MainWindow_entry_and_close_exercised':True,'all_seven_real_external_operations_zero':True},'root_visual_review':pin('verification/sections/369-root-visual.json'),'source_audit':pin('verification/sections/369-source-audit.json'),'original_project_window':pin('verification/sections/369-main-window.json'),'source_sha256':n['source_sha256_after'],'validated_source_sha256':w['source_sha256_after'],'full_suite_rerun':False,'last_full_receipt':'verification/full-365/summary.json','last_full_receipt_is_historical_for_this_changed_source':True,'last_full_validation_sha256':sha('verification/full-365/summary.json'),'next_periodic_full_section':380,'P3_complete':False,'P2_complete':False,'P1_complete':False,'private_state_contents_parsed_copied_or_restored':False,'private_state_hashed_locally_for_preservation_only':True,'private_hashes_published':False,'game_operated':False,'chat_sent':False,'cloud_publication_binding':'enclosing_commit','cloud_published':False,'execution_environment':'local_original_windows_project_venv','local_source_parity_required_for_cloud_publication':True}
(ROOT/'verification/sections/369.json').write_bytes(enc(r));details=change+'\n\n'+validation+'\n\n'+limits+'\n\n'+pending
old_wip=(ROOT/'WORK_IN_PROGRESS.md').read_bytes();(ROOT/'WORK_IN_PROGRESS.md').write_bytes(('## 第369节 + '+title+'\n\n'+now+'。'+details+'\n\n以下为历史记录；当前断点以上述369为准。\n\n').replace('\n','\r\n').encode()+old_wip)
doc('PROJECT_COMPLETED.md','## 第369节 + '+title+'\n\n'+now+'。'+details+'\n\n'+(ROOT/'PROJECT_COMPLETED.md').read_text('utf8'))
s=(ROOT/'AGENTS.md').read_text('utf8');end=s.index('\n## 项目级最高优先要求');note='下一到期完整检查须给304/305两份full320验证脚本显式传入--source-freeze及当轮根声明冻结文件；默认320仅供历史绑定。350原失败与组合复验见verification/full-350/summary.json。312补充窗口采用既有120秒默认，304/305显式传入当轮source-freeze。'
doc('AGENTS.md','## 当前续接 · 第369节 + '+title+'\n\n'+details+'\n\n继续P3；370从实际剩余节点/事件条件、掉落和固定地图缺口接续，未启动。资料条件对照不替代本局实际状态、生成、生效或结算。通用页面不恢复独立版本栏目。用户当前授权继续至370，完整收尾后暂停。只跑本机必要检查；下一全量380，严格低于15%才开始当前完整小节收尾。\n\n'+note+'\n'+s[end:])
s=(ROOT/'PROJECT_REQUIREMENTS.md').read_text('utf8');start=s.index('<!-- current-delivery:start -->');end=s.index('<!-- current-delivery:end -->')+len('<!-- current-delivery:end -->');doc('PROJECT_REQUIREMENTS.md',s[:start]+'<!-- current-delivery:start -->\n## 第369节 + '+title+'\n\n'+details+'\n<!-- current-delivery:end -->'+s[end:])
s=(ROOT/'PROJECT_PROGRESS.md').read_text('utf8')
doc('PROJECT_PROGRESS.md',s)
cp=read('DEVELOPMENT_CHECKPOINT.json');assert cp['completed_sections']==368 and cp['next_section']==369
for key in('current_section_validation','latest_section_environment','cloud_publication_closeout'):
 if key in cp:cp['historical_before369_'+key]=cp.pop(key)
cp.update(completed_sections=369,latest_functional_section=369,next_section=370,batch_status='P3_SECTION369_LOCAL_ACCEPTED_PUBLICATION_PENDING',next_action='第369节 + '+title+'已本机必要验收；普通推送核对后370接续P3实际剩余缺口，未启动。下次380。',full_validation_due=False)
cp['sections'].append({'number':369,'completion_ref':'p3-section-369','topic':title,'verification':'verification/sections/369.json'});cp['functional_sections_since_latest_requirement'].append(369)
cp['current_section_save']={'section':369,'verification':'verification/sections/369.json','scope':'current_functional_section','binding':'enclosing_commit'};cp['last_verified_cloud_save']['scope']='previous_functional_section'
cp['current_section_validation']={'section':369,'receipt':'verification/sections/369.json','methods_run':n['methods_ran'],'native_isolated_window_checks':w['unique_checks'],'real_nonzero_refresh_states':2,'full_suite_rerun':False,'last_full_receipt':'verification/full-365/summary.json','last_full_receipt_is_historical_for_current_changes':True}
cp['latest_section_environment']={'section':369,'receipt':'verification/sections/369.json','native_windows':validation,'native_game_or_chat_verified':False,'current_section_full_rerun':False,'last_full_receipt':'verification/full-365/summary.json'}
cp['windows_native_validation']=validation;cp['current_batch'].update(status=cp['batch_status'],completed_sections=369,next_section=370,next_section_started=False,receipt='verification/sections/369.json',batch_closed=False)
cp['policy'].update(verification_execution_preference='local_project_environment',avoid_duplicate_cloud_tests=True)
u=read('verification/sections/369-usage.json');cp['policy'].update(current_usage_remaining_percent=u['remaining_percent'],current_usage_receipt='verification/sections/369-usage.json',usage_percent_available=True,usage_wrap_up_triggered=u['triggered'])
cp['current_data_versions'].update({'current_documented_boss_configurations': 5, 'current_documented_boss_exact_references': 9, 'current_documented_boss_topics': 38, 'current_documented_boss_actual_numeric_calibration_verified': False})

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
doc('CLOUD_HANDOFF.md',(ROOT/'CLOUD_HANDOFF.md').read_text('utf8')+'\n<!-- section369-handoff:start -->\n## 第369节 + '+title+'\n\n'+details+'\n<!-- section369-handoff:end -->\n')
out=ROOT/'verification/sections/369-closeout';out.mkdir();shutil.copyfile(ROOT/'.cache/open_test_window_369.py',out/'execution-main-window.py')
runpy.run_path(str(ROOT/'scripts/update_cloud_index.py'))['update'](ROOT)
(out/'execution-closeout.py').write_bytes(Path(__file__).read_bytes());(out/'applied.json').write_bytes(enc({'section':369,'local_accepted':True,'ordinary_cloud_publication_verified':False,'next370_started':False,'at_Beijing':now}))
print(json.dumps({'section':369,'local_accepted':True,'ordinary_publication_pending':True},ensure_ascii=False))
