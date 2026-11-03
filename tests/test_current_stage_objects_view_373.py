import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
from unittest.mock import patch
import unittest
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QTextCursor
from rouge import current_stage_objects as model
from rouge.current_stage_objects_view import CurrentStageObjectsPanel,CurrentStageObjectsDialog
class CurrentStageObjectsView373Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.app=QApplication.instance()or QApplication([])
    def setUp(self):self.panel=CurrentStageObjectsPanel('ro6_n_1_1');self.panel.resize(1000,440);self.panel.show();self.app.processEvents()
    def tearDown(self):self.panel.close();self.panel.deleteLater();self.app.processEvents()
    def select(self):self.panel.entries.setCurrentIndex(1);self.app.processEvents();self.assertIsNotNone(self.panel.selected())
    def test_initial_scope_unselected_and_actual_activation_unselected(self):self.assertIsNotNone(self.panel.result);self.assertIsNone(self.panel.selected());self.assertFalse(self.panel.action_button.isEnabled());self.assertFalse(self.panel.position_button.isEnabled())
    def test_search_and_link_filters_are_real_separate_choices(self):
        self.panel.search.setText('祭坛');self.app.processEvents();self.assertEqual(self.panel.entries.count(),2);self.panel.link.setCurrentIndex(self.panel.link.findData('linked'));self.assertEqual(self.panel.entries.count(),1);self.assertIsNone(self.panel.selected())
    def test_exact_activation_signal(self):
        received=[];self.panel.actionSelected.connect(received.append);self.select();self.panel.activations.setCurrentIndex(1);self.assertTrue(self.panel.follow_action());self.assertEqual(received,['4'])
    def test_instance_map_opens_exact_declaration_not_activation_route(self):
        self.select();self.assertTrue(self.panel.open_position());p=self.panel.position_dialog.panel;self.assertEqual(p.key,self.panel.entries.currentData());self.assertIsNotNone(p.result);self.assertEqual(p.result['row']['raw']['position'],self.panel.selected()['raw']['position'])
    def test_cards_do_not_expose_position_or_activation_buttons(self):
        p=CurrentStageObjectsPanel('ro6_n_2_2');p.kind.setCurrentIndex(p.kind.findData('card'));p.entries.setCurrentIndex(1);self.assertEqual(p.selected()['kind'],'card');self.assertFalse(p.position_button.isEnabled());self.assertFalse(p.action_button.isEnabled());p.deleteLater()
    def test_same_source_keeps_search_filters_selection_activation_and_two_readings(self):
        self.select();self.panel.activations.setCurrentIndex(1);key=self.panel.entries.currentData();action=self.panel.activations.currentData()
        for reader in(self.panel.player,self.panel.technical):
            self.panel.tabs.setCurrentWidget(reader);cursor=reader.textCursor();cursor.setPosition(12);cursor.setPosition(30,QTextCursor.MoveMode.KeepAnchor);reader.setTextCursor(cursor);prior=(cursor.anchor(),cursor.position(),cursor.selectedText());tab=self.panel.tabs.currentIndex();self.assertTrue(self.panel.refresh_reference());now=reader.textCursor();self.assertEqual((now.anchor(),now.position(),now.selectedText()),prior);self.assertEqual(self.panel.tabs.currentIndex(),tab)
        self.assertEqual(self.panel.entries.currentData(),key);self.assertEqual(self.panel.activations.currentData(),action)
    def test_changed_selection_clears_actual_owned_map(self):
        self.select();self.panel.open_position();d=self.panel.position_dialog;self.panel.entries.setCurrentIndex(2);self.assertFalse(d.isVisible());self.assertIsNone(d.panel.result);self.assertIsNone(self.panel.selected_action())
    def test_bad_source_clears_readers_and_owned_map(self):
        self.select();self.panel.open_position();d=self.panel.position_dialog
        with patch.object(model,'packet',return_value=None):self.assertFalse(self.panel.refresh_reference())
        self.assertIsNone(self.panel.result);self.assertEqual(self.panel.technical.toPlainText(),'');self.assertFalse(d.isVisible());self.assertIsNone(d.panel.result)
    def test_source_recovery_requires_manual_reselection(self):
        self.select();self.panel.clear_reference();self.assertTrue(self.panel.refresh_reference());self.assertIsNone(self.panel.selected());self.assertIsNone(self.panel.selected_action())
    def test_forged_snapshot_cannot_jump_or_open_position(self):
        self.select();self.panel.activations.setCurrentIndex(1);self.panel.result['entries'][0]['name']='forged';self.assertFalse(self.panel.follow_action());self.assertIsNone(self.panel.result)
    def test_direct_close_and_Escape_done_clear_dialog_and_map(self):
        for via in('close','reject'):
            d=CurrentStageObjectsDialog('ro6_n_1_1');d.show();d.panel.entries.setCurrentIndex(1);d.panel.open_position();m=d.panel.position_dialog;getattr(d,via)();self.app.processEvents();self.assertIsNone(d.panel.result);self.assertFalse(m.isVisible());self.assertIsNone(m.panel.result);d.deleteLater()
