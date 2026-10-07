import unittest
import json
from pathlib import Path
from rouge.damage import calculate_damage
from rouge.estimate import format_estimate


def evaluate(skill, **extra):
    return calculate_damage({'operator':'char_1029_yato2','skill':skill,'base_attack':1000,**extra})


def sources(result):
    return {c['name']:c for c in result['unbound_cast_reference']['conditional_components']}


class YatoDeploymentReferenceTests(unittest.TestCase):
    def test_both_skills_preserve_zero_short_and_long_observation_windows(self):
        for skill in (2,3):
            for mode in ('frames','continuous'):
                for window in (0,1,10):
                    with self.subTest(skill=skill,mode=mode,window=window):
                        r=evaluate(skill,timing_mode=mode,window_seconds=window)
                        self.assertEqual(r['estimate']['skill']['window_seconds'],window)
                        if window==0:
                            self.assertEqual(r['total_damage'],0)
                            self.assertTrue(all(c['hits']==0 and c['total']==0 for c in r['components']))
                        else:self.assertIsNone(r['total_damage'])

    def test_zero_target_lifetime_excludes_damage_even_with_declared_dash_hits(self):
        for skill in (2,3):
            for mode in ('frames','continuous'):
                for extra in ({},{'window_seconds':1}):
                    r=evaluate(skill,timing_mode=mode,timing={'target_disappears_seconds':0},dash_hits=3,**extra)
                    self.assertEqual(r['total_damage'],0)
                    self.assertFalse(r['unbound_cast_reference']['source_possible'])
                    self.assertTrue(all(c['hits']==0 and c['total']==0 for c in r['components']))
                    self.assertGreater(sum(c['total'] for c in sources(r).values()),0)

    def test_owner_supply_and_interrupt_windows_do_not_prove_path_cancellation(self):
        for skill in (2,3):
            for mode in ('frames','continuous'):
                for timing in ({'target_windows':[]},{'target_windows':[[5,10]]},{'interrupt_windows':[[0,3600]]}):
                    r=evaluate(skill,timing_mode=mode,timing=timing,window_seconds=10)
                    self.assertTrue(r['unbound_cast_reference']['source_possible'])
                    self.assertIsNone(r['total_damage'])
                    self.assertGreater(sum(c['total'] for c in sources(r).values()),0)

    def test_s2_preserves_sixteen_per_hit_mitigated_sources_and_talent_coefficient(self):
        r=evaluate(2,enemy_defense=100,enemy_resistance=50)
        refs=sources(r)
        self.assertEqual(refs['乱舞']['hits'],16)
        self.assertAlmostEqual(refs['乱舞']['per_hit'],1595)
        self.assertAlmostEqual(refs['强化双雷剑麒麟']['per_hit'],423.75)
        self.assertAlmostEqual(sum(c['total'] for c in refs.values()),32300)
        parameters={label:value for label,value,_ in r['unbound_cast_reference']['parameter_rows']}
        self.assertEqual(parameters['物理斩击倍率参数'],1.5)
        self.assertEqual(parameters['第一天赋运算倍率参数'],3.75)
        self.assertEqual(r['estimate']['skill']['skill_attack'],1130)

    def test_attack_speed_cannot_change_fixed_or_declared_conditional_counts(self):
        for skill in (2,3):
            extra={'dash_hits':3} if skill==3 else {}
            base=evaluate(skill,**extra)
            fast=evaluate(skill,effects=[{'kind':'attack_speed','value':100}],**extra)
            self.assertEqual(sources(base),sources(fast))
            self.assertEqual(base['timing']['streams'],[])
            self.assertEqual(fast['timing']['streams'],[])

    def test_s3_declared_zero_one_multiple_and_maximum_hits_remain_conditional(self):
        for mode in ('frames','continuous'):
            for count in (0,1,3,100):
                r=evaluate(3,timing_mode=mode,dash_hits=count,window_seconds=1,enemy_defense=100,enemy_resistance=50)
                refs=sources(r)
                self.assertEqual(refs['空中回旋乱舞']['hits'],count)
                self.assertEqual(refs['双雷剑麒麟']['hits'],count)
                self.assertAlmostEqual(refs['空中回旋乱舞']['total'],3290*count)
                self.assertAlmostEqual(refs['双雷剑麒麟']['total'],339*count)
                if count:self.assertIsNone(r['total_damage'])
                else:self.assertEqual(r['total_damage'],0)

    def test_s3_positive_declared_count_with_zero_window_keeps_only_the_reference(self):
        for mode in ('frames','continuous'):
            r=evaluate(3,timing_mode=mode,dash_hits=3,window_seconds=0)
            self.assertEqual(r['total_damage'],0)
            self.assertEqual(r['estimate']['skill']['window_seconds'],0)
            self.assertEqual(sum(c['total'] for c in sources(r).values()),12204)
            self.assertFalse(r['unbound_cast_reference']['window_reference']['source_possible'])

    def test_s3_preserves_existing_public_count_validation(self):
        for value in (-1,.5,101,float('nan'),float('inf')):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError,'dash_hits'):
                    evaluate(3,dash_hits=value)

    def test_deployment_initial_zero_and_nonrepeat_survive_unknown_cast_end(self):
        for skill in (2,3):
            for mode in ('frames','continuous'):
                r=evaluate(skill,timing_mode=mode,window_seconds=1)
                s=r['estimate']['skill']
                self.assertEqual(s['mode'],'deployment')
                self.assertEqual(s['initial_seconds'],0)
                for key in ('duration_seconds','recharge_seconds','cycle_seconds','total_damage','phase_damage','cycle_damage','cycle_dps'):
                    self.assertIsNone(s[key])
                self.assertIsNone(r['unbound_cast_reference']['actual_end_seconds'])
                self.assertIsNone(r['unbound_cast_reference']['actual_hit_times_seconds'])
                self.assertTrue(r['timing']['phase_clock_unbound'])
                self.assertFalse(r['complete'])
                for c in r['components']:
                    self.assertNotIn('times_seconds',c)
                    self.assertNotIn('instant_event',c)
                    self.assertIsNone(c['actual_total'])
                    self.assertIsNone(s['hit_counts'][c['name']])

    def test_report_distinguishes_conditional_slashes_and_distance_parameters(self):
        text=format_estimate(evaluate(2,window_seconds=1))
        self.assertIn('乱舞条件总量：27,120',text)
        self.assertIn('斩击数量参数：16',text)
        self.assertIn('第一天赋运算倍率参数：3.75',text)
        self.assertIn('观察窗口总伤：未知',text)
        self.assertIn('实际命中时刻：未知',text)
        self.assertIn('伤害观察窗口：1.00',text)
        dash=format_estimate(evaluate(3,dash_hits=3,window_seconds=1))
        self.assertIn('声明回旋命中次数：3',dash)
        self.assertIn('基础突进距离参数：2',dash)
        self.assertIn('最大突进距离参数：5',dash)
        receipt=json.loads((Path(__file__).resolve().parents[1]/'research/p2-yato-deployment-reference/source-receipt.json').read_text())
        raw=receipt['selectors']['skill_table.skchr_yato2_3.levels[9]']
        blackboard={item['key']:item['value'] for item in raw['blackboard']}
        self.assertEqual(blackboard['dist_interval'],.2)
        self.assertEqual(blackboard['dist_unit'],.3)
        self.assertEqual(raw['durationType'],'NONE')
        self.assertEqual(raw['duration'],-1)
        self.assertNotIn('突进距离间隔参数',dash)
        self.assertNotIn('突进距离单位参数',dash)

    def test_s1_remains_on_its_existing_attack_model(self):
        for mode in ('frames','continuous'):
            r=evaluate(1,timing_mode=mode,window_seconds=1,enemy_defense=100,enemy_resistance=50)
            self.assertNotIn('unbound_cast_reference',r)
            self.assertEqual(r['total_damage'],4572)
            self.assertEqual(r['estimate']['skill']['duration_seconds'],20)
            self.assertEqual(r['estimate']['skill']['mode'],'deployment')


if __name__=='__main__':unittest.main()
