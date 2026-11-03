from pathlib import Path
from hashlib import sha256,sha1
from datetime import datetime,timezone
import ast,ctypes,difflib,json,re,runpy,subprocess,sys,time
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts'),str(R/'.cache/305-window-tooldeps')]
BASE='a53cdf96a35133d2e1aa9ad801935ed4f2a55d2c';B=R/'verification/maintenance/calculation-context-review-20261031';prefix=B.relative_to(R).as_posix()+'/'
def read(n):return json.loads((R/n).read_bytes())
def pin(n):
 p=R/n;raw=p.read_bytes();return {'path':p.relative_to(R).as_posix(),'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}
def write(n,v):(R/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf8')
def text(n,v):
 p=R/n
 if not p.exists():p.parent.mkdir(parents=True,exist_ok=True);p.write_text(v,'utf8');return
 a=p.read_bytes().decode('utf8').splitlines(keepends=True);out=v.splitlines(keepends=True)
 for x,y,k in difflib.SequenceMatcher(None,[s.rstrip('\r\n')for s in a],[s.rstrip('\r\n')for s in out],autojunk=False).get_matching_blocks():
  for i in range(k):out[y+i]=a[x+i]
 p.write_bytes(''.join(out).encode('utf8'))
def old(n):return subprocess.check_output(['git','show',BASE+':'+n])
assert subprocess.check_output(['git','rev-parse','HEAD']).decode().strip()==BASE
before=read('research/calculation-context-review-20261031/source-before.json');assert sha256(old('rouge/app.py')).hexdigest()==before['sha256']
changed=['rouge/app.py'];unchanged=['rouge/damage.py','rouge/reporting.py','rouge/estimate.py','rouge/ui_state.py','rouge/run_state.py','rouge/account_cache.py','PROJECT_REQUIREMENTS.md']
receiver_files=['rouge/'+name+'_view.py'for name in('offline_tools','paired_calibration','attack_state_sequence','timing_calibration','bounded_calibration','calibration_experiment','recipient_native_ratio','relic_order_precision')]
for n in unchanged+receiver_files:assert old(n)==(R/n).read_bytes(),n
assert not subprocess.check_output(['git','diff','--name-only',BASE,'--','rouge/data']).strip()
names={'offline_tools','paired_calibration','attack_state_sequence','timing_calibration','bounded_calibration','calibration_experiment','recipient_native_ratio','relic_order_precision'}
class WithoutFanout(ast.NodeTransformer):
 def visit_If(self,node):
  t=node.test
  if isinstance(t,ast.Call)and isinstance(t.func,ast.Name)and t.func.id=='hasattr'and len(t.args)==2 and isinstance(t.args[1],ast.Constant)and t.args[1].value in names:return None
  return self.generic_visit(node)
 def visit_For(self,node):
  if isinstance(node.iter,ast.Attribute)and node.iter.attr=='_scenario_receivers':return None
  return self.generic_visit(node)
previous=ast.parse((R/'research/calculation-context-review-20261031/before-calculate.py').read_bytes()).body[0]
previous.name='_calculate_current';previous.body=previous.body[1:];previous=WithoutFanout().visit(previous)
current=next(n for n in ast.walk(ast.parse((R/'rouge/app.py').read_bytes()))if isinstance(n,ast.FunctionDef)and n.name=='_calculate_current');current=WithoutFanout().visit(current)
assert ast.dump(previous,include_attributes=False)==ast.dump(current,include_attributes=False),'Calculation adapter changed beyond batching/fanout extraction'
tests=read(prefix+'tests-current/results.json');assert tests['passed']and tests['tests_run']==16 and tests['failed']==tests['errors']==0 and not tests['skipped']and not tests['forbidden_external_calls']
ids=re.findall(r'^test_\w+ \(([^)]+)\)',(R/(prefix+'tests-current/stderr.txt')).read_text('utf8'),re.M);assert len(ids)==len(set(ids))==16
assert read(prefix+'tests-current/process.json')['actual_observed_exit']==0
paired=read(prefix+'tests-current/paired-scenarios.json');assert len(paired)==87 and len({r['operator']for r in paired})==32 and all(r['complete_result_and_report_equal']for r in paired)
original=read(prefix+'before/results.json');assert original['tests_run']==6 and original['failed']==4 and original['errors']==0 and read(prefix+'before/process.json')['actual_observed_exit']==1
authoring=read(prefix+'tests-final/results.json');assert authoring['tests_run']==16 and authoring['failed']==0 and authoring['errors']==1
native=read(prefix+'native/receipt.json');assert native['passed']and native['unique_checks']==23 and not any(native['external_operation_attempts'].values())and read(prefix+'native-process.json')['actual_observed_exit']==0
assert native['source_sha256_after']['rouge/app.py']==pin('rouge/app.py')['sha256']
images=native['screenshots']+read(prefix+'native/images.json')['images'];assert len(images)==5
for row in images:assert sha256((R/row.get('file',row.get('path'))).read_bytes()).hexdigest()==row['sha256']
write(prefix+'native/visual-review.json',{'images':images,'all_five_final_originals_individually_viewed':True,'current_error_and_diagnostic_import_unavailable_checked':True,'temporary_public_previews_only':True,'whole_video_parity_claimed':False})
for n in ('.cache/verify_calculation_context_native.py','.cache/run_calculation_context_checks.py'):(B/Path(n).name).write_bytes((R/n).read_bytes())
(B/'tests-current/test-source.py').write_bytes((R/'tests/test_calculation_context_review.py').read_bytes())
live=read(prefix+'live-window/window.json');assert live['passed']and live['private_six_paths_unchanged']
import win32gui,win32process
for w in live['owned_windows']:assert win32gui.IsWindowVisible(w['hwnd'])and win32process.GetWindowThreadProcessId(w['hwnd'])[1]==w['pid']and not ctypes.windll.user32.IsHungAppWindow(w['hwnd'])
first=read('.cache/calculation-context-review-live-status.json');time.sleep(2.2);last=read('.cache/calculation-context-review-live-status.json');assert last['toolbar_visible']and last['elapsed_since_launch']>first['elapsed_since_launch']
write(prefix+'live-window/desktop-review.json',{'actual_Windows_MCP_snapshot_and_image_view':True,'region':[1716,1164,2130,1218],'test_window_visible_responding_and_Qt_timer_advanced':True,'private_six_paths_unchanged_during_startup':True,'private_contents_or_hashes_published':False,'game_operated':False,'chat_sent':False})
net=len((R/'rouge/app.py').read_bytes().splitlines())-len(old('rouge/app.py').splitlines())
write(prefix+'source-review.json',{'baseline_commit':BASE,'changed_source':[pin(n)for n in changed],'unchanged_models_state_and_requirements':[pin(n)for n in unchanged],'unchanged_receivers_set_scenario_or_context_methods_reviewed_only_not_whole_modules':[pin(n)for n in receiver_files],'calculation_adapter_AST_equal_excluding_original_batch_gate_and_context_fanout':True,'removed_existence_branch_count':8,'replacement':'Initialize an empty receiver tuple before building controls, register the eight existing bound receiver methods after all are created. Keep original batch gate, calculation body/error reporting and ordering. On any unavailable current result, finally publishes None to the same receivers; existing set_scenario disables import without rewriting manual editors.','valid_32_operator_87_skill_complete_results_and_reports_equal':True,'physical_production_lines_net_added':net,'net_code_reduction_claimed':False,'independent_87_skill_mechanism_calibration_claimed':False,'end_to_end_speed_claimed':False,'private_source_or_duplicate_send_guards_removed':False,'test_authoring_failure':'First expansion iterated skill list members as integer IDs; actual source list contains records. Replaced with documented one-based list positions and reran all sixteen tests. Original failure receipt retained; not a product defect.','before_test_scope':'Six cases, four current-cache failures. Original equality case covered first three operators; final equality case expanded to all32/87, initial nine-skill success scope separate. Initial failure test module was not separately hash-frozen; raw original names/trace/exit and baseline app source are retained, not claimed as a frozen final test module.','REA_scope':'Complete Python source plus actual Qt runtime review under the skill; no new REA tool call. Existing toolbar bytecode and CJS analyses remain separate.','remaining':'Startup/developer-panel lifecycle and resource cost, other input/import paths and full private/native integration, independent mechanisms, entire video and whole program remain.'})
title='计算无可用结果时清除旧条件，集中登记八处面板更新'
write(prefix+'summary.json',{'kind':'implementation_review_maintenance','title':title,'baseline_commit':BASE,'completed_sections':440,'functional_section_added':False,'implemented_scope_passed':True,'different_tests':16,'passed_tests':16,'skipped':0,'new_tests':6,'original_reproduction_tests':6,'original_reproduction_failures':4,'original_actual_exit':1,'paired_UI_scenarios':87,'paired_UI_operators':32,'native_primary_unique_checks':23,'final_primary_images':5,'all_final_images_individually_viewed':True,'removed_existence_branches':8,'net_code_reduction_claimed':False,'independent_mechanism_calibration_claimed':False,'source_and_private_guards_retained':True,'test_window_updated':True,'private_six_paths_unchanged_during_startup':True,'source_review':pin(prefix+'source-review.json'),'tests':pin(prefix+'tests-current/results.json'),'native':pin(prefix+'native/receipt.json'),'full_validation_rerun':False,'full440_only_original_frozen_source':True,'whole_program_complete':False,'whole_video_parity_complete':False,'P3_complete':False,'P2_complete':False,'P1_complete':False,'game_operated':False,'chat_sent':False,'private_data_included':False,'publication_binding':'enclosing maintenance commit, ordinary push and actual remote/blob verification required'})
text('research/calculation-context-review-20261031/README.md','''# 当前计算到其它面板的条件更新回顾

阅读MainWindow构建、calculate入口及八个接收器的set_scenario/set_context方法（并非这八份模块的完整回顾），复用已有面板和更新方法。六项隔离场景先在真实基线上复现四个失败：输入错误、无干员、无技能和未实现干员时，主结果已不可用，五个明确“导入当前”入口仍缓存上一次条件；独立编辑/观察不等于这些旧条件仍可代表当前。

现保留批量输入入口，抽出原计算主体；没有可用结果时统一发布None，原方法关闭导入但保留编辑正文和独立计算。窗口构建前登记空接收表，八个面板建成后登记原绑定方法，代替八处分散hasattr判断；成功更新次序保持，其余构建阶段确有需要的判断保留。去掉批量门与分发后原计算主体AST完全相同，公式、报告、状态、八个接收器源码及资料不改。净增7物理行，不把删八个条件分支宣传为净减代码或提速。

最终16项不同必要检查通过，含六个新场景、六项本局/账号/重启/批量输入原检查及四项计算内核原检查。32名/87种已接入技能的原入口和新入口完整结果、报告逐一相等；这不是独立机制校准或实际面板准确证明。原生23项沿真实玩家窗口核对错误、恢复、无技能与未实现干员，五张最终原图逐张查看，独立声明编辑保持。原始六项四失败/退出1保留；首次扩大全目录测试将技能记录误当编号而出错，同批按原列表的一基序号修正并重跑，保留失败，不算产品问题。初始测试模块未单独冻结，原栈/名称/实际退出与基线源码保留；不冒充它与最终测试模块完全相同。

原项目测试小窗已更新并可见响应，启动六处私人路径保持，无游戏操作/真实聊天/个人上传。本轮使用完整源码与Qt实际运行，不新调用REA或制造字节码。功能440/未开441，719有序选择器；full440仍只原冻结源码。其它输入/导入、启动隐藏面板成本、独立机制、全视频外观/交互、全程序和P3/P2/P1未完成，识别最后。
''')
entry=f'''<!-- calculation-context-review-20261031:start -->
## 实现回顾维护 · {title}

修正四类无结果路径仍能导入旧条件的问题，复用原接收器禁用当前导入并保留声明正文；八个分散存在性判断改为创建后统一登记，构建期空表保留。原主体去除批量门/分发后AST相同，模型与数据不变；净增7行，不声称净减或提速。

原六项四失败保留，最终16项不同检查、32人87技能完整结果/报告新旧一致，原生23项及五图查看通过；不冒充87技能机制独立校准。小窗更新、启动六私人路径保持，零游戏/聊天/上传。回执：`{prefix}summary.json`。440/未开441、719选择器；其它导入/启动面板、机制、全程序/视频与P3/P2/P1未完成，识别最后。
<!-- calculation-context-review-20261031:end -->

'''
for n in ('WORK_IN_PROGRESS.md','PROJECT_COMPLETED.md'):text(n,entry+(R/n).read_text('utf8'))
n='PROGRAM_REVIEW.md';s=(R/n).read_text('utf8');s+='\n[当前计算条件分发回顾](research/calculation-context-review-20261031/README.md)修复无结果仍缓存旧导入条件，复用八个接收器并统一登记；32人87技能原结果/报告保持，16项检查和23项原生通过。仅入口与更新方法范围，不是独立机制校准或八份接收器全模块审查，全程序/视频仍未完成。\n';text(n,s)
n='PROJECT_PROGRESS.md';s=(R/n).read_text('utf8').replace('其余附属资料窗的对象释放和其它父页/原始日志的来源刷新','其余附属资料窗的对象释放和其它父页/原始日志的来源刷新、其余输入/导入路径及隐藏面板启动成本',1);text(n,s)
n='IMPLEMENTATION_STRATEGY.md';text(n,(R/n).read_text('utf8')+'\n[计算更新本机复用](research/calculation-context-review-20261031/README.md)使用八个已有接收方法的显式登记表，替换散落存在性判断；空表覆盖窗口构建阶段，批量输入完成后再算，失败清当前导入缓存而不改声明编辑。未重写数值模型，不称净减代码或端到端提速。\n')
cp=read('DEVELOPMENT_CHECKPOINT.json');cp['current_maintenance_save']={'kind':'implementation_review_maintenance','title':title,'receipt':prefix+'summary.json','binding':'enclosing_commit','functional_section_added':False,'status':'partial_program_review_calculation_context','review_checklist':'PROGRAM_REVIEW.md','review_checklist_sha256':pin('PROGRAM_REVIEW.md')['sha256'],'application_review_complete':False};cp['current_batch']['receipt']=prefix+'summary.json';cp['next_action']='继续完整程序回顾与视频逐页核对：隐藏面板启动/可达性、其它导入/来源刷新、同名变体卡片与历史有证字段，独立机制和完整视频仍未完成。计算无结果的旧当前条件已清理、八接收器分发已复用，32人87技能相等不充当准确性校准；识别最后。'
text('DEVELOPMENT_CHECKPOINT.json',json.dumps(cp,ensure_ascii=False,indent=2)+'\n');idx=runpy.run_path(str(R/'scripts/update_cloud_index.py'));idx['update'](R);assert idx['validate_delivery'](R,cp)['current_section']==440
from scripts.verify_full_available import maintained_selectors
selectors=maintained_selectors();assert len(selectors)==719 and selectors[-1]=='tests.test_calculation_context_review'
a=b"ADDITIONAL_MODULES += ('tests.test_history_reference_review',)";assert (R/'scripts/verify_full_available.py').read_bytes()==old('scripts/verify_full_available.py').replace(a,a+b"\r\n\r\nADDITIONAL_MODULES += ('tests.test_calculation_context_review',)")
assert read('CLOUD_INDEX.json')['requirements']['sha256']==pin('PROJECT_REQUIREMENTS.md')['sha256']
write(prefix+'final-audit.json',{'passed':True,'baseline_commit':BASE,'summary':pin(prefix+'summary.json'),'requirements':pin('PROJECT_REQUIREMENTS.md'),'cloud_index':pin('CLOUD_INDEX.json'),'different_tests':16,'paired_skill_scenarios':87,'native_checks':23,'ordered_selectors':719,'whole_program_complete':False,'whole_video_parity_complete':False,'at_UTC':datetime.now(timezone.utc).isoformat()})
(B/'record-source.py').write_bytes(Path(__file__).read_bytes())
files={p.relative_to(R).as_posix():{k:v for k,v in pin(p.relative_to(R)).items()if k!='path'}for p in sorted(B.rglob('*'))if p.is_file()and p.name!='archive-manifest.json'}
write(prefix+'archive-manifest.json',{'kind':'explicit_public_archive','files':files})
print(json.dumps({'passed':True,'different_tests':16,'paired_skills':87,'native_checks':23,'final_images':5,'archive_files':len(files),'whole_goal_complete':False}))
