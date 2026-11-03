from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import ast,ctypes,difflib,json,runpy,subprocess,sys,time
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts'),str(R/'.cache/305-window-tooldeps')]
BASE='4f956331776d491c7348be1d505bbac62f0f9c56';B=R/'verification/maintenance/enemy-atlas-review-20261031';prefix=B.relative_to(R).as_posix()+'/'
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
changed=['rouge/current_battle_view.py','rouge/player_catalog_grid.py']
untouched=['rouge/current_battle_reference.py','rouge/current_enemy_traits.py','rouge/current_reward_reference.py','rouge/current_settlement_modes_reference.py','rouge/branch_choice.py','rouge/player_inventory.py','rouge/player_parts.py','rouge/player_tools.py','rouge/player_shop_memory.py','rouge/run_state.py','rouge/app.py','PROJECT_REQUIREMENTS.md']
for n in untouched:assert old(n)==(R/n).read_bytes(),n
assert not subprocess.check_output(['git','diff','--name-only',BASE,'--','rouge/data','research/runtime-reference-loaders-20261031']).strip()
def methods(raw,name):
 c=next(n for n in ast.parse(raw).body if isinstance(n,ast.ClassDef)and n.name==name)
 return {n.name:ast.dump(n,include_attributes=False)for n in c.body if isinstance(n,ast.FunctionDef)}
before=methods(old(changed[0]),'CurrentBattlePanel');after=methods((R/changed[0]).read_bytes(),'CurrentBattlePanel')
edited={'__init__','_clear','install_enemy_choices','_enemy_changed'}
assert before.keys()<=after.keys()and all(before[n]==after[n]for n in before if n not in edited)
assert methods(old(changed[1]),'CatalogGrid')==methods((R/changed[1]).read_bytes(),'CatalogGrid')
assert methods(old(changed[1]),'IconTile')['paint']==methods((R/changed[1]).read_bytes(),'IconTile')['paint']
tests=read(prefix+'tests-current/results.json');native=read(prefix+'native-current/window.json')
assert tests['passed']and tests['tests_run']==75 and not tests['skipped']and not tests['forbidden_external_calls']
assert native['passed']and native['unique_checks']==101 and not native['source_drift']and not any(native['external_operation_attempts'].values())
for folder in ['tests-current','native-current']:assert read(prefix+folder+'/process.json')['actual_observed_exit']==0
for n in changed:assert native['source_sha256_after'][n]==pin(n)['sha256']
(B/'native-current/verifier-source.py').write_bytes((R/'scripts/verify_enemy_atlas_review.py').read_bytes())
write(prefix+'source-review.json',{'baseline_commit':BASE,'changed_source':[pin(n)for n in changed],'unchanged_models_state_consumers_and_requirements':[pin(n)for n in untouched],'existing_battle_methods_retained':len(before),'unchanged_existing_methods':sorted(set(before)-edited),'edited_existing_methods':sorted(edited),'new_atlas_methods':sorted(set(after)-set(before)),'original_CatalogGrid_methods_and_IconTile_paint_AST_unchanged':True,'reuse':'Existing CatalogGrid, branch icons, exact identity and original enemy text. Atlas rebuilding reads no image bytes; verified icons are shared, not copied through a new model. Delegate sizeHint now returns existing gridSize.','performance_limit':'No end-to-end latency or recognition speed measurement; no speedup claimed. Production code grows; shared reuse is not net line deletion.','no_numerical_mechanism_or_data_change':True,'data_and_runtime_manifest_worktree_unchanged':True,'REA_scope':'Complete Python source reviewed directly per REA skill; no new REA call, binary reverse engineering or whole-program completion claimed.','official_Qt_references':['https://doc.qt.io/qt-6/qlistwidget.html','https://doc.qt.io/qt-6/qlistview.html'],'application_review_complete':False})
names=['enemy-atlas-overview','enemy-atlas-selected','enemy-atlas-collapsed','enemy-atlas-empty-search','enemy-atlas-width-560','enemy-atlas-width-920','enemy-atlas-restored','shared-inventory-grid','shared-parts-grid']
write(prefix+'image-review.json',{'reviewer':'/root','actual_final_images_individually_loaded_with_view_image':[pin(prefix+'native-current/'+n+'.png')for n in names],'first_pass_images_retained':'Original native79 passed but selected enemy body was too short and delegate used only part of tile width. Actual image review led to side-by-side portrait/body, smaller atlas and shared delegate sizeHint; current101 is a new execution.','retained_base_reader_images_not_all_newly_reviewed':True,'video_basis':'Original 95-second frame re-viewed this turn, pinned in previous scene-reader maintenance. Adds direct candidate pictures and disclosure but not the full Tomimi accordion/table/geometry.','whole_video_parity_claimed':False})
live=read(prefix+'live-window/window.json');assert live['passed']and live['private_six_paths_unchanged']
import win32gui,win32process
for w in live['owned_windows']:assert win32gui.IsWindowVisible(w['hwnd'])and win32process.GetWindowThreadProcessId(w['hwnd'])[1]==w['pid']and not ctypes.windll.user32.IsHungAppWindow(w['hwnd'])
a=read('.cache/enemy-atlas-review-live-status.json');time.sleep(2.2);b=read('.cache/enemy-atlas-review-live-status.json');assert b['toolbar_visible']and b['elapsed_since_launch']>a['elapsed_since_launch']
for n in changed:assert live['source_sha256_after'][n]==pin(n)['sha256']
write(prefix+'live-window/desktop-review.json',{'actual_windows_mcp_snapshot_called':True,'actual_image_viewed':True,'region':[1716,1164,2130,1218],'owned_window_visible_and_responding':True,'Qt_timer_advanced':True,'private_six_paths_unchanged_during_startup':True,'private_contents_or_hashes_published':False,'game_operated':False,'chat_sent':False})
title='复用图标网格直接查看敌人，保留分类与折叠并改善正文空间'
write(prefix+'summary.json',{'kind':'implementation_review_maintenance','title':title,'baseline_commit':BASE,'completed_sections':440,'functional_section_added':False,'implemented_scope_passed':True,'related_unique_tests':75,'test_receipt':pin(prefix+'tests-current/results.json'),'native_unique_checks':101,'native_receipt':pin(prefix+'native-current/window.json'),'earlier_scopes':[pin(prefix+'tests/results.json'),pin(prefix+'native/window.json')],'overlapping_scopes_not_added':True,'source_review':pin(prefix+'source-review.json'),'image_review':pin(prefix+'image-review.json'),'live_window':pin(prefix+'live-window/desktop-review.json'),'application_review_complete':False,'video_parity_complete':False,'P3_complete':False,'P2_complete':False,'P1_complete':False,'full_validation_rerun':False,'full440_only_original_frozen_source':True,'private_data_included':False,'game_operated':False,'chat_sent':False,'publication_binding':'enclosing maintenance commit; ordinary push and actual remote/blob equality required'})
text('research/enemy-atlas-review-20261031/README.md','''# 敌人图册与共享图块回顾

有完整Python源码，按REA技能直接审查和运行，不机械扫描PYC；本轮没有新增REA调用，不表示全程序逆向完成。继续追踪原固定关卡、精确敌人引用、三档分类、原文搜索、出怪/机制资料链路，数据模型和敌人全文保持。

敌人页复用已有CatalogGrid与BranchChoice中已核验的图标，不另建图片目录/模型、不重复读图。按图选择与原下拉选择互相同步，普通、精英、领袖及未确认类别仍是独立分支；搜索、准确资料身份、同名不同引用、空结果、来源失效和恢复分别保留。图册可收起，刷新保留有效选择和收起状态；只有明确选择才显示对应机制，候选条数不冒充实际敌人数。未核验面板仍未知，没有改数值、资料或本局。

首轮真实原生79项虽通过，实际查看图片发现图册加独立头像挤占正文，文字绘制也未用足图块宽度。改为头像在正文旁边并缩小图册高度；复用原网格的gridSize补充委托sizeHint，既有绘制和网格方法不变。[Qt列表接口](https://doc.qt.io/qt-6/qlistwidget.html)与[图标视图](https://doc.qt.io/qt-6/qlistview.html)只作为框架用法依据，不作为游戏机制来源。没有引入网页运行库或复制外部项目代码。

最终75个不同相关测试、101项原生唯一检查实际退出0、无跳过，覆盖原地图/最近资料链路及藏品/零件共享网格；首轮67/79原件保留，重叠不累计。九张新最终原图逐张查看。图册两种窗口宽度、实际图片点击、键盘分支/搜索、折叠及刷新、父窗与子窗关闭、来源丢失/恢复均实测。8个新测试中的同名不同引用用合成隔离记录测试身份不合并，不宣称该合成记录是游戏实遇。

净程序代码增加，不称整体代码精简、识别或端到端提速；只证明图册重建复用现有已核验图标。程序实际测试小窗更新打开，可见响应、计时推进，启动六处私人路径保持。全工程/视频/P3/P2/P1仍未完成，完整手风琴分组、表格、地图/路线预览、尺寸字体与其它入口仍需逐项对照。full440只证明旧冻结来源，本轮维护不增加功能节数。
''')
for n,addition in {
 'PROGRAM_REVIEW.md':'[敌人图册回顾](research/enemy-atlas-review-20261031/README.md)复用已有网格与分类图标，增加直接按图阅读、同步选择和折叠；修正实际截图发现的正文挤压与共享图块宽度。75项相关测试/101项原生检查通过，模型和原文不变，不代表面板准确、完整视频效果或全程序完成。',
 'VIDEO_PARITY.md':'[敌人图册回顾](research/enemy-atlas-review-20261031/README.md)从隐藏在下拉框中的图片改为可直接点击的候选图册，分类/搜索/收起与同源阅读保持；已修正首轮正文空间不足及共享图块文字宽度。它只推进图像化阅读，仍不等于原片完整的折叠分组、表格、难度修正与布局。',
 'IMPLEMENTATION_STRATEGY.md':'[敌人图册回顾](research/enemy-atlas-review-20261031/README.md)优先复用既有CatalogGrid和BranchChoice图标，不另造图片加载/缓存/身份系统。图册重建无新增图片读取；真实耗时未测，不称速度提升。共享委托只补sizeHint，原绘制和网格逻辑保留；已有藏品/零件测试和原生交互覆盖。'
}.items():text(n,(R/n).read_text('utf8')+'\n'+addition+'\n')
n='PROJECT_PROGRESS.md';t=(R/n).read_text('utf8');t=t.replace('其它资料入口的紧凑阅读/重复提示','其它资料入口的紧凑阅读/重复提示、敌人完整折叠分组和表格');text(n,t)
entry=f'''<!-- enemy-atlas-review-20261031:start -->
## 实现回顾维护 · {title}

复用原CatalogGrid/分类图标与精确敌人资料，图片点击与下拉互相同步、三档分类和搜索保持、可展开收起且刷新不重置。模型/原文/本局未改，不冒充实际敌人数或完整面板。首轮图发现正文挤压和图块宽度不足后，改头像正文并排并补共享sizeHint；净代码增加，不称全程序精简或提速。

最终75个不同相关测试/101项原生唯一检查通过，实际退出0/无跳过，保留首轮67/79，交叠不累计；九张新最终原图逐张查看，藏品/零件共享网格也实际点击/缩放核对。原测试小窗更新可见响应，启动六处私人路径保持；功能440/未开441，全程序/视频/P3/P2/P1仍未完成，识别最后。回执：`{prefix}summary.json`。
<!-- enemy-atlas-review-20261031:end -->

'''
for n in ['WORK_IN_PROGRESS.md','PROJECT_COMPLETED.md']:text(n,entry+(R/n).read_text('utf8'))
cp=read('DEVELOPMENT_CHECKPOINT.json');cp['current_maintenance_save']={'kind':'implementation_review_maintenance','title':title,'receipt':prefix+'summary.json','binding':'enclosing_commit','functional_section_added':False,'status':'partial_program_review_enemy_atlas_and_shared_tile_geometry','review_checklist':'PROGRAM_REVIEW.md','review_checklist_sha256':pin('PROGRAM_REVIEW.md')['sha256'],'application_review_complete':False};cp['current_batch']['receipt']=prefix+'summary.json';cp['next_action']='继续完整程序回顾：其它阅读器、敌人完整折叠/表格/正文与视频几何差异、完整事件与固定战斗资料；补齐其余招募/强化/异常恢复连续场景和独立机制算例。敌人候选图册/精确分类选择、地图/最近资料窗共享与关闭清理不重复推进。未核验面板、完整条件及来源适用性仍未知；识别最后。'
text('DEVELOPMENT_CHECKPOINT.json',json.dumps(cp,ensure_ascii=False,indent=2)+'\n');module=runpy.run_path(str(R/'scripts/update_cloud_index.py'));module['update'](R);assert module['validate_delivery'](R,cp)['current_section']==440
from scripts.verify_full_available import maintained_selectors
selectors=maintained_selectors();assert len(selectors)==704 and selectors[-1]=='tests.test_enemy_atlas_review';assert read('CLOUD_INDEX.json')['requirements']['sha256']==pin('PROJECT_REQUIREMENTS.md')['sha256']
write(prefix+'final-audit.json',{'passed':True,'baseline_commit':BASE,'summary':pin(prefix+'summary.json'),'requirements':pin('PROJECT_REQUIREMENTS.md'),'cloud_index':pin('CLOUD_INDEX.json'),'ordered_selectors':704,'related_tests':75,'native_checks':101,'whole_program_complete':False,'whole_video_parity_complete':False,'at_UTC':datetime.now(timezone.utc).isoformat()})
(B/'record-source.py').write_bytes(Path(__file__).read_bytes());archive={p.relative_to(R).as_posix():{k:v for k,v in pin(p.relative_to(R)).items()if k!='path'}for p in sorted(B.rglob('*'))if p.is_file()and p.name!='archive-manifest.json'};write(prefix+'archive-manifest.json',{'kind':'explicit_public_archive','files':archive})
print(json.dumps({'passed':True,'related_tests':75,'native_checks':101,'archive_files':len(archive),'goal_complete':False}))
