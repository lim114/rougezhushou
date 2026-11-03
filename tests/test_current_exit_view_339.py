from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication
from rouge import current_exit as model
from rouge.current_exit_view import CurrentExitDialog
from rouge.expansion_view import ExpansionUpdatePanel
from rouge.node_catalog_view import NodeCatalogPanel
from tests.test_current_exit_339 import clone

class CurrentExitView339Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])
    def dialog(self,target=None):
        d=CurrentExitDialog(target);d.show();self.qt.processEvents();self.addCleanup(d.close);return d
    def select(self,p,role,occurrence=0):
        c=[v for v in p.result['choices'].values()if v['role']==role][occurrence];p.scene.setCurrentIndex(p.scene.findData(c['scene_id']));p.choices.setCurrentRow(next(i for i in range(p.choices.count())if p.choices.item(i).data(Qt.ItemDataRole.UserRole)==c['id']));return c
    def test_defaults_unknown_and_only_event_appropriate_controls(self):
        p=self.dialog().panel;self.assertTrue(all(v is None for v in p.result['declared'].values()));self.assertFalse(hasattr(p,'controller'));self.assertFalse(hasattr(p,'source_key'));self.assertFalse(p.open_battle())
    def test_grade15_16_and_gold9_10_boundaries_do_not_change_variant_or_run(self):
        p=self.dialog().panel;c=self.select(p,'persuade_part');p.action_points.setValue(7);p.difficulty.setValue(15);self.assertIn('等量希望为7',p.player.toPlainText());self.assertTrue(p.next_button.isEnabled());p.difficulty.setValue(16);self.assertIn('不再获得加工品',p.player.toPlainText());self.assertFalse(p.follow_scene());self.assertIsNone(p.result['choices'][c['id']]['actual_variant_id'])
        self.select(p,'help');p.gold.setValue(9);self.assertFalse(p.follow_scene());p.gold.setValue(10);self.assertTrue(p.follow_scene());self.assertEqual(p.choices.count(),0)
    def test_repeated_document_dialogue_ends_instead_of_looping_reward(self):
        p=self.dialog().panel;self.select(p,'persuade_part');self.assertTrue(p.follow_scene());self.assertEqual(p.choices.count(),2);self.select(p,'persuade_part',1);self.assertTrue(p.follow_scene());self.assertEqual(p.scene_id,'document:exit-repeat-result');self.assertEqual(p.choices.count(),0);self.assertFalse(p.next_button.isVisible())
    def test_source_only_originals_never_appear_as_initial_menu(self):
        p=self.dialog().panel
        for i in range(2):
            c=self.select(p,'persuade_no_part',i);self.assertIn('前置情景没有文献证据',p.player.toPlainText());self.assertFalse(c['document_parent_verified']);self.assertTrue(p.follow_scene());self.assertEqual(p.scene_id,'document:exit-repeat-result')
    def test_ambiguous_originals_start_without_chosen_document_occurrence(self):
        for category,key in [('choices','choice_ro6_final1_1'),('choices','choice_ro6_final1_5'),('scenes','scene_ro6_final1_3')]:
            p=self.dialog(model.locate(category,key)).panel;self.assertIsNone(p.scene_id);self.assertIsNone(p.choice_id);self.assertIn('不止一处',p.player.toPlainText())
    def test_same_identity_refresh_keeps_two_real_nonzero_readings_conditions_and_request(self):
        d=self.dialog(model.locate('choices','choice_ro6_final1_8'));d.resize(850,440);p=d.panel;p.gold.setValue(10);p.action_points.setValue(7);p.difficulty.setValue(16)
        for reader in(p.player,p.technical):
            p.tabs.setCurrentWidget(reader);self.qt.processEvents();cur=reader.textCursor();cur.setPosition(3);cur.setPosition(16,QTextCursor.MoveMode.KeepAnchor);reader.setTextCursor(cur);bar=reader.verticalScrollBar();self.assertGreater(bar.maximum(),0);bar.setValue(min(4,bar.maximum()));old=(cur.anchor(),cur.position(),bar.value(),p.scene_id,p.choice_id,p.tabs.currentIndex(),dict(p.result['declared']),dict(p.source_request));self.assertTrue(p.refresh_reference());cur=reader.textCursor();self.assertEqual(old,(cur.anchor(),cur.position(),bar.value(),p.scene_id,p.choice_id,p.tabs.currentIndex(),dict(p.result['declared']),dict(p.source_request)))
    def test_all14_version_entries_open_with_exact_source_request(self):
        p=ExpansionUpdatePanel();p.show();self.addCleanup(p.close);p.scope.setCurrentIndex(p.scope.findData(False));r=model.reference()
        for cat,keys in [('scenes',r['data']['originals']['scenes']),('choices',r['data']['originals']['choices']),('relics',['rogue_6_relic_final_7'])]:
            p.category.setCurrentIndex(p.category.findData(cat))
            for key in keys:
                p.entries.setCurrentRow(next(i for i in range(p.entries.count())if p.entries.item(i).data(Qt.ItemDataRole.UserRole)==key));self.assertTrue(p.open_documented_flow());self.assertEqual(p.flow_dialog.panel.source_request,{'category':cat,'key':key})
        old=p.flow_dialog;self.assertTrue(p.open_documented_flow());self.assertFalse(old.isVisible());p._unavailable();self.assertFalse(p.flow_dialog.isVisible())
    def test_actual_source_loss_clears_old_followup_and_manual_recovery(self):
        p=self.dialog().panel;self.select(p,'help')
        with TemporaryDirectory()as folder:
            root=Path(folder);clone(root);file=root/model.DATA;raw=file.read_bytes()
            with patch.object(model,'ROOT',root):
                file.write_bytes(raw+b' ');self.assertFalse(p.refresh_reference());self.assertIsNone(p.result);self.assertEqual(p.technical.toPlainText(),'');file.write_bytes(raw);self.assertTrue(p.refresh_reference());self.assertIsNone(p.scene_id);self.assertIsNone(p.choice_id)
    def test_node_entry_default_unknown_source_failure_keeps_old_catalogue_then_close(self):
        p=NodeCatalogPanel();p.show();self.addCleanup(p.close);p.list.setCurrentRow(next(i for i,e in enumerate(p.entries)if e['key']=='event:community_group_033'));self.assertTrue(p.open_current_event_reference());d=p.current_reference_window;self.assertTrue(all(v is None for v in d.panel.result['declared'].values()));self.assertIn('请核对实际游戏版本',d.node_reference_banner.text());p.refresh();self.assertTrue(d.isVisible());p.close();self.assertFalse(d.isVisible())
if __name__=='__main__':unittest.main()
