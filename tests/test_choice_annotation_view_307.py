"""Changed default reading and its source-loss behavior; actual Qt run by root."""
import unittest
from unittest.mock import patch
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication
from rouge import choice_annotations as model
from rouge.node_catalog_view import NodeCatalogPanel,event_details_text,event_text


class ChoiceAnnotationView307Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])

    def setUp(self):
        self.panel=NodeCatalogPanel();self.panel.resize(1100,700);self.panel.show()
        self.addCleanup(self.panel.close);self.qt.processEvents()

    def select(self,event_id):
        self.panel.list.setCurrentRow(next(i for i,e in enumerate(self.panel.entries)
            if e['kind']=='event'and e['record']['id']==event_id))
        self.qt.processEvents()

    def test_player_and_technical_default_reading_classifies_all_ten_with_existing_entries(self):
        for event_id in dict.fromkeys(k[0]for k in model.NEW_RESULT_IDENTITIES):
            self.select(event_id)
            text=self.panel.player_detail.toPlainText();technical=self.panel.detail.toPlainText()
            for identity in model.NEW_RESULT_IDENTITIES:
                if identity[0]!=event_id:continue
                row=model.choice_reference(*identity)['reference']
                self.assertIn(row['label']+'（原文）：',text)
                self.assertIn(row['text'],technical)
                self.assertNotIn('条件原文：'+row['text'],text)
            self.assertNotIn('这段附加条件尚未完整解析',text)
        self.select('community_group_023')
        self.assertIn('数量不一致',self.panel.player_detail.toPlainText())
        self.assertFalse(self.panel.resting_button.isHidden())
        self.select('community_group_031')
        self.assertFalse(self.panel.curiosity_node_rules_button.isHidden())

    def test_same_identity_refresh_keeps_current_tab_and_nonzero_scroll(self):
        self.select('community_group_023')
        for widget in(self.panel.player_detail,self.panel.detail):
            self.panel.reading_tabs.setCurrentWidget(widget);self.qt.processEvents()
            cursor=widget.textCursor();cursor.setPosition(3);cursor.setPosition(12,QTextCursor.MoveMode.KeepAnchor)
            widget.setTextCursor(cursor);bar=widget.verticalScrollBar();self.assertGreater(bar.maximum(),0)
            bar.setValue(min(25,bar.maximum()));position=bar.value();selection=widget.textCursor().selectedText()
            self.panel.refresh();self.qt.processEvents()
            self.assertIs(self.panel.reading_tabs.currentWidget(),widget)
            self.assertEqual(widget.textCursor().selectedText(),selection);self.assertEqual(bar.value(),position)

    def test_source_loss_drops_old_classification_but_keeps_literal_note_and_raw_details_fresh(self):
        self.select('community_group_008')
        self.assertIn('选择后可能的战斗（原文）：',self.panel.player_detail.toPlainText())
        # The legacy event_text cache must not hold a formerly valid classification.
        self.assertIn('选择后可能的战斗（原文）：',event_text('community_group_008'))
        with patch.object(model,'_packet',return_value=None):
            self.panel.refresh();self.qt.processEvents()
            text=self.panel.player_detail.toPlainText()
            self.assertIn('附注原文（类型待核对）：',text)
            self.assertNotIn('选择后可能的战斗（原文）：',text)
            self.assertIn('随机出现以下追猎可遭遇关卡的一个',text)
            self.assertIn('附注原文（类型待核对）：',event_text('community_group_008'))
            self.assertIn('附注原文（类型待核对）：',event_details_text('community_group_008'))
        self.panel.refresh();self.qt.processEvents()
        self.assertIn('选择后可能的战斗（原文）：',self.panel.player_detail.toPlainText())


if __name__=='__main__':unittest.main()
