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
parent='2593e7286b13d72d8c51a94a719983dfb9c424f8'
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()==parent
assert subprocess.check_output(['git','branch','--show-current'],cwd=ROOT).decode().strip()=='codex/p2-development'
title='窥视箱中的关键藏品条件、同文案分歧与双首领地图入口'
change='当前“版本与更新”的窥视箱中4个情景和7份原选项均可直达独立条件阅读窗，按文献整理5组选项。祭日之契分为尚未确认、持有和未持有三种本页对照；未持有时禁用对应的后续与作战入口，持有也不冒称完整出现资格。文献明确关联的混沌源阶理论与失恒常量各自打开当前固定原图、敌人、出怪及奖励资料。三份同文案的保护证据记录保留全部差异，只跟随共同明确的后续，不选定实际使用版本。“打印”确认项的真实父场景与作战未绑定，不借相邻地图；黑色石板后续也不自动补入该项。刷新保留情景、选项、条件、页签与阅读，条件变更关闭旧地图，资料坏源清旧、恢复手选、重复开窗及父窗关闭均清理旧子窗。'
limits='依据BWIKI调查记录固定修订352356原表（保留调查中标记）与当前bee3游戏记录。复用321实际下载的同SHA原HTTP，单独摘出本事件两张表，不重复下载整个页面。原表失恒常量链接位于NEXT选项，不移动到相邻ZONE_END“打印”记录；文献中的主选项分组不冒充游戏父脚本。保留4情景、5组选项及全部7原记录，3份相同文案记录的实际来源选择、内部机制物品效果与真实父子关系仍未知。祭日持有仅是原文列出的条件对照，不是自动本局读取、完整资格或实际结局判断。未证明隐藏分支、实际战斗进入、服务器生成条件及完整奖励；不提供路线建议或概率，不操作游戏、聊天，不改本局持有、私人状态和旧计算。P3/P2/P1未完成，识别优化最后。'
validation='实际53项必要检查与31项Windows原生唯一检查通过；4情景/5组选项/7原记录和同文3变体均核对，实际主窗口从情景与原选项目录进入，分别打开两份首领固定地图。三态条件、未持有阻断、切换关闭旧地图、明确后续不虚接确认、未绑定作战无入口、两组非零滚动选区经父页刷新保持、公开文件实际损坏清旧/恢复手选及父子窗生命周期通过。八张最终截图均已直接查看，七类采样/聊天/凭证调用为零，临时本局和旧计算上下文不变。原项目实际测试窗口已更新、可见响应，正常关闭至启动期间私人五路径不变。511旧维护选择器原序保持，现513；只在本机运行必要检查，不重复已通过且未变的全量和索引单测。320完整范围、失败和不可用记录保留作历史证据，不当本节全量；下次定期全量335。'
nname='verification/sections/322-necessary-attempt1/process.json';wname='verification/sections/322-native-attempt1/actual/window.json';pname='verification/sections/322-native-attempt1/process.json'
n,w,p=map(read,(nname,wname,pname));m=read('verification/sections/322-main-window.json');a=read('verification/sections/322-source-audit.json');v=read('verification/sections/322-root-visual.json')
assert n['passed']and n['methods_ran']==53 and n['exit_code']==0
assert w['passed']and w['qpa']=='windows'and w['qt_exit_code']==0 and w['unique_checks']==31 and w['verification_window_closed']
assert len(w['same_identity_refresh_observations'])==2 and len(w['screenshots'])==8 and all(x==0 for x in w['external_operation_attempts'].values())
assert len([x for x in w['actual_readings']if 'choice'in x])==5
assert p['passed']and p['window_receipt_sha256']==sha(wname)
for result in(n,w):
 assert result['source_sha256_before']==result['source_sha256_after']
 for name,h in result['source_sha256_after'].items():assert sha(name)==h,name
assert v['passed']and len(v['images_actually_viewed_by_root'])==8 and a['ordered_previous511_preserved']and len(a['current_selectors'])==513
assert m['passed']and m['private_entire_normal_close_and_start_interval_unchanged']and m['window_visible_and_responsive']
now=datetime.now(timezone(timedelta(hours=8))).isoformat();pending='<!-- section322-publication-pending -->本地验收完成，普通推送及真实远端核对待完成。'
r={'section':322,'kind':'functional_section','title':title,'new_capability':change,'limitations':[limits],'at_Beijing':now,'branch':'codex/p2-development','necessary_validation':{**pin(nname),'methods_run':53,'actual_exit':0},'native_windows_validation':{**pin(wname),'process':pin(pname),'unique_checks':31,'actual_Qt_exit':0,'documented_option_groups_checked':5,'primary_choice_records_checked':7,'documented_scenes_checked':4,'real_nonzero_refresh_states':2,'actual_MainWindow_entry_exercised':True,'all_seven_real_external_operations_zero':True},'root_visual_review':pin('verification/sections/322-root-visual.json'),'source_audit':pin('verification/sections/322-source-audit.json'),'original_project_window':pin('verification/sections/322-main-window.json'),'source_sha256':n['source_sha256_after'],'validated_source_sha256':w['source_sha256_after'],'full_suite_rerun':False,'last_full_receipt':'verification/full-320/summary.json','last_full_receipt_is_historical_for_this_changed_source':True,'last_full_validation_sha256':sha('verification/full-320/summary.json'),'next_periodic_full_section':335,'P3_complete':False,'P2_complete':False,'P1_complete':False,'private_state_contents_parsed_copied_or_restored':False,'private_state_hashed_locally_for_preservation_only':True,'private_hashes_published':False,'game_operated':False,'chat_sent':False,'cloud_publication_binding':'enclosing_commit','cloud_published':False,'execution_environment':'local_original_windows_project_venv','local_source_parity_required_for_cloud_publication':True}
(ROOT/'verification/sections/322.json').write_bytes(enc(r));details=change+'\n\n'+validation+'\n\n'+limits+'\n\n'+pending
old_wip=subprocess.check_output(['git','show',parent+':WORK_IN_PROGRESS.md'],cwd=ROOT)
prefix=('## 第322节 + '+title+'\n\n'+now+'。'+details+'\n\n以下为历史记录；当前断点以上述322为准。\n\n').replace('\n','\r\n').encode('utf8');(ROOT/'WORK_IN_PROGRESS.md').write_bytes(prefix+old_wip)
doc('PROJECT_COMPLETED.md','## 第322节 + '+title+'\n\n'+now+'。'+details+'\n\n'+(ROOT/'PROJECT_COMPLETED.md').read_text('utf8'))
s=(ROOT/'AGENTS.md').read_text('utf8');end=s.index('\n## ',3);doc('AGENTS.md','## 当前续接 · 第322节 + '+title+'\n\n'+details+'\n\n继续P3；323从当前事件前置、完整奖励池和固定地图的实际剩余缺口接续，未启动。测试优先本机，保留到期完整范围，下次335；严格低于15%才开始完整收尾。\n'+s[end:])
s=(ROOT/'PROJECT_REQUIREMENTS.md').read_text('utf8');start=s.index('<!-- current-delivery:start -->');end=s.index('<!-- current-delivery:end -->')+len('<!-- current-delivery:end -->');doc('PROJECT_REQUIREMENTS.md',s[:start]+'<!-- current-delivery:start -->\n## 第322节 + '+title+'\n\n'+details+'\n<!-- current-delivery:end -->'+s[end:])
s=(ROOT/'PROJECT_PROGRESS.md').read_text('utf8');old='其余新增事件完整前置';new='窥视箱中三份同文案记录的实际选择依据、“打印”确认项的真实父情景及精确作战、其余新增事件完整前置';assert s.count(old)==1;doc('PROJECT_PROGRESS.md',s.replace(old,new,1))
cp=read('DEVELOPMENT_CHECKPOINT.json');assert cp['completed_sections']==321 and cp['next_section']==322
for key in('current_section_validation','latest_section_environment','cloud_publication_closeout'):
 if key in cp:cp['historical_before322_'+key]=cp.pop(key)
cp.update(completed_sections=322,latest_functional_section=322,next_section=323,batch_status='P3_SECTION322_LOCAL_ACCEPTED_PUBLICATION_PENDING',next_action='第322节 + '+title+'已本机必要验收；普通推送核对后323接续P3实际剩余缺口，未启动。下次定期全量335。',full_validation_due=False)
cp['sections'].append({'number':322,'completion_ref':'p3-section-322','topic':title,'verification':'verification/sections/322.json'});cp['functional_sections_since_latest_requirement'].append(322)
cp['current_section_save']={'section':322,'verification':'verification/sections/322.json','scope':'current_functional_section','binding':'enclosing_commit'};cp['last_verified_cloud_save']['scope']='previous_functional_section'
cp['current_section_validation']={'section':322,'receipt':'verification/sections/322.json','necessary_methods_passed':53,'native_isolated_window_checks':31,'documented_option_groups_checked':5,'primary_choice_records_checked':7,'documented_scenes_checked':4,'real_nonzero_refresh_states':2,'full_suite_rerun':False,'last_full_receipt':'verification/full-320/summary.json','last_full_receipt_is_historical_for_current_changes':True}
cp['latest_section_environment']={'section':322,'receipt':'verification/sections/322.json','native_windows':validation,'native_game_or_chat_verified':False,'current_section_full_rerun':False,'last_full_receipt':'verification/full-320/summary.json'}
cp['windows_native_validation']=validation;cp['current_batch'].update(status=cp['batch_status'],completed_sections=322,next_section=323,next_section_started=False,receipt='verification/sections/322.json',batch_closed=False)
cp['policy'].update(current_usage_remaining_percent=70,current_usage_receipt='verification/sections/322-preparation/usage-final.json',verification_execution_preference='local_project_environment',avoid_duplicate_cloud_tests=True)
cp['current_data_versions'].update(box_event_game_commit='bee3f83c5d60590b5e1cd42b8d09d00ce32ab10d',box_event_document_revision=352356,box_event_scenes=4,box_event_documented_option_groups=5,box_event_primary_variants=7,box_event_actual_variant_selected=None,box_event_full_game_prerequisites_verified=False)
(ROOT/'DEVELOPMENT_CHECKPOINT.json').write_bytes(enc(cp))
doc('CLOUD_HANDOFF.md',(ROOT/'CLOUD_HANDOFF.md').read_text('utf8')+'\n<!-- section322-handoff:start -->\n## 第322节 + '+title+'\n\n'+details+'\n<!-- section322-handoff:end -->\n')
out=ROOT/'verification/sections/322-preparation';shutil.copyfile(ROOT/'.cache/open_test_window_322.py',out/'execution-main-window.py')
runpy.run_path(str(ROOT/'scripts/update_cloud_index.py'))['update'](ROOT)
out=ROOT/'verification/sections/322-closeout';out.mkdir();(out/'execution-closeout.py').write_bytes(Path(__file__).read_bytes());(out/'applied.json').write_bytes(enc({'section':322,'local_accepted':True,'ordinary_cloud_publication_verified':False,'next323_started':False,'at_Beijing':now}))
print(json.dumps({'section':322,'local_accepted':True,'ordinary_publication_pending':True},ensure_ascii=False))
