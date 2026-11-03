from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication
from rouge import current_ritual_reference as model
from rouge.current_ritual_view import CurrentRitualPanel
from rouge.expansion_view import ExpansionUpdatePanel
from tests.test_current_ritual_reference_324 import clone

class CurrentRitualView324Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])
    def panel(self,event='ritual',sid=None,cid=None):
        p=CurrentRitualPanel(event,sid,cid);p.resize(900,500);p.show();self.addCleanup(p.close);self.qt.processEvents();return p
    def select(self,p,cid):
        for i in range(p.choices.count()):
            if p.choices.item(i).data(Qt.ItemDataRole.UserRole)==cid:p.choices.setCurrentRow(i);return
        self.fail('Missing '+cid)
    def test_all_nine_scenes_and_thirteen_choices_no_immediate_battle(self):
        for event in('ritual','tears'):
            p=self.panel(event)
            for sid,s in p.result['scenes'].items():
                p.scene.setCurrentIndex(p.scene.findData(sid));self.assertEqual(p.choices.count(),len(s['choice_ids']))
                for cid in s['choice_ids']:
                    self.select(p,cid);self.assertIn(p.result['data']['originals']['choices'][cid]['title'],p.player.toPlainText());self.assertFalse(p.battle_button.isVisible());self.assertFalse(p.open_battle());self.assertEqual(p.related_button.isVisible(),event=='ritual')
    def test_three_exact_source_windows_alternatives_no_source_and_owned_closure(self):
        p=self.panel(sid='scene_ro6_end3_1',cid='choice_ro6_end3_3');self.assertTrue(p.open_material());old=p.material_dialog;self.assertEqual(old.panel.event_id,'tears');self.assertEqual(old.panel.choice_id,'choice_ro6_chimera2_1');self.assertIn('全部源石锭',old.panel.player.toPlainText())
        self.select(p,'choice_ro6_end3_4');self.assertFalse(old.isVisible());self.assertFalse(p.material_button.isVisible());self.assertFalse(p.open_material())
        p.scene.setCurrentIndex(p.scene.findData('scene_ro6_end3_3'));self.select(p,'choice_ro6_end3_6');self.assertTrue(p.open_material());old=p.material_dialog;self.assertEqual(old.panel.tabs.currentIndex(),1);self.assertIn('焚毁',old.panel.doc_player.toPlainText());self.assertIsNone(old.panel.result['actual_reward_pool']);p.scene.setCurrentIndex(p.scene.findData('scene_ro6_end3_4'));self.assertFalse(old.isVisible())
        self.select(p,'choice_ro6_end3_9');self.assertTrue(p.open_material());self.assertEqual(p.material_dialog.panel.stage_id,'ro6_t_12');self.assertTrue(p.open_related());self.assertEqual(p.battle_dialog.panel.stage_id,'ro6_b_6');a=p.material_dialog;b=p.battle_dialog;p.close();self.assertFalse(a.isVisible());self.assertFalse(b.isVisible())
    def test_optional_exchange_source_failure_isolated_core_keeps_related(self):
        p=self.panel(sid='scene_ro6_end3_3',cid='choice_ro6_end3_6');p.open_material();old=p.material_dialog
        with patch('rouge.current_exchange_reference.target_entry',return_value=None):
            self.assertFalse(p.open_material());self.assertFalse(old.isVisible());self.assertFalse(p.material_button.isVisible());self.assertIsNotNone(p.result);self.assertTrue(p.open_related());self.assertTrue(p.related_button.isVisible())
        from rouge.current_exchange_reference import target_entry
        self.assertTrue(p.refresh_reference());self.assertTrue(p.material_button.isVisible());self.assertTrue(p.open_material());child=p.material_dialog;self.assertTrue(p.refresh_reference());self.assertTrue(child.isVisible());self.assertEqual(child.panel.group_id,target_entry('choices','choice_ro6_sacrifice2_21')['group_id'])
    def test_refresh_preserves_both_nonzero_readers_and_material_child(self):
        p=self.panel(sid='scene_ro6_end3_1',cid='choice_ro6_end3_3');p.resize(850,420);p.open_material();child=p.material_dialog
        for reader in(p.player,p.technical):
            p.tabs.setCurrentWidget(reader);self.qt.processEvents();c=reader.textCursor();c.setPosition(3);c.setPosition(16,QTextCursor.MoveMode.KeepAnchor);reader.setTextCursor(c);bar=reader.verticalScrollBar();self.assertGreater(bar.maximum(),0);bar.setValue(min(4,bar.maximum()));before=(c.anchor(),c.position(),bar.value(),p.tabs.currentIndex(),p.scene_id,p.choice_id,child.panel.scene_id,child.panel.choice_id)
            self.assertTrue(p.refresh_reference());self.qt.processEvents();c=reader.textCursor();self.assertEqual(before,(c.anchor(),c.position(),bar.value(),p.tabs.currentIndex(),p.scene_id,p.choice_id,child.panel.scene_id,child.panel.choice_id));self.assertTrue(child.isVisible())
    def test_actual_source_loss_clears_two_children_recovery_manual(self):
        p=self.panel(sid='scene_ro6_end3_4',cid='choice_ro6_end3_9');p.open_material();p.open_related();a=p.material_dialog;b=p.battle_dialog
        with TemporaryDirectory()as folder:
            root=Path(folder);clone(root);f=root/model.DATA;raw=f.read_bytes()
            with patch.object(model,'ROOT',root):
                f.write_bytes(raw+b' ');self.assertFalse(p.refresh_reference());self.assertFalse(a.isVisible());self.assertFalse(b.isVisible());self.assertIsNone(p.result);self.assertEqual(p.technical.toPlainText(),'');self.assertFalse(p.related_button.isVisible());f.write_bytes(raw);self.assertTrue(p.refresh_reference());self.assertIsNone(p.scene_id);self.assertIsNone(p.choice_id);self.assertFalse(p.open_material())
    def test_actual_expansion_scene_choice_material_and_key_overview_entry(self):
        p=ExpansionUpdatePanel();p.show();self.addCleanup(p.close);p.scope.setCurrentIndex(p.scope.findData(False))
        for cat,key in(('scenes','scene_ro6_end3_4'),('choices','choice_ro6_end3_10'),('relics','rogue_6_relic_final_4'),('relics','rogue_6_relic_cargo_13'),('scenes','scene_ro6_chimera2_enter')):
            p.category.setCurrentIndex(p.category.findData(cat));i=next(i for i in range(p.entries.count())if p.entries.item(i).data(Qt.ItemDataRole.UserRole)==key);p.entries.setCurrentRow(i);self.assertTrue(p.flow_button.isVisible());self.assertTrue(p.open_documented_flow());child=p.flow_dialog;target=model.locate(cat,key);self.assertEqual(child.panel.scene_id,target['scene_id']);self.assertEqual(child.panel.choice_id,target['choice_id']);self.assertTrue(p.refresh_reference());self.assertTrue(child.isVisible())
        self.assertTrue(p.open_documented_flow());self.assertFalse(child.isVisible());child=p.flow_dialog;p._unavailable();self.assertFalse(child.isVisible())

if __name__=='__main__':unittest.main()
