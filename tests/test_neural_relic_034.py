"""Evidence-backed neural burst parts must not masquerade as complete damage."""
import copy
import unittest

from rouge.damage import calculate_damage
from rouge.estimate import format_estimate

RIVER='rogue_6_relic_fight_22'
ICE='rogue_6_relic_fight_21'


def scenario(**extra):
    return {'operator':'char_4204_mantra','skill':2,'enemy_resistance':0,
            'initial_neural_buildup':999,'window_seconds':1,**extra}


def calculate(**extra):
    return calculate_damage(scenario(**{'relic_ids':[RIVER],**extra}))


def component(result,name):
    return next(c for c in result['components'] if c['name']==name)


class NeuralRelic034Tests(unittest.TestCase):
    def test_burst_is_doubled_before_elemental_resistance(self):
        r=calculate(enemy_elemental_resistance=20)
        self.assertEqual(component(r,'神经损伤爆发')['per_hit'],9600)
        self.assertEqual(r['neural_relic_reference']['instant_raw_damage'],12000)
        self.assertEqual(r['neural_relic_reference']['periodic_raw_damage'],1000)
        self.assertEqual(r['neural_relic_reference']['periodic_interval'],1)

    def test_attached_elements_and_damage_based_buildup_do_not_inherit_burst_factor(self):
        base=calculate_damage(scenario(enemy_elemental_resistance=20))
        r=calculate(enemy_elemental_resistance=20)
        for name in ('爆发期间附带元素','潜在神经损伤积累（不是生命伤害）'):
            self.assertEqual(component(base,name),component(r,name))
        self.assertEqual(component(r,'爆发期间附带元素')['per_hit'],151)

    def test_known_window_subtotal_uses_independent_single_hit_example(self):
        r=calculate()
        # 755*2.4 arts + 12000 burst + 755*.25 attached element.
        self.assertEqual(r['known_damage_subtotals']['window_damage'],14000.75)
        self.assertIsNone(r['total_damage'])
        self.assertIsNone(r['estimate']['skill']['total_damage'])
        self.assertIsNone(r['estimate']['skill']['cycle_dps'])
        self.assertIsNone(r['estimate']['skill']['window_dps'])
        self.assertFalse(r['complete'])
        self.assertFalse(r['estimate']['complete'])

    def test_resisted_known_subtotal_is_11563(self):
        self.assertEqual(calculate(enemy_elemental_resistance=20)['known_damage_subtotals']['window_damage'],11563)

    def test_window_before_the_first_burst_retains_known_zero(self):
        timing={'windup_frames':6,'recovery_frames':0,'projectile_travel_seconds':.5}
        r=calculate(window_seconds=.7,timing=timing)
        self.assertEqual(r['total_damage'],0)
        self.assertEqual(r['estimate']['skill']['window_dps'],0)
        self.assertFalse(r['neural_relic_reference']['affected_damage_phases']['window'])
        self.assertIsNone(r['estimate']['skill']['total_damage'])
        after=calculate(window_seconds=.8,timing=timing)
        self.assertIsNone(after['total_damage'])
        self.assertEqual(after['known_damage_subtotals']['window_damage'],14000.75)

    def test_zero_supply_has_no_invented_periodic_damage(self):
        r=calculate(initial_neural_buildup=0,timing={'target_windows':[],'initial_target_windows':[]})
        self.assertEqual(r['total_damage'],0)
        self.assertEqual(r['estimate']['skill']['total_damage'],0)
        self.assertNotIn('known_damage_subtotals',r)
        self.assertFalse(r['neural_relic_reference']['periodic_damage_possible'])

    def test_unverified_phantom_recharge_does_not_erase_known_skill_or_window(self):
        # A historical3.2s recharge burst used an unverified S1 end/resume.
        r=calculate(operator='char_1042_phatm2',skill=1,initial_neural_buildup=400)
        self.assertEqual(r['total_damage'],1590)
        self.assertEqual(r['estimate']['skill']['total_damage'],1590)
        self.assertIsNone(r['estimate']['skill']['cycle_damage'])
        self.assertEqual(r['neural_relic_reference']['affected_damage_phases'],
                         {'cast':False,'window':False,'cycle':False})
        self.assertEqual(r['neural_relic_reference']['cycle_burst_times'],[])

    def test_elemental_vulnerability_applies_without_doubling_the_attached_source(self):
        r=calculate(relic_ids=[RIVER,ICE],enemy_elemental_resistance=20)
        self.assertEqual(component(r,'神经损伤爆发')['per_hit'],16800)
        self.assertEqual(component(r,'爆发期间附带元素')['per_hit'],264.25)

    def test_boss_threshold_and_burst_times_are_not_changed_by_the_relic(self):
        for mode in ('frames','continuous'):
            s=scenario(enemy_is_boss=True,initial_neural_buildup=1999,timing_mode=mode,
                       window_seconds=30)
            base=calculate_damage(s);r=calculate_damage({**s,'relic_ids':[RIVER]})
            before=component(base,'神经损伤爆发');after=component(r,'神经损伤爆发')
            self.assertEqual(before['times_seconds'],after['times_seconds'])
            self.assertEqual(before['hits'],after['hits'])
            self.assertEqual(after['per_hit'],12000)

    def test_source_free_burst_does_not_scale_with_caster_attack(self):
        r=calculate(effects=[{'kind':'attack_pct','value':1}])
        self.assertEqual(component(r,'神经损伤爆发')['per_hit'],12000)
        self.assertEqual(component(r,'爆发期间附带元素')['per_hit'],377.5)

    def test_initial_break_does_not_create_a_fake_new_burst_or_ten_ticks(self):
        r=calculate(enemy_in_neural_break=True,initial_neural_buildup=0,
                    timing={'target_windows':[],'initial_target_windows':[]})
        self.assertTrue(r['neural_relic_reference']['preexisting_break_assumed'])
        self.assertEqual(r['neural_relic_reference']['cast_burst_times'],[])
        self.assertIsNone(r['total_damage'])
        self.assertFalse(any('河谷' in c['name'] for c in r['components']))
        self.assertFalse(r['neural_relic_reference']['periodic_damage_scheduled'])

    def test_initial_recharge_cycle_and_healing_are_unchanged(self):
        for mode in ('frames','continuous'):
            for op,skills in (('char_4204_mantra',(1,2)),('char_1042_phatm2',(1,2,3))):
                for skill in skills:
                    with self.subTest(mode=mode,op=op,skill=skill):
                        s=scenario(operator=op,skill=skill,timing_mode=mode)
                        base=calculate_damage(s);r=calculate_damage({**s,'relic_ids':[RIVER]})
                        self.assertEqual(base['estimate']['base_stats'],r['estimate']['base_stats'])
                        for key in ('initial_seconds','recharge_seconds','cycle_seconds','total_healing','cycle_hps'):
                            self.assertEqual(base['estimate']['skill'][key],r['estimate']['skill'][key])

    def test_duplicate_inventory_does_not_quadruple_the_burst(self):
        r=calculate(relic_ids=[RIVER,RIVER])
        self.assertEqual(component(r,'神经损伤爆发')['per_hit'],12000)

    def test_damage_type_bypasses_physical_defense_and_arts_resistance(self):
        self.assertEqual(component(calculate(enemy_defense=99999,enemy_resistance=90),'神经损伤爆发')['per_hit'],12000)

    def test_no_reference_or_subtotal_section_on_unrelated_operator(self):
        r=calculate(operator='mechanist',skill=3,initial_neural_buildup=0)
        self.assertNotIn('neural_relic_reference',r)
        self.assertNotIn('known_damage_subtotals',r)
        self.assertNotIn('河谷祭祈 · 神经爆发参考',format_estimate(r))
        self.assertNotIn('已建模伤害小计',format_estimate(r))

    def test_known_and_unknown_metrics_have_distinct_report_labels(self):
        text=format_estimate(calculate())
        self.assertIn('单次技能总伤：未知',text)
        self.assertIn('本轮周期每秒伤害：未知',text)
        self.assertIn('观察窗口已计伤害小计：14,000.75',text)
        self.assertIn('额外持续伤害首跳时刻：未知',text)
        self.assertNotIn('元素伤害已在总伤中计入',text)

    def test_without_relic_original_damage_and_report_are_retained(self):
        r=calculate_damage(scenario())
        self.assertEqual(r['total_damage'],8000.75)
        self.assertNotIn('neural_relic_reference',r)
        self.assertNotIn('known_damage_subtotals',r)

    def test_caller_scenario_is_not_mutated(self):
        s=scenario(relic_ids=[RIVER],timing={'target_windows':[[0,60]]})
        before=copy.deepcopy(s)
        calculate_damage(s)
        self.assertEqual(s,before)


if __name__=='__main__':
    unittest.main()
