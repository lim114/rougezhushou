def check(window,gui,require):
 from copy import deepcopy
 from .player_replay_archive import reload_history
 from tests.test_player_feature_430 import scene_state
 before=deepcopy(window.run.state)
 try:
  window.show_compact();compact=window.compact_window;compact.open_replay();p=compact.replay_popup.panel
  archive=deepcopy(before);archive.update(scene_state());archive['id']='isolated-recorded-scene';p.history_store.archive(archive);reload_history(p)
  p.sessions.setCurrentIndex(p.sessions.findData('archive:'+archive['id']));p.entries.setCurrentRow(0);gui.processEvents()
  require(p.scene_button.isVisible(),'qualified_historical_content_has_reference_navigation')
  require(p.open_selected_scene(),'historical_scene_opens_detached_reader');gui.processEvents();reader=p.scene_popup.panel
  require(reader.event_choices.count()>=2 and reader.notice.text().startswith('历史记录：'),'history_reader_is_explicitly_not_current_scene')
  reader.event_choices.setCurrentIndex(1);reader.event_entries.setCurrentIndex(1);gui.processEvents()
  require(reader.open_event(),'historical_event_can_open_exact_documented_flow');gui.processEvents();target=reader._target()
  require(reader.event_dialog.panel.scene_id==target['scene_id'],'history_flow_keeps_exact_scene_identity')
  require(window.run.state==before,'history_reference_navigation_does_not_restore_game_state')
  reader.event_dialog.close();entry=reader.event_entries.currentData();p.refresh();gui.processEvents()
  require(reader.event_entries.currentData()==entry,'unchanged_history_refresh_preserves_scene_reading')
  p.sessions.setCurrentIndex(0);gui.processEvents();require(p.scene_popup is None,'changing_history_session_closes_owned_scene_reader')
  p.sessions.setCurrentIndex(p.sessions.findData('archive:'+archive['id']));p.entries.setCurrentRow(0);p.open_selected_scene();gui.processEvents()
  window.player_validation_target=p.scene_popup
 finally:window.run.state=before
