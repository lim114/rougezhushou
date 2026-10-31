from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import ast,difflib,json,re,runpy,subprocess,sys
R=Path.cwd();BASE='e56f0bf8552881ceabf994974bab0f18fd1f784f';stem='inventory-layout-20261101';B=R/'verification/maintenance'/stem;research=R/'research'/stem
title='收藏品窗口比例、紧凑网格与可展开资料说明'
def read(n):return json.loads((R/n).read_bytes())
def write(n,v):(R/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf8')
def pin(n):
 p=R/n;raw=p.read_bytes();return {'path':p.relative_to(R).as_posix(),'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}
def save(n,s):
 p=R/n
 if not p.exists():p.write_text(s,'utf8');return
 a=p.read_bytes().decode('utf8').splitlines(keepends=True);b=s.splitlines(keepends=True)
 for x,y,k in difflib.SequenceMatcher(None,[v.rstrip('\r\n')for v in a],[v.rstrip('\r\n')for v in b],autojunk=False).get_matching_blocks():b[y:y+k]=a[x:x+k]
 p.write_bytes(''.join(b).encode('utf8'))
assert subprocess.check_output(['git','rev-parse','HEAD']).decode().strip()==BASE
assert subprocess.check_output(['git','branch','--show-current']).decode().strip()=='codex/p2-development'
t=read(f'verification/maintenance/{stem}/related/results.json');assert t['passed']and t['tests_run']==77 and not t['failed']and not t['errors']and not t['skipped']and not t['forbidden_external_calls']
assert read(f'verification/maintenance/{stem}/related/process.json')['actual_observed_exit']==0
ids=re.findall(r'^test_\w+ \(([^)]+)\)',(B/'related/stderr.txt').read_text('utf8'),re.M);assert len(ids)==len(set(ids))==77
n=read(f'verification/maintenance/{stem}/native-final/window.json');assert n['passed']and n['unique_checks']==50 and not n['source_drift']and not any(n['external_operation_attempts'].values())
for path,digest in n['source_sha256_after'].items():assert sha256((R/path).read_bytes()).hexdigest()==digest,path
geo=read(f'verification/maintenance/{stem}/native-final/geometry.json');before_geo=read(f'verification/maintenance/{stem}/before/geometry.json');assert [r['columns']for r in geo['rows']]==[6,9,12]and[r['actual_height']for r in geo['rows']]==[560]*3
images=geo['images']+n['screenshots'];assert len(images)==5
for row in images:assert sha256((R/row['file']).read_bytes()).hexdigest()==row['sha256']
write(f'verification/maintenance/{stem}/native-final/root-image-review.json',{'all_five_current_owned_PNG_actually_viewed':True,'images':images,'synthetic_public_fixture_not_actual_user_inventory':True,'appearance_not_substitute_for_interactions':True,'video_full_parity_complete':False})
write(f'verification/maintenance/{stem}/native-final/observed-exit.json',{'actual_observed_exit':0,'actual_tool_exec_session':27760,'native_process_id':n['process_id'],'outer_Popen_PID_not_invented':True})
changes={}
allowed={'player_compact':{'ToolPopover.__init__','CompactAssistant.open_inventory'},'player_inventory':{'InventoryPanel.__init__','InventoryPanel.refresh'},'player_catalog_grid':{'CatalogGrid.set_tile_size'},'player_resource_strip':{'ResourceStrip.__init__'}}
def methods(raw):return {c.name+'.'+f.name:ast.dump(f,include_attributes=False)for c in ast.parse(raw).body if isinstance(c,ast.ClassDef)for f in c.body if isinstance(f,ast.FunctionDef)}
for leaf,expected in allowed.items():
 path='rouge/'+leaf+'.py';raw=(research/('before-'+leaf+'.py')).read_bytes();assert raw==subprocess.check_output(['git','show',BASE+':'+path]);a,b=methods(raw),methods((R/path).read_bytes());changed={key for key in a.keys()&b.keys()if a[key]!=b[key]};assert a.keys()==b.keys()and changed==expected,(leaf,changed)
 changes[path]={'changed_methods':sorted(changed),'other_method_AST_unchanged':True,'added_or_removed_methods':0}
sources=[*('rouge/'+k+'.py'for k in allowed),'scripts/verify_full_available.py','tests/test_inventory_layout_review.py']
assets=list((R/'rouge/data/player-theme').rglob('*'));assets=[p for p in assets if p.is_file()];assert len(assets)==127
for p in assets:assert p.read_bytes()==subprocess.check_output(['git','show',BASE+':'+p.relative_to(R).as_posix()])
sys.path.insert(0,str(R/'scripts'));ns={'__name__':'baseline_density_selectors','__file__':str(R/'scripts/verify_full_available.py')};exec(compile(subprocess.check_output(['git','show',BASE+':scripts/verify_full_available.py']),ns['__file__'],'exec'),ns)
from verify_full_available import maintained_selectors
old,new=ns['maintained_selectors'](),maintained_selectors();assert len(old)==730 and len(new)==731 and new[:-1]==old and new[-1]=='tests.test_inventory_layout_review'
write(f'verification/maintenance/{stem}/source-review.json',{'base_commit':BASE,'changed_or_new_sources':{p:pin(p)for p in sources},'method_AST_review':changes,'application_source_files':539,'new_application_modules':0,'new_low_probability_defensive_layer':False,'no_formula_or_OCR_algorithm_change':True,'external_resources_127_unchanged':True,'Qt_BSD_flow_layout_unchanged':True,'whole_program_code_constraints_complete':False,'old_selector_order_preserved':True,'ordered_selectors_before':730,'ordered_selectors_after':731,'full_suite_rerun':False,'REA_scope':'Complete Python source reviewed directly per REA instructions. No new REA invocation or whole-program proof.'})
write(f'research/{stem}/sources.json',{'video':{'local_original_sha256':'0b83e44f0816508ef095120961496337e6bd65d5f531ee350c078950dfb98bda','reference_seconds':172,'reused_unchanged_frame_and_prior_view':'Previous theme batch viewed current extracted172.png. This batch compares that reference with current owned screenshots; no entire continuous playback claim.','link':'https://www.bilibili.com/video/BV15Eaa6AErJ/','target_source_retrieval':'Targeted web search returned the author video but did not yield licensed original program source in this search. Not a claim that no such repository exists.'},'external_code_reused':{'PyQtDarkTheme':'rouge/data/player-theme/source.json','prior_actual_adoption_receipt':'verification/maintenance/player-theme-20261101/summary.json','all127_static_files_unchanged':True,'Qt_flow_layout':'rouge/flow_layout.py','flow_source_version':'Qt for Python6.11.2, original BSD attribution retained','local_adaptation':'Window hierarchy/spacing and resource QWidget size policy only; no new UI framework or claim to original video source.','official_size_policy_documentation':'https://doc.qt.io/qt-6/qsizepolicy.html#Policy-enum','official_layout_documentation':'https://doc.qt.io/qt-6/qlayout.html#sizeConstraint-prop'}})
for leaf in('probe_inventory_minimum.py','probe_inventory_minimum2.py'):(B/leaf).write_bytes((R/'.cache'/leaf).read_bytes())
(B/'related/run-source.py').write_bytes((R/'.cache/run_density_related.py').read_bytes())
write(f'verification/maintenance/{stem}/size-policy-investigation.json',{'observed_before_policy_change':{'owned_dialog_size':[1200,680],'minimum_size':[419,680],'root_layout_minimum':[419,680],'root_total_height_for_width':{'480':591,'640':560,'900':544,'1200':515},'resource_widget_size_hint':[105,305]},'observation_format':'Values transcribed from actual probe console; not original redirected stdout. Original native receipts retained.','SetNoConstraint_candidate':'Initial1200x540 possible, subsequent widths returned to680; not adopted.','adopted':'QSizePolicy.Preferred instead of Minimum for ResourceStrip vertical size. Original Qt flow implementation unchanged.','final_width_height_columns':geo['rows'],'before_width_height_columns':before_geo['rows'],'before_and_after_actual_heights_differ':'Both requested560; before clamped714, final560. Do not call equal-area comparison or performance gain.','first_probe_failure':'minimum-probe/window.json: own harness skipped445 prerequisite but final wrapper still required player_source_map_image. No product defect inferred; second probe calls original445.','final_default_requested_and_actual_logical_size':[1200,540],'full_cross_screen_DPI_coverage':False})
write(f'verification/maintenance/{stem}/failure-disposition.json',{'no_related_or_current_native_product_failures':True,'own_probe_failure':'minimum-probe/window.json','probe_failure_actual_observed_exit':1,'probe2_actual_observed_exit':0,'intermediate_after_43_not_current_final50':['after/window.json','after-policy/window.json'],'first_16_smoke_tests_included_in77_not_added':True,'complete_inventory_claim_fix':'Both summary and expanded status now use existing inventory_summary qualified quantities/members, not inventory_verified flag alone. Conflicting count case tested.','new_layers_or_weakened_source_checks':False})
live=read(f'verification/maintenance/{stem}/live-window/window.json');assert live['passed']and live['private_six_paths_unchanged']
status=read('.cache/inventory-layout-live-status.json');assert status['toolbar_visible']and status['inventory_visible']and status['elapsed_since_launch']>34
write(f'verification/maintenance/{stem}/live-window/desktop-review.json',{'actual_Windows_mcp_toolbar_region_physical_pixels':[2120,1450,2544,1520],'toolbar_actually_viewed':True,'actual_owned_visible_responding_inventory_HWND':16322232,'actual_owned_inventory_PID':18828,'Qt_status_inventory_and_toolbar_visible':True,'fresh_timer_advanced':True,'startup_six_private_paths_unchanged':True,'no_game_input_or_chat_or_private_restore':True,'private_inventory_screenshot_not_archived':True})
private=read('.cache/inventory-layout-before.json')['private'];changed=[p for p,h in private.items()if(sha256((R/p).read_bytes()).hexdigest()if(R/p).is_file()else None)!=h]
write(f'verification/maintenance/{stem}/private-scope.json',{'six_private_paths_unchanged_whole_batch':not changed,'changed_paths_if_any':changed,'origin_not_inferred_and_no_rollback':True,'private_contents_and_hashes_not_published':True})
save(f'research/{stem}/README.md',f'''# {title}

基线{BASE}，本轮为界面维护，功能仍445、446未开始。全程序与原片全部功能/交互/外观未完成。

## 参考与实现选择

以未变原片172秒收藏品窗为对照，原窗单独标题、资源行、长说明及常驻动作占空间。沿用已实际采用的外部PyQtDarkTheme静态QSS/图标和Qt官方BSD Flow Layout；127份主题资源及Flow源码整字节不变，许可保留。本轮定向检索没有取得可供改造的原程序授权源码，不从搜索未命中推断不存在；不把本机布局胶合代码称为复用原视频源码。完整第三方来源和官方布局文档见sources.json。

资源并入标题位置，正文上方保留分类/搜索与简短持有状态；全部来源/适用范围文字可展开阅读，资料不可用和清单不完整仍直接显示。所选藏品的来源、完整条目及交换入口随说明区展开/收起，既有信号和精确身份保持。用原inventory_summary判断读全，修正仅凭flag就显示完整的问题，矛盾数量有实际检查。

库存初始图标60，可调48–104；共享图册减少图标两侧空白但保留名字、原图、身份和键盘阅读。默认在本机实际达到1200×540逻辑尺寸，按屏幕可用范围限制请求；不能据此称所有显示器/缩放已覆盖。原片仍有顶部一行排列、部分图标/比例及其它交互差异；其它图册长说明、地图、笔记和历史排版仍待对照。

## 实际问题与验证

只改默认大小时窗口仍被撑到680高。实测根布局在1200宽需约515高，资源Widget却以其窄最小宽度推算出305高的sizeHint，并被Minimum纵向策略当作下限。SetNoConstraint隔离候选缩放后仍回680，未采用；最终改为Preferred，让已有按宽度换行参与实际分配，不关闭布局管理或加入固定高度补丁。初始探查漏掉445夹具前置导致一条自有验收失败，原件保留，第二轮按正确流程执行，不冒充产品缺陷。

最终77个不同相关测试、50项当前原生唯一检查均通过，实际进程退出0。覆盖库存筛选/读全、来源失效/恢复不追选、固定来源阅读、条目/敌人等共享图册、资源鼠标入口与多宽度换行。640/900/1200宽原生实测，资源十项无重叠或裁切，三种其它目录的小窗底部可见；地图共享资源条另查。初始16项包含于77中、不相加；中间43项与旧28项亦不累计成当前总数。

同请求宽度1200时每行9→12件；请求高560时原实现实际被撑714、当前560，宽640/900/1200分别6/9/12列。高度和默认图标大小都已改变，不能称相同面积、同图标大小的公平密度基准，更不是OCR、启动耗时或FPS提升。五张当前隔离原图已实际查看，公共合成80件不是用户本局库存；外观不代替交互证据。

实际项目测试窗已更新并打开收藏品窗，Win32可见响应且Qt计时器推进；Windows-mcp查看实际工具条。启动六私人路径保持，整批仅本机摘要核对，无私人值/哈希或实际库存截图进入公开归档；不操作游戏、不发聊天、不清空记录。731登记选择器保留旧730次序；本轮未跑全量，下次455，full440只证明其旧来源。

[本批回执](../../verification/maintenance/{stem}/summary.json)。
''')
summary={'kind':'implementation_review_maintenance','section':445,'title':title,'passed':True,'functional_section_added':False,'baseline_commit':BASE,'changed_source':{p:pin(p)['sha256']for p in sources},'necessary_distinct_tests':77,'native_unique_checks':50,'native_receipt':pin(f'verification/maintenance/{stem}/native-final/window.json'),'source_review':pin(f'verification/maintenance/{stem}/source-review.json'),'whole_program_review_complete':False,'whole_video_parity_complete':False,'P3_P2_P1_complete':False,'goal_active':True,'next_full_section':455,'at_UTC':datetime.now(timezone.utc).isoformat()};write(f'verification/maintenance/{stem}/summary.json',summary)
entry=f'''<!-- {stem}:start -->
## 界面实现维护 · {title}

资源并入标题行，完整资料说明可展开，持有完整性/资料失效仍直接显示；条目动作随说明区收起，窗口比例与图册间距调整。修正资源栏Minimum尺寸策略撑高窗口、单独flag误称读全的问题；外部主题127资源与Qt BSD Flow源码保持。

77项不同相关检查、50项当前原生检查通过，五张隔离原图已看；640/900/1200宽资源无重叠或裁切，默认本机实际1200×540。旧探查夹具失败/未采用方案保留，不累计中间测试。同宽每行9→12件，高度/图标也变，不称等面积基准或性能提升。实际测试窗已更新并打开库存，启动六私人路径保持。功能445、446未开，下次完整455；全程序/视频、P3/P2/P1未完成。[回执](verification/maintenance/{stem}/summary.json)。
<!-- {stem}:end -->

'''
for path in('WORK_IN_PROGRESS.md','PROJECT_COMPLETED.md'):
 s=(R/path).read_text('utf8')
 if path=='WORK_IN_PROGRESS.md':s=s[s.index('<!-- player-theme-20261101:start -->'):]
 save(path,entry+s)
path='PROGRAM_REVIEW.md';s=(R/path).read_text('utf8').replace('资源/标题密度与窗口比例、其它窗口及游戏叠加层与视频逐页对应。','其它图册的长说明、导航与窗口比例、其余窗口及游戏叠加层与视频逐页对应。',1);save(path,s+f'\n[收藏品密度与尺寸回顾](research/{stem}/README.md)覆盖紧凑网格、可展开范围、动作归位和资源纵向策略；77项相关/50项原生只证明当前所列范围，原片仍有顶部排列和其它页差异。\n')
path='PROJECT_PROGRESS.md';s=(R/path).read_text('utf8').replace('资源和说明密度、标题占用、窗口比例及其余界面的布局、字体、图标、间距与浮窗呈现逐页对齐','收藏品顶部导航/资源的一行排列与其余窗口比例、其它图册长说明/默认阅读、其余界面的布局、字体、图标、间距与浮窗呈现逐页对齐',1);save(path,s)
path='IMPLEMENTATION_STRATEGY.md';s=(R/path).read_text('utf8').replace('下一步集中处理资源/说明密度、比例及剩余页面。','库存密度/展开说明和实际默认尺寸已完成本机所列范围；下一步核对顶部导航排列、其它图册长说明及剩余页面。',1);save(path,s+f'\n[库存布局维护](research/{stem}/README.md)复用已采用的外部主题与Qt布局，仅作本机胶合；实际高度/多宽度而非默认数字参与验收。\n')
path='VIDEO_PARITY.md';s=(R/path).read_text('utf8');mark='## 工具条与自动关联';assert mark in s;s=s.replace(mark,f'本轮[收藏品窗口](research/{stem}/README.md)已收拢重复标题和长说明/动作、调整网格与实际默认比例；保持所有可展开范围说明，修复资源栏撑高和矛盾数量误称完整。原片172秒的顶部一行排列及其它图册长说明、窗口间距/比例仍需对照，未宣称全视频一致。\n\n'+mark,1);save(path,s)
path='PROJECT_REQUIREMENTS.md';s=(R/path).read_text('utf8');mark='P3→P2→P1；';assert mark in s;s=s.replace(mark,'紧凑窗口须以实际可见尺寸和内容核对，不以resize请求数字代替；完整适用范围可折叠，但持有清单不完整、资料失效仍直接显示，读全须使用数量/成员相符的已有口径。移动条目操作区时保留选择、来源与阅读状态。\n\n'+mark,1);save(path,s)
cp=read('DEVELOPMENT_CHECKPOINT.json');assert cp['completed_sections']==445 and cp['next_section']==446
cp['current_maintenance_save']={'kind':'implementation_maintenance','title':title,'receipt':f'verification/maintenance/{stem}/summary.json','binding':'enclosing_commit','functional_section_added':False,'status':'partial_inventory_layout_video_adaptation','review_checklist':'PROGRAM_REVIEW.md','review_checklist_sha256':pin('PROGRAM_REVIEW.md')['sha256'],'application_review_complete':False}
cp['current_batch']['receipt']=f'verification/maintenance/{stem}/summary.json';cp['current_batch']['scope']='Whole-program/video review remains active. Functional445 unchanged; inventory layout, source explanation/action grouping and resource vertical policy improved. Top navigation arrangement, other readers and game overlay still pending.446 not started.'
cp['next_action']='继续对照原片处理收藏品顶部导航排列、其它图册长说明/默认阅读、笔记/历史及剩余窗口比例和交互；优先采用成熟外部代码并本地化，保留静态主题与本轮尺寸/阅读状态修正。MaaFw多页面连续等条件比较和OCR同步；全程序/视频及P3/P2/P1未完成。445保持、446未启动、下次完整455。'
save('DEVELOPMENT_CHECKPOINT.json',json.dumps(cp,ensure_ascii=False,indent=2)+'\n');idx=runpy.run_path(str(R/'scripts/update_cloud_index.py'));idx['update'](R);assert idx['validate_delivery'](R,cp)['current_section']==445
write(f'verification/maintenance/{stem}/final-audit.json',{'passed':True,'functional_section':445,'functional_section_added':False,'next_section':446,'current_distinct_tests':77,'native_unique_checks':50,'ordered_selectors':731,'next_full':455,'current_full_rerun':False,'requirements':pin('PROJECT_REQUIREMENTS.md'),'index':pin('CLOUD_INDEX.json'),'maintenance_receipt':pin(f'verification/maintenance/{stem}/summary.json'),'goal_active':True,'whole_program_or_video_complete':False})
(B/'record-source.py').write_bytes(Path(__file__).read_bytes());files={p.relative_to(R).as_posix():{k:v for k,v in pin(p.relative_to(R)).items()if k!='path'}for p in B.rglob('*')if p.is_file()and p.name!='archive-manifest.json'};write(f'verification/maintenance/{stem}/archive-manifest.json',{'kind':'explicit_public_archive_no_private_contents_or_expected_values','files':files})
print(json.dumps({'recorded':True,'functional_section':445,'new_functional_section':False,'related_tests':77,'native_unique_checks':50,'ordered_selectors':731,'public_archive_files':len(files),'whole_batch_six_private_unchanged':not changed,'whole_goal_complete':False}))
