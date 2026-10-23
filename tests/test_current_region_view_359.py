"""Temporary local widgets; no actual game, run, or account access."""
from unittest.mock import patch
import unittest

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from rouge import current_region_reference as model
from rouge.current_region_view import CurrentRegionPanel, CurrentRegionDialog


class CurrentRegionView359Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.panel = CurrentRegionPanel()
        self.panel.resize(1000, 770)
        self.panel.show()
        self.app.processEvents()

    def tearDown(self):
        self.panel.close()
        self.app.processEvents()

    def test_default_branches_and_selective_controls(self):
        panel = self.panel
        self.assertEqual(panel.entries.count(), 27)
        self.assertIsNone(panel.selected_id())
        self.assertFalse(panel.declarations.isVisible())
        panel.select_region('zone_1')
        self.assertTrue(panel.wings_row.isVisible())
        self.assertTrue(panel.goal_row.isVisible())
        self.assertIsNone(panel.selected_result['declared']['action_points'])
        panel.wings.setCurrentIndex(1)
        self.assertEqual(panel.selected_result['base_and_wings_reference_subtotal'], 6)
        panel.select_region('zone_3')
        self.assertFalse(panel.wings_row.isVisible())
        self.assertIn('击败', panel.goal_label.text())
        self.assertIsNone(panel.selected_result['declared']['wings'])
        panel.group.setCurrentIndex(3)
        self.assertEqual(panel.entries.count(), 19)
        self.assertIsNone(panel.selected_id())
        panel.entries.setCurrentRow(0)
        self.assertFalse(panel.goal_row.isVisible())
        self.assertFalse(panel.wings_row.isVisible())
        self.assertIsNone(panel.selected_result['declared']['goal_completed'])

    def test_same_source_refresh_preserves_exact_region_declarations_and_reading(self):
        panel = self.panel
        panel.select_region('zone_1')
        panel.action_points.setValue(0)
        panel.goal_completed.setCurrentIndex(2)
        panel.wings.setCurrentIndex(1)
        panel.tabs.setCurrentIndex(1)
        self.app.processEvents()
        panel.technical.verticalScrollBar().setValue(15)
        position = panel.technical.verticalScrollBar().value()
        self.assertGreater(position, 0)
        self.assertTrue(panel.refresh_reference())
        self.assertEqual(panel.selected_id(), 'zone_1')
        self.assertEqual(panel.tabs.currentIndex(), 1)
        self.assertEqual(panel.technical.verticalScrollBar().value(), position)
        self.assertEqual(panel.selected_result['declared'], {'action_points': 0, 'goal_completed': False, 'wings': True})
        self.assertIs(panel.selected_result['exhaustion_description_conditions_match'], True)
        self.assertIsNone(panel.selected_result['actual_exhaustion_triggered'])
        panel.tabs.setCurrentIndex(0)
        self.app.processEvents()
        panel.player.verticalScrollBar().setValue(5)
        position = panel.player.verticalScrollBar().value()
        self.assertGreater(position, 0)
        panel.refresh_reference()
        self.assertEqual(panel.tabs.currentIndex(), 0)
        self.assertEqual(panel.player.verticalScrollBar().value(), position)

    def test_selection_change_and_bad_source_clear_stale_information(self):
        panel = self.panel
        panel.select_region('zone_1')
        panel.action_points.setValue(0)
        panel.goal_completed.setCurrentIndex(2)
        panel.select_region('zone_7')
        self.assertEqual(panel.action_points.value(), -1)
        self.assertIsNone(panel.selected_result['declared']['goal_completed'])
        self.assertIn('盲目者所见', panel.player.toPlainText())
        with patch.object(model, 'packet', return_value=None):
            self.assertFalse(panel.refresh_reference())
            self.assertIsNone(panel.result)
            self.assertIsNone(panel.selected_result)
            self.assertEqual(panel.entries.count(), 0)
            self.assertFalse(panel.declarations.isVisible())
            self.assertEqual(panel.technical.toPlainText(), '')
            self.assertNotIn('盲目者所见', panel.player.toPlainText())
        self.assertTrue(panel.refresh_reference())
        self.assertIsNone(panel.selected_id())
        self.assertIsNone(panel.selected_result)

    def test_exact_incoming_target_forgery_deselection_and_close(self):
        dialog = CurrentRegionDialog({'zone_id': 'zone_7'})
        dialog.show()
        self.assertEqual(dialog.panel.selected_id(), 'zone_7')
        dialog.close()
        self.assertIsNone(dialog.panel.result)
        self.assertEqual(dialog.panel.entries.count(), 0)
        for target in ({'zone_id': 'zone_70'}, {'zone_id': 'zone_1', 'extra': True}, {'zone_id': True}):
            forged = CurrentRegionDialog(target)
            self.assertIsNone(forged.panel.selected_id())
            forged.close()
        panel = self.panel
        panel.select_region('zone_1')
        panel.entries.currentItem().setData(Qt.ItemDataRole.UserRole, 'zone_70')
        self.assertFalse(panel._render(panel.selected_id(), preserve=False))
        self.assertIsNone(panel.result)
        panel.refresh_reference()
        panel.select_region('zone_1')
        panel.entries.setCurrentRow(-1)
        self.assertIsNone(panel.selected_result)
        self.assertFalse(panel.declarations.isVisible())


if __name__ == '__main__':
    unittest.main()
