import copy
import unittest

from rouge.charge_timeline import compare_charge_windows, format_charge_windows
from rouge.damage import calculate_damage


def scenario(**extra):
    return {'operator': 'mechanist', 'skill': 3, 'base_attack': 1000,
            'timing_mode': 'continuous', **extra}


class ChargeTimelineTests(unittest.TestCase):
    def test_worked_damage_and_exact_boundary_keep_equal_time_hits(self):
        s = scenario(enemy_defense=400, enemy_resistance=50, charge_count=99, window_seconds=20)
        result = compare_charge_windows(s, [4, 3.5, 0, 3.5], [0, 3.5, 4, 5])
        self.assertEqual(result['per_hit_damage_reference'], 11000)
        self.assertEqual([r['charge_hits'] for r in result['windows']], [0, 1, 3, 4])
        row = result['windows'][1]
        self.assertEqual((row['bombard_damage'], row['charge_damage'], row['conditional_damage_subtotal']),
                         (4940, 11000, 15940))
        self.assertEqual(row['conditional_dps'], 15940 / 3.5)
        self.assertIsNone(result['windows'][0]['conditional_dps'])
        self.assertEqual(result['windows'][0]['conditional_damage_subtotal'], 0)
        self.assertEqual(result['events'][-1]['cumulative_charge_damage_reference'], 44000)

    def test_bombardment_matches_public_calculator_in_both_modes(self):
        for mode in ('frames', 'continuous'):
            s = scenario(timing_mode=mode, timing={'projectile_travel_seconds': 2.1},
                         effects=[{'kind': 'attack_pct', 'value': .2}])
            result = compare_charge_windows(s, [1, 3, 15], [3.5, 10, 40])
            for row in result['windows']:
                baseline = calculate_damage({**s, 'charge_count': 0, 'window_seconds': row['window_seconds']})
                self.assertEqual(row['bombard_damage'], baseline['total_damage'])
                self.assertEqual(row['conditional_damage_subtotal'] - row['charge_damage'], baseline['total_damage'])
            # Ordinary attack +20% shares the skill's +280% additive layer.
            self.assertEqual(result['per_hit_damage_reference'], 12000)

    def test_owner_empty_supply_does_not_locate_independent_collisions(self):
        result = compare_charge_windows(scenario(timing={'target_windows': []}), [1], [3.5])
        row = result['windows'][0]
        self.assertEqual(row['bombard_damage'], 0)
        self.assertEqual(row['charge_damage'], 11400)
        self.assertIn('只影响既有轰击', '\n'.join(result['notes']))

    def test_projectile_delay_never_moves_a_declared_collision(self):
        s = scenario(timing_mode='frames', timing={'projectile_travel_seconds': 35.1})
        result = compare_charge_windows(s, [1.001, 1.001], [1.001, 1.002])
        self.assertEqual([r['charge_hits'] for r in result['windows']], [0, 2])
        self.assertEqual(result['hit_times_seconds'], [1.001, 1.001])
        self.assertEqual([r['bombard_damage'] for r in result['windows']], [0, 0])

    def test_empty_and_later_declarations_never_claim_complete_cast(self):
        for times in ([], [40, 50]):
            result = compare_charge_windows(scenario(), times, [3.5, 40])
            self.assertEqual([r['charge_hits'] for r in result['windows']], [0, 0])
            self.assertIsNone(result['full_cast_damage'])
            self.assertIsNone(result['cycle_damage'])
            self.assertFalse(result['native_collision_clock_verified'])
        self.assertEqual(len(result['events']), 2)

    def test_input_and_returned_conditions_remain_isolated(self):
        s = scenario(timing={'target_windows': [[0, 5]], 'opaque': {'x': [1]}}, charge_count=4)
        times = [3, 1, 1]; windows = [4, 2]; original = copy.deepcopy((s, times, windows))
        result = compare_charge_windows(s, times, windows)
        self.assertEqual((s, times, windows), original)
        result['scenario']['timing']['opaque']['x'].append(2)
        self.assertEqual(s['timing']['opaque']['x'], [1])
        self.assertEqual(result['hit_times_seconds'], [1, 1, 3])
        self.assertEqual([r['window_seconds'] for r in result['windows']], [4, 2])

    def test_strict_time_and_window_types_and_bounds(self):
        invalid = [True, '1', None, {}, -1, 3600.1, float('nan'), float('inf'), 10**400]
        for value in invalid:
            for times, windows in (([value], [1]), ([], [value])):
                with self.subTest(value=type(value).__name__, times=bool(times)):
                    with self.assertRaises(ValueError):compare_charge_windows(scenario(), times, windows)
        for times, windows in ((None, [1]), ([1] * 101, [1]), ([], []), ([], [1] * 13)):
            with self.assertRaises(ValueError):compare_charge_windows(scenario(), times, windows)
        self.assertEqual(compare_charge_windows(scenario(), [3600], [0])['hit_times_seconds'], [3600])

    def test_duration_gate_uses_current_rank_and_no_extrapolation(self):
        for rank in (1, 7, 10):
            s = scenario(skill_rank=rank)
            duration = calculate_damage(s)['estimate']['skill']['duration_seconds']
            self.assertEqual(compare_charge_windows(s, [], [duration])['skill_duration_parameter_seconds'], duration)
            with self.assertRaisesRegex(ValueError, '持续时间'):
                compare_charge_windows(s, [], [duration + .001])

    def test_other_skill_or_operator_rejected(self):
        for s in (scenario(skill=2), scenario(operator='kaltsit'), scenario(skill=True)):
            with self.assertRaisesRegex(ValueError, '仅适用于'):compare_charge_windows(s, [], [1])

    def test_copyable_report_keeps_conditions_unknowns_and_warnings(self):
        result = compare_charge_windows(scenario(unconfirmed_training=['信赖']), [1, 2], [3.5])
        report = format_charge_windows(result)
        self.assertIn('"base_attack": 1000', report)
        self.assertIn('完整施放总伤：未知', report)
        self.assertIn('本体0.8秒', report)
        self.assertIn('信赖', report)
        self.assertIn('冲锋2次', report)


if __name__ == '__main__':
    unittest.main()
