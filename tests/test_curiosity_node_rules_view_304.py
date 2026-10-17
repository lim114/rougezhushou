from copy import deepcopy
import unittest
from unittest.mock import patch

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QTextCursor
from rouge import curiosity_node_rules as model
from rouge.curiosity_node_rules_view import CuriosityNodeRulesPanel, reference_text
from rouge.node_catalog_view import NodeCatalogPanel

A='community_group_030'
B='community_group_031'
KEYS={A:[A+':scene:0:choice:'+str(n) for n in (0,1)],
      B:[B+':scene:0:choice:0',B+':scene:0:choice:1',B+':scene:2:choice:0']}


class CuriosityRulesViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gui=QApplication.instance() or QApplication([])

    def setUp(self):
        self.panel=CuriosityNodeRulesPanel()
        self.addCleanup(self.panel.close)
        self.addCleanup(self.panel._clear_battle)

    def choose(self,event,key):
        self.panel.set_reference(event,scope_key='test-scope')
        index=self.panel.choice.findData(key)
        self.assertGreaterEqual(index,0)
        self.panel.choice.setCurrentIndex(index)
        self.gui.processEvents()

    def test_five_choices_have_separate_rules_and_only_two_stage_buttons(self):
        for event,keys in KEYS.items():
            packet=model.event_reference(event)
            self.panel.set_reference(event,scope_key='test-scope')
            self.assertEqual(self.panel.choice.currentIndex(),-1)
            self.assertIsNone(self.panel.battle_window)
            for key in keys:
                with self.subTest(choice=key):
                    self.choose(event,key)
                    row=next(r for r in packet['choices'] if r['reference_id']==key)
                    text=self.panel.player_text.toPlainText()
                    for rule in row['documented_rules']:
                        self.assertIn(rule['title'],text)
                        self.assertIn(rule['text'],text)
                    self.assertEqual(self.panel.open_stage_button.isEnabled(),bool(row.get('related_stage_reference')))
                    self.assertIsNone(self.panel.battle_window)
            self.panel.set_reference(None)

    def test_plain_player_text_has_scope_and_not_raw_ids_or_implementation_terms(self):
        for event in KEYS:
            packet=model.event_reference(event)
            for row in packet['choices']:
                text=reference_text(row,packet)
                self.assertIn('第五层',text)
                self.assertIn('本局尚未确认',text)
                self.assertNotIn('FEATURE',text)
                self.assertNotIn('community_group_',text)
                self.assertNotIn('rogue_6_',text)

    def test_same_scope_refresh_preserves_selection_tab_scroll_and_cursor(self):
        self.panel.resize(620,360)
        self.choose(B,KEYS[B][0])
        reader=self.panel.source_text
        self.panel.reading_tabs.setCurrentWidget(reader)
        self.panel.show()
        self.gui.processEvents()
        cursor=reader.textCursor()
        cursor.setPosition(120)
        cursor.setPosition(160,QTextCursor.MoveMode.KeepAnchor)
        reader.setTextCursor(cursor)
        reader.verticalScrollBar().setValue(max(1,reader.verticalScrollBar().maximum()//2))
        self.assertGreater(reader.verticalScrollBar().value(),0)
        before=(self.panel.choice.currentData(),self.panel.reading_tabs.currentIndex(),reader.textCursor().selectionStart(),reader.textCursor().selectionEnd(),reader.verticalScrollBar().value())
        self.panel.set_reference(B,scope_key='test-scope')
        self.gui.processEvents()
        after=(self.panel.choice.currentData(),self.panel.reading_tabs.currentIndex(),reader.textCursor().selectionStart(),reader.textCursor().selectionEnd(),reader.verticalScrollBar().value())
        self.assertEqual(before,after)

    def test_new_scope_clears_selection_but_keeps_reference_available(self):
        self.choose(A,KEYS[A][0])
        self.panel.set_reference(A,scope_key='another-node')
        self.assertEqual(self.panel.choice.count(),2)
        self.assertEqual(self.panel.choice.currentIndex(),-1)
        self.assertFalse(self.panel.open_stage_button.isEnabled())
        self.assertNotIn('正在查阅',self.panel.player_text.toPlainText())

    def test_source_loss_clears_old_text_then_recovery_does_not_reselect(self):
        self.choose(B,KEYS[B][0])
        with patch.object(model,'event_reference',return_value={'target':True,'source_valid':False,'status':'unknown'}):
            self.panel.refresh_reference()
            self.assertEqual(self.panel.choice.count(),0)
            self.assertFalse(self.panel.open_stage_button.isEnabled())
            self.assertIsNone(self.panel.battle_window)
            self.assertIn('清除',self.panel.player_text.toPlainText())
            self.assertNotIn('无法离开',self.panel.player_text.toPlainText())
        self.panel.refresh_reference()
        self.assertEqual(self.panel.choice.currentIndex(),-1)
        self.assertEqual(self.panel.choice.count(),3)

    def test_cross_event_detail_cannot_display_or_open_stale_stage(self):
        self.panel.set_reference(B,scope_key='test-scope')
        wrong=model.choice_reference(A,A+':scene:0',KEYS[A][0])
        with patch.object(model,'choice_reference',return_value=wrong):
            self.panel.choice.setCurrentIndex(0)
            self.assertIsNone(self.panel.packet)
            self.assertFalse(self.panel.open_stage_button.isEnabled())
            self.assertFalse(self.panel.open_related_stage())

    def test_unrelated_events_have_no_entry_and_selected_node_scope_is_preserved(self):
        panel=NodeCatalogPanel()
        self.addCleanup(panel.close)
        def event(identity):
            panel.kind.setCurrentIndex(panel.kind.findData('event'))
            panel.search.clear()
            panel.refresh()
            i=next(i for i,r in enumerate(panel.entries) if r['kind']=='event' and r['record']['id']==identity)
            panel.list.setCurrentRow(i)
            self.gui.processEvents()
        event(A)
        self.assertFalse(panel.curiosity_node_rules_button.isHidden())
        panel.open_curiosity_node_rules()
        dialog=panel.curiosity_node_rules_window
        self.addCleanup(dialog.close)
        self.assertIsNotNone(dialog)
        dialog.choice.setCurrentIndex(0)
        before=deepcopy(dialog.packet)
        panel.refresh()
        self.assertEqual(dialog.packet,before)
        self.assertEqual(dialog.choice.currentData(),KEYS[A][0])
        event('community_group_001')
        self.assertTrue(panel.curiosity_node_rules_button.isHidden())
        self.assertIsNone(dialog.packet)
        self.assertEqual(dialog.choice.count(),0)

    def test_preview_only_filter_does_not_change_complete_document_on_refresh(self):
        panel=NodeCatalogPanel()
        self.addCleanup(panel.close)
        panel.kind.setCurrentIndex(panel.kind.findData('event'))
        panel.search.setText('窥视箱中')
        panel.refresh()
        index=next(i for i,r in enumerate(panel.entries) if r['kind']=='event' and r['record']['id']==B)
        panel.list.setCurrentRow(index)
        before=(panel.player_detail.toPlainText(),panel.detail.toPlainText())
        panel.event_scene_filter.setCurrentIndex(panel.event_scene_filter.findData(B+':scene:0'))
        panel.event_choice_filter.setCurrentIndex(panel.event_choice_filter.findData(KEYS[B][1]))
        self.assertEqual(panel.event_stage.count(),0)
        self.assertEqual((panel.player_detail.toPlainText(),panel.detail.toPlainText()),before)
        panel.refresh()
        self.assertEqual((panel.player_detail.toPlainText(),panel.detail.toPlainText()),before)
        self.assertEqual(panel.event_choice_filter.currentData(),KEYS[B][1])


if __name__=='__main__':
    unittest.main()
