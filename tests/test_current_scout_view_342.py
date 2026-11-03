from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication
from rouge import current_scout as model
from rouge.current_scout_view import CurrentScoutDialog
from rouge.expansion_view import ExpansionUpdatePanel
from rouge.node_catalog_view import NodeCatalogPanel
from tests.test_current_scout_342 import clone

class CurrentScoutView342Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])
    def dialog(self,*args):
        d=CurrentScoutDialog(*args);d.show();self.qt.processEvents();self.addCleanup(d.close);return d
    def choose(self,p,key):
        p.scene.setCurrentIndex(p.scene.findData(p.result['choices'][key]['scene_id']));p.choices.setCurrentRow(next(i for i in range(p.choices.count())if p.choices.item(i).data(Qt.ItemDataRole.UserRole)==key));self.qt.processEvents()
    def test_default_no_item_or_irrelevant_inputs(self):
        p=self.dialog().panel;self.assertIsNone(p.choice_id);self.assertTrue(p.return_card.isHidden());self.assertEqual(p.choices.count(),3)
        self.assertFalse(any(hasattr(p,n)for n in('offer','gold','difficulty','parts','operator','action_points')))
    def test_source_confirmation_image_and_no_fifth_explanatory_button(self):
        p=self.dialog('scene_ro6_scout_enter','choice_ro6_scout_3').panel;self.assertTrue(p.return_card.isVisible());self.assertFalse(p.return_icon.pixmap().isNull());self.assertTrue(p.follow_scene());self.assertEqual(p.choices.count(),1);self.choose(p,'choice_ro6_scout_4');self.assertTrue(p.return_card.isVisible());self.assertFalse(p.follow_scene());self.assertFalse(p.battle_button.isVisible());self.assertIn('不作为另一个可点击',p.player.toPlainText())
    def test_inside_and_rest_hide_source_item_and_never_borrow_return_rewards(self):
        p=self.dialog('scene_ro6_scout_enter','choice_ro6_scout_3').panel
        for key in('choice_ro6_scout_1','choice_ro6_scout_2'):
            self.choose(p,key);self.assertTrue(p.return_card.isHidden());self.assertTrue(p.return_icon.pixmap().isNull());self.assertTrue(p.follow_scene());self.assertEqual(p.choices.count(),0);self.assertFalse(p.follow_scene())
    def test_two_nonzero_reading_states_keep_choice_and_tab_on_refresh(self):
        d=self.dialog('scene_ro6_scout_enter','choice_ro6_scout_3');d.resize(850,440);p=d.panel
        for reader in(p.player,p.technical):
            p.tabs.setCurrentWidget(reader);self.qt.processEvents();c=reader.textCursor();c.setPosition(3);c.setPosition(16,QTextCursor.MoveMode.KeepAnchor);reader.setTextCursor(c);bar=reader.verticalScrollBar();self.assertGreater(bar.maximum(),0);bar.setValue(min(4,bar.maximum()));old=(c.anchor(),c.position(),bar.value(),p.scene_id,p.choice_id,p.tabs.currentIndex());self.assertTrue(p.refresh_reference());c=reader.textCursor();self.assertEqual(old,(c.anchor(),c.position(),bar.value(),p.scene_id,p.choice_id,p.tabs.currentIndex()))
    def test_bad_image_only_fallback_source_failure_clears_and_manual_recovery(self):
        p=self.dialog('scene_ro6_scout_enter','choice_ro6_scout_3').panel
        with TemporaryDirectory()as folder:
            root=Path(folder);clone(root)
            with patch.object(model,'ROOT',root):
                pic=root/p.result['data']['icon_reference']['file'];raw=pic.read_bytes();pic.write_bytes(raw+b'x');text=p.player.toPlainText();self.assertTrue(p.refresh_reference());self.assertEqual(p.player.toPlainText(),text);self.assertIn('图片暂缺',p.return_icon.text());pic.write_bytes(raw)
                f=root/model.DATA;raw=f.read_bytes();f.write_bytes(raw+b' ');self.assertFalse(p.refresh_reference());self.assertIsNone(p.result);self.assertTrue(p.return_card.isHidden());self.assertEqual(p.technical.toPlainText(),'');f.write_bytes(raw);self.assertTrue(p.refresh_reference());self.assertIsNone(p.scene_id);self.assertIsNone(p.choice_id)
    def test_version_parent_all_eight_entries_and_refresh_ownership(self):
        p=ExpansionUpdatePanel();self.addCleanup(p.close);p.show();p.scope.setCurrentIndex(p.scope.findData(False));r=model.reference();old=None
        for category in('scenes','choices'):
            p.category.setCurrentIndex(p.category.findData(category))
            for key in r['data']['originals'][category]:
                p.entries.setCurrentRow(next(i for i in range(p.entries.count())if p.entries.item(i).data(Qt.ItemDataRole.UserRole)==key));self.qt.processEvents();self.assertTrue(p.open_documented_flow());d=p.flow_dialog;target=model.locate(category,key);self.assertEqual((d.panel.scene_id,d.panel.choice_id),(target['scene_id'],target['choice_id']))
                if old:self.assertFalse(old.isVisible())
                old=d
        self.assertTrue(p.refresh_reference());self.assertTrue(old.isVisible());p._unavailable();self.assertFalse(old.isVisible())
    def test_catalogue_current_reader_defaults_and_parent_close(self):
        p=NodeCatalogPanel();self.addCleanup(p.close);p.show();p.list.setCurrentRow(next(i for i,e in enumerate(p.entries)if e['key']=='event:community_group_024'));self.qt.processEvents();self.assertTrue(p.open_current_event_reference());d=p.current_reference_window;self.assertIsNone(d.panel.choice_id);self.assertTrue(d.panel.return_card.isHidden());self.assertIn('请核对实际游戏版本',d.node_reference_banner.text());p.refresh();self.assertTrue(d.isVisible());p.close();self.qt.processEvents();self.assertFalse(d.isVisible())

if __name__=='__main__':unittest.main()
