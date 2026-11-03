import unittest
from rouge.damage import calculate_damage
from rouge.estimate import format_estimate


def evaluate(**extra):
    return calculate_damage({'operator': 'char_1044_hsgma2', 'skill': 3,
                             'base_attack': 1000, 'last_stand_seconds': 5, **extra})


class ManualCloseReferenceTests(unittest.TestCase):
    def test_zero_window_does_not_generate_or_append_terminal_phase(self):
        r = evaluate(window_seconds=0)
        self.assertEqual(r['total_damage'], 0)
        self.assertEqual(r['estimate']['skill']['window_seconds'], 0)
        self.assertTrue(all(c['hits'] == 0 for c in r['components']))

    def test_short_requested_window_is_not_expanded_by_terminal_duration(self):
        r = evaluate(window_seconds=1)
        self.assertEqual(r['estimate']['skill']['window_seconds'], 1)
        self.assertIsNone(r['total_damage'])

    def test_terminal_duration_is_not_a_close_time_or_attack_schedule(self):
        r = evaluate()
        ref = r['manual_close_reference']
        self.assertEqual(ref['declared_terminal_seconds'], 5)
        self.assertEqual(ref['terminal_limit_parameter_seconds'], 11)
        self.assertIsNone(ref['close_seconds'])
        self.assertIsNone(ref['terminal_hit_times_seconds'])
        tail = next(c for c in r['components'] if c['name'] == '主动关闭后四连击')
        self.assertNotIn('times_seconds', tail)
        self.assertEqual(tail['hits'], 0)
        self.assertIsNone(tail['actual_total'])

    def test_active_phase_count_is_not_actual_without_close_time(self):
        r = evaluate()
        self.assertIsNone(r['estimate']['skill']['hit_counts']['技能攻击'])
        self.assertEqual(r['known_damage_subtotals']['window_damage'], 0)
        self.assertGreater(r['manual_close_reference']['active_body_damage_reference'], 0)
        self.assertIsNone(r['total_damage'])
        self.assertIsNone(r['estimate']['skill']['total_damage'])

    def test_immediate_target_disappearance_is_known_zero(self):
        r = evaluate(timing={'target_disappears_seconds': 0})
        self.assertEqual(r['total_damage'], 0)
        self.assertEqual(r['estimate']['skill']['total_damage'], 0)

    def test_zero_declared_terminal_duration_preserves_existing_reference(self):
        r = evaluate(last_stand_seconds=0)
        self.assertNotIn('manual_close_reference', r)
        self.assertFalse(any(c['name'] == '主动关闭后四连击' for c in r['components']))
        self.assertEqual(r['estimate']['skill']['duration_seconds'], 32)
        self.assertGreater(r['total_damage'], 0)

    def test_unknown_ended_cast_does_not_produce_cycle(self):
        skill = evaluate()['estimate']['skill']
        for key in ('duration_seconds', 'recharge_seconds', 'cycle_seconds', 'cycle_dps'):
            self.assertIsNone(skill[key])

    def test_declared_tail_cannot_exceed_source_limit(self):
        with self.assertRaises(ValueError):
            evaluate(last_stand_seconds=12)

    def test_continuous_and_report_preserve_window_and_unknown(self):
        r = evaluate(timing_mode='continuous', window_seconds=1)
        self.assertEqual(r['estimate']['skill']['window_seconds'], 1)
        self.assertIsNone(r['total_damage'])
        text = format_estimate(r)
        self.assertIn('地狱变相 · 关闭尾段待核验', text)
        self.assertIn('实际主动关闭时刻：未知', text)
        self.assertIn('指定尾段时长参考：5', text)
        self.assertIn('单次技能总伤：未知', text)


if __name__ == '__main__':
    unittest.main()
