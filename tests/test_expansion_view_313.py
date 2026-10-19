"""Update-reader selection, real image loading and refresh behavior."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import json,shutil,unittest
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication
from rouge import expansion_reference as model
from rouge.expansion_view import ExpansionUpdatePanel
ROOT=Path(__file__).resolve().parents[1]

class ExpansionView313Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.app=QApplication.instance()or QApplication([])
    def panel(self):
        p=ExpansionUpdatePanel();p.resize(1040,620);p.show();self.addCleanup(p.close);self.app.processEvents();return p
    def select(self,p,cat,key,all_rows=False):
        p.category.setCurrentIndex(p.category.findData(cat));p.scope.setCurrentIndex(p.scope.findData(not all_rows))
        i=next(i for i in range(p.entries.count())if p.entries.item(i).data(Qt.ItemDataRole.UserRole)==key)
        p.entries.setCurrentRow(i);self.app.processEvents();return p.result
    def test_initial_manual_choice_and_complete184_stage_catalog(self):
        p=self.panel();self.assertIsNone(p.result);self.assertEqual(p.entries.count(),80)
        p.scope.setCurrentIndex(p.scope.findData(False));self.assertEqual(p.entries.count(),184)
        self.assertIsNone(p.result);self.assertIn('同名变体',p.count.text())
    def test_every_changed_stage_keeps_its_exact_source_and_loads_a_real_image(self):
        p=self.panel()
        for row in model.rows('stages'):
            result=self.select(p,'stages',row['id'])
            self.assertEqual(result,model.detail('stages',row['id']));self.assertIsNotNone(p.image_raw)
            self.assertIsNotNone(p.map_image.pixmap());self.assertFalse(p.map_image.pixmap().isNull())
            self.assertIn('尚未校准',p.player.toPlainText());self.assertFalse(p.next_button.isVisible())
            self.assertEqual(json.loads(p.technical.toPlainText()),result)
    def test_all_categories_default_changes_and_search_dont_choose_an_entry(self):
        p=self.panel()
        for key,_ in model.CATEGORIES:
            p.category.setCurrentIndex(p.category.findData(key));self.app.processEvents()
            self.assertEqual(p.entries.count(),len(model.rows(key)));self.assertIsNone(p.result)
        p.category.setCurrentIndex(p.category.findData('choices'));p.search.setText('帮助倒下')
        self.assertEqual(p.entries.count(),1);self.assertIsNone(p.result)
    def test_only_explicit_next_scene_follows_and_no_parent_scene_is_inferred(self):
        p=self.panel();self.select(p,'choices','choice_ro6_final1_8');self.assertTrue(p.next_button.isEnabled());self.assertTrue(p.follow_scene())
        self.assertEqual(p.category.currentData(),'scenes');self.assertIs(p.scope.currentData(),False)
        self.assertEqual(p.result['row']['id'],'scene_ro6_final1_4');self.assertIn('不是本场景内的选项',p.player.toPlainText())
        self.select(p,'choices','choice_ro6_end4_3');self.assertFalse(p.next_button.isVisible());self.assertFalse(p.follow_scene())
    def test_same_source_refresh_preserves_real_nonzero_reader_search_filter_and_selection(self):
        p=self.panel();p.category.setCurrentIndex(p.category.findData('choices'));p.search.setText('帮助倒下');self.select(p,'choices','choice_ro6_final1_8')
        p.resize(900,400);self.app.processEvents()
        for reader in(p.player,p.technical):
            p.tabs.setCurrentWidget(reader);self.app.processEvents();cursor=reader.textCursor();cursor.setPosition(2);cursor.setPosition(10,QTextCursor.MoveMode.KeepAnchor);reader.setTextCursor(cursor)
            bar=reader.verticalScrollBar();self.assertGreater(bar.maximum(),0);bar.setValue(min(8,bar.maximum()))
            before=(cursor.anchor(),cursor.position(),cursor.selectedText(),bar.value(),p.tabs.currentIndex(),p.search.text(),p.scope.currentData(),p.result['row']['id'])
            self.assertTrue(p.refresh_reference());self.app.processEvents();cursor=reader.textCursor()
            after=(cursor.anchor(),cursor.position(),cursor.selectedText(),bar.value(),p.tabs.currentIndex(),p.search.text(),p.scope.currentData(),p.result['row']['id'])
            self.assertEqual(before,after)
    def test_real_source_loss_clears_text_picture_link_and_selection_recovery_is_manual(self):
        p=self.panel();self.select(p,'choices','choice_ro6_final1_8')
        manifest=json.loads((ROOT/model.MANIFEST).read_bytes())
        with TemporaryDirectory()as folder:
            root=Path(folder)
            for name in(model.MANIFEST,*manifest['files']):
                target=root/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,target)
            source=root/model.PACK/'current-topic.json';raw=source.read_bytes()
            with patch.object(model,'ROOT',root):
                source.write_bytes(raw+b' ');self.assertFalse(p.refresh_reference());self.assertIsNone(p.result)
                self.assertEqual(p.entries.count(),0);self.assertEqual(p.player.toPlainText(),'');self.assertEqual(p.technical.toPlainText(),'');self.assertFalse(p.next_button.isEnabled());self.assertIsNone(p.image_raw)
                source.write_bytes(raw);self.assertTrue(p.refresh_reference());self.assertIsNone(p.result);self.assertEqual(p.entries.currentRow(),-1)
    def test_bad_image_cannot_keep_old_map_and_other_categories_clear_map(self):
        p=self.panel();self.select(p,'stages','ro6_b_7');self.assertIsNotNone(p.image_raw)
        with patch.object(model,'image_bytes',return_value=None):
            p.refresh_reference();self.assertIsNone(p.image_raw)
            pixmap=p.map_image.pixmap();self.assertTrue(pixmap is None or pixmap.isNull())
        self.select(p,'choices','choice_ro6_final1_8');self.assertIsNone(p.image_raw)
        pixmap=p.map_image.pixmap();self.assertTrue(pixmap is None or pixmap.isNull())
    def test_resize_only_rescales_same_original_without_markers_or_image_substitution(self):
        p=self.panel();self.select(p,'stages','ro6_n_7_1');raw=p.image_raw
        for w,h in((820,500),(1300,860)):
            p.resize(w,h);self.app.processEvents();self.assertEqual(p.image_raw,raw);self.assertIsNotNone(p.map_image.pixmap())

if __name__=='__main__':unittest.main()
