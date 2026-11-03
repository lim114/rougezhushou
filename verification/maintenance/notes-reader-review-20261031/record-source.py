from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import ast,json,sys,subprocess,difflib,runpy,re,time,ctypes,types

R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts')]
B=R/'verification/maintenance/notes-reader-review-20261031';prefix=B.relative_to(R).as_posix()+'/'
baseline='a7f437e534cffd13df7d4a9e55defb10f32f9a72'
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
def functions(raw):
 return {n.name:ast.dump(n,include_attributes=False)for n in ast.parse(raw).body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}
assert subprocess.check_output(['git','rev-parse','HEAD']).decode().strip()==baseline
changed=['rouge/player_recent_notes.py','rouge/player_notes.py','rouge/player_note_selector.py','rouge/player_note_library.py','rouge/player_note_library_acceptance.py','rouge/player_note_style.py','rouge/current_event_directory.py','rouge/current_event_resources.py','rouge/current_event_item_uses.py']
reviewed=changed+['rouge/player_note_preview.py','rouge/player_note_export.py','rouge/player_reference_notes.py','rouge/ui_state.py','rouge/run_state.py']
initial=read(prefix+'tests/results.json');assert initial['tests_run']==56 and initial['failed']==1 and initial['errors']==2
related=[];ids=[]
for folder,count in [('tests-current',97),('views',35)]:
 d=read(prefix+folder+'/results.json');assert d['passed']and d['tests_run']==count and not d['failed']and not d['errors']and not d['skipped']and not d['forbidden_external_calls']
 assert read(prefix+folder+'/process.json')['actual_observed_exit']==0
 found=re.findall(r'^\w+ \((tests\.[^)]+)\) \.\.\. ok$',(B/folder/'stderr.txt').read_text('utf8'),re.M)
 assert len(found)==count,(folder,len(found));ids.extend(found);related.append({'receipt':pin(prefix+folder+'/results.json'),'count':count,'process':pin(prefix+folder+'/process.json')})
assert len(set(ids))==132
native=read(prefix+'native/window.json');assert native['passed']and native['unique_checks']==54 and not any(native['external_operation_attempts'].values())
assert read(prefix+'native/process.json')['actual_observed_exit']==0
assert not native['source_drift']
assert all(native['source_sha256_after'][n]==pin(n)['sha256']for n in changed)
invariants={}
for n,names in [('rouge/player_notes.py',['NoteStore','content_key']),('rouge/player_note_library.py',['NoteLibrary','_regular'])]:
 a,b=functions(old(n)),functions((R/n).read_bytes())
 for name in names:assert a[name]==b[name];invariants[n+':'+name]='unchanged AST'
unchanged=['rouge/run_state.py','rouge/player_note_preview.py','rouge/player_note_export.py','rouge/player_reference_notes.py','rouge/ui_state.py','PROJECT_REQUIREMENTS.md']
for n in unchanged:assert old(n)==(R/n).read_bytes()
for n in changed[-3:]:
 a,b=functions(old(n)),functions((R/n).read_bytes());assert set(a)==set(b)
 for name in a:
  if name!='packet':assert a[name]==b[name],(n,name)
 invariants[n]='Only packet schema/data binding changes; all other function/class AST equal'
frozen={}
for base in ['research/p3-current-event-directory-372','research/p3-current-event-resources-374','research/p3-current-event-item-uses-376']:
 paths=subprocess.check_output(['git','ls-tree','-r','--name-only',baseline,'--',base]).decode().splitlines()
 for n in paths:assert old(n)==(R/n).read_bytes();frozen[n]=pin(n)
for n in ['rouge/data/current-event-directory.json','rouge/data/current-event-resources.json','rouge/data/current-event-item-uses.json']:assert old(n)==(R/n).read_bytes();frozen[n]=pin(n)
from rouge import current_event_directory as directory,current_event_resources as resources,current_event_item_uses as uses,player_note_selector as selector,expansion_reference as version
old_mod=types.ModuleType('rouge._old_notes_directory');old_mod.__package__='rouge';old_mod.__file__=str(R/'rouge/current_event_directory.py');exec(compile(old('rouge/current_event_directory.py'),old_mod.__file__,'exec'),old_mod.__dict__)
assert old_mod.packet()is None
old_manifest=read('research/p3-current-event-directory-372/runtime-manifest.json')
drifts=[n for n,v in old_manifest['files'].items()if {k:v for k,v in pin(n).items()if k!='path'}!=v]
assert set(drifts)=={'rouge/node_catalog.py','rouge/expansion_reference.py'},drifts
packets=[directory.packet(),resources.packet(),uses.packet()];assert all(packets)
assert len(packets[0]['data']['rows'])==39 and len(packets[1]['data']['rows'])==88 and len(packets[2]['data']['rows'])==12
catalogue=selector.catalogue_snapshot();assert len(catalogue['rows'])==539 and not catalogue['unavailable']
runtime=[]
for model in (directory,resources,uses):
 m=read(model.MANIFEST);assert sha256((R/model.MANIFEST).read_bytes()).hexdigest()==model.MANIFEST_SHA256
 assert not any(n.endswith('.py')for n in m['files'])
 for n,v in m['files'].items():assert {k:v for k,v in pin(n).items()if k!='path'}==v,n
 runtime.append({'manifest':pin(model.MANIFEST),'file_count':len(m['files']),'all_runtime_files_match':True,'program_code_in_runtime_files':False})
notes=read(directory.NOTES);assert len(notes['historical_recipe_code_sources'])==24
for model,path,field in [(resources,'rouge/data/current-event-resources.json','directory_source_identity'),(uses,'rouge/data/current-event-item-uses.json','source_directory_identity')]:
 a,b=read(path),model.packet()['data'];assert {k:v for k,v in a.items()if k!=field}=={k:v for k,v in b.items()if k!=field}
reproduction=read(prefix+'before-reproduction.json');assert reproduction['actual_RunState_reset_retains_old_paused_context']and reproduction['clean_same_note_reopen_ignores_external_change']and reproduction['manual_context_selection_reads']==2
write(prefix+'source-review.json',{'baseline_commit':baseline,'changed_source':[pin(n)for n in changed],'source_read_scope':[pin(n)for n in reviewed],'unchanged_classes_or_functions':invariants,'unchanged_storage_reading_export_and_requirements':[pin(n)for n in unchanged],'unchanged_frozen_recipe_files':frozen,'runtime_data_manifests':runtime,'old_runtime_failure_reproduced':True,'old_source_pin_drifts':drifts,'restored_catalogue_counts':{'events':39,'event_resource_rows':88,'item_use_rows':12,'note_contexts':539},'all_derived_data_equal_except_source_binding':True,'old_recipe_provenance_code_files_retained':24,'REA_scope':'Complete Python source reviewed directly under REA skill; existing toolbar/bridge reverse evidence retained. No new REA/PYC invocation or whole-application claim.','reuse':'Existing NoteStore, exact key, library metadata/atomic writes, NotePreview, shared replace_text and Qt QSignalBlocker/QTimer; no dependency.','retained_protections':'Exact version/identity, digest/conflict/atomic storage and symlink rejection, unsaved draft, no auto resend and private run state.','application_review_complete':False})
write(prefix+'before-after.json',{'passed':True,'baseline_reproduction':pin(prefix+'before-reproduction.json'),'current_actual_regression_evidence':related,'real_run_reset_old_paused_context_retained_before':True,'real_run_reset_now_clears_only_reading_context':True,'saved_note_and_editor_draft_kept':True,'same_note_clean_reopen_reads_external_change':True,'manual_selection_note_reads_before':2,'manual_selection_note_reads_after':1,'search_burst_queries':4,'search_burst_disk_scans_after':1,'search_timer_ms':150,'search_is_not_whole_program_performance_measurement':True,'old_event_packet_available':False,'current_event_packet_available':True,'old_note_catalogue_available':False,'current_note_contexts':539,'numerical_mechanism_changed':False})
shots=[{'image':pin(p.relative_to(R)),'reviewer':'/root','review_method':'individually loaded with view_image; all seven images actually viewed','scope':'isolated fixture, not real game or personal note'}for p in sorted((B/'native').glob('*.png'))];assert len(shots)==7
write(prefix+'image-review.json',{'images':shots,'source_video_identity_receipt':pin('verification/sections/392-video-review.json'),'reference_frames':[pin('.cache/reference-local-video-385/timeline/'+n)for n in ['frame-064.jpg','frame-069.jpg','frame-071.jpg']],'review_findings':'Four aligned headers, explicit partial-source state and local search/editor text visible. Current readonly preview plus separate editor still differs from inline editing and parent-scope notes in reference.','whole_video_parity_claimed':False})
live=read(prefix+'live-window/window.json');assert live['passed']and live['private_six_paths_unchanged']and all(live['source_sha256_after'][n]==pin(n)['sha256']for n in changed)
import win32gui,win32process
for w in live['owned_windows']:assert win32gui.IsWindowVisible(w['hwnd'])and win32process.GetWindowThreadProcessId(w['hwnd'])[1]==w['pid']and not ctypes.windll.user32.IsHungAppWindow(w['hwnd'])
a=read('.cache/runtime-notes-review-live-status.json');time.sleep(2.2);b=read('.cache/runtime-notes-review-live-status.json');assert b['toolbar_visible']and b['elapsed_since_launch']>a['elapsed_since_launch']
write(prefix+'live-window/desktop-review.json',{'reviewer':'/root','actual_windows_mcp_snapshot_called':True,'actual_image_viewed':True,'region':[1716,1164,2130,1218],'owned_test_window_visible_and_responding':True,'Qt_timer_advanced':True,'private_six_paths_unchanged_during_startup':True,'private_contents_or_hashes_published':False,'game_operated':False,'chat_sent':False})
title='笔记按真实新局清理阅读、同步外部保存，并恢复未变事件资料的加载'
write(prefix+'summary.json',{'kind':'implementation_maintenance','title':title,'baseline_commit':baseline,'completed_sections':440,'functional_section_added':False,'next_section_started':False,'implemented_scope_passed':True,'related_unique_tests':132,'related_ranges':related,'native_unique_checks':54,'native_receipt':pin(prefix+'native/window.json'),'source_review':pin(prefix+'source-review.json'),'comparison':pin(prefix+'before-after.json'),'image_review':pin(prefix+'image-review.json'),'runtime':pin(prefix+'live-window/desktop-review.json'),'first_failure':'Original 56-test run retained with 1 failure and 2 errors. Pre-existing source-code pins disabled unchanged event data, cascading into an empty note catalogue. Fixed with separate data-only runtime packages; old frozen artifacts retained.','runtime_builder':'Public scripts/build_event_runtime_manifests.py reproduces/checks exact CRLF snapshots, refuses to overwrite differing data. Initial LF writer mismatch rejected existing bytes without writes; fixed line endings then both commands succeeded.','application_review_complete':False,'video_parity_complete':False,'P3_complete':False,'P2_complete':False,'P1_complete':False,'full_validation_rerun':False,'full440_only_original_frozen_source':True,'private_data_included':False,'game_operated':False,'chat_sent':False,'publication_binding':'enclosing maintenance commit, ordinary push and actual remote/blob check follows'})
research='research/notes-reader-review-20261031/README.md'
text(research,'''# 笔记阅读、保存联动与事件运行目录回顾

按REA技能直接阅读完整Python源码并做隔离运行验证；已有工具条和聊天桥接REA证据保留，不机械生成PYC或声称全程序已审完。本轮审查范围和摘要见source-review.json。没有替换数值机制、识别策略或聊天后端。

## 修正与复用

暂停跟随的笔记原来使用不存在的run_id字段判断新局，真实RunState使用id；旧测试也用了错误夹具，未暴露问题。现按真实id撤下旧局阅读与编辑目标，已保存笔记和未保存编辑草稿保留。用户手选固定资料会更新观察到的局身份，不被随后刷新误清。未保存草稿不被外部文件或场景变化覆盖。

编辑器原来重复打开同一笔记就直接返回，无法读到其它编辑器的保存。现仅无草稿时重新核对文件；内容不变保持原阅读，内容变化复用项目replace_text保留Unicode光标、选择与滚动。Qt官方QSignalBlocker抑制程序填入造成的脏标记，不触发自动保存。手选笔记阻止勾选框中间刷新，从先读旧文件再读新文件改为只读目标一次。存储、元数据、原子写入、锁、冲突和链接文件拒绝规则未变。

本机笔记库连续输入采用Qt单次150毫秒定时器，四次连输只扫描一次；回车立即搜索，隐藏取消等待。仅减少重复本机文件扫描，不作为整机或识别性能结论。阅读/编辑/笔记库共用浅色样式，四列使用主题、层数、节点、详情。复用现有NoteStore、NoteLibrary、NotePreview及Qt控件，不加依赖。QSignalBlocker官方说明：https://doc.qt.io/qtforpython-6/PySide6/QtCore/QSignalBlocker.html 。

## 原目录的额外问题

必要检查发现基线事件目录已不可用：旧运行清单把24个构建时Python源码也作为资料有效性门槛；其中expansion_reference.py和node_catalog.py的既有重构与旧摘要不同，但全部非代码资料未变。导致39项事件、其88项资源和12项物品用途派生结果以及笔记目录消失。这不是机制资料缺失。

新建三份独立运行资料包，继续逐字节核对全部引用数据/文献/清单；24份代码摘要只保留为原构建来源。原372/374/376冻结包和三份原始数据不改写。资源和用途快照仅更换来源清单身份，其余全部内容一致。scripts/build_event_runtime_manifests.py可再现或核对包，不覆盖不同字节。固定笔记分类相互独立，一种来源失效只撤下该类并明确提示，不再隐藏其它仍可核对资料；完整时539项，来源身份不变，现有私人笔记键不迁移。

## 验证和剩余差异

97项笔记/模型与35项资料视图检查共132个不同用例通过，无跳过；21类现有事件阅读器、来源破坏/恢复及准确资料入口仍受测试覆盖。原生隔离窗口54项唯一检查通过，真实退出0，九类外部操作为零。首次56项的1失败2错误原件保留，不改写成通过。七张最终原图实际逐张查看。原项目测试小窗已正常更新可见且有响应，启动区间六处私人路径保持；不操作游戏、不发送聊天、不上传私人数据。

回看录像约3:12、3:27、3:33的现有原图：视频为单窗内编辑/预览并可显示上级笔记；本项目目前仍有只读备忘录和独立编辑窗口，尚未达到这个完整交互。上级范围笔记、完整分类、真实页面归属和其余外观继续待办，不能以四列/浅色样式冒称一致。功能仍440，本次为维护不启动441；下次定期全量455，full440仅证明其原冻结源码。全程序/视频及P3/P2/P1仍未完成，识别优化最后。
''')
n='PROGRAM_REVIEW.md';t=(R/n).read_text('utf8').replace('当前总范围530份','当前总范围531份（含本轮新增共享笔记样式）');marker='| 桌面聊天桥接 |';row='| 笔记、预览与本机检索 | 已查跟随/选择/读取/存储/元数据/导出与自动保存链路，修复真实新局阅读清理、同笔记外部更新及重复读取/搜索；恢复事件资料目录，完整分类539项。存储/导出保护未变。 | 视频单窗内编辑/预览、上级范围笔记、其余分类/真实页归属及全部外观仍待验；本轮未操作游戏或发送聊天。 |\n'
assert row not in t;t=t.replace(marker,row+marker);t+='\n[笔记阅读与事件运行目录回顾](research/notes-reader-review-20261031/README.md)记录真实局身份和编辑同步修复、原源码摘要误禁未变资料的问题；新运行包保留数据核对和旧冻结来源，未改机制，单窗编辑/上级范围等视频差异仍未解决。\n';text(n,t)
n='VIDEO_PARITY.md';t=(R/n).read_text('utf8');t+='\n[笔记阅读回顾](research/notes-reader-review-20261031/README.md)已统一四列标题、浅色笔记库与阅读/保存同步，修复真实新局残留，并恢复539项准确资料目录。视频单窗内编辑/预览与上级范围笔记尚未实现，不能把当前独立编辑窗口当作一致。\n';text(n,t)
entry=f'''<!-- notes-reader-review-20261031:start -->
## 实现维护 · {title}

真实RunState.id判断新局，清除旧阅读而保留笔记和草稿；同笔记无草稿重开可同步外部保存，复用Unicode阅读保持。手选只读目标一次，本机搜索四次连输合并一次，150毫秒停顿或回车立即执行；笔记库共用浅色样式和四列标题。

基线旧清单因两份已重构源码摘要失配误禁未变事件资料。新独立运行包保留全部数据/文献摘要，旧24份代码作为构建来源而非运行资料门槛；旧冻结包和原始数据不改写，派生88/12行仅更换来源身份。事件39项及完整笔记539项恢复，各分类失效独立提示。

最终132个不同相关用例、原生54项唯一检查通过，无跳过，真实退出0；初轮56项的1失败2错误原件保留。七张原图已逐张查看，测试窗正常更新可见响应，启动区间六处私人路径保持。存储/导出/数值机制不变；不操作游戏、不发聊天。功能仍440，441未启动，全程序/视频及P3/P2/P1未完成，识别最后。回执：`{prefix}summary.json`。
<!-- notes-reader-review-20261031:end -->

'''
for n in ['WORK_IN_PROGRESS.md','PROJECT_COMPLETED.md']:text(n,entry+(R/n).read_text('utf8'))
n='PROJECT_PROGRESS.md';t=(R/n).read_text('utf8');t=t.replace('其余排版和外观覆盖；未观察步骤','视频单窗内编辑/预览与上级范围笔记、其余排版和外观覆盖；未观察步骤');text(n,t)
cp=read('DEVELOPMENT_CHECKPOINT.json');cp['current_maintenance_save']={'kind':'implementation_maintenance','title':title,'receipt':prefix+'summary.json','binding':'enclosing_commit','functional_section_added':False,'status':'partial_program_review_notes_state_and_public_runtime_catalogues_checked','review_checklist':'PROGRAM_REVIEW.md','review_checklist_sha256':pin('PROGRAM_REVIEW.md')['sha256'],'application_review_complete':False};cp['current_batch']['receipt']=prefix+'summary.json';cp['next_action']='继续全程序回顾与视频对齐：笔记单窗内编辑/预览与上级范围、其余资料入口、招募/强化连续状态和独立机制校准、历史楼层/资源和完整统计。旧局阅读、编辑同步及未变资料误禁已修复，不重复推进；识别优化最后。'
text('DEVELOPMENT_CHECKPOINT.json',json.dumps(cp,ensure_ascii=False,indent=2)+'\n');m=runpy.run_path(str(R/'scripts/update_cloud_index.py'));m['update'](R);assert m['validate_delivery'](R,cp)['current_section']==440
from scripts.verify_full_available import maintained_selectors
selectors=maintained_selectors();assert len(selectors)==697 and selectors[-1]=='tests.test_notes_reader_review'
assert read('CLOUD_INDEX.json')['requirements']['sha256']==pin('PROJECT_REQUIREMENTS.md')['sha256']
assert all(native['source_sha256_after'][n]==pin(n)['sha256']for n in changed)
write(prefix+'final-audit.json',{'passed':True,'baseline_commit':baseline,'summary':pin(prefix+'summary.json'),'cloud_index':pin('CLOUD_INDEX.json'),'requirements':pin('PROJECT_REQUIREMENTS.md'),'ordered_selectors':697,'related_unique_tests':132,'native_unique_checks':54,'private_contents_included':False,'whole_program_complete':False,'whole_video_parity_complete':False,'public_runtime_manifests_match':True,'at_UTC':datetime.now(timezone.utc).isoformat()})
(B/'record-source.py').write_bytes(Path(__file__).read_bytes())
manifest={p.relative_to(R).as_posix():{k:v for k,v in pin(p.relative_to(R)).items()if k!='path'}for p in sorted(B.rglob('*'))if p.is_file()and p.name!='archive-manifest.json'}
write(prefix+'archive-manifest.json',{'kind':'explicit_public_archive','files':manifest});print(json.dumps({'passed':True,'related_unique_tests':132,'native_unique_checks':54,'archive_files':len(manifest),'goal_complete':False}))
