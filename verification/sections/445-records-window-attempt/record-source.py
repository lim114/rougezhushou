from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import json,subprocess,difflib,runpy,sys,re
R=Path.cwd();sys.path.insert(0,str(R/'scripts'));BASE='91fd3ce5481bc149902dc40cd47d6a8e064b6f64';B=R/'verification/sections/445-records'
title='藏品来源节点分组、图标与准确地图入口'
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
checks=read('verification/sections/445-related-final/results.json')
assert checks['passed']and checks['tests_run']==70 and not checks['failed']and not checks['errors']and not checks['skipped']and not checks['forbidden_external_calls']
assert read('verification/sections/445-related-final/process.json')['actual_observed_exit']==0
ids=re.findall(r'^test_\w+ \(([^)]+)\)',(R/'verification/sections/445-related-final/stderr.txt').read_text('utf8'),re.M);assert len(ids)==len(set(ids))==70
native=read('verification/sections/445-native-source-nodes-final/window.json');assert native['passed']and native['unique_checks']==25 and not native['source_drift']and not any(native['external_operation_attempts'].values())
assert read('verification/sections/445-native-source-nodes-final/process.json')['actual_observed_exit']==0
for n,digest in native['source_sha256_after'].items():assert sha256((R/n).read_bytes()).hexdigest()==digest,n
live=read('verification/sections/445-live-window/window.json');assert live['passed']and live['private_six_paths_unchanged']
status=read('.cache/source-nodes-445-live-status.json');assert status['toolbar_visible']and status['elapsed_since_launch']>4
B.mkdir(exist_ok=False)
write('verification/sections/445-native-source-nodes-final/root-image-review.json',{'two_actual_final_PNGs_viewed':True,'images':native['screenshots'],'appearance_does_not_replace_25_actual_interaction_checks':True,'isolated_widgets_not_live_game_or_complete_video_parity':True})
write('verification/sections/445-live-window/desktop-review.json',{'Windows_mcp_region':[1716,1164,2130,1218],'actual_toolbar_viewed':True,'visible_responding_and_Qt_timer_advanced':True,'startup_six_private_paths_unchanged':True,'not_a_live_game_accuracy_claim':True})
before=read('.cache/source-nodes-445-before.json')['private'];changed=[n for n,v in before.items()if(sha256((R/n).read_bytes()).hexdigest()if(R/n).is_file()else None)!=v]
write('verification/sections/445-records/private-scope.json',{'whole_batch_private_six_unchanged':not changed,'changed_paths_if_any':changed,'change_origin_not_inferred':bool(changed),'startup_six_paths_unchanged':True,'private_contents_hashes_images_or_expected_values_published':False,'private_backup_restore_or_rollback':False})
sources=['rouge/player_source_cards.py','rouge/player_item_hover.py','rouge/player_map.py','rouge/player_acceptance.py','rouge/player_item_acceptance.py','scripts/player_ui_verification.py','scripts/verify_full_available.py','tests/test_source_nodes_445.py']
for n in('rouge/player_source_cards.py','rouge/player_item_hover.py','rouge/player_map.py'):assert (R/'research/source-nodes-445'/('before-'+Path(n).name)).read_bytes()==subprocess.check_output(['git','show',BASE+':'+n])
old_native=read('verification/sections/445-native-source-map-436/window.json');assert old_native['passed']and old_native['unique_checks']==18 and not old_native['source_drift']and not any(old_native['external_operation_attempts'].values())
assert read('verification/sections/445-native-source-map-436/process.json')['actual_observed_exit']==0
for n,digest in old_native['source_sha256_after'].items():assert sha256((R/n).read_bytes()).hexdigest()==digest,n
write('verification/sections/445-native-source-map-436/root-image-review.json',{'actual_final_PNG_viewed':True,'images':old_native['screenshots'],'old_scope_436_kept_separate_from_current25':True})
write('verification/sections/445-records/source-review.json',{'base_commit':BASE,'changed_or_new_sources':{n:pin(n)for n in sources},'application_source_files':538,'new_application_modules':0,'REA_scope':'Complete Python source reviewed directly under REA skill; no new REA invocation or whole-program conclusion.','implementation':'Exact existing enum/name qualification distinguishes actual map types from other origins; node clicks carry exact pool/type into the existing read-only map. Original atlas is cropped once per type and decoded once per process, preserving all old node pixels.','external_reuse_priority':'External mature solutions take priority over internal component reuse. This section did not integrate external production code; independent MaaFw static-image experiment is recorded separately, not counted as production reuse.','defenses':'No broad try/catch, generic recovery or low-probability defensive layer. Existing source/type/private admission stays.','mechanism_or_OCR_changed':False,'whole_program_or_video_complete':False})
write('verification/sections/445-records/failure-disposition.json',{'initial_unit':'verification/sections/445-initial-unit-observation/failure.json','native_first':'verification/sections/445-native-source-nodes/window.json','native_first_picture_issue':'Extra screenshot reopened the map after the helper restored temporary state, producing an empty-map picture. Actual preceding interaction passed.','native_picture_repair':'Capture the real owned map widget while the temporary map remains installed; preserve first picture and capture source.','external_probe_failures':['verification/sections/445-maafw-probe/failure.json','verification/sections/445-maafw-probe-final/failure.json','verification/sections/445-maafw-static-controller/failure.json','verification/sections/445-maafw-matrix/failure.json'],'originals_retained':True,'no_product_acceptance_weakened':True})
external=read('verification/sections/445-maafw-matrix-final/results.json');assert len(external['rows'])==12 and not external['real_controllers_or_actions']and not external['production_integrated']
assert all(r['matches_expected']for r in external['rows']if r['detector']=='SIFT')
assert sum(not r['matches_expected']for r in external['rows']if r['detector']=='AKAZE')==1
assert sum(not r['matches_expected']for r in external['rows']if r['detector']=='ORB')==2
root=R/'.cache/external-solutions-445';repos=read('.cache/external-solutions-445/inventory.json')
write('verification/sections/445-records/external-source-review.json',{'priority':'Mature external solutions before internal reuse; requirements and AGENTS updated.','repositories':[{'repository':row['repository'],'commit':row['commit'],'readme_license_files':row['readme_license_files']}for row in repos],'selected_source_file_sha256':{p.name:sha256(p.read_bytes()).hexdigest()for p in root.glob('*.py')},'wheel':{k:v for k,v in read('.cache/external-solutions-445/wheel.json').items()if k!='files'},'runtime_Python_bindings_sha256':{n:sha256((root/'runtime/maa'/n).read_bytes()).hexdigest()for n in('tasker.py','controller.py','pipeline.py','define.py')},'checkout_and_binary_artifact_pinned_independently_not_assumed_same_build':True,'licenses':{'MaaFramework':'LGPL-3.0 at LICENSE.md','PyQt-Fluent-Widgets':'README says GPLv3 for non-commercial projects, commercial license for commercial use'},'project_environment_changed':False,'runtime_isolated_in_cache':True,'runtime_evidence':'verification/sections/445-maafw-matrix-final/results.json','mature_external_production_code_adopted':False,'not_completed_recognition_replacement':True})
oldpath=R/'.cache/item445-before-selectors.py';oldpath.write_bytes(subprocess.check_output(['git','show',BASE+':scripts/verify_full_available.py']))
old=runpy.run_path(str(oldpath))['maintained_selectors']();new=runpy.run_path(str(R/'scripts/verify_full_available.py'))['maintained_selectors']()
assert len(old)==728 and len(new)==729 and new[:len(old)]==old
write('verification/sections/445-records/selector-prefix.json',{'previous_count':728,'current_count':729,'all_previous_order_preserved':True,'appended':list(new[len(old):]),'registered_not_full_suite_executed':True})
save('research/source-nodes-445/README.md',f'''# 第445节 + {title}

基线{BASE}。项目原片158秒的物品卡用图标区分取得节点。本节把原先同列的地图节点与其它来源分开：只有已核对的枚举/中文名对应才列入“对应地图节点”，林间代步、流窜的居民及仅有来源名称的记录保留在“其它取得来源”。不猜图标或地图位置，不删原来源、池、统计、条件或资料范围。

明确节点卡可点击或键盘直接打开助手地图并筛选对应类型；有同类记录时标在对应位置，未记录不补造。原查池、展开条件、独立地图按钮、清除筛选和刷新保持。来源失效拒绝旧身份跳转；打开地图关闭挡住它的物品目录。不操作游戏、不自动选路、不将来源当本局实际掉落。

地图与来源卡共用原图集裁切，缓存从每个地图实例移到共享图像入口，图集每进程解码一次，所有原节点图片逐像素保持；无新模型、图片、依赖或应用模块进入生产，不称全部提速或净减代码。最终70项不同相关检查通过，25项当前/18项旧436原生范围分别通过；当前两张及旧436图逐张查看。第一张地图附图在恢复临时状态后重新打开而为空，已改为状态恢复前捕获真实地图，原图与脚本保留。动态旧源码测试遗漏__file__的夹具失败保留，产品资格未放宽。

用户明确“优先复用外部成熟方案”，已写入AGENTS、项目要求与实现路线，原“内部整合首选”判断已修正。下面的外部试验与本节产品功能分开，不以内部组件复用冒充已采用他人方案。

## 外部成熟方案核查与实际试验

先克隆并读README/许可，再定向读源码。MaaFramework固定b176dd8883c19fa1a46e1aa3cb553b0808176347：[README](https://github.com/MaaXYZ/MaaFramework/blob/b176dd8883c19fa1a46e1aa3cb553b0808176347/README.md)、[许可](https://github.com/MaaXYZ/MaaFramework/blob/b176dd8883c19fa1a46e1aa3cb553b0808176347/LICENSE.md)、[识别协议](https://github.com/MaaXYZ/MaaFramework/blob/b176dd8883c19fa1a46e1aa3cb553b0808176347/docs/en_us/3.1-PipelineProtocol.md)。实际读Python Tasker/Context/Resource/Controller、类型和协议；提供直接对已有图像识别的接口，适合进一步比较替换手写分流/定位流程。主分支源码与下述发布二进制独立固定，不假定同一次构建。

MaaFw5.14.3 Windows轮子及StrEnum0.4.15只解压到.cache隔离目录，未改项目虚拟环境或打包第三方库。首轮缺StrEnum，补齐后发现发布轮子没有MaaDbgControlUnit.dll；按其CustomController接口只提供静态公开图像，所有输入方法拒绝，实际识别跑通。自己两处启动脚本的复用目录和不存在帧名错误也分别保留，不能称外部库故障。没有绑定真实游戏或执行action/post_task。

默认SIFT按Horizontal选取位置，原图选中了错误候选；按官方协议改为Score排序及20匹配点候选参数后，原图、0.75倍缩放图、另一张无目标公开页面与空白四例符合预期。AKAZE缩放正例漏检，ORB两个正例漏检。该阈值使用过先前同图证据，不是独立训练/验收；两张公开视频和派生图不代表全面准确率。SIFT单次约278–510ms、AKAZE127–209ms、ORB22–69ms，只属此次CPU单模板调用，不与现有完整页面流程作等价速度比较。更快不等于适用，不直接替换生产。

PyQt-Fluent-Widgets固定6b9c646ce107660f66d20cec8af967c2c8d79764：[README](https://github.com/zhiyiYo/PyQt-Fluent-Widgets/blob/6b9c646ce107660f66d20cec8af967c2c8d79764/README.md)、[许可](https://github.com/zhiyiYo/PyQt-Fluent-Widgets/blob/6b9c646ce107660f66d20cec8af967c2c8d79764/LICENSE)、[布局实现](https://github.com/zhiyiYo/PyQt-Fluent-Widgets/blob/6b9c646ce107660f66d20cec8af967c2c8d79764/qfluentwidgets/components/layout/flow_layout.py)。实际读自适应布局示例与实现，README列PySide6包；本次源码默认分支为PyQt5。README采用GPLv3/商业授权安排，不能把可读源码当任意可复制；Fluent整套风格也不自动等于参考视频。未安装或复制到生产；保留后续明确许可与视频组件适配比较，不因内部已有控件就认定外部方案无价值。

下一步优先对MaaFramework的多页面、文字/数字、实际连续输入和资源/识别耗时进行与原流程等条件比较，再决定替换范围。当前仅试验，OCR未完成替换；729选择器登记保留前728次序，未跑全量，下次完整455。测试小窗更新可见响应，启动六私人路径保持；整批摘要另存，不回滚或上传私人内容。完整视频/程序、其余密度/滚动条外观及P3/P2/P1仍未完成。

[本节回执](../../verification/sections/445.json)。
''')
entry=f'''<!-- player-section-445 -->
## 第445节 + {title}

准确地图节点与其它取得来源分组，图标与地图共用原图，节点卡直接打开对应类型与位置，池/条件/统计保持，不认作本局掉落。70项相关检查、25项当前和18项旧436原生范围分别通过；测试窗更新，启动私人六路径保持。

外部成熟方案优先已写入要求；实际克隆固定并读MaaFramework与PyQt-Fluent-Widgets源码/许可，隔离MaaFw静态图像识别已跑通，默认误选、缩放漏检和自有启动错误保留。尚未接入生产，不以内部复用或试验成功冒充替换完成。729选择器旧序保持，下次完整455；全程序/视频与P3/P2/P1未完成。回执verification/sections/445.json。

'''
for n in('WORK_IN_PROGRESS.md','PROJECT_COMPLETED.md'):
 text=(R/n).read_text('utf8')
 if n=='WORK_IN_PROGRESS.md':text=text[text.index('<!-- player-section-444 -->'):]
 save(n,entry+text)
for n in('PROGRAM_REVIEW.md','IMPLEMENTATION_STRATEGY.md'):
 save(n,(R/n).read_text('utf8')+'\n[第445节来源节点与外部方案核查](research/source-nodes-445/README.md)补准确节点分组、图标和地图入口；外部成熟方案优先已明确，MaaFw隔离纯图像试验跑通但有配置误选/漏检，不冒称已替换识别。其余完整覆盖/视频与全程序仍待验。\n')
n='PROJECT_REQUIREMENTS.md';text=(R/n).read_text('utf8').replace('当前功能第444节','当前功能第445节',1)
marker='## 商店信息读取与历史';assert marker in text
save(n,text.replace(marker,'取得来源须区分已明确对应的地图节点和其它来源；只有核对过的节点枚举及中文名才显示对应图标和地图入口。跳转只查看已有同类记录或候选，不表示当前可达或会掉落；其它来源保留条件和统计，不猜节点。\n\n'+marker,1))
n='VIDEO_PARITY.md';save(n,(R/n).read_text('utf8')+'\n[第445节](research/source-nodes-445/README.md)为来源卡补准确节点图标、直接对应地图入口，并分开其它取得来源；当前仍有说明密度/滚动条与完整外观缺口，不冒称视频全部一致。外部成熟方案优先，MaaFw仅隔离候选试验，未替换生产。\n')
n='PROJECT_PROGRESS.md';text=(R/n).read_text('utf8');text=text.replace('按入口单次校验、单次逻辑不过度抽函数及新增低概率防御先征求同意的规则回顾已有实现；','优先评估外部成熟代码的适用性、许可和本机接入，MaaFramework仍缺多页面/字段/连续输入的等条件验证与实际替换；按入口单次校验、单次逻辑不过度抽函数及新增低概率防御先征求同意的规则回顾已有实现；',1);save(n,text)
receipt={'section':445,'kind':'functional_section','title':title,'new_capability':'来源区分准确地图节点与其它取得途径；共用原节点图，点击/键盘直接对应地图类型和位置，池/条件/统计不变。外部成熟方案优先要求与独立候选试验一并保存。','limitations':'外部MaaFw仅隔离静态图像试验，未接入生产；其它窗口、当前资料适用性、真实连续识别与P3/P2/P1及全视频/全程序仍未完成，不声称提速。','necessary_validation':pin('verification/sections/445-related-final/process.json'),'unit_tests_run':70,'native_windows_scopes':{'source_nodes':{'receipt':'verification/sections/445-native-source-nodes-final/window.json','unique_checks':25},'old436':{'receipt':'verification/sections/445-native-source-map-436/window.json','unique_checks':18}},'actual_local_test_window':pin('verification/sections/445-live-window/window.json'),'source_review':pin('verification/sections/445-records/source-review.json'),'source_sha256':{n:sha256((R/n).read_bytes()).hexdigest()for n in sources},'full_suite_rerun':False,'old_full440_proves_current_source':False,'goal_active':True,'whole_program_or_video_complete':False,'at_UTC':datetime.now(timezone.utc).isoformat()}
write('verification/sections/445.json',receipt)
cp=read('DEVELOPMENT_CHECKPOINT.json');assert cp['completed_sections']==444 and cp['next_section']==445
cp['completed_sections']=445;cp['next_section']=446;cp['sections'].append({'number':445,'completion_ref':'player-section-445','topic':title,'verification':'verification/sections/445.json'})
cp['current_section_save']={'section':445,'verification':'verification/sections/445.json','scope':'current_functional_section','binding':'enclosing_commit'};cp['last_verified_cloud_save']['scope']='previous_functional_section'
cp['current_section_validation']={'section':445,'receipt':'verification/sections/445.json','necessary_checks':70,'native_scopes':{'source_nodes':25,'old436':18},'full_validation_rerun':False}
cp['current_batch'].update(completed_sections=445,next_section=446,next_section_started=False,receipt='verification/sections/445.json',scope='Whole-program review and complete video parity remain active. Functional445 exact source-node grouping/icons/map navigation completed in verified scope; external MaaFw remains an isolated candidate.446 not started.')
cp['next_action']='优先继续外部成熟方案适配核查，先做MaaFramework多页面/字段/连续输入及原流程等条件比较，再决定替换；保留本节准确来源节点与地图入口。其余P3图文/数据/视频与存量实现约束、P2/P1仍未完成。446未启动，下次完整455。'
if isinstance(cp.get('player_feature_sections'),list):cp['player_feature_sections'].append(445)
assert cp['functional_sections_since_latest_requirement'][-1]==444;cp['functional_sections_since_latest_requirement'].append(445)
save('DEVELOPMENT_CHECKPOINT.json',json.dumps(cp,ensure_ascii=False,indent=2)+'\n')
idx=runpy.run_path(str(R/'scripts/update_cloud_index.py'));idx['update'](R);assert idx['validate_delivery'](R,cp)['current_section']==445
write('verification/sections/445-records/final-audit.json',{'passed':True,'functional_section':445,'necessary_distinct_tests':70,'native_scopes_separate':[25,18],'ordered_selectors':729,'active_functional_list_includes445':True,'requirements':pin('PROJECT_REQUIREMENTS.md'),'index':pin('CLOUD_INDEX.json'),'section_receipt':pin('verification/sections/445.json'),'current_full_rerun':False,'goal_active':True,'whole_program_or_video_complete':False})
(B/'record-source.py').write_bytes(Path(__file__).read_bytes())
files={}
for folder in(R/'verification/sections').glob('445-*'):
 if folder.is_dir():files.update({p.relative_to(R).as_posix():{k:v for k,v in pin(p.relative_to(R)).items()if k!='receipt'}for p in folder.rglob('*')if p.is_file()and p.name!='archive-manifest.json'})
files['verification/sections/445.json']={k:v for k,v in pin('verification/sections/445.json').items()if k!='receipt'}
write('verification/sections/445-records/archive-manifest.json',{'kind':'explicit_public_archive_no_private_inputs_or_expected_values','files':files})
print(json.dumps({'passed':True,'section':445,'necessary_distinct_tests':70,'native_scopes_separate':[25,18],'public_archive_files':len(files),'whole_goal_complete':False}))
