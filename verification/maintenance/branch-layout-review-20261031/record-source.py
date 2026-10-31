from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import ast,ctypes,difflib,json,runpy,subprocess,sys,time
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts')]
BASE='46b831486bcc217c233f14f0c62bcf7f4d20de8c';B=R/'verification/maintenance/branch-layout-review-20261031';prefix=B.relative_to(R).as_posix()+'/'
def read(n):return json.loads((R/n).read_bytes())
def pin(n):
 p=R/n;raw=p.read_bytes();return {'path':p.relative_to(R).as_posix(),'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}
def write(n,value):(R/n).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n','utf8')
def text(n,value):
 p=R/n
 if not p.exists():p.parent.mkdir(parents=True,exist_ok=True);p.write_text(value,'utf8');return
 old=p.read_bytes().decode('utf8').splitlines(keepends=True);new=value.splitlines(keepends=True);out=list(new)
 for a,b,num in difflib.SequenceMatcher(None,[s.rstrip('\r\n')for s in old],[s.rstrip('\r\n')for s in new],autojunk=False).get_matching_blocks():
  for i in range(num):out[b+i]=old[a+i]
 p.write_bytes(''.join(out).encode('utf8'))
def old(n):return subprocess.check_output(['git','show',BASE+':'+n])
assert subprocess.check_output(['git','rev-parse','HEAD']).decode().strip()==BASE
path='rouge/branch_choice.py';before=old(path);after=(R/path).read_bytes();assert before==(B/'before/branch_choice.py').read_bytes()
def selection_methods(raw):
 cls=next(c for c in ast.parse(raw).body if isinstance(c,ast.ClassDef)and c.name=='BranchChoice')
 return {f.name:ast.dump(f,include_attributes=False)for f in cls.body if isinstance(f,ast.FunctionDef)and f.name!='__init__'}
assert selection_methods(before)==selection_methods(after)
untouched=['rouge/current_battle_view.py','rouge/current_reward_view.py','rouge/player_map_reader.py','rouge/player_compact.py','rouge/app.py','rouge/run_state.py','rouge/node_catalog_view.py','PROJECT_REQUIREMENTS.md']
for n in untouched:assert old(n)==(R/n).read_bytes()
final=read(prefix+'tests-verified/results.json');assert final['passed']and final['tests_run']==40 and not final['skipped']and not final['forbidden_external_calls'];assert read(prefix+'tests-verified/process.json')['actual_observed_exit']==0
native=read(prefix+'native-complete/window.json');assert native['passed']and native['unique_checks']==46 and not native['source_drift']and not any(native['external_operation_attempts'].values());assert read(prefix+'native-complete/process.json')['actual_observed_exit']==0
assert native['source_sha256_after'][path]==pin(path)['sha256']
(B/'native-complete/verifier-source.py').write_bytes((R/'scripts/verify_branch_layout_review.py').read_bytes())
write(prefix+'source-review.json',{'baseline_commit':BASE,'changed_source':[pin(path)],'unchanged_selection_and_refresh_method_AST':list(selection_methods(before)),'unchanged_readers_data_state_and_requirements':[pin(n)for n in untouched],'framework_reuse':'Existing installed Qt6.11.2 QFormLayout WrapLongRows and AllNonFixedFieldsGrow; the existing shared BranchChoice remains the single category implementation. No breakpoint, manual resize handler or polling added.','additional_code_reason':'A small shared CategoryCombo computes text/icon width through the active QStyle. Raw sizeHint clipped under the actual stylesheet; text rendering also subtracts two pixels each side, confirmed in pinned Qt source. Net production code is larger, not claimed a line-count reduction.','primary_sources':[{'url':'https://doc.qt.io/qt-6/qformlayout.html#RowWrapPolicy-enum','establishes':'Toolkit supplies automatic row wrapping and widget label/field roles.'},{'url':'https://doc.qt.io/qt-6/qcombobox.html#SizeAdjustPolicy-enum','establishes':'Minimum-contents policy avoids sizing a field to its entire longest entry.'},{'url':'https://raw.githubusercontent.com/qt/qtbase/v6.11.2/src/widgets/styles/qcommonstyle.cpp','establishes':'CE_ComboBoxLabel reserves icon width plus4 and two-pixel text margins each side; installed Qt6.11.2.'}],'application_review_complete':False,'whole_video_parity_complete':False})
write(prefix+'initial-observations.json',{'kind':'terminal_observations_not_reconstructed_raw_logs','direct_first_test_run':{'exit':1,'tests':6,'failures':3,'errors':1,'error':'New test omitted required make_reader parent; fixed before corrected baseline run.','raw_log_saved':False,'exact_initial_test_source':pin(prefix+'before/initial-test-source.py')},'direct_new_icon_case':{'exit':1,'errors':1,'error':'Verifier used nonexistent QComboBox.currentIcon; use itemIcon(currentIndex).','raw_log_saved':False},'direct_followup_seven':{'exit':1,'failures':1,'error':'New icon case assumed a placeholder target was automatically selected. Explicitly select its exact target; no product behavior changed.','raw_log_saved':False},'retained_originals':['before-corrected','tests','tests-current','tests-final','before-layout-final-correction','native','native-final','native-verified','native-current'],'actual_product_gap_after_initial_green':'Visual review found closing parenthesis still clipped. Original width test omitted native two-pixel text margins. Pinned Qt6.11.2 source verified these, product and assertions fixed, final tests40/native46 genuinely rerun.','narrow_width_test_correction':'A fixed350 threshold could fit after layout changes, and manually summed hints omitted toolkit spacing. Final test uses Qt parent minimumSizeHint and actual nonoverlapping geometry, without assuming a font/resolution threshold.','video_extraction_first_failure':'cv2.imwrite rejected the Windows Unicode path; cv2.imencode plus Path.write_bytes produced the three local-only frames. No product code affected.'})
images=[pin(p.relative_to(R))for p in sorted((B/'native-complete').glob('*.png'))];assert len(images)==7
write(prefix+'image-review.json',{'reviewer':'/root','final_images':images,'method':'All seven actual final originals separately opened with view_image this turn.','observed_fixes':'Complete closing parenthesis in narrow default-style category; equal control heights in styled player rewards; fields wrap at real minimum width and return to a single row.','remaining':'The actual player map-reference factory is a light themed tool window; it is not the earlier dark full catalogue. Long explanatory paragraphs, repeated notices, full catalogue density and complete video appearance/interaction remain unresolved.','reference_video':pin(prefix+'video-reference.json'),'video_frames_actually_viewed_after_fresh_extraction':3,'video_not_continuously_rewatched':True,'whole_video_parity_claimed':False})
live=read(prefix+'live-window/window.json');assert live['passed']and live['private_six_paths_unchanged'];assert live['source_sha256_after'][path]==pin(path)['sha256']
import win32gui,win32process
for w in live['owned_windows']:assert win32gui.IsWindowVisible(w['hwnd'])and win32process.GetWindowThreadProcessId(w['hwnd'])[1]==w['pid']and not ctypes.windll.user32.IsHungAppWindow(w['hwnd'])
a=read('.cache/branch-layout-review-live-status.json');time.sleep(2.2);b=read('.cache/branch-layout-review-live-status.json');assert b['toolbar_visible']and b['elapsed_since_launch']>a['elapsed_since_launch']
write(prefix+'live-window/desktop-review.json',{'actual_windows_mcp_snapshot_called':True,'actual_image_viewed':True,'region':[1716,1164,2130,1218],'owned_window_visible_and_responding':True,'Qt_timer_advanced':True,'private_six_paths_unchanged_during_startup':True,'private_contents_or_hashes_published':False,'game_operated':False,'chat_sent':False})
title='共享分类控件自动换行、完整显示类别并保留准确选择'
write(prefix+'summary.json',{'kind':'implementation_review_maintenance','title':title,'baseline_commit':BASE,'completed_sections':440,'functional_section_added':False,'implemented_scope_passed':True,'related_unique_tests':40,'skips':0,'test_receipt':pin(prefix+'tests-verified/results.json'),'native_unique_checks':46,'native_receipt':pin(prefix+'native-complete/window.json'),'source_review':pin(prefix+'source-review.json'),'initial_observations':pin(prefix+'initial-observations.json'),'image_review':pin(prefix+'image-review.json'),'live_window':pin(prefix+'live-window/desktop-review.json'),'scope':'Shared category geometry, fonts/icons and resize state; actual player fixed-reference factory, reward exact-source click and unchanged eligibility/state logic. Not all windows, cross-monitor DPI, actual game/chat or independent mechanism calibration.','application_review_complete':False,'video_parity_complete':False,'P3_complete':False,'P2_complete':False,'P1_complete':False,'full_validation_rerun':False,'full440_only_original_frozen_source':True,'private_data_included':False,'game_operated':False,'chat_sent':False,'publication_binding':'enclosing maintenance commit; ordinary push and actual remote/blob equality required'})
text('research/branch-layout-review-20261031/README.md','''# 共享分类与真实玩家资料窗口回顾

按REA技能，完整Python源码直接审查和运行验证；既有工具条/桥接REA证据保留，本轮没有新增REA调用，不把普通源码检查包装成二进制逆向。

先纠正入口前提：先前深色完整目录及独立实例并不是所有默认玩家窗口。实际地图资料使用player_map_reader.make_reader和独立浅色样式，本轮从这个真实工厂创建并核对工具窗，不冒称本轮点击了游戏/地图中的节点。

原共享BranchChoice将类别限定七字符宽度；真实窗口文字裁切，极长目标名称还能迫使测试窗扩至1417逻辑像素。复用已安装Qt6.11.2的QFormLayout自动换行与字段增长：宽时同排，窄时上下排列，目标长名称不再决定整窗最小宽度。没有分辨率表、手写resize分支或轮询。原七个选择/更新方法AST保持，准确身份、占位未选择、职业分组/已招募总览和刷新行为不变。

仅换布局仍不足：真实样式的文字区小于普通sizeHint；一份绿色窗口图仍截掉右括号，实际查看发现后修正。小型共享CategoryCombo按当前样式的文字区、字体和图标计算类别宽度；固定版本Qt的CE_ComboBoxLabel还会左右各减2像素，已查原源码并纳入断言。分类/条目图标槽均28逻辑像素，避免控件高度不齐。本轮净程序代码增加，不能宣称减少代码行数；收益是共享实现和复用框架，避免每页自写窗口/DPI分支。

来源：[Qt自动换行](https://doc.qt.io/qt-6/qformlayout.html#RowWrapPolicy-enum)、[下拉框尺寸策略](https://doc.qt.io/qt-6/qcombobox.html#SizeAdjustPolicy-enum)、[Qt6.11.2绘制源码](https://raw.githubusercontent.com/qt/qtbase/v6.11.2/src/widgets/styles/qcommonstyle.cpp)。仅调用已安装Qt公开接口，没有复制或引入新的第三方组件。

40个不同相关测试和最终原生46项唯一检查通过；保留改前实际4失败、改中失败/初次绿色但视觉仍不全的原回执，未重写。少量控制台首试只保存真实观察说明，未伪造原日志；测试自身的parent参数、图标API、占位自动选中及窄宽度假设分别纠正。最终窄宽度取Qt实际minimumSizeHint，避免依赖测试机字体的固定阈值。7张最终图实际逐张查看；从原始录像新提取158/164/172秒三图并逐张看，原片SHA与旧记录一致、三图与旧提取整字节相同；没有声称重看全片。原片和视频帧只留本地，公开记录只放摘要。

实际小窗已更新打开，可见响应且Qt计时推进；启动六处私人路径保持，不发布内容或摘要，不操作游戏、不发聊天。功能仍440，维护不新增节数，下一全量455。其余资料页的说明密度/重复提示、布局/视觉、全部窗口/跨屏和完整程序回顾仍未完成；识别最后。P3/P2/P1保持未完成。
''')
n='PROGRAM_REVIEW.md';t=(R/n).read_text('utf8');t=t.replace('此前核对工具条字节码、浮窗生命周期和地图阅读。 |','此前核对工具条字节码、浮窗生命周期和地图阅读；共享分类改用Qt自动换行，核对真实玩家资料窗的完整文字和选择保持。 |');t+='\n[共享分类回顾](research/branch-layout-review-20261031/README.md)区分真实浅色玩家资料窗与深色完整目录，修复类别裁切/右括号、长目标撑宽和控件高度；40个不同相关测试、46项隔离原生检查覆盖。其它页面密度/视觉、完整跨屏、全部功能与视频仍未完成。\n';text(n,t)
n='VIDEO_PARITY.md';t=(R/n).read_text('utf8');t=t.replace('当前奖励类别文字在该窗口宽度下裁切','当时当前奖励类别文字裁切（已由后续共享分类回顾修正）');t+='\n[共享分类与真实资料窗](research/branch-layout-review-20261031/README.md)：类别完整可读、窄窗自动换行，缩放和同源刷新保留准确目标与出现条件，点击仍跳至精确配置条目；已修正图中发现的右括号和控件高度问题。深色完整目录不是默认浅色资料小窗，两者不能混作同一外观验收。视频新取三帧仅证明本次局部对照；密集长说明、重复提示与全部视觉/交互仍未一致。\n';text(n,t)
n='PROJECT_PROGRESS.md';t=(R/n).read_text('utf8');t=t.replace('核对其它资料入口、固定作战完整数据','核对其它资料入口的紧凑阅读/重复提示、固定作战完整数据');text(n,t)
entry=f'''<!-- branch-layout-review-20261031:start -->
## 实现回顾维护 · {title}

复用Qt自带表单自动换行和当前样式尺寸，修复共享分类文字裁切、长目标撑宽及控件高度；选择/更新七方法AST不变，不增分辨率表或轮询。真实玩家入口是独立浅色工具窗，不能用深色完整目录代替。最初绿色图仍缺右括号，查Qt固定源码补齐真实文字边距并强化断言，旧原件保留。

最终40个不同相关测试、46项原生唯一检查通过，真实退出0；7张最终原图逐张查看，原片新取三帧核对而非重看全片。实际测试小窗更新可见响应，启动六处私人路径保持。净程序代码增加，不称代码行减少或全程序提速；完整回顾/视频及P3/P2/P1仍未完成，功能440/未开441，识别最后。回执：`{prefix}summary.json`。
<!-- branch-layout-review-20261031:end -->

'''
for n in ['WORK_IN_PROGRESS.md','PROJECT_COMPLETED.md']:text(n,entry+(R/n).read_text('utf8'))
cp=read('DEVELOPMENT_CHECKPOINT.json');cp['current_maintenance_save']={'kind':'implementation_review_maintenance','title':title,'receipt':prefix+'summary.json','binding':'enclosing_commit','functional_section_added':False,'status':'partial_program_review_shared_category_layout_and_actual_player_window','review_checklist':'PROGRAM_REVIEW.md','review_checklist_sha256':pin('PROGRAM_REVIEW.md')['sha256'],'application_review_complete':False};cp['current_batch']['receipt']=prefix+'summary.json';cp['next_action']='继续完整程序回顾：实际玩家资料窗的重复说明/按钮与紧凑阅读、其余资料阅读器缓存/失效、事件及配置窗口布局和视频差异；再核对招募/强化连续状态与独立机制算例。共享分类裁切/自动换行已修复不重复推进；不以局部绿色检查冒充全程序或视频一致，识别最后。'
text('DEVELOPMENT_CHECKPOINT.json',json.dumps(cp,ensure_ascii=False,indent=2)+'\n');module=runpy.run_path(str(R/'scripts/update_cloud_index.py'));module['update'](R);assert module['validate_delivery'](R,cp)['current_section']==440
from scripts.verify_full_available import maintained_selectors
selectors=maintained_selectors();assert len(selectors)==701 and selectors[-1]=='tests.test_branch_layout_review';assert read('CLOUD_INDEX.json')['requirements']['sha256']==pin('PROJECT_REQUIREMENTS.md')['sha256']
write(prefix+'final-audit.json',{'passed':True,'baseline_commit':BASE,'summary':pin(prefix+'summary.json'),'requirements':pin('PROJECT_REQUIREMENTS.md'),'cloud_index':pin('CLOUD_INDEX.json'),'ordered_selectors':701,'unique_related_tests':40,'native_unique_checks':46,'whole_program_complete':False,'whole_video_parity_complete':False,'at_UTC':datetime.now(timezone.utc).isoformat()})
(B/'record-source.py').write_bytes(Path(__file__).read_bytes());archive={p.relative_to(R).as_posix():{k:v for k,v in pin(p.relative_to(R)).items()if k!='path'}for p in sorted(B.rglob('*'))if p.is_file()and p.name!='archive-manifest.json'};write(prefix+'archive-manifest.json',{'kind':'explicit_public_archive','files':archive});print(json.dumps({'passed':True,'unique_tests':40,'native_checks':46,'archive_files':len(archive),'goal_complete':False}))
