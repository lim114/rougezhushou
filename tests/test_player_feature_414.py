import unittest
from PySide6.QtWidgets import QApplication,QListView
from PySide6.QtCore import Qt
from types import SimpleNamespace
from rouge.player_inventory import InventoryPanel
class GridTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.gui=QApplication.instance()or QApplication([])
 def setUp(self):self.panel=InventoryPanel(SimpleNamespace(state={}));self.panel.held.setChecked(False)
 def tearDown(self):self.panel.close()
 def test_grid_is_adaptive_non_draggable(self):
  grid=self.panel.entries;self.assertEqual(grid.viewMode(),QListView.ViewMode.IconMode);self.assertEqual(grid.resizeMode(),QListView.ResizeMode.Adjust);self.assertFalse(grid.dragEnabled())
 def test_scale_preserves_item_identity(self):
  p=self.panel;p.entries.setCurrentRow(0);key=p.entries.currentItem().data(Qt.ItemDataRole.UserRole);before=p.entries.gridSize();p.icon_scale.setValue(104)
  self.assertNotEqual(p.entries.gridSize(),before);self.assertEqual(key,p.entries.currentItem().data(Qt.ItemDataRole.UserRole));self.assertEqual(p.entries.selected_identity,key)
 def test_rarity_shortcuts_and_combo_stay_in_sync(self):
  p=self.panel;p.rarity_buttons.button(2).click();self.assertEqual(p.rarity.currentData(),'RARE');self.assertTrue(all(r['rarity']=='RARE'for r in p.rows.values()))
  p.rarity.setCurrentIndex(3);self.assertTrue(p.rarity_buttons.button(3).isChecked())
 def test_more_filters_keeps_current_state(self):
  p=self.panel;p.more.click();p.search.setText('攻击');p.kind.setCurrentIndex(1);p.more.click();p.refresh();self.assertEqual(p.search.text(),'攻击');self.assertEqual(p.kind.currentData(),'RELIC');self.assertTrue(p.rows)
 def test_refresh_keeps_grid_item_and_detail_scroll(self):
  p=self.panel;p.entries.setCurrentRow(0);item=p.entries.currentItem();p.detail.verticalScrollBar().setValue(5);value=p.detail.verticalScrollBar().value();p.refresh()
  self.assertIs(p.entries.currentItem(),item);self.assertEqual(p.detail.verticalScrollBar().value(),value)
