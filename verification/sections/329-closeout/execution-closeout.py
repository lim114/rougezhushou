from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone,timedelta
import json,runpy,subprocess,shutil
ROOT=Path(__file__).resolve().parents[1]
def read(n):return json.loads((ROOT/n).read_bytes())
def enc(v):return(json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode()
def sha(n):return sha256((ROOT/n).read_bytes()).hexdigest()
def pin(n):return {'receipt':n,'sha256':sha(n)}
def doc(n,s):
 p=ROOT/n;style='\r\n'if b'\r\n'in p.read_bytes()else'\n';p.write_bytes(s.replace('\r\n','\n').replace('\n',style).encode())
parent='1dd98bf6f1c7bc5ae959598323b538039dfeef1a'
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()==parent
assert subprocess.check_output(['git','branch','--show-current'],cwd=ROOT).decode().strip()=='codex/p2-development'
title='八类资源事件的选项、代价与奖励'
change='新增桑尼的邀请、色味不同源、货从口出、沉重的契约、敲动杠杆、血衣之下、擒与缚、泪之聚落八类完整固定事件资料，32段对话、24个文献选项与24份完整原记录。每个选择准确跟随本事件明文后续，不把跨事件相同离开文案合并。明确区分希望、源石锭、目标生命值上限、护盾与行动力七项资源说明；五项随机奖励分别显示1/3件收藏品或1件加工品/概念体/自然物，不混类别、不相加选项、不指定完整池。六项具名收藏品显示准确物品名与作用资料，未独立写明数量仍不补1件、不记已领取。仅货从口出与敲动杠杆显示本页源石锭对照，未知仍可查文献，固定4/10费用按3/4/9/10边界阻断已知不足的后续，其它离开选项独立。半目标生命值不套其它事件保1点或猜取整，全部源石锭不当固定费用，零资源是否可选仍未知。版本页32情景/24原选项共56入口准确进入；刷新保持两组非零阅读、选项、阶段及本页对照，实际公开副本损坏清旧/手选恢复、重复开窗和父页失效关闭子窗。无关资源输入和说明不出现在其它事件。'
limits='复用321实际下载的BWIKI352356原HTTP，八张完整事件表按原字符位置和字节摘要摘录；本轮针对沉重的契约、敲动杠杆等公开条文复读，不冒称新下载完整HTML。32情景、24完整选项与11物品逐项核对bee3及a550记录；同名离开通过文献后续及当前完整目的地限定本事件，不按ID猜服务器父脚本。固定源石锭不足只作本页阅读对照，足够不等于完整出现资格。随机物品只有原文明示数量和类别，完整池/稀有度/加成/实际发放未知；具名未写件数仍未知，不把效果资料接入本局计算。半目标生命值的取整/最低剩余、全部源石锭零余额入口和实际扣除、各事件服务器完整资格与真实执行仍未闭合。P3/P2/P1未完成、识别最后，不操作游戏或聊天、不改本局及私人设置，不给路线建议或生成概率。'
validation='本机首轮39项必要检查通过。实际界面复读仅调整player_text中的无关源石锭与生命/护盾提示，保留初版模型完整字节并确认该函数以外AST不变；扩充原模型测试方法中的相关断言，最终8项模型复验通过，其余31项未变检查复用，不声称最终重跑39项。最终31项Windows原生唯一检查通过，遍历全部32情景24文献选项、仅两事件有固定费用对照、未知/9/10与3/4边界、离开分支独立、三类随机零件不混池、六具名奖励资料与未知件数、半生命不套保1点、全源石锭零余额资格未知、两组真实非零阅读经父页刷新保留、实际坏源清旧/手选恢复、重复开窗及父源失效清子窗。最终9张PNG全部直接查看，首轮和复验原日志并存；七类外部调用零、临时本局及旧计算上下文不变。原项目测试窗已正常更新、可见响应，正常关闭到启动私人五路径不变。525旧选择器原序保持，现527。测试只本机，未重复全量或未变索引25单测；320全量/原失败/不可用范围仍属历史，下次335。'
nname='verification/sections/329-necessary-attempt2/process.json';wname='verification/sections/329-native-attempt2/actual/window.json';pname='verification/sections/329-native-attempt2/process.json'
n,w,p=map(read,(nname,wname,pname));m=read('verification/sections/329-main-window.json');a=read('verification/sections/329-source-audit.json');v=read('verification/sections/329-root-visual.json')
assert n['passed']and n['methods_ran']==8 and w['passed']and w['qpa']=='windows'and w['qt_exit_code']==0 and w['unique_checks']==31 and w['verification_window_closed']
assert len(w['same_identity_refresh_observations'])==2 and len(w['screenshots'])==9 and len(w['actual_readings'])==24 and all(x==0 for x in w['external_operation_attempts'].values())
assert p['passed']and p['window_receipt_sha256']==sha(wname)
for result in(n,w):
 assert result['source_sha256_before']==result['source_sha256_after']
 for name,h in result['source_sha256_after'].items():assert sha(name)==h,name
assert v['passed']and len(v['final_screenshot_reviews'])==9 and a['ordered_previous525_preserved']and len(a['current_selectors'])==527
assert m['passed']and m['private_entire_normal_close_and_start_interval_unchanged']and m['window_visible_and_responsive']
now=datetime.now(timezone(timedelta(hours=8))).isoformat();pending='<!-- section329-publication-pending -->本地验收完成，普通推送及真实远端核对待完成。'
r={'section':329,'kind':'functional_section','title':title,'new_capability':change,'limitations':[limits],'at_Beijing':now,'branch':'codex/p2-development','necessary_validation':{**pin(nname),'final_model_methods_run':8,'initial39_receipt':'verification/sections/329-necessary-attempt1/process.json','initial39_all_passed':True,'other31_unchanged_checks_reused':True,'scope':pin('verification/sections/329-check-scope/scope.json'),'actual_exit':0},'native_windows_validation':{**pin(wname),'process':pin(pname),'unique_checks':31,'actual_Qt_exit':0,'documented_events':8,'documented_scenes':32,'document_choices':24,'original_choice_variants':24,'reference_items':11,'fixed_gold_choices':5,'named_reward_choices':6,'real_nonzero_refresh_states':2,'actual_MainWindow_entry_exercised':True,'all_seven_real_external_operations_zero':True},'root_visual_review':pin('verification/sections/329-root-visual.json'),'source_audit':pin('verification/sections/329-source-audit.json'),'original_project_window':pin('verification/sections/329-main-window.json'),'source_sha256':n['source_sha256_after'],'validated_source_sha256':w['source_sha256_after'],'full_suite_rerun':False,'last_full_receipt':'verification/full-320/summary.json','last_full_receipt_is_historical_for_this_changed_source':True,'last_full_validation_sha256':sha('verification/full-320/summary.json'),'next_periodic_full_section':335,'P3_complete':False,'P2_complete':False,'P1_complete':False,'private_state_contents_parsed_copied_or_restored':False,'private_state_hashed_locally_for_preservation_only':True,'private_hashes_published':False,'game_operated':False,'chat_sent':False,'cloud_publication_binding':'enclosing_commit','cloud_published':False,'execution_environment':'local_original_windows_project_venv','local_source_parity_required_for_cloud_publication':True}
(ROOT/'verification/sections/329.json').write_bytes(enc(r));details=change+'\n\n'+validation+'\n\n'+limits+'\n\n'+pending
old_wip=subprocess.check_output(['git','show',parent+':WORK_IN_PROGRESS.md'],cwd=ROOT)
prefix=('## 第329节 + '+title+'\n\n'+now+'。'+details+'\n\n以下为历史记录；当前断点以上述329为准。\n\n').replace('\n','\r\n').encode();(ROOT/'WORK_IN_PROGRESS.md').write_bytes(prefix+old_wip)
doc('PROJECT_COMPLETED.md','## 第329节 + '+title+'\n\n'+now+'。'+details+'\n\n'+(ROOT/'PROJECT_COMPLETED.md').read_text('utf8'))
s=(ROOT/'AGENTS.md').read_text('utf8');end=s.index('\n## ',3);doc('AGENTS.md','## 当前续接 · 第329节 + '+title+'\n\n'+details+'\n\n继续P3；330从当前事件前置、完整奖励池和固定地图实际剩余缺口接续，未启动。测试优先本机，保留到期完整范围，下次335；严格低于15%才开始完整收尾。\n'+s[end:])
s=(ROOT/'PROJECT_REQUIREMENTS.md').read_text('utf8');start=s.index('<!-- current-delivery:start -->');end=s.index('<!-- current-delivery:end -->')+len('<!-- current-delivery:end -->');doc('PROJECT_REQUIREMENTS.md',s[:start]+'<!-- current-delivery:start -->\n## 第329节 + '+title+'\n\n'+details+'\n<!-- current-delivery:end -->'+s[end:])
s=(ROOT/'PROJECT_PROGRESS.md').read_text('utf8');old='其余未覆盖完整事件表及其奖励条件';new='八类已列资源事件的完整服务器资格、随机池及具名实际发放、沉重的契约半生命取整/最低剩余、泪之聚落零余额入口与实际扣除，其余未覆盖完整事件表及其奖励条件';assert s.count(old)==1;doc('PROJECT_PROGRESS.md',s.replace(old,new,1))
cp=read('DEVELOPMENT_CHECKPOINT.json');assert cp['completed_sections']==328 and cp['next_section']==329
for key in('current_section_validation','latest_section_environment','cloud_publication_closeout'):
 if key in cp:cp['historical_before329_'+key]=cp.pop(key)
cp.update(completed_sections=329,latest_functional_section=329,next_section=330,batch_status='P3_SECTION329_LOCAL_ACCEPTED_PUBLICATION_PENDING',next_action='第329节 + '+title+'已本机必要验收；普通推送核对后330接续P3实际剩余缺口，未启动。下次335。',full_validation_due=False)
cp['sections'].append({'number':329,'completion_ref':'p3-section-329','topic':title,'verification':'verification/sections/329.json'});cp['functional_sections_since_latest_requirement'].append(329)
cp['current_section_save']={'section':329,'verification':'verification/sections/329.json','scope':'current_functional_section','binding':'enclosing_commit'};cp['last_verified_cloud_save']['scope']='previous_functional_section'
cp['current_section_validation']={'section':329,'receipt':'verification/sections/329.json','initial39_all_passed':True,'final_model8_passed':True,'other31_reused':True,'native_isolated_window_checks':31,'documented_events':8,'documented_scenes':32,'document_choices':24,'original_choice_variants':24,'reference_items':11,'fixed_gold_choices':5,'named_reward_choices':6,'real_nonzero_refresh_states':2,'full_suite_rerun':False,'last_full_receipt':'verification/full-320/summary.json','last_full_receipt_is_historical_for_current_changes':True}
cp['latest_section_environment']={'section':329,'receipt':'verification/sections/329.json','native_windows':validation,'native_game_or_chat_verified':False,'current_section_full_rerun':False,'last_full_receipt':'verification/full-320/summary.json'}
cp['windows_native_validation']=validation;cp['current_batch'].update(status=cp['batch_status'],completed_sections=329,next_section=330,next_section_started=False,receipt='verification/sections/329.json',batch_closed=False)
cp['policy'].update(current_usage_remaining_percent=67,current_usage_receipt='verification/sections/329-preparation/usage-final.json',verification_execution_preference='local_project_environment',avoid_duplicate_cloud_tests=True)
cp['current_data_versions'].update(current_resource_events_game_commit='bee3f83c5d60590b5e1cd42b8d09d00ce32ab10d',current_resource_events_document_revision=352356,current_resource_events_count=8,current_resource_events_scenes=32,current_resource_events_choices=24,current_resource_events_fixed_gold_is_local_only=True,current_resource_events_actual_eligibility_verified=False)
(ROOT/'DEVELOPMENT_CHECKPOINT.json').write_bytes(enc(cp))
doc('CLOUD_HANDOFF.md',(ROOT/'CLOUD_HANDOFF.md').read_text('utf8')+'\n<!-- section329-handoff:start -->\n## 第329节 + '+title+'\n\n'+details+'\n<!-- section329-handoff:end -->\n')
out=ROOT/'verification/sections/329-preparation';shutil.copyfile(ROOT/'.cache/open_test_window_329.py',out/'execution-main-window.py')
runpy.run_path(str(ROOT/'scripts/update_cloud_index.py'))['update'](ROOT)
out=ROOT/'verification/sections/329-closeout';out.mkdir();(out/'execution-closeout.py').write_bytes(Path(__file__).read_bytes());(out/'applied.json').write_bytes(enc({'section':329,'local_accepted':True,'ordinary_cloud_publication_verified':False,'next330_started':False,'at_Beijing':now}))
print(json.dumps({'section':329,'local_accepted':True,'ordinary_publication_pending':True},ensure_ascii=False))
