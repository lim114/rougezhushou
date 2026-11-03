import unittest

from rouge.damage import _prepare_damage
from rouge.operator_engine import Combat


def plan(elapsed=0, offset=0, **extra):
    scenario, attributes, _, _ = _prepare_damage({'operator': 'char_1038_whitw2',
        'skill': 2, 'base_attack': 1000, 'deployment_elapsed_seconds': elapsed,
        '_timeline_offset_seconds': offset, 'drone_warmup_hits': 100, **extra})
    return Combat(scenario, attributes).plan(normal=True, window=3)


def drones(result):
    return [c for c in result['components'] if c['name'] == '浮游单元']


class HeadwolfPhaseClockTests(unittest.TestCase):
    def test_identical_operator_age_has_identical_damage_in_both_phases(self):
        for mode in ('frames', 'continuous'):
            first = drones(plan(elapsed=40, timing_mode=mode))
            recharge = drones(plan(offset=40, timing_mode=mode))
            self.assertEqual(first, recharge)
            self.assertAlmostEqual(recharge[0]['per_hit'], 1210)

    def test_recharge_age_reaches_extra_drone_threshold(self):
        r = drones(plan(offset=60))
        self.assertTrue(r)
        self.assertEqual(r[0]['hits'], 2)
        self.assertAlmostEqual(r[0]['total'], 2420)

    def test_phase_offset_and_prior_deployment_age_are_added_once(self):
        self.assertEqual(drones(plan(elapsed=30, offset=30)), drones(plan(elapsed=60)))

    def test_boost_threshold_uses_event_time_on_current_phase(self):
        r = drones(plan(offset=19, timing={'windup_frames': 0, 'recovery_frames': 0}))
        self.assertAlmostEqual(r[0]['per_hit'], 1100)
        self.assertAlmostEqual(r[1]['per_hit'], 1210)

    def test_potential_changes_interval_without_resetting_recharge_age(self):
        r = drones(plan(offset=48, potential=6))
        self.assertEqual(r[0]['hits'], 2)

    def test_eligible_module_talent_overrides_keep_the_same_age_semantics(self):
        extra = {'module_id': 'uniequip_002_whitw2', 'module_level': 3}
        self.assertEqual(drones(plan(offset=60, **extra)), drones(plan(elapsed=60, **extra)))

    def test_zero_phase_offset_preserves_base_initial_age(self):
        self.assertAlmostEqual(drones(plan())[0]['per_hit'], 1100)
        self.assertEqual(drones(plan())[0]['hits'], 1)


if __name__ == '__main__':
    unittest.main()
