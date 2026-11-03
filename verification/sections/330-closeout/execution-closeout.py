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
parent='bc8ca1b58af6f2311d47584fbea966593608ab7b'
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()==parent
assert subprocess.check_output(['git','branch','--show-current'],cwd=ROOT).decode().strip()=='codex/p2-development'
title='无人商店的持有条件、换档与同文案记录'
change='新增无人商店完整固定原表的四组文献选项、11份当前原选项和4份原情景阅读，保留所有同文记录。搬大桶/两小桶/化石巨桶分别保留各3份原记录，开桶保留2份，不能当多次选择、领取或扣费。三项搬运明确只列1件收藏品，不把桶数、四叶草化石增加可选项当作多领件数。化石未知/持有/未持有仅限制巨桶分支，不按持有文字扣除；单次开桶4源石锭按未知/3/4边界对照，不套化石要求、不累计为8。开桶不是立即多领1件，也不猜稀有度、池、次数或换档先后。两份文案完全相同的开桶后续分别阅读，普通跟随不默认任一份，后续不重新接回最初四项形成伪循环。版本页4情景/11选项共15入口准确保留原始来源，资料定位不等于本局实际选项。刷新保持两组真实非零阅读、选项、本页条件与指定来源；实际坏源清旧并手选恢复、重复开窗及父页失效清理子窗，普通玩家只看到持有条件、单次代价、数量与未知。'
limits='复用321实际下载的BWIKI352356完整无人商店表，精确原字符范围、原始字节和摘要保留；本轮公开网页独立复读四组文案，不冒称重新下载HTML或恢复服务器脚本。11完整原选项、4完整情景与1件四叶草化石逐项比较bee3及a550。两份开桶后续原记录除ID外文案相同，但不能据此合并、指定阶段、连续次数或实际父关系；A/B只为区别资料记录，不代表先后或稀有度。固定4源石锭/持有条件只作本页对照，足够或持有不等于完整资格；原文三项1件不因重复记录或增加可选项改数。当前完整奖励池、升级脚本/档次、原始变体实际归属、完整出现前置及真实发放仍未知。P3/P2/P1未完成、识别最后，不操作游戏聊天、不改本局及私人设置，不给路线建议或概率。'
validation='本机31项相关必要检查通过，可重复构建字节核对通过；Windows原生临时MainWindow34项唯一检查通过，核对15精确原始入口、4情景/4组选择/11变体、化石三态只影响持有分支、普通两小桶仍1件且不需化石/源石锭、指定原记录不冒充实际变体、3/4源石锭边界、两份同文后续无默认/分别查看/无伪循环、开桶不是领取或重复扣费、两组真实非零阅读经父页刷新保持、实际公开副本损坏清旧/手选恢复、重复开窗/父源失效清子窗。7张实际PNG全部直接查看，七类外部调用零，临时本局与旧计算上下文不变。原项目测试窗正常更新并可见响应，正常关闭到启动私人五路径不变。527旧选择器原序保留，现529。全部测试本机，未重复全量或未变索引25单测；320完整范围/失败/不可用原件仍属历史，下一全量335。'
nname='verification/sections/330-necessary-attempt1/process.json';wname='verification/sections/330-native-attempt1/actual/window.json';pname='verification/sections/330-native-attempt1/process.json'
n,w,p=map(read,(nname,wname,pname));m=read('verification/sections/330-main-window.json');a=read('verification/sections/330-source-audit.json');v=read('verification/sections/330-root-visual.json')
assert n['passed']and n['methods_ran']==31 and w['passed']and w['qpa']=='windows'and w['qt_exit_code']==0 and w['unique_checks']==34 and w['verification_window_closed']
assert len(w['same_identity_refresh_observations'])==2 and len(w['screenshots'])==7 and len(w['actual_readings'])==4 and all(x==0 for x in w['external_operation_attempts'].values())
assert p['passed']and p['window_receipt_sha256']==sha(wname)
for result in(n,w):
 assert result['source_sha256_before']==result['source_sha256_after']
 for name,h in result['source_sha256_after'].items():assert sha(name)==h,name
assert v['passed']and len(v['final_screenshot_reviews'])==7 and a['ordered_previous527_preserved']and len(a['current_selectors'])==529
assert m['passed']and m['private_entire_normal_close_and_start_interval_unchanged']and m['window_visible_and_responsive']
now=datetime.now(timezone(timedelta(hours=8))).isoformat();pending='<!-- section330-publication-pending -->本地验收完成，普通推送及真实远端核对待完成。'
r={'section':330,'kind':'functional_section','title':title,'new_capability':change,'limitations':[limits],'at_Beijing':now,'branch':'codex/p2-development','necessary_validation':{**pin(nname),'methods_run':31,'actual_exit':0},'native_windows_validation':{**pin(wname),'process':pin(pname),'unique_checks':34,'actual_Qt_exit':0,'documented_events':1,'documented_scenes':4,'document_choice_groups':4,'original_choices':11,'same_text_followup_records':2,'held_relic_choices':1,'fixed_gold_choices':1,'real_nonzero_refresh_states':2,'actual_MainWindow_entry_exercised':True,'all_seven_real_external_operations_zero':True},'root_visual_review':pin('verification/sections/330-root-visual.json'),'source_audit':pin('verification/sections/330-source-audit.json'),'original_project_window':pin('verification/sections/330-main-window.json'),'source_sha256':n['source_sha256_after'],'validated_source_sha256':w['source_sha256_after'],'full_suite_rerun':False,'last_full_receipt':'verification/full-320/summary.json','last_full_receipt_is_historical_for_this_changed_source':True,'last_full_validation_sha256':sha('verification/full-320/summary.json'),'next_periodic_full_section':335,'P3_complete':False,'P2_complete':False,'P1_complete':False,'private_state_contents_parsed_copied_or_restored':False,'private_state_hashed_locally_for_preservation_only':True,'private_hashes_published':False,'game_operated':False,'chat_sent':False,'cloud_publication_binding':'enclosing_commit','cloud_published':False,'execution_environment':'local_original_windows_project_venv','local_source_parity_required_for_cloud_publication':True}
(ROOT/'verification/sections/330.json').write_bytes(enc(r));details=change+'\n\n'+validation+'\n\n'+limits+'\n\n'+pending
old_wip=subprocess.check_output(['git','show',parent+':WORK_IN_PROGRESS.md'],cwd=ROOT)
prefix=('## 第330节 + '+title+'\n\n'+now+'。'+details+'\n\n以下为历史记录；当前断点以上述330为准。\n\n').replace('\n','\r\n').encode();(ROOT/'WORK_IN_PROGRESS.md').write_bytes(prefix+old_wip)
doc('PROJECT_COMPLETED.md','## 第330节 + '+title+'\n\n'+now+'。'+details+'\n\n'+(ROOT/'PROJECT_COMPLETED.md').read_text('utf8'))
s=(ROOT/'AGENTS.md').read_text('utf8');end=s.index('\n## ',3);doc('AGENTS.md','## 当前续接 · 第330节 + '+title+'\n\n'+details+'\n\n继续P3；331从当前事件前置、完整奖励池和固定地图实际剩余缺口接续，未启动。测试优先本机，保留到期完整范围，下次335；严格低于15%才开始完整收尾。\n'+s[end:])
s=(ROOT/'PROJECT_REQUIREMENTS.md').read_text('utf8');start=s.index('<!-- current-delivery:start -->');end=s.index('<!-- current-delivery:end -->')+len('<!-- current-delivery:end -->');doc('PROJECT_REQUIREMENTS.md',s[:start]+'<!-- current-delivery:start -->\n## 第330节 + '+title+'\n\n'+details+'\n<!-- current-delivery:end -->'+s[end:])
s=(ROOT/'PROJECT_PROGRESS.md').read_text('utf8');old='其余未覆盖完整事件表及其奖励条件';new='无人商店升级档次/次数/脚本、两份同文后续及11原选项的实际变体归属、完整奖励池/出现前置和真实领取，其余未覆盖完整事件表及其奖励条件';assert s.count(old)==1;doc('PROJECT_PROGRESS.md',s.replace(old,new,1))
cp=read('DEVELOPMENT_CHECKPOINT.json');assert cp['completed_sections']==329 and cp['next_section']==330
for key in('current_section_validation','latest_section_environment','cloud_publication_closeout'):
 if key in cp:cp['historical_before330_'+key]=cp.pop(key)
cp.update(completed_sections=330,latest_functional_section=330,next_section=331,batch_status='P3_SECTION330_LOCAL_ACCEPTED_PUBLICATION_PENDING',next_action='第330节 + '+title+'已本机必要验收；普通推送核对后331接续P3实际剩余缺口，未启动。下次335。',full_validation_due=False)
cp['sections'].append({'number':330,'completion_ref':'p3-section-330','topic':title,'verification':'verification/sections/330.json'});cp['functional_sections_since_latest_requirement'].append(330)
cp['current_section_save']={'section':330,'verification':'verification/sections/330.json','scope':'current_functional_section','binding':'enclosing_commit'};cp['last_verified_cloud_save']['scope']='previous_functional_section'
cp['current_section_validation']={'section':330,'receipt':'verification/sections/330.json','necessary_methods_passed':31,'native_isolated_window_checks':34,'documented_events':1,'documented_scenes':4,'document_choice_groups':4,'original_choices':11,'same_text_followup_records':2,'held_relic_choices':1,'fixed_gold_choices':1,'real_nonzero_refresh_states':2,'full_suite_rerun':False,'last_full_receipt':'verification/full-320/summary.json','last_full_receipt_is_historical_for_current_changes':True}
cp['latest_section_environment']={'section':330,'receipt':'verification/sections/330.json','native_windows':validation,'native_game_or_chat_verified':False,'current_section_full_rerun':False,'last_full_receipt':'verification/full-320/summary.json'}
cp['windows_native_validation']=validation;cp['current_batch'].update(status=cp['batch_status'],completed_sections=330,next_section=331,next_section_started=False,receipt='verification/sections/330.json',batch_closed=False)
cp['policy'].update(current_usage_remaining_percent=100,current_usage_receipt='verification/sections/330-preparation/usage-final.json',verification_execution_preference='local_project_environment',avoid_duplicate_cloud_tests=True)
cp['current_data_versions'].update(current_unattended_shop_game_commit='bee3f83c5d60590b5e1cd42b8d09d00ce32ab10d',current_unattended_shop_document_revision=352356,current_unattended_shop_scenes=4,current_unattended_shop_choice_groups=4,current_unattended_shop_original_choices=11,current_unattended_shop_same_text_followups_separate=True,current_unattended_shop_actual_upgrade_verified=False)
(ROOT/'DEVELOPMENT_CHECKPOINT.json').write_bytes(enc(cp))
doc('CLOUD_HANDOFF.md',(ROOT/'CLOUD_HANDOFF.md').read_text('utf8')+'\n<!-- section330-handoff:start -->\n## 第330节 + '+title+'\n\n'+details+'\n<!-- section330-handoff:end -->\n')
out=ROOT/'verification/sections/330-preparation';shutil.copyfile(ROOT/'.cache/open_test_window_330.py',out/'execution-main-window.py')
runpy.run_path(str(ROOT/'scripts/update_cloud_index.py'))['update'](ROOT)
out=ROOT/'verification/sections/330-closeout';out.mkdir();(out/'execution-closeout.py').write_bytes(Path(__file__).read_bytes());(out/'applied.json').write_bytes(enc({'section':330,'local_accepted':True,'ordinary_cloud_publication_verified':False,'next331_started':False,'at_Beijing':now}))
print(json.dumps({'section':330,'local_accepted':True,'ordinary_publication_pending':True},ensure_ascii=False))
