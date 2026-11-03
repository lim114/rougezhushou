import unittest
from rouge.damage import calculate_damage
from rouge.estimate import format_estimate


def evaluate(**extra):
    return calculate_damage({'operator': 'char_1015_aglna2', 'skill': 2,
                             'base_attack': 1000, **extra})


class AglnaLiftoffReferenceTests(unittest.TestCase):
    def test_requested_short_horizon_is_not_extended_by_chant(self):
        for window in (0, .1, 1, 2, 2.5, 10):
            r = evaluate(window_seconds=window)
            self.assertEqual(r['estimate']['skill']['window_seconds'], window)
        self.assertEqual(evaluate(window_seconds=0)['total_damage'], 0)

    def test_positive_short_window_does_not_prove_actual_takeoff_or_no_hits(self):
        r = evaluate(window_seconds=1)
        self.assertIsNone(r['total_damage'])
        self.assertEqual(r['aglna_liftoff_reference']['window_attack_phase_reference']['conditional_damage'], 0)
        self.assertIsNone(r['aglna_liftoff_reference']['actual_takeoff_seconds'])

    def test_default_conditional_parameters_are_retained_separately(self):
        r = evaluate()
        ref = r['aglna_liftoff_reference']
        self.assertEqual(ref['chant_duration_parameter_seconds'], 2.5)
        self.assertEqual(ref['nominal_skill_duration_parameter_seconds'], 22)
        self.assertEqual(ref['cast_attack_phase_reference']['attack_phase_seconds'], 19.5)
        self.assertEqual(ref['cast_attack_phase_reference']['conditional_damage'], 101331)
        self.assertFalse(ref['lifecycle_binding_verified'])
        self.assertIsNone(r['total_damage'])

    def test_isolated_phase_events_are_not_published_as_absolute_hit_times(self):
        r = evaluate()
        self.assertEqual(r['timing']['streams'], [])
        self.assertFalse(r['timing']['resource_and_damage_shared_clock'])
        self.assertTrue(r['aglna_liftoff_reference']['cast_attack_phase_reference']['timing']['streams'])
        for c in r['components']:
            self.assertNotIn('times_seconds', c)
            self.assertIsNone(c['actual_total'])
            self.assertIn('absolute takeoff binding unverified', c['timing_reference'])

    def test_no_living_or_available_target_has_no_source(self):
        for timing in ({'target_disappears_seconds': 0}, {'target_windows': []}):
            r = evaluate(timing=timing)
            self.assertEqual(r['total_damage'], 0)

    def test_unverified_end_does_not_create_cycle(self):
        skill = evaluate()['estimate']['skill']
        for key in ('duration_seconds', 'recharge_seconds', 'cycle_seconds', 'cycle_damage', 'cycle_dps'):
            self.assertIsNone(skill[key])
        self.assertEqual(skill['initial_seconds'], 4)

    def test_continuous_keeps_requested_zero_and_unknown_absolute_phase(self):
        r = evaluate(timing_mode='continuous', window_seconds=0)
        self.assertEqual(r['total_damage'], 0)
        self.assertEqual(r['estimate']['skill']['window_seconds'], 0)
        self.assertIsNone(r['aglna_liftoff_reference']['actual_takeoff_seconds'])

    def test_report_distinguishes_parameter_from_binding(self):
        text = format_estimate(evaluate(window_seconds=1))
        self.assertIn('重力自定义 · 起飞阶段待核验', text)
        self.assertIn('实际起飞时刻：未知', text)
        self.assertIn('吟唱时长参数参考：2.50', text)
        self.assertIn('伤害观察窗口：1', text)
        self.assertIn('单次技能总伤：未知', text)


if __name__ == '__main__':
    unittest.main()
