def check(window,gui,require):
 from copy import deepcopy
 from .player_map_acceptance import fixtures
 from .player_map_reference import node_dossier
 before=deepcopy(window.run.state)
 try:
  graphs,node,other,_=fixtures();window.run.state['maps']={g['zone_id']:g for g in graphs};window.show_compact();compact=window.compact_window;compact.open_map();gui.processEvents();p=compact.map_popup.panel;p.view.select_node(node);p.select_interactive(node);p.entry_search.setText('桑尼');gui.processEvents()
  require(len(p.rows)==1 and next(iter(p.rows.values()))['title']=='桑尼的邀请','node_query_filters_only_qualified_selected_node_names')
  root=p.entries.topLevelItem(0);p.entries.setCurrentItem(root.child(0));key=p.selected_reference;text=p.detail.toPlainText();root.setExpanded(False);p.refresh();gui.processEvents()
  require(not p.entries.topLevelItem(0).isExpanded(),'actual_collapsed_group_survives_map_refresh')
  require(p.entry_search.text()=='桑尼'and p.selected_reference==key and p.detail.toPlainText()==text,'query_selection_and_reading_survive_refresh_together')
  p.view.select_node(other);gui.processEvents();require(p.entry_search.text()=='','different_node_does_not_inherit_other_node_query')
  p.entry_search.setText('另一份筛选');p.view.select_node(node);gui.processEvents();require(p.entry_search.text()=='桑尼','returning_to_node_restores_own_reading')
  target=node_dossier(graphs[0],node,{})['rows'][0]['id'];p.entry_search.setText('没有匹配项');require(p.open_hover_entry(node,'event',target),'explicit_hover_link_can_reveal_filtered_target');gui.processEvents()
  require(p.entry_search.text()==''and p.selected_reference[1:]==('event',target),'hover_navigation_keeps_exact_id_and_clears_only_conflicting_query')
  p.entry_search.setText('桑尼');require(not p.open_hover_entry(node,'event','missing')and p.entry_search.text()=='桑尼','invalid_hover_identity_does_not_discard_user_query')
  root=p.entries.topLevelItem(0);root.setExpanded(True);p.entries.setCurrentItem(root.child(0));gui.processEvents();window.player_validation_target=compact.map_popup
 finally:window.run.state=before
