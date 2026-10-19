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
parent='ca2ec4574304e8cb547b0e54473f16ce9665fc10'
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()==parent
assert subprocess.check_output(['git','branch','--show-current'],cwd=ROOT).decode().strip()=='codex/p2-development'
title='当前回滚文明的完整提供物目录与明确交换数量'
change='新增当前版回滚文明交换资料窗，按真实RELIC物品完整列出284件收藏品，其中259件可交出、25件不可交出，独立按能否交出、稀有度、更新差异和中文名称筛选。与旧基准对照保留272件未改动、12件新增，四件新增结局藏品均不可交出；395条效果定义不当物品数量，提供物目录不当换入奖励池。单独阅读固定原表13处记载整理的9组交换条文及43份完整文案相符原记录，明确领取1件收藏品、1件零件及随机消耗2件自然物；焚毁“文明”显示关联作用而保留独立领取件数未知，不默认1件。当前收藏品、回滚文明场景及已对应的原选项均可进入，场景只打开总览、不虚构专属选项。默认页使用普通中文，内部数量和候选记录放在来源详情。刷新保留两页、四个阅读区、物品/条文与筛选；坏源清旧恢复手选、重复开窗与父窗关闭均清理旧窗口。'
limits='使用bee3当前与a550旧基准全RELIC物品独立核对，原272目录和旧计算未替换。复用321实际下载并校验SHA的BWIKI固定修订352356原HTTP，只摘录回滚文明一张表；完整文案且非空描述匹配，不按编号判断首/再次交换，也不把通用空描述“离开”凭标题纳入。43份为文字和去向范围相符的候选，不是已恢复的游戏父情景、实际可选记录或奖励次数；46个同名原场景仅供来源核对和进入资料总览。当前可交出字段不证明账户解锁、本局持有、实际选择或完整奖励池；不按稀有度推算换入池，具名焚毁文明的独立领取数量仍未知。全部实际交付、领取、库存消耗、发放脚本和服务器资格仍未知；不操作游戏、聊天或私人状态，不提供路线建议和概率。P3/P2/P1未完成，识别优化最后。'
validation='首次51项必要检查通过；实窗复读后仅改两个人类阅读文本函数，源码AST核对确认其它模块定义不变，14项受影响检查按最终源码复验通过，其余37项不重复运行，详情见323-readability-scope。最终31项Windows原生唯一检查通过：实际主窗口的收藏品/事件场景/原选项入口、284总数与新增4不可交/8可交筛选、9组条文及43候选保留、明确1件与2自然物和具名数量未知、四个真实非零滚动选区经父页刷新保持、公开文件实际损坏清旧/恢复手选及重复开窗/父窗关闭。五张最终改变的PNG已直接查看，另一张与已直接查看的首轮PNG字节完全一致；首轮截图与日志保留。七类采样、聊天和凭证调用为零，临时本局与旧计算上下文不变；原项目实际窗口正常更新并可见响应，正常关闭至启动的私人五路径不变。513旧维护选择器原序保留，现515；只做本机必要验证，未重跑全量或未变索引单测。历史320完整范围及不可用原件保留，不当本节全量，下次定期全量335。'
nname='verification/sections/323-necessary-attempt2/process.json';wname='verification/sections/323-native-attempt2/actual/window.json';pname='verification/sections/323-native-attempt2/process.json'
n,w,p=map(read,(nname,wname,pname));m=read('verification/sections/323-main-window.json');a=read('verification/sections/323-source-audit.json');v=read('verification/sections/323-root-visual.json')
assert n['passed']and n['methods_ran']==14 and n['exit_code']==0
assert w['passed']and w['qpa']=='windows'and w['qt_exit_code']==0 and w['unique_checks']==31 and w['verification_window_closed']
assert len(w['same_identity_refresh_observations'])==4 and len(w['screenshots'])==6 and all(x==0 for x in w['external_operation_attempts'].values())
assert len([x for x in w['actual_readings']if 'document_group'in x])==9
assert p['passed']and p['window_receipt_sha256']==sha(wname)
initial=read('verification/sections/323-necessary-attempt1/process.json');scope=read('verification/sections/323-readability-scope.json');assert initial['passed']and initial['methods_ran']==51 and scope['module_AST_outside_two_player_text_functions_equal']and scope['affected_methods_passed']==14
for result in(n,w):
 assert result['source_sha256_before']==result['source_sha256_after']
 for name,h in result['source_sha256_after'].items():assert sha(name)==h,name
assert v['passed']and len(v['final_screenshot_reviews'])==6 and a['ordered_previous513_preserved']and len(a['current_selectors'])==515
assert m['passed']and m['private_entire_normal_close_and_start_interval_unchanged']and m['window_visible_and_responsive']
now=datetime.now(timezone(timedelta(hours=8))).isoformat();pending='<!-- section323-publication-pending -->本地验收完成，普通推送及真实远端核对待完成。'
r={'section':323,'kind':'functional_section','title':title,'new_capability':change,'limitations':[limits],'at_Beijing':now,'branch':'codex/p2-development','necessary_validation':{**pin(nname),'methods_run':14,'prior51_receipt':'verification/sections/323-necessary-attempt1/process.json','other37_reused_not_rerun':True,'readability_scope':pin('verification/sections/323-readability-scope.json'),'actual_exit':0},'native_windows_validation':{**pin(wname),'process':pin(pname),'unique_checks':31,'actual_Qt_exit':0,'documented_option_groups_checked':9,'primary_text_candidates_preserved':43,'current_relic_catalogue_complete':284,'real_nonzero_refresh_states':4,'actual_MainWindow_entry_exercised':True,'all_seven_real_external_operations_zero':True},'root_visual_review':pin('verification/sections/323-root-visual.json'),'source_audit':pin('verification/sections/323-source-audit.json'),'original_project_window':pin('verification/sections/323-main-window.json'),'source_sha256':n['source_sha256_after'],'validated_source_sha256':w['source_sha256_after'],'full_suite_rerun':False,'last_full_receipt':'verification/full-320/summary.json','last_full_receipt_is_historical_for_this_changed_source':True,'last_full_validation_sha256':sha('verification/full-320/summary.json'),'next_periodic_full_section':335,'P3_complete':False,'P2_complete':False,'P1_complete':False,'private_state_contents_parsed_copied_or_restored':False,'private_state_hashed_locally_for_preservation_only':True,'private_hashes_published':False,'game_operated':False,'chat_sent':False,'cloud_publication_binding':'enclosing_commit','cloud_published':False,'execution_environment':'local_original_windows_project_venv','local_source_parity_required_for_cloud_publication':True}
(ROOT/'verification/sections/323.json').write_bytes(enc(r));details=change+'\n\n'+validation+'\n\n'+limits+'\n\n'+pending
old_wip=subprocess.check_output(['git','show',parent+':WORK_IN_PROGRESS.md'],cwd=ROOT)
prefix=('## 第323节 + '+title+'\n\n'+now+'。'+details+'\n\n以下为历史记录；当前断点以上述323为准。\n\n').replace('\n','\r\n').encode('utf8');(ROOT/'WORK_IN_PROGRESS.md').write_bytes(prefix+old_wip)
doc('PROJECT_COMPLETED.md','## 第323节 + '+title+'\n\n'+now+'。'+details+'\n\n'+(ROOT/'PROJECT_COMPLETED.md').read_text('utf8'))
s=(ROOT/'AGENTS.md').read_text('utf8');end=s.index('\n## ',3);doc('AGENTS.md','## 当前续接 · 第323节 + '+title+'\n\n'+details+'\n\n继续P3；324从当前事件前置、完整奖励池和固定地图的实际剩余缺口接续，未启动。测试优先本机，保留到期完整范围，下次335；严格低于15%才开始完整收尾。\n'+s[end:])
s=(ROOT/'PROJECT_REQUIREMENTS.md').read_text('utf8');start=s.index('<!-- current-delivery:start -->');end=s.index('<!-- current-delivery:end -->')+len('<!-- current-delivery:end -->');doc('PROJECT_REQUIREMENTS.md',s[:start]+'<!-- current-delivery:start -->\n## 第323节 + '+title+'\n\n'+details+'\n<!-- current-delivery:end -->'+s[end:])
s=(ROOT/'PROJECT_PROGRESS.md').read_text('utf8');old='其余具名奖励来源、完整掉落池与零件池范围';new='回滚文明首/再次交换与同文案记录的实际归属、完整换入池及账户选择、焚毁“文明”独立领取件数、其余具名奖励来源、完整掉落池与零件池范围';assert s.count(old)==1;doc('PROJECT_PROGRESS.md',s.replace(old,new,1))
cp=read('DEVELOPMENT_CHECKPOINT.json');assert cp['completed_sections']==322 and cp['next_section']==323
for key in('current_section_validation','latest_section_environment','cloud_publication_closeout'):
 if key in cp:cp['historical_before323_'+key]=cp.pop(key)
cp.update(completed_sections=323,latest_functional_section=323,next_section=324,batch_status='P3_SECTION323_LOCAL_ACCEPTED_PUBLICATION_PENDING',next_action='第323节 + '+title+'已本机必要验收；普通推送核对后324接续P3实际剩余缺口，未启动。下次定期全量335。',full_validation_due=False)
cp['sections'].append({'number':323,'completion_ref':'p3-section-323','topic':title,'verification':'verification/sections/323.json'});cp['functional_sections_since_latest_requirement'].append(323)
cp['current_section_save']={'section':323,'verification':'verification/sections/323.json','scope':'current_functional_section','binding':'enclosing_commit'};cp['last_verified_cloud_save']['scope']='previous_functional_section'
cp['current_section_validation']={'section':323,'receipt':'verification/sections/323.json','initial_necessary_methods_passed':51,'final_affected_methods_rechecked':14,'other37_unchanged_scope_reused':True,'native_isolated_window_checks':31,'documented_option_groups_checked':9,'primary_text_candidates_preserved':43,'current_relic_catalogue_complete':284,'real_nonzero_refresh_states':4,'full_suite_rerun':False,'last_full_receipt':'verification/full-320/summary.json','last_full_receipt_is_historical_for_current_changes':True}
cp['latest_section_environment']={'section':323,'receipt':'verification/sections/323.json','native_windows':validation,'native_game_or_chat_verified':False,'current_section_full_rerun':False,'last_full_receipt':'verification/full-320/summary.json'}
cp['windows_native_validation']=validation;cp['current_batch'].update(status=cp['batch_status'],completed_sections=323,next_section=324,next_section_started=False,receipt='verification/sections/323.json',batch_closed=False)
cp['policy'].update(current_usage_remaining_percent=70,current_usage_receipt='verification/sections/323-preparation/usage-final.json',verification_execution_preference='local_project_environment',avoid_duplicate_cloud_tests=True)
cp['current_data_versions'].update(current_exchange_game_commit='bee3f83c5d60590b5e1cd42b8d09d00ce32ab10d',current_exchange_document_revision=352356,current_exchange_complete_relic_items=284,current_exchange_offer_true=259,current_exchange_offer_false=25,current_exchange_document_groups=9,current_exchange_full_caption_candidates=43,current_exchange_reward_pool_verified=False)
(ROOT/'DEVELOPMENT_CHECKPOINT.json').write_bytes(enc(cp))
doc('CLOUD_HANDOFF.md',(ROOT/'CLOUD_HANDOFF.md').read_text('utf8')+'\n<!-- section323-handoff:start -->\n## 第323节 + '+title+'\n\n'+details+'\n<!-- section323-handoff:end -->\n')
out=ROOT/'verification/sections/323-preparation';shutil.copyfile(ROOT/'.cache/open_test_window_323.py',out/'execution-main-window.py')
runpy.run_path(str(ROOT/'scripts/update_cloud_index.py'))['update'](ROOT)
out=ROOT/'verification/sections/323-closeout';out.mkdir();(out/'execution-closeout.py').write_bytes(Path(__file__).read_bytes());(out/'applied.json').write_bytes(enc({'section':323,'local_accepted':True,'ordinary_cloud_publication_verified':False,'next324_started':False,'at_Beijing':now}))
print(json.dumps({'section':323,'local_accepted':True,'ordinary_publication_pending':True},ensure_ascii=False))
