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
parent='045de1aa7cebd98940b6243e9fa3c9eb0c69b1b0'
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()==parent
assert subprocess.check_output(['git','branch','--show-current'],cwd=ROOT).decode().strip()=='codex/p2-development'
title='七类遭遇的完整对话、条件与代价'
change='新增思乡心切、划算买卖、鸭托邦、传奇团伙、黑诞、原始娱乐、掠夺成性七张完整原表的逐步阅读：23段对话、25组文献选项、28份当前原始选项记录。根选项/准备对话/战斗确认分别归属，不在准备选项提前开图；黑诞4份同文案逃离记录合为一个可读组选项但保留全部原件与共同明确后续，不当4次扣除。笼控器三态对照只在黑诞出现，未持有只阻断对应猎印分支，战斗和逃离资料保留；猎印具名效果只作资料，领取件数及实际发放未知。半数源石锭不猜奇数取整，生命代价明确至少保留1点，不自动扣费。9个具名作战确认打开326精确选项/配置阅读器，战斗阅读器可返回本选项的完整对话，保持普通/紧急边界及手动选图。版本页23情景和28原选项可准确进入；刷新保留两组非零阅读、笼控器对照、后续情景、配置及嵌套地图；坏源清旧/恢复手选、重复打开/父窗关闭清理整棵子窗，地图目录单独失效不影响完整对话。默认文字去掉父脚本和处理类型术语，供普通玩家阅读。'
limits='复用321真实下载的BWIKI352356原HTTP及326已核SHA摘录，保留七张完整表的原字符位置、全文文案与nextSceneId核对。只把原表根标签与明确后续用于文献流程；不按ID、序号或同标题猜游戏父脚本。25为文献组选项、28为原记录，不是已恢复的本局选择池；黑诞三份TRADE/一份NEXT全部保留，不指定实际变体。笼控器是SCRAP持有前提，不从持有文字推已消耗或发放1件猎印；既有藏品计算未改变。当前7事件23情景28选项及2物品逐项比较固定bee3与a550完整记录；固定文献不冒充当前服务器的完整出现资格、真实发放脚本/奖励池或实际入口。已针对半数取整与猎印额外来源搜索，未得到完整整数/发放执行依据，不推算奇数扣费、战胜后实际领取件数或套用加成。P3/P2/P1未完成、识别最后，不操作游戏/聊天、不清本局或覆盖私人设置，不给路线建议与概率。'
validation='本机首次94项必要检查全部通过。实窗可读性复读后仅改player_text中的两处内部术语和范围文字，完整重建初版模块字节核对原SHA，确认该函数以外AST不变；最终8项模型检查再验通过，其余86项未变检查复用，不声称最终重跑94项。最终39项Windows原生唯一检查通过，遍历全部23情景25组选项及9个精确作战阅读入口，笼控器控件只在黑诞、三态与其它选项独立、4变体不重复扣除、半源石锭整数未知、准备对话只跟随后续、精确紧急配置与战斗阅读返回完整对话均核对。两组真实非零滚动选区/条件/配置/嵌套地图经父页刷新保留，实际公开副本损坏清旧/恢复手选、可选地图源单独失败及整棵子窗关闭通过。最终五张不同PNG直接查看，另外两张分别与已直接查看的首轮坏源图和最终紧急确认图逐字节相同；首轮94项/窗口和最终复验日志均保留。七类外部调用零、临时本局和旧计算上下文不变；原项目测试窗口正常更新、可见响应，正常关闭至启动私人五路径不变。521旧维护选择器原序保持，现523。仅本机必要测试，未重跑已通过全量或未变索引25单测；320完整范围/失败/不可用原件仍为历史，下一定期全量335。'
nname='verification/sections/327-necessary-attempt2/process.json';wname='verification/sections/327-native-attempt2/actual/window.json';pname='verification/sections/327-native-attempt2/process.json'
n,w,p=map(read,(nname,wname,pname));m=read('verification/sections/327-main-window.json');a=read('verification/sections/327-source-audit.json');v=read('verification/sections/327-root-visual.json');scope=read('verification/sections/327-check-scope.json')
assert n['passed']and n['methods_ran']==8 and scope['passed']and scope['other86_unchanged_methods_reused_not_rerun']
assert w['passed']and w['qpa']=='windows'and w['qt_exit_code']==0 and w['unique_checks']==39 and w['verification_window_closed']
assert len(w['same_identity_refresh_observations'])==2 and len(w['screenshots'])==7 and len(w['actual_readings'])==25 and all(x==0 for x in w['external_operation_attempts'].values())
assert p['passed']and p['window_receipt_sha256']==sha(wname)
for result in(n,w):
 assert result['source_sha256_before']==result['source_sha256_after']
 for name,h in result['source_sha256_after'].items():assert sha(name)==h,name
assert v['passed']and len(v['final_screenshot_reviews'])==7 and a['ordered_previous521_preserved']and len(a['current_selectors'])==523
assert m['passed']and m['private_entire_normal_close_and_start_interval_unchanged']and m['window_visible_and_responsive']
now=datetime.now(timezone(timedelta(hours=8))).isoformat();pending='<!-- section327-publication-pending -->本地验收完成，普通推送及真实远端核对待完成。'
r={'section':327,'kind':'functional_section','title':title,'new_capability':change,'limitations':[limits],'at_Beijing':now,'branch':'codex/p2-development','necessary_validation':{**pin(nname),'final_model_methods_run':8,'initial94_receipt':'verification/sections/327-necessary-attempt1/process.json','initial94_all_passed':True,'other86_unchanged_checks_reused':True,'scope':pin('verification/sections/327-check-scope.json'),'actual_exit':0},'native_windows_validation':{**pin(wname),'process':pin(pname),'unique_checks':39,'actual_Qt_exit':0,'documented_events':7,'documented_scenes':23,'document_choice_groups':25,'original_choice_variants':28,'exact_battle_choice_links':9,'real_nonzero_refresh_states':2,'actual_MainWindow_entry_exercised':True,'all_seven_real_external_operations_zero':True},'root_visual_review':pin('verification/sections/327-root-visual.json'),'source_audit':pin('verification/sections/327-source-audit.json'),'original_project_window':pin('verification/sections/327-main-window.json'),'source_sha256':n['source_sha256_after'],'validated_source_sha256':w['source_sha256_after'],'full_suite_rerun':False,'last_full_receipt':'verification/full-320/summary.json','last_full_receipt_is_historical_for_this_changed_source':True,'last_full_validation_sha256':sha('verification/full-320/summary.json'),'next_periodic_full_section':335,'P3_complete':False,'P2_complete':False,'P1_complete':False,'private_state_contents_parsed_copied_or_restored':False,'private_state_hashed_locally_for_preservation_only':True,'private_hashes_published':False,'game_operated':False,'chat_sent':False,'cloud_publication_binding':'enclosing_commit','cloud_published':False,'execution_environment':'local_original_windows_project_venv','local_source_parity_required_for_cloud_publication':True}
(ROOT/'verification/sections/327.json').write_bytes(enc(r));details=change+'\n\n'+validation+'\n\n'+limits+'\n\n'+pending
old_wip=subprocess.check_output(['git','show',parent+':WORK_IN_PROGRESS.md'],cwd=ROOT)
prefix=('## 第327节 + '+title+'\n\n'+now+'。'+details+'\n\n以下为历史记录；当前断点以上述327为准。\n\n').replace('\n','\r\n').encode('utf8');(ROOT/'WORK_IN_PROGRESS.md').write_bytes(prefix+old_wip)
doc('PROJECT_COMPLETED.md','## 第327节 + '+title+'\n\n'+now+'。'+details+'\n\n'+(ROOT/'PROJECT_COMPLETED.md').read_text('utf8'))
s=(ROOT/'AGENTS.md').read_text('utf8');end=s.index('\n## ',3);doc('AGENTS.md','## 当前续接 · 第327节 + '+title+'\n\n'+details+'\n\n继续P3；328从当前事件前置、完整奖励池和固定地图的实际剩余缺口接续，未启动。测试优先本机，保留到期完整范围，下次335；严格低于15%才开始完整收尾。\n'+s[end:])
s=(ROOT/'PROJECT_REQUIREMENTS.md').read_text('utf8');start=s.index('<!-- current-delivery:start -->');end=s.index('<!-- current-delivery:end -->')+len('<!-- current-delivery:end -->');doc('PROJECT_REQUIREMENTS.md',s[:start]+'<!-- current-delivery:start -->\n## 第327节 + '+title+'\n\n'+details+'\n<!-- current-delivery:end -->'+s[end:])
s=(ROOT/'PROJECT_PROGRESS.md').read_text('utf8');old='其余具名奖励来源、完整掉落池与零件池范围';new='七类已列遭遇的服务器完整出现条件、黑诞实际逃离变体/生命扣除与笼控器消耗/猎印实际发放、传奇团伙半源石锭整数处理、其余未覆盖完整事件表及其奖励条件、其余具名奖励来源、完整掉落池与零件池范围';assert s.count(old)==1;doc('PROJECT_PROGRESS.md',s.replace(old,new,1))
cp=read('DEVELOPMENT_CHECKPOINT.json');assert cp['completed_sections']==326 and cp['next_section']==327
for key in('current_section_validation','latest_section_environment','cloud_publication_closeout'):
 if key in cp:cp['historical_before327_'+key]=cp.pop(key)
cp.update(completed_sections=327,latest_functional_section=327,next_section=328,batch_status='P3_SECTION327_LOCAL_ACCEPTED_PUBLICATION_PENDING',next_action='第327节 + '+title+'已本机必要验收；普通推送核对后328接续P3实际剩余缺口，未启动。下次定期全量335。',full_validation_due=False)
cp['sections'].append({'number':327,'completion_ref':'p3-section-327','topic':title,'verification':'verification/sections/327.json'});cp['functional_sections_since_latest_requirement'].append(327)
cp['current_section_save']={'section':327,'verification':'verification/sections/327.json','scope':'current_functional_section','binding':'enclosing_commit'};cp['last_verified_cloud_save']['scope']='previous_functional_section'
cp['current_section_validation']={'section':327,'receipt':'verification/sections/327.json','initial94_all_passed':True,'final_model8_passed':True,'other86_reused':True,'native_isolated_window_checks':39,'documented_events':7,'documented_scenes':23,'document_choices':25,'original_choice_variants':28,'exact_battle_choice_links':9,'real_nonzero_refresh_states':2,'full_suite_rerun':False,'last_full_receipt':'verification/full-320/summary.json','last_full_receipt_is_historical_for_current_changes':True}
cp['latest_section_environment']={'section':327,'receipt':'verification/sections/327.json','native_windows':validation,'native_game_or_chat_verified':False,'current_section_full_rerun':False,'last_full_receipt':'verification/full-320/summary.json'}
cp['windows_native_validation']=validation;cp['current_batch'].update(status=cp['batch_status'],completed_sections=327,next_section=328,next_section_started=False,receipt='verification/sections/327.json',batch_closed=False)
cp['policy'].update(current_usage_remaining_percent=67,current_usage_receipt='verification/sections/327-preparation/usage-final.json',verification_execution_preference='local_project_environment',avoid_duplicate_cloud_tests=True)
cp['current_data_versions'].update(current_encounters_game_commit='bee3f83c5d60590b5e1cd42b8d09d00ce32ab10d',current_encounters_document_revision=352356,current_encounters_events=7,current_encounters_scenes=23,current_encounters_choices=25,current_encounters_original_variants=28,current_encounters_controller_is_reference_only=True,current_encounters_actual_eligibility_verified=False)
(ROOT/'DEVELOPMENT_CHECKPOINT.json').write_bytes(enc(cp))
doc('CLOUD_HANDOFF.md',(ROOT/'CLOUD_HANDOFF.md').read_text('utf8')+'\n<!-- section327-handoff:start -->\n## 第327节 + '+title+'\n\n'+details+'\n<!-- section327-handoff:end -->\n')
out=ROOT/'verification/sections/327-preparation';shutil.copyfile(ROOT/'.cache/open_test_window_327.py',out/'execution-main-window.py')
runpy.run_path(str(ROOT/'scripts/update_cloud_index.py'))['update'](ROOT)
out=ROOT/'verification/sections/327-closeout';out.mkdir();(out/'execution-closeout.py').write_bytes(Path(__file__).read_bytes());(out/'applied.json').write_bytes(enc({'section':327,'local_accepted':True,'ordinary_cloud_publication_verified':False,'next328_started':False,'at_Beijing':now}))
print(json.dumps({'section':327,'local_accepted':True,'ordinary_publication_pending':True},ensure_ascii=False))
