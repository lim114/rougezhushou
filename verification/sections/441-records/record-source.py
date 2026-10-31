from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import json,subprocess,difflib,runpy,sys,re
R=Path.cwd();B=R/'verification/sections/441-records';B.mkdir(exist_ok=False);D=R/'research/hud-resources-441';D.mkdir(exist_ok=False)
BASE='215a8354cced2452941373bd403e3c931164d457';title='六项界面资源读取与本局资源栏、历史同步'
def read(n):return json.loads((R/n).read_bytes())
def write(n,v):(R/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf8')
def pin(n):
    raw=(R/n).read_bytes();return {'receipt':str(n).replace('\\','/'),'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}
def save(n,s):
    p=R/n
    if not p.exists():p.write_text(s,'utf8');return
    a=p.read_bytes().decode('utf8').splitlines(keepends=True);b=s.splitlines(keepends=True)
    for x,y,k in difflib.SequenceMatcher(None,[v.rstrip('\r\n')for v in a],[v.rstrip('\r\n')for v in b],autojunk=False).get_matching_blocks():b[y:y+k]=a[x:x+k]
    p.write_bytes(''.join(b).encode('utf8'))
assert subprocess.check_output(['git','rev-parse','HEAD']).decode().strip()==BASE
assert subprocess.check_output(['git','branch','--show-current']).decode().strip()=='codex/p2-development'
checks=read('verification/sections/441-hud-checks-current/results.json');assert checks['passed']and checks['tests_run']==43 and not checks['skipped']and not checks['failed']and not checks['errors']and not checks['forbidden_external_calls']
assert read('verification/sections/441-hud-checks-current/process.json')['actual_observed_exit']==0
ids=re.findall(r'^test_\w+ \(([^)]+)\)',(R/'verification/sections/441-hud-checks-current/stderr.txt').read_text('utf8'),re.M);assert len(ids)==len(set(ids))==43
assert read('verification/sections/441-hud-checks-scope-before-repair/process.json')['actual_observed_exit']==1
native=read('verification/sections/441-native-hud/window.json');assert native['passed']and native['unique_checks']==32 and not any(native['external_operation_attempts'].values())and not native['source_drift']
assert read('verification/sections/441-native-hud/process.json')['actual_observed_exit']==0
for n,digest in native['source_sha256_after'].items():assert sha256((R/n).read_bytes()).hexdigest()==digest,n
geometry=read('verification/sections/441-hud-geometry-current/results.json');assert geometry['passed']and len(geometry['cases'])==10
pairs=read('verification/sections/441-hud-sample-pairs/results.json');assert pairs['passed']and len(pairs['pairs'])==20
local=read('.cache/hud-private-six-field-check.json');assert local['manual_image_reviewed']and not local['private_runtime_state_applied']and all(v['equal']for v in local['rows'].values())
live=read('verification/sections/441-live-window/window.json');assert live['passed']and live['private_six_paths_unchanged']
write('verification/sections/441-native-hud/root-image-review.json',{'actual_PNG_viewed':True,'images':native['screenshots'],'six_resources_readable_and_zero_distinct_from_unread':True,'temporary_state_only':True,'not_live_game_or_complete_video_parity':True})
write('verification/sections/441-live-window/desktop-review.json',{'actual_visible_responding_Qt_timer_advanced':True,'physical_rect_queried':[1716,1164,2130,1218],'native_feature_PNG_actually_viewed':True,'private_six_paths_unchanged_at_startup':True,'not_a_live_game_resource_accuracy_claim':True})
public60=read('.cache/hud-public-check/60.json');resources=public60['run']['resources']
assert {k:resources[k]['value']for k in('life','shield','command','hope')}=={'life':6,'shield':1,'command':1,'hope':7}
write('verification/sections/441-records/public-reference.json',{'video_frame':60,'public_frame_png_sha256':sha256((R/'.cache/vlm-public-reference-frames/60.png').read_bytes()).hexdigest(),'resources_read':resources,'scope':'Public reference frame only; cropped/occluded action and valuation are not filled. 20 private development samples and current run contents are not in this record.'})
before=read('.cache/hud-resources-before.json')['private'];changed=[n for n,v in before.items()if(sha256((R/n).read_bytes()).hexdigest()if(R/n).exists()else None)!=v]
write('verification/sections/441-records/private-scope.json',{'whole_batch_private_six_unchanged':not changed,'changed_paths_if_any':changed,'change_origin_not_inferred':bool(changed),'startup_private_six_unchanged':True,'private_contents_hashes_and_expected_values_published':False,'no_private_backup_restore_or_rollback':True,'private_sample_numeric_expectations_only_in_ignored_cache':True})
assert not(set(changed)-{'.local/run-state.json'})
sources=['rouge/hud_resources.py','rouge/resource_recognition.py','rouge/run_recognition.py','rouge/run_state.py','rouge/relic_counter_semantics.py','rouge/player_resource_facts.py','rouge/player_acceptance.py','rouge/player_resource_acceptance.py','scripts/verify_full_available.py','tests/test_hud_resources_441.py','tests/test_player_resource_strip.py','rouge/data/ui-icons/hud-counter-sources.json','rouge/data/ui-icons/hud-hope.png','rouge/data/ui-icons/hud-shield.png']
write('verification/sections/441-records/source-review.json',{'base_commit':BASE,'changed_or_new_sources':{n:pin(n)for n in sources},'runtime_source_added':1,'REA_scope':'REA skill routes complete Python source to direct source/runtime review; no new REA-tool invocation or full-program conclusion.','reuse':'Existing RapidOCR1.4.4, OpenCV, anchors.crop, RunState, ResourceStrip, resource/floor history; no new model/provider/dependency.','calculation_models_or_relic_mechanisms_changed':False,'new_low_probability_defensive_layer':False,'once_at_ingress':'New six-key integer admission extends existing RunState resource entry; no repeated state validation or broad exception swallowing.','conditional_old_api':'Optional engine preserves the preexisting read_resources(image,texts) API while the sampling path supplies the engine for new fields.','whole_source_compliance_complete':False})
for source,target in(('.cache/verify_hud_resource_samples.py','sample-pair-source.py'),('.cache/verify_hud_geometry_current.py','geometry-current-source.py')):(B/target).write_bytes((R/source).read_bytes())
(B/'record-source.py').write_bytes(Path(__file__).read_bytes())
write('verification/sections/441-records/failure-disposition.json',{'original_first_checks':'verification/sections/441-hud-checks-attempt1','original_failures':3,'scope':'Two new fixture expectations were corrected: exact current zone name is required, tooltip says最近读到. The old blanket-unread assertion was updated to require observed life while retaining all five genuinely unread peers. Original receipts kept.','actual_existing_CLI_scope_bug':'verification/sections/441-hud-checks-scope-before-repair','CLI_repair':'Grade16 declaration was below sys.exit(main()); moved entrypoint after all declarations, then appendedHUD441. New interception test observes the actual CLI loader names and stops before running the full suite. No full-suite receipt is fabricated.'})
save(D.relative_to(R)/'README.md',f'''# 第441节 + {title}

基线{BASE}。这是参考视频资源读取缺口的功能节，不是用研究或测试凑编号。完整程序回顾及视频全部效果仍未完成。

目标生命、护盾、指挥等级、希望、行动力与总估价原为常驻“未读”。现由当前标签和已核对图标定位，再复用现有OCR；标签直接能唯一对应数字时不重复识别，已分离的希望数字直接用原识别器，不再让检测器重复找这个单字。护盾和希望模板仅含静态图案，取自用户提供的公开参考录像60秒，未夹带数字；来源裁剪和摘要随图保留。本轮不使用视觉大模型，不新增依赖/联网推理或修改游戏机制。

区域随当前标签大小/图标位置生成，不使用固定屏幕象限。希望只读黄色可用量，不把灰色希望上限、指挥等级或保密等级当成它。目标生命保留当前值/上限。不可见、含糊和负号形式未确认时不钳位或推算；当前范围为非负整数，不能据此声称游戏永不出现其它形式。

语义依据：[PRTS集成战略机制](https://prts.wiki/w/集成战略)区分希望与希望上限；[黑流树海资料](https://prts.wiki/w/树海肉鸽)区分目标生命上限、护盾与行动力。它们是社区资料，不冒称官方当前服务器实测。本轮只读取显示值，不按这些资料推算状态或新增战斗数值效果。分辨率定位/数值识别以实际图像对照验证，参考[OpenCV模板匹配](https://docs.opencv.org/4.x/d4/dc6/tutorial_py_template_matching.html)及当前已装RapidOCR接口；原许可和署名保持。

六字段接入原本局保存、重启、数值变化历史与同帧区域资源快照；离开页面或未读保留各自最近数值和时刻，只有用户手动新局清空。原资源胶囊共用一组更新，正常显示0与未读、生命当前值/上限；普通玩家无需理解代码字段。新字段仅用于读取/显示，不进入未核验的藏品计算。历史仍沿用标量数量，尚未补齐上限单独变化的历史；灰色希望上限也未读取，不以当前上限补写旧层。

43项不同必要检查通过，0跳过/失败/错误；32项实际Windows原生唯一检查通过，真实PNG已逐张查看。20张既有本机开发样本，新旧完整解释除新增六键外相同；一个公开参考图和一份人工核对的本机旧样本，各原尺寸/0.65/0.8/1.25及平移留边共10组，预先人工核对的可见字段一致，本机样本覆盖全部六项。它们不是10次独立游戏对局，不证明任意布局、遮挡、动态转场或当前游戏新帧全部正确。私人样本图片/数值/身份/像素摘要不发布，参数化复现脚本需本机忽略的对照输入。

新增读取会带来局部处理成本；配对顺序、缓存、初始化和负载有影响，本轮不声称完整读取提速、游戏FPS或CPU代价已验收。原前三个失败保留：两条夹具/用词修正及旧常驻未读断言更新；全量脚本的真实执行/导入范围不一致另行复现并修正。原导入723选择器保持顺序，追加441后724，实际CLI在载入测试前取得同一顺序；不是执行了724模块全量。上次full440只证明它的原冻结源码，下次455。

实际测试小窗已正常更新，可见、响应且Qt计时器推进，启动六私人路径保持；本批若有本局记录变化仅按摘要如实记载，不恢复旧局。未操作游戏、发送聊天或上传私人输入。全程序、视频其余流程/外观及P3/P2/P1未完成。

[功能回执](../../verification/sections/441.json)。
''')
entry=f'''<!-- player-section-441 -->
## 第441节 + {title}

六字段从当前标签/图标读取，接入原本局保存、重启、数量变化历史及资源胶囊；生命显示当前值/上限，0与未读分开，未读保留各自最近值与时刻，不导入未核验藏品计算。只复用现有OCR/OpenCV与状态/界面组件，未接入视觉大模型。灰色希望上限、上限独立历史与其余布局/连续实机准确性仍待验证。

43项必要检查、32项原生唯一检查通过；20样本旧事实保持，10组尺度/平移可见字段匹配，非10次独立对局，不称全流程提速。原失败和实际CLI漏grade16选择器的修复证据保留；724有序选择器与真实CLI选择相同，未重跑全量。测试小窗更新、启动私人六路径保持。回执verification/sections/441.json；全程序/全视频与P3/P2/P1仍未完成，下次全量455。

'''
for n in('WORK_IN_PROGRESS.md','PROJECT_COMPLETED.md'):
    s=(R/n).read_text('utf8')
    if n=='WORK_IN_PROGRESS.md':s=s[s.index('<!-- page-feature-vector-review-20261031:start -->'):]
    save(n,entry+s)
n='AGENTS.md';s=(R/n).read_text('utf8');old='第440节已收尾；当前按用户要求继续全程序回顾与实现改进，441未启动。下一完整验收455，维护不增加功能节数。';assert old in s;s=s.replace(old,'当前断点、进行中工作与下一完整验收见 `DEVELOPMENT_CHECKPOINT.json` 和 `WORK_IN_PROGRESS.md`；持续进行全程序回顾，维护不增加功能节数。',1);save(n,s)
n='PROGRAM_REVIEW.md';s=(R/n).read_text('utf8').replace('当前总范围537份','当前总范围538份',1);s=s.replace('六项资源自动读取尚未覆盖，','灰色希望上限、上限独立历史和其余布局/连续实机资源准确性尚待核对，',1);save(n,s+'\n[第441节资源读取](research/hud-resources-441/README.md)新增六项读值并复用保存/历史/胶囊，43项必要及32项原生检查通过，20样本旧事实保持、10组可见字段匹配；非所有布局或独立连续游戏验收。修复全量CLI漏grade16注册，724顺序与导入一致但未执行全量。全程序/视频及存量规则整改仍未完成。\n')
n='PROJECT_PROGRESS.md';s=(R/n).read_text('utf8');s=s.replace('六项资源自动读取','灰色希望上限读取、上限独立变化历史与其余资源布局/连续实机准确性');save(n,s)
n='PROJECT_REQUIREMENTS.md';s=(R/n).read_text('utf8');marker='## 神经网络识别候选的采用边界';assert marker in s;s=s.replace(marker,'## 界面资源的读取与保留\n\n目标生命、护盾、指挥等级、希望、行动力和总估价按当前可见标签/图标对应，生命当前值与上限分开；不以保密等级、希望灰色上限、地图步数或藏品推算代替实际读值。0与未读分开，未读保留同局最近确认值及读取时间，旧层只显示当时记录，不能用当前资源补写。采样坐标随当前特征调整；新增显示字段不自动变成藏品数值机制。\n\n'+marker,1);save(n,s)
n='VIDEO_PARITY.md';s=(R/n).read_text('utf8').replace('目标生命等六项仍未支持读取。','第441节已接入目标生命等六项读值，灰色希望上限及其余版式/连续准确性仍待验。',1);save(n,s+'\n[第441节资源读取](research/hud-resources-441/README.md)补常驻六项“未读”的真实读取路径和现有资源胶囊展示；未重做窗口布局，不称完整视频一致。只在对应标签/图标清晰时更新，既有本机样本和公开参考图的几何对照不是全部游戏环境验收。\n')
save('IMPLEMENTATION_STRATEGY.md',(R/'IMPLEMENTATION_STRATEGY.md').read_text('utf8')+'\n[第441节](research/hud-resources-441/README.md)优先复用已有OCR、图标匹配、状态和资源胶囊，接通六项界面读值。未采用高延迟且字段归属失败的视觉模型；新路线仍可独立比较，不将小范围图像测试推广为全部环境或CPU/FPS结论。\n')
receipt={'section':441,'kind':'functional_section','title':title,'new_capability':'目标生命、护盾、指挥等级、希望、行动力和总估价从当前标签/图标读值，接入本局保存、重启、数量变化历史及已有资源胶囊；未读保留最近确认值，0与未知分开，生命显示当前值/上限。','limitations':'希望上限、上限独立变化历史及其余字体/遮挡/布局和连续实机准确性仍未完成；本机旧样本和公开参考图的几何变体不等于独立实机对局。不将显示字段导入未经核验的藏品计算，未声称完整读取提速。','necessary_validation':pin('verification/sections/441-hud-checks-current/process.json'),'unit_tests_run':43,'native_windows_validation':{'receipt':'verification/sections/441-native-hud/window.json','unique_checks':32,'process':pin('verification/sections/441-native-hud/process.json')},'root_visual_review':pin('verification/sections/441-native-hud/root-image-review.json'),'sample_pairs':pin('verification/sections/441-hud-sample-pairs/results.json'),'geometry':pin('verification/sections/441-hud-geometry-current/results.json'),'actual_local_test_window':pin('verification/sections/441-live-window/window.json'),'source_sha256':{n:sha256((R/n).read_bytes()).hexdigest()for n in sources},'full_suite_rerun':False,'old_full440_proves_current_source':False,'source_review':pin('verification/sections/441-records/source-review.json'),'goal_active':True,'whole_program_or_video_complete':False,'at_UTC':datetime.now(timezone.utc).isoformat()}
write('verification/sections/441.json',receipt)
cp=read('DEVELOPMENT_CHECKPOINT.json');assert cp['completed_sections']==440 and cp['next_section']==441
cp['completed_sections']=441;cp['next_section']=442;cp['sections'].append({'number':441,'completion_ref':'player-section-441','topic':title,'verification':'verification/sections/441.json'})
cp['current_section_save']={'section':441,'verification':'verification/sections/441.json','scope':'current_functional_section','binding':'enclosing_commit'}
cp['last_verified_cloud_save']['scope']='previous_functional_section'
cp['current_section_validation']={'section':441,'receipt':'verification/sections/441.json','necessary_checks':43,'native_unique_checks':32,'full_validation_rerun':False}
cp['historical_implementation_maintenance_before441']=cp.pop('current_maintenance_save')
cp['current_batch'].update(completed_sections=441,next_section=442,next_section_started=False,receipt='verification/sections/441.json',scope='Whole-program review and implementation improvement continues. Functional441 resource readout completed;442 not started. Complete all original requirements, not file inventory or isolated compatibility.')
cp['next_action']='继续全程序与视频逐链路回顾，保留六项已接入读值；补灰色希望上限、上限独立历史、其余布局/遮挡/连续实机准确性与资源成本，继续P3资料/地图/资源和界面。OCR同步优化，存量三条代码规则继续整改；P3/P2/P1、完整数值和全视频未完成。442未启动，下次完整455。'
if isinstance(cp.get('player_feature_sections'),list):cp['player_feature_sections'].append(441)
save('DEVELOPMENT_CHECKPOINT.json',json.dumps(cp,ensure_ascii=False,indent=2)+'\n')
idx=runpy.run_path(str(R/'scripts/update_cloud_index.py'));idx['update'](R);assert idx['validate_delivery'](R,cp)['current_section']==441
sys.path.insert(0,str(R/'scripts'));from verify_full_available import maintained_selectors
assert len(maintained_selectors())==724
write('verification/sections/441-records/final-audit.json',{'passed':True,'functional_section':441,'source_review':pin('verification/sections/441-records/source-review.json'),'requirements':pin('PROJECT_REQUIREMENTS.md'),'index':pin('CLOUD_INDEX.json'),'section_receipt':pin('verification/sections/441.json'),'necessary_distinct_tests':43,'native_unique_checks':32,'ordered_selectors':724,'current_full_rerun':False,'goal_active':True,'whole_program_or_video_complete':False})
files={p.relative_to(R).as_posix():{k:v for k,v in pin(p.relative_to(R)).items()if k!='receipt'}for p in sorted((R/'verification/sections').rglob('441*'))if p.is_file()}
for folder in(R/'verification/sections').glob('441-*'):
    if folder.is_dir():files.update({p.relative_to(R).as_posix():{k:v for k,v in pin(p.relative_to(R)).items()if k!='receipt'}for p in folder.rglob('*')if p.is_file()and p.name!='archive-manifest.json'})
files['verification/sections/441.json']={k:v for k,v in pin('verification/sections/441.json').items()if k!='receipt'}
write('verification/sections/441-records/archive-manifest.json',{'kind':'explicit_public_archive_no_private_inputs_or_expected_values','files':files})
print(json.dumps({'passed':True,'section':441,'tests':43,'native':32,'archive_files':len(files),'whole_goal_complete':False}))
