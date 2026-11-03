from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication
from rouge import current_unattended_shop as model
from rouge.current_unattended_shop_view import CurrentUnattendedShopPanel
from rouge.expansion_view import ExpansionUpdatePanel
from tests.test_current_unattended_shop_330 import clone,by_original
class CurrentUnattendedShopView330Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])
    def panel(self,n=None):
        p=CurrentUnattendedShopPanel(model.locate('choices','choice_ro6_wish_'+str(n))if n else None);p.resize(850,440);p.show();self.addCleanup(p.close);self.qt.processEvents();return p
    def select(self,p,key):
        for i in range(p.choices.count()):
            if p.choices.item(i).data(Qt.ItemDataRole.UserRole)==key:p.choices.setCurrentRow(i);return
        self.fail('Missing '+key)
    def test_four_scenes_four_groups_only_entry_has_actions_no_false_battle(self):
        p=self.panel();count=0
        for sid,s in p.result['scenes'].items():
            p.scene.setCurrentIndex(p.scene.findData(sid));self.assertEqual(p.choices.count(),len(s['choice_ids']))
            for key in s['choice_ids']:self.select(p,key);count+=1;self.assertIn(p.result['choices'][key]['title'],p.player.toPlainText());self.assertFalse(p.battle_button.isVisible())
        self.assertEqual(count,4)
    def test_two_same_text_followups_manual_no_default_and_3_4_gold_boundaries(self):
        p=self.panel(8);self.assertEqual(p.result['requested_original_id'],'choice_ro6_wish_8');self.assertIsNone(p.result['actual_variant']);self.assertFalse(p.follow_scene());self.assertFalse(p.next_button.isEnabled());self.assertTrue(all(b.isVisible()for b in p.followup_buttons));self.assertFalse(p.open_documented_followup('scene_ro6_wish_1'));p.gold.setValue(3);self.assertFalse(any(b.isEnabled()for b in p.followup_buttons));self.assertFalse(p.open_documented_followup('scene_ro6_wish_3'));p.gold.setValue(4)
        for sid in('scene_ro6_wish_2','scene_ro6_wish_3'):
            p.go_start();self.select(p,by_original(p.result,3)['id']);self.assertTrue(p.open_documented_followup(sid));self.assertEqual(p.scene_id,sid);self.assertEqual(p.choices.count(),0);self.assertFalse(any(b.isVisible()for b in p.followup_buttons));self.assertIsNone(p.result['actual_upgrade'])
    def test_fossil_unknown_false_true_gates_only_held_option_gold_not_affect_it(self):
        p=self.panel(6);selected=p.choice_id;p.gold.setValue(0)
        for held in(None,False,True):
            p.fossil.setCurrentIndex(p.fossil.findData(held));self.assertEqual(p.choice_id,selected);self.assertEqual(p.next_button.isEnabled(),held is not False)
            if held is False:self.assertFalse(p.follow_scene())
        p.fossil.setCurrentIndex(p.fossil.findData(False));self.select(p,by_original(p.result,2)['id']);self.assertTrue(p.next_button.isEnabled());self.assertTrue(p.follow_scene());self.assertEqual(p.scene_id,'scene_ro6_wish_1')
    def test_two_nonzero_readers_keep_fossil_gold_requested_record_and_choice(self):
        p=self.panel(3);p.gold.setValue(4);p.fossil.setCurrentIndex(p.fossil.findData(True))
        for reader in(p.player,p.technical):
            p.tabs.setCurrentWidget(reader);self.qt.processEvents();c=reader.textCursor();c.setPosition(3);c.setPosition(16,QTextCursor.MoveMode.KeepAnchor);reader.setTextCursor(c);bar=reader.verticalScrollBar();self.assertGreater(bar.maximum(),0);bar.setValue(min(4,bar.maximum()));before=(c.anchor(),c.position(),bar.value(),p.tabs.currentIndex(),p.scene_id,p.choice_id,p.gold.value(),p.fossil.currentData(),p.result['requested_original_id']);self.assertTrue(p.refresh_reference());self.qt.processEvents();c=reader.textCursor();self.assertEqual(before,(c.anchor(),c.position(),bar.value(),p.tabs.currentIndex(),p.scene_id,p.choice_id,p.gold.value(),p.fossil.currentData(),p.result['requested_original_id']))
    def test_actual_damage_clears_followups_requested_record_manual_recovery(self):
        p=self.panel(8);p.gold.setValue(4)
        with TemporaryDirectory()as folder:
            root=Path(folder);clone(root);f=root/model.DATA;raw=f.read_bytes()
            with patch.object(model,'ROOT',root):
                f.write_bytes(raw+b' ');self.assertFalse(p.refresh_reference());self.assertIsNone(p.result);self.assertEqual(p.technical.toPlainText(),'');self.assertFalse(any(b.isVisible()for b in p.followup_buttons));f.write_bytes(raw);self.assertTrue(p.refresh_reference());self.assertIsNone(p.scene_id);self.assertIsNone(p.choice_id);self.assertIsNone(p.result['requested_original_id']);self.assertEqual(p.gold.value(),4)
    def test_all15_version_entries_requested_source_kept_refresh_and_owned_close(self):
        p=ExpansionUpdatePanel();p.show();self.addCleanup(p.close);p.scope.setCurrentIndex(p.scope.findData(False));r=model.reference()
        for cat,keys in(('scenes',r['scenes']),('choices',r['data']['originals']['choices'])):
            p.category.setCurrentIndex(p.category.findData(cat))
            for key in keys:
                i=next(i for i in range(p.entries.count())if p.entries.item(i).data(Qt.ItemDataRole.UserRole)==key);p.entries.setCurrentRow(i);self.assertTrue(p.flow_button.isVisible());self.assertTrue(p.open_documented_flow());child=p.flow_dialog;t=model.locate(cat,key);self.assertEqual((child.panel.scene_id,child.panel.choice_id,child.panel.result['requested_original_id']),(t['scene_id'],t['choice_id'],t['original_choice_id']));self.assertTrue(p.refresh_reference());self.assertTrue(child.isVisible())
        old=child;p.open_documented_flow();self.assertFalse(old.isVisible());child=p.flow_dialog;p._unavailable();self.assertFalse(child.isVisible())
if __name__=='__main__':unittest.main()
