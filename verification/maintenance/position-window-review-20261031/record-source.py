from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import ast,ctypes,difflib,json,runpy,subprocess,sys,time
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts'),str(R/'.cache/305-window-tooldeps')]
BASE='53e1f6e1022d5caf92d334051734d16483582fe0';B=R/'verification/maintenance/position-window-review-20261031';prefix=B.relative_to(R).as_posix()+'/'
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
changed=['rouge/current_battle_view.py','rouge/current_action_positions_view.py']
baseline=['research/position-window-review-20261031/before-current-battle-view.py','research/position-window-review-20261031/before-current-action-positions-view.py']
for n,b in zip(changed,baseline):assert old(n)==(R/b).read_bytes()
untouched=['rouge/current_enemy_spawns.py','rouge/current_enemy_spawns_view.py','rouge/current_spawn_candidates.py','rouge/current_spawn_candidates_view.py','rouge/current_action_positions.py','rouge/current_map_position.py','rouge/current_map_position_view.py','rouge/current_battle_reference.py','rouge/current_route_itinerary_view.py','rouge/current_stage_objects_view.py','rouge/run_state.py','rouge/app.py','PROJECT_REQUIREMENTS.md']
for n in untouched:assert old(n)==(R/n).read_bytes(),n
assert not subprocess.check_output(['git','diff','--name-only',BASE,'--','rouge/data','research/runtime-reference-loaders-20261031']).strip()
def methods(raw,name):
 c=next(n for n in ast.parse(raw).body if isinstance(n,ast.ClassDef)and n.name==name)
 return {n.name:ast.dump(n,include_attributes=False)for n in c.body if isinstance(n,ast.FunctionDef)}
a=methods(old(changed[0]),'CurrentBattlePanel');b=methods((R/changed[0]).read_bytes(),'CurrentBattlePanel');edited={'_spawn_source_invalidated','_spawn_position_requested','open_action_positions','open_map_positions'}
assert a.keys()==b.keys()and all(a[n]==b[n]for n in a if n not in edited)
a=methods(old(changed[1]),'CurrentActionPositionsPanel');b=methods((R/changed[1]).read_bytes(),'CurrentActionPositionsPanel');assert set(b)-set(a)=={'set_reference'}and all(a[n]==b[n]for n in a if n!='refresh_reference')
suite=read(prefix+'tests-current/results.json');native=read(prefix+'native/window.json');failed=read(prefix+'tests/results.json')
assert suite['passed']and suite['tests_run']==70 and not suite['skipped']and not suite['forbidden_external_calls']
assert failed['tests_run']==70 and failed['failed']==1 and not failed['errors']and read(prefix+'tests/process.json')['actual_observed_exit']==1
assert native['passed']and native['unique_checks']==65 and not native['source_drift']and not any(native['external_operation_attempts'].values())
for folder in ['tests-current','native']:assert read(prefix+folder+'/process.json')['actual_observed_exit']==0
for n in changed:assert native['source_sha256_after'][n]==pin(n)['sha256']
(B/'native/verifier-source.py').write_bytes((R/'scripts/verify_position_window_review.py').read_bytes())
maintained=[]
for number,expected,script in [('319',30,'scripts/verify_current_map_position_window_319.py'),('320',25,'scripts/verify_current_action_positions_window_320.py')]:
 folder='retained-'+number;v=read(prefix+folder+'/window.json');assert v['passed']and v['unique_checks']==expected and v['qt_exit_code']==0 and v['verification_window_closed']and not any(v['external_operation_attempts'].values())
 assert read(prefix+folder+'/process.json')['actual_observed_exit']==0
 assert v['source_sha256_before']==v['source_sha256_after']
 for n in changed:assert v['source_sha256_after'][n]==pin(n)['sha256']
 (B/folder/'verifier-source.py').write_bytes((R/script).read_bytes());maintained.append(pin(prefix+folder+'/window.json'))
obs=read(prefix+'native/lifecycle-images.json')['observations'];assert obs=={'map_dialog_objects_after_three_reopens':1,'action_dialog_objects_after_three_reopens':1}
write(prefix+'source-review.json',{'baseline_commit':BASE,'changed_source':[pin(n)for n in changed],'verified_own_prior_source':[pin(n)for n in baseline],'unchanged_models_consumers_state_and_requirements':[pin(n)for n in untouched],'parent_existing_methods_retained':True,'edited_parent_methods':sorted(edited),'new_action_panel_method':'set_reference; clears old point on stage/action change before refreshing','verified_controlled_counts':{'three_map_opens':{'before_owned_dialogs':3,'after_owned_dialogs':1},'three_same_action_opens':{'before_owned_dialogs':3,'after_owned_dialogs':1}},'actual_native_observations':obs,'source_and_context_rules':'Fresh parent source gate remains. Same map/action reopening preserves reading; different action clears selected point even when source identities match. Shared action window detaches old candidate/enemy ownership before manual reuse, owned invalidation still clears/closes it.','evidence_limit':'Owned QObject counts only, not RSS, complete memory leak audit, elapsed-time speedup or all auxiliary windows. Prior parent executes with current unchanged child classes, not a whole historical app.','data_and_runtime_manifest_worktree_unchanged':True,'REA_scope':'Python complete source review per REA skill; prior actual REA evidence separate, no new REA call.','application_review_complete':False})
new_names=['map-window-reused','same-action-window-reused','changed-action-unselected','manual-reader-survives-old-source-loss','window'];reused=[]
for p in sorted((B/'native').glob('*.png')):
 if p.stem in new_names:continue
 old_image=R/'verification/maintenance/map-jump-review-20261031/native'/p.name;assert old_image.read_bytes()==p.read_bytes();reused.append({'current':pin(p.relative_to(R)),'identical_previously_individually_viewed':pin(old_image.relative_to(R))})
assert len(reused)==6
write(prefix+'image-review.json',{'reviewer':'/root','five_new_or_changed_originals_individually_loaded_with_view_image':[pin(prefix+'native/'+n+'.png')for n in new_names],'six_exact_byte_identical_originals_reuse_prior_visual_review':reused,'retained319_320_images_kept_as_interaction_evidence_not_all_newly_individually_viewed':True,'whole_video_parity_claimed':False})
live=read(prefix+'live-window/window.json');assert live['passed']and live['private_six_paths_unchanged']
import win32gui,win32process
for w in live['owned_windows']:assert win32gui.IsWindowVisible(w['hwnd'])and win32process.GetWindowThreadProcessId(w['hwnd'])[1]==w['pid']and not ctypes.windll.user32.IsHungAppWindow(w['hwnd'])
a=read('.cache/position-window-review-live-status.json');time.sleep(2.2);b=read('.cache/position-window-review-live-status.json');assert b['toolbar_visible']and b['elapsed_since_launch']>a['elapsed_since_launch']
for n in changed:assert live['source_sha256_after'][n]==pin(n)['sha256']
write(prefix+'live-window/desktop-review.json',{'actual_windows_mcp_snapshot_called':True,'actual_image_viewed':True,'region':[1716,1164,2130,1218],'owned_window_visible_and_responding':True,'Qt_timer_advanced':True,'private_six_paths_unchanged_during_startup':True,'private_contents_or_hashes_published':False,'game_operated':False,'chat_sent':False})
title='固定地图与出怪位置窗口复用，切换记录清旧位置并正确管理来源归属'
write(prefix+'summary.json',{'kind':'implementation_review_maintenance','title':title,'baseline_commit':BASE,'completed_sections':440,'functional_section_added':False,'implemented_scope_passed':True,'related_unique_tests':70,'test_receipt':pin(prefix+'tests-current/results.json'),'first_failed_old_replacement_assertion':pin(prefix+'tests/results.json'),'first_failure_not_whole_engine_source_freeze':True,'native_unique_checks':65,'native_receipt':pin(prefix+'native/window.json'),'maintained_native_receipts':maintained,'maintained_native_unique_checks_separate':[30,25],'overlapping_scopes_not_added':True,'source_review':pin(prefix+'source-review.json'),'image_review':pin(prefix+'image-review.json'),'live_window':pin(prefix+'live-window/desktop-review.json'),'application_review_complete':False,'video_parity_complete':False,'P3_complete':False,'P2_complete':False,'P1_complete':False,'full_validation_rerun':False,'full440_only_original_frozen_source':True,'private_data_included':False,'game_operated':False,'chat_sent':False,'publication_binding':'enclosing maintenance commit; ordinary push and actual remote/blob equality required'})
text('research/position-window-review-20261031/README.md','''# 固定地图与出怪位置窗口生命周期回顾

按REA技能对完整Python源码做源码/实际运行审查，本轮不新增REA调用；旧桥接和工具条的REA证据保持。检查发现固定地图与出怪位置入口重复构造Qt子窗，关闭只隐藏，父页面继续持有对象。实际执行自有旧父类和当前父类，分别连续打开三次：两种窗口均为旧3个→新1个。该对照使用当前未改的子窗类型，不是完整历史应用运行，也不是RSS测量或全程序内存结论。

保留一个地图窗和一个出怪位置窗，重开核对当前来源；同一记录保留阅读和选择。出怪位置面板增加set_reference，换关卡/条目先清旧点，refresh也检查准确条目身份，避免同一资料来源的另一出怪记录沿用旧“位置0”。没有改变数值、地图、等待参数、校准或本局。

共用出怪位置窗后，原来源不能仍拥有后来手动打开的资料。进入新入口先解除旧的敌人/候选组归属；由对应来源打开后再登记，失效时只清其当前拥有的窗口。实际候选组跳转、来源失效清理、手动重开和旧来源再次失效均验证；根窗口关闭仍关闭附属窗口。保护来源和私人状态的检查保持，没有因为概率低就删除。

70个不同相关测试通过，首轮70项有1项失败：原319测试仍要求“旧窗隐藏且新建替换”，现保留原关闭/来源失败断言并改为同实例可见。失败原件和Git原文保留；不是首轮整工程来源冻结。原生65项通过，另两份维护入口319/320分别30/25项通过，全部实际退出0，范围不相加。319/320沿用现有两层真实导航，数值、滚动/选择、来源失败及关闭范围保持；只将重复打开的窗口替换要求改为复用，不删验收。

五张新/变化原图逐张查看，六张原图经整字节一致复用上轮逐张审阅；319/320附加图只作交互原件，不冒称全部新审阅。实际测试小窗更新可见响应，计时推进，启动六处私人路径保持。其余辅助窗口对象释放、完整视频布局/地图路线/条件、机制准确与全程序回顾仍未完成；功能仍440，旧full440只对应原冻结来源，下一全量455，识别最后。
''')
for n,addition in {
 'PROGRAM_REVIEW.md':'[固定地图窗口生命周期回顾](research/position-window-review-20261031/README.md)实测两类窗口连续三次打开对象3→1，保留同记录阅读、切条目清旧点，修正共享位置窗的旧来源归属。70项相关测试/65项原生检查通过，319/320独立30/25项保持；其它辅助窗口、完整视频及全程序仍未完成。',
 'VIDEO_PARITY.md':'[固定地图窗口回顾](research/position-window-review-20261031/README.md)重复打开复用同一个已核对窗口并保留阅读，换出怪记录清除旧点；不会把先前候选来源的失效误用到后来手动资料。交互改善不表示已复现原片完整地图路径、折叠/表格或外观。',
 'IMPLEMENTATION_STRATEGY.md':'[固定地图窗口回顾](research/position-window-review-20261031/README.md)复用原Qt窗口/面板，不引入新控制器框架；三次打开旧3个→新1个是对象数对照，不等于RSS或端到端性能提升。必须按准确条目清理旧位置和登记当前来源归属，不能以简单隐藏或删除保护代替正确复用。'
}.items():text(n,(R/n).read_text('utf8')+'\n'+addition+'\n')
n='PROJECT_PROGRESS.md';t=(R/n).read_text('utf8');t=t.replace('重复开启附属资料窗的对象释放','其余附属资料窗的对象释放');text(n,t)
entry=f'''<!-- position-window-review-20261031:start -->
## 实现回顾维护 · {title}

连续三次打开固定地图/出怪位置，自有旧父类各保留3个对象→当前各1个；同记录重开保留阅读，切准确条目清旧点。当前来源归属重新登记，候选来源失效仍关其拥有的窗口，不误关后来手动打开的资料。未改模型/数据/本局，不称RSS、全程序内存或端到端提速。

70个不同相关测试、65项原生唯一检查通过；319/320维护入口另各30/25项通过，实际退出0，交叠不累计。首轮1项旧替换断言失败和原文保留，改为复用要求且原来源/关闭验收保持。5张新图逐张查看，6张整字节一致复用上轮，附加原件不冒称全新审阅。实际小窗更新响应，启动六处私人路径保持；功能440/未开441，全程序/视频/P3/P2/P1仍未完成，识别最后。回执：`{prefix}summary.json`。
<!-- position-window-review-20261031:end -->

'''
for n in ['WORK_IN_PROGRESS.md','PROJECT_COMPLETED.md']:text(n,entry+(R/n).read_text('utf8'))
cp=read('DEVELOPMENT_CHECKPOINT.json');cp['current_maintenance_save']={'kind':'implementation_review_maintenance','title':title,'receipt':prefix+'summary.json','binding':'enclosing_commit','functional_section_added':False,'status':'partial_program_review_bounded_position_windows_and_context_ownership','review_checklist':'PROGRAM_REVIEW.md','review_checklist_sha256':pin('PROGRAM_REVIEW.md')['sha256'],'application_review_complete':False};cp['current_batch']['receipt']=prefix+'summary.json';cp['next_action']='继续完整程序回顾：其余辅助资料窗的对象释放与准确来源归属、完整事件/固定作战资料、敌人完整折叠/表格/正文和视频几何、招募/强化/异常恢复连续场景与独立机制算例。固定地图/出怪位置窗口复用、切条目清旧点和当前来源归属已实测，不重复计推进；识别最后。'
text('DEVELOPMENT_CHECKPOINT.json',json.dumps(cp,ensure_ascii=False,indent=2)+'\n');module=runpy.run_path(str(R/'scripts/update_cloud_index.py'));module['update'](R);assert module['validate_delivery'](R,cp)['current_section']==440
from scripts.verify_full_available import maintained_selectors
selectors=maintained_selectors();assert len(selectors)==706 and selectors[-1]=='tests.test_position_window_review';assert read('CLOUD_INDEX.json')['requirements']['sha256']==pin('PROJECT_REQUIREMENTS.md')['sha256']
write(prefix+'final-audit.json',{'passed':True,'baseline_commit':BASE,'summary':pin(prefix+'summary.json'),'requirements':pin('PROJECT_REQUIREMENTS.md'),'cloud_index':pin('CLOUD_INDEX.json'),'ordered_selectors':706,'related_tests':70,'native_checks':65,'separate_maintained_native_checks':[30,25],'whole_program_complete':False,'whole_video_parity_complete':False,'at_UTC':datetime.now(timezone.utc).isoformat()})
(B/'record-source.py').write_bytes(Path(__file__).read_bytes());archive={p.relative_to(R).as_posix():{k:v for k,v in pin(p.relative_to(R)).items()if k!='path'}for p in sorted(B.rglob('*'))if p.is_file()and p.name!='archive-manifest.json'};write(prefix+'archive-manifest.json',{'kind':'explicit_public_archive','files':archive})
print(json.dumps({'passed':True,'related_tests':70,'native_checks':65,'separate_native':[30,25],'archive_files':len(archive),'goal_complete':False}))
