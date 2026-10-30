"""Native UI workflow over isolated shop observations, no game/API calls."""
def check(window,gui,require):
 from copy import deepcopy
 from PySide6.QtCore import Qt
 from tests.test_player_feature_426 import observations
 before=deepcopy(window.run.state)
 try:
  first=observations();second=deepcopy(first);second['at']=101.0;second['items']=second['items'][1:]
  window.run.state['history'] += [first,second]
  window.show_compact();compact=window.compact_window;compact.open_inventory();popup=compact.inventory_popup;panel=popup.shop;popup.pages.setCurrentWidget(panel);gui.processEvents()
  require(panel.snapshots.count()==2,'two_observed_shop_lists_available_after_leaving_page')
  require('前次读到、本次未读到'in panel.comparison.text()and first['items'][0]['name']in panel.comparison.text(),'partial_list_comparison_retains_unread_item_name')
  require('不同商店'in panel.comparison.text()and '变化不证明刷新'in panel.comparison.text(),'comparison_does_not_claim_transaction_or_same_shop')
  panel.entries.setCurrentRow(0);identity=panel.entries.currentItem().data(Qt.ItemDataRole.UserRole);panel.search.setText(panel.entries.currentItem().text());gui.processEvents()
  require(panel.entries.count()==1,'shop_snapshot_name_search_filters_exact_read_list')
  panel.entries.setCurrentRow(0);panel.source_button.click();gui.processEvents()
  require(panel.source_card.isVisible()and panel.source_card.identity==identity,'shop_item_directly_opens_exact_source_card')
  require(panel.source_card.index is popup.panel.source_index,'shop_and_inventory_share_current_public_data')
  require('不是抽取权重'in panel.source_card.notice.text(),'shop_source_statistics_keep_probability_boundary')
  panel.source_card.dismiss();old_item=panel.entries.currentItem();compact.refresh();gui.processEvents()
  require(panel.entries.currentItem()is old_item and panel.search.text()!='','ordinary_refresh_preserves_shop_search_and_selection')
  panel.snapshots.setCurrentIndex(1);gui.processEvents();require('尚无前次'in panel.comparison.text(),'earliest_shop_record_has_no_invented_predecessor')
  panel.search.clear();panel.entries.setCurrentRow(0);panel.source_button.click();gui.processEvents();panel.hide();gui.processEvents()
  require(not panel.source_card.isVisible(),'hidden_shop_does_not_leave_source_card')
  panel.show();window.run.state['id']='isolated-new-run';window.run.state['history']=[];panel.refresh();gui.processEvents()
  require(panel.entries.count()==0 and panel.search.text()==''and not panel.source_button.isEnabled(),'new_run_clears_old_shop_view_only_in_fixture')
  window.run.state=deepcopy(before);window.run.state['history'] += [first,second];panel.refresh();panel.entries.setCurrentRow(0);gui.processEvents()
  window.player_validation_target=popup
 finally:window.run.state=before
