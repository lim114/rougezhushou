from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import json,subprocess,difflib,runpy,sys,re
R=Path.cwd();sys.path.insert(0,str(R/'scripts'));BASE='8e762f788408cd49ed1ab3769acfcf67d0cf302b';B=R/'verification/sections/444-records'
title='点击查看并固定藏品来源与紧凑条目阅读'
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
checks=read('verification/sections/444-related-final/results.json')
assert checks['passed']and checks['tests_run']==73 and not checks['failed']and not checks['errors']and not checks['skipped']and not checks['forbidden_external_calls']
assert read('verification/sections/444-related-final/process.json')['actual_observed_exit']==0
ids=re.findall(r'^test_\w+ \(([^)]+)\)',(R/'verification/sections/444-related-final/stderr.txt').read_text('utf8'),re.M);assert len(ids)==len(set(ids))==73
native=read('verification/sections/444-native-item-reading/window.json');assert native['passed']and native['unique_checks']==29 and not native['source_drift']and not any(native['external_operation_attempts'].values())
assert read('verification/sections/444-native-item-reading/process.json')['actual_observed_exit']==0
for n,digest in native['source_sha256_after'].items():assert sha256((R/n).read_bytes()).hexdigest()==digest,n
live=read('verification/sections/444-live-window/window.json');assert live['passed']and live['private_six_paths_unchanged']
status=read('.cache/item-reading-444-live-status.json');assert status['toolbar_visible']and status['elapsed_since_launch']>4
B.mkdir(exist_ok=False)
write('verification/sections/444-native-item-reading/root-image-review.json',{'two_actual_final_PNGs_viewed':True,'images':native['screenshots'],'appearance_does_not_replace_29_actual_interaction_checks':True,'isolated_widgets_not_live_game_or_complete_video_parity':True})
write('verification/sections/444-live-window/desktop-review.json',{'Windows_mcp_region':[1716,1164,2130,1218],'actual_toolbar_viewed':True,'visible_responding_and_Qt_timer_advanced':True,'startup_six_private_paths_unchanged':True,'not_a_live_game_accuracy_claim':True})
before=read('.cache/item-reading-444-before.json')['private'];changed=[n for n,v in before.items()if(sha256((R/n).read_bytes()).hexdigest()if(R/n).is_file()else None)!=v]
write('verification/sections/444-records/private-scope.json',{'whole_batch_private_six_unchanged':not changed,'changed_paths_if_any':changed,'change_origin_not_inferred':bool(changed),'startup_six_paths_unchanged':True,'private_contents_hashes_images_or_expected_values_published':False,'private_backup_restore_or_rollback':False})
sources=['rouge/expansion_view.py','rouge/player_acceptance.py','rouge/player_compact.py','rouge/player_inventory.py','rouge/player_item_acceptance.py','scripts/player_ui_verification.py','scripts/verify_full_available.py','tests/test_item_reading_444.py']
for n in('rouge/player_inventory.py','rouge/player_compact.py','rouge/expansion_view.py'):assert (R/'research/item-reading-444'/('before-'+Path(n).name)).read_bytes()==subprocess.check_output(['git','show',BASE+':'+n])
write('verification/sections/444-records/source-review.json',{'base_commit':BASE,'changed_or_new_sources':{n:pin(n)for n in sources},'application_source_files':len([p for p in(R/'rouge').rglob('*')if p.suffix in('.py','.cjs')]),'new_application_modules':0,'REA_scope':'REA skill routes complete Python source to direct source/runtime review. No new REA invocation or whole-program conclusion.','reuse':'Existing ItemHoverCard, inventory exact IDs, source pools and source fingerprint refresh; existing Qt QDialog.finished and full exact reference lookup; existing relic_icon and labelled picture provenance. No new dependencies, models, downloads, data source or state store.','simplification':'Use existing source card for explicit pinned reading, keep full lookup separate; close the obscuring inventory on successful full lookup. Hide no-map placeholder instead of building a second item reader. No new generic dispatcher or recovery framework. Net source lines increase for new capability.','ingress':'Reuse existing refresh/source admission. New source action validates selected item once; full action uses exact existing lookup result. No broad new try/catch or low-probability defense.','temporary_hide_vs_close':'QDialog.finished dismisses on real close; toolbar temporary hide preserves pinned reading for restoration.','mechanisms_or_OCR_algorithms_changed':False,'source_links':['https://doc.qt.io/qtforpython-6/PySide6/QtWidgets/QDialog.html#PySide6.QtWidgets.QDialog.finished'],'whole_program_or_video_complete':False})
first=read('verification/sections/444-related/results.json');assert not first['passed']and first['tests_run']==73 and first['errors']==1
write('verification/sections/444-records/failure-disposition.json',{'original_failure':'verification/sections/444-related/results.json','actual_exit':read('verification/sections/444-related/process.json')['actual_observed_exit'],'cause':'New group-reference test selected a LEGACY item while default item-kind filter was RELIC. StopIteration was a fixture precondition error, not missing catalog data.','repair':'Explicitly choose all item kinds before exact lookup; original test source/logs retained. No product filter, identity qualification or acceptance weakened.','final':'verification/sections/444-related-final/results.json'})
oldpath=R/'.cache/item444-before-selectors.py';oldpath.write_bytes(subprocess.check_output(['git','show',BASE+':scripts/verify_full_available.py']))
old=runpy.run_path(str(oldpath))['maintained_selectors']();new=runpy.run_path(str(R/'scripts/verify_full_available.py'))['maintained_selectors']()
assert len(old)==727 and len(new)==728 and new[:len(old)]==old
write('verification/sections/444-records/selector-prefix.json',{'previous_count':727,'current_count':728,'all_previous_order_preserved':True,'appended':list(new[len(old):]),'registered_not_full_suite_executed':True})
save('research/item-reading-444/README.md',f'''# 第444节 + {title}

基线{BASE}。对照项目原片2:35–2:57：藏品来源保持紧凑卡片，完整图鉴与图文筛选另行打开。本轮实际查看原片158秒与两张最终窗口原图；不把截图相似度当成交互或完整视频一致性。

此前目录按钮仅显式打开大窗口，并非跳转错误。新增“查看并固定取得来源”复用原ItemHoverCard、准确物品ID、全部已列池和条件阅读，点击或键盘均可打开；原“完整条目与相关查询”保留，成功后关闭挡在正文上方的目录。关闭目录同步清除其来源卡；快捷键暂时隐藏仍保留固定状态，恢复显示原条目。复用[Qt QDialog.finished](https://doc.qt.io/qtforpython-6/PySide6/QtWidgets/QDialog.html#PySide6.QtWidgets.QDialog.finished)区分真实关闭与暂时隐藏，不新增状态框架或异常吞没。

通用阅读器复用已有准确藏品/零件图片，分组参考图继续明确注明未核验独立图样；无地图条目不占地图空白，真实关卡原图保持，声明有图但读取失败时保留解释。刷新、切换条目、返回、来源失效与恢复的准确身份/选择边界保持。数据目录、统计口径、计算与OCR没有变化，没有新图片下载、模型、依赖或应用模块；新增功能增加代码，不称代码净减。

最终73项不同必要检查通过，0失败/错误/跳过；29项当前原生唯一检查通过，两张最终图逐张查看。新增分组图测试首轮误用默认收藏品过滤，改为明确总览后通过；原测试与失败日志保留，未修改产品筛选或放宽来源核验。既有图鉴、物品来源、延迟填充、原地图和全条目导航相关检查保留。728选择器追加且前727顺序不变，仅登记不等于全量执行；下次完整455，full440仅证明旧冻结源码。

测试窗口已更新并由Windows-mcp实际查看，可见响应且Qt计时器推进，启动六私人路径保持；全批变化摘要另见private-scope.json，不推断原因、不回滚旧局。不操作游戏、不发送聊天、不上传私人内容。独立目录点击不是游戏画面悬停验收；完整视频外观/交互、其余窗口与连续识别和P3/P2/P1仍未完成。

[本节回执](../../verification/sections/444.json)。
''')
entry=f'''<!-- player-section-444 -->
## 第444节 + {title}

目录可点击或键盘打开并固定原来源卡，完整条目保持独立入口且关闭遮挡目录；真实关闭清卡，暂时隐藏/恢复保留阅读。完整条目复用准确物品图片及分组图说明，无地图不留空白，有地图及读取失败解释保持。

73项不同必要检查、29项原生唯一检查通过，两张最终原图已看；分组图测试默认筛选前置错误及原失败保留。测试小窗更新可见响应、启动六私人路径保持，728选择器旧序保持，未重跑全量。独立目录不替代游戏悬停，完整程序/视频与P3/P2/P1未完成，下次完整455。回执verification/sections/444.json。

'''
for n in('WORK_IN_PROGRESS.md','PROJECT_COMPLETED.md'):
 s=(R/n).read_text('utf8')
 if n=='WORK_IN_PROGRESS.md':s=s[s.index('<!-- deferred-reference-review-20261031:start -->'):]
 save(n,entry+s)
for n in('PROGRAM_REVIEW.md','IMPLEMENTATION_STRATEGY.md'):
 save(n,(R/n).read_text('utf8')+'\n[第444节条目阅读回顾](research/item-reading-444/README.md)复用来源卡提供明确点击/键盘入口，保留全条目并消除遮挡和无地图空白；已有图片与分组标注共用。其它流程、完整视频与全程序整改仍未完成。\n')
n='PROJECT_REQUIREMENTS.md';s=(R/n).read_text('utf8').replace('当前功能第443节','当前功能第444节',1)
marker='## 商店信息读取与历史';assert marker in s
save(n,s.replace(marker,'目录中的物品应能直接打开并固定来源卡，同时保留明确的完整条目入口；进入完整阅读时关闭遮挡的目录。暂时隐藏不丢固定阅读，真实关闭清除附属卡。完整条目复用准确图片，分组参考须就地说明；无地图不留占位，有图读取失败仍解释，不借其它物品图或地图。目录操作不能替代游戏画面悬停验收。\n\n'+marker,1))
n='VIDEO_PARITY.md';s=(R/n).read_text('utf8');target='尚不算游戏悬停完成。交换提供物集合与奖励池分开。';assert target in s
save(n,s.replace(target,'第444节补明确的点击/键盘固定来源入口与完整条目分流，关闭遮挡目录、保留暂时隐藏阅读；完整条目复用图片并去无地图空白。尚不算游戏悬停完成。交换提供物集合与奖励池分开。',1))
# Todo contains only unresolved scope: no completed-section append here.
n='PROJECT_PROGRESS.md';s=(R/n).read_text('utf8');s=s.replace('仍需核对其它资料窗口、笔记字体、间距','仍需核对其它资料窗口的图文排版与阅读入口、笔记字体、间距',1);save(n,s)
receipt={'section':444,'kind':'functional_section','title':title,'new_capability':'目录点击/键盘固定复用的准确来源卡；完整条目分流关闭遮挡目录，真实关闭清卡而暂时隐藏保留；完整阅读器复用物品图片和分组标注、无地图不占位。','limitations':'目录操作不替代游戏悬停；其它窗口、完整视频外观/交互、连续真实识别与P3/P2/P1仍未完成。未修改数值/OCR或声称提速。','necessary_validation':pin('verification/sections/444-related-final/process.json'),'unit_tests_run':73,'native_windows_scopes':{'item_reading':{'receipt':'verification/sections/444-native-item-reading/window.json','unique_checks':29}},'actual_local_test_window':pin('verification/sections/444-live-window/window.json'),'source_review':pin('verification/sections/444-records/source-review.json'),'source_sha256':{n:sha256((R/n).read_bytes()).hexdigest()for n in sources},'full_suite_rerun':False,'old_full440_proves_current_source':False,'goal_active':True,'whole_program_or_video_complete':False,'at_UTC':datetime.now(timezone.utc).isoformat()}
write('verification/sections/444.json',receipt)
cp=read('DEVELOPMENT_CHECKPOINT.json');assert cp['completed_sections']==443 and cp['next_section']==444
cp['historical_implementation_maintenance_before444']=cp.pop('current_maintenance_save')
cp['completed_sections']=444;cp['next_section']=445;cp['sections'].append({'number':444,'completion_ref':'player-section-444','topic':title,'verification':'verification/sections/444.json'})
cp['current_section_save']={'section':444,'verification':'verification/sections/444.json','scope':'current_functional_section','binding':'enclosing_commit'};cp['last_verified_cloud_save']['scope']='previous_functional_section'
cp['current_section_validation']={'section':444,'receipt':'verification/sections/444.json','necessary_checks':73,'native_scopes':{'item_reading':29},'full_validation_rerun':False}
cp['current_batch'].update(completed_sections=444,next_section=445,next_section_started=False,receipt='verification/sections/444.json',scope='Whole-program review and complete video parity remain active. Functional444 exact source reading and picture-backed full reader completed in verified scope;445 not started.')
cp['next_action']='继续全程序及视频逐链路回顾，推进其余P3地图/节点/物品和图文阅读、准确条件与真实连续读取；OCR同步优化，比较轻量定位等候选，存量三条规则继续整改。完整视频/全程序与P3/P2/P1仍未完成。445未启动，下次完整455。'
if isinstance(cp.get('player_feature_sections'),list):cp['player_feature_sections'].append(444)
assert cp['functional_sections_since_latest_requirement'][-1]==443;cp['functional_sections_since_latest_requirement'].append(444)
save('DEVELOPMENT_CHECKPOINT.json',json.dumps(cp,ensure_ascii=False,indent=2)+'\n')
idx=runpy.run_path(str(R/'scripts/update_cloud_index.py'));idx['update'](R);assert idx['validate_delivery'](R,cp)['current_section']==444
write('verification/sections/444-records/final-audit.json',{'passed':True,'functional_section':444,'necessary_distinct_tests':73,'native_scopes_separate':[29],'ordered_selectors':728,'active_functional_list_includes444':True,'requirements':pin('PROJECT_REQUIREMENTS.md'),'index':pin('CLOUD_INDEX.json'),'section_receipt':pin('verification/sections/444.json'),'current_full_rerun':False,'goal_active':True,'whole_program_or_video_complete':False})
(B/'record-source.py').write_bytes(Path(__file__).read_bytes())
files={}
for folder in(R/'verification/sections').glob('444-*'):
 if folder.is_dir():files.update({p.relative_to(R).as_posix():{k:v for k,v in pin(p.relative_to(R)).items()if k!='receipt'}for p in folder.rglob('*')if p.is_file()and p.name!='archive-manifest.json'})
files['verification/sections/444.json']={k:v for k,v in pin('verification/sections/444.json').items()if k!='receipt'}
write('verification/sections/444-records/archive-manifest.json',{'kind':'explicit_public_archive_no_private_inputs_or_expected_values','files':files})
print(json.dumps({'passed':True,'section':444,'necessary_distinct_tests':73,'native_scopes_separate':[29],'public_archive_files':len(files),'whole_goal_complete':False}))
