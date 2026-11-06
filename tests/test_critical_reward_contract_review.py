import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import unittest
from unittest.mock import Mock,patch
from rouge.current_critical_reward_origins_view import make_event_dialog,CurrentCriticalRewardPanel
from PySide6.QtWidgets import QApplication


class CriticalRewardContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.app=QApplication.instance() or QApplication([])

    def test_missing_internal_item_id_raises(self):
        with self.assertRaises(KeyError):make_event_dialog({})

    def test_wrong_actual_flow_target_is_closed_and_cleared(self):
        p=CurrentCriticalRewardPanel('rogue_6_relic_final_7');self.addCleanup(p.close)
        self.assertEqual(p.result['rows'][0]['event_id'],'entry')
        child=Mock();child.panel.result={};child.panel.scene_id='wrong';child.panel.choice_id='wrong'
        with patch('rouge.current_exit_view.CurrentExitDialog',return_value=child):
            self.assertFalse(p.open_flow())
        child.close.assert_called_once_with();child.show.assert_not_called()
        self.assertIsNone(p.result);self.assertIsNone(p.flow_dialog)
        self.assertFalse(p.flow_button.isEnabled())

    def test_source_lost_at_click_does_not_construct_flow(self):
        p=CurrentCriticalRewardPanel('rogue_6_relic_final_7');self.addCleanup(p.close)
        with patch('rouge.current_critical_reward_origins_view.model.reference',return_value=None),patch('rouge.current_exit_view.CurrentExitDialog') as create:
            self.assertFalse(p.open_flow())
        create.assert_not_called();self.assertIsNone(p.result)
