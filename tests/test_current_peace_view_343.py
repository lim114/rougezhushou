from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication
from rouge import current_peace as model
from rouge.current_peace_view import CurrentPeaceDialog
from rouge.expansion_view import ExpansionUpdatePanel
from rouge.node_catalog_view import NodeCatalogPanel
from tests.test_current_peace_343 import clone

class CurrentPeaceView343Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])
    def dialog(self,*args):
        d=CurrentPeaceDialog(*args);d.show();self.qt.processEvents();self.addCleanup(d.close);return d
    def choose(self,p,key):
        p.scene.setCurrentIndex(p.scene.findData(p.result['choices'][key]['scene_id']));p.choices.setCurrentRow(next(i for i in range(p.choices.count())if p.choices.item(i).data(Qt.ItemDataRole.UserRole)==key));self.qt.processEvents()
    def test_default_no_reward_no_condition_or_resource_input(self):
        p=self.dialog().panel;self.assertIsNone(p.choice_id);self.assertTrue(p.reward_card.isHidden());self.assertTrue(p.completion_controls.isHidden());self.assertIsNone(p.completed.currentData());self.assertEqual(p.choices.count(),2);self.assertFalse(any(hasattr(p,n)for n in('offer','gold','difficulty','parts','operator','action_points')))
    def test_join_has_exact_image_and_followup_two_distinct_options(self):
        p=self.dialog('scene_ro6_task1_enter','choice_ro6_task1_1').panel;self.assertTrue(p.reward_card.isVisible());self.assertFalse(p.reward_icon.pixmap().isNull());self.assertTrue(p.completion_controls.isHidden());self.assertTrue(p.follow_scene());self.assertEqual(p.choices.count(),2);self.assertIsNone(p.choice_id)
    def test_completion_control_only_move_and_no_map_or_inverse(self):
        p=self.dialog('scene_ro6_task1_1','choice_ro6_task1_3').panel;self.assertTrue(p.completion_controls.isVisible());self.assertFalse(p.battle_button.isVisible());self.assertFalse(p.follow_scene())
        for value in(True,False,None):
            p.completed.setCurrentIndex(p.completed.findData(value));self.assertEqual(p.choice_id,'choice_ro6_task1_3');self.assertIsNone(p.result['actual_moved']);self.assertIn('未完成并不保证一定移动',p.player.toPlainText())
        self.choose(p,'choice_ro6_task1_4');self.assertTrue(p.completion_controls.isHidden());self.assertIn('【仅作标记】',p.player.toPlainText());self.assertNotIn('【仅本页条件对照】',p.player.toPlainText())
    def test_leave_clears_reward_and_move_specific_conditions(self):
        p=self.dialog('scene_ro6_task1_1','choice_ro6_task1_3').panel;p.completed.setCurrentIndex(p.completed.findData(True));self.choose(p,'choice_ro6_task1_2');self.assertTrue(p.reward_card.isHidden());self.assertTrue(p.reward_icon.pixmap().isNull());self.assertTrue(p.completion_controls.isHidden());self.assertTrue(p.follow_scene());self.assertEqual(p.choices.count(),0)
    def test_two_nonzero_readings_choice_condition_and_tab_preserved(self):
        d=self.dialog('scene_ro6_task1_1','choice_ro6_task1_3');d.resize(850,440);p=d.panel;p.completed.setCurrentIndex(p.completed.findData(False))
        for reader in(p.player,p.technical):
            p.tabs.setCurrentWidget(reader);self.qt.processEvents();c=reader.textCursor();c.setPosition(3);c.setPosition(16,QTextCursor.MoveMode.KeepAnchor);reader.setTextCursor(c);bar=reader.verticalScrollBar();self.assertGreater(bar.maximum(),0);bar.setValue(min(4,bar.maximum()));old=(c.anchor(),c.position(),bar.value(),p.scene_id,p.choice_id,p.tabs.currentIndex(),p.completed.currentData());self.assertTrue(p.refresh_reference());c=reader.textCursor();self.assertEqual(old,(c.anchor(),c.position(),bar.value(),p.scene_id,p.choice_id,p.tabs.currentIndex(),p.completed.currentData()))
    def test_bad_picture_fallback_source_loss_clear_and_manual_recovery(self):
        p=self.dialog('scene_ro6_task1_1','choice_ro6_task1_3').panel
        with TemporaryDirectory()as folder:
            root=Path(folder);clone(root)
            with patch.object(model,'ROOT',root):
                pic=root/p.result['data']['icon_reference']['file'];raw=pic.read_bytes();pic.write_bytes(raw+b'x');text=p.player.toPlainText();self.assertTrue(p.refresh_reference());self.assertEqual(p.player.toPlainText(),text);self.assertIn('图片暂缺',p.reward_icon.text());pic.write_bytes(raw)
                f=root/model.DATA;raw=f.read_bytes();f.write_bytes(raw+b' ');self.assertFalse(p.refresh_reference());self.assertTrue(p.reward_card.isHidden());self.assertTrue(p.completion_controls.isHidden());self.assertEqual(p.technical.toPlainText(),'');f.write_bytes(raw);self.assertTrue(p.refresh_reference());self.assertIsNone(p.scene_id);self.assertIsNone(p.choice_id)
    def test_all_seven_version_entries_refresh_and_owned_child_cleanup(self):
        p=ExpansionUpdatePanel();self.addCleanup(p.close);p.show();p.scope.setCurrentIndex(p.scope.findData(False));r=model.reference();old=None
        for category in('scenes','choices'):
            p.category.setCurrentIndex(p.category.findData(category))
            for key in r['data']['originals'][category]:
                p.entries.setCurrentRow(next(i for i in range(p.entries.count())if p.entries.item(i).data(Qt.ItemDataRole.UserRole)==key));self.qt.processEvents();self.assertTrue(p.open_documented_flow());d=p.flow_dialog;t=model.locate(category,key);self.assertEqual((d.panel.scene_id,d.panel.choice_id),(t['scene_id'],t['choice_id']))
                if old:self.assertFalse(old.isVisible())
                old=d
        self.assertTrue(p.refresh_reference());self.assertTrue(old.isVisible());p._unavailable();self.assertFalse(old.isVisible())
    def test_node_current_reader_default_version_notice_and_parent_close(self):
        p=NodeCatalogPanel();self.addCleanup(p.close);p.show();p.list.setCurrentRow(next(i for i,e in enumerate(p.entries)if e['key']=='event:community_group_019'));self.qt.processEvents();self.assertTrue(p.open_current_event_reference());d=p.current_reference_window;self.assertIsNone(d.panel.choice_id);self.assertIsNone(d.panel.completed.currentData());self.assertTrue(d.panel.reward_card.isHidden());self.assertIn('请核对实际游戏版本',d.node_reference_banner.text());p.refresh();self.assertTrue(d.isVisible());p.close();self.qt.processEvents();self.assertFalse(d.isVisible())

if __name__=='__main__':unittest.main()
