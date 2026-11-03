"""Prepared360 actual-widget cases; not executed in cache-only preparation."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import json
import unittest
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication
from rouge import current_upgrade_tickets as model
from rouge.current_upgrade_tickets_view import CurrentUpgradeTicketsDialog
from tests.test_current_upgrade_tickets_360 import clone


class CurrentUpgradeTicketsView360Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.qt=QApplication.instance() or QApplication([])

    def dialog(self):
        dialog=CurrentUpgradeTicketsDialog(); dialog.show(); self.qt.processEvents()
        self.addCleanup(dialog.close); return dialog

    def select(self,panel,identity):
        index=next(i for i in range(panel.entries.count()) if panel.entries.item(i).data(Qt.ItemDataRole.UserRole)==identity)
        panel.entries.setCurrentRow(index); self.qt.processEvents()

    def test_18_manual_original_choices_with_real_profession_kind_star_branches(self):
        panel=self.dialog().panel; self.assertEqual(panel.entries.count(),18); self.assertIsNone(panel.ticket_id)
        self.assertEqual((panel.profession.count(),panel.kind.count(),panel.star.count()),(9,4,7))
        self.assertFalse(panel.source_button.isVisible())
        for row in model.reference()['rows']:
            self.select(panel,row['id']); self.assertEqual(panel.result['selected'],row)
            self.assertIn(model.version._plain(row['item']['usage']),panel.player.toPlainText())
            self.assertEqual(json.loads(panel.technical.toPlainText()),json.loads(json.dumps(panel.result)))
            self.assertEqual(panel.source_button.isVisible(),model.destination(row['id']) is not None)
        panel.profession.setCurrentIndex(panel.profession.findData('PIONEER'))
        panel.kind.setCurrentIndex(panel.kind.findData('relic'))
        panel.star.setCurrentIndex(panel.star.findData(6)); self.qt.processEvents()
        self.assertEqual(panel.entries.count(),1); self.assertIsNone(panel.ticket_id)
        self.assertFalse(panel.result['run_updated']); self.assertIsNone(panel.result['actual_candidates'])

    def test_two_nonzero_readings_and_filters_selection_and_tab_survive_refresh(self):
        dialog=self.dialog(); dialog.resize(760,390); panel=dialog.panel
        panel.search.setText('钝爪'); self.select(panel,'rogue_6_upgrade_ticket_pioneer_from_relic')
        for reader in (panel.player,panel.technical):
            panel.tabs.setCurrentWidget(reader); self.qt.processEvents()
            cursor=reader.textCursor(); cursor.setPosition(3); cursor.setPosition(19,QTextCursor.MoveMode.KeepAnchor); reader.setTextCursor(cursor)
            bar=reader.verticalScrollBar(); self.assertGreater(bar.maximum(),0); bar.setValue(min(5,bar.maximum()))
            before=(cursor.anchor(),cursor.position(),bar.value(),panel.tabs.currentIndex(),panel.ticket_id,panel.search.text())
            self.assertTrue(panel.refresh_reference()); self.qt.processEvents(); cursor=reader.textCursor()
            self.assertEqual(before,(cursor.anchor(),cursor.position(),bar.value(),panel.tabs.currentIndex(),panel.ticket_id,panel.search.text()))

    def test_exact_rest_original_and_selected_relic_original_are_real_readers(self):
        panel=self.dialog().panel; self.select(panel,'rogue_6_upgrade_ticket_all')
        self.assertTrue(panel.open_source()); child=panel.source_dialog
        self.assertEqual(child.panel.source_request,{'category':'choices','key':'choice_ro6_rest_4'})
        self.assertIsNone(child.panel.result['actual_received'])
        self.select(panel,'rogue_6_upgrade_ticket_pioneer_from_relic'); self.assertFalse(child.isVisible())
        self.assertTrue(panel.open_source()); child=panel.source_dialog
        self.assertEqual(child.panel.result['row']['category'],'relics')
        self.assertEqual(child.panel.result['row']['id'],'rogue_6_relic_assign_1')
        self.assertIn('钝爪-新典训',child.panel.player.toPlainText())
        self.assertEqual(child.panel.category.currentData(),'relics'); self.assertFalse(child.panel.scope.currentData())
        self.select(panel,'rogue_6_upgrade_ticket_pioneer'); self.assertFalse(child.isVisible())
        self.assertFalse(panel.source_button.isVisible()); self.assertFalse(panel.open_source())

    def test_linked_recruit_directory_is_separate_and_parent_owns_both_child_types(self):
        dialog=self.dialog(); panel=dialog.panel
        self.assertTrue(panel.open_recruit()); recruit=panel.recruit_dialog
        self.assertEqual(recruit.panel.entries.count(),47); self.assertIsNone(recruit.panel.ticket_id)
        self.select(panel,'rogue_6_upgrade_ticket_all'); self.assertFalse(recruit.isVisible())
        self.assertTrue(panel.open_source()); source=panel.source_dialog
        self.assertTrue(panel.open_recruit()); self.assertFalse(source.isVisible()); recruit=panel.recruit_dialog
        dialog.close(); self.qt.processEvents(); self.assertFalse(recruit.isVisible())

    def test_real_bad_source_closes_child_clears_all_old_content_then_restores_manually(self):
        panel=self.dialog().panel; self.select(panel,'rogue_6_upgrade_ticket_all'); self.assertTrue(panel.open_source()); child=panel.source_dialog
        with TemporaryDirectory() as folder:
            root=Path(folder); clone(root); path=root/model.DATA; raw=path.read_bytes()
            with patch.object(model,'ROOT',root):
                path.write_bytes(raw+b'x'); self.assertFalse(panel.refresh_reference())
                self.assertEqual(panel.entries.count(),0); self.assertIsNone(panel.result); self.assertIsNone(panel.ticket_id)
                self.assertIsNone(panel.source_identity); self.assertFalse(child.isVisible())
                self.assertEqual(panel.player.toPlainText(),''); self.assertEqual(panel.technical.toPlainText(),'')
                self.assertFalse(panel.source_button.isVisible()); self.assertFalse(panel.recruit_button.isEnabled())
                path.write_bytes(raw); self.assertTrue(panel.refresh_reference()); self.assertEqual(panel.entries.count(),18)
                self.assertIsNone(panel.ticket_id); self.assertIsNone(panel.entries.currentItem())
                self.select(panel,'rogue_6_upgrade_ticket_all'); self.assertTrue(panel.open_source())

    def test_filter_change_closes_owned_source_and_preserved_refresh_keeps_real_child(self):
        panel=self.dialog().panel; self.select(panel,'rogue_6_upgrade_ticket_all'); self.assertTrue(panel.open_source()); child=panel.source_dialog
        before=(child.panel.scene_id,child.panel.choice_id)
        self.assertTrue(panel.refresh_reference()); self.qt.processEvents(); self.assertTrue(child.isVisible())
        self.assertEqual((child.panel.scene_id,child.panel.choice_id),before)
        panel.kind.setCurrentIndex(panel.kind.findData('profession')); self.qt.processEvents()
        self.assertFalse(child.isVisible()); self.assertIsNone(panel.ticket_id)


if __name__=='__main__': unittest.main()
