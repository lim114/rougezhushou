def check(window,gui,require):
 from copy import deepcopy
 from .player_map_acceptance import fixtures
 before=deepcopy(window.run.state);old=window.map_view.graph;hist=window.map_view.historical
 try:
  gs,node,*_=fixtures();gs[0]['last_confirmed_current_node']=node;window.run.state['maps']={g['zone_id']:g for g in gs};window.map_view.set_map(gs[0],historical=True);window.show_compact();bar=window.compact_window;bar.open_map();p=bar.map_popup.panel;p.floors.setCurrentIndex(1);p.latest_position.click();gui.processEvents();require(p.view.graph['zone_id']==gs[0]['zone_id']and p.view.selected==node,'latest_button_returns_exact_saved_position');require(p.view.historical,'previous_position_not_claimed_current');p.node_query.setText('诡意行商');require('#28332e'in p.node_query.styleSheet(),'finder_has_explicit_readable_text_contrast');p.node_query.clear();p.details_toggle.setChecked(False);p.refresh();gui.processEvents();require(p.latest_position.isEnabled(),'refresh_keeps_available_position_shortcut');window.player_validation_target=bar.map_popup
 finally:window.run.state=before;window.map_view.set_map(old,historical=hist)
