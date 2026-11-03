"""Candidate354 view cases; preparation only, not a claimed native acceptance."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import json
import unittest
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication
from rouge import current_recruit_tickets as model
from rouge.current_recruit_tickets_view import CurrentRecruitTicketsDialog
from tests.test_current_recruit_tickets_354 import clone


class CurrentRecruitTicketsView354Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])

    def dialog(self):
        dialog=CurrentRecruitTicketsDialog();dialog.show();self.qt.processEvents();self.addCleanup(dialog.close);return dialog

    def select(self,panel,identity):
        row=next(i for i in range(panel.entries.count())if panel.entries.item(i).data(Qt.ItemDataRole.UserRole)==identity)
        panel.entries.setCurrentRow(row);self.qt.processEvents()

    def test_47_manual_choices_complete_chinese_and_real_independent_branches(self):
        panel=self.dialog().panel;self.assertEqual(panel.entries.count(),47);self.assertIsNone(panel.ticket_id)
        self.assertEqual(panel.profession.count(),9);self.assertEqual(panel.family.count(),6)
        self.assertTrue(panel.exit_button.isEnabled());self.assertTrue(panel.rest_button.isEnabled())
        for row in model.reference()['rows']:
            self.select(panel,row['id']);self.assertEqual(panel.result['selected'],row)
            self.assertIn(model.version._plain(row['original_item']['usage']),panel.player.toPlainText())
            self.assertEqual(json.loads(panel.technical.toPlainText()),json.loads(json.dumps(panel.result)))
        panel.profession.setCurrentIndex(panel.profession.findData('PIONEER'))
        panel.family.setCurrentIndex(panel.family.findData('protocol'));self.qt.processEvents()
        wanted=model.reference(profession='PIONEER',ticket_family='protocol')['rows']
        self.assertEqual(panel.entries.count(),len(wanted));self.assertIsNone(panel.ticket_id)
        self.assertIsNone(panel.result['actual_inventory']);self.assertFalse(panel.result['run_updated'])

    def test_two_real_nonzero_readings_filter_selection_and_tab_survive_refresh(self):
        dialog=self.dialog();dialog.resize(720,390);panel=dialog.panel
        panel.search.setText('高级人事资深');self.select(panel,'rogue_6_recruit_ticket_all_discount')
        for reader in(panel.player,panel.technical):
            panel.tabs.setCurrentWidget(reader);self.qt.processEvents();cursor=reader.textCursor()
            cursor.setPosition(3);cursor.setPosition(17,QTextCursor.MoveMode.KeepAnchor);reader.setTextCursor(cursor)
            bar=reader.verticalScrollBar();self.assertGreater(bar.maximum(),0);bar.setValue(min(4,bar.maximum()))
            old=(cursor.anchor(),cursor.position(),bar.value(),panel.tabs.currentIndex(),panel.ticket_id,panel.search.text())
            self.assertTrue(panel.refresh_reference());self.qt.processEvents();cursor=reader.textCursor()
            self.assertEqual(old,(cursor.anchor(),cursor.position(),bar.value(),panel.tabs.currentIndex(),panel.ticket_id,panel.search.text()))

    def test_exact_exit_and_rest_original_entries_no_guessed_inventory(self):
        panel=self.dialog().panel
        self.assertTrue(panel.open_event('exit'));child=panel.event_dialog
        self.assertEqual(child.panel.source_request,{'category':'choices','key':'choice_ro6_final1_2'})
        self.assertEqual(child.panel.choice_id,'document-choice:799598136660c8ca2985fd825fcc47e0e8b380dc4eeeab004841efe9426f6cbe')
        self.assertTrue(all(value is None for value in child.panel.result['declared'].values()))
        self.assertTrue(panel.open_event('rest'));self.assertFalse(child.isVisible());child=panel.event_dialog
        self.assertEqual(child.panel.source_request,{'category':'choices','key':'choice_ro6_rest_7'})
        self.assertEqual(child.panel.choice_id,'document-choice:13fa1fe394f2e12446f89f31bc957eed734baf21743a9fad16c7949e3e3e027a')
        self.assertIsNone(child.panel.result['actual_received']);self.assertIsNone(child.panel.result['actual_eligible'])
        self.assertFalse(panel.open_event('unknown'));self.assertTrue(child.isVisible())
        panel.close_children();self.assertFalse(child.isVisible());self.assertIsNone(panel.event_dialog)

    def test_bad_source_closes_child_clears_both_readers_and_recovers_manually(self):
        panel=self.dialog().panel;self.select(panel,'rogue_6_recruit_ticket_pioneer');self.assertTrue(panel.open_event('exit'));child=panel.event_dialog
        with TemporaryDirectory()as folder:
            root=Path(folder);clone(root);path=root/model.DATA;raw=path.read_bytes()
            with patch.object(model,'ROOT',root):
                path.write_bytes(raw+b'x');self.assertFalse(panel.refresh_reference())
                self.assertIsNone(panel.result);self.assertIsNone(panel.ticket_id);self.assertEqual(panel.entries.count(),0)
                self.assertEqual(panel.player.toPlainText(),'');self.assertEqual(panel.technical.toPlainText(),'')
                self.assertFalse(panel.exit_button.isEnabled());self.assertFalse(child.isVisible())
                path.write_bytes(raw);self.assertTrue(panel.refresh_reference());self.assertIsNone(panel.ticket_id)
                self.assertIsNone(panel.entries.currentItem());self.assertEqual(panel.entries.count(),47)
                self.select(panel,'rogue_6_recruit_ticket_pioneer');self.assertTrue(panel.open_event('exit'))

    def test_filter_change_and_actual_parent_close_clear_owned_event(self):
        dialog=self.dialog();panel=dialog.panel;self.select(panel,'rogue_6_recruit_ticket_pioneer')
        self.assertTrue(panel.open_event('exit'));child=panel.event_dialog
        panel.profession.setCurrentIndex(panel.profession.findData('SNIPER'));self.qt.processEvents()
        self.assertFalse(child.isVisible());self.assertIsNone(panel.ticket_id)
        self.assertTrue(panel.open_event('rest'));child=panel.event_dialog
        dialog.close();self.qt.processEvents();self.assertFalse(child.isVisible())


if __name__=='__main__':unittest.main()
