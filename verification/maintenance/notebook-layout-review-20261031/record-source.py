from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import ast,ctypes,difflib,json,re,runpy,subprocess,sys,time
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts'),str(R/'.cache/305-window-tooldeps')]
BASE='16275f656caae29729f8ef30bace380fba08a3b3';B=R/'verification/maintenance/notebook-layout-review-20261031';prefix=B.relative_to(R).as_posix()+'/'
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
changed=['rouge/player_inline_notes.py','rouge/player_note_style.py','rouge/player_compact.py']
for name in changed:
 before='research/notebook-layout-review-20261031/before-'+Path(name).name;assert old(name)==(R/before).read_bytes()
unchanged=['rouge/player_notes.py','rouge/player_note_preview.py','rouge/player_note_library.py','rouge/player_note_export.py','rouge/player_note_scopes.py','rouge/player_recent_notes.py','rouge/player_note_selector.py','rouge/run_state.py','rouge/damage.py','rouge/reporting.py','PROJECT_REQUIREMENTS.md']
for n in unchanged:assert old(n)==(R/n).read_bytes(),n
assert not subprocess.check_output(['git','diff','--name-only',BASE,'--','rouge/data']).strip()
tests=read(prefix+'tests-release/results.json');assert tests['passed']and tests['tests_run']==76 and tests['failed']==tests['errors']==0 and not tests['skipped']and not tests['forbidden_external_calls']
ids=re.findall(r'^test_\w+ \(([^)]+)\)',(R/(prefix+'tests-release/stderr.txt')).read_text('utf8'),re.M);assert len(ids)==len(set(ids))==76
assert read(prefix+'tests-release/process.json')['actual_observed_exit']==0
native=read(prefix+'native-final/receipt.json');legacy=read(prefix+'legacy-inline-current/receipt.json')
for rec,count,process in [(native,34,'native-final-process.json'),(legacy,66,'legacy-inline-current/process.json')]:
 assert rec['passed']and rec['unique_checks']==count and not any(rec['external_operation_attempts'].values())
 assert read(prefix+process)['actual_observed_exit']==0
 for name in changed:assert rec['source_sha256_after'][name]==pin(name)['sha256'],name
assert read(prefix+'native-process.json')['actual_observed_exit']==1
assert not read(prefix+'tests-current/results.json')['passed']
images=native['screenshots']+read(prefix+'native-final/images.json')['images'];assert len(images)==7
reused={'conflict-visible.png','inline-edit.png','inline-reading.png','reading-after-resize.png'}
visual=[]
for row in images:
 name=row.get('file',row.get('path'));p=R/name;assert sha256(p.read_bytes()).hexdigest()==row['sha256']
 if p.name in reused:assert p.read_bytes()==(B/'native-current'/p.name).read_bytes()
 visual.append({'file':p.relative_to(R).as_posix(),'sha256':row['sha256'],'review':'exact whole bytes of individually viewed current-attempt image'if p.name in reused else'individually viewed final original image'})
write(prefix+'native-final/visual-review.json',{'final_images':visual,'final_image_paths':7,'new_final_images_individually_viewed':3,'exact_byte_reuse_of_current_images_also_viewed_this_turn':4,'legacy_auxiliary_images_not_new_full_visual_audit':6,'whole_video_parity_claimed':False})
for source in ('.cache/verify_notebook_layout_native.py','.cache/run_notebook_layout_checks.py'):(B/Path(source).name).write_bytes((R/source).read_bytes())
(B/'tests-release/test-source.py').write_bytes((R/'tests/test_notebook_layout_review.py').read_bytes())
live=read(prefix+'live-window/window.json');assert live['passed']and live['private_six_paths_unchanged']
import win32gui,win32process
for w in live['owned_windows']:assert win32gui.IsWindowVisible(w['hwnd'])and win32process.GetWindowThreadProcessId(w['hwnd'])[1]==w['pid']and not ctypes.windll.user32.IsHungAppWindow(w['hwnd'])
first=read('.cache/notebook-layout-review-live-status.json');time.sleep(2.2);last=read('.cache/notebook-layout-review-live-status.json');assert last['toolbar_visible']and last['elapsed_since_launch']>first['elapsed_since_launch']
write(prefix+'live-window/desktop-review.json',{'actual_Windows_MCP_snapshot_image_viewed':True,'region':[1716,1164,2130,1218],'actual_test_window_visible_responding_and_timer_advanced':True,'private_six_paths_unchanged_during_startup':True,'private_contents_or_hashes_published':False,'game_operated':False,'chat_sent':False})
video=read('.cache/notebook-layout-review-video/frames.json');assert len(video['frames'])==3 and video['video_sha256']=='0b83e44f0816508ef095120961496337e6bd65d5f531ee350c078950dfb98bda'
for frame in video['frames']:assert pin('.cache/notebook-layout-review-video/'+str(frame['second'])+'.png')['sha256']==frame['sha256']
video.update({'all_three_frames_individually_viewed':True,'prior_original_194_and205_frames_also_viewed':True,'source_frames_kept_local_only':True,'whole_video_rewatched':False,'audio_transcribed':False,'facts_observed':'Four selectors; parent-content option; save state above note; click body edits Markdown; later frame returns to rendered reading; pale wide window and white content card. Exact transition timing, all focus boundaries and all visual dimensions not proven.'})
write(prefix+'video-reference.json',video)
net=sum(len((R/n).read_bytes().splitlines())-len(old(n).splitlines())for n in changed)
write(prefix+'source-review.json',{'baseline_commit':BASE,'changed_source':[pin(n)for n in changed],'unchanged_store_notes_models_and_requirements':[pin(n)for n in unchanged],'reuse':'One existing NotesDialog/NoteStore/editor/preview/actions, reparented existing control layout into hidden options. Local Qt event filters and existing autosave timer signals; no editor/storage copy or new dependencies.','native_original_validation_adaptations':'Two original explicit-edit mouse-click paths first reveal More; all prior assertions retained.','physical_production_lines_net_added':net,'net_code_reduction_claimed':False,'performance_improvement_claimed':False,'defensive_guards_removed':False,'accuracy_private_state_conflict_guards_retained':True,'initial_real_native_defect':'FocusOut-only handling did not react to an actual click on the notebook blank surface. Added local surface event handling, no global event interception; original failure and executed source retained.','first_unit_failure':'90 Markdown soft newline lines wrapped into one paragraph, so the fixture wrongly expected scroll. Corrected fixture to separate paragraphs, no product scroll threshold relaxed.','primary_Qt_sources':['https://doc.qt.io/qtforpython-6/PySide6/QtCore/QObject.html#PySide6.QtCore.QObject.eventFilter','https://doc.qt.io/qt-6/qabstracttextdocumentlayout.html#documentSizeChanged'],'REA_scope':'Skill already read; complete Python source and actual runtime examined, no new REA call. Earlier REA bytecode and CJS analyses not conflated.','not_complete':'Full video typography, spacing, exact remaining controls, cross-screen/DPI, complete ownership and whole-program review remain. No game or chat validation.'})
title='笔记支持点击正文编辑、离开后阅读并收拢常驻操作'
write(prefix+'summary.json',{'kind':'implementation_review_maintenance','title':title,'baseline_commit':BASE,'completed_sections':440,'functional_section_added':False,'implemented_scope_passed':True,'different_tests':76,'passed_tests':76,'skipped':0,'new_tests':8,'native_primary_unique_checks':34,'legacy_inline_unique_checks_separate':66,'overlapping_native_ranges_not_added':True,'actual_native_exits':[0,0],'final_primary_images':7,'new_final_viewed':3,'exact_byte_reused_viewed_this_turn':4,'initial_failures_preserved':True,'original_private_storage_and_mechanisms_unchanged':True,'test_window_updated':True,'private_six_paths_unchanged_during_startup':True,'source_review':pin(prefix+'source-review.json'),'tests':pin(prefix+'tests-release/results.json'),'native':pin(prefix+'native-final/receipt.json'),'legacy_native':pin(prefix+'legacy-inline-current/receipt.json'),'full_validation_rerun':False,'full440_only_original_frozen_source':True,'whole_program_complete':False,'whole_video_parity_complete':False,'P3_complete':False,'P2_complete':False,'P1_complete':False,'game_operated':False,'chat_sent':False,'private_data_included':False,'publication_binding':'enclosing maintenance commit, ordinary push and actual remote verification required'})
text('research/notebook-layout-review-20261031/README.md','''# 笔记直接编辑、阅读与紧凑布局

回看本机原录像194/205秒原图，并从整字节不变原片新提取207/210/213秒三帧实际查看，保留摘要与解码位置，不发布原片或新帧。看见四列选择、上级内容选项、上方保存状态、正文点击进入Markdown输入及后续排版阅读；不能由几帧证明所有切换时间和完整视觉一致。本批按REA技能直接审完整Python链路并运行，不新调用REA，不机械扫描字节码。

复用原NotesDialog、NoteStore、同一正文/预览和原按钮/布局；未增加编辑副本、库、存储格式或框架。常用页面只留选择、上级内容、保存状态和正文卡，原保存/放弃/导出/跟随/刷新等收进可展开更多操作；点正文或按回车/F2编辑。自动保存开启时离开输入或点击本笔记空白区域返回排版阅读；手动模式草稿保留，保存冲突展开原提示并保留双方。原分类不可核对的旧笔记在正文标题明确说明，不藏在更多操作里。

初始尺寸900×360逻辑像素，短笔记按内容高度、长笔记保留滚动，实际720×420、1100×450、900×360变换核对内容与光标；未宣称全跨屏/DPI完成。复用Qt本地事件过滤和现有自动保存定时器信号，依据[QObject事件过滤](https://doc.qt.io/qtforpython-6/PySide6/QtCore/QObject.html#PySide6.QtCore.QObject.eventFilter)、[文档尺寸信号](https://doc.qt.io/qt-6/qabstracttextdocumentlayout.html#documentSizeChanged)。不拦截游戏、全局鼠标或按键。首轮实际窗口证明仅FocusOut不能覆盖空白点击，已补本窗口处理；失败源/原件保留。未删保存锁、摘要冲突或未保存草稿保护；本批净增界面代码，不冒称净精简或实测提速。

76个不同检查全通过、无跳过，含8项新场景及68项已有笔记/预览/目录/导出/跟随/原存储范围。首轮75项中1项把Markdown软换行误当独立段落，修正公开夹具并保留原失败，未改滚动阈值。最终实际原生主流程34项、原单窗66项分别退出0，重叠不累计；两处旧实际鼠标入口先展开更多，其余原断言保留，保存/草稿/上级/完整目录/旧分类和原key核对仍在。最终主流程7张原图：3张新最终原图逐张查看，4张与本轮也已逐张查看的前次原图整字节一致复用；旧入口附图6张只作交互原件，未新冒称完整外观审阅。

原项目小窗已正常更新，可见响应且计时推进，正常关闭/启动期间私人六路径保持；不操作游戏、不发送聊天、不上传个人数据。功能440/未开441，选择器715，full440只证明其原冻结源码。字体、边距、完整比例/跨屏、所有视频交互与整个程序/P3/P2/P1仍未完成；识别最后。
''')
entry=f'''<!-- notebook-layout-review-20261031:start -->
## 实现回顾维护 · {title}

复用原编辑器/存储与按钮，正文可点选/键盘编辑，自动保存后离开输入回到排版阅读；常驻操作收进更多，上方显示保存状态与准确标题，旧分类警告仍就近可见。手动草稿、冲突及身份保护保持；原生空白点击失焦缺口同批修正，不称净减代码或提速。

76个不同检查全通过；最终主原生34项、原单窗66项分别真实退出0，重叠不累计。主图7张中3新最终图逐张查看、4与本轮已看原图整字节一致复用；失败原件保留。实际小窗更新响应、启动六处私人路径保持。回执：`{prefix}summary.json`。功能440/未开441，字体间距、跨屏/完整视频、全程序及P3/P2/P1仍未完成，识别最后。
<!-- notebook-layout-review-20261031:end -->

'''
for n in ('WORK_IN_PROGRESS.md','PROJECT_COMPLETED.md'):text(n,entry+(R/n).read_text('utf8'))
for n in ('PROJECT_PROGRESS.md','PROGRAM_REVIEW.md'):
 t=(R/n).read_text('utf8').replace('笔记紧凑排版/跨屏','笔记字体、间距与跨屏').replace('笔记紧凑排版及其余','笔记字体、间距及其余')
 if n=='PROGRAM_REVIEW.md':t+='\n[紧凑笔记交互回顾](research/notebook-layout-review-20261031/README.md)复用原编辑器实现正文点击编辑与失焦阅读，操作收拢，草稿/冲突/旧分类说明保持。76项不同检查及34/66两组原生范围分别通过；字体间距、全跨屏、全视频与全程序仍未完成。\n'
 text(n,t)
text('VIDEO_PARITY.md',(R/'VIDEO_PARITY.md').read_text('utf8')+'\n[紧凑笔记交互](research/notebook-layout-review-20261031/README.md)按原片207/210秒点击编辑/排版阅读补齐操作路径，原按钮收拢、短卡与上方保存状态保持；76项不同检查及34/66原生范围分别通过。字体、边距、全窗口/跨屏和原片其它细节仍非完全一致，不把本批当完整外观验收。\n')
text('IMPLEMENTATION_STRATEGY.md',(R/'IMPLEMENTATION_STRATEGY.md').read_text('utf8')+'\n[笔记本地复用](research/notebook-layout-review-20261031/README.md)沿用已有Qt正文、预览、存储、按钮及自动保存计时器，在原适配层集中处理点击/阅读与操作收拢；无新依赖或复制编辑器，仍保留必要的草稿与冲突保护。净增加界面适配代码，不称净精简或端到端提速。\n')
cp=read('DEVELOPMENT_CHECKPOINT.json');cp['current_maintenance_save']={'kind':'implementation_review_maintenance','title':title,'receipt':prefix+'summary.json','binding':'enclosing_commit','functional_section_added':False,'status':'partial_program_review_notebook_layout','review_checklist':'PROGRAM_REVIEW.md','review_checklist_sha256':pin('PROGRAM_REVIEW.md')['sha256'],'application_review_complete':False};cp['current_batch']['receipt']=prefix+'summary.json';cp['next_action']='继续全程序/视频回顾：核对历史列表卡片与楼层页签、其它附属阅读器和缓存失效、缺图/数值依赖及独立机制；笔记字体间距、完整跨屏与真实页面归属仍待验。本批直接点击编辑/失焦阅读已接入，不重复计完成；识别最后。'
text('DEVELOPMENT_CHECKPOINT.json',json.dumps(cp,ensure_ascii=False,indent=2)+'\n');idx=runpy.run_path(str(R/'scripts/update_cloud_index.py'));idx['update'](R);assert idx['validate_delivery'](R,cp)['current_section']==440
from scripts.verify_full_available import maintained_selectors
selectors=maintained_selectors();assert len(selectors)==715 and selectors[-1]=='tests.test_notebook_layout_review'
anchor=b"ADDITIONAL_MODULES += ('tests.test_relic_report_scope_review',)";assert (R/'scripts/verify_full_available.py').read_bytes()==old('scripts/verify_full_available.py').replace(anchor,anchor+b"\r\n\r\nADDITIONAL_MODULES += ('tests.test_notebook_layout_review',)")
assert read('CLOUD_INDEX.json')['requirements']['sha256']==pin('PROJECT_REQUIREMENTS.md')['sha256']
write(prefix+'final-audit.json',{'passed':True,'baseline_commit':BASE,'summary':pin(prefix+'summary.json'),'requirements':pin('PROJECT_REQUIREMENTS.md'),'cloud_index':pin('CLOUD_INDEX.json'),'different_tests':76,'native_ranges_separate':[34,66],'ordered_selectors':715,'whole_program_complete':False,'whole_video_parity_complete':False,'at_UTC':datetime.now(timezone.utc).isoformat()})
(B/'record-source.py').write_bytes(Path(__file__).read_bytes())
files={p.relative_to(R).as_posix():{k:v for k,v in pin(p.relative_to(R)).items()if k!='path'}for p in sorted(B.rglob('*'))if p.is_file()and p.name!='archive-manifest.json'}
write(prefix+'archive-manifest.json',{'kind':'explicit_public_archive','files':files})
print(json.dumps({'passed':True,'different_tests':76,'native_separate_ranges':[34,66],'final_image_paths':7,'archive_files':len(files),'whole_goal_complete':False}))
