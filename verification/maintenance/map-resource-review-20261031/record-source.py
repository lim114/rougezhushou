from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
from collections import Counter
import ast,ctypes,difflib,json,re,runpy,subprocess,sys,time
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts'),str(R/'.cache/305-window-tooldeps')]
BASE='bb9647cf450eea009a2b37e4fb7937ac2f67fc0e';B=R/'verification/maintenance/map-resource-review-20261031';prefix=B.relative_to(R).as_posix()+'/'
def read(n):return json.loads((R/n).read_bytes())
def pin(n):
 p=R/n;raw=p.read_bytes();return {'path':p.relative_to(R).as_posix(),'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}
def write(n,v):(R/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf8')
def text(n,value):
 p=R/n
 if not p.exists():p.parent.mkdir(parents=True,exist_ok=True);p.write_text(value,'utf8');return
 old=p.read_bytes().decode('utf8').splitlines(keepends=True);new=value.splitlines(keepends=True);out=list(new)
 for a,b,num in difflib.SequenceMatcher(None,[s.rstrip('\r\n')for s in old],[s.rstrip('\r\n')for s in new],autojunk=False).get_matching_blocks():
  for i in range(num):out[b+i]=old[a+i]
 p.write_bytes(''.join(out).encode('utf8'))
def old(n):return subprocess.check_output(['git','show',BASE+':'+n])
assert subprocess.check_output(['git','rev-parse','HEAD']).decode().strip()==BASE
changed=['rouge/run_state.py','rouge/player_floor_resources.py'];before=['research/map-resource-review-20261031/before-run-state.py','research/map-resource-review-20261031/before-player-floor-resources.py']
for n,p in zip(changed,before):assert old(n)==(R/p).read_bytes()
unchanged=['rouge/player_replay_nodes.py','rouge/player_replay.py','rouge/player_history_store.py','rouge/map_recognition.py','rouge/recipient_state.py','rouge/training_view.py','rouge/player_team.py','rouge/app.py','PROJECT_REQUIREMENTS.md']
for n in unchanged:assert old(n)==(R/n).read_bytes(),n
assert not subprocess.check_output(['git','diff','--name-only',BASE,'--','rouge/data','research/runtime-reference-loaders-20261031']).strip()
def methods(raw,name):
 c=next(n for n in ast.parse(raw).body if isinstance(n,ast.ClassDef)and n.name==name)
 return {n.name:ast.dump(n,include_attributes=False)for n in c.body if isinstance(n,ast.FunctionDef)}
a=methods(old(changed[0]),'RunState');b=methods((R/changed[0]).read_bytes(),'RunState');assert a.keys()==b.keys()and all(a[n]==b[n]for n in a if n!='apply')
def functions(raw):return {n.name:ast.dump(n,include_attributes=False)for n in ast.parse(raw).body if isinstance(n,ast.FunctionDef)}
a=functions(old(changed[1]));b=functions((R/changed[1]).read_bytes());assert a.keys()==b.keys()and all(a[n]==b[n]for n in a if n!='record_snapshot')
assert methods(old(changed[1]),'FloorResourcesPage')==methods((R/changed[1]).read_bytes(),'FloorResourcesPage')
suite=read(prefix+'tests-current/results.json');native=read(prefix+'native/window.json');failed=read(prefix+'tests/results.json');comparison=read(prefix+'tests-current/comparisons.json')['comparisons']
assert suite['passed']and suite['tests_run']==105 and not suite['skipped']and not suite['forbidden_external_calls'];assert failed['tests_run']==37 and failed['failed']==2 and failed['errors']==0
assert native['passed']and native['unique_checks']==31 and not native['source_drift']and not any(native['external_operation_attempts'].values())
for folder in ['tests-current','native']:assert read(prefix+folder+'/process.json')['actual_observed_exit']==0
assert read(prefix+'tests/process.json')['actual_observed_exit']==1
def names(n):return re.findall(r'^test_\w+ \(([^)]+)\)',(R/n).read_text('utf8'),re.M)
ids=names(prefix+'tests-current/stderr.txt');assert len(ids)==len(set(ids))==105
prior_log='verification/maintenance/run-lifecycle-review-20261031/tests/stderr.txt';prior=names(prior_log);duplicates={k:v for k,v in Counter(prior).items()if v>1};assert len(prior)==89 and len(set(prior))==83 and len(duplicates)==6 and all(v==2 for v in duplicates.values())
write(prefix+'prior-count-correction.json',{'supersedes_count_claim_only':'verification/maintenance/run-lifecycle-review-20261031/summary.json','original_raw_receipts_unchanged':True,'actual_original_verbose_log':pin(prior_log),'original_executions':89,'original_distinct_test_ids':83,'duplicate_test_ids':duplicates,'cause':'Directly imported TestCase class was discovered a second time by unittest module loading. Replaced class import with module import; final105 current test IDs proven unique. Test assertions not removed.','original_83_distinct_results_passed':True,'current_revalidation_included_same_prior_scope':True})
for n in changed:assert native['source_sha256_after'][n]==pin(n)['sha256']
(B/'native/verifier-source.py').write_bytes((R/'scripts/verify_map_resource_review.py').read_bytes())
write(prefix+'source-review.json',{'baseline_commit':BASE,'changed_source':[pin(n)for n in changed],'own_prior_source':[pin(n)for n in before],'all_other_RunState_methods_AST_unchanged':True,'other_snapshot_functions_and_FloorResourcesPage_AST_unchanged':True,'unchanged_projections_archive_models_state_and_requirements':[pin(n)for n in unchanged],'old_new_reproduction':comparison,'defect':'Actual accepted one-frame map+gold7 appended resource snapshot after both map rows, so prefix replay showed unknown despite accepted same-frame resource.','fix':'Pass current apply history_start into existing snapshot writer; after existing acceptance and dedup checks insert before only this observation new same-zone map-reading rows. Layout ownership stays before snapshot. Previous prefix unchanged even if two applies share timestamp.','preserved_boundaries':'No old history reorder/repair, no lookahead from later timestamps, no new event schema/UUID, no current resource fill, no reward/floor-entry/outcome claim. State save/reset and original source qualification intact.','first_test_failure':'Reload fixtures lacked required grid and source fields of actual matched game-map shape. Fixed test fixture; original readonly shape guard unchanged. First failed test/source/logs retained. Imported helper also duplicated six existing tests; corrected import and counter proof separate.','code_size_or_speed_improvement_claimed':False,'REA_scope':'Complete Python source reviewed directly per REA skill; no new REA invocation. Earlier actual bridge/toolbar analysis separate.','whole_program_complete':False})
public=read('.cache/public-map-git-candidates-20261031/summary.json');assert len(public['repositories'])==3 and all(not r['fetched_code_installed_or_executed_or_copied_to_application']for r in public['repositories'])
public['decision']='Reviewed README/tree and one root GPL license only, not complete simulator implementations. No clear license found in checked Tomimi/stage-viewer metadata/named-file scope; no claim that all file headers were inspected. AKSimulator GPLv3 and three.js/unfinished roadmap do not establish current CN/black forest compatibility. Keep existing local Qt reader; candidates need broader source/data/license/integration validation before replacing it.'
write(prefix+'public-reuse-review.json',public)
images=[pin(p.relative_to(R))for p in sorted((B/'native').glob('*.png'))];assert len(images)==5
write(prefix+'image-review.json',{'reviewer':'/root','all_five_final_originals_individually_loaded_with_view_image':images,'scope':'First map row gold7, later append keeps selected7, later row99, local archive retains7 and final archive view. Public generated inputs, not actual game captures.','whole_video_parity_claimed':False})
live=read(prefix+'live-window/window.json');assert live['passed']and live['private_six_paths_unchanged']
import win32gui,win32process
for w in live['owned_windows']:assert win32gui.IsWindowVisible(w['hwnd'])and win32process.GetWindowThreadProcessId(w['hwnd'])[1]==w['pid']and not ctypes.windll.user32.IsHungAppWindow(w['hwnd'])
a=read('.cache/map-resource-review-live-status.json');time.sleep(2.2);b=read('.cache/map-resource-review-live-status.json');assert b['toolbar_visible']and b['elapsed_since_launch']>a['elapsed_since_launch']
for n in changed:assert live['source_sha256_after'][n]==pin(n)['sha256']
write(prefix+'live-window/desktop-review.json',{'actual_windows_mcp_snapshot_called':True,'actual_image_viewed':True,'region':[1716,1164,2130,1218],'owned_window_visible_and_responding':True,'Qt_timer_advanced':True,'private_six_paths_unchanged_during_startup':True,'private_contents_or_hashes_published':False,'game_operated':False,'chat_sent':False})
title='地图复盘显示同次读取的资源，保留旧历史并纠正重复测试统计'
write(prefix+'summary.json',{'kind':'implementation_review_maintenance','title':title,'baseline_commit':BASE,'completed_sections':440,'functional_section_added':False,'implemented_scope_passed':True,'related_unique_tests':105,'actual_verbose_test_ids_unique':True,'native_unique_checks':31,'source_review':pin(prefix+'source-review.json'),'test_receipt':pin(prefix+'tests-current/results.json'),'first_failed_fixture_receipt':pin(prefix+'tests/results.json'),'prior_count_correction':pin(prefix+'prior-count-correction.json'),'public_reuse_review':pin(prefix+'public-reuse-review.json'),'native_receipt':pin(prefix+'native/window.json'),'image_review':pin(prefix+'image-review.json'),'live_window':pin(prefix+'live-window/desktop-review.json'),'application_review_complete':False,'video_parity_complete':False,'P3_complete':False,'P2_complete':False,'P1_complete':False,'full_validation_rerun':False,'full440_only_original_frozen_source':True,'private_data_included':False,'game_operated':False,'chat_sent':False,'publication_binding':'enclosing maintenance commit; ordinary push and actual remote/blob equality required'})
text('research/map-resource-review-20261031/README.md','''# 地图读取与同帧资源的历史归属回顾

实际用自有旧RunState和现有公共地图数据重放：同一输入包含准确地图与源石锭7，旧版先写位置/节点、最后写同帧资源快照，逐条前缀地图因而两行均显示资源未知。问题不是资源未读，而是当次已读事实的保存顺序。现沿用原快照验收和去重，传入本次apply开始的历史长度，将资源快照插入当前批次同区域第一条地图阅读之前；布局确认/切换仍在前。没有扫描未来时间、改写旧行、补造旧局、改事件格式或加新协议。相同时间戳的两次apply也只在各自新范围插入，旧选择索引不变。

八项新检查验证旧新复现、未来99不覆盖过去7、同时间戳批次分离、布局更换、无新资源不伪造本次快照、旧记录不追填、保存重启/归档以及实际Qt复盘保持选择。最终105项不同相关检查实际退出0、无跳过，执行前/日志后均确认身份无重复；包含上轮83项独立生命周期范围。原生31项通过，实际打开复盘和归档、鼠标选中首条/末条、刷新旧选择保留；五张最终原图逐张查看。没有游戏采样、实际游戏数值或结算主张。

第一轮新测试的匹配地图夹具漏了真实记录必需的grid和source，重启被原形状保护拒绝；修正夹具，未放宽校验，原两失败及源码保留。另核对上轮原89次执行只有83个不同检查，6项被直接导入的TestCase重复发现；当前改为模块导入，断言保留。原回执不改写，计数纠正见prior-count-correction.json；本轮第一轮37次/31不同也保留。不能用执行次数冒充独立覆盖。

## 公开项目替代方案核对

定向搜索并通过普通公共Git路径固定三个仓库，读取全路径清单及根README/许可文件，未安装、运行或复制其实现。GitHub API树请求遭匿名403限流后未重复该API，使用正常Git只读；私有/个人数据未发送。完整来源摘要在public-reuse-review.json。

- [Tomimi](https://github.com/tanch-p/tomimi-dev/tree/5d341e921628dd101004a561ef2d3553ebed1978)：与之前固定提交相同，README为Svelte5/SvelteKit2、Three.js/本地Spine；本轮元数据与命名路径范围没找到明确许可文件，不冒称所有源码头部已查或已授权复用。以前五文件片段审查仍不等于完整模拟器验收。
- [stage-viewer](https://github.com/Awedtan/stage-viewer/tree/11b18075e615b0b394b1a9ee52d82113424450ac)：README为重建/模拟关卡的在制个人项目，原始数据来源列YoStar；所查路径无许可命名文件，未验证当前国服与黑流树海适配。
- [AKSimulator](https://github.com/Sunsetra/AKSimulator/tree/e836b5a1317dd5585060159f10ee8238bbbd4072)：明确GPLv3，README为Three.js基础支持库，自动寻路/战斗仍列计划；这不证明当前数据或完整运行兼容。未审完其实现，也不把它当可直接接入Qt的已验证替代。

当前修复直接复用本项目快照、前缀投影、归档和Qt组件，比为此重写浏览器/引擎接入少一个未经验证的运行栈；这是限定范围的工程取舍，不是三个项目不可用或全网没有方案的结论。后续仍可扩大源码、许可与适配核对，不能只凭公开可读宣称已经复用。

本轮按REA技能直接审完整Python源码，无新REA调用；没有数值机制、数据/图片/运行声明变化或速度测量。实际项目测试小窗已更新，Qt计时推进、可见响应，启动六处私人路径保持，只公开布尔证明。功能440/未开441，源码536份；全程序、完整视频、P3/P2/P1仍未完成，识别最后，full440只适用旧冻结来源。
''')
# Correct mutable review prose, never rewrite the original raw receipts.
n='research/run-lifecycle-review-20261031/README.md';t=(R/n).read_text('utf8');assert '实际89项不同相关检查退出0'in t;t=t.replace('实际89项不同相关检查退出0','原89次执行对应83项不同相关检查（6项因导入重复运行），均退出0');t+='\n计数更正：本轮地图/资源回顾核对原verbose日志，修正TestCase直接导入造成的重复发现；原89次执行回执保留，独立范围为83项，全部纳入当前105项无重复检查复验。详见`../../verification/maintenance/map-resource-review-20261031/prior-count-correction.json`。\n';text(n,t)
n='PROGRAM_REVIEW.md';t=(R/n).read_text('utf8');t=t.replace('89项相关检查通过；未复现产品缺陷','83项不同检查通过（原89次含6重复，原件保留）；未复现产品缺陷');t+='\n[地图与资源归属回顾](research/map-resource-review-20261031/README.md)修正新读取同帧资源位于地图日志之后导致复盘缺值的问题，只调整当前批次新日志，旧前缀保持；105项不同检查/31项原生检查通过。核对三个公开仓库的固定树/README/许可候选，未引入未验实现；其余地图/资源/实机、机制和全程序仍未完成。\n';text(n,t)
for n in ['WORK_IN_PROGRESS.md','PROJECT_COMPLETED.md']:
 t=(R/n).read_text('utf8');t=t.replace('89项相关检查真实退出0，无跳过；未复现产品缺陷','原89次执行含83项不同检查，6项重复；原回执保持，计数本轮另证。独立范围通过，无跳过；未复现产品缺陷');text(n,t)
for n,addition in {
 'VIDEO_PARITY.md':'[地图同帧资源归属回顾](research/map-resource-review-20261031/README.md)修正实际接受地图与资源同次读取却在复盘首行显示未知的问题；旧记录不追填、后来数量不盖过去。105项不同检查/31项原生范围和五张原图覆盖，完整资源/地图记录及视频全部效果仍未完成。',
 'IMPLEMENTATION_STRATEGY.md':'[地图资源回顾](research/map-resource-review-20261031/README.md)用当前apply新日志边界复用已有同帧快照和历史前缀投影，修正顺序而不新造时间关联协议。另固定检查Tomimi/stage-viewer/AKSimulator的README树与许可范围，未完成当前国服/Qt适配或取得未明示授权，不把检索当实际复用；保留现有局外/本机架构。'
}.items():text(n,(R/n).read_text('utf8')+'\n'+addition+'\n')
entry=f'''<!-- map-resource-review-20261031:start -->
## 实现回顾维护 · {title}

同次准确地图与资源已接受，原资源快照却排在地图日志后，导致两条首图记录显示未知。现只在本次apply新范围中把已验资源快照放到地图阅读前、布局声明后；旧前缀、相同时间戳的前批、旧记录和归档不追填。105项不同检查/31项原生检查实际退出0，五张最终原图逐张查看，首轮夹具缺grid/source失败原件保留；实际小窗更新响应，启动六处私人路径保持。

上轮89次实际是83项不同检查，6项重复发现；原回执不变，本轮修正测试导入并单独记录计数，完整独立范围重新纳入无重复105项。三个公开地图候选只读固定树/README/许可，未安装或复制未验源码。回执：`{prefix}summary.json`。功能440/未开441，全程序/全视频与P3/P2/P1未完成，识别最后。
<!-- map-resource-review-20261031:end -->

'''
for n in ['WORK_IN_PROGRESS.md','PROJECT_COMPLETED.md']:text(n,entry+(R/n).read_text('utf8'))
cp=read('DEVELOPMENT_CHECKPOINT.json');cp['current_maintenance_save']={'kind':'implementation_review_maintenance','title':title,'receipt':prefix+'summary.json','binding':'enclosing_commit','functional_section_added':False,'status':'partial_program_review_same_frame_map_resources','review_checklist':'PROGRAM_REVIEW.md','review_checklist_sha256':pin('PROGRAM_REVIEW.md')['sha256'],'application_review_complete':False};cp['current_batch']['receipt']=prefix+'summary.json';cp['next_action']='继续全程序回顾：其它物品移除/计数/资格与跨层地图历史、异常恢复连续输入，核对未审数值链路与有明确许可的可复用实现；完整视频列表/楼层导航/资源胶囊和地图效果保留。已修新同帧资源复盘缺值，不追填旧记录；前轮计数83不同/89次已更正，识别最后。'
text('DEVELOPMENT_CHECKPOINT.json',json.dumps(cp,ensure_ascii=False,indent=2)+'\n');module=runpy.run_path(str(R/'scripts/update_cloud_index.py'));module['update'](R);assert module['validate_delivery'](R,cp)['current_section']==440
from scripts.verify_full_available import maintained_selectors
selectors=maintained_selectors();assert len(selectors)==712 and selectors[-1]=='tests.test_map_resource_review';assert read('CLOUD_INDEX.json')['requirements']['sha256']==pin('PROJECT_REQUIREMENTS.md')['sha256']
write(prefix+'final-audit.json',{'passed':True,'baseline_commit':BASE,'summary':pin(prefix+'summary.json'),'requirements':pin('PROJECT_REQUIREMENTS.md'),'cloud_index':pin('CLOUD_INDEX.json'),'ordered_selectors':712,'related_unique_tests':105,'native_unique_checks':31,'whole_program_complete':False,'whole_video_parity_complete':False,'at_UTC':datetime.now(timezone.utc).isoformat()})
(B/'record-source.py').write_bytes(Path(__file__).read_bytes());archive={p.relative_to(R).as_posix():{k:v for k,v in pin(p.relative_to(R)).items()if k!='path'}for p in sorted(B.rglob('*'))if p.is_file()and p.name!='archive-manifest.json'};write(prefix+'archive-manifest.json',{'kind':'explicit_public_archive','files':archive})
print(json.dumps({'passed':True,'related_unique_tests':105,'native_unique_checks':31,'archive_files':len(archive),'goal_complete':False}))
