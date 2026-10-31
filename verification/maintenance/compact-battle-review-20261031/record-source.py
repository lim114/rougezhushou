from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import ast,ctypes,difflib,json,runpy,subprocess,sys,time
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts')]
BASE='56bffce0917787a25846a76788f69704c5ac42ec';B=R/'verification/maintenance/compact-battle-review-20261031';prefix=B.relative_to(R).as_posix()+'/'
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
changed=['rouge/current_battle_view.py','rouge/current_reward_view.py','rouge/current_battle_reference.py','rouge/player_map_reader.py']
def without_notice(raw):
 t=ast.parse(raw);t.body=[n for n in t.body if not(isinstance(n,ast.Assign)and any(isinstance(a,ast.Name)and a.id=='NOTICE'for a in n.targets))];return ast.dump(t,include_attributes=False)
assert without_notice(old(changed[2]))==without_notice((R/changed[2]).read_bytes())
def methods(raw):
 c=next(x for x in ast.parse(raw).body if isinstance(x,ast.ClassDef)and x.name=='CurrentRewardPanel');return {m.name:ast.dump(m,include_attributes=False)for m in c.body if isinstance(m,ast.FunctionDef)and m.name!='__init__'}
assert methods(old(changed[1]))==methods((R/changed[1]).read_bytes())
untouched=['rouge/current_reward_reference.py','rouge/current_settlement_modes_reference.py','rouge/current_settlement_modes_view.py','rouge/run_state.py','rouge/app.py','rouge/branch_choice.py','PROJECT_REQUIREMENTS.md']
for n in untouched:assert old(n)==(R/n).read_bytes()
assert not subprocess.check_output(['git','diff','--name-only',BASE,'--','rouge/data','research/runtime-reference-loaders-20261031']).strip()
suite=read(prefix+'tests-current/results.json');assert suite['passed']and suite['tests_run']==60 and not suite['skipped']and not suite['forbidden_external_calls'];assert read(prefix+'tests-current/process.json')['actual_observed_exit']==0
assert read(prefix+'tests/results.json')['passed']and read(prefix+'integration-current/results.json')['passed']
native=read(prefix+'native-current/window.json');assert native['passed']and native['unique_checks']==52 and not native['source_drift']and not any(native['external_operation_attempts'].values());assert read(prefix+'native-current/process.json')['actual_observed_exit']==0
for n in changed:assert native['source_sha256_after'][n]==pin(n)['sha256']
(B/'native-current/verifier-source.py').write_bytes((R/'scripts/verify_compact_battle_review.py').read_bytes())
ref=read(prefix+'tomimi-reference.json');assert ref['commit']=='5d341e921628dd101004a561ef2d3553ebed1978'and ref['clone_exit']==0 and ref['README_read']and not ref['code_copied_into_product'];assert ref['package_license_field']is None and not ref['license_named_paths']
write(prefix+'source-review.json',{'baseline_commit':BASE,'changed_source':[pin(n)for n in changed],'unchanged_models_state_shared_category_and_requirements':[pin(n)for n in untouched],'current_battle_reference_change_only_NOTICE_assignment':True,'all_existing_reward_update_selection_link_and_failure_method_AST_unchanged':list(methods(old(changed[1]))),'data_and_runtime_manifest_worktree_unchanged':True,'framework_reuse':'Existing Qt stacked widget and tabs; same conditional-reward and settlement reader instances, no new calculation model or web runtime. One parent refresh invokes each original reader once.','primary_sources':['https://doc.qt.io/qt-6/qstackedwidget.html','https://doc.qt.io/qt-6/qtabwidget.html'],'REA_scope':'Python complete source reviewed directly per REA skill. Existing toolbar and bridge REA evidence retained, no artificial PYC scan or new REA execution claimed.','tomimi_reference':pin(prefix+'tomimi-reference.json'),'tomimi_limit':'Only clone, pinned README, package metadata and tracked path inventory read. No dependencies installed, application run, simulator implementation audited, code copied or recording-version identity proved. No explicit reuse license found in this checked scope; public repository is not proof of permission.','application_review_complete':False})
images=[pin(p.relative_to(R))for p in sorted((B/'native-current').glob('*.png'))];assert len(images)==7
write(prefix+'image-review.json',{'reviewer':'/root','final_images':images,'method':'All seven final originals individually loaded with view_image this turn.','first_pass_images_retained':'The first native51 was green but disclosure labels were white on light background; inspecting actual originals led to scoped QCheckBox styling and a native palette check. Current52 is a new real execution.','video_reference':pin(prefix+'video-reference.json'),'fresh_video_frames_individually_viewed':3,'scope':'85/95/108 seconds show node statistics and the external Tomimi stage browser. Confirms video has a separate web information flow, not a proof that the four local Qt categories reproduce that full browser.','whole_video_parity_claimed':False,'remaining':'Remaining dense paragraphs, pixel/size/palette fidelity, other readers, actual complete game/desktop integrations and full versioned data coverage.'})
live=read(prefix+'live-window/window.json');assert live['passed']and live['private_six_paths_unchanged'];assert all(live['source_sha256_after'][n]==pin(n)['sha256']for n in changed)
import win32gui,win32process
for w in live['owned_windows']:assert win32gui.IsWindowVisible(w['hwnd'])and win32process.GetWindowThreadProcessId(w['hwnd'])[1]==w['pid']and not ctypes.windll.user32.IsHungAppWindow(w['hwnd'])
a=read('.cache/compact-battle-review-live-status.json');time.sleep(2.2);b=read('.cache/compact-battle-review-live-status.json');assert b['toolbar_visible']and b['elapsed_since_launch']>a['elapsed_since_launch']
write(prefix+'live-window/desktop-review.json',{'actual_windows_mcp_snapshot_called':True,'actual_image_viewed':True,'region':[1716,1164,2130,1218],'owned_window_visible_and_responding':True,'Qt_timer_advanced':True,'private_six_paths_unchanged_during_startup':True,'private_contents_or_hashes_published':False,'game_operated':False,'chat_sent':False})
title='作战资料收拢为四栏、合并奖励入口并统一刷新'
write(prefix+'summary.json',{'kind':'implementation_review_maintenance','title':title,'baseline_commit':BASE,'completed_sections':440,'functional_section_added':False,'implemented_scope_passed':True,'related_unique_tests':60,'skips':0,'test_receipt':pin(prefix+'tests-current/results.json'),'earlier_scope':[pin(prefix+'tests/results.json'),pin(prefix+'integration-current/results.json')],'test_overlap_not_added':True,'native_unique_checks':52,'native_receipt':pin(prefix+'native-current/window.json'),'source_review':pin(prefix+'source-review.json'),'image_review':pin(prefix+'image-review.json'),'live_window':pin(prefix+'live-window/desktop-review.json'),'scope':'Four top-level categories, two nested reward kinds, one parent refresh, explicit full scope and raw source, retained reading/exact jumps and independent child failures. No new numerical mechanic or complete environment correction.','application_review_complete':False,'video_parity_complete':False,'P3_complete':False,'P2_complete':False,'P1_complete':False,'full_validation_rerun':False,'full440_only_original_frozen_source':True,'private_data_included':False,'game_operated':False,'chat_sent':False,'publication_binding':'enclosing maintenance commit; ordinary push and actual remote/blob equality required'})
text('research/compact-battle-review-20261031/README.md','''# 固定作战阅读整合与视频参考复核

按REA技能直接审查现有完整Python源码；保留既有工具条/桥接的真正REA结果，本轮没有新增REA调用、PYC扫描或全程序完成声明。

六个顶层页签合为地图、敌人、出怪、奖励四栏。奖励内切换“可能获得”和“通关收入”，复用原两个阅读器实例和数据模型，不混合条件奖励、基础经验或实际结算。原始资料移到显式开关，返回时仍在原玩家页；完整范围说明按需展开，数值未知与条件继续写在对应内容中。嵌入模式只留一个父刷新按钮，仍各调用原模型一次；独立奖励页保留其说明和刷新，不破坏其它入口。

复用Qt已有[QStackedWidget](https://doc.qt.io/qt-6/qstackedwidget.html)和[QTabWidget](https://doc.qt.io/qt-6/qtabwidget.html)，没有另造页面/窗口管理系统或引入浏览器依赖。原奖励选择/更新/准确跳转/失效方法AST保持，基础结算与奖励模型原字节保持；战斗模型只将NOTICE中的“待迁移”改为玩家能理解的“尚未完整计入难度、分队和技能影响”，不是补齐计算。原始数据和运行清单均未改变。净代码量增加，不宣称删减行数、识别或全程序提速。

最终60个不同相关测试和原生52项唯一检查通过，0跳过、实际退出0。保留原60/51回执及加强后的实跑，不重复累计。旧结算集成测试只指定曾经的顶层子页却未检查实际可见，现通过两层准确页签打开并增加可见断言，数值/状态原断言保留。第一轮图虽绿，说明开关在浅底上白字仍不可读；实际查看后增加仅限玩家浅色资料窗的复选文字样式及检查。7张最终原图逐张查看；状态、滚动、完整原始数据、精确奖励到配置条目、单独来源失败和父来源失败/恢复分别验证。

本机原片新提取85/95/108秒三帧并逐张查看，原片SHA与固定记录相同，不冒称连续重看全片。95/108秒展示的是Tomimi独立网页资料浏览，不是整个视频助手源码。查到[Tomimi公开仓库](https://github.com/tanch-p/tomimi-dev)，实际无检出部分克隆并固定5d341e921628dd101004a561ef2d3553ebed1978，先读README、package和全跟踪路径清单：Svelte5/SvelteKit2，README描述关卡资料与模拟器。当前所查范围未见明示许可（package无license字段、清单无LICENSE/COPYING命名），尚未读完/运行模拟器、移植代码或核对录像时版本；未安装依赖、复制源码或上传个人数据。下一步可继续核对算法/数据依据和可授权复用边界，不能凭公开可读就称已获复用许可或已接入。

实际测试小窗正常更新打开，可见响应、Qt计时推进，启动六处私人路径保持。功能仍440、未开441，下一全量455；原full440仅原冻结源码。其余阅读器、长说明密度、完整外观/比例/交互、全部数据适用性与全程序回顾仍未完成，识别最后，P3/P2/P1保持未完成。
''')
n='PROGRAM_REVIEW.md';t=(R/n).read_text('utf8');t=t.replace('核对真实玩家资料窗的完整文字和选择保持。 |','核对真实玩家资料窗的完整文字和选择保持，作战资料收拢四栏、奖励整合与统一刷新。 |');t+='\n[固定作战阅读整合](research/compact-battle-review-20261031/README.md)保留两种奖励独立模型与原始数据，统一刷新/可选来源阅读和准确返回；60个不同相关测试、52项原生检查覆盖。另核对Tomimi公开仓库README及许可命名范围，未读完模拟器或复制/运行；不能视为全程序、视频源码或机制校准完成。\n';text(n,t)
n='VIDEO_PARITY.md';t=(R/n).read_text('utf8');t+='\n[作战资料四栏整合](research/compact-battle-review-20261031/README.md)把奖励及通关收入归并，完整范围/原始资料按需查看；选中项、滚动、来源跳转和失败清理保持。新取85/95/108秒画面确认原片包含独立Tomimi网页资料流，本地Qt四栏只推进阅读整合，不能冒称该网页或整套原片已一致。Tomimi当前公开仓库已固定提交做元数据核验，复用许可/模拟器/录像版本仍待核对，未复制或接通。\n';text(n,t)
n='IMPLEMENTATION_STRATEGY.md';t=(R/n).read_text('utf8');t+='\n## 本次明确的新参考来源\n\n原片95/108秒显示Tomimi独立网页资料。已实际克隆并先读[公开仓库](https://github.com/tanch-p/tomimi-dev/tree/5d341e921628dd101004a561ef2d3553ebed1978)README和包/路径元数据；尚未核验源码复用许可，也未阅读完整模拟器、安装运行或移植。它可能提供关卡排版/模拟架构的研究线索，但不等于整个视频助手源码、录像部署版本或游戏引擎的机制证据。继续保持Qt主程序和独立数据来源；若后续取得明确许可和兼容性/离线隐私依据，再比较局部复用的总成本，不因发现仓库立即换框架。详见本批[研究记录](research/compact-battle-review-20261031/README.md)。\n';text(n,t)
n='PROJECT_PROGRESS.md';t=(R/n).read_text('utf8');t=t.replace('核对其它资料入口的紧凑阅读/重复提示、固定作战完整数据','核对其它资料入口的紧凑阅读/重复提示、Tomimi参考项目的许可/离线适配与时钟证据、固定作战完整数据');text(n,t)
entry=f'''<!-- compact-battle-review-20261031:start -->
## 实现回顾维护 · {title}

四主栏目，奖励内切换可能获得/通关收入，原始资料与完整说明显式打开；嵌入模式统一父刷新，独立页保留控制。Qt原组件及两类奖励模型复用，战斗模型只修改玩家说明措辞，计算/原数据不变；同源阅读、精确跳转及子/父来源失效分别保持。

最终60个不同相关测试、52项原生检查通过，实际退出0/无跳过，原60/51及加强集成可见断言的回执保留、重叠不累计。首轮绿色图的浅色白字问题已修正，7张最终图逐张查看；原片新取三帧确认Tomimi网页流程。Tomimi公开仓库已固定提交先读README/包及路径，未核验复用许可、完整模拟器/录像版本，未复制/运行或接入。实际测试小窗更新可见响应，启动六处私人路径保持。功能440/未开441；完整回顾/视频及P3/P2/P1未完成，识别最后。回执：`{prefix}summary.json`。
<!-- compact-battle-review-20261031:end -->

'''
for n in ['WORK_IN_PROGRESS.md','PROJECT_COMPLETED.md']:text(n,entry+(R/n).read_text('utf8'))
cp=read('DEVELOPMENT_CHECKPOINT.json');cp['current_maintenance_save']={'kind':'implementation_review_maintenance','title':title,'receipt':prefix+'summary.json','binding':'enclosing_commit','functional_section_added':False,'status':'partial_program_review_four_battle_categories_and_shared_rewards','review_checklist':'PROGRAM_REVIEW.md','review_checklist_sha256':pin('PROGRAM_REVIEW.md')['sha256'],'application_review_complete':False};cp['current_batch']['receipt']=prefix+'summary.json';cp['next_action']='继续完整程序回顾：其它事件/资料阅读器与长说明密度、视频外观比例和交互；核对固定Tomimi参考项目许可、模拟器/离线适配及独立机制证据，不能把公开源码当录像版本或游戏引擎事实。作战四栏/奖励整合和统一刷新已完成，不重复推进；其余招募/强化连续状态和独立数值算例保留，识别最后。'
text('DEVELOPMENT_CHECKPOINT.json',json.dumps(cp,ensure_ascii=False,indent=2)+'\n');module=runpy.run_path(str(R/'scripts/update_cloud_index.py'));module['update'](R);assert module['validate_delivery'](R,cp)['current_section']==440
from scripts.verify_full_available import maintained_selectors
selectors=maintained_selectors();assert len(selectors)==702 and selectors[-1]=='tests.test_compact_battle_review';assert read('CLOUD_INDEX.json')['requirements']['sha256']==pin('PROJECT_REQUIREMENTS.md')['sha256']
write(prefix+'final-audit.json',{'passed':True,'baseline_commit':BASE,'summary':pin(prefix+'summary.json'),'requirements':pin('PROJECT_REQUIREMENTS.md'),'cloud_index':pin('CLOUD_INDEX.json'),'ordered_selectors':702,'unique_related_tests':60,'native_unique_checks':52,'whole_program_complete':False,'whole_video_parity_complete':False,'at_UTC':datetime.now(timezone.utc).isoformat()})
(B/'record-source.py').write_bytes(Path(__file__).read_bytes());archive={p.relative_to(R).as_posix():{k:v for k,v in pin(p.relative_to(R)).items()if k!='path'}for p in sorted(B.rglob('*'))if p.is_file()and p.name!='archive-manifest.json'};write(prefix+'archive-manifest.json',{'kind':'explicit_public_archive','files':archive});print(json.dumps({'passed':True,'unique_tests':60,'native_checks':52,'archive_files':len(archive),'goal_complete':False}))
