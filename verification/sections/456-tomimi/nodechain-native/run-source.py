from pathlib import Path
from hashlib import sha256
from copy import deepcopy
import sys,json,subprocess,traceback
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts')];out=R/'verification/sections/456-tomimi/nodechain-native'
if len(sys.argv)==1:
 out.mkdir(exist_ok=False)
 with(out/'stdout.txt').open('xb')as a,(out/'stderr.txt').open('xb')as b:
  child=subprocess.Popen([sys.executable,'-B','-X','utf8',__file__,'child'],cwd=R,stdout=a,stderr=b);print({'actual_retained_PID':child.pid},flush=True);code=child.wait()
 (out/'process.json').write_text(json.dumps({'actual_retained_PID':child.pid,'actual_observed_exit':code},indent=2)+'\n','utf8');(out/'run-source.py').write_bytes(Path(__file__).read_bytes());print({'actual_exit':code});raise SystemExit(code)
from PySide6.QtCore import Qt,QPoint,QTimer
from PySide6.QtTest import QTest
from rouge import player_acceptance,player_map_acceptance as acceptance,public_event_samples as model
import player_ui_verification as ui
data_paths=['rouge/data/tomimi-stage-links.json','rouge/player_reference_links.py','rouge/current_battle_view.py','rouge/current_event_battles_view.py','rouge/reference_copy.py','tests/test_reverse_events_455.py'];data_before={n:sha256((R/n).read_bytes()).hexdigest()for n in data_paths};(out/'additional-source-before.json').write_text(json.dumps(data_before,indent=2)+'\n','utf8')
errors=[]
def hook(kind,value,tb):errors.append(str(value));traceback.print_exception(kind,value,tb)
sys.excepthook=hook

def check(section,window,gui,require):
 from unittest.mock import patch
 from rouge.player_map_reader import make_reader
 from rouge import current_event_battles as battles
 before=deepcopy(window.run.state);graphs,candidate,passed,known=acceptance.fixtures();old_graph=deepcopy(window.map_view.graph);old_historical=window.map_view.historical
 node=next(n for n in graphs[0]['nodes']if n['id']==candidate);node.update(observed_type='林间空地',remembered_type='不期而遇',remembered_content={'kind':'event','title':'黑诞'})
 window.run.state['maps']={g['zone_id']:g for g in graphs};window.show_compact();c=window.compact_window
 for timer in window.findChildren(QTimer):timer.stop()
 c.open_map();gui.processEvents();host=c.reference_window;handle=int(host.winId());p=c.map_popup.panel;p.view.select_node(candidate);gui.processEvents();key=next(k for k in p.rows if k[1:]==('event','community_group_008'))
 for i in range(p.entries.topLevelItemCount()):
  root=p.entries.topLevelItem(i)
  for j in range(root.childCount()):
   if root.child(j).data(0,Qt.ItemDataRole.UserRole)==key:p.entries.setCurrentItem(root.child(j))
 require(p.open_entry(),'history_node_opens_exact_encounter');gui.processEvents();source=p.reference_popup;flow=source.panel;cid=next(v['id']for v in flow.result['choices'].values()if'choice_ro6_normal2_2'in v['variant_ids'])
 flow.choices.setCurrentRow(next(i for i in range(flow.choices.count())if flow.choices.item(i).data(Qt.ItemDataRole.UserRole)==cid));cursor=flow.player.textCursor();cursor.setPosition(3);cursor.setPosition(12,cursor.MoveMode.KeepAnchor);flow.player.setTextCursor(cursor);selection=cursor.selectedText();images=[]
 def save(name):
  path=out/(name+'.png');require(host.grab().save(str(path)),name+'_saved');images.append({'file':path.relative_to(R).as_posix(),'sha256':sha256(path.read_bytes()).hexdigest()})
 QTest.mouseClick(flow.battle_button,Qt.MouseButton.LeftButton);gui.processEvents();config=host.pages.currentWidget();require(config.panel.stages.currentData()is None,'configuration_not_automatically_selected');config.panel.stages.setCurrentIndex(config.panel.stages.findData('ro6_t_13'));QTest.mouseClick(config.panel.open_button,Qt.MouseButton.LeftButton);gui.processEvents();stage=host.pages.currentWidget();require(stage.panel.stage_id=='ro6_t_13','exact_battle_selected')
 stage.panel.tabs.setCurrentIndex(0);stage.panel.map_details.expand(animate=False);gui.processEvents();stage.panel.overview_scroll.ensureWidgetVisible(stage.panel.event_origins_button);QTest.mouseClick(stage.panel.event_origins_button,Qt.MouseButton.LeftButton);gui.processEvents();origins=host.pages.currentWidget();require(origins is not stage and origins.source_parent is stage,'origins_button_opens_in_same_chain');require(origins.panel.stage_id=='ro6_t_13','reverse_lookup_keeps_exact_stage_filter');require(origins.panel.choice_id is None and origins.panel.stages.currentData()is None,'reverse_lookup_requires_choice_and_configuration');require(getattr(stage.panel,'event_origins_dialog',None)is None,'no_parallel_native_origin_dialog')
 origins.panel.choices.setCurrentRow(next(i for i in range(origins.panel.choices.count())if origins.panel.choices.item(i).data(Qt.ItemDataRole.UserRole)=='choice_ro6_normal2_2'));gui.processEvents();require('不是本局实际入口'not in origins.panel.player.toPlainText(),'short_default_summary');require('不是本局实际入口'in origins.panel.reference_notes.toPlainText(),'original_explanation_in_details');require(not origins.panel.scope.isExpanded(),'scope_initially_collapsed');require({r['id']for r in battles.stage_rows(origins.panel.result,origins.panel.choice_id)}=={'ro6_t_13'},'reverse_choice_lists_only_exact_configuration');require(origins.panel.choices.height()<2*origins.panel.choices.sizeHintForRow(0)+2*origins.panel.choices.frameWidth(),'single_option_list_has_no_large_blank_area');require(origins.panel.player.viewport().height()>=4*origins.panel.player.fontMetrics().lineSpacing(),'source_summary_has_readable_body');save('source-options-in-main-window')
 count=len(host.linked_pages);QTest.mouseClick(origins.panel.flow_button,Qt.MouseButton.LeftButton);gui.processEvents();require(host.pages.currentWidget()is source,'full_event_returns_to_existing_ancestor');require(flow.choice_id==cid and flow.player.textCursor().selectedText()==selection,'ancestor_event_keeps_exact_choice_and_reading');require(len(host.linked_pages)==count and source.source_parent is None,'no_duplicate_flow_or_parent_cycle')
 require(flow.open_battle(),'existing_configuration_reopens');gui.processEvents();require(host.pages.currentWidget()is config,'same_configuration_page_retained');require(config.panel.open_battle(),'existing_stage_reopens');gui.processEvents();require(host.pages.currentWidget()is stage,'same_stage_page_retained');require(stage.panel.open_event_origins(),'existing_origins_reopens');gui.processEvents();require(host.pages.currentWidget()is origins,'same_origin_page_retained');origins.panel.stages.setCurrentIndex(origins.panel.stages.findData('ro6_t_13'));QTest.mouseClick(origins.panel.open_button,Qt.MouseButton.LeftButton);gui.processEvents();require(host.pages.currentWidget()is stage and int(host.winId())==handle,'origin_configuration_returns_to_existing_stage');require(len(host.linked_pages)==count,'stage_return_does_not_duplicate_chain')
 lake_root=make_reader('battle',{'id':'ro6_e_t_5','title':'湖泊关联作战'},c,historical=True,page_owner=c);lake_root.prepare=lake_root.panel.refresh_reference;c.present(lake_root);require(lake_root.panel.open_event_origins(),'lake_stage_has_origin');gui.processEvents();lake_origins=host.pages.currentWidget();lake_origins.panel.choices.setCurrentRow(next(i for i in range(lake_origins.panel.choices.count())if lake_origins.panel.choices.item(i).data(Qt.ItemDataRole.UserRole)=='choice_ro6_bat5_9'));QTest.mouseClick(lake_origins.panel.flow_button,Qt.MouseButton.LeftButton);gui.processEvents();lake=host.pages.currentWidget();kind,target=lake_origins.panel._flow_target(lake_origins.panel.choice_id);require(kind=='lake'and lake.panel.scene_id==target['scene_id']and lake.panel.choice_id==target['choice_id'],'lake_opens_exact_phase_and_choice');require(lake.source_parent is lake_origins and lake.window()is host,'lake_shares_reference_host');require(lake.panel.choices.height()<2*lake.panel.choices.sizeHintForRow(0)+2*lake.panel.choices.frameWidth(),'single_lake_choice_has_no_large_blank_area');require(lake.panel.player.viewport().height()>=4*lake.panel.player.fontMetrics().lineSpacing(),'full_flow_has_readable_body');require('【范围与未知】'not in lake.panel.player.toPlainText()and'【范围与未知】'in lake.panel.reference_notes.toPlainText(),'flow_scope_moved_to_details');require(not lake.panel.reference_scope.isExpanded(),'flow_scope_initially_collapsed');save('full-lake-event-in-main-window')
 cursor=lake.panel.player.textCursor();cursor.setPosition(2);cursor.setPosition(10,cursor.MoveMode.KeepAnchor);lake.panel.player.setTextCursor(cursor);selection=cursor.selectedText();QTest.mouseClick(host.back,Qt.MouseButton.LeftButton);gui.processEvents();QTest.mouseClick(lake_origins.panel.flow_button,Qt.MouseButton.LeftButton);gui.processEvents();require(host.pages.currentWidget()is lake and lake.panel.player.textCursor().selectedText()==selection,'lake_reopen_keeps_reading')
 with patch('rouge.current_lake.reference',return_value=None):
  c.refresh();gui.processEvents();require(host.pages.currentWidget()is lake_origins and lake not in host.history,'lost_flow_returns_only_to_valid_origin')
 require(lake_origins.panel.open_full_flow(),'flow_recovers_from_fresh_reference');gui.processEvents();lake=host.pages.currentWidget();QTest.mouseClick(host.back,Qt.MouseButton.LeftButton);gui.processEvents();lake_origins.panel.choices.setCurrentRow(-1);QTest.mouseClick(host.forward,Qt.MouseButton.LeftButton);gui.processEvents();require(host.pages.currentWidget()is lake_origins and lake not in host.history,'changed_choice_removes_dependent_flow');save('unselected-origin-retains-parent')
 c.present(c.map_popup);host.discard(lake_root,fallback=c.map_popup);require(c.present(origins),'restore_map_bound_origin_chain')
 with patch('rouge.current_node_readers.recheck',return_value=None):
  c.refresh();gui.processEvents();require(p.reference_popup is None and host.pages.currentWidget()is c.map_popup,'lost_root_binding_returns_to_map');require(all(q not in host.history for q in(source,config,stage,origins))and not host.linked_pages,'root_loss_removes_reverse_and_forward_chain')
 require(int(host.winId())==handle,'all_pages_use_one_native_host');require(not errors,'no_Qt_slot_exceptions');require(all(w is host or w is c or not w.isVisible()for w in gui.topLevelWidgets()),'only_one_visible_reference_window');window.run.state=before;window.map_view.set_map(old_graph,historical=old_historical);window.player_validation_target=host
 (out/'images.json').write_text(json.dumps({'images':images,'public_fixtures_only':True,'scope':'Actual map->encounter->configuration->stage->source options->original event, and direct fixed-stage lake flow; exact sources and reading retained.'},ensure_ascii=False,indent=2)+'\n','utf8')

player_acceptance.check=check
raise SystemExit(ui.run(456,out/'window.json'))
