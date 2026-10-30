def check(window,gui,require):
 from copy import deepcopy
 from PySide6.QtCore import Qt
 from .player_replay_archive import reload_history
 from tests.test_player_feature_426 import observations
 before=deepcopy(window.run.state)
 try:
  window.show_compact();compact=window.compact_window;compact.open_replay();p=compact.replay_popup.panel
  archive=deepcopy(before);archive['id']='isolated-old-shop-run';first=observations();second=deepcopy(first);second['items']=second['items'][1:];second['at']=101
  archive['history']=[first,second];p.history_store.archive(archive);reload_history(p);p.sessions.setCurrentIndex(p.sessions.findData('archive:'+archive['id']));gui.processEvents()
  require(p.shop.panel.snapshots.count()==2,'archived_shop_lists_available_after_current_run_changed')
  require(window.run.state==before,'reading_archived_shops_does_not_restore_current_run')
  p.tabs.setCurrentIndex(0);p.entries.setCurrentRow(0);gui.processEvents()
  require(first['items'][0]['name']in p.detail.toPlainText(),'generic_read_record_exposes_observed_shop_goods')
  require(p.shop_button.isVisible(),'qualified_shop_log_has_direct_list_navigation')
  p.shop_button.click();gui.processEvents();require(p.tabs.currentWidget()is p.shop and p.shop.panel.snapshots.currentData()==0,'log_link_preserves_exact_history_position')
  p.shop.panel.entries.setCurrentRow(0);p.shop.panel.source_button.click();gui.processEvents()
  require(p.shop.panel.source_card.isVisible()and p.shop.panel.source_card.index is window.inventory_panel.source_index,'archived_goods_use_shared_public_source_reader')
  p.shop.panel.source_card.dismiss();p.sessions.setCurrentIndex(0);gui.processEvents()
  require(p.shop.panel.entries.count()==0,'returning_to_current_run_does_not_keep_archive_goods')
  p.sessions.setCurrentIndex(p.sessions.findData('archive:'+archive['id']));p.tabs.setCurrentWidget(p.shop);gui.processEvents()
  item=p.shop.panel.entries.item(0);p.shop.panel.entries.setCurrentItem(item);p.refresh();require(p.shop.panel.entries.currentItem()is item,'unchanged_history_refresh_keeps_goods_selection')
  require(not p.shop.comparison_toggle.isChecked()and not p.shop.panel.comparison.isVisible(),'archive_comparison_is_collapsed_to_prioritize_goods')
  require(p.shop.panel.entries.visualItemRect(item).bottom()<=p.shop.panel.entries.viewport().height(),'first_goods_tile_is_fully_visible_in_actual_archive_window')
  p.shop.comparison_toggle.click();gui.processEvents();require('变化不证明刷新'in p.shop.panel.comparison.text()and p.shop.panel.comparison.isVisible(),'archived_comparison_can_be_expanded');p.shop.comparison_toggle.click();gui.processEvents()
  require(window.run.state==before,'full_history_workflow_leaves_current_state_unchanged')
  window.player_validation_target=compact.replay_popup
 finally:window.run.state=before
