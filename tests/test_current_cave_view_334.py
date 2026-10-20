from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication
from rouge import current_cave as model
from rouge.current_cave_view import CurrentCaveDialog
from rouge.expansion_view import ExpansionUpdatePanel
from rouge.node_catalog_view import NodeCatalogPanel
from tests.test_current_cave_334 import clone
class CurrentCaveView334Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])
 def dialog(self,target=None):
  d=CurrentCaveDialog(target);d.show();self.addCleanup(d.close);self.qt.processEvents();return d
 def pick(self,p,role,scene=None):
  sid=scene or p.result['choices']['cave-choice:'+role]['scene_ids'][0];p.scene.setCurrentIndex(p.scene.findData(sid));p.choices.setCurrentRow(next(i for i in range(p.choices.count())if p.choices.item(i).data(Qt.ItemDataRole.UserRole)=='cave-choice:'+role));return model.choice_reference(p.result,p.scene_id,p.choice_id)
 def test_four_separate_results_none_default_cannot_jump_unlisted_or_recommend(self):
  p=self.dialog().panel;self.pick(p,'dig');self.assertFalse(p.follow_scene());self.assertEqual(sum(b.isVisible()for b in p.outcome_buttons),4);self.assertFalse(p.open_documented_outcome('cave-scene:end'))
  for role in('crow','squirrel','empty','danger'):
   self.pick(p,'dig');self.assertTrue(p.open_documented_outcome('cave-scene:'+role));self.assertEqual(p.scene_id,'cave-scene:'+role);self.assertIsNone(p.result['actual_outcome'])
  self.pick(p,'again','cave-scene:low_empty');self.assertEqual(sum(b.isVisible()for b in p.outcome_buttons),4);self.assertFalse(p.follow_scene())
 def test_two_followup_choices_source_specific_targets_no_guessed_max_or_fake_map(self):
  p=self.dialog().panel
  for role,low in[('gold','low_gold'),('empty','low_empty')]:
   self.pick(p,role);self.assertFalse(p.follow_scene());self.assertEqual(sum(b.isVisible()for b in p.followup_buttons),2);self.assertTrue(p.open_reference_followup('cave-scene:'+low));self.pick(p,role);self.assertTrue(p.open_reference_followup('cave-scene:end'))
  for key,sid in[('choice_ro6_bat6_3','cave-scene:low_gold'),('choice_ro6_bat6_19','cave-scene:end')]:
   p=self.dialog(model.locate('choices',key)).panel;self.assertEqual(p.source_request['key'],key);self.assertEqual(sum(b.isVisible()for b in p.followup_buttons),0);self.assertTrue(p.follow_scene());self.assertEqual(p.scene_id,sid)
  self.pick(p,'battle');self.assertTrue(p.battle_button.isVisible());self.assertFalse(p.battle_button.isEnabled());self.assertFalse(p.open_battle());self.assertIsNone(p.battle_dialog)
 def test_shared_original_scene_or_again_choice_requires_phase_then_keeps_source(self):
  for category,key in[('scenes','scene_ro6_bat6_6'),('choices','choice_ro6_bat6_7')]:
   p=self.dialog(model.locate(category,key)).panel;self.assertIsNone(p.scene_id);self.assertIn('请先选择',p.player.toPlainText());p.scene.setCurrentIndex(p.scene.findData('cave-scene:low_empty'));self.assertEqual(p.source_request['key'],key)
   if category=='choices':self.assertEqual(p.choice_id,'cave-choice:again')
 def test_parent_refresh_keeps_two_real_nonzero_readers_source_and_phase(self):
  d=self.dialog(model.locate('choices','choice_ro6_bat6_3'));d.resize(850,440);p=d.panel
  for reader in(p.player,p.technical):
   p.tabs.setCurrentWidget(reader);self.qt.processEvents();c=reader.textCursor();c.setPosition(3);c.setPosition(16,QTextCursor.MoveMode.KeepAnchor);reader.setTextCursor(c);bar=reader.verticalScrollBar();self.assertGreater(bar.maximum(),0);bar.setValue(min(4,bar.maximum()));prior=(c.anchor(),c.position(),bar.value(),p.tabs.currentIndex(),p.scene_id,p.choice_id,p.source_request.copy());self.assertTrue(p.refresh_reference());c=reader.textCursor();self.assertEqual(prior,(c.anchor(),c.position(),bar.value(),p.tabs.currentIndex(),p.scene_id,p.choice_id,p.source_request))
 def test_version_and_catalogue_entries_repeat_open_source_loss_and_no_irrelevant_inputs(self):
  p=ExpansionUpdatePanel();p.show();self.addCleanup(p.close);p.scope.setCurrentIndex(p.scope.findData(False));p.category.setCurrentIndex(p.category.findData('choices'))
  for key in('choice_ro6_bat6_3','choice_ro6_bat6_19','choice_ro6_bat6_7'):
   p.entries.setCurrentRow(next(i for i in range(p.entries.count())if p.entries.item(i).data(Qt.ItemDataRole.UserRole)==key));self.assertTrue(p.flow_button.isVisible());self.assertTrue(p.open_documented_flow());self.assertEqual(p.flow_dialog.panel.source_request,{'category':'choices','key':key})
  old=p.flow_dialog;p.open_documented_flow();self.assertFalse(old.isVisible());p._unavailable();self.assertFalse(p.flow_dialog.isVisible())
  n=NodeCatalogPanel();n.show();self.addCleanup(n.close);n.list.setCurrentRow(next(i for i,e in enumerate(n.entries)if e['key']=='event:community_group_017'));self.assertTrue(n.open_current_event_reference());d=n.current_reference_window;r=d.panel;self.assertIsNone(r.source_request);self.assertIsNone(r.choice_id);self.assertFalse(any(hasattr(r,k)for k in('gold','controller','seeds','fossil')));n.refresh();self.assertTrue(d.isVisible());n.close();self.assertFalse(d.isVisible())
 def test_actual_source_damage_clears_old_source_and_manual_recovery(self):
  p=self.dialog(model.locate('choices','choice_ro6_bat6_3')).panel
  with TemporaryDirectory()as folder:
   root=Path(folder);clone(root);f=root/model.DATA;raw=f.read_bytes()
   with patch.object(model,'ROOT',root):
    f.write_bytes(raw+b' ');self.assertFalse(p.refresh_reference());self.assertIsNone(p.result);self.assertIsNone(p.source_request);self.assertEqual(p.technical.toPlainText(),'');self.assertFalse(any(b.isVisible()for b in p.outcome_buttons+p.followup_buttons));f.write_bytes(raw);self.assertTrue(p.refresh_reference());self.assertIsNone(p.scene_id);self.assertIsNone(p.choice_id);self.assertIsNone(p.source_request)
if __name__=='__main__':unittest.main()
