from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication
from rouge import current_startup as m
from rouge.current_startup_view import CurrentStartupDialog
from rouge.expansion_view import ExpansionUpdatePanel
from tests.test_current_startup_350 import clone
class CurrentStartupView350Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])
    def dialog(self,cid=None):
        d=CurrentStartupDialog(m.locate('choices',cid)if cid else None);d.show();self.qt.processEvents();self.addCleanup(d.close);return d
    def select(self,p,cid):
        p.choices.setCurrentRow(next(i for i in range(p.choices.count())if p.choices.item(i).data(Qt.ItemDataRole.UserRole)==cid));self.qt.processEvents()
    def test_all_twelve_exact_selections_related_inputs_only_and_six_images(self):
        for cid in m.reference()['choices']:
            p=self.dialog(cid).panel;self.assertEqual(p.choice_id,cid);inherited=p.result['choices'][cid]['kind']=='inherited'
            self.assertEqual(p.gold.isVisible(),cid=='choice_ro6_startbuff_3');self.assertEqual(p.inherited.isVisible(),inherited)
            if inherited:self.assertFalse(p.reward_icon.pixmap().isNull())
            self.assertFalse(p.next_button.isVisible());self.assertFalse(p.battle_button.isVisible());self.assertIsNone(p.result['actual_received']);p.close()
    def test_group_filters_do_not_claim_actual_menu_or_hold_selection_in_wrong_group(self):
        p=self.dialog('choice_ro6_startbuff_7').panel;p.group.setCurrentIndex(p.group.findData('regular'));self.assertEqual(p.choices.count(),6);self.assertIsNone(p.choice_id);self.assertIn('不是本次菜单',p.group.itemText(0));self.assertIsNone(p.result['actual_displayed_choice_ids'])
        p.group.setCurrentIndex(p.group.findData('inherited'));self.assertEqual(p.choices.count(),6);self.select(p,'choice_ro6_startbuff_10');self.assertTrue(p.inherited.isVisible())
    def test_two_nonzero_readings_and_manual_inputs_survive_same_source_refresh(self):
        d=self.dialog('choice_ro6_startbuff_3');d.resize(700,390);p=d.panel;p.gold.setValue(5);p.previous.setValue(2);p.mode.setCurrentIndex(p.mode.findData('NORMAL'))
        for reader in(p.player,p.technical):
            p.tabs.setCurrentWidget(reader);self.qt.processEvents();cursor=reader.textCursor();cursor.setPosition(3);cursor.setPosition(15,QTextCursor.MoveMode.KeepAnchor);reader.setTextCursor(cursor);bar=reader.verticalScrollBar();self.assertGreater(bar.maximum(),0);bar.setValue(min(3,bar.maximum()));old=(cursor.anchor(),cursor.position(),bar.value(),p.tabs.currentIndex(),p.choice_id)
            self.assertTrue(p.refresh_reference());self.qt.processEvents();cursor=reader.textCursor();self.assertEqual(old,(cursor.anchor(),cursor.position(),bar.value(),p.tabs.currentIndex(),p.choice_id))
        self.assertEqual(p.gold.value(),5);self.assertEqual(p.previous.value(),2)
    def test_bad_source_clears_selection_text_and_image_then_manual_recovery(self):
        p=self.dialog('choice_ro6_startbuff_7').panel
        with TemporaryDirectory()as folder:
            root=Path(folder);clone(root);path=root/m.DATA;raw=path.read_bytes()
            with patch.object(m,'ROOT',root):
                path.write_bytes(raw+b'x');self.assertFalse(p.refresh_reference());self.assertIsNone(p.result);self.assertEqual(p.technical.toPlainText(),'');self.assertTrue(p.reward_icon.pixmap().isNull());path.write_bytes(raw);self.assertTrue(p.refresh_reference());self.assertIsNone(p.choice_id)
    def test_version_actual_source_target_refresh_and_close(self):
        p=ExpansionUpdatePanel();self.addCleanup(p.close);p.show();p.scope.setCurrentIndex(p.scope.findData(False));p.category.setCurrentIndex(p.category.findData('choices'))
        cid='choice_ro6_startbuff_12';p.entries.setCurrentRow(next(i for i in range(p.entries.count())if p.entries.item(i).data(Qt.ItemDataRole.UserRole)==cid));self.qt.processEvents();self.assertTrue(p.flow_button.isVisible());self.assertTrue(p.open_documented_flow());d=p.flow_dialog;self.assertEqual(d.panel.choice_id,cid);self.assertTrue(p.refresh_reference());self.assertIs(p.flow_dialog,d);self.assertEqual(d.panel.choice_id,cid);p.close();self.assertFalse(d.isVisible())
if __name__=='__main__':unittest.main()
