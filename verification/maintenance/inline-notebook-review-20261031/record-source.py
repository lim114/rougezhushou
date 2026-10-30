from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import ast,json,sys,subprocess,difflib,runpy,re,time,ctypes
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts')]
B=R/'verification/maintenance/inline-notebook-review-20261031';prefix=B.relative_to(R).as_posix()+'/'
baseline='186544860f22c0b9e8845059dc7a49cc2cb67706'
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
def old(n):return subprocess.check_output(['git','show',baseline+':'+n])
def definitions(raw):return {n.name:n for n in ast.parse(raw).body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}
def same(a,b):return ast.dump(a,include_attributes=False)==ast.dump(b,include_attributes=False)
assert subprocess.check_output(['git','rev-parse','HEAD']).decode().strip()==baseline
changed=['rouge/app.py','rouge/player_compact.py','rouge/player_feature_419_acceptance.py','rouge/player_note_selector.py','rouge/player_note_style.py','rouge/player_notes.py','rouge/player_reference_notes.py','rouge/player_inline_notes.py','rouge/player_note_scopes.py']
for name in ['NoteStore','content_key']:assert same(definitions(old('rouge/player_notes.py'))[name],definitions((R/'rouge/player_notes.py').read_bytes())[name])
a=definitions(old('rouge/player_notes.py'))['NotesDialog'];b=definitions((R/'rouge/player_notes.py').read_bytes())['NotesDialog'];am={x.name:x for x in a.body if isinstance(x,ast.FunctionDef)};bm={x.name:x for x in b.body if isinstance(x,ast.FunctionDef)}
assert set(bm)==set(am)|{'reject'}
for name in am:
 if name!='set_context':assert same(am[name],bm[name]),name
unchanged=['rouge/player_note_library.py','rouge/player_note_preview.py','rouge/player_note_export.py','rouge/player_note_export_ui.py','rouge/player_recent_notes.py','rouge/run_state.py','rouge/current_event_directory.py','rouge/current_event_resources.py','rouge/current_event_item_uses.py','PROJECT_REQUIREMENTS.md']
for n in unchanged:assert old(n)==(R/n).read_bytes()
initial=read(prefix+'tests/results.json');assert initial['tests_run']==109 and initial['failed']==2 and initial['errors']==1
ids=set()
for folder,count in [('tests-current',109),('tests-current-delivery',18)]:
 d=read(prefix+folder+'/results.json');assert d['passed']and d['tests_run']==count and not d['skipped']and not d['forbidden_external_calls'];assert read(prefix+folder+'/process.json')['actual_observed_exit']==0
 matched=re.findall(r'^\w+ \((tests\.[^)]+)\) \.\.\. ok$',(B/folder/'stderr.txt').read_text('utf8'),re.M);assert len(matched)==count;ids.update(matched)
assert len(ids)==115
natives=[]
for folder,count in [('native-delivery',66),('native-reference-delivery',22),('native-selector-delivery',19),('native-autosave-delivery',17)]:
 d=read(prefix+folder+'/window.json');assert d['passed']and d['unique_checks']==count and not any(d['external_operation_attempts'].values())and not d['source_drift'];assert read(prefix+folder+'/process.json')['actual_observed_exit']==0
 assert all(d['source_sha256_after'][n]==pin(n)['sha256']for n in changed)
 natives.append({'receipt':pin(prefix+folder+'/window.json'),'process':pin(prefix+folder+'/process.json'),'unique_checks':count})
write(prefix+'source-review.json',{'baseline_commit':baseline,'changed_source':[pin(n)for n in changed],'unchanged_storage_export_state_and_public_mechanisms':[pin(n)for n in unchanged],'NoteStore_and_content_key_AST_unchanged':True,'existing_editor_methods_unchanged_except_context_label_and_added_Escape_routing':True,'existing_reference_note_keys_migrated':False,'new_scope_key_kind':'note-scope','source_version_floor_and_node_are_part_of_scope_identity':True,'same_shared_editor_and_store_used_in_actual_native_window':True,'simplification':'One saved-note entry route, one editor, one store; parent navigation reuses the same selector. Stable preview stamp suppresses repeated editor reads. No new parser, renderer, database or dependency.','REA_scope':'Complete Python source read directly under REA skill. Existing bridge/toolbar reverse evidence retained; no artificial PYC or whole-program claim.','retained_protections':'Conflict/digest/atomic save and symlink guards, unsaved draft ownership, exact source/unknown classification, ordinary publication and private-state boundaries.','application_review_complete':False})
shots=[]
for folder in ['native-delivery','native-reference-delivery','native-selector-delivery','native-autosave-delivery']:
 for p in sorted((B/folder).glob('*.png')):shots.append({'image':pin(p.relative_to(R)),'reviewer':'/root','review_method':'individually loaded with view_image','scope':'isolated public fixtures, not user notes or game'})
assert len(shots)==11
write(prefix+'image-review.json',{'images':shots,'reference_frames_actually_viewed':[pin('.cache/reference-local-video-385/timeline/'+n)for n in ['frame-064.jpg','frame-065.jpg','frame-066.jpg','frame-069.jpg','frame-071.jpg']],'video_identity_receipt':pin('verification/sections/392-video-review.json'),'visual_failures_retained':['native/parent-notes.png: dark squeezed parent viewport','native-final-cards/archived-note.png: deleted parent widgets remained visible until deferred Qt deletion'],'fixes':'Light ancestor surface, bounded readable outer scrolling, document-sized child cards and immediate hide before deferred delete. Correct exact-entry picker and autosave description.','whole_video_parity_claimed':False})
live=read(prefix+'live-window/window.json');assert live['passed']and live['private_six_paths_unchanged']and all(live['source_sha256_after'][n]==pin(n)['sha256']for n in changed)
import win32gui,win32process
for w in live['owned_windows']:assert win32gui.IsWindowVisible(w['hwnd'])and win32process.GetWindowThreadProcessId(w['hwnd'])[1]==w['pid']and not ctypes.windll.user32.IsHungAppWindow(w['hwnd'])
a=read('.cache/runtime-inline-notes-review-live-status.json');time.sleep(2.2);b=read('.cache/runtime-inline-notes-review-live-status.json');assert b['toolbar_visible']and b['elapsed_since_launch']>a['elapsed_since_launch']
write(prefix+'live-window/desktop-review.json',{'actual_windows_mcp_snapshot_called':True,'actual_image_viewed':True,'region':[1716,1164,2130,1218],'owned_test_window_visible_and_responding':True,'Qt_timer_advanced':True,'private_six_paths_unchanged_during_startup':True,'private_contents_or_hashes_published':False,'game_operated':False,'chat_sent':False})
title='复用同一编辑器完成单窗笔记、上级通用笔记与准确入口联动'
write(prefix+'summary.json',{'kind':'implementation_review_maintenance','title':title,'baseline_commit':baseline,'completed_sections':440,'functional_section_added':False,'implemented_scope_passed':True,'related_unique_tests':115,'test_scope':'Initial current 109 passed; original 97 unchanged scopes reused, all 12 original new cases and 6 further cases verified in final 18. Intermediate 13/16/17 results not added again.','current_focused_receipt':pin(prefix+'tests-current-delivery/results.json'),'related_existing_receipt':pin(prefix+'tests-current/results.json'),'native_ranges':natives,'native_ranges_overlap_not_summed':True,'source_review':pin(prefix+'source-review.json'),'image_review':pin(prefix+'image-review.json'),'runtime':pin(prefix+'live-window/desktop-review.json'),'initial_failures':'First 109 run retained: 2 actual editor-switch failures fixed by retaining intended edit mode, and 1 fixture error fixed by creating its temporary notes folder before simulating an external write.','visual_failure':'First native green was insufficient: root image review caught stale parent cards still visible after layout removal. Now hides immediately, and explicit pre-deferred-delete visibility and actual archived-note assertions passed.','stable_editor_refresh_measurement':{'consecutive_unchanged_refreshes':30,'additional_note_reads':0,'external_changed_file_reads_for_preview_and_editor':2,'whole_program_speedup_claimed':False},'application_review_complete':False,'video_parity_complete':False,'P3_complete':False,'P2_complete':False,'P1_complete':False,'full_validation_rerun':False,'full440_only_original_frozen_source':True,'private_data_included':False,'game_operated':False,'chat_sent':False,'publication_binding':'enclosing maintenance commit, ordinary push with actual remote and public-file blob verification'})
text('research/inline-notebook-review-20261031/README.md','''# 单窗笔记、手选范围与上级内容

本轮继续按REA技能阅读完整Python源码与实际Qt行为；不机械生成PYC，不冒称全程序审完。回看本地录像约3:12–3:33的主题/楼层/节点/详情、通用笔记与Markdown片段。视频中的上级开关可见，但原片未演示它的全部边界；本实现按明确手选范围提供上级只读内容，不宣称未知细节完全复刻。

## 复用路线与实际改动

保留既有NotesDialog、NoteStore、NotePreview、元数据与导出，使用Qt官方setParent(parent, flags)一次嵌入QStackedWidget，清除Qt.Dialog标记。编辑、预览、已保存笔记、固定资料和最近场景入口汇入一个浮窗，不增加第二份编辑正文或存储。诊断模式仍保留原窗口。官方依据：[QDialog](https://doc.qt.io/qtforpython-6/PySide6/QtWidgets/QDialog.html)和[QWidget](https://doc.qt.io/qtforpython-6/PySide6/QtWidgets/QWidget.html)。

主题、层数、节点类别可保存通用笔记，具体场景仍用原准确身份；原笔记键不迁移。新通用笔记包含资料版本、楼层和节点类别。上级内容只读，点击可在同一编辑器打开；多楼层/多类别未唯一确定时不猜归属，实时同名场景不借固定目录身份。当前目录缺失的已保存笔记只能由本机笔记库明确打开，仍按旧键编辑，没有冒用当前同名资料或上级笔记。

复用原保存锁、摘要冲突和原子写入规则。未保存手动草稿阻止切换、关闭及Escape；开启自动保存时先保存原所属范围再切换，冲突保留双方且暂停。读取推进或手动新局不改草稿归属。外部入口同步四列实际选择，不保留错误的“通用笔记”高亮；编辑模式不再沿用“此处不自动保存”的只读说明。

原编辑器每次普通刷新都可能重新读文件，现复用已读预览的文件变化标记；30次未变化刷新额外读取为0，文件变化后预览和编辑各读一次。只是组件读取次数，不是整机或识别耗时。上级卡用文档高度适配并由外层滚动，避免正文裁切和双重滚动；切换时立即隐藏旧卡，再交给Qt延后销毁。

## 验证与剩余范围

相关115个不同用例通过：97个既有未变范围复用，最终18项覆盖全部新场景，不重复累计中间结果。当前原生主流程66项、固定资料22项、分类19项、自动保存17项分别通过，真实退出0，重叠不累计。首次109项的2个实际失败和1个夹具错误保留。绿色窗口回执曾漏掉旧卡片延后删除的可见残留，实际截图发现后同批修正并增强断言；旧截图不覆盖。

最终11张原图逐张查看，原项目测试窗已正常更新可见响应，启动区间六处私人路径保持；所有隔离用例只用临时公开构造数据，外部操作计数为零，不操作游戏、不发聊天、不上传个人数据。资料/计算机制和识别策略未改。菜单密度、边距、窗口比例及其余视频/跨屏/真实页面归属仍未全部一致；保留现有完整待办。功能计数仍440，本轮为实现回顾维护，不增加节数，下一周期全量455。完整程序回顾、P3/P2/P1和全部视频目标仍未完成。
''')
n='PROGRAM_REVIEW.md';t=(R/n).read_text('utf8').replace('当前总范围531份（含本轮新增共享笔记样式）','当前总范围533份（含共享笔记样式及本轮单窗/范围模块）');t=t.replace('视频单窗内编辑/预览、上级范围笔记、其余分类/真实页归属及全部外观仍待验','其余分类/真实页归属、笔记紧凑排版/跨屏及全部外观仍待验');t=t.replace('恢复事件资料目录，完整分类539项。存储/导出保护未变。','恢复事件资料目录，完整分类539项；复用同一编辑器完成单窗、主题/楼层/节点通用笔记及上级只读内容。存储/导出保护未变。');t+='\n[单窗笔记回顾](research/inline-notebook-review-20261031/README.md)已接入范围通用笔记与上级内容、固定/已保存笔记统一入口；初轮截图发现的残留卡片已修正。原片全部排版、跨屏和其它链路仍未完成。\n';text(n,t)
n='VIDEO_PARITY.md';t=(R/n).read_text('utf8').replace('视频单窗内编辑/预览与上级范围笔记尚未实现，不能把当前独立编辑窗口当作一致。','后续单窗回顾已复用同一编辑器并接入上级通用笔记；其余排版、完整分类和真实归属仍待验。');t+='\n[单窗笔记回顾](research/inline-notebook-review-20261031/README.md)已让最近场景、固定资料和已保存笔记共用一个浮窗编辑/预览，并支持主题/楼层/节点通用笔记与上级只读内容。原笔记身份/保存规则保持；额外按钮密度、边距、窗口比例和全部原片细节仍未全部一致，不以本轮交互通过替代全套视觉验收。\n';text(n,t)
entry=f'''<!-- inline-notebook-review-20261031:start -->
## 实现回顾维护 · {title}

既有编辑器一次嵌入，最近场景/固定资料/保存笔记入口汇入同一浮窗。新主题/楼层/节点通用笔记按资料版本与范围保存，上级只读、可点开编辑；不猜同名场景归属。旧版本笔记仍按原键明确打开。草稿、自动保存、冲突、Escape与关闭规则同用，原存储/导出保护不变。

相关115个不同用例通过，当前18项覆盖全部新增场景；原生主流程66项及固定资料22/分类19/自动保存17项分别通过，重叠不累计。初轮109项的2实际失败1夹具错误、绿色回执漏掉的旧卡可见残留与修正前图片保留；增强实际可见断言。30次未变化刷新额外文件读取0，仅组件工作量。最终11张原图逐张查看，测试窗更新可见响应，启动区间六处私人路径保持。功能仍440，441未启动，完整回顾/视频与P3/P2/P1未完成，识别最后。回执：`{prefix}summary.json`。
<!-- inline-notebook-review-20261031:end -->

'''
for n in ['WORK_IN_PROGRESS.md','PROJECT_COMPLETED.md']:text(n,entry+(R/n).read_text('utf8'))
n='PROJECT_PROGRESS.md';t=(R/n).read_text('utf8').replace('视频单窗内编辑/预览与上级范围笔记、','').replace('核对其它资料窗口、视频交互/外观','核对其它资料窗口、笔记紧凑排版及其余视频交互/外观');text(n,t)
cp=read('DEVELOPMENT_CHECKPOINT.json');cp['current_maintenance_save']={'kind':'implementation_review_maintenance','title':title,'receipt':prefix+'summary.json','binding':'enclosing_commit','functional_section_added':False,'status':'partial_program_review_shared_notebook_and_scope_navigation_verified','review_checklist':'PROGRAM_REVIEW.md','review_checklist_sha256':pin('PROGRAM_REVIEW.md')['sha256'],'application_review_complete':False};cp['current_batch']['receipt']=prefix+'summary.json';cp['next_action']='继续全程序回顾与视频逐项对齐：笔记紧凑排版/完整分类和真实归属、其余资料入口与窗口、招募/强化连续状态和独立机制校准、历史楼层/资源与完整统计。单窗编辑/上级通用笔记已接入，不重复列待办；识别优化最后。'
text('DEVELOPMENT_CHECKPOINT.json',json.dumps(cp,ensure_ascii=False,indent=2)+'\n');m=runpy.run_path(str(R/'scripts/update_cloud_index.py'));m['update'](R);assert m['validate_delivery'](R,cp)['current_section']==440
from scripts.verify_full_available import maintained_selectors
selectors=maintained_selectors();assert len(selectors)==698 and selectors[-1]=='tests.test_inline_notebook_review';assert read('CLOUD_INDEX.json')['requirements']['sha256']==pin('PROJECT_REQUIREMENTS.md')['sha256']
write(prefix+'final-audit.json',{'passed':True,'baseline_commit':baseline,'summary':pin(prefix+'summary.json'),'requirements':pin('PROJECT_REQUIREMENTS.md'),'cloud_index':pin('CLOUD_INDEX.json'),'ordered_selectors':698,'unique_related_tests':115,'native_ranges':[66,22,19,17],'native_counts_not_summed':True,'private_contents_included':False,'whole_program_complete':False,'whole_video_parity_complete':False,'at_UTC':datetime.now(timezone.utc).isoformat()})
(B/'record-source.py').write_bytes(Path(__file__).read_bytes());manifest={p.relative_to(R).as_posix():{k:v for k,v in pin(p.relative_to(R)).items()if k!='path'}for p in sorted(B.rglob('*'))if p.is_file()and p.name!='archive-manifest.json'};write(prefix+'archive-manifest.json',{'kind':'explicit_public_archive','files':manifest});print(json.dumps({'passed':True,'unique_tests':115,'native':[66,22,19,17],'archive_files':len(manifest),'goal_complete':False}))
