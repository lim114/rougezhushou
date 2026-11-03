from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication
from rouge import current_resting as model
from rouge.current_resting_view import CurrentRestingDialog
from rouge.expansion_view import ExpansionUpdatePanel
from rouge.node_catalog_view import NodeCatalogPanel
from tests.test_current_resting_345 import clone,PATHS,path_keys

class CurrentRestingView345Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])
    def dialog(self,target=None):
        d=CurrentRestingDialog(target);d.show();self.qt.processEvents();self.addCleanup(d.close);return d
    def choose(self,p,cid):
        p.scene.setCurrentIndex(p.scene.findData(p.result['choices'][cid]['scene_id']));p.choices.setCurrentRow(next(i for i in range(p.choices.count())if p.choices.item(i).data(Qt.ItemDataRole.UserRole)==cid));self.qt.processEvents()
    def test_default_no_reward_popup_or_unrelated_resource_controls(self):
        p=self.dialog().panel;self.assertIsNone(p.choice_id);self.assertEqual(p.choices.count(),1);self.assertTrue(p.reward_card.isHidden());self.assertTrue(p.original_button.isHidden());self.assertFalse(any(hasattr(p,k)for k in('naturals','gold','offer','difficulty','operator','action_points')))
    def test_seven_document_paths_and_legacy_scope_stop_without_added_menu(self):
        p=self.dialog().panel
        for (first,last),end in PATHS:
            p.go_start()
            for key in path_keys(first,last):self.choose(p,key);self.assertTrue(p.follow_scene())
            self.assertEqual(p.scene_id,end);self.assertEqual(p.choices.count(),0);self.assertFalse(p.follow_scene());self.assertTrue(p.original_button.isHidden())
    def test_result_cards_not_buttons_and_old_extra_candidate_clearly_unproven(self):
        p=self.dialog().panel;p.scene.setCurrentIndex(p.scene.findData('outcomes:squirrel'));self.assertEqual(p.choices.count(),3);self.assertIn('来源分组不同',p.player.toPlainText());self.choose(p,'result:legacy-squirrel-mud');self.assertIn('当前归属未证',p.player.toPlainText());self.assertIn('不是新增游戏按钮',p.player.toPlainText());self.assertTrue(p.follow_scene());self.assertIn('只保留完整文字供核对',p.player.toPlainText())
    def test_99_comparison_leaf_follows_exact_bed_and_prevents_recursive_popup(self):
        p=self.dialog().panel;self.choose(p,'reward:gold99');self.assertTrue(p.original_button.isVisible());self.assertIn('与原项不同',p.next_button.text());self.assertTrue(p.open_original());child=p.original_dialog;self.assertEqual(child.panel.result['requested_original']['id'],'choice_ro6_surprise_12');self.assertTrue(child.panel.original_button.isHidden());self.assertFalse(child.panel.open_original());self.assertIn('病床后续',child.panel.next_button.text());self.assertTrue(child.panel.follow_scene());self.assertEqual(child.panel.result['scenes'][child.panel.scene_id]['source_scene_ids'],['scene_ro6_surprise_1']);self.assertEqual(child.panel.choices.count(),0)
    def test_popup_only_two_conflicting_document_choices_not_resource_or_named_item(self):
        p=self.dialog().panel
        for c in p.result['choices'].values():
            self.choose(p,c['id']);self.assertIs(p.original_button.isVisible(),c['explicit_next_conflict'])
        self.choose(p,'option:enter');self.assertTrue(p.reward_card.isVisible());self.assertFalse(p.reward_icon.pixmap().isNull());self.assertIn('不能相加成198',p.player.toPlainText());self.choose(p,'reward:gold99');self.assertTrue(p.reward_card.isHidden());self.assertTrue(p.reward_icon.pixmap().isNull())
    def test_parent_refresh_preserves_two_nonzero_readings_choice_and_tab(self):
        d=self.dialog();d.resize(850,440);p=d.panel;self.choose(p,'reward:gold99')
        for reader in(p.player,p.technical):
            p.tabs.setCurrentWidget(reader);self.qt.processEvents();c=reader.textCursor();c.setPosition(3);c.setPosition(16,QTextCursor.MoveMode.KeepAnchor);reader.setTextCursor(c);bar=reader.verticalScrollBar();self.assertGreater(bar.maximum(),0);bar.setValue(min(4,bar.maximum()));old=(c.anchor(),c.position(),bar.value(),p.scene_id,p.choice_id,p.tabs.currentIndex());self.assertTrue(p.refresh_reference());c=reader.textCursor();self.assertEqual(old,(c.anchor(),c.position(),bar.value(),p.scene_id,p.choice_id,p.tabs.currentIndex()))
    def test_owned_comparison_keeps_view_on_refresh_reopen_and_choice_switch_close(self):
        p=self.dialog().panel;self.choose(p,'reward:gold99');self.assertTrue(p.open_original());child=p.original_dialog;self.assertTrue(child.panel.follow_scene());self.assertTrue(p.refresh_reference());self.assertIs(p.original_dialog,child);self.assertEqual(child.panel.scene_id,'source-next');self.assertTrue(p.open_original());self.assertFalse(child.isVisible());child=p.original_dialog;self.choose(p,'reward:observe');self.assertFalse(child.isVisible())
    def test_bad_picture_keeps_text_source_damage_clears_recovery_manual(self):
        p=self.dialog().panel;self.choose(p,'option:enter')
        with TemporaryDirectory()as folder:
            root=Path(folder);clone(root)
            with patch.object(model,'ROOT',root):
                pic=root/p.result['data']['icon_reference']['file'];raw=pic.read_bytes();pic.write_bytes(raw+b'x');text=p.player.toPlainText();self.assertTrue(p.refresh_reference());self.assertIn('图片暂缺',p.reward_icon.text());self.assertEqual(p.player.toPlainText(),text);pic.write_bytes(raw)
                self.choose(p,'reward:gold99');self.assertTrue(p.open_original());child=p.original_dialog;f=root/model.DATA;raw=f.read_bytes();f.write_bytes(raw+b' ');self.assertFalse(p.refresh_reference());self.assertFalse(child.isVisible());self.assertTrue(p.original_button.isHidden());self.assertEqual(p.technical.toPlainText(),'');f.write_bytes(raw);self.assertTrue(p.refresh_reference());self.assertIsNone(p.scene_id);self.assertIsNone(p.choice_id)
    def test_version_exact_original99_keeps_source_scope_not_document_end(self):
        p=ExpansionUpdatePanel();self.addCleanup(p.close);p.show();p.scope.setCurrentIndex(p.scope.findData(False));p.category.setCurrentIndex(p.category.findData('choices'));key='choice_ro6_surprise_12';p.entries.setCurrentRow(next(i for i in range(p.entries.count())if p.entries.item(i).data(Qt.ItemDataRole.UserRole)==key));self.qt.processEvents();self.assertTrue(p.open_documented_flow());d=p.flow_dialog;self.assertEqual(d.panel.result['requested_original']['nextSceneId'],'scene_ro6_surprise_1');self.assertTrue(d.panel.follow_scene());self.assertEqual(d.panel.scene_id,'source-next');self.assertTrue(p.refresh_reference());self.assertTrue(d.isVisible());p._unavailable();self.assertFalse(d.isVisible())
    def test_node_default_scope_version_notice_and_parent_close_nested_comparison(self):
        p=NodeCatalogPanel();self.addCleanup(p.close);p.show();p.list.setCurrentRow(next(i for i,e in enumerate(p.entries)if e['key']=='event:community_group_023'));self.qt.processEvents();self.assertTrue(p.open_current_event_reference());d=p.current_reference_window;self.assertIsNone(d.panel.choice_id);self.assertIn('请核对实际游戏版本',d.node_reference_banner.text());self.choose(d.panel,'reward:gold99');self.assertTrue(d.panel.open_original());child=d.panel.original_dialog;p.refresh();self.assertTrue(child.isVisible());p.close();self.qt.processEvents();self.assertFalse(d.isVisible());self.assertFalse(child.isVisible())

if __name__=='__main__':unittest.main()
