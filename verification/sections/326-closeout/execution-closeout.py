from pathlib import Path
from hashlib import sha256
from datetime import datetime, timezone, timedelta
import json, runpy, subprocess, shutil
ROOT=Path(__file__).resolve().parents[1]
def read(n):return json.loads((ROOT/n).read_bytes())
def enc(v):return(json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode('utf8')
def sha(n):return sha256((ROOT/n).read_bytes()).hexdigest()
def pin(n):return {'receipt':n,'sha256':sha(n)}
def doc(n,s):
 p=ROOT/n;style='\r\n'if b'\r\n'in p.read_bytes()else'\n';p.write_bytes(s.replace('\r\n','\n').replace('\n',style).encode('utf8'))
parent='c04af76cc88e5eca502d97a01891afdd53cab1c8'
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()==parent
assert subprocess.check_output(['git','branch','--show-current'],cwd=ROOT).decode().strip()=='codex/p2-development'
title='当前具名事件作战入口与关卡反查'
change='新增当前事件作战资料窗，完整收录固定原表内全部具名ISW链接的9事件13文献格，按12个完整原选项整理20条可查配置引用、17份当前配置，明确排除3条紧急选项误配普通配置。湖中仙女重复两格只保留一个选项与两处来源；黑诞列三个具名作战、六份同名配置，不默认实际版本或连续战斗，不把艰难当紧急。版本页对应原选项可直达，36个同名情景只打开该事件总览，不推父关系；当前固定作战页新增反查来源选项入口，普通反查不混入明确紧急选项。所有地图先手选配置，再用当前精确ID打开原图、敌人、出怪和奖励资料。父页刷新保留两组非零阅读、选项、配置及嵌套反查窗口；资料实际损坏清旧/恢复手选，重复开窗、换配置、父窗关闭清理整棵子窗；事件来源单独失效不清掉核心地图和其它关卡页。'
limits='复用321实际下载并核SHA的BWIKI352356原HTTP，扫描该固定响应全部h3事件表的具名ISW锚点，摘录9张完整原表并保留原标题双锚、行列、完整文案与链接。不声称已覆盖没有这类锚点的全部事件或所有来源。完整caption与bee3当前选择唯一匹配，紧急只依据原格明确括注和当前isElite/difficulty，不因省略紧急字样排除同名紧急引用。初始按t/c编号猜levelId不同的前提已被原始完整记录纠正：黑诞三名各两配置共享levelId，但完整配置不是全部相同；不由同文件推实际入口/完全相同机制。当前与a550完整比较的5份灰坑/大红按钮记录为新增，其余60份记录对照相同，不把新增当旧版复用。20为跨选项配置引用，17为配置ID，不是20张地图、战斗次数或概率；实际父情景、当前入口脚本、版本选择、服务器资格及完整奖励仍未知。旧25/57入口缺口未据此销项，P3/P2/P1未完成，识别最后；不操作游戏或聊天，不改本局/私人配置与旧计算，不推荐路线。'
validation='本机首轮86项必要检查中85项通过、1项错误地要求所有记录与旧版相同；改为精确核对5份新增记录与各完整当前/旧值后该项独立通过。之后仅改一个玩家文本措辞，重建初版模块字节核对原SHA并确认player_text以外AST不变，最终7项模型检查通过，其余79项未变检查复用，不声称最终重跑86项。最终37项Windows原生唯一检查通过，逐一打开12选项的20配置引用，验证明确紧急排除、黑诞三名六配置、湖中重复记载、双向入口、普通/紧急反查分离、两组真实非零滚动选区/配置/嵌套窗口经刷新保持、实际公开副本损坏清旧/恢复手选及完整子窗关闭。首轮大窗文字可完整容纳导致非零滚动断言失败，保留原失败，改验收窗口为850x450后保留原断言复验通过；措辞修正后原窗口全范围再验通过。七张最终PNG全部直接查看；七类外部调用零、临时本局和旧计算上下文不变。原项目测试窗口正常更新可见响应，正常关闭至启动私人五路径不变。519旧维护选择器原序保持，现521；仅本机必要测试，未重跑全量或未变索引25单测，320完整范围/失败/不可用原件保留为历史，下次335。'
nname='verification/sections/326-necessary-attempt3/process.json';wname='verification/sections/326-native-attempt3/actual/window.json';pname='verification/sections/326-native-attempt3/process.json'
n,w,p=map(read,(nname,wname,pname));m=read('verification/sections/326-main-window.json');a=read('verification/sections/326-source-audit.json');v=read('verification/sections/326-root-visual.json');scope=read('verification/sections/326-check-scope.json')
assert n['passed']and n['methods_ran']==7 and scope['passed']and scope['other79_unchanged_methods_reused_not_rerun']
assert w['passed']and w['qpa']=='windows'and w['qt_exit_code']==0 and w['unique_checks']==37 and w['verification_window_closed']
assert len(w['same_identity_refresh_observations'])==2 and len(w['screenshots'])==7 and len(w['actual_readings'])==20 and all(x==0 for x in w['external_operation_attempts'].values())
assert p['passed']and p['window_receipt_sha256']==sha(wname)
for result in(n,w):
 assert result['source_sha256_before']==result['source_sha256_after']
 for name,h in result['source_sha256_after'].items():assert sha(name)==h,name
assert v['passed']and len(v['directly_viewed'])==7 and a['ordered_previous519_preserved']and len(a['current_selectors'])==521
assert m['passed']and m['private_entire_normal_close_and_start_interval_unchanged']and m['window_visible_and_responsive']
now=datetime.now(timezone(timedelta(hours=8))).isoformat();pending='<!-- section326-publication-pending -->本地验收完成，普通推送及真实远端核对待完成。'
r={'section':326,'kind':'functional_section','title':title,'new_capability':change,'limitations':[limits],'at_Beijing':now,'branch':'codex/p2-development','necessary_validation':{**pin(nname),'final_model_methods_run':7,'initial86_receipt':'verification/sections/326-necessary-attempt1/process.json','initial85_passed1_test_premise_fixed':True,'other79_unchanged_checks_reused':True,'scope':pin('verification/sections/326-check-scope.json'),'actual_exit':0},'native_windows_validation':{**pin(wname),'process':pin(pname),'unique_checks':37,'actual_Qt_exit':0,'documented_events':9,'documented_named_battle_cells':13,'unique_choices':12,'admitted_choice_stage_refs':20,'stage_configs':17,'explicit_emergency_exclusions':3,'real_nonzero_refresh_states':2,'actual_MainWindow_entry_exercised':True,'all_seven_real_external_operations_zero':True},'root_visual_review':pin('verification/sections/326-root-visual.json'),'source_audit':pin('verification/sections/326-source-audit.json'),'original_project_window':pin('verification/sections/326-main-window.json'),'source_sha256':n['source_sha256_after'],'validated_source_sha256':w['source_sha256_after'],'full_suite_rerun':False,'last_full_receipt':'verification/full-320/summary.json','last_full_receipt_is_historical_for_this_changed_source':True,'last_full_validation_sha256':sha('verification/full-320/summary.json'),'next_periodic_full_section':335,'P3_complete':False,'P2_complete':False,'P1_complete':False,'private_state_contents_parsed_copied_or_restored':False,'private_state_hashed_locally_for_preservation_only':True,'private_hashes_published':False,'game_operated':False,'chat_sent':False,'cloud_publication_binding':'enclosing_commit','cloud_published':False,'execution_environment':'local_original_windows_project_venv','local_source_parity_required_for_cloud_publication':True}
(ROOT/'verification/sections/326.json').write_bytes(enc(r));details=change+'\n\n'+validation+'\n\n'+limits+'\n\n'+pending
old_wip=subprocess.check_output(['git','show',parent+':WORK_IN_PROGRESS.md'],cwd=ROOT)
prefix=('## 第326节 + '+title+'\n\n'+now+'。'+details+'\n\n以下为历史记录；当前断点以上述326为准。\n\n').replace('\n','\r\n').encode('utf8');(ROOT/'WORK_IN_PROGRESS.md').write_bytes(prefix+old_wip)
doc('PROJECT_COMPLETED.md','## 第326节 + '+title+'\n\n'+now+'。'+details+'\n\n'+(ROOT/'PROJECT_COMPLETED.md').read_text('utf8'))
s=(ROOT/'AGENTS.md').read_text('utf8');end=s.index('\n## ',3);doc('AGENTS.md','## 当前续接 · 第326节 + '+title+'\n\n'+details+'\n\n继续P3；327从当前事件前置、完整奖励池和固定地图的实际剩余缺口接续，未启动。测试优先本机，保留到期完整范围，下次335；严格低于15%才开始完整收尾。\n'+s[end:])
s=(ROOT/'PROJECT_REQUIREMENTS.md').read_text('utf8');start=s.index('<!-- current-delivery:start -->');end=s.index('<!-- current-delivery:end -->')+len('<!-- current-delivery:end -->');doc('PROJECT_REQUIREMENTS.md',s[:start]+'<!-- current-delivery:start -->\n## 第326节 + '+title+'\n\n'+details+'\n<!-- current-delivery:end -->'+s[end:])
s=(ROOT/'PROJECT_PROGRESS.md').read_text('utf8');old='其余具名奖励来源、完整掉落池与零件池范围';new='已列具名作战选项的真实父情景、实际版本选择与入口脚本、其余未列链接的作战来源及全部事件选项/条件、其余具名奖励来源、完整掉落池与零件池范围';assert s.count(old)==1;doc('PROJECT_PROGRESS.md',s.replace(old,new,1))
cp=read('DEVELOPMENT_CHECKPOINT.json');assert cp['completed_sections']==325 and cp['next_section']==326
for key in('current_section_validation','latest_section_environment','cloud_publication_closeout'):
 if key in cp:cp['historical_before326_'+key]=cp.pop(key)
cp.update(completed_sections=326,latest_functional_section=326,next_section=327,batch_status='P3_SECTION326_LOCAL_ACCEPTED_PUBLICATION_PENDING',next_action='第326节 + '+title+'已本机必要验收；普通推送核对后327接续P3实际剩余缺口，未启动。下次定期全量335。',full_validation_due=False)
cp['sections'].append({'number':326,'completion_ref':'p3-section-326','topic':title,'verification':'verification/sections/326.json'});cp['functional_sections_since_latest_requirement'].append(326)
cp['current_section_save']={'section':326,'verification':'verification/sections/326.json','scope':'current_functional_section','binding':'enclosing_commit'};cp['last_verified_cloud_save']['scope']='previous_functional_section'
cp['current_section_validation']={'section':326,'receipt':'verification/sections/326.json','initial86_passed85_failed1_test_premise':True,'failed1_fixed_rechecked':True,'final_model7_passed':True,'other79_reused':True,'native_isolated_window_checks':37,'named_battle_document_cells':13,'choices':12,'config_refs':20,'unique_stage_ids':17,'real_nonzero_refresh_states':2,'full_suite_rerun':False,'last_full_receipt':'verification/full-320/summary.json','last_full_receipt_is_historical_for_current_changes':True}
cp['latest_section_environment']={'section':326,'receipt':'verification/sections/326.json','native_windows':validation,'native_game_or_chat_verified':False,'current_section_full_rerun':False,'last_full_receipt':'verification/full-320/summary.json'}
cp['windows_native_validation']=validation;cp['current_batch'].update(status=cp['batch_status'],completed_sections=326,next_section=327,next_section_started=False,receipt='verification/sections/326.json',batch_closed=False)
cp['policy'].update(current_usage_remaining_percent=68,current_usage_receipt='verification/sections/326-preparation/usage-final.json',verification_execution_preference='local_project_environment',avoid_duplicate_cloud_tests=True)
cp['current_data_versions'].update(current_event_battles_game_commit='bee3f83c5d60590b5e1cd42b8d09d00ce32ab10d',current_event_battles_document_revision=352356,current_event_battles_events=9,current_event_battles_document_cells=13,current_event_battles_choices=12,current_event_battles_config_refs=20,current_event_battles_config_ids=17,current_event_battles_emergency_exclusions=3,current_event_battles_actual_eligibility_verified=False)
(ROOT/'DEVELOPMENT_CHECKPOINT.json').write_bytes(enc(cp))
doc('CLOUD_HANDOFF.md',(ROOT/'CLOUD_HANDOFF.md').read_text('utf8')+'\n<!-- section326-handoff:start -->\n## 第326节 + '+title+'\n\n'+details+'\n<!-- section326-handoff:end -->\n')
out=ROOT/'verification/sections/326-preparation';shutil.copyfile(ROOT/'.cache/open_test_window_326.py',out/'execution-main-window.py')
runpy.run_path(str(ROOT/'scripts/update_cloud_index.py'))['update'](ROOT)
out=ROOT/'verification/sections/326-closeout';out.mkdir();(out/'execution-closeout.py').write_bytes(Path(__file__).read_bytes());(out/'applied.json').write_bytes(enc({'section':326,'local_accepted':True,'ordinary_cloud_publication_verified':False,'next327_started':False,'at_Beijing':now}))
print(json.dumps({'section':326,'local_accepted':True,'ordinary_publication_pending':True},ensure_ascii=False))
