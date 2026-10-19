from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import json,shutil,unittest
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication
from rouge import current_battle_reference as model
from rouge.current_battle_view import CurrentBattlePanel
ROOT=Path(__file__).resolve().parents[1]

class CurrentBattleView314Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.app=QApplication.instance()or QApplication([])
    def panel(self,sid='ro6_b_7'):
        p=CurrentBattlePanel(sid);p.resize(1000,620);p.show();self.addCleanup(p.close);self.app.processEvents();return p
    def test_native_widget_actual_map_and_separate_category_branches(self):
        p=self.panel();self.assertEqual(p.result['id'],'ro6_b_7');self.assertFalse(p.map_image.pixmap().isNull())
        self.assertEqual(p.enemy_combo.currentData(),None);self.assertIsNone(p.actions.currentItem())
        expected={model.TIERS.get(e['tier'],'类别未确认')for e in p.result['enemies']}
        self.assertEqual({p.enemy_choices.branch.itemText(i)for i in range(1,p.enemy_choices.branch.count())},expected)
        self.assertEqual(p.queue_kind.count(),3);self.assertEqual(json.loads(p.technical.toPlainText()),p.result)
    def test_each_enemy_exact_identity_picture_or_visible_missing_state_and_no_white_values(self):
        p=self.panel('ro6_n_2_6')
        for e in p.result['enemies']:
            self.assertTrue(p.enemy_choices.select_value(e['key']));self.app.processEvents();self.assertIn(e['name'],p.enemy_player.toPlainText());self.assertIn('不以白值替代',p.enemy_player.toPlainText())
            pix=p.enemy_portrait.pixmap()
            if model.picture_bytes(e['portrait'])is None:self.assertTrue(pix is None or pix.isNull());self.assertIn('未取得图片',p.enemy_portrait.text())
            else:self.assertFalse(pix.isNull())
    def test_main_vs_branch_filter_is_real_separate_choice_without_autoselection(self):
        p=self.panel()
        for kind in('main','branch'):
            p.queue_kind.setCurrentIndex(p.queue_kind.findData(kind));self.app.processEvents();rows=[a for a in p.result['actions']if a['queue']['kind']==kind]
            self.assertEqual(p.actions.count(),len(rows));self.assertIsNone(p.actions.currentItem())
            if rows:p.actions.setCurrentRow(0);self.assertIn('准确时刻：未知',p.action_player.toPlainText())
    def test_refresh_preserves_selected_enemy_action_filter_tab_real_scroll_and_selection(self):
        p=self.panel();p.resize(900,440);self.app.processEvents();p.enemy_choices.select_value(p.result['enemies'][0]['key'])
        p.queue_kind.setCurrentIndex(p.queue_kind.findData('branch'));p.actions.setCurrentRow(0);self.app.processEvents()
        for widget in(p.summary,p.enemy_player,p.action_player,p.technical):
            p.tabs.setCurrentIndex(0 if widget is p.summary else 1 if widget is p.enemy_player else 2 if widget is p.action_player else 3);self.app.processEvents()
            if widget is p.action_player:widget.parentWidget().setSizes([680,160]);self.app.processEvents()
            c=widget.textCursor();c.setPosition(1);c.setPosition(10,QTextCursor.MoveMode.KeepAnchor);widget.setTextCursor(c);bar=widget.verticalScrollBar()
            self.assertGreater(bar.maximum(),0);bar.setValue(min(5,bar.maximum()));prior=(c.anchor(),c.position(),bar.value(),p.tabs.currentIndex(),p.enemy_combo.currentData(),p.action_key,p.queue_kind.currentData())
            self.assertTrue(p.refresh_reference());self.app.processEvents();c=widget.textCursor()
            self.assertEqual(prior,(c.anchor(),c.position(),bar.value(),p.tabs.currentIndex(),p.enemy_combo.currentData(),p.action_key,p.queue_kind.currentData()))
    def test_real_source_corruption_clears_all_stale_readers_images_and_choices(self):
        p=self.panel();p.enemy_choices.select_value(p.result['enemies'][0]['key']);p.actions.setCurrentRow(0)
        manifest=json.loads((ROOT/model.MANIFEST).read_bytes())
        with TemporaryDirectory()as folder:
            temp=Path(folder)
            for n in(model.MANIFEST,*manifest['files']):
                dest=temp/n;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/n,dest)
            source=temp/model.PACK/'source-inputs.json';raw=source.read_bytes()
            with patch.object(model,'ROOT',temp):
                source.write_bytes(raw+b' ');self.assertFalse(p.refresh_reference());self.assertIsNone(p.result);self.assertEqual(p.actions.count(),0)
                for w in(p.summary,p.enemy_player,p.action_player,p.technical):self.assertEqual(w.toPlainText(),'')
                pix=p.map_image.pixmap();self.assertTrue(pix is None or pix.isNull())
                source.write_bytes(raw);self.assertTrue(p.refresh_reference());self.assertIsNone(p.enemy_combo.currentData());self.assertIsNone(p.actions.currentItem());self.assertIsNone(p.enemy_key);self.assertIsNone(p.action_key)
    def test_bad_or_missing_images_clear_previous_map_and_portrait(self):
        p=self.panel();p.enemy_choices.select_value(p.result['enemies'][0]['key'])
        with patch('rouge.expansion_reference.image_bytes',return_value=None),patch.object(model,'picture_bytes',return_value=None):
            self.assertTrue(p.refresh_reference());pix=p.map_image.pixmap();self.assertTrue(pix is None or pix.isNull());pix=p.enemy_portrait.pixmap();self.assertTrue(pix is None or pix.isNull())

if __name__=='__main__':unittest.main()
