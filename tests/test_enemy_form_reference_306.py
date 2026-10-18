"""Exact documentary form relationships; no Qt/game/chat or actual combat state."""
from copy import deepcopy
from importlib.util import module_from_spec,spec_from_file_location
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
from rouge import enemy_form_reference as form,battle_preview

ROOT=Path(__file__).resolve().parents[1]
TARGETS={'enemy_2133_shdopl_lancer':('enemy_1072_dlancer','萨卡兹穿刺手'),
 'enemy_2133_shdopl_mpmage':('enemy_10079_mpmage','稳定态萨卡兹术师结晶'),
 'enemy_2133_shdopl_sword':('enemy_1075_dmgswd','萨卡兹魔剑士'),
 'enemy_2133_shdopl_demonk':('enemy_1501_demonk','萨卡兹百夫长')}

class EnemyForm306(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.battle=json.loads((ROOT/form.BATTLE).read_bytes())
  cls.level=json.loads((ROOT/form.LEVEL).read_bytes())
  cls.docs=json.loads((ROOT/form.DOC).read_bytes())
  cls.tuples=[(sid,eid,0)for sid in('ro6_n_2_3','ro6_e_2_3')for eid in TARGETS]
 def first(self):return form.disguise_reference(*self.tuples[0])
 def assertUnknown(self,result):
  for key in form.ACTUAL_FIELDS:self.assertIsNone(result[key],key)
  for key in('modifiers_changed','maps_changed','level_type_applied','run_state_updated','current_server_verified'):self.assertIs(result[key],False,key)
 def test_exact_eight_body_and_independent_target_objects(self):
  for sid,eid,lv in self.tuples:
   with self.subTest(stage=sid,enemy=eid):
    r=form.disguise_reference(sid,eid,lv);target_id,target_name=TARGETS[eid];s=self.battle['stages'][sid]
    self.assertEqual(r['status'],'documented_reference');self.assertTrue(r['source_valid'])
    self.assertEqual(r['body_reference'],next(x for x in s['enemies']if x['id']==eid and x['level']==lv))
    self.assertEqual(r['disguise_enemy_reference'],next(x for x in s['enemies']if x['id']==target_id))
    self.assertEqual(r['documented_variant_name'],'空值体('+target_name+')');self.assertUnknown(r)
 def test_complete_original_local_reference_retained(self):
  for sid,eid,lv in self.tuples:
   r=form.disguise_reference(sid,eid,lv)
   self.assertEqual(r['complete_original_reference'],next(x for x in self.level['enemyDbRefs']if x['id']==eid and x['level']==lv))
   self.assertEqual(r['declared_summon_enemy_key'],TARGETS[eid][0])
 def test_alias_tier_not_promoted_from_normal_placeholder_or_document(self):
  for identity in self.tuples:
   r=form.disguise_reference(*identity);raw=r['complete_original_reference']['overwrittenData']['levelType']
   self.assertEqual(raw,{'m_defined':False,'m_value':'NORMAL'});self.assertIsNone(r['fixed_body_tier'])
   self.assertIsNone(r['body_reference']['level_type']);self.assertEqual(r['documented_base_tier_reference'],'普通');self.assertUnknown(r)
 def test_blackboard_zero_never_becomes_summon_level(self):
  r=self.first();self.assertEqual(r['complete_original_reference']['overwrittenData']['talentBlackboard'][0]['value'],0.0)
  self.assertEqual(r['selected_disguise_reference_level'],0);self.assertIsNone(r['declared_summon_level']);self.assertIsNone(r['actual_disguise_level'])
 def test_source_names_and_body_values_not_replaced_by_base_or_disguise(self):
  r=self.first();self.assertEqual((r['fixed_name'],r['community_base_name']),('空植体','空值体'))
  self.assertEqual(r['body_reference']['reference_stats']['maxHp'],6000)
  self.assertEqual(r['body_reference']['reference_stats']['atk'],400)
  self.assertEqual(r['disguise_enemy_reference']['reference_stats']['atk'],450)
  self.assertNotEqual(r['body_reference']['id'],r['disguise_enemy_reference']['id'])
 def test_crystal_target_not_mistaken_for_separate_caster(self):
  r=form.disguise_reference('ro6_n_2_3','enemy_2133_shdopl_mpmage',0)
  self.assertEqual(r['disguise_enemy_reference']['name'],'稳定态萨卡兹术师结晶')
  self.assertNotEqual(r['declared_summon_enemy_key'],'enemy_1022_dmage')
 def test_complete_lifecycle_preserves_conditions_and_quoted_priority(self):
  r=self.first();phases=r['documented_lifecycle']
  self.assertEqual([x['phase_key']for x in phases],['hidden_body','disguise','revealed_body'])
  quoted='\n'.join(q for x in phases for q in x['source_quotes'])
  pages={p['title']:p for p in self.docs['query']['pages'].values()};body=pages['空值体']['revisions'][0]['slots']['main']['*']
  for p in phases:
   self.assertTrue(p['conditions'])
   for q in p['source_quotes']:self.assertIn(q,body)
  for text in('优先级+2000','跳过重生','无原因退场','剩余路径','当前停驻','所在地块中心'):self.assertIn(text,quoted)
  self.assertUnknown(r)
 def test_damage_wording_difference_is_disclosed_not_unified(self):
  r=self.first();d=next(x for x in r['source_differences']if x['key']=='damage_vs_attack')
  self.assertIn('受攻击时解除',r['body_reference']['description']);self.assertIn('受到伤害时',d['text']);self.assertIn('未造成伤害',d['text'])
 def test_no_io_for_non_targets_wrong_stage_or_bool_levels(self):
  with patch.object(form,'_packet',side_effect=AssertionError('no source read')):
   for sid,eid,level in[(None,None,None),([],{},0),('ro6_n_2_3',list(TARGETS)[0],False),('ro6_n_2_3',list(TARGETS)[0],0.0),('ro6_n_2_3',list(TARGETS)[0],1),('ro6_n_4_1',list(TARGETS)[0],0),('ro6_n_2_3','enemy_2133_shdopl',0),('ro6_n_2_3','enemy_2133_shdopl_b',0)]:
    self.assertIsNone(form.disguise_reference(sid,eid,level))
 def test_returned_nested_objects_are_defensive_and_fresh(self):
  r=self.first();r['reference']['documented_lifecycle'][0]['conditions'].clear();r['body_reference']['reference_stats']['atk']='poison';r['disguise_enemy_reference']['abilities'].clear()
  q=self.first();self.assertTrue(q['documented_lifecycle'][0]['conditions']);self.assertEqual(q['body_reference']['reference_stats']['atk'],400)
  s=self.battle['stages']['ro6_n_2_3'];self.assertEqual(q['disguise_enemy_reference'],next(x for x in s['enemies']if x['id']==TARGETS[self.tuples[0][1]][0]))
 def test_complete_legacy_stage_cache_pollution_fails_closed(self):
  b=deepcopy(self.battle);b['stages']['ro6_n_2_3']['map'][0][0]='poison'
  with patch.object(battle_preview,'battle_data',return_value=b):
   r=self.first();self.assertEqual(r['status'],'source_unavailable');self.assertIsNone(r['reference']);self.assertEqual(r['documented_lifecycle'],[]);self.assertUnknown(r)
 def test_each_runtime_member_tamper_delete_and_recover(self):
  manifest=json.loads((ROOT/form.MANIFEST).read_bytes())
  with tempfile.TemporaryDirectory()as td:
   temp=Path(td)
   for name in[form.MANIFEST,*manifest['runtime_files']]:
    f=temp/name;f.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,f)
   with patch.object(form,'ROOT',temp):
    self.assertTrue(self.first()['source_valid'])
    for name in manifest['runtime_files']:
     f=temp/name;old=f.read_bytes()
     for mode in('tamper','delete'):
      if mode=='tamper':f.write_bytes(old+b' ')
      else:f.unlink()
      r=self.first();self.assertFalse(r['source_valid']);self.assertIsNone(r['body_reference']);self.assertIsNone(r['disguise_enemy_reference']);self.assertIsNone(r['source_identity']);self.assertUnknown(r)
      f.write_bytes(old);self.assertTrue(self.first()['source_valid'])
 def test_manifest_itself_is_freshly_checked(self):
  with tempfile.TemporaryDirectory()as td:
   temp=Path(td);f=temp/form.MANIFEST;f.parent.mkdir(parents=True);f.write_bytes((ROOT/form.MANIFEST).read_bytes()+b' ')
   with patch.object(form,'ROOT',temp):self.assertEqual(self.first()['status'],'source_unavailable')
 def test_reference_does_not_invoke_environment_or_combat_prediction(self):
  before=deepcopy(battle_preview.battle_data())
  with patch.object(battle_preview,'enemy_preview',side_effect=AssertionError('must not predict')):
   r=self.first();self.assertTrue(r['source_valid'])
  self.assertEqual(battle_preview.battle_data(),before);self.assertUnknown(r)
 def test_plain_reading_has_named_independent_abilities_and_no_raw_ids(self):
  r=self.first();text=form.reference_text(r)
  for phrase in('萨卡兹穿刺手','逐渐加速','伪装退场后','剩余路径','未造成伤害','类别仍未知','实际召唤等级'):self.assertIn(phrase,text)
  for raw in('enemy_2133','summon.enemy_key','m_defined','m_value','黑板','级别0','实例','回调'):self.assertNotIn(raw,text)
  detailed=form.reference_text(r,technical=True);self.assertIn('summon.enemy_key',detailed);self.assertIn(r['enemy_id'],detailed)
 def test_unavailable_reading_never_keeps_previous_target(self):
  with patch.object(form,'_packet',return_value=None):r=self.first()
  text=form.reference_text(r);self.assertIn('旧对应敌人与说明已清除',text);self.assertNotIn('萨卡兹穿刺手',text);self.assertIsNone(form.disguise_reference('other','enemy_2133_shdopl_lancer',0))
 def test_complete_document_builder_reproduces_all_outputs(self):
  path=ROOT/'scripts/build_enemy_form_reference_306.py';spec=spec_from_file_location('form306_builder',path);builder=module_from_spec(spec);spec.loader.exec_module(builder)
  with tempfile.TemporaryDirectory()as td:
   temp=Path(td)
   for name in(form.DOC,form.GLOSSARY,form.PACK+'/backend-template.py'):
    dst=temp/name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,dst)
   result=builder.build(ROOT,temp)
   for name in result['outputs']:self.assertEqual((temp/name).read_bytes(),(ROOT/name).read_bytes(),name)

if __name__=='__main__':unittest.main()
