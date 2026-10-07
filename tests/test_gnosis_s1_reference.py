import unittest

from rouge.damage import calculate_damage
from rouge.estimate import format_estimate


def evaluate(**extra):
    return calculate_damage({'operator': 'char_206_gnosis', 'skill': 1,
                             'base_attack': 1000, **extra})


class GnosisS1ReferenceTests(unittest.TestCase):
    def test_no_target_cannot_create_two_hits(self):
        for extra in ({'target_windows': []}, {'target_disappears_seconds': 0},
                      {'interrupt_windows': [[0, 3600]]}):
            r = evaluate(timing=extra)
            self.assertEqual(r['total_damage'], 0)
            self.assertFalse(r['gnosis_s1_reference']['source_possible']['cast'])
            self.assertEqual(r['estimate']['skill']['total_damage'], 0)

    def test_zero_window_is_known_zero_without_two_hits(self):
        r = evaluate(window_seconds=0)
        self.assertEqual(r['total_damage'], 0)
        self.assertFalse(r['gnosis_s1_reference']['source_possible']['window'])

    def test_possible_source_retains_reference_but_does_not_invent_gap(self):
        r = evaluate(window_seconds=5)
        self.assertEqual(r['gnosis_s1_reference']['two_hit_damage_reference'], 3400)
        self.assertIsNone(r['gnosis_s1_reference']['relative_hit_times_seconds'])
        self.assertIsNone(r['total_damage'])
        self.assertIsNone(r['estimate']['skill']['total_damage'])
        self.assertNotIn('times_seconds', r['components'][0])
        self.assertIsNone(r['components'][0]['actual_total'])

    def test_second_hit_and_end_unknown_do_not_produce_cycle(self):
        r = evaluate(window_seconds=5)
        skill = r['estimate']['skill']
        self.assertIsNone(skill['initial_seconds'])
        for key in ('duration_seconds', 'recharge_seconds', 'cycle_seconds',
                    'cycle_damage', 'cycle_dps'):
            self.assertIsNone(skill[key])

    def test_insufficient_sp_does_not_invent_first_cast_time(self):
        self.assertIsNone(evaluate()['estimate']['skill']['initial_seconds'])

    def test_acquisition_after_nominal_interval_is_not_lost(self):
        r = evaluate(window_seconds=20, timing={'target_windows': [[10, 20]]})
        self.assertTrue(r['gnosis_s1_reference']['source_possible']['cast'])
        self.assertTrue(r['gnosis_s1_reference']['source_possible']['window'])
        self.assertTrue(all(t >= 10 for t in
                            r['gnosis_s1_reference']['source_acquisition_times']['cast']))
        self.assertIsNone(r['total_damage'])

    def test_continuous_reference_cannot_become_a_verified_two_hit_clock(self):
        r = evaluate(timing_mode='continuous')
        self.assertFalse(r['gnosis_s1_reference']['multi_event_binding_verified'])
        self.assertIsNone(r['estimate']['skill']['cycle_seconds'])

    def test_report_shows_parameter_reference_and_unknown_interval(self):
        text = format_estimate(evaluate(window_seconds=5))
        self.assertIn('高速思考 · 两段时间待核验', text)
        self.assertIn('实际两段间隔：未知', text)
        self.assertIn('两段合计条件参考：3,400', text)
        self.assertIn('单次技能总伤：未知', text)


if __name__ == '__main__':
    unittest.main()
