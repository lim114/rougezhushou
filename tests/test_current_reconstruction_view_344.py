from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication
from rouge import current_reconstruction as model,current_exchange_reference as offers
from rouge.current_reconstruction_view import CurrentReconstructionDialog
from rouge.expansion_view import ExpansionUpdatePanel
from rouge.node_catalog_view import NodeCatalogPanel
from tests.test_current_reconstruction_344 import clone
from tests.test_current_exchange_reference_323 import clone as clone_offers

class CurrentReconstructionView344Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])
    def dialog(self,target=None):
        d=CurrentReconstructionDialog(target);d.show();self.qt.processEvents();self.addCleanup(d.close);return d
    def choose(self,p,cid):
        p.scene.setCurrentIndex(p.scene.findData(p.result['choices'][cid]['scene_id']));p.choices.setCurrentRow(next(i for i in range(p.choices.count())if p.choices.item(i).data(Qt.ItemDataRole.UserRole)==cid));self.qt.processEvents()
    def test_default_four_document_options_no_assumed_inventory_or_irrelevant_controls(self):
        p=self.dialog().panel;self.assertIsNone(p.choice_id);self.assertEqual(p.choices.count(),4);self.assertEqual(p.naturals.value(),-1);self.assertTrue(p.natural_controls.isHidden());self.assertTrue(p.reward_card.isHidden());self.assertTrue(p.catalogue_button.isHidden());self.assertFalse(any(hasattr(p,k)for k in('gold','offer','difficulty','operator','action_points')))
    def test_natural_controls_only_restore_and_count_boundary_blocks_followup(self):
        p=self.dialog().panel;self.choose(p,'doc-choice:10');self.assertTrue(p.natural_controls.isVisible())
        for value in(0,1):p.naturals.setValue(value);self.assertFalse(p.follow_scene())
        p.naturals.setValue(2);self.assertTrue(p.follow_scene());self.assertTrue(p.natural_controls.isHidden());self.choose(p,'doc-choice:12');self.assertTrue(p.reward_card.isVisible());self.assertFalse(p.reward_icon.pixmap().isNull());self.assertIn('不再次消耗2件自然物',p.player.toPlainText());self.assertTrue(p.follow_scene());self.assertEqual(p.choices.count(),0)
    def test_all_six_document_paths_stop_at_own_terminal_and_do_not_sum_rewards(self):
        p=self.dialog().panel
        for path,end in [([2,4,16,18],'doc:19'),([6,8,22,24],'doc:25'),([2,4,20],'doc:21'),([6,8,26],'doc:27'),([10,12],'doc:13'),([14],'doc:15')]:
            p.go_start()
            for row in path:self.choose(p,'doc-choice:'+str(row));self.assertTrue(p.follow_scene())
            self.assertEqual(p.scene_id,end);self.assertEqual(p.choices.count(),0);self.assertFalse(p.follow_scene());self.assertTrue(p.catalogue_button.isHidden())
    def test_offer_directory_only_known_relic_offerings_not_reward_or_parts(self):
        p=self.dialog().panel
        for cid in('doc-choice:2','doc-choice:16'):
            self.choose(p,cid);self.assertTrue(p.catalogue_button.isVisible());self.assertTrue(p.open_catalogue());child=p.catalogue_dialog;self.assertIsNone(child.panel.item_id);self.assertIn('不是奖励池',child.panel.count.text());self.assertEqual(child.panel.items.count(),284)
        for cid in('doc-choice:4','doc-choice:6','doc-choice:8','doc-choice:22','doc-choice:24','doc-choice:12'):
            self.choose(p,cid);self.assertTrue(p.catalogue_button.isHidden());self.assertFalse(p.open_catalogue());self.assertFalse(child.isVisible())
    def test_raw_continue_has_no_doc_next_or_relic_directory_and_raw_scene_no_menu(self):
        p=self.dialog(model.locate('choices','choice_ro6_sacrifice1_6')).panel;self.assertEqual(p.choice_id,'source-choice');self.assertFalse(p.follow_scene());self.assertTrue(p.catalogue_button.isHidden());self.assertIn('不按编号指定类型',p.player.toPlainText())
        p=self.dialog(model.locate('scenes','scene_ro6_sacrifice1_enter')).panel;self.assertEqual(p.choices.count(),0);self.assertEqual(p.scene_id,'source-scene')
    def test_parent_refresh_preserves_two_nonzero_readings_and_natural_condition(self):
        d=self.dialog();d.resize(850,440);p=d.panel;self.choose(p,'doc-choice:10');p.naturals.setValue(2)
        for reader in(p.player,p.technical):
            p.tabs.setCurrentWidget(reader);self.qt.processEvents();c=reader.textCursor();c.setPosition(3);c.setPosition(16,QTextCursor.MoveMode.KeepAnchor);reader.setTextCursor(c);bar=reader.verticalScrollBar();self.assertGreater(bar.maximum(),0);bar.setValue(min(4,bar.maximum()));old=(c.anchor(),c.position(),bar.value(),p.scene_id,p.choice_id,p.tabs.currentIndex(),p.naturals.value());self.assertTrue(p.refresh_reference());c=reader.textCursor();self.assertEqual(old,(c.anchor(),c.position(),bar.value(),p.scene_id,p.choice_id,p.tabs.currentIndex(),p.naturals.value()))
    def test_owned_offer_directory_state_survives_refresh_and_switch_closes_it(self):
        p=self.dialog().panel;self.choose(p,'doc-choice:2');self.assertTrue(p.open_catalogue());child=p.catalogue_dialog;op=child.panel;op.offer.setCurrentIndex(op.offer.findData(False));op.search.setText('焚毁');op.items.setCurrentRow(0);self.qt.processEvents();selected=op.item_id;self.assertIsNotNone(selected);self.assertTrue(p.refresh_reference());self.assertIs(p.catalogue_dialog,child);self.assertEqual((op.item_id,op.search.text(),op.offer.currentData()),(selected,'焚毁',False));self.choose(p,'doc-choice:6');self.assertFalse(child.isVisible())
    def test_optional_offer_source_loss_closes_only_child_not_verified_event(self):
        p=self.dialog().panel;self.choose(p,'doc-choice:2');self.assertTrue(p.open_catalogue());child=p.catalogue_dialog;text=p.player.toPlainText()
        with TemporaryDirectory()as folder:
            root=Path(folder);clone_offers(root);f=root/offers.DATA;f.write_bytes(f.read_bytes()+b' ')
            with patch.object(offers,'ROOT',root):self.assertTrue(p.refresh_reference());self.assertFalse(child.isVisible());self.assertTrue(p.catalogue_button.isHidden());self.assertEqual(p.player.toPlainText(),text);self.assertFalse(p.open_catalogue())
        self.assertTrue(p.refresh_reference());self.assertTrue(p.catalogue_button.isVisible());self.assertIsNone(p.catalogue_dialog)
    def test_bad_reward_picture_keeps_text_whole_source_loss_clears_and_recovers_manually(self):
        p=self.dialog().panel;self.choose(p,'doc-choice:12')
        with TemporaryDirectory()as folder:
            root=Path(folder);clone(root)
            with patch.object(model,'ROOT',root):
                pic=root/p.result['data']['icon_reference']['file'];raw=pic.read_bytes();pic.write_bytes(raw+b'x');text=p.player.toPlainText();self.assertTrue(p.refresh_reference());self.assertIn('图片暂缺',p.reward_icon.text());self.assertEqual(p.player.toPlainText(),text);pic.write_bytes(raw)
                f=root/model.DATA;raw=f.read_bytes();f.write_bytes(raw+b' ');self.assertFalse(p.refresh_reference());self.assertTrue(p.reward_card.isHidden());self.assertEqual(p.technical.toPlainText(),'');f.write_bytes(raw);self.assertTrue(p.refresh_reference());self.assertIsNone(p.scene_id);self.assertIsNone(p.choice_id)
    def test_exact_version_entry_default_original_does_not_autoconnnect_document(self):
        p=ExpansionUpdatePanel();self.addCleanup(p.close);p.show();p.scope.setCurrentIndex(p.scope.findData(False));p.category.setCurrentIndex(p.category.findData('choices'));key='choice_ro6_sacrifice1_1';p.entries.setCurrentRow(next(i for i in range(p.entries.count())if p.entries.item(i).data(Qt.ItemDataRole.UserRole)==key));self.qt.processEvents();self.assertTrue(p.open_documented_flow());d=p.flow_dialog;self.assertEqual(d.panel.result['requested_original']['id'],key);self.assertFalse(d.panel.follow_scene());self.assertTrue(p.refresh_reference());self.assertTrue(d.isVisible());p._unavailable();self.assertFalse(d.isVisible())
    def test_node_default_and_parent_closes_event_and_owned_catalogue(self):
        p=NodeCatalogPanel();self.addCleanup(p.close);p.show();p.list.setCurrentRow(next(i for i,e in enumerate(p.entries)if e['key']=='event:community_group_025'));self.qt.processEvents();self.assertTrue(p.open_current_event_reference());d=p.current_reference_window;self.assertEqual(d.panel.scene_id,'doc:1');self.assertIsNone(d.panel.choice_id);self.assertIn('请核对实际游戏版本',d.node_reference_banner.text());self.choose(d.panel,'doc-choice:2');self.assertTrue(d.panel.open_catalogue());child=d.panel.catalogue_dialog;p.refresh();self.assertTrue(child.isVisible());p.close();self.qt.processEvents();self.assertFalse(d.isVisible());self.assertFalse(child.isVisible())

if __name__=='__main__':unittest.main()
