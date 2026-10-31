from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import ast,difflib,json,re,runpy,subprocess,sys
R=Path.cwd();BASE='2bebbf4e48c654b2119e01fee4d22ba913d09795';stem='catalogue-header-20261101';B=R/'verification/maintenance'/stem;research=R/'research'/stem
title='顶部分页与资源同行，道具、零件和商店阅读统一'
def read(n):return json.loads((R/n).read_bytes())
def write(n,v):(R/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf8')
def pin(n):
 p=R/n;b=p.read_bytes();return {'path':p.relative_to(R).as_posix(),'sha256':sha256(b).hexdigest(),'bytes':len(b)}
def save(n,s):
 p=R/n
 if not p.exists():p.write_text(s,'utf8');return
 a=p.read_bytes().decode('utf8').splitlines(keepends=True);b=s.splitlines(keepends=True)
 for x,y,k in difflib.SequenceMatcher(None,[v.rstrip('\r\n')for v in a],[v.rstrip('\r\n')for v in b],autojunk=False).get_matching_blocks():b[y:y+k]=a[x:x+k]
 p.write_bytes(''.join(b).encode('utf8'))
assert subprocess.check_output(['git','rev-parse','HEAD']).decode().strip()==BASE
assert subprocess.check_output(['git','branch','--show-current']).decode().strip()=='codex/p2-development'
t=read(f'verification/maintenance/{stem}/related-final/results.json');assert t['passed']and t['tests_run']==83 and not t['failed']and not t['errors']and not t['skipped']and not t['forbidden_external_calls']
assert read(f'verification/maintenance/{stem}/related-final/process.json')['actual_observed_exit']==0
ids=re.findall(r'^test_\w+ \(([^)]+)\)',(B/'related-final/stderr.txt').read_text('utf8'),re.M);assert len(ids)==len(set(ids))==83
n=read(f'verification/maintenance/{stem}/native-final/window.json');assert n['passed']and n['unique_checks']==62 and not n['source_drift']and not any(n['external_operation_attempts'].values())
for p,h in n['source_sha256_after'].items():assert sha256((R/p).read_bytes()).hexdigest()==h,p
detail=read(f'verification/maintenance/{stem}/native-final/details.json');assert [r['actual_size']for r in detail['geometry']]==[[480,560],[640,560],[900,560],[1200,560]]
images=detail['images']+n['screenshots'];assert len(images)==11
for row in images:assert sha256((R/row['file']).read_bytes()).hexdigest()==row['sha256']
unique={row['sha256']:row['file']for row in images};assert len(unique)==10
write(f'verification/maintenance/{stem}/native-final/root-image-review.json',{'actual_current_unique_images_viewed':10,'image_file_entries':11,'images':images,'window_png_byte_identical_to_final_inventory_png':True,'public_synthetic_fixture_not_user_run':True,'appearance_not_substitute_for62_window_checks':True,'whole_video_complete':False})
write(f'verification/maintenance/{stem}/native-final/observed-exit.json',{'actual_observed_exit':0,'actual_tool_exec_session':41826,'native_process_id':n['process_id'],'outer_PID_not_invented':True})
allowed={'player_compact':({'CompactAssistant.refresh','CompactAssistant.open_inventory'},set()),'player_catalog_grid':({'add_catalog_controls'},set()),'player_parts':({'PartsPanel.__init__','PartsPanel.refresh'},set()),'player_tools':({'ToolsPanel.__init__','ToolsPanel.refresh'},set()),'player_shop_memory':({'ShopMemoryPanel.__init__','ShopMemoryPanel.show_snapshot','ShopMemoryPanel.selected'},set()),'player_resource_strip':({'ResourceStrip.__init__'},{'ResourceStrip.resizeEvent'})}
def funcs(raw):
 tree=ast.parse(raw);out={f.name:ast.dump(f,include_attributes=False)for f in tree.body if isinstance(f,ast.FunctionDef)}
 for cls in tree.body:
  if isinstance(cls,ast.ClassDef):out.update({cls.name+'.'+f.name:ast.dump(f,include_attributes=False)for f in cls.body if isinstance(f,ast.FunctionDef)})
 return out
changes={}
for leaf,(expected,added)in allowed.items():
 path='rouge/'+leaf+'.py';before=(research/('before-'+leaf+'.py')).read_bytes();assert before==subprocess.check_output(['git','show',BASE+':'+path]);after=(R/path).read_bytes();a,b=funcs(before),funcs(after)
 changed={k for k in a.keys()&b.keys()if a[k]!=b[k]};assert changed==expected and b.keys()-a.keys()==added and not a.keys()-b.keys(),(leaf,changed)
 assert sum(isinstance(x,ast.Try)for x in ast.walk(ast.parse(before)))==sum(isinstance(x,ast.Try)for x in ast.walk(ast.parse(after)))
 changes[path]={'changed_functions':sorted(changed),'added_functions':sorted(added),'other_function_AST_unchanged':True,'try_count_unchanged':True}
sources=[*('rouge/'+k+'.py'for k in allowed),'scripts/verify_full_available.py','tests/test_catalogue_header_review.py']
subprocess.run(['git','diff','--exit-code',BASE,'--','rouge/data/player-theme','rouge/flow_layout.py'],check=True,stdout=subprocess.PIPE)
sys.path.insert(0,str(R/'scripts'));ns={'__name__':'catalogue_baseline_selectors','__file__':str(R/'scripts/verify_full_available.py')};exec(compile(subprocess.check_output(['git','show',BASE+':scripts/verify_full_available.py']),ns['__file__'],'exec'),ns)
from verify_full_available import maintained_selectors
old,new=ns['maintained_selectors'](),maintained_selectors();assert len(old)==731 and len(new)==732 and new[:-1]==old and new[-1]=='tests.test_catalogue_header_review'
write(f'verification/maintenance/{stem}/source-review.json',{'base_commit':BASE,'changed_or_new_sources':{p:pin(p)for p in sources},'function_AST_review':changes,'application_source_files':539,'new_application_modules':0,'new_low_probability_defensive_layer':False,'formula_OCR_shop_record_qualification_and_part_tool_row_models_unchanged':True,'external127_theme_files_and_BSD_Flow_source_Git_diff_unchanged':True,'old731_selector_order_preserved':True,'ordered_selectors_after':732,'full_suite_rerun':False,'REA_scope':'Complete Python source -> direct source/runtime review per REA instructions; no new REA invocation or entire-program conclusion.','whole_program_review_complete':False})
(B/'related-final/run-source.py').write_bytes((R/'.cache/run_catalogue_related.py').read_bytes())
write(f'verification/maintenance/{stem}/failure-disposition.json',{'first_15_tests':'first-test-fixture-error/failure.json','actual_initial_exit':1,'reason':'Own tool failure test patched nonexistent alias source; changed to actual expansion_reference alias. Original test preserved; no product error inferred.','final83_distinct_tests':'related-final/results.json','first54_window_checks':'after/window.json','narrow_header_observation':'Initial640 width forced seven resource rows/212 height, actual dialog650. Tests checked chips but did not require composite wrapping.','repair':'Navigation/crew and seven resource labels now share the unchanged Qt Flow Layout, and leading widget max widths follow actual ResourceStrip resize. No fixed resolution template or new fallback framework.','responsive62_before_final_selector_freeze':'after-responsive/window.json','current62':'native-final/window.json','repeated_parts_source_loss':'Error summary moved before equal-row early return; three consecutive failures verified without resetting state.','shop_reading':'Only replace exact detail text when it changes; cursor remains on old chosen snapshot after new observation or save issue update.','source_validation_weakened':False,'intermediate_checks_not_added_to83_or62':True})
write(f'research/{stem}/sources.json',{'video':{'source':'project local original mp4,172-second inventory reference','sha256':'0b83e44f0816508ef095120961496337e6bd65d5f531ee350c078950dfb98bda','basis':'Unchanged source/frame and previously actually viewed172-second reference reused; current native pages viewed. No new entire-video continuous playback claim.','url':'https://www.bilibili.com/video/BV15Eaa6AErJ/'},'production_reuse':{'PyQtDarkTheme':'rouge/data/player-theme/source.json, existing fixed MIT static assets unchanged','Qt_BSD_Flow':'rouge/flow_layout.py unchanged, original attribution retained','official_QTabBar':'https://doc.qt.io/qt-6/qtabbar.html','official_QSplitter':'https://doc.qt.io/qt-6/qsplitter.html','local_glue':'Standard Qt navigation and splitter with adopted external theme; no new UI framework dependency. Not original Tab program source or full external application transplant.'}})
status=read('.cache/catalogue-header-live-status.json');assert status['toolbar_visible']and status['inventory_visible']and status['elapsed_since_launch']>54
live=read(f'verification/maintenance/{stem}/live-window/window.json');assert live['passed']and live['private_six_paths_unchanged']
write(f'verification/maintenance/{stem}/live-window/desktop-review.json',{'actual_Windows_mcp_toolbar_region':[2120,1450,2544,1520],'toolbar_actually_viewed':True,'live_owned_PID':18792,'Qt_toolbar_and_inventory_visible_timer_advanced':True,'startup_six_private_paths_unchanged':True,'actual_private_inventory_screenshot_not_archived':True,'game_operated_or_chat_sent':False})
private=read('.cache/catalogue-header-before.json')['private'];changed=[p for p,h in private.items()if(sha256((R/p).read_bytes()).hexdigest()if(R/p).is_file()else None)!=h]
write(f'verification/maintenance/{stem}/private-scope.json',{'six_private_paths_unchanged_whole_batch':not changed,'changed_paths_if_any':changed,'origin_not_inferred_and_no_rollback':True,'private_contents_and_hashes_not_published':True})
save(f'research/{stem}/README.md',f'''# {title}

基线{BASE}。本轮为维护，功能445保持、446未开始；全程序/P3/P2/P1与全部视频效果未完成。

## 实现及依据

继续采用已接入的PyQtDarkTheme静态控件状态/图标和Qt官方BSD Flow Layout，不增加主题运行库、框架或重新复制一套列表。用Qt现成QTabBar双向关联原四份分页，原QTabWidget及页面身份保持；QSplitter按Qt官方隐藏/恢复子窗规则承载左图册/右说明，本地只做既有数据和布局胶合。127份主题资源和Flow原代码不改，许可保留。不声称已经取得原视频程序源码、整套外部业务实现或全程序完成。来源见sources.json。

原片172秒分类与资源同处顶部：本轮宽1200时实际同一行，窄窗由同一Flow自然换行，不以固定分辨率切模板。初版把导航独立放在资源左侧，640宽资源被挤成7行、212高；改为共同排列，640宽资源区66高、窗口实际560高，480宽资源区99高。资源行数不包括导航所在行，不能混称整栏行数；当前四宽/一套DPI不能代表全部屏幕。

收藏品标签只列已确认收藏品；道具独列数量，不用包含道具的游戏合计冒充收藏品数。完整读全使用原inventory_summary口径；合计/来源说明保留在标签提示与展开资料。零件数量/容量仍是已读数量，不是成员清单。干员按钮沿用原队伍入口；明确页面跳转与键盘选择保持同步，刷新不跳回默认页。

三份道具/零件/商店图册使用同一可收起侧栏与底部图标大小/资料说明控件，初始图标60、可调48–104；条目专用动作随阅读区收起。完整来源文字可展开，资料不可用、零件成员未读、商品不代表在售/持有和未保存继续直接说明。未改固定数据、资格校验、统计、公式、OCR或真实游戏采样。

## 发现并修正

零件源连续不可用时，第二轮相同行早退会把错误提示覆盖回普通说明；现先更新错误状态，三次连续失败后仍保持提示与空列表，恢复不追选。商店新增一份记录/保存问题更新时，仍读旧记录会重设完全相同正文而丢光标；现仅文字改变才重设。合成公开记录的正位置光标8保持，不把它称为所有历史/游标场景完成。

首轮15项测试有1个自有夹具错误：patch了不存在的source别名。改为真实expansion_reference别名；原测试和实际退出保留，不冒充产品错误。最终83项不同相关检查、62项当前原生唯一检查通过，实际进程退出0，外部游戏/聊天调用均零；原28/54/62中间检查、首轮15不与最终相加。480/640/900/1200实际尺寸分别为请求宽×560，全部导航/干员/资源框都在同一资源区内、无重叠，键盘切换与程序跳转双向同步；组件层360宽另测。

当前11个图片条目共10份不同字节，主代理已实际查看10份；window.png与final-inventory.png整字节相同。公开合成50件收藏品/1件道具/7个零件数量及1970测试时刻不是用户本局或实机读取，图片不替代交互证明。实际项目测试窗已更新并打开库存，Win32启动可见响应、Qt计时推进，Windows-mcp查看实际工具条；不改焦点、不操作游戏或发聊天。私人六路径启动保持，整批只作本机摘要比较，不公开内容/哈希或实际库存截图。

732登记选择器保留旧731次序，本轮未跑全量，下次455；full440仍只证明旧冻结源码。地图、笔记、历史、剩余图文/交互与原片合并筛选的准确口径、真实连续游戏/跨屏等仍有缺口，不称整体已一致，也无OCR/FPS或启动提速结论。

[维护回执](../../verification/maintenance/{stem}/summary.json)。
''')
summary={'kind':'implementation_review_maintenance','section':445,'title':title,'passed':True,'functional_section_added':False,'baseline_commit':BASE,'changed_source':{p:pin(p)['sha256']for p in sources},'necessary_distinct_tests':83,'native_unique_checks':62,'native_receipt':pin(f'verification/maintenance/{stem}/native-final/window.json'),'source_review':pin(f'verification/maintenance/{stem}/source-review.json'),'whole_program_review_complete':False,'whole_video_parity_complete':False,'P3_P2_P1_complete':False,'goal_active':True,'next_full_section':455,'at_UTC':datetime.now(timezone.utc).isoformat()};write(f'verification/maintenance/{stem}/summary.json',summary)
entry=f'''<!-- {stem}:start -->
## 界面实现维护 · {title}

原四分页由Qt导航与资源共同换行；收藏品/道具独立数量，零件数量不当成员库存。道具/零件/商店共用可收起侧栏，完整资料可展开而失效、未读与未保存直接显示。修正连续零件源失效提示被早退覆盖、旧商店阅读被同文刷新重置；外部主题127资源及Qt BSD Flow源码保持。

83项不同相关检查、62项当前原生检查通过；480/640/900/1200宽导航/资源无重叠或裁切，宽1200实为一行，窄窗共同换行。11图条目中10份不同原图已看；首轮自有别名夹具错误保留。实际测试窗更新并打开库存，启动六私人路径保持。功能445、446未开、下次完整455；地图/笔记/历史和其余视频效果、P3/P2/P1未完成。[回执](verification/maintenance/{stem}/summary.json)。
<!-- {stem}:end -->

'''
for p in('WORK_IN_PROGRESS.md','PROJECT_COMPLETED.md'):
 s=(R/p).read_text('utf8')
 if p=='WORK_IN_PROGRESS.md':s=s[s.index('<!-- inventory-layout-20261101:start -->'):]
 save(p,entry+s)
p='PROJECT_PROGRESS.md';s=(R/p).read_text('utf8').replace('收藏品顶部导航/资源的一行排列与其余窗口比例、其它图册长说明/默认阅读、其余界面的布局、字体、图标、间距与浮窗呈现逐页对齐','地图/笔记/历史及其余窗口的比例、布局、字体、图标、间距与浮窗呈现逐页对齐；核对并实现原片藏品合并筛选的准确口径与操作，不擅自合并独立变体身份或效果',1);save(p,s)
p='PROGRAM_REVIEW.md';s=(R/p).read_text('utf8').replace('其它图册的长说明、导航与窗口比例、其余窗口及游戏叠加层与视频逐页对应。','地图/笔记/历史及其余资料的间距与呈现、原片合并筛选的准确口径、其余窗口与游戏叠加层逐项对应。',1);save(p,s+f'\n[顶部分页和三类图册回顾](research/{stem}/README.md)实际核对共同换行、独立数量、侧栏动作和阅读/连续失效；83项相关与62项原生范围不代表整个程序或视频完成。\n')
p='IMPLEMENTATION_STRATEGY.md';s=(R/p).read_text('utf8').replace('下一步核对顶部导航排列、其它图册长说明及剩余页面。','顶部共同换行和三类图册侧栏已在本机所列范围核对；下一步处理原片合并筛选的准确口径、地图/笔记/历史及剩余页面。',1);save(p,s+f'\n[分页与侧栏维护](research/{stem}/README.md)使用原Qt分页、现成QTabBar/QSplitter和已采用外部主题，无新UI框架；窄窗按真实宽度排列，部件与整体视频范围分别验收。\n')
p='VIDEO_PARITY.md';s=(R/p).read_text('utf8').replace('原片172秒的顶部一行排列及其它图册长说明、窗口间距/比例仍需对照，未宣称全视频一致。',f'原片172秒的顶部同区排列及三类图册侧栏已由[本轮维护](research/{stem}/README.md)适配，宽/窄窗、独立数量和完整来源另验；其它窗口间距/比例、原片藏品合并筛选的准确口径与剩余交互仍未完成，未宣称全视频一致。',1);save(p,s)
p='PROJECT_REQUIREMENTS.md';s=(R/p).read_text('utf8');mark='P3→P2→P1；';assert mark in s;s=s.replace(mark,'顶部导航与资源应按实际可用宽度共同排列并保持键盘/直接跳转同步；收藏品、道具、包含道具的游戏合计与零件数量分开口径。条目阅读收起后刷新不强行打开，新增商店记录不抢走旧记录阅读位置；持续资料失效不得在相同行早退时隐藏提示。\n\n'+mark,1);save(p,s)
cp=read('DEVELOPMENT_CHECKPOINT.json');assert cp['completed_sections']==445 and cp['next_section']==446
cp['current_maintenance_save']={'kind':'implementation_maintenance','title':title,'receipt':f'verification/maintenance/{stem}/summary.json','binding':'enclosing_commit','functional_section_added':False,'status':'partial_video_header_and_three_catalogues','review_checklist':'PROGRAM_REVIEW.md','review_checklist_sha256':pin('PROGRAM_REVIEW.md')['sha256'],'application_review_complete':False}
cp['current_batch']['receipt']=f'verification/maintenance/{stem}/summary.json';cp['current_batch']['scope']='Whole-program/video review remains active. Functional445 unchanged; common top navigation/resources and three catalogue side readers adapted, repeated source-loss and shop reading repaired. Map/note/history, merge-filter semantics and other effects remain pending.446 not started.'
cp['next_action']='继续原片效果逐项回顾：先核对藏品合并筛选的实际口径、地图/笔记/历史等剩余页面与完整交互；优先成熟外部代码适配，保留顶部共同换行、独立数量与侧栏阅读。MaaFw多页面/连续等条件比较和OCR同步；全程序/视频及P3/P2/P1未完成。功能445、446未启动、下次完整455。'
save('DEVELOPMENT_CHECKPOINT.json',json.dumps(cp,ensure_ascii=False,indent=2)+'\n');idx=runpy.run_path(str(R/'scripts/update_cloud_index.py'));idx['update'](R);assert idx['validate_delivery'](R,cp)['current_section']==445
write(f'verification/maintenance/{stem}/final-audit.json',{'passed':True,'functional_section':445,'functional_section_added':False,'next_section':446,'current_distinct_tests':83,'native_unique_checks':62,'ordered_selectors':732,'next_full':455,'current_full_rerun':False,'requirements':pin('PROJECT_REQUIREMENTS.md'),'index':pin('CLOUD_INDEX.json'),'maintenance_receipt':pin(f'verification/maintenance/{stem}/summary.json'),'goal_active':True,'whole_program_or_video_complete':False})
(B/'record-source.py').write_bytes(Path(__file__).read_bytes());files={p.relative_to(R).as_posix():{k:v for k,v in pin(p.relative_to(R)).items()if k!='path'}for p in B.rglob('*')if p.is_file()and p.name!='archive-manifest.json'};write(f'verification/maintenance/{stem}/archive-manifest.json',{'kind':'explicit_public_archive_no_private_contents_or_expected_values','files':files})
print(json.dumps({'recorded':True,'functional_section':445,'new_functional_section':False,'related_tests':83,'native_unique_checks':62,'ordered_selectors':732,'public_archive_files':len(files),'whole_batch_six_private_unchanged':not changed,'whole_goal_complete':False}))
