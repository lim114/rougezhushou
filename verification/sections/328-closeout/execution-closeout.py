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
parent='ab25ca9766c480f09dc149dd37467a186c24db63'
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()==parent
assert subprocess.check_output(['git','branch','--show-current'],cwd=ROOT).decode().strip()=='codex/p2-development'
title='湖中仙女的阶段、重复投入与两种结果'
change='新增湖中仙女完整固定原表的10段对话与10份原选项，按14个阶段选项关系分开阅读。询问、已捞出磁石、已捞出破损手表不混为一轮；拒绝和离开跨三个阶段出现时先选阶段，不默认最初遇见，刷新保持阶段提示。原表合写的重复投入按明确注记与当前唯一明文后续单列，不把两条同标题继续投入误合并。原始随机继续选项保持没有指定后续，两种记载结果各有独立查看按钮，不替本局选结果、不同时计奖励；每次明确代价1源石锭只显示本次，礼物分支明确1件珍贵收藏品而不猜具体池。两项作战确认直达326配置阅读及固定地图，战斗页反查回精确阶段；未限定版本保留普通/紧急配置，明确紧急排除普通，不默认本局版本。版本页20个原场景/选项入口可直接查阅或要求先选阶段。刷新保留两组真实非零阅读、阶段、选项、已选配置和嵌套地图；实际资料损坏清旧并手选恢复、可选地图源失败与完整对话隔离、重复打开及父窗关闭清理全部子窗。默认中文只讲阶段、代价、结果和未知。'
limits='复用321真实下载的BWIKI352356原HTTP与326核过摘要的完整湖中表摘录，保留精确字节与字符位置；公开网页文字独立复读不冒充新HTML下载。10段当前对话和10份完整原选项逐项比较bee3与a550基准。磁石后继续投入以原表明确重复注及唯一明文后续定位破表，不按编号猜父脚本；随机继续项仍为NEXT_PROB且nextSceneId为空，两种结果是文献分支而非恢复的本局脚本。1为单次文案代价而非累计投入；1件珍贵收藏品不等于已恢复具体奖励池或实际发放。完整服务器资格、实际重复脚本/父关系、实际随机结果与奖励池仍未知，不补概率、不自动支付或领取、不改本局。P3/P2/P1未完成，识别最后，不操作游戏或聊天，不覆盖私人配置，不提供路线建议。'
validation='本机100项相关必要检查通过，资料可重复构建字节核对通过；原生Windows临时MainWindow共39项唯一检查通过，遍历10段对话14个阶段选项关系、跨阶段同选项先选阶段、磁石与手表分离、随机无默认后续且两个结果独立查阅、1件珍贵奖励未知池、两项精确作战及反查阶段、当前紧急固定地图、两组真实非零阅读状态经父页刷新保留、公开副本实际损坏清旧/手选恢复、可选地图源独立失败及完整子窗关闭。8张实际PNG全部直接查看。七类外部调用零，临时本局与旧计算上下文不变；原项目测试窗已正常更新、可见响应且前台，正常关闭至启动私人五路径不变。523旧选择器原序保留，现525；未重复已通过全量或未变索引25单测，320全量回执/失败/不可用原件仍属历史，下次335。两次构建准备失败及一次验收文件生成时的元组格式断言均保留，不伪装为功能测试通过。'
nname='verification/sections/328-necessary-attempt1/process.json';wname='verification/sections/328-native-attempt1/actual/window.json';pname='verification/sections/328-native-attempt1/process.json'
n,w,p=map(read,(nname,wname,pname));m=read('verification/sections/328-main-window.json');a=read('verification/sections/328-source-audit.json');v=read('verification/sections/328-root-visual.json')
assert n['passed']and n['methods_ran']==100 and w['passed']and w['qpa']=='windows'and w['qt_exit_code']==0 and w['unique_checks']==39 and w['verification_window_closed']
assert len(w['same_identity_refresh_observations'])==2 and len(w['screenshots'])==8 and len(w['actual_readings'])==14 and all(x==0 for x in w['external_operation_attempts'].values())
assert p['passed']and p['window_receipt_sha256']==sha(wname)
for result in(n,w):
 assert result['source_sha256_before']==result['source_sha256_after']
 for name,h in result['source_sha256_after'].items():assert sha(name)==h,name
assert v['passed']and len(v['final_screenshot_reviews'])==8 and a['ordered_previous523_preserved']and len(a['current_selectors'])==525
assert m['passed']and m['private_entire_normal_close_and_start_interval_unchanged']and m['window_visible_and_responsive']
now=datetime.now(timezone(timedelta(hours=8))).isoformat();pending='<!-- section328-publication-pending -->本地验收完成，普通推送及真实远端核对待完成。'
r={'section':328,'kind':'functional_section','title':title,'new_capability':change,'limitations':[limits],'at_Beijing':now,'branch':'codex/p2-development','necessary_validation':{**pin(nname),'methods_run':100,'actual_exit':0},'native_windows_validation':{**pin(wname),'process':pin(pname),'unique_checks':39,'actual_Qt_exit':0,'documented_scenes':10,'original_choices':10,'scene_choice_references':14,'separate_documented_random_outcomes':2,'exact_battle_choice_links':2,'real_nonzero_refresh_states':2,'actual_MainWindow_entry_exercised':True,'all_seven_real_external_operations_zero':True},'root_visual_review':pin('verification/sections/328-root-visual.json'),'source_audit':pin('verification/sections/328-source-audit.json'),'original_project_window':pin('verification/sections/328-main-window.json'),'source_sha256':n['source_sha256_after'],'validated_source_sha256':w['source_sha256_after'],'full_suite_rerun':False,'last_full_receipt':'verification/full-320/summary.json','last_full_receipt_is_historical_for_this_changed_source':True,'last_full_validation_sha256':sha('verification/full-320/summary.json'),'next_periodic_full_section':335,'P3_complete':False,'P2_complete':False,'P1_complete':False,'private_state_contents_parsed_copied_or_restored':False,'private_state_hashed_locally_for_preservation_only':True,'private_hashes_published':False,'game_operated':False,'chat_sent':False,'cloud_publication_binding':'enclosing_commit','cloud_published':False,'execution_environment':'local_original_windows_project_venv','local_source_parity_required_for_cloud_publication':True}
(ROOT/'verification/sections/328.json').write_bytes(enc(r));details=change+'\n\n'+validation+'\n\n'+limits+'\n\n'+pending
old_wip=subprocess.check_output(['git','show',parent+':WORK_IN_PROGRESS.md'],cwd=ROOT)
prefix=('## 第328节 + '+title+'\n\n'+now+'。'+details+'\n\n以下为历史记录；当前断点以上述328为准。\n\n').replace('\n','\r\n').encode();(ROOT/'WORK_IN_PROGRESS.md').write_bytes(prefix+old_wip)
doc('PROJECT_COMPLETED.md','## 第328节 + '+title+'\n\n'+now+'。'+details+'\n\n'+(ROOT/'PROJECT_COMPLETED.md').read_text('utf8'))
s=(ROOT/'AGENTS.md').read_text('utf8');end=s.index('\n## ',3);doc('AGENTS.md','## 当前续接 · 第328节 + '+title+'\n\n'+details+'\n\n继续P3；329从当前事件前置、完整奖励池和固定地图实际剩余缺口接续，未启动。测试优先本机，保留到期完整范围，下次335；严格低于15%才开始完整收尾。\n'+s[end:])
s=(ROOT/'PROJECT_REQUIREMENTS.md').read_text('utf8');start=s.index('<!-- current-delivery:start -->');end=s.index('<!-- current-delivery:end -->')+len('<!-- current-delivery:end -->');doc('PROJECT_REQUIREMENTS.md',s[:start]+'<!-- current-delivery:start -->\n## 第328节 + '+title+'\n\n'+details+'\n<!-- current-delivery:end -->'+s[end:])
s=(ROOT/'PROJECT_PROGRESS.md').read_text('utf8');old='其余未覆盖完整事件表及其奖励条件';new='湖中仙女完整出现资格、实际重复/随机脚本与阶段父关系、具体珍贵奖励池及真实领取，其余未覆盖完整事件表及其奖励条件';assert s.count(old)==1;doc('PROJECT_PROGRESS.md',s.replace(old,new,1))
cp=read('DEVELOPMENT_CHECKPOINT.json');assert cp['completed_sections']==327 and cp['next_section']==328
for key in('current_section_validation','latest_section_environment','cloud_publication_closeout'):
 if key in cp:cp['historical_before328_'+key]=cp.pop(key)
cp.update(completed_sections=328,latest_functional_section=328,next_section=329,batch_status='P3_SECTION328_LOCAL_ACCEPTED_PUBLICATION_PENDING',next_action='第328节 + '+title+'已本机必要验收；普通推送核对后329接续P3实际剩余缺口，未启动。下次335。',full_validation_due=False)
cp['sections'].append({'number':328,'completion_ref':'p3-section-328','topic':title,'verification':'verification/sections/328.json'});cp['functional_sections_since_latest_requirement'].append(328)
cp['current_section_save']={'section':328,'verification':'verification/sections/328.json','scope':'current_functional_section','binding':'enclosing_commit'};cp['last_verified_cloud_save']['scope']='previous_functional_section'
cp['current_section_validation']={'section':328,'receipt':'verification/sections/328.json','necessary_methods_passed':100,'native_isolated_window_checks':39,'documented_scenes':10,'original_choices':10,'scene_choice_references':14,'separate_documented_random_outcomes':2,'exact_battle_choice_links':2,'real_nonzero_refresh_states':2,'full_suite_rerun':False,'last_full_receipt':'verification/full-320/summary.json','last_full_receipt_is_historical_for_current_changes':True}
cp['latest_section_environment']={'section':328,'receipt':'verification/sections/328.json','native_windows':validation,'native_game_or_chat_verified':False,'current_section_full_rerun':False,'last_full_receipt':'verification/full-320/summary.json'}
cp['windows_native_validation']=validation;cp['current_batch'].update(status=cp['batch_status'],completed_sections=328,next_section=329,next_section_started=False,receipt='verification/sections/328.json',batch_closed=False)
cp['policy'].update(current_usage_remaining_percent=67,current_usage_receipt='verification/sections/328-preparation/usage-final.json',verification_execution_preference='local_project_environment',avoid_duplicate_cloud_tests=True)
cp['current_data_versions'].update(current_lake_game_commit='bee3f83c5d60590b5e1cd42b8d09d00ce32ab10d',current_lake_document_revision=352356,current_lake_scenes=10,current_lake_original_choices=10,current_lake_scene_choice_references=14,current_lake_random_outcomes_separate=True,current_lake_actual_eligibility_verified=False)
(ROOT/'DEVELOPMENT_CHECKPOINT.json').write_bytes(enc(cp))
doc('CLOUD_HANDOFF.md',(ROOT/'CLOUD_HANDOFF.md').read_text('utf8')+'\n<!-- section328-handoff:start -->\n## 第328节 + '+title+'\n\n'+details+'\n<!-- section328-handoff:end -->\n')
out=ROOT/'verification/sections/328-preparation';shutil.copyfile(ROOT/'.cache/open_test_window_328.py',out/'execution-main-window.py')
runpy.run_path(str(ROOT/'scripts/update_cloud_index.py'))['update'](ROOT)
out=ROOT/'verification/sections/328-closeout';out.mkdir();(out/'execution-closeout.py').write_bytes(Path(__file__).read_bytes());(out/'applied.json').write_bytes(enc({'section':328,'local_accepted':True,'ordinary_cloud_publication_verified':False,'next329_started':False,'at_Beijing':now}))
print(json.dumps({'section':328,'local_accepted':True,'ordinary_publication_pending':True},ensure_ascii=False))
