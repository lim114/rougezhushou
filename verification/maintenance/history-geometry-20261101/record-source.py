from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import json,ast,subprocess,sys,re,difflib,runpy
R=Path.cwd();BASE='fbfe7c8f5e073db0ae7ddfa6f4489e24db195898';stem='history-geometry-20261101';B=R/'verification/maintenance'/stem;research=R/'research'/stem
title='历史窗口实际比例、统计结果前置与重复藏品样本修正'
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
t=read(B/'related-verified/results.json');assert t['passed']and t['tests_run']==83 and not(t['failed']or t['errors']or t['skipped']or t['forbidden_external_calls']);assert read(B/'related-verified/process.json')['actual_observed_exit']==0
ids=re.findall(r'^test_\w+ \(([^)]+)\)',(B/'related-verified/stderr.txt').read_text('utf8'),re.M);assert len(ids)==len(set(ids))==83
native=[]
for name,count in [('native-verified',56),('legacy-verified-406',19),('legacy-verified-408',24),('legacy-verified-432',19)]:
 receipt=read(B/name/'window.json');assert receipt['passed']and receipt['unique_checks']==count and not receipt['source_drift']and not any(receipt['external_operation_attempts'].values());assert read(B/name/'process.json')['actual_observed_exit']==0
 for n,h in receipt['source_sha256_after'].items():assert sha256((R/n).read_bytes()).hexdigest()==h,n
 native.append(pin(B/name/'window.json'))
portrait=read(B/'native-verified/portrait-current.json');assert portrait['requested']==portrait['actual']==[640,650]and portrait['exact_portrait_target_passed']
trace=read(B/'height-trace/height-trace.json');assert trace['actual']==[640,699]
stats=next(r for r in trace['trace']if r['class']=='PersonalStatisticsPage');assert stats['height_for_width'][0][1]==552 and stats['visible']is False
assert read(B/'first-count-failure/process.json')['actual_observed_exit']==1
images=read(B/'native-verified/images.json');assert len(images)==8
direct={'compact-session-cards.png','statistics-unavailable.png'}
reuse={'plain-note.png':'verification/maintenance/notes-history-layout-20261101/compact-delivery/plain-note.png','compact-history-map.png':(B/'native/compact-history-map.png').relative_to(R).as_posix(),'expanded-history-scope.png':(B/'native/expanded-history-scope.png').relative_to(R).as_posix(),'statistics-summary.png':(B/'native-current/statistics-summary.png').relative_to(R).as_posix(),'statistics-full-scope.png':(B/'native-current/statistics-full-scope.png').relative_to(R).as_posix(),'statistics-large-text.png':(B/'native-current/statistics-large-text.png').relative_to(R).as_posix()}
for row in images:
 p=R/row['file'];assert sha256(p.read_bytes()).hexdigest()==row['sha256'];name=p.name
 if name in direct:row['root_review']='current PNG actually viewed'
 else:
  original=R/reuse[name];assert original.read_bytes()==p.read_bytes();row['root_review']='whole bytes identical to earlier actually viewed PNG';row['earlier_viewed_file']=reuse[name]
card=B/'legacy-verified-408/statistics-card.png';previous=B/'legacy-current-408/statistics-card.png';assert card.read_bytes()==previous.read_bytes()
write(B/'root-image-review.json',{'current_native_unique_images':8,'current_direct_viewed':2,'whole_byte_reuse_of_earlier_viewed':6,'images':images,'legacy_card_also_reviewed_by_exact_byte_reuse':{'current':pin(card),'earlier_viewed':previous.relative_to(R).as_posix()},'remaining_visual_difference':'The existing pale vertical export card is not the original video249/257/270 dark horizontal big-number card. Remains a todo.','other_legacy_PNGs_retained_for_interaction_not_new_complete_visual_review':True,'appearance_not_interaction_proof':True,'synthetic_public_state_only':True,'whole_video_complete':False})
live=read(B/'live-window-final/window.json');status=read('.cache/history-geometry-live-status.json');assert live['passed']and live['private_six_paths_unchanged']and status['history_visible']and status['toolbar_visible']and status['elapsed_since_launch']>4
write(B/'live-window-final/desktop-review.json',{'Windows_mcp_title_region':[1610,475,1820,515],'actual_history_title_viewed':True,'actual_test_PID':live['owned_windows'][0]['pid'],'visible_responding_and_Qt_timer_advanced':True,'private_list_contents_or_images_archived':False,'startup_private_six_unchanged':True,'game_binding_active':status['game_binding_active'],'game_chat_or_cross_screen_accuracy_claimed':False})
before=read('.cache/history-geometry-before.json')['private'];changed=[n for n,h in before.items()if(sha256((R/n).read_bytes()).hexdigest()if(R/n).is_file()else None)!=h]
write(B/'private-scope.json',{'whole_batch_six_private_paths_unchanged':not changed,'changed_paths_if_any':changed,'origin_not_inferred':bool(changed),'private_values_contents_or_hashes_published':False,'private_backup_restore_rollback':False})
sources=['rouge/player_personal_statistics.py','rouge/player_replay.py','rouge/player_replay_archive.py','rouge/player_statistics_card.py','rouge/player_statistics_samples.py','scripts/verify_full_available.py','tests/test_history_statistics_layout_review.py'];changes={}
for name in sources:
 p=research/('before-'+Path(name).name)
 if not p.exists():continue
 assert p.read_bytes()==subprocess.check_output(['git','show',BASE+':'+name])
 if not name.startswith('rouge/'):continue
 def methods(raw):
  tree=ast.parse(raw);answer={n.name:ast.dump(n,include_attributes=False)for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))};answer.update({parent.name+'.'+n.name:ast.dump(n,include_attributes=False)for parent in tree.body if isinstance(parent,ast.ClassDef)for n in parent.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))});return answer
 a,b=methods(p.read_bytes()),methods((R/name).read_bytes());changes[name]={'changed':[n for n in a.keys()&b.keys()if a[n]!=b[n]],'added':list(b.keys()-a.keys()),'removed':list(a.keys()-b.keys())}
assert changes['rouge/player_personal_statistics.py']['added']==['PersonalStatisticsPage.toggle_details']
sys.path[:0]=[str(R),str(R/'scripts')];ns={'__name__':'history_geometry_before_selectors','__file__':str(R/'scripts/verify_full_available.py')};exec(compile(subprocess.check_output(['git','show',BASE+':scripts/verify_full_available.py']),ns['__file__'],'exec'),ns)
from verify_full_available import maintained_selectors
a,b=ns['maintained_selectors'](),maintained_selectors();assert len(a)==735 and len(b)==736 and b[:-1]==a
assert sum(p.suffix in('.py','.js','.cjs')for p in(R/'rouge').rglob('*')if p.is_file()and'__pycache__'not in p.parts)==540
flow=read('research/resource-strip-review-20261031/upstream-source.json');video=read('.cache/history-statistics-video-20261101/observations.json')
write(research/'sources.json',{'video':{'sha256':video['video_sha256'],'actual_frames_viewed_seconds':[249,257,270],'frames':video['frames'],'video_and_frames_local_only':True,'not_continuous_full_playback':True},'Qt_runtime_trace':pin(B/'height-trace/height-trace.json'),'Qt_native_source_read_not_copied':[{'url':'https://raw.githubusercontent.com/qt/qtbase/v6.11.2/src/widgets/kernel/qstackedlayout.cpp','version':'v6.11.2','fact':'heightForWidth queries the widgets directly, including hidden pages; a size-policy-only experiment is insufficient.','license_header_read':'Qt commercial or LGPL3/GPL options; no C++ code copied.'},{'url':'https://raw.githubusercontent.com/qt/qtbase/v6.11.2/src/widgets/widgets/qtabwidget.cpp','version':'v6.11.2','fact':'Tab height delegates to stacked pages and adds frame/tab dimensions.'}],'actual_existing_external_code_reused_for_new_card_options':{**flow,'production_file':pin('rouge/flow_layout.py'),'license':pin('licenses/qt-flow-layout-BSD-3-Clause.txt'),'unchanged_upstream_adaptation':True},'native_Qt_implementation_docs':['https://doc.qt.io/qt-6/qscrollarea.html','https://doc.qt.io/qt-6/richtext-html-subset.html'],'pyqtgraph_candidate':{'documentation':'https://pyqtgraph.readthedocs.io/en/latest/api_reference/widgets/tablewidget.html','source_actually_read':'https://pyqtgraph.readthedocs.io/en/latest/_modules/pyqtgraph/widgets/TableWidget.html','documentation_version':'0.15.0.dev0','actual_scope':'Array/dict data handling, editable/sortable table items and copy/save actions over QTableWidget; not a complete video program.','adopted_or_installed_or_copied':False,'reason':'These additional capabilities do not simplify four read-only summary rows and an in-place scope link. Use already available native Qt rich-text layout; no measured speed claim or assertion that all external solutions were excluded.','license_or_commit_not_claimed_as_adopted':True},'reference_video_program_source_obtained':False,'actual_new_third_party_package_integration':False,'previous_production_external_theme_and_BSD_Flow_retained':True})
write(B/'source-review.json',{'base_commit':BASE,'changed_or_new_sources':{n:pin(n)for n in sources},'function_AST_review':changes,'application_source_files':540,'new_application_modules':0,'new_event_slot':'toggle_details is a Qt anchor event handler, not a one-off extraction layer.','new_low_probability_defensive_layer':False,'new_generic_exception_or_recovery_framework':False,'new_dependency':False,'stats_projection_change':'A complete, confirmed repeated-kettle bar now qualifies its one archive in the existing denominator; absent proof stays excluded. No gain/reward replay or fabricated state.','storage_schema_game_mechanics_OCR_and_capture_unchanged':True,'external_code_retained':'Qt BSD Flow Layout applied to four card-option controls; source/attribution unchanged. Native rich text and scroll APIs are not claimed as a new outside project adoption.','previous735_selector_order_preserved':True,'ordered_selectors_after':736,'full_suite_rerun':False,'REA_scope':'Complete Python source/runtime reviewed directly according to REA skill; no new REA invocation or whole-program completion claim.'})
write(B/'failure-disposition.json',{'old_failed_portrait_receipts_retained':'verification/maintenance/notes-history-layout-20261101/portrait-deferral.json','restart_condition_fulfilled_by':pin(B/'height-trace/height-trace.json'),'actual_new_root_cause':'Hidden PersonalStatisticsPage returns552 height-for-width; outer QTabWidget/ReplayPanel/header propagate699. Actual scroll content removes hidden-page height pressure.','initial_diagnostic_setup_failure':'Missing new parent directory; tool chunk390bd1, no child process launched. Fixed directory creation; not a new product repair attempt.','original_count_failure':'first-count-failure/process.json','fixture_corrections':'fixture-disposition.json','additional_full_scope_test_typo':'Test expected归档时 but actual canonical cohort text says归档中; fixed assertion to original text, no source text changed to pass. Tool chunkc16374.','intermediate_green_not_final':['related','related-final','related-delivery','related-current','native','native-final','native-delivery','native-current'],'visual_issues_corrected_after_green':['Long statistics prose preceded actual numbers','100percent HTML table width caused a needless horizontal scrollbar; intrinsic Qt table sizing used','Default pale link on white had poor contrast; now uses actual text palette','Source-unavailable samples falsely displayed0 archives; now explicit unknown distinct from known empty.'],'final_related_distinct_tests':83,'final_native_unique_checks':56,'original_native_scopes_separate':{'406':19,'408':24,'432':19},'intermediate_or_shared_checks_not_added_together':True,'original_target_threshold_preserved':True,'whole_video_or_program_passed':False})
save(research/'README.md',f'''# 历史窗口比例与个人统计阅读

基线{BASE}；本轮维护不增加功能节数，仍446、后续447。全程序、全部视频功能/外观及P3/P2/P1未完成。

## 新证据与已修正范围

前批640×650实际640×699的三份失败原件仍保留。本轮先测实际布局：隐藏的PersonalStatisticsPage返回552高度，外层页签、阅读页和标题把它传成699；Qt6.11.2源码明确查询所有堆叠子页，单改隐藏页策略不能阻止这一点。满足原延期重启条件后才恢复修复，统计长内容改为原生滚动页；当前完整打开流程实际640×650，不以请求尺寸代替实测。

个人统计把已证均值/比例、计入与未计入局数放在前面，完整原有口径按链接展开；真实链接、展开后刷新保留和关闭已验证。使用当前文字调色板保持链接对比，Qt原生内容宽度消除多余水平滚动。标题明确整个本机归档，不把当前选中单局说明冒充统计范围；返回历史保留原说明开关状态。窗口内窄尺寸可纵向滚动，展示字段沿用Qt官方BSD Flow随实际文字宽度换行，18pt文字单独验收。

发现旧统计资格只数不同藏品ID，将已确认多个热水壶的完整归档误排除；原两条实际失败已保留。现沿用446已有完整栏物理件数证据计入一次归档，缺证仍排除，不由数量差额猜件数，不修改状态或重放奖励。数值只证明公开临时夹具：3热水壶+1普通藏品+1道具的栏总数5、藏品4，完整清单样本1局；不是当前游戏/独立机制准确性验收。源不可读时逐局页改为统计未知，只有确实读到空归档才显示0局。

## 外部成熟方案与原片边界

优先复用目标仍是他人成熟代码。实际用于新字段排列的是已固定Qt6.11.2的BSD Flow原源码适配，作者许可和主题资源不变。另查阅PyQtGraph TableWidget的公开原始实现及0.15dev文档：数组/字典、排序、编辑及复制/导出不减少本轮四行只读结果和展开口径的接入工作，未安装/采用/复制；这不是对所有外部方案作排除结论。结果表和内容滚动仅调用已有Qt原生能力，不冒称新接入外部项目。Qt C++源码只用于根因核对，没有复制其受许可代码。

新回看原片249/257/270秒并逐张查看，证实深色横向大数字卡含结算、实托邦、藏品/零件图标组合和个人资料；当前浅色纵向导出卡明显不同，仍保留待办，录像示例值不能填入本机。只有三帧新复核，不冒称连续重看全片或取得参考程序源码。

## 最终验证与交付范围

最终83项不同相关检查、56项当前原生唯一检查通过；原406/408/432分别19/24/19项原生范围另验，不相加当作不同覆盖。实际子进程退出0，当前源摘要匹配、外部操作均0。原始两条数字失败、诊断失败和中间绿回执、实际发现的视觉/零局问题均保留；自有夹具的无效字段与文字/字体假设单独说明，未降低原断言门槛。最终8份当前图按2份直接查看、6份与此前已看原图整字节复用；另核对原导出卡确认外观差距，其余旧PNG只作交互原件保存。

原测试窗口已正常更新并打开历史列表，可见响应、Qt计时推进，启动及本批六私人路径保持；不分发私人内容/图片/哈希，无备份/恢复/回滚，不操作游戏或发送聊天。源码仍540份，前735选择器原序保持、当前736，下一完整455；full440仅证明原冻结源码，不作当前完整验收。界面其它外观、统计更多字段/完整数据、真实游戏连续读取和全部功能仍待完成。
''')
entry=f'''<!-- {stem}:start -->
## 界面实现维护 · {title}

实际测到隐藏统计页撑高历史窗，按原延期条件恢复修复后实测640×650；长内容页内滚动，四字段沿用外部Qt BSD Flow换行。统计数值和样本数前置，完整口径链接可展开；整局归档范围与单局阅读分开。修正重复热水壶完整样本被排除、来源失效冒称0局，保留原未知边界。

83项不同相关、56项当前原生检查通过，原406/408/432分别19/24/19项另验；当前8图按2份直接/6份整字节复用核对。旧三次高度失败与原两条计数失败保留；视频249/257/270秒深色横向卡仍与原导出卡不同，未销项。测试窗已更新打开历史，私人六路径保持。功能446、447未开，736有序选择器，下次完整455；全程序/视频及P3/P2/P1未完成。[回执](verification/maintenance/{stem}/summary.json)。
<!-- {stem}:end -->

'''
for name in('WORK_IN_PROGRESS.md','PROJECT_COMPLETED.md'):save(name,entry+(R/name).read_text('utf8'))
name='PROJECT_PROGRESS.md';s=(R/name).read_text('utf8');old='历史初始目标640×650实际640×699（3次修复失败，须先定位具体页的高度请求再恢复），';assert old in s;s=s.replace(old,'',1);s=s.replace('历史卡片结算/种子/完整资源及图标字段与其余视频交互/外观','历史卡片结算/种子/完整资源及图标字段、视频249/257/270秒深色横向大数字展示卡及收藏品/零件图标组合与其余视频交互/外观',1);save(name,s)
name='PROGRAM_REVIEW.md';save(name,(R/name).read_text('utf8')+f'\n[历史窗口与个人统计回顾](research/{stem}/README.md)已定位真实隐藏页的高度来源并达成初始640×650，结果/样本数前置且原完整口径可展开，修正多热水壶完整样本资格和失效冒称0局。83项相关与56项当前原生、19/24/19旧范围分别核对。原片深色大数字横卡、完整字段和其它视频外观仍未实现；源码仍540份。\n')
name='IMPLEMENTATION_STRATEGY.md';s=(R/name).read_text('utf8');old='历史精确高度仍640×699（目标640×650），先定位具体页的宽高布局请求再恢复修复。';assert old in s;s=s.replace(old,'历史精确高度已按隐藏统计页实测根因修正，当前完整流程640×650；统计长内容滚动、结果前置，源失效与真0局区分。',1);s=s.replace('下一步处理其它未核对外观、历史未明图标/完整数据、地图细节及连续读取','下一步优先核对原片深色横向大数字展示卡与图标组合，继续其它未核对外观、历史未明图标/完整数据、地图细节及连续读取',1);save(name,s)
name='VIDEO_PARITY.md';s=(R/name).read_text('utf8');old='精确初始640×650仍实际640×699，三次失败未销项；';assert old in s;s=s.replace(old,f'初始640×650已由[统计页根因测量与滚动维护](research/{stem}/README.md)实测达成，原三失败保留；',1)
lines=[]
for line in s.splitlines():
 if line.startswith('| 04:09'):line=line[:-1]+f' 本轮[个人统计阅读](research/{stem}/README.md)将均值/比例与分母前置、完整口径可展开，已确认重复热水壶的归档计入原完整清单分母；失效未知与真0局分开。结算、实托邦和组合字段仍未齐全。 |'
 if line.startswith('| 04:36'):line=line[:-1]+' 本轮新看249/257/270秒，原片为深色横向大数字与图片组合卡；当前浅色纵向导出卡仍有明显差距，不称外观一致。 |'
 lines.append(line)
save(name,'\n'.join(lines)+'\n')
name='PROJECT_REQUIREMENTS.md';s=(R/name).read_text('utf8');marker='P3→P2→P1；';assert marker in s;save(name,s.replace(marker,'个人统计先显示已证均值/比例及计入、未计入样本数，完整口径可展开；归档前最近读值不冒充结算或收益。统计来源是整个本机归档，不借所选单局的标题；资料不可读显示未知，只有明确空归档才显示0局。已证物理件数与不同藏品身份分开计数，完整清单资格保持一致。长内容和较大文字按实际可用宽高滚动/换行，不依赖隐藏页撑大外窗。视频深色横向展示卡仍须按真实效果另验，不用示例数值补本机。\n\n'+marker,1))
cp=read('DEVELOPMENT_CHECKPOINT.json');assert cp['completed_sections']==446 and cp['next_section']==447
receipt={'kind':'implementation_maintenance','title':title,'section':446,'functional_section_added':False,'passed':True,'acceptance_status':'listed_scope_passed_whole_video_pending','portrait_target_passed':True,'portrait_requested':[640,650],'portrait_actual':[640,650],'new_capability':'Actual compact history geometry and scrollable statistics; values/counts first, full scope link, known repeated-kettle sample eligibility and unavailable vs known-zero distinctions.','limitations':'Actual game/continuous reads, dark horizontal video presentation card and complete fields, whole-program/video andP3/P2/P1 remain incomplete.','source_sha256':{n:sha256((R/n).read_bytes()).hexdigest()for n in sources},'necessary_tests':83,'native_scopes_separate':{'current':56,'original406':19,'original408':24,'original432':19},'native_receipts':native,'local_test_window':pin(B/'live-window-final/window.json'),'source_review':pin(B/'source-review.json'),'image_review':pin(B/'root-image-review.json'),'full_suite_rerun':False,'old_full440_proves_current_source':False,'goal_active':True,'whole_program_or_video_complete':False,'at_UTC':datetime.now(timezone.utc).isoformat()};write(B/'summary.json',receipt)
cp['historical_notes_history_layout_maintenance_save']=cp.pop('current_maintenance_save')
cp['current_maintenance_save']={'kind':'implementation_maintenance','title':title,'receipt':f'verification/maintenance/{stem}/summary.json','binding':'enclosing_commit','functional_section_added':False,'status':'listed_scope_passed_video_presentation_card_pending','review_checklist':'PROGRAM_REVIEW.md','review_checklist_sha256':pin('PROGRAM_REVIEW.md')['sha256'],'application_review_complete':False}
cp['current_batch']['receipt']=f'verification/maintenance/{stem}/summary.json';cp['current_batch']['scope']='Whole-program/video review active. Functional446 unchanged. Actual640x650 closed from measured hidden-page root cause; statistics values and counts first, repeated-kettle sample eligibility and unknown source fixed. Dark horizontal video card and remaining full parity pending.447 not started.'
cp['next_action']='按原片249/257/270秒推进深色横向大数字展示卡与图标组合，先找外部成熟公开方案再本机适配；不补造结算、实托邦或示例数值。继续其余地图/历史细节与完整数据、OCR连续读取；历史精确640×650已核对销项。全程序/P3/P2/P1未完成，功能446、后续447，下次完整455。'
save('DEVELOPMENT_CHECKPOINT.json',json.dumps(cp,ensure_ascii=False,indent=2)+'\n');index=runpy.run_path(str(R/'scripts/update_cloud_index.py'));index['update'](R);assert index['validate_delivery'](R,cp)['current_section']==446
write(B/'final-audit.json',{'passed':True,'scope':'Listed implementation maintenance and publication readiness; not whole video completion.','functional_section':446,'functional_section_added':False,'next_section':447,'current_distinct_tests':83,'native_unique_checks':56,'additional_native_scopes':[19,24,19],'portrait_target_passed':True,'ordered_selectors':736,'next_full':455,'current_full_rerun':False,'requirements':pin('PROJECT_REQUIREMENTS.md'),'index':pin('CLOUD_INDEX.json'),'maintenance_receipt':pin(B/'summary.json'),'goal_active':True,'whole_program_or_video_complete':False})
(B/'record-source.py').write_bytes(Path(__file__).read_bytes());files={p.relative_to(R).as_posix():pin(p)for p in B.rglob('*')if p.is_file()and p.name!='archive-manifest.json'};write(B/'archive-manifest.json',{'kind':'explicit_public_archive_no_private_values_or_expected_private_hashes','files':files})
print(json.dumps({'recorded':True,'functional_section':446,'new_functional_section':False,'tests':83,'native_scopes_separate':[56,19,24,19],'actual_history':[640,650],'ordered_selectors':736,'public_archive_files':len(files),'whole_batch_private_six_unchanged':not changed,'whole_goal_complete':False}))
