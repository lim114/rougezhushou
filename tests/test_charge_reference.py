import unittest

from rouge.damage import calculate_damage
from rouge.estimate import format_estimate


def evaluate(**extra):
    return calculate_damage({'operator': 'mechanist', 'skill': 3,
                             'base_attack': 1000, **extra})


class ChargeReferenceTests(unittest.TestCase):
    def test_declared_linear_damage_is_retained_without_inventing_collision(self):
        r = evaluate(window_seconds=3.5, charge_count=1, enemy_defense=400,
                     enemy_resistance=50, timing_mode='continuous')
        self.assertEqual(r['total_damage'], 15940)
        self.assertEqual(r['charge_reference']['declared_count_damage'], 11000)
        self.assertIsNone(r['charge_reference']['collision_times_seconds'])
        self.assertFalse(r['charge_reference']['events_scheduled'])

    def test_window_count_does_not_establish_cast_phase_or_cycle(self):
        r = evaluate(window_seconds=3.5, charge_count=4)
        for key in ('total_damage', 'phase_damage', 'cycle_damage', 'cycle_dps'):
            self.assertIsNone(r['estimate']['skill'][key])
        self.assertEqual(r['charge_reference']['hits_requested'], 4)
        self.assertEqual(r['charge_reference']['declared_count_damage'], 45600)

    def test_known_bombard_and_recharge_subtotals_match_zero_charge(self):
        for mode in ('frames', 'continuous'):
            for window in (None, 3.5, 30):
                extra = {'timing_mode': mode}
                if window is not None:
                    extra['window_seconds'] = window
                baseline = evaluate(**extra)['estimate']['skill']
                r = evaluate(charge_count=2, **extra)
                for key in ('total_damage', 'phase_damage', 'cycle_damage', 'cycle_dps',
                            'window_damage'):
                    self.assertEqual(r['known_damage_subtotals'][key], baseline[key])
                for key in ('initial_seconds', 'recharge_seconds', 'cycle_seconds',
                            'duration_seconds', 'total_healing'):
                    self.assertEqual(r['estimate']['skill'][key], baseline[key])

    def test_no_charge_preserves_complete_result(self):
        self.assertEqual(evaluate(), evaluate(charge_count=0))

    def test_zero_window_rejects_contradictory_hit_count(self):
        with self.assertRaisesRegex(ValueError, '零长度'):
            evaluate(window_seconds=0, charge_count=1)
        self.assertEqual(evaluate(window_seconds=0)['total_damage'], 0)

    def test_late_projectiles_stay_separate_from_charge_reference(self):
        extra = {'timing': {'windup_frames': 0, 'recovery_frames': 0,
                            'start_delay_frames': 24, 'projectile_travel_seconds': 35.1}}
        baseline = evaluate(**extra)
        r = evaluate(charge_count=1, **extra)
        self.assertEqual(r['components'][0], baseline['components'][0])
        self.assertEqual(r['known_damage_subtotals']['phase_damage'], 9880)
        self.assertEqual(r['known_damage_subtotals']['cycle_damage'], 11 * 9880)

    def test_report_distinguishes_declared_damage_from_collision_clock(self):
        text = format_estimate(evaluate(window_seconds=3.5, charge_count=1))
        self.assertIn('结构性原理 · 冲锋次数参考', text)
        self.assertIn('冲锋碰撞时刻：未知', text)
        self.assertIn('单次技能总伤：未知', text)
        self.assertIn('本体0.8秒落地延迟不用于冲锋', text)


if __name__ == '__main__':
    unittest.main()
