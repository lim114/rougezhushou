from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication
from rouge import current_rest_travel as model
from rouge.current_rest_travel_view import CurrentRestTravelPanel
from rouge.expansion_view import ExpansionUpdatePanel
from tests.test_current_rest_travel_331 import clone,by_original
class CurrentRestTravelView331Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])
    def panel(self,title,key=None):
        t=model.locate('choices',key)if key else None;p=CurrentRestTravelPanel(title,t);p.resize(850,440);p.show();self.addCleanup(p.close);self.qt.processEvents();return p
    def select(self,p,key):
        for i in range(p.choices.count()):
            if p.choices.item(i).data(Qt.ItemDataRole.UserRole)==key:p.choices.setCurrentRow(i);return
        self.fail('Missing '+key)
    def test_all11_document_scenes10_choice_groups_no_resource_inputs_or_false_battle(self):
        count=0
        for title in('金色凝滞','三重身'):
            p=self.panel(title);self.assertFalse(hasattr(p,'gold'));self.assertFalse(hasattr(p,'fossil'))
            for sid,s in p.result['scenes'].items():
                p.scene.setCurrentIndex(p.scene.findData(sid));self.assertEqual(p.choices.count(),len(s['choice_ids']))
                for key in s['choice_ids']:self.select(p,key);count+=1;self.assertIn(p.result['choices'][key]['title'],p.player.toPlainText());self.assertFalse(p.battle_button.isVisible())
        self.assertEqual(count,10)
    def test_rest_all_seven_reference_choices_notice_preserved_exact_followups(self):
        p=self.panel('金色凝滞')
        for n in range(1,8):
            p.go_start();c=by_original(p.result,'choice_ro6_rest_'+str(n));self.select(p,c['id']);self.assertIn('原注写“随机3个”',p.player.toPlainText());self.assertIsNone(p.result['actual_menu']);self.assertTrue(p.follow_scene());self.assertEqual(p.scene_id,c['next_scene_id']);self.assertEqual(p.choices.count(),0)
    def test_triple_accept_is_prose_not_zone_end_decline_has_exact_exit_never_moves(self):
        p=self.panel('三重身','choice_ro6_evacuate3_3');self.assertEqual(p.result['source_request']['key'],'choice_ro6_evacuate3_3');self.assertIn('展示标记不能证明额外生命奖励',p.player.toPlainText());self.assertTrue(p.follow_scene());self.assertEqual(p.choices.count(),0);self.assertFalse(p.follow_scene());p.go_start();self.select(p,by_original(p.result,'choice_ro6_evacuate_2')['id']);self.assertTrue(p.follow_scene());exit=by_original(p.result,'choice_ro6_evacuate_4');self.select(p,exit['id']);self.assertFalse(p.next_button.isEnabled());self.assertFalse(p.follow_scene());self.assertIsNone(p.result['actual_departed'])
    def test_two_nonzero_readers_keep_source_scene_and_option_refresh(self):
        p=self.panel('三重身','choice_ro6_evacuate3_3')
        for reader in(p.player,p.technical):
            p.tabs.setCurrentWidget(reader);self.qt.processEvents();c=reader.textCursor();c.setPosition(3);c.setPosition(16,QTextCursor.MoveMode.KeepAnchor);reader.setTextCursor(c);bar=reader.verticalScrollBar();self.assertGreater(bar.maximum(),0);bar.setValue(min(4,bar.maximum()));before=(c.anchor(),c.position(),bar.value(),p.tabs.currentIndex(),p.scene_id,p.choice_id,p.source_request);self.assertTrue(p.refresh_reference());self.qt.processEvents();c=reader.textCursor();self.assertEqual(before,(c.anchor(),c.position(),bar.value(),p.tabs.currentIndex(),p.scene_id,p.choice_id,p.source_request))
    def test_actual_public_damage_clears_source_and_requires_manual_recovery(self):
        p=self.panel('金色凝滞','choice_ro6_rest_7')
        with TemporaryDirectory()as folder:
            root=Path(folder);clone(root);f=root/model.DATA;raw=f.read_bytes()
            with patch.object(model,'ROOT',root):
                f.write_bytes(raw+b' ');self.assertFalse(p.refresh_reference());self.assertIsNone(p.result);self.assertEqual(p.technical.toPlainText(),'');f.write_bytes(raw);self.assertTrue(p.refresh_reference());self.assertIsNone(p.scene_id);self.assertIsNone(p.choice_id);self.assertIsNone(p.source_request)
    def test_all36_version_entries_keep_original_request_and_parent_owned_refresh_close(self):
        p=ExpansionUpdatePanel();p.show();self.addCleanup(p.close);p.scope.setCurrentIndex(p.scope.findData(False));d=model.packet()['data']
        for cat,keys in(('scenes',d['originals']['scenes']),('choices',d['originals']['choices'])):
            p.category.setCurrentIndex(p.category.findData(cat))
            for key in keys:
                i=next(i for i in range(p.entries.count())if p.entries.item(i).data(Qt.ItemDataRole.UserRole)==key);p.entries.setCurrentRow(i);self.assertTrue(p.flow_button.isVisible());self.assertTrue(p.open_documented_flow());child=p.flow_dialog;t=model.locate(cat,key);self.assertEqual((child.panel.scene_id,child.panel.choice_id,child.panel.source_request),(t['scene_id'],t['choice_id'],t['source_request']));self.assertTrue(p.refresh_reference());self.assertTrue(child.isVisible())
        old=child;p.open_documented_flow();self.assertFalse(old.isVisible());child=p.flow_dialog;p._unavailable();self.assertFalse(child.isVisible())
if __name__=='__main__':unittest.main()
