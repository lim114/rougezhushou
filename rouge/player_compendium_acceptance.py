"""Actual isolated Qt interactions for the source-scoped DLC1 compendium."""
def check(window,gui,require):
    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest
    from copy import deepcopy
    from . import public_archive
    before=deepcopy(window.run.state)
    window.show_compact();window.compact_window.open_inventory();gui.processEvents()
    popup=window.compact_window.inventory_popup;panel=popup.panel
    require(popup.isVisible(),'inventory_popup_visible')
    panel.held.setChecked(False);panel.version.setCurrentIndex(panel.version.findData('dlc1'))
    require(panel.category.findData('生存助力')>=0,'game_category_filter_available')
    require(panel.category.findData('支援道具')<0,'tools_not_misrepresented_as_relic_inventory')
    panel.search.setText('精选兽肉罐头');panel.entries.setCurrentRow(0);gui.processEvents()
    require(panel.entries.currentItem().data(Qt.ItemDataRole.UserRole)=='rogue_6_relic_legacy_22','exact_item_found_in_compendium')
    require('【混沌化】'in panel.detail.toPlainText()and'取得与解锁'in panel.detail.toPlainText(),'all_grade_effects_and_acquisition_readable')
    require('不代表本局当前档位'in panel.detail.toPlainText(),'grade_not_inferred_from_document')
    identity=panel.entries.currentItem().data(Qt.ItemDataRole.UserRole);text=panel.detail.toPlainText()
    panel.refresh();gui.processEvents()
    require(panel.entries.currentItem().data(Qt.ItemDataRole.UserRole)==identity and panel.detail.toPlainText()==text,'refresh_preserves_selection_and_reading')
    panel.version.setCurrentIndex(panel.version.findData('base'));gui.processEvents()
    require('【混沌化】'not in panel.detail.toPlainText()and'固定国服'in panel.detail.toPlainText(),'base_does_not_borrow_dlc1_description')
    panel.version.setCurrentIndex(panel.version.findData('dlc1'));panel.search.clear()
    panel.category.setCurrentIndex(panel.category.findData('生存助力'));gui.processEvents()
    require(panel.entries.count()>0 and all(r['category']=='生存助力'for r in panel.rows.values()),'actual_category_selection_filters_rows')
    panel.rarity.setCurrentIndex(1);gui.processEvents()
    require(all(r['rarity']==panel.rarity.currentData()for r in panel.rows.values()),'rarity_and_category_intersect')
    panel.rarity.setCurrentIndex(0);panel.category.setCurrentIndex(0);panel.search.setText('精选兽肉罐头');panel.entries.setCurrentRow(0)
    window.open_public_archive();gui.processEvents()
    dialog=window.public_archive;dialog.data=public_archive.load();dialog.install()
    pool=next(r for r in dialog.data['versions']['dlc1']if'rogue_6_active_tool_6'in r['collectibles'])
    require(dialog.select_exact_pool('dlc1',pool['id']),'exact_tool_pool_available')
    names=[dialog.members.item(i,0).text()for i in range(dialog.members.rowCount())]
    require(all(n in names for n in ('支援补给站','支援地雷组','支援轰隆隆','支援起重机','支援防暴桩','支援雾机')),'all_six_tools_named_in_actual_pool_table')
    require(window.run.state==before,'compendium_does_not_modify_run')
    popup.show();QTest.qWait(100);gui.processEvents();window.player_validation_target=popup
