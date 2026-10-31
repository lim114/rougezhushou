from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import ast,ctypes,difflib,json,runpy,subprocess,sys,time
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts'),str(R/'.cache/305-window-tooldeps')]
BASE='fc00bba6888a4bdb84a3b6ae36dba1d19896f8bf';B=R/'verification/maintenance/enemy-overview-review-20261031';prefix=B.relative_to(R).as_posix()+'/'
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
changed=['rouge/current_battle_view.py','rouge/enemy_overview.py'];prior='research/enemy-overview-review-20261031/before-current-battle-view.py';assert old(changed[0])==(R/prior).read_bytes()
unchanged=['rouge/current_battle_reference.py','rouge/current_enemy_traits.py','rouge/player_map_reader.py','rouge/player_catalog_grid.py','rouge/run_state.py','rouge/app.py','PROJECT_REQUIREMENTS.md']
for n in unchanged:assert old(n)==(R/n).read_bytes(),n
assert not subprocess.check_output(['git','diff','--name-only',BASE,'--','rouge/data','research/runtime-reference-loaders-20261031']).strip()
def methods(raw,name):
 c=next(n for n in ast.parse(raw).body if isinstance(n,ast.ClassDef)and n.name==name)
 return {n.name:ast.dump(n,include_attributes=False)for n in c.body if isinstance(n,ast.FunctionDef)}
a=methods(old(changed[0]),'CurrentBattlePanel');b=methods((R/changed[0]).read_bytes(),'CurrentBattlePanel');edited={'__init__','_clear','_sync_enemy_grid','_enemy_changed'};assert a.keys()==b.keys()and all(a[n]==b[n]for n in a if n not in edited)
assert methods(old(changed[0]),'CurrentBattleDialog')==methods((R/changed[0]).read_bytes(),'CurrentBattleDialog')
suite=read(prefix+'tests-current/results.json');native=read(prefix+'native-current/window.json');failed=read(prefix+'tests/results.json')
assert suite['passed']and suite['tests_run']==29 and not suite['skipped']and not suite['forbidden_external_calls']
assert native['passed']and native['unique_checks']==48 and not native['source_drift']and not any(native['external_operation_attempts'].values())
assert not failed['passed']and failed['failed']==2 and not failed['errors']
assert not read(prefix+'native/window.json')['passed']
for folder in ['tests-current','native-current']:assert read(prefix+folder+'/process.json')['actual_observed_exit']==0
for folder in ['tests','native']:assert read(prefix+folder+'/process.json')['actual_observed_exit']==1
for n in changed:assert native['source_sha256_after'][n]==pin(n)['sha256']
(B/'native-current/verifier-source.py').write_bytes((R/'scripts/verify_enemy_overview_review.py').read_bytes())
write(prefix+'source-review.json',{'baseline_commit':BASE,'changed_source':[pin(n)for n in changed],'prior_own_source':pin(prior),'unchanged_models_original_grid_factory_state_and_requirements':[pin(n)for n in unchanged],'edited_parent_methods':sorted(edited),'all_other_parent_methods_and_dialog_AST_unchanged':True,'verified_scope':'Three exact stage variants keep full own-prior reference and each complete enemy text. Original source and numeric models unchanged. Additional tests cover branch/search, duplicate names, missing portrait, fold retention and independent source loss.','table_semantics':'Exact reference keys and original verified branch icons reused. Fold by ordinary/elite/boss/unknown; counts are candidate reference rows, not actual spawn counts. Motion/attack/damage declarations reuse existing Chinese maps and scope. At most 180 mechanism characters in table with explicit continuation; full text in tooltip and original reader.','numeric_gap':'No base or video stats inserted. Current final numeric environment still unverified; table is a mechanism overview, not the full predicted-stat table shown in video.','first_failures':'Original regression found added detail-wrapper margins and overview minimum height enlarged narrow layouts enough to remove an existing real scroll range. Fixed zero extra detail margins and ignored overview vertical size hint. New source-recovery test/verifier also wrongly expected enemy tab to stay open; original resets to stage overview. Preserve product reset and explicitly reopen enemy tab in test. Original failed sources/logs retained.','REA_scope':'Complete Python reviewed directly per REA skill; no new REA invocation. Actual older toolbar and bridge analysis kept separate.','performance_claimed':False,'application_review_complete':False})
frames=[pin('.cache/compact-battle-review-video/'+str(n)+'.png')for n in [85,95,108]]
write(prefix+'reference-review.json',{'source':'user supplied local recording; existing extracted originals individually re-viewed in this batch','frames_individually_loaded_with_view_image':frames,'reference_times_seconds':[85,95,108],'observed':'95 and108 show a separate Tomimi webpage with collapsed sections, enemy image overview and multi-column table;85 shows node candidates. These frames do not establish complete app source or complete video parity.','official_widget_reference':'https://doc.qt.io/qt-6/qtreewidget.html','reuse':'Qt shipped QTreeWidget and original local branch/icon/reader models; no external project source copied and no new framework or webview dependency.','full_video_continuously_replayed':False})
images=[pin(p.relative_to(R))for p in sorted((B/'native-current').glob('*.png'))];assert len(images)==8
write(prefix+'image-review.json',{'reviewer':'/root','all_eight_final_originals_individually_loaded_with_view_image':images,'failed_attempt_originals_retained_not_counted_as_final':True,'actual_resize_observations':read(prefix+'native-current/review-images.json')['observations'],'whole_video_parity_claimed':False,'remaining_visual_gap':'Not the complete Tomimi predicted-value table or its entire page; original giant detail paragraphs and remaining layout/geometry still pending.'})
live=read(prefix+'live-window/window.json');assert live['passed']and live['private_six_paths_unchanged']
import win32gui,win32process
for w in live['owned_windows']:assert win32gui.IsWindowVisible(w['hwnd'])and win32process.GetWindowThreadProcessId(w['hwnd'])[1]==w['pid']and not ctypes.windll.user32.IsHungAppWindow(w['hwnd'])
a=read('.cache/enemy-overview-review-live-status.json');time.sleep(2.2);b=read('.cache/enemy-overview-review-live-status.json');assert b['toolbar_visible']and b['elapsed_since_launch']>a['elapsed_since_launch']
for n in changed:assert live['source_sha256_after'][n]==pin(n)['sha256']
write(prefix+'live-window/desktop-review.json',{'actual_windows_mcp_snapshot_called':True,'actual_image_viewed':True,'region':[1716,1164,2130,1218],'owned_window_visible_and_responding':True,'Qt_timer_advanced':True,'private_six_paths_unchanged_during_startup':True,'private_contents_or_hashes_published':False,'game_operated':False,'chat_sent':False})
title='敌人机制支持分组表格总览，折叠与准确阅读同步'
write(prefix+'summary.json',{'kind':'implementation_review_maintenance','title':title,'baseline_commit':BASE,'completed_sections':440,'functional_section_added':False,'implemented_scope_passed':True,'related_unique_tests':29,'native_unique_checks':48,'source_review':pin(prefix+'source-review.json'),'reference_review':pin(prefix+'reference-review.json'),'test_receipt':pin(prefix+'tests-current/results.json'),'native_receipt':pin(prefix+'native-current/window.json'),'first_failed_tests':pin(prefix+'tests/results.json'),'first_failed_native':pin(prefix+'native/window.json'),'image_review':pin(prefix+'image-review.json'),'live_window':pin(prefix+'live-window/desktop-review.json'),'application_review_complete':False,'video_parity_complete':False,'P3_complete':False,'P2_complete':False,'P1_complete':False,'full_validation_rerun':False,'full440_only_original_frozen_source':True,'private_data_included':False,'game_operated':False,'chat_sent':False,'publication_binding':'enclosing maintenance commit; ordinary push and actual remote/blob equality required'})
text('research/enemy-overview-review-20261031/README.md','''# 敌人机制的分组表格总览

重新逐张查看本机原片85/95/108秒的已提取原图；95/108秒是独立Tomimi网页的可折叠内容、敌人图标和多列表格，不是本项目已实现完整预计面板的证明。按照已有资料能力，补可折叠机制总览并保留数值缺口，不照抄录像数字。

复用Qt自带[QTreeWidget](https://doc.qt.io/qt-6/qtreewidget.html)和本地已有模型/头像，未复制外部项目源码、引入浏览器或新框架。未选具体敌人时，原空提示区域显示按普通、精英、领袖和类别未确认分组的三列表格：敌人、行动与攻击声明、机制要点。图鉴声明不是当前阻挡或阶段事实；生命/攻防/法抗的完整预计结果仍待核对，不填白值。组内数量明确是候选资料数，同名不同引用、无图条目独立保留。长机制明确截短，悬停和点选仍有完整原文；选中后进入原来的准确敌人阅读器，不改数值或机制。

父页刷新、分类和搜索复用原准确条目与已核对图标，不另读图片；同源刷新保留折叠/阅读，换来源清旧表。来源恢复仍沿原逻辑回关卡总览，手动再切敌人页，不恢复旧敌人选择。三份准确配置与自有原父类执行对照，完整result及逐敌人全文一致。29项相关测试、48项原生检查真实退出0/无跳过；实际点击、键盘折叠、原文阅读的非零滚动/选区、刷新保持、同名分开、无图/无匹配、来源失效和恢复覆盖。620和920像素请求均为实际窗口宽度，表格可见宽度548/848，不冒充全DPI/跨屏验收。八张最终原图分别实际查看。

首轮原29项测试有两失败：新增包装边距和表格最小高度改变窄窗口布局，导致原回归的滚动范围消失；已修正详情额外边距和隐藏总览的高度约束。另一项新测试及首轮原生误认为资料恢复后仍在敌人页，实际原行为回关卡页；修正验收而保留产品行为。失败源码/日志均保留，未放宽原滚动断言。最终全部相关范围重新执行，未只重跑新测试。

真实项目小窗已更新可见响应、Qt计时推进，启动六处私人路径保持，只公开布尔结果；没有实机采样、游戏操作或聊天。新增一个应用源码，总清点536份，不代表完整审查。代码量增加，本轮不宣称删减、速度或机制精度提升。按REA技能直接审查完整Python源码，没有新REA调用；原实际字节码/桥接REA证据仍保留。

功能仍440/未开441。当前机制表格只推进原片展示的一部分；完整预计数值表、难度环境、其它折叠页面/排版/跨屏、全程序与全视频及P3/P2/P1仍未完成，识别最后。full440只适用于原冻结源码。后续继续核对本局招募/强化连续状态和其它未审链路，避免仅用界面改动代替完整回顾。
''')
n='PROGRAM_REVIEW.md';t=(R/n).read_text('utf8');assert '当前总范围535份'in t;t=t.replace('当前总范围535份','当前总范围536份');t+='\n[敌人分组表格回顾](research/enemy-overview-review-20261031/README.md)在未选敌人时显示可折叠机制对照，复用原准确条目/图标，点击仍读原全文；29项相关测试/48项原生检查通过并修正窄窗高度回归。预计面板、全关资料覆盖、完整视频和全程序仍未完成。\n';text(n,t)
for n,addition in {
 'VIDEO_PARITY.md':'[敌人机制表格回顾](research/enemy-overview-review-20261031/README.md)复核原片95/108秒，在原图册下补按普通/精英/领袖折叠的机制总览表，点选进入完整准确资料，刷新保留折叠；29项相关测试/48项原生检查与八张最终原图覆盖。没有当前完整预计面板或原片完整表格数字，不能称整体一致。',
 'IMPLEMENTATION_STRATEGY.md':'[敌人总览表格回顾](research/enemy-overview-review-20261031/README.md)复用Qt树表格与原branch icons/精确键/机制全文，补折叠与快速对照而不新建模型；原数值未知保持，未复制Tomimi源码或猜许可。修正隐藏页面最小高度影响其它页的实际回归；源码新增不称精简或速度改善。'
}.items():text(n,(R/n).read_text('utf8')+'\n'+addition+'\n')
n='PROJECT_PROGRESS.md';t=(R/n).read_text('utf8');assert '敌人完整折叠分组和表格'in t;text(n,t.replace('敌人完整折叠分组和表格','敌人完整预计数值表、全关资料覆盖和其它折叠布局'))
entry=f'''<!-- enemy-overview-review-20261031:start -->
## 实现回顾维护 · {title}

敌人未选时显示按普通/精英/领袖分组的机制表，复用原准确条目和图标；点选进入完整原文、同源折叠/阅读保持，未知面板不填白值。三配置完整新旧资料及逐敌人全文一致。29项相关测试/48项原生检查真实退出0，保留首轮两测试失败和原生失败，已修正高度回归及新验收的恢复页误判；八张最终原图逐张查看。原片95/108秒仅局部复核，不称完整视频效果。实际小窗更新响应、启动六处私人路径保持。回执：`{prefix}summary.json`。

功能440/未开441，源码清点536份不作完整审查；完整预计数值表、其它资料和全程序/全视频、P3/P2/P1仍未完成，识别最后。
<!-- enemy-overview-review-20261031:end -->

'''
for n in ['WORK_IN_PROGRESS.md','PROJECT_COMPLETED.md']:text(n,entry+(R/n).read_text('utf8'))
cp=read('DEVELOPMENT_CHECKPOINT.json');cp['current_maintenance_save']={'kind':'implementation_review_maintenance','title':title,'receipt':prefix+'summary.json','binding':'enclosing_commit','functional_section_added':False,'status':'partial_program_review_enemy_mechanism_overview','review_checklist':'PROGRAM_REVIEW.md','review_checklist_sha256':pin('PROGRAM_REVIEW.md')['sha256'],'application_review_complete':False};cp['current_batch']['receipt']=prefix+'summary.json';cp['next_action']='继续完整程序回顾：核对同局招募/进阶/定向强化与缺字段/异常恢复连续链路，保持正负证据和仅手动新局；独立机制/预计数值、其它资料窗释放和全片界面/交互仍待验。敌人机制总览已分组表格/折叠，不重复计推进；识别最后。'
text('DEVELOPMENT_CHECKPOINT.json',json.dumps(cp,ensure_ascii=False,indent=2)+'\n');module=runpy.run_path(str(R/'scripts/update_cloud_index.py'));module['update'](R);assert module['validate_delivery'](R,cp)['current_section']==440
from scripts.verify_full_available import maintained_selectors
selectors=maintained_selectors();assert len(selectors)==710 and selectors[-1]=='tests.test_enemy_overview_review';assert read('CLOUD_INDEX.json')['requirements']['sha256']==pin('PROJECT_REQUIREMENTS.md')['sha256']
tracked={p for p in subprocess.check_output(['git','ls-files','rouge']).decode('utf8').splitlines()if p.endswith(('.py','.cjs','.js'))};assert len(tracked|{changed[1]})==536
write(prefix+'final-audit.json',{'passed':True,'baseline_commit':BASE,'summary':pin(prefix+'summary.json'),'requirements':pin('PROJECT_REQUIREMENTS.md'),'cloud_index':pin('CLOUD_INDEX.json'),'ordered_selectors':710,'application_source_files':536,'related_tests':29,'native_checks':48,'whole_program_complete':False,'whole_video_parity_complete':False,'at_UTC':datetime.now(timezone.utc).isoformat()})
(B/'record-source.py').write_bytes(Path(__file__).read_bytes());archive={p.relative_to(R).as_posix():{k:v for k,v in pin(p.relative_to(R)).items()if k!='path'}for p in sorted(B.rglob('*'))if p.is_file()and p.name!='archive-manifest.json'};write(prefix+'archive-manifest.json',{'kind':'explicit_public_archive','files':archive})
print(json.dumps({'passed':True,'related_tests':29,'native_checks':48,'archive_files':len(archive),'goal_complete':False}))
