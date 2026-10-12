"""Four exact auxiliary identities, per-stage declarations, real preview entry."""
import copy,hashlib,json,unittest
from unittest.mock import patch
from rouge.battle_preview import battle_data,enemy_preview,enemy_text,DATA
from rouge.enemy_panel import enemy_panel_reference
from rouge.auxiliary_enemy_mechanisms import reference_for,reference_text,reference_data
from scripts.build_auxiliary_enemy_mechanisms import build,BASE,OUTPUT
CASES=(('ro6_b_1','enemy_2156_shsmok'),('ro6_b_1_b','enemy_2156_shsmok'),('ro6_t_4','enemy_2156_shsmok'),('ro6_e_t_4','enemy_2156_shsmok'),('ro6_b_3','enemy_2154_shdfb'),('ro6_b_3_b','enemy_2154_shdfb'),('ro6_b_4_b','enemy_1177_dufrbl_2'),('ro6_duel_2','enemy_2121_dyspl2'))
class AuxiliarySourceTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.output,cls.receipt=build()
 def test_four_unique_typed_native_graphs_and_eight_exact_fixed_references(self):
  self.assertEqual(reference_data(),self.output);self.assertEqual((self.receipt['profiles'],self.receipt['stage_bindings'],self.receipt['enemy_stage_references']),(4,8,8))
  for sid,eid in CASES:
   r=reference_for(sid,eid,0);self.assertIsNotNone(r);self.assertEqual(r['profile']['enemy_id'],eid)
   self.assertTrue(r['profile']['native_prefab']['selected_graph_exact']);self.assertTrue(r['profile']['native_prefab']['components'])
   self.assertFalse(r['full_current_mechanics_verified']);self.assertFalse(r['parameters_applied_to_prediction'])
   for key in ('actual_instance_present','actual_target','exact_first_tick','exact_end_time','complete_effective_values'):self.assertIsNone(r[key])
  self.assertEqual(self.receipt['independent_constructor_refs'],1)
 def test_explicit_prefabkey_preserves_derived_identity_without_suffix_or_name_guess(self):
  r=reference_for('ro6_b_4_b','enemy_1177_dufrbl_2',0);self.assertEqual(r['profile']['database_prefab_key'],'enemy_1177_dufrbl')
  self.assertEqual(r['binding']['enemy_id'],'enemy_1177_dufrbl_2');self.assertTrue(r['profile']['documentation']['shared_prefab_document_only'])
  self.assertFalse(r['profile']['documentation']['document_numeric_defaults_inherited'])
  self.assertIsNone(reference_for('ro6_b_4_b','enemy_1177_dufrbl',0))
 def test_fire_independent_constructor_keeps_six_fivehundred_and_never_inherits_default(self):
  first=reference_for('ro6_b_3','enemy_2154_shdfb',0);other=reference_for('ro6_b_3_b','enemy_2154_shdfb',0)
  params=lambda r:{v['key']:v['value'] for v in r['binding']['declared_talent_blackboard']}
  self.assertEqual(first['binding']['source_constructor_mode'],'database');self.assertEqual(other['binding']['source_constructor_mode'],'stage_constructor')
  self.assertEqual((params(first)['Passive.duration'],params(first)['DamageAura.value'],params(first)['DamageAura.circle']),(10,1000,2))
  self.assertEqual((params(other)['Passive.duration'],params(other)['DamageAura.value'],params(other)['DamageAura.circle']),(6,500,1.5))
  self.assertEqual(other['binding']['original_reference']['useDb'],False)
  self.assertIn('独立构造',reference_text(other));self.assertNotIn('10秒',reference_text(other))
 def test_source_guards_refuse_unknown_grade_stage_mode_source_and_prefab(self):
  sid,eid=CASES[0];r=enemy_panel_reference(sid,eid,0)
  for grade in (1,True,-1,0.0,None):self.assertIsNone(reference_for(sid,eid,grade))
  self.assertIsNone(reference_for('similar-stage',eid,0));self.assertIsNone(reference_for(sid,'similar-enemy',0))
  for kind in ('mode','source','grade','stage'):
   bad=copy.deepcopy(r)
   if kind=='mode':bad['construction_reference']['mode']='stage_constructor'
   elif kind=='source':bad['source']['stage']['sha256']='changed'
   elif kind=='grade':bad['requested_level']=1
   else:bad['stage_id']='another'
   self.assertIsNone(reference_for(sid,eid,0,bad),kind)
  bad=copy.deepcopy(self.output);bad['bindings'][sid][eid+'@0']['prefab_key']='different'
  with patch('rouge.auxiliary_enemy_mechanisms.reference_data',return_value=bad):self.assertIsNone(reference_for(sid,eid,0,r))
 def test_api_copies_are_independent_and_plain_view_hides_technical_parameters(self):
  sid,eid=CASES[4];r=reference_for(sid,eid,0);text=reference_text(r);technical=reference_text(r,True)
  self.assertIn('法术伤害和凋亡损伤',text);self.assertIn('此资料不计入预计面板',text);self.assertNotIn('DamageAura.value',text);self.assertNotIn('Torappu.',text)
  self.assertIn('DamageAura.value',technical);self.assertIn('原关卡SHA256',technical)
  r['binding']['declared_talent_blackboard'][0]['value']=999;self.assertNotEqual(reference_for(sid,eid,0)['binding']['declared_talent_blackboard'][0]['value'],999)
 def test_actual_enemy_preview_adds_reference_without_changing_any_numerical_or_existing_field(self):
  for sid,eid in CASES:
   with patch('rouge.auxiliary_enemy_mechanisms.reference_for',return_value=None):prior=enemy_preview(sid,eid,0)
   current=enemy_preview(sid,eid,0);reference=current.pop('auxiliary_mechanism_reference');self.assertEqual(current,prior)
   current['auxiliary_mechanism_reference']=reference;self.assertIn('辅助单位机制参考',enemy_text(current));self.assertNotIn('DamageAura.value',enemy_text(current))
  sid='ro6_n_1_1';enemy=battle_data()['stages'][sid]['enemies'][0];ordinary=enemy_preview(sid,enemy['id'],enemy['level'])
  self.assertNotIn('auxiliary_mechanism_reference',ordinary);self.assertNotIn('辅助单位机制参考',enemy_text(ordinary))
 def test_source_rebuild_is_readonly_and_portrait_and_dynamic_mechanisms_stay_unresolved(self):
  paths=[p for p in BASE.iterdir() if p.is_file()]+[OUTPUT];before={p:hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
  self.assertEqual(build(),(self.output,self.receipt));self.assertEqual({p:hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},before)
  for key in ('game_actions','chat_requests','official_portraits_added'):self.assertEqual(self.receipt[key],0)
  self.assertFalse(self.receipt['actual_runtime_mechanics_verified']);self.assertFalse(self.receipt['quantities_applied_to_prediction'])
class AuxiliaryPreviewWidgetTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  from PySide6.QtWidgets import QApplication
  cls.app=QApplication.instance() or QApplication([])
 def test_all_eight_fixed_enemy_panels_show_readable_reference_and_keep_missing_images(self):
  from rouge.battle_view import BattlePreviewPanel
  for sid,eid in CASES:
   p=BattlePreviewPanel();p._load_stage(sid);p._render_enemy(eid,0);text=p.enemy_detail.toPlainText()
   self.assertIn('辅助单位机制参考',text);self.assertIn('当前完整脚本和实际触发仍未闭合',text);self.assertIn('图片未取得',p.enemy_picture.image.text())
   self.assertNotIn('DamageAura.value',text);self.assertNotIn('Torappu.',text);self.assertEqual(p.enemy_picture.key[1],eid);p.close()
 def test_context_refresh_keeps_enemy_reading_and_source_variant_when_enemy_remains(self):
  from rouge.battle_view import BattlePreviewPanel
  p=BattlePreviewPanel();p.resize(1400,1000);p._load_stage('ro6_b_3_b');p.show();self.app.processEvents();p._render_enemy('enemy_2154_shdfb',0)
  self.assertIn('本关使用独立构造',p.enemy_detail.toPlainText());p.enemy_detail.verticalScrollBar().setValue(p.enemy_detail.verticalScrollBar().maximum());scroll=p.enemy_detail.verticalScrollBar().value()
  p.set_context({'difficulty':1});self.app.processEvents();self.assertEqual(p._shown_enemy,('ro6_b_3_b','enemy_2154_shdfb',0));self.assertIn('本关使用独立构造',p.enemy_detail.toPlainText());self.assertEqual(p.enemy_detail.verticalScrollBar().value(),min(scroll,p.enemy_detail.verticalScrollBar().maximum()))
  p.technical.setChecked(True);self.app.processEvents();p._render_enemy('enemy_2154_shdfb',0);self.assertIn('DamageAura.value',p.enemy_detail.toPlainText());self.assertIn('500.0',p.enemy_detail.toPlainText());self.assertIn('6.0',p.enemy_detail.toPlainText());p.close()
if __name__=='__main__':unittest.main()
