import unittest
from rouge.damage import calculate_damage
from rouge.estimate import format_estimate


def evaluate(**extra):
    return calculate_damage({'operator': 'char_437_mizuki', 'skill': 1,
                             'base_attack': 1000, **extra})


class MizukiS1ReferenceTests(unittest.TestCase):
    def test_zero_window_keeps_requested_zero_without_instant_damage(self):
        r = evaluate(window_seconds=0)
        self.assertEqual(r['total_damage'], 0)
        self.assertEqual(r['estimate']['skill']['window_seconds'], 0)
        self.assertFalse(r['mizuki_s1_reference']['source_possible']['window'])

    def test_absent_or_interrupted_target_cannot_create_skill_damage(self):
        for timing in ({'target_windows': []}, {'target_disappears_seconds': 0},
                       {'interrupt_windows': [[0, 3600]]}):
            r = evaluate(timing=timing)
            self.assertEqual(r['total_damage'], 0)
            self.assertEqual(r['estimate']['skill']['total_damage'], 0)
            self.assertFalse(r['mizuki_s1_reference']['source_possible']['cast'])

    def test_late_target_can_supply_exactly_one_attack_reference(self):
        r = evaluate(window_seconds=8, timing={'target_windows': [[3, 8]]})
        self.assertTrue(r['mizuki_s1_reference']['source_possible']['window'])
        self.assertEqual([c['hits'] for c in r['components']], [1, 1])
        times = r['mizuki_s1_reference']['source_acquisition_times']['window']
        self.assertEqual(len(times), 1)
        self.assertGreaterEqual(times[0], 3)

    def test_known_damage_parameters_do_not_invent_actual_bound_events(self):
        r = evaluate()
        ref = r['mizuki_s1_reference']
        self.assertEqual(ref['physical_per_hit_reference'], 3000)
        self.assertEqual(ref['arts_per_hit_reference'], 1500)
        self.assertFalse(ref['skill_binding_verified'])
        self.assertIsNone(r['total_damage'])
        for c in r['components']:
            self.assertIsNone(c['actual_total'])
            self.assertNotIn('instant_event', c)
            self.assertNotIn('times_seconds', c)

    def test_actual_end_and_cycle_do_not_come_from_normal_attack_interval(self):
        skill = evaluate()['estimate']['skill']
        for key in ('duration_seconds', 'initial_seconds', 'recharge_seconds',
                    'cycle_seconds', 'cycle_damage', 'cycle_dps'):
            self.assertIsNone(skill[key])

    def test_window_before_reference_acquisition_has_no_observed_source(self):
        r = evaluate(window_seconds=.1)
        self.assertEqual(r['total_damage'], 0)
        self.assertIsNone(r['estimate']['skill']['total_damage'])

    def test_continuous_reference_does_not_prove_binding(self):
        r = evaluate(timing_mode='continuous', window_seconds=0)
        self.assertEqual(r['total_damage'], 0)
        self.assertFalse(r['mizuki_s1_reference']['skill_binding_verified'])

    def test_report_preserves_reference_and_unknown(self):
        text = format_estimate(evaluate(window_seconds=5))
        self.assertIn('唤醒 · 下次攻击与结束待核验', text)
        self.assertIn('单次物理伤害条件参考：3,000', text)
        self.assertIn('实际技能结束：未知', text)
        self.assertIn('单次技能总伤：未知', text)


if __name__ == '__main__':
    unittest.main()
