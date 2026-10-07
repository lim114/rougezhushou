import unittest
from rouge.damage import calculate_damage
from rouge.estimate import format_estimate

OPS = ('char_196_sunbr', 'char_2025_shu')


def evaluate(op, **extra):
    return calculate_damage({'operator': op, 'skill': 1, 'base_attack': 1000, **extra})


class NextAttackHealingReferenceTests(unittest.TestCase):
    def test_zero_and_short_windows_are_preserved(self):
        for op in OPS:
            for window in (0, 1):
                r = evaluate(op, window_seconds=window)
                self.assertEqual(r['estimate']['skill']['window_seconds'], window)
                if window == 0:
                    self.assertEqual(r['total_healing'], 0)
                    self.assertEqual(r['estimate']['skill']['window_healing'], 0)
                else:
                    self.assertIsNone(r['total_healing'])

    def test_zero_eligible_recipients_has_known_zero_healing(self):
        for op in OPS:
            r = evaluate(op, healing_targets=0)
            self.assertEqual(r['total_healing'], 0)
            self.assertEqual(r['estimate']['skill']['total_healing'], 0)

    def test_source_parameters_retain_one_target_and_three_charges(self):
        for op, expected in zip(OPS, (1600, 1800)):
            for count in (1, 5):
                r = evaluate(op, healing_targets=count)
                ref = r['next_attack_healing_reference']
                self.assertEqual(ref['per_heal_reference'], expected)
                self.assertEqual(ref['recipient_limit'], 1)
                self.assertEqual(ref['charge_count_parameter'], 3)
                self.assertEqual(r['components'][0]['hits'], 1)
                self.assertIsNone(r['components'][0]['actual_total'])
                self.assertIsNone(r['estimate']['skill']['hit_counts']['治疗替代下次攻击'])

    def test_enemy_target_absence_does_not_cancel_eligible_friend_reference(self):
        for op in OPS:
            for timing in ({'target_windows': []}, {'target_disappears_seconds': 0}):
                r = evaluate(op, timing=timing)
                self.assertTrue(r['next_attack_healing_reference']['source_possible']['window'])
                self.assertIsNone(r['total_healing'])

    def test_healing_uncertainty_does_not_turn_zero_damage_unknown(self):
        for op in OPS:
            r = evaluate(op)
            self.assertEqual(r['total_damage'], 0)
            self.assertEqual(r['estimate']['skill']['total_damage'], 0)
            self.assertIsNone(r['total_healing'])
            self.assertEqual(r['known_healing_subtotals']['window_healing'], 0)

    def test_heal_acquisition_and_cycle_do_not_come_from_normal_attack_end(self):
        for op in OPS:
            r = evaluate(op)
            self.assertIsNone(r['next_attack_healing_reference']['actual_acquisition_times_seconds'])
            for key in ('duration_seconds', 'recharge_seconds', 'cycle_seconds', 'cycle_healing', 'cycle_hps'):
                self.assertIsNone(r['estimate']['skill'][key])
            self.assertEqual(r['estimate']['skill']['initial_seconds'], 4)

    def test_continuous_reference_keeps_zero_window(self):
        for op in OPS:
            r = evaluate(op, timing_mode='continuous', window_seconds=0)
            self.assertEqual(r['total_healing'], 0)
            self.assertEqual(r['estimate']['skill']['window_seconds'], 0)

    def test_report_exposes_reference_and_friend_condition(self):
        for op in OPS:
            text = format_estimate(evaluate(op, window_seconds=1))
            self.assertIn('下次攻击治疗 · 获取与结束待核验', text)
            self.assertIn('实际友方治疗时刻：未知', text)
            self.assertIn('单次技能总治疗：未知', text)
            self.assertIn('敌方供靶区间不代表友方受疗资格', text)


if __name__ == '__main__':
    unittest.main()
