import unittest

from rouge.damage import calculate_damage
from rouge.estimate import format_estimate


def evaluate(**extra):
    return calculate_damage({'operator': 'char_1038_whitw2', 'skill': 3,
                             'base_attack': 1000, **extra})


class DroneArrivalReferenceTests(unittest.TestCase):
    def test_unbound_parameter_is_not_an_arrival_clock(self):
        ref = evaluate()['drone_lifecycle_reference']
        self.assertEqual(ref['unbound_attack_times_parameter'], 1.3)
        self.assertIsNone(ref['arrival_seconds'])
        self.assertIsNone(ref['independent_attack_times_seconds'])
        self.assertIsNone(ref['same_target_hit_counter'])

    def test_owner_events_do_not_create_special_drone_hits(self):
        r = evaluate()
        self.assertFalse(any(c['name'] == '浮游单元' for c in r['components']))
        drone = next(c for c in r['components'] if c['name'] == '特殊浮游单元条件参考')
        self.assertEqual(drone['per_hit'], 360)
        self.assertEqual(drone['hits'], 0)
        self.assertIsNone(drone['actual_total'])
        self.assertNotIn('times_seconds', drone)
        self.assertIsNone(r['estimate']['skill']['hit_counts'][drone['name']])

    def test_body_subtotal_is_preserved_without_autonomous_drone_damage(self):
        r = evaluate()
        body = next(c for c in r['components'] if c['name'] == '本体攻击')
        self.assertEqual(r['known_damage_subtotals']['window_damage'], body['total'])
        self.assertEqual(body['times_seconds'][0], .4)
        self.assertEqual(r['known_damage_subtotals']['window_damage'], 55800)
        self.assertIsNone(r['total_damage'])

    def test_empty_owner_range_cannot_cancel_global_drone_source(self):
        r = evaluate(timing={'target_windows': []})
        self.assertTrue(r['drone_lifecycle_reference']['drone_source_possible']['window'])
        self.assertEqual(r['known_damage_subtotals']['window_damage'], 0)
        self.assertIsNone(r['total_damage'])

    def test_zero_lifetime_or_window_cannot_create_drone_hits(self):
        for extra in ({'window_seconds': 0}, {'timing': {'target_disappears_seconds': 0}}):
            r = evaluate(**extra)
            self.assertEqual(r['total_damage'], 0)
            self.assertFalse(r['drone_lifecycle_reference']['drone_source_possible']['window'])

    def test_warmup_and_deployment_age_cannot_supply_missing_independent_hits(self):
        for warmup, age in ((0, 0), (7, 60), (100, 100)):
            r = evaluate(drone_warmup_hits=warmup, deployment_elapsed_seconds=age)
            self.assertEqual(r['known_damage_subtotals']['window_damage'], 55800)
            self.assertIsNone(r['drone_lifecycle_reference']['same_target_hit_counter'])
            self.assertIsNone(r['total_damage'])

    def test_module_changes_initial_reference_without_proving_arrival(self):
        r = evaluate(module_id='uniequip_002_whitw2', module_level=1)
        self.assertAlmostEqual(r['drone_lifecycle_reference']['drone_initial_per_hit_reference'], 630)
        self.assertIsNone(r['drone_lifecycle_reference']['arrival_seconds'])

    def test_cycle_keeps_body_reference_but_not_unknown_return_drone_clock(self):
        r = evaluate()
        self.assertGreater(r['known_damage_subtotals']['cycle_damage'], 55800)
        self.assertFalse(r['drone_lifecycle_reference']['return_phase_clock_verified'])
        self.assertIsNone(r['estimate']['skill']['cycle_damage'])
        self.assertIsNone(r['estimate']['skill']['cycle_dps'])

    def test_continuous_and_report_preserve_unknown(self):
        r = evaluate(timing_mode='continuous', window_seconds=5)
        self.assertIsNone(r['total_damage'])
        text = format_estimate(r)
        self.assertIn('特殊浮游单元 · 独立攻击待核验', text)
        self.assertIn('attack@times原始参数（含义未绑定）：1.3', text)
        self.assertIn('实际到达时间：未知', text)
        self.assertIn('同目标实际命中计数：未知', text)


if __name__ == '__main__':
    unittest.main()
