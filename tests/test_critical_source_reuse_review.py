import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import unittest
from unittest.mock import patch
from PySide6.QtWidgets import QApplication
from rouge import current_critical_reward_origins as model
from rouge.current_critical_reward_origins_view import make_event_dialog,CurrentCriticalRewardDialog
from rouge.current_reward_origins_view import CurrentRewardOriginsPanel


class CriticalSourceReuseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.app=QApplication.instance() or QApplication([])

    def test_parent_to_panel_reads_once_and_refresh_reads_again(self):
        p=CurrentRewardOriginsPanel('relics','rogue_6_relic_final_7');self.addCleanup(p.close)
        p.entries.setCurrentRow(0)
        with patch.object(model,'reference',wraps=model.reference) as read:
            self.assertTrue(p.open_event());self.assertEqual(read.call_count,1)
            self.assertTrue(p.event_dialog.panel.refresh_reference());self.assertEqual(read.call_count,2)

    def test_standalone_factory_validates_once_then_constructs_from_snapshot(self):
        row=model.reference('relics','rogue_6_relic_final_7')['rows'][0]
        with patch.object(model,'reference',wraps=model.reference) as read:
            dialog=make_event_dialog(row);self.addCleanup(dialog.close)
            self.assertEqual(read.call_count,1)
            self.assertEqual(dialog.panel.result['item_id'],row['item_id'])

    def test_standalone_dialog_still_loads_and_explicit_unavailable_does_not_reload(self):
        with patch.object(model,'reference',wraps=model.reference) as read:
            dialog=CurrentCriticalRewardDialog('rogue_6_relic_final_7');self.addCleanup(dialog.close)
            self.assertEqual(read.call_count,1)
        with patch.object(model,'reference') as read:
            missing=CurrentCriticalRewardDialog('rogue_6_relic_final_7',initial_reference=None);self.addCleanup(missing.close)
            read.assert_not_called();self.assertIsNone(missing.panel.result)
