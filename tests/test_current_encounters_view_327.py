from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication
from rouge import current_encounters as model
from rouge.current_encounters_view import CurrentEncountersPanel
from rouge.current_event_battles_view import CurrentEventBattlesPanel
from rouge.expansion_view import ExpansionUpdatePanel
from tests.test_current_encounters_327 import clone,by_original
class CurrentEncountersView327Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])
    def panel(self,title,original=None):
        target=model.locate('choices',original)if original else None;p=CurrentEncountersPanel(title,target['scene_id']if target else None,target['choice_id']if target else None);p.resize(960,550);p.show();self.addCleanup(p.close);self.qt.processEvents();return p
    def select(self,p,cid):
        for i in range(p.choices.count()):
            if p.choices.item(i).data(Qt.ItemDataRole.UserRole)==cid:p.choices.setCurrentRow(i);return
        self.fail('Missing '+cid)
    def test_all_23_scenes_25_groups_and_only_black_has_controller_control(self):
        for title in model.packet()['data']['events']:
            p=self.panel(title);self.assertEqual(hasattr(p,'controller'),title=='黑诞')
            for sid,s in p.result['scenes'].items():
                p.scene.setCurrentIndex(p.scene.findData(sid));self.assertEqual(p.choices.count(),len(s['choice_ids']))
                for cid in s['choice_ids']:
                    self.select(p,cid);c=p.result['choices'][cid];self.assertIn(c['title'],p.player.toPlainText());self.assertEqual(p.battle_button.isVisible(),c['has_documented_battle_link'])
    def test_required_controller_false_blocks_only_its_branch_same_choice_kept(self):
        p=self.panel('黑诞','choice_ro6_normal2_1');selected=p.choice_id
        for value in(None,False,True,None):
            p.controller.setCurrentIndex(p.controller.findData(value));self.assertEqual(p.choice_id,selected);self.assertEqual(p.next_button.isEnabled(),value is not False)
            if value is False:self.assertFalse(p.follow_scene())
        self.select(p,by_original(p.result,'choice_ro6_normal2_2')['id']);p.controller.setCurrentIndex(p.controller.findData(False));self.assertTrue(p.battle_button.isEnabled());self.assertTrue(p.open_battle());self.assertEqual(p.battle_dialog.panel.choice_id,'choice_ro6_normal2_2')
    def test_setup_only_follows_narrative_then_exact_emergency_config_browser(self):
        p=self.panel('鸭托邦','choice_ro6_bat3_2');self.assertFalse(p.battle_button.isVisible());self.assertFalse(p.open_battle());self.assertTrue(p.follow_scene());cid=by_original(p.result,'choice_ro6_bat3_5')['id'];self.select(p,cid);self.assertTrue(p.open_battle());child=p.battle_dialog;self.assertEqual(child.panel.stages.itemData(1),'ro6_e_t_3');self.assertEqual(child.panel.stages.count(),2);self.assertIsNone(child.panel.stages.currentData());p.go_start();self.assertFalse(child.isVisible())
    def test_two_nonzero_readers_controller_and_child_state_preserved_refresh(self):
        p=self.panel('黑诞','choice_ro6_normal2_2');p.resize(850,440);p.controller.setCurrentIndex(p.controller.findData(False));p.open_battle();child=p.battle_dialog;child.panel.stages.setCurrentIndex(child.panel.stages.findData('ro6_t_13'))
        for reader in(p.player,p.technical):
            p.tabs.setCurrentWidget(reader);self.qt.processEvents();c=reader.textCursor();c.setPosition(3);c.setPosition(16,QTextCursor.MoveMode.KeepAnchor);reader.setTextCursor(c);bar=reader.verticalScrollBar();self.assertGreater(bar.maximum(),0);bar.setValue(min(4,bar.maximum()));before=(c.anchor(),c.position(),bar.value(),p.tabs.currentIndex(),p.scene_id,p.choice_id,p.controller.currentData(),child.panel.stages.currentData());self.assertTrue(p.refresh_reference());self.qt.processEvents();c=reader.textCursor();self.assertEqual(before,(c.anchor(),c.position(),bar.value(),p.tabs.currentIndex(),p.scene_id,p.choice_id,p.controller.currentData(),child.panel.stages.currentData()));self.assertTrue(child.isVisible())
    def test_optional_battle_source_failure_keeps_flow_and_actual_core_damage_clears(self):
        p=self.panel('鸭托邦','choice_ro6_bat3_5');p.open_battle();child=p.battle_dialog
        with patch('rouge.current_event_battles.locate',return_value=None):self.assertTrue(p.refresh_reference());self.assertIsNotNone(p.result);self.assertFalse(p.battle_button.isEnabled());self.assertFalse(child.isVisible());self.assertFalse(p.open_battle())
        p.refresh_reference();self.assertTrue(p.open_battle());child=p.battle_dialog
        with TemporaryDirectory()as folder:
            root=Path(folder);clone(root);f=root/model.DATA;raw=f.read_bytes()
            with patch.object(model,'ROOT',root):
                f.write_bytes(raw+b' ');self.assertFalse(p.refresh_reference());self.assertFalse(child.isVisible());self.assertIsNone(p.result);self.assertEqual(p.technical.toPlainText(),'');f.write_bytes(raw);self.assertTrue(p.refresh_reference());self.assertIsNone(p.scene_id);self.assertIsNone(p.choice_id)
    def test_battle_browser_full_dialog_exact_parent_preserves_refresh_and_closes(self):
        p=CurrentEventBattlesPanel('鸭托邦','choice_ro6_bat3_5');p.show();self.addCleanup(p.close);self.assertTrue(p.flow_button.isVisible());self.assertTrue(p.open_full_flow());child=p.flow_dialog;self.assertEqual(child.panel.scene_id,'scene_ro6_bat3_2');self.assertEqual(child.panel.choice_id,model.locate('choices','choice_ro6_bat3_5')['choice_id']);self.assertTrue(p.refresh_reference());self.assertTrue(child.isVisible());self.assertTrue(p.open_full_flow());self.assertFalse(child.isVisible());child=p.flow_dialog;p.close();self.assertFalse(child.isVisible())
    def test_actual_update_all_original_variants_and_scenes_have_exact_full_flow_entry(self):
        p=ExpansionUpdatePanel();p.show();self.addCleanup(p.close);p.scope.setCurrentIndex(p.scope.findData(False));d=model.packet()['data']
        for cat,keys in(('scenes',d['originals']['scenes']),('choices',d['originals']['choices'])):
            p.category.setCurrentIndex(p.category.findData(cat))
            for key in keys:
                i=next(i for i in range(p.entries.count())if p.entries.item(i).data(Qt.ItemDataRole.UserRole)==key);p.entries.setCurrentRow(i);self.assertTrue(p.flow_button.isVisible());self.assertTrue(p.open_documented_flow());child=p.flow_dialog;target=model.locate(cat,key);self.assertEqual(child.panel.scene_id,target['scene_id']);self.assertEqual(child.panel.choice_id,target['choice_id']);self.assertTrue(p.refresh_reference());self.assertTrue(child.isVisible())
        p._unavailable();self.assertFalse(child.isVisible())

if __name__=='__main__':unittest.main()
