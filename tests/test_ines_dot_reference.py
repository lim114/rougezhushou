import unittest
from rouge.damage import calculate_damage
from rouge.estimate import format_estimate


def evaluate(**extra):
    return calculate_damage({'operator': 'char_4087_ines', 'skill': 1,
                             'base_attack': 1000, **extra})


class InesDotReferenceTests(unittest.TestCase):
    def test_absent_or_interrupted_target_cannot_create_dot(self):
        for timing in ({'target_windows': []}, {'target_disappears_seconds': 0},
                       {'interrupt_windows': [[0, 3600]]}):
            r = evaluate(timing=timing)
            self.assertEqual(r['total_damage'], 0)
            self.assertFalse(r['ines_dot_reference']['source_possible']['cast'])
            self.assertTrue(all(c['hits'] == 0 for c in r['components']))
            fee = next(s for s in r['report']['sections'] if s['id'] == 'dp')
            self.assertEqual(next(m['value'] for m in fee['metrics'] if m['key'] == 'per_cast'), 0)

    def test_zero_window_is_not_reset_to_attack_interval(self):
        r = evaluate(window_seconds=0)
        self.assertEqual(r['total_damage'], 0)
        self.assertEqual(r['estimate']['skill']['window_seconds'], 0)
        self.assertFalse(r['ines_dot_reference']['source_possible']['window'])

    def test_late_acquisition_can_create_one_source_reference(self):
        r = evaluate(window_seconds=10, timing={'target_windows': [[5, 10]]})
        self.assertTrue(r['ines_dot_reference']['source_possible']['window'])
        physical = next(c for c in r['components'] if c['name'] == '淬影突袭物理攻击')
        self.assertEqual(physical['hits'], 1)
        self.assertGreaterEqual(physical['times_seconds'][0], 5)

    def test_tick_parameters_do_not_invent_three_actual_events(self):
        r = evaluate()
        ref = r['ines_dot_reference']
        self.assertEqual(ref['per_second_damage_reference'], 872)
        self.assertEqual(ref['duration_parameter_seconds'], 3)
        self.assertFalse(ref['dot_stacks'])
        self.assertIsNone(ref['actual_first_tick_seconds'])
        self.assertIsNone(ref['actual_tick_count'])
        dot = next(c for c in r['components'] if c['name'] == '淬影突袭持续法术')
        self.assertEqual(dot['hits'], 0)
        self.assertIsNone(dot['actual_total'])
        self.assertNotIn('times_seconds', dot)

    def test_physical_reference_subtotal_remains_without_full_cycle(self):
        r = evaluate()
        self.assertEqual(r['known_damage_subtotals']['window_damage'], 1090)
        self.assertIsNone(r['total_damage'])
        for key in ('total_damage', 'phase_damage', 'duration_seconds',
                    'recharge_seconds', 'cycle_seconds', 'cycle_damage'):
            self.assertIsNone(r['estimate']['skill'][key])
        self.assertEqual(r['estimate']['skill']['initial_seconds'], 0)

    def test_declared_preexisting_attack_steal_is_preserved(self):
        r = evaluate(stolen_enemy_count=0)
        self.assertEqual(r['ines_dot_reference']['per_second_damage_reference'], 800)
        self.assertEqual(r['known_damage_subtotals']['window_damage'], 1000)

    def test_continuous_reference_keeps_zero_window_and_unknown_tick_phase(self):
        r = evaluate(timing_mode='continuous', window_seconds=0)
        self.assertEqual(r['total_damage'], 0)
        self.assertEqual(r['estimate']['skill']['window_seconds'], 0)

    def test_report_discloses_unknown_ticks_and_fee_source(self):
        text = format_estimate(evaluate(window_seconds=5))
        self.assertIn('淬影突袭 · 持续伤害待核验', text)
        self.assertIn('实际首跳：未知', text)
        self.assertIn('实际跳数：未知', text)
        self.assertIn('下次攻击回费条件参考：2', text)
        self.assertNotIn('开启时立即回费：2', text)


if __name__ == '__main__':
    unittest.main()
