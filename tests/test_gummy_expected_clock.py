import unittest

from rouge.damage import calculate_damage, _prepare_damage
from rouge.operator_engine import Combat
from rouge.timing import phase_totals


class GummyExpectedClockTests(unittest.TestCase):
    def plan(self, **extra):
        scenario, attributes, _, _ = _prepare_damage({
            'operator': 'char_196_sunbr', 'skill': 2, 'base_attack': 1000, **extra})
        return Combat(scenario, attributes).plan(normal=True, window=5)

    def test_weighted_alternatives_share_one_attack_stream(self):
        r = self.plan(timing={'windup_frames': 0, 'recovery_frames': 0})
        self.assertEqual(len(r['timing']['streams']), 1)
        basic, talent = r['components']
        self.assertEqual(basic['times_seconds'], talent['times_seconds'])
        self.assertEqual(len(basic['times_seconds']), 5)
        self.assertAlmostEqual(basic['hits'] + talent['hits'], 5)

    def test_expected_event_damage_preserves_marginal_probability_reference(self):
        r = self.plan(timing={'windup_frames': 0, 'recovery_frames': 0})
        basic, talent = r['components']
        # E2 talent: 15% for200%ATK, remaining85% for100%ATK.
        self.assertEqual(basic['event_amounts'], [850] * 5)
        self.assertEqual(talent['event_amounts'], [300] * 5)
        self.assertEqual(r['damage'], 5750)
        self.assertEqual(phase_totals(r['components'], 1)[0], 1150)

    def test_no_target_has_no_expected_attack_events(self):
        r = self.plan(timing={'target_windows': []})
        self.assertEqual(r['damage'], 0)
        self.assertTrue(all(c['times_seconds'] == [] for c in r['components']))

    def test_recharge_projectiles_outside_cycle_are_not_counted(self):
        r = calculate_damage({'operator': 'char_196_sunbr', 'skill': 2,
            'base_attack': 1000, 'timing': {'projectile_travel_seconds': 100}})
        self.assertEqual(r['estimate']['skill']['cycle_damage'], 0)

    def test_continuous_reference_keeps_weighted_damage_sum(self):
        r = self.plan(timing_mode='continuous')
        self.assertAlmostEqual(r['damage'], 4600)
        self.assertEqual(r['damage'], sum(sum(c['event_amounts']) for c in r['components']))


if __name__ == '__main__':
    unittest.main()
