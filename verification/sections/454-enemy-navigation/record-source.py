from pathlib import Path
from hashlib import sha256
from datetime import datetime, timezone
import json, subprocess, runpy, difflib, sys, ctypes
R = Path.cwd()
sys.path[:0] = [str(R), str(R/'scripts'), str(R/'.cache/305-window-tooldeps')]
B = R/'verification/sections/454-enemy-navigation'
D = R/'research/enemy-navigation-454'
D.mkdir(exist_ok=True)

def read(p): return json.loads((R/p).read_bytes())
def pin(p):
    raw = (R/p).read_bytes()
    return {'sha256':sha256(raw).hexdigest(), 'bytes':len(raw)}
def write(p, x): (R/p).write_text(json.dumps(x, ensure_ascii=False, indent=2)+'\n', 'utf8')
def save(p, s):
    p = R/p
    old = p.read_bytes().decode('utf8').splitlines(keepends=True) if p.exists() else []
    new = s.splitlines(keepends=True)
    for x,y,k in difflib.SequenceMatcher(None,[v.rstrip('\r\n')for v in old],[v.rstrip('\r\n')for v in new],autojunk=False).get_matching_blocks(): new[y:y+k] = old[x:x+k]
    p.write_bytes(''.join(new).encode('utf8'))

names = subprocess.check_output(['git','diff','--name-only','-z']).decode('utf8').split('\0') + subprocess.check_output(['git','ls-files','--others','--exclude-standard','-z']).decode('utf8').split('\0')
sources = sorted({p for p in names if p.startswith(('rouge/','tests/')) and p.endswith('.py')})
runs = []
count = 0
for name in ['navigation-final','standalone-final','copy-final2','map-final2','guest-source-isolated']:
    p = B/name; x = read(p/'results.json'); proc = read(p/'process.json')
    assert x['passed'] and not (x['failed'] or x['errors'] or x['skipped'] or x['forbidden_external_calls']) and proc['actual_observed_exit']==0 and proc['tested_source_unchanged']
    drift = [n for n,h in read(p/'source-before.json').items() if sha256((R/n).read_bytes()).hexdigest()!=h]
    # One unrelated copy assertion was updated after the independent navigation/standalone runs ended.
    if name in ['navigation-final','standalone-final']: assert set(drift) <= {'tests/test_battle_overview_sections_review.py'}, drift
    else: assert not drift, drift
    count += x['tests_run']
    runs.append({'result':(p/'results.json').relative_to(R).as_posix(),'process':(p/'process.json').relative_to(R).as_posix(),'tests_run':x['tests_run'],'later_unrelated_test_assertion_change':drift,'product_and_executed_tests_unchanged':True})
n = read(B/'native-final2/window.json')
assert n['passed'] and not n['source_drift'] and not any(n['external_operation_attempts'].values()) and read(B/'native-final2/process.json')['actual_observed_exit']==0
for p,h in n['source_sha256_after'].items(): assert pin(p)['sha256']==h,p
assert read(B/'native-final2/image-review.json')['all_images_reviewed']
private = read('.cache/enemy454-private-before.json')
assert all((sha256((R/p).read_bytes()).hexdigest()if(R/p).is_file()else None)==h for p,h in private.items())
import win32gui, win32process
status = read('.cache/enemy454-live-status.json'); h = status['native_host']
assert status['toolbar_visible'] and status['main_reference_visible'] and win32gui.IsWindowVisible(h) and not ctypes.windll.user32.IsHungAppWindow(h)
live = read(B/'live-window-final/window.json')
live.update(desktop_visual_review_pending=False,desktop_visual_review={'tool':'Windows-mcp Screenshot','observed':'current shared map window and toolbar visible and responding','private_screenshot_published':False},final_native_window={'hwnd':h,'pid':win32process.GetWindowThreadProcessId(h)[1],'visible':True,'responding':True})
write(B/'live-window-final/window.json',live)
write(B/'usage.json',{'primary_used_percent':69,'primary_remaining_percent':31,'secondary':'unavailable','source':'read-only Codex usage tool this batch','strict_under15_triggered':False})
title = '敌人机制地图统一导航与说明精简'
scope = '七类敌人机制和五类固定地图接入主资料窗，支持逐级返回、保留阅读与格子选择，关联敌人可返回对应敌人页。精简地图、事件、作战和机制页面的重复说明，来源与适用范围收进“资料说明”。'
remaining = '后续：事件材料与反查、目录和完整工作区统一，首次打开高度问题，视频外观细节与识别覆盖、准确率、耗时。'
review = {'section':454,'changed_or_new_sources':{p:pin(p) for p in sources},'review':'Seven exact existing panels share retained parent-qualified pages. Elbert checks the original base source; Hanko preserves its original exception. Five map routes keep exact level/source verification. Related-enemy return selects the exact battle key. Default copy is shortened by exact presentation phrases and known scope sections; original mechanism models/data remain intact, full notes stay in the disclosure. Clearing a source clears old notes. No new dependency or defensive scaffolding.','whole_program_review_complete':False,'scope_details':'Native tests use real MainWindow factories, seven exact mechanisms and five maps. Legacy node catalogue does not bind ro6_b_7 and ro6_t_16; these use direct shared fixed-stage factories. Root map-binding chain retains section453 evidence.'}
write(B/'source-review.json',review)
write(B/'issues.json',{'retained_initial_failures':['enemy-01/results.json','copy-final/results.json','map-selected-final/process.json','grouped-native-review/process.json'],'corrections':['Related-enemy fixture corrected from ro6_b_6 to verified ro6_b_5; production mechanics unchanged.','Old assertion expecting 暂不可用 updated to the new 暂无敌人资料 label; clearing/recovery assertions retained.'],'native_process_review':{'combined_map_then_guest_test_exit':3221226505,'same_order_reproduced_twice':True,'restart_condition':'obtain a matched-PID native stack or a smaller lifecycle reproducer before another grouped retry','isolated_guest_and_separated_map_rerun_passed':True,'cause':'Not yet isolated; grouped-run native failure retained, not counted as passed.'},'map_selection_review':'Original native142 used a centre combo with no entries on some maps. Final native147 uses actual grid clicks and requires a nonempty (0,0) selection in all five maps.','remaining':remaining})
reuse = read('research/map-readers-452/reuse.json')
reuse['decision'] = 'Continue adopted mature Qt QStackedWidget and pinned LGPL frameless frame. Reuse the seven exact mechanism panels and fixed-map panels through small local navigation glue. Copy uses the existing collapsible disclosure; no extra package or framework.'
reuse['unknown'] = remaining
write(D/'reuse.json',reuse)
save(D/'README.md',f'# 第454节 + {title}\n\n{scope}\n\n本机必要检查{count}项、原生窗口{n["unique_checks"]}项通过，公开样例截图已逐张查看；测试窗口已更新。原失败与修正分开保存，私人六路径保持。\n\n{remaining}\n\n[回执](../../verification/sections/454.json) · [复用说明](reuse.json)\n')
entry = f'## 第454节 + {title}\n\n{scope}\n\n必要检查{count}项、原生窗口{n["unique_checks"]}项通过，测试窗口已更新。[验收记录](verification/sections/454.json)。\n\n'
for p in ['WORK_IN_PROGRESS.md','PROJECT_COMPLETED.md']: save(p,entry+(R/p).read_bytes().decode('utf8'))
p='PROJECT_PROGRESS.md';s=(R/p).read_bytes().decode('utf8').replace('继续将事件材料来源、作战反查完整事件、敌人机制等其余深层入口、笔记目录、公开档案与完整工作区迁入主资料浮窗；','继续将事件材料来源、作战反查完整事件等其余深层入口、笔记目录、公开档案与完整工作区迁入主资料浮窗；',1);s+='\n- 窗口验证维护：地图目录与旧独立机制窗口测试连续执行时，Qt进程两次异常退出；单独执行和真实主窗导航通过。保留原记录，取得原生调用栈或更小复现后定位。\n';save(p,s)
p='PROJECT_REQUIREMENTS.md';s=(R/p).read_bytes().decode('utf8').replace('当前功能第453节','当前功能第454节',1);save(p,s)
for p,t in [('VIDEO_PARITY.md','七类机制和五类固定地图已迁入同一主窗；默认说明精简、完整来源按需展开。'),('IMPLEMENTATION_STRATEGY.md','复用现有Qt主窗承载、机制面板和固定地图，保留各自准确来源判断；文案调整只在展示层。'),('PROGRAM_REVIEW.md','七类机制逐级导航、五类固定地图及关联敌人回跳已回顾；修正测试关卡与旧文案断言。完整程序回顾继续。')]:save(p,(R/p).read_bytes().decode('utf8')+f'\n[第454节](research/enemy-navigation-454/README.md)：{t}\n')
receipt={'section':454,'kind':'functional_section','title':title,'new_capability':scope,'passed':True,'passed_scope':review['scope_details'],'limitations':remaining,'unit_tests_run':count,'necessary_validation':runs,'native_windows_scopes':{'current':{'receipt':'verification/sections/454-enemy-navigation/native-final2/window.json','unique_checks':n['unique_checks']}},'source_sha256':{p:pin(p)['sha256']for p in sources},'source_review':'verification/sections/454-enemy-navigation/source-review.json','actual_local_test_window':'verification/sections/454-enemy-navigation/live-window-final/window.json','full_checks_cancelled':True,'full_suite_rerun':False,'whole_program_or_video_complete':False,'goal_active':True,'at_UTC':datetime.now(timezone.utc).isoformat()};write('verification/sections/454.json',receipt)
cp=read('DEVELOPMENT_CHECKPOINT.json');assert cp['completed_sections']==453 and cp['next_section']==454
cp.update(completed_sections=454,next_section=455,batch_status='ACTIVE_AFTER454');cp['sections'].append({'number':454,'completion_ref':'player-section-454','topic':title,'verification':'verification/sections/454.json'});cp['current_section_save']={'section':454,'verification':'verification/sections/454.json','scope':'current_functional_section','binding':'enclosing_commit'};cp['last_verified_cloud_save']['scope']='previous_functional_section';cp['current_section_validation']={'section':454,'receipt':'verification/sections/454.json','necessary_checks':count,'native_scopes':{'current':n['unique_checks']},'full_validation_rerun':False};cp['current_batch'].update(status='ACTIVE_AFTER454',completed_sections=454,next_section=455,next_section_started=False,receipt='verification/sections/454.json',scope=scope);cp['policy'].update(current_usage_remaining_percent=31,current_usage_receipt='verification/sections/454-enemy-navigation/usage.json');cp['next_action']='继续事件材料/反查和目录、完整工作区统一；默认说明简洁、来源展开。451首次高度须新几何证据，识别同步回顾。仅必要检查，全量机制保持关闭。';cp['functional_sections_since_latest_requirement'].append(454)
if isinstance(cp.get('player_feature_sections'),list):cp['player_feature_sections'].append(454)
save('DEVELOPMENT_CHECKPOINT.json',json.dumps(cp,ensure_ascii=False,indent=2)+'\n');idx=runpy.run_path(str(R/'scripts/update_cloud_index.py'));idx['update'](R);idx['validate_delivery'](R,cp)
write(B/'final-audit.json',{'passed':True,'section':454,'necessary_distinct_tests':count,'native_checks':n['unique_checks'],'private_six_unchanged':True,'full_checks_cancelled':True,'goal_active':True,'requirements':pin('PROJECT_REQUIREMENTS.md'),'index':pin('CLOUD_INDEX.json')})
(B/'record-source.py').write_bytes(Path(__file__).read_bytes())
files={p.relative_to(R).as_posix():pin(p)for root in(B,D)for p in root.rglob('*')if p.is_file()and p.name!='archive-manifest.json'};files['verification/sections/454.json']=pin('verification/sections/454.json');write(B/'archive-manifest.json',{'kind':'explicit_public_section454_no_private_cache_models_or_video','files':files})
print(json.dumps({'section':454,'necessary_distinct_methods':count,'native_checks':n['unique_checks'],'public_files':len(files),'goal_active':True}))
