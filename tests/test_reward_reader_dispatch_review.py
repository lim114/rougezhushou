import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import unittest
from copy import deepcopy
from unittest.mock import patch
from PySide6.QtWidgets import QApplication
from rouge.current_named_reward_origins_view import make_event_dialog
from rouge.current_reward_origins_view import CurrentRewardOriginsPanel


class RewardReaderDispatchReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.app=QApplication.instance() or QApplication([])

    def test_named_factory_unknown_verified_reader_raises(self):
        row={'item_id':'item','reader_key':'new-reader','target':{}}
        with patch('rouge.current_named_reward_origins_view.model.reference',return_value={'rows':[row]}):
            with self.assertRaisesRegex(ValueError,'new-reader'):
                make_event_dialog(row)

    def test_panel_unknown_verified_reader_raises(self):
        panel=CurrentRewardOriginsPanel('relics','rogue_6_relic_cargo_13')
        self.addCleanup(panel.close);panel.entries.setCurrentRow(0)
        panel.result['rows'][0]['reader']='new-reader'
        with patch('rouge.current_reward_origins_view.model.reference',return_value=deepcopy(panel.result)):
            with self.assertRaisesRegex(ValueError,'new-reader'):
                panel.open_event()
        self.assertIsNone(panel.event_dialog)
