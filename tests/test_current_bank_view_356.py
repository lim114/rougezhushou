"""Temporary Qt widgets only; no actual main window, account, or game state."""
from unittest.mock import patch
import unittest

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from rouge import current_bank_reference as model
from rouge.current_bank_view import CurrentBankPanel, CurrentBankDialog


class CurrentBankView356Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.panel = CurrentBankPanel()
        self.panel.resize(1000, 700)
        self.panel.show()
        self.app.processEvents()

    def tearDown(self):
        self.panel.close()
        self.app.processEvents()

    def test_default_unknown_selective_controls_and_repeated_refresh(self):
        panel = self.panel
        self.assertEqual(panel.entries.count(), 5)
        self.assertEqual(panel.entries.currentRow(), -1)
        self.assertEqual(panel.values(), {'cumulative': None, 'peak_balance': None})
        self.assertFalse(panel.peak_row.isVisible())
        self.assertFalse(panel.item_button.isVisible())
        panel.select_reward('bank_reward_4')
        panel.cumulative.setValue(250)
        panel.peak_balance.setValue(249)
        panel.tabs.setCurrentIndex(1)
        self.app.processEvents()
        panel.technical.verticalScrollBar().setValue(12)
        old_scroll = panel.technical.verticalScrollBar().value()
        self.assertGreater(old_scroll, 0)
        panel.refresh_reference()
        self.assertEqual(panel.selected_id(), 'bank_reward_4')
        self.assertEqual(panel.tabs.currentIndex(), 1)
        self.assertEqual(panel.technical.verticalScrollBar().value(), old_scroll)
        self.assertEqual(panel.values(), {'cumulative': 250, 'peak_balance': 249})
        self.assertTrue(panel.peak_row.isVisible())
        panel.select_reward('bank_reward_3')
        self.assertFalse(panel.peak_row.isVisible())
        self.assertFalse(panel.item_button.isVisible())

    def test_exact_item_child_reuse_source_loss_and_manual_reselection(self):
        panel = self.panel
        panel.select_reward('bank_reward_4')
        self.assertTrue(panel.open_item())
        child = panel.item_dialog
        self.assertEqual(child.panel.result['target'], {'category': 'relics', 'key': model.ITEM_ID})
        self.assertIsNotNone(child.panel.image_raw)
        child.panel.tabs.setCurrentIndex(1)
        self.app.processEvents()
        child.panel.technical.verticalScrollBar().setValue(8)
        scroll = child.panel.technical.verticalScrollBar().value()
        self.assertTrue(panel.open_item())
        self.assertIs(panel.item_dialog, child)
        self.assertEqual(child.panel.tabs.currentIndex(), 1)
        panel.refresh_reference()
        self.assertEqual(child.panel.technical.verticalScrollBar().value(), scroll)
        with patch.object(model, 'packet', return_value=None):
            self.assertFalse(panel.refresh_reference())
            self.assertIsNone(panel.result)
            self.assertEqual(panel.entries.count(), 0)
            self.assertFalse(child.isVisible())
            self.assertFalse(panel.item_button.isVisible())
        self.assertTrue(panel.refresh_reference())
        self.assertEqual(panel.entries.currentRow(), -1)
        self.assertIsNone(panel.item_dialog)

    def test_deselection_bad_targets_and_parent_close_owned_tree(self):
        panel = self.panel
        self.assertFalse(panel.select_reward('bank_reward_40'))
        self.assertFalse(panel.open_item())
        panel.select_reward('bank_reward_4')
        self.assertTrue(panel.open_item())
        child = panel.item_dialog
        panel.entries.setCurrentRow(-1)
        self.assertFalse(child.isVisible())
        self.assertIsNone(panel.item_dialog)
        dialog = CurrentBankDialog({'reward_id': 'bank_reward_4'})
        dialog.show()
        self.assertEqual(dialog.panel.selected_id(), 'bank_reward_4')
        self.assertTrue(dialog.panel.open_item())
        nested = dialog.panel.item_dialog
        dialog.close()
        self.assertFalse(nested.isVisible())
        forged = CurrentBankDialog({'reward_id': 'bank_reward_2'})
        self.assertEqual(forged.panel.entries.currentRow(), -1)
        forged.close()

    def test_forged_selected_reward_never_opens_an_item(self):
        panel = self.panel
        panel.select_reward('bank_reward_4')
        panel.entries.currentItem().setData(Qt.ItemDataRole.UserRole, 'bank_reward_40')
        self.assertFalse(panel.open_item())
        self.assertIsNone(panel.item_dialog)


if __name__ == '__main__':
    unittest.main()
