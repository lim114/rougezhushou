from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication
from rouge import current_resource_events as model
from rouge.current_resource_events_view import CurrentResourceEventsPanel
from rouge.expansion_view import ExpansionUpdatePanel
from tests.test_current_resource_events_329 import clone,by_original
class CurrentResourceEventsView329Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])
    def panel(self,title,key=None):
        t=model.locate('choices',key)if key else None;p=CurrentResourceEventsPanel(title,t['scene_id']if t else None,t['choice_id']if t else None);p.resize(850,440);p.show();self.addCleanup(p.close);self.qt.processEvents();return p
    def select(self,p,key):
        for i in range(p.choices.count()):
            if p.choices.item(i).data(Qt.ItemDataRole.UserRole)==key:p.choices.setCurrentRow(i);return
        self.fail('Missing '+key)
    def test_all32_scenes24_actions_gold_control_only_fixed_cost_events(self):
        count=0
        for title in model.packet()['data']['events']:
            p=self.panel(title);self.assertEqual(hasattr(p,'gold'),title in model.GOLD_EVENTS)
            for sid,s in p.result['scenes'].items():
                p.scene.setCurrentIndex(p.scene.findData(sid));self.assertEqual(p.choices.count(),len(s['choice_ids']))
                for key in s['choice_ids']:self.select(p,key);count+=1;self.assertIn(p.result['choices'][key]['title'],p.player.toPlainText());self.assertFalse(p.battle_button.isVisible());self.assertTrue(p.next_button.isEnabled())
        self.assertEqual(count,24)
    def test_fixed_cost_boundaries_disable_only_unpaid_choice_and_preserve_selection(self):
        p=self.panel('敲动杠杆','choice_ro6_res5_2');selected=p.choice_id
        for gold in(-1,0,9,10):
            p.gold.setValue(gold);self.assertEqual(p.choice_id,selected);self.assertEqual(p.next_button.isEnabled(),gold==-1 or gold>=10)
            if gold==9:self.assertFalse(p.follow_scene());self.assertIn('不足以支付',p.player.toPlainText())
        p.gold.setValue(3);self.select(p,by_original(p.result,'choice_ro6_res5_3')['id']);self.assertTrue(p.follow_scene());self.assertEqual(p.scene_id,'scene_ro6_res5_3')
    def test_each_random_part_category_keeps_unknown_pool_and_exact_follow(self):
        p=self.panel('货从口出')
        for n,kind in enumerate(('加工品','概念体','自然物'),1):
            p.go_start();self.select(p,by_original(p.result,'choice_ro6_res3_'+str(n))['id']);self.assertIn('1件'+kind,p.player.toPlainText());p.gold.setValue(3);self.assertFalse(p.follow_scene());p.gold.setValue(4);self.assertTrue(p.follow_scene());self.assertEqual(p.scene_id,'scene_ro6_res3_'+str(n))
    def test_two_nonzero_readers_gold_phase_choice_survive_refresh(self):
        p=self.panel('敲动杠杆','choice_ro6_res5_2');p.gold.setValue(10)
        for reader in(p.player,p.technical):
            p.tabs.setCurrentWidget(reader);self.qt.processEvents();c=reader.textCursor();c.setPosition(3);c.setPosition(16,QTextCursor.MoveMode.KeepAnchor);reader.setTextCursor(c);bar=reader.verticalScrollBar();self.assertGreater(bar.maximum(),0);bar.setValue(min(4,bar.maximum()));before=(c.anchor(),c.position(),bar.value(),p.tabs.currentIndex(),p.scene_id,p.choice_id,p.gold.value());self.assertTrue(p.refresh_reference());self.qt.processEvents();c=reader.textCursor();self.assertEqual(before,(c.anchor(),c.position(),bar.value(),p.tabs.currentIndex(),p.scene_id,p.choice_id,p.gold.value()))
    def test_actual_public_damage_clears_and_recovery_requires_manual_scene(self):
        p=self.panel('货从口出','choice_ro6_res3_1');p.gold.setValue(4)
        with TemporaryDirectory()as folder:
            root=Path(folder);clone(root);f=root/model.DATA;raw=f.read_bytes()
            with patch.object(model,'ROOT',root):
                f.write_bytes(raw+b' ');self.assertFalse(p.refresh_reference());self.assertIsNone(p.result);self.assertEqual(p.technical.toPlainText(),'');f.write_bytes(raw);self.assertTrue(p.refresh_reference());self.assertIsNone(p.scene_id);self.assertIsNone(p.choice_id);self.assertEqual(p.gold.value(),4)
    def test_all56_version_entries_exact_and_parent_refresh_owns_window(self):
        p=ExpansionUpdatePanel();p.show();self.addCleanup(p.close);p.scope.setCurrentIndex(p.scope.findData(False));d=model.packet()['data']
        for cat,keys in(('scenes',d['originals']['scenes']),('choices',d['originals']['choices'])):
            p.category.setCurrentIndex(p.category.findData(cat))
            for key in keys:
                i=next(i for i in range(p.entries.count())if p.entries.item(i).data(Qt.ItemDataRole.UserRole)==key);p.entries.setCurrentRow(i);self.assertTrue(p.flow_button.isVisible());self.assertTrue(p.open_documented_flow());child=p.flow_dialog;t=model.locate(cat,key);self.assertEqual((child.panel.scene_id,child.panel.choice_id),(t['scene_id'],t['choice_id']));self.assertTrue(p.refresh_reference());self.assertTrue(child.isVisible())
        old=child;self.assertTrue(p.open_documented_flow());self.assertFalse(old.isVisible());child=p.flow_dialog;p._unavailable();self.assertFalse(child.isVisible())
if __name__=='__main__':unittest.main()
