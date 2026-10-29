def check(window,gui,require):
 from PySide6.QtCore import Qt,QPoint
 from PySide6.QtTest import QTest
 window.show_compact();window.compact_window.open_inventory();gui.processEvents();popup=window.compact_window.inventory_popup;p=popup.panel
 p.held.setChecked(False);require(popup.isVisible()and not p.reader.isVisible(),'grid_default_reader_collapsed')
 require(p.entries.gridSize().width()>90,'icon_tile_has_usable_size')
 QTest.qWait(100);gui.processEvents();a=p.entries.visualItemRect(p.entries.item(0));b=p.entries.visualItemRect(p.entries.item(1))
 require(a.top()==b.top()and a.left()!=b.left(),'actual_multiple_columns')
 QTest.mouseClick(p.entries.viewport(),Qt.MouseButton.LeftButton,pos=a.center());gui.processEvents()
 require(p.reader.isVisible()and bool(p.detail.toPlainText()),'actual_tile_click_opens_reading')
 identity=p.entries.currentItem().data(Qt.ItemDataRole.UserRole);p.hide_reader.click();gui.processEvents()
 require(not p.reader.isVisible()and p.entries.currentItem().data(Qt.ItemDataRole.UserRole)==identity,'collapse_keeps_selection')
 p.rarity_buttons.button(2).click();gui.processEvents();require(p.rarity.currentData()=='RARE'and all(r['rarity']=='RARE'for r in p.rows.values()),'actual_rarity_chip_filters')
 p.rarity_buttons.button(0).click();p.icon_scale.setValue(96);gui.processEvents();require(p.entries.iconSize().width()==96,'actual_scale_slider_changes_tiles')
 popup.resize(700,560);QTest.qWait(80);gui.processEvents();require(p.entries.viewport().width()<=popup.width(),'grid_reflows_at_smaller_window')
 p.entries.setFocus();p.entries.setCurrentRow(0);QTest.keyClick(p.entries,Qt.Key.Key_Right);gui.processEvents();require(p.entries.currentRow()>=1 and p.reader.isVisible(),'keyboard_browsing_opens_reader')
 popup.resize(1000,650);p.hide_reader.click();p.icon_scale.setValue(72);QTest.qWait(80);gui.processEvents();window.player_validation_target=popup
