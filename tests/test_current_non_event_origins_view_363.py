"""Prepared363 widget cases; no native acceptance has been performed."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import json,unittest
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication
from rouge import current_non_event_origins as model
from rouge.current_non_event_origins_view import CurrentNonEventOriginsDialog
from tests.test_current_non_event_origins_363 import clone


class CurrentNonEventOriginsView363Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])

    def dialog(self,target=None):
        dialog=CurrentNonEventOriginsDialog(target);dialog.show();self.qt.processEvents();self.addCleanup(dialog.close);return dialog

    def select(self,panel,identity):
        index=next(i for i in range(panel.entries.count())if panel.entries.item(i).data(Qt.ItemDataRole.UserRole)==identity)
        panel.entries.setCurrentRow(index);self.qt.processEvents()

    def test_ten_choices_real_kind_timing_branches_and_full_player_explanations(self):
        panel=self.dialog().panel;self.assertEqual(panel.entries.count(),10);self.assertIsNone(panel.identity)
        self.assertEqual((panel.kind.count(),panel.timing.count()),(3,3));self.assertFalse(panel.source_button.isVisible())
        for row in model.reference()['rows']:
            self.select(panel,row['id']);self.assertEqual(panel.result['selected'],row)
            self.assertIn(model.version._plain(row['source_item']['usage']),panel.player.toPlainText())
            self.assertIn(model.version._plain(row['item']['usage']),panel.player.toPlainText())
            self.assertEqual(json.loads(panel.technical.toPlainText()),json.loads(json.dumps(panel.result)))
        panel.kind.setCurrentIndex(panel.kind.findData('relic'));panel.timing.setCurrentIndex(panel.timing.findData('initial'))
        self.qt.processEvents();self.assertEqual(panel.entries.count(),0);self.assertIsNone(panel.identity)

    def test_exact_reverse_source_and_reward_targets_and_nonzero_reading_survive_refresh(self):
        target=model.locate('scrap','rogue_6_scrap_G_08');dialog=self.dialog(target);dialog.resize(760,390);panel=dialog.panel
        self.assertEqual(panel.identity,target['identity']);self.assertEqual(panel.source_request,target['source_request'])
        for reader in(panel.player,panel.technical):
            panel.tabs.setCurrentWidget(reader);self.qt.processEvents();cursor=reader.textCursor()
            cursor.setPosition(4);cursor.setPosition(20,QTextCursor.MoveMode.KeepAnchor);reader.setTextCursor(cursor)
            bar=reader.verticalScrollBar();self.assertGreater(bar.maximum(),0);bar.setValue(min(5,bar.maximum()))
            before=(cursor.anchor(),cursor.position(),bar.value(),panel.tabs.currentIndex(),panel.identity,panel.source_request)
            self.assertTrue(panel.refresh_reference());self.qt.processEvents();cursor=reader.textCursor()
            self.assertEqual(before,(cursor.anchor(),cursor.position(),bar.value(),panel.tabs.currentIndex(),panel.identity,panel.source_request))
        source=model.locate('squads','rogue_6_band_5');self.assertTrue(panel.open_target(source));self.assertEqual(panel.source_request,source['source_request'])
        self.assertFalse(panel.open_target({'identity':'wrong','source_request':source['source_request']}))

    def test_both_real_originals_are_exact_and_recruit_voucher_link_selects_actual354_row(self):
        panel=self.dialog(model.locate('squads','rogue_6_band_27')).panel
        self.assertTrue(panel.open_original('source'));source=panel.original_dialog
        self.assertEqual(source.panel.category.currentData(),'squads');self.assertEqual(source.panel.result['row']['id'],'rogue_6_band_27')
        self.assertTrue(panel.open_original('item'));self.assertFalse(source.isVisible());item=panel.original_dialog
        self.assertEqual(item.panel.category.currentData(),'scrap');self.assertEqual(item.panel.result['row']['id'],'rogue_6_scrap_G_08')
        row=next(r for r in model.reference(kind='relic')['rows']if r['source_id']=='rogue_6_relic_legacy_133')
        self.select(panel,row['id']);self.assertFalse(item.isVisible());self.assertTrue(panel.open_original('item'));child=panel.original_dialog
        self.assertEqual(child.panel.ticket_id,'rogue_6_recruit_ticket_temp_6_up')
        self.assertEqual(child.panel.entries.count(),47);self.assertEqual(child.panel.result['selected']['stars'],[6])
        self.assertIsNone(child.panel.result['actual_recruited'])

    def test_bad_source_clears_both_readers_and_target_closes_child_then_recovers_for_manual_choice(self):
        panel=self.dialog(model.locate('squads','rogue_6_band_27')).panel
        self.assertTrue(panel.open_original('source'));child=panel.original_dialog
        with TemporaryDirectory()as folder:
            root=Path(folder);clone(root);path=root/model.DATA;raw=path.read_bytes()
            with patch.object(model,'ROOT',root):
                path.write_bytes(raw+b'x');self.assertFalse(panel.refresh_reference())
                self.assertIsNone(panel.identity);self.assertIsNone(panel.source_request);self.assertIsNone(panel.result)
                self.assertEqual(panel.entries.count(),0);self.assertFalse(child.isVisible())
                self.assertEqual(panel.player.toPlainText(),'');self.assertEqual(panel.technical.toPlainText(),'')
                self.assertFalse(panel.source_button.isVisible());self.assertFalse(panel.item_button.isVisible())
                path.write_bytes(raw);self.assertTrue(panel.refresh_reference());self.assertEqual(panel.entries.count(),10)
                self.assertIsNone(panel.identity);self.assertIsNone(panel.entries.currentItem());self.assertIsNone(panel.source_request)
                self.select(panel,model.reference()['rows'][0]['id']);self.assertTrue(panel.open_original('source'))

    def test_filter_change_and_parent_close_clear_owned_children_preserved_refresh_keeps_exact_original(self):
        dialog=self.dialog(model.locate('squads','rogue_6_band_27'));panel=dialog.panel
        self.assertTrue(panel.open_original('source'));child=panel.original_dialog
        self.assertTrue(panel.refresh_reference());self.qt.processEvents();self.assertTrue(child.isVisible())
        self.assertEqual(child.panel.result['row']['id'],'rogue_6_band_27')
        panel.search.setText('银印');self.qt.processEvents();self.assertFalse(child.isVisible())
        self.assertIsNone(panel.identity);self.assertIsNone(panel.source_request)
        self.select(panel,model.reference(query='银印')['rows'][0]['id']);self.assertTrue(panel.open_original('item'));child=panel.original_dialog
        dialog.close();self.qt.processEvents();self.assertFalse(child.isVisible())


if __name__=='__main__':unittest.main()
