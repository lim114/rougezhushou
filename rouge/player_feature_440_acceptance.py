def check(window,gui,require):
 from copy import deepcopy
 from .player_map_acceptance import fixtures
 from .player_map_find import coverage
 before=deepcopy(window.run.state)
 try:
  gs,*_=fixtures();window.run.state['maps']={g['zone_id']:g for g in gs};window.show_compact();bar=window.compact_window;bar.open_map();p=bar.map_popup.panel;gui.processEvents();require('已读或历史类型2处'in p.coverage_notice.text(),'coverage_separates_observed_from_template_and_candidates');p.read_scope.setCurrentIndex(p.read_scope.findData('unknown'));expected=coverage(p.graphs)['unknown'];require(p.node_results.count()==expected,'unknown_scope_keeps_only_unconfirmed_type_positions');key=p.node_results.currentData();p.refresh();require(p.read_scope.currentData()=='unknown'and p.node_results.currentData()==key,'scope_and_exact_choice_survive_refresh');require(p.locate_found_node(),'unknown_saved_node_remains_locatable_without_invented_content');p.read_scope.setCurrentIndex(0);window.player_validation_target=bar.map_popup
 finally:window.run.state=before
