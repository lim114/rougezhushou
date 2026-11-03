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
parent='d27d96f827d09b31ad9b4b2a3e98745c5c1c6c62'
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()==parent
assert subprocess.check_output(['git','branch','--show-current'],cwd=ROOT).decode().strip()=='codex/p2-development'
title='大红按钮、制图桌和手术祭坛的逐步选项、奖励与作战预览'
change='新增三个事件的逐步查阅窗口，将原来平铺的11个选项按文献明确对应到10个情景，只显示所选情景有证的选项，支持查看结果、手动进入后续情景及返回开头。具名收藏品显示生命蓝图与破碎噩兆的说明；粗糙涂鸦只注明1件珍贵收藏品，不虚构随机物品。大红按钮的明确战斗选项可直达当前灰坑固定地图、敌人和出怪资料。旧日重燃条件页只在这三项显示入口，当前版本情景目录也可从对应10项准确进入；其它事件不显示专用入口。刷新保留情景、选项、页签和阅读，资料失效清除旧内容与入口，恢复后手动重选，切换事件、重复开窗和关闭父窗均关闭旧子窗。'
limits='依据BWIKI调查记录固定修订352356的三张原表，逐格对照bee3当前游戏文本和明确nextSceneId，并核对2件收藏品及唯一灰坑关卡；这是文献父子关系，不是恢复服务器父选项脚本。11个原选项已在316平铺资料中存在，本节新增的是情景归属和逐步阅读，不重复计原选项为新增数据。战斗入口按原表具名灰坑及游戏battle图标核对，原type为TRADE，不能按BATTLE类型误排。完整出现前置、隐藏分支、实际是否可选、制图桌完整随机池和手术祭坛半生命上限的整数处理仍未知。未恢复本局选择、领取或战斗执行，不计算资源扣除，不改本局记忆或旧数值。P3/P2/P1未完成，识别优化最后。'
validation='实际55项必要检查和29项Windows原生唯一检查通过；11个选项、10个情景逐项检查，实际主窗口经两种入口打开逐步阅读和灰坑原图，2组非零滚动选区经父页刷新保持，真实公开文件副本损坏清旧/恢复手选及父子窗关闭通过。六张最终截图均已直接查看。七类采样、聊天和凭证调用均为零，临时本局与旧计算上下文不变；原项目测试窗口正常更新、可见响应，正常关闭至启动的私人五路径不变。509旧维护选择器原序保留，现511。所有测试在本机执行；本节不重跑未受影响的已通过全量，完整320范围与失败/不可用原件保留作历史证据，下次定期全量335。符号链接1314、历史私样本及游戏聊天仍未计通过。'
nname='verification/sections/321-necessary-attempt1/process.json';wname='verification/sections/321-native-attempt1/actual/window.json';pname='verification/sections/321-native-attempt1/process.json'
n,w,p=map(read,(nname,wname,pname));m=read('verification/sections/321-main-window.json');a=read('verification/sections/321-source-audit.json');v=read('verification/sections/321-root-visual.json')
assert n['passed']and n['methods_ran']==55 and n['exit_code']==0
assert w['passed']and w['qpa']=='windows'and w['qt_exit_code']==0 and w['unique_checks']==29 and w['verification_window_closed']
assert len(w['same_identity_refresh_observations'])==2 and len(w['screenshots'])==6 and all(x==0 for x in w['external_operation_attempts'].values())
assert len([x for x in w['actual_readings']if 'choice'in x])==11
assert p['passed']and p['window_receipt_sha256']==sha(wname)
for result in(n,w):
 assert result['source_sha256_before']==result['source_sha256_after']
 for name,h in result['source_sha256_after'].items():assert sha(name)==h,name
assert v['passed']and len(v['images_actually_viewed_by_root'])==6 and a['ordered_previous509_preserved']and len(a['current_selectors'])==511
assert m['passed']and m['private_entire_normal_close_and_start_interval_unchanged']and m['window_visible_and_responsive']
now=datetime.now(timezone(timedelta(hours=8))).isoformat();pending='<!-- section321-publication-pending -->本地验收完成，普通推送及真实远端核对待完成。'
r={'section':321,'kind':'functional_section','title':title,'new_capability':change,'limitations':[limits],'at_Beijing':now,'branch':'codex/p2-development','necessary_validation':{**pin(nname),'methods_run':55,'actual_exit':0},'native_windows_validation':{**pin(wname),'process':pin(pname),'unique_checks':29,'actual_Qt_exit':0,'documented_choices_checked':11,'documented_scenes_checked':10,'real_nonzero_refresh_states':2,'actual_MainWindow_entry_exercised':True,'all_seven_real_external_operations_zero':True},'root_visual_review':pin('verification/sections/321-root-visual.json'),'source_audit':pin('verification/sections/321-source-audit.json'),'original_project_window':pin('verification/sections/321-main-window.json'),'source_sha256':n['source_sha256_after'],'validated_source_sha256':w['source_sha256_after'],'full_suite_rerun':False,'last_full_receipt':'verification/full-320/summary.json','last_full_receipt_is_historical_for_this_changed_source':True,'last_full_validation_sha256':sha('verification/full-320/summary.json'),'next_periodic_full_section':335,'P3_complete':False,'P2_complete':False,'P1_complete':False,'private_state_contents_parsed_copied_or_restored':False,'private_state_hashed_locally_for_preservation_only':True,'private_hashes_published':False,'game_operated':False,'chat_sent':False,'cloud_publication_binding':'enclosing_commit','cloud_published':False,'execution_environment':'local_original_windows_project_venv','local_source_parity_required_for_cloud_publication':True}
(ROOT/'verification/sections/321.json').write_bytes(enc(r));details=change+'\n\n'+validation+'\n\n'+limits+'\n\n'+pending
old_wip=subprocess.check_output(['git','show',parent+':WORK_IN_PROGRESS.md'],cwd=ROOT)
prefix=('## 第321节 + '+title+'\n\n'+now+'。'+details+'\n\n以下为历史记录；当前断点以上述321为准。\n\n').replace('\n','\r\n').encode('utf8');(ROOT/'WORK_IN_PROGRESS.md').write_bytes(prefix+old_wip)
doc('PROJECT_COMPLETED.md','## 第321节 + '+title+'\n\n'+now+'。'+details+'\n\n'+(ROOT/'PROJECT_COMPLETED.md').read_text('utf8'))
s=(ROOT/'AGENTS.md').read_text('utf8');end=s.index('\n## ',3);doc('AGENTS.md','## 当前续接 · 第321节 + '+title+'\n\n'+details+'\n\n继续P3；322从当前事件前置、完整奖励池和固定地图的实际剩余缺口接续，未启动。测试优先本机，保留到期完整范围，下次335；严格低于15%才开始完整收尾。\n'+s[end:])
s=(ROOT/'PROJECT_REQUIREMENTS.md').read_text('utf8');start=s.index('<!-- current-delivery:start -->');end=s.index('<!-- current-delivery:end -->')+len('<!-- current-delivery:end -->');doc('PROJECT_REQUIREMENTS.md',s[:start]+'<!-- current-delivery:start -->\n## 第321节 + '+title+'\n\n'+details+'\n<!-- current-delivery:end -->'+s[end:])
s=(ROOT/'PROJECT_PROGRESS.md').read_text('utf8');old='制图桌完整出现前置/节点类型、其余新增事件完整前置';new='大红按钮/制图桌/手术祭坛文献以外的隐藏选项与服务器实际条件、制图桌完整出现前置/节点类型、其余新增事件完整前置';assert s.count(old)==1;doc('PROJECT_PROGRESS.md',s.replace(old,new,1))
cp=read('DEVELOPMENT_CHECKPOINT.json');assert cp['completed_sections']==320 and cp['next_section']==321
for key in('current_section_validation','latest_section_environment','cloud_publication_closeout'):
 if key in cp:cp['historical_before321_'+key]=cp.pop(key)
cp.update(completed_sections=321,latest_functional_section=321,next_section=322,batch_status='P3_SECTION321_LOCAL_ACCEPTED_PUBLICATION_PENDING',next_action='第321节 + '+title+'已本机必要验收；普通推送核对后322接续P3实际剩余缺口，未启动。下次定期全量335。',full_validation_due=False)
cp['sections'].append({'number':321,'completion_ref':'p3-section-321','topic':title,'verification':'verification/sections/321.json'});cp['functional_sections_since_latest_requirement'].append(321)
cp['current_section_save']={'section':321,'verification':'verification/sections/321.json','scope':'current_functional_section','binding':'enclosing_commit'};cp['last_verified_cloud_save']['scope']='previous_functional_section'
cp['current_section_validation']={'section':321,'receipt':'verification/sections/321.json','necessary_methods_passed':55,'native_isolated_window_checks':29,'documented_choices_checked':11,'documented_scenes_checked':10,'real_nonzero_refresh_states':2,'full_suite_rerun':False,'last_full_receipt':'verification/full-320/summary.json','last_full_receipt_is_historical_for_current_changes':True}
cp['latest_section_environment']={'section':321,'receipt':'verification/sections/321.json','native_windows':validation,'native_game_or_chat_verified':False,'current_section_full_rerun':False,'last_full_receipt':'verification/full-320/summary.json'}
cp['windows_native_validation']=validation;cp['current_batch'].update(status=cp['batch_status'],completed_sections=321,next_section=322,next_section_started=False,receipt='verification/sections/321.json',batch_closed=False)
cp['policy'].update(current_usage_remaining_percent=71,current_usage_receipt='verification/sections/321-preparation/usage-final.json',verification_execution_preference='local_project_environment',avoid_duplicate_cloud_tests=True)
cp['current_data_versions'].update(documented_event_flows_game_commit='bee3f83c5d60590b5e1cd42b8d09d00ce32ab10d',documented_event_flows_community_revision=352356,documented_event_flows_events=3,documented_event_flows_scenes=10,documented_event_flows_choices=11,documented_event_flows_full_game_prerequisites_verified=False)
(ROOT/'DEVELOPMENT_CHECKPOINT.json').write_bytes(enc(cp))
doc('CLOUD_HANDOFF.md',(ROOT/'CLOUD_HANDOFF.md').read_text('utf8')+'\n<!-- section321-handoff:start -->\n## 第321节 + '+title+'\n\n'+details+'\n<!-- section321-handoff:end -->\n')
out=ROOT/'verification/sections/321-preparation';shutil.copyfile(ROOT/'.cache/open_test_window_321.py',out/'execution-main-window.py')
runpy.run_path(str(ROOT/'scripts/update_cloud_index.py'))['update'](ROOT)
out=ROOT/'verification/sections/321-closeout';out.mkdir();(out/'execution-closeout.py').write_bytes(Path(__file__).read_bytes());(out/'applied.json').write_bytes(enc({'section':321,'local_accepted':True,'ordinary_cloud_publication_verified':False,'next322_started':False,'at_Beijing':now}))
print(json.dumps({'section':321,'local_accepted':True,'ordinary_publication_pending':True},ensure_ascii=False))
