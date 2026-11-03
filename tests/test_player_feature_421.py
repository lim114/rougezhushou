import unittest
from types import SimpleNamespace
from unittest.mock import patch
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from rouge.player_parts import PartsPanel,part_rows
from rouge.player_tools import ToolsPanel
class GridTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.gui=QApplication.instance()or QApplication([])
 def test_part_branches_grid_and_selection_survive_scaling(self):
  p=PartsPanel(SimpleNamespace(state={}));p.show()
  try:
   p.branches.setCurrentIndex(1);self.assertEqual(p.kind.currentData(),'MOVE');self.assertEqual(p.entries.count(),len(part_rows(kind='MOVE')))
   p.entries.setCurrentRow(0);identity=p.entries.currentItem().data(Qt.ItemDataRole.UserRole);self.assertTrue(p.details_toggle.isChecked());p.icon_scale.setValue(104);p.resize(480,620);self.gui.processEvents();p.refresh();self.assertEqual(p.entries.currentItem().data(Qt.ItemDataRole.UserRole),identity);self.assertEqual(p.entries.tile_icon,104)
   p.details_toggle.setChecked(False);self.assertFalse(p.detail.isVisible());p.refresh();self.assertFalse(p.details_toggle.isChecked())
   with patch('rouge.player_parts.source.packet',return_value=None):p.refresh()
   self.assertEqual(p.entries.count(),0);self.assertFalse(p.details_toggle.isChecked());self.assertIsNone(p.entries.selected_identity)
  finally:p.close()
 def test_tool_grid_still_defaults_to_verified_possession(self):
  p=ToolsPanel(SimpleNamespace(state={}))
  try:
   self.assertEqual(p.entries.count(),0);p.held.setChecked(False);self.assertGreater(p.entries.count(),0);p.entries.setCurrentRow(0);self.assertTrue(p.details_toggle.isChecked());self.assertIn('不自动使用',p.detail.toPlainText())
  finally:p.close()
