from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import ast,json,subprocess,difflib,sys,re,runpy
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts')];BASE='79009b919b7084c48141145a36db0eb046837561';stem='owned-window-follow-20261101';B=R/'verification/maintenance'/stem;D=R/'research'/stem;title='辅助资料窗跟随、隐藏恢复与关闭状态统一'
def read(n):return json.loads((R/n).read_bytes())
def pin(n):
 p=R/n;raw=p.read_bytes();return {'receipt':p.relative_to(R).as_posix(),'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}
def write(n,v):(R/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf8')
def save(n,text):
 p=R/n
 if not p.exists():p.write_text(text,'utf8');return
 a=p.read_bytes().decode('utf8').splitlines(keepends=True);b=text.splitlines(keepends=True)
 for x,y,k in difflib.SequenceMatcher(None,[v.rstrip('\r\n')for v in a],[v.rstrip('\r\n')for v in b],autojunk=False).get_matching_blocks():b[y:y+k]=a[x:x+k]
 p.write_bytes(''.join(b).encode('utf8'))
assert subprocess.check_output(['git','rev-parse','HEAD']).decode().strip()==BASE
assert subprocess.check_output(['git','branch','--show-current']).decode().strip()=='codex/p2-development'
sources=['rouge/player_game_binding.py','rouge/player_compact.py','rouge/player_item_hover.py','rouge/player_map_hover.py','rouge/player_game_hover.py','rouge/player_game_map.py','rouge/player_scene_battle.py','rouge/player_recent_scene.py','rouge/player_map.py','rouge/player_replay.py','rouge/player_shop_memory.py','scripts/verify_full_available.py','tests/test_owned_window_follow_review.py']
for name in sources:
 before=D/('before-'+Path(name).name)
 if before.exists():assert before.read_bytes()==subprocess.check_output(['git','show',BASE+':'+name]),name
v=read(B/'related-current/results.json');assert v['passed']and v['tests_run']==96 and not(v['failed']or v['errors']or v['skipped']or v['forbidden_external_calls']);assert read(B/'related-current/process.json')['actual_observed_exit']==0
ids=re.findall(r'^test_\w+ \(([^)]+)\)',(B/'related-current/stderr.txt').read_text('utf8'),re.M);assert len(ids)==len(set(ids))==96
native={}
for name,count in [('native-current',55),('legacy-final-393',34),('legacy-final-416',22),('legacy-final-447',54)]:
 n=read(B/name/'window.json');assert n['passed']and n['unique_checks']==count and not n['source_drift']and not any(n['external_operation_attempts'].values());assert read(B/name/'process.json')['actual_observed_exit']==0
 for path,digest in n['source_sha256_after'].items():assert sha256((R/path).read_bytes()).hexdigest()==digest,(name,path)
 for row in n['screenshots']:assert sha256((R/row['file']).read_bytes()).hexdigest()==row['sha256']
 native[name]={'receipt':pin(B/name/'window.json'),'checks':count,'process':pin(B/name/'process.json')}
images=read(B/'native-current/extra-images.json');assert len(images)==2
for row in images:assert sha256((R/row['file']).read_bytes()).hexdigest()==row['sha256']
root=read(B/'native-current/window.json')['screenshots'];assert root[0]['sha256']==next(v['sha256']for v in images if v['file'].endswith('event-reference.png'))
legacy_images=[read(B/name/'window.json')['screenshots'][0]for name in ['legacy-final-393','legacy-final-416','legacy-final-447']]
write(B/'root-image-review.json',{'directly_viewed_current_images':images+legacy_images,'direct_current_distinct_count':5,'root_screenshot_byte_identical_to_event_reference':root,'public_synthetic_states_only':True,'appearance_does_not_replace_native_checks':True,'video_rewatched_this_turn':False,'whole_video_complete':False})
live=read(B/'live-window/window.json');status=read('.cache/owned-follow-live-status.json');assert live['passed']and live['private_six_paths_unchanged']and status['elapsed_since_launch']>4 and status['toolbar_visible']and status['event_reader_visible']and status['common_dark_theme']and status['conditions_collapsed']
for name,digest in live['source_sha256_after'].items():assert sha256((R/name).read_bytes()).hexdigest()==digest
write(B/'live-window/desktop-review.json',{'Windows_mcp_region':[1410,573,2210,609],'actual_title_region_viewed':True,'actual_owned_event_reader_visible_responding_and_fresh_Qt_timer':True,'non_activating_attribute_used_for_reference_dialog':True,'whole_window_unoccluded_or_all_game_binding_claimed':False,'game_binding_active':status['game_binding_active'],'private_window_contents_images_or_hashes_published':False,'not_real_game_or_chat_accuracy':True})
write(B/'live-window/launcher-environment.json',{'initial_system_python_failure':'ModuleNotFoundError: No module named win32gui','before_private_read_or_process_close_or_launch':True,'resolved':'Use existing project .venv/Scripts/python.exe, same interpreter environment as native checks. No dependency installation or package change.','subsequent_update_passed':True})
private=read('.cache/owned-window-follow-before.json')['private'];changed=[name for name,digest in private.items()if(sha256((R/name).read_bytes()).hexdigest()if(R/name).is_file()else None)!=digest]
write(B/'private-scope.json',{'whole_batch_private_six_unchanged':not changed,'startup_private_six_unchanged':True,'changed_paths_if_any':changed,'private_contents_or_actual_hashes_published':False,'private_backup_or_restore':False});assert not changed
class DropRole(ast.NodeTransformer):
 def visit_Expr(self,node):
  call=node.value
  if isinstance(call,ast.Call)and isinstance(call.func,ast.Attribute)and call.func.attr=='setProperty'and call.args and isinstance(call.args[0],ast.Constant)and call.args[0].value=='playerVisibility':return None
  return self.generic_visit(node)
role_only=['player_game_hover.py','player_game_map.py','player_item_hover.py','player_map_hover.py']
for leaf in role_only:
 assert ast.dump(ast.parse((D/('before-'+leaf)).read_text('utf8')))==ast.dump(DropRole().visit(ast.parse((R/'rouge'/leaf).read_text('utf8')))),leaf
binding_old=ast.parse((D/'before-player_game_binding.py').read_text('utf8'));binding_new=ast.parse((R/'rouge/player_game_binding.py').read_text('utf8'))
for name in ['physical_pixels','BindingApi','clamp_window']:
 old=next(v for v in binding_old.body if getattr(v,'name',None)==name);new=next(v for v in binding_new.body if getattr(v,'name',None)==name);assert ast.dump(old)==ast.dump(new),name
method_changes={}
expected={'player_compact.py':{'CompactAssistant.toggle_visibility'},'player_map.py':{'MapPanel.hideEvent','MapPanel.check_reference'},'player_replay.py':{'ReplayPanel.hideEvent'},'player_shop_memory.py':{'ShopMemoryPanel.hideEvent'},'player_recent_scene.py':{'RecentScenePanel.hideEvent','RecentScenePanel.closeEvent','RecentScenePanel._close_readers'},'player_scene_battle.py':{'SceneBattlePanel.closeEvent','SceneBattlePanel.hideEvent','SceneBattlePanel._close_readers'}}
for leaf,allowed in expected.items():
 def methods(tree):return {cls.name+'.'+f.name:ast.dump(f)for cls in tree.body if isinstance(cls,ast.ClassDef)for f in cls.body if isinstance(f,(ast.FunctionDef,ast.AsyncFunctionDef))}
 old=methods(ast.parse((D/('before-'+leaf)).read_text('utf8')));new=methods(ast.parse((R/'rouge'/leaf).read_text('utf8')));actual={n for n in set(old)|set(new)if old.get(n)!=new.get(n)};assert actual==allowed,(leaf,actual);method_changes[leaf]=sorted(actual)
oldfile=R/'.cache/owned-follow-selectors-before.py';oldfile.write_bytes(subprocess.check_output(['git','show',BASE+':scripts/verify_full_available.py']));old=runpy.run_path(str(oldfile))['maintained_selectors']();new=runpy.run_path(str(R/'scripts/verify_full_available.py'))['maintained_selectors']();assert len(old)==738 and len(new)==739 and new[:len(old)]==old
write(B/'selector-prefix.json',{'previous_count':738,'current_count':739,'old_order_preserved':True,'added':list(new[len(old):]),'not_full_suite_execution':True})
tracked=[p for p in subprocess.check_output(['git','ls-files','-z','--','rouge']).decode('utf8').split('\0')if p and Path(p).suffix in('.py','.js','.cjs','.mjs')];assert len(tracked)==541
write(D/'evidence.json',{'base_commit':BASE,'external_evaluation':{'candidate':'PyWinCtl','repository':'https://github.com/Kalmat/PyWinCtl','license':'BSD-3-Clause, inspected not redistributed','inspected':['official README and Windows implementation getAllWindows','official documentation and LICENSE.txt'],'urls':['https://github.com/Kalmat/PyWinCtl/blob/master/README.md','https://github.com/Kalmat/PyWinCtl/blob/master/src/pywinctl/_pywinctl_win.py','https://raw.githubusercontent.com/Kalmat/PyWinCtl/master/LICENSE.txt','https://pywinctl.readthedocs.io/en/stable/docstrings.html'],'pinned_adopted_commit':None,'why_not_adopted':'OS-level HWND objects cannot replace Qt parent ownership, hidden-QDialog close acceptance or source refresh lifecycle. Replacing the readonly geometry adapter would add integration without solving the observed defects.','package_installed_or_product_code_copied':False},'authoritative_Qt_source':{'version':'v6.11.2','urls':['https://raw.githubusercontent.com/qt/qtbase/v6.11.2/src/widgets/kernel/qwidget.cpp','https://raw.githubusercontent.com/qt/qtbase/v6.11.2/src/widgets/dialogs/qdialog.cpp','https://doc.qt.io/QT-6/qapplication.html','https://doc.qt.io/QT-6/application-windows.html'],'actual_source_facts':['QWidget dispatches Close to virtual closeEvent once.','Hidden QDialog accepts Close directly, so finished signal alone does not observe all hidden accepted closes.','Top-level QWidget can still have a parent; ownership is followed with parentWidget chain.'],'runtime_package_upgraded':False},'reuse_scope':'Existing externally adopted PyQtDarkTheme, superqt QCollapsible and Qt BSD Flow remain. Qt API bridge changes this batch are not a new external project adoption.','MaaFramework':'Existing LGPL3 candidate b176dd8883c19fa1a46e1aa3cb553b0808176347 / isolated5.14.3 reviewed, not newly integrated or benchmarked this turn. Full multi-page/equal-field/continuous-input evidence still needed.','whole_program_or_video_complete':False,'no_new_mechanism_or_speed_claim':True})
write(B/'source-review.json',{'base_commit':BASE,'changed_or_new_sources':{name:pin(name)for name in sources},'application_source_files':541,'new_application_modules':0,'actual_external_adoption_this_batch':False,'existing_external_integrations_preserved':True,'role_only_AST_equal_after_removing_property_calls':role_only,'readonly_identity_geometry_and_clamp_AST_unchanged':['physical_pixels','BindingApi','clamp_window'],'remaining_view_changed_methods':method_changes,'other_callbacks_AST_unchanged':True,'formulas_OCR_mechanism_datasets_or_frame_payloads_modified':False,'defenses':'No broad exception/retry or speculative fallback. Common parent-chain is used by discovery, accepted-close pruning and global hiding; retained role used in discovery workflows and restoration. Existing deleted-QObject/source validation retained for reachable deletion/refresh. Close cleanup shares a polymorphic hook used by both close and ordinary hide, not a single-use helper.','REA_scope':'Ordinary Python source and actual WindowsQt lifecycle review; no new REA call, PYC or complete-program claim.','limits':'Actual game and multi-monitor transitions, other reader layouts, continuous capture/recognition, all video/P3/P2/P1 incomplete. Replay/shop temporary hide hooks use shared rule; no claim of every interactive source lifetime tested.','whole_program_or_video_complete':False})
assert read(B/'related-final/results.json')['failed']==1
assert read(B/'native/process.json')['actual_observed_exit']==1
write(B/'intermediate-disposition.json',{'actual_before_source':BASE,'before_observation':'before/ shows dynamic event absent from fixed list, zero17/11 movement, hidden accepted close resurrected, modal workflow hidden. This observational exit0 is not acceptance.','rejected_signal_only_solution':'qt-signal-actual.json confirms hidden accepted close emits no finished; qt-signal-filter-close.json confirms original closeEvent dispatch exactly once with accepted and ignored closes.','first_native_failure':{'receipt':pin(B/'native/window.json'),'actual_exit':1,'meaning':'Real parent hideEvent closed child source before suspension. Fixed by marking all owned live windows before hide, distinguishing temporary suspension from ordinary hide/close in actual source panels.'},'related_final_failure':{'receipt':pin(B/'related-final/results.json'),'actual_exit':1,'tests':95,'failed':1,'meaning':'Qt isAncestorOf is not a complete parentWidget chain across independent windows. Closed parent left nested child pending; fixed common full parent-chain without weakening assertion.'},'geometry_observed_failure':{'receipt':pin(B/'geometry-return-before.json'),'actual':[200,200],'expected':[217,211],'meaning':'Unavailable snapshot previously cleared last applied geometry. Preserve previous rectangle only for return delta; latest snapshot remainsNone and is never treated as a fresh game frame.'},'intermediate_passes_not_final_or_accumulated':['related61','native-final53','native-delivery53','legacy-current393/416/447'],'current_final':'related-current96 and native-current55; legacy-final393/416/447 separate34/22/54. All bind unchanged current product source through native hashes.','full_validation_not_run':True,'assertions_not_weakened':True})
save(D/'README.md',f'''# 实现维护 · {title}

先比较外部成熟方案：[PyWinCtl](https://github.com/Kalmat/PyWinCtl)的说明、BSD许可、Windows窗口枚举实现与文档已查。它管理操作系统窗口，不能直接替代Qt资料窗归属、隐藏后关闭是否接受、来源刷新时清理等语义；因此本批没有安装或宣称采用它。现有外部PyQtDarkTheme、superqt折叠类和Qt BSD Flow保持，Qt接口连接不算新引入公开项目。MaaFramework仍是待等条件验证的识别候选，不能把先前静态特征试验当完整识别方案已替换。

旧程序按窗口变量固定列举，真实最近事件的资料窗和嵌套地图位置窗会遗漏。现按Qt实际顶层QDialog与完整parentWidget链发现，父先子后；嵌入笔记不是独立窗。游戏失效和手动收起共用保留队列，抓取所有可见窗后才逐个隐藏。暂时收起保留当前资料、笔记草稿及有效固定卡；真正关闭或来源失效清理，不在恢复时重开。游戏悬停和地图覆盖层仍须新鲜画面准入，不能靠恢复队列重放；临时提示不保留，已固定资料卡也须未失效。

Qt v6.11.2原源码和本机探针说明：隐藏QDialog接受关闭可能不发finished，不能只靠该信号。事件过滤仅处理待恢复窗口的Close，调用原closeEvent一次；接受则清除整个后代队列，拒绝则保留。真实未保存笔记拒绝关闭和草稿保留通过。模态操作中暂缓移动/隐藏，结束后使用最新状态；失效时snapshot仍为None，仅保留上次已应用矩形，供同一游戏返回时算移动差额，不冒充新鲜画面。

原生首轮暴露父hideEvent主动清掉资料，相关95项中另一次真实失败暴露isAncestorOf跨独立窗不完整；均修正并保留原件，最后一次96项通过。最终原生55项和旧快捷键/跟随/统计34、22、54项分开，不能相加重复当覆盖。五份不同当前隔离原图已查看，根图与事件图整字节相同；外观不替代交互检查。其余源页面完整交互、实机/跨屏、完整视频及P3/P2/P1仍未完成。

原项目测试窗已正常更新打开，Windows-mcp实际查看标题区并结合Qt计时/可见/响应检查；六私人路径只本地摘要比较不变，不发布实际摘要或内容。没有操作游戏、发送聊天或启动采样。仍功能447、后续448，选择器739且原序不变，下次完整455；本批仅维护，不增加功能节数。
''')
entry=f'''<!-- {stem}:start -->
## 实现维护 · {title}

按实际Qt归属发现事件/嵌套地图等资料窗，游戏失效与手动收起共用恢复状态；暂时隐藏保留有效阅读和草稿，真实关闭/来源失效不再误重开。模态操作期间暂缓跟随，返回后沿最后已应用位置更新；游戏悬停和覆盖层仍须新鲜信息，普通临时提示不回放。外部PyWinCtl经适用性比较不采用，现有外部主题/折叠/Flow保持，本批Qt连接不冒称新项目复用。

96项当前相关、55项最终原生检查通过；旧393/416/447的34/22/54项分别核对。原父隐藏清源失败、跨窗后代队列失败和失效丢几何实测均保留，修复未缩减断言。五份不同当前隔离原图已看，测试窗已更新打开，六私人路径保持。功能447、448未开，739有序选择器，下次完整455；实际游戏/跨屏、其余窗口/识别及全部视频/P3/P2/P1未完成。[回执](verification/maintenance/{stem}/summary.json)。
<!-- {stem}:end -->

'''
for name in('WORK_IN_PROGRESS.md','PROJECT_COMPLETED.md'):save(name,entry+(R/name).read_text('utf8'))
name='PROJECT_REQUIREMENTS.md';text=(R/name).read_text('utf8');marker='P3→P2→P1；';assert marker in text;text=text.replace(marker,'辅助资料窗按实际归属参与游戏跟随和收起恢复，嵌入编辑器不作独立窗口移动；暂时隐藏应保留有效阅读、固定资料和未保存草稿，真正关闭或来源失效不再恢复。手动收起不能被游戏恢复越过；模态操作期间暂缓跟随。游戏悬停/地图覆盖层及未固定临时提示不从队列重放，仍须当前有效来源和新鲜画面；上次窗口矩形仅供同一游戏返回时定位，不充当新鲜状态。完整工作台保持独立。\n\n'+marker,1);save(name,text)
name='PROJECT_PROGRESS.md';text=(R/name).read_text('utf8');text=text.replace('其余附属资料窗的对象释放和其它父页/原始日志的来源刷新','其它未覆盖父页/原始日志的来源刷新、释放与真实游戏/跨屏连续联动',1);save(name,text)
name='PROGRAM_REVIEW.md';text=(R/name).read_text('utf8');assert '当前总范围541份'in text;save(name,text+f'\n[窗口归属/恢复回顾](research/{stem}/README.md)改用Qt实际顶层归属链，并区分暂时隐藏、真关闭/来源失效、模态操作和临时游戏提示；已验证真实事件、固定作战/嵌套地图、未保存笔记及原统计放大链路，原父隐藏清源/后代清理/丢几何失败保留并修正。541份只是清点范围；其它生命周期、实机/跨屏、其余布局和全部视频未完成。\n')
name='IMPLEMENTATION_STRATEGY.md';save(name,(R/name).read_text('utf8')+f'\n[辅助窗口跟随/恢复](research/{stem}/README.md)先比较外部PyWinCtl适用性，因其操作系统窗口模型不处理Qt来源/关闭语义而不引入；本地小范围桥接不冒称外部新采用。按Qt真实归属统一恢复并保留草稿，临时游戏提示仍须新鲜来源；完整视频、实机跨屏与等条件识别替换继续待办。\n')
name='VIDEO_PARITY.md';save(name,(R/name).read_text('utf8')+f'\n[辅助窗口生命周期维护](research/{stem}/README.md)已在真实Qt隔离窗口核对事件/嵌套地图跟随、收起恢复、来源失效关闭及未保存草稿。原片本轮未重看，不增加逐段外观验收；实际游戏/跨屏及完整功能、交互和外观仍未完成。\n')
receipt={'kind':'implementation_maintenance','title':title,'section':447,'functional_section_added':False,'passed':True,'acceptance_status':'listed_scope_passed_whole_video_pending','necessary_distinct_case_ids':96,'current_related_receipt':pin(B/'related-current/results.json'),'native_unique_checks':55,'native_receipts_separate_scopes':native,'local_test_window':pin(B/'live-window/window.json'),'source_review':pin(B/'source-review.json'),'image_review':pin(B/'root-image-review.json'),'source_sha256':{name:sha256((R/name).read_bytes()).hexdigest()for name in sources},'limits':'Other reader lifetimes/layouts, actual game/multi-monitor/continuous capture-recognition, full video and P3/P2/P1 incomplete. No new external package adoption, formula or OCR changes, or speed claim.','full_suite_rerun':False,'old_full440_proves_current_source':False,'goal_active':True,'whole_program_or_video_complete':False,'at_UTC':datetime.now(timezone.utc).isoformat()};write(B/'summary.json',receipt)
cp=read('DEVELOPMENT_CHECKPOINT.json');assert cp['completed_sections']==447 and cp['next_section']==448 and cp['current_maintenance_save']['title']=='事件对照条件收拢、紧凑阅读与入口主题统一'
cp['event_reader_layout_maintenance_20261101']=cp.pop('current_maintenance_save')
cp['current_maintenance_save']={'kind':'implementation_maintenance','title':title,'receipt':f'verification/maintenance/{stem}/summary.json','binding':'enclosing_commit','functional_section_added':False,'status':'listed_scope_passed_full_video_pending','review_checklist':'PROGRAM_REVIEW.md','review_checklist_sha256':pin('PROGRAM_REVIEW.md')['sha256'],'application_review_complete':False}
cp['current_batch']['receipt']=f'verification/maintenance/{stem}/summary.json';cp['current_batch']['scope']='Whole-program/video review active. Functional447 unchanged. Owned Qt auxiliary visibility/following/accepted-close/source lifetime maintenance accepted in listed scope; real game/multiscreen/other readers, recognition and full video incomplete.448 not started.'
cp['next_action']='继续其它资料窗图文/长说明、原生窗框、真实游戏/跨屏及全部视频交互核对；先比较并采用适用的外部成熟代码。MaaFramework等识别候选仍缺多页面/等字段/连续输入比较与实际替换，OCR同步优化；完整统计和机制保持待办。全程序/P3/P2/P1未完成；功能447、后续448，下次完整455。'
save('DEVELOPMENT_CHECKPOINT.json',json.dumps(cp,ensure_ascii=False,indent=2)+'\n');idx=runpy.run_path(str(R/'scripts/update_cloud_index.py'));idx['update'](R);assert idx['validate_delivery'](R,cp)['current_section']==447
write(B/'final-audit.json',{'passed':True,'functional_section':447,'functional_section_added':False,'next_section':448,'current_distinct_tests':96,'native_unique_checks':55,'separate_legacy_native_checks':{'393':34,'416':22,'447':54},'ordered_selectors':739,'next_full':455,'current_full_rerun':False,'requirements':pin('PROJECT_REQUIREMENTS.md'),'index':pin('CLOUD_INDEX.json'),'maintenance_receipt':pin(B/'summary.json'),'goal_active':True,'whole_program_or_video_complete':False})
(B/'record-source.py').write_bytes(Path(__file__).read_bytes());files={p.relative_to(R).as_posix():pin(p)for p in B.rglob('*')if p.is_file()and p.name!='archive-manifest.json'};write(B/'archive-manifest.json',{'kind':'explicit_public_archive_only_no_private_cache_or_video','files':files})
print(json.dumps({'passed':True,'functional_section':447,'new_functional_section':False,'distinct_case_ids':96,'final_native_checks':55,'selectors':739,'private_six_unchanged':not changed,'archive_files':len(files),'goal_complete':False}))
