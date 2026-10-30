from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import ast,json,sys,subprocess,difflib,runpy,re,time,ctypes
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts')]
B=R/'verification/maintenance/runtime-loader-review-20261031';prefix=B.relative_to(R).as_posix()+'/'
baseline='cb64f25638e732a5eda52a5fe2f8c4ec1d33a7d5'
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
def old(n):return subprocess.check_output(['git','show',baseline+':'+n])
assert subprocess.check_output(['git','rev-parse','HEAD']).decode().strip()==baseline
from scripts.build_reference_runtime_manifests import build
from scripts.audit_runtime_reference_bindings import audit
from rouge import battle_event_references as battle,named_reward_items as items,ritual_weakening as ritual
packs=build();survey=audit(R);assert survey['static_resolved_runtime_bindings']==92 and not survey['unresolved']and survey['all_resolved_runtime_bytes_match'];assert survey==read(prefix+'current-static-survey.json')
models=[battle,items,ritual];changed=['rouge/battle_event_references.py','rouge/named_reward_items.py','rouge/ritual_weakening.py','rouge/battle_entry_reference_view.py']
from tests.test_runtime_reference_review import outputs
assert sum(len(outputs(model))for model in models)==41
for n in changed[:3]:
 def tree(raw):
  t=ast.parse(raw);t.body=[x for x in t.body if not(isinstance(x,ast.Assign)and any(isinstance(a,ast.Name)and a.id in ('MANIFEST','MANIFEST_SHA256')for a in x.targets))];return ast.dump(t,include_attributes=False)
 assert tree(old(n))==tree((R/n).read_bytes())
untouched=['rouge/data/battle-event-references.json','rouge/data/named-reward-items.json','rouge/data/ritual-weakening.json','rouge/node_catalog.py','rouge/event_planning.py','rouge/node_rewards.py','rouge/battle_view.py','rouge/named_reward_items_view.py','rouge/ritual_weakening_view.py','rouge/app.py','rouge/run_state.py','scripts/build_named_reward_items_301.py','scripts/build_ritual_weakening_302.py','scripts/build_battle_event_references_296.py','PROJECT_REQUIREMENTS.md']
for n in untouched:assert old(n)==(R/n).read_bytes(),n
frozen=[]
for base in ['research/p3-battle-entry-compatibility-299','research/p3-named-reward-items-301','research/p3-ritual-weakening-302']:
 for n in subprocess.check_output(['git','ls-tree','-r','--name-only',baseline,'--',base]).decode().splitlines():assert old(n)==(R/n).read_bytes();frozen.append(pin(n))
before=read(prefix+'before-availability.json');assert before['baseline_commit']==baseline and not any(before['public_reference_available'].values())
available=[battle.source_data()is not None,items._verified_packet(items.EVENT_IDS[0])is not None,ritual.source_data()is not None];assert all(available)
write(prefix+'after-availability.json',{'public_reference_available':dict(zip(['battle-events','named-items','ritual'],available)),'data_changed':False,'full_current_game_coverage_claimed':False})
initial=read(prefix+'tests/results.json');assert initial['tests_run']==139 and initial['failed']==2 and initial['errors']==0 and not initial['skipped']
repaired=read(prefix+'tests-repaired/results.json');assert repaired['passed']and repaired['tests_run']==2 and not repaired['skipped']
ids=set()
for folder in ['tests','tests-repaired','view-check']:
 d=read(prefix+folder+'/results.json');assert not d['forbidden_external_calls']
 if folder!='tests':assert d['passed']and read(prefix+folder+'/process.json')['actual_observed_exit']==0
 ids.update(re.findall(r'^\w+ \((tests\.[^)]+)\) \.\.\. ok$',(B/folder/'stderr.txt').read_text('utf8'),re.M))
assert len(ids)==139
native=read(prefix+'native-current/window.json');assert native['passed']and native['unique_checks']==42 and not native['source_drift']and not any(native['external_operation_attempts'].values());assert read(prefix+'native-current/process.json')['actual_observed_exit']==0
assert all(native['source_sha256_after'][n]==pin(n)['sha256']for n in changed)
remaining=[r['module']for r in survey['rows']if r['runtime_code_files']];assert len(remaining)==7
write(prefix+'source-review.json',{'baseline_commit':baseline,'changed_source':[pin(n)for n in changed],'loaders_only_two_binding_assignments_changed':True,'untouched_state_data_builders_and_requirements':[pin(n)for n in untouched],'old_frozen_files_unchanged':frozen,'new_runtime_manifests':packs,'static_manifest_audit':pin(prefix+'current-static-survey.json'),'remaining_runtime_build_code_bindings':remaining,'static_audit_scope':'92 directly declared manifest/support-file bindings. No target module imported by auditor; byte consistency is not schema, semantics, UI, mechanics or all dynamic loader coverage.','REA_scope':'Complete Python source reviewed directly under REA skill; prior toolbar/bridge reverse evidence retained. No mechanical PYC scan or whole-program claim.','simplification':'Remove historical source code from three runtime data gates, reuse the existing validators/caches/readers. Replay original builders unchanged with exact public archived guard bytes in a temporary tree.','retained_protections':'Every selected data/authority/document byte, typed API/cache comparisons, exact navigation/source tokens, private state and no duplicate sends remain protected.','application_review_complete':False})
shots=[];previously_viewed={'named-item.png','named-scrap.png','ritual.png','ritual-battle.png','source-unavailable.png'}
for p in sorted((B/'native-current').glob('*.png')):
 reuse=p.name in previously_viewed and p.read_bytes()==(B/'native'/p.name).read_bytes()
 shots.append({'image':pin(p.relative_to(R)),'reviewer':'/root','review_method':'same turn earlier individually viewed original, whole-file bytes equal'if reuse else'individually loaded current original with view_image','earlier_image':pin((B/'native'/p.name).relative_to(R))if reuse else None,'scope':'isolated public reader data, not game or private run'})
assert len(shots)==8 and sum(s['earlier_image']is not None for s in shots)==5
write(prefix+'image-review.json',{'images':shots,'new_actual_originals_viewed':3,'whole_byte_equal_review_reuses':5,'additional_originals_viewed_before_text_fix':6,'whole_video_parity_claimed':False,'remaining_visual_scope':'These legacy full reference readers still need the compact layout and appearance alignment described in VIDEO_PARITY; restored data does not prove full parity.'})
live=read(prefix+'live-window/window.json');assert live['passed']and live['private_six_paths_unchanged']and all(live['source_sha256_after'][n]==pin(n)['sha256']for n in changed)
import win32gui,win32process
for w in live['owned_windows']:assert win32gui.IsWindowVisible(w['hwnd'])and win32process.GetWindowThreadProcessId(w['hwnd'])[1]==w['pid']and not ctypes.windll.user32.IsHungAppWindow(w['hwnd'])
a=read('.cache/runtime-reference-review-live-status.json');time.sleep(2.2);b=read('.cache/runtime-reference-review-live-status.json');assert b['toolbar_visible']and b['elapsed_since_launch']>a['elapsed_since_launch']
write(prefix+'live-window/desktop-review.json',{'actual_windows_mcp_snapshot_called':True,'actual_image_viewed':True,'region':[1716,1164,2130,1218],'owned_window_visible_and_responding':True,'Qt_timer_advanced':True,'private_six_paths_unchanged_during_startup':True,'private_contents_or_hashes_published':False,'game_operated':False,'chat_sent':False})
title='恢复战斗事件入口、具名奖励和调谐仪式资料，分开构建溯源与运行校验'
write(prefix+'summary.json',{'kind':'implementation_review_maintenance','title':title,'baseline_commit':baseline,'completed_sections':440,'functional_section_added':False,'implemented_scope_passed':True,'related_unique_tests':139,'test_scope':'First current run 137 passed and two historical builder replays failed; only the two repaired failures rerun. Changed text reader scope rerun, all overlapping methods deduplicated. No production mechanism model changed.','initial_receipt':pin(prefix+'tests/results.json'),'repaired_receipt':pin(prefix+'tests-repaired/results.json'),'reader_receipt':pin(prefix+'view-check/results.json'),'native_unique_checks':42,'native_receipt':pin(prefix+'native-current/window.json'),'source_review':pin(prefix+'source-review.json'),'image_review':pin(prefix+'image-review.json'),'runtime':pin(prefix+'live-window/desktop-review.json'),'static_resolved_bindings':92,'static_byte_consistency_not_semantic_coverage':True,'initial_failures':'Unchanged 301/302 historical builders required old parser bytes in the live checkout. New isolated replay supplies exactly pinned historical guard bytes without executing historical application code or modifying old builders/outputs; all original assertions retained.','application_review_complete':False,'video_parity_complete':False,'P3_complete':False,'P2_complete':False,'P1_complete':False,'full_validation_rerun':False,'full440_only_original_frozen_source':True,'private_data_included':False,'game_operated':False,'chat_sent':False,'publication_binding':'enclosing maintenance commit, ordinary publication and actual remote/blob check follows'})
text('research/runtime-reference-loaders-20261031/README.md','''# 资料运行绑定与历史构建回顾

本轮按REA技能直接审查完整Python源码和实际运行，不机械生成PYC；已有工具条/桥接REA证据保留。本机92个直接声明MANIFEST_SHA256的模块已做清单及所声明运行/支持文件的字节核对，全部一致；这是静态绑定范围，不证明每个函数运行、公式准确或所有动态路径已审完。初查86个绑定及6个未解析支持目录保留，随后补齐目录表达式得到92，不把文件数当完成度。

## 真实问题与替换

修正前固定战斗事件入口、具名奖励物品和调谐仪式三个资料加载器实际均不可用。它们的数据/文献未变，旧清单却将已重构node_catalog.py的字节也作为运行资料门槛。新建三份运行清单，仍核对全部选中资料、权威记录和文献；程序字节只作为历史构建来源。三个加载器各仅更换MANIFEST及其SHA两项声明，所有函数AST保持。旧299/301/302资料包、数据、构建脚本与原回执不覆盖；新来源身份也不会接受旧令牌串用。

完整保留类型/缓存污染校验、准确事件/场景/选项映射、未知本局状态、数据损坏清理与恢复后重新手选。旧守卫字节在临时公开目录回放，与当前41份入口/事件/选项结果仅有来源清单身份差别；这不是独立机制算例，也不冒称当年的原程序实机。首次137通过2失败是旧构建器要求当前源码等于冻结版本；新replay_reference_recipe.py在临时目录放回已核对历史输入，调用原构建器的只读流程，不执行历史应用代码、不改旧文件，原全部断言通过。当前运行包由build_reference_runtime_manifests.py复现/核对，不覆盖不同字节。

原生窗口已核对奖励藏品与零件图片、仪式六种选择与相关固定作战、来源丢失后清空旧条目/关闭所属预览、恢复后不自动选择，以及固定战斗准确跳回事件场景和选项。说明里的“点击下方入口”与顶部按钮位置不符，已改为直接引用按钮名称。未把仪式说明应用为实际弱化数值，未自动领取或进入战斗。

## 边界及证据

139个不同相关用例通过；两项失败只补跑原失败，说明文字变更复跑对应视图范围，重复不累计。当前原生42项唯一检查通过，真实退出0，九类外部操作零。最终8张图中3张当前原图实际查看，5张按整字节相同复用同批先前逐张审阅。实际测试小窗已更新可见响应，启动区间六处私人路径保持；不操作游戏、不发聊天、不上传个人数据。

其余7个资料包仍将构建脚本纳入运行校验，当前字节一致；后续须逐包核对依赖再决定替换，不能仅凭低概率删除真实代码/数据一致性保护。完整机制、版本覆盖、紧凑浮窗、其它界面与视频效果和跨屏仍未完成。功能仍440，本轮为实现回顾维护，不增加节数；下一周期全量455，旧full440只证明其原冻结来源，P3/P2/P1及完整程序目标保持未完成。
''')
n='PROGRAM_REVIEW.md';t=(R/n).read_text('utf8');t=t.replace('来源仍每轮核对。 | 其它阅读器共享、缓存更新失效与全部数据适用性；','来源仍每轮核对；静态核对92份声明绑定，修复三条资料误失效链路。 | 其余7份构建脚本运行绑定、其它阅读器共享、缓存更新失效与全部数据适用性；');t+='\n[运行资料绑定回顾](research/runtime-reference-loaders-20261031/README.md)已恢复固定战斗对应事件、具名奖励和调谐仪式资料；保留旧冻结来源与原构建器，来源令牌/类型/数据保护不降级。92份静态字节核对不代表92个完整功能或全程序语义完成。\n';text(n,t)
n='VIDEO_PARITY.md';t=(R/n).read_text('utf8');t+='\n[资料运行绑定回顾](research/runtime-reference-loaders-20261031/README.md)恢复了因旧源码摘要误禁的战斗事件入口、奖励图文和调谐仪式说明，并核对实际按钮跳转与失效清理；未改机制和数值。旧完整资料阅读器的控件密度、紧凑浮窗和视觉统一仍待继续，与视频全部一致仍未实现。\n';text(n,t)
entry=f'''<!-- runtime-loader-review-20261031:start -->
## 实现回顾维护 · {title}

三条实际不可用资料链路已恢复；数据未变，只将历史程序字节移出运行门槛，保留全部数据/文献、缓存类型比较和准确令牌校验。原299/301/302包、数据与构建脚本不改写；两项旧构建测试通过临时公开目录回放旧字节，保留原断言。按钮位置说明改用按钮名称。

相关139个不同用例、当前原生42项唯一检查通过；首轮137通过2失败及修复后两项复跑均保留，不重复累计视图检查。静态92份声明绑定/运行或支持文件字节一致，不等于全部加载器语义或机制已审完。8张最终图3张当前实看、5张整字节复用本批已逐张查看的原图。实际测试窗更新可见响应，启动区间六处私人路径保持；不操作游戏、不发聊天。功能仍440，441未启动，全程序/视频及P3/P2/P1未完成，识别最后。回执：`{prefix}summary.json`。
<!-- runtime-loader-review-20261031:end -->

'''
for n in ['WORK_IN_PROGRESS.md','PROJECT_COMPLETED.md']:text(n,entry+(R/n).read_text('utf8'))
n='PROJECT_PROGRESS.md';t=(R/n).read_text('utf8').replace('核对其余资料入口、固定作战完整数据','核对其余7份构建脚本的运行绑定、其它资料入口、固定作战完整数据');text(n,t)
cp=read('DEVELOPMENT_CHECKPOINT.json');cp['current_maintenance_save']={'kind':'implementation_review_maintenance','title':title,'receipt':prefix+'summary.json','binding':'enclosing_commit','functional_section_added':False,'status':'partial_program_review_three_runtime_reference_routes_restored','review_checklist':'PROGRAM_REVIEW.md','review_checklist_sha256':pin('PROGRAM_REVIEW.md')['sha256'],'application_review_complete':False};cp['current_batch']['receipt']=prefix+'summary.json';cp['next_action']='继续全程序回顾：其余7个构建脚本运行绑定与资料缓存依赖、其它阅读器共享/失效、紧凑窗口和视频差异，随后招募/强化连续状态与独立机制校准。三条误失效链路已恢复不重复推进；92静态绑定不是语义完成，识别优化最后。'
text('DEVELOPMENT_CHECKPOINT.json',json.dumps(cp,ensure_ascii=False,indent=2)+'\n');m=runpy.run_path(str(R/'scripts/update_cloud_index.py'));m['update'](R);assert m['validate_delivery'](R,cp)['current_section']==440
from scripts.verify_full_available import maintained_selectors
selectors=maintained_selectors();assert len(selectors)==699 and selectors[-1]=='tests.test_runtime_reference_review';assert read('CLOUD_INDEX.json')['requirements']['sha256']==pin('PROJECT_REQUIREMENTS.md')['sha256']
code=(R/'scripts/verify_full_available.py').read_text('utf8');assert code.index("ADDITIONAL_MODULES += ('tests.test_runtime_reference_review',)")<code.index("if __name__ == '__main__':")
write(prefix+'final-audit.json',{'passed':True,'baseline_commit':baseline,'summary':pin(prefix+'summary.json'),'requirements':pin('PROJECT_REQUIREMENTS.md'),'cloud_index':pin('CLOUD_INDEX.json'),'ordered_selectors':699,'unique_related_tests':139,'native_unique_checks':42,'static_resolved_bindings':92,'static_audit_not_semantic_proof':True,'private_contents_included':False,'whole_program_complete':False,'whole_video_parity_complete':False,'at_UTC':datetime.now(timezone.utc).isoformat()})
(B/'record-source.py').write_bytes(Path(__file__).read_bytes());manifest={p.relative_to(R).as_posix():{k:v for k,v in pin(p.relative_to(R)).items()if k!='path'}for p in sorted(B.rglob('*'))if p.is_file()and p.name!='archive-manifest.json'};write(prefix+'archive-manifest.json',{'kind':'explicit_public_archive','files':manifest});print(json.dumps({'passed':True,'unique_tests':139,'native_checks':42,'archive_files':len(manifest),'goal_complete':False}))
