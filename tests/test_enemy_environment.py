import unittest
import tempfile,time
from pathlib import Path
import cv2,numpy as np
from rouge.damage import calculate_damage
from rouge.recognition import ScreenReader
from rouge.run_state import RunState

class EnemyEnvironmentTests(unittest.TestCase):
    def test_relic_enemy_modifiers_follow_stage_and_difficulty_and_are_reported(self):
        args={'operator':'mechanist','skill':1,'relic_ids':['rogue_6_relic_legacy_84'],
            'target_enemy':{'stage_id':'ro6_e_1_2','enemy_id':'enemy_1093_ccsbr','level':0},
            'run_config':{'difficulty':{'value':10},'zone':{'id':'zone_1'}}}
        result=calculate_damage(args);target=result['run_resolution']['enemy']
        self.assertAlmostEqual(target['stats']['def'],64.8)
        self.assertAlmostEqual(target['stats']['maxHp'],5153.655)
        plain=calculate_damage({'operator':'mechanist','skill':1,'enemy_defense':64.8,'enemy_resistance':10})
        self.assertAlmostEqual(result['total_damage'],plain['total_damage'])

    def test_portal_keeps_main_depth_and_missing_context_does_not_guess(self):
        with tempfile.TemporaryDirectory() as folder:
            memory=RunState(Path(folder)/'run.json')
            partial={'relics':{'ids':[],'count':None,'icons':[]},'operators':[]}
            memory.apply({**partial,'config':{'zone':{'id':'zone_2','name':'甜美的伤口'}}},time.time())
            portal={'id':None,'hidden':True,'name':'未萌生的摇篮','candidates':['zone_portal_normal_1_1','zone_portal_normal_1_2']}
            memory.apply({**partial,'config':{'zone':portal,'difficulty':{'value':10}}},time.time())
            args={'operator':'mechanist','skill':1,'target_enemy':{'stage_id':'ro6_n_1_2','enemy_id':'enemy_1093_ccsbr','level':0}}
            known=calculate_damage({**args,'run_config':memory.state['config']})
            self.assertAlmostEqual(known['run_resolution']['enemy']['stats']['maxHp'],3869.762)
            unknown=calculate_damage({**args,'run_config':{'difficulty':{'value':10},'zone':portal}})
            self.assertAlmostEqual(unknown['run_resolution']['enemy']['stats']['maxHp'],3380)
            self.assertTrue(any('区域深度尚未确认' in s for s in unknown['run_resolution']['pending']))
            with self.assertRaises(ValueError):calculate_damage({**args,'target_enemy':{'stage_id':'ro6_n_1_2','enemy_id':'not_a_real_enemy','level':0}})

    def test_visible_region_updates_and_survives_partial_pages_and_restart(self):
        root=Path(__file__).resolve().parents[1]
        image=cv2.imdecode(np.fromfile(root/'samples/native-client/run-map-empty.png',dtype=np.uint8),1)
        observed=ScreenReader().read(image)['run']
        self.assertEqual(observed['config']['zone']['id'],'zone_1')
        with tempfile.TemporaryDirectory() as folder:
            memory=RunState(Path(folder)/'run.json');identity=memory.state['id']
            memory.apply(observed,time.time())
            partial={'relics':{'ids':[],'count':None,'icons':[]},'operators':[],'config':{}}
            memory.apply(partial,time.time())
            self.assertEqual(memory.state['config']['zone']['id'],'zone_1')
            memory.apply({**partial,'config':{'zone':{'id':'zone_3','name':'血色空脉'}}},time.time())
            restored=RunState(memory.file)
            self.assertEqual(restored.state['id'],identity)
            self.assertEqual(restored.state['config']['zone']['id'],'zone_3')
            self.assertTrue(any(h.get('field')=='zone' for h in restored.state['history']))

    def test_boss_reduction_is_independent_from_relic_vulnerability_and_preserves_healing_and_timing(self):
        target={'stage_id':'ro6_b_3','enemy_id':'enemy_2143_shwksc','level':0}
        base={'operator':'mechanist','skill':3,'charge_count':1,'target_enemy':target,
            'effects':[{'kind':'damage_taken','damage_type':'magic','value':.2}]}
        ten=calculate_damage({**base,'run_config':{'difficulty':{'value':10},'zone':{'id':'zone_3'}}})
        eleven=calculate_damage({**base,'run_config':{'difficulty':{'value':11},'zone':{'id':'zone_3'}}})
        self.assertEqual(eleven['run_resolution']['enemy']['level_type'],'BOSS')
        self.assertAlmostEqual(eleven['total_damage'],ten['total_damage']*.8)
        self.assertEqual(eleven['estimate']['skill']['cycle_seconds'],ten['estimate']['skill']['cycle_seconds'])
        self.assertAlmostEqual(eleven['estimate']['skill']['cycle_damage'],ten['estimate']['skill']['cycle_damage']*.8)
        for op,skill in [('kaltsit',1),('kaltsit',2),('char_298_susuro',2),('char_328_cammou',2)]:
            args={'operator':op,'skill':skill,'target_enemy':target,'run_config':{'difficulty':{'value':10}}}
            before=calculate_damage(args)
            after=calculate_damage({**args,'run_config':{'difficulty':{'value':11}}})
            self.assertAlmostEqual(after['total_damage'],before['total_damage']*.8)
            self.assertEqual(after['estimate']['skill']['total_healing'],before['estimate']['skill']['total_healing'])

    def test_emergency_stage_and_region_use_pinned_enemy_instead_of_manual_defense(self):
        result=calculate_damage({'operator':'mechanist','skill':1,'enemy_defense':99999,
            'target_enemy':{'stage_id':'ro6_e_1_2','enemy_id':'enemy_1093_ccsbr','level':0},
            'run_config':{'difficulty':{'value':10},'zone':{'id':'zone_1'}}})
        target=result['run_resolution']['enemy']
        # Warfighter: HP2600 / ATK290 / DEF60; emergency HPx1.5 ATK/DEFx1.2;
        # grade10 HPx1.3; first main region HP/ATKx1.07.
        self.assertAlmostEqual(target['stats']['maxHp'],5424.9)
        self.assertAlmostEqual(target['stats']['atk'],372.36)
        self.assertAlmostEqual(target['stats']['def'],72)
        self.assertEqual(target['level_type'],'NORMAL')
        plain=calculate_damage({'operator':'mechanist','skill':1,'enemy_defense':72,'enemy_resistance':10})
        self.assertAlmostEqual(result['total_damage'],plain['total_damage'])
        self.assertTrue(any(s['id']=='enemy_environment' for s in result['report']['sections']))
