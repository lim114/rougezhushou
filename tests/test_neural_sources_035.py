"""No source-free buildup; unsupported secondary clocks remain unknown."""
import copy,unittest
from rouge.damage import calculate_damage
from rouge.estimate import format_estimate

OP='char_1042_phatm2';RIVER='rogue_6_relic_fight_22'


def scenario(**extra):
    return {'operator':OP,'skill':3,'enemy_resistance':0,**extra}


def calculate(**extra):return calculate_damage(scenario(**extra))


class NeuralSources035Tests(unittest.TestCase):
    def test_empty_supply_does_not_create_neural_damage_or_bursts(self):
        for ids in ([],[RIVER]):
            r=calculate(relic_ids=ids,timing={'target_windows':[]})
            self.assertEqual(r['total_damage'],0)
            self.assertEqual(r['estimate']['skill']['total_damage'],0)
            self.assertNotIn('neural_skill_reference',r)
            self.assertEqual(sum(c['total'] for c in r['components']),0)

    def test_target_arriving_after_skill_has_no_skill_secondary_source(self):
        r=calculate(timing={'target_windows':[[40,100]]})
        self.assertEqual(r['total_damage'],0)
        self.assertEqual(r['estimate']['skill']['total_damage'],0)
        self.assertNotIn('neural_skill_reference',r)
        self.assertIsNotNone(r['estimate']['skill']['cycle_damage'])

    def test_disappeared_target_cannot_activate_a_secondary_source(self):
        r=calculate(timing={'target_disappears_seconds':.1})
        self.assertEqual(r['total_damage'],0)
        self.assertNotIn('neural_skill_reference',r)

    def test_delayed_first_impact_does_not_create_early_buildup(self):
        r=calculate(window_seconds=2,timing={'projectile_travel_seconds':10})
        self.assertEqual(r['total_damage'],0)
        self.assertFalse(r['neural_skill_reference']['affected_damage_phases']['window'])
        self.assertIsNone(r['estimate']['skill']['total_damage'])

    def test_one_second_window_before_first_hit_retains_known_zero(self):
        r=calculate(window_seconds=1)
        self.assertEqual(r['total_damage'],0)
        self.assertEqual(r['estimate']['skill']['window_dps'],0)
        self.assertEqual(r['known_damage_subtotals']['window_damage'],0)

    def test_after_first_hit_secondary_clock_and_full_damage_are_unknown(self):
        r=calculate(window_seconds=2)
        self.assertIsNone(r['total_damage'])
        self.assertIsNone(r['estimate']['skill']['total_damage'])
        self.assertIsNone(r['estimate']['skill']['cycle_dps'])
        reference=r['neural_skill_reference']
        self.assertEqual(reference['qualified_seed_times']['window'],[1.6])
        self.assertEqual(reference['periodic_buildup_ratio'],.1)
        self.assertEqual(reference['periodic_buildup_raw'],119.25)
        self.assertEqual(reference['periodic_interval'],1)
        self.assertIsNone(reference['first_tick_seconds'])
        self.assertFalse(reference['secondary_events_scheduled'])

    def test_known_arts_subtotals_match_independent_continuous_count(self):
        r=calculate(timing_mode='continuous',base_attack=1000)
        # E2 S3 +125%: 18 ordinary 2250 arts hits, followed by 25 base 1000 hits.
        known=r['known_damage_subtotals']
        self.assertEqual(known['total_damage'],40500)
        self.assertEqual(known['cycle_damage'],65500)
        self.assertAlmostEqual(known['cycle_dps'],65500/70)
        self.assertFalse(any(c['name']=='神经损伤爆发' for c in r['components']))

    def test_potential_buildup_contains_direct_sources_only(self):
        r=calculate(timing_mode='continuous',base_attack=1000)
        buildup=next(c for c in r['components'] if c['damage_type']=='buildup')
        self.assertEqual(buildup['total'],18*2250*.3)

    def test_direct_only_burst_count_is_not_presented_as_actual_count(self):
        r=calculate()
        self.assertNotIn('神经损伤爆发',r['estimate']['skill']['hit_counts'])
        self.assertIn('当前情景损伤爆发次数：未知',format_estimate(r))

    def test_buildup_immunity_does_not_activate_secondary_damage(self):
        r=calculate(enemy_buildup_resistance=100)
        self.assertNotIn('neural_skill_reference',r)
        self.assertEqual(r['total_damage'],21465)

    def test_range_exit_is_not_used_to_invent_status_removal(self):
        r=calculate(timing={'target_windows':[[0,.1]],'windup_frames':0,'recovery_frames':0})
        self.assertIsNone(r['total_damage'])
        self.assertEqual(r['known_damage_subtotals']['window_damage'],1192.5)
        self.assertIn('不假设离开范围就终止',format_estimate(r))

    def test_neural_burst_resistance_does_not_change_the_known_arts_subtotal(self):
        base=calculate();resisted=calculate(enemy_elemental_resistance=50)
        self.assertEqual(base['known_damage_subtotals'],resisted['known_damage_subtotals'])

    def test_river_does_not_restore_an_unsupported_burst_schedule(self):
        base=calculate();r=calculate(relic_ids=[RIVER])
        self.assertEqual(base['known_damage_subtotals'],r['known_damage_subtotals'])
        self.assertIsNone(r['neural_relic_reference']['cast_burst_times'])
        self.assertIsNone(r['neural_relic_reference']['window_burst_times'])
        self.assertIsNone(r['neural_relic_reference']['cycle_burst_times'])
        self.assertEqual(r['neural_relic_reference']['instant_raw_damage'],12000)
        self.assertTrue(r['neural_relic_reference']['periodic_damage_possible'])
        self.assertFalse(r['neural_relic_reference']['periodic_damage_scheduled'])

    def test_cycle_initial_recharge_healing_and_attributes_are_preserved(self):
        for ids in ([],[RIVER]):
            r=calculate(relic_ids=ids)
            self.assertEqual(r['estimate']['skill']['initial_seconds'],10)
            self.assertEqual(r['estimate']['skill']['recharge_seconds'],40)
            self.assertEqual(r['estimate']['skill']['cycle_seconds'],70)
            self.assertEqual(r['estimate']['skill']['total_healing'],0)
            self.assertEqual(r['estimate']['base_stats']['attack'],530)

    def test_report_does_not_mention_river_when_not_selected(self):
        text=format_estimate(calculate())
        self.assertIn('空剧场 · 持续损伤待核验',text)
        self.assertIn('单次技能总伤：未知',text)
        self.assertIn('单次技能已计伤害小计：21,465',text)
        self.assertNotIn('河谷祭祈',text)

    def test_reference_section_absent_on_other_skill_and_operator(self):
        for op,skill in ((OP,1),(OP,2),('char_4204_mantra',2),('mechanist',3)):
            r=calculate(operator=op,skill=skill)
            self.assertNotIn('neural_skill_reference',r)
            self.assertNotIn('空剧场 · 持续损伤待核验',format_estimate(r))

    def test_skill_rank_changes_reference_from_pinned_skill_attack(self):
        for rank in (1,7,10):
            r=calculate(skill_rank=rank)
            self.assertAlmostEqual(r['neural_skill_reference']['periodic_buildup_raw'],
                                   r['estimate']['skill']['skill_attack']*.1)

    def test_enemy_phase_and_relic_combinations_do_not_make_unknown_full_output_finite(self):
        r=calculate(relic_ids=[RIVER,'rogue_6_relic_fight_21'],enemy_is_boss=True)
        self.assertIsNone(r['total_damage'])
        self.assertIsNone(r['estimate']['skill']['cycle_dps'])

    def test_s1_has_no_neural_source_when_the_attack_was_not_emitted(self):
        for timing in ({'target_windows':[]},{'target_disappears_seconds':0},
                       {'movement_windows':[[0,2]]}):
            r=calculate(skill=1,initial_neural_buildup=999,timing=timing)
            self.assertEqual(r['total_damage'],0)
            self.assertEqual(sum(c['total'] for c in r['components'] if c['damage_type']=='buildup'),0)

    def test_input_is_not_mutated(self):
        s=scenario(relic_ids=[RIVER],timing={'target_windows':[[0,2]]})
        before=copy.deepcopy(s);calculate_damage(s)
        self.assertEqual(s,before)


if __name__=='__main__':unittest.main()
