"""Worked enemy values at public calculation boundary."""
import unittest
from rouge.damage import calculate_damage

class DifficultyRuleTests(unittest.TestCase):
    def test_low_difficulty_is_exclusive_not_cumulative_and_composes_with_emergency_and_relic(self):
        args={'operator':'mechanist','skill':1,
            'target_enemy':{'stage_id':'ro6_n_1_2','enemy_id':'enemy_1093_ccsbr','level':0}}
        for grade,hp,atk in [(0,1560,203),(1,2080,232),(2,2210,246.5),(3,2340,261),(4,2600,290)]:
            with self.subTest(grade=grade):
                result=calculate_damage({**args,'run_config':{'difficulty':{'value':grade}}})
                enemy=result['run_resolution']['enemy']
                self.assertAlmostEqual(enemy['stats']['maxHp'],hp)
                self.assertAlmostEqual(enemy['stats']['atk'],atk)
                self.assertEqual(enemy['stats']['def'],60)
                self.assertFalse(any('低难度独立减益' in p for p in enemy['pending']))
        mixed=calculate_damage({**args,'target_enemy':{**args['target_enemy'],'stage_id':'ro6_e_1_2'},
            'run_config':{'difficulty':{'value':0}},'relic_ids':['rogue_6_relic_legacy_84']})
        self.assertAlmostEqual(mixed['run_resolution']['enemy']['stats']['maxHp'],2223)
        self.assertAlmostEqual(mixed['run_resolution']['enemy']['stats']['atk'],243.6)
        self.assertAlmostEqual(mixed['run_resolution']['enemy']['stats']['def'],64.8)

    def test_high_grade_enemy_specific_stats_use_the_threshold_and_keep_dynamic_effects_pending(self):
        cases=[
            ('ro6_b_6','enemy_2150_shchmr',12,'def',4000),
            ('ro6_b_6','enemy_2150_shchmr',13,'def',6000),
            ('ro6_b_5','enemy_2148_shorbb',13,'maxHp',1092000),
            ('ro6_b_5','enemy_2148_shorbb',14,'maxHp',2262000),
            ('ro6_n_1_2','enemy_2137_shsdgo',14,'maxHp',27144),
            ('ro6_n_1_2','enemy_2137_shsdgo',15,'maxHp',42120),
            ('ro6_n_1_2','enemy_1093_ccsbr',15,'maxHp',4056)]
        for sid,eid,grade,field,value in cases:
            with self.subTest(enemy=eid,grade=grade):
                result=calculate_damage({'operator':'mechanist','skill':1,
                    'target_enemy':{'stage_id':sid,'enemy_id':eid,'level':0},
                    'run_config':{'difficulty':{'value':grade},'zone':{'id':'zone_1'}}})
                enemy=result['run_resolution']['enemy']
                self.assertAlmostEqual(enemy['stats'][field],value)
                if (eid,grade) in [('enemy_2150_shchmr',13),('enemy_2148_shorbb',14),('enemy_2137_shsdgo',15)]:
                    self.assertTrue(any(s.get('evidence') for s in enemy['steps']))
                    self.assertTrue(enemy['pending'])
                    report=next(s for s in result['report']['sections'] if s['id']=='enemy_environment')
                    self.assertTrue(any('尚未逐级实战验证' in n for n in report['notes']))

    def test_orb_active_column_reduction_is_type_specific_and_recomputes_damage_healing(self):
        base={'target_enemy':{'stage_id':'ro6_b_5','enemy_id':'enemy_2148_shorbb','level':0},
            'run_config':{'difficulty':{'value':11}}}
        for mode,physical,magic,healing in [('active_same_column',373.023,323.12,6162.36),
                                          ('active_other_column',159.867,138.48,6070.04)]:
            with self.subTest(mode=mode):
                target={**base['target_enemy'],'orb_mode':mode}
                mech=calculate_damage({**base,'target_enemy':target,'operator':'mechanist','skill':1})
                self.assertAlmostEqual(mech['total_damage'],physical)
                neutral=calculate_damage({**base,'operator':'mechanist','skill':1})
                self.assertEqual(mech['estimate']['skill']['cycle_seconds'],neutral['estimate']['skill']['cycle_seconds'])
                ratio=.7 if mode=='active_same_column' else .3
                self.assertAlmostEqual(mech['estimate']['skill']['cycle_damage'],neutral['estimate']['skill']['cycle_damage']*ratio)
                amiya=calculate_damage({**base,'target_enemy':target,'operator':'char_1037_amiya3','skill':2})
                components={c['name']:c for c in amiya['components']}
                self.assertAlmostEqual(components['慈悲愿景开启伤害']['total'],magic)
                self.assertAlmostEqual(components['技能攻击']['total'],12001.6)
                self.assertAlmostEqual(components['咒愈师伤害转治疗']['total'],healing)
                self.assertAlmostEqual(components['诚挚期许本体生命回复']['total'],1327.104)

    def test_orb_unknown_context_is_prominent_in_report_before_damage_numbers(self):
        from rouge.reporting import format_report
        args={'operator':'mechanist','skill':1,
            'target_enemy':{'stage_id':'ro6_b_5','enemy_id':'enemy_2148_shorbb','level':0},
            'run_config':{'difficulty':{'value':11}}}
        result=calculate_damage(args)
        self.assertFalse(result['complete'])
        self.assertNotIn('type_factors',result['run_resolution']['enemy'])
        self.assertIn('未套用自身减伤的参考', '\n'.join(format_report(result).splitlines()[:4]))
        with self.assertRaises(ValueError):
            calculate_damage({**args,'target_enemy':{**args['target_enemy'],'orb_mode':'guess'}})
