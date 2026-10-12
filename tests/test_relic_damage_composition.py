"""Only source-bound combinations close the qualified damage reference."""
import copy,unittest
from rouge.damage import calculate_damage
from rouge.relics import mechanics,prepare
from rouge.relic_damage_factors import source_factor,verified_rule,parameter_factor
from rouge.catalog import catalog
from rouge.supplemental_skills import defaults,skill_reference
from rouge.supplemental_run import run_skill_reference,format_run_reference
from tests.test_supplemental_run_141 import environment

PHY=['rogue_6_relic_legacy_5','rogue_6_relic_legacy_6','rogue_6_relic_legacy_7']
MAG=['rogue_6_relic_legacy_8','rogue_6_relic_legacy_9','rogue_6_relic_legacy_10']
EP=['rogue_6_relic_legacy_104','rogue_6_relic_fight_21']
BOOK='rogue_6_relic_legacy_73'

def example(**extra):
 return calculate_damage({'operator':'char_4204_mantra','skill':2,'enemy_resistance':0,
  'initial_neural_buildup':999,'window_seconds':1,**extra})
def component(result,name):return next(c for c in result['components']if c['name']==name)
def rule(identity,dtype):
 return next({**r,'relic_id':identity,'_verified_rule':True} for r in mechanics()['relics'][identity]['effects']
  if r.get('kind')=='damage_taken' and r.get('damage_type')==dtype)

class RelicDamageCompositionTests(unittest.TestCase):
 def test_base_one_same_type_merges_excess_not_independent_products(self):
  for ids,dtype,factor in ((PHY[:2],'physical',1.4),(PHY,'physical',1.75),(MAG,'magic',1.9)):
   with self.subTest(dtype=dtype):
    rules=[rule(i,dtype)for i in ids]
    self.assertTrue(all(verified_rule(r,dtype)for r in rules))
    self.assertAlmostEqual(source_factor(rules,dtype),factor)
    self.assertAlmostEqual(source_factor(list(reversed(rules)),dtype),factor)
    self.assertEqual(source_factor(rules+[rules[0]],dtype),source_factor(rules,dtype))
 def test_unknown_prefab_or_source_is_not_promoted(self):
  a,b=[rule(i,'physical')for i in PHY[:2]]
  for key,value in (('relic_id','future'),('group','enemy_damage_scale[mag]'),
    ('source_buff_key','global_buff_normal'),('composition_evidence','other'),('source_buff_index',1)):
   wrong={**b,key:value}
   self.assertIsNone(source_factor([a,wrong],'physical'))
  self.assertEqual(source_factor([a,b],'magic'),1)
 def test_elemental_independent_modifier_instances_multiply(self):
  rules=[rule(i,'elemental')for i in EP]
  self.assertEqual(source_factor(rules,'elemental'),3.5)
  self.assertEqual(parameter_factor(rules,'elemental'),3.5)
  self.assertEqual(parameter_factor(rules+[{'kind':'damage_taken','damage_type':'elemental','value':0}],'elemental'),3.5)
  self.assertEqual(source_factor(rules+rules,'elemental'),3.5)
 def test_actual_burst_and_resistance_both_ids_and_order(self):
  for ids in (EP,EP[::-1],EP+EP):
   for resistance in (0,50):
    r=example(relic_ids=ids,enemy_elemental_resistance=resistance)
    self.assertEqual(component(r,'神经损伤爆发')['per_hit'],21000*(1-resistance/100))
    self.assertTrue(r['relic_resolution']['complete'])
    self.assertFalse(any(row['pending']for row in r['relic_resolution']['records']))
 def test_damage_types_and_buildup_do_not_receive_element_factor(self):
  base=example();ice=example(relic_ids=[EP[1]]);both=example(relic_ids=EP)
  for c in both['components']:
   if c['damage_type']=='magic':self.assertEqual(c['per_hit'],component(base,c['name'])['per_hit'])
   if c['damage_type']=='buildup':self.assertEqual(c['per_hit'],component(ice,c['name'])['per_hit'])
  true_rule=rule('rogue_6_relic_legacy_11','true')
  self.assertEqual(source_factor([true_rule],'true'),2.5)
  for dtype in ('physical','magic','true','healing'):
   self.assertEqual(parameter_factor([rule(i,'elemental')for i in EP],dtype),1)
 def test_neutral_manual_effect_does_not_discard_native_pair(self):
  r=example(relic_ids=EP,effects=[{'kind':'damage_taken','damage_type':'elemental','value':0}])
  self.assertEqual(component(r,'神经损伤爆发')['per_hit'],21000)
  self.assertNotIn('damage_composition_unresolved',r['relic_resolution'])
 def test_foreign_manual_layer_keeps_subtotal_but_masks_complete(self):
  manual=[{'kind':'damage_taken','damage_type':'elemental','value':.2}]
  subtotal=example(effects=manual);mixed=example(relic_ids=EP,effects=manual)
  self.assertTrue(mixed['relic_resolution']['damage_composition_unresolved'])
  self.assertEqual(component(mixed,'神经损伤爆发')['per_hit'],component(subtotal,'神经损伤爆发')['per_hit'])
  self.assertIsNone(mixed['total_damage'])
  self.assertIsNone(mixed['estimate']['skill']['window_damage'])
  self.assertEqual(mixed['known_damage_subtotals']['window_damage'],subtotal['total_damage'])
  self.assertEqual(mixed['estimate']['skill']['initial_seconds'],subtotal['estimate']['skill']['initial_seconds'])
  self.assertEqual(mixed['estimate']['skill']['recharge_seconds'],subtotal['estimate']['skill']['recharge_seconds'])
 def test_foreign_composition_without_elemental_output_retains_zero(self):
  r=example(relic_ids=EP,effects=[{'kind':'damage_taken','damage_type':'elemental','value':.2}],timing={'target_windows':[]})
  self.assertEqual(r['total_damage'],0)
  self.assertEqual(r['estimate']['skill']['window_dps'],0)
 def test_manual_proof_markers_cannot_impersonate_raw_bound_source(self):
  forged=rule(EP[0],'elemental')
  r=example(relic_ids=EP,effects=[forged])
  self.assertTrue(r['relic_resolution']['damage_composition_unresolved'])
  self.assertIsNone(r['total_damage'])
 def test_book_combat_condition_stays_reference_only(self):
  args={'operator':'mechanist','skill':1,'relic_ids':MAG+[BOOK],'relic_context':{'deployed_casters':8}}
  r=calculate_damage(args)
  self.assertFalse(any(e.get('relic_id')==BOOK for e in r.get('applied_effects',[])))
  self.assertTrue(next(row for row in r['relic_resolution']['records']if row['id']==BOOK)['reference_effects'])
 def test_low_star_reference_after_defense_and_magic_resistance(self):
  for identity,ids,dtype,row in (('char_124_kroos',PHY[:2],'physical',0),('char_210_stward',MAG,'magic',1)):
   p=defaults(identity);p.update(enemy_defense=300,enemy_resistance=50)
   base=skill_reference(p);r=run_skill_reference(p,environment(ids));factor=1.4 if dtype=='physical'else 1.9
   self.assertAlmostEqual(r['rows'][row]['value'],base['rows'][row]['value']*factor)
   ref=r['damage_reference']['damage_composition_reference'][dtype]
   self.assertFalse(ref['native_source_order_verified']);self.assertFalse(ref['native_runtime_verified'])
   self.assertIn('参数算术参考',format_run_reference(r))
   self.assertTrue(r['attribute_resolution']['complete_for_attribute_scope'])
