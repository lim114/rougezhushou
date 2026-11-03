import unittest

from rouge.damage import calculate_damage


def evaluate(op='char_328_cammou', **extra):
    return calculate_damage({'operator': op, 'skill': 2, 'base_attack': 1000, **extra})


class DroneAttackClockTests(unittest.TestCase):
    def test_delayed_cammou_drone_hits_are_clipped_at_skill_end(self):
        r = evaluate(timing={'projectile_travel_seconds': 4})
        self.assertEqual(r['total_damage'], 73185)
        self.assertEqual(r['estimate']['skill']['phase_damage'], 73185)
        self.assertEqual(r['estimate']['skill']['total_damage'], 87465)

    def test_all_drone_units_retain_the_existing_owner_clock_reference(self):
        for skill in (1, 2):
            r = evaluate('char_1038_whitw2', skill=skill,
                         window_seconds=10, deployment_elapsed_seconds=60)
            for c in r['components']:
                if c['name'] != '浮游单元':
                    continue
                self.assertEqual(len(c['times_seconds']), c['hits'])
                self.assertEqual(len(set(c['times_seconds'])), 1)
                self.assertIn('independent drone clock unverified', c['timing_reference'])

    def test_large_travel_does_not_assign_drone_hits_to_this_cycle(self):
        for op in ('char_328_cammou', 'char_1038_whitw2'):
            r = evaluate(op, timing={'projectile_travel_seconds': 100})
            self.assertGreater(r['estimate']['skill']['total_damage'], 0)
            self.assertEqual(r['estimate']['skill']['phase_damage'], 0)
            self.assertEqual(r['estimate']['skill']['cycle_damage'], 0)

    def test_disappearance_cancels_body_and_drone_reference_impacts(self):
        r = evaluate(timing={'projectile_travel_seconds': 4,
                             'target_disappears_seconds': 2})
        self.assertEqual(r['total_damage'], 0)
        self.assertEqual(r['estimate']['skill']['total_damage'], 0)

    def test_supply_window_acquisition_times_remain_shared_reference(self):
        r = evaluate(window_seconds=10, timing={'target_windows': [[4, 8]]})
        owner = set(r['components'][0]['times_seconds'])
        drones = [t for c in r['components'] if c['name'] == '浮游单元'
                  for t in c['times_seconds']]
        self.assertTrue(drones)
        self.assertTrue(set(drones).issubset(owner))

    def test_continuous_reference_totals_and_warmup_are_preserved(self):
        r = evaluate(timing_mode='continuous', window_seconds=3,
                     drone_warmup_hits=7)
        drones = [c for c in r['components'] if c['name'] == '浮游单元']
        self.assertTrue(drones)
        for c in drones:
            self.assertAlmostEqual(c['per_hit'], 1870)
        self.assertEqual(r['total_damage'], sum(c['total'] for c in r['components']))


if __name__ == '__main__':
    unittest.main()
