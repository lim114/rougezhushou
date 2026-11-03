from pathlib import Path
from hashlib import sha256,sha1
from datetime import datetime,timezone
import ast,ctypes,difflib,json,re,runpy,subprocess,sys,time
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts'),str(R/'.cache/305-window-tooldeps')]
BASE='9b6c86649a884fb614d665048c13f08565e819e2';B=R/'verification/maintenance/history-reference-review-20261031';prefix=B.relative_to(R).as_posix()+'/'
def read(n):return json.loads((R/n).read_bytes())
def pin(n):
 p=R/n;raw=p.read_bytes();return {'path':p.relative_to(R).as_posix(),'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}
def write(n,v):(R/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf8')
def text(n,v):
 p=R/n
 if not p.exists():p.parent.mkdir(parents=True,exist_ok=True);p.write_text(v,'utf8');return
 a=p.read_bytes().decode('utf8').splitlines(keepends=True);out=v.splitlines(keepends=True)
 for x,y,k in difflib.SequenceMatcher(None,[s.rstrip('\r\n')for s in a],[s.rstrip('\r\n')for s in out],autojunk=False).get_matching_blocks():
  for i in range(k):out[y+i]=a[x+i]
 p.write_bytes(''.join(out).encode('utf8'))
def old(n):return subprocess.check_output(['git','show',BASE+':'+n])
assert subprocess.check_output(['git','rev-parse','HEAD']).decode().strip()==BASE
changed=['rouge/player_replay.py','rouge/player_evidence_history.py','rouge/player_shop_memory.py']
for n in changed:assert old(n)==(R/('research/history-reference-review-20261031/before-'+Path(n).name)).read_bytes()
unchanged=['rouge/expansion_reference.py','rouge/player_history_store.py','rouge/player_history_codec.py','rouge/player_replay_nodes.py','rouge/player_replay_archive.py','rouge/run_state.py','rouge/damage.py','PROJECT_REQUIREMENTS.md']
for n in unchanged:assert old(n)==(R/n).read_bytes(),n
assert not subprocess.check_output(['git','diff','--name-only',BASE,'--','rouge/data']).strip()
tests=read(prefix+'tests-final/results.json');assert tests['passed']and tests['tests_run']==58 and tests['failed']==tests['errors']==0 and not tests['skipped']and not tests['forbidden_external_calls']
ids=re.findall(r'^test_\w+ \(([^)]+)\)',(R/(prefix+'tests-final/stderr.txt')).read_text('utf8'),re.M);assert len(ids)==len(set(ids))==58
assert read(prefix+'tests-final/process.json')['actual_observed_exit']==0
before=read(prefix+'before/results.json');assert before['tests_run']==6 and before['failed']==4 and before['errors']==0 and read(prefix+'before/process.json')['actual_observed_exit']==1
native=read(prefix+'native/receipt.json');assert native['passed']and native['unique_checks']==22 and not any(native['external_operation_attempts'].values())and read(prefix+'native-process.json')['actual_observed_exit']==0
for n in changed:assert native['source_sha256_after'][n]==pin(n)['sha256']
images=native['screenshots']+read(prefix+'native/images.json')['images'];assert len(images)==5
for row in images:assert sha256((R/row.get('file',row.get('path'))).read_bytes()).hexdigest()==row['sha256']
write(prefix+'native/visual-review.json',{'images':images,'all_five_final_originals_individually_viewed':True,'actual_compact_parent_refresh_used':True,'temporary_current_and_archive_only':True,'whole_video_parity_claimed':False})
for n in ('.cache/verify_history_reference_native.py','.cache/run_history_reference_checks.py'):(B/Path(n).name).write_bytes((R/n).read_bytes())
(B/'tests-final/test-source.py').write_bytes((R/'tests/test_history_reference_review.py').read_bytes())
live=read(prefix+'live-window/window.json');assert live['passed']and live['private_six_paths_unchanged']
import win32gui,win32process
for w in live['owned_windows']:assert win32gui.IsWindowVisible(w['hwnd'])and win32process.GetWindowThreadProcessId(w['hwnd'])[1]==w['pid']and not ctypes.windll.user32.IsHungAppWindow(w['hwnd'])
first=read('.cache/history-reference-review-live-status.json');time.sleep(2.2);last=read('.cache/history-reference-review-live-status.json');assert last['toolbar_visible']and last['elapsed_since_launch']>first['elapsed_since_launch']
write(prefix+'live-window/desktop-review.json',{'actual_Windows_MCP_snapshot_and_image_view':True,'region':[1716,1164,2130,1218],'test_window_visible_responding_and_Qt_timer_advanced':True,'private_six_paths_unchanged_during_startup':True,'private_contents_or_hashes_published':False,'game_operated':False,'chat_sent':False})
write(prefix+'source-review.json',{'baseline_commit':BASE,'changed_source':[pin(n)for n in changed],'unchanged_source_and_requirements':[pin(n)for n in unchanged],'existing_packet_source_hash_checks_retained':True,'refactor':'Parent refresh always delegates source-dependent evidence/shop to their own local refresh guards, removing duplicate shop call sites. Evidence validates source each call but caches identical raw input before evidence projection; original projected-row guard still preserves objects for unrelated history appends. Shop history validates eligible entries against one coherent packet per invocation rather than loading a packet for each candidate.','measured_component_work':{'source_reads_for_one_13_candidate_shop_fixture_before':13,'source_reads_after':1,'evidence_projection_calls_for_three_stable_parent_refreshes':0,'source_availability_still_checked':True},'end_to_end_performance_or_RSS_claimed':False,'net_code_reduction_claimed':False,'defensive_source_state_or_send_guards_removed':False,'REA_scope':'Complete Python source and requested native Qt runtime review according to skill; no new REA call, old bytecode/CJS evidence separate.','remaining':'Other source-dependent readers, raw timeline details and all parent scheduling not exhaustively reviewed; full lifecycle/cross-screen, independent mechanisms and whole program/video remain.'})
title='历史来源变化实时清理，商店记录共用单次资料读取'
write(prefix+'summary.json',{'kind':'implementation_review_maintenance','title':title,'baseline_commit':BASE,'completed_sections':440,'functional_section_added':False,'implemented_scope_passed':True,'different_tests':58,'passed_tests':58,'skipped':0,'new_tests':6,'original_reproduction_tests':6,'original_reproduction_failures':4,'original_actual_exit':1,'native_primary_unique_checks':22,'final_primary_images':5,'all_final_images_individually_viewed':True,'component_shop_source_reads_before':13,'component_shop_source_reads_after':1,'end_to_end_speed_claimed':False,'source_and_private_guards_retained':True,'test_window_updated':True,'private_six_paths_unchanged_during_startup':True,'source_review':pin(prefix+'source-review.json'),'tests':pin(prefix+'tests-final/results.json'),'native':pin(prefix+'native/receipt.json'),'full_validation_rerun':False,'full440_only_original_frozen_source':True,'whole_program_complete':False,'whole_video_parity_complete':False,'P3_complete':False,'P2_complete':False,'P1_complete':False,'game_operated':False,'chat_sent':False,'private_data_included':False,'publication_binding':'enclosing maintenance commit, ordinary push and actual remote/blob verification required'})
text('research/history-reference-review-20261031/README.md','''# 历史来源刷新与重复读取回顾

沿完整Python源码和实际Qt父子页面检查，不生成无必要字节码、不新调用REA。先用六项隔离测试在本次基线复现四个失败：当前和归档对局的记录不变时，父页提前返回，子页来源失效检查根本未执行；13条候选商店记录会重复读取同一固定资料包13次；稳定父刷新也没有再次验证持有记录来源。原失败、退出1与修复后原件分别保留，不改写为通过。

现将两个来源依赖子页统一放在父页历史短路之前刷新，删除重复调用分支；持有记录每次仍核验来源，但输入未变时不重建投影。原投影结果守卫保留，不相关资源日志增加时原条目对象/阅读保持。商店只在有候选记录时读取一次原固定资料包，将同一已核验物品表用于每条名称/ID确认；没有候选时不读资料，包失效时不借旧包。原摘要校验、归档原子存储和数据、资格判定条件、公式与私人保护保持。

58个不同必要检查全通过，无跳过。六个新场景覆盖当前、归档、稳定刷新、无关日志、13候选商店及空清单；原52项历史/目录/图片/来源范围一起保留。Windows原生22项沿实际紧凑窗口父刷新核对当前/归档丢失和恢复，选中项保持、归档字节不改、当前局不回写；五张最终原图逐张查看。组件工作量为13次资料读取变1次，稳定三刷新投影0次但来源仍核对；不宣称整机/端到端提速或净减代码。

原项目测试窗口已更新可见响应，启动六处私人路径保持；只有临时构造记录，无游戏操作、真实聊天或个人上传。维护不加功能节，440/未开441，718有序选择器；全量440仅原冻结来源。其它父页刷新、原始日志详情、完整视频/跨屏、独立机制及全程序/P3/P2/P1仍未完成，识别最后。
''')
entry=f'''<!-- history-reference-review-20261031:start -->
## 实现回顾维护 · {title}

实证父页历史不变会跳过持有记录来源核对，当前/归档旧参考滞留；已修正父调用并复用子页输入守卫，稳定刷新不重建、无关日志不换原条目。商店13候选同包读取从13次到1次，无候选0次；保留原来源摘要与每条资格条件，不声称端到端提速或净减代码。

原六项四失败/退出1保留，最终58项不同检查通过，原生22项和五张最终图核对；小窗更新响应、启动六私人路径保持，零游戏/聊天/上传。回执：`{prefix}summary.json`。功能440/未开441、718选择器；其它父页/原始日志、机制、全视频与程序/P3/P2/P1未完成，识别最后。
<!-- history-reference-review-20261031:end -->

'''
for n in ('WORK_IN_PROGRESS.md','PROJECT_COMPLETED.md'):text(n,entry+(R/n).read_text('utf8'))
n='PROGRAM_REVIEW.md';s=(R/n).read_text('utf8');s+='\n[历史来源父刷新回顾](research/history-reference-review-20261031/README.md)修正当前/归档记录不变时的来源清理遗漏，稳定刷新不重建证据行；商店候选共用一次已核验资料读取。58项不同检查及22项原生通过，原四失败保留；其它父页和原始日志、完整视频/机制与全程序仍未完成。\n';text(n,s)
n='PROJECT_PROGRESS.md';s=(R/n).read_text('utf8').replace('其余附属资料窗的对象释放','其余附属资料窗的对象释放和其它父页/原始日志的来源刷新',1);text(n,s)
n='IMPLEMENTATION_STRATEGY.md';text(n,(R/n).read_text('utf8')+'\n[历史来源读取复用](research/history-reference-review-20261031/README.md)使用既有包校验器和子页本地守卫，父页历史短路不再挡住来源变化；稳定输入跳过重复投影，原投影相等守卫保留。商店每批候选共享同一次核验表，无候选不读包；减少实际组件重复工作，不以减少必要来源保护换速度。\n')
cp=read('DEVELOPMENT_CHECKPOINT.json');cp['current_maintenance_save']={'kind':'implementation_review_maintenance','title':title,'receipt':prefix+'summary.json','binding':'enclosing_commit','functional_section_added':False,'status':'partial_program_review_parent_reference_refresh','review_checklist':'PROGRAM_REVIEW.md','review_checklist_sha256':pin('PROGRAM_REVIEW.md')['sha256'],'application_review_complete':False};cp['current_batch']['receipt']=prefix+'summary.json';cp['next_action']='继续完整程序回顾与视频逐页核对：其它父页和原始日志的来源刷新、同名变体卡片可读区分、其它资料窗缓存/释放、历史有证字段及独立机制。当前/归档持有记录来源清理和商店单次资料读取已修复，不重复计推进；完整程序/视频未完成，识别最后。'
text('DEVELOPMENT_CHECKPOINT.json',json.dumps(cp,ensure_ascii=False,indent=2)+'\n');idx=runpy.run_path(str(R/'scripts/update_cloud_index.py'));idx['update'](R);assert idx['validate_delivery'](R,cp)['current_section']==440
from scripts.verify_full_available import maintained_selectors
selectors=maintained_selectors();assert len(selectors)==718 and selectors[-1]=='tests.test_history_reference_review'
a=b"ADDITIONAL_MODULES += ('tests.test_relic_display_images_review',)";assert (R/'scripts/verify_full_available.py').read_bytes()==old('scripts/verify_full_available.py').replace(a,a+b"\r\n\r\nADDITIONAL_MODULES += ('tests.test_history_reference_review',)")
assert read('CLOUD_INDEX.json')['requirements']['sha256']==pin('PROJECT_REQUIREMENTS.md')['sha256']
write(prefix+'final-audit.json',{'passed':True,'baseline_commit':BASE,'summary':pin(prefix+'summary.json'),'requirements':pin('PROJECT_REQUIREMENTS.md'),'cloud_index':pin('CLOUD_INDEX.json'),'different_tests':58,'native_checks':22,'ordered_selectors':718,'whole_program_complete':False,'whole_video_parity_complete':False,'at_UTC':datetime.now(timezone.utc).isoformat()})
(B/'record-source.py').write_bytes(Path(__file__).read_bytes())
files={p.relative_to(R).as_posix():{k:v for k,v in pin(p.relative_to(R)).items()if k!='path'}for p in sorted(B.rglob('*'))if p.is_file()and p.name!='archive-manifest.json'}
write(prefix+'archive-manifest.json',{'kind':'explicit_public_archive','files':files})
print(json.dumps({'passed':True,'different_tests':58,'native_checks':22,'final_images':5,'archive_files':len(files),'whole_goal_complete':False}))
