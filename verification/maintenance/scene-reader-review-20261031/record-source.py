from pathlib import Path
from hashlib import sha256
from datetime import datetime, timezone
import ctypes, difflib, json, runpy, subprocess, sys, time

R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts'),str(R/'.cache/305-window-tooldeps')]
BASE='c1c4231424d6ec0dd3f6a5657c922fd4d0e2b047'
B=R/'verification/maintenance/scene-reader-review-20261031';prefix=B.relative_to(R).as_posix()+'/'
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
changed=['rouge/player_map_reader.py','rouge/player_recent_scene.py','rouge/player_scene_battle.py']
unchanged=['rouge/current_battle_reference.py','rouge/current_reward_reference.py','rouge/current_settlement_modes_reference.py','rouge/current_battle_view.py','rouge/current_reward_view.py','rouge/run_state.py','rouge/app.py','rouge/current_event_directory_view.py','PROJECT_REQUIREMENTS.md']
for n in unchanged:assert old(n)==(R/n).read_bytes(),n
assert not subprocess.check_output(['git','diff','--name-only',BASE,'--','rouge/data','research/runtime-reference-loaders-20261031']).strip()
baseline='research/scene-reader-review-20261031/before-player-map-reader.py'
assert old(changed[0])==(R/baseline).read_bytes()
suite=read(prefix+'tests-current/results.json');assert suite['passed']and suite['tests_run']==60 and not suite['skipped']and not suite['forbidden_external_calls']
assert read(prefix+'tests-current/process.json')['actual_observed_exit']==0
red=read(prefix+'close-before/results.json');assert red['failed']==1 and red['tests_run']==1 and read(prefix+'close-before/process.json')['actual_observed_exit']==1
native=[]
for folder in ['native','retained-compact-native']:
 v=read(prefix+folder+'/window.json');assert v['passed']and v['unique_checks']==52 and not v['source_drift']and not any(v['external_operation_attempts'].values())
 assert read(prefix+folder+'/process.json')['actual_observed_exit']==0
 for n in changed:assert v['source_sha256_after'][n]==pin(n)['sha256'],n
 (B/folder/'verifier-source.py').write_bytes((R/('scripts/verify_scene_reader_review.py'if folder=='native'else 'scripts/verify_compact_battle_review.py')).read_bytes())
 native.append(pin(prefix+folder+'/window.json'))
subset=read('.cache/tomimi-reference-subset-20261031/subset.json')
assert subset['commit']=='5d341e921628dd101004a561ef2d3553ebed1978'and len(subset['files'])==5 and not subset['code_copied_into_product']
subset['review_scope']='Targeted excerpts of five selected source files, not a complete semantic review of these files or the simulator. Source retained only in ignored local cache.'
subset['source_files_in_public_archive']=False
subset['observed_architecture']='Svelte/Three.js simulator, separate wave/fragment/action clocks and configurable offline runtime; Simulator.ts uses a 1/60 step. This is simulator implementation, not proof of the game engine clock or complete event scripts.'
subset['reuse_decision']='No source copied; no explicit reuse permission found in checked README/package/path and selected-file scope. Do not port the whole runtime before permission, dependencies, privacy and output fidelity are established.'
write(prefix+'tomimi-subset-review.json',subset)
ref=read('verification/maintenance/compact-battle-review-20261031/video-reference.json')
frame=R/'.cache/compact-battle-review-video/95.png';assert sha256(frame.read_bytes()).hexdigest()==ref['frames'][1]['frame_sha256']
import cv2,numpy as np
im=cv2.imdecode(np.frombuffer(frame.read_bytes(),np.uint8),cv2.IMREAD_COLOR)
points=[(430,320),(430,450),(1400,300)];rgb=[im[y,x][::-1].tolist()for x,y in points];assert rgb==[[38,37,40]]*3
write(prefix+'video-reference.json',{'source_video_sha256':ref['source_video_sha256'],'source_video_bytes':ref['source_video_bytes'],'actual_frame_viewed':95,'frame_sha256':sha256(frame.read_bytes()).hexdigest(),'sample_xy':points,'actual_RGB':rgb,'shared_reference_canvas':'#262528','scope':'One re-viewed original-video frame, external Tomimi stage browser, not the complete Tab appearance or full continuous video replay.','full_video_rewatched':False})
write(prefix+'source-review.json',{'baseline_commit':BASE,'changed_source':[pin(n)for n in changed],'unchanged_models_state_event_factory_and_requirements':[pin(n)for n in unchanged],'prior_own_factory':pin(baseline),'data_and_runtime_manifest_worktree_unchanged':True,'measured_factory_calls':{'old':2,'new':1,'stage_ids':['ro6_n_1_2','ro6_n_2_6','ro6_b_7'],'full_battle_reward_settlement_packets_equal':True,'not_end_to_end_timing':True},'actual_cleanup_failure':'Owner close left spawn candidate child visible. Original red test exits1; same test and necessary suites pass after connecting existing panel cleanup to shared dialog finished.','reuse':'Existing ToolPopover, CurrentBattlePanel cleanup and shared Qt stylesheet. No new UI runtime or numerical model.','REA_scope':'Complete Python source reviewed directly according to REA skill; previous actual toolbar/bridge REA evidence retained. No new REA call or whole-program review claimed.','application_review_complete':False})
images=[pin(p.relative_to(R))for p in sorted((B/'native').glob('*.png'))];assert len(images)==6
write(prefix+'image-review.json',{'reviewer':'/root','actual_final_images_individually_loaded_with_view_image':images,'retained_compact_scope_images_not_newly_individually_reviewed':True,'actual_video_frame_reviewed':pin(prefix+'video-reference.json'),'remaining_visual_gaps':'Large text regions, density, typography, accordions, tables, exact geometry and other windows remain different from the video. Canvas color/shared reader only; whole-video parity is not achieved.','whole_video_parity_claimed':False})
live=read(prefix+'live-window/window.json');assert live['passed']and live['private_six_paths_unchanged']
import win32gui,win32process
for w in live['owned_windows']:assert win32gui.IsWindowVisible(w['hwnd'])and win32process.GetWindowThreadProcessId(w['hwnd'])[1]==w['pid']and not ctypes.windll.user32.IsHungAppWindow(w['hwnd'])
a=read('.cache/scene-reader-review-live-status.json');time.sleep(2.2);b=read('.cache/scene-reader-review-live-status.json');assert b['toolbar_visible']and b['elapsed_since_launch']>a['elapsed_since_launch']
for n in changed:assert live['source_sha256_after'][n]==pin(n)['sha256']
write(prefix+'live-window/desktop-review.json',{'actual_windows_mcp_snapshot_called':True,'actual_image_viewed':True,'region':[1716,1164,2130,1218],'owned_window_visible_and_responding':True,'Qt_timer_advanced':True,'private_six_paths_unchanged_during_startup':True,'private_contents_or_hashes_published':False,'game_operated':False,'chat_sent':False})
title='地图与最近场景复用深色资料窗，减少重复读取并修复遗留子窗'
write(prefix+'summary.json',{'kind':'implementation_review_maintenance','title':title,'baseline_commit':BASE,'completed_sections':440,'functional_section_added':False,'implemented_scope_passed':True,'related_unique_tests':60,'test_receipt':pin(prefix+'tests-current/results.json'),'original_close_failure':pin(prefix+'close-before/results.json'),'native_scopes':native,'native_unique_checks_per_scope':[52,52],'overlapping_scopes_not_added':True,'source_review':pin(prefix+'source-review.json'),'image_review':pin(prefix+'image-review.json'),'live_window':pin(prefix+'live-window/desktop-review.json'),'tomimi_selected_excerpts':pin(prefix+'tomimi-subset-review.json'),'application_review_complete':False,'video_parity_complete':False,'P3_complete':False,'P2_complete':False,'P1_complete':False,'full_validation_rerun':False,'full440_only_original_frozen_source':True,'private_data_included':False,'game_operated':False,'chat_sent':False,'publication_binding':'enclosing maintenance commit; ordinary push and actual remote/blob equality required'})
text('research/scene-reader-review-20261031/README.md','''# 地图和最近场景的共享资料窗口回顾

按REA技能审查完整Python源码及实际原生交互，既有工具条/桥接REA证据仍保留；本轮无新REA调用，不把局部审查称为全程序逆向完成。

地图、最近作战共用原ToolPopover与CurrentBattlePanel；最近事件复用同一资料窗样式和原精确事件工厂。固定作战入口原先预读关卡，构造面板时又读一次，现在只由面板校验来源；保留失败返回和无效面板清理。三个固定配置ro6_n_1_2、ro6_n_2_6、ro6_b_7完整作战/奖励/结算资料元组新旧相等，实际模型调用2→1；这不是识别或全程序延迟提升的证据。

实际复现关闭父窗后“出怪候选”子窗仍可见，原失败用例真实退出1。连接已有面板清理至共享窗口finished后，真实关闭按钮同时关闭子窗；重新打开复用原窗，刷新基础资料并保留有效奖励/来源选择。切换精确配置、来源丢失和恢复仍按原流程处理，未改本局、账号、机制、数据或事件工厂。

重新查看原片95秒画面（Tomimi独立网页），三个实际像素均为RGB(38,37,40)。共享资料窗背景改为#262528并配亮色文字；原片的全部折叠结构、表格、比例与其它界面尚未复现，不能把颜色一致当整体一致。旧浅色记录仅属历史。

60个不同相关测试、两份各52项原生检查实际退出0，无真实游戏/聊天/服务商调用，交叠范围不累计；新原生六张最终原图逐张查看。原项目测试小窗正常更新打开，计时推进，启动六处私人路径保持。full440仍只证明旧冻结来源，功能节仍440、未开441。

## 公开实现的适配判断

继续查阅固定[Tomimi源码](https://github.com/tanch-p/tomimi-dev/tree/5d341e921628dd101004a561ef2d3553ebed1978)的SpawnManager、StageRuntime、Simulator、EnemyWaves和waveHelpers五份选定文件片段。依赖Svelte/Three.js和独立资源/设置；波次、组与条目分时处理，离线模拟器步长1/60秒是其实现选择，不能证明游戏引擎或未公开触发脚本。只查阅片段，尚未逐行完整审查或安装/运行。

已查README/package/命名清单及选定文件中未发现明示复用许可，不代表已完整审核全仓库许可。源码只留忽略的本机缓存，本仓库仅保存自有旧工厂与研究元数据，没有复制外部代码。当前没有证据支持整体迁移比复用现有Qt和本地资料更省成本；这是工程判断，不是基准结论。继续核对可授权的局部复用和独立机制依据，不以该模拟器输出替代游戏事实。
''')
n='PROGRAM_REVIEW.md';t=(R/n).read_text('utf8');t+='\n[共享场景资料窗回顾](research/scene-reader-review-20261031/README.md)复用地图/最近场景窗口与深色样式，消除重复关卡读取，并修复实际父窗关闭遗留子窗。三配置完整资料保持、60个相关测试和两组各52项原生范围通过，不累计重叠；Tomimi五文件仅片段审查、未复制/运行。全程序、完整机制和视频效果仍未完成。\n';text(n,t)
n='VIDEO_PARITY.md';t=(R/n).read_text('utf8');t+='\n[共享场景资料窗](research/scene-reader-review-20261031/README.md)按原片95秒Tomimi资料页实际像素统一深色背景和亮色文字，地图/最近作战及事件复用相同样式。之前浅色修正保留为历史，不能代表当前目标。密集长文、折叠结构、表格、字体、几何和其它窗口仍有差异，完整一致仍未完成。\n';text(n,t)
n='IMPLEMENTATION_STRATEGY.md';t=(R/n).read_text('utf8');t+='\n[本轮共享资料窗研究](research/scene-reader-review-20261031/README.md)采用已有Qt组件消除两入口重复创建，复用原清理流程；模型调用2→1不等于端到端速度改善。Tomimi固定提交五份文件片段说明其Svelte/Three.js离线模拟依赖，1/60步长不能作为游戏机制证据；许可、完整运行和实际兼容未核验，未复制源码，不以全量换框架为默认方案。\n';text(n,t)
n='PROJECT_PROGRESS.md';t=(R/n).read_text('utf8');t=t.replace('Tomimi参考项目的许可/离线适配与时钟证据','Tomimi参考项目的明确许可、完整离线依赖与独立时钟证据');text(n,t)
entry=f'''<!-- scene-reader-review-20261031:start -->
## 实现回顾维护 · {title}

复用原Qt资料窗、精确来源与清理；三配置完整资料结果不变、关卡模型读取2→1，不称全程序或识别提速。实际复现父窗关闭后子窗遗留并修复，重开仍保留有效选择/恢复基础资料。按原片95秒像素统一深色画布，完整折叠结构/排版/尺寸与视频仍不同。Tomimi五份文件仅片段阅读，未核验明确复用许可、完整模拟或游戏时钟，未复制/运行。

60个不同相关测试、两份各52项原生范围通过且真实退出0，重叠不相加；初轮遗留子窗失败原件保留。六张新原图逐张查看，原项目测试窗更新可见响应，六处私人路径启动保持。功能440/未开441；全程序回顾/视频及P3/P2/P1仍未完成，识别最后。回执：`{prefix}summary.json`。
<!-- scene-reader-review-20261031:end -->

'''
for n in ['WORK_IN_PROGRESS.md','PROJECT_COMPLETED.md']:text(n,entry+(R/n).read_text('utf8'))
cp=read('DEVELOPMENT_CHECKPOINT.json');cp['current_maintenance_save']={'kind':'implementation_review_maintenance','title':title,'receipt':prefix+'summary.json','binding':'enclosing_commit','functional_section_added':False,'status':'partial_program_review_shared_scene_readers','review_checklist':'PROGRAM_REVIEW.md','review_checklist_sha256':pin('PROGRAM_REVIEW.md')['sha256'],'application_review_complete':False};cp['current_batch']['receipt']=prefix+'summary.json';cp['next_action']='继续完整程序回顾：其它阅读器、密集文字与视频折叠/表格/窗口尺寸差异、完整事件与固定战斗资料；补齐其余招募/强化/异常恢复连续场景和独立机制算例。共享地图/最近场景资料窗及已复现关闭清理已完成，不重复计推进；Tomimi仅选定片段审查，明确复用许可/完整运行/游戏时钟未证，不复制或以其模拟输出冒充游戏事实；识别最后。'
text('DEVELOPMENT_CHECKPOINT.json',json.dumps(cp,ensure_ascii=False,indent=2)+'\n')
module=runpy.run_path(str(R/'scripts/update_cloud_index.py'));module['update'](R);assert module['validate_delivery'](R,cp)['current_section']==440
from scripts.verify_full_available import maintained_selectors
selectors=maintained_selectors();assert len(selectors)==703 and selectors[-1]=='tests.test_scene_reader_review'
assert read('CLOUD_INDEX.json')['requirements']['sha256']==pin('PROJECT_REQUIREMENTS.md')['sha256']
write(prefix+'final-audit.json',{'passed':True,'baseline_commit':BASE,'summary':pin(prefix+'summary.json'),'requirements':pin('PROJECT_REQUIREMENTS.md'),'cloud_index':pin('CLOUD_INDEX.json'),'ordered_selectors':703,'related_tests':60,'native_checks_per_scope':[52,52],'whole_program_complete':False,'whole_video_parity_complete':False,'at_UTC':datetime.now(timezone.utc).isoformat()})
(B/'record-source.py').write_bytes(Path(__file__).read_bytes())
archive={p.relative_to(R).as_posix():{k:v for k,v in pin(p.relative_to(R)).items()if k!='path'}for p in sorted(B.rglob('*'))if p.is_file()and p.name!='archive-manifest.json'}
write(prefix+'archive-manifest.json',{'kind':'explicit_public_archive','files':archive})
print(json.dumps({'passed':True,'related_tests':60,'native_checks_per_scope':[52,52],'archive_files':len(archive),'goal_complete':False}))
