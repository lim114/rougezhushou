"""Public calculation boundary stays intact after private duplicate removal."""
from pathlib import Path
from types import ModuleType
from copy import deepcopy
from hashlib import sha256
from unittest.mock import patch
import json,math,unittest
from rouge import damage

ROOT=Path(__file__).resolve().parents[1];COMPARISONS=[]

class CoreCalculationReviewTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  raw=(ROOT/'research/core-calculation-review-20261031/before-damage.py').read_bytes();cls.old=ModuleType('rouge._before_core_calculation_review');cls.old.__package__='rouge';exec(compile(raw,'<own-prior-damage>','exec'),cls.old.__dict__)
 def compare(self,scenario):
  before=deepcopy(scenario);expected=self.old.calculate_damage(deepcopy(scenario));actual=damage.calculate_damage(scenario);self.assertEqual(actual,expected);self.assertEqual(scenario,before)
  COMPARISONS.append({'operator':scenario['operator'],'skill':scenario['skill'],'input':scenario,'complete_result_equal':True,'full_result_sha256':sha256(json.dumps(actual,ensure_ascii=False,sort_keys=True,default=str).encode('utf8')).hexdigest()})
 def test_all_nine_skills_keep_complete_results_reports_unknowns_and_relic_timing(self):
  COMPARISONS.clear()
  variants=[{}, {'trust':0,'potential':6,'skill_rank':1},
   {'enemy_defense':500,'enemy_resistance':30,'effects':[{'kind':'attack_pct','value':.3},{'kind':'hp_pct','value':.2},{'kind':'attack_speed','value':50}]},
   {'relic_ids':['rogue_6_relic_legacy_97']},
   {'relic_ids':['rogue_6_relic_fight_25','rogue_6_relic_legacy_23_c']},
   {'timing':{'target_windows':[]}},
   {'window_seconds':8,'timing':{'windup_frames':6,'recovery_frames':9}}]
  for op in ['kaltsit','silverash','mechanist']:
   for skill in [1,2,3]:
    for variant in variants:
     with self.subTest(op=op,skill=skill,variant=variant):self.compare({'operator':op,'skill':skill,**deepcopy(variant)})
   for elite,maximum in [(0,50),(1,80)]:
    for skill in range(1,elite+2):
     with self.subTest(op=op,elite=elite,skill=skill):self.compare({'operator':op,'skill':skill,'elite':elite,'level':maximum,'skill_rank':7})
  for scenario in [
   {'operator':'silverash','skill':2,'activation_count':2,'deployment_stacks':2,'companion_attack':1000},
   {'operator':'mechanist','skill':2,'shield_break_count':2},
   {'operator':'mechanist','skill':3,'charge_count':1}]:self.compare(scenario)
  self.assertEqual(len(COMPARISONS),75)
 def test_public_invalid_selection_still_has_same_type_and_error_at_original_boundary(self):
  for op in ['kaltsit','silverash','mechanist']:
   for field,values in [('skill',[None,False,True,0,4,1.0,'1',[],{}]),('skill_rank',[None,False,True,0,11,1.0,'1',[],{}])]:
    for value in values:
     s={'operator':op,'skill':1,field:value};results=[]
     for calculate in [self.old.calculate_damage,damage.calculate_damage]:
      try:calculate(deepcopy(s));self.fail('Invalid public selection accepted')
      except (ValueError,TypeError,KeyError)as e:results.append((type(e),str(e)))
     self.assertEqual(results[0],results[1])
 def test_original_numeric_and_active_skill_gates_are_not_removed(self):
  scenarios=[{'operator':'mechanist','skill':1,'base_attack':-1},
   {'operator':'kaltsit','skill':2,'base_attack':float('nan')},
   {'operator':'silverash','skill':3,'enemy_resistance':101},
   {'operator':'mechanist','skill':1,'enemy_defense':True},
   {'operator':'mechanist','skill':2,'shield_break_count':True},
   {'operator':'mechanist','skill':3,'charge_count':-1},
   {'operator':'silverash','skill':2,'deployment_stacks':3},
   {'operator':'silverash','skill':2,'deployment_stacks':1,'companion_attack':True}]
  for s in scenarios:
   errors=[]
   for calculate in [self.old.calculate_damage,damage.calculate_damage]:
    with self.assertRaises(ValueError)as failure:calculate(deepcopy(s))
    errors.append(str(failure.exception))
   self.assertEqual(errors[0],errors[1])
 def test_same_calculation_uses_fewer_duplicate_catalog_lookups_in_damage_module(self):
  counts=[];values=[]
  for module in [self.old,damage]:
   with patch.object(module,'catalog',wraps=module.catalog)as lookup:values.append(module.calculate_damage({'operator':'mechanist','skill':1}));counts.append(lookup.call_count)
  self.assertEqual(values[0],values[1]);self.assertEqual(counts,[5,3])

if __name__=='__main__':unittest.main()
