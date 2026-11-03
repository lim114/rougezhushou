from pathlib import Path
from hashlib import sha256,sha1
from datetime import datetime,timezone
import ast,ctypes,difflib,json,re,runpy,subprocess,sys,time
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts'),str(R/'.cache/305-window-tooldeps')]
BASE='2391a879ebad3dca7a4337e60a6b66b7cb70343a';B=R/'verification/maintenance/player-tool-navigation-review-20261031';prefix=B.relative_to(R).as_posix()+'/'
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
assert subprocess.check_output(['git','branch','--show-current']).decode().strip()=='codex/p2-development'
changed=['rouge/app.py','rouge/player_workspace.py','rouge/diagnostic_workspace.py']
unchanged=['rouge/damage.py','rouge/reporting.py','rouge/estimate.py','rouge/ui_state.py','rouge/run_state.py','rouge/account_cache.py','rouge/offline_tools_view.py','rouge/player_context.py']
for n in unchanged:assert old(n)==(R/n).read_bytes(),n
assert not subprocess.check_output(['git','diff','--name-only',BASE,'--','rouge/data']).strip()
methods={'show_barrier_ledger','show_shield_grants','show_shield_inventory','show_explosion_values','make_damage_tab','update_skill_options','sync_player_tools'}
def app_methods(raw):
 c=next(n for n in ast.parse(raw).body if isinstance(n,ast.ClassDef)and n.name=='MainWindow')
 return {n.name:ast.dump(n,include_attributes=False)for n in c.body if isinstance(n,ast.FunctionDef)}
a=app_methods(old('rouge/app.py'));b=app_methods((R/'rouge/app.py').read_bytes())
assert set(a)==set(b)and {n for n in a if a[n]!=b[n]}==methods
tests=read(prefix+'tests-verified/results.json');assert tests['passed']and tests['tests_run']==26 and tests['failed']==tests['errors']==0 and not tests['skipped']and not tests['forbidden_external_calls']
ids=re.findall(r'^test_\w+ \(([^)]+)\)',(R/(prefix+'tests-verified/stderr.txt')).read_text('utf8'),re.M);assert len(ids)==len(set(ids))==26
assert read(prefix+'tests-verified/process.json')['actual_observed_exit']==0
original=read(prefix+'before/results.json');assert original['tests_run']==7 and original['failed']==6 and original['errors']==0 and read(prefix+'before/process.json')['actual_observed_exit']==1
native=read(prefix+'native-current/receipt.json');assert native['passed']and native['unique_checks']==38 and not any(native['external_operation_attempts'].values())and read(prefix+'native-current-process.json')['actual_observed_exit']==0
for n in changed:assert native['source_sha256_after'][n]==pin(n)['sha256'],n
images=native['screenshots']+read(prefix+'native-current/images.json')['images'];assert len(images)==5
for row in images:assert sha256((R/row.get('file',row.get('path'))).read_bytes()).hexdigest()==row['sha256']
write(prefix+'native-current/visual-review.json',{'images':images,'all_five_final_originals_individually_viewed':True,'default_technical_queries_collapsed':True,'only_explicit_opt_in_shows_raw_query_fields':True,'temporary_public_previews_only':True,'whole_video_parity_claimed':False})
for n in ('.cache/verify_player_tool_navigation_native.py','.cache/run_player_tool_navigation_checks.py'):(B/Path(n).name).write_bytes((R/n).read_bytes())
(B/'tests-verified/test-source.py').write_bytes((R/'tests/test_player_tool_navigation_review.py').read_bytes())
live=read(prefix+'live-window/window.json');assert live['passed']and live['private_six_paths_unchanged']
import win32gui,win32process
for w in live['owned_windows']:assert win32gui.IsWindowVisible(w['hwnd'])and win32process.GetWindowThreadProcessId(w['hwnd'])[1]==w['pid']and not ctypes.windll.user32.IsHungAppWindow(w['hwnd'])
first=read('.cache/player-tool-navigation-review-live-status.json');time.sleep(2.2);last=read('.cache/player-tool-navigation-review-live-status.json');assert last['toolbar_visible']and last['elapsed_since_launch']>first['elapsed_since_launch']
write(prefix+'live-window/desktop-review.json',{'actual_Windows_MCP_snapshot_and_image_view':True,'region':[1716,1164,2130,1218],'test_window_visible_responding_and_Qt_timer_advanced':True,'private_six_paths_unchanged_during_startup':True,'private_contents_or_hashes_published':False,'game_operated':False,'chat_sent':False})
video=read('.cache/player-tool-navigation-video/frames.json')
for row in video['frames']:assert sha256((R/f".cache/player-tool-navigation-video/{row['requested_second']}.png").read_bytes()).hexdigest()==row['sha256']
write(prefix+'video-reference-review.json',{**video,'both_original_frames_individually_viewed':True,'frames_kept_local_not_distributed':True,'observed':'95秒关卡资料折叠分组与108秒完整敌人数值/机制表；本批四个技术查询不是视频对应功能。','whole_video_rewatched_or_parity_complete':False})
rule_lines=['入口只校验一次，拒绝重复判空和滥用try/catch','单次逻辑不乱抽函数','低概率防御性代码，先征求开发者同意后再添加']
for n in ('AGENTS.md','PROJECT_REQUIREMENTS.md'):
 s=(R/n).read_text('utf8');assert all(x in s for x in rule_lines)and '新增与已有代码均适用'in s
 assert old(n)!=(R/n).read_bytes()
assert '同步优化，不再置于最后'in (R/'AGENTS.md').read_text('utf8')
net=sum(len((R/n).read_bytes().splitlines())-len(old(n).splitlines())for n in changed)
write(prefix+'source-review.json',{'baseline_commit':BASE,'changed_source':[pin(n)for n in changed],'unchanged_models_state_and_existing_tools':[pin(n)for n in unchanged],'changed_MainWindow_methods':sorted(methods),'all_other_MainWindow_methods_AST_equal':True,'production_physical_lines_net_added':net,'four_original_player_actions_now_reach_exact_existing_query':True,'default_generic_developer_navigation_stays_blocked':True,'existing_fold_reused_default_collapsed_only_mechanist_S2':True,'warm_instrumented_eight_constructor_total_seconds':0.2973370002582669,'warm_single_probe_not_cold_or_end_to_end_benchmark':True,'lazy_widget_framework_added':False,'numerical_mechanism_or_source_data_changed':False,'code_rules':{'applies_to':'new and existing code; progressively verify and fix existing modules','texts':rule_lines,'whole_program_already_compliant_claimed':False,'low_probability_new_defensive_code_requires_developer_agreement':True},'recognition_priority':'OCR, coverage, adaptation, accuracy and latency improve concurrently; no longer last; existing implementations included. No OCR source changed or speed improvement claimed in this maintenance.','REA_scope':'Complete source and actual Qt runtime review; no new REA tool invocation. Earlier toolbar/CJS evidence remains separate.','retained_failures':'Original7 checks6 functional failures; tests-complete26 checks1 visibility assumption failure because test had not selected the calculation page; corrected test navigation, actual native38 already passed.','remaining':'Whole-program old-code compliance, other player/import actions, cold startup, full predicted enemy table/video parity, P3/P2/P1 and OCR improvements.'})
title='修复四个技能资料入口，折叠技术查询并更新存量代码与OCR规则'
write(prefix+'summary.json',{'kind':'implementation_review_maintenance','title':title,'baseline_commit':BASE,'completed_sections':440,'functional_section_added':False,'implemented_scope_passed':True,'different_tests':26,'new_functional_tests':8,'passed_tests':26,'skipped':0,'original_reproduction_checks':7,'original_functional_failures':6,'native_primary_unique_checks':38,'final_primary_images':5,'all_final_images_individually_viewed':True,'source_review':pin(prefix+'source-review.json'),'tests':pin(prefix+'tests-verified/results.json'),'native':pin(prefix+'native-current/receipt.json'),'test_window_updated':True,'private_six_paths_unchanged_during_startup':True,'full_validation_rerun':False,'full440_only_original_frozen_source':True,'whole_program_complete':False,'whole_existing_code_compliant':False,'whole_video_parity_complete':False,'P3_complete':False,'P2_complete':False,'P1_complete':False,'OCR_source_optimized_in_this_batch':False,'recognition_priority':'concurrent','requirements_updated':True,'game_operated':False,'chat_sent':False,'private_data_included':False,'publication_binding':'enclosing maintenance commit; ordinary push and actual remote/blob verification required'})
text('research/player-tool-navigation-review-20261031/README.md','''# 玩家资料入口与技术查询回顾

当前Python/Qt源码与实际运行核对发现：机械师S2四个资料按钮调用的通用导航拒绝所有开发页，按钮点击无响应。原7项检查包含6个功能失败与1个构造测量通过，保留原栈和退出1。现显式玩家按钮可到达准确的原查询，普通开发页导航继续关闭；复用既有对话框及原查询，不开放整组调试页。四个按钮归入机械师S2专属的技术核对折叠栏，默认收起，手动输入与返回阅读保持；其余干员不显示。

实现参考Qt官方[QDialog](https://doc.qt.io/qtforpython-6/PySide6/QtWidgets/QDialog.html)的已有非模态show及[QTabWidget](https://doc.qt.io/qtforpython-6/PySide6/QtWidgets/QTabWidget.html)页签栏接口，未引入新依赖或复制外部源码。实际八构造器的单次暖测合计约0.297秒，不含模块导入/冷启动，不能证明全启动速度；没有据此增加惰性控件代理。生产物理行净变化0，不宣称端到端提速。模型、查询器、状态与数据不变。

最终26项不同检查通过（8项新功能检查），原生38项通过；实际鼠标展开折叠栏、点击四按钮、原查询/草稿/返回/Escape与普通导航边界均核对，五张最终原图逐张查看。原一次测试未先切到计算页就断言子按钮可见的失败单独保留，纠正测试导航后26项完整通过。原项目小窗已更新且可见响应，六私人路径启动期间保持，零游戏操作/真实聊天/上传。

重新查看本机原视频95、108秒两帧，图像仅本机保留；视频的完整敌人数值表与其它功能/外观仍待完成，本批技术入口不冒充视频效果一致。完整源码与运行回顾，没有新增REA工具调用；不冒充整个程序已回顾。

用户本批新规则已写入AGENTS和项目要求：入口单次校验、单次逻辑不过度抽函数、新增低概率防御先征求开发者同意；适用于新增及已有代码，存量逐模块核对，不能声称已整体符合。OCR及覆盖/适配/准确率/耗时同步优化，不再置后；本批仅更新安排，未改OCR或声称提速。功能440、未开441，720有序选择器；full440仅原冻结源码，P3/P2/P1和全视频/全程序未完成。
''')
entry=f'''<!-- player-tool-navigation-review-20261031:start -->
## 实现回顾维护 · {title}

四个机械师S2资料按钮现在打开准确的既有查询；普通开发页仍不开放。复用原对话框与折叠栏，技术字段需主动展开，普通玩家结果不变。原7项中6个功能失败保留，最终26项不同检查、原生38项和五张最终原图已核对；暖测不冒充冷启动提速。小窗更新可见响应，六私人路径保持，零游戏操作/真实聊天/上传。

最新规则覆盖新增和存量：入口单次校验、单次逻辑不过度抽函数、新增低概率防御先征求开发者同意。OCR及识别覆盖、适配、准确率与耗时同步推进，替代下文历史“识别最后”；存量合规与OCR优化未整体完成。回执：`{prefix}summary.json`。功能440/未开441，720选择器；全程序/视频与P3/P2/P1仍未完成。
<!-- player-tool-navigation-review-20261031:end -->

'''
for n in ('WORK_IN_PROGRESS.md','PROJECT_COMPLETED.md'):text(n,entry+(R/n).read_text('utf8'))
n='PROGRAM_REVIEW.md';text(n,(R/n).read_text('utf8')+'\n[四个技能资料入口回顾](research/player-tool-navigation-review-20261031/README.md)已修复原按钮无响应并复用原窗/原查询，技术字段默认折叠。26项检查及38项原生通过，非全程序完成；当前三条实现规则同时覆盖存量，OCR优化同步推进，历史后置要求不再有效。\n')
cp=read('DEVELOPMENT_CHECKPOINT.json');cp['current_maintenance_save']={'kind':'implementation_review_maintenance','title':title,'receipt':prefix+'summary.json','binding':'enclosing_commit','functional_section_added':False,'status':'partial_program_review_player_tool_navigation','review_checklist':'PROGRAM_REVIEW.md','review_checklist_sha256':pin('PROGRAM_REVIEW.md')['sha256'],'application_review_complete':False};cp['current_batch']['receipt']=prefix+'summary.json';cp['next_action']='继续全程序与视频回顾：完整敌人预计数值表、其它资料/输入入口及来源刷新、独立机制；OCR及识别覆盖/适配/准确率/耗时同步推进，不再置后。三条实现约束覆盖新增和存量代码，逐模块查明并修正重复校验、过度抽函数和冗余防御；新增低概率防御先征求开发者同意，不冒称已整体整改。'
text('DEVELOPMENT_CHECKPOINT.json',json.dumps(cp,ensure_ascii=False,indent=2)+'\n')
idx=runpy.run_path(str(R/'scripts/update_cloud_index.py'));idx['update'](R);assert idx['validate_delivery'](R,cp)['current_section']==440
from scripts.verify_full_available import maintained_selectors
selectors=maintained_selectors();assert len(selectors)==720 and selectors[-1]=='tests.test_player_tool_navigation_review'
assert read('CLOUD_INDEX.json')['requirements']['sha256']==pin('PROJECT_REQUIREMENTS.md')['sha256']
write(prefix+'final-audit.json',{'passed':True,'baseline_commit':BASE,'summary':pin(prefix+'summary.json'),'agents':pin('AGENTS.md'),'requirements':pin('PROJECT_REQUIREMENTS.md'),'cloud_index':pin('CLOUD_INDEX.json'),'different_tests':26,'native_checks':38,'ordered_selectors':720,'whole_program_complete':False,'whole_existing_code_compliant':False,'whole_video_parity_complete':False,'at_UTC':datetime.now(timezone.utc).isoformat()})
(B/'record-source.py').write_bytes(Path(__file__).read_bytes())
files={p.relative_to(R).as_posix():{k:v for k,v in pin(p.relative_to(R)).items()if k!='path'}for p in sorted(B.rglob('*'))if p.is_file()and p.name!='archive-manifest.json'}
write(prefix+'archive-manifest.json',{'kind':'explicit_public_archive','files':files})
print(json.dumps({'passed':True,'different_tests':26,'native_checks':38,'final_images':5,'archive_files':len(files),'requirements_updated':True,'whole_goal_complete':False}))
