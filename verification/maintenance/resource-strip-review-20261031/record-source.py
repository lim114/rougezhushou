from pathlib import Path
from hashlib import sha256
from datetime import datetime, timezone
import ast, json, subprocess, sys, difflib, runpy, time, ctypes, win32gui, win32process

R = Path.cwd(); sys.path[:0] = [str(R), str(R/'scripts')]
base = R/'verification/maintenance/resource-strip-review-20261031'
baseline = 'db346f5aa3bee94ceb5b1f0abf9e792d7b4a7d98'

def read(path): return json.loads((R/path).read_bytes())
def pin(path):
    p=R/path;raw=p.read_bytes()
    return {'path':p.relative_to(R).as_posix(),'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}
def write(path,value): (R/path).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n','utf8')
def text(path,value):
    p=R/path
    if not p.exists():p.write_text(value,'utf8');return
    old=p.read_bytes().decode('utf8').splitlines(keepends=True);new=value.splitlines(keepends=True);out=list(new)
    for a,b,n in difflib.SequenceMatcher(None,[s.rstrip('\r\n')for s in old],[s.rstrip('\r\n')for s in new],autojunk=False).get_matching_blocks():
        for i in range(n):out[b+i]=old[a+i]
    p.write_bytes(''.join(out).encode('utf8'))

assert subprocess.check_output(['git','rev-parse','HEAD']).decode().strip()==baseline
changed=['rouge/player_compact.py','rouge/player_map.py','rouge/player_overview.py','rouge/player_map_acceptance.py',
    'rouge/flow_layout.py','rouge/player_resource_facts.py','rouge/player_resource_strip.py']
original_source=R/'.cache/qt-flow-layout-source/flowlayout.py'
upstream=read('research/resource-strip-review-20261031/upstream-source.json')
assert sha256(original_source.read_bytes()).hexdigest()==upstream['source_sha256']
assert pin('licenses/qt-flow-layout-BSD-3-Clause.txt')['sha256']==upstream['license_sha256']
def flow(path):return next(x for x in ast.parse(path.read_bytes()).body if isinstance(x,ast.ClassDef) and x.name=='FlowLayout')
assert ast.dump(flow(original_source))==ast.dump(flow(R/'rouge/flow_layout.py'))
text('research/resource-strip-review-20261031/qt-flow-layout-upstream.py', original_source.read_text('utf8'))

tests=read('verification/maintenance/resource-strip-review-20261031/tests/results.json')
assert tests['passed'] and tests['tests_run']==54 and not tests['skipped'] and not tests['forbidden_external_calls']
assert read('verification/maintenance/resource-strip-review-20261031/tests/process.json')['actual_observed_exit']==0
native=[]
for folder,checks in [('native-final',35),('native-392',34),('native-422',16)]:
    path=f'verification/maintenance/resource-strip-review-20261031/{folder}/window.json';v=read(path)
    assert v['passed'] and v['unique_checks']==checks and v['qpa']=='windows' and not any(v['external_operation_attempts'].values())
    assert all(v['source_sha256_after'][n]==pin(n)['sha256'] for n in changed)
    if folder!='native-final':assert read(f'verification/maintenance/resource-strip-review-20261031/{folder}/process.json')['actual_observed_exit']==0
    native.append({'scope':folder,'checks':checks,'receipt':pin(path),'overlapping_checks_not_added':True})
write('verification/maintenance/resource-strip-review-20261031/native-final/process-observation.json',{
    'observation':'functions.exec_command synchronous completed result, chunk 7a7dcf',
    'actual_observed_exit':0,'outer_retained_Popen_handle_claimed':False})
live=read('verification/maintenance/resource-strip-review-20261031/live-window/window.json')
assert live['passed'] and live['private_six_paths_unchanged']
assert all(live['source_sha256_after'][n]==pin(n)['sha256']for n in changed)
for row in live['owned_windows']:
    assert win32gui.IsWindowVisible(row['hwnd']) and win32process.GetWindowThreadProcessId(row['hwnd'])[1]==row['pid'] and not ctypes.windll.user32.IsHungAppWindow(row['hwnd'])
a=read('.cache/runtime-resources-live-status.json');time.sleep(2.2);b=read('.cache/runtime-resources-live-status.json')
assert b['toolbar_visible'] and b['elapsed_since_launch']>a['elapsed_since_launch']
write('verification/maintenance/resource-strip-review-20261031/live-window/desktop-review.json',{
    'actor':'/root','actual_windows_mcp_snapshot_called':True,'actual_image_viewed':True,
    'region':[1716,1164,2130,1218],'owned_window_visible_and_responding':True,'Qt_timer_advanced':True,
    'private_hashes_or_contents_published':False,'game_operated':False,'chat_sent':False})
from scripts.verify_full_available import maintained_selectors
old=read('verification/sections/440-source-audit.json')['current_selectors']
assert maintained_selectors()==old+['tests.test_player_popover_refresh','tests.test_desktop_receipts','tests.test_catalog_refresh_review','tests.test_state_calculation_updates','tests.test_player_resource_strip']
assert len(maintained_selectors())==692
review={'baseline_commit':baseline,'kind':'complete_source_and_controlled_runtime_review',
    'changed_application_and_acceptance_source':[pin(n)for n in changed],
    'additional_source_read':[pin(n)for n in ('rouge/player_context.py','rouge/player_floor_resources.py','rouge/player_resource_history.py',
        'rouge/resource_recognition.py','rouge/run_state.py','rouge/record_flags.py','rouge/player_replay.py')],
    'Qt_flow_class_AST_identical_to_pinned_upstream':True,
    'formula_recognition_and_RunState_mutation_implementations_unchanged':True,
    'REA':'Prior toolbar and three-bridge evidence retained; no new REA session or PYC completeness claim. Complete Python sources reviewed directly according to skill.',
    'whole_program_review_complete':False}
write('verification/maintenance/resource-strip-review-20261031/review-source.json',review)
final_images=['native-final/map-840.png','native-final/map-1100.png','native-final/inventory-840.png','native-final/window.png',
    'native-392/window.png','native-392/node-hover.png','native-422/window.png']
write('verification/maintenance/resource-strip-review-20261031/image-review.json',{
    'actor':'/root','mode':'each actual full image loaded with view_image',
    'images':[pin('verification/maintenance/resource-strip-review-20261031/'+n)for n in final_images],
    'earlier_diagnostic_images_also_viewed':['native/map-840.png','native/map-1100.png','native/inventory-840.png','native/window.png'],
    'reference_frames_actually_viewed':['.cache/rea-review-20261031/video-map-141s.png','.cache/video414/172.png'],
    'reference_frames_not_public_game_samples':True,'continuous_full_video_playback_this_turn':False,
    'remaining_visual_differences':'Overall proportions, remaining panels, controls and density differ; six resource values remain unsupported. No full video parity claim.'})
summary={'kind':'implementation_maintenance','title':'地图与藏品资源胶囊复用、页面联动及收藏品总数修正',
    'baseline_commit':baseline,'completed_sections':440,'functional_section_added':False,'next_section_started':False,
    'implemented_fixes_passed':True,'application_review_complete':False,'video_parity_complete':False,
    'source_review':pin('verification/maintenance/resource-strip-review-20261031/review-source.json'),
    'implemented':['Shared width-driven light/dark resource pills with local inventory/parts/team links.',
        'Overview excludes tactical tools from the relic-only denominator only after a full qualified count match.',
        'A true verification flag without matching count no longer claims complete inventory.',
        'Visible readers refresh from current state; hidden readers do no resource refresh; replaced temporary run clears stale values.',
        'Difficulty/squad remain visible and historical floor resources remain separate.'],
    'related_tests':{'passed':54,'failed':0,'errors':0,'skipped':0,'receipt':pin('verification/maintenance/resource-strip-review-20261031/tests/results.json')},
    'native_scopes':native,'native_counts_overlap_not_totalled':True,
    'image_review':pin('verification/maintenance/resource-strip-review-20261031/image-review.json'),
    'runtime':pin('verification/maintenance/resource-strip-review-20261031/live-window/desktop-review.json'),
    'maintained_selectors_count':692,'original_order_and_scope_preserved':True,'full_validation_rerun':False,
    'full440_only_original_frozen_sources':True,'upstream_source':pin('research/resource-strip-review-20261031/upstream-source.json'),
    'unsupported_resources':['目标生命','护盾','指挥等级','希望','行动力','总估价'],
    'mechanism_changes':False,'recognition_changes':False,'game_operated':False,'chat_sent':False,
    'private_data_included':False,'P3_complete':False,'P2_complete':False,'P1_complete':False,
    'publication_binding':'enclosing maintenance commit; actual remote checked after ordinary push'}
write('verification/maintenance/resource-strip-review-20261031/summary.json',summary)
text('research/resource-strip-review-20261031/README.md','''# 资源栏、库存口径与资料联动回顾

本轮直接审查完整Python源码与实际Qt运行；REA原工具条/聊天桥接证据保持，不把未执行的逆向或文件扫描算作整体完成。原片141秒地图和172秒藏品页逐张核对：地图浅色、藏品深色资源胶囊共用一种布局，窄窗自然换行。

复用[Qt官方Flow Layout](https://doc.qt.io/qtforpython-6/examples/example_widgets_layouts_flowlayout.html)，固定v6.11.2。类主体AST与原件相同，去掉演示窗口和未使用导入，保留作者、许可证及固定来源，不安装新依赖。完整源码和许可均随此维护保存；这是Qt布局复用，不是找到参考视频程序源码。

## 实际修正

- 概况原来把含战术道具的底部合计直接当收藏品分母，且单凭inventory_verified就声称完整。现在按既有持有标记与清单口径核对；例如两件藏品和一件道具，收藏品显示2/2，另列一件道具。未核对完整时不靠已知道具数推断未读收藏品总数。
- 地图与藏品窗口共用ResourceStrip，点击藏品、零件箱或干员直接到对应本地页面。更新已有标签，不重建控件；隐藏时不刷新，恢复与当前状态替换时重读。读取到0与尚未读取分开。
- 最近资源与历史楼层读取仍分开；保密等级和分队留在地图说明。没有改采样、识别、机制、数值计算或本局记忆。

## 验收与边界

54项相关检查通过；原生扩展35项、地图392范围34项、历史资源422范围16项分别通过，重叠不累计。实际窗口、点击与7张最终原图逐张核对，初始4张诊断图也已查看。原项目测试小窗已更新打开，六处私人状态启动区间保持，摘要不公开。全量选择器保持原序并追加至692，full-440仍只证明其原冻结源码。

目标生命、护盾、指挥等级、希望、行动力、总估价当前自动读取未覆盖，继续明确显示未读。其它窗口比例、控件密度、布局和完整交互仍有差异；未宣称全程序审查、实机准确性、P3/P2/P1或视频效果全部完成。本轮为维护，不新增441。
''')
t=(R/'PROGRAM_REVIEW.md').read_text('utf8')
t=t.replace('这是原始范围清单，不能当作逐文件正确性验收；','本轮新增共享布局、资源事实与资源栏3份源码，当前总范围528份；原始清单不作为新增模块或逐文件正确性验收；')
t=t.replace('| 公开资料与缓存 |','| 地图/藏品资源与页面联动 | 已审查当前资源、库存口径及历史快照，复用Qt官方布局、共享资源胶囊并修正收藏品分母和错误完整标记；原生点击、更新和临时新局替换已验证。 | 六项资源自动读取尚未覆盖，剩余窗口比例、布局与视频交互仍需逐项验收。 |\n| 公开资料与缓存 |')
t+='\n本轮[资源栏与库存口径回顾](research/resource-strip-review-20261031/README.md)只证明相关源码、隔离窗口和联动范围；未完成的全程序与实机验收保持。\n'
text('PROGRAM_REVIEW.md',t)
t=(R/'VIDEO_PARITY.md').read_text('utf8')
t=t.replace('资源条、各窗口比例/说明密度以及其它交互和外观仍未全部一致。','资源条布局本轮已复用Qt官方Flow Layout并接入地图/藏品窗口，支持本地页面跳转；目标生命等六项仍未支持读取。各窗口比例/说明密度以及其它交互和外观仍未全部一致，见[资源栏回顾](research/resource-strip-review-20261031/README.md)。')
text('VIDEO_PARITY.md',t)
entry='''<!-- resource-strip-review-20261031:start -->
## 实现维护 · 地图/藏品资源与库存口径

资源胶囊按实际宽度换行，地图浅色、藏品深色复用同一组件，可直接跳到藏品、零件箱或队伍；刷新保留搜索和地图选择，隐藏停止资源刷新，状态替换清旧值。概况修正含道具总计被当作收藏品分母及单凭标记冒称完整。复用Qt官方v6.11.2布局，保留作者、固定来源和BSD许可，无新依赖；未改识别或数值机制。

54项相关检查、原生扩展35项、地图392范围34项与历史资源422范围16项分别通过，重叠不累计；最终7张原图实际查看，原项目测试小窗更新打开，启动区间六处私人状态保持。目标生命等六项读取仍缺失，不补猜。功能仍440、441未启动；全程序回顾、视频全部一致及P3/P2/P1均未完成，full-440仅证明原冻结来源。回执：`verification/maintenance/resource-strip-review-20261031/summary.json`。
<!-- resource-strip-review-20261031:end -->

'''
for n in ('WORK_IN_PROGRESS.md','PROJECT_COMPLETED.md'):
    t=(R/n).read_text('utf8');assert '<!-- resource-strip-review-20261031:start -->'not in t;text(n,entry+t)
t=(R/'PROJECT_PROGRESS.md').read_text('utf8')
t=t.replace('全程序回顾尚未完成，剩余审查范围', '全程序回顾尚未完成；仍需核对其它资料窗口、视频交互/外观与六项资源自动读取，剩余审查范围',1)
text('PROJECT_PROGRESS.md',t)
cp=read('DEVELOPMENT_CHECKPOINT.json')
cp['current_maintenance_save']={'kind':'implementation_maintenance','title':summary['title'],
    'receipt':'verification/maintenance/resource-strip-review-20261031/summary.json','binding':'enclosing_commit',
    'functional_section_added':False,'status':'partial_program_review_resource_links_and_inventory_counts_checked',
    'review_checklist':'PROGRAM_REVIEW.md','review_checklist_sha256':pin('PROGRAM_REVIEW.md')['sha256'],'application_review_complete':False}
cp['current_batch']['receipt']='verification/maintenance/resource-strip-review-20261031/summary.json'
cp['next_action']='继续全程序回顾：剩余资料窗口、状态/强化连续场景、独立机制依据和视频交互/外观；六项资源读取与其它识别优化最后。已完成资源胶囊与库存口径修正不重复记进度，不把局部检查当整体完成。'
text('DEVELOPMENT_CHECKPOINT.json',json.dumps(cp,ensure_ascii=False,indent=2)+'\n')
m=runpy.run_path(str(R/'scripts/update_cloud_index.py'));m['update'](R);assert m['validate_delivery'](R,cp)['current_section']==440
print(json.dumps({'recorded':True,'whole_program_complete':False,'related_tests_passed':54,'full_selectors':692}))
