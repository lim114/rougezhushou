import unittest
from unittest.mock import patch
from PySide6.QtWidgets import QApplication
from rouge import current_exchange_reference as offers
from rouge.current_exchange_view import CurrentExchangePanel
from rouge.current_reconstruction_view import CurrentReconstructionPanel


class ExchangeSourceReuseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qt = QApplication.instance() or QApplication([])

    def test_explicit_source_and_none_do_not_reload(self):
        fresh = offers.packet()
        with patch.object(offers, 'packet') as read:
            panel = CurrentExchangePanel(initial_reference=fresh)
            self.addCleanup(panel.close)
            self.assertIs(panel.result, fresh)
            self.assertTrue(panel.refresh_reference(source=fresh))
            self.assertFalse(panel.refresh_reference(source=None))
            self.assertIsNone(panel.result)
            read.assert_not_called()

    def test_parent_open_and_refresh_read_once_per_operation(self):
        panel = CurrentReconstructionPanel()
        self.addCleanup(panel.close)
        choice = panel.result['choices']['doc-choice:2']
        panel.scene_id, panel.choice_id = choice['scene_id'], choice['id']
        fresh = offers.packet()
        with patch.object(offers, 'packet', return_value=fresh) as read:
            self.assertTrue(panel.open_catalogue())
            read.assert_called_once_with()
            self.assertIs(panel.catalogue_dialog.panel.result, fresh)
        with patch.object(offers, 'packet', return_value=fresh) as read:
            panel._update_specific(choice)
            read.assert_called_once_with()
        child = panel.catalogue_dialog
        with patch.object(offers, 'packet', return_value=None) as read:
            panel._update_specific(choice)
            read.assert_called_once_with()
            self.assertIsNone(panel.catalogue_dialog)
            self.assertFalse(child.isVisible())
            self.assertIsNotNone(panel.result)
