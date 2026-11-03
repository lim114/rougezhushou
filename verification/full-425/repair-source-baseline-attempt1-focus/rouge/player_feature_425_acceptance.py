def check(window,gui,require):
 from copy import deepcopy
 from PySide6.QtCore import QRect
 from PySide6.QtTest import QTest
 from .player_map_acceptance import fixtures
 before=deepcopy(window.run.state);window.show_compact();c=window.compact_window;overlay=c.game_overlay;overlay.timer.stop();c.game_binding.timer.stop();c.game_hover.timer.stop()
 try:
  graphs,candidate,_,_=fixtures();graph=graphs[0];window.run.state['maps']={g['zone_id']:g for g in graphs};data={'graph':graph,'rect':QRect(100,100,1000,650),'points':[(candidate,200,200)]};snapshot={'active':True,'key':(1,2),'physical_client':(100,100,1000,650),'cursor':(300,300),'cursor_on_game':True,'screen':gui.primaryScreen()};overlay.current=data
  overlay.hover(data,snapshot);require(overlay.card is None,'node_card_waits_for_stable_hover');QTest.qWait(450);overlay.hover(data,snapshot);gui.processEvents()
  require(overlay.card is not None and overlay.card.isVisible(),'native_node_card_opens_after_owned_fixture_dwell')
  require(overlay.card.binding==(window.run.state['id'],graph['zone_id'],graph['template_id'],candidate),'node_card_binds_exact_run_zone_template_node')
  require(bool(overlay.card.entry_buttons),'node_card_has_documented_candidate_links')
  kind,identity,_=overlay.card.entry_buttons[0];require(overlay.open_entry(candidate,kind,identity),'node_candidate_link_opens_exact_map_entry');gui.processEvents();panel=c.map_popup.panel
  require(panel.view.selected==candidate and panel.selected_reference[1:]==(kind,identity),'node_link_keeps_exact_candidate_identity')
  require(not overlay.open_entry(candidate,kind,'not-a-real-candidate'),'missing_candidate_never_opens_same_named_replacement')
  require(c.buttons['场景笔记'].isEnabled(),'manual_notes_available_without_recent_scene')
  c.present(c.settings_popup);gui.processEvents();require(c.settings_scroll.verticalScrollBar().maximum()>0,'long_settings_scroll_in_small_window');c.settings_popup.hide()
  overlay.clear_hover();overlay.current=data;overlay.hover(data,snapshot);QTest.qWait(450);overlay.hover(data,snapshot);gui.processEvents();require(overlay.card.isVisible(),'node_reading_can_be_reopened')
  old=overlay.card.binding;window.run.state['id']='isolated-new-run';require(not overlay.open_entry(candidate,kind,identity),'new_run_invalidates_old_link');window.run.state=deepcopy(before);window.run.state['maps']={g['zone_id']:g for g in graphs};window.player_validation_target=overlay.card
 finally:window.run.state=deepcopy(before)
