from pathlib import Path
from hashlib import sha256
from datetime import datetime, timezone
import ast, ctypes, difflib, json, re, runpy, subprocess, sys, time

R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts')]
BASE='40bb988899546f5175add0ed49f2cd26e14c5402'
B=R/'verification/maintenance/remaining-runtime-guards-20261031';prefix=B.relative_to(R).as_posix()+'/'
def read(n):return json.loads((R/n).read_bytes())
def pin(n):
 p=R/n;raw=p.read_bytes();return {'path':p.relative_to(R).as_posix(),'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}
def write(n,value):(R/n).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n','utf8')
def text(n,value):
 p=R/n
 if not p.exists():p.parent.mkdir(parents=True,exist_ok=True);p.write_text(value,'utf8');return
 old=p.read_bytes().decode('utf8').splitlines(keepends=True);new=value.splitlines(keepends=True);out=list(new)
 for a,b,num in difflib.SequenceMatcher(None,[s.rstrip('\r\n')for s in old],[s.rstrip('\r\n')for s in new],autojunk=False).get_matching_blocks():
  for i in range(num):out[b+i]=old[a+i]
 p.write_bytes(''.join(out).encode('utf8'))
def old(n):return subprocess.check_output(['git','show',BASE+':'+n])
assert subprocess.check_output(['git','rev-parse','HEAD']).decode().strip()==BASE
from tests.reference_guard_cases import MODELS
from scripts.audit_runtime_reference_bindings import audit
from scripts.build_reference_runtime_manifests import build
from scripts.verify_full_available import maintained_selectors
packs=build();survey=audit(R)
assert survey['static_resolved_runtime_bindings']==92 and survey['all_resolved_runtime_bytes_match']and not survey['unresolved']
assert not any(r['runtime_code_files']for r in survey['rows'])
assert survey==read(prefix+'static-audit.json')
models=['rouge/'+Path(m.__file__).name for m,_ in MODELS]
def tree(raw):
 node=ast.parse(raw);node.body=[n for n in node.body if not(isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id in ('MANIFEST','MANIFEST_SHA256')for t in n.targets))];return ast.dump(node,include_attributes=False)
for n in models:
 assert tree(old(n))==tree((R/n).read_bytes())
 assert old(n)==(R/'research/remaining-runtime-guards-20261031/baseline'/Path(n).name).read_bytes()
record=read(prefix+'candidate-probe.json');assert record['passed']and record['baseline_commit']==BASE
untouched={'PROJECT_REQUIREMENTS.md','rouge/app.py','rouge/run_state.py','rouge/node_catalog.py','rouge/event_planning.py','rouge/node_rewards.py','rouge/current_battle_view.py','rouge/node_catalog_view.py','rouge/battle_view.py'}
for m,_ in MODELS:
 original=record['old_bindings'][m.__name__]['path'];untouched.add(original)
 packet=read(original)
 untouched.update(p for p in packet['files']if p.endswith(('.py','.js','.cjs')))
 if hasattr(m,'DATA'):untouched.add(m.DATA)
for m in ['battle_event_references','named_reward_items','ritual_weakening']:untouched.add('rouge/'+m+'.py')
for tag in ['battle-events','named-items','ritual']:untouched.add('research/runtime-reference-loaders-20261031/'+tag+'/source-manifest.json')
for n in untouched:assert old(n)==(R/n).read_bytes(),n
ids=set()
for name in ['tests','tests-repaired']:
 result=read(prefix+name+'/results.json');assert not result['forbidden_external_calls']and not result['skipped']
 process=read(prefix+name+'/process.json');assert process['actual_observed_exit']==(1 if name=='tests'else 0)
 if name=='tests':assert result['tests_run']==207 and result['failed']==1 and not result['errors']
 else:assert result['passed']and result['tests_run']==2
 ids.update(re.findall(r'^\w+ \((tests\.[^)]+)\) \.\.\. ok$',(B/name/'stderr.txt').read_text('utf8'),re.M))
assert len(ids)==207
native=read(prefix+'native-final/window.json');assert native['passed']and native['unique_checks']==45 and not native['source_drift']
assert not any(native['external_operation_attempts'].values())and read(prefix+'native-final/process.json')['actual_observed_exit']==0
for n in models:assert native['source_sha256_after'][n]==pin(n)['sha256']
assert not read(prefix+'native/window.json')['passed']and not read(prefix+'native-current/window.json')['passed']
# Preserve the first verifier as reconstructed from the immediately following
# captured source: these two exact verifier versions differ by that assertion.
first=(B/'native-current/verifier-source.py').read_text('utf8').replace("require('若已完成当前层' in node.player_detail.toPlainText(), 'documented_movement_exception_readable')", "require('下一层' in node.player_detail.toPlainText(), 'documented_movement_readable')")
(B/'native/verifier-source-reconstruction.py').write_text(first,'utf8')
(B/'native-final/verifier-source.py').write_bytes((R/'scripts/verify_remaining_runtime_guards.py').read_bytes())
write(prefix+'source-review.json',{'baseline_commit':BASE,'changed_source':[pin(n)for n in models],'only_two_manifest_declarations_changed_per_model':True,'unchanged_data_original_manifests_builders_and_existing_three_routes':[pin(n)for n in sorted(untouched)],'new_manifest_generation':packs,'static_audit':pin(prefix+'static-audit.json'),'runtime_code_bindings_in_audited_scope':0,'static_audit_scope':'92 directly declared manifest/support bindings, now including separate DATA/DATA_SHA256 and support proof pins. Byte consistency is not runtime schema, semantic or complete dynamic-loader coverage.','comparison_groups':record['case_counts'],'complete_public_output_comparison_count':sum(record['case_counts'].values()),'component_build_script_reads_before':sum(record['public_builder_reads_before'].values()),'component_build_script_reads_after':sum(record['public_builder_reads_after'].values()),'recognition_or_application_speedup_claimed':False,'REA_scope':'Existing Python source reviewed directly as REA skill directs; prior actual toolbar and bridge REA results retained. No new REA execution is claimed in this batch.','application_review_complete':False})
shots=[pin(p.relative_to(R))for p in sorted((B/'native-final').glob('*.png'))];assert len(shots)==7
write(prefix+'image-review.json',{'reviewer':'/root','images':shots,'review_method':'each final original separately loaded with view_image this turn','whole_video_parity_claimed':False,'observed_gaps':'Legacy event and configuration readers still dark, dense and tall; current rewards category label clips at this size. These public-reader views do not meet complete compact-video appearance. No UI source changed in this batch.'})
live=read(prefix+'live-window/window.json');assert live['passed']and live['private_six_paths_unchanged']
import win32gui,win32process
for w in live['owned_windows']:assert win32gui.IsWindowVisible(w['hwnd'])and win32process.GetWindowThreadProcessId(w['hwnd'])[1]==w['pid']and not ctypes.windll.user32.IsHungAppWindow(w['hwnd'])
a=read('.cache/runtime-remaining-guards-review-live-status.json');time.sleep(2.2);b=read('.cache/runtime-remaining-guards-review-live-status.json');assert b['toolbar_visible']and b['elapsed_since_launch']>a['elapsed_since_launch']
write(prefix+'live-window/desktop-review.json',{'actual_windows_mcp_snapshot_called':True,'actual_image_viewed':True,'region':[1716,1164,2130,1218],'owned_window_visible_and_responding':True,'Qt_timer_advanced':True,'private_six_paths_unchanged_during_startup':True,'private_contents_or_hashes_published':False,'game_operated':False,'chat_sent':False})
title='七处资料加载去除构建脚本运行依赖，保留数据核验与准确跳转'
write(prefix+'summary.json',{'kind':'implementation_review_maintenance','title':title,'baseline_commit':BASE,'completed_sections':440,'functional_section_added':False,'implemented_scope_passed':True,'related_unique_tests':207,'skips':0,'initial_tests_passed':206,'initial_tests_failed':1,'repaired_tests_run':2,'overlap_deduplicated':True,'test_receipts':[pin(prefix+n+'/results.json')for n in ['tests','tests-repaired']],'native_unique_checks':45,'native_receipt':pin(prefix+'native-final/window.json'),'native_initial_failures':'Incorrect next-layer wording expectation, then a hidden final validation target; both verifier-only defects corrected. Two failing receipts and observed exits retained. First verifier reconstruction explicitly labelled, not asserted original capture.','unit_initial_failure':'New temp-tree fixture omitted separately pinned stage-entry generated DATA; include that independent file and test its corruption. Production reader unchanged.','source_review':pin(prefix+'source-review.json'),'image_review':pin(prefix+'image-review.json'),'live_window':pin(prefix+'live-window/desktop-review.json'),'static_resolved_bindings':92,'static_runtime_code_dependencies':0,'static_byte_consistency_not_semantics':True,'application_review_complete':False,'video_parity_complete':False,'P3_complete':False,'P2_complete':False,'P1_complete':False,'full_validation_rerun':False,'full440_only_original_frozen_source':True,'private_data_included':False,'game_operated':False,'chat_sent':False,'publication_binding':'enclosing maintenance commit; ordinary push and actual remote/blob equality required'})
text('research/remaining-runtime-guards-20261031/README.md','''# 七处资料加载依赖精简

按REA技能，完整Python源码直接阅读并验证运行，不为覆盖率机械生成PYC；已有工具条和桥接REA证据保留，本批未新增REA工具调用。

招募说明、当前奖励、事件具名奖励链接、移动奖励、和平守卫者、安眠一隅及准确关卡入口七个加载器只核对构建脚本字节，没有执行这些脚本。复用既有运行清单生成器，将历史代码只留在溯源部分，七处程序各仅更换MANIFEST和MANIFEST_SHA256，全部函数AST保持。所有原数据、原文、构建器和旧冻结清单不覆盖；独立数据摘要、类型/缓存/准确令牌和来源失效清理继续保留。原三个已恢复加载器及其新清单字节保持。

实际临时候选对照10组共255份完整公开结果（只归一化清单路径/身份），包含184个固定关卡奖励配置、此前三类41份结果、3个当前目录及其它精确分支。正式绑定后测试核对同一输出摘要。一次七源包读取中的构建脚本读取从10次到0次；这只是组件读取计数，不能称识别或全程序提速。来源资料快照与范围未升级，不证明当前服务器完整。

207个不同相关测试覆盖通过，0跳过。首次206通过1失败是新隔离夹具漏掉独立摘要绑定的关卡入口DATA；补齐后只重跑该失败及随后改动的静态审计用例，重叠不累计。审计也补充DATA/DATA_SHA256和6份支持证明的独立绑定，92份声明字节一致且不再依赖程序文件；静态范围不等于92种功能或全程序语义。

本机隔离原生45项唯一检查通过：准确招募/移动说明、四类安眠选项/后续场景、固定入口、当前奖励至准确配置条目、奖励单独来源丢失/恢复及状态不变。两次原生失败分别为验证脚本误期望下一层文案和最终目标页面未切回，原回执保留；第一版脚本为明确标注的重建，不伪称当时捕获。7张最终原图逐张查看，深色密集界面、过长窗口和奖励类别文字裁切仍需改进，不冒称视频一致。

实际测试小窗已正常更新并打开，Win32可见响应、Qt计时推进及Windows-mcp截图核对。启动区间六处私人路径保持，不发布内容/摘要，不操作游戏、不发聊天。功能仍440，未开441，下一全量455；full440仅原冻结源码，P3/P2/P1及完整回顾未完成。
''')
n='PROGRAM_REVIEW.md';t=(R/n).read_text('utf8');t=t.replace('修复三条资料误失效链路。 | 其余7份构建脚本运行绑定、其它阅读器共享','修复三条资料误失效链路，七处加载器去除构建脚本运行依赖，数据核验保留。 | 其它阅读器共享');t+='\n[七处资料依赖回顾](research/remaining-runtime-guards-20261031/README.md)保留全部函数与数据，255份公开结果对照、207个不同相关测试和45项隔离原生检查覆盖。92份静态绑定已含独立DATA和支持证明，不代表完整功能或机制准确；其余阅读器外观仍未对齐视频。\n';text(n,t)
n='PROJECT_PROGRESS.md';t=(R/n).read_text('utf8').replace('核对其余7份构建脚本的运行绑定、其它资料入口','核对其它资料入口');t=t.replace('其它窗口的统一图片入口','其它窗口的统一图片入口');text(n,t)
n='VIDEO_PARITY.md';t=(R/n).read_text('utf8');t+='\n[七处加载依赖精简](research/remaining-runtime-guards-20261031/README.md)保留准确资料跳转和未知边界；实际原生图复核仍发现旧事件/配置阅读器过长、深色密集，当前奖励类别文字在该窗口宽度下裁切。这些是下一步具体视觉缺口，数据对照一致不能代替视频效果一致。\n';text(n,t)
entry=f'''<!-- remaining-runtime-guards-20261031:start -->
## 实现回顾维护 · {title}

七处程序各仅换清单与摘要声明；复用现有构建工具，原数据、构建脚本及旧冻结包不变，数据损坏、缓存类型和准确来源保护保留。255份完整公开结果对照一致，一轮七源包构建脚本读取10→0，仅组件计数，不称全程序/识别提速。

207个不同相关测试覆盖通过、0跳过；原夹具缺独立DATA的失败及修复后复跑保留。最终原生45项唯一检查通过、实际退出0，验证脚本两次原失败保留；7张最终原图逐张查看，旧资料窗口紧凑排版/密度及类别文字裁切仍待修正。实际测试窗已更新可见响应，启动六处私人路径保持。功能仍440，441未开，完整回顾/视频和P3/P2/P1未完成，识别最后。回执：`{prefix}summary.json`。
<!-- remaining-runtime-guards-20261031:end -->

'''
for n in ['WORK_IN_PROGRESS.md','PROJECT_COMPLETED.md']:text(n,entry+(R/n).read_text('utf8'))
cp=read('DEVELOPMENT_CHECKPOINT.json');cp['current_maintenance_save']={'kind':'implementation_review_maintenance','title':title,'receipt':prefix+'summary.json','binding':'enclosing_commit','functional_section_added':False,'status':'partial_program_review_seven_runtime_build_dependencies_removed','review_checklist':'PROGRAM_REVIEW.md','review_checklist_sha256':pin('PROGRAM_REVIEW.md')['sha256'],'application_review_complete':False};cp['current_batch']['receipt']=prefix+'summary.json';cp['next_action']='继续完整实现回顾：其它资料阅读器与缓存/失效、旧事件与固定配置窗口紧凑布局和奖励类别裁切，核对招募/强化连续状态及独立机制算例。七处构建脚本运行依赖已精简不重复推进；92静态绑定不是全程序语义完成，识别优化最后。'
text('DEVELOPMENT_CHECKPOINT.json',json.dumps(cp,ensure_ascii=False,indent=2)+'\n');module=runpy.run_path(str(R/'scripts/update_cloud_index.py'));module['update'](R);assert module['validate_delivery'](R,cp)['current_section']==440
selectors=maintained_selectors();assert len(selectors)==700 and selectors[-1]=='tests.test_remaining_runtime_guards';assert read('CLOUD_INDEX.json')['requirements']['sha256']==pin('PROJECT_REQUIREMENTS.md')['sha256']
write(prefix+'final-audit.json',{'passed':True,'baseline_commit':BASE,'summary':pin(prefix+'summary.json'),'requirements':pin('PROJECT_REQUIREMENTS.md'),'cloud_index':pin('CLOUD_INDEX.json'),'ordered_selectors':700,'unique_related_tests':207,'native_unique_checks':45,'static_resolved_bindings':92,'whole_program_complete':False,'whole_video_parity_complete':False,'at_UTC':datetime.now(timezone.utc).isoformat()})
(B/'record-source.py').write_bytes(Path(__file__).read_bytes())
archive={p.relative_to(R).as_posix():{k:v for k,v in pin(p.relative_to(R)).items()if k!='path'}for p in sorted(B.rglob('*'))if p.is_file()and p.name!='archive-manifest.json'}
write(prefix+'archive-manifest.json',{'kind':'explicit_public_archive','files':archive})
print(json.dumps({'passed':True,'unique_tests':207,'native_checks':45,'archive_files':len(archive),'goal_complete':False}))
