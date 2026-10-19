from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication
from rouge import current_lake as model
from rouge.current_lake_view import CurrentLakePanel
from rouge.current_event_battles_view import CurrentEventBattlesPanel
from rouge.expansion_view import ExpansionUpdatePanel
from tests.test_current_lake_328 import clone,cid,sid
class CurrentLakeView328Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])
    def panel(self,n=None):
        p=CurrentLakePanel(model.locate('choices',cid(n))if n else None);p.resize(850,440);p.show();self.addCleanup(p.close);self.qt.processEvents();return p
    def select(self,p,key):
        for i in range(p.choices.count()):
            if p.choices.item(i).data(Qt.ItemDataRole.UserRole)==key:p.choices.setCurrentRow(i);return
        self.fail('Missing '+key)
    def test_all_ten_scenes_fourteen_action_contexts_no_extra_choices(self):
        p=self.panel();total=0
        for key,s in p.result['scenes'].items():
            p.scene.setCurrentIndex(p.scene.findData(key));self.assertEqual(p.choices.count(),len(s['choice_ids']))
            for c in s['choice_ids']:
                self.select(p,c);total+=1;self.assertIn(p.result['choices'][c]['title'],p.player.toPlainText());self.assertEqual(p.battle_button.isVisible(),c in(cid(5),cid(9)))
        self.assertEqual(total,14)
    def test_shared_choice_waits_for_phase_preserves_prompt_then_focuses_exact_action(self):
        for n in(4,6):
            p=self.panel(n);self.assertIsNone(p.scene_id);self.assertIsNone(p.choice_id);self.assertIn('请先从上方选择',p.player.toPlainText());self.assertTrue(p.refresh_reference());self.assertIn('请先从上方选择',p.player.toPlainText())
            for s in(1,5,6):p.scene.setCurrentIndex(p.scene.findData(sid(s)));self.assertEqual(p.choice_id,cid(n))
    def test_repeated_action_reaches_watch_random_ordinary_follow_disabled_two_results_separate(self):
        p=self.panel(7);self.assertEqual(p.scene_id,sid(5));self.assertTrue(p.follow_scene());self.assertEqual(p.scene_id,sid(6));self.select(p,cid(8));self.assertFalse(p.follow_scene());self.assertFalse(p.next_button.isEnabled());self.assertTrue(all(b.isVisible()for b in p.outcome_buttons));self.assertFalse(p.open_documented_outcome(sid(9)))
        for s in(7,8):
            p.scene.setCurrentIndex(p.scene.findData(sid(6)));self.select(p,cid(8));self.assertTrue(p.open_documented_outcome(sid(s)));self.assertEqual(p.scene_id,sid(s));self.assertIsNone(p.result['actual_outcome']);self.assertFalse(any(b.isVisible()for b in p.outcome_buttons));self.assertFalse(p.open_documented_outcome(sid(7)))
    def test_normal_urgent_readers_exact_no_default_version_and_back_to_same_phase(self):
        for n,s,stage_count in((5,3,3),(9,7,2)):
            p=self.panel(n);self.assertTrue(p.open_battle());child=p.battle_dialog;self.assertEqual(child.panel.choice_id,cid(n));self.assertEqual(child.panel.stages.count(),stage_count);self.assertIsNone(child.panel.stages.currentData());self.assertTrue(child.panel.open_full_flow());full=child.panel.flow_dialog;self.assertEqual((full.panel.scene_id,full.panel.choice_id),(sid(s),cid(n)));self.assertTrue(p.refresh_reference());self.assertTrue(child.isVisible());self.assertTrue(full.isVisible());p.go_start();self.assertFalse(child.isVisible());self.assertFalse(full.isVisible())
    def test_two_nonzero_readers_parent_refresh_keeps_phase_choice_and_nested_map(self):
        p=self.panel(9);self.assertTrue(p.open_battle());child=p.battle_dialog;child.panel.stages.setCurrentIndex(child.panel.stages.findData('ro6_e_t_5'));self.assertTrue(child.panel.open_battle());battle=child.panel.battle_dialog
        for reader in(p.player,p.technical):
            p.tabs.setCurrentWidget(reader);self.qt.processEvents();c=reader.textCursor();c.setPosition(3);c.setPosition(16,QTextCursor.MoveMode.KeepAnchor);reader.setTextCursor(c);bar=reader.verticalScrollBar();self.assertGreater(bar.maximum(),0);bar.setValue(min(4,bar.maximum()));before=(c.anchor(),c.position(),bar.value(),p.tabs.currentIndex(),p.scene_id,p.choice_id,child.panel.stages.currentData());self.assertTrue(p.refresh_reference());self.qt.processEvents();c=reader.textCursor();self.assertEqual(before,(c.anchor(),c.position(),bar.value(),p.tabs.currentIndex(),p.scene_id,p.choice_id,child.panel.stages.currentData()));self.assertTrue(child.isVisible());self.assertTrue(battle.isVisible())
    def test_optional_map_loss_core_damage_and_manual_recovery_close_children(self):
        p=self.panel(5);p.open_battle();child=p.battle_dialog
        with patch('rouge.current_event_battles.locate',return_value=None):self.assertTrue(p.refresh_reference());self.assertIsNotNone(p.result);self.assertFalse(p.battle_button.isEnabled());self.assertFalse(child.isVisible());self.assertFalse(p.open_battle())
        p.refresh_reference();self.assertTrue(p.open_battle());child=p.battle_dialog
        with TemporaryDirectory()as folder:
            root=Path(folder);clone(root);f=root/model.DATA;raw=f.read_bytes()
            with patch.object(model,'ROOT',root):
                f.write_bytes(raw+b' ');self.assertFalse(p.refresh_reference());self.assertFalse(child.isVisible());self.assertIsNone(p.result);self.assertEqual(p.technical.toPlainText(),'');self.assertFalse(any(b.isVisible()for b in p.outcome_buttons));f.write_bytes(raw);self.assertTrue(p.refresh_reference());self.assertIsNone(p.scene_id);self.assertIsNone(p.choice_id)
    def test_version_reader_all_original_scene_and_choice_entries_exact_or_require_phase(self):
        p=ExpansionUpdatePanel();p.show();self.addCleanup(p.close);p.scope.setCurrentIndex(p.scope.findData(False));r=model.reference()
        for cat,keys in(('scenes',r['scenes']),('choices',r['choices'])):
            p.category.setCurrentIndex(p.category.findData(cat))
            for key in keys:
                i=next(i for i in range(p.entries.count())if p.entries.item(i).data(Qt.ItemDataRole.UserRole)==key);p.entries.setCurrentRow(i);self.assertTrue(p.flow_button.isVisible());self.assertTrue(p.open_documented_flow());child=p.flow_dialog;t=model.locate(cat,key);self.assertEqual(child.panel.scene_id,t['scene_id']);self.assertEqual(child.panel.choice_id,None if t['phase_needed']else t['choice_id']);self.assertTrue(p.refresh_reference());self.assertTrue(child.isVisible())
        p._unavailable();self.assertFalse(child.isVisible())
if __name__=='__main__':unittest.main()
