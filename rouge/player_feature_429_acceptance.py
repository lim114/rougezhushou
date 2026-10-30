def check(window,gui,require):
 from PySide6.QtCore import Qt
 window.show_compact();compact=window.compact_window;compact.open_inventory();popup=compact.inventory_popup;panel=popup.panel
 panel.held.setChecked(False);panel.more.setChecked(True);panel.version.setCurrentIndex(panel.version.findData('dlc1'));panel.search.setText('独活');gui.processEvents()
 require(panel.entries.count()>0,'acquisition_event_name_search_returns_catalogued_goods')
 panel.entries.setCurrentRow(0);gui.processEvents()
 require('独活'in panel.detail.toPlainText()and '取得与解锁'in panel.detail.toPlainText(),'default_detail_preserves_acquisition_original_text')
 panel.access.setCurrentIndex(panel.access.findData('special'));gui.processEvents();require(panel.entries.count()>0,'special_obtain_filter_intersects_event_name_query')
 selected=panel.entries.item(0).data(Qt.ItemDataRole.UserRole);panel.entries.setCurrentRow(0);compact.refresh();gui.processEvents()
 require(panel.search.text()=='独活'and panel.entries.currentItem().data(Qt.ItemDataRole.UserRole)==selected,'refresh_keeps_acquisition_query_and_reading')
 panel.search.clear();panel.access.setCurrentIndex(0);panel.source_node.setCurrentIndex(panel.source_node.findData('不期而遇'));gui.processEvents()
 require(panel.entries.count()>0 and all('不期而遇'in r['source_nodes']for r in panel.rows.values()),'node_filter_uses_explicit_version_scoped_memberships')
 require('不判断本局解锁'in panel.status.text(),'filters_keep_actual_eligibility_unknown')
 panel.entries.setCurrentRow(0);panel.version.setCurrentIndex(panel.version.findData('base'));gui.processEvents()
 require(panel.source_node.currentData()=='不期而遇','version_change_does_not_silently_drop_user_node_filter')
 panel.version.setCurrentIndex(panel.version.findData('dlc1'));panel.source_node.setCurrentIndex(0);panel.access.setCurrentIndex(panel.access.findData('special'));panel.search.setText('独活');panel.entries.setCurrentRow(0);gui.processEvents()
 window.player_validation_target=popup
