def check(window,gui,require):
 from PySide6.QtCore import Qt
 from PySide6.QtTest import QTest
 window.show_compact();c=window.compact_window;c.open_inventory();popup=c.inventory_popup;popup.pages.setCurrentIndex(2);p=popup.parts;gui.processEvents();QTest.qWait(100)
 require(p.branches.count()==4,'parts_have_all_and_three_game_category_branches')
 p.branches.setCurrentIndex(2);gui.processEvents();require(p.kind.currentData()=='GOODS'and p.entries.count()>0,'natural_object_branch_filters_grid')
 p.entries.setCurrentRow(0);identity=p.entries.currentItem().data(Qt.ItemDataRole.UserRole);require(not p.entries.currentItem().icon().isNull(),'part_artwork_reused')
 require(p.detail.isVisible()and '效果资料'in p.detail.toPlainText(),'grid_selection_expands_effects')
 p.icon_scale.setValue(88);popup.resize(780,650);gui.processEvents();c.refresh();require(p.entries.currentItem().data(Qt.ItemDataRole.UserRole)==identity,'resizing_and_refresh_keep_part_reading')
 p.details_toggle.click();gui.processEvents();require(not p.detail.isVisible(),'effects_can_be_collapsed')
 p.branches.setCurrentIndex(0);p.entries.setCurrentRow(-1);popup.resize(840,650);gui.processEvents();QTest.qWait(100)
 require(p.entries.visualItemRect(p.entries.item(0)).top()==p.entries.visualItemRect(p.entries.item(1)).top(),'actual_part_grid_has_multiple_columns')
 window.player_validation_target=popup
