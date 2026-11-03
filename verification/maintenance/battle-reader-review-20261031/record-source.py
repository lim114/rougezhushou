from pathlib import Path
from hashlib import sha256
from statistics import median
from datetime import datetime,timezone
import json,sys,subprocess,difflib,runpy,re,time,ctypes,win32gui,win32process

R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts')];base=R/'verification/maintenance/battle-reader-review-20261031'
baseline='b5ce07b802f51d42095f10fb12ce261b08dbd2f1'
def read(n):return json.loads((R/n).read_bytes())
def pin(n):
    p=R/n;v=p.read_bytes();return {'path':p.relative_to(R).as_posix(),'sha256':sha256(v).hexdigest(),'bytes':len(v)}
def write(n,v):(R/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf8')
def text(n,v):
    p=R/n
    if not p.exists():p.write_text(v,'utf8');return
    old=p.read_bytes().decode('utf8').splitlines(keepends=True);new=v.splitlines(keepends=True);out=list(new)
    # Retain original per-line endings; avoid unrelated whole-checkpoint churn.
    for a,b,num in difflib.SequenceMatcher(None,[s.rstrip('\r\n')for s in old],[s.rstrip('\r\n')for s in new],autojunk=False).get_matching_blocks():
        for i in range(num):out[b+i]=old[a+i]
    p.write_bytes(''.join(out).encode('utf8'))

changed=['rouge/current_battle_view.py','rouge/current_reward_view.py','rouge/current_settlement_modes_view.py','rouge/expansion_view.py','rouge/reference_image.py']
assert subprocess.check_output(['git','rev-parse','HEAD']).decode().strip()==baseline
assert set(subprocess.check_output(['git','diff','--name-only','--','rouge']).decode().splitlines())==set(changed[:-1])
prior=read('verification/maintenance/battle-reader-review-20261031/replay/processes.json')
current=read('verification/maintenance/battle-reader-review-20261031/replay/current-processes.json')
assert len(prior)==6 and len(current)==3 and all(x['actual_observed_exit']==0 for x in prior+current)
rows=[read('verification/maintenance/battle-reader-review-20261031/replay/'+n+'.json')for n in ['before-1','before-2','before-3','after-current-1','after-current-2','after-current-3']]
assert all(len(v['rows'])==18 and v['qpa']=='windows' for v in rows)
for key in ('all_data_and_text_sha256','expansion_data_and_text_sha256'):assert len({v[key]for v in rows})==1
for v in rows:
    for name,h in v['source_sha256'].items():
        raw=subprocess.check_output(['git','show',baseline+':'+name])if v['mode']=='before'else(R/name).read_bytes()
        assert sha256(raw).hexdigest()==h
    for counts in v['work_counts'].values():assert set(counts.values())==({2}if v['mode']=='before'else{1})
measures={sid:{mode:{action:median(m['ms']for row in rows if row['mode']==mode for m in row['measurements']if m['stage_id']==sid and m['action']==action)for action in ('construct','filtered_refresh')}for mode in ('before','after')}for sid in ('ro6_n_5_2','ro6_b_7')}
initial=read('verification/maintenance/battle-reader-review-20261031/tests/results.json');final=read('verification/maintenance/battle-reader-review-20261031/tests-final/results.json')
assert initial['passed'] and initial['tests_run']==60 and final['passed'] and final['tests_run']==6
ids=[]
for folder in ('tests','tests-final'):
    assert read(f'verification/maintenance/battle-reader-review-20261031/{folder}/process.json')['actual_observed_exit']==0
    ids.append(set(re.findall(r'^test_\w+ \(([^)]+)\)',(base/folder/'stderr.txt').read_text('utf8'),re.M)))
assert len(ids[0])==60 and len(ids[1])==6 and len(ids[0]|ids[1])==61 and len(ids[0]&ids[1])==5
cleanup=read('verification/maintenance/battle-reader-review-20261031/cleanup-extraction.json')
assert cleanup['panel_cleanup_AST_equal_to_original_ordered_calls'] and cleanup['dialog_cleanup_AST_equal_after_self_panel_normalization'] and cleanup['new_source_sha256']==pin('rouge/current_battle_view.py')['sha256']
write('verification/maintenance/battle-reader-review-20261031/tests-reconciled.json',{'unique_available_passed':61,'initial_passed':60,'final_focused_passed':6,'overlap':5,
    'initial_ids':sorted(ids[0]),'final_ids':sorted(ids[1]),'unrepeated_55_checks':'Reused after exact ordered cleanup extraction; original sources, actual exits and logs retained.',
    'extraction':pin('verification/maintenance/battle-reader-review-20261031/cleanup-extraction.json'), 'failed':0,'errors':0,'unavailable_in_this_selected_scope':0})
native=read('verification/maintenance/battle-reader-review-20261031/native-current/window.json')
assert native['passed'] and native['unique_checks']==50 and not any(native['external_operation_attempts'].values())
assert read('verification/maintenance/battle-reader-review-20261031/native-current/process.json')['actual_observed_exit']==0
assert all(native['source_sha256_after'][n]==pin(n)['sha256']for n in changed)
assert read('verification/maintenance/battle-reader-review-20261031/native/process.json')['actual_observed_exit']==1
assert read('verification/maintenance/battle-reader-review-20261031/native-final/process.json')['actual_observed_exit']==0
images=[]
for p in sorted((base/'native-current').glob('*.png')):
    old=base/'native-final'/p.name
    assert p.read_bytes()==old.read_bytes()
    images.append({'current':pin(p.relative_to(R)),'reviewed_original':pin(old.relative_to(R)),'method':'exact whole-byte reuse of image actually loaded with view_image by /root this turn'})
assert len(images)==7
write('verification/maintenance/battle-reader-review-20261031/image-review.json',{'reviewer':'/root','final_images':images,
    'initial_failed_fixture_images_also_individually_viewed':['native/battle-680.png','native/battle-1120.png','native/enemy.png','native/action.png'],
    'reference_frames_actually_viewed':['.cache/reference-local-video-385/timeline/frame-026.jpg','.cache/reference-local-video-385/timeline/frame-027.jpg','.cache/reference-local-video-385/timeline/frame-028.jpg','.cache/reference-local-video-385/timeline/frame-029.jpg'],
    'reference_scope':'Node-card interaction frames, not a complete fixed-battle design specification; no new continuous whole-video playback or video parity claim.'})
write('verification/maintenance/battle-reader-review-20261031/fixture-correction.json',{'original_failure':'native/window.json',
    'reason':'The isolated directory default filtered to changed entries, while the exact map fixture was an unchanged stage. Explicitly selected all entries in the test before locating its ID.',
    'product_filters_or_source_validation_weakened':False,'original_failure_retained':True,'final_current_scope':'native-current/window.json'})
live=read('verification/maintenance/battle-reader-review-20261031/live-window-final/window.json')
assert live['passed'] and live['private_six_paths_unchanged'] and all(live['source_sha256_after'][n]==pin(n)['sha256']for n in changed)
for w in live['owned_windows']:assert win32gui.IsWindowVisible(w['hwnd']) and win32process.GetWindowThreadProcessId(w['hwnd'])[1]==w['pid'] and not ctypes.windll.user32.IsHungAppWindow(w['hwnd'])
a=read('.cache/runtime-battle-final-live-status.json');time.sleep(2.2);b=read('.cache/runtime-battle-final-live-status.json')
assert b['toolbar_visible'] and b['elapsed_since_launch']>a['elapsed_since_launch']
write('verification/maintenance/battle-reader-review-20261031/live-window-final/desktop-review.json',{'actor':'/root','actual_windows_mcp_snapshot_called':True,'image_actually_viewed':True,
    'region':[1716,1164,2130,1218],'actual_Qt_timer_advanced':True,'owned_window_visible_and_responding':True,
    'private_six_paths_unchanged_during_startup':True,'private_contents_or_hashes_published':False,'game_operated':False,'chat_sent':False})
from scripts.verify_full_available import maintained_selectors
old=read('verification/sections/440-source-audit.json')['current_selectors']
assert maintained_selectors()==old+['tests.test_player_popover_refresh','tests.test_desktop_receipts','tests.test_catalog_refresh_review','tests.test_state_calculation_updates','tests.test_player_resource_strip','tests.test_battle_reader_review']
assert len(maintained_selectors())==693
additional=['rouge/current_battle_reference.py','rouge/current_reward_reference.py','rouge/current_settlement_modes_reference.py','rouge/current_settlement_view.py',
    'rouge/player_scene_battle.py','rouge/player_recent_scene.py','rouge/branch_choice.py','rouge/battle_entry_reference_view.py','rouge/battle_view.py']
for name in additional:assert subprocess.check_output(['git','show',baseline+':'+name])==(R/name).read_bytes()
write('verification/maintenance/battle-reader-review-20261031/review-source.json',{'baseline_commit':baseline,'changed_source':[pin(n)for n in changed],
    'additional_source_reviewed':[pin(n)for n in additional],
    'review_scope':'Battle construction, image presentation, exact enemy/action selection, reward and settlement initialization, source loss/restoration, and reader ownership/cleanup; additional large modules are selected-path reviews, not all mechanics validated.',
    'REA_scope':'Existing toolbar and bridge REA evidence retained; current complete Python source and controlled runtime reviewed directly according to REA skill. No new REA session or generated PYC coverage claim.',
    'raw_source_documents_and_numeric_mechanics_unchanged':True,'whole_program_review_complete':False})
summary={'kind':'implementation_maintenance','title':'固定作战资料重复读取、地图图片与窗口清理复用','baseline_commit':baseline,
    'completed_sections':440,'functional_section_added':False,'next_section_started':False,'implemented_scope_passed':True,
    'application_review_complete':False,'video_parity_complete':False,
    'source_review':pin('verification/maintenance/battle-reader-review-20261031/review-source.json'),
    'replay_current_processes':pin('verification/maintenance/battle-reader-review-20261031/replay/current-processes.json'),
    'before_after_current_processes':6,'fixed_stages_per_process':2,'actions_per_process':18,'complete_results_and_reports_equal':True,
    'construction_reward_and_settlement_reads':{'before_each':2,'after_each':1},'filtered_refresh_and_navigation_rebuilds':{'before_each':2,'after_each':1},
    'median_local_ms':measures,'timing_scope':'Three before and three current-after independent Windows Qt processes, two fixed public stages. Not recognition speed, whole-app speed, current gameplay accuracy, or proof of a universal refresh improvement.',
    'related_unique_passed':61,'related_receipt':pin('verification/maintenance/battle-reader-review-20261031/tests-reconciled.json'),
    'native_checks':50,'native_receipt':pin('verification/maintenance/battle-reader-review-20261031/native-current/window.json'),
    'image_review':pin('verification/maintenance/battle-reader-review-20261031/image-review.json'),
    'runtime':pin('verification/maintenance/battle-reader-review-20261031/live-window-final/desktop-review.json'),
    'maintained_selectors_count':693,'original_full_order_and_scope_preserved':True,'full_validation_rerun':False,'full440_only_original_frozen_source':True,
    'P3_complete':False,'P2_complete':False,'P1_complete':False,'game_operated':False,'chat_sent':False,'private_data_included':False,
    'publication_binding':'enclosing maintenance commit, actual remote checked after ordinary push'}
write('verification/maintenance/battle-reader-review-20261031/summary.json',summary)
text('research/battle-reader-review-20261031/README.md','''# 固定作战资料、缩略图与窗口清理回顾

本轮按REA技能要求，直接审查现有Python源码与实际Windows Qt运行。保留先前工具条、三份聊天桥接的REA静态证据；没有把未执行的逆向、文件清点或本轮局部测试当作整个程序完成。

## 已修正

- 固定作战同时构建奖励、基础结算子面板时，子面板先读取一次，父面板立即再次刷新。改为父面板统一完成第一次读取；独立打开子面板仍立即读取。全部来源、数量未知与精确配置匹配规则保持。
- 含所选敌人的筛选刷新和跨波次/分支跳转各有两次出怪列表重建，合并为一次；准确选中项、分类、搜索和阅读保持。
- 抽出原项目图片缩放逻辑，固定战斗与目录复用ReferenceImage和Qt现有图像组件，按图片区域的实际大小保持原图比例。拖动窗口时复用解码后的原图，不反复从PNG解码，也不从上一次缩小的图再次放大。来源丢失时清原图，随后缩放不会复活旧图。去掉目录父窗口的重复resize实现及初始化判空。
- 面板与外层对话框两份相同清理列表合并一处。原16项清理调用的语法树与顺序均保持；实际关闭两种入口均清除所属机关资料结果。

图片实现沿用本项目原缩放方式，采用[Qt图像查看示例](https://doc.qt.io/qtforpython-6/examples/example_widgets_imageviewer.html)所用的QLabel/QPixmap和尺寸策略；没有引入新依赖或复制整套第三方查看器。此缩略图不替代有独立校准门槛的原图位置映射。

## 实际验收

三轮旧版和三轮最终实现，两个固定配置、每进程18种状态，完整关卡结果、默认与选中说明、奖励/基础结算、来源失效/恢复输出一致；目录准确条目及图片来源也一致。旧版与初版改进的另三轮对照保留为中间证据，不冒充最终来源。构建时奖励/结算各2→1次，相关列表重建2→1次。具体耗时原件分别保存；刷新中位数不作普遍加速结论，不代表识别、全应用或游戏实际准确性。

首轮60项相关检查通过；清理抽取后6项必要检查通过，重叠5项，实际可用独立范围61项。其余55项保留原通过证据及未改变清理顺序的独立核对；不重复全套检查。最终当前源码原生50项通过。首轮窗口测试的默认筛选夹具失败原件保留；只修正测试所选范围，没有放宽产品规则。7张最终图片按整字节一致复用本轮逐张查看的原件；另4张首轮图也已实际查看。

测试小窗按最终源码更新打开，正常关闭/启动区间六处私人状态保持；摘要只留本机。完整选择器保持原序追加至693，full-440只证明其原冻结来源，本次不增441。

## 保留缺口

本轮没有增加实际出怪时钟、坐标校准、敌人最终面板、当前服务器验证或奖励池机制；已有未知仍保留。原片本轮回看的是节点候选卡片片段，并非固定战斗页的完整设计依据，不能据此宣称本轮界面已与视频一致。其余资料窗口、说明密度、交互和全程序其它链路继续回顾；识别最后。P3/P2/P1和完整视频目标尚未完成。
''')
t=(R/'PROGRAM_REVIEW.md').read_text('utf8')
t=t.replace('本轮新增共享布局、资源事实与资源栏3份源码，当前总范围528份','随后新增共享布局、资源事实、资源栏与固定地图图片组件4份源码，当前总范围529份')
t=t.replace('此前已核对部分地图与资料浮窗的刷新、导航和阅读保持。','已核对部分地图与资料浮窗，并继续审查固定作战构建、精确筛选、缩略图与窗口清理；合并重复读取和关闭流程，两个固定配置的18种状态完成新旧对照。')
t+='\n本轮[固定作战阅读链路回顾](research/battle-reader-review-20261031/README.md)保持关卡来源与未知数值，不把局部输出一致当作完整机制准确或全部数据覆盖。\n'
text('PROGRAM_REVIEW.md',t)
t=(R/'VIDEO_PARITY.md').read_text('utf8');t+='\n[固定作战阅读链路回顾](research/battle-reader-review-20261031/README.md)已合并重复读取与窗口清理，目录和固定作战共用等比图片组件。本轮只回看节点卡片片段；固定战斗布局、其余窗口密度与完整视频效果仍待核对，不因缩略图适配而销项。\n';text('VIDEO_PARITY.md',t)
entry='''<!-- battle-reader-review-20261031:start -->
## 实现维护 · 固定作战阅读、缩略图与窗口清理

固定战斗的奖励/结算首次读取各2→1次，相关出怪筛选/跳转重建2→1次；固定战斗与目录共用等比图片组件，复用解码原图，失效后不复活旧图。两份相同窗口清理列表归一，原16项调用顺序保持，来源检查不减少。

三轮旧版与三轮当前实现、每进程两固定配置18种状态的完整结果与文字一致；不是机制或实机准确性校准。初轮60项、最终6项检查通过，重叠5项，独立可用范围61项；清理抽取的等价核对保留。当前源码原生50项通过，7张图按整字节相同复用本轮逐张审阅，首轮夹具失败保留。最终测试小窗更新可见响应，启动区间六处私人状态保持。未新增实际时钟、坐标校准或完整面板。功能仍440、441未启动；全程序/视频及P3/P2/P1仍未完成，full-440只证明原冻结来源。回执：`verification/maintenance/battle-reader-review-20261031/summary.json`。
<!-- battle-reader-review-20261031:end -->

'''
for n in ('WORK_IN_PROGRESS.md','PROJECT_COMPLETED.md'):
    t=(R/n).read_text('utf8');assert '<!-- battle-reader-review-20261031:start -->'not in t;text(n,entry+t)
t=(R/'PROJECT_PROGRESS.md').read_text('utf8');t=t.replace('补齐其余招募/强化/异常恢复的连续场景与独立机制依据，核对其余资料入口、缺图和视频交互/外观','补齐其余招募/强化/异常恢复的连续场景与独立机制依据，核对其余资料入口、固定作战完整数据/实际时钟、缺图和视频交互/外观');text('PROJECT_PROGRESS.md',t)
cp=read('DEVELOPMENT_CHECKPOINT.json');cp['current_maintenance_save']={'kind':'implementation_maintenance','title':summary['title'],
    'receipt':'verification/maintenance/battle-reader-review-20261031/summary.json','binding':'enclosing_commit','functional_section_added':False,
    'status':'partial_program_review_fixed_battle_reading_and_shared_image_checked','review_checklist':'PROGRAM_REVIEW.md',
    'review_checklist_sha256':pin('PROGRAM_REVIEW.md')['sha256'],'application_review_complete':False}
cp['current_batch']['receipt']='verification/maintenance/battle-reader-review-20261031/summary.json'
cp['next_action']='继续完整程序回顾：其余资料窗口/节点卡片与视频差异、状态/强化连续场景及独立机制依据；固定作战完整数据、实际时钟与完整面板保留缺口。已完成重复读取、图片组件和窗口清理不重复推进，识别优化最后。'
text('DEVELOPMENT_CHECKPOINT.json',json.dumps(cp,ensure_ascii=False,indent=2)+'\n')
m=runpy.run_path(str(R/'scripts/update_cloud_index.py'));m['update'](R);assert m['validate_delivery'](R,cp)['current_section']==440
(base/'replay-source.py').write_bytes((R/'.cache/battle_reader_replay.py').read_bytes())
(base/'initial-construction-profile.txt').write_bytes((R/'.cache/battle-review-20261101/construction-profile.txt').read_bytes())
(base/'record-source.py').write_bytes(Path(__file__).read_bytes())
print(json.dumps({'recorded':True,'available_unique_scope':61,'native_checks':50,'original_full_selectors_preserved':693,'whole_program_complete':False}))
