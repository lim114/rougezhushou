def check(window,gui,require):
 from copy import deepcopy
 from unittest.mock import patch
 before=deepcopy(window.run.state)
 try:
  window.run.state['last_node_content']={'kind':'event','title':'桑尼的邀请'}
  window.show_compact();compact=window.compact_window;compact.scene_button.click();gui.processEvents();p=compact.scene_popup.panel
  require(compact.scene_popup.isVisible()and p.event_body.isVisible(),'compact_recent_event_opens_without_full_main_window')
  require(not p.stages.isVisible()and not p.tabs.isVisible(),'event_does_not_show_unrelated_enemy_controls')
  require(p.event_choices.count()>=2 and p.event_choices.currentData()is None,'documented_candidates_require_manual_selection')
  p.event_choices.setCurrentIndex(1);p.event_entries.setCurrentIndex(1);gui.processEvents()
  require('选项或结果原文'in p.event_text.toPlainText(),'selected_event_entry_displays_cited_text')
  require(not p.event_more.isChecked()and '当前服务器资格'not in p.event_text.toPlainText(),'default_event_reader_prioritizes_useful_game_text')
  p.event_more.setChecked(True);require('当前服务器资格'in p.event_text.toPlainText(),'detailed_conditions_remain_expandable');p.event_more.setChecked(False)
  entry=p.event_entries.currentData();text=p.event_text.toPlainText();window.run.state['last_node_content']['captured_at']=123;compact.refresh();gui.processEvents()
  require(p.event_entries.currentData()==entry and p.event_text.toPlainText()==text,'timestamp_refresh_preserves_event_entry_reading')
  require(p.open_event(),'event_has_verified_flow_navigation');gui.processEvents();target=p._target()
  require(p.event_dialog.isVisible()and p.event_dialog.panel.scene_id==target['scene_id'],'flow_reader_opens_exact_cited_scene')
  require(p.event_dialog.panel.choice_id==target['choice_id'],'flow_reader_opens_exact_cited_choice')
  p.event_dialog.close();p.event_note.click();gui.processEvents()
  require(window.player_notes.isVisible()and window.player_notes.content['kind']=='reference-scene','scene_note_opens_as_manual_fixed_reference')
  require(window.player_notes.content['event_id']==target['scene_id'],'note_is_bound_to_exact_fixed_scene')
  window.player_notes.close();compact.open_scene_battle();gui.processEvents()
  with patch('rouge.player_recent_scene.events.reference',return_value=None):
   require(not p.open_event()and p.event_dialog is None and not p.event_open.isEnabled(),'source_loss_invalidates_event_navigation')
  p.refresh();require(p.event_choices.currentData()is None,'source_recovery_does_not_restore_unconfirmed_stage')
  p.event_choices.setCurrentIndex(1);p.event_entries.setCurrentIndex(1)
  window.player_validation_target=compact.scene_popup
 finally:window.run.state=before
