from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import ast,ctypes,difflib,json,re,runpy,subprocess,sys,time
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts'),str(R/'.cache/305-window-tooldeps')]
BASE='f40a86f812d584f08ac9349bc7f362a498e34db0'
B=R/'verification/maintenance/relic-report-scope-review-20261031';prefix=B.relative_to(R).as_posix()+'/'
def read(n):return json.loads((R/n).read_bytes())
def pin(n):
 p=R/n;raw=p.read_bytes();return {'path':p.relative_to(R).as_posix(),'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}
def write(n,v):(R/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf8')
def text(n,v):
 p=R/n
 if not p.exists():p.parent.mkdir(parents=True,exist_ok=True);p.write_text(v,'utf8');return
 a=p.read_bytes().decode('utf8').splitlines(keepends=True);b=v.splitlines(keepends=True);out=list(b)
 for x,y,k in difflib.SequenceMatcher(None,[s.rstrip('\r\n')for s in a],[s.rstrip('\r\n')for s in b],autojunk=False).get_matching_blocks():
  for i in range(k):out[y+i]=a[x+i]
 p.write_bytes(''.join(out).encode('utf8'))
def old(n):return subprocess.check_output(['git','show',BASE+':'+n])
assert subprocess.check_output(['git','rev-parse','HEAD']).decode().strip()==BASE
before='research/relic-report-scope-review-20261031/before-reporting.py'
assert old('rouge/reporting.py')==(R/before).read_bytes()
def funcs(raw):return{n.name:ast.dump(n,include_attributes=False)for n in ast.parse(raw).body if isinstance(n,ast.FunctionDef)}
a=funcs(old('rouge/reporting.py'));b=funcs((R/'rouge/reporting.py').read_bytes())
assert a.keys()==b.keys() and all(a[n]==b[n]for n in a if n not in ('build_report','format_report'))
unchanged=['rouge/damage.py','rouge/estimate.py','rouge/relics.py','rouge/relic_attributes.py','rouge/relic_damage_factors.py','rouge/operator_engine.py','rouge/run_modifiers.py','rouge/timing.py','rouge/app.py','PROJECT_REQUIREMENTS.md']
for n in unchanged:assert old(n)==(R/n).read_bytes(),n
assert not subprocess.check_output(['git','diff','--name-only',BASE,'--','rouge/data']).strip()
results=read(prefix+'tests-current/results.json')
assert results['passed']and results['tests_run']==54 and results['failed']==results['errors']==0 and not results['forbidden_external_calls']
assert len(results['skipped'])==1 and '0.30用户缩减计算范围'in results['skipped'][0]['reason']
ids=re.findall(r'^test_\w+ \(([^)]+)\)',(R/(prefix+'tests-current/stderr.txt')).read_text('utf8'),re.M)
assert len(ids)==len(set(ids))==54
for name in ('tests','tests-current'):assert read(prefix+name+'/process.json')['actual_observed_exit']==(1 if name=='tests'else 0)
comparisons=read(prefix+'tests-current/comparisons.json')['comparisons'];assert len(comparisons)==21 and all(c['numeric_state_and_original_unknowns_equal']for c in comparisons)
native=read(prefix+'native-final/receipt.json');assert native['passed']and native['unique_checks']==29 and not any(native['external_operation_attempts'].values())
assert read(prefix+'native-final-process.json')['actual_observed_exit']==0
assert read(prefix+'native-current-process.json')['actual_observed_exit']==1
assert read(prefix+'native-process.json')['actual_observed_exit']==0
for source in ('.cache/verify_relic_report_scope_native.py','.cache/run_relic_report_scope_checks.py'):
 (B/Path(source).name).write_bytes((R/source).read_bytes())
(B/'tests-current/test-source.py').write_bytes((R/'tests/test_relic_report_scope_review.py').read_bytes())
images=native['screenshots']+read(prefix+'native-final/report-images.json')['images']
for i in images:assert sha256((R/i.get('file',i.get('path'))).read_bytes()).hexdigest()==i['sha256']
write(prefix+'native-final/visual-review.json',{'final_actual_images':images,'all_four_viewed_individually':True,'ordinary_skill_and_relic_controls_match_report':True,'reference_images_not_game_samples':True,'whole_video_parity_claimed':False,'initial_injected_report_view_is_limited_and_not_controls_integration':True,'initial_native_26_checks_not_added_to_final29':True})
live=read(prefix+'live-window/window.json');assert live['passed']and live['private_six_paths_unchanged']
import win32gui,win32process
for w in live['owned_windows']:assert win32gui.IsWindowVisible(w['hwnd'])and win32process.GetWindowThreadProcessId(w['hwnd'])[1]==w['pid']and not ctypes.windll.user32.IsHungAppWindow(w['hwnd'])
first=read('.cache/relic-report-scope-review-live-status.json');time.sleep(2.2);last=read('.cache/relic-report-scope-review-live-status.json');assert last['toolbar_visible']and last['elapsed_since_launch']>first['elapsed_since_launch']
write(prefix+'live-window/desktop-review.json',{'actual_Windows_MCP_snapshot_and_image_view':True,'region':[1716,1164,2130,1218],'owned_window_visible_responding_and_Qt_timer_advanced':True,'private_six_paths_unchanged_during_startup':True,'private_contents_or_hashes_published':False,'game_operated':False,'chat_sent':False})
from rouge.relics import mechanics
source_evidence=[{'id':rid,'name':mechanics()['relics'][rid]['name'],'source':mechanics()['relics'][rid]['source'],'effects':mechanics()['relics'][rid]['effects']}for rid in ('rogue_6_relic_legacy_60','rogue_6_relic_cargo_10','rogue_6_relic_legacy_84','rogue_6_relic_legacy_85','rogue_6_relic_legacy_100')]
write(prefix+'source-review.json',{'baseline_commit':BASE,'changed_source':[pin('rouge/reporting.py')],'own_prior_source':pin(before),'all_other_reporting_functions_AST_equal':True,'unchanged_calculators_state_and_requirements':[pin(n)for n in unchanged],'pinned_existing_mechanism_evidence':source_evidence,'scope':'Presentation correction only. Existing resolution.complete=False qualifies all reported numeric values as confirmed-effects references. Composite full result is explicitly unknown. No new dependency/stacking/activation claims; individual unaffected values are not erased. Legacy raw numeric estimate fields remain reference values and root report metadata records their scope; complete_result is null. Not a full field-by-field dependency graph.','before':'Unknown gold omitted Jinjiu bonus but report showed attack speed100 and an unqualified total-damage group. Unknown emergency origin similarly omitted companion bonuses. Existing generic incomplete status was insufficient near results.','reused':'Existing shared build_report, metric/section, format_report and actual MainWindow render path; no extra framework or per-operator duplicated coverage logic.','defensive_guards_removed':False,'runtime_speedup_claimed':False,'REA_scope':'Skill read. Complete Python source directly reviewed; no new REA call. Earlier actual toolbar bytecode and three CJS analyses remain separate.'})
title='藏品条件未确认时明确展示已计效果参考与未知完整结果'
write(prefix+'summary.json',{'kind':'implementation_review_maintenance','title':title,'baseline_commit':BASE,'completed_sections':440,'functional_section_added':False,'implemented_scope_passed':True,'test_executions_and_unique_ids':54,'passed_tests':53,'historical_skipped':results['skipped'],'new_tests':7,'public_scenarios_own_before_after_compared':21,'unchanged_non_report_result':True,'native_unique_checks':29,'native_actual_exit':0,'final_images_viewed':4,'source_review':pin(prefix+'source-review.json'),'tests':pin(prefix+'tests-current/results.json'),'native_receipt':pin(prefix+'native-final/receipt.json'),'test_window_updated':True,'private_six_paths_unchanged':True,'initial_failures_preserved':True,'full_validation_rerun':False,'full440_only_original_frozen_source':True,'whole_program_complete':False,'whole_video_parity_complete':False,'P3_complete':False,'P2_complete':False,'P1_complete':False,'game_operated':False,'chat_sent':False,'private_data_included':False,'publication_binding':'enclosing maintenance commit, ordinary push and real remote check required'})
text('research/relic-report-scope-review-20261031/README.md','''# 藏品缺条件与未核验组合的报告口径回顾

按REA技能使用完整Python源码，实际追踪prepare/finish、属性层、技能输出、共用build_report/format_report及MainWindow.render_damage。本轮没有新调用REA，不能称全程序已逆向完成。复用已有固定来源mechanics资料与原规则：金酒之杯缺gold、同行者缺招募来源会不套用对应加成；残破合影/恐鱼干未核验组合保持排除。没有新猜公式或改变机制。

实际执行自有原报告：前两种条件缺失仍给出攻速/面板和未就近限定的单次技能总伤；仅末尾警告和通用“不完整”不足以说明这些数值未包含全部所选效果。现共用报告入口增加藏品覆盖范围：完整结果明确未知、原数值限定为已计效果参考，属性前就地说明，并标识伤害/治疗/时序组。参考值不保证下限，不推断每个字段都受影响；确认条件后自动恢复原报告。保留既有部分数值和已有未知，不改旧计算字段为虚假完整总量；结构化report.relic_coverage记录partial、numeric_scope及complete_result=null。尚未实现逐字段完整依赖图。

复用现有报告/指标与Qt显示入口，无新库、无逐干员重复处理，不因概率小删除准确性保护；本次净增加报告代码，不称提速或代码净精简。21个公开情景实际旧/新非report结果全部相同，含首批9技能、0/24/25金币、两种明确招募来源、未核验减防组合、医疗/先锋能力隐藏、培养未知和仅资料藏品。54个不同检查中53通过，1项原战斗专属历史跳过，不计通过；新7项包含真实MainWindow普通/技术/结构化视图和刷新。

最终实际Windows原生29项检查通过、根退出0；真实技能S3与金酒之杯控件进行未知→25金币→未知计算，检查默认提示、结构化空完整值、技术资料、非零滚动保持和结果不被显示修改。最终4张实际图片逐张查看。初次26项仅注入结果展示，不作控件集成证明；加强脚本第一轮误写不存在的relic_search，原失败与脚本保留，改为实际relic_filter后29项通过。单元首轮把仍有局外短时攻击待接入项的绿叶菜罐头当纯战斗参考，已改为荣耀绶带，保留原失败与测试源，不放宽产品门槛。

原项目测试小窗已更新、可见响应、计时推进，正常关闭/启动期间私人六路径保持；不操作游戏、发送聊天或上传个人对局。功能仍440、未开441；完整选择器714，full440只证明旧冻结源码。全部机制/字段依赖、完整视频效果和全程序/P3/P2/P1仍未完成，识别最后。
''')
entry=f'''<!-- relic-report-scope-review-20261031:start -->
## 实现回顾维护 · {title}

已复现缺金币/招募来源时普通报告未就近限定数值，现共用报告将面板/技能输出标为已计效果参考，完整组合结果未知；条件确认后恢复原文，原数值和已有未知不变，不猜叠加或逐字段影响。21公开情景非报告结果相同，54不同检查中53通过/1原历史跳过；最终真实控件原生29项通过、退出0，4张最终图逐张查看，初轮夹具/脚本失败原件保留。

原项目小窗已更新响应，启动六处私人路径保持；无游戏/聊天/个人上传。回执：`{prefix}summary.json`。功能440/未开441；字段完整依赖与机制、全程序/全视频及P3/P2/P1未完成，识别最后。
<!-- relic-report-scope-review-20261031:end -->

'''
for n in ['WORK_IN_PROGRESS.md','PROJECT_COMPLETED.md']:text(n,entry+(R/n).read_text('utf8'))
text('PROGRAM_REVIEW.md',(R/'PROGRAM_REVIEW.md').read_text('utf8')+'\n[藏品结果口径回顾](research/relic-report-scope-review-20261031/README.md)修正缺条件时数值范围表达，完整结果未知、原数值明确限定已计效果参考。21情景非报告结果保持，54项中53通过/1原历史跳过、29项原生检查通过；不是逐字段完整依赖或机制校准，全程序与视频仍未完成。\n')
text('IMPLEMENTATION_STRATEGY.md',(R/'IMPLEMENTATION_STRATEGY.md').read_text('utf8')+'\n[藏品报告共用口径](research/relic-report-scope-review-20261031/README.md)在原build_report/format_report统一读取已有覆盖标记，复用原指标/Qt显示，避免逐干员重复提示或新增计算框架。公式与原字段保持，缺条件不默认为0；净增加提示代码，不称性能或净精简。\n')
n='PROJECT_PROGRESS.md';t=(R/n).read_text('utf8');old_phrase='完整条件统计的证据、缺图';assert old_phrase in t;t=t.replace(old_phrase,'完整条件统计的证据、藏品未覆盖项的逐字段影响与独立数值校准、缺图',1);text(n,t)
cp=read('DEVELOPMENT_CHECKPOINT.json');cp['current_maintenance_save']={'kind':'implementation_review_maintenance','title':title,'receipt':prefix+'summary.json','binding':'enclosing_commit','functional_section_added':False,'status':'partial_program_review_relic_report_scope','review_checklist':'PROGRAM_REVIEW.md','review_checklist_sha256':pin('PROGRAM_REVIEW.md')['sha256'],'application_review_complete':False};cp['current_batch']['receipt']=prefix+'summary.json';cp['next_action']='继续完整程序回顾：当前数值仍缺逐字段完整依赖/独立机制及87技能校准，不能把本次报告范围修正当计算准确性完成；继续未审资料/缓存失效、附属窗口与视频交互外观，识别最后。缺条件报告已就近限定，不重复计入完成。'
text('DEVELOPMENT_CHECKPOINT.json',json.dumps(cp,ensure_ascii=False,indent=2)+'\n')
index=runpy.run_path(str(R/'scripts/update_cloud_index.py'));index['update'](R);assert index['validate_delivery'](R,cp)['current_section']==440
from scripts.verify_full_available import maintained_selectors
selectors=maintained_selectors();assert len(selectors)==714 and selectors[-1]=='tests.test_relic_report_scope_review'
old_selector=old('scripts/verify_full_available.py');anchor=b"ADDITIONAL_MODULES += ('tests.test_core_calculation_review',)"
assert (R/'scripts/verify_full_available.py').read_bytes()==old_selector.replace(anchor,anchor+b"\r\n\r\nADDITIONAL_MODULES += ('tests.test_relic_report_scope_review',)")
assert read('CLOUD_INDEX.json')['requirements']['sha256']==pin('PROJECT_REQUIREMENTS.md')['sha256']
write(prefix+'final-audit.json',{'passed':True,'baseline_commit':BASE,'summary':pin(prefix+'summary.json'),'requirements':pin('PROJECT_REQUIREMENTS.md'),'cloud_index':pin('CLOUD_INDEX.json'),'ordered_selectors':714,'different_tests':54,'passed_tests':53,'historical_skipped':1,'native_checks':29,'whole_program_complete':False,'whole_video_parity_complete':False,'at_UTC':datetime.now(timezone.utc).isoformat()})
(B/'record-source.py').write_bytes(Path(__file__).read_bytes())
files={p.relative_to(R).as_posix():{k:v for k,v in pin(p.relative_to(R)).items()if k!='path'}for p in sorted(B.rglob('*'))if p.is_file()and p.name!='archive-manifest.json'}
write(prefix+'archive-manifest.json',{'kind':'explicit_public_archive','files':files})
print(json.dumps({'passed':True,'passed_tests':53,'historical_skipped':1,'native_checks':29,'public_scenarios':21,'archive_files':len(files),'whole_goal_complete':False}))
