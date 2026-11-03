from pathlib import Path
from hashlib import sha256
import ast,json,subprocess,sys,difflib,runpy,re,time,ctypes,win32gui,win32process
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts')];base=R/'verification/maintenance/node-card-review-20261031'
baseline='cbe2a2609a704e1d8c7b20b3858c58792c7cef5c'
def read(n):return json.loads((R/n).read_bytes())
def pin(n):
    p=R/n;raw=p.read_bytes();return {'path':p.relative_to(R).as_posix(),'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}
def write(n,value):(R/n).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n','utf8')
def text(n,value):
    p=R/n
    if not p.exists():p.write_text(value,'utf8');return
    old=p.read_bytes().decode('utf8').splitlines(keepends=True);new=value.splitlines(keepends=True);out=list(new)
    for a,b,num in difflib.SequenceMatcher(None,[s.rstrip('\r\n')for s in old],[s.rstrip('\r\n')for s in new],autojunk=False).get_matching_blocks():
        for i in range(num):out[b+i]=old[a+i]
    p.write_bytes(''.join(out).encode('utf8'))

changed=['rouge/app.py','rouge/node_catalog.py','rouge/node_statistics_source.py','rouge/player_compact.py','rouge/player_game_map.py',
    'rouge/player_map.py','rouge/player_map_hover.py','rouge/player_map_reference.py','rouge/public_node_statistics.py','rouge/public_node_statistics_view.py']
assert subprocess.check_output(['git','rev-parse','HEAD']).decode().strip()==baseline
assert set(subprocess.check_output(['git','diff','--name-only','--','rouge']).decode().splitlines())==set(changed)-{'rouge/node_statistics_source.py'}
for name in('rouge/node_catalog.py','rouge/public_node_statistics.py'):
    old=ast.parse(subprocess.check_output(['git','show',baseline+':'+name]));new=ast.parse((R/name).read_bytes())
    a={n.name:n for n in old.body if isinstance(n,ast.FunctionDef)};b={n.name:n for n in new.body if isinstance(n,ast.FunctionDef)}
    exceptions={'node_dossier'}if name.endswith('node_catalog.py')else{'frequency_rows'}
    assert all(ast.dump(v)==ast.dump(b[k])for k,v in a.items()if k not in exceptions)
comparison=read('verification/maintenance/node-card-review-20261031/before-after.json')
assert comparison['all_public_rows_exactly_equal'] and comparison['public_query_cases']==606 and len(comparison['domain_cases'])==15
assert comparison['full_domain_results_equal'] and comparison['fetch_parser_validation_AST_unchanged']
for name,pins in comparison['source'].items():
    assert pins['current_sha256']==pin(name)['sha256']
    assert pins['before_sha256']==sha256(subprocess.check_output(['git','show',baseline+':'+name])).hexdigest()
write('verification/maintenance/node-card-review-20261031/comparison-observation.json',{'actual_completed_exec_command_chunk':'d865d8',
    'actual_observed_exit':0,'execution':'inline Python via exec_command, not a retained Popen claim',
    'comparison':pin('verification/maintenance/node-card-review-20261031/before-after.json')})
tests=read('verification/maintenance/node-card-review-20261031/tests/results.json');final=read('verification/maintenance/node-card-review-20261031/tests-final/results.json')
assert tests['passed'] and tests['tests_run']==132 and final['passed'] and final['tests_run']==10
ids=[]
for folder in('tests','tests-final'):
    assert read(f'verification/maintenance/node-card-review-20261031/{folder}/process.json')['actual_observed_exit']==0
    ids.append(set(re.findall(r'^test_\w+ \(([^)]+)\)',(base/folder/'stderr.txt').read_text('utf8'),re.M)))
assert len(ids[0])==132 and len(ids[1])==10 and ids[1]<=ids[0]
write('verification/maintenance/node-card-review-20261031/tests-reconciled.json',{'unique_available_passed':132,'initial_passed':132,'final_focused_passed':10,
    'overlap':10,'initial_ids':sorted(ids[0]),'final_ids':sorted(ids[1]),
    'final_change_scope':'Only two hover layout lines after initial suite: hide missing type picture, keep two equal thumbnail columns. Ten relevant checks and full native extension rerun.',
    'other_122_reused':True,'failures_remaining':0,'unavailable_in_selected_scope':0})
native=read('verification/maintenance/node-card-review-20261031/native-current/window.json')
assert native['passed'] and native['unique_checks']==60 and not any(native['external_operation_attempts'].values())
assert read('verification/maintenance/node-card-review-20261031/native-current/process.json')['actual_observed_exit']==0
assert all(native['source_sha256_after'][n]==pin(n)['sha256']for n in changed)
extra=read('verification/maintenance/node-card-review-20261031/native-current/review-images.json')
assert len(extra['images'])==5 and all(row['visible_owned_at_save']for row in extra['images'])
images=[]
for p in sorted((base/'native-current').glob('*.png')):
    old=base/'native-final'/p.name;same=p.read_bytes()==old.read_bytes()
    images.append({'image':pin(p.relative_to(R)),'review_method':'exact whole-byte reuse from this-turn view_image original'if same else'loaded individually with view_image by /root',
        'original':pin(old.relative_to(R))if same else None,
        'scope':'diagnostic widget grab, not visible-hover evidence'if p.name=='node-hover.png'else'isolated public-fixture UI',
        'synthetic_percentages_are_not_real_website_statistics':True})
assert len(images)==7
assert all(p.read_bytes()==(base/'native-final'/p.name).read_bytes()for p in(base/'native').glob('*.png'))
write('verification/maintenance/node-card-review-20261031/image-review.json',{'reviewer':'/root','current_images':images,
    'all_seven_native_final_images_actually_loaded_this_turn':True,'current_changed_passed_history_and_diagnostic_actually_loaded':True,
    'earlier_native_images_reused_by_exact_bytes_from_viewed_native_final':True,
    'reference_frames_actually_viewed':['.cache/reference-local-video-385/timeline/frame-026.jpg','.cache/reference-local-video-385/timeline/frame-029.jpg'],
    'whole_video_parity_claimed':False})
fetch=read('research/node-card-review-20261031/live-fetch.json')
assert fetch['passed'] and len(fetch['requests'])==3 and fetch['uploads']==0 and not fetch['game_or_account_parameters']
assert all(row['method']=='GET'and row['body_is_none']for row in fetch['requests'])
assert fetch['data_sha256']==pin('research/node-card-review-20261031/live-public-statistics.json')['sha256']
assert fetch['same_counts_as_bundled'] and fetch['updated_at']=='2026-10-01T05:31:38.191161+00:00' and fetch['sample_count']==481984
live=read('verification/maintenance/node-card-review-20261031/live-window/window.json')
assert live['passed'] and live['private_six_paths_unchanged'] and all(live['source_sha256_after'][n]==pin(n)['sha256']for n in changed)
for w in live['owned_windows']:assert win32gui.IsWindowVisible(w['hwnd']) and win32process.GetWindowThreadProcessId(w['hwnd'])[1]==w['pid'] and not ctypes.windll.user32.IsHungAppWindow(w['hwnd'])
a=read('.cache/runtime-node-source-live-status.json');time.sleep(2.2);b=read('.cache/runtime-node-source-live-status.json');assert b['toolbar_visible']and b['elapsed_since_launch']>a['elapsed_since_launch']
write('verification/maintenance/node-card-review-20261031/live-window/desktop-review.json',{'actor':'/root','actual_windows_mcp_snapshot_called':True,
    'actual_image_viewed':True,'region':[1716,1164,2130,1218],'actual_Qt_timer_advanced':True,'owned_window_visible_and_responding':True,
    'private_six_paths_unchanged_during_startup':True,'private_contents_or_hashes_published':False,'game_operated':False,'chat_sent':False})
write('verification/maintenance/node-card-review-20261031/fixture-correction.json',{'first_observed_tool_chunk':'e6594f','first_failure_exit':1,
    'retained_reproduction':'fixture-reproduction/process.json','reproduction_exit':1,'reproduction_tests':33,'reproduction_errors':8,
    'reason':'Standalone toolbar fake owners lacked the new shared source getter. Explicitly provided the getter in three test fixtures; production owner contract was not weakened by getattr fallback.',
    'original_short_tool_output_not_claimed_as_full_disk_log':True,'final_scope':'tests-reconciled.json'})
from scripts.verify_full_available import maintained_selectors
old=read('verification/sections/440-source-audit.json')['current_selectors']
assert maintained_selectors()==old+['tests.test_player_popover_refresh','tests.test_desktop_receipts','tests.test_catalog_refresh_review',
    'tests.test_state_calculation_updates','tests.test_player_resource_strip','tests.test_battle_reader_review','tests.test_node_card_source_review']
assert len(maintained_selectors())==694
for name in('rouge/run_state.py','rouge/node_catalog_view.py','rouge/capture.py'):
    assert subprocess.check_output(['git','show',baseline+':'+name])==(R/name).read_bytes()
write('verification/maintenance/node-card-review-20261031/review-source.json',{'baseline_commit':baseline,'changed_source':[pin(n)for n in changed],
    'unchanged_sources':[pin(n)for n in ('rouge/run_state.py','rouge/node_catalog_view.py','rouge/capture.py')],
    'existing_catalog_functions_except_history_extraction_AST_unchanged':True,'fetch_parser_and_validation_AST_unchanged':True,
    'review_scope':'Public statistics load/update/cache, map and overlay consumers, card rebuild key, history-only dossier, unknown-type guard and exact history navigation. Not a complete review of every app method or game mechanic.',
    'REA_scope':'Prior toolbar/bridge static evidence retained. This round uses complete Python source and controlled Windows execution according to the REA skill, without a new REA or PYC coverage claim.',
    'application_review_complete':False})
summary={'kind':'implementation_maintenance','title':'节点统计共享源、已读历史入口与未知类型候选修正','baseline_commit':baseline,
    'completed_sections':440,'functional_section_added':False,'next_section_started':False,'implemented_scope_passed':True,
    'application_review_complete':False,'video_parity_complete':False,'source_review':pin('verification/maintenance/node-card-review-20261031/review-source.json'),
    'related_unique_available_passed':132,'related_receipt':pin('verification/maintenance/node-card-review-20261031/tests-reconciled.json'),
    'native_checks':60,'native_receipt':pin('verification/maintenance/node-card-review-20261031/native-current/window.json'),
    'comparison':pin('verification/maintenance/node-card-review-20261031/before-after.json'),'public_queries_equal':606,'core_catalog_cases_equal':15,
    'live_public_fetch':pin('research/node-card-review-20261031/live-fetch.json'),'real_public_update_date':'2026-10-01','real_public_sample_count':481984,
    'live_public_counts_equal_to_bundled':True,'public_GET_requests':3,'personal_uploads':0,
    'image_review':pin('verification/maintenance/node-card-review-20261031/image-review.json'),
    'runtime':pin('verification/maintenance/node-card-review-20261031/live-window/desktop-review.json'),
    'maintained_selectors_count':694,'full_scope_order_preserved':True,'full_validation_rerun':False,'full440_only_original_frozen_source':True,
    'P3_complete':False,'P2_complete':False,'P1_complete':False,'game_operated':False,'chat_sent':False,'private_data_included':False,
    'publication_binding':'enclosing maintenance commit, actual remote checked after ordinary push'}
write('verification/maintenance/node-card-review-20261031/summary.json',summary)
text('research/node-card-review-20261031/README.md','''# 节点统计、历史与地图卡片回顾

本轮直接审查现有Python源码与实际Qt运行；先前REA工具条/聊天桥接证据保留，没有新开REA会话或制造PYC覆盖。全程序回顾仍未完成。

## 事实与修正

- 候选类型原本已经三列，本轮没有把已存在的能力重做。事件图卡仍沿用两列，修正只有一项时撑满整行的问题；无图的空地类型不再占空白图片高度。
- 统计窗口原来读最新本机缓存，地图/卡片/游戏标注却固定用随包统计。现在共用一个公开来源对象：新数据先核对并原子保存，成功后各处更新；失败保留旧来源，损坏缓存明确无统计，不静默换旧数据。数据不变的重复读取不重建地图，隐藏地图下次打开再更新，固定阅读与选中位置保留。
- 已通过节点的卡片补充已读历史事件/作战，可打开准确历史条目。当前类型不明且保留旧类型时，侧栏原来可能走入全目录联合；现在侧栏和卡片共用资格入口，只显示明确候选或保存的历史。历史不当作现在再发生、当前生成候选或出现次数。
- 抽取既有历史读取代码复用；没有历史战斗时不再额外构建完整战斗目录。统计接受后建立索引，查询复用同一频率计算方式、分母和类别次序，保留未知与精确字符串距离键。

## 实现选择与资料

采用现有Qt [QObject/Signal](https://doc.qt.io/qtforpython-6/PySide6/QtCore/Signal.html)通知与原项目缓存/目录代码，无新增依赖。也核对了[Qt共享模型方案](https://doc.qt.io/qtforpython-6/overviews/qtwidgets-model-view-programming.html)；本项目地图与卡片是自绘/独立窗口，本轮选择小型共享来源，保留现有绘制器和各自阅读选择。这是本项目的实现判断，不是声称已接入Qt Item Model或找到参考程序源码。

实际只读[路标公开统计](https://www.lubiao.wiki/tools/blackstream-route)共3次GET，无请求体、对局或账号参数。数据更新时间仍为2026-10-01，481984条总记录，与随包计数一致；并非取得新的DLC2条件概率。原件及请求记录在同目录保存。所有查询和计算在本机完成，不上传个人对局。

## 验收边界

606组查询与15组核心目录结果逐项对照旧源码一致。一次本机606查询批次含索引构建约108.13→1.83毫秒；旧地图本身已有缓存，此测量不是实际地图、整机或识别加速倍数，也不证明当前完整条件概率。

132项相关检查通过；最终两行布局调整后10项相关检查重跑通过，重叠不累计。当前源码原生60项通过，包含固定卡片随模拟统计更新、隐藏不重建、历史准确跳转及未知不填全目录。截图中的70/80/90%是明确标注的隔离样例，不是真实网站计数；基础工具额外生成的隐藏卡片抓图只作诊断，不作可见窗口证据。此前8个假窗口夹具错误的完整独立复现保留，修正夹具后通过，未放宽实际应用接口。

最终测试小窗已更新打开，启动区间六处私人状态保持，摘要只留本机。完整选择器保持原序追加至694；full-440只证明原冻结来源，本次不增441。原片本轮回看节点卡片片段；外观尺寸、图卡构成、其余界面和交互仍未全部一致。本批没有新增战斗时钟、实际敌人面板或条件概率；P3/P2/P1与完整目标仍未完成，识别最后。
''')
t=(R/'PROGRAM_REVIEW.md').read_text('utf8').replace('共享布局、资源事实、资源栏与固定地图图片组件4份源码，当前总范围529份','共享布局、资源事实、资源栏、固定地图图片组件与公开统计来源5份源码，当前总范围530份')
t=t.replace('| 公开资料与缓存 |','| 公开节点统计与已读历史 | 已接通统计表、地图、悬浮卡和只读标注的共同来源；606查询及15组核心目录结果对照，修正未知类型全目录回退，补已读历史的准确入口。 | 完整条件概率、版本适用性、其余资料/界面与全套游戏窗口交互仍需核对；本轮无真实游戏采集。 |\n| 公开资料与缓存 |')
t+='\n本轮[节点统计与历史回顾](research/node-card-review-20261031/README.md)记录共享来源和局部目录修正；公开数据仍更新于10月1日，不证明当前DLC完整概率或实际生成。\n';text('PROGRAM_REVIEW.md',t)
t=(R/'VIDEO_PARITY.md').read_text('utf8');t+='\n[节点统计与历史回顾](research/node-card-review-20261031/README.md)已让联网接受的公开缓存同步到地图/卡片/只读标注，并补已读历史入口、修正未知类型全目录回退。当前公开数据仍为10月1日；606查询不改变旧口径，不冒充完整条件概率。原片三列类型/两列图卡保持，单项卡片列宽已修正；全部外观与交互仍未一致。\n';text('VIDEO_PARITY.md',t)
entry='''<!-- node-card-review-20261031:start -->
## 实现维护 · 节点统计共享与已读历史

统计表、地图、卡片与只读标注共用公开缓存和索引，成功接受后同步，失败保留旧源，隐藏地图不重建。卡片补历史事件/作战的准确入口；未知类型仅有旧类型时不再填入全目录，历史不当当前候选。抽取历史读取、共用频率计算，保留分母、排序和未知；单项图卡维持两列，无图类型不留空图高度。

606查询及15组核心目录旧新结果一致；132项相关检查通过，最终布局后10项复核有重叠，当前源码原生60项通过。模拟70/80/90%明确不是实际统计，隐藏抓图不作可见证据；假窗口夹具错误的独立复现保留。实际3次公开GET读到481984条总记录，更新仍为2026-10-01且计数与随包一致，不是新DLC2概率。最终测试窗已更新打开，启动区间六处私人状态保持。功能仍440、441未启动；全程序回顾、视频全部一致及P3/P2/P1未完成，full-440只证明原冻结来源。回执：`verification/maintenance/node-card-review-20261031/summary.json`。
<!-- node-card-review-20261031:end -->

'''
for n in('WORK_IN_PROGRESS.md','PROJECT_COMPLETED.md'):
    t=(R/n).read_text('utf8');assert '<!-- node-card-review-20261031:start -->'not in t;text(n,entry+t)
t=(R/'PROJECT_PROGRESS.md').read_text('utf8').replace('核对其余资料入口、固定作战完整数据/实际时钟、缺图和视频交互/外观','核对其余资料入口、固定作战完整数据/实际时钟、完整条件统计的证据、缺图和视频交互/外观');text('PROJECT_PROGRESS.md',t)
cp=read('DEVELOPMENT_CHECKPOINT.json');cp['current_maintenance_save']={'kind':'implementation_maintenance','title':summary['title'],
    'receipt':'verification/maintenance/node-card-review-20261031/summary.json','binding':'enclosing_commit','functional_section_added':False,
    'status':'partial_program_review_shared_public_source_and_node_history_checked','review_checklist':'PROGRAM_REVIEW.md',
    'review_checklist_sha256':pin('PROGRAM_REVIEW.md')['sha256'],'application_review_complete':False}
cp['current_batch']['receipt']='verification/maintenance/node-card-review-20261031/summary.json'
cp['next_action']='继续完整程序回顾：地图卡片与视频的尺寸/图卡/交互差异、其余资料窗口和状态/强化连续场景；完整条件概率及机制需独立证据，不把10月1日公开频率当当前DLC概率。已完成统计共享和历史入口不重复推进，识别优化最后。'
text('DEVELOPMENT_CHECKPOINT.json',json.dumps(cp,ensure_ascii=False,indent=2)+'\n')
m=runpy.run_path(str(R/'scripts/update_cloud_index.py'));m['update'](R);assert m['validate_delivery'](R,cp)['current_section']==440
(base/'record-source.py').write_bytes(Path(__file__).read_bytes())
print(json.dumps({'recorded':True,'selected_tests':132,'native_current_checks':60,'full_ordered_selectors':694,'whole_program_complete':False}))
