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
parent='524567b9d9c0d483ecb8b2bcc78dd5ded434e9fb';assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()==parent
assert subprocess.check_output(['git','branch','--show-current'],cwd=ROOT).decode().strip()=='codex/p2-development'
title='特殊地形的中文效果说明、分类查找与格图定位'
change='固定地图加入特殊地形中文名称、每格自身参数的效果说明与注意事项，可按地形类别查找全部对应格子，再选择具体格子联动说明和高亮。十九类原始地块中十八类取得名称依据；医疗符文、特种战术点、活性源石和热泵通道仅解释本格明确数值，不借其他关卡或默认值。通道入口/出口不按距离或编号猜配对，尚未校准的格子只在格图定位；原图仍严格沿用已有校准。刷新保留类别、格子、页签及阅读位置，坏源清空旧内容；修正实测发现的格子选择与下拉框不同步问题。'
limits='名称依据固定BWIKI与PRTS完整地形文献；参数字段含义另有明确标为缓存摘要、未取得完整修订原件的文献证据，不能冒称当前全文或服务器核验。tile_pollution_roadf仍缺准确名称和效果，不凭变量片段猜成污染区。首次生效、重触发、结束时刻、实际通道配对和本局最终面板未证；本页不把地形效果写入计算。除已有校准位置外的格子、实际脚点与绝对精度仍待核验。未操作游戏、未发聊天、未加入路线建议或概率；P3/P2/P1未完成，识别最后。'
validation='本机38项必要测试与24项原生窗口唯一检查通过，实际从通用战斗预览进入九组真实地形，验证类型交集、精确格子、高亮、无原图校准时不猜位置、两组非零阅读和父刷新、坏源清除与恢复手选、关闭所属窗口；七类真实外部操作均零。首次原生因Python元组在Qt下拉框查询失败，已保留原失败及改前源码，改为稳定字符串身份后两套验证均通过。最终五张实际截图主代理逐张复查。原项目测试窗正常更新并可见响应，完整关闭/启动区间私人五路径保持。572旧选择器原序保留，新加2个共574。350完整检查仅为本节前历史证据，本节不重复全量，下一定期365；1314符号链接、历史Windows/私样本、游戏聊天等未冒称通过。索引实现不变，复用25项旧单测并实际验证当前索引/要求。按授权继续至370后暂停。'
nname='verification/sections/353-necessary-attempt2/process.json';wname='verification/sections/353-native-attempt2/actual/window.json';pname='verification/sections/353-native-attempt2/process.json'
n,w,p=map(read,(nname,wname,pname));m=read('verification/sections/353-main-window.json');a=read('verification/sections/353-source-audit.json');v=read('verification/sections/353-root-visual.json')
assert n['passed']and n['methods_ran']==38 and w['passed']and w['qpa']=='windows'and w['qt_exit_code']==0 and w['unique_checks']==24 and w['verification_window_closed']
assert len(w['same_identity_refresh_observations'])==2 and len(w['screenshots'])==5 and len(w['actual_readings'])==9 and all(x==0 for x in w['external_operation_attempts'].values())
assert p['passed']and p['window_receipt_sha256']==sha(wname)
for result in(n,w):
 assert result['source_sha256_before']==result['source_sha256_after']
 for name,h in result['source_sha256_after'].items():assert sha(name)==h,name
assert v['passed']and len(v['final_screenshot_reviews'])==5 and a['ordered_previous572_preserved']and len(a['current_selectors'])==574
assert m['passed']and m['private_entire_normal_close_and_start_interval_unchanged']and m['window_visible_and_responsive']
now=datetime.now(timezone(timedelta(hours=8))).isoformat();pending='<!-- section353-publication-pending -->本地验收完成，普通推送及真实远端核对待完成。'
r={'section':353,'kind':'functional_section','title':title,'new_capability':change,'limitations':[limits],'at_Beijing':now,'branch':'codex/p2-development','necessary_validation':{**pin(nname),'methods_run':n['methods_ran'],'actual_exit':0},'native_windows_validation':{**pin(wname),'process':pin(pname),'unique_checks':w['unique_checks'],'actual_Qt_exit':0,'terrain_subjects':9,'documented_terrain_names':18,'raw_tile_kinds':19,'real_nonzero_refresh_states':2,'actual_MainWindow_entry_and_close_exercised':True,'all_seven_real_external_operations_zero':True},'root_visual_review':pin('verification/sections/353-root-visual.json'),'source_audit':pin('verification/sections/353-source-audit.json'),'original_project_window':pin('verification/sections/353-main-window.json'),'source_sha256':n['source_sha256_after'],'validated_source_sha256':w['source_sha256_after'],'full_suite_rerun':False,'last_full_receipt':'verification/full-350/summary.json','last_full_receipt_is_historical_for_this_changed_source':True,'last_full_validation_sha256':sha('verification/full-350/summary.json'),'next_periodic_full_section':365,'P3_complete':False,'P2_complete':False,'P1_complete':False,'private_state_contents_parsed_copied_or_restored':False,'private_state_hashed_locally_for_preservation_only':True,'private_hashes_published':False,'game_operated':False,'chat_sent':False,'cloud_publication_binding':'enclosing_commit','cloud_published':False,'execution_environment':'local_original_windows_project_venv','local_source_parity_required_for_cloud_publication':True}
(ROOT/'verification/sections/353.json').write_bytes(enc(r));details=change+'\n\n'+validation+'\n\n'+limits+'\n\n'+pending
old_wip=(ROOT/'WORK_IN_PROGRESS.md').read_bytes();(ROOT/'WORK_IN_PROGRESS.md').write_bytes(('## 第353节 + '+title+'\n\n'+now+'。'+details+'\n\n以下为历史记录；当前断点以上述353为准。\n\n').replace('\n','\r\n').encode()+old_wip)
doc('PROJECT_COMPLETED.md','## 第353节 + '+title+'\n\n'+now+'。'+details+'\n\n'+(ROOT/'PROJECT_COMPLETED.md').read_text('utf8'))
s=(ROOT/'AGENTS.md').read_text('utf8');end=s.index('\n## 项目级最高优先要求');note='下一到期完整检查须给304/305两份full320验证脚本显式传入--source-freeze及当轮根声明冻结文件；默认320仅供历史绑定。350原失败与组合复验见verification/full-350/summary.json。312补充窗口采用既有120秒默认，304/305显式传入当轮source-freeze。'
doc('AGENTS.md','## 当前续接 · 第353节 + '+title+'\n\n'+details+'\n\n继续P3；354从实际剩余节点/事件条件、掉落和固定地图缺口接续，未启动。特殊地形说明不替代本局生效或未核验原图校准。通用页面不恢复独立版本栏目。用户当前授权继续至370，完整收尾后暂停。只跑本机必要检查；下一全量365，严格低于15%才开始当前完整小节收尾。\n\n'+note+'\n'+s[end:])
s=(ROOT/'PROJECT_REQUIREMENTS.md').read_text('utf8');start=s.index('<!-- current-delivery:start -->');end=s.index('<!-- current-delivery:end -->')+len('<!-- current-delivery:end -->');doc('PROJECT_REQUIREMENTS.md',s[:start]+'<!-- current-delivery:start -->\n## 第353节 + '+title+'\n\n'+details+'\n<!-- current-delivery:end -->'+s[end:])
s=(ROOT/'PROJECT_PROGRESS.md').read_text('utf8');s=s.replace('更新：2026-10-23。','更新：2026-10-24。');old='当前33引用/13原图的其余地块';assert s.count(old)==1;s=s.replace(old,'未命名特殊地块的准确名称/效果、地形首次生效与实际通道配对；当前33引用/13原图的其余地块',1);doc('PROJECT_PROGRESS.md',s)
cp=read('DEVELOPMENT_CHECKPOINT.json');assert cp['completed_sections']==352 and cp['next_section']==353
for key in('current_section_validation','latest_section_environment','cloud_publication_closeout'):
 if key in cp:cp['historical_before353_'+key]=cp.pop(key)
cp.update(completed_sections=353,latest_functional_section=353,next_section=354,batch_status='P3_SECTION353_LOCAL_ACCEPTED_PUBLICATION_PENDING',next_action='第353节 + '+title+'已本机必要验收；普通推送核对后354接续P3实际剩余缺口，未启动。下次365。',full_validation_due=False)
cp['sections'].append({'number':353,'completion_ref':'p3-section-353','topic':title,'verification':'verification/sections/353.json'});cp['functional_sections_since_latest_requirement'].append(353)
cp['current_section_save']={'section':353,'verification':'verification/sections/353.json','scope':'current_functional_section','binding':'enclosing_commit'};cp['last_verified_cloud_save']['scope']='previous_functional_section'
cp['current_section_validation']={'section':353,'receipt':'verification/sections/353.json','methods_run':n['methods_ran'],'native_isolated_window_checks':w['unique_checks'],'terrain_subjects':9,'documented_terrain_names':18,'raw_tile_kinds':19,'real_nonzero_refresh_states':2,'full_suite_rerun':False,'last_full_receipt':'verification/full-350/summary.json','last_full_receipt_is_historical_for_current_changes':True}
cp['latest_section_environment']={'section':353,'receipt':'verification/sections/353.json','native_windows':validation,'native_game_or_chat_verified':False,'current_section_full_rerun':False,'last_full_receipt':'verification/full-350/summary.json'}
cp['windows_native_validation']=validation;cp['current_batch'].update(status=cp['batch_status'],completed_sections=353,next_section=354,next_section_started=False,receipt='verification/sections/353.json',batch_closed=False)
cp['policy'].update(verification_execution_preference='local_project_environment',avoid_duplicate_cloud_tests=True)
cp['current_data_versions'].update(current_terrain_raw_kinds=19,current_terrain_documented_names=18,current_terrain_actual_execution_verified=False)
cp['current_available_full_validation']['historical_for_current_changed_source']=True
cp['current_available_full_validation']['current_worktree_validation_authority']=False
cp['last_full_validation']['historical_for_current_changed_source']=True
(ROOT/'DEVELOPMENT_CHECKPOINT.json').write_bytes(enc(cp))
doc('CLOUD_HANDOFF.md',(ROOT/'CLOUD_HANDOFF.md').read_text('utf8')+'\n<!-- section353-handoff:start -->\n## 第353节 + '+title+'\n\n'+details+'\n<!-- section353-handoff:end -->\n')
out=ROOT/'verification/sections/353-closeout';out.mkdir();shutil.copyfile(ROOT/'.cache/open_test_window_353.py',out/'execution-main-window.py')
runpy.run_path(str(ROOT/'scripts/update_cloud_index.py'))['update'](ROOT)
(out/'execution-closeout.py').write_bytes(Path(__file__).read_bytes());(out/'applied.json').write_bytes(enc({'section':353,'local_accepted':True,'ordinary_cloud_publication_verified':False,'next354_started':False,'at_Beijing':now}))
print(json.dumps({'section':353,'local_accepted':True,'ordinary_publication_pending':True},ensure_ascii=False))
