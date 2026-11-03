from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone,timedelta
import json,subprocess,runpy,shutil
ROOT=Path(__file__).resolve().parents[1]
def read(n):return json.loads((ROOT/n).read_bytes())
def enc(v):return(json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode('utf8')
def sha(n):return sha256((ROOT/n).read_bytes()).hexdigest()
def pin(n):return{'receipt':n,'sha256':sha(n)}
def doc(n,s):
 p=ROOT/n;style='\r\n'if b'\r\n'in p.read_bytes()else'\n';p.write_bytes(s.replace('\r\n','\n').replace('\n',style).encode('utf8'))
parent='595ef0ff364319f2b5f284bbae24b7cf536e4c4e';assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()==parent
assert subprocess.check_output(['git','branch','--show-current'],cwd=ROOT).decode().strip()=='codex/p2-development'
title='独活的同行者奖励与前往、标记后续'
change='新增独活完整事件资料的逐步查阅，保留3段对话、4个选项与7份精确原始入口。去看看小狗可查看同行者奖励及之后的两个独立选项；小心为上的对话独立结束，不自动接入后续。跟随小狗说明前往应急助力，请小狗告知营地位置说明标记应急助力，两者不当成下一段对话，也不当已经移动、标记或招募。同行者原文逐项显示应急助力招募源石锭减少50%，应急干员生命、攻击、防御增加40%，明确适用对象；不扩展到全部招募或全队，不猜领取件数，不改数值模型。节点目录新增独活入口及3处原始情景全文对应，共29目录组、27事件、11类阅读器。版本参考和实际资格未知的提示保持可见；默认不显示无关资源条件。刷新保留两个阅读区的真实非零位置、选择与来源，坏源清旧、恢复后手动重开，重复开窗、父页或主窗关闭均清理所属窗口。'
limits='复用321真实下载的BWIKI352356完整原HTTP，独活整表保留原字符范围与摘要；本轮独立复读BWIKI调查记录和PRTS同行者原文，不冒称重新下载HTML或核对当前服务器。3情景、4选项及1份收藏品完整原件逐项比较固定bee3/a550版本。文献选项一分支只连接去看小狗后的对话，不恢复隐藏父脚本；MOVE与VISION没有下一段ID，不能据此补具体节点、移动成本或招募结果。同行者效果只作资料说明，领取件数、完整出现条件、服务器实际分支/发放/叠加、实际移动和标记仍未知。仅局外查阅，不操作游戏或聊天，不改本局、库存、地图、数值计算和私人配置，不给路线建议或概率。P3/P2/P1未完成，识别最后。'
full=read('verification/full-335/summary.json');assert full['after_section']==335 and full['available_checks_passed'] and full['scope_not_reduced'] and not full['complete_repository_validation']
validation='本机37项相关必要测试与36项Windows原生窗口检查通过，构建字节一致，6张实际PNG均由主代理查看。检查覆盖全部7个原始入口、前往和标记的区别、独立离开、奖励适用对象、两组真实非零阅读状态、父页刷新、坏源清旧/手动恢复和整树关闭；七类真实外部操作计数为零，临时状态与旧计算上下文不变。到期335完整可用范围在本机实际执行并通过：保留539个维护选择器、52份旧保存状态及4283项独立完整检查、862项修订断言，原30项窗口实际执行并保留其可用29项，另有50组P3原生窗口补充；首轮55个组件全部实际终止；两组旧检查被320摘要拦下，保留原失败，仅维护两份验证脚本的显式冻结源码参数，AST核对除绑定及一个参数外完全一致，再完整复验两组窗口通过（70项、72项）。首轮与复验共同覆盖完整可用范围，不冒称首轮全绿或所有组件共享同一版验证脚本；全部303张实际PNG以原图字节复用或主代理查看的对照图核对。具体测试数量与不可用记录以verification/full-335/summary.json为准，不把跳过或不可用计通过。原真实符号链接WinError1314若仍不可用则保留原失败，历史原Linux/Wine/私人Windows及实机游戏聊天仍未验收。311的300秒仅为完整工作流预算，不冒充原120秒通过或正常延迟基准；历史320原失败保留。原项目测试窗已正常更新且可见响应，正常关闭到启动私人五路径一致。537旧选择器原序保留，现539。测试全部本机，无云端重复运行；未变索引25单测复用，当前文档和索引仍实际校验。下一定期全量350。'
nname='verification/sections/335-necessary-attempt1/process.json';wname='verification/sections/335-native-attempt1/actual/window.json';pname='verification/sections/335-native-attempt1/process.json'
n,w,p=map(read,(nname,wname,pname));m=read('verification/sections/335-main-window.json');a=read('verification/sections/335-source-audit.json');v=read('verification/sections/335-root-visual.json')
assert n['passed']and n['methods_ran']==37 and w['passed']and w['qpa']=='windows'and w['qt_exit_code']==0 and w['unique_checks']==36 and w['verification_window_closed']
assert len(w['same_identity_refresh_observations'])==2 and len(w['screenshots'])==6 and len(w['actual_readings'])==2 and all(x==0 for x in w['external_operation_attempts'].values())
assert p['passed']and p['window_receipt_sha256']==sha(wname)
for result in(n,w):
 assert result['source_sha256_before']==result['source_sha256_after']
 for name,h in result['source_sha256_after'].items():assert sha(name)==h,name
assert v['passed']and len(v['final_screenshot_reviews'])==6 and a['ordered_previous537_preserved']and len(a['current_selectors'])==539
assert m['passed']and m['private_entire_normal_close_and_start_interval_unchanged']and m['window_visible_and_responsive']
now=datetime.now(timezone(timedelta(hours=8))).isoformat();pending='<!-- section335-publication-pending -->本地验收完成，普通推送及真实远端核对待完成。'
r={'section':335,'kind':'functional_section','title':title,'new_capability':change,'limitations':[limits],'at_Beijing':now,'branch':'codex/p2-development','necessary_validation':{**pin(nname),'methods_run':37,'actual_exit':0},'native_windows_validation':{**pin(wname),'process':pin(pname),'unique_checks':36,'actual_Qt_exit':0,'documented_events':1,'document_scenes':3,'document_choices':4,'original_source_entries':7,'new_catalogue_groups':1,'exact_scene_links':3,'real_nonzero_refresh_states':2,'actual_MainWindow_entry_and_close_exercised':True,'all_seven_real_external_operations_zero':True},'root_visual_review':pin('verification/sections/335-root-visual.json'),'source_audit':pin('verification/sections/335-source-audit.json'),'original_project_window':pin('verification/sections/335-main-window.json'),'source_sha256':n['source_sha256_after'],'validated_source_sha256':w['source_sha256_after'],'full_suite_rerun':True,'last_full_receipt':'verification/full-335/summary.json','last_full_receipt_is_historical_for_this_changed_source':False,'last_full_validation_sha256':sha('verification/full-335/summary.json'),'full_validation_is_composite_with_two_verifier_binding_rechecks':True,'original_failed_full_retained':True,'next_periodic_full_section':350,'P3_complete':False,'P2_complete':False,'P1_complete':False,'private_state_contents_parsed_copied_or_restored':False,'private_state_hashed_locally_for_preservation_only':True,'private_hashes_published':False,'game_operated':False,'chat_sent':False,'cloud_publication_binding':'enclosing_commit','cloud_published':False,'execution_environment':'local_original_windows_project_venv','local_source_parity_required_for_cloud_publication':True}
(ROOT/'verification/sections/335.json').write_bytes(enc(r));details=change+'\n\n'+validation+'\n\n'+limits+'\n\n'+pending
old_wip=subprocess.check_output(['git','show',parent+':WORK_IN_PROGRESS.md'],cwd=ROOT);(ROOT/'WORK_IN_PROGRESS.md').write_bytes(('## 第335节 + '+title+'\n\n'+now+'。'+details+'\n\n以下为历史记录；当前断点以上述335为准。\n\n').replace('\n','\r\n').encode()+old_wip)
doc('PROJECT_COMPLETED.md','## 第335节 + '+title+'\n\n'+now+'。'+details+'\n\n'+(ROOT/'PROJECT_COMPLETED.md').read_text('utf8'))
s=(ROOT/'AGENTS.md').read_text('utf8');end=s.index('\n## ',3);doc('AGENTS.md','## 当前续接 · 第335节 + '+title+'\n\n'+details+'\n\n继续P3；336从当前事件完整条件、奖励池与固定地图实际剩余缺口接续，未启动。测试优先本机；本次335到期完整可用范围已验收，下次350；严格低于15%才开始完整收尾。\n'+s[end:])
s=(ROOT/'PROJECT_REQUIREMENTS.md').read_text('utf8');start=s.index('<!-- current-delivery:start -->');end=s.index('<!-- current-delivery:end -->')+len('<!-- current-delivery:end -->');doc('PROJECT_REQUIREMENTS.md',s[:start]+'<!-- current-delivery:start -->\n## 第335节 + '+title+'\n\n'+details+'\n<!-- current-delivery:end -->'+s[end:])
s=(ROOT/'PROJECT_PROGRESS.md').read_text('utf8');old='其余未覆盖完整事件表及其奖励条件';new='独活完整出现资格、同行者实际领取件数与应急助力前往/标记目标及执行，其余未覆盖完整事件表及其奖励条件';assert s.count(old)==1;doc('PROJECT_PROGRESS.md',s.replace(old,new,1))
cp=read('DEVELOPMENT_CHECKPOINT.json');assert cp['completed_sections']==334 and cp['next_section']==335
for key in('current_section_validation','latest_section_environment','cloud_publication_closeout'):
 if key in cp:cp['historical_before335_'+key]=cp.pop(key)
cp.update(completed_sections=335,latest_functional_section=335,next_section=336,batch_status='P3_SECTION335_LOCAL_ACCEPTED_PUBLICATION_PENDING',next_action='第335节 + '+title+'已本机必要及到期完整可用范围验收；普通推送核对后336接续P3实际剩余缺口，未启动。下次350。',full_validation_due=False)
cp['sections'].append({'number':335,'completion_ref':'p3-section-335','topic':title,'verification':'verification/sections/335.json'});cp['functional_sections_since_latest_requirement'].append(335)
cp['current_section_save']={'section':335,'verification':'verification/sections/335.json','scope':'current_functional_section','binding':'enclosing_commit'};cp['last_verified_cloud_save']['scope']='previous_functional_section'
cp['current_section_validation']={'section':335,'receipt':'verification/sections/335.json','methods_run':37,'native_isolated_window_checks':36,'documented_events':1,'document_scenes':3,'document_choices':4,'original_source_entries':7,'new_catalogue_groups':1,'exact_scene_links':3,'real_nonzero_refresh_states':2,'full_suite_rerun':True,'last_full_receipt':'verification/full-335/summary.json','last_full_receipt_is_historical_for_current_changes':False}
cp['latest_section_environment']={'section':335,'receipt':'verification/sections/335.json','native_windows':validation,'native_game_or_chat_verified':False,'current_section_full_rerun':True,'last_full_receipt':'verification/full-335/summary.json'}
cp['windows_native_validation']=validation;cp['current_batch'].update(status=cp['batch_status'],completed_sections=335,next_section=336,next_section_started=False,receipt='verification/sections/335.json',batch_closed=False)
cp['policy'].update(current_usage_remaining_percent=96,current_usage_receipt='verification/sections/335-preparation/usage-final-before-publication.json',verification_execution_preference='local_project_environment',avoid_duplicate_cloud_tests=True)
cp['current_data_versions'].update(current_lone_dog_game_commit='bee3f83c5d60590b5e1cd42b8d09d00ce32ab10d',current_lone_dog_document_revision=352356,current_lone_dog_events=1,current_lone_dog_scenes=3,current_lone_dog_choices=4,current_lone_dog_items=1,current_node_reader_aggregate_catalogue_groups=29,current_node_reader_aggregate_event_titles=27,current_node_reader_aggregate_types=11,current_node_actual_version_or_phase_verified=False)
for key in ('current_available_full_validation','last_full_validation'):
 cp['historical_before335_'+key]=cp.get(key)
cp['current_available_full_validation']={'section':335,'receipt':'verification/full-335/summary.json','available_scope_passed':True,'actual_validation_attempt':1,'binding_only_recheck_attempt':2,'single_full_run_all_green':False,'source_freeze':full['source_freeze'],'source_freeze_sha256':full['source_freeze_sha256'],'native_windows_game_chat_verified':False}
cp['last_full_validation']={'after_section':335,'receipt':'verification/full-335/summary.json','available_checks_passed':True,'complete_repository_validation':False,'scope_not_reduced':True,'source_freeze':full['source_freeze'],'source_freeze_sha256':full['source_freeze_sha256']}
cp['next_full_validation_after']=350
for key in ('policy','current_batch_commit_policy','current_batch'):cp[key]['next_full_validation_after']=350
(ROOT/'DEVELOPMENT_CHECKPOINT.json').write_bytes(enc(cp))
doc('CLOUD_HANDOFF.md',(ROOT/'CLOUD_HANDOFF.md').read_text('utf8')+'\n<!-- section335-handoff:start -->\n## 第335节 + '+title+'\n\n'+details+'\n<!-- section335-handoff:end -->\n')
out=ROOT/'verification/sections/335-preparation';shutil.copyfile(ROOT/'.cache/open_test_window_335.py',out/'execution-main-window.py')
note='\n下一到期完整检查须给304/305两份full320验证脚本显式传入--source-freeze及当轮根声明冻结文件；默认320仅供历史绑定，不能把旧摘要改成当前通过。当前335原失败、验证脚本两处绑定维护与完整复验见verification/full-335/summary.json。\n'
for name in ('WORK_IN_PROGRESS.md','AGENTS.md','CLOUD_HANDOFF.md'):
 p=ROOT/name;doc(name,note+p.read_text('utf8'))
runpy.run_path(str(ROOT/'scripts/update_cloud_index.py'))['update'](ROOT)
out=ROOT/'verification/sections/335-closeout';out.mkdir();(out/'execution-closeout.py').write_bytes(Path(__file__).read_bytes());(out/'applied.json').write_bytes(enc({'section':335,'local_accepted':True,'ordinary_cloud_publication_verified':False,'next336_started':False,'at_Beijing':now}))
print(json.dumps({'section':335,'local_accepted':True,'ordinary_publication_pending':True},ensure_ascii=False))
