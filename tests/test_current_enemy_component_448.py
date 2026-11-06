from copy import deepcopy
from pathlib import Path
from hashlib import sha256
from types import ModuleType
import unittest
from PySide6.QtWidgets import QApplication
from rouge import current_battle_reference as model
from rouge.current_enemy_forecast import forecasts
from rouge import enemy_environment

ROOT=Path(__file__).resolve().parents[1]


class CurrentEnemyComponent448Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.qt=QApplication.instance()or QApplication([])
  cls.normal=model.stage_reference('ro6_n_2_6');cls.emergency=model.stage_reference('ro6_e_2_6')
 def config(self,grade=15,zone='zone_1'):
  return {'difficulty':{'value':grade},'zone':{'id':zone}}
 def test_current_normal_elite_and_emergency_public_arithmetic_examples(self):
  examples=[(self.normal,15,'zone_1','0',[12480,480,200,50]),
            (self.normal,15,'zone_1','1',[15600,828,500,30]),
            (self.emergency,15,'zone_1','0',[18720,528,240,50]),
            (self.emergency,15,'zone_1','1',[23400,910.8,600,30]),
            (self.normal,16,'zone_2','0',[16250,625,200,50])]
  for stage,grade,zone,key,expected in examples:
   row=forecasts(stage,self.config(grade,zone))[key]
   for name,value in zip(('maxHp','atk','def','magicResistance'),expected):self.assertAlmostEqual(row['environment_component'][name],value)
   self.assertIsNone(row['complete_current_total']);self.assertFalse(row['actual_gameplay_verified']);self.assertEqual(row['scope'],'current_declared_fixed_environment_component');self.assertTrue(any('env_system_new'in line for line in row['pending']))
 def test_low_grade_reductions_do_not_accumulate(self):
  for grade,hp,atk in [(0,4800,280),(1,6400,320),(2,6800,340),(3,7200,360),(4,8000,400)]:
   row=forecasts(self.normal,self.config(grade))['0']['environment_component'];self.assertEqual(row['maxHp'],hp);self.assertEqual(row['atk'],atk)
 def test_forged_current_sources_or_rows_remain_unknown_and_inputs_unchanged(self):
  for mutation in ('source_identity','source','level','tier','core','difficulty','difficulty_source'):
   stage=deepcopy(self.normal);config=self.config(16)
   if mutation=='source_identity':stage['source_identity']='foreign'
   elif mutation=='source':stage['source']['sha256']='foreign'
   elif mutation=='level':stage['level']['runes']=[]
   elif mutation=='tier':stage['enemies'][0]['tier']='BOSS'
   elif mutation=='core':stage['enemies'][0]['declared_traits']['explicit_core_attributes']['atk']+=1
   elif mutation=='difficulty':stage['difficulty_reference']['16']['bossValue']=99
   else:stage['difficulty_source']['commit']='foreign'
   before=deepcopy((stage,config));rows=forecasts(stage,config);self.assertTrue(all(r['environment_component']is None and r['pending']for r in rows.values()),mutation);self.assertEqual((stage,config),before)
 def test_missing_conditions_remain_unknown_instead_of_claiming_a_total(self):
  self.assertEqual(forecasts(self.normal,{}),{})
  for config in [self.config(17),{'difficulty':{'value':15,'mode':'OTHER'}}]:self.assertTrue(all(r['environment_component']is None for r in forecasts(self.normal,config).values()))
  rows=forecasts(self.normal,{'difficulty':{'value':15}});self.assertTrue(all(r['complete_current_total']is None for r in rows.values()));self.assertTrue(any('区域' in x for row in rows.values()for x in row['pending']))
 def test_existing_rich_environment_results_match_exact_before_source(self):
  raw=(ROOT/'research/current-enemy-component-448/before-enemy_environment.py').read_bytes();self.assertEqual(sha256(raw).hexdigest(),'d7fdc1a06e81214455f5d1e4ac1a6aa038656c5f9f2a56a40534546569c7070c');old=ModuleType('rouge._environment_before448');old.__package__='rouge';old.__file__=str(ROOT/'rouge/enemy_environment.py');exec(compile(raw,'<exact-before448-environment>','exec'),old.__dict__)
  cases=[('ro6_n_1_2','enemy_1093_ccsbr',0),('ro6_e_1_2','enemy_1093_ccsbr',0),('ro6_b_1','enemy_2138_shdbjg',0)]
  for sid,eid,level in cases:
   for grade in (0,1,3,4,8,11,15,16):
    outputs=[]
    for module in(old,enemy_environment):
     scenario={'target_enemy':{'stage_id':sid,'enemy_id':eid,'level':level},'run_config':self.config(grade,'zone_2')};resolution={'difficulty':{'value':grade},'notes':[],'pending':[]};module.resolve_enemy(scenario,resolution,difficulty_profiles=self.normal['difficulty_reference']);outputs.append((scenario,resolution))
    self.assertEqual(outputs[0],outputs[1],(sid,grade))
 def test_new_subtotals_reach_actual_reader_and_refresh_keeps_selection(self):
  from rouge.current_battle_view import CurrentBattlePanel
  p=CurrentBattlePanel(self.normal['id']);self.addCleanup(p.close);p.set_context(self.config());self.assertTrue(p.enemy_choices.select_value('0'));before=p.enemy_player.toPlainText();self.assertIn('12,480',before);self.assertIn('完整面板：待补齐阶段、技能与藏品影响。',before);p.set_context(self.config(zone='zone_2'));self.assertEqual(p.enemy_key,'0');self.assertIn('14,976',p.enemy_player.toPlainText());self.assertNotEqual(before,p.enemy_player.toPlainText())
