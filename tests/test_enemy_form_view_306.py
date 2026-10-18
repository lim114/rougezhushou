"""Necessary reader and manual-entry behavior; actual Qt execution by root only."""
import unittest
from unittest.mock import patch
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication

from rouge import enemy_form_reference as model
from rouge.enemy_form_view import EnemyFormReferencePanel,target_identity
from rouge.battle_view import BattlePreviewPanel

KEY=('ro6_n_2_3','enemy_2133_shdopl_lancer',0)


class EnemyFormView306Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qt=QApplication.instance()or QApplication([])

    def reader(self):
        window=EnemyFormReferencePanel();window.resize(820,420)
        window.show();self.addCleanup(window.close);self.qt.processEvents()
        return window

    def battle(self):
        panel=BattlePreviewPanel();self.addCleanup(panel.close)
        panel._load_stage(KEY[0]);panel._render_enemy(*KEY[1:])
        return panel

    def test_all_eight_references_show_exact_distinct_portraits_and_independent_abilities(self):
        window=self.reader()
        for sid in model.STAGES:
            for eid in model.ALIASES:
                key=(sid,eid,0)
                with self.subTest(key=key):
                    self.assertTrue(window.set_reference(key))
                    row=window.result['reference'];target=row['disguise_enemy_reference']
                    self.assertEqual(window.body_picture.key[:2],('enemy',eid))
                    self.assertEqual(window.disguise_picture.key[:2],('enemy',target['id']))
                    text=window.player.toPlainText()
                    self.assertIn(target['name'],text)
                    for ability in target['abilities']:self.assertIn(ability,text)
                    self.assertIn('空植体',text);self.assertIn('空值体',text)
                    self.assertIn('实际召唤等级',text)
                    self.assertNotIn('enemy_2133_',text)
                    self.assertFalse(window.isModal())
                    self.assertIs(window.tabs.currentWidget(),window.player)
                    self.assertIn('complete_original_reference',window.technical.toPlainText())
                    self.assertTrue(all(window.result[field]is None for field in model.ACTUAL_FIELDS))

    def test_same_identity_refresh_preserves_each_reader_selection_scroll_and_tab(self):
        window=self.reader();self.assertTrue(window.set_reference(KEY))
        for widget in (window.player,window.technical):
            window.tabs.setCurrentWidget(widget);self.qt.processEvents()
            cursor=widget.textCursor();cursor.setPosition(3)
            cursor.setPosition(12,QTextCursor.MoveMode.KeepAnchor);widget.setTextCursor(cursor)
            bar=widget.verticalScrollBar();self.assertGreater(bar.maximum(),0)
            bar.setValue(min(17,bar.maximum()));scroll=bar.value()
            selected=widget.textCursor().selectedText();scope=window.scope_key
            self.assertTrue(window.refresh_reference());self.qt.processEvents()
            self.assertIs(window.tabs.currentWidget(),widget)
            self.assertEqual(window.scope_key,scope)
            self.assertEqual(widget.textCursor().selectedText(),selected)
            self.assertEqual(bar.value(),scroll)

    def test_source_failure_clears_both_readers_and_both_pictures_until_explicit_reopen(self):
        window=self.reader();window.set_reference(KEY);window.tabs.setCurrentWidget(window.technical)
        with patch.object(model,'_packet',return_value=None):
            self.assertFalse(window.refresh_reference())
        self.assertIsNone(window.identity);self.assertIsNone(window.result)
        self.assertEqual(window.player.toPlainText(),'');self.assertEqual(window.technical.toPlainText(),'')
        self.assertEqual(window.body_picture.key,(None,None,''))
        self.assertEqual(window.disguise_picture.key,(None,None,''))
        self.assertFalse(window.refresh_reference())
        self.assertEqual(window.player.toPlainText(),'')
        self.assertTrue(window.set_reference(KEY))
        self.assertIs(window.tabs.currentWidget(),window.player)

    def test_non_target_and_mismatched_packet_clear_without_defaulting(self):
        window=self.reader();window.set_reference(KEY)
        result=model.disguise_reference(*KEY)
        for key in (None,('ro6_n_2_3','enemy_2133_shdopl',0),
                    ('ro6_n_2_3',KEY[1],False),('ro6_n_2_3',KEY[1],0.0)):
            self.assertFalse(target_identity(key));self.assertFalse(window.set_reference(key))
            self.assertIsNone(window.result)
        other=(KEY[0],model.ALIASES[1],0)
        self.assertFalse(window.set_reference(other,result))
        self.assertEqual(window.disguise_picture.key,(None,None,''))

    def test_battle_entry_only_eight_tuples_and_requires_manual_open(self):
        panel=self.battle()
        self.assertFalse(panel.enemy_form_button.isHidden())
        self.assertIsNone(panel.enemy_form_window)
        self.assertTrue(panel.open_enemy_form())
        window=panel.enemy_form_window;self.assertEqual(window.identity,KEY)
        context_before=panel.context.copy()
        panel._render_enemy(model.ALIASES[1],0)
        self.assertIsNone(window.identity);self.assertEqual(window.player.toPlainText(),'')
        self.assertEqual(window.body_picture.key,(None,None,''))
        self.assertEqual(window.disguise_picture.key,(None,None,''))
        self.assertTrue(panel.open_enemy_form())
        self.assertEqual(window.identity,(KEY[0],model.ALIASES[1],0))
        ordinary=window.result['reference']['declared_summon_enemy_key']
        panel._render_enemy(ordinary,0)
        self.assertTrue(panel.enemy_form_button.isHidden());self.assertFalse(panel.open_enemy_form())
        self.assertIsNone(window.result);self.assertEqual(window.technical.toPlainText(),'')
        panel._load_stage(None)
        self.assertTrue(panel.enemy_form_button.isHidden())
        self.assertEqual(panel.context,context_before)

    def test_battle_source_failure_recovery_enables_manual_button_without_restoring_old_window(self):
        panel=self.battle();self.assertTrue(panel.open_enemy_form())
        window=panel.enemy_form_window
        with patch.object(model,'_packet',return_value=None):
            panel._refresh_enemy_form()
            self.assertFalse(panel.enemy_form_button.isEnabled());self.assertFalse(panel.open_enemy_form())
        self.assertIsNone(window.identity);self.assertEqual(window.player.toPlainText(),'')
        panel._refresh_enemy_form()
        self.assertTrue(panel.enemy_form_button.isEnabled())
        self.assertIsNone(window.identity);self.assertEqual(window.technical.toPlainText(),'')
        self.assertTrue(panel.open_enemy_form());self.assertEqual(window.identity,KEY)


if __name__=='__main__':unittest.main()
