"""S1 buff parameters do not establish first-hit attachment or burst timing."""
import copy
import unittest

from rouge.damage import calculate_damage
from rouge.estimate import format_estimate

OP = 'char_1042_phatm2'
RIVER = 'rogue_6_relic_fight_22'


def evaluate(**extra):
    return calculate_damage({'operator': OP, 'skill': 1, 'base_attack': 1000, **extra})


class S1NeuralBoundaryTests(unittest.TestCase):
    def test_default_reference_keeps_arts_and_masks_burst_total(self):
        r = evaluate()
        self.assertIsNone(r['total_damage'])
        self.assertIsNone(r['estimate']['skill']['total_damage'])
        self.assertEqual(r['known_damage_subtotals']['total_damage'], 3000)
        self.assertEqual(r['known_damage_subtotals']['window_damage'], 3000)
        self.assertFalse(any(c['name'] == '神经损伤爆发' for c in r['components']))
        self.assertNotIn('神经损伤爆发', r['estimate']['skill']['hit_counts'])
        self.assertFalse(r['complete'])
        self.assertFalse(r['estimate']['complete'])

    def test_source_amount_is_independent_of_arts_scale_and_enemy_resistance(self):
        r = evaluate(enemy_resistance=90)
        reference = r['neural_s1_reference']
        self.assertEqual(reference['direct_buildup_raw'], 300)
        self.assertEqual(reference['binding_multiplier'], 1.8)
        self.assertEqual(reference['binding_duration_seconds'], 3)
        self.assertFalse(reference['binding_multiplier_applied'])
        self.assertFalse(reference['first_attachment_verified'])
        self.assertFalse(reference['refresh_order_verified'])
        self.assertAlmostEqual(r['known_damage_subtotals']['total_damage'], 300)
        buildup = next(c for c in r['components'] if c['damage_type'] == 'buildup')
        self.assertEqual(buildup['total'], 600)
        self.assertIsNone(buildup['actual_total'])

    def test_single_hit_window_is_unknown_even_when_unscaled_reference_does_not_burst(self):
        r = evaluate(window_seconds=.51, initial_neural_buildup=500)
        self.assertIsNone(r['total_damage'])
        self.assertEqual(r['known_damage_subtotals']['window_damage'], 1500)
        self.assertEqual(r['neural_s1_reference']['qualified_hit_times']['window'], [.5])

    def test_no_hit_window_keeps_known_zero_and_full_cast_unknown(self):
        for window in (0, .5):
            with self.subTest(window=window):
                r = evaluate(window_seconds=window)
                self.assertEqual(r['total_damage'], 0)
                self.assertIsNone(r['estimate']['skill']['total_damage'])
                self.assertEqual(r['known_damage_subtotals']['window_damage'], 0)
                self.assertFalse(r['neural_s1_reference']['affected_damage_phases']['window'])

    def test_window_end_excludes_second_reference_hit(self):
        for window, known in ((.9, 1500), (.91, 3000)):
            with self.subTest(window=window):
                r = evaluate(window_seconds=window)
                self.assertIsNone(r['total_damage'])
                self.assertEqual(r['known_damage_subtotals']['window_damage'], known)

    def test_disappearance_preserves_first_arts_hit_only(self):
        r = evaluate(timing={'target_disappears_seconds': .8})
        self.assertEqual(r['known_damage_subtotals']['total_damage'], 1500)
        self.assertIsNone(r['total_damage'])
        self.assertEqual(r['neural_s1_reference']['qualified_hit_times']['cast'], [.5])

    def test_no_target_does_not_create_binding_or_unknown_damage(self):
        for timing in ({'target_windows': []}, {'target_disappears_seconds': 0}):
            with self.subTest(timing=timing):
                r = evaluate(timing=timing)
                self.assertEqual(r['total_damage'], 0)
                self.assertEqual(r['estimate']['skill']['total_damage'], 0)
                self.assertNotIn('neural_s1_reference', r)

    def test_buildup_immunity_keeps_arts_total_known(self):
        r = evaluate(enemy_buildup_resistance=100)
        self.assertEqual(r['total_damage'], 3000)
        self.assertEqual(r['estimate']['skill']['total_damage'], 3000)
        self.assertNotIn('neural_s1_reference', r)

    def test_zero_attack_has_no_unknown_damage_from_a_zero_source(self):
        r = evaluate(base_attack=0)
        self.assertEqual(r['total_damage'], 0)
        self.assertNotIn('neural_s1_reference', r)

    def test_preexisting_break_suppresses_buildup_before_its_end(self):
        r = evaluate(enemy_in_neural_break=True)
        self.assertEqual(r['total_damage'], 3000)
        self.assertNotIn('neural_s1_reference', r)
        later = evaluate(enemy_in_neural_break=True,
                         timing={'start_delay_frames': 300}, window_seconds=12)
        self.assertIsNone(later['total_damage'])
        self.assertEqual(later['neural_s1_reference']['qualified_hit_times']['window'], [10.5, 10.9])

    def test_boss_threshold_and_high_initial_buildup_do_not_restore_a_burst_schedule(self):
        for boss, initial in ((False, 999), (True, 1999)):
            with self.subTest(boss=boss):
                r = evaluate(enemy_is_boss=boss, initial_neural_buildup=initial)
                self.assertIsNone(r['total_damage'])
                self.assertFalse(any(c['name'] == '神经损伤爆发' for c in r['components']))
                self.assertEqual(r['known_damage_subtotals']['total_damage'], 3000)

    def test_skill_rank_and_potential_use_pinned_parameters_only(self):
        for rank, potential in ((1, 1), (7, 3), (10, 6)):
            with self.subTest(rank=rank, potential=potential):
                r = evaluate(skill_rank=rank, potential=potential)
                reference = r['neural_s1_reference']
                self.assertAlmostEqual(reference['direct_buildup_raw'], 330 if potential >= 3 else 300)
                self.assertIsNone(r['total_damage'])

    def test_continuous_mode_does_not_reintroduce_unverified_multiplier(self):
        r = evaluate(timing_mode='continuous')
        self.assertIsNone(r['total_damage'])
        self.assertEqual(r['known_damage_subtotals']['total_damage'], 3000)
        self.assertEqual(r['neural_s1_reference']['qualified_hit_times']['cast'], [.5, .9])

    def test_river_and_elemental_resistance_do_not_restore_unknown_bursts(self):
        r = evaluate(relic_ids=[RIVER], initial_neural_buildup=999,
                     enemy_elemental_resistance=50)
        self.assertIsNone(r['total_damage'])
        self.assertEqual(r['known_damage_subtotals']['total_damage'], 3000)
        river = r['neural_relic_reference']
        self.assertIsNone(river['cast_burst_times'])
        self.assertIsNone(river['window_burst_times'])
        self.assertEqual(river['burst_schedule_status'], 'unknown_due_to_s1_binding')
        self.assertTrue(river['periodic_damage_possible'])

    def test_report_distinguishes_parameter_base_reference_and_actual_unknowns(self):
        text = format_estimate(evaluate())
        for label in ('暗夜回声 · 束缚倍率待核验', '单次技能总伤：未知',
                      '潜在损伤积累：未知', '当前情景损伤爆发次数：未知',
                      '单次技能已计伤害小计：3,000', '单段未计束缚倍率的损伤基础参考：300'):
            self.assertIn(label, text)
        self.assertNotIn('元素伤害已在总伤中计入', text)

    def test_unknown_lifecycle_and_known_attributes_are_preserved(self):
        r = evaluate()
        skill = r['estimate']['skill']
        self.assertEqual(skill['initial_seconds'], 0)
        self.assertEqual(skill['total_healing'], 0)
        self.assertEqual(r['estimate']['base_stats']['attack'], 1000)
        for key in ('duration_seconds', 'recharge_seconds', 'cycle_seconds', 'cycle_damage'):
            self.assertIsNone(skill[key])

    def test_unrelated_skills_and_operators_have_no_s1_boundary(self):
        for op, skill in ((OP, 2), (OP, 3), ('mechanist', 1), ('char_4204_mantra', 2)):
            r = evaluate(operator=op, skill=skill)
            self.assertNotIn('neural_s1_reference', r)
            self.assertNotIn('暗夜回声 · 束缚倍率待核验', format_estimate(r))

    def test_caller_input_is_preserved(self):
        args = {'operator': OP, 'skill': 1, 'relic_ids': [RIVER],
                'timing': {'target_windows': [[0, 2]]}}
        before = copy.deepcopy(args)
        calculate_damage(args)
        self.assertEqual(args, before)


if __name__ == '__main__':
    unittest.main()
