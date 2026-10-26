import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
from unittest.mock import patch
from copy import deepcopy
import unittest
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QTextCursor
from rouge import current_enemy_spawns as model
from rouge.current_enemy_spawns_view import CurrentEnemySpawnsPanel,CurrentEnemySpawnsDialog

class CurrentEnemySpawnsView371Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.app=QApplication.instance()or QApplication([])
    def setUp(self):self.panel=CurrentEnemySpawnsPanel('ro6_n_1_1','5');self.panel.resize(1000,420);self.panel.show();self.app.processEvents()
    def tearDown(self):self.panel.close();self.panel.deleteLater();self.app.processEvents()
    def select(self):self.panel.entries.setCurrentIndex(1);self.app.processEvents();self.assertIsNotNone(self.panel.selected())
    def test_initial_exact_enemy_and_unselected_actions(self):self.assertEqual(self.panel.result['enemy_key'],'5');self.assertIsNone(self.panel.selected());self.assertFalse(self.panel.action_button.isEnabled())
    def test_actual_main_branch_filter_and_changed_filter_drops_old_entry(self):
        self.select();self.panel.kind.setCurrentIndex(self.panel.kind.findData('branch'));self.assertIsNone(self.panel.selected());self.assertFalse(self.panel.position_button.isEnabled());self.assertEqual(self.panel.entries.count(),1)
    def test_action_signal_contains_exact_ordinal(self):
        received=[];self.panel.actionSelected.connect(received.append);self.select();key=self.panel.entries.currentData();self.assertTrue(self.panel.follow_action());self.assertEqual(received,[key])
    def test_position_signal_requires_existing_exact_position_reference(self):
        received=[];self.panel.actionPositionRequested.connect(received.append);self.select();key=self.panel.entries.currentData();self.assertTrue(self.panel.follow_position());self.assertEqual(received,[key])
    def test_no_direct_record_keeps_unknown_instead_of_excluding_entity(self):
        p=CurrentEnemySpawnsPanel('ro6_n_1_1','8');self.assertEqual(p.result['entries'],[]);self.assertIn('不能据此排除',p.player.toPlainText());self.assertFalse(p.action_button.isEnabled());p.deleteLater()
    def test_same_source_refresh_keeps_filter_selection_tab_and_two_readers(self):
        self.select();self.panel.kind.setCurrentIndex(self.panel.kind.findData('main'));self.select();key=self.panel.entries.currentData()
        for reader in(self.panel.player,self.panel.technical):
            self.panel.tabs.setCurrentWidget(reader);c=reader.textCursor();c.setPosition(10);c.setPosition(25,QTextCursor.MoveMode.KeepAnchor);reader.setTextCursor(c);before=(c.anchor(),c.position(),c.selectedText());tab=self.panel.tabs.currentIndex();self.assertTrue(self.panel.refresh_reference());now=reader.textCursor();self.assertEqual((now.anchor(),now.position(),now.selectedText()),before);self.assertEqual(self.panel.tabs.currentIndex(),tab)
        self.assertEqual(self.panel.entries.currentData(),key);self.assertEqual(self.panel.kind.currentData(),'main')
    def test_bad_source_clears_both_readers_portrait_and_actions(self):
        self.select();received=[];self.panel.sourceInvalidated.connect(lambda:received.append(True))
        with patch.object(model,'evidence',return_value=None):self.assertFalse(self.panel.refresh_reference())
        self.assertIsNone(self.panel.result);self.assertIsNone(self.panel.selected());self.assertEqual(self.panel.technical.toPlainText(),'');self.assertEqual(self.panel.player.toPlainText(),model.UNAVAILABLE);self.assertFalse(self.panel.action_button.isEnabled());self.assertEqual(received,[True]);self.assertEqual(self.panel.portrait.text(),'')
    def test_recovery_requires_manual_action_reselection(self):
        self.select();self.panel.clear_reference();self.assertTrue(self.panel.refresh_reference());self.assertIsNone(self.panel.selected());self.assertFalse(self.panel.action_button.isEnabled())
    def test_forged_old_snapshot_cannot_send_action(self):
        self.select();self.panel.result['enemy']['name']='forged';self.assertFalse(self.panel.follow_action());self.assertIsNone(self.panel.result)
    def test_position_source_failure_clears_old_snapshot(self):
        self.select()
        with patch.object(model,'position_reference',return_value=None):self.assertFalse(self.panel.follow_position())
        self.assertIsNone(self.panel.result)
    def test_direct_dialog_close_and_escape_done_clear_actual_data(self):
        for via in('close','reject'):
            d=CurrentEnemySpawnsDialog('ro6_n_1_1','0');d.show();self.app.processEvents();self.assertIsNotNone(d.panel.result);getattr(d,via)();self.app.processEvents();self.assertIsNone(d.panel.result);self.assertEqual(d.panel.technical.toPlainText(),'');d.deleteLater()
