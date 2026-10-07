import unittest
from rouge.damage import calculate_damage
from rouge.estimate import format_estimate


def evaluate(**extra):
    return calculate_damage({'operator': 'char_1046_sbell2', 'skill': 2,
                             'base_attack': 1000, **extra})


class SnowFieldReferenceTests(unittest.TestCase):
    def test_no_living_target_does_not_receive_snow_ticks(self):
        for mode in ('frames', 'continuous'):
            r = evaluate(timing_mode=mode, timing={'target_disappears_seconds': 0})
            self.assertEqual(r['total_damage'], 0)
            self.assertFalse(r['snow_field_reference']['source_possible']['window'])

    def test_zero_window_and_zero_coverage_keep_known_zero_source(self):
        for mode in ('frames', 'continuous'):
            r = evaluate(timing_mode=mode, window_seconds=0)
            self.assertEqual(r['total_damage'], 0)
            self.assertEqual(r['estimate']['skill']['window_seconds'], 0)
            r = evaluate(timing_mode=mode, snow_coverage=0)
            body = next(c['total'] for c in r['components'] if c['name'] == '技能攻击')
            self.assertEqual(r['total_damage'], body)
            self.assertFalse(r['snow_field_reference']['source_possible']['window'])

    def test_positive_fraction_does_not_prove_floor_tick_count(self):
        r = evaluate(window_seconds=.1, snow_coverage=.1)
        self.assertIsNone(r['total_damage'])
        self.assertIsNone(r['snow_field_reference']['actual_tick_times_seconds'])
        self.assertEqual(r['estimate']['skill']['window_seconds'], .1)

    def test_no_body_acquisition_does_not_prove_empty_snow_field(self):
        r = evaluate(timing={'target_windows': []})
        self.assertTrue(r['snow_field_reference']['source_possible']['window'])
        self.assertIsNone(r['total_damage'])
        self.assertEqual(r['known_damage_subtotals']['window_damage'], 0)

    def test_parameter_reference_and_known_body_are_distinct(self):
        r = evaluate(window_seconds=10, snow_coverage=.5)
        ref = r['snow_field_reference']
        self.assertEqual(ref['per_tick_damage_reference'], 200)
        self.assertEqual(ref['tick_interval_parameter_seconds'], 1)
        self.assertEqual(ref['declared_coverage_fraction'], .5)
        self.assertIsNone(ref['actual_coverage_windows_seconds'])
        self.assertIsNone(r['total_damage'])
        body = next(c['total'] for c in r['components'] if c['name'] == '技能攻击')
        self.assertEqual(r['known_damage_subtotals']['window_damage'], body)
        snow = next(c for c in r['components'] if c['name'] == '积雪持续伤害')
        self.assertNotIn('times_seconds', snow)
        self.assertIsNone(r['estimate']['skill']['hit_counts']['积雪持续伤害'])

    def test_infinite_skill_window_subtotal_is_not_full_cast_total(self):
        r = evaluate()
        skill = r['estimate']['skill']
        for key in ('duration_seconds', 'total_damage', 'cycle_seconds', 'cycle_damage'):
            self.assertIsNone(skill[key])
        self.assertIsNone(r['known_damage_subtotals']['total_damage'])
        self.assertIsNone(r['known_damage_subtotals']['cycle_damage'])

    def test_report_retains_parameters_and_unknown_actual_output(self):
        text = format_estimate(evaluate(window_seconds=1))
        self.assertIn('积雪场地 · 覆盖与首跳待核验', text)
        self.assertIn('每次积雪跳伤条件参考：200', text)
        self.assertIn('实际积雪跳伤时刻：未知', text)
        self.assertIn('伤害观察窗口：1', text)
        self.assertIn('观察窗口总伤：未知', text)


if __name__ == '__main__':
    unittest.main()
