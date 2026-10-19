from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication
from rouge import current_sand_reference as model
from rouge.current_sand_view import CurrentSandPanel
from rouge.expansion_view import ExpansionUpdatePanel
from tests.test_current_sand_reference_325 import clone,GOOD
class CurrentSandView325Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])
    def panel(self,event='curiosity',sid=None,cid='choice_ro6_end1_1'):
        p=CurrentSandPanel(event,sid,cid);p.resize(1050,620);p.show();self.addCleanup(p.close);self.qt.processEvents();return p
    def select(self,p,key):
        for i in range(p.choices.count()):
            if p.choices.item(i).data(Qt.ItemDataRole.UserRole)==key:p.choices.setCurrentRow(i);return
        self.fail('Missing '+key)
    def values(self,p,v):
        for key,value in v.items():
            if key=='gold':p.gold.setValue(-1 if value is None else value)
            else:p.controls[key].setCurrentIndex(p.controls[key].findData(value))
    def test_all_document_choices_scenes_and_no_immediate_battle(self):
        for event in('informer','curiosity'):
            p=self.panel(event,cid=None)
            for sid,s in p.result['scenes'].items():
                p.scene.setCurrentIndex(p.scene.findData(sid));self.assertEqual(p.choices.count(),len(s['choice_ids']))
                for cid in s['choice_ids']:
                    self.select(p,cid);self.assertFalse(p.battle_button.isVisible());self.assertFalse(p.open_battle());self.assertIn(p.result['data']['originals']['choices'][cid]['title'],p.player.toPlainText())
    def test_gold_marker_and_history_allow_reading_but_not_unmet_next(self):
        p=self.panel();self.values(p,GOOD);self.assertEqual(p.choice_id,'choice_ro6_end1_1');self.assertTrue(p.next_button.isEnabled());self.values(p,{'gold':49});self.assertFalse(p.next_button.isEnabled());self.assertFalse(p.follow_scene());self.assertIn('已知不符',p.player.toPlainText());self.values(p,{'gold':50,'target_marked':True});self.assertFalse(p.next_button.isEnabled());self.select(p,'choice_ro6_end1_2');self.assertTrue(p.next_button.isEnabled());self.select(p,'choice_ro6_end1_1');self.values(p,{'scope':'history'});self.assertTrue(p.next_button.isEnabled());self.assertTrue(p.follow_scene());self.assertEqual(p.scene_id,'scene_ro6_end1_1');self.assertEqual(p.choices.count(),0)
    def test_related_box_preserves_own_covenant_unknown_and_closes_on_context_change(self):
        p=self.panel();self.assertTrue(p.open_related());child=p.related_dialog;self.assertEqual(child.panel.scene_id,'scene_ro6_end2_enter');self.assertIsNone(child.panel.covenant.currentData());self.assertTrue(p.refresh_reference());self.assertTrue(child.isVisible());self.values(p,{'gold':0});self.assertFalse(child.isVisible());self.assertTrue(p.open_related());child=p.related_dialog
        with patch('rouge.box_event_reference.locate',return_value=None):self.assertFalse(p.open_related());self.assertFalse(child.isVisible());self.assertIsNotNone(p.result)
    def test_same_source_context_and_two_nonzero_readers_kept_on_parent_refresh(self):
        p=self.panel();self.values(p,GOOD);p.resize(950,510);p.open_related();child=p.related_dialog
        for reader in(p.player,p.technical):
            p.tabs.setCurrentWidget(reader);self.qt.processEvents();c=reader.textCursor();c.setPosition(3);c.setPosition(15,QTextCursor.MoveMode.KeepAnchor);reader.setTextCursor(c);bar=reader.verticalScrollBar();self.assertGreater(bar.maximum(),0);bar.setValue(min(4,bar.maximum()));before=(c.anchor(),c.position(),bar.value(),p.tabs.currentIndex(),p.choice_id,p.result['context'])
            self.assertTrue(p.refresh_reference());self.qt.processEvents();c=reader.textCursor();self.assertEqual(before,(c.anchor(),c.position(),bar.value(),p.tabs.currentIndex(),p.choice_id,p.result['context']));self.assertTrue(child.isVisible())
    def test_actual_corruption_clears_and_recovery_manual_no_private_reset(self):
        p=self.panel();p.open_related();child=p.related_dialog
        with TemporaryDirectory()as folder:
            root=Path(folder);clone(root);f=root/model.DATA;raw=f.read_bytes()
            with patch.object(model,'ROOT',root):
                f.write_bytes(raw+b' ');self.assertFalse(p.refresh_reference());self.assertIsNone(p.result);self.assertFalse(child.isVisible());self.assertEqual(p.technical.toPlainText(),'');self.assertFalse(p.related_button.isVisible());f.write_bytes(raw);self.assertTrue(p.refresh_reference());self.assertIsNone(p.scene_id);self.assertIsNone(p.choice_id)
    def test_update_entry_all_seven_five_two_relics_refresh_and_close(self):
        p=ExpansionUpdatePanel();p.show();self.addCleanup(p.close);p.scope.setCurrentIndex(p.scope.findData(False));d=model.packet()['data']
        for cat,keys in(('scenes',d['scenes']),('choices',d['choices']),('relics',['rogue_6_relic_final_1','rogue_6_relic_final_2'])):
            p.category.setCurrentIndex(p.category.findData(cat))
            for key in keys:
                i=next(i for i in range(p.entries.count())if p.entries.item(i).data(Qt.ItemDataRole.UserRole)==key);p.entries.setCurrentRow(i);self.assertTrue(p.flow_button.isVisible());self.assertTrue(p.open_documented_flow());child=p.flow_dialog;target=model.locate(cat,key);self.assertEqual(child.panel.scene_id,target['scene_id']);self.assertEqual(child.panel.choice_id,target['choice_id']);self.assertIsNone(child.panel.result['context']['has_alpha']);self.assertTrue(p.refresh_reference());self.assertTrue(child.isVisible())
        child.panel.open_related();box=child.panel.related_dialog;self.assertTrue(p.open_documented_flow());self.assertFalse(child.isVisible());self.assertFalse(box.isVisible());child=p.flow_dialog;p.close();self.assertFalse(child.isVisible())

if __name__=='__main__':unittest.main()
