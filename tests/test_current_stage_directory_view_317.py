from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import json,shutil,unittest
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication
from rouge import current_stage_directory as model
from rouge.expansion_view import ExpansionUpdatePanel
ROOT=Path(__file__).resolve().parents[1]

class CurrentStageDirectoryView317Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])
    def panel(self):
        p=ExpansionUpdatePanel();p.resize(1040,620);p.show();self.addCleanup(p.close);p.scope.setCurrentIndex(p.scope.findData(False));self.qt.processEvents();return p
    def select(self,p,sid):
        i=next(i for i in range(p.entries.count())if p.entries.item(i).data(Qt.ItemDataRole.UserRole)==sid);p.entries.setCurrentRow(i);self.qt.processEvents()
    def test_layer_and_kind_are_real_independent_branches(self):
        p=self.panel();self.assertEqual(p.entries.count(),184);self.assertIsNone(p.result)
        p.stage_floor.setCurrentIndex(p.stage_floor.findData('floor6'));self.assertEqual(p.entries.count(),11);p.stage_kind.setCurrentIndex(p.stage_kind.findData('boss'));self.assertEqual(p.entries.count(),3);self.assertIsNone(p.result)
        p.stage_kind.setCurrentIndex(p.stage_kind.findData('normal'));self.assertEqual(p.entries.count(),4)
    def test_unknown_layer_keeps_graypit_and_does_not_claim_all_floors(self):
        p=self.panel();p.stage_floor.setCurrentIndex(p.stage_floor.findData('unknown'));self.assertEqual(p.entries.count(),22);self.select(p,'ro6_s_1');self.assertIn('层数未确认',p.player.toPlainText());self.assertIn('不能',p.player.toPlainText());self.assertTrue(p.open_current_battle());self.assertEqual(p.current_battle_dialog.panel.stage_id,'ro6_s_1');p.current_battle_dialog.close()
    def test_exact_classification_source_is_separate_from_original_technical_contract(self):
        p=self.panel();self.select(p,'ro6_b_7_b');self.assertEqual(json.loads(p.technical.toPlainText()),p.result);self.assertEqual(json.loads(p.stage_source.toPlainText()),p.stage_info);self.assertEqual(p.stage_info['row']['region'],'盲目者所见');self.assertIn('第6层',p.player.toPlainText());self.assertNotIn('未恢复新关卡出怪',p.player.toPlainText());self.assertIn('已接入的敌人',p.player.toPlainText())
    def test_scope_search_and_filters_intersect_without_renumbering(self):
        p=self.panel();p.stage_floor.setCurrentIndex(p.stage_floor.findData('floor6'));p.stage_kind.setCurrentIndex(p.stage_kind.findData('boss'));p.search.setText('熄日');self.assertEqual(p.entries.count(),2);labels=[p.entries.item(i).text()for i in range(2)];p.scope.setCurrentIndex(p.scope.findData(True));self.assertEqual([p.entries.item(i).text()for i in range(2)],labels)
        self.select(p,'ro6_b_7');self.assertIn('资料1',p.entries.currentItem().text());p.search.clear();self.assertIsNone(p.result)
    def test_all_three_readers_preserve_nonzero_selection_scroll_filters_and_tab(self):
        p=self.panel();p.resize(900,450);p.stage_floor.setCurrentIndex(p.stage_floor.findData('floor6'));p.stage_kind.setCurrentIndex(p.stage_kind.findData('boss'));self.select(p,'ro6_b_7_b')
        for reader in(p.player,p.technical,p.stage_source):
            p.tabs.setCurrentWidget(reader);self.qt.processEvents();c=reader.textCursor();c.setPosition(2);c.setPosition(12,QTextCursor.MoveMode.KeepAnchor);reader.setTextCursor(c);bar=reader.verticalScrollBar();self.assertGreater(bar.maximum(),0);bar.setValue(min(5,bar.maximum()));before=(c.anchor(),c.position(),bar.value(),p.tabs.currentIndex(),p.stage_floor.currentData(),p.stage_kind.currentData(),p.result['row']['id']);self.assertTrue(p.refresh_reference());self.qt.processEvents();c=reader.textCursor();self.assertEqual(before,(c.anchor(),c.position(),bar.value(),p.tabs.currentIndex(),p.stage_floor.currentData(),p.stage_kind.currentData(),p.result['row']['id']))
    def test_other_categories_hide_filters_keep_prior_choice_on_return_without_auto_selection(self):
        p=self.panel();p.stage_floor.setCurrentIndex(p.stage_floor.findData('floor6'));p.category.setCurrentIndex(p.category.findData('choices'));self.qt.processEvents();self.assertFalse(p.stage_filters.isVisible());self.assertFalse(p.tabs.isTabVisible(2));p.category.setCurrentIndex(p.category.findData('stages'));self.assertEqual(p.stage_floor.currentData(),'floor6');self.assertEqual(p.entries.count(),11);self.assertIsNone(p.result)
    def test_actual_classification_source_loss_closes_old_preview_and_manual_recovery(self):
        p=self.panel();self.select(p,'ro6_s_1');self.assertTrue(p.open_current_battle());dialog=p.current_battle_dialog;manifest=json.loads((ROOT/model.MANIFEST).read_bytes())
        with TemporaryDirectory()as folder:
            root=Path(folder)
            for name in(model.MANIFEST,*manifest['files']):
                target=root/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,target)
            with patch.object(model,'ROOT',root):
                file=root/model.DATA;raw=file.read_bytes();file.write_bytes(raw+b' ');self.assertFalse(p.refresh_reference());self.assertFalse(dialog.isVisible());self.assertIsNone(p.result);self.assertEqual(p.stage_source.toPlainText(),'');self.assertFalse(p.battle_button.isEnabled());file.write_bytes(raw);self.assertTrue(p.refresh_reference());self.assertIsNone(p.result);self.assertEqual(p.entries.currentRow(),-1)

if __name__=='__main__':unittest.main()
