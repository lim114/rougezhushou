from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
from importlib.metadata import version
import ast,ctypes,difflib,json,re,runpy,subprocess,sys,statistics,time
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts'),str(R/'.cache/305-window-tooldeps')]
BASE='e4dd8ba4ae1aff7dd386c70fd374898b31d6e37c';B=R/'verification/maintenance/ocr-runtime-review-20261031';prefix=B.relative_to(R).as_posix()+'/'
def read(n):return json.loads((R/n).read_bytes())
def pin(n):
 p=R/n;raw=p.read_bytes();return {'path':p.relative_to(R).as_posix(),'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}
def write(n,v):(R/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf8')
def text(n,v):
 p=R/n
 if not p.exists():p.parent.mkdir(parents=True,exist_ok=True);p.write_text(v,'utf8');return
 a=p.read_bytes().decode('utf8').splitlines(keepends=True);b=v.splitlines(keepends=True)
 for x,y,k in difflib.SequenceMatcher(None,[s.rstrip('\r\n')for s in a],[s.rstrip('\r\n')for s in b],autojunk=False).get_matching_blocks():b[y:y+k]=a[x:x+k]
 p.write_bytes(''.join(b).encode('utf8'))
assert subprocess.check_output(['git','rev-parse','HEAD']).decode().strip()==BASE
assert subprocess.check_output(['git','branch','--show-current']).decode().strip()=='codex/p2-development'
changed=['rouge/recognition.py','rouge/player_shop_hover.py']
for name in changed:
 before=subprocess.check_output(['git','show',BASE+':'+name]);after=(R/name).read_bytes()
 assert before.count(b'intra_op_num_threads=2')==1 and after==before.replace(b'intra_op_num_threads=2',b'intra_op_num_threads=4')
assert subprocess.check_output(['git','diff','--name-only',BASE,'--','rouge']).decode().splitlines()==sorted(changed)
assert not subprocess.check_output(['git','diff','--name-only',BASE,'--','scripts/verify_full_available.py']).strip()
ids=[]
for folder,count in(('necessary',102),('integration',29)):
 result=read(prefix+folder+'/results.json');assert result['passed']and result['tests_run']==count and not result['failed']and not result['errors']and not result['skipped']and not result['forbidden_external_calls']
 assert read(prefix+folder+'/process.json')['actual_observed_exit']==0
 cases=re.findall(r'^test_\w+ \(([^)]+)\)',(B/folder/'stderr.txt').read_text('utf8'),re.M);assert len(cases)==len(set(cases))==count;ids+=cases
assert len(ids)==len(set(ids))==131
parity=read(prefix+'raw-parity/results.json');assert parity['passed']and len(parity['cases'])==20 and parity['cls_disabled_cases']==3
assert parity['source_stable']==pin('rouge/recognition.py')['sha256']and read(prefix+'raw-parity-process.json')['actual_exit']==0
compatibility_cost={str(threads):{'wall_ms':sum(r['measurements'][str(threads)]['elapsed_ms']for r in parity['cases']),
 'process_CPU_ms':sum(r['measurements'][str(threads)]['process_CPU_ms']for r in parity['cases'])}for threads in(2,4)}
write(prefix+'raw-parity/cost-scope.json',{'totals_in_same_comparison_process':compatibility_cost,'all20_four_thread_calls_faster':all(r['measurements']['4']['elapsed_ms']<r['measurements']['2']['elapsed_ms']for r in parity['cases']),'CPU_cost_increased_in_this_process':True,'limits':'Both2-thread and4-thread engine groups remain alive. Process CPU time includes all their pools, so this is not a clean per-engine production energy/FPS measurement. Whole test-suite durations are not paired performance evidence.'})
pipeline=read(prefix+'public-pipeline/results.json');assert pipeline['passed']and len(pipeline['rows'])==6 and all(r['all_interpreted_facts_equal']for r in pipeline['rows'])
write(prefix+'public-pipeline/process-observation.json',{'unified_exec_session_id':22261,'actual_observed_exit':0,'Popen_PID_not_invented':True})
trial_root=R/'.cache/ocr-runtime-trials';trial_summary={};base_rows=None
for tag in('baseline','ort4','cv1','ort4cv1'):
 v=read('.cache/ocr-runtime-trials/'+tag+'/results.json');assert v['passed']and len(v['rows'])==3
 if base_rows is None:base_rows=v['rows']
 assert [r['raw_result_sha256']for r in v['rows']]==[r['raw_result_sha256']for r in base_rows]
 trial_summary[tag]={'intra_op':v['intra_op'],'inter_op':v['inter_op'],'OpenCV_threads':v['OpenCV_threads'],'median_ms':{str(r['public_second']):statistics.median(r['milliseconds'])for r in v['rows']}}
 out=B/'isolated-trials'/tag;out.mkdir(parents=True,exist_ok=False)
 (out/'results.json').write_bytes((trial_root/tag/'results.json').read_bytes())
 for kind in('stdout','stderr'):(out/(kind+'.txt')).write_bytes((trial_root/(tag+'-'+kind+'.txt')).read_bytes())
(B/'isolated-trials/processes.json').write_bytes((trial_root/'processes.json').read_bytes())
reductions={k:100*(1-trial_summary['ort4']['median_ms'][k]/trial_summary['baseline']['median_ms'][k])for k in trial_summary['baseline']['median_ms']}
assert all(20<v<35 for v in reductions.values())
write(prefix+'isolated-trials/comparison.json',{'passed':True,'trials':trial_summary,'selected':'ort4','OpenCV_global_setting_changed':False,'OCR_median_reduction_percent':reductions,'not_a_general_all_PC_speedup_or_game_FPS_claim':True})
local=read('.cache/ocr-runtime-client-paired/results.json');assert local['availability']=='captured'and len(local['rows'])==3 and local['private_six_unchanged']and local['foreground_unchanged']and all(r['all_interpreted_facts_equal']for r in local['rows'])
assert local['local_only']and not local['run_state_applied']and not local['raw_pixels_or_interpreted_values_saved']
live=read(prefix+'live-window/window.json');assert live['passed']and live['private_six_paths_unchanged']
for name in changed:assert live['source_sha256_after'][name]==pin(name)['sha256']
import win32gui,win32process
for w in live['owned_windows']:assert win32gui.IsWindowVisible(w['hwnd'])and win32process.GetWindowThreadProcessId(w['hwnd'])[1]==w['pid']and not ctypes.windll.user32.IsHungAppWindow(w['hwnd'])
a=read('.cache/ocr-runtime-review-live-status.json');time.sleep(2.2);b=read('.cache/ocr-runtime-review-live-status.json');assert b['toolbar_visible']and b['elapsed_since_launch']>a['elapsed_since_launch']
write(prefix+'live-window/desktop-review.json',{'Windows_MCP_toolbar_snapshot_actually_viewed':True,'region':[1716,1164,2130,1218],'visible_responding_and_Qt_timer_advanced':True,'private_six_paths_unchanged':True,'private_contents_hashes_or_game_images_published':False,'game_operated':False,'chat_sent':False})
import rapidocr_onnxruntime
pkg=Path(rapidocr_onnxruntime.__file__).parent
files=['main.py','utils/infer_engine.py','ch_ppocr_rec/text_recognize.py','ch_ppocr_det/text_detect.py','ch_ppocr_cls/text_cls.py','config.yaml']
package_pins={n:sha256((pkg/n).read_bytes()).hexdigest()for n in files}
models={p.name:sha256(p.read_bytes()).hexdigest()for p in (pkg/'models').glob('*.onnx')}
write(prefix+'source-review.json',{'baseline_commit':BASE,'changed_source':[pin(n)for n in changed],'only_intra_op_constant2_to4_changed':True,'new_production_functions_classes_or_guards':0,'numeric_models_source_data_capture_state_and_UI_changed':False,'package_versions':{'rapidocr_onnxruntime':version('rapidocr-onnxruntime'),'onnxruntime':version('onnxruntime')},'installed_source_sha256':package_pins,'installed_model_sha256':models,'primary_sources':['https://github.com/RapidAI/RapidOCR/blob/v1.4.4/python/rapidocr_onnxruntime/ch_ppocr_rec/text_recognize.py','https://github.com/RapidAI/RapidOCR/blob/v1.4.4/LICENSE','https://onnxruntime.ai/docs/performance/tune-performance/threading.html'],'reuse':'Existing installed RapidOCR1.4.4 Apache2.0 interface and ONNX Runtime; no new engine, model, dependency install, copied upstream implementation or local package edits.','limits':'Per-model parallelism is4; not a claim of at most4 process threads. More CPU may be used; other hardware and playing-game latency/FPS remain unverified.'})
for n in('.cache/trial_ocr_runtime.py','.cache/run_ocr_runtime_trials.py','.cache/verify_ocr_threads_parity.py','.cache/run_ocr_threads_parity.py','.cache/benchmark_ocr_runtime_pipeline.py','.cache/run_ocr_runtime_checks.py','.cache/run_ocr_runtime_integration.py'):(B/Path(n).name).write_bytes((R/n).read_bytes())
candidate=R/'verification/maintenance/full-frame-ocr-review-20261031'
for n in('.cache/benchmark_full_frame_ocr_pipeline.py','.cache/run_full_frame_ocr_checks.py','.cache/run_full_frame_ocr_integration.py'):(candidate/Path(n).name).write_bytes((R/n).read_bytes())
write('verification/maintenance/full-frame-ocr-review-20261031/disposition.json',{'adopted':False,'candidate_checks':66,'candidate_integration_checks':29,'public_pipeline_pairs':6,'candidate_real_client_pairs_local_only':3,'recognized_batch_hits_on_these_changed_frames':0,'reason':'Complete outputs equal but no stable improvement. Both production source files restored before thread-only tuning; candidate is archived research, not shipping code or current passing test coverage.','initial_test_runner_failure':'A nonexistent test_dynamic_ocr module was mistakenly selected; actual DynamicOCR contracts are in existing page_ocr_056 and seed_bridge suites. Original failed receipt kept.','no_capture_images_or_interpreted_values_published':True})
(candidate/'initial-batch-experiment.json').write_bytes((R/'.cache/universal-frame-ocr-experiment/results.json').read_bytes())
(candidate/'initial-batch-experiment-source.py').write_bytes((R/'.cache/experiment_universal_frame_ocr.py').read_bytes())
title='复用现有识别库调优并行度，撤回无收益的整帧缓存接入'
write(prefix+'summary.json',{'passed':True,'kind':'implementation_review_maintenance','title':title,'baseline_commit':BASE,'functional_section':440,'functional_section_added':False,'different_current_necessary_tests':131,'original_sample_full_output_pairs':20,'orientation_classifier_disabled_pairs':3,'public_pipeline_pairs':6,'isolated_OCR_median_reduction_percent':reductions,'real_client_pairs_verified_local_only':3,'real_client_receipts_images_or_values_published':False,'current_model_weights_recognition_thresholds_and_regions_changed':False,'global_OpenCV_threads_changed':False,'per_model_intra_op_threads_before':2,'per_model_intra_op_threads_after':4,'game_FPS_CPU_cost_other_hardware_complete_accuracy_or_video_parity_verified':False,'full_regression_rerun':False,'next_full':455,'application_review_complete':False,'all_existing_code_compliant':False,'test_window_updated_visible_responding':True,'private_six_paths_unchanged':True,'game_operated':False,'chat_sent':False,'goal_active':True,'at_UTC':datetime.now(timezone.utc).isoformat()})
text('research/full-frame-ocr-review-20261031/README.md','''# 未采用的整帧缓存接入候选

完整源码回顾确认，现有视觉控制模板只有干员详情、模组、队伍和强化弹窗，尚无探索页模板；探索回退不是某个探索模板误判。尝试把已接入PageOCR用于DynamicOCR必须整幅读取的入口，仍保留小变动区域、当前完整检测和原识别结果，不猜页面、不跳过文字。

候选66项必要检查及29项样本集成检查通过；六组公开录像输入完整解释结果相同。三组本机新鲜客户区只读对照也相同，记录只留本机，不发布画面、文字、实际培养或本局数据。但这些连续输入的识别批次均未命中缓存，没有稳定耗时收益，故撤回两处生产改动，候选测试移入研究目录，不加入当前选择器或冒充当前通过。原独立缓存能力保留。

候选源码、测试及实际回执保留。初次选错不存在的test_dynamic_ocr模块的加载失败没有删除；真实DynamicOCR契约由已有page_ocr_056及seed_bridge范围验证。此轮否定了默认扩大缓存接入的收益假设，没有交付探索视觉路由或全局提速。后续采用的仅是[库运行参数调整](../ocr-runtime-review-20261031/README.md)，与本候选分开。
''')
text('research/ocr-runtime-review-20261031/README.md',f'''# 识别运行参数回顾与两处实际调整

基线{BASE}。沿REA技能的完整源码/实际运行路线继续审查，不为已具备完整Python源码的模块重复作字节码清点；本批未新增REA工具调用，不称完整程序回顾结束。

先验证现有PageOCR复用到未知整帧的方案，候选输出相同却没有缓存命中或稳定收益，已撤回，见[候选回执](../../verification/maintenance/full-frame-ocr-review-20261031/disposition.json)。不把兼容测试通过当作优化成立，也未新增探索页模板。OpenCV单线程试验无优势，保持原全局设置。

直接复用现有[RapidOCR1.4.4识别接口](https://github.com/RapidAI/RapidOCR/blob/v1.4.4/python/rapidocr_onnxruntime/ch_ppocr_rec/text_recognize.py)与[Apache2.0许可](https://github.com/RapidAI/RapidOCR/blob/v1.4.4/LICENSE)，参照[ONNX Runtime线程文档](https://onnxruntime.ai/docs/performance/tune-performance/threading.html)测量2/4模型内线程和原/单线程OpenCV四组配置。库按宽高比分批，不据当前main推断旧版本行为；安装源码及模型摘要另存。没有安装/替换库、模型或复制新的数值/识别核。

独立子进程中三组公开录像画面，各预热后完整识别三次，4线程的中位耗时相对2线程降低{min(reductions.values()):.1f}%–{max(reductions.values()):.1f}%，全部原框/文本/置信度摘要相同。最终只将ScreenReader和ShopNameReader两个原构造器的intra_op_num_threads从2改4，其余字节保持。不是新引擎、近似缓存、减少检测、提高置信门槛或增加防御/单次辅助函数。

20张既有本机开发样本的完整框、文字、置信度逐项相等，另3例关闭方向分类后也相等；只保存数量、用例名和耗时，不保存图片、文字或个人样本像素摘要。这是兼容对照，不是独立准确率校准。六组公开录像整条解释结果也相同，5组总耗时下降、1组略慢；慢项仍包括本局信息和地图细化，不能把OCR局部收益当作所有页面的端到端收益。三组新鲜实机帧只读对照在本机完成且解释结果相同，原件不进入公开包，不改焦点、不写本局。

131项不同必要/样本集成检查通过；旧候选95项不并入该数字。Windows实际测试小窗已更新，可见、响应且定时器推进，六私人路径保持。未操作游戏、发聊天、上传个人数据或重置。20例配对均更快，但同一对照进程的CPU时间合计也增加；该进程同时保有两组模型，不能把其CPU数值直接当生产能耗或游戏影响。每个模型可用4线程，不代表全进程只有4线程；其它硬件、游戏同跑帧率/延迟仍未验证，不保证所有电脑更快。整套测试总时长不能当相同输入性能对照。

功能仍440、未开441，723选择器次序与内容不变，下次完整验收455。全程序、存量三条约束、P3/P2/P1和完整视频效果仍未完成；本轮无界面外观或机制公式改动。
''')
entry=f'''<!-- ocr-runtime-review-20261031:start -->
## 实现回顾维护 · {title}

两处原识别构造器的模型内线程2→4，模型/阈值/区域和其余生产字节保持；三组公开画面各三次暖读的OCR中位数降低{min(reductions.values()):.1f}%–{max(reductions.values()):.1f}%。20样本原框/文字/置信度及3例无方向分类相等，六组公开视频完整解释相同、总耗时5降1升；不称全场景提速。实机三组只读对照只留本机，六私人路径保持。

当前131项不同检查通过，小窗更新可见响应。无命中/无稳定收益的通用整帧批次候选已撤回，其95项仅作研究原件，不加入当前通过数。回执：`{prefix}summary.json`。功能440、未开441，723选择器不变；全程序、视频、存量合规与P3/P2/P1仍未完成。
<!-- ocr-runtime-review-20261031:end -->

'''
for n in('WORK_IN_PROGRESS.md','PROJECT_COMPLETED.md'):text(n,entry+(R/n).read_text('utf8'))
n='PROGRAM_REVIEW.md';s=(R/n).read_text('utf8').replace('本轮未采集游戏。','完整连续游戏验证未完成；最近仅作本机只读新鲜帧对照，原件不公开。',1);text(n,s+'\n[识别运行参数回顾](research/ocr-runtime-review-20261031/README.md)已核对视觉路由实际覆盖，撤回无收益的默认整帧缓存候选，仅调优两个现有库构造器。131项当前检查、20样本/3例无方向分类和6组公开解释对照通过；探索视觉路由、其它布局/准确率、CPU代价与完整视频仍待验。现有三条代码约束继续逐模块整改，不把本轮调参当整个程序完成。\n')
n='PROJECT_PROGRESS.md';s=(R/n).read_text('utf8').replace('继续降低OCR耗时；','核验其余页面、弱硬件与游戏同跑时的端到端耗时和CPU代价；',1);text(n,s)
n='PROJECT_REQUIREMENTS.md';s=(R/n).read_text('utf8');marker='## OCR同步优化（2026-10-31最新更正）';assert marker in s;s=s.replace(marker,'## 识别优化采用标准\n\n候选方案须同时对照完整读取结果、耗时和资源代价，兼容检查通过不等于有收益；无稳定收益的默认接入应撤回并保留证据。分清OCR局部、整条读取、同帧复用与真实游戏；按固定版本复用现有库，线程/硬件优化不扩大成所有电脑提速或完整准确率证明。\n\n'+marker,1);text(n,s)
n='VIDEO_PARITY.md';s=(R/n).read_text('utf8').replace('之后按上表剩余缺口推进；识别覆盖和耗时仍最后统一处理。','之后按上表剩余缺口推进；识别覆盖、准确率、适配和耗时同步优化。',1);text(n,s+'\n[OCR运行参数回顾](research/ocr-runtime-review-20261031/README.md)只改善读取实现，并保留所有当前文字与解释结果。没有缓存命中的整帧候选已撤回，现用库线程设置有局部实测收益；这不增加视觉模板、不证明实时完整采样或视频外观已一致。\n')
n='IMPLEMENTATION_STRATEGY.md';text(n,(R/n).read_text('utf8')+'\n[OCR运行参数回顾](research/ocr-runtime-review-20261031/README.md)优先复用已安装的库并测量现有接口，避免为没有稳定收益的复用层增加默认复杂度。两处构造参数调优保持模型和阈值；未知页面的视觉模板、全文检测及资源成本仍分别验收，不把所有回退当分类器误判。\n')
cp=read('DEVELOPMENT_CHECKPOINT.json');cp['current_maintenance_save']={'kind':'implementation_review_maintenance','title':title,'receipt':prefix+'summary.json','binding':'enclosing_commit','functional_section_added':False,'status':'partial_program_review_measured_OCR_runtime_tuning','review_checklist':'PROGRAM_REVIEW.md','review_checklist_sha256':pin('PROGRAM_REVIEW.md')['sha256'],'application_review_complete':False};cp['current_batch']['receipt']=prefix+'summary.json';cp['next_action']='继续逐链路回顾完整程序并对照视频补齐资料/地图/资源与外观；存量三条约束继续同批修正。OCR同步补探索视觉路由、其余页面准确率/分辨率与本局信息/地图细化耗时，核验4线程的CPU代价、游戏同跑与弱硬件，不把局部提速当全部完成。保留剩余1011引用、完整数值/当前版本条件与P3/P2/P1缺口；441未启动。'
text('DEVELOPMENT_CHECKPOINT.json',json.dumps(cp,ensure_ascii=False,indent=2)+'\n');idx=runpy.run_path(str(R/'scripts/update_cloud_index.py'));idx['update'](R);assert idx['validate_delivery'](R,cp)['current_section']==440
from scripts.verify_full_available import maintained_selectors
assert len(maintained_selectors())==723
assert read('CLOUD_INDEX.json')['requirements']['sha256']==pin('PROJECT_REQUIREMENTS.md')['sha256']
write(prefix+'final-audit.json',{'passed':True,'baseline_commit':BASE,'summary':pin(prefix+'summary.json'),'requirements':pin('PROJECT_REQUIREMENTS.md'),'cloud_index':pin('CLOUD_INDEX.json'),'current_distinct_tests':131,'rejected_candidate_tests_not_added':True,'ordered_selectors_unchanged':723,'whole_program_complete':False,'whole_video_parity_complete':False,'goal_active':True,'at_UTC':datetime.now(timezone.utc).isoformat()})
(B/'record-source.py').write_bytes(Path(__file__).read_bytes())
for root in(B,candidate):
 files={p.relative_to(R).as_posix():{k:v for k,v in pin(p.relative_to(R)).items()if k!='path'}for p in sorted(root.rglob('*'))if p.is_file()and p.name!='archive-manifest.json'}
 write(root.relative_to(R).as_posix()+'/archive-manifest.json',{'kind':'explicit_public_archive','files':files})
print(json.dumps({'passed':True,'current_distinct_tests':131,'candidate_not_adopted':True,'OCR_percent_reductions':reductions,'whole_goal_complete':False}))
