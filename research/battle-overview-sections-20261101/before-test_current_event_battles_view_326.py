from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication
from rouge import current_event_battles as model
from rouge.current_event_battles_view import CurrentEventBattlesPanel
from rouge.current_battle_view import CurrentBattlePanel
from rouge.expansion_view import ExpansionUpdatePanel
from tests.test_current_event_battles_326 import clone
class CurrentEventBattlesView326Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])
    def panel(self,*a,**kw):
        p=CurrentEventBattlesPanel(*a,**kw);p.resize(980,560);p.show();self.addCleanup(p.close);self.qt.processEvents();return p
    def select(self,p,cid):
        for i in range(p.choices.count()):
            if p.choices.item(i).data(Qt.ItemDataRole.UserRole)==cid:p.choices.setCurrentRow(i);return
        self.fail('Missing '+cid)
    def test_all_twelve_options_no_default_version_and_all_twenty_exact_previews(self):
        p=self.panel();self.assertEqual(p.choices.count(),12);self.assertIsNone(p.choice_id);self.assertFalse(p.open_battle())
        for c in p.result['rows']:
            self.select(p,c['id']);self.assertIsNone(p.stages.currentData());self.assertFalse(p.open_button.isEnabled());self.assertEqual(p.stages.count(),len(c['stage_ids'])+1)
            for sid in c['stage_ids']:
                p.stages.setCurrentIndex(p.stages.findData(sid));self.assertTrue(p.open_battle());old=p.battle_dialog;self.assertEqual(old.panel.stage_id,sid);self.assertTrue(old.isVisible());p.stages.setCurrentIndex(0);self.assertFalse(old.isVisible())
    def test_emergency_only_one_map_black_six_and_repeated_lake_single_choice(self):
        p=self.panel('鸭托邦','choice_ro6_bat3_5');self.assertEqual(p.stages.count(),2);self.assertEqual(p.stages.itemData(1),'ro6_e_t_3');self.assertIn('已排除',p.player.toPlainText());self.assertIsNone(p.stages.currentData())
        p=self.panel('黑诞','choice_ro6_normal2_2');self.assertEqual(p.stages.count(),7);self.assertIn('多个作战名称',p.player.toPlainText());p=self.panel('湖中仙女');self.assertEqual(p.choices.count(),2)
    def test_reverse_stage_excludes_false_emergency_link_and_preserves_own_stage_filter(self):
        for sid,count in(('ro6_t_3',1),('ro6_e_t_3',2)):
            p=CurrentBattlePanel(sid);p.show();self.addCleanup(p.close);self.assertTrue(p.event_origins_button.isVisible());self.assertTrue(p.open_event_origins());child=p.event_origins_dialog;self.assertEqual(child.panel.stage_id,sid);self.assertEqual(child.panel.choices.count(),count);self.assertTrue(p.refresh_reference());self.assertTrue(child.isVisible());p.close();self.assertFalse(child.isVisible())
    def test_two_nonzero_readers_stage_and_nested_owned_reader_keep_refresh(self):
        p=self.panel('鸭托邦','choice_ro6_bat3_3');p.resize(850,450);p.stages.setCurrentIndex(p.stages.findData('ro6_t_3'));p.open_battle();child=p.battle_dialog;child.panel.open_event_origins();grandchild=child.panel.event_origins_dialog
        for reader in(p.player,p.technical):
            p.tabs.setCurrentWidget(reader);self.qt.processEvents();c=reader.textCursor();c.setPosition(3);c.setPosition(15,QTextCursor.MoveMode.KeepAnchor);reader.setTextCursor(c);bar=reader.verticalScrollBar();self.assertGreater(bar.maximum(),0);bar.setValue(min(4,bar.maximum()));before=(c.anchor(),c.position(),bar.value(),p.tabs.currentIndex(),p.choice_id,p.stages.currentData());self.assertTrue(p.refresh_reference());self.qt.processEvents();c=reader.textCursor();self.assertEqual(before,(c.anchor(),c.position(),bar.value(),p.tabs.currentIndex(),p.choice_id,p.stages.currentData()));self.assertTrue(child.isVisible());self.assertTrue(grandchild.isVisible())
        self.select(p,'choice_ro6_bat3_5');self.assertFalse(child.isVisible());self.assertFalse(grandchild.isVisible())
    def test_actual_source_damage_clear_all_old_children_recovery_manual(self):
        p=self.panel('黑诞','choice_ro6_normal2_2');p.stages.setCurrentIndex(1);p.open_battle();child=p.battle_dialog;child.panel.open_event_origins();grandchild=child.panel.event_origins_dialog
        with TemporaryDirectory()as folder:
            root=Path(folder);clone(root);f=root/model.DATA;raw=f.read_bytes()
            with patch.object(model,'ROOT',root):
                f.write_bytes(raw+b' ');self.assertFalse(p.refresh_reference());self.assertIsNone(p.result);self.assertFalse(child.isVisible());self.assertFalse(grandchild.isVisible());self.assertEqual(p.technical.toPlainText(),'');f.write_bytes(raw);self.assertTrue(p.refresh_reference());self.assertIsNone(p.choice_id);self.assertFalse(p.open_battle())
    def test_optional_event_source_failure_keeps_core_battle_image_and_other_pages(self):
        p=CurrentBattlePanel('ro6_t_3');p.show();self.addCleanup(p.close);p.open_event_origins();child=p.event_origins_dialog;raw=p.summary.toPlainText()
        with patch.object(model,'packet',return_value=None):
            self.assertTrue(p.refresh_reference());self.assertIsNotNone(p.result);self.assertEqual(p.summary.toPlainText(),raw);self.assertFalse(p.event_origins_button.isVisible());self.assertIsNone(child.panel.result);self.assertFalse(p.open_event_origins());self.assertFalse(child.isVisible())
    def test_real_update_scene_context_only_choice_exact_and_parent_lifecycle(self):
        p=ExpansionUpdatePanel();p.show();self.addCleanup(p.close);p.scope.setCurrentIndex(p.scope.findData(False));d=model.packet()['data']
        for cat,key in(('scenes','scene_ro6_normal2_enter'),('choices','choice_ro6_normal2_2'),('choices','choice_ro6_bat3_5')):
            p.category.setCurrentIndex(p.category.findData(cat));i=next(i for i in range(p.entries.count())if p.entries.item(i).data(Qt.ItemDataRole.UserRole)==key);p.entries.setCurrentRow(i);self.assertTrue(p.event_battles_button.isVisible());self.assertTrue(p.open_event_battles());child=p.event_battles_dialog;target=model.locate(cat,key);self.assertEqual(child.panel.event_id,target['event_id']);self.assertEqual(child.panel.choice_id,target['choice_id']);self.assertTrue(p.refresh_reference());self.assertTrue(child.isVisible())
        child.panel.stages.setCurrentIndex(1);child.panel.open_battle();battle=child.panel.battle_dialog;self.assertTrue(p.open_event_battles());self.assertFalse(child.isVisible());self.assertFalse(battle.isVisible());child=p.event_battles_dialog;p._unavailable();self.assertFalse(child.isVisible())

if __name__=='__main__':unittest.main()
