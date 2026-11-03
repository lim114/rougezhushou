"""Compact inventory keeps its source limits, selected reading and held evidence."""
from copy import deepcopy
from types import SimpleNamespace
from unittest.mock import patch
import unittest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
from rouge.player_inventory import InventoryPanel

class InventoryLayoutReview(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.gui=QApplication.instance()or QApplication([])
 def panel(self):
  run=SimpleNamespace(state={});p=InventoryPanel(run);self.addCleanup(p.close);p.held.setChecked(False);p.resize(980,540);p.show();self.gui.processEvents();return p,run
 def test_scope_is_accessible_without_losing_filter_or_reading(self):
  p,run=self.panel();p.search.setText('攻击');p.entries.setCurrentRow(0);self.gui.processEvents();identity=p.entries.currentItem().data(Qt.ItemDataRole.UserRole)
  self.assertFalse(p.status.isVisible());self.assertIn('未核对完整',p.summary.text());p.scope.click();self.assertTrue(p.status.isVisible());self.assertIn('不是当前DLC完整目录或已生效证明',p.status.text())
  p.refresh();self.assertTrue(p.scope.isChecked());self.assertEqual(p.search.text(),'攻击');self.assertEqual(p.entries.currentItem().data(Qt.ItemDataRole.UserRole),identity)
 def test_source_loss_remains_visible_and_recovery_does_not_reselect(self):
  p,run=self.panel();p.entries.setCurrentRow(0);self.assertTrue(p.reader.isVisible())
  with patch('rouge.player_inventory.reference.packet',return_value=None):p.refresh()
  self.assertFalse(p.status.isVisible());self.assertIn('资料暂不可用',p.summary.text());self.assertFalse(p.reader.isVisible());self.assertEqual(p.entries.count(),0)
  p.refresh();self.assertGreater(p.entries.count(),0);self.assertIsNone(p.entries.currentItem());self.assertFalse(p.source_button.isVisible())
 def test_complete_claim_uses_quantities_and_members_not_a_flag_alone(self):
  p,run=self.panel();identity=next(iter(p.rows));run.state={'inventory_verified':True,'relic_count':2,'relics':{identity:{}}};before=deepcopy(run.state);p.refresh()
  self.assertIn('未核对完整',p.summary.text());self.assertNotIn('本局收藏品已核对完整',p.status.text());self.assertEqual(run.state,before)
  run.state['relic_count']=1;p.refresh();self.assertIn('持有清单已核对完整',p.summary.text())
 def test_item_actions_follow_the_selected_reader_and_survive_refresh(self):
  p,run=self.panel();self.assertFalse(p.source_button.isVisible());p.entries.setCurrentRow(0);self.gui.processEvents();self.assertTrue(p.source_button.isVisible());self.assertTrue(p.reference_button.isVisible())
  selected=p.entries.currentItem();text=p.detail.toPlainText();p.hide_reader.click();p.refresh();self.assertFalse(p.reader.isVisible());self.assertIs(p.entries.currentItem(),selected);self.assertEqual(p.detail.toPlainText(),text)

if __name__=='__main__':unittest.main()
