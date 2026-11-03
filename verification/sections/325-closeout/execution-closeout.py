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
parent='41b3123a0d63d5953ee1c9b26b82c013ef7c1fca'
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()==parent
assert subprocess.check_output(['git','branch','--show-current'],cwd=ROOT).decode().strip()=='codex/p2-development'
title='线人与好奇心与死的条件、奖励和后续资料'
change='新增线人4段对话/3选项与好奇心与死3段对话/2选项的逐步资料窗，按文献情景分别列出选项。沙盘α具名获得与1件珍贵加工品/1件随机收藏品分开，不补具名领取件数或随机名单；修正结果的50源石锭只用于标记，不当奖励或立即战斗。可按层数、节点、强制重启解锁、两种沙盘持有、标记和源石锭作本页三态对照，已知不符保留阅读并禁用后续；历史查阅不被当前资源抹除，双沙盘却未标记提示冲突，不覆盖已知支付不足。对应7情景/5原选项/两件沙盘均能直达，点目录不冒充实际持有。关联窥视箱中保持独立条件与固定作战资料，非当前选项跳转；刷新保留条件、两组非零阅读及子窗，切换/失效/重复/父窗关闭清理子窗。'
limits='复用321实际下载的BWIKI352356中两张完整原表与PRTS433770第二结局完整DOM，以原字节/字符位置摘录并核对SHA；修正首轮Windows文本写入换行导致的摘要不符，原失败保留。当前PRTS网页文字独立复核层数、沙盘、标记和50源石锭，未冒称重新下载当前HTML。旧433770第二结局没有后来的祭日之契结局条件，不将该旧段当当前完整结局规则；窥视箱中沿用322独立新依据。完整选择文案及明确nextSceneId对照bee3当前与a550完整记录，不按ID猜父情景。文献条件符合只表示已列条件，不是服务器全部资格；完整前置、随机池、实际发放、具名件数、本局真实标记及沙盘实际获取仍未知，商店1源石锭不保证有货，三节点分布不推广至所有第五层。不操作游戏、聊天，不改本局/私人配置和旧计算，不推荐路线或概率；P3/P2/P1未完成，识别最后。'
validation='本机首轮59项必要检查通过。独立复读修正标记矛盾不能覆盖已知支付不足、且仅对好奇心与死生效的边界，新增1项边界检查后重验受影响两个模块17项通过，其余43项未变模块通过证据复用，不声称最终重跑60项。最终37项Windows原生唯一检查通过，含7情景/5选项、49/50源石锭与已标记边界、随机奖励不受标记费用误排、历史条件保留、沙盘目录不冒充持有、关联窥视箱中及混沌源阶理论精确原图、两组非零滚动选区经父页刷新保留、公开副本实际损坏清旧/恢复手选及完整子窗关闭。原生首轮验收脚本的同名context变量误比较失败保留，只改为独立declared_context后原范围复验通过；最终边界修正再按全范围复验。八张最终PNG全部与上一轮字节相同，四张上一轮已直接查看，另四张最终直接查看。七类外部调用零、临时本局和旧计算上下文不变；原项目窗口已正常更新可见响应，正常关闭至启动私人五路径不变。517旧维护选择器原序保持，现519；测试仅本机必要范围，未重跑全量或未变索引25单测，320完整范围/失败/不可用原件仍属历史，下次335。'
nname='verification/sections/325-necessary-attempt2/process.json';wname='verification/sections/325-native-attempt3/actual/window.json';pname='verification/sections/325-native-attempt3/process.json'
n,w,p=map(read,(nname,wname,pname));m=read('verification/sections/325-main-window.json');a=read('verification/sections/325-source-audit.json');v=read('verification/sections/325-root-visual.json');scope=read('verification/sections/325-check-scope.json')
assert n['passed']and n['methods_ran']==17 and scope['passed']and scope['other43_unchanged_module_methods_reused_not_rerun']
assert w['passed']and w['qpa']=='windows'and w['qt_exit_code']==0 and w['unique_checks']==37 and w['verification_window_closed']
assert len(w['same_identity_refresh_observations'])==2 and len(w['screenshots'])==8 and len(w['actual_readings'])==5 and all(x==0 for x in w['external_operation_attempts'].values())
assert p['passed']and p['window_receipt_sha256']==sha(wname)
for result in(n,w):
 assert result['source_sha256_before']==result['source_sha256_after']
 for name,h in result['source_sha256_after'].items():assert sha(name)==h,name
assert v['passed']and len(v['final_screenshot_reviews'])==8 and a['ordered_previous517_preserved']and len(a['current_selectors'])==519
assert m['passed']and m['private_entire_normal_close_and_start_interval_unchanged']and m['window_visible_and_responsive']
now=datetime.now(timezone(timedelta(hours=8))).isoformat();pending='<!-- section325-publication-pending -->本地验收完成，普通推送及真实远端核对待完成。'
r={'section':325,'kind':'functional_section','title':title,'new_capability':change,'limitations':[limits],'at_Beijing':now,'branch':'codex/p2-development','necessary_validation':{**pin(nname),'methods_run_on_final_affected_modules':17,'initial59_receipt':'verification/sections/325-necessary-attempt1/process.json','other43_unchanged_modules_reused':True,'scope':pin('verification/sections/325-check-scope.json'),'actual_exit':0},'native_windows_validation':{**pin(wname),'process':pin(pname),'unique_checks':37,'actual_Qt_exit':0,'documented_flow_scenes':7,'documented_flow_choices':5,'related_current_map':'ro6_b_5','real_nonzero_refresh_states':2,'actual_MainWindow_entry_exercised':True,'all_seven_real_external_operations_zero':True},'root_visual_review':pin('verification/sections/325-root-visual.json'),'source_audit':pin('verification/sections/325-source-audit.json'),'original_project_window':pin('verification/sections/325-main-window.json'),'source_sha256':n['source_sha256_after'],'validated_source_sha256':w['source_sha256_after'],'full_suite_rerun':False,'last_full_receipt':'verification/full-320/summary.json','last_full_receipt_is_historical_for_this_changed_source':True,'last_full_validation_sha256':sha('verification/full-320/summary.json'),'next_periodic_full_section':335,'P3_complete':False,'P2_complete':False,'P1_complete':False,'private_state_contents_parsed_copied_or_restored':False,'private_state_hashed_locally_for_preservation_only':True,'private_hashes_published':False,'game_operated':False,'chat_sent':False,'cloud_publication_binding':'enclosing_commit','cloud_published':False,'execution_environment':'local_original_windows_project_venv','local_source_parity_required_for_cloud_publication':True}
(ROOT/'verification/sections/325.json').write_bytes(enc(r));details=change+'\n\n'+validation+'\n\n'+limits+'\n\n'+pending
old_wip=subprocess.check_output(['git','show',parent+':WORK_IN_PROGRESS.md'],cwd=ROOT)
prefix=('## 第325节 + '+title+'\n\n'+now+'。'+details+'\n\n以下为历史记录；当前断点以上述325为准。\n\n').replace('\n','\r\n').encode('utf8');(ROOT/'WORK_IN_PROGRESS.md').write_bytes(prefix+old_wip)
doc('PROJECT_COMPLETED.md','## 第325节 + '+title+'\n\n'+now+'。'+details+'\n\n'+(ROOT/'PROJECT_COMPLETED.md').read_text('utf8'))
s=(ROOT/'AGENTS.md').read_text('utf8');end=s.index('\n## ',3);doc('AGENTS.md','## 当前续接 · 第325节 + '+title+'\n\n'+details+'\n\n继续P3；326从当前事件前置、完整奖励池和固定地图的实际剩余缺口接续，未启动。测试优先本机，保留到期完整范围，下次335；严格低于15%才开始完整收尾。\n'+s[end:])
s=(ROOT/'PROJECT_REQUIREMENTS.md').read_text('utf8');start=s.index('<!-- current-delivery:start -->');end=s.index('<!-- current-delivery:end -->')+len('<!-- current-delivery:end -->');doc('PROJECT_REQUIREMENTS.md',s[:start]+'<!-- current-delivery:start -->\n## 第325节 + '+title+'\n\n'+details+'\n<!-- current-delivery:end -->'+s[end:])
s=(ROOT/'PROJECT_PROGRESS.md').read_text('utf8');old='其余具名奖励来源、完整掉落池与零件池范围';new='线人与好奇心与死的当前服务器完整资格、沙盘实际获取/标记状态与完整随机奖励池，相关结局全部前置及实际脚本、其余具名奖励来源、完整掉落池与零件池范围';assert s.count(old)==1;doc('PROJECT_PROGRESS.md',s.replace(old,new,1))
cp=read('DEVELOPMENT_CHECKPOINT.json');assert cp['completed_sections']==324 and cp['next_section']==325
for key in('current_section_validation','latest_section_environment','cloud_publication_closeout'):
 if key in cp:cp['historical_before325_'+key]=cp.pop(key)
cp.update(completed_sections=325,latest_functional_section=325,next_section=326,batch_status='P3_SECTION325_LOCAL_ACCEPTED_PUBLICATION_PENDING',next_action='第325节 + '+title+'已本机必要验收；普通推送核对后326接续P3实际剩余缺口，未启动。下次定期全量335。',full_validation_due=False)
cp['sections'].append({'number':325,'completion_ref':'p3-section-325','topic':title,'verification':'verification/sections/325.json'});cp['functional_sections_since_latest_requirement'].append(325)
cp['current_section_save']={'section':325,'verification':'verification/sections/325.json','scope':'current_functional_section','binding':'enclosing_commit'};cp['last_verified_cloud_save']['scope']='previous_functional_section'
cp['current_section_validation']={'section':325,'receipt':'verification/sections/325.json','initial59_passed':True,'final_affected_modules17_passed':True,'other43_unchanged_modules_reused':True,'native_isolated_window_checks':37,'flow_scenes':7,'flow_choices':5,'real_nonzero_refresh_states':2,'full_suite_rerun':False,'last_full_receipt':'verification/full-320/summary.json','last_full_receipt_is_historical_for_current_changes':True}
cp['latest_section_environment']={'section':325,'receipt':'verification/sections/325.json','native_windows':validation,'native_game_or_chat_verified':False,'current_section_full_rerun':False,'last_full_receipt':'verification/full-320/summary.json'}
cp['windows_native_validation']=validation;cp['current_batch'].update(status=cp['batch_status'],completed_sections=325,next_section=326,next_section_started=False,receipt='verification/sections/325.json',batch_closed=False)
cp['policy'].update(current_usage_remaining_percent=69,current_usage_receipt='verification/sections/325-preparation/usage-final.json',verification_execution_preference='local_project_environment',avoid_duplicate_cloud_tests=True)
cp['current_data_versions'].update(current_sand_game_commit='bee3f83c5d60590b5e1cd42b8d09d00ce32ab10d',current_sand_document_revision=352356,current_sand_independent_document_revision=433770,current_sand_documented_scenes=7,current_sand_documented_choices=5,current_sand_actual_eligibility_verified=False,current_sand_rewards_received=False)
(ROOT/'DEVELOPMENT_CHECKPOINT.json').write_bytes(enc(cp))
doc('CLOUD_HANDOFF.md',(ROOT/'CLOUD_HANDOFF.md').read_text('utf8')+'\n<!-- section325-handoff:start -->\n## 第325节 + '+title+'\n\n'+details+'\n<!-- section325-handoff:end -->\n')
out=ROOT/'verification/sections/325-preparation';shutil.copyfile(ROOT/'.cache/open_test_window_325.py',out/'execution-main-window.py')
runpy.run_path(str(ROOT/'scripts/update_cloud_index.py'))['update'](ROOT)
out=ROOT/'verification/sections/325-closeout';out.mkdir();(out/'execution-closeout.py').write_bytes(Path(__file__).read_bytes());(out/'applied.json').write_bytes(enc({'section':325,'local_accepted':True,'ordinary_cloud_publication_verified':False,'next326_started':False,'at_Beijing':now}))
print(json.dumps({'section':325,'local_accepted':True,'ordinary_publication_pending':True},ensure_ascii=False))
