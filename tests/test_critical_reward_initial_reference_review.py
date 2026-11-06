import unittest
from unittest.mock import patch

from PySide6.QtWidgets import QApplication

from rouge import current_critical_reward_origins as model
from rouge.current_critical_reward_origins_view import CurrentCriticalRewardPanel


class CriticalRewardInitialReferenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qt = QApplication.instance() or QApplication([])

    def test_all_initial_modes_read_once_and_match_explicit_default_context(self):
        for event, _, item_id in model.SELECTIONS:
            with self.subTest(event=event):
                with patch.object(model, 'reference', wraps=model.reference) as read:
                    panel = CurrentCriticalRewardPanel(item_id)
                self.addCleanup(panel.close)
                self.assertEqual(read.call_count, 1)
                self.assertEqual(panel.event_id, event)
                self.assertEqual(panel.result, model.reference('relics', item_id, panel.values()))

    def test_unavailable_initial_source_stays_clear_until_explicit_refresh(self):
        item_id = model.SELECTIONS[0][2]
        with patch.object(model, 'reference', return_value=None) as read:
            panel = CurrentCriticalRewardPanel(item_id)
        self.addCleanup(panel.close)
        self.assertEqual(read.call_count, 1)
        self.assertIsNone(panel.result)
        self.assertEqual(panel.player.toPlainText(), model.UNAVAILABLE)
        self.assertEqual(panel.technical.toPlainText(), '')
        self.assertFalse(panel.flow_button.isEnabled())

    def test_later_refresh_reads_current_source_and_clears_previous_result(self):
        panel = CurrentCriticalRewardPanel(model.SELECTIONS[0][2])
        self.addCleanup(panel.close)
        self.assertIsNotNone(panel.result)
        with patch.object(model, 'reference', return_value=None) as read:
            self.assertFalse(panel.refresh_reference())
        read.assert_called_once_with('relics', panel.item_id, panel.values())
        self.assertIsNone(panel.result)
        self.assertEqual(panel.technical.toPlainText(), '')
        self.assertFalse(panel.flow_button.isEnabled())


if __name__ == '__main__':
    unittest.main()
