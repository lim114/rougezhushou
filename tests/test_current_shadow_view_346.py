from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication
from rouge import current_shadow as model
from rouge.current_shadow_view import CurrentShadowDialog
from rouge.expansion_view import ExpansionUpdatePanel
from rouge.node_catalog_view import NodeCatalogPanel
from tests.test_current_shadow_346 import clone,JOIN_NODES
class CurrentShadowView346Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])
    def dialog(self,target=None):
        d=CurrentShadowDialog(target);d.show();self.qt.processEvents();self.addCleanup(d.close);return d
    def choose(self,p,cid):
        p.scene.setCurrentIndex(p.scene.findData(p.result['choices'][cid]['scene_id']));p.choices.setCurrentRow(next(i for i in range(p.choices.count())if p.choices.item(i).data(Qt.ItemDataRole.UserRole)==cid));self.qt.processEvents()
    def test_default_no_assumed_choice_no_unrelated_conditions(self):
        p=self.dialog().panel;self.assertEqual(p.scene_id,'node-1');self.assertIsNone(p.choice_id);self.assertEqual(p.choices.count(),2);self.assertTrue(p.reward_card.isHidden());self.assertFalse(any(hasattr(p,k)for k in('gold','life','naturals','difficulty','operator','action_points')))
    def test_all49_document_steps_and_random_cards_follow_own_target(self):
        p=self.dialog().panel
        for c in p.result['choices'].values():self.choose(p,c['id']);self.assertTrue(p.follow_scene(),c['id']);self.assertEqual(p.scene_id,c['next_scene_id'])
        p.scene.setCurrentIndex(p.scene.findData('node-18'));self.assertEqual(p.choices.count(),0);self.assertFalse(p.follow_scene())
    def test_eighth_action_point_loop_remains_manual_separate_from_named_reward(self):
        p=self.dialog().panel
        for _ in range(2):
            self.choose(p,'node-15:option:0');self.assertIn('消耗3目标生命值',p.player.toPlainText());self.assertTrue(p.follow_scene());self.choose(p,'node-15:option:0:result:0');self.assertIn('不是可以自行挑选',p.player.toPlainText());p.follow_scene();self.choose(p,'node-16:option:0');self.assertIn('不能由此认定无限次数',p.player.toPlainText());p.follow_scene();self.assertEqual(p.scene_id,'node-15')
        self.choose(p,'node-17:option:0');self.assertTrue(p.reward_card.isVisible());self.assertFalse(p.reward_icon.pixmap().isNull());self.assertTrue(p.follow_scene());self.assertEqual(p.scene_id,'node-18');self.assertTrue(p.reward_card.isHidden())
    def test_raw_choice_no_next_or_inferred_menu_and_explicit_alternate(self):
        p=self.dialog(model.locate('choices','choice_ro6_normal4_25')).panel;self.assertEqual(p.choice_id,'source-choice');self.assertFalse(p.follow_scene());self.assertIn('不根据相同消耗猜',p.player.toPlainText())
        p=self.dialog(model.locate('choices','choice_ro6_normal4_28')).panel;self.assertTrue(p.follow_scene());self.assertEqual(p.result['scenes'][p.scene_id]['source_scene_ids'],['scene_ro6_normal4_26']);self.assertEqual(p.choices.count(),0)
    def test_parent_refresh_preserves_two_nonzero_readings_choice_and_tab(self):
        d=self.dialog();d.resize(850,440);p=d.panel;self.choose(p,'node-17:option:0')
        for reader in(p.player,p.technical):
            p.tabs.setCurrentWidget(reader);self.qt.processEvents();c=reader.textCursor();c.setPosition(3);c.setPosition(16,QTextCursor.MoveMode.KeepAnchor);reader.setTextCursor(c);bar=reader.verticalScrollBar();self.assertGreater(bar.maximum(),0);bar.setValue(min(4,bar.maximum()));old=(c.anchor(),c.position(),bar.value(),p.scene_id,p.choice_id,p.tabs.currentIndex());self.assertTrue(p.refresh_reference());c=reader.textCursor();self.assertEqual(old,(c.anchor(),c.position(),bar.value(),p.scene_id,p.choice_id,p.tabs.currentIndex()))
    def test_bad_picture_keeps_text_broken_source_clears_manual_recovery(self):
        p=self.dialog(model.locate('relics','rogue_6_relic_artifact_4')).panel;self.assertTrue(p.reward_card.isVisible())
        with TemporaryDirectory()as f:
            root=Path(f);clone(root)
            with patch.object(model,'ROOT',root):
                pic=root/p.result['data']['icon_reference']['file'];pic.write_bytes(pic.read_bytes()+b'x');text=p.player.toPlainText();self.assertTrue(p.refresh_reference());self.assertEqual(p.player.toPlainText(),text);self.assertIn('图片暂缺',p.reward_icon.text());file=root/model.DATA;raw=file.read_bytes();file.write_bytes(raw+b' ');self.assertFalse(p.refresh_reference());self.assertEqual(p.technical.toPlainText(),'');self.assertTrue(p.reward_card.isHidden());self.assertTrue(p.reward_icon.pixmap().isNull());file.write_bytes(raw);self.assertTrue(p.refresh_reference());self.assertIsNone(p.scene_id);self.assertIsNone(p.choice_id)
    def test_version_original_and_relic_acquisition_entrances_close_on_loss(self):
        p=ExpansionUpdatePanel();self.addCleanup(p.close);p.show();p.scope.setCurrentIndex(p.scope.findData(False));p.category.setCurrentIndex(p.category.findData('relics'));key='rogue_6_relic_artifact_4';p.entries.setCurrentRow(next(i for i in range(p.entries.count())if p.entries.item(i).data(Qt.ItemDataRole.UserRole)==key));self.qt.processEvents();self.assertTrue(p.open_documented_flow());d=p.flow_dialog;self.assertTrue(d.panel.reward_card.isVisible());self.assertTrue(p.refresh_reference());self.assertTrue(d.isVisible());self.assertTrue(p.open_documented_flow());self.assertFalse(d.isVisible());d=p.flow_dialog;p._unavailable();self.assertFalse(d.isVisible())
    def test_node_banner_default_parent_refresh_and_close(self):
        p=NodeCatalogPanel();self.addCleanup(p.close);p.show();p.list.setCurrentRow(next(i for i,e in enumerate(p.entries)if e['key']=='event:community_group_010'));self.qt.processEvents();self.assertTrue(p.open_current_event_reference());d=p.current_reference_window;self.assertIsNone(d.panel.choice_id);self.assertIn('请核对实际游戏版本',d.node_reference_banner.text());self.choose(d.panel,'node-20:option:0');p.refresh();self.assertTrue(d.isVisible());self.assertEqual(d.panel.choice_id,'node-20:option:0');p.close();self.qt.processEvents();self.assertFalse(d.isVisible())
if __name__=='__main__':unittest.main()
