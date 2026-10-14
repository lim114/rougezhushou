from pathlib import Path
from datetime import datetime,timezone,timedelta
import hashlib,json,re,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
def sha(name):return hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
def load(name):return json.loads((ROOT/name).read_bytes())
def write(name,value):(ROOT/name).write_bytes((json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
def text(name,value):(ROOT/name).write_bytes(value.replace('\r\n','\n').encode('utf8'))
stamp=datetime.now(timezone(timedelta(hours=8))).isoformat()
full='verification/full-275/'
offline=load(full+'windows-offline-attempt3.json');process=load(full+'windows-offline-attempt3-process.json')
freeze=load(full+'source-freeze-reset-repair.json');prior=load(full+'source-freeze.json')
assert offline['available_checks_passed'] and offline['failures']==offline['errors']==0
assert process['terminal'] and process['actual_process_exit']==0
assert offline['selectors']==freeze['selectors'] and set(prior['selectors'])<=set(offline['selectors'])
assert offline['source_sha256']==freeze['source_sha256'] and not offline['source_drift']
for p,h in freeze['source_sha256'].items():assert sha(p)==h,p
for p,h in freeze['reference_sha256'].items():assert sha(p)==h,p
legacy=load(full+'legacy-window-attempt3/actual/native275-launcher-closure.json')
legacy_result=load(full+'legacy-window-attempt3/actual/wine-ui-100.json')
supervisor=load(full+'legacy-window-attempt3/supervisor.json')
audit=load(full+'saved-readback-attempt3/independent-full275-saved-readback-summary.json')
assert legacy['passed'] and legacy['actual_current_native_windows_window_verified'] and not legacy['source_drift']
assert legacy_result['passed'] and legacy_result['complete_ui_validation']
assert supervisor['status']=='completed' and supervisor['owned_job_no_live_execution_verified'] and supervisor['supervisor_exit']==0
assert audit['passed'] and audit['runtime_records']==4283 and audit['saved_typed_rows']==52
assert audit['current862_assert_AST_order_matches_original261'] and audit['original552_maintry_bytes_unchanged']
assert audit['historical_projection_controls']==42 and audit['exact_bridge_indices']==[18,19,20,21,38,39,40,41,44,45]
current30=load(full+'current-window-attempt3/current30/actual/window.json')
current29=load(full+'current-window-attempt3/current29/actual/window.json')
assert not current30['passed'] and current30['failure']['type']=='OSError' and '1314' in current30['failure']['message']
assert current29['passed'] and len(current29['checks'])==29
assert set(freeze['exact_delta']) == {'rouge/sp_recovery_clock.py','rouge/sp_setter_reference.py','rouge/data/sp-setter-source.json','tests/test_sp_recovery_clock.py'}
assert audit['actual_native_attempt']==3
correction=load(full+'saved-readback-attempt3/label-correction.json')
assert sha(full+'saved-readback-attempt3/independent-full275-saved-readback-summary.json')=='7756177db3eaac979879d6cdf85f75b55b5f2d4ee95e1155d8ca23d2130f4f50'
window=load('verification/sections/275-window-reset-repair.json');main=load('verification/sections/275-main-window-reset-repair.json')
assert window['passed'] and window['qpa']=='windows' and window['visible']
for p,h in window['loaded_source_sha256'].items():assert sha(p)==h,p
assert main['native_original_window_startup'] and main['private_json_files_changed']==0 and main['private_json_new_files']==0
assert main['desktop_visually_inspected_with']!='pending'
review=load(full+'repair/sp-clock-reset/new-source-review.json');assert review['passed'] and review['core_sha256']==sha('rouge/sp_setter_reference.py')
necessary=load(full+'repair/necessary-contracts.json');assert necessary['passed'] and necessary['errors']==necessary['failures']==0
prep=load('.cache/full275-preparation.json')
write(full+'runtime-preparation.json',prep)
write(full+'native-symlink-preflight.json',load('.cache/full275-preflight/symlink-probe.json'))
summary={'after_section':275,'kind':'functional_section_full_validation','checked_at_Beijing':stamp,
 'available_checks_passed':True,'complete_repository_validation':False,'scope_not_reduced':True,
 'native_current_windows_gui_verified':True,'native_windows_game_chat_verified':False,
 'actual_platform':'Native Windows offline and isolated real Windows MainWindow; WSL/Linux/Wine not available here.',
 'source_files':len(freeze['source_sha256']),'maintained_selectors':len(offline['selectors']),
 'all_original407_and_261_393_selectors_retained':True,'source_drift':[],
 'tested_worktree_parent_commit':freeze['parent_commit'],
 'source_freeze':'verification/full-275/source-freeze-reset-repair.json','source_freeze_sha256':sha(full+'source-freeze-reset-repair.json'),
 'offline_windows':{k:offline[k] for k in ('tests_run','tests_passed','historical_or_declared_skips','failures','errors','unavailable_records','unavailable_parent_count','qt_shutdown','qt_shutdown_error')},
 'actual_offline_process_exit':0,'offline_receipt':full+'windows-offline-attempt3.json',
 'legacy_window':{'passed':True,'actual_child_and_supervisor_exit':0,'owned_job_no_live_execution_verified':True,
  'runtime_seconds':supervisor.get('runtime_seconds',supervisor.get('elapsed_seconds')),
  'runtime_check_records':4283,'passed_flag_records':4281,'metadata_records':2,'saved_states':52,'explicit_text_requests':156,
  'current_assertion_AST_and_order':862,'original_maintry_checks':552,'original_maintry_bytes_unchanged':True,
  'historical_projection_records':42,'exact_bridge_indices':audit['exact_bridge_indices'],'real_empty_trace_rows':26,
  'typed_readback_verified':True,'receipt':full+'legacy-window-attempt3/actual/wine-ui-100.json',
  'closure':full+'legacy-window-attempt3/actual/native275-launcher-closure.json',
  'independent_saved_readback':full+'saved-readback-attempt3/independent-full275-saved-readback-summary.json',
  'inherited_wine_filenames_and_historical_header_flags_preserved':True,
  'actual_current_Windows_authority':'Fresh win32 visible HWND/QPA Windows ledger plus actual owned Windows supervisor; not original historical Windows/game/chat integration.'},
 'current_window':{'maintained_scope':30,'available_original_workflows_passed':29,'actual_full30_attempt_preserved':True,
  'symlink_specialization':'unavailable: actual native Path.symlink_to raised WinError1314 before its product assertions; not passed',
  'current29_receipt':full+'current-window-attempt3/current29/actual/window.json',
  'full30_failure_receipt':full+'current-window-attempt3/current30/actual/window.json',
  'window_freeze_authority':'Fresh A3 actual current30/current29 and legacy execution bind all1160 repaired sources. Earlier A1/A2 remain historical evidence only.'},
 'unavailable_scopes':['16 genuine Windows symlink prerequisite subcases /6 parents, attempted and retained with exact traceback; no privilege changes or surrogate links.',
  'Original Linux/Wine execution environment unavailable; historical261 evidence remains historical.',
  'Historical private/native integration, deferred original095/109 scope and game/chat actions remain unverified.'],
 'original_failures_preserved':{'offline_attempt1':full+'windows-offline-attempt1.json',
  'legacy_attempt1':full+'first-attempt-evidence/legacy/actual/wine-ui-100.json',
  'first_frozen_all1159_sources':full+'first-attempt-evidence/frozen-public-source.tar.gz',
  'contract_maintenance':full+'repair/legacy-contracts/draft-application.json'},
 'contract_maintenance_limits':'Exact pre/post047 AST historical boundary restored; current16 guard retained. Default nodes have no route advice; historical text only explicit diagnostics. Failed planes remain rejected alongside separately verified direct points. Ten actual old060 inputs retained, full current pair only excludes five river reference blocks;2517+65 old numeric leaves conserved and49 source-backed certainty retirements explicit. No product numbers changed to satisfy old tests.',
 'P2_complete':False,'current_worktree_validation_authority':True,'reset_repair':{'same_input_receipt':full+'repair/sp-clock-reset/same-input-repair.json','fresh_source_review':full+'repair/sp-clock-reset/new-source-review.json','restart_rule':'Reset(newP,true) P=R=max(0,newP); KeepPast P remains raw and R=max(0,newP-(oldP-oldR)); MarkInvalid -Q/-Q'},'readback_label_correction':full+'saved-readback-attempt3/label-correction.json','next_full_validation_after':290,'goal_target_section':300}
write(full+'summary.json',summary)
files=['rouge/sp_recovery_clock.py','tests/test_sp_recovery_clock.py','rouge/sp_setter_reference.py','rouge/data/sp-setter-source.json','rouge/calibration.py','rouge/offline_tools_view.py',
 'scripts/verify_full_available.py','scripts/verify_sp_setter_window_275.py','tests/test_sp_setter_reference.py',
 'tests/test_offline_tools_view.py','tests/test_base_settlement_planning.py','tests/test_full_validation_prerequisites.py',
 'tests/test_readable_battle_047.py','tests/test_readable_map_047.py','tests/test_map_projection_048.py','tests/test_map_projection_049.py','tests/test_river_reporting_060.py']
for folder in ('research/p2-sp-setter-275','research/presentation-source-guard/047-original-pre','research/river-reporting-original-060','verification/full-275'):
 files += [p.relative_to(ROOT).as_posix() for p in sorted((ROOT/folder).rglob('*')) if p.is_file()]
files += [p.relative_to(ROOT).as_posix() for p in sorted((ROOT/'verification/sections').glob('275*')) if p.is_file() and p.name not in ('275.json','275-publication.json')]
assert len(files)==len(set(files));required={p:sha(p) for p in files}
source=load('rouge/data/sp-setter-source.json');reused=dict(source['source_artifacts_sha256'])
for p,h in reused.items():assert sha(p)==h,p
for p in ('rouge/app.py','rouge/information_scope.py','rouge/sp_recovery_clock.py','tests/test_route_information_scope.py',
 'tests/test_readable_battle_047_current_guard.py','tests/test_readable_battle_047_successor.py','tests/test_river_reporting_060_successor.py'):
 reused[p]=sha(p)
record={'section':275,'kind':'functional_section','title':'SP写入存活条件、独立上限与public返回/完整复制资格',
 'at_Beijing':stamp,'branch':'codex/p2-development','prior_commit':freeze['parent_commit'],
 'remaining_item':'P2自然技力请求的实际写入资格/限幅/返回边界；实际SP/14与30属性/初始化与完整周期仍未完成',
 'new_capability':['public setter固定force=false，先独立存活读取，再上限读取；internal/do分支的显式force不借恢复force',
  '原生signed max(min(value,maxSp*Q),0)与已知零分支，normal getter/encoding/16+16+8复制阶段分别保留',
  'public void正常返回与internal false明确分开，复制异常前缀不称完整结构、不称实际编码/解码SP',
  '与274显式独立tick/drain/recover请求链接、目标/无间隔变化资格和真实正常返回矛盾，部分已证与完整未知分开',
  '中文局外工具公共三算例、刷新保留、禁止覆写实际情景与本局记录'],
 'files':files,'required_raw_sha256':required,'reused_source_sha256':reused,
 'validation':{'new_test_methods':32,'related_checks':191,'related_log':'verification/full-275/repair/sp-clock-reset/related-final.log',
  'independent_source_probes':32,'independent_source_checks':163,'readonly_review':'verification/full-275/repair/sp-clock-reset/new-source-review.json',
  'candidate_original_file':{'methods':55,'unique_reachable_instructions':2599,'unique_instruction_bytes':11190,'raw_source_spans_rechecked':3971,'preparation_artifact_byte_guards':14,'game_dll_executed':False,'process_memory_read':False},
  'full':summary,'contract_maintenance_checks':{'tests_run':160,'tests_passed':154,'unavailable_records':16,'failures':0,'errors':0,'receipt':full+'repair/necessary-contracts.json'},
  'native_public_window':window,'native_original_startup':main,
  'literal_public_gold':{'independent_clock_request_raw':[38654705664,30064771072],
   'encoder_argument_raw':[25769803776,0],'copy_bytes':[40,0,40],'qualified_full_copies':2,'actual_SP':None}},
 'limits':['FP编码输入与正常复制资格参考不是实际SP或完整初动/回转/周期；未知完整总量仍未知。',
  '275定期可用全量通过，16真实权限缺口/原Linux-Wine/历史私样本/游戏聊天不计通过；未修改privileges或旧缓存。',
  'P2未完成；276初始SP/控制器纯文件47方法证据仅准备，未计功能。'],
 'next_section':276,'next_full_validation_after':290,'goal_target_section':300}
write('verification/sections/275.json',record)
cp=load('DEVELOPMENT_CHECKPOINT.json');assert cp['completed_sections']==274 and cp['next_section']==275
cp['historical_before275_cloud_publication_closeout']=cp.pop('cloud_publication_closeout');cp['last_verified_cloud_save']['scope']='previous_functional_section'
cp['completed_sections']=cp['latest_functional_section']=275;cp['next_section']=276;cp['batch_status']='ACTIVE_BATCH_262_300_SECTION275_LOCAL_VALIDATED'
cp['current_section_save']={'section':275,'verification':'verification/sections/275.json','scope':'current_functional_section','binding':'enclosing_commit','commit_reference':'the commit containing275 source/receipt/requirements/index','batch_closed':False}
cp['current_batch'].update(status=cp['batch_status'],next_section=276,next_section_started=False,next_full_validation_after=290,receipt='verification/sections/275.json',batch_closed=False)
cp['next_full_validation_after']=cp['policy']['next_full_validation_after']=cp['current_batch_commit_policy']['next_full_validation_after']=290
cp['sections'].append({'number':275,'kind':'functional_section','topic':record['title'],'verification':'verification/sections/275.json'})
cp['functional_sections_since_latest_requirement'].append(275)
cp['historical_before275_last_full_validation']=cp['last_full_validation']
cp['last_full_validation']={'after_section':275,'receipt':full+'summary.json','available_checks_passed':True,'complete_repository_validation':False,'scope_not_reduced':True,'native_current_windows_gui_verified':True,'native_windows_game_chat_verified':False,'unresolved_available_failures':False,'original_failed_attempts_preserved':True}
cp['current_available_full_validation']={'section':275,'available_scope_passed':True,'receipt':full+'summary.json','native_windows_game_chat_verified':False}
cp['next_action']='276接续有证初始SP中间值/两次独立容量与SP controller Reset/UpdateData/默认0时钟链；47方法仅准备，不借275 setter或任意MXCSR。后续至300；定期290及最终300完整全量；P2优先，探索仅节点信息。'
cp['latest_section_environment']={'section':275,'native_windows':'191 related,160 maintenance and4331 full offline; real legacy52/4283 plus29 current workflows and public setter window/original app visible','native_game_or_chat_verified':False,'new_Linux_Wine_full_run':False,'full_reference':full+'summary.json','native_symlink_unavailable_records':16}
cp['native_section275_validation']={'receipt':'verification/sections/275-main-window-reset-repair.json','native_original_window_startup':True,'private_json_files_checked':3,'private_json_files_changed':0}
cp['historical_user_resume280']=cp['latest_user_resume']
cp['latest_user_resume']={'at_Beijing':stamp,'quote':'逐批推进至300节','kind':'explicit_goal','target_section':300,'continuous_work_authorized':True}
cp['policy']['stop_after_section']=cp['policy']['current_user_batch_target_section']=300
cp['batch_target_section']=cp['batch_stop_after_section']=300
cp['current_batch']['end']=300
cp['policy']['batch_target_section']=300
write('DEVELOPMENT_CHECKPOINT.json',cp)
paragraph=f'{stamp}。新增独立存活/force/上限、signed FP限幅与编码/40字节复制资格，public void正常与internal false分离；接274独立请求，不推实际SP/完整周期。55方法/2599原指令/11190字节/3971 span，32新方法、191相关检查及32探针/163独立核对通过。收尾原件核验发现274 restart遗漏Max(0,newP)，同输入修正P/R为0/0；保留负KeepPast及MarkInvalid区别、原反例/失败/旧源码与A1/A2。完整A3保持408选择器/1160源码：Windows4331项、4252通过、73声明跳过、16真权限不可用，零失败错误。A3旧窗口4283记录/52状态/156请求/42投影/10桥接及typed读回、862 AST/552原主流程通过，current29通过；current30真实1314不计通过。047/060真实原件恢复及合同维护有证，未恢复旧完整总量的错误确定性。修复后公共Windows窗口与原24132测试窗口实际可见，3私人JSON未变。原Linux/Wine、历史私样本/游戏聊天未计通过；P2未完成。回执verification/sections/275.json与verification/full-275/summary.json；下一276，目标300，定期290/最终300全量。'
wip=(ROOT/'WORK_IN_PROGRESS.md').read_text();wip,n=re.subn(r'<!-- section275-active:start -->.*?<!-- section275-active:end -->\n\n','',wip,count=1,flags=re.S);assert n==1
text('WORK_IN_PROGRESS.md','## 功能第275节 · '+record['title']+'\n\n'+paragraph+'\n\n'+wip)
text('PROJECT_COMPLETED.md','## 功能第275节 · '+record['title']+'\n\n'+paragraph+'\n\n'+(ROOT/'PROJECT_COMPLETED.md').read_text())
req=(ROOT/'PROJECT_REQUIREMENTS.md').read_text()
block='<!-- current-delivery:start -->\n当前恢复目标：逐批推进至300节（替代280）。275实质功能与定期完整可用验收完成，后续276；定期290、最终300保持全部选择器/52状态/当前30专项范围。Windows完整离线4331项，16真symlink权限缺口不计通过；原Linux/Wine/历史私样本/游戏聊天未复验，P2未完成。\n探索只提供节点、事件条件、连接、历史与作战入口，不推荐/排序/比较/自动选路。275完成SP存活门/独立上限、编码/40字节复制及public/internal返回参考；修正274 restart的原件Max(0,newP)，不改变KeepPast负周期或MarkInvalid。真实SP/实际14与30属性/初动/完整回转周期仍未知。276初始化/控制器47方法仅source preparation，不能套public setter的0 clamp或任意float舍入。\n<!-- current-delivery:end -->'
req,n=re.subn(r'<!-- current-delivery:start -->.*?<!-- current-delivery:end -->',block,req,flags=re.S);assert n==1
req=req.replace('2026-10-14最新目标：“逐批推进至280节”，明确恢复开发，替代下列261后等待/暂停要求。当前262–280按每节实质交付推进；275定期全量，最终280完整可用范围验收，保留原件缺口。280后停止目标，不自动扩大为旧400目标。','2026-10-14最新目标：“逐批推进至300节”，替代280目标及261后暂停。当前262–300按每节实质交付推进；275/290定期全量、最终300完整可用范围验收，保留原件及环境缺口。300后停止该目标，不自动扩大为旧400目标。')
text('PROJECT_REQUIREMENTS.md',req)
progress=(ROOT/'PROJECT_PROGRESS.md').read_text();old='补回047原pre源码和060原十例输出（原SHA66e5babd…f6e0326），逐叶核验其余历史变更适用性；原Windows12条历史失败保留，待原件及私样本复验'
assert old in progress
text('PROJECT_PROGRESS.md',progress.replace(old,'其余历史版本/原Windows及私样本的完整适用性复验；真实Windows符号链接权限专项尚不可执行，原失败保留'))
agents=(ROOT/'AGENTS.md').read_text();first,rest=agents.split('\n',1);assert '当前274功能' in first
text('AGENTS.md','用户2026-10-14最新恢复目标：“逐批推进至300节”，替代280及261后等待。当前275功能与完整可用全量完成，后续276；P2优先，有证P3可独立推进，P1保留，识别最后。每节实质功能、验收、要求/索引同提交，普通推送后核对真实远端。完整范围保持，下一定期290与最终300；权限/原Linux-Wine/原Windows历史与私样本未计通过。300完成后停止该目标；下段261为历史交接。\n'+rest)
attrs=(ROOT/'.gitattributes').read_text()
for rule in ('verification/full-275/** -text whitespace=cr-at-eol,-blank-at-eol,-blank-at-eof','verification/sections/275* -text whitespace=cr-at-eol,-blank-at-eol,-blank-at-eof'):
 if rule not in attrs:attrs+='\n'+rule+'\n'
text('.gitattributes',attrs)
from scripts.update_cloud_index import update,validate_delivery
update(ROOT)
for p in ('CLOUD_INDEX.json','CLOUD_HANDOFF.md'):text(p,(ROOT/p).read_text())
print(json.dumps({'section':275,'delivery_guard':validate_delivery(ROOT,cp),'required_files':len(required),'full_tests':offline['tests_run'],'full_failures':0,'full_errors':0,'unavailable_not_passed':16,'private_changed':0},ensure_ascii=False))
