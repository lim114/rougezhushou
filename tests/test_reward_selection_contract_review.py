import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import unittest
from unittest.mock import patch
from PySide6.QtWidgets import QApplication
from rouge.current_reward_origins_view import CurrentRewardOriginsPanel


class ObservedPanel(CurrentRewardOriginsPanel):
    def __init__(self):
        self.selection_states=[]
        super().__init__('relics','rogue_6_relic_cargo_13')

    def _selected(self,item,*args):
        self.selection_states.append(self.result is not None)
        super()._selected(item,*args)


class RewardSelectionContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.app=QApplication.instance() or QApplication([])

    def test_refresh_clear_restore_never_emits_selection_without_model(self):
        p=ObservedPanel();self.addCleanup(p.close)
        self.assertEqual(p.selection_states,[])
        p.entries.setCurrentRow(0);p.entries.setCurrentRow(-1)
        self.assertEqual(p.selection_states,[True,True])
        p.entries.setCurrentRow(0);count=len(p.selection_states)
        p.refresh_reference();self.assertEqual(len(p.selection_states),count)
        with patch('rouge.current_reward_origins_view.model.reference',return_value=None):
            self.assertFalse(p.refresh_reference())
        self.assertIsNone(p.result);self.assertEqual(len(p.selection_states),count)
        self.assertTrue(p.refresh_reference());self.assertEqual(len(p.selection_states),count)
        p.entries.setCurrentRow(0);self.assertTrue(all(p.selection_states))

    def test_broken_selection_call_order_is_not_silently_ignored(self):
        p=CurrentRewardOriginsPanel('relics','rogue_6_relic_cargo_13');self.addCleanup(p.close)
        p._clear()
        with self.assertRaises(TypeError):p._selected(None)
