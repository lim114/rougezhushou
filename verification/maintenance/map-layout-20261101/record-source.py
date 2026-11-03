from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import json,ast,difflib,subprocess,runpy,re,sys
R=Path.cwd();BASE='cbcb7849720e151edb21645cedb1bd9449a515c4';stem='map-layout-20261101';B=R/'verification/maintenance'/stem;research=R/'research'/stem
title='独立地图比例、分层资源与可收起工具'
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
t=read(B/'related-final/results.json');assert t['passed']and t['tests_run']==114 and not(t['failed']or t['errors']or t['skipped']or t['forbidden_external_calls'])
assert read(B/'related-final/process.json')['actual_observed_exit']==0
ids=re.findall(r'^test_\w+ \(([^)]+)\)',(B/'related-final/stderr.txt').read_text('utf8'),re.M);assert len(ids)==len(set(ids))==114
native=read(B/'native-current/window.json');old=read(B/'source-map445/window.json')
for name,receipt,count in [('native-current',native,61),('source-map445',old,25)]:
 assert receipt['passed']and receipt['unique_checks']==count and not receipt['source_drift']and not any(receipt['external_operation_attempts'].values())
 assert read(B/name/'process.json')['actual_observed_exit']==0
 for n,h in receipt['source_sha256_after'].items():assert sha256((R/n).read_bytes()).hexdigest()==h,n
images=read(B/'native-current/details.json')['images']+native['screenshots']+old['screenshots'];assert len(images)==7
for row in images:assert sha256((R/row['file']).read_bytes()).hexdigest()==row['sha256']
write(B/'root-image-review.json',{'actual_final_PNGs_viewed':7,'images':images,'current61_and_old25_native_scopes_separate':True,'public_synthetic_state_only':True,'appearance_not_interaction_proof':True,'whole_video_complete':False})
status=read('.cache/map-layout-live-status.json');assert status['toolbar_visible']and status['map_visible']and status['elapsed_since_launch']>4
live=read(B/'live-window/window.json');assert live['passed']and live['private_six_paths_unchanged']
write(B/'live-window/desktop-review.json',{'Windows_mcp_region':[770,760,1000,810],'actual_current_map_title_viewed':True,'owned_map_and_toolbar_visible_responding_Qt_timer_advanced':True,'startup_private_six_unchanged':True,'private_window_images_or_values_archived':False,'game_binding_active':status['game_binding_active'],'not_live_game_or_chat_accuracy':True})
before=read('.cache/map-layout-before.json')['private'];changed=[n for n,h in before.items()if(sha256((R/n).read_bytes()).hexdigest()if(R/n).is_file()else None)!=h]
write(B/'private-scope.json',{'whole_batch_six_private_paths_unchanged':not changed,'changed_paths_if_any':changed,'origin_not_inferred':bool(changed),'private_contents_or_hashes_published':False,'private_backup_restore_or_rollback':False})
sources=['rouge/player_map.py','rouge/player_compact.py','rouge/player_map_acceptance.py','rouge/player_resource_strip.py','scripts/verify_full_available.py','tests/test_map_layout_review.py','licenses/qt-image-viewer-BSD-3-Clause.txt']
changes={}
for name in sources:
 p=research/('before-'+Path(name).name)
 if not p.exists():continue
 assert p.read_bytes()==subprocess.check_output(['git','show',BASE+':'+name])
 if not name.startswith('rouge/'):continue
 def methods(raw):
  tree=ast.parse(raw);return {parent.name+'.'+n.name:ast.dump(n,include_attributes=False)for parent in tree.body if isinstance(parent,ast.ClassDef)for n in parent.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
 a,b=methods(p.read_bytes()),methods((R/name).read_bytes());assert a.keys()==b.keys()
 changes[name]=[key for key in a if a[key]!=b[key]]
assert changes['rouge/player_compact.py']==['CompactAssistant.open_map']
assert changes['rouge/player_resource_strip.py']==['ResourceStrip.set_rows']
sys.path[:0]=[str(R),str(R/'scripts')];ns={'__name__':'map_baseline_selectors','__file__':str(R/'scripts/verify_full_available.py')};exec(compile(subprocess.check_output(['git','show',BASE+':scripts/verify_full_available.py']),ns['__file__'],'exec'),ns)
from verify_full_available import maintained_selectors
a,b=ns['maintained_selectors'](),maintained_selectors();assert len(a)==733 and len(b)==734 and b[:-1]==a
external=R/'.cache/map-external-20261101';qt=read(external/'qt-pin.json');superqt=read(external/'superqt-head.json')['sha']
(research/'upstream-qt-imageviewer.py').write_bytes((external/'qt-imageviewer.py').read_bytes())
write(research/'sources.json',{'video':{'sha256':'0b83e44f0816508ef095120961496337e6bd65d5f531ee350c078950dfb98bda','actual_frames_viewed_seconds':[70,83,141,145],'local_only_no_video_or_frames_distributed':True,'not_continuous_full_playback':True},'Qt_image_viewer':{**qt,'repository':'https://github.com/qtproject/pyside-pyside-setup','source_path':'examples/widgets/imageviewer/imageviewer.py','reviewed_source_functions':['_scale_image','_adjust_scrollbar'],'actual_adoption':'Center-preserving scrollbar formula in MapPanel.change_zoom; no print/file-dialog/demo application code or new dependency.','upstream_copy':pin(research/'upstream-qt-imageviewer.py'),'license':pin('licenses/qt-image-viewer-BSD-3-Clause.txt'),'readme_sha256':sha256((external/'qt-README.md').read_bytes()).hexdigest()},'superqt_candidate':{'repository':'https://github.com/pyapp-kit/superqt','commit':superqt,'reviewed':['README.md','LICENSE','pyproject.toml','src/superqt/collapsible/_collapsible.py'],'source_sha256':{n:sha256((external/n).read_bytes()).hexdigest()for n in('superqt-README.md','superqt-LICENSE','superqt-pyproject.toml','superqt-collapsible.py')},'adopted':False,'reason':'QtPy/Pygments dependencies and animated general collapsible widget do not replace this map renderer or simplify a single existing tools container; keep native Qt toggle/layout and unchanged upstream BSD Flow Layout.'},'previous_production_reuse':['PyQtDarkTheme2.1.0 static assets','Qt6.11.2 BSD Flow Layout'],'reference_video_program_source_obtained':False})
write(B/'source-review.json',{'base_commit':BASE,'changed_or_new_sources':{n:pin(n)for n in sources},'function_AST_review':changes,'application_source_files':540,'new_application_modules':0,'new_low_probability_defensive_layer':False,'new_generic_exception_recovery_or_acquisition_replay':False,'mechanism_math_OCR_game_overlay_and_map_identity_unchanged':True,'external_theme_and_Flow_source_unchanged':True,'actual_external_source_adopted':'Qt6.11.2 Image Viewer center-preserving scrollbar formula, BSD-3-Clause','previous733_selector_order_preserved':True,'ordered_selectors_after':734,'full_suite_rerun':False,'REA_scope':'Complete Python source reviewed directly under REA skill; no new REA invocation, decompilation or entire-program completion claim.'})
write(B/'failure-disposition.json',{'earlier_green_receipts':['related/results.json','related-current/results.json','native/window.json'],'current_receipts':['related-final/results.json','native-current/window.json','source-map445/window.json'],'intermediate_passes_not_added_to_final114_or61':True,'actual_visual_issues':'Earlier native images showed white close glyph on light header and weak selected-floor styling; exact Map window selectors repaired. Resource scope switch retained chip values but wrong order; reorder retained labels without recreating them.','actual_isolated_probe_exit1':'Temporary unreferenced QWidget parent was collected, deleting ToolPopover; fixed by keeping parent reference. Not a product exception.','old392_assertion_update':'Historical fixture must show missing historical resources, not recent-run placeholder pills; source and exact value check remain.','test_thresholds_or_source_admission_weakened':False,'retained_before_source_and_window':True,'unavailable':'No actual game, multipage recognition, cross-screen game binding or chat validation claimed.'})
save(research/'README.md',f'''# {title}

基线{BASE}。本轮为维护，功能446不增节数、447未启动。全程序、全部视频效果及P3/P2/P1未完成。

实际回看原片70/83秒的游戏覆盖层和141/145秒的独立浅色地图。独立地图不应照搬覆盖层常驻类型栏。本轮改为简短楼层标签、资源胶囊和主要地图，查找、缩放、完整范围与类型筛选放入“地图工具”。节点仍可直接点开资料，来源卡仍可按准确类型定位。实际默认1200×460，节点画布圆角，选中楼层深底和关闭按钮对比单独核对；缩放/展开可以改变阅读空间，不称所有状态均保持默认比例。

历史楼层资源栏只使用同区域、同地图模板的既有快照；0和上限保留，其它缺项不从当前资源补写。无匹配快照明确未记录，只有区域未确认模板的记录也不能充当本图快照。当前地图显示本局最近读值，说明与历史读取时刻仍可展开。相同历史刷新保留原标签，切回当前范围恢复固定排列，不重建已有控件；没有改保存格式或私人记录。

## 外部成熟代码实际采用

固定Qt6.11.2提交{qt['commit']}，实际读取[官方Image Viewer源码](https://github.com/qtproject/pyside-pyside-setup/blob/{qt['commit']}/examples/widgets/imageviewer/imageviewer.py)及README和BSD许可，采用其缩放后保持视野中心的滚动条公式；按本地图真实画布大小计算缩放比。原件在upstream-qt-imageviewer.py，版权/许可在licenses/qt-image-viewer-BSD-3-Clause.txt。无新运行依赖，不复制打印/文件对话框或执行示例程序。已采用的PyQtDarkTheme静态资源和Qt官方Flow Layout继续使用。

另查阅superqt固定{superqt}的README、BSD许可、折叠源码和依赖：通用动画折叠控件还引入QtPy等依赖，不能替代地图渲染或减少这里的状态连接，故未安装/采用。不按仓库存在或仅使用Qt接口冒称外部方案已接通；本轮实际采用的是上述官方缩放源码。参考视频原程序源码仍未取得，完整Python源按REA技能直接审查，没有新增REA工具调用。

## 实际验收及未完成范围

最终114项不同相关检查、61项当前原生唯一检查通过；另25项来源卡→地图原生范围独立通过，不合并当作86个不同交互。七张最终隔离原图已逐张查看。覆盖640/900/1200实际宽度、1200×460默认比例、折叠/展开工具、准确筛选、节点资料、历史/当前/无记录和不同模板、刷新保持、资源排列、官方缩放中心与真实关闭重开。改前源码和窗口、早期通过回执及后续视觉问题均保留；不是只靠测试条数判外观。

真实测试窗口已正常更新并打开地图，可见响应且Qt计时器推进，启动六私人路径保持；只公开布尔结果，不分发私人图片/值/哈希。没有游戏控制、聊天或私人状态回滚。本轮未跑全量，734选择器保留前733顺序，下次455；full440仅证明其原冻结源码。

实际游戏和跨屏覆盖、转场/连续识别、地图节点长文和小尺寸标签、全部资料与外观仍有缺口；笔记、历史和其它页面继续核对。当前仅修正地图呈现与资源阅读，不新增概率、生成、机制数值或路线建议，也不称性能提升。
''')
entry=f'''<!-- {stem}:start -->
## 界面实现维护 · {title}

独立地图按原片141/145秒收拢为楼层、资源与地图，工具和完整说明按需展开；历史资源只用准确模板快照，未记录不借当前值。实际采用Qt官方BSD缩放中心公式，原主题/Flow源码保持；修正关闭对比、楼层选中样式及资源范围切换的排列。

最终114项不同相关检查、61项当前原生与独立25项来源跳转范围通过，七张最终原图已看；1200×460默认与640/900/1200工具宽度按实际窗口核对。测试窗已更新打开地图，启动私人六路径保持。功能446、447未开，734选择器原序保持，下次完整455；真实游戏/跨屏、节点长文、笔记/历史及全视频/P3/P2/P1仍未完成。[回执](verification/maintenance/{stem}/summary.json)。
<!-- {stem}:end -->

'''
for name in('WORK_IN_PROGRESS.md','PROJECT_COMPLETED.md'):
 s=(R/name).read_text('utf8')
 if name=='WORK_IN_PROGRESS.md':s=s[s.index('<!-- player-section-446 -->'):]
 save(name,entry+s)
name='PROJECT_PROGRESS.md';s=(R/name).read_text('utf8');old='地图/笔记/历史及其余窗口的比例、布局、字体、图标、间距与浮窗呈现逐页对齐；';assert old in s
save(name,s.replace(old,'地图节点长文、小尺寸标签与其余资料展开效果、笔记/历史及其它窗口的比例、布局、字体、图标、间距与浮窗呈现逐页对齐；',1))
name='PROGRAM_REVIEW.md';save(name,(R/name).read_text('utf8')+f'\n[独立地图呈现回顾](research/{stem}/README.md)完成工具收拢、准确历史资源胶囊和当前排列、1200×460实际比例及Qt官方缩放源码适配；114项相关、61项当前和25项来源窗口分别核对，不代表全部地图/跨屏/游戏或视频完成。源码仍540份，无新应用模块。\n')
name='IMPLEMENTATION_STRATEGY.md';s=(R/name).read_text('utf8');s=s.replace('下一步处理地图/笔记/历史及剩余页面、真实连续读取。','独立地图比例、工具收拢和分层资源已在本轮范围核对，下一步处理笔记/历史及地图其余细节、真实连续读取。',1);save(name,s)
name='VIDEO_PARITY.md';save(name,(R/name).read_text('utf8')+f'\n[本轮独立地图维护](research/{stem}/README.md)对应原片141/145秒，楼层短标签、资源胶囊、主要地图和收起工具，实际1200×460；历史资源只取准确模板快照，无记录不借当前数值，缩放采用Qt官方源码保持中心。70/83秒游戏覆盖层未改，真实游戏/跨屏和全部细节不冒称一致。\n')
name='PROJECT_REQUIREMENTS.md';s=(R/name).read_text('utf8');marker='P3→P2→P1；';assert marker in s
save(name,s.replace(marker,'独立地图与游戏标注层分别对齐原片，不把类型工具常驻侧栏挤占独立地图；查找与完整说明可收起但有效筛选和历史/最近来源仍可见。历史地图资源只取准确区域与模板的既有快照，缺项不借当前值；不同资源范围恢复正常排列，保留原标签和阅读状态。\n\n'+marker,1))
cp=read('DEVELOPMENT_CHECKPOINT.json');assert cp['completed_sections']==446 and cp['next_section']==447 and 'current_maintenance_save'not in cp
receipt={'kind':'implementation_maintenance','title':title,'section':446,'functional_section_added':False,'passed':True,'new_capability':'独立地图工具收拢、准确历史资源胶囊、实际窗口比例与成熟Qt缩放中心算法；修正对比和资源排列。','limitations':'只证明所列隔离范围；真实游戏/连续读取/跨屏、节点长文、笔记/历史及其余视频效果、P3/P2/P1未完成。','source_sha256':{n:sha256((R/n).read_bytes()).hexdigest()for n in sources},'necessary_tests':114,'native_scopes_separate':{'current':61,'source_map445':25},'native_receipts':[pin(B/'native-current/window.json'),pin(B/'source-map445/window.json')],'local_test_window':pin(B/'live-window/window.json'),'source_review':pin(B/'source-review.json'),'full_suite_rerun':False,'old_full440_proves_current_source':False,'goal_active':True,'whole_program_or_video_complete':False,'at_UTC':datetime.now(timezone.utc).isoformat()};write(B/'summary.json',receipt)
cp['current_maintenance_save']={'kind':'implementation_maintenance','title':title,'receipt':f'verification/maintenance/{stem}/summary.json','binding':'enclosing_commit','functional_section_added':False,'status':'partial_video_map_presentation_and_floor_resources','review_checklist':'PROGRAM_REVIEW.md','review_checklist_sha256':pin('PROGRAM_REVIEW.md')['sha256'],'application_review_complete':False}
cp['current_batch']['receipt']=f'verification/maintenance/{stem}/summary.json';cp['current_batch']['scope']='Whole-program/video review active. Functional446 unchanged. Independent map layout and historical resource reading refined with adopted Qt zoom formula; live game, note/history and remaining parity pending.447 not started.'
cp['next_action']='继续笔记/历史与其余视频效果逐页回顾；地图保留本轮比例、准确历史资源和Qt源码缩放，节点长文/小尺寸标签及真实连续读取继续处理。优先外部成熟代码适配，MaaFramework等条件验证和OCR同步，全程序/P3/P2/P1未完成。功能446、后续447，下次完整455。'
save('DEVELOPMENT_CHECKPOINT.json',json.dumps(cp,ensure_ascii=False,indent=2)+'\n');idx=runpy.run_path(str(R/'scripts/update_cloud_index.py'));idx['update'](R);assert idx['validate_delivery'](R,cp)['current_section']==446
write(B/'final-audit.json',{'passed':True,'functional_section':446,'functional_section_added':False,'next_section':447,'current_distinct_tests':114,'native_unique_checks':61,'additional_native_scope445':25,'ordered_selectors':734,'next_full':455,'current_full_rerun':False,'requirements':pin('PROJECT_REQUIREMENTS.md'),'index':pin('CLOUD_INDEX.json'),'maintenance_receipt':pin(B/'summary.json'),'goal_active':True,'whole_program_or_video_complete':False})
(B/'record-source.py').write_bytes(Path(__file__).read_bytes());files={p.relative_to(R).as_posix():pin(p)for p in B.rglob('*')if p.is_file()and p.name!='archive-manifest.json'};write(B/'archive-manifest.json',{'kind':'explicit_public_archive_no_private_contents_or_expected_values','files':files})
print(json.dumps({'recorded':True,'functional_section':446,'new_functional_section':False,'related_tests':114,'native_scopes_separate':[61,25],'ordered_selectors':734,'public_archive_files':len(files),'whole_batch_private_six_unchanged':not changed,'whole_goal_complete':False}))
