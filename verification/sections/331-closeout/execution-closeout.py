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
parent='1599c549a4f9bb4cb571399efc41b007ac6479c3'
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()==parent
assert subprocess.check_output(['git','branch','--show-current'],cwd=ROOT).decode().strip()=='codex/p2-development'
title='金色凝滞与三重身的选项、奖励和后续'
change='新增金色凝滞与三重身两张完整固定原表的逐步查阅，11段文献对话组、10组选项，保留17份原情景与19份完整原选项。金色凝滞七项逐条说明目标生命值上限、可携带上限、希望、高级物资配给券、行动力、零件箱容量及使用已有留存券，数量未写不补券数，不把容量当人数/物品或上限当实际回复。显式保留原注随机3个，求援是否另占/共享这三项仍未知，不把七项目录当当前同时可选，不相加各项收益。三重身三种画面按同文合读而全部原件保留；接受提议六份同文原选项共同明确1件珍贵加工品、保留行动力并进入下一区域，但附带生命上限展示标记不能证明额外生命奖励。接受后的对话不自动接入自己找路后的离开确认；该确认三份ZONE_END均没有下一段ID，不假造下一区域位置或执行移动。36个版本页原情景/选项入口保留精确来源，仅资料定位不确定本局画面、菜单或实际变体。刷新保持两组真实非零阅读、情景、选项与来源，实际坏源清旧/手选恢复、重复开窗和父源失效清子窗；默认文字移除父关系等技术词，只显示玩家可读说明。'
limits='复用321实际下载的BWIKI352356两张完整原表，原字符位置/字节/摘要保留；本轮公开网页独立复读随机3个注及三重身文案，不冒称重取完整HTML。17原情景、19完整选项及6展示物品逐项核对bee3与a550，不按编号、背景或展示物品猜服务器父脚本/奖励。三重身同文对话分组仅为阅读，三张画面及全部9原情景仍保留，接受6份展示标记不同的记录均保留，不以生命上限标记追加数值或将加工品当收藏品。离开确认只按原表摆放关联自己找路文献阶段，其真实执行、父归属与实际入口未知。金色凝滞完整菜单抽取/求援是否共享名额、资源变化实际结算、具名券领取张数、三重身完整出现资格/画面与变体选择/实际换区及珍贵加工品完整池仍未知。P3/P2/P1未完成、识别最后；不操作游戏/聊天、不改私人本局、留存券或地图，不给路线建议或概率。'
validation='本机首轮31项必要检查全部通过。实窗复读后仅将player_text中的父关系等术语改为选项属于哪段对话，保留初版完整模型字节并确认函数以外AST不变；最终8项模型复验通过，其余23项未变检查复用，不声称最终重跑31项。最终39项Windows原生唯一检查通过，遍历36个精确原始入口、11段文献对话/10组选项、七项休憩后续、随机3个注与求援名额未知、各类容量与数量不混算、具名券作用与未知张数、三重身三画面/六接受记录不作实际选择、展示生命标记不加奖、接受与自己找路确认边界、ZONE_END无伪后续、两组真实非零阅读经父页刷新保持、实际坏源清旧/手选恢复、重复开窗及父源失效清子窗。最终六张PNG直接查看，另两张与已直接查看首轮图逐字节相同；首轮与复验日志并存。七类外部调用零，临时本局与旧计算上下文不变；原测试窗正常更新、可见响应，正常关闭到启动私人五路径不变。529旧选择器原序保持，现531。仅本机必要验证，未重复全量或未变索引25单测；320全量/原失败/不可用范围仍属历史，下次335。'
nname='verification/sections/331-necessary-attempt2/process.json';wname='verification/sections/331-native-attempt2/actual/window.json';pname='verification/sections/331-native-attempt2/process.json'
n,w,p=map(read,(nname,wname,pname));m=read('verification/sections/331-main-window.json');a=read('verification/sections/331-source-audit.json');v=read('verification/sections/331-root-visual.json')
assert n['passed']and n['methods_ran']==8 and w['passed']and w['qpa']=='windows'and w['qt_exit_code']==0 and w['unique_checks']==39 and w['verification_window_closed']
assert len(w['same_identity_refresh_observations'])==2 and len(w['screenshots'])==8 and len(w['actual_readings'])==10 and all(x==0 for x in w['external_operation_attempts'].values())
assert p['passed']and p['window_receipt_sha256']==sha(wname)
for result in(n,w):
 assert result['source_sha256_before']==result['source_sha256_after']
 for name,h in result['source_sha256_after'].items():assert sha(name)==h,name
assert v['passed']and len(v['final_screenshot_reviews'])==8 and a['ordered_previous529_preserved']and len(a['current_selectors'])==531
assert m['passed']and m['private_entire_normal_close_and_start_interval_unchanged']and m['window_visible_and_responsive']
now=datetime.now(timezone(timedelta(hours=8))).isoformat();pending='<!-- section331-publication-pending -->本地验收完成，普通推送及真实远端核对待完成。'
r={'section':331,'kind':'functional_section','title':title,'new_capability':change,'limitations':[limits],'at_Beijing':now,'branch':'codex/p2-development','necessary_validation':{**pin(nname),'final_model_methods_run':8,'initial31_receipt':'verification/sections/331-necessary-attempt1/process.json','initial31_all_passed':True,'other23_unchanged_checks_reused':True,'scope':pin('verification/sections/331-check-scope/scope.json'),'actual_exit':0},'native_windows_validation':{**pin(wname),'process':pin(pname),'unique_checks':39,'actual_Qt_exit':0,'documented_events':2,'document_scene_groups':11,'original_scenes':17,'document_choice_groups':10,'original_choices':19,'original_source_entries':36,'travel_accept_variants':6,'travel_exit_variants':3,'real_nonzero_refresh_states':2,'actual_MainWindow_entry_exercised':True,'all_seven_real_external_operations_zero':True},'root_visual_review':pin('verification/sections/331-root-visual.json'),'source_audit':pin('verification/sections/331-source-audit.json'),'original_project_window':pin('verification/sections/331-main-window.json'),'source_sha256':n['source_sha256_after'],'validated_source_sha256':w['source_sha256_after'],'full_suite_rerun':False,'last_full_receipt':'verification/full-320/summary.json','last_full_receipt_is_historical_for_this_changed_source':True,'last_full_validation_sha256':sha('verification/full-320/summary.json'),'next_periodic_full_section':335,'P3_complete':False,'P2_complete':False,'P1_complete':False,'private_state_contents_parsed_copied_or_restored':False,'private_state_hashed_locally_for_preservation_only':True,'private_hashes_published':False,'game_operated':False,'chat_sent':False,'cloud_publication_binding':'enclosing_commit','cloud_published':False,'execution_environment':'local_original_windows_project_venv','local_source_parity_required_for_cloud_publication':True}
(ROOT/'verification/sections/331.json').write_bytes(enc(r));details=change+'\n\n'+validation+'\n\n'+limits+'\n\n'+pending
old_wip=subprocess.check_output(['git','show',parent+':WORK_IN_PROGRESS.md'],cwd=ROOT)
prefix=('## 第331节 + '+title+'\n\n'+now+'。'+details+'\n\n以下为历史记录；当前断点以上述331为准。\n\n').replace('\n','\r\n').encode();(ROOT/'WORK_IN_PROGRESS.md').write_bytes(prefix+old_wip)
doc('PROJECT_COMPLETED.md','## 第331节 + '+title+'\n\n'+now+'。'+details+'\n\n'+(ROOT/'PROJECT_COMPLETED.md').read_text('utf8'))
s=(ROOT/'AGENTS.md').read_text('utf8');end=s.index('\n## ',3);doc('AGENTS.md','## 当前续接 · 第331节 + '+title+'\n\n'+details+'\n\n继续P3；332从当前事件前置、完整奖励池和固定地图实际剩余缺口接续，未启动。测试优先本机，保留到期完整范围，下次335；严格低于15%才开始完整收尾。\n'+s[end:])
s=(ROOT/'PROJECT_REQUIREMENTS.md').read_text('utf8');start=s.index('<!-- current-delivery:start -->');end=s.index('<!-- current-delivery:end -->')+len('<!-- current-delivery:end -->');doc('PROJECT_REQUIREMENTS.md',s[:start]+'<!-- current-delivery:start -->\n## 第331节 + '+title+'\n\n'+details+'\n<!-- current-delivery:end -->'+s[end:])
s=(ROOT/'PROJECT_PROGRESS.md').read_text('utf8');old='其余未覆盖完整事件表及其奖励条件';new='金色凝滞菜单实际抽取/求援名额、资源实际结算及具名券领取张数，三重身完整资格/画面及变体选择/真实确认入口/实际换区和珍贵加工品完整池，其余未覆盖完整事件表及其奖励条件';assert s.count(old)==1;doc('PROJECT_PROGRESS.md',s.replace(old,new,1))
cp=read('DEVELOPMENT_CHECKPOINT.json');assert cp['completed_sections']==330 and cp['next_section']==331
for key in('current_section_validation','latest_section_environment','cloud_publication_closeout'):
 if key in cp:cp['historical_before331_'+key]=cp.pop(key)
cp.update(completed_sections=331,latest_functional_section=331,next_section=332,batch_status='P3_SECTION331_LOCAL_ACCEPTED_PUBLICATION_PENDING',next_action='第331节 + '+title+'已本机必要验收；普通推送核对后332接续P3实际剩余缺口，未启动。下次335。',full_validation_due=False)
cp['sections'].append({'number':331,'completion_ref':'p3-section-331','topic':title,'verification':'verification/sections/331.json'});cp['functional_sections_since_latest_requirement'].append(331)
cp['current_section_save']={'section':331,'verification':'verification/sections/331.json','scope':'current_functional_section','binding':'enclosing_commit'};cp['last_verified_cloud_save']['scope']='previous_functional_section'
cp['current_section_validation']={'section':331,'receipt':'verification/sections/331.json','initial31_all_passed':True,'final_model8_passed':True,'other23_reused':True,'native_isolated_window_checks':39,'documented_events':2,'document_scene_groups':11,'original_scenes':17,'document_choice_groups':10,'original_choices':19,'original_source_entries':36,'travel_accept_variants':6,'travel_exit_variants':3,'real_nonzero_refresh_states':2,'full_suite_rerun':False,'last_full_receipt':'verification/full-320/summary.json','last_full_receipt_is_historical_for_current_changes':True}
cp['latest_section_environment']={'section':331,'receipt':'verification/sections/331.json','native_windows':validation,'native_game_or_chat_verified':False,'current_section_full_rerun':False,'last_full_receipt':'verification/full-320/summary.json'}
cp['windows_native_validation']=validation;cp['current_batch'].update(status=cp['batch_status'],completed_sections=331,next_section=332,next_section_started=False,receipt='verification/sections/331.json',batch_closed=False)
cp['policy'].update(current_usage_remaining_percent=100,current_usage_receipt='verification/sections/331-preparation/usage-final.json',verification_execution_preference='local_project_environment',avoid_duplicate_cloud_tests=True)
cp['current_data_versions'].update(current_rest_travel_game_commit='bee3f83c5d60590b5e1cd42b8d09d00ce32ab10d',current_rest_travel_document_revision=352356,current_rest_travel_events=2,current_rest_travel_document_scenes=11,current_rest_travel_original_scenes=17,current_rest_travel_document_choices=10,current_rest_travel_original_choices=19,current_rest_travel_actual_menu_or_travel_verified=False)
(ROOT/'DEVELOPMENT_CHECKPOINT.json').write_bytes(enc(cp))
doc('CLOUD_HANDOFF.md',(ROOT/'CLOUD_HANDOFF.md').read_text('utf8')+'\n<!-- section331-handoff:start -->\n## 第331节 + '+title+'\n\n'+details+'\n<!-- section331-handoff:end -->\n')
out=ROOT/'verification/sections/331-preparation';shutil.copyfile(ROOT/'.cache/open_test_window_331.py',out/'execution-main-window.py')
runpy.run_path(str(ROOT/'scripts/update_cloud_index.py'))['update'](ROOT)
out=ROOT/'verification/sections/331-closeout';out.mkdir();(out/'execution-closeout.py').write_bytes(Path(__file__).read_bytes());(out/'applied.json').write_bytes(enc({'section':331,'local_accepted':True,'ordinary_cloud_publication_verified':False,'next332_started':False,'at_Beijing':now}))
print(json.dumps({'section':331,'local_accepted':True,'ordinary_publication_pending':True},ensure_ascii=False))
