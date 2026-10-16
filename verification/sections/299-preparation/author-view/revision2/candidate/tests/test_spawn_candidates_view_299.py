"""Real source-backed299 dialog contracts; prepared without executing Qt/tests."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication
from rouge import spawn_candidates as model
from rouge.spawn_candidates_view import SpawnCandidatesPanel

ROOT=Path(__file__).resolve().parents[1]

class SpawnCandidatesView299Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])
 def setUp(self):
  self.panel=SpawnCandidatesPanel();self.panel.show();self.panel.set_reference('ro6_n_2_1',scope_key='public299');self.qt.processEvents()
 def tearDown(self):self.panel.close();self.panel.deleteLater();self.qt.processEvents()
 def choose(self,control,value):
  at=control.findData(value);self.assertGreaterEqual(at,0);control.setCurrentIndex(at);self.qt.processEvents()
 def select(self,stage,action,kind='group',origin=None):
  self.panel.set_reference(stage,origin,scope_key='public299');self.choose(self.panel.relation_kind,kind)
  relations=self.panel.packet['groups'if kind=='group'else'packages']
  relation=next(r for r in relations if any(m['action_id']==action for m in r['members']))
  self.choose(self.panel.relation,relation['reference_id']);member=next(m for m in relation['members']if m['action_id']==action)
  self.choose(self.panel.member,member['reference_id']);return self.panel._selected()
 def cleared(self):
  self.assertIsNone(self.panel.packet);self.assertIsNone(self.panel._view_key);self.assertIsNone(self.panel._manual_identity)
  self.assertEqual(self.panel.relation.currentIndex(),-1);self.assertEqual(self.panel.member.currentIndex(),-1)
  self.assertEqual(self.panel.picture.key,(None,None,''));self.assertTrue(self.panel.picture.isHidden());self.assertFalse(self.panel.open_spawn_button.isEnabled())
 def test_default_has_independent_relation_branches_and_no_selected_member_or_jump(self):
  self.assertEqual([self.panel.relation_kind.itemData(i)for i in range(self.panel.relation_kind.count())],['group','package'])
  self.assertEqual(self.panel.relation.currentIndex(),-1);self.assertEqual(self.panel.member.currentIndex(),-1)
  self.assertIsNone(self.panel._manual_identity);self.assertFalse(self.panel.open_spawn_button.isEnabled())
  self.assertTrue(self.panel.picture.isHidden());self.assertIn('尚未选择具体记录',self.panel.player_text.toPlainText())
  self.assertIsNone(self.panel.packet['actual_selection']);self.assertIsNone(self.panel.packet['probabilities'])
 def test_complete_same_queue_group_keeps_all_four_spawn_and_empty_source_members(self):
  relation,member=self.select('ro6_n_1_1','w3.f1.a1')
  self.assertEqual(relation['queue_id'],'w3.f1');self.assertEqual(relation['group_key'],'c1')
  self.assertEqual([m['action_id']for m in relation['members']],[f'w3.f1.a{i}'for i in range(1,6)])
  self.assertEqual([m['action_type']for m in relation['members']],['SPAWN']*4+['EMPTY'])
  self.assertEqual(self.panel.member.count(),5);self.assertIsInstance(self.panel.member.currentData(),str)
  self.assertEqual(member['action_id'],'w3.f1.a1');self.assertIn('不是实际敌人数',self.panel.player_text.toPlainText())
 def test_package_retains_member_without_group_and_does_not_claim_simultaneous_generation(self):
  relation,member=self.select('ro6_n_1_4','w1.f3.a5','package')
  self.assertEqual(relation['kind'],'package');self.assertEqual(relation['package_key'],'s')
  self.assertEqual([m['action_id']for m in relation['members']],['w1.f3.a4','w1.f3.a5'])
  self.assertIsNone(member['raw_action']['randomSpawnGroupKey']);self.assertIn('不能据此断定它们同时出场',self.panel.player_text.toPlainText())
  self.assertIn('randomSpawnGroupPackKey',self.panel.source_text.toPlainText())
  self.choose(self.panel.relation_kind,'group');self.assertIsNone(self.panel.relation.currentData());self.assertIsNone(self.panel.member.currentData())
 def test_empty_action_and_empty_activation_key_are_distinct_and_neither_has_enemy_picture(self):
  _,empty=self.select('ro6_n_1_1','w3.f1.a5');self.assertEqual(empty['action_type'],'EMPTY')
  self.assertIn('这是空白候选记录，未列出要生成的敌人或激活的物件',self.panel.player_text.toPlainText())
  self.assertIn('不能据此认为本局没有敌人',self.panel.player_text.toPlainText());self.assertFalse(self.panel.open_spawn_button.isEnabled())
  self.assertNotIn('不生成敌人',self.panel.player_text.toPlainText())
  self.assertTrue(self.panel.picture.isHidden())
  _,activate=self.select('ro6_n_1_1','w1.f1.a1');self.assertEqual(activate['action_type'],'ACTIVATE_PREDEFINED')
  self.assertEqual(activate['predefined_reference']['status'],'empty_key')
  self.assertIn('原记录没有指定激活目标',self.panel.player_text.toPlainText());self.assertNotIn('这是空动作记录',self.panel.player_text.toPlainText())
  self.assertFalse(self.panel.open_spawn_button.isEnabled());self.assertEqual(self.panel.picture.key,(None,None,''))
 def test_exact_predefined_alias_uses_scene_object_reference_without_borrowed_enemy_jump(self):
  _,member=self.select('ro6_n_1_1','w1.f1.a2');reference=member['predefined_reference']
  self.assertEqual(reference['status'],'exact_alias');self.assertEqual(reference['alias'],'trap_321_shnbox#1')
  self.assertFalse(reference['position_is_actual']);self.assertEqual(reference['objects'][0]['entity_id'],'trap_321_shnbox')
  self.assertIn('恶笼草',self.panel.player_text.toPlainText());self.assertIn('场景物件',self.panel.player_text.toPlainText())
  self.assertIn('trap_321_shnbox#1',self.panel.source_text.toPlainText());self.assertIn('raw_action',self.panel.source_text.toPlainText())
  self.assertTrue(self.panel.picture.isHidden());self.assertFalse(self.panel.open_spawn_button.isEnabled());self.assertIsNone(member['spawn_reference'])
 def test_verified_enemy_picture_and_manual_jump_use_the_exact_other_candidate_token(self):
  relation,member=self.select('ro6_n_2_1','w1.f4.a8',origin='w1.f4.a1');events=[]
  self.panel.spawnReferenceSelected.connect(events.append)
  self.assertEqual(member['enemy_references'][0]['source_role'],'fixed_stage_enemy_reference')
  self.assertEqual(self.panel.picture.key[0:2],('enemy','enemy_1352_eslime'));self.assertTrue(self.panel.picture.isVisible())
  self.assertTrue(self.panel.open_spawn_button.isEnabled());self.assertTrue(self.panel.open_selected_spawn())
  self.assertEqual(events,[member['token']]);self.assertEqual(events[0]['origin_action_id'],'w1.f4.a1')
  self.assertEqual(events[0]['action_id'],'w1.f4.a8');self.assertEqual(events[0]['relation_id'],relation['reference_id'])
  self.assertIsNone(model.resolve_reference(events[0])['actual_selection'])
 def test_tampered_local_token_is_freshly_rejected_clears_old_picture_and_emits_no_jump(self):
  self.select('ro6_n_2_1','w1.f4.a8',origin='w1.f4.a1');events=[];invalid=[]
  self.panel.spawnReferenceSelected.connect(events.append);self.panel.sourceInvalidated.connect(lambda:invalid.append(True))
  self.panel._selected()[1]['token']['unexpected']='must reject'
  self.assertFalse(self.panel.open_selected_spawn());self.assertEqual(events,[]);self.assertTrue(invalid);self.cleared()
 def test_group_or_member_change_clears_prior_manual_identity_without_invalidating_source(self):
  self.select('ro6_n_2_1','w1.f4.a8');signals=[];self.panel.sourceInvalidated.connect(lambda:signals.append(True))
  self.choose(self.panel.relation_kind,'package');self.assertIsNone(self.panel.member.currentData());self.assertIsNone(self.panel._manual_identity)
  self.assertTrue(self.panel.picture.isHidden());self.assertEqual(signals,[])
 def test_branch_action_cannot_fall_back_to_full_main_queue_or_reuse_main_named_group(self):
  self.select('ro6_n_1_1','w3.f1.a1');self.panel.set_reference('ro6_n_1_1','branch:shsbox2.p1.a1',scope_key='public299')
  self.cleared();self.assertFalse(self.panel.open_selected_spawn())
 def test_same_scope_refresh_preserves_manual_ids_tab_real_scroll_and_text_selection_without_invalidation(self):
  self.select('ro6_n_2_1','w1.f4.a8',origin='w1.f4.a1');self.panel.reading_tabs.setCurrentWidget(self.panel.source_text);self.qt.processEvents()
  widget=self.panel.source_text;cursor=widget.textCursor();cursor.setPosition(5);cursor.setPosition(20,QTextCursor.MoveMode.KeepAnchor);widget.setTextCursor(cursor)
  bar=widget.verticalScrollBar();self.assertGreater(bar.maximum(),0);bar.setValue(max(1,bar.maximum()//2))
  def state():
   c=widget.textCursor();return(self.panel.relation_kind.currentData(),self.panel.relation.currentData(),self.panel.member.currentData(),
    deepcopy(self.panel._manual_identity),self.panel.reading_tabs.currentIndex(),widget.toPlainText(),c.anchor(),c.position(),c.selectedText(),bar.value(),self.panel.picture.key)
  saved=state();self.assertTrue(saved[-3]);self.assertGreater(saved[-2],0);signals=[];self.panel.sourceInvalidated.connect(lambda:signals.append(True))
  for _ in range(3):self.panel.refresh_reference();self.qt.processEvents();self.assertEqual(state(),saved)
  self.panel.set_reference('ro6_n_2_1','w1.f4.a1',scope_key='public299');self.qt.processEvents();self.assertEqual(state(),saved);self.assertEqual(signals,[])
 def test_changed_parent_scope_or_stage_clears_choices_and_picture_and_requests_child_cleanup(self):
  self.select('ro6_n_2_1','w1.f4.a8');signals=[];self.panel.sourceInvalidated.connect(lambda:signals.append(True))
  self.panel.set_reference('ro6_n_2_1',scope_key='different-public299');self.assertTrue(signals)
  self.assertEqual(self.panel.relation.currentIndex(),-1);self.assertEqual(self.panel.member.currentIndex(),-1);self.assertIsNone(self.panel._manual_identity)
  self.assertTrue(self.panel.picture.isHidden());self.panel.set_reference(None);self.cleared()
 def test_real_warm_manifest_and_level_failures_clear_both_readers_and_restore_unselected(self):
  self.select('ro6_n_2_1','w1.f4.a8');packet=deepcopy(self.panel.packet);manifest=json.loads((ROOT/model.MANIFEST).read_bytes())
  with tempfile.TemporaryDirectory(prefix='rouge299-public-source-')as directory:
   clone=Path(directory)
   for name in set(manifest['files'])|{model.MANIFEST}:
    original=ROOT/name;self.assertTrue(original.is_file());self.assertFalse(original.is_symlink());self.assertTrue(original.resolve().is_relative_to(ROOT.resolve()))
    target=clone/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(original.read_bytes())
   with patch.object(model,'ROOT',clone):
    for name in(model.MANIFEST,packet['source_file']):
     with self.subTest(damaged=name):
      self.select('ro6_n_2_1','w1.f4.a8');self.assertTrue(self.panel.packet['source_valid'])
      target=clone/name;raw=target.read_bytes()
      try:
       target.write_bytes(raw+b' ');self.panel.refresh_reference();self.qt.processEvents();self.cleared()
       self.assertTrue(all('已清除'in reader.toPlainText()for reader in(self.panel.player_text,self.panel.source_text)))
      finally:target.write_bytes(raw)
      self.assertEqual(target.read_bytes(),raw);self.panel.refresh_reference();self.qt.processEvents()
      self.assertTrue(self.panel.packet['source_valid']);self.assertIsNone(self.panel.relation.currentData());self.assertIsNone(self.panel.member.currentData())
      self.assertTrue(self.panel.picture.isHidden());self.assertFalse(self.panel.open_spawn_button.isEnabled())

if __name__=='__main__':unittest.main()
