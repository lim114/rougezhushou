import unittest

from rouge.damage import calculate_damage
from rouge.estimate import format_estimate


def evaluate(**extra):
    return calculate_damage({'operator': 'char_1038_whitw2', 'skill': 3,
                             'base_attack': 1000, **extra})


class DroneAuraReferenceTests(unittest.TestCase):
    def test_immediate_target_disappearance_has_no_aura_damage(self):
        r = evaluate(timing={'target_disappears_seconds': 0})
        self.assertEqual(r['total_damage'], 0)
        self.assertEqual(r['estimate']['skill']['total_damage'], 0)
        self.assertFalse(r['drone_lifecycle_reference']['aura_source_possible']['cast'])

    def test_empty_owner_range_does_not_prove_global_aura_absence(self):
        r = evaluate(timing={'target_windows': []})
        self.assertIsNone(r['total_damage'])
        self.assertTrue(r['drone_lifecycle_reference']['aura_source_possible']['window'])
        self.assertEqual(r['known_damage_subtotals']['window_damage'], 0)

    def test_zero_window_is_known_zero_but_full_cast_remains_unknown(self):
        r = evaluate(window_seconds=0)
        self.assertEqual(r['total_damage'], 0)
        self.assertIsNone(r['estimate']['skill']['total_damage'])
        self.assertFalse(r['drone_lifecycle_reference']['aura_source_possible']['window'])

    def test_short_window_does_not_infer_zero_ticks_from_floor(self):
        r = evaluate(window_seconds=.1)
        self.assertIsNone(r['total_damage'])
        self.assertTrue(r['drone_lifecycle_reference']['aura_source_possible']['window'])
        self.assertIsNone(r['drone_lifecycle_reference']['aura_tick_count'])

    def test_aura_preserves_per_tick_reference_without_fabricated_schedule(self):
        r = evaluate()
        ref = r['drone_lifecycle_reference']
        self.assertEqual(ref['aura_per_tick_damage_reference'], 2160)
        self.assertEqual(ref['aura_interval_description_seconds'], 1)
        self.assertFalse(ref['aura_stacks'])
        self.assertFalse(ref['aura_coverage_verified'])
        aura = next(c for c in r['components'] if c['name'] == '狼群光环（不叠加）')
        self.assertEqual(aura['hits'], 0)
        self.assertIsNone(aura['actual_total'])
        self.assertNotIn('times_seconds', aura)
        self.assertIsNone(r['estimate']['skill']['hit_counts'][aura['name']])

    def test_full_phase_and_cycle_do_not_publish_40_guessed_pulses(self):
        r = evaluate()
        for key in ('total_damage', 'phase_damage', 'cycle_damage', 'cycle_dps'):
            self.assertIsNone(r['estimate']['skill'][key])
        self.assertIsNone(r['total_damage'])
        self.assertGreater(r['known_damage_subtotals']['window_damage'], 0)

    def test_continuous_reference_cannot_establish_aura_tick_phase(self):
        r = evaluate(timing_mode='continuous')
        self.assertIsNone(r['total_damage'])
        self.assertIsNone(r['drone_lifecycle_reference']['aura_first_tick_seconds'])

    def test_report_discloses_coverage_and_source_parameter(self):
        text = format_estimate(evaluate(window_seconds=5))
        self.assertIn('狼群光环 · 覆盖与跳伤待核验', text)
        self.assertIn('单次跳伤条件参考：2,160', text)
        self.assertIn('实际首跳：未知', text)
        self.assertIn('本体攻击范围没有目标不证明光环无覆盖', text)
        self.assertIn('单次技能总伤：未知', text)


if __name__ == '__main__':
    unittest.main()
