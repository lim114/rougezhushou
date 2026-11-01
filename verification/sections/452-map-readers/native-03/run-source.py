from pathlib import Path
from hashlib import sha256
from copy import deepcopy
import sys,json,subprocess,traceback
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts')];out=R/'verification/sections/452-map-readers/native-03'
if len(sys.argv)==1:
 out.mkdir(exist_ok=False)
 with(out/'stdout.txt').open('xb')as a,(out/'stderr.txt').open('xb')as b:
  child=subprocess.Popen([sys.executable,'-B','-X','utf8',__file__,'child'],cwd=R,stdout=a,stderr=b);print({'actual_retained_PID':child.pid},flush=True);code=child.wait()
 (out/'process.json').write_text(json.dumps({'actual_retained_PID':child.pid,'actual_observed_exit':code},indent=2)+'\n','utf8');(out/'run-source.py').write_bytes(Path(__file__).read_bytes());print({'actual_exit':code});raise SystemExit(code)
from PySide6.QtCore import Qt,QPoint,QTimer
from PySide6.QtTest import QTest
from rouge import player_acceptance,player_map_acceptance as acceptance,public_event_samples as model
import player_ui_verification as ui
data_paths=['rouge/player_reference_window.py','rouge/player_map.py','rouge/player_map_reader.py','rouge/current_node_readers_view.py','rouge/player_compact.py','tests/test_map_reader_host_452.py'];data_before={n:sha256((R/n).read_bytes()).hexdigest()for n in data_paths};(out/'additional-source-before.json').write_text(json.dumps(data_before,indent=2)+'\n','utf8')
errors=[]
def hook(kind,value,tb):errors.append(str(value));traceback.print_exception(kind,value,tb)
sys.excepthook=hook
def check(section,window,gui,require):
 from unittest.mock import patch
 from PySide6.QtGui import QTextCursor
 import win32gui
 before=deepcopy(window.run.state);graphs,candidate,passed,known=acceptance.fixtures();old_graph=deepcopy(window.map_view.graph);old_historical=window.map_view.historical
 window.run.state['maps']={g['zone_id']:g for g in graphs};window.show_compact();c=window.compact_window
 for timer in window.findChildren(QTimer):timer.stop()
 c.open_map();gui.processEvents();host=c.reference_window;handle=int(host.winId());p=c.map_popup.panel;images=[]
 def save(name):
  path=out/(name+'.png');require(host.grab().save(str(path)),name+'_saved');images.append({'file':path.relative_to(R).as_posix(),'sha256':sha256(path.read_bytes()).hexdigest()})
 def select(kind,identity=None):
  key=next(k for k in p.rows if k[1]==kind and (identity is None or k[2]==identity))
  for i in range(p.entries.topLevelItemCount()):
   root=p.entries.topLevelItem(i)
   for j in range(root.childCount()):
    item=root.child(j)
    if item.data(0,Qt.ItemDataRole.UserRole)==key:
     p.entries.setCurrentItem(item);gui.processEvents();return key
  raise AssertionError('Exact map entry not in visible source tree')
 p.view.select_node(candidate);gui.processEvents();select('event','community_group_000');require(p.open_entry(),'map452_exact_event_open');gui.processEvents();page=p.reference_popup;require(page is not None and page.window() is host and not page.isWindow(),'map452_event_in_same_native_host');require(int(host.winId())==handle,'map452_event_same_handle');require(p.reference_binding==p.reader_binding(),'map452_event_exact_map_binding');require('桑尼'in page.windowTitle(),'map452_event_chinese_title');require(page.node_reference_binding['expected_summary']['id']=='community_group_000','map452_event_provider_binding_exact');require(page.node_reference_banner.isVisible(),'map452_event_scope_banner_visible')
 flow=page.panel;flow.choices.setCurrentRow(0);flow.tabs.setCurrentWidget(flow.player);cursor=flow.player.textCursor();cursor.setPosition(3);cursor.setPosition(12,QTextCursor.MoveMode.KeepAnchor);flow.player.setTextCursor(cursor);reading=(flow.scene_id,flow.choice_id,flow.player.toPlainText(),cursor.anchor(),cursor.position());save('event-in-main-window')
 QTest.mouseClick(host.back,Qt.MouseButton.LeftButton);gui.processEvents();require(p.isVisible() and not page.isVisible(),'map452_back_returns_map_only');require(p.selected_reference[2]=='community_group_000','map452_back_keeps_selected_event');require(p.reference_popup is page,'map452_back_retains_source_reader')
 QTest.mouseClick(host.forward,Qt.MouseButton.LeftButton);gui.processEvents();cursor=flow.player.textCursor();require(c.active_popup is page and page.isVisible(),'map452_forward_returns_same_event_page');require((flow.scene_id,flow.choice_id,flow.player.toPlainText(),cursor.anchor(),cursor.position())==reading,'map452_same_source_preserves_full_event_reading');require(int(host.winId())==handle,'map452_forward_keeps_native_handle');c.refresh();gui.processEvents();require(p.reference_popup is page and page.isVisible(),'map452_live_refresh_keeps_matching_source')
 with patch('rouge.current_resource_events.reference',return_value=None):
  c.refresh();gui.processEvents();require(p.reference_popup is None,'map452_lost_event_source_clears_binding');require(page not in host.history,'map452_lost_source_removed_from_both_navigation_directions');require(c.active_popup is c.map_popup and p.isVisible(),'map452_lost_source_returns_map');require(not host.forward.isEnabled(),'map452_lost_source_cannot_be_reopened_by_forward')
 node=next(n['id']for n in graphs[0]['nodes']if n.get('template_type')=='作战');p.view.select_node(node);gui.processEvents();key=select('battle');stage=p.rows[key]['id'];require(p.open_entry(),'map452_exact_battle_open');gui.processEvents();battle=p.reference_popup;require(battle is not None and battle.panel.stage_id==stage and battle.panel.result is not None,'map452_battle_exact_stage_identity');require(battle.window() is host and int(host.winId())==handle,'map452_battle_same_native_host');battle.panel.tabs.setCurrentIndex(1);save('battle-in-main-window')
 QTest.mouseClick(host.back,Qt.MouseButton.LeftButton);gui.processEvents();require(p.isVisible() and p.reference_popup is battle,'map452_battle_back_keeps_exact_reader');QTest.mouseClick(host.forward,Qt.MouseButton.LeftButton);gui.processEvents();require(battle.panel.tabs.currentIndex()==1 and battle.isVisible(),'map452_battle_enemy_tab_retained')
 c.open_recent_notes();gui.processEvents();require(c.recent_notes_popup.isVisible(),'map452_another_main_page_open');p.close_reference();gui.processEvents();require(c.recent_notes_popup.isVisible() and host.isVisible(),'map452_invalidating_hidden_reader_keeps_other_main_page_visible');require(battle not in host.history,'map452_hidden_reader_removed_from_history')
 c.open_map();p.view.select_node(candidate);gui.processEvents();select('event','community_group_000');require(p.open_entry(),'map452_event_reopens_from_fresh_binding');gui.processEvents();fresh=p.reference_popup;host.setProperty('playerSuspended',True);host.hide();require(not host.isVisible(),'map452_temporarily_hidden')
 with patch('rouge.current_resource_events.reference',return_value=None):
  host.show();gui.processEvents();require(p.reference_popup is None and p.isVisible(),'map452_restore_rechecks_source_before_retained_reader');require(fresh not in host.history,'map452_restore_discards_invalid_navigation')
 host.setProperty('playerSuspended',False)
 p.view.select_node(candidate);gui.processEvents();select('event','community_group_000');require(p.open_entry(),'map452_fresh_event_after_source_recovery');gui.processEvents();fresh=p.reference_popup;window.run.state={**deepcopy(before),'id':'isolated-manual-new-run452','maps':{}};c.refresh();gui.processEvents();require(p.reference_popup is None and fresh not in host.history,'map452_manual_new_run_invalidates_bound_page');require(p.selected_reference is None and not p.rows,'map452_manual_new_run_clears_old_node_entry');require(p.isVisible(),'map452_manual_new_run_shows_empty_map_not_old_reader');save('new-run-clears-old-reader')
 require(not errors,'map452_no_Qt_slot_exception');require(all(w is host or w is c or not w.isVisible()for w in gui.topLevelWidgets()),'map452_only_one_visible_main_reference_window')
 window.run.state=before;window.map_view.set_map(old_graph,historical=old_historical);window.player_validation_target=host
 (out/'images.json').write_text(json.dumps({'images':images,'public_fixtures_only':True,'actual_game_or_whole_video_parity':False},indent=2)+'\n','utf8')

player_acceptance.check=check
raise SystemExit(ui.run(452,out/'window.json'))

