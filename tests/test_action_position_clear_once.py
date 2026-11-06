import unittest
from unittest.mock import patch
from PySide6.QtWidgets import QApplication
from rouge.current_action_positions_view import CurrentActionPositionsPanel
from rouge import current_action_positions as model


class ActionPositionClearOnceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qt = QApplication.instance() or QApplication([])

    def test_changed_target_failure_clears_once(self):
        panel = CurrentActionPositionsPanel('ro6_n_2_3', '1')
        self.addCleanup(panel.close)
        self.assertIsNotNone(panel.result)
        with patch.object(model, 'reference', return_value=None), patch.object(panel, 'clear_reference', wraps=panel.clear_reference) as clear:
            self.assertFalse(panel.set_reference('missing', 'missing'))
            clear.assert_called_once_with()
        self.assertIsNone(panel.result)
        self.assertIsNone(panel.entry_key)
        self.assertEqual(panel.combo.count(), 0)
        self.assertEqual(panel.player.toPlainText(), model.UNAVAILABLE)

    def test_changed_target_success_resets_selection_without_intermediate_clear(self):
        panel = CurrentActionPositionsPanel('ro6_n_2_3', '1')
        self.addCleanup(panel.close)
        panel.combo.setCurrentIndex(1)
        fresh = model.reference('ro6_n_2_3', '1')
        fresh['action_key'] = 'other'
        with patch.object(model, 'reference', return_value=fresh), patch.object(panel, 'clear_reference', wraps=panel.clear_reference) as clear:
            self.assertTrue(panel.set_reference('ro6_n_2_3', 'other'))
            clear.assert_not_called()
        self.assertIsNone(panel.entry_key)
        self.assertEqual(panel.combo.currentIndex(), 0)
        self.assertEqual(panel.result['action_key'], 'other')
