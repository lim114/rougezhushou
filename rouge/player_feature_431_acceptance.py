def check(window,gui,require):
 from copy import deepcopy
 from unittest.mock import patch
 from PySide6.QtCore import Qt
 from .player_map_acceptance import fixtures
 before=deepcopy(window.run.state)
 try:
  graphs,node,*_=fixtures();window.run.state['maps']={g['zone_id']:g for g in graphs};window.show_compact();c=window.compact_window;c.open_map();gui.processEvents();p=c.map_popup.panel
  p.view.select_node(node);p.select_interactive(node);gui.processEvents()
  def choose(kind):
   for i in range(p.entries.topLevelItemCount()):
    root=p.entries.topLevelItem(i)
    for j in range(root.childCount()):
     child=root.child(j);key=child.data(0,Qt.ItemDataRole.UserRole)
     if key and key[1]==kind:p.entries.setCurrentItem(child);return key
   raise AssertionError('No exact '+kind+' fixture candidate')
  key=choose('event');p.open_button.click();gui.processEvents();dialog=p.reference_popup
  require(dialog is not None and dialog.isVisible()and not window.isVisible(),'full_event_reader_opens_beside_map_without_main_window')
  require(dialog.node_reference_binding['expected_summary']['id']==key[2],'floating_event_keeps_exact_map_catalog_group')
  p.refresh();gui.processEvents();require(p.reference_popup is dialog,'ordinary_map_refresh_preserves_open_event_reader')
  p.view.select_node(next(n['id']for n in graphs[0]['nodes']if n['id']!=node));gui.processEvents();require(p.reference_popup is None,'switching_node_immediately_closes_old_reader')
  current=window.run.state['maps'][graphs[0]['zone_id']];selected=next(n for n in current['nodes']if n['id']==node);selected['observed_type']='作战';selected.pop('prediction',None);p.refresh();p.view.select_node(node);p.select_interactive(node);key=choose('battle');p.open_button.click();gui.processEvents();dialog=p.reference_popup
  require(dialog is not None and dialog.isVisible()and dialog.panel.stage_id==key[2],'map_battle_link_opens_exact_fixed_preview_in_tool_window')
  require(not window.isVisible(),'battle_preview_does_not_force_large_main_window')
  with patch('rouge.current_battle_reference.stage_reference',return_value=None):
   p.check_reference();require(p.reference_popup is None,'unavailable_battle_source_closes_owned_preview')
  p.open_button.click();gui.processEvents();require(p.reference_popup is not None,'restored_source_can_be_explicitly_reopened')
  window.player_validation_target=p.reference_popup
 finally:window.run.state=before
