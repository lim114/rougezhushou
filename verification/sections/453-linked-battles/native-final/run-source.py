from pathlib import Path
from hashlib import sha256
from copy import deepcopy
import sys,json,subprocess,traceback
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts')];out=R/'verification/sections/453-linked-battles/native-final'
if len(sys.argv)==1:
 out.mkdir(exist_ok=False)
 with(out/'stdout.txt').open('xb')as a,(out/'stderr.txt').open('xb')as b:
  child=subprocess.Popen([sys.executable,'-B','-X','utf8',__file__,'child'],cwd=R,stdout=a,stderr=b);print({'actual_retained_PID':child.pid},flush=True);code=child.wait()
 (out/'process.json').write_text(json.dumps({'actual_retained_PID':child.pid,'actual_observed_exit':code},indent=2)+'\n','utf8');(out/'run-source.py').write_bytes(Path(__file__).read_bytes());print({'actual_exit':code});raise SystemExit(code)
from PySide6.QtCore import Qt,QPoint,QTimer
from PySide6.QtTest import QTest
from rouge import player_acceptance,player_map_acceptance as acceptance,public_event_samples as model
import player_ui_verification as ui
data_paths=['rouge/player_reference_links.py','rouge/player_reference_window.py','rouge/player_compact.py','rouge/documented_event_flow_view.py','rouge/current_encounters_view.py','rouge/current_lake_view.py','rouge/current_event_battles_view.py','rouge/current_ritual_view.py','tests/test_linked_battles_453.py'];data_before={n:sha256((R/n).read_bytes()).hexdigest()for n in data_paths};(out/'additional-source-before.json').write_text(json.dumps(data_before,indent=2)+'\n','utf8')
errors=[]
def hook(kind,value,tb):errors.append(str(value));traceback.print_exception(kind,value,tb)
sys.excepthook=hook
def check(section,window,gui,require):
 from unittest.mock import patch
 from PySide6.QtGui import QTextCursor
 before=deepcopy(window.run.state);graphs,candidate,passed,known=acceptance.fixtures();old_graph=deepcopy(window.map_view.graph);old_historical=window.map_view.historical
 node=next(n for n in graphs[0]['nodes']if n['id']==candidate);node.update(observed_type='林间空地',remembered_type='不期而遇',remembered_content={'kind':'event','title':'黑诞'})
 window.run.state['maps']={g['zone_id']:g for g in graphs};window.show_compact();c=window.compact_window
 for timer in window.findChildren(QTimer):timer.stop()
 c.open_map();gui.processEvents();host=c.reference_window;handle=int(host.winId());p=c.map_popup.panel;p.view.select_node(candidate);gui.processEvents();key=next(k for k in p.rows if k[1:] == ('event','community_group_008'))
 for i in range(p.entries.topLevelItemCount()):
  root=p.entries.topLevelItem(i)
  for j in range(root.childCount()):
   if root.child(j).data(0,Qt.ItemDataRole.UserRole)==key:p.entries.setCurrentItem(root.child(j))
 require(p.open_entry(),'links453_history_node_exact_event_open');gui.processEvents();source=p.reference_popup;flow=source.panel;flow.controller.setCurrentIndex(flow.controller.findData(True));cid=next(v['id']for v in flow.result['choices'].values()if 'choice_ro6_normal2_2'in v['variant_ids']);flow.choices.setCurrentRow(next(i for i in range(flow.choices.count())if flow.choices.item(i).data(Qt.ItemDataRole.UserRole)==cid));gui.processEvents();reading=flow.player.toPlainText();images=[]
 def save(name):
  path=out/(name+'.png');require(host.grab().save(str(path)),name+'_saved');images.append({'file':path.relative_to(R).as_posix(),'sha256':sha256(path.read_bytes()).hexdigest()})
 require(flow.open_battle(),'links453_event_opens_configurations');gui.processEvents();config=host.pages.currentWidget();require(config.source_parent is source and config.window() is host,'links453_configuration_parent_and_same_host');require(config.panel.stages.currentData() is None,'links453_no_default_actual_stage');require(not config.panel.open_battle(),'links453_no_stage_open_before_player_selects');save('configurations-in-main-window')
 config.panel.stages.setCurrentIndex(config.panel.stages.findData('ro6_t_13'));require(config.panel.open_battle(),'links453_selected_fixed_stage_opens');gui.processEvents();stage=host.pages.currentWidget();require(stage.panel.stage_id=='ro6_t_13'and stage.panel.result['id']=='ro6_t_13','links453_exact_requested_stage_result');require(stage.source_parent is config and int(host.winId())==handle,'links453_nested_stage_same_native_host');require(flow.battle_dialog is None and config.panel.battle_dialog is None,'links453_no_parallel_native_child_dialogs');stage.panel.tabs.setCurrentIndex(0);save('linked-stage-in-main-window')
 QTest.mouseClick(host.back,Qt.MouseButton.LeftButton);gui.processEvents();require(host.pages.currentWidget() is config and config.panel.stages.currentData()=='ro6_t_13','links453_back_keeps_configuration_selection');QTest.mouseClick(host.back,Qt.MouseButton.LeftButton);gui.processEvents();require(host.pages.currentWidget() is source and flow.choice_id==cid and flow.player.toPlainText()==reading,'links453_back_keeps_event_choice_and_text')
 require(flow.open_battle(),'links453_repeat_event_link_open');gui.processEvents();require(host.pages.currentWidget() is config,'links453_repeat_open_reuses_same_reader');require(config.panel.open_battle(),'links453_repeat_stage_link_open');gui.processEvents();require(host.pages.currentWidget() is stage,'links453_repeat_stage_preserves_reader');host.setProperty('playerSuspended',True);host.hide();host.show();host.setProperty('playerSuspended',False);gui.processEvents();require(host.pages.currentWidget() is stage and stage.isVisible(),'links453_suspend_restore_requalifies_same_dependent_chain');c.refresh();gui.processEvents();require(host.pages.currentWidget() is stage and stage.isVisible(),'links453_same_source_live_refresh_retains_nested_reader')
 with patch('rouge.current_battle_reference.stage_reference',return_value=None):
  c.refresh();gui.processEvents();require(stage not in host.history and host.pages.currentWidget() is config,'links453_lost_child_source_returns_only_to_valid_parent');require(p.reference_popup is source and source in host.history,'links453_lost_child_keeps_valid_root_event')
 require(config.panel.open_battle(),'links453_stage_recovers_with_fresh_reference');gui.processEvents();stage=host.pages.currentWidget();QTest.mouseClick(host.back,Qt.MouseButton.LeftButton);QTest.mouseClick(host.back,Qt.MouseButton.LeftButton);gui.processEvents();require(host.pages.currentWidget() is source,'links453_root_event_for_condition_change');flow.controller.setCurrentIndex(flow.controller.findData(False));QTest.mouseClick(host.forward,Qt.MouseButton.LeftButton);gui.processEvents();require(host.pages.currentWidget() is config,'links453_unrelated_condition_keeps_valid_configuration');QTest.mouseClick(host.back,Qt.MouseButton.LeftButton);gui.processEvents();other=next(flow.choices.item(i).data(Qt.ItemDataRole.UserRole)for i in range(flow.choices.count())if flow.choices.item(i).data(Qt.ItemDataRole.UserRole)!=cid);flow.choices.setCurrentRow(next(i for i in range(flow.choices.count())if flow.choices.item(i).data(Qt.ItemDataRole.UserRole)==other));QTest.mouseClick(host.forward,Qt.MouseButton.LeftButton);gui.processEvents();require(host.pages.currentWidget() is source,'links453_changed_choice_keeps_current_event');require(config not in host.history and stage not in host.history,'links453_changed_parent_choice_removes_entire_dependent_chain');require(not host.forward.isEnabled(),'links453_expired_dependent_chain_cannot_be_forwarded')
 flow.controller.setCurrentIndex(flow.controller.findData(True));flow.choices.setCurrentRow(next(i for i in range(flow.choices.count())if flow.choices.item(i).data(Qt.ItemDataRole.UserRole)==cid));require(flow.open_battle(),'links453_choice_recovery_new_configuration');gui.processEvents();config=host.pages.currentWidget();require(config.panel.stages.currentData() is None,'links453_recovered_configuration_requires_new_selection');config.panel.stages.setCurrentIndex(config.panel.stages.findData('ro6_t_13'));require(config.panel.open_battle(),'links453_new_stage_after_condition_recovery');gui.processEvents();stage=host.pages.currentWidget()
 with patch('rouge.current_node_readers.recheck',return_value=None):
  c.refresh();gui.processEvents();require(p.reference_popup is None and host.pages.currentWidget() is c.map_popup,'links453_lost_root_mapping_returns_map');require(all(q not in host.history for q in(source,config,stage))and not host.linked_pages,'links453_lost_root_mapping_clears_all_dependent_navigation')
 require(p.open_entry(),'links453_root_recovers_for_new_run_case');gui.processEvents();source=p.reference_popup;flow=source.panel;flow.controller.setCurrentIndex(flow.controller.findData(True));flow.choices.setCurrentRow(next(i for i in range(flow.choices.count())if flow.choices.item(i).data(Qt.ItemDataRole.UserRole)==cid));require(flow.open_battle(),'links453_configuration_recovers_for_new_run');gui.processEvents();config=host.pages.currentWidget();config.panel.stages.setCurrentIndex(config.panel.stages.findData('ro6_t_13'));require(config.panel.open_battle(),'links453_stage_recovers_for_new_run');gui.processEvents();stage=host.pages.currentWidget();window.run.state={**deepcopy(before),'id':'isolated-manual-new-run453','maps':{}};c.refresh();gui.processEvents();require(p.reference_popup is None and not host.linked_pages,'links453_new_run_clears_dependent_registry');require(all(q not in host.history for q in(source,config,stage))and host.pages.currentWidget() is c.map_popup,'links453_new_run_removes_all_dependent_history');save('new-run-clears-linked-chain')
 require(not errors,'links453_no_Qt_slot_exceptions');require(all(w is host or w is c or not w.isVisible()for w in gui.topLevelWidgets()),'links453_only_one_visible_main_reference_window');require(window.run.state=={**before,'id':'isolated-manual-new-run453','maps':{}},'links453_only_explicit_isolated_new_run_changes_state');save('invalidated-chain-returns-map')
 window.run.state=before;window.map_view.set_map(old_graph,historical=old_historical);window.player_validation_target=host
 (out/'images.json').write_text(json.dumps({'images':images,'public_fixtures_only':True,'actual_game_or_whole_video_parity':False},indent=2)+'\n','utf8')

player_acceptance.check=check
raise SystemExit(ui.run(453,out/'window.json'))

