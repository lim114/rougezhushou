import unittest

from rouge.damage import calculate_damage
from rouge.timing import phase_totals


def evaluate(**extra):
    return calculate_damage({'operator': 'char_206_gnosis', 'skill': 3,
        'base_attack': 1000, 'frozen_at_skill_end': False, **extra})


class GnosisAttackClockTests(unittest.TestCase):
    def test_cast_preserves_late_projectiles_but_phase_clips_them(self):
        r = evaluate(timing={'projectile_travel_seconds': 4})
        skill = r['estimate']['skill']
        self.assertEqual(skill['total_damage'], 19000)
        self.assertEqual(skill['phase_damage'], 13000)
        self.assertEqual(r['components'][0]['total'], 13000)
        self.assertIn('times_seconds', r['components'][0])

    def test_cycle_excludes_own_and_recharge_projectiles_after_boundary(self):
        r = evaluate(timing={'projectile_travel_seconds': 45})
        skill = r['estimate']['skill']
        stream = r['timing']['streams'][0]
        normal = r['timing']['recharge_streams'][0]
        cast_count = sum(t < skill['cycle_seconds'] for t in stream['emitted_times_seconds'])
        recharge_count = sum(skill['duration_seconds'] + t < skill['cycle_seconds']
                             for t in normal['times_seconds'])
        self.assertEqual(skill['phase_damage'], 0)
        self.assertEqual(skill['cycle_damage'], 1000 * (cast_count + recharge_count))
        self.assertEqual(skill['cycle_damage'], 12000)

    def test_window_impact_end_is_excluded_and_next_frame_included(self):
        config = {'windup_frames': 6, 'recovery_frames': 6,
                  'projectile_travel_seconds': .5}
        before = evaluate(window_seconds=.7, timing=config)
        after = evaluate(window_seconds=22/30, timing=config)
        self.assertEqual(before['total_damage'], 0)
        self.assertEqual(after['total_damage'], 1000)
        self.assertEqual(after['components'][0]['times_seconds'], [.7])

    def test_disappearance_cancels_delayed_impacts(self):
        r = evaluate(timing={'projectile_travel_seconds': 4,
                             'target_disappears_seconds': 3})
        self.assertEqual(r['total_damage'], 0)
        self.assertEqual(r['components'][0]['times_seconds'], [])
        self.assertEqual(r['estimate']['skill']['phase_damage'], 0)

    def test_no_target_has_no_body_damage(self):
        r = evaluate(timing={'target_windows': []})
        self.assertEqual(r['total_damage'], 0)
        self.assertEqual(r['estimate']['skill']['cycle_damage'], 0)

    def test_frozen_fragile_and_resistance_remain_per_hit_factors(self):
        r = evaluate(cold_state=2, enemy_resistance=50,
                     timing={'projectile_travel_seconds': 4})
        self.assertAlmostEqual(r['components'][0]['per_hit'], 975)
        self.assertAlmostEqual(r['estimate']['skill']['phase_damage'], 13 * 975)

    def test_continuous_reference_uses_its_existing_times(self):
        r = evaluate(timing_mode='continuous')
        c = r['components'][0]
        self.assertEqual(len(c['times_seconds']), c['hits'])
        self.assertEqual(phase_totals([c], 13)[0], r['estimate']['skill']['phase_damage'])


if __name__ == '__main__':
    unittest.main()
