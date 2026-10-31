from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import ast,difflib,json,re,runpy,subprocess,sys

R=Path.cwd();BASE='e84a78ae0bd20d21596629be241c2bb008386ceb';stem='player-theme-20261101'
B=R/'verification/maintenance'/stem;research=R/'research'/stem
title='外部主题静态适配与玩家浮窗基础控件统一'
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
tests=read(f'verification/maintenance/{stem}/related-verified/results.json')
assert tests['passed']and tests['tests_run']==98 and not tests['failed']and not tests['errors']and not tests['skipped']and not tests['forbidden_external_calls']
assert read(f'verification/maintenance/{stem}/related-verified/process.json')['actual_observed_exit']==0
ids=re.findall(r'^test_\w+ \(([^)]+)\)',(B/'related-verified/stderr.txt').read_text('utf8'),re.M);assert len(ids)==len(set(ids))==98
native=read(f'verification/maintenance/{stem}/native-verified/window.json')
assert native['passed']and native['unique_checks']==37 and not native['source_drift']and not any(native['external_operation_attempts'].values())
for n,digest in native['source_sha256_after'].items():assert sha256((R/n).read_bytes()).hexdigest()==digest,n
images=native['screenshots']+read(f'verification/maintenance/{stem}/native-verified/extra-images.json')['images'];assert len(images)==5
for row in images:assert sha256((R/row['file']).read_bytes()).hexdigest()==row['sha256']
write(f'verification/maintenance/{stem}/native-verified/root-image-review.json',{'all_five_current_owned_PNG_actually_viewed':True,'images':images,'not_substitute_for_37_native_interactions':True,'remaining_visible_gaps':['resource/header density','overall proportions and layouts','other readers','game overlay versus independent map reader'],'synthetic_state_not_user_run_or_game_validation':True})
write(f'verification/maintenance/{stem}/native-verified/observed-exit.json',{'actual_observed_exit':0,'tool_exec_session':70198,'process_id_reported_by_native_receipt':native['process_id'],'retained_tool_session_not_invented_outer_Popen_PID':True})
allowed={'player_compact':{'ToolPopover.__init__','CompactAssistant.open_replay','CompactAssistant.notes_popup','CompactAssistant.open_inventory','CompactAssistant.open_map'},'player_item_hover':{'ItemHoverCard.__init__'},'player_map_hover':{'NodeHoverCard.__init__'},'player_map_reader':{'readable'},'player_notes':{'NotesDialog.__init__'},'player_note_library':{'NoteLibraryDialog.__init__'},'player_catalog_grid':set()}
changes={}
def functions(raw):
 t=ast.parse(raw);result={n.name:ast.dump(n,include_attributes=False)for n in t.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
 for c in t.body:
  if isinstance(c,ast.ClassDef):result.update({c.name+'.'+n.name:ast.dump(n,include_attributes=False)for n in c.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))})
 return result
for name,expected in allowed.items():
 n='rouge/'+name+'.py';before=(research/('before-'+name+'.py')).read_bytes();assert before==subprocess.check_output(['git','show',BASE+':'+n])
 a,b=functions(before),functions((R/n).read_bytes());changed={k for k in a.keys()&b.keys()if a[k]!=b[k]};assert a.keys()==b.keys()and changed==expected,(name,changed)
 changes[n]={'changed_functions':sorted(changed),'added_or_removed_functions':0,'other_function_AST_unchanged':True}
sources=['pyproject.toml','rouge/player_theme.py',*('rouge/'+n+'.py'for n in allowed),'scripts/build_player_theme.py','scripts/player_ui_verification.py','scripts/verify_full_available.py','tests/test_player_theme_review.py','tests/test_scene_reader_review.py']
sources+=sorted(p.relative_to(R).as_posix()for p in(R/'rouge/data/player-theme').rglob('*')if p.is_file())
manifest=read('rouge/data/player-theme/source.json');assert len(manifest['files'])==126 and manifest['generated_from_wheel_version']=='2.1.0'
assert len(list((R/'rouge/data/player-theme/icons').glob('*.svg')))==122
for n,row in manifest['files'].items():assert pin('rouge/data/player-theme/'+n)['sha256']==row['sha256']
count=sum(1 for p in(R/'rouge').rglob('*')if p.is_file()and p.suffix in('.py','.cjs','.js'));assert count==539
sys.path.insert(0,str(R/'scripts'))
ns={'__name__':'theme_review_baseline_selectors','__file__':str(R/'scripts/verify_full_available.py')};exec(compile(subprocess.check_output(['git','show',BASE+':scripts/verify_full_available.py']),ns['__file__'],'exec'),ns)
from verify_full_available import maintained_selectors
old,new=ns['maintained_selectors'](),maintained_selectors();assert len(old)==729 and len(new)==730 and new[:len(old)]==old and new[-1]=='tests.test_player_theme_review'
write(f'verification/maintenance/{stem}/source-review.json',{'base_commit':BASE,'changed_or_new_sources':{n:pin(n)for n in sources},'method_AST_review':changes,'application_source_files':count,'new_application_modules':1,'packaged_external_asset_files':127,'production_external_adoption':'PyQtDarkTheme2.1.0 generated QSS/palette/122SVG, MIT retained; external Python runtime not shipped or installed.','REA_scope':'Complete Python source -> direct source/runtime review per REA skill. No new REA call or whole-program reverse engineering claim.','new_low_probability_defensive_layer':False,'no_formula_or_OCR_algorithm_change':True,'whole_program_code_constraints_complete':False,'ordered_selectors_before':729,'ordered_selectors_after':730,'previous_order_preserved':True,'full_suite_rerun':False})
live=read(f'verification/maintenance/{stem}/live-window-verified/window.json');assert live['passed']and live['private_six_paths_unchanged']
status=read('.cache/player-theme-verified-live-status.json');assert status['toolbar_visible']and status['elapsed_since_launch']>514
write(f'verification/maintenance/{stem}/live-window-verified/desktop-review.json',{'Windows_mcp_actual_toolbar_screenshot_region_physical_pixels':[2120,1450,2544,1520],'actual_toolbar_viewed':True,'owned_HWND':44567256,'owned_PID':28560,'visible_and_responding_Win32_rechecked':True,'Qt_timer_advanced':True,'initial_regions_used_old_coordinates_or_logical_pixels_and_did_not_show_toolbar':True,'no_focus_or_input_or_game_action':True,'startup_six_private_paths_unchanged':True,'not_full_video_or_live_game_validation':True})
before=read('.cache/player-theme-before.json')['private'];changed=[n for n,v in before.items()if(sha256((R/n).read_bytes()).hexdigest()if(R/n).is_file()else None)!=v]
write(f'verification/maintenance/{stem}/private-scope.json',{'whole_batch_private_six_unchanged':not changed,'changed_paths_if_any':changed,'change_origin_not_inferred':bool(changed),'startup_six_unchanged':True,'private_contents_hashes_images_or_expected_values_published':False,'no_private_backup_restore_or_rollback':True})
write(f'research/{stem}/external-sources.json',{'adopted':{'repository':'https://github.com/5yutan5/PyQtDarkTheme','reviewed_commit':manifest['reviewed_commit'],'docs_and_targeted_source_read':['README.md','LICENSE.txt','pyproject.toml','qdarktheme/_main.py','qdarktheme/_resources/colors.py','qdarktheme/_resources/stylesheets.py','loader/template helpers'],'license':'MIT','wheel_version':'2.1.0','wheel_hashes':read('.cache/qt-themes-446/wheels.json'),'upstream_python_requires':'>=3.7,<3.12','builder_exercised_python':manifest['build_exercised_python'],'builder_exercised_Qt':manifest['generated_Qt'],'static_production_assets':'rouge/data/player-theme/source.json','runtime_upstream_dependency':False,'support_for_Python312_not_claimed':True},'not_adopted':{'repository':'https://github.com/ColinDuquesnoy/QDarkStyleSheet','reviewed_commit':'6f3962e63749893f951be73ebfec93e83fffebf2','docs_and_targeted_source_read':['README.rst','LICENSE.rst','setup.py','qdarkstyle/__init__.py','qdarkstyle/palette.py','dark_palette.py','light_palette.py'],'code_license':'MIT','images_license':'CC-BY-4.0 per reviewed license','reason':'Per-widget fixed light/dark styling needs local palette isolation; reviewed loader resets custom palette choice and touches application link colors. Flat PyQtDarkTheme static QSS/geometry/state rules fit this batch with smaller runtime integration. Not a runtime performance comparison.','executed_or_production_adopted':False},'video_reference':{'source':'project local original mp4','original_sha256':'0b83e44f0816508ef095120961496337e6bd65d5f531ee350c078950dfb98bda','original_bytes':47052763,'frames_reviewed_for_this_scope_seconds':[70,172,194],'52_seconds_is_intro_montage_not_actual_map_panel':True,'no_continuous_entire_video_playback_claim':True,'game_overlay_70_seconds_not_equal_to_independent_map_reader':True}})
(B/'candidate-source.py').write_bytes((R/'.cache/preview_theme446.py').read_bytes())
(B/'related-verified/run-source.py').write_bytes((R/'.cache/run_theme_related_verified.py').read_bytes())
write(f'verification/maintenance/{stem}/failure-disposition.json',{'palette_failure':'palette-failure/failure.json','repair':'Export complete for_stylesheet=False palette rather than inherit system Base. Original palette/source/builder preserved; contrast threshold not reduced.','first_related_actual_result':'related/results.json','first_related_tests':98,'first_related_failures':2,'cause':'Two legacy assertions demanded the entire style equal the old skin; implementation intentionally prefixes external QSS. Updated to retained legacy suffix plus explicit theme contract; exact source, palette, close, refresh, and run-state assertions stay. Original test source saved.','earlier_native':'native/window.json','intermediate_native':'native-final/window.json','final_native':'native-verified/window.json','screenshot_fixture_correction':'Process pending layout events before grabbing owned inventory; first half-width frame is not evidence of a product layout repair.','last_product_fix':'Retain full black inventory surface/pane instead of inherited upstream green. Final98 and37 cover this source.','candidate_directory':'verification/sections/446-theme-candidate','candidate_is_experiment_at_functional445_not_functional446':True,'no_threshold_or_source_admission_weakened':True})
save(f'research/{stem}/README.md',f'''# {title}

基线{BASE}。本轮是界面实现维护，功能仍445，446未开始；全程序及视频全部功能、交互和外观未完成。

## 实际采用的外部方案

先克隆并阅读两个成熟Qt主题项目的文档、许可和相关加载器，再比较本机接入成本。采用[PyQtDarkTheme](https://github.com/5yutan5/PyQtDarkTheme/tree/96eb7e368039ab446952573bafc17d54b7ef5123)2.1.0生成的浅/深QSS、完整调色板及122个SVG；127份生产静态文件含MIT许可与来源清单，实际由玩家浮窗读取。它们提供真实第三方控件几何、状态和图标规则，不把本项目原组件复用称作外部替换。

另核对[QDarkStyleSheet](https://github.com/ColinDuquesnoy/QDarkStyleSheet/tree/6f3962e63749893f951be73ebfec93e83fffebf2)的README、许可、安装声明与加载器；其应用调色板入口和本轮每窗固定主题需求不完全相同，未复制运行或采用，不作运行性能优劣结论。精确来源和阅读范围见external-sources.json。

上游2.1.0声明Python>=3.7,<3.12，本机生成器在Python{manifest['build_exercised_python']}与Qt{manifest['generated_Qt']}隔离实际运行，不据此宣称上游支持3.12。原库只用于构建，不装入项目虚拟环境、不带入生产依赖，不启用系统主题监听、不改全局QApplication调色板。生产仅加载本地静态QSS/JSON/SVG；中文路径和打包收录有实际检查。

## 本机适配与视频边界

共享基础控件、按钮/标签、关闭区与中文字体；地图/历史/笔记用浅色，收藏品/条目/节点/场景资料用深色并保留专门阅读皮肤。原透明工具条和游戏叠加层不套用不透明主题。备注保存、未保存退出保护、选择/阅读保持和来源核验继续存在。

原片70秒是游戏地图叠加，不能与独立浅色地图窗口混为一致；172秒收藏品与194秒笔记仍显示当前资源/标题密度、窗口比例及部分排版差异。这里只完成共同控件及基础色彩的实际外部适配，未宣称全视频看完、全部窗口统一或像素一致。当前全程序源码539份，多一份共享主题模块；文件数量不证明逐文件正确性。

## 实际验证与保留的问题

最终98个不同相关检查通过，真实进程退出0；当前源码37项原生唯一检查通过、实际退出0，五张最终自有窗口原图已实际查看。包括精确来源卡到地图、选择/刷新、笔记阅读与未保存关闭、历史、透明工具条不被改色。早期25项隔离主题候选及中间37项不累计为新增验证；候选目录名称446不代表功能446开始。旧729选择器次序保持，仅追加1项成为730；本轮未跑全量，下次完整455，full440仍只证明旧冻结源码。

首轮浅色文字/底色对比仅约1.03，原因是本机生成器导出上游刻意不完整的调色板，继承系统暗底；改为导出完整调色板，没有降低4.5检查门槛，不称完整无障碍审计。首轮98检查中两个旧样式全字符串断言失败，已更新为原皮肤后缀加共享主题合同，其它来源/状态断言保留。原件、实际失败和最终结果并存。截图夹具补处理布局事件、最终库存黑底修正均明确分开。

原项目测试小窗已更新；Win32可见响应、Qt计时器推进，Windows-mcp按物理像素位置看到了实际工具条，未改焦点或操作游戏。启动六私人路径保持，整批仅作本机摘要比较，公开回执不含私人值或哈希；有变化不归因和回滚。窗口当前未绑定游戏，不冒充真实游戏悬停、连续采样或聊天验证。没有重跑计算公式/OCR算法，也无FPS、启动耗时或代码净缩减结论。

下一步先核对资源/说明密度、比例与其它窗口逐页布局，继续优先适配成熟外部代码；MaaFw仍仅隔离候选。P3/P2/P1及全程序回顾保持未完成。

[维护回执](../../verification/maintenance/{stem}/summary.json)。
''')
summary={'kind':'implementation_review_maintenance','section':445,'title':title,'passed':True,'functional_section_added':False,'baseline_commit':BASE,'changed_source':{n:sha256((R/n).read_bytes()).hexdigest()for n in sources},'necessary_distinct_tests':98,'native_unique_checks':37,'native_receipt':pin(f'verification/maintenance/{stem}/native-verified/window.json'),'source_review':pin(f'verification/maintenance/{stem}/source-review.json'),'external_adoption':'PyQtDarkTheme2.1.0 static production resources, local per-widget adaptation','whole_program_review_complete':False,'whole_video_parity_complete':False,'P3_P2_P1_complete':False,'goal_active':True,'next_full_section':455,'at_UTC':datetime.now(timezone.utc).isoformat()}
write(f'verification/maintenance/{stem}/summary.json',summary)
entry=f'''<!-- {stem}:start -->
## 界面实现维护 · {title}

实际采用PyQtDarkTheme2.1.0静态QSS、完整调色板与122SVG，MIT许可和来源保留；原库仅隔离构建，不作为生产Python依赖。玩家浮窗共用基础控件与字体，浅/深阅读皮肤保留，透明工具条/游戏叠加层不改。对比QDarkStyle源码后未采用其应用主题入口，不冒称性能比较。

最终98项不同相关检查、37项当前原生唯一检查通过，五张最终图已看；首轮调色板与旧样式断言失败原件保留。测试小窗更新可见响应，启动六私人路径保持；730选择器旧序保持，未跑全量，下次455。功能445、446未开。资源/标题密度、比例、其余窗口与全部游戏视频交互仍有差异，全程序/P3/P2/P1未完成。[回执](verification/maintenance/{stem}/summary.json)。
<!-- {stem}:end -->

'''
for n in('WORK_IN_PROGRESS.md','PROJECT_COMPLETED.md'):
 s=(R/n).read_text('utf8')
 if n=='WORK_IN_PROGRESS.md':s=s[s.index('<!-- player-section-445 -->'):]
 save(n,entry+s)
n='PROGRAM_REVIEW.md';s=(R/n).read_text('utf8').replace('当前总范围538份（含共享笔记样式及本轮单窗/范围模块）','当前总范围539份（含共享笔记样式、单窗/范围及本轮共享主题模块）',1)
s=s.replace('其余隐藏工具和初始算例的预计算成本、全部窗口与视频逐页对应。','其余隐藏工具和初始算例的预计算成本、资源/标题密度与窗口比例、其它窗口及游戏叠加层与视频逐页对应。',1)
save(n,s+f'\n[外部主题静态适配](research/{stem}/README.md)实际采用PyQtDarkTheme生成资源，98项相关与37项原生检查通过；源码/许可、构建版本限制及失败修复分别保留。基础控件统一不代表布局密度、游戏叠加层或全视频一致。\n')
n='PROJECT_PROGRESS.md';s=(R/n).read_text('utf8').replace('更新：2026-10-31。','更新：2026-11-01。',1).replace('其余界面的布局、配色、字体、图标、间距及浮窗呈现逐页对齐','资源和说明密度、标题占用、窗口比例及其余界面的布局、字体、图标、间距与浮窗呈现逐页对齐',1);save(n,s)
n='IMPLEMENTATION_STRATEGY.md';s=(R/n).read_text('utf8');mark='## 目标与不能混淆的前提';assert mark in s
s=s.replace(mark,f'本轮已将[PyQtDarkTheme静态资源](research/{stem}/README.md)真正用于生产浮窗，不引入其Python运行库；下一步集中处理资源/说明密度、比例及剩余页面。基础主题不是视频布局替代品，游戏叠加与独立地图分别核对。\n\n'+mark,1);save(n,s)
n='VIDEO_PARITY.md';s=(R/n).read_text('utf8');mark='## 工具条与自动关联';assert mark in s
s=s.replace(mark,f'本轮[外部主题适配](research/{stem}/README.md)接入成熟PyQtDarkTheme静态控件、调色板与SVG，浅色地图/历史/笔记和深色资料/库存各保留皮肤；98项相关与37项原生检查、五张图只证明此范围。资源/说明密度、窗口比例、其它页面及70秒游戏叠加与独立地图的区别继续验收，不以主题相似声称全效果一致。\n\n'+mark,1);save(n,s)
n='PROJECT_REQUIREMENTS.md';s=(R/n).read_text('utf8');mark='P3→P2→P1；';assert mark in s
s=s.replace(mark,'主题复用须实际采用外部成熟方案并保留许可，构建工具与生产依赖分开；按窗应用，透明工具条和游戏叠加层不得被通用不透明主题覆盖。基础配色/控件统一不替代视频比例、布局密度和交互验收。\n\n'+mark,1);save(n,s)
cp=read('DEVELOPMENT_CHECKPOINT.json');assert cp['completed_sections']==445 and cp['next_section']==446
cp['current_maintenance_save']={'kind':'implementation_maintenance','title':title,'receipt':f'verification/maintenance/{stem}/summary.json','binding':'enclosing_commit','functional_section_added':False,'status':'partial_video_theme_external_static_adoption','review_checklist':'PROGRAM_REVIEW.md','review_checklist_sha256':pin('PROGRAM_REVIEW.md')['sha256'],'application_review_complete':False}
cp['current_batch']['receipt']=f'verification/maintenance/{stem}/summary.json';cp['current_batch']['scope']='Whole-program review and full video parity remain active. Functional445 unchanged. External PyQtDarkTheme static resources adopted in production readers; layout density/proportions, remaining windows and game overlay still pending.446 not started.'
cp['next_action']='继续全程序与视频逐页回顾，优先外部成熟代码适配；先核对资源/说明密度、标题占用、窗口比例及剩余资料页，游戏叠加与独立地图分开验收。保留外部静态主题与准确节点入口。MaaFw多页面/连续等条件比较及OCR同步；P3/P2/P1和全部视频仍未完成。功能445，446未启动，下次完整455。'
save('DEVELOPMENT_CHECKPOINT.json',json.dumps(cp,ensure_ascii=False,indent=2)+'\n')
idx=runpy.run_path(str(R/'scripts/update_cloud_index.py'));idx['update'](R);assert idx['validate_delivery'](R,cp)['current_section']==445
write(f'verification/maintenance/{stem}/final-audit.json',{'passed':True,'functional_section':445,'functional_section_added':False,'next_section':446,'current_distinct_tests':98,'native_unique_checks':37,'ordered_selectors':730,'next_full':455,'current_full_rerun':False,'requirements':pin('PROJECT_REQUIREMENTS.md'),'index':pin('CLOUD_INDEX.json'),'maintenance_receipt':pin(f'verification/maintenance/{stem}/summary.json'),'goal_active':True,'whole_program_or_video_complete':False})
(B/'record-source.py').write_bytes(Path(__file__).read_bytes())
files={p.relative_to(R).as_posix():{k:v for k,v in pin(p.relative_to(R)).items()if k!='path'}for folder in(B,R/'verification/sections/446-theme-candidate')for p in folder.rglob('*')if p.is_file()and p.name!='archive-manifest.json'}
write(f'verification/maintenance/{stem}/archive-manifest.json',{'kind':'explicit_public_archive_no_private_contents_or_expected_values','files':files})
print(json.dumps({'recorded':True,'functional_section':445,'functional_section_added':False,'related_tests':98,'native_checks':37,'production_external_asset_files':127,'public_archive_files':len(files),'private_six_whole_batch_unchanged':not changed,'whole_goal_complete':False}))
