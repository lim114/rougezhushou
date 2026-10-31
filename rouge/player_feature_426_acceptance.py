"""Native UI workflow over isolated shop observations, no game/API calls."""

def check_prices(window,gui,require):
 from copy import deepcopy
 from pathlib import Path
 import json
 from PySide6.QtCore import Qt,QTimer
 from .player_shop_hover import shop_snapshot
 from .player_shop_memory import recorded_shops
 before=deepcopy(window.run.state)
 for timer in window.findChildren(QTimer):timer.stop()
 try:
  frame=json.loads((Path(__file__).resolve().parents[1]/'research/shop-price-443/public-164-ocr.json').read_bytes())
  snapshot=shop_snapshot(frame['raw'],frame['shape']);at=window.run.state['started_at']+1
  require(window.apply_run_observation({'page':'shop','shop':snapshot},at),'shop443_normal_sampler_entry_accepts_shop_without_hover')
  first=recorded_shops(window.run.state)[-1][0]
  newer=deepcopy(snapshot);newer['items'][0]['price']=0
  require(window.apply_run_observation({'page':'shop','shop':newer},at+1),'shop443_same_names_new_price_observed')
  require(window.run.state['relics']==before['relics'],'shop443_does_not_claim_held_or_purchase')
  window.show_compact();bar=window.compact_window;bar.open_inventory();popup=bar.inventory_popup
  panel=popup.shop;popup.pages.setCurrentWidget(panel);gui.processEvents()
  panel.snapshots.setCurrentIndex(panel.snapshots.findData(first));panel.entries.setCurrentRow(0)
  require('6源石锭'in panel.detail.toPlainText(),'shop443_old_price_is_readable_after_leaving_shop')
  require('不证明持有、购买'in panel.detail.toPlainText(),'shop443_price_is_not_a_transaction')
  panel.search.setText('浪花');panel.entries.setCurrentRow(0);current=panel.entries.currentItem();bar.refresh();gui.processEvents()
  require(panel.snapshots.currentData()==first and panel.entries.currentItem()is current,'shop443_refresh_preserves_old_snapshot_and_selection')
  require('6源石锭'in panel.detail.toPlainText(),'shop443_latest_zero_does_not_replace_old_price')
  panel.snapshots.setCurrentIndex(0);panel.entries.setCurrentRow(0);gui.processEvents()
  require('0源石锭'in panel.detail.toPlainText(),'shop443_zero_is_a_known_price')
  require(not panel.comparison.isVisible(),'shop443_long_comparison_collapsed_by_default')
  panel.comparison_toggle.click();gui.processEvents()
  require(panel.comparison.isVisible(),'shop443_comparison_expands_on_request')
  require('6→0源石锭'in panel.comparison.text()and'变化不证明刷新'in panel.comparison.text(),'shop443_price_change_is_not_refresh_or_purchase')
  panel.comparison_toggle.click();gui.processEvents()
  panel.source_button.click();gui.processEvents()
  require(panel.source_card.isVisible()and panel.source_card.identity=='rogue_6_scrap_G_05','shop443_price_keeps_exact_source_navigation')
  panel.source_card.dismiss();panel.search.clear();panel.entries.setCurrentRow(3);gui.processEvents()
  require('标价：未读'in panel.detail.toPlainText(),'shop443_clipped_goods_price_stays_unknown')
  panel.entries.setCurrentRow(0);gui.processEvents()
  require(not panel.entries.item(0).icon().pixmap(72,72).isNull(),'shop443_exact_existing_part_picture_visible')
  panel.notice.setText('隔离验收：公开名称和图标，6→0标价变化由测试构造，不代表实际对局。'+panel.notice.text())
  window.player_validation_target=popup
 finally:window.run.state=before

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
