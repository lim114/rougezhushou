from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import ast,ctypes,difflib,json,runpy,subprocess,sys,time
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts'),str(R/'.cache/305-window-tooldeps')]
BASE='1fb313cb7a9d8a1eef95389833feac71e4ddbafc';B=R/'verification/maintenance/map-jump-review-20261031';prefix=B.relative_to(R).as_posix()+'/'
def read(n):return json.loads((R/n).read_bytes())
def pin(n):
 p=R/n;raw=p.read_bytes();return {'path':p.relative_to(R).as_posix(),'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}
def write(n,v):(R/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf8')
def text(n,value):
 p=R/n
 if not p.exists():p.parent.mkdir(parents=True,exist_ok=True);p.write_text(value,'utf8');return
 old=p.read_bytes().decode('utf8').splitlines(keepends=True);new=value.splitlines(keepends=True);out=list(new)
 for a,b,num in difflib.SequenceMatcher(None,[s.rstrip('\r\n')for s in old],[s.rstrip('\r\n')for s in new],autojunk=False).get_matching_blocks():
  for i in range(num):out[b+i]=old[a+i]
 p.write_bytes(''.join(out).encode('utf8'))
def old(n):return subprocess.check_output(['git','show',BASE+':'+n])
assert subprocess.check_output(['git','rev-parse','HEAD']).decode().strip()==BASE
changed=['rouge/current_enemy_spawns_view.py','rouge/current_map_position_view.py']
baseline=['research/map-jump-review-20261031/before-current-enemy-spawns-view.py','research/map-jump-review-20261031/before-current-map-position-view.py']
for n,b in zip(changed,baseline):assert old(n)==(R/b).read_bytes()
untouched=['rouge/current_enemy_spawns.py','rouge/current_spawn_candidates.py','rouge/current_spawn_candidates_view.py','rouge/current_action_positions.py','rouge/current_action_positions_view.py','rouge/current_map_position.py','rouge/current_battle_reference.py','rouge/current_battle_view.py','rouge/current_route_itinerary_view.py','rouge/current_stage_objects_view.py','rouge/run_state.py','rouge/app.py','PROJECT_REQUIREMENTS.md']
for n in untouched:assert old(n)==(R/n).read_bytes(),n
assert not subprocess.check_output(['git','diff','--name-only',BASE,'--','rouge/data','research/runtime-reference-loaders-20261031']).strip()
def methods(raw,name):
 c=next(n for n in ast.parse(raw).body if isinstance(n,ast.ClassDef)and n.name==name)
 return {n.name:ast.dump(n,include_attributes=False)for n in c.body if isinstance(n,ast.FunctionDef)}
a=methods(old(changed[0]),'CurrentEnemySpawnsPanel');b=methods((R/changed[0]).read_bytes(),'CurrentEnemySpawnsPanel');assert a.keys()==b.keys()and all(a[n]==b[n]for n in a if n!='follow_position')
for name in ['CurrentTileGrid','CurrentMapPositionPanel','CurrentMapPositionDialog']:assert methods(old(changed[1]),name)==methods((R/changed[1]).read_bytes(),name)
a=methods(old(changed[1]),'CurrentOriginalCenters');b=methods((R/changed[1]).read_bytes(),'CurrentOriginalCenters');assert a.keys()==b.keys()and all(a[n]==b[n]for n in a if n not in ['__init__','set_image'])
suite=read(prefix+'tests/results.json');native=read(prefix+'native/window.json');observed=read(prefix+'native/review-images.json')['observations']
assert suite['passed']and suite['tests_run']==54 and not suite['skipped']and not suite['forbidden_external_calls']
assert native['passed']and native['unique_checks']==43 and not native['source_drift']and not any(native['external_operation_attempts'].values())
assert observed=={'decodes_after_open_selection_refresh_and_resize':1,'current_full_parent_jump_reverse_resolutions':2}
for folder in ['tests','native']:assert read(prefix+folder+'/process.json')['actual_observed_exit']==0
for n in changed:assert native['source_sha256_after'][n]==pin(n)['sha256']
(B/'native/verifier-source.py').write_bytes((R/'scripts/verify_map_jump_review.py').read_bytes())
write(prefix+'source-review.json',{'baseline_commit':BASE,'changed_source':[pin(n)for n in changed],'verified_own_prior_source':[pin(n)for n in baseline],'unchanged_sources_and_requirements':[pin(n)for n in untouched],'all_existing_methods_retained':True,'unchanged_grid_geometry_markers_paint_and_map_panel_methods':True,'changes':'Enemy follow_position delegates once to the existing fresh position_reference gate; same raw PNG bytes reuse the existing decoded QPixmap. Bytearray inputs are retained as immutable bytes. No shared cross-stage cache or source-validation bypass.','verified_comparison':{'four_same_image_set_calls':{'before_decodes':4,'after_decodes':1,'complete_pixels_and_marker_centers_equal':True},'direct_enemy_position_jump':{'before_reverse_resolutions':2,'after_reverse_resolutions':1,'exact_emitted_key_and_complete_enemy_spawn_reference_equal':True}},'native_observations':observed,'performance_limit':'Operation counts, not elapsed-time measurements or full-program/recognition speedup. Parent independently resolves once more, retained.','official_Qt_reference':'https://doc.qt.io/qt-6/qpixmap.html','data_and_runtime_manifest_worktree_unchanged':True,'REA_scope':'Complete Python source reviewed directly per REA skill; previous actual bridge/toolbar REA evidence remains separate; no new REA call or whole-program completion.','application_review_complete':False})
images=[pin(p.relative_to(R))for p in sorted((B/'native').glob('*.png'))];assert len(images)==7
write(prefix+'image-review.json',{'reviewer':'/root','all_seven_native_originals_individually_loaded_with_view_image':images,'scope':'Fixed grid and original PNG side by side, selected/unselected calibrated center, resizing and exact enemy action lookup. No added calibration or complete route drawing; dense reader text, full image mapping and video geometry still incomplete.','whole_video_parity_claimed':False})
live=read(prefix+'live-window/window.json');assert live['passed']and live['private_six_paths_unchanged']
import win32gui,win32process
for w in live['owned_windows']:assert win32gui.IsWindowVisible(w['hwnd'])and win32process.GetWindowThreadProcessId(w['hwnd'])[1]==w['pid']and not ctypes.windll.user32.IsHungAppWindow(w['hwnd'])
a=read('.cache/map-jump-review-live-status.json');time.sleep(2.2);b=read('.cache/map-jump-review-live-status.json');assert b['toolbar_visible']and b['elapsed_since_launch']>a['elapsed_since_launch']
for n in changed:assert live['source_sha256_after'][n]==pin(n)['sha256']
write(prefix+'live-window/desktop-review.json',{'actual_windows_mcp_snapshot_called':True,'actual_image_viewed':True,'region':[1716,1164,2130,1218],'owned_window_visible_and_responding':True,'Qt_timer_advanced':True,'private_six_paths_unchanged_during_startup':True,'private_contents_or_hashes_published':False,'game_operated':False,'chat_sent':False})
title='地图换选复用原图解码，敌人位置跳转去除重复核验'
write(prefix+'summary.json',{'kind':'implementation_review_maintenance','title':title,'baseline_commit':BASE,'completed_sections':440,'functional_section_added':False,'implemented_scope_passed':True,'related_unique_tests':54,'test_receipt':pin(prefix+'tests/results.json'),'native_unique_checks':43,'native_receipt':pin(prefix+'native/window.json'),'source_review':pin(prefix+'source-review.json'),'image_review':pin(prefix+'image-review.json'),'live_window':pin(prefix+'live-window/desktop-review.json'),'application_review_complete':False,'video_parity_complete':False,'P3_complete':False,'P2_complete':False,'P1_complete':False,'full_validation_rerun':False,'full440_only_original_frozen_source':True,'private_data_included':False,'game_operated':False,'chat_sent':False,'publication_binding':'enclosing maintenance commit; ordinary push and actual remote/blob equality required'})
text('research/map-jump-review-20261031/README.md','''# 敌人、出怪与固定地图的读取回顾

有完整Python源码，按REA技能直接审查和实际运行；本轮不新增REA调用，原桥接/工具条REA证据保留。核对敌人反查、直接记录筛选与解析、地图格子、原图标记及其到出怪位置的联动；候选组另查选中与位置解析片段，未将其标成完整语义审查。

敌人页follow_position先执行一次_resolve，而position_reference内部又完整执行resolve_action。现在使用当前选中记录调用原position_reference一次；其完整新鲜来源/内容核对保留，父页独立核对也保留。旧/新实际执行的内部反查次数2→1，发出的精确条目键和完整敌人反查资料一致。实际父子跳转当前共两次反查，不能把内部一次误称全流程一次。来源丢失、被改快照、未选条目均不发送跳转，失效时清理仍在。

CurrentOriginalCenters原先每次换格/刷新都重新解码PNG。现在只在完整图片字节变化时重建现有QPixmap；标记更新和原绘制/缩放公式不变，无跨关卡全局缓存。可变缓冲区按不可变字节保存，以便下次确实比较变化；损坏、缺图或清除时旧像素/标记清空，恢复后重读。[Qt QPixmap官方文档](https://doc.qt.io/qt-6/qpixmap.html)用于核对图片加载和显示接口，不作为地图校准依据。

执行固定自有旧源码和当前组件：四次相同图片更新解码4→1，完整QImage与标记中心均一致；单独验证损坏/缺失/恢复及可变输入。54个不同相关测试覆盖原地图、出怪位置、完整行程和物件界面，43项原生窗口检查实际退出0、无跳过。真实点击格子、列表、敌人到出怪/位置入口、两种尺寸、刷新、来源失效和关闭均核对；七张原图逐张查看。实际应用小窗已更新打开，计时推进，六处私人路径启动保持。

数值、等待参数、地图数据、校准、来源清单和本局均未改变。次数减少不证明端到端耗时提升；代码净增加，不称总体删行。完整路径和原图任意格投影、全套条件/当前敌人面板、视频布局与全程序回顾仍未完成。源数据和已有必要保护不能仅以概率低为由删去；候选/公开资料不能代替本局生成。功能仍440，full440仅原冻结来源，下一全量455。
''')
for n,addition in {
 'PROGRAM_REVIEW.md':'[敌人到固定地图回顾](research/map-jump-review-20261031/README.md)核对直接出怪反查与位置跳转，复用未变原图解码、去掉内部重复核验；新旧像素/中心/精确键与完整资料一致，54项相关测试/43项原生检查通过。父页和来源核对保留；完整路线、任意格投影、窗口生命周期与视频布局仍待审查，不代表全程序完成。',
 'VIDEO_PARITY.md':'[固定地图读取回顾](research/map-jump-review-20261031/README.md)保持原格图与固定原图/已核对标记，换选和刷新复用图片解码，敌人→出怪→地图精确跳转保持。未新增位置校准、整段路径或视频布局；原图未核对的位置仍不标。',
 'IMPLEMENTATION_STRATEGY.md':'[敌人/地图链路回顾](research/map-jump-review-20261031/README.md)直接复用现有Qt图片与现有最终来源核对，删除按钮层重复解析；同字节解码4→1、内部反查2→1为实际工作量对照，不是延迟/全程序提速。未新增全局缓存、界面运行库或数值假设。'
}.items():text(n,(R/n).read_text('utf8')+'\n'+addition+'\n')
n='PROJECT_PROGRESS.md';t=(R/n).read_text('utf8');t=t.replace('其它资料入口的紧凑阅读/重复提示、敌人完整折叠分组和表格','其它资料入口的紧凑阅读/重复提示、重复开启附属资料窗的对象释放、敌人完整折叠分组和表格');text(n,t)
entry=f'''<!-- map-jump-review-20261031:start -->
## 实现回顾维护 · {title}

复用现有QPixmap，只在完整图像字节变化时解码；四次相同更新4→1，完整像素和标记中心一致。敌人位置按钮内部反查2→1，精确键与完整反查结果不变；父页独立核验保留，全父子流程仍两次。未改数值/数据/地图校准/本局，未称端到端或识别提速，净程序代码增加。

54个不同相关测试/43项原生唯一检查通过，实际退出0/无跳过；来源损坏/缺图/恢复、可变缓冲、实际格子/列表点击、准确出怪到地图及关闭分别核对。七张原图逐张查看，实际小窗更新可见响应，启动六处私人路径保持。功能440/未开441，全程序/视频/P3/P2/P1仍未完成；窗口释放、完整路线/位置和其余链路继续审查，识别最后。回执：`{prefix}summary.json`。
<!-- map-jump-review-20261031:end -->

'''
for n in ['WORK_IN_PROGRESS.md','PROJECT_COMPLETED.md']:text(n,entry+(R/n).read_text('utf8'))
cp=read('DEVELOPMENT_CHECKPOINT.json');cp['current_maintenance_save']={'kind':'implementation_review_maintenance','title':title,'receipt':prefix+'summary.json','binding':'enclosing_commit','functional_section_added':False,'status':'partial_program_review_exact_enemy_map_navigation_and_image_reuse','review_checklist':'PROGRAM_REVIEW.md','review_checklist_sha256':pin('PROGRAM_REVIEW.md')['sha256'],'application_review_complete':False};cp['current_batch']['receipt']=prefix+'summary.json';cp['next_action']='继续完整程序回顾：核对重复开启附属资料窗的对象生命周期，不能把关闭隐藏当已释放；其余阅读器、敌人完整折叠/表格/正文和视频几何差异、完整事件/固定战斗资料、招募/强化/异常恢复连续场景与独立机制算例仍保留。已证图片解码复用和内部跳转去重不重复计推进；识别最后。'
text('DEVELOPMENT_CHECKPOINT.json',json.dumps(cp,ensure_ascii=False,indent=2)+'\n');module=runpy.run_path(str(R/'scripts/update_cloud_index.py'));module['update'](R);assert module['validate_delivery'](R,cp)['current_section']==440
from scripts.verify_full_available import maintained_selectors
selectors=maintained_selectors();assert len(selectors)==705 and selectors[-1]=='tests.test_map_jump_review';assert read('CLOUD_INDEX.json')['requirements']['sha256']==pin('PROJECT_REQUIREMENTS.md')['sha256']
write(prefix+'final-audit.json',{'passed':True,'baseline_commit':BASE,'summary':pin(prefix+'summary.json'),'requirements':pin('PROJECT_REQUIREMENTS.md'),'cloud_index':pin('CLOUD_INDEX.json'),'ordered_selectors':705,'related_tests':54,'native_checks':43,'whole_program_complete':False,'whole_video_parity_complete':False,'at_UTC':datetime.now(timezone.utc).isoformat()})
(B/'record-source.py').write_bytes(Path(__file__).read_bytes());archive={p.relative_to(R).as_posix():{k:v for k,v in pin(p.relative_to(R)).items()if k!='path'}for p in sorted(B.rglob('*'))if p.is_file()and p.name!='archive-manifest.json'};write(prefix+'archive-manifest.json',{'kind':'explicit_public_archive','files':archive})
print(json.dumps({'passed':True,'related_tests':54,'native_checks':43,'archive_files':len(archive),'goal_complete':False}))
