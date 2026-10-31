from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import ast,ctypes,difflib,json,runpy,subprocess,sys,time
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts'),str(R/'.cache/305-window-tooldeps')]
BASE='240aaaec87330d7044408da1f2ff65c0e585d620';B=R/'verification/maintenance/event-battle-reader-review-20261031';prefix=B.relative_to(R).as_posix()+'/'
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
changed=['rouge/current_event_battles_view.py'];prior='research/event-battle-reader-review-20261031/before-current-event-battles-view.py';assert old(changed[0])==(R/prior).read_bytes()
unchanged=['rouge/current_event_battles.py','rouge/current_battle_reference.py','rouge/current_battle_view.py','rouge/player_map_reader.py','rouge/current_encounters.py','rouge/current_lake.py','rouge/run_state.py','rouge/app.py','PROJECT_REQUIREMENTS.md']
for n in unchanged:assert old(n)==(R/n).read_bytes(),n
assert not subprocess.check_output(['git','diff','--name-only',BASE,'--','rouge/data','research/runtime-reference-loaders-20261031']).strip()
def methods(raw,name):
 c=next(n for n in ast.parse(raw).body if isinstance(n,ast.ClassDef)and n.name==name)
 return {n.name:ast.dump(n,include_attributes=False)for n in c.body if isinstance(n,ast.FunctionDef)}
a=methods(old(changed[0]),'CurrentEventBattlesPanel');b=methods((R/changed[0]).read_bytes(),'CurrentEventBattlesPanel');assert a.keys()==b.keys()and all(a[n]==b[n]for n in a if n not in {'_close_battle','open_battle'})
a=methods(old(changed[0]),'CurrentEventBattlesDialog');b=methods((R/changed[0]).read_bytes(),'CurrentEventBattlesDialog');assert set(b)-set(a)=={'reject'}and all(a[n]==b[n]for n in a)
suite=read(prefix+'tests/results.json');native=read(prefix+'native-current/window.json');failed=read(prefix+'native/window.json');comparisons=read(prefix+'tests/comparisons.json')['comparisons']
assert suite['passed']and suite['tests_run']==35 and not suite['skipped']and not suite['forbidden_external_calls']
assert native['passed']and native['unique_checks']==55 and not native['source_drift']and not any(native['external_operation_attempts'].values())
assert not failed['passed']and read(prefix+'native/process.json')['actual_observed_exit']==1 and 'all_six_documented_alternatives_retained'in failed['failure']
for folder in ['tests','native-current']:assert read(prefix+folder+'/process.json')['actual_observed_exit']==0
assert len(comparisons)==20 and len({c['stage_id']for c in comparisons})==17 and all(c['full_parent_and_child_reference_and_text_equal']for c in comparisons)
for n in changed:assert native['source_sha256_after'][n]==pin(n)['sha256']
(B/'native-current/verifier-source.py').write_bytes((R/'scripts/verify_event_battle_reader_review.py').read_bytes())
write(prefix+'source-review.json',{'baseline_commit':BASE,'changed_source':[pin(n)for n in changed],'prior_own_source':pin(prior),'unchanged_models_shared_factory_state_and_requirements':[pin(n)for n in unchanged],'edited_panel_methods':['_close_battle','open_battle'],'all_other_panel_methods_AST_unchanged':True,'original_dialog_methods_AST_unchanged_and_reject_added':True,'complete_source_and_text_replay':comparisons,'new_behavior':'Use existing shared frameless ToolPopover battle reader and scoped dark theme. Same exact stage refreshes and reuses one window; changed selection or unavailable source closes and deletes retired owned window. Dialog Escape/reject closes owned battle and full-flow.','preserved_boundaries':'Same event-reference equality and admitted-stage membership; no assumed actual stage or actual eligibility. Source loss clears and recovery requires original manual selection. Models, data, current run and selected parent reading unchanged.','allocation_evidence':'Three repeated native close/open cycles keep the identical window and perform one stage_reference per reopen. Old implementation constructs one new CurrentBattleDialog on every open by direct source. No CPU or latency improvement claimed.','first_native_failure':'Verifier passed parent window as positional stage_id when constructing secondary event dialog. Original failed source/receipt preserved; corrected to parent=window. Product code unchanged between attempts.','REA_scope':'Complete Python source reviewed directly per REA skill; no new REA invocation. Existing bridge/toolbar REA evidence separate.','application_review_complete':False})
images=[pin(p.relative_to(R))for p in sorted((B/'native-current').glob('*.png'))];assert len(images)==6
write(prefix+'image-review.json',{'reviewer':'/root','all_six_final_originals_individually_loaded_with_view_image':images,'failed_attempt_images_retained_but_not_counted_as_final_review':True,'scope':'Two actual shared battle pages, changed exact battle, event candidate source, source-recovery state and final emergency-only event entry. Existing large event list and text layout still differ from complete video goals.','whole_video_parity_claimed':False})
live=read(prefix+'live-window/window.json');assert live['passed']and live['private_six_paths_unchanged']
import win32gui,win32process
for w in live['owned_windows']:assert win32gui.IsWindowVisible(w['hwnd'])and win32process.GetWindowThreadProcessId(w['hwnd'])[1]==w['pid']and not ctypes.windll.user32.IsHungAppWindow(w['hwnd'])
a=read('.cache/event-battle-reader-review-live-status.json');time.sleep(2.2);b=read('.cache/event-battle-reader-review-live-status.json');assert b['toolbar_visible']and b['elapsed_since_launch']>a['elapsed_since_launch']
for n in changed:assert live['source_sha256_after'][n]==pin(n)['sha256']
write(prefix+'live-window/desktop-review.json',{'actual_windows_mcp_snapshot_called':True,'actual_image_viewed':True,'region':[1716,1164,2130,1218],'owned_window_visible_and_responding':True,'Qt_timer_advanced':True,'private_six_paths_unchanged_during_startup':True,'private_contents_or_hashes_published':False,'game_operated':False,'chat_sent':False})
title='事件作战入口复用紧凑资料窗，保留阅读并释放换关旧窗口'
write(prefix+'summary.json',{'kind':'implementation_review_maintenance','title':title,'baseline_commit':BASE,'completed_sections':440,'functional_section_added':False,'implemented_scope_passed':True,'related_unique_tests':35,'native_unique_checks':55,'fixed_choice_stage_links_compared':20,'distinct_exact_stage_ids':17,'source_review':pin(prefix+'source-review.json'),'test_receipt':pin(prefix+'tests/results.json'),'native_receipt':pin(prefix+'native-current/window.json'),'first_failed_verifier_receipt':pin(prefix+'native/window.json'),'image_review':pin(prefix+'image-review.json'),'live_window':pin(prefix+'live-window/desktop-review.json'),'application_review_complete':False,'video_parity_complete':False,'P3_complete':False,'P2_complete':False,'P1_complete':False,'full_validation_rerun':False,'full440_only_original_frozen_source':True,'private_data_included':False,'game_operated':False,'chat_sent':False,'publication_binding':'enclosing maintenance commit; ordinary push and actual remote/blob equality required'})
text('research/event-battle-reader-review-20261031/README.md','''# 事件到作战预览的窗口复用

按REA技能直接审查完整Python源码，本轮没有新REA调用。发现事件的具名选项仍另建CurrentBattleDialog，每次打开都新建对象，与地图和最近场景已用的共享阅读窗不同。现直接复用player_map_reader.make_reader和原四类资料页：深色、无系统边框、可拖动/缩放与关闭；没有新建窗口框架或改动模型。

同一准确关卡再次打开刷新原对象，保留仍有效的奖励/来源和阅读页，重新载入关闭时清掉的结算基础资料。更换选项/关卡、失去来源或关闭父页时，关闭并deleteLater释放旧窗口；实际DeferredDelete后对象失效已核验。父对话框Escape/reject也关闭附属作战和完整对话。保留原事件来源整份对照、允许关卡集合、默认不选本局版本、失效清理与恢复后手选，不因精简而删除资料准确性保护。

执行自有原事件面板和新面板，12个选项中的20条作战对应（17份不同配置）完整父资料/双正文、关卡/奖励/结算资料一致；这只覆盖原具名对应，不是全部事件或当前游戏完整目录。35项不同相关测试（事件作战、完整不期而遇、湖中仙女、共享阅读窗）及55项原生检查实际退出0，无跳过。实际按钮、键盘切换、关闭、准确来源反查、三次同对象重开/每次一份关卡刷新、奖励选择、非零滚动选区、旧对象释放和失效恢复已核对。没有将同对象复用说成实测速度提升。

首轮验收脚本把父窗口位置参数误传为stage_id，产生错误范围，原脚本和失败回执保留；修正parent=window后通过，产品源码在两次原生检查间未变。六张最终原生原图均逐张查看，首轮原图不算最终审阅。真实项目小窗已更新响应，Qt计时推进，启动期间六处私人路径不变，只公开布尔结果；没有游戏操作、真实聊天或个人上传。

模型/数据/来源声明和项目要求未变，应用源码仍535份。原事件列表的大块空白、长正文、其余窗口释放、完整折叠/表格/跨屏与全片交互仍未完成；本轮只统一事件到作战的入口效果，不冒称全视频一致。全程序、P3/P2/P1未完成，识别最后，功能440/未开441，full440仅原冻结源码。下一步继续未审机制资料窗、连续状态和真正的视频差距，不重复计入已关闭事项。
''')
n='PROGRAM_REVIEW.md';t=(R/n).read_text('utf8');t+='\n[事件到作战窗口回顾](research/event-battle-reader-review-20261031/README.md)复用地图/最近场景的紧凑资料窗，保留同关阅读、释放换关旧对象并补Escape清理；20条具名对应/17份配置完整资料一致，35项相关测试/55项原生检查通过。其它窗口、完整资料和视频/全程序仍未完成。\n';text(n,t)
for n,addition in {
 'VIDEO_PARITY.md':'[事件作战阅读窗回顾](research/event-battle-reader-review-20261031/README.md)使具名事件入口直接复用地图/最近场景的深色无边框预览和四组原资料，同关阅读保留、换关释放旧窗，55项原生检查和六张最终原图核对。事件列表的大块空白/长正文及其它页面仍与完整目标有差距，不称全片一致。',
 'IMPLEMENTATION_STRATEGY.md':'[事件作战入口回顾](research/event-battle-reader-review-20261031/README.md)直接复用已验证make_reader，替换另一套窗口构造；同关刷新复用、换关失效释放，保持原准确来源门槛和完整模型。三次重开原对象/单份刷新有实际证据，未声称速度或全程序正确性。'
}.items():text(n,(R/n).read_text('utf8')+'\n'+addition+'\n')
entry=f'''<!-- event-battle-reader-review-20261031:start -->
## 实现回顾维护 · {title}

事件到作战入口复用现有深色无边框资料窗和四组原内容，同关重开保留奖励/来源与阅读、恢复结算基础资料；换关或来源失效关闭并延迟释放旧窗口，Escape清理附属资料。20条具名对应/17份配置的新旧完整父子资料一致，35项相关测试/55项原生检查真实退出0；首轮验收脚本参数误传原件保留。六张最终原图逐张查看，实际项目小窗更新响应，启动六处私人路径保持。回执：`{prefix}summary.json`。

不是当前完整游戏目录或独立机制校准；其它阅读器、事件页排版及全程序/全视频仍未完成。功能440/未开441，P3/P2/P1未完成，识别最后。
<!-- event-battle-reader-review-20261031:end -->

'''
for n in ['WORK_IN_PROGRESS.md','PROJECT_COMPLETED.md']:text(n,entry+(R/n).read_text('utf8'))
cp=read('DEVELOPMENT_CHECKPOINT.json');cp['current_maintenance_save']={'kind':'implementation_review_maintenance','title':title,'receipt':prefix+'summary.json','binding':'enclosing_commit','functional_section_added':False,'status':'partial_program_review_shared_event_battle_reader','review_checklist':'PROGRAM_REVIEW.md','review_checklist_sha256':pin('PROGRAM_REVIEW.md')['sha256'],'application_review_complete':False};cp['current_batch']['receipt']=prefix+'summary.json';cp['next_action']='继续完整程序回顾：其余机制资料窗的实际差异和对象释放、事件列表/正文紧凑排版、完整视频折叠/表格/几何与独立机制证据；同局招募/强化/异常恢复和其它未审字段继续保留。事件到作战已共享原阅读窗及换关释放，不重复计推进；识别最后。'
text('DEVELOPMENT_CHECKPOINT.json',json.dumps(cp,ensure_ascii=False,indent=2)+'\n');module=runpy.run_path(str(R/'scripts/update_cloud_index.py'));module['update'](R);assert module['validate_delivery'](R,cp)['current_section']==440
from scripts.verify_full_available import maintained_selectors
selectors=maintained_selectors();assert len(selectors)==709 and selectors[-1]=='tests.test_event_battle_reader_review';assert read('CLOUD_INDEX.json')['requirements']['sha256']==pin('PROJECT_REQUIREMENTS.md')['sha256']
tracked={p for p in subprocess.check_output(['git','ls-files','rouge']).decode('utf8').splitlines()if p.endswith(('.py','.cjs','.js'))};assert len(tracked)==535
write(prefix+'final-audit.json',{'passed':True,'baseline_commit':BASE,'summary':pin(prefix+'summary.json'),'requirements':pin('PROJECT_REQUIREMENTS.md'),'cloud_index':pin('CLOUD_INDEX.json'),'ordered_selectors':709,'application_source_files':535,'related_tests':35,'native_checks':55,'whole_program_complete':False,'whole_video_parity_complete':False,'at_UTC':datetime.now(timezone.utc).isoformat()})
(B/'record-source.py').write_bytes(Path(__file__).read_bytes());archive={p.relative_to(R).as_posix():{k:v for k,v in pin(p.relative_to(R)).items()if k!='path'}for p in sorted(B.rglob('*'))if p.is_file()and p.name!='archive-manifest.json'};write(prefix+'archive-manifest.json',{'kind':'explicit_public_archive','files':archive})
print(json.dumps({'passed':True,'related_tests':35,'native_checks':55,'archive_files':len(archive),'goal_complete':False}))
