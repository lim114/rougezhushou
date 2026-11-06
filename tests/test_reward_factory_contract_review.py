import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import unittest
from types import SimpleNamespace
from unittest.mock import Mock,patch
from PySide6.QtWidgets import QApplication
from rouge.current_named_reward_origins_view import make_event_dialog
from rouge.current_reward_origins_view import CurrentRewardOriginsPanel


class RewardFactoryContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.app=QApplication.instance() or QApplication([])

    def test_missing_internal_row_identity_propagates(self):
        with self.assertRaises(KeyError):make_event_dialog({})

    def test_invalid_child_cleared_and_closed_once(self):
        panel=CurrentRewardOriginsPanel('relics','rogue_6_relic_cargo_13')
        self.addCleanup(panel.close)
        panel.entries.setCurrentRow(0)
        child=Mock();child.panel=SimpleNamespace(result=None)
        with patch('rouge.current_named_reward_origins_view.make_event_dialog',return_value=child), patch.object(panel,'_close_event',wraps=panel._close_event) as close:
            self.assertFalse(panel.open_event())
        self.assertEqual(close.call_count,2)  # previous child, then failed child via _clear
        child.close.assert_called_once_with()
        self.assertIsNone(panel.event_dialog)
        self.assertIsNone(panel.result)
        self.assertEqual(panel.entries.count(),0)
        self.assertFalse(panel.open_button.isEnabled())
