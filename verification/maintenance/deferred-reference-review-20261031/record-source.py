from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import json,subprocess,difflib,runpy,sys,ast,re,statistics
R=Path.cwd();base='0a3b7b0b177eed6147c47ebea2700b7ec5832486';stem='deferred-reference-review-20261031';B=R/'verification/maintenance'/stem
title='四个资料目录按需填充与准确分类直接打开'
def read(n):return json.loads((R/n).read_bytes())
def write(n,v):(R/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf8')
def pin(n):
 raw=(R/n).read_bytes();return {'path':str(n).replace('\\','/'),'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}
def save(n,s):
 p=R/n
 if not p.exists():p.write_text(s,'utf8');return
 a=p.read_bytes().decode('utf8').splitlines(keepends=True);b=s.splitlines(keepends=True)
 for x,y,k in difflib.SequenceMatcher(None,[v.rstrip('\r\n')for v in a],[v.rstrip('\r\n')for v in b],autojunk=False).get_matching_blocks():b[y:y+k]=a[x:x+k]
 p.write_bytes(''.join(b).encode('utf8'))
assert subprocess.check_output(['git','rev-parse','HEAD']).decode().strip()==base
assert subprocess.check_output(['git','branch','--show-current']).decode().strip()=='codex/p2-development'
tests=read(f'verification/maintenance/{stem}/tests-final/results.json');assert tests['passed']and tests['tests_run']==50 and not tests['failed']and not tests['errors']and not tests['skipped']and not tests['forbidden_external_calls']
assert read(f'verification/maintenance/{stem}/tests-final/process.json')['actual_observed_exit']==0
ids=re.findall(r'^test_\w+ \(([^)]+)\)',(B/'tests-final/stderr.txt').read_text('utf8'),re.M);assert len(ids)==len(set(ids))==50
native=read(f'verification/maintenance/{stem}/native-final/window.json');assert native['passed']and native['unique_checks']==43 and not native['source_drift']and not any(native['external_operation_attempts'].values())
assert read(f'verification/maintenance/{stem}/native-final/process.json')['actual_observed_exit']==0
for n,digest in native['source_sha256_after'].items():assert sha256((R/n).read_bytes()).hexdigest()==digest,n
write(f'verification/maintenance/{stem}/native-final/root-image-review.json',{'actual_current_PNG_viewed':True,'images':native['screenshots'],'appearance_not_a_substitute_for_43_native_interactions':True,'no_new_video_layout_or_game_accuracy_claim':True})
benchmark=read(f'verification/maintenance/{stem}/benchmark-final/summary.json');assert benchmark['passed']and benchmark['independent_process_pairs']==3
whole={mode:[]for mode in('before','after')};first={}
for i in range(3):
 assert read(f'verification/maintenance/{stem}/benchmark-final/{i}-process.json')['actual_observed_exit']==0
 row=read(f'verification/maintenance/{stem}/benchmark-final/{i}-result.json');assert row['passed']and row['external_attempts']==0
 for data in row['rows']:
  whole[data['mode']].append(data['startup_ms']+sum(v['milliseconds']for v in data['lookups']))
  if data['mode']=='after':assert all(v==0 for v in data['initial_directory_counts'].values())
write(f'verification/maintenance/{stem}/benchmark-final/scope.json',{'initial_serial_before_final_navigation_order_change':'verification/maintenance/'+stem+'/benchmark/summary.json','current_final_measurements':pin(f'verification/maintenance/{stem}/benchmark-final/summary.json'),'first_final_pair_overlapped_independent_validation_processes':True,'machine_load_influences_absolute_latency':True,'three_processes_small_sample':True,'constructor_plus_all_ten_lookups_median_ms':{mode:statistics.median(v)for mode,v in whole.items()},'not_cold_process_startup_or_game_FPS':True,'work_is_deferred_to_first_lookup':True})
changes={}
for current,oldname,allowed_changed,allowed_added in [('rouge/app.py','before-app.py',{'__init__','reference_panel'},set()),('rouge/expansion_view.py','before-expansion_view.py',{'__init__','_populate'},{'ensure_populated','showEvent'})]:
 old=(R/'research'/stem/oldname).read_bytes();assert old==subprocess.check_output(['git','show',base+':'+current])
 def methods(raw):return {n.name:ast.dump(n,include_attributes=False)for c in ast.parse(raw).body if isinstance(c,ast.ClassDef)for n in c.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
 before,after=methods(old),methods((R/current).read_bytes());changed={n for n in before.keys()&after.keys()if before[n]!=after[n]};added=after.keys()-before.keys()
 assert changed==allowed_changed and added==allowed_added and not before.keys()-after.keys(),(current,changed,added)
 changes[current]={'changed_methods':sorted(changed),'added_methods':sorted(added),'all_other_methods_AST_unchanged':True}
sources=['rouge/app.py','rouge/expansion_view.py','scripts/verify_full_available.py','tests/test_deferred_reference_review.py']
write(f'verification/maintenance/{stem}/source-review.json',{'base_commit':base,'changed_or_new_sources':{n:pin(n)for n in sources},'method_AST_review':changes,'application_source_files':538,'new_application_modules':0,'REA_scope':'REA skill routes complete Python sources to direct source/runtime review. No new REA tool call or whole-program conclusion.','reuse':'Existing Qt showEvent, exact reference category routing, refresh_reference and fixed-source validation; no new loader framework, model, dependency or source cache.','removed_redundancy':'Removed unreachable negative combo index check after supported category admission; combo categories and routing keys are constructed from the same fixed list, all ten tested. Type/key qualification stays at entry.','new_low_probability_defensive_layer':False,'no_calculation_formula_or_OCR_algorithm_change':True,'whole_program_code_constraints_complete':False})
live=read(f'verification/maintenance/{stem}/live-window/window.json');assert live['passed']and live['private_six_paths_unchanged']
status=read('.cache/deferred-reference-review-live-status.json');assert status['toolbar_visible']and status['elapsed_since_launch']>4
write(f'verification/maintenance/{stem}/live-window/desktop-review.json',{'actual_Windows_mcp_screenshot_region':[1716,1164,2130,1218],'actual_toolbar_viewed_visible_responding_timer_advanced':True,'startup_six_private_paths_unchanged':True,'not_live_game_or_full_video_verification':True})
before=read('.cache/deferred-reference-review-before.json')['private'];changed=[n for n,v in before.items()if(sha256((R/n).read_bytes()).hexdigest()if(R/n).is_file()else None)!=v]
write(f'verification/maintenance/{stem}/private-scope.json',{'whole_batch_private_six_unchanged':not changed,'changed_paths_if_any':changed,'change_origin_not_inferred':bool(changed),'startup_six_unchanged':True,'private_contents_hashes_images_or_expected_values_published':False,'no_private_backup_restore_or_rollback':True})
write(f'verification/maintenance/{stem}/failure-disposition.json',{'first_implementation_failure':'verification/maintenance/startup-review-20261031-after/failure.json','cause':'Own initial method insertion placed constructor tail under showEvent. Repaired constructor boundary; original faulty source retained. Not a claimed preexisting defect.','native_attempts':['native','native-verified','native-verified-final'],'fixture_corrections':['Harness already requested relics, so only the other three directories remain unopened at the extension point.','Existing notes apply only to stages/scenes; all four query menus exist, eligible two note actions checked.','Harness left a support-name search; all-category enumeration explicitly clears that test search.'],'final_native':'native-final/window.json','original_failures_kept':True,'no_source_threshold_or_product_scope_weakened':True})
save(f'research/{stem}/README.md',f'''# {title}

基线{base}，当前功能443、444未开始。本轮为完整程序回顾维护，不新增功能节数，完整程序与视频效果仍未完成。

## 从实际运行定位

隔离空局真实Windows Qt构建的cProfile约1.77秒，其中4个未打开的ExpansionUpdatePanel构造/填充合计约0.35秒；固定资料packet共9次。剖析本身带开销，不作为生产启动基准。修复后独立剖析约1.49秒、packet4次；其它初始算例和隐藏面板成本仍保留待办，不从此推断全部应延迟。

普通玩家布局的四个通用资料目录只先创建原控件，首次显示、明确分类查找或显式核对时才填充。复用Qt showEvent与原refresh_reference；所有数据仍通过原来源核验，不加全局资料缓存、加载框架或新的异常吞没。独立阅读器默认立即填充、原诊断布局保持立即填充。MainWindow直接请求非默认分类时先选准确分类再显示，避免先填一次未请求的默认分类。重复ensure不重新读取或重置选择。

移除reference_panel中入口已确认分类后重复判断组合框索引为负的分支：分类路由与选项由同一固定构造表产生；十类全部核对，未知类型/键仍在入口拒绝。资料路径核验、私人保存与防重复发送未因低发生率移除。ensure用于首次显示和精确查询两个入口，不为单次逻辑另建通用层。

## 结果与边界

最终50项不同必要检查通过，0失败/错误/跳过；43项真实原生窗口检查通过，最终图已实际查看。十类目录的顺序、标题、首项中文/技术正文与全部查询动作状态和改动前一致；主窗口精确跳转、未知分类入口、保留阅读、资料丢失清空与恢复不追选已核对。其它方法AST保持，数值公式和识别代码未改；不重跑未变的87技能或443图像检查，也不冒称它们本轮重新实测。

三份独立Qt进程各暖一次再交错比较旧/新构造，最终中位约{benchmark['before_median_ms']:.1f}→{benchmark['after_median_ms']:.1f}毫秒。首组与其它验证进程重叠，绝对延迟受机器负载影响；前一份顺序串行证据中位约837→583毫秒属于先前导航顺序，分开保留。目录工作移到首次查询，首次打开并非免费；全十类查找耗时随原始值保留，不推广为冷进程启动、所有操作/机器或游戏FPS提升。

第一轮补丁误放构造尾部导致query_menu缺失，已修复且保留错误源码/实际失败。三个原生断言的前置假设分别错误：共享框架已读藏品、笔记只适用两类、上轮搜索尚在；均按真实流程修正，原件未覆盖，未放宽产品来源核验。旧功能443回执仍只证明原功能源码；当前维护证据独立，下次完整455，未重跑全量。727登记选择器追加且保留旧次序，不等于执行727模块。

实际测试小窗已更新可见响应、Qt计时器推进，启动六私人路径保持；整批摘要核对另见private-scope.json，有变化不归因或回滚。未操作游戏、发送聊天或上传私人数据。通用目录原有排版及其它视频交互/外观、其余初始化和完整P3/P2/P1仍未完成。

[维护回执](../../verification/maintenance/{stem}/summary.json)。
''')
summary={'kind':'implementation_review_maintenance','section':443,'title':title,'passed':True,'functional_section_added':False,'baseline_commit':base,'changed_source':{n:sha256((R/n).read_bytes()).hexdigest()for n in sources},'necessary_distinct_tests':50,'native_unique_checks':43,'native_receipt':pin(f'verification/maintenance/{stem}/native-final/window.json'),'source_review':pin(f'verification/maintenance/{stem}/source-review.json'),'benchmark':pin(f'verification/maintenance/{stem}/benchmark-final/summary.json'),'whole_program_review_complete':False,'whole_video_parity_complete':False,'P3_P2_P1_complete':False,'goal_active':True,'next_full_section':455,'at_UTC':datetime.now(timezone.utc).isoformat()}
write(f'verification/maintenance/{stem}/summary.json',summary)
entry=f'''<!-- {stem}:start -->
## 实现回顾维护 · {title}

四个未打开目录不再启动即填充，首次显示/准确查询复用原核验入口；非默认分类先定位再显示，独立与诊断布局保留原立即填充。重复负索引判断移除，其它方法AST不变；没有新缓存、依赖或异常吞没。

50项不同必要检查、43项原生检查通过，十类完整顺序/首项正文/动作状态与旧实现一致；三进程暖构建与首次查询成本分开记录，机器负载/初次工作后移不隐去，不称冷启动/FPS提升。初始构造补丁和三个夹具假设错误原件保留。测试小窗更新可见响应、启动六私人路径保持。功能443、未开444；全程序/视频和P3/P2/P1未完成，下次完整455。[回执](verification/maintenance/{stem}/summary.json)。
<!-- {stem}:end -->

'''
for n in('WORK_IN_PROGRESS.md','PROJECT_COMPLETED.md'):
 s=(R/n).read_text('utf8')
 if n=='WORK_IN_PROGRESS.md':s=s[s.index('<!-- player-section-443 -->'):]
 save(n,entry+s)
n='PROGRAM_REVIEW.md';s=(R/n).read_text('utf8').replace('其它隐藏面板是否应按需创建、全部窗口与视频逐页对应。','其余隐藏工具和初始算例的预计算成本、全部窗口与视频逐页对应。',1)
save(n,s+f'\n[四个通用目录按需填充回顾](research/{stem}/README.md)保留来源/精确跳转与十类完整阅读，50项检查及43项原生范围通过；不代表其它初始化、全程序或视频效果完成。\n')
n='PROJECT_PROGRESS.md';s=(R/n).read_text('utf8').replace('其余输入/导入路径及隐藏面板启动成本','其余输入/导入路径及其它隐藏工具/初始算例的预计算成本');save(n,s)
for n in('IMPLEMENTATION_STRATEGY.md','VIDEO_PARITY.md'):
 save(n,(R/n).read_text('utf8')+f'\n[资料目录按需填充维护](research/{stem}/README.md)只调整四个未读目录的填充时点及精确分类打开次序，复用现有Qt与来源核验；当前窗口排版、原片其它外观/流程与完整性能仍待对照，不算新增功能节。\n')
n='PROJECT_REQUIREMENTS.md';s=(R/n).read_text('utf8');marker='## 商店信息读取与历史';assert marker in s
s=s.replace(marker,'资料初始化优化须保留首次打开和精确分类跳转的可用性、来源核验与阅读状态；延后工作应计入首次查询成本，不能只用构造耗时宣称完整流程提速。\n\n'+marker,1);save(n,s)
cp=read('DEVELOPMENT_CHECKPOINT.json');assert cp['completed_sections']==443 and cp['next_section']==444
cp['current_maintenance_save']={'kind':'implementation_maintenance','title':title,'receipt':f'verification/maintenance/{stem}/summary.json','binding':'enclosing_commit','functional_section_added':False,'status':'partial_program_review_reference_population_deferred','review_checklist':'PROGRAM_REVIEW.md','review_checklist_sha256':pin('PROGRAM_REVIEW.md')['sha256'],'application_review_complete':False}
cp['current_batch']['receipt']=f'verification/maintenance/{stem}/summary.json'
cp['next_action']='继续完整程序与视频逐链路回顾，保留四个目录按需填充与精确跳转；其余隐藏工具/初始算例成本、P3资料/地图/物品条件和窗口排版及连续读取继续核对。OCR同步；全程序、视频、P3/P2/P1和完整数值仍未完成。功能443，444未启动，下次完整455。'
save('DEVELOPMENT_CHECKPOINT.json',json.dumps(cp,ensure_ascii=False,indent=2)+'\n')
idx=runpy.run_path(str(R/'scripts/update_cloud_index.py'));idx['update'](R);assert idx['validate_delivery'](R,cp)['current_section']==443
sys.path.insert(0,str(R/'scripts'));from verify_full_available import maintained_selectors
old=runpy.run_path(str(R/'scripts/verify_full_available.py'));assert len(maintained_selectors())==727
write(f'verification/maintenance/{stem}/final-audit.json',{'passed':True,'functional_section':443,'functional_section_added':False,'next_section':444,'current_distinct_tests':50,'native_unique_checks':43,'ordered_selectors':727,'next_full':455,'current_full_rerun':False,'requirements':pin('PROJECT_REQUIREMENTS.md'),'index':pin('CLOUD_INDEX.json'),'maintenance_receipt':pin(f'verification/maintenance/{stem}/summary.json'),'goal_active':True,'whole_program_or_video_complete':False})
(B/'record-source.py').write_bytes(Path(__file__).read_bytes())
files={}
for folder in [B,*sorted((R/'verification/maintenance').glob('startup-review-20261031*'))]:
 files.update({p.relative_to(R).as_posix():{k:v for k,v in pin(p.relative_to(R)).items()if k!='path'}for p in folder.rglob('*')if p.is_file()and p.name!='archive-manifest.json'})
write(f'verification/maintenance/{stem}/archive-manifest.json',{'kind':'explicit_public_archive_no_private_contents_or_expected_values','files':files})
print(json.dumps({'recorded':True,'functional_section':443,'new_section_added':False,'necessary_distinct_tests':50,'native_unique_checks':43,'public_archive_files':len(files),'whole_goal_complete':False}))
