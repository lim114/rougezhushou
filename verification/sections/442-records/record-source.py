from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import json,subprocess,difflib,runpy,sys,re
R=Path.cwd();B=R/'verification/sections/442-records';B.mkdir(exist_ok=False)
BASE='480aa07f84e011f646cee90cd0d886023ce93694';title='希望上限识别与资源上限、容量历史回看'
def read(n):return json.loads((R/n).read_bytes())
def write(n,v):(R/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf8')
def pin(n):
    raw=(R/n).read_bytes();return {'receipt':str(n).replace('\\','/'),'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}
def save(n,s):
    p=R/n
    if not p.exists():p.write_text(s,'utf8');return
    a=p.read_text('utf8').splitlines(keepends=True);b=s.splitlines(keepends=True)
    # Preserve unchanged lines' actual original terminators.
    a=p.read_bytes().decode('utf8').splitlines(keepends=True)
    for x,y,k in difflib.SequenceMatcher(None,[v.rstrip('\r\n')for v in a],[v.rstrip('\r\n')for v in b],autojunk=False).get_matching_blocks():b[y:y+k]=a[x:x+k]
    p.write_bytes(''.join(b).encode('utf8'))
assert subprocess.check_output(['git','rev-parse','HEAD']).decode().strip()==BASE
assert subprocess.check_output(['git','branch','--show-current']).decode().strip()=='codex/p2-development'
checks=read('verification/sections/442-capacity-final/results.json')
assert checks['passed']and checks['tests_run']==52 and not checks['skipped']and not checks['failed']and not checks['errors']and not checks['forbidden_external_calls']
assert read('verification/sections/442-capacity-final/process.json')['actual_observed_exit']==0
ids=re.findall(r'^test_\w+ \(([^)]+)\)',(R/'verification/sections/442-capacity-final/stderr.txt').read_text('utf8'),re.M);assert len(ids)==len(set(ids))==52
native=read('verification/sections/442-native-capacity/window.json')
assert native['passed']and native['unique_checks']==22 and not any(native['external_operation_attempts'].values())and not native['source_drift']
assert read('verification/sections/442-native-capacity/process.json')['actual_observed_exit']==0
for n,digest in native['source_sha256_after'].items():assert sha256((R/n).read_bytes()).hexdigest()==digest,n
geometry=read('verification/sections/442-capacity-geometry-attempt2/results.json');assert geometry['passed']and len(geometry['cases'])==10
pairs=read('verification/sections/442-capacity-sample-pairs/results.json');assert pairs['passed']and len(pairs['pairs'])==20
clipping=read('verification/sections/442-capacity-clipping/results.json');assert clipping['passed']and len(clipping['cases'])==2
live=read('verification/sections/442-live-window/window.json');assert live['passed']and live['private_six_paths_unchanged']
status=read('.cache/resource-capacity-442-live-status.json');assert status['toolbar_visible']and status['elapsed_since_launch']>4
write('verification/sections/442-native-capacity/root-image-review.json',{'actual_PNG_viewed_one_by_one':True,'images':native['screenshots'],'capacity_history_and_old_map_pill_readable':True,'selected_old_limit_thirteen_stays_after_latest_nineteen':True,'temporary_state_only':True,'not_live_game_or_complete_video_parity':True})
write('verification/sections/442-live-window/desktop-review.json',{'actual_visible_responding_Qt_timer_advanced':True,'actual_Windows_mcp_screenshot_region':[1716,1164,2130,1218],'toolbar_actually_viewed':True,'private_six_paths_unchanged_at_startup':True,'not_live_game_resource_accuracy_or_full_video_parity':True})
before=read('.cache/resource-capacity-442-before.json')['private']
changed=[n for n,v in before.items()if(sha256((R/n).read_bytes()).hexdigest()if(R/n).is_file()else None)!=v]
write('verification/sections/442-records/private-scope.json',{'whole_batch_private_six_unchanged':not changed,'changed_paths_if_any':changed,'change_origin_not_inferred':bool(changed),'startup_private_six_paths_unchanged':True,'private_contents_hashes_images_and_expected_values_published':False,'private_backup_restore_or_rollback':False})
sources=['rouge/hud_resources.py','rouge/player_acceptance.py','rouge/player_floor_resources.py','rouge/player_replay_nodes.py','rouge/player_resource_acceptance.py','rouge/player_resource_facts.py','rouge/player_resource_history.py','rouge/relic_counter_semantics.py','rouge/run_state.py','scripts/player_ui_verification.py','scripts/verify_full_available.py','tests/test_resource_capacity_442.py']
write('verification/sections/442-records/source-review.json',{'base_commit':BASE,'changed_or_new_sources':{n:pin(n)for n in sources},'new_application_modules':0,'application_source_files':538,'REA_scope':'REA skill routes complete Python source to direct source/runtime review. No new REA-tool invocation or whole-program conclusion.','reuse':'Existing RapidOCR/OpenCV, template anchors and segmented digit recognizer, RunState, resource history, floor snapshots and replay widgets. No new model/dependency/provider.','source_evidence':'https://prts.wiki/w/集成战略 distinguishes available hope from its upper limit. Community mechanics evidence; current displayed numbers are read from pixels, never derived from this rule.','calculation_models_or_relic_mechanisms_changed':False,'observed_clipping_fix':'Original icon-relative ROI clipped the grey counter on the actual existing local reference; first geometry attempt retained. New extent follows the observed yellow glyph size, rejects cut grey digits and retains available hope.','new_low_probability_defensive_layer':False,'remaining_code_compliance_or_whole_program_review_complete':False})
for src,name in(('.cache/verify_capacity_sample_pairs_442.py','sample-pair-source.py'),('.cache/verify_capacity_geometry_442_attempt2.py','geometry-source.py'),('.cache/verify_capacity_clipping_442.py','clipping-source.py')):(B/name).write_bytes((R/src).read_bytes())
write('verification/sections/442-records/observation-boundaries.json',{'sample_pairs_terminal_result':pin('verification/sections/442-capacity-sample-pairs/results.json'),'sample_pair_outer_exec_handle_missing_at_resume':90945,'sample_pair_exit_code_not_retained':True,'sample_pair_job_not_restarted_for_missing_observation_handle':True,'clipping_actual_outer_exec_exit_observed':0,'native_and_necessary_process_exits_retained_separately':True,'not_a_full_suite_run':True})
write('verification/sections/442-records/failure-disposition.json',{'original_history_tests':'verification/sections/442-capacity-before','initial_tests':8,'initial_failures':6,'initial_errors':1,'history_fix':'Initial resource records retain capacity; unchanged amount with changed limit logs a new observation; post-upgrade reread is current, never edits legacy events. Floor identity includes capacities and historical UI reads only selected snapshot.','original_geometry':'verification/sections/442-capacity-geometry','original_geometry_failed_private_variants':5,'geometry_fix':'Extend grey-number ROI from actual yellow glyph box/font. Full new capacity is required; clipping never turns a partial digit into a capacity.','final_geometry':'verification/sections/442-capacity-geometry-attempt2','original_evidence_kept_unmodified':True})
save('research/resource-capacity-442/README.md',f'''# 第442节 + {title}

基线{BASE}。本节补参考视频资源读取与本局历史的实际缺口，不以研究或测试凑节数。全程序及完整视频效果仍未完成。

## 实际问题与处理

第441节只读黄色可用希望，灰色上限缺失。当前复用原图标定位、OpenCV分色和原单行数字识别器，分别读取两者；区域随当前图标、字号和黄色数字位置调整，没有增加固定屏幕象限或换一套模型。可用值明确而上限不完整时只保留可用值，不把残缺数字或相邻指挥等级当作上限。第一轮已有本机参考图的5种几何变体都因原范围裁掉灰色数字而未读上限，失败原件保留；按实际黄色字框扩展后通过，另测两份公开图右侧裁切仍不补猜。

[PRTS集成战略资料](https://prts.wiki/w/集成战略)区分希望与希望上限，持有希望不超过上限。这是社区机制证据，不冒称当前服务器实测。本轮只读显示值，不推导希望、藏品效果或战斗数值；对原识别器/图标来源与许可沿用[441记录](../hud-resources-441/README.md)。

原数量历史漏掉了“7/13→7/17”的上限独立变化，最初8项检查出现6失败/1错误。现在初次读到、上限单独变化和上限从可读变为未读均保留对应记录；数量变化与上限变化分开显示。旧日志没有上限时继续保持未知，升级后再次读到才记当前时刻，不能把最新上限补到过去。生命上限、希望上限和零件箱容量共用已存在历史与快照；不赋予其它资源未核验的容量语义。

同区域快照比较同时考虑容量；读取历史地图只用所选步骤自己的数量和上限。数量为0与未读分开，自动刷新保留原选择；缺少中间上限时不跨未知记录计算变化。复用既有组件与共享格式化，没有增加应用模块、依赖或宽泛异常吞没；冗余资源名称映射、循环内重复导入与重复数值检查同批合并。不以新增防御层解决已知裁切。

## 当前证据与限制

最终52项不同必要检查通过，0失败/错误/跳过；22项真实Windows原生唯一检查通过，两份最终截图已逐张查看。20张既有开发样本的新旧完整解释，仅扣除刻意新增的hope.capacity后相同；其终态结果文件完整保留，恢复时外层会话句柄已不存在，未保留的退出码不编造，也未因此重启任务。

一个公开参考图和一个人工核对的既有本机开发图，各原尺寸、0.65/0.8/1.25和留边平移共10组，已核对字段/生命上限/希望上限匹配；公开图可用希望7、上限13。两份裁切也是同一公开图的派生，均保留可用7并不声称读全上限。这些不是12次独立对局，不证明其它布局、遮挡、转场或连续实机全部准确。参数化脚本不包含私人图片、身份、实际数字或像素摘要；本机对照预期只在忽略目录。

几何、样本配对与原生过程曾并行占用CPU；本节增加一项灰色数字识别，不声称整体提速、GPU资源无代价或游戏FPS改善。完整选择器顺序保留并追加本节为725，仅核对实际CLI载入次序，没有重跑725模块全量；full440只证明原冻结源码，下次完整455。

实际测试小窗已更新、可见响应且Qt计时器推进，启动六私人路径保持；整批摘要核对另见private-scope.json，如有变化只记事实不归因、不恢复旧局。未操作游戏、发聊天或上传私人数据。其它资源/布局、连续读取、完整结算、全程序存量约束整改和视频其余功能/交互/外观仍待完成。

[本节回执](../../verification/sections/442.json)。
''')
entry=f'''<!-- player-section-442 -->
## 第442节 + {title}

灰色希望上限与黄色可用量分开读取；生命/希望上限和零件箱容量保留各自历史，上限改变而数量不变也记录。旧层只显示当时已读值，升级后不追填旧日志；自动刷新保留阅读选择。复用现有识别与历史组件，不引入新模型或计算机制。

最终52项必要检查、22项原生唯一检查通过，两张最终原图已查看；20样本原事实保持、10组几何字段匹配和2组裁切保留可用值，均不冒充独立连续游戏准确性或性能提升。首轮失败保留，725选择器顺序已核对，未跑全量。测试小窗更新可见响应，启动六私人路径保持。回执verification/sections/442.json；全程序/全视频及P3/P2/P1未完成，下次完整455。

'''
for n in('WORK_IN_PROGRESS.md','PROJECT_COMPLETED.md'):
    s=(R/n).read_text('utf8')
    if n=='WORK_IN_PROGRESS.md':s=s[s.index('<!-- player-section-441 -->'):]
    save(n,entry+s)
old='灰色希望上限读取、上限独立变化历史与其余资源布局/连续实机准确性'
n='PROJECT_PROGRESS.md';s=(R/n).read_text('utf8');assert old in s;s=s.replace(old,'其余资源布局、遮挡/转场、连续实机读取与完整结算准确性');save(n,s)
n='PROGRAM_REVIEW.md';s=(R/n).read_text('utf8');s=s.replace('灰色希望上限、上限独立历史和其余布局/连续实机资源准确性尚待核对，','其余布局、遮挡/转场、连续实机资源与完整结算准确性尚待核对，',1)
save(n,s+'\n[第442节希望上限与资源历史](research/resource-capacity-442/README.md)补独立容量变化和旧层准确回看；52项必要/22项原生、20组原事实对照和有限几何/裁切检查保持。只证明已验范围，不视为全程序或全部资源准确性完成。\n')
n='PROJECT_REQUIREMENTS.md';s=(R/n).read_text('utf8');start=s.index('<!-- player-batch-current:start -->');end=s.index('<!-- player-batch-current:end -->')+len('<!-- player-batch-current:end -->')
block='''<!-- player-batch-current:start -->
## 当前批次要求 · 全程序回顾与视频效果对齐

持续完整程序回顾，优先复用经许可且适合本机的实现，发现有证问题及时修正；最终验收包含参考视频全部功能、交互及外观，不以文件扫描、局部测试或节数代替。保持Python/Qt，当前功能第442节；真实断点、回执与发布证明见DEVELOPMENT_CHECKPOINT.json和云端索引，下一完整范围455。full440仅证明它的原冻结源码。

P3→P2→P1；OCR及识别覆盖、适配、准确率与耗时同步优化。新增及存量代码按入口单次校验、单次逻辑不过度抽函数、新增低概率防御先征求同意回顾。最高优先五条要求继续有效。

资源数量、上限和容量应分别读取和保留；旧历史只显示当时记录，未知不补猜。当前希望上限与容量历史的已验范围见442回执；其它布局、连续游戏准确性和完整结算仍未完成。大模型仅作为待比较候选，运行成功或格式合法不等于准确可用。

仅局外查阅及后台只读采样；不操作游戏、发开发测试聊天、上传私人数据、清空本局或覆盖私人配置。普通ChatGPT会话目标保留，不以Codex后端代替；只读取公开统计离线计算，不推荐或自动选路。商店先读已有文字，游戏画面藏品悬停不由助手目录替代；不同DPI/布局和视频外观逐项核对。

每节实质功能、必要验收、当前要求与索引同提交普通推送并核对真实远端；严格低于15%才开始当前完整小节收尾。历史逐节内容见PROJECT_COMPLETED.md，不堆入当前要求。
<!-- player-batch-current:end -->'''
s=s[:start]+block+s[end:]
old='目标生命、护盾、指挥等级、希望、行动力和总估价按当前可见标签/图标对应，生命当前值与上限分开；'
assert old in s;s=s.replace(old,'目标生命、护盾、指挥等级、希望、行动力和总估价按当前可见标签/图标对应，生命和希望的当前值与上限分开，零件箱数量与容量分开；',1)
marker='## 神经网络识别候选的采用边界';assert marker in s
s=s.replace(marker,'上限/容量单独变化也须记录，与数量变化分别说明；初读不当作从零增加，旧日志不追填，中间未读不跨越计算变化。区域/地图快照只使用同次接受的字段，当前与历史保持分开。上限裁切或归属不明确时保留已证数量，上限保持未读。\n\n'+marker,1);save(n,s)
n='VIDEO_PARITY.md';s=(R/n).read_text('utf8').replace('第441节已接入目标生命等六项读值，灰色希望上限及其余版式/连续准确性仍待验。','第441–442节已接入六项读值、希望上限及容量历史，其余版式/遮挡与连续准确性仍待验。',1)
save(n,s+'\n[第442节](research/resource-capacity-442/README.md)补灰色希望上限和旧层数量/上限回看，数量不变时也保留上限变化。未读字段不追填；现有小窗/历史组件复用，不冒称全部视频外观或完整实机记录已验。\n')
n='IMPLEMENTATION_STRATEGY.md';s=(R/n).read_text('utf8').replace('本次为第440节后的实现维护，不启动441。','当前第442节资源上限与历史已验，下一节以当前断点为准。',1)
save(n,s+'\n[第442节](research/resource-capacity-442/README.md)沿用当前识别器与颜色分离补希望上限，复用原本局历史、区域快照与阅读组件。现有参考图实际裁切失败同批修正；不新增模型、固定象限、通用重试或异常吞没层。\n')
receipt={'section':442,'kind':'functional_section','title':title,'new_capability':'读取灰色希望上限；生命/希望上限与零件容量单独变动也入历史和同区域快照；旧层保留当时上限，刷新保留阅读，不追填旧日志。','limitations':'有限开发样本/公开图几何与裁切对照，不是独立连续实机准确性。完整资源、其余版式、结算、全程序和视频仍未完成，未宣称提速或接入视觉大模型。','necessary_validation':pin('verification/sections/442-capacity-final/process.json'),'unit_tests_run':52,'native_windows_validation':{'receipt':'verification/sections/442-native-capacity/window.json','unique_checks':22,'process':pin('verification/sections/442-native-capacity/process.json')},'root_visual_review':pin('verification/sections/442-native-capacity/root-image-review.json'),'sample_pairs':pin('verification/sections/442-capacity-sample-pairs/results.json'),'geometry':pin('verification/sections/442-capacity-geometry-attempt2/results.json'),'clipping':pin('verification/sections/442-capacity-clipping/results.json'),'actual_local_test_window':pin('verification/sections/442-live-window/window.json'),'source_sha256':{n:sha256((R/n).read_bytes()).hexdigest()for n in sources},'source_review':pin('verification/sections/442-records/source-review.json'),'full_suite_rerun':False,'old_full440_proves_current_source':False,'goal_active':True,'whole_program_or_video_complete':False,'at_UTC':datetime.now(timezone.utc).isoformat()}
write('verification/sections/442.json',receipt)
cp=read('DEVELOPMENT_CHECKPOINT.json');assert cp['completed_sections']==441 and cp['next_section']==442
cp['completed_sections']=442;cp['next_section']=443;cp['sections'].append({'number':442,'completion_ref':'player-section-442','topic':title,'verification':'verification/sections/442.json'})
cp['current_section_save']={'section':442,'verification':'verification/sections/442.json','scope':'current_functional_section','binding':'enclosing_commit'}
cp['last_verified_cloud_save']['scope']='previous_functional_section'
cp['current_section_validation']={'section':442,'receipt':'verification/sections/442.json','necessary_checks':52,'native_unique_checks':22,'full_validation_rerun':False}
cp['current_batch'].update(completed_sections=442,next_section=443,next_section_started=False,receipt='verification/sections/442.json',scope='Whole-program review and complete video parity remain active. Functional442 hope capacity and historical resource limits completed in verified scope;443 not started.')
cp['next_action']='继续全程序/视频逐链路回顾，保留希望上限与资源容量历史；优先其余P3地图/事件/物品及界面缺口，识别跨布局/遮挡/连续准确性与资源成本同步核对。存量代码三条规则继续整改；全程序、视频、完整数值与P3/P2/P1未完成。443未启动，下次完整455。'
if isinstance(cp.get('player_feature_sections'),list):cp['player_feature_sections'].append(442)
assert isinstance(cp['functional_sections_since_latest_requirement'],list);assert cp['functional_sections_since_latest_requirement'][-1]==441
cp['functional_sections_since_latest_requirement'].append(442)
save('DEVELOPMENT_CHECKPOINT.json',json.dumps(cp,ensure_ascii=False,indent=2)+'\n')
idx=runpy.run_path(str(R/'scripts/update_cloud_index.py'));idx['update'](R);assert idx['validate_delivery'](R,cp)['current_section']==442
sys.path.insert(0,str(R/'scripts'));from verify_full_available import maintained_selectors
assert len(maintained_selectors())==725
write('verification/sections/442-records/final-audit.json',{'passed':True,'functional_section':442,'source_review':pin('verification/sections/442-records/source-review.json'),'requirements':pin('PROJECT_REQUIREMENTS.md'),'index':pin('CLOUD_INDEX.json'),'section_receipt':pin('verification/sections/442.json'),'necessary_distinct_tests':52,'native_unique_checks':22,'ordered_selectors':725,'active_functional_list_includes442':cp['functional_sections_since_latest_requirement'][-1]==442,'current_full_rerun':False,'goal_active':True,'whole_program_or_video_complete':False})
(B/'record-source.py').write_bytes(Path(__file__).read_bytes())
files={}
for folder in(R/'verification/sections').glob('442-*'):
    if folder.is_dir():files.update({p.relative_to(R).as_posix():{k:v for k,v in pin(p.relative_to(R)).items()if k!='receipt'}for p in folder.rglob('*')if p.is_file()and p.name!='archive-manifest.json'})
files['verification/sections/442.json']={k:v for k,v in pin('verification/sections/442.json').items()if k!='receipt'}
write('verification/sections/442-records/archive-manifest.json',{'kind':'explicit_public_archive_no_private_inputs_or_expected_values','files':files})
print(json.dumps({'passed':True,'section':442,'necessary_distinct_tests':52,'native_unique_checks':22,'archive_files':len(files),'whole_goal_complete':False}))
