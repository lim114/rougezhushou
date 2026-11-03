"""Qt candidate tests; written only during preparation, not yet executed."""
import unittest
from unittest.mock import patch
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication
from rouge import documented_choice_items as results
from rouge.documented_choice_item_view import DocumentedChoiceItemPanel


class DocumentedChoiceItemViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance() or QApplication([])
    def setUp(self):
        self.panel=DocumentedChoiceItemPanel();self.panel.resize(850,650)
        self.panel.set_reference(results.EVENT,scope_key='public:informant');self.panel.show();self.qt.processEvents()
    def tearDown(self):self.panel.close();self.panel.deleteLater();self.qt.processEvents()
    def choose(self):self.panel.choice.setCurrentIndex(0);self.qt.processEvents()
    def state(self,reader):
        c=reader.textCursor();return c.anchor(),c.position(),reader.verticalScrollBar().value()

    def test_default_does_not_choose_or_open_and_icon_is_empty(self):
        self.assertEqual(self.panel.choice.count(),1);self.assertEqual(self.panel.choice.currentIndex(),-1)
        self.assertFalse(self.panel.open_item_button.isEnabled());self.assertFalse(self.panel.icon.isVisible())
        self.assertIsNone(self.panel._details_identity);self.assertIn('尚未手动打开',self.panel.item_text.toPlainText())

    def test_manual_read_shows_actual_source_icon_full_item_and_unlock_distinction(self):
        self.choose();self.assertFalse(self.panel.icon.isVisible());self.assertIsNone(self.panel._details_identity)
        self.panel.open_item_button.click();self.qt.processEvents()
        self.assertTrue(self.panel.icon.isVisible());self.assertFalse(self.panel.icon.pixmap().isNull())
        text=self.panel.item_text.toPlainText();self.assertIn('沙盘α · 收藏品',text)
        self.assertIn('部署费用+2',text);self.assertIn('来自梅兰德基金会',text)
        self.assertIn('完成游戏结局',text);self.assertIn('不等于本事件的完整出现条件',text)
        self.assertIn('实际领取',text);self.assertNotIn('rogue_6',text);self.assertNotIn('https://',text)

    def test_same_scope_refresh_preserves_opened_item_tabs_and_nonzero_reading(self):
        self.choose();self.panel.open_item_button.click();self.panel.reading_tabs.setCurrentWidget(self.panel.source_text)
        reader=self.panel.source_text;bar=reader.verticalScrollBar();self.qt.processEvents();self.assertGreater(bar.maximum(),0)
        cursor=QTextCursor(reader.document());cursor.setPosition(4);cursor.setPosition(30,QTextCursor.MoveMode.KeepAnchor)
        reader.setTextCursor(cursor);bar.setValue(max(1,bar.maximum()//2));self.qt.processEvents()
        before=self.state(reader);self.assertGreater(before[-1],0);selected=self.panel.choice.currentData()
        self.panel.set_reference(results.EVENT,scope_key='public:informant');self.qt.processEvents()
        self.assertEqual(self.panel.choice.currentData(),selected);self.assertEqual(self.state(reader),before)
        self.assertEqual(self.panel.reading_tabs.currentWidget(),reader);self.assertTrue(self.panel.icon.isVisible())

    def test_scope_or_event_change_clears_opened_item_icon_and_selection(self):
        self.choose();self.panel.open_item_button.click()
        self.panel.set_reference(results.EVENT,scope_key='another-node')
        self.assertIsNone(self.panel.choice.currentData());self.assertIsNone(self.panel._details_identity)
        self.assertFalse(self.panel.icon.isVisible());self.assertFalse(self.panel.open_item_button.isEnabled())
        self.panel.set_reference('community_group_007',scope_key='other')
        self.assertEqual(self.panel.choice.count(),0)
        for reader in (self.panel.item_text,self.panel.choice_text,self.panel.source_text):
            self.assertNotIn('沙盘α',reader.toPlainText())

    def test_source_failure_clears_all_three_readers_icon_and_recovery_stays_unselected(self):
        self.choose();self.panel.open_item_button.click()
        with patch.object(results,'event_item_references',side_effect=OSError('isolated source failure')):
            self.panel.refresh_reference()
        self.assertEqual(self.panel.choice.count(),0);self.assertFalse(self.panel.icon.isVisible())
        for reader in (self.panel.item_text,self.panel.choice_text,self.panel.source_text):
            self.assertIn('已清除',reader.toPlainText());self.assertNotIn('沙盘α',reader.toPlainText())
        self.panel.refresh_reference();self.assertEqual(self.panel.choice.count(),1)
        self.assertIsNone(self.panel.choice.currentData());self.assertIsNone(self.panel._details_identity)
        self.assertFalse(self.panel.icon.isVisible());self.assertFalse(self.panel.open_item_button.isEnabled())

    def test_detail_revalidation_failure_cannot_keep_old_icon_or_item(self):
        self.choose();self.panel.open_item_button.click()
        with patch.object(results,'item_details',return_value={'status':'unknown'}):self.panel.refresh_reference()
        self.assertFalse(self.panel.icon.isVisible());self.assertIsNone(self.panel._details_identity)
        for reader in (self.panel.item_text,self.panel.choice_text,self.panel.source_text):self.assertNotIn('沙盘α',reader.toPlainText())

    def test_tampered_complete_reference_key_is_not_opened_as_the_first_item(self):
        self.choose();self.panel.choice.blockSignals(True)
        self.panel.choice.setItemData(0,'forged-other-choice-item');self.panel.choice.blockSignals(False)
        self.panel.open_selected_item();self.assertIsNone(self.panel._details_identity)
        self.assertFalse(self.panel.icon.isVisible());self.assertEqual(self.panel.choice.count(),0)
        self.assertIn('已清除',self.panel.item_text.toPlainText())

    def test_deselect_does_not_keep_previous_item_as_current_details(self):
        self.choose();self.panel.open_item_button.click();self.panel.choice.setCurrentIndex(-1);self.qt.processEvents()
        self.assertIsNone(self.panel._details_identity);self.assertFalse(self.panel.icon.isVisible())
        self.assertFalse(self.panel.open_item_button.isEnabled());self.assertIn('尚未手动打开',self.panel.item_text.toPlainText())


if __name__=='__main__':unittest.main()
