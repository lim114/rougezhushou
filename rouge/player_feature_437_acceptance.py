def check(window,gui,require):
 from copy import deepcopy
 from .player_map_acceptance import fixtures
 before=deepcopy(window.run.state)
 try:
  gs,*_=fixtures();window.run.state['maps']={g['zone_id']:g for g in gs};window.show_compact();bar=window.compact_window;bar.open_map();p=bar.map_popup.panel;gui.processEvents();p.node_query.setText('第2层');require(p.node_results.count()==len(gs[1]['nodes']),'finder_lists_only_matching_recorded_floor');key=p.node_results.currentData();require(p.locate_found_node(),'finder_exact_location_opens');gui.processEvents();require(p.view.graph['zone_id']==key[0]and p.view.selected==key[2],'finder_switches_floor_and_selects_exact_node');p.refresh();require(p.node_query.text()=='第2层'and p.node_results.currentData()==key,'finder_refresh_preserves_query_and_choice');p.node_query.setText('不存在的记录');require(p.node_results.count()==0 and not p.find_node.isEnabled(),'no_match_not_replaced_by_other_nodes');p.node_query.setText('第2层');p.locate_found_node();window.player_validation_target=bar.map_popup
 finally:window.run.state=before
