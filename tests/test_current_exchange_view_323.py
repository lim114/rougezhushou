from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication
from PySide6.QtTest import QTest
from rouge import current_exchange_reference as model
from rouge.current_exchange_view import CurrentExchangePanel
from rouge.expansion_view import ExpansionUpdatePanel
from tests.test_current_exchange_reference_323 import clone


class CurrentExchangeView323Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])
    def panel(self,target=None):
        p=CurrentExchangePanel(target);p.resize(950,550);p.show();self.addCleanup(p.close);self.qt.processEvents();return p

    def test_all_item_flags_filtered_separately_and_cross_filters_clear_hidden_selection(self):
        p=self.panel();self.assertEqual(p.items.count(),284);self.assertIsNone(p.item_id);self.assertEqual(p.groups.count(),9)
        p.offer.setCurrentIndex(p.offer.findData(False));self.assertEqual(p.items.count(),25);p.change.setCurrentIndex(p.change.findData('added'));self.assertEqual(p.items.count(),4)
        p._select(p.items,'rogue_6_relic_final_8');self.assertIn('不可交出',p.item_player.toPlainText());self.assertIn('不能说明能否换到',p.item_player.toPlainText())
        p.offer.setCurrentIndex(p.offer.findData(True));self.assertEqual(p.items.count(),8);self.assertIsNone(p.item_id);self.assertNotIn('祭日之契',p.item_player.toPlainText());self.assertEqual(p.item_technical.toPlainText(),'')
        p.search.setText('不存在');self.assertEqual(p.items.count(),0);self.assertIn('0件',p.count.text())

    def test_explicit_target_selection_and_all_nine_doc_groups_no_actual_reward(self):
        p=self.panel(model.target_entry('relics','rogue_6_relic_final_7'));self.assertEqual(p.item_id,'rogue_6_relic_final_7');self.assertEqual(p.tabs.currentIndex(),0)
        for i in range(p.groups.count()):
            p.groups.setCurrentRow(i);self.assertIn(p.result['data']['document_groups'][i]['title'],p.doc_player.toPlainText());self.assertIsNone(p.result['actual_reward_pool']);self.assertFalse(p.result['run_updated'])
        p=self.panel(model.target_entry('choices','choice_ro6_sacrifice2_23'));self.assertEqual(p.tabs.currentIndex(),1);self.assertEqual(p.group_id,'3');self.assertIn('1件零件',p.doc_player.toPlainText())
        p=self.panel(model.target_entry('scenes','scene_ro6_sacrifice1_enter'));self.assertEqual(p.tabs.currentIndex(),1);self.assertIsNone(p.group_id)

    def test_same_source_all_four_nonzero_readers_filters_and_selections_survive_refresh(self):
        p=self.panel();p.resize(850,460);p.offer.setCurrentIndex(p.offer.findData(False));p.change.setCurrentIndex(p.change.findData('added'));p._select(p.items,'rogue_6_relic_final_8');p.groups.setCurrentRow(3)
        for outer,inner,reader in((0,p.item_tabs,p.item_player),(0,p.item_tabs,p.item_technical),(1,p.doc_tabs,p.doc_player),(1,p.doc_tabs,p.doc_technical)):
            p.tabs.setCurrentIndex(outer);inner.setCurrentWidget(reader);self.qt.processEvents();c=reader.textCursor();c.setPosition(2);c.setPosition(13,QTextCursor.MoveMode.KeepAnchor);reader.setTextCursor(c);bar=reader.verticalScrollBar();self.assertGreater(bar.maximum(),0);bar.setValue(min(4,bar.maximum()));before=(c.anchor(),c.position(),bar.value(),p.tabs.currentIndex(),inner.currentIndex(),p.item_id,p.group_id,p.offer.currentData(),p.change.currentData())
            self.assertTrue(p.refresh_reference());self.qt.processEvents();c=reader.textCursor();self.assertEqual(before,(c.anchor(),c.position(),bar.value(),p.tabs.currentIndex(),inner.currentIndex(),p.item_id,p.group_id,p.offer.currentData(),p.change.currentData()))

    def test_actual_file_damage_clears_both_lists_and_readers_recovery_needs_selection(self):
        p=self.panel(model.target_entry('relics','rogue_6_relic_final_8'));p.groups.setCurrentRow(3)
        with TemporaryDirectory()as folder:
            root=Path(folder);clone(root);f=root/model.DATA;raw=f.read_bytes()
            with patch.object(model,'ROOT',root):
                f.write_bytes(raw+b' ');self.assertFalse(p.refresh_reference());self.assertIsNone(p.result);self.assertEqual(p.items.count(),0);self.assertEqual(p.groups.count(),0);self.assertEqual(p.item_technical.toPlainText(),'');self.assertEqual(p.doc_technical.toPlainText(),'');f.write_bytes(raw);self.assertTrue(p.refresh_reference());self.assertIsNone(p.item_id);self.assertIsNone(p.group_id)

    def test_actual_update_entries_item_scene_choice_and_owned_repeat_close(self):
        p=ExpansionUpdatePanel();p.show();self.addCleanup(p.close);p.scope.setCurrentIndex(p.scope.findData(False))
        for category,key in(('relics','rogue_6_relic_cargo_15'),('relics','rogue_6_relic_final_8'),('scenes','scene_ro6_sacrifice1_enter'),('choices','choice_ro6_sacrifice2_23')):
            p.category.setCurrentIndex(p.category.findData(category));row=next(i for i in range(p.entries.count())if p.entries.item(i).data(Qt.ItemDataRole.UserRole)==key);p.entries.setCurrentRow(row);self.assertTrue(p.exchange_button.isVisible());QTest.mouseClick(p.exchange_button,Qt.MouseButton.LeftButton);d=p.exchange_dialog;target=model.target_entry(category,key)
            self.assertTrue(d.isVisible());self.assertEqual(d.panel.item_id,target['item_id']);self.assertEqual(d.panel.group_id,target['group_id']);self.assertTrue(p.refresh_reference());self.assertTrue(d.isVisible());self.assertTrue(p.open_current_exchange());self.assertFalse(d.isVisible())
        d=p.exchange_dialog;p.category.setCurrentIndex(p.category.findData('stages'));self.assertFalse(p.exchange_button.isVisible());self.assertFalse(d.isVisible());self.assertFalse(p.open_current_exchange())

    def test_parent_failure_close_and_source_failure_block_stale_entries(self):
        p=ExpansionUpdatePanel();p.show();self.addCleanup(p.close);p.scope.setCurrentIndex(p.scope.findData(False));p.category.setCurrentIndex(p.category.findData('relics'));row=next(i for i in range(p.entries.count())if p.entries.item(i).data(Qt.ItemDataRole.UserRole)=='rogue_6_relic_final_8');p.entries.setCurrentRow(row);p.open_current_exchange();d=p.exchange_dialog
        with patch.object(model,'packet',return_value=None):self.assertFalse(p.open_current_exchange());self.assertFalse(d.isVisible());self.assertFalse(p.exchange_button.isVisible())
        p.refresh_reference();self.assertTrue(p.open_current_exchange());d=p.exchange_dialog;p.close();self.assertFalse(d.isVisible())


if __name__=='__main__':unittest.main()
