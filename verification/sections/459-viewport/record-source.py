from pathlib import Path
from hashlib import sha256
from datetime import datetime, timezone
import json, subprocess, runpy, difflib, sys, ctypes
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts'),str(R/'.cache/305-window-tooldeps')]
B=R/'verification/sections/459-viewport';D=R/'research/viewport-459';D.mkdir(exist_ok=True)

def read(p):return json.loads((R/p).read_bytes())
def pin(p):
 raw=(R/p).read_bytes();return {'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}
def write(p,x):(R/p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf8')
def save(p,s):
 p=R/p;old=p.read_bytes().decode('utf8').splitlines(keepends=True)if p.exists()else[];new=s.splitlines(keepends=True)
 for x,y,k in difflib.SequenceMatcher(None,[v.rstrip('\r\n')for v in old],[v.rstrip('\r\n')for v in new],autojunk=False).get_matching_blocks():new[y:y+k]=old[x:x+k]
 p.write_bytes(''.join(new).encode('utf8'))

unit=[]
for name, count in [('necessary01',53),('necessary-navigation',13)]:
 u=read(B/name/'results.json');p=read(B/name/'process.json')
 assert u['passed']and u['tests_run']==count and not(u['failed']or u['errors']or u['skipped']or u['forbidden_external_calls'])
 assert p['actual_observed_exit']==0 and p['tested_source_unchanged']
 for n,h in read(B/name/'source-before.json').items():assert pin(n)['sha256']==h,n
 unit.append({'result':f'verification/sections/459-viewport/{name}/results.json','process':f'verification/sections/459-viewport/{name}/process.json','tests_run':count})
native={}
for name in ['native-final','native-web']:
 n=read(B/name/'window.json');p=read(B/name/'process.json')
 assert n['passed']and not n['source_drift']and not any(n['external_operation_attempts'].values())and p['actual_observed_exit']==0
 for path,h in {**n['source_sha256_after'],**read(B/name/'additional-source-before.json')}.items():assert pin(path)['sha256']==h,path
 native[name]={'receipt':f'verification/sections/459-viewport/{name}/window.json','unique_checks':n['unique_checks']}
rows=read(B/'native-final/observations.json')['records'];assert all(r['actual']==r['preferred']and r['viewport_size'][1]>=120 for r in rows)
assert rows[-1]['last_visible_rect'][0]>=0 and rows[-1]['last_visible_rect'][1]<rows[-1]['viewport_size'][1]
private=read('.cache/viewport459-private-before.json');assert all((sha256((R/p).read_bytes()).hexdigest()if(R/p).is_file()else None)==h for p,h in private.items())
import win32gui,win32process
status=read('.cache/viewport459-live-status.json');hwnd=status['native_host']
assert status['toolbar_visible']and status['main_reference_visible']and win32gui.IsWindowVisible(hwnd)and not ctypes.windll.user32.IsHungAppWindow(hwnd)
live=read(B/'live-window-final/window.json');assert live['private_six_paths_unchanged']
live.update(desktop_visual_review_pending=False,desktop_visual_review={'tool':'Windows-mcp Screenshot','observed':'Updated light map and compact toolbar visible; native window responds.','private_screenshot_published':False},final_native_window={'hwnd':hwnd,'pid':win32process.GetWindowThreadProcessId(hwnd)[1],'visible':True,'responding':True})
write(B/'live-window-final/window.json',live)
reviewed=[f'verification/sections/459-viewport/native-final/notes-{n}.png'for n in ['empty','edit','read']]+[f'verification/sections/459-viewport/native-web/{n}.png'for n in ['ro6_n_1_2-website-map','real-website-simulator-playing']]
write(B/'image-review.json',{'reviewed_images':{p:pin(p)for p in reviewed},'observed':'Compact light notebook in empty/edit/read states; website map and play/pause in the same shared native host.','review_tool':'view_image','all_listed_images_reviewed':True})
profile=read(B/'ocr-profile-quiet/results.json');assert profile['passed']and profile['recognition_sources_unchanged']and profile['same_pixel_output_equality_checked']
assert len(profile['rows'])==12 and all(r['identical_frame_facts_equal']for r in profile['rows'])
assert read(B/'ocr-profile-quiet-process.json')['actual_observed_exit']==0
for p,h in read(B/'ocr-profile-quiet/source-before.json').items():assert pin(p)['sha256']==h,p
for folder,script,wrapper in [('ocr-profile','profile_viewport459_ocr.py','run_viewport459_ocr.py'),('ocr-profile-quiet','profile_viewport459_ocr_quiet.py','run_viewport459_ocr_quiet.py')]:
 (B/folder/'measurement-source.py').write_bytes((R/'.cache'/script).read_bytes());(B/folder/'runner-source.py').write_bytes((R/'.cache'/wrapper).read_bytes())
write(B/'usage.json',{'primary_used_percent':71,'primary_remaining_percent':29,'secondary_available':False,'source':'Codex get_usage_limits read this turn','reset_credits_used':False})
names=subprocess.check_output(['git','diff','--name-only','-z']).decode('utf8').split('\0')+subprocess.check_output(['git','ls-files','--others','--exclude-standard','-z']).decode('utf8').split('\0')
sources=sorted({p for p in names if p.startswith(('rouge/','tests/'))and p.endswith('.py')})
assert sources==['rouge/player_reference_window.py','tests/test_reference_viewport_459.py'],sources
title='主资料窗自适应滚动阅读';scope='主资料窗保持紧凑尺寸，长正文可以完整滚动阅读；标题栏随当前页面调整，返回后保留阅读位置。修正从藏品页切换后标题过高、首次笔记增高的问题。'
remaining='继续其余深层资料与公开档案整合、笔记排版和视频细节对齐；识别优先减少整页文字处理与本局信息解析的重复工作。'
write(B/'source-review.json',{'section':459,'changed_or_new_sources':{p:pin(p)for p in sources},'review':'Use documented Qt QScrollArea for each retained ToolPage body; its viewport bounds active height-for-width layout. PageHeaders sizeHint/minimumSizeHint use the active header rather than the maximum of all registered pages. Keep dynamic visible-header wrapping, original source/draft guards, browser and reader ownership. No new dependencies, broad catches or retry layer.','whole_program_review_complete':False})
write(D/'reuse.json',{'adopted':'Qt/PySide6 QScrollArea, installed PySide6 6.11.2','primary_documentation':'https://doc.qt.io/qtforpython-6/PySide6/QtWidgets/QScrollArea.html','reason':'Existing native Qt widget directly supplies resizable content and ensureWidgetVisible; no new scrolling framework is needed. Existing qframelesswindow0.8.2 and PyQtDarkTheme2.1.0 sources/attribution retained.','adaptation':'One independent viewport per retained page; current-header sizing keeps hidden tall resource headers from taking visible body space.','additional_third_party_dependency':False})
write(D/'geometry.json',{'original_451':'../../verification/sections/451-reference-window/unresolved-size.json','new_evidence_458':'../note-references-458/geometry-findings.json','baseline':'../../verification/sections/459-viewport/probe-baseline/observations.json','scroll_only':'../../verification/sections/459-viewport/probe-scroll/observations.json','header_diagnostic':'../../verification/sections/459-viewport/probe-scroll-diagnostic/observations.json','final':'../../verification/sections/459-viewport/native-final/observations.json','cause':['Active word-wrapped content propagated height-for-width to the top-level dialog.','After inventory registration, the header stack retained its 280px aggregate size hint; short pages lost body space.'],'result':'Per-page viewport plus current-header size hints retains requested sizes for9 primary pages, notebook edit/read and long-content page. Last control remains reachable.','first_open_notebook_growth_fixed_in_recorded_primary_sequence':True,'other_video_layout_work':'Continue remaining entry points, typography and very small available-area layouts.'})
quiet=profile['rows'];full=[r for r in quiet if r['reuse']=='none'];same=[r for r in quiet if r['repeat_same_pixels']]
write(D/'recognition-profile.json',{'receipt':'../../verification/sections/459-viewport/ocr-profile-quiet/results.json','source_binding':'../../verification/sections/459-viewport/ocr-profile-quiet/source-before.json','video_sha256':profile['reference_video_sha256'],'sampled_seconds':[44,44.05,52,52.05,60,95],'reads':12,'same_pixel_fact_equalities':len(same),'full_read_ms':[r['total_ms']for r in full],'same_pixel_repeat_ms':[r['total_ms']for r in same],'finding':'Full OCR and run parsing dominate these four distinct video frames; map extraction is also material on the60s frame. Identical-frame reuse is already fast.','previous_measurement':'Earlier exploratory profile overlapped navigation test execution; quiet profile is used for the cost diagnosis.','scope':'Offline reference-video composite frames, not a client-crop accuracy set or a gameplay throughput measurement. No recognition algorithm change or before/after speedup claim.','next':'Inspect run parsing subcosts and avoid re-reading the same useful text while retaining field attribution and current-page source qualification.','versions':{'PySide6':'6.11.2','rapidocr_onnxruntime':'1.4.4','onnxruntime':'1.30.0','opencv-python':'4.14.0.94'}})
save(D/'README.md',f'# 第459节 + {title}\n\n{scope}\n\n66项定向检查通过；主页面原生检查52项、嵌入网页检查47项通过。笔记编辑、来源跳转、返回阅读以及网页地图和路线演算均已核对，测试窗口已更新。\n\n复用Qt滚动容器，修正按宽算高传递与隐藏标题的尺寸影响。[尺寸记录](geometry.json) · [复用说明](reuse.json) · [识别测量](recognition-profile.json) · [回执](../../verification/sections/459.json)。\n\n{remaining}\n')
entry=f'## 第459节 + {title}\n\n{scope}\n\n66项定向检查、52项主页面原生检查和47项嵌入网页检查通过；测试窗口已更新。[验收记录](verification/sections/459.json)。\n\n'
for p in ['WORK_IN_PROGRESS.md','PROJECT_COMPLETED.md']:
 s=(R/p).read_bytes().decode('utf8')
 if p=='WORK_IN_PROGRESS.md':s=s[s.index('## 第458节 +'):]
 save(p,entry+s)
p='PROJECT_PROGRESS.md';s=(R/p).read_bytes().decode('utf8').replace('核对首次切换后窗口异常增高及剩余阅读状态/导航外观；','核对其余阅读状态、导航外观和极小区域的排版；',1);save(p,s)
p='PROJECT_REQUIREMENTS.md';s=(R/p).read_bytes().decode('utf8').replace('当前功能第458节','当前功能第459节',1);s+='\n主资料窗的长内容在正文区域滚动阅读，外窗保持玩家设定的尺寸；标题栏随当前页面内容调整，返回时保留各页阅读位置。\n';save(p,s)
for p,t in [('VIDEO_PARITY.md','主资料窗新增独立正文滚动区域，标题栏按当前页调整；笔记、地图与嵌入网站保持紧凑阅读和返回状态。'),('IMPLEMENTATION_STRATEGY.md','优先采用Qt现成滚动容器，保留原有页面与成熟窗框；以实际尺寸追踪定位两处布局影响，避免反复叠加最小尺寸补丁。'),('PROGRAM_REVIEW.md','完成当前主资料页的正文滚动、隐藏高标题、首次笔记尺寸及导航/草稿/网页回归；识别测量定位整页OCR与run解析开销，后续定向减少重复处理。')]:save(p,(R/p).read_bytes().decode('utf8')+f'\n[第459节](research/viewport-459/README.md)：{t}\n')
write('verification/sections/459.json',{'section':459,'kind':'functional_section','title':title,'new_capability':scope,'passed':True,'passed_scope':'Independent scrollable ToolPage bodies, visible-header-only sizing,9 primary-page requested sizes after event delivery, notebook empty/edit/read, reachable long-content last control; source/draft/navigation tests and actual embedded website map/play/pause retained.','limitations':remaining,'unit_tests_run':66,'necessary_validation':unit,'native_windows_scopes':native,'recognition_profile':'verification/sections/459-viewport/ocr-profile-quiet/results.json','recognition_algorithm_changed':False,'source_sha256':{p:pin(p)['sha256']for p in sources},'source_review':'verification/sections/459-viewport/source-review.json','actual_local_test_window':'verification/sections/459-viewport/live-window-final/window.json','full_checks_cancelled':True,'full_suite_rerun':False,'whole_program_or_video_complete':False,'goal_active':True,'at_UTC':datetime.now(timezone.utc).isoformat()})
cp=read('DEVELOPMENT_CHECKPOINT.json');assert cp['completed_sections']==458 and cp['next_section']==459
cp.update(completed_sections=459,next_section=460,batch_status='ACTIVE_AFTER459');cp['sections'].append({'number':459,'completion_ref':'player-section-459','topic':title,'verification':'verification/sections/459.json'})
cp['current_section_save']={'section':459,'verification':'verification/sections/459.json','scope':'current_functional_section','binding':'enclosing_commit'};cp['last_verified_cloud_save']['scope']='previous_functional_section'
cp['current_section_validation']={'section':459,'receipt':'verification/sections/459.json','necessary_checks':66,'native_scopes':{k:v['unique_checks']for k,v in native.items()},'full_validation_rerun':False}
cp['current_batch'].update(status='ACTIVE_AFTER459',completed_sections=459,next_section=460,next_section_started=False,receipt='verification/sections/459.json',scope=scope)
cp['policy'].update(current_usage_remaining_percent=29,current_usage_receipt='verification/sections/459-viewport/usage.json')
cp['next_action']='继续其余深层资料与公开档案整合、笔记排版和视频细节；按公开帧测量定位本局信息解析中的重复文字处理，再做字段一致和耗时对照。'
cp['functional_sections_since_latest_requirement'].append(459)
if isinstance(cp.get('player_feature_sections'),list):cp['player_feature_sections'].append(459)
save('DEVELOPMENT_CHECKPOINT.json',json.dumps(cp,ensure_ascii=False,indent=2)+'\n')
idx=runpy.run_path(str(R/'scripts/update_cloud_index.py'));idx['update'](R);idx['validate_delivery'](R,cp)
write(B/'final-audit.json',{'passed':True,'section':459,'necessary_distinct_tests':66,'native_checks':native,'private_six_unchanged':True,'full_checks_cancelled':True,'goal_active':True,'requirements':pin('PROJECT_REQUIREMENTS.md'),'index':pin('CLOUD_INDEX.json')})
(B/'record-source.py').write_bytes(Path(__file__).read_bytes())
files={p.relative_to(R).as_posix():pin(p)for root in(B,D)for p in root.rglob('*')if p.is_file()and p.name!='archive-manifest.json'};files['verification/sections/459.json']=pin('verification/sections/459.json')
write(B/'archive-manifest.json',{'kind':'explicit_public_section459_no_private_cache_models_or_video','files':files})
print(json.dumps({'section':459,'necessary_distinct_methods':66,'native_checks':native,'public_files':len(files),'goal_active':True}))
