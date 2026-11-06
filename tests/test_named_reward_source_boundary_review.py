import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import unittest
from unittest.mock import Mock,patch
from PySide6.QtWidgets import QApplication
from rouge.current_reward_origins_view import CurrentRewardOriginsPanel
from rouge import current_named_reward_origins as named
from rouge.current_named_reward_origins_view import make_event_dialog


class NamedRewardSourceReuseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.app=QApplication.instance() or QApplication([])

    def setUp(self):
        self.panel=CurrentRewardOriginsPanel('relics','rogue_6_relic_cargo_13')
        self.addCleanup(self.panel.close);self.panel.entries.setCurrentRow(0)

    def test_parent_validates_named_source_once(self):
        child=Mock();child.panel.result={}
        with patch.object(named,'reference',wraps=named.reference) as read,patch('rouge.current_named_reward_origins_view._dialog_from_verified_row',return_value=child):
            self.assertTrue(self.panel.open_event())
        self.assertEqual(read.call_count,1)
        child.show.assert_called_once_with()

    def test_standalone_factory_still_revalidates(self):
        row=self.panel.result['rows'][0]
        with patch.object(named,'reference',return_value=None) as read,patch('rouge.current_named_reward_origins_view._dialog_from_verified_row') as create:
            self.assertIsNone(make_event_dialog(row))
        read.assert_called_once_with('relics',row['item_id']);create.assert_not_called()

    def test_source_checked_after_previous_child_closed(self):
        child=Mock();self.panel.event_dialog=child;order=[]
        child.close.side_effect=lambda:order.append('closed')
        def unavailable(*args):
            order.append('checked');return None
        with patch('rouge.current_reward_origins_view.model.reference',side_effect=unavailable):
            self.assertFalse(self.panel.open_event())
        self.assertEqual(order,['closed','checked'])
        self.assertIsNone(self.panel.result)
