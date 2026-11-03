"""Real fixed-source enemy reading with compact controls and heading navigation."""
from unittest.mock import patch
import unittest
from PySide6.QtCore import QPoint
from PySide6.QtGui import QFont, QTextCursor
from PySide6.QtWidgets import QApplication
from rouge import current_battle_reference as model
from rouge.current_battle_view import CurrentBattlePanel
from rouge.mechanism_reading import MechanismTextBrowser


class EnemyReadingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qt=QApplication.instance()or QApplication([])

    def panel(self):
        p=CurrentBattlePanel('ro6_n_2_6');p.resize(800,480);p.show();p.tabs.setCurrentIndex(1)
        p.enemy_choices.select_value(p.result['enemies'][0]['key']);self.qt.processEvents()
        self.addCleanup(p.close);return p

    def headings(self,p):
        return [line[1:-1]for line in p.enemy_player.toPlainText().splitlines()
                if line.startswith('【')and line.endswith('】')]

    def test_topics_follow_actual_report_headings_and_use_native_rich_text(self):
        p=self.panel();self.assertIsInstance(p.enemy_player,MechanismTextBrowser)
        self.assertEqual([p.enemy_topics.itemText(i)for i in range(1,p.enemy_topics.count())],self.headings(p))
        for i in range(1,p.enemy_topics.count()):
            number=int(p.enemy_topics.itemData(i).rsplit('-',1)[1]);block=p.enemy_player.document().findBlockByNumber(number)
            self.assertEqual(block.text(),'【'+p.enemy_topics.itemText(i)+'】')
            self.assertEqual(QTextCursor(block).charFormat().fontWeight(),QFont.Weight.Bold)

    def test_topic_selection_scrolls_to_body_section(self):
        p=self.panel();p.enemy_topics.setCurrentIndex(p.enemy_topics.findText('介绍与机制'));self.qt.processEvents()
        self.assertGreater(p.enemy_player.verticalScrollBar().value(),0)
        top=p.enemy_player.cursorForPosition(QPoint(4,4)).blockNumber()
        heading=int(p.enemy_topics.currentData().rsplit('-',1)[1]);self.assertLessEqual(top,heading)

    def test_same_source_refresh_keeps_topic_text_selection_and_scroll(self):
        p=self.panel();p.enemy_topics.setCurrentIndex(p.enemy_topics.findText('介绍与机制'));self.qt.processEvents()
        cursor=p.enemy_player.textCursor();cursor.setPosition(3);cursor.setPosition(7,QTextCursor.MoveMode.KeepAnchor);p.enemy_player.setTextCursor(cursor)
        p.enemy_player.verticalScrollBar().setValue(35);selected=cursor.selectedText();topic=p.enemy_topics.currentData();offset=p.enemy_player.verticalScrollBar().value()
        with patch.object(p.enemy_player,'setPlainText',side_effect=AssertionError('Same report must retain document')):
            self.assertTrue(p.refresh_reference())
        self.assertEqual(p.enemy_topics.currentData(),topic);self.assertEqual(p.enemy_player.textCursor().selectedText(),selected);self.assertEqual(p.enemy_player.verticalScrollBar().value(),offset)

    def test_changed_enemy_resets_topic_and_builds_only_new_headings(self):
        p=self.panel();p.enemy_topics.setCurrentIndex(p.enemy_topics.count()-1)
        p.enemy_choices.select_value(p.result['enemies'][1]['key']);self.assertEqual(p.enemy_topics.currentText(),'总览')
        self.assertEqual([p.enemy_topics.itemText(i)for i in range(1,p.enemy_topics.count())],self.headings(p))

    def test_details_are_optional_and_removed_topic_cannot_stay_selected(self):
        p=self.panel();p.details_toggle.setChecked(True);self.assertGreater(p.enemy_topics.findText('适用提醒'),0)
        p.enemy_topics.setCurrentIndex(p.enemy_topics.findText('适用提醒'));p.details_toggle.setChecked(False)
        self.assertEqual(p.enemy_topics.findText('适用提醒'),-1);self.assertEqual(p.enemy_topics.currentText(),'总览')

    def test_search_notice_only_uses_space_for_active_query(self):
        p=self.panel();self.assertTrue(p.enemy_search_notice.isHidden());name=p.result['enemies'][0]['name'];p.enemy_search.setText(name)
        self.assertFalse(p.enemy_search_notice.isHidden());self.assertIn('找到',p.enemy_search_notice.text())
        p.enemy_search.clear();self.assertTrue(p.enemy_search_notice.isHidden())
        self.assertEqual(p.enemy_search.parentWidget(),p.enemy_grid_toggle.parentWidget())

    def test_source_loss_clears_topics_and_recovery_waits_for_selection(self):
        p=self.panel();p.enemy_topics.setCurrentIndex(p.enemy_topics.count()-1)
        with patch.object(model,'stage_reference',return_value=None):self.assertFalse(p.refresh_reference())
        self.assertEqual(p.enemy_topics.count(),1);self.assertIsNone(p.enemy_topics.currentData())
        self.assertTrue(p.refresh_reference());self.assertIsNone(p.enemy_key);self.assertEqual(p.enemy_topics.count(),1)

    def test_compact_layout_leaves_reading_space_and_no_horizontal_scroll(self):
        p=self.panel()
        for width in(800,600):
            p.resize(width,480);self.qt.processEvents()
            self.assertEqual(p.enemy_scroll.horizontalScrollBar().maximum(),0)
            self.assertEqual(p.enemy_scroll.verticalScrollBar().maximum(),0)
            self.assertEqual(p.enemy_player.viewport().visibleRegion().boundingRect().height(),p.enemy_player.viewport().height())
            self.assertGreaterEqual(p.enemy_player.viewport().height(),6*p.enemy_player.fontMetrics().lineSpacing())
            self.assertTrue(p.enemy_topics.isVisible());self.assertTrue(p.enemy_spawns_button.isVisible())


if __name__=='__main__':unittest.main()
