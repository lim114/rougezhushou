def check(window,gui,require):
 from copy import deepcopy
 from .player_map_acceptance import fixtures
 from .player_item_hover import ItemHoverCard
 from .player_source_map import targets
 from .player_item_sources import ItemSourceIndex
 from .public_archive import load
 before=deepcopy(window.run.state)
 try:
  graphs,*_=fixtures();window.run.state['maps']={g['zone_id']:g for g in graphs};window.show_compact();bar=window.compact_window;index=ItemSourceIndex(load())
  chosen=next((v,i,p)for(v,i),ps in index.by_item.items()for p in ps if targets(index,v,i,p['id']))
  v,i,p=chosen;card=ItemHoverCard(bar);card.install({'id':i,'name':'藏品来源定位测试'},v,index,'actual-public-source');card.choose_card(p['id']);gui.processEvents()
  require(card.map_targets.count()>0,'explicit_public_node_enum_has_map_entry');old=deepcopy(window.run.state);require(card.open_map_source(),'source_card_opens_compact_map');gui.processEvents();panel=bar.map_popup.panel
  require(panel.view.filter_kind==card.map_targets.currentData(),'source_navigation_preserves_exact_node_type');require(panel.clear_filter.isVisible()and panel.filter_notice.text(),'non_palette_type_has_visible_filter_and_clear');require(window.run.state==old,'source_navigation_does_not_change_run');panel.refresh();require(panel.view.filter_kind==card.map_targets.currentData(),'source_filter_survives_refresh');panel.clear_filter.click();require(panel.view.filter_kind is None,'clear_source_filter_restores_all_types');card.close();panel.set_type_filter('作战');window.player_validation_target=bar.map_popup
 finally:window.run.state=before
