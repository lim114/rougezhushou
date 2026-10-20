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
parent='733cb8a08711f9cc3b7bfc55a73cdbb1babc5439';assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()==parent
assert subprocess.check_output(['git','branch','--show-current'],cwd=ROOT).decode().strip()=='codex/p2-development'
title='沉寂之屋与红苔的完整选项、条件和下一区域影响'
change='新增沉寂之屋、呼吸的红苔两张完整事件表的逐步查阅，保留8段对话、6组选项及6份完整原记录。沉寂之屋分别说明2目标生命值或8源石锭两条获取笼控器的方法，明确笼控器是零件而非收藏品；未写件数不补1件，生命代价不套黑诞保留1点的规则，两种获取方式不相加。呼吸的红苔分别说明持有笼控器获得30源石锭、种下1枚种子以及离开三条独立分支；持有不当已经消耗，种子不当奖励，两种前置互不继承。两条前往希望的沃土说明限定下一区域，不误画成当前节点、不当当前全队加成，也不凭机制展示物品发放零件。仅沉寂之屋显示源石锭对照，仅红苔显示笼控器三态和种子数量；未知仍可查文献，已知不足只阻断对应选项后续，不阻断其它分支。版本资料页14个原情景/选项入口可精确进入；节点目录新增2个来源准入、8个原情景ID和全文对应，共27目录分组/25事件/9类阅读器。沿用332的版本参考提示与默认未知，不代入本局库存；刷新保留两组真实非零阅读、选择及本页条件，坏源清旧/手选恢复、重复开窗和父页/主窗关闭清子窗。'
limits='复用321实际下载的BWIKI352356完整原HTTP，两表保留原字符范围、字节及摘要；本轮公开网页独立复读两表与PRTS笼控器来源，不冒称重新下载HTML或当前服务器验证。8段原情景、6原选项及3份物品完整记录逐项比较固定bee3/a550版本，精确后续只供文献阅读，不按编号或同名恢复服务器脚本。2目标生命值与8源石锭是替代代价，生命底限未知；笼控器明确为SCRAP，领取件数未明，持有不证明消耗。种下1枚与30源石锭只属于各自分支，FEATURE下层天气生成不是可领取的库存零件；当前区域阶段、属性、具体节点覆盖、随机池和实际发放仍未核验，不把300旧基准阶段或数字搬入当前模型。完整出现条件、实际选项/资源扣除/件数、种子使用与下一区域执行仍未知，P3/P2/P1未完成、识别最后。不操作游戏/聊天，不改本局、私人配置、地图或旧计算，不给路线建议和概率。'
validation='本机35项相关必要测试全部通过，含新模型8项、新界面5项、332既有节点接入11项和版本页11项；完整两表可重复构建字节一致。Windows原生临时MainWindow共47项唯一检查通过，遍历14个原始入口、8段对话6组选项、2/8不同代价、7/8源石锭边界、笼控器三态及0/1种子边界、分支独立与离开、无猜件数/生命保底/当前加成、两组真实非零阅读状态经父页刷新保留，实际坏源清旧/手选恢复、重复开窗、父源失效和实际主窗关闭清子窗。节点目录两入口默认不代入测试的100源石锭/持有/3枚种子，新增源失效时保留旧目录文字；最终7张实际PNG全部直接查看，包含外层版本提示。七类真实外部调用零，临时本局及旧计算上下文不变；原项目测试窗正常更新可见响应且前台，正常关闭到启动私人五路径一致。533旧维护选择器原序保留，现535。首次添加选择器的准备断言因实际模块声明是单行元组而失败，随后按实际结构修正，未当作功能验收失败或通过。旧332两个源文件换行归一为CRLF，无关逻辑不变。仅本机必要验证，不重跑全量或未变索引25单测；320完整范围/原失败/不可用证据仍属历史，下次335。'
nname='verification/sections/333-necessary-attempt1/process.json';wname='verification/sections/333-native-attempt1/actual/window.json';pname='verification/sections/333-native-attempt1/process.json'
n,w,p=map(read,(nname,wname,pname));m=read('verification/sections/333-main-window.json');a=read('verification/sections/333-source-audit.json');v=read('verification/sections/333-root-visual.json')
assert n['passed']and n['methods_ran']==35 and w['passed']and w['qpa']=='windows'and w['qt_exit_code']==0 and w['unique_checks']==47 and w['verification_window_closed']
assert len(w['same_identity_refresh_observations'])==2 and len(w['screenshots'])==7 and len(w['actual_readings'])==6 and all(x==0 for x in w['external_operation_attempts'].values())
assert p['passed']and p['window_receipt_sha256']==sha(wname)
for result in(n,w):
 assert result['source_sha256_before']==result['source_sha256_after']
 for name,h in result['source_sha256_after'].items():assert sha(name)==h,name
assert v['passed']and len(v['final_screenshot_reviews'])==7 and a['ordered_previous533_preserved']and len(a['current_selectors'])==535
assert m['passed']and m['private_entire_normal_close_and_start_interval_unchanged']and m['window_visible_and_responsive']
now=datetime.now(timezone(timedelta(hours=8))).isoformat();pending='<!-- section333-publication-pending -->本地验收完成，普通推送及真实远端核对待完成。'
r={'section':333,'kind':'functional_section','title':title,'new_capability':change,'limitations':[limits],'at_Beijing':now,'branch':'codex/p2-development','necessary_validation':{**pin(nname),'methods_run':35,'actual_exit':0},'native_windows_validation':{**pin(wname),'process':pin(pname),'unique_checks':47,'actual_Qt_exit':0,'documented_events':2,'document_scenes':8,'document_choices':6,'original_source_entries':14,'new_catalogue_groups':2,'exact_scene_links':8,'real_nonzero_refresh_states':2,'actual_MainWindow_entry_and_close_exercised':True,'all_seven_real_external_operations_zero':True},'root_visual_review':pin('verification/sections/333-root-visual.json'),'source_audit':pin('verification/sections/333-source-audit.json'),'original_project_window':pin('verification/sections/333-main-window.json'),'source_sha256':n['source_sha256_after'],'validated_source_sha256':w['source_sha256_after'],'full_suite_rerun':False,'last_full_receipt':'verification/full-320/summary.json','last_full_receipt_is_historical_for_this_changed_source':True,'last_full_validation_sha256':sha('verification/full-320/summary.json'),'next_periodic_full_section':335,'P3_complete':False,'P2_complete':False,'P1_complete':False,'private_state_contents_parsed_copied_or_restored':False,'private_state_hashed_locally_for_preservation_only':True,'private_hashes_published':False,'game_operated':False,'chat_sent':False,'cloud_publication_binding':'enclosing_commit','cloud_published':False,'execution_environment':'local_original_windows_project_venv','local_source_parity_required_for_cloud_publication':True}
(ROOT/'verification/sections/333.json').write_bytes(enc(r));details=change+'\n\n'+validation+'\n\n'+limits+'\n\n'+pending
old_wip=subprocess.check_output(['git','show',parent+':WORK_IN_PROGRESS.md'],cwd=ROOT);(ROOT/'WORK_IN_PROGRESS.md').write_bytes(('## 第333节 + '+title+'\n\n'+now+'。'+details+'\n\n以下为历史记录；当前断点以上述333为准。\n\n').replace('\n','\r\n').encode()+old_wip)
doc('PROJECT_COMPLETED.md','## 第333节 + '+title+'\n\n'+now+'。'+details+'\n\n'+(ROOT/'PROJECT_COMPLETED.md').read_text('utf8'))
s=(ROOT/'AGENTS.md').read_text('utf8');end=s.index('\n## ',3);doc('AGENTS.md','## 当前续接 · 第333节 + '+title+'\n\n'+details+'\n\n继续P3；334从当前事件前置、完整奖励池、未有目录的新事件与固定地图实际剩余缺口接续，未启动。测试优先本机；保留到期完整范围，下次335；严格低于15%才开始完整收尾。\n'+s[end:])
s=(ROOT/'PROJECT_REQUIREMENTS.md').read_text('utf8');start=s.index('<!-- current-delivery:start -->');end=s.index('<!-- current-delivery:end -->')+len('<!-- current-delivery:end -->');doc('PROJECT_REQUIREMENTS.md',s[:start]+'<!-- current-delivery:start -->\n## 第333节 + '+title+'\n\n'+details+'\n<!-- current-delivery:end -->'+s[end:])
s=(ROOT/'PROJECT_PROGRESS.md').read_text('utf8').replace('更新：2026-10-20。','更新：2026-10-21。');old='其余未覆盖完整事件表及其奖励条件';new='沉寂之屋笼控器领取件数/实际发放与生命代价底限、红苔完整资格/实际消耗和下一区域执行/阶段/节点覆盖及后续奖励，其余未覆盖完整事件表及其奖励条件';assert s.count(old)==1;doc('PROJECT_PROGRESS.md',s.replace(old,new,1))
cp=read('DEVELOPMENT_CHECKPOINT.json');assert cp['completed_sections']==332 and cp['next_section']==333
for key in('current_section_validation','latest_section_environment','cloud_publication_closeout'):
 if key in cp:cp['historical_before333_'+key]=cp.pop(key)
cp.update(completed_sections=333,latest_functional_section=333,next_section=334,batch_status='P3_SECTION333_LOCAL_ACCEPTED_PUBLICATION_PENDING',next_action='第333节 + '+title+'已本机必要验收；普通推送核对后334接续P3实际剩余缺口，未启动。下次335。',full_validation_due=False)
cp['sections'].append({'number':333,'completion_ref':'p3-section-333','topic':title,'verification':'verification/sections/333.json'});cp['functional_sections_since_latest_requirement'].append(333)
cp['current_section_save']={'section':333,'verification':'verification/sections/333.json','scope':'current_functional_section','binding':'enclosing_commit'};cp['last_verified_cloud_save']['scope']='previous_functional_section'
cp['current_section_validation']={'section':333,'receipt':'verification/sections/333.json','methods_run':35,'native_isolated_window_checks':47,'documented_events':2,'document_scenes':8,'document_choices':6,'original_source_entries':14,'new_catalogue_groups':2,'exact_scene_links':8,'real_nonzero_refresh_states':2,'full_suite_rerun':False,'last_full_receipt':'verification/full-320/summary.json','last_full_receipt_is_historical_for_current_changes':True}
cp['latest_section_environment']={'section':333,'receipt':'verification/sections/333.json','native_windows':validation,'native_game_or_chat_verified':False,'current_section_full_rerun':False,'last_full_receipt':'verification/full-320/summary.json'}
cp['windows_native_validation']=validation;cp['current_batch'].update(status=cp['batch_status'],completed_sections=333,next_section=334,next_section_started=False,receipt='verification/sections/333.json',batch_closed=False)
cp['policy'].update(current_usage_remaining_percent=98,current_usage_receipt='verification/sections/333-preparation/usage-final.json',verification_execution_preference='local_project_environment',avoid_duplicate_cloud_tests=True)
cp['current_data_versions'].update(current_vine_events_game_commit='bee3f83c5d60590b5e1cd42b8d09d00ce32ab10d',current_vine_document_revision=352356,current_vine_events=2,current_vine_scenes=8,current_vine_choices=6,current_vine_items=3,current_node_reader_aggregate_catalogue_groups=27,current_node_reader_aggregate_event_titles=25,current_node_reader_aggregate_types=9,current_node_actual_version_or_phase_verified=False)
(ROOT/'DEVELOPMENT_CHECKPOINT.json').write_bytes(enc(cp))
doc('CLOUD_HANDOFF.md',(ROOT/'CLOUD_HANDOFF.md').read_text('utf8')+'\n<!-- section333-handoff:start -->\n## 第333节 + '+title+'\n\n'+details+'\n<!-- section333-handoff:end -->\n')
out=ROOT/'verification/sections/333-preparation';shutil.copyfile(ROOT/'.cache/open_test_window_333.py',out/'execution-main-window.py')
runpy.run_path(str(ROOT/'scripts/update_cloud_index.py'))['update'](ROOT)
out=ROOT/'verification/sections/333-closeout';out.mkdir();(out/'execution-closeout.py').write_bytes(Path(__file__).read_bytes());(out/'applied.json').write_bytes(enc({'section':333,'local_accepted':True,'ordinary_cloud_publication_verified':False,'next334_started':False,'at_Beijing':now}))
print(json.dumps({'section':333,'local_accepted':True,'ordinary_publication_pending':True},ensure_ascii=False))
