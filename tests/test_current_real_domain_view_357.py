"""Candidate357 view tests; preparation is not claimed native validation."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import json,unittest
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication
from rouge import current_real_domain as model
from rouge.current_real_domain_view import CurrentRealDomainDialog
from tests.test_current_real_domain_357 import clone


class CurrentRealDomainView357Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])
    def dialog(self,target=None):
        dialog=CurrentRealDomainDialog(target);dialog.show();self.qt.processEvents();self.addCleanup(dialog.close);return dialog
    def select(self,panel,key):
        panel.entries.setCurrentRow(next(i for i in range(panel.entries.count())if panel.entries.item(i).data(Qt.ItemDataRole.UserRole)==key));self.qt.processEvents()

    def test_all34_exact_rows_manual_selection_and_real_kind_type_branches(self):
        panel=self.dialog().panel;self.assertEqual(panel.entries.count(),34);self.assertIsNone(panel.row_id);self.assertTrue(panel.conditions.isHidden())
        for row in model.reference()['rows']:
            self.select(panel,row['id']);self.assertEqual(panel.result['selected'],row)
            self.assertIn(row['original']['functionDesc'],panel.player.toPlainText())
            self.assertEqual(json.loads(panel.technical.toPlainText()),json.loads(json.dumps({'reference':panel.result,'opening_source':panel.source_request})))
        panel.kind.setCurrentIndex(panel.kind.findData('policy'));self.qt.processEvents();self.assertEqual(panel.entries.count(),4);self.assertEqual(panel.type_filter.count(),5);self.assertIsNone(panel.row_id)
        panel.kind.setCurrentIndex(panel.kind.findData('idea'));panel.type_filter.setCurrentIndex(panel.type_filter.findData('rogue_6_weather_5'))
        self.assertEqual(panel.entries.count(),3);self.assertIsNone(panel.row_id)

    def test_only_relevant_special_condition_controls_and_origins_visible(self):
        panel=self.dialog().panel
        self.select(panel,'rogue_6_weather_1_a');self.assertTrue(panel.floor.isVisible());self.assertFalse(panel.squad.isVisible());self.assertFalse(panel.paired.isVisible());self.assertFalse(panel.origin_row.isVisible())
        self.select(panel,'rogue_6_weather_8_a');self.assertFalse(panel.floor.isVisible());self.assertFalse(panel.squad.isVisible());self.assertTrue(panel.paired.isVisible());self.assertEqual(panel.origins.count(),3);self.assertFalse(panel.open_button.isEnabled())
        self.select(panel,model.GAIN);self.assertTrue(panel.squad.isVisible());self.assertTrue(panel.paired.isVisible());self.assertFalse(panel.floor.isVisible());self.assertEqual(panel.paired.count(),11)
        self.select(panel,'rogue_6_weather_10_a');self.assertFalse(panel.squad.isVisible());self.assertFalse(panel.paired.isVisible());self.assertEqual(panel.origins.count(),2)

    def test_two_actual_nonzero_readings_manual_fields_selection_and_tab_preserved(self):
        dialog=self.dialog();dialog.resize(760,450);panel=dialog.panel
        panel.search.setText('希望的沃土');self.select(panel,'rogue_6_weather_8_c');panel.mode.setCurrentIndex(panel.mode.findData('NORMAL'));panel.difficulty.setValue(12);panel.paired.setCurrentIndex(panel.paired.findData(model.GAIN))
        for reader in(panel.player,panel.technical):
            panel.tabs.setCurrentWidget(reader);self.qt.processEvents();cursor=reader.textCursor();cursor.setPosition(3);cursor.setPosition(17,QTextCursor.MoveMode.KeepAnchor);reader.setTextCursor(cursor)
            bar=reader.verticalScrollBar();self.assertGreater(bar.maximum(),0);bar.setValue(min(4,bar.maximum()));old=(cursor.anchor(),cursor.position(),bar.value(),panel.tabs.currentIndex(),panel.row_id,panel.search.text(),panel.difficulty.value(),panel.paired.currentData())
            self.assertTrue(panel.refresh_reference());self.qt.processEvents();cursor=reader.textCursor()
            self.assertEqual(old,(cursor.anchor(),cursor.position(),bar.value(),panel.tabs.currentIndex(),panel.row_id,panel.search.text(),panel.difficulty.value(),panel.paired.currentData()))

    def test_exact_source_target_filters_three_phases_without_auto_phase_or_values(self):
        target=model.locate('choices','choice_ro6_normal3_1');panel=self.dialog(target).panel
        self.assertEqual(panel.entries.count(),3);self.assertIsNone(panel.row_id);self.assertEqual(panel.type_filter.currentData(),model.HOPE)
        self.assertEqual(panel.source_request,target);self.assertIn('具体档位',panel.source_banner.text())
        self.assertEqual(panel.difficulty.value(),-1);self.assertIsNone(panel.mode.currentData())
        self.assertIsNone(panel.result['actual_weather']);self.assertFalse(panel.result['run_updated'])

    def test_real_related_event_choices_and_unknown_actual_conditions(self):
        panel=self.dialog().panel;self.select(panel,'rogue_6_weather_8_a')
        for key in('red_controller','red_seed'):
            panel.origins.setCurrentIndex(panel.origins.findData(key));self.assertTrue(panel.open_origin());child=panel.event_dialog;target=model.destination(key)['target']
            self.assertEqual((child.panel.event_id,child.panel.scene_id,child.panel.choice_id),(target['event_id'],target['scene_id'],target['choice_id']))
            self.assertEqual(child.panel.seeds.value(),-1);self.assertIsNone(child.panel.controller.currentData());self.assertIsNone(child.panel.result['actual_eligible'])
        old=panel.event_dialog;self.select(panel,'rogue_6_weather_10_a');self.assertFalse(old.isVisible());panel.origins.setCurrentIndex(panel.origins.findData('resting'))
        self.assertTrue(panel.open_origin());self.assertEqual(panel.event_dialog.panel.source_request,{'category':'scenes','key':'scene_ro6_surprise_enter'})
        self.assertIsNone(panel.event_dialog.panel.choice_id)

    def test_source_loss_closes_owned_event_clears_readers_then_manual_recovery(self):
        panel=self.dialog().panel;self.select(panel,'rogue_6_weather_8_a');panel.origins.setCurrentIndex(panel.origins.findData('red_seed'));self.assertTrue(panel.open_origin());child=panel.event_dialog
        with TemporaryDirectory()as folder:
            root=Path(folder);clone(root);path=root/model.DATA;raw=path.read_bytes()
            with patch.object(model,'ROOT',root):
                path.write_bytes(raw+b'x');self.assertFalse(panel.refresh_reference());self.assertIsNone(panel.result);self.assertIsNone(panel.row_id)
                self.assertEqual(panel.entries.count(),0);self.assertEqual(panel.player.toPlainText(),'');self.assertEqual(panel.technical.toPlainText(),'');self.assertFalse(child.isVisible())
                path.write_bytes(raw);self.assertTrue(panel.refresh_reference());self.assertEqual(panel.entries.count(),34);self.assertIsNone(panel.row_id)
                self.assertIsNone(panel.entries.currentItem());self.assertTrue(panel.conditions.isHidden())

    def test_same_source_parent_refresh_preserves_child_and_actual_parent_close(self):
        dialog=self.dialog();panel=dialog.panel;self.select(panel,'rogue_6_weather_8_a');panel.origins.setCurrentIndex(panel.origins.findData('red_controller'));panel.open_origin();child=panel.event_dialog
        child.panel.controller.setCurrentIndex(child.panel.controller.findData(True));self.assertTrue(panel.refresh_reference());self.qt.processEvents()
        self.assertIs(panel.event_dialog,child);self.assertTrue(child.isVisible());self.assertTrue(child.panel.controller.currentData())
        dialog.close();self.qt.processEvents();self.assertFalse(child.isVisible())


if __name__=='__main__':unittest.main()
