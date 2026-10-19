from copy import deepcopy
from unittest.mock import patch
import unittest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
from rouge.expansion_view import ExpansionUpdatePanel
from rouge.battle_preview import battle_data

class CurrentBattleIntegration314Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.app=QApplication.instance()or QApplication([])
    def panel(self):
        p=ExpansionUpdatePanel();p.show();self.addCleanup(p.close);self.app.processEvents();return p
    def test_exact_current_stage_opens_its_own_preview_legacy_baseline_unmodified(self):
        legacy=deepcopy(battle_data());p=self.panel();key='ro6_n_4_1_dlc1';i=next(i for i in range(p.entries.count())if p.entries.item(i).data(Qt.ItemDataRole.UserRole)==key)
        p.entries.setCurrentRow(i);self.assertTrue(p.battle_button.isEnabled());self.assertTrue(p.open_current_battle());d=p.current_battle_dialog;self.addCleanup(d.close);self.app.processEvents()
        self.assertTrue(d.isVisible());self.assertEqual(d.panel.result['id'],key);self.assertEqual(d.panel.result['level_key'],'levels/obt/roguelike/ro6/dlc1/level_rogue6_4-1_dlc1.json');self.assertEqual(battle_data(),legacy)
    def test_nonstage_source_failure_and_no_selection_have_no_battle_jump(self):
        p=self.panel();self.assertFalse(p.open_current_battle());self.assertFalse(p.battle_button.isVisible())
        p.category.setCurrentIndex(p.category.findData('choices'));p.entries.setCurrentRow(0);self.assertFalse(p.battle_button.isVisible());self.assertFalse(p.open_current_battle())
        with patch('rouge.expansion_reference.packet',return_value=None):self.assertFalse(p.refresh_reference());self.assertFalse(p.battle_button.isEnabled());self.assertFalse(p.open_current_battle())
    def test_reopening_and_parent_clear_do_not_leave_stale_child_dialogs(self):
        p=self.panel();p.entries.setCurrentRow(0);self.assertTrue(p.open_current_battle());old=p.current_battle_dialog;self.addCleanup(old.close)
        self.assertTrue(p.open_current_battle());current=p.current_battle_dialog;self.addCleanup(current.close);self.assertFalse(old.isVisible());self.assertTrue(current.isVisible())
        with patch('rouge.expansion_reference.packet',return_value=None):self.assertFalse(p.refresh_reference());self.assertFalse(current.isVisible())

if __name__=='__main__':unittest.main()
