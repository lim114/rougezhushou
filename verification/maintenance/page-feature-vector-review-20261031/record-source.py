from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import ast,json,difflib,re,statistics,subprocess,runpy,sys
R=Path.cwd();B=R/'verification/maintenance/page-feature-vector-review-20261031';P=B.relative_to(R).as_posix()+'/';D=R/'research/page-feature-vector-review-20261031';BASE='1b276ea48991ceafa03ea5cbacefc8d7a294d4f0'
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
assert subprocess.check_output(['git','rev-parse','HEAD']).decode().strip()==BASE
assert subprocess.check_output(['git','branch','--show-current']).decode().strip()=='codex/p2-development'
assert subprocess.check_output(['git','diff','--name-only','--','rouge']).decode().splitlines()==['rouge/page_features.py']
name='rouge/page_features.py';old=ast.parse((D/'before-page_features.py').read_text('utf8'));new=ast.parse((R/name).read_text('utf8'))
for tree in(old,new):tree.body=[n for n in tree.body if not(isinstance(n,ast.FunctionDef)and n.name=='_scene_features')]
assert ast.dump(old)==ast.dump(new)
tests=read(P+'necessary/results.json');assert tests['passed']and tests['tests_run']==97 and not tests['skipped']and not tests['failed']and not tests['errors']and not tests['forbidden_external_calls']
assert read(P+'necessary/process.json')['actual_observed_exit']==0
ids=re.findall(r'^test_\w+ \(([^)]+)\)',(B/'necessary/stderr.txt').read_text('utf8'),re.M);assert len(ids)==len(set(ids))==97
paired=read(P+'paired/results.json');assert paired['passed']and len(paired['route_cases'])==60 and len(paired['synthetic_feature_cases'])==3 and paired['source_sha256']==pin(name)['sha256']
raw=read(P+'final-feature-parity.json');assert raw['passed']and len(raw['cases'])==60 and raw['source_sha256']==pin(name)['sha256']
pipeline=read(P+'pipeline/results.json');assert pipeline['passed']and len(pipeline['rows'])==20 and pipeline['source_sha256']==pin(name)['sha256']
experiment=read('.cache/page-feature-vector-experiment/results.json');assert experiment['passed']and len(experiment['cases'])==60
write(P+'feature-experiment.json',experiment)
metrics={'feature_before_median_ms':experiment['before_median_ms'],'feature_after_median_ms':experiment['after_median_ms'],
    'feature_pairs_faster':sum(statistics.median(r['after_ms'])<statistics.median(r['before_ms'])for r in experiment['cases']),
    'route_before_median_ms':statistics.median(r['milliseconds']['before']for r in paired['route_cases']),
    'route_after_median_ms':statistics.median(r['milliseconds']['after']for r in paired['route_cases']),
    'route_pairs_faster':sum(r['milliseconds']['after']<r['milliseconds']['before']for r in paired['route_cases']),
    'complete_read_pairs_faster':sum(r['milliseconds']['after']<r['milliseconds']['before']for r in pipeline['rows']),
    'not_a_whole_pipeline_or_all_PC_speedup':True}
write(P+'comparison.json',metrics)
vlm=B/'vlm';vlm.mkdir(exist_ok=False)
copies={'.cache/page-feature-vector-model-candidate.json':'model-candidate.json','.cache/page-feature-vlm-packages.json':'package-metadata.json',
    '.cache/vlm-openvino-setup/install-report.json':'install-report.json','.cache/vlm-openvino-setup/process.json':'install-process.json',
    '.cache/vlm-openvino-device-check/devices.json':'devices.json','.cache/vlm-openvino-device-check/process.json':'device-process.json',
    '.cache/vlm-qwen3-4b-int4-candidate/download-complete.json':'model-download-complete.json',
    '.cache/vlm-public-reference-results/GPU/results.json':'initial-results.json','.cache/vlm-public-reference-results/GPU/field-comparison.json':'initial-field-comparison.json',
    '.cache/vlm-public-reference-results/GPU/prompt.txt':'initial-prompt.txt','.cache/vlm-public-reference-process/process.json':'initial-process.json',
    '.cache/vlm-public-semantic-results/results.json':'semantic-results.json','.cache/vlm-public-semantic-results/field-comparison.json':'semantic-field-comparison.json',
    '.cache/vlm-public-semantic-results/prompt.txt':'semantic-prompt.txt','.cache/vlm-public-semantic-process/process.json':'semantic-process.json',
    '.cache/vlm-public-reference-frames/60-ground-truth.json':'60-ground-truth.json','.cache/vlm-public-reference-frames/44-ground-truth.json':'44-ground-truth.json',
    '.cache/probe_vlm_public_reference.py':'initial-probe-source.py','.cache/probe_vlm_semantic_fields.py':'semantic-probe-source.py',
    '.cache/download_vlm_openvino_candidate.py':'download-proxy-source.py','.cache/download_vlm_openvino_direct.py':'download-direct-source.py'}
for source,target in copies.items():(vlm/target).write_bytes((R/source).read_bytes())
assert read(P+'vlm/install-process.json')['actual_observed_exit']==0 and read(P+'vlm/device-process.json')['actual_observed_exit']==0
assert read(P+'vlm/initial-process.json')['actual_observed_exit']==0 and read(P+'vlm/semantic-process.json')['actual_observed_exit']==0
initial=read(P+'vlm/initial-results.json');semantic=read(P+'vlm/semantic-results.json');assert initial['runtime_ran']and semantic['runtime_ran']
assert [json.loads(r['raw_text'])['confidentiality_level']for r in initial['rows']]==[1,1]
assert [json.loads(r['raw_text'])['confidentiality_level']for r in semantic['rows']]==[1,10]
baseline=read('.cache/vlm-public-reference-frames/60-current-reader.json')
baseline_rows=[]
for v in baseline:
    run=v['run'];baseline_rows.append({'page':v['page'],'total_ms':v['performance']['total_ms'],'difficulty':run['config']['difficulty']['value'],'zone':run['config']['zone']['name'],'operator_count':run['crew_count'],'relic_count':run['relics']['count'],'visible_node_types':sorted({n['type']for n in v['nodes']})})
assert len(baseline_rows)==2 and all(r['difficulty']==6 for r in baseline_rows)
write(P+'vlm/current-reader-same-public-frame.json',{'scope':'Same60s public image, current ScreenReader cache disabled, two complete reads; not all VLM fields are currently extracted and equal JSON schema is not assumed. First read includes initialization.','rows':baseline_rows,'not_whole_accuracy_proof':True})
write(P+'vlm/decision.json',{'adopted_in_production':False,'runtime_works_on_this_Intel_Arc_iGPU':True,'local_public_image_inference_not_remote_chat':True,
    'reason':'Exact field attribution fails under both prompts, non-game text is invented as nodes, and observed latency is too high for the intended frequent sampling. This rejects this tested configuration, not all VLMs.',
    'follow_up':'Evaluate a compact page/control detector and evidence-bound field readers; a VLM can remain a candidate for infrequent complex pages after independent coverage/latency/resource checks. Do not return self-reported confidence as game probability.',
    'primary_download_attempt':'Proxy route stopped on first LFS request with TLS EOF; actual exec session68744 exit1. Second direct request reused six fully downloaded metadata files and completed pinned24-file download; session69825 exit0. No disabled TLS or implicit credential use.',
    'runtime_dependencies_isolated':True,'project_environment_or_requirements_changed':False,'weights_committed':False,
    'license_scope':'Official converted card declaresApache2.0; its original upstream LICENSE URL returned404 during review. No model redistribution or production packaging accepted in this maintenance.',
    'telemetry':'Opt-out executed successfully inside isolated LOCALAPPDATA; actual consent file0 reviewed. Inference uses local IR and HF_HUB_OFFLINE/TRANSFORMERS_OFFLINE flags. No private inference input used.',
    'sampled_process_RSS_GiB':5.51,'RSS_scope':'One actual process sample during initial inference; not peak RSS, GPU allocation, power or gameFPS.',
    'whole_program_or_vision_accuracy_complete':False})
live=read(P+'live-window/window.json');assert live['passed']and live['private_six_paths_unchanged']and live['source_sha256_after'][name]==pin(name)['sha256']
write(P+'live-window/desktop-review.json',{'actual_Windows_MCP_crop_viewed':True,'physical_rect':[1716,1164,2130,1218],'DPI_aware_rect_queried_before_capture':True,'visible_responding_and_Qt_timer_advanced':True,'no_UI_appearance_change_claimed':True})
before=read('.cache/page-feature-vector-before.json')['private'];window_before=read('.cache/page-feature-vector-window-before.json')
private_changes=[n for n,v in before.items()if(sha256((R/n).read_bytes()).hexdigest()if(R/n).exists()else None)!=v]
write(P+'private-state-scope.json',{'whole_batch_unchanged':not private_changes,'paths_changed_during_batch':private_changes,'origin_not_assigned':True,'controlled_window_startup_six_paths_unchanged':live['private_six_paths_unchanged'],'no_private_contents_or_hashes_in_public_receipt':True,'no_private_copy_restore_or_rollback':True,'comparison_scripts_do_not_apply_run_state':True})
assert set(private_changes)<={'.local/run-state.json'}
write(P+'source-review.json',{'baseline_commit':BASE,'changed_source':[pin(name)],'only_scene_feature_function_changed_in_production_AST':True,'new_production_functions_classes_guards':0,'physical_line_delta':1,'not_a_code_line_reduction_claim':True,'detection_thresholds_anchor_data_and_runtime_models_unchanged':True,'existing_OpenCV_reused':'4.14.0.94 KeyPoint_convert andNumPy vector selection; no new production dependency','REA_scope':'REA skill used to route review. Complete Python source and controlled runtime comparison used here; no new REA tool call or whole-program reverse engineering claim.'})
for source,target in(('.cache/experiment_page_features_vector.py','feature-experiment-source.py'),('.cache/verify_page_feature_vector.py','paired/verify-source.py'),('.cache/verify_page_feature_pipeline.py','pipeline/verify-source.py'),('.cache/verify_final_scene_features.py','final-feature-source.py')):(B/target).write_bytes((R/source).read_bytes())
summary={'kind':'implementation_review_maintenance','passed':True,'section':440,'functional_section_added':False,'baseline_commit':BASE,'changed_source':[pin(name)],'necessary_distinct_tests':97,'test_failures':0,'test_errors':0,'test_skips':0,
    'final_feature_pairs':60,'full_route_pairs':60,'synthetic_empty_edge_cases':3,'complete_read_pairs':20,'all_complete_read_facts_equal':True,'performance':metrics,
    'local_VLM_runtime_tested':True,'local_VLM_adopted':False,'VLM_accuracy_acceptance_passed':False,'VLM_live_realtime_accepted':False,
    'actual_test_window_updated_visible_responding':True,'private_state_scope':P+'private-state-scope.json','no_game_operation_or_real_chat_send_or_private_upload':True,
    'whole_program_review_complete':False,'whole_video_parity_complete':False,'P3_P2_P1_complete':False,'next_full_section':455,'goal_active':True,'at_UTC':datetime.now(timezone.utc).isoformat()}
write(P+'summary.json',summary)
title='页面特征批量提取与本地视觉模型实测，保留准确性未通过的替换候选'
save(D.relative_to(R)/'README.md',f'''# 页面分流回顾与本地视觉模型试验

基线{BASE}。本轮按REA技能的完整源码/运行证据路线继续，不为完整Python源码机械生成字节码或称全程序已逆向完成。

生产只改`rouge/page_features.py`的特征点收集：复用[OpenCV KeyPoint批量转换](https://docs.opencv.org/4.13.0/d2/d29/classcv_1_1KeyPoint.html)与NumPy筛选，保留原双精度平移/边界比较后再转float32。分块、ORB、所有阈值、锚点、RANSAC、像素缓存和页面语义不变，无新依赖/辅助函数/防御分支；物理行净增1，不称代码净减。已装OpenCV4.14.0.94，API行为由实际样本对照验证，非假定在线文档版本等于安装版本。

20张本机既有开发样本及缩放/平移共60组：最终特征数组逐项相等，完整页面计划（除耗时）相等；另3例空白/小图/纹理形状保持。初步配对中位数：特征80.36→70.57ms（57/60更快），完整分流154.55→146.34ms（51/60更快）。20组完整读取解释保持，但总耗时仅12组下降，不称所有页面/机器或游戏FPS提升。97项不同当前必要检查通过；未将此前131检查或候选原件并入。样本不公开图片、文字、身份或像素摘要，对照相等不是独立准确率证明。

## 本地视觉模型：运行可行，当前配置不宜替换自动采样

参照[Qwen3-VL官方资料](https://github.com/QwenLM/Qwen3-VL/blob/main/README.md)、[OpenVINO支持表](https://docs.openvino.ai/2026/documentation/compatibility-and-support/supported-models.html)和[官方转换模型卡](https://huggingface.co/OpenVINO/Qwen3-VL-4B-Instruct-int4-ov)。固定模型修订`3ffb805d532a250e5010c5aa5ce6579e60b31d71`，24文件约2.89GiB，声明尺寸及LFS摘要全部核对。模型卡标注Apache2.0，但指向原模型LICENSE的链接本次404，未接受权重分发/打包。未复制模型卡全文或提交权重。

项目虚拟环境没有改动。独立`.cache`环境固定OpenVINO2026.4.1、GenAI/Tokenizers2026.4.1.0、Pillow12.3.0；本机实测可见CoreUltra5 125H、IntelArc iGPU及NPU，但只有GPU完成本次模型推理，不冒称NPU适配。按[官方遥测说明](https://docs.openvino.ai/2024/about-openvino/additional-resources/telemetry.html)在隔离LOCALAPPDATA关闭遥测；离线推理只用用户提供的公开参考录像44/60秒，不使用私人游戏画面或外部聊天。一次RSS采样5.51GiB，不当作峰值、显存、能耗或FPS。

60秒图第一提示重复两次：8个手工核对字段中7项相符，7类节点名称集合相符，分队不猜；保密等级两次错误为1，实际6。加载45.06秒，提取27.94/18.83秒。增加不含答案的字段说明后，该图仍把难度读1，区域名混入拉丁字、层数漏读；44秒介绍拼图难度错为10（实际15），并把说明文字当节点。两个输入不是两次独立真实对局，不称总体准确率。仅分类60秒图正确却耗时10.80秒；同图当前读取器冷/暖完整读8.20/3.70秒、难度正确6，但功能字段不完全同构，不据此宣称全面优于所有视觉模型。

本次不接入生产。后续研究小型页面/控件定位模型，以及受独立字段依据约束的读取；视觉大模型仍可作低频复杂页面候选，须另验覆盖/准确性/延迟/资源。不能因JSON合法或同图重复答案稳定就当数据可信，也不能让模型补出不可见状态。初始手工参考也曾误读“脉”为“腔”，已在推理前按放大原像素和固定目录纠正，原说明保留。

## 窗口与状态边界

97项检查用隔离状态，未操作游戏、发聊天或上传私人数据。实际测试小窗正常关闭旧实例并更新，Windows-mcp裁剪确实查看，Qt计时器推进；启动六路径保持。整个批次本局文件出现变化，来源未归因，不声称全程六路径未变、不复制/回滚；其余五路径保持。功能440/未开441、723有序选择器不变，下次完整455；完整视频效果、存量整改、全程序与P3/P2/P1仍未完成。

[本轮回执](../../{P}summary.json)。
''')
entry=f'''<!-- page-feature-vector-review-20261031:start -->
## 实现回顾维护 · {title}

只将原页面特征收集改为OpenCV/NumPy批量处理，阈值与资料保持；60组特征/完整计划、3例空形状和20组完整解释相等，97项检查通过。特征中位80.36→70.57ms、分流154.55→146.34ms，完整读取有快有慢，不称全流程提速或代码净减。

隔离环境在本机GPU真实运行固定Qwen3-VL4B；公开参考图字段归属和非游戏节点判断失败，提取18–28秒、单分类10.80秒，保留失败原文且未接入生产。小窗更新可见响应、启动六路径保持；整批本局文件变化未归因且不回滚。回执：`{P}summary.json`。440/未开441，723选择器不变；全程序、视频、数值与P3/P2/P1仍未完成。
<!-- page-feature-vector-review-20261031:end -->

'''
for n in('WORK_IN_PROGRESS.md','PROJECT_COMPLETED.md'):save(n,entry+(R/n).read_text('utf8'))
n='PROGRAM_REVIEW.md';s=(R/n).read_text('utf8');s=s.replace('识别优化仍最后。','OCR识别优化同步推进。',1);s=s.replace('整页识别尚未提速。','已测线程/特征局部收益，完整读取仍有快有慢，不能称全面提速。',1);save(n,s+'\n[页面分流与视觉模型回顾](research/page-feature-vector-review-20261031/README.md)已用批量坐标处理保持60组完整分流及20组解释；97项检查通过。隔离Qwen3-VL4B在本机GPU实跑，两个公开输入存在字段归属/节点内容错误且延迟高，未接入默认采样；其它布局/独立准确率、轻量模型与全程序/视频仍待验。\n')
n='PROJECT_PROGRESS.md';s=(R/n).read_text('utf8');s=s.replace('全程序回顾尚未完成；','全程序回顾尚未完成；识别仍需解决探索与其它页面覆盖、字段归属、跨布局和连续延迟；本地视觉模型当前配置未通过准确性/实时性，替换方案须继续比较，不能以模型可运行代替验收；',1);save(n,s)
n='PROJECT_REQUIREMENTS.md';s=(R/n).read_text('utf8');marker='## 识别优化采用标准';assert marker in s;s=s.replace(marker,'## 神经网络识别候选的采用边界\n\n纯视觉模型与专门识别均可比较，不预设最终路线。页面分类正确、JSON合法或同图答案稳定不能替代字段归属与实际数值准确性；低频复杂页面和高频自动采样分别验延迟、覆盖与资源。候选运行及模型文件先隔离，未通过时不得写入真实本局；不猜不可见状态，不上传私人画面，不将测试成功当全场景通过。\n\n'+marker,1);save(n,s)
n='IMPLEMENTATION_STRATEGY.md';save(n,(R/n).read_text('utf8')+'\n[页面特征与本地视觉模型实测](research/page-feature-vector-review-20261031/README.md)保留原阈值、用现有批量接口减少特征处理开销。Qwen3-VL4B已在隔离GPU上实跑，但字段归属和延迟不满足当前自动采样，未接入生产；后续按真实覆盖/准确性/成本比较轻量定位与低频复杂页面方案，不预设混合方案或纯大模型一定获胜。\n')
n='VIDEO_PARITY.md';save(n,(R/n).read_text('utf8')+'\n[页面特征与本地视觉模型回顾](research/page-feature-vector-review-20261031/README.md)只推进读取实现和候选验真，未改变界面外观；公开录像图的本地推理不是完整视频、实机自动采样或全部字段准确性验收。\n')
cp=read('DEVELOPMENT_CHECKPOINT.json');cp['current_maintenance_save']={'kind':'implementation_review_maintenance','title':title,'receipt':P+'summary.json','binding':'enclosing_commit','functional_section_added':False,'status':'partial_program_review_vectorized_features_and_rejected_VLM_candidate','review_checklist':'PROGRAM_REVIEW.md','review_checklist_sha256':pin('PROGRAM_REVIEW.md')['sha256'],'application_review_complete':False};cp['current_batch']['receipt']=P+'summary.json';cp['next_action']='继续完整程序与视频逐链路回顾、已有三条代码约束整改和P3资料/地图/资源/界面；OCR同步推进探索覆盖、字段归属、连续延迟、分辨率与CPU/游戏同跑核验。Qwen3-VL4B实测可运行但准确性/实时性未过，未接入生产；新模型路线先比较覆盖和资源，不重复无新依据调提示。保留剩余1011敌人引用、完整数值及P3/P2/P1缺口；441未启动。'
save('DEVELOPMENT_CHECKPOINT.json',json.dumps(cp,ensure_ascii=False,indent=2)+'\n');idx=runpy.run_path(str(R/'scripts/update_cloud_index.py'));idx['update'](R);assert idx['validate_delivery'](R,cp)['current_section']==440
sys.path.insert(0,str(R/'scripts'));from verify_full_available import maintained_selectors
assert len(maintained_selectors())==723
write(P+'final-audit.json',{'passed':True,'baseline_commit':BASE,'summary':pin(P+'summary.json'),'requirements':pin('PROJECT_REQUIREMENTS.md'),'cloud_index':pin('CLOUD_INDEX.json'),'current_distinct_tests':97,'source_only_one_function':True,'ordered_selectors_unchanged':723,'VLM_trial_not_adopted_or_counted_as_accuracy_pass':True,'whole_program_or_video_complete':False,'goal_active':True})
(B/'record-source.py').write_bytes(Path(__file__).read_bytes())
files={p.relative_to(R).as_posix():{k:v for k,v in pin(p.relative_to(R)).items()if k!='path'}for p in sorted(B.rglob('*'))if p.is_file()and p.name!='archive-manifest.json'}
write(P+'archive-manifest.json',{'kind':'explicit_public_archive','files':files})
print(json.dumps({'passed':True,'tests':97,'VLM_tested_but_not_adopted':True,'public_receipt_files':len(files),'whole_goal_complete':False}))
