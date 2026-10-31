from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import ast,ctypes,difflib,json,re,runpy,subprocess,sys,time
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts'),str(R/'.cache/305-window-tooldeps')]
BASE='be46c55462e3b7d2afeb644fcdefcff87ffdd178';B=R/'verification/maintenance/ocr-cache-review-20261031';prefix=B.relative_to(R).as_posix()+'/'
def read(n):return json.loads((R/n).read_bytes())
def pin(n):
 p=R/n;raw=p.read_bytes();return {'path':p.relative_to(R).as_posix(),'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}
def write(n,v):(R/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf8')
def text(n,v):
 p=R/n
 if not p.exists():p.parent.mkdir(parents=True,exist_ok=True);p.write_text(v,'utf8');return
 a=p.read_bytes().decode('utf8').splitlines(keepends=True);out=v.splitlines(keepends=True)
 for x,y,k in difflib.SequenceMatcher(None,[s.rstrip('\r\n')for s in a],[s.rstrip('\r\n')for s in out],autojunk=False).get_matching_blocks():out[y:y+k]=a[x:x+k]
 p.write_bytes(''.join(out).encode('utf8'))
def old(n):return subprocess.check_output(['git','show',BASE+':'+n])
assert subprocess.check_output(['git','rev-parse','HEAD']).decode().strip()==BASE
assert subprocess.check_output(['git','branch','--show-current']).decode().strip()=='codex/p2-development'
changed=['rouge/page_ocr.py','rouge/recognition_cache.py'];unchanged=['rouge/app.py','rouge/recognition.py','rouge/dynamic_ocr.py','rouge/capture.py','rouge/player_workspace.py','rouge/current_battle_reference.py','rouge/current_battle_view.py','rouge/enemy_overview.py','rouge/damage.py','rouge/run_state.py','rouge/account_cache.py']
for n in unchanged:assert old(n)==(R/n).read_bytes(),n
assert not subprocess.check_output(['git','diff','--name-only',BASE,'--','rouge/data']).strip()
def functions(raw):return {node.name:ast.dump(node,include_attributes=False)for node in ast.walk(ast.parse(raw))if isinstance(node,ast.FunctionDef)}
a=functions(old(changed[0]));b=functions((R/changed[0]).read_bytes());assert set(a)-set(b)=={'_cache_key'}and not(set(b)-set(a))
assert {name for name in b if a[name]!=b[name]}=={'_recognize_batch'}
a=functions(old(changed[1]));b=functions((R/changed[1]).read_bytes());assert set(a)==set(b)and {name for name in b if a[name]!=b[name]}=={'call'}
tests=read(prefix+'tests-current/results.json');assert tests['passed']and tests['tests_run']==89 and tests['failed']==tests['errors']==0 and not tests['skipped']and not tests['forbidden_external_calls']
ids=re.findall(r'^test_\w+ \(([^)]+)\)',(R/(prefix+'tests-current/stderr.txt')).read_text('utf8'),re.M);assert len(ids)==len(set(ids))==89
assert read(prefix+'tests-current/process.json')['actual_observed_exit']==0
benchmark=read(prefix+'benchmark/results.json');assert benchmark['passed']and len(benchmark['raw_frame_cases'])==4 and read(prefix+'benchmark-process.json')['actual_observed_exit']==0
for row in benchmark['raw_frame_cases']:
 assert pin(row['source'])['sha256']==row['source_sha256']and len(row['rounds'])==3
 assert all(r['complete_text_boxes_strings_confidences_equal_to_original_engine']for r in row['rounds'])
live=read(prefix+'live-window/window.json');assert live['passed']and live['private_six_paths_unchanged']
for n in changed:assert live['source_sha256_after'][n]==pin(n)['sha256']
import win32gui,win32process
for w in live['owned_windows']:assert win32gui.IsWindowVisible(w['hwnd'])and win32process.GetWindowThreadProcessId(w['hwnd'])[1]==w['pid']and not ctypes.windll.user32.IsHungAppWindow(w['hwnd'])
first=read('.cache/ocr-cache-review-live-status.json');time.sleep(2.2);last=read('.cache/ocr-cache-review-live-status.json');assert last['toolbar_visible']and last['elapsed_since_launch']>first['elapsed_since_launch']
write(prefix+'live-window/desktop-review.json',{'actual_Windows_MCP_snapshot_and_image_view':True,'region':[1716,1164,2130,1218],'test_window_visible_responding_and_Qt_timer_advanced':True,'private_six_paths_unchanged_during_startup':True,'private_contents_or_hashes_published':False,'game_operated':False,'chat_sent':False,'actual_game_OCR_validation_claimed':False})
for n in ('.cache/run_ocr_cache_checks.py','.cache/benchmark_ocr_cache_review.py','.cache/run_ocr_cache_benchmark.py','.cache/update_ocr_review_docs.py'):(B/Path(n).name).write_bytes((R/n).read_bytes())
(B/'tests-current/test-source.py').write_bytes((R/'tests/test_ocr_cache_review.py').read_bytes())
installed=R/'.venv/Lib/site-packages/rapidocr_onnxruntime'
write(prefix+'provider-source.json',{'distribution_version':'1.4.4','python_version':sys.version,'source_files':[{'file':n,'sha256':sha256((installed/n).read_bytes()).hexdigest(),'bytes':(installed/n).stat().st_size}for n in('main.py','ch_ppocr_rec/text_recognize.py')],'repository':'https://github.com/RapidAI/RapidOCR','python_mapping_reference':'https://docs.python.org/3.12/library/stdtypes.html#mapping-types-dict','new_provider_code_copied':False,'new_dependencies':False,'separate_v144_GitHub_tag_open_failed':True,'latest_upstream_not_claimed_equivalent_to_installed':True})
net=sum(len((R/n).read_bytes().splitlines())-len(old(n).splitlines())for n in changed)
write(prefix+'source-review.json',{'baseline_commit':BASE,'changed_source':[pin(n)for n in changed],'unchanged_callers_UI_capture_state_and_models':[pin(n)for n in unchanged],'all_PageOCR_methods_except_batch_and_removed_single_use_key_helper_AST_equal':True,'other_ExactImageCache_methods_AST_equal':True,'change':'Use Python built-in tuple/bytes dictionary equality for exact pixels, shape, dtype and original context/batch order, instead of SHA256 key plus second full byte check. Remove unreachable miss-side replacement and the single-use key helper. Disabled PageOCR cache no longer serializes cache keys.','retained':'Current full detection, original recognition batch ordering/padding, classification, confidence, coordinates, configuration invalidation, force discovery, deep copies, memory/entry budgets and frame snapshot provenance.','new_low_probability_defensive_branches':False,'formula_data_or_game_actions_changed':False,'physical_production_lines_net_added':net,'cache_component_benchmark':benchmark['cache_hit_component']['medians'],'whole_page_benchmark':benchmark['whole_page_warm_median_ms'],'whole_page_faster_claimed':False,'private_popup_sample':'Five existing055 tests use their existing original local sample; no image, contents or extracted text copied to this archive. New comparison uses only already-public isolated UI images.','existing_055_test_change':'Replace obsolete custom-SHA monkeypatch with same independent-return and one-pixel-different-input behavior; public test identity renamed accordingly. No provider/semantic expectation relaxed.','REA_scope':'Complete Python source plus actual installed OCR runtime comparison; no new REA tool invocation or mechanical bytecode inventory.','remaining':'Detector/classifier/full routing cost and complete actual game coverage, full existing-code compliance, video enemy table/numeric migration, other source/runtime paths and P3/P2/P1.'})
title='精简两处OCR精确缓存，修正云端识别优化优先级'
write(prefix+'summary.json',{'kind':'implementation_review_maintenance','title':title,'baseline_commit':BASE,'completed_sections':440,'functional_section_added':False,'implemented_scope_passed':True,'different_tests':89,'new_cache_tests':6,'new_cloud_priority_test':1,'failed':0,'errors':0,'skipped':0,'raw_actual_OCR_frame_cases':4,'paired_rounds':12,'old_new_original_full_output_equal':True,'cache_component_medians_ms':benchmark['cache_hit_component']['medians'],'whole_page_warm_median_ms':benchmark['whole_page_warm_median_ms'],'whole_page_speedup_claimed':False,'physical_production_lines_net_added':net,'test_window_updated':True,'private_six_paths_unchanged_during_startup':True,'source_review':pin(prefix+'source-review.json'),'tests':pin(prefix+'tests-current/results.json'),'benchmark':pin(prefix+'benchmark/results.json'),'full_validation_rerun':False,'full440_only_original_frozen_source':True,'whole_program_complete':False,'whole_existing_code_compliant':False,'whole_video_parity_complete':False,'P3_complete':False,'P2_complete':False,'P1_complete':False,'recognition_priority':'concurrent','game_operated':False,'chat_sent':False,'private_data_included':False,'publication_binding':'enclosing maintenance commit; ordinary push and actual remote/blob verification required'})
text('research/ocr-cache-review-20261031/README.md','''# 已有OCR缓存实现回顾

回顾PageOCR、ExactImageCache及调用方，原实现对完整像素先做SHA256，再在命中时独立比较同一像素。改用Python内置字典的元组/bytes键，形状、类型、上下文和批次顺序保留；字典直接以实际内容判等。移除单次调用的取键函数及不可达的图像缓存未命中替换分支，关闭页面缓存时不再构造缓存键。生产物理行净减少7行。未增加低概率防御，不删除当前帧来源、完整检测、配置失效、强制重读、独立返回、内存上限或私人状态/聊天保护。

依据[Python映射类型](https://docs.python.org/3.12/library/stdtypes.html#mapping-types-dict)与本机实际RapidOCR1.4.4源码；[上游仓库](https://github.com/RapidAI/RapidOCR)仅说明来源，v1.4.4标签网页未取得，不用最新分支冒充安装版本。本批没有新增第三方依赖/复制代码，模型及授权说明保持。

89项不同相关检查通过，含6项新缓存行为、1项当前云端优先级和原55/56/58/种子切换范围；原55五项读取既有本机样本，不把样本、原图或识别文字放入公开归档。修正原测试中针对已删除摘要接口的猴补丁，保留一像素变化、返回独立、形状/类型/上下文及预算等行为要求。

真实安装引擎在两张已公开的隔离界面原图、各两种尺寸上对照：四组各三轮，新旧文字、坐标、置信度与原引擎逐一相同；不是当前游戏准确率。9轮交替顺序、每轮300次的暖缓存命中：图像缓存中位数约0.141→0.076毫秒，页面批次缓存约0.251→0.130毫秒。整页暖测中位数371.75→386.49毫秒，没有变快；样本小且受运行噪声影响，不能宣传全流程或全游戏提速。完整检测/分类仍执行，需要继续定位这些阶段及页面分流成本。

同步修复云端索引生成器写死“识别最后”的旧文字，索引和交接现在反映OCR同步优化；当前方案/视频清单有效段落一并更新，历史原回执不改。实际测试小窗已更新，可见响应，启动六私人路径保持，零游戏操作/真实聊天/个人上传。

没有新REA工具调用：本批完整源码和实际OCR运行比较，沿用REA技能的证据分类；此前字节码与CJS分析另存。完整程序/视频、当前版本敌人预计数值表与P3/P2/P1未完成，功能440/未开441、721有序选择器。PRTS黑流树海主题页的难度/逐区修正说明已定向找到，后续仍须逐项对照固定原表与具体技能/阶段，不能直接搬旧模型或把文献当本局实际状态。
''')
write(prefix+'numeric-followup-sources.json',{'scope':'targeted source lead, not numerical implementation or current server proof','sources':[{'url':'https://prts.wiki/w/沉沦者的黑流树海','observed':'主题页区分保密等级追加条件与逐区域敌人难度叠乘；仍须对照固定原表和具体实体/阶段。','new_formula_implemented':False},{'url':'https://tomimi.dev/zh/black','observed':'公开固定作战资料入口；不是本项目已复制、已授权或已校准的源码。','new_code_or_data_copied':False}],'numeric_environment_migrated':False})
entry=f'''<!-- ocr-cache-review-20261031:start -->
## 实现回顾维护 · {title}

已有两处OCR缓存用Python内置精确像素键替代“摘要再全像素核对”，去掉单次取键函数及不可达分支；帧来源、全检测、配置/坐标、强制重读、独立返回和预算保持。净减7行；89项不同必要检查通过，四组实际引擎原图各三轮完整输出一致。

暖缓存局部中位数约0.141→0.076、0.251→0.130毫秒，但整页暖测371.75→386.49毫秒，没有提速，不冒充游戏效果或全流程提升。索引生成器与当前交接同步改为OCR同步优化，历史回执不改。小窗已更新可见响应，六私人路径保持，零游戏/聊天/上传。回执：`{prefix}summary.json`。功能440/未开441、721选择器；全程序/存量合规/视频与P3/P2/P1未完成。
<!-- ocr-cache-review-20261031:end -->

'''
for n in ('WORK_IN_PROGRESS.md','PROJECT_COMPLETED.md'):text(n,entry+(R/n).read_text('utf8'))
n='PROGRAM_REVIEW.md';text(n,(R/n).read_text('utf8')+'\n[已有OCR精确缓存回顾](research/ocr-cache-review-20261031/README.md)移除双重摘要/像素核对，四组实际引擎完整结果保持，89项相关检查通过；仅暖缓存局部开销下降，整页未提速。索引旧优先级已修复；剩余检测/分类/页面分流及完整游戏覆盖同步继续。\n')
n='PROJECT_PROGRESS.md';s=(R/n).read_text('utf8');s=s.replace('验证更多真实页面与连续帧的端到端耗时收益，继续降低OCR耗时','定位完整检测、分类及页面分流的主要耗时，验证更多真实页面与连续帧的端到端耗时收益，继续降低OCR耗时',1);text(n,s)
cp=read('DEVELOPMENT_CHECKPOINT.json');cp['policy']['recognition_optimization']='concurrent_with_feature_work_including_existing_code';cp['policy']['code_constraints_scope']='new_and_existing_code';cp['current_maintenance_save']={'kind':'implementation_review_maintenance','title':title,'receipt':prefix+'summary.json','binding':'enclosing_commit','functional_section_added':False,'status':'partial_program_review_ocr_cache','review_checklist':'PROGRAM_REVIEW.md','review_checklist_sha256':pin('PROGRAM_REVIEW.md')['sha256'],'application_review_complete':False};cp['current_batch']['receipt']=prefix+'summary.json';cp['next_action']='继续全程序与视频回顾：按来源完善当前敌人预计数值表及具体实体/阶段，核对其它资料/输入入口及来源刷新；同步定位完整检测、分类及页面分流的主要耗时，扩大实际页面/连续帧覆盖。两处精确缓存已简化且完整输出保持，但整页未提速，不把局部命中耗时当全流程收益。三条实现规则覆盖新增及存量，逐模块整改，新低概率防御先征求同意。'
text('DEVELOPMENT_CHECKPOINT.json',json.dumps(cp,ensure_ascii=False,indent=2)+'\n');idx=runpy.run_path(str(R/'scripts/update_cloud_index.py'));idx['update'](R);assert idx['validate_delivery'](R,cp)['current_section']==440
from scripts.verify_full_available import maintained_selectors
selectors=maintained_selectors();assert len(selectors)==721 and selectors[-1]=='tests.test_ocr_cache_review'
assert read('CLOUD_INDEX.json')['requirements']['sha256']==pin('PROJECT_REQUIREMENTS.md')['sha256']
assert '同步优化'in read('CLOUD_INDEX.json')['priority_order']and '识别优化最后'not in read('CLOUD_INDEX.json')['priority_order']
write(prefix+'final-audit.json',{'passed':True,'baseline_commit':BASE,'summary':pin(prefix+'summary.json'),'agents':pin('AGENTS.md'),'requirements':pin('PROJECT_REQUIREMENTS.md'),'cloud_index':pin('CLOUD_INDEX.json'),'different_tests':89,'raw_OCR_cases':4,'ordered_selectors':721,'whole_program_complete':False,'whole_existing_code_compliant':False,'whole_video_parity_complete':False,'at_UTC':datetime.now(timezone.utc).isoformat()})
(B/'record-source.py').write_bytes(Path(__file__).read_bytes())
files={p.relative_to(R).as_posix():{k:v for k,v in pin(p.relative_to(R)).items()if k!='path'}for p in sorted(B.rglob('*'))if p.is_file()and p.name!='archive-manifest.json'}
write(prefix+'archive-manifest.json',{'kind':'explicit_public_archive','files':files})
print(json.dumps({'passed':True,'different_tests':89,'raw_OCR_cases':4,'archive_files':len(files),'recognition_priority':'concurrent','whole_page_speedup_claimed':False,'whole_goal_complete':False}))
