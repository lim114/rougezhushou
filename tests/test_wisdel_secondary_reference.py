import unittest

from rouge.damage import calculate_damage
from rouge.estimate import format_estimate


def evaluate(**extra):
    return calculate_damage({'operator': 'char_1035_wisdel', 'skill': 1,
                             'base_attack': 1000, **extra})


class WisdelSecondaryReferenceTests(unittest.TestCase):
    def test_s1_no_target_has_no_attack_or_secondary_source(self):
        for timing in ({'target_windows': []}, {'target_disappears_seconds': 0},
                       {'interrupt_windows': [[0, 3600]]}):
            r = evaluate(timing=timing)
            self.assertEqual(r['total_damage'], 0)
            self.assertEqual(r['estimate']['skill']['total_damage'], 0)
            self.assertFalse(r['wisdel_secondary_reference']['source_possible']['cast'])
            self.assertTrue(all(c['hits'] == 0 for c in r['components']))

    def test_zero_observation_is_known_zero(self):
        r = evaluate(window_seconds=0)
        self.assertEqual(r['total_damage'], 0)
        self.assertFalse(r['wisdel_secondary_reference']['source_possible']['window'])
        self.assertIsNone(r['estimate']['skill']['total_damage'])

    def test_late_s1_acquisition_is_not_discarded_at_nominal_interval(self):
        r = evaluate(window_seconds=20, timing={'target_windows': [[10, 20]]})
        self.assertTrue(r['wisdel_secondary_reference']['source_possible']['cast'])
        self.assertTrue(r['wisdel_secondary_reference']['source_possible']['window'])
        self.assertIsNone(r['total_damage'])

    def test_s1_does_not_publish_invented_lifecycle_or_cycle(self):
        r = evaluate()
        for key in ('duration_seconds', 'initial_seconds', 'recharge_seconds',
                    'cycle_seconds', 'cycle_damage', 'cycle_dps'):
            self.assertIsNone(r['estimate']['skill'][key])
        self.assertIsNone(r['total_damage'])
        self.assertIsNone(r['estimate']['skill']['hit_counts']['余震'])

    def test_single_check_parameter_does_not_become_union_probability(self):
        r = evaluate()
        ref = r['wisdel_secondary_reference']
        self.assertEqual(ref['described_single_check_probability'], .15)
        self.assertEqual(ref['explosion_per_hit_reference'], 1500)
        self.assertIsNone(ref['explosion_expected_count'])
        self.assertFalse(ref['random_independence_verified'])
        self.assertFalse(ref['shadow_lifecycle_verified'])
        explosion = next(c for c in r['components'] if c['name'] == '残影单次爆炸条件参考')
        self.assertEqual(explosion['hits'], 0)
        self.assertIsNone(explosion['actual_total'])
        self.assertNotIn('times_seconds', explosion)

    def test_s2_and_s3_keep_owner_reference_subtotal_without_secondary_totals(self):
        for skill in (2, 3):
            r = evaluate(skill=skill)
            main = sum(c['total'] for c in r['components'] if c['name'] == '维什戴尔主攻击')
            self.assertEqual(r['known_damage_subtotals']['window_damage'], main)
            self.assertIsNone(r['total_damage'])
            self.assertIsNone(r['estimate']['skill']['phase_damage'])
            self.assertIsNone(r['estimate']['skill']['cycle_damage'])

    def test_overload_does_not_place_four_attacks_at_one_owner_event(self):
        r = evaluate(skill=2, overload=True)
        main = next(c for c in r['components'] if c['name'] == '维什戴尔主攻击')
        self.assertNotIn('times_seconds', main)
        self.assertIsNone(main['actual_total'])
        self.assertEqual(r['known_damage_subtotals']['window_damage'], 0)

    def test_no_source_cannot_create_first_damage_bonus(self):
        r = evaluate(timing={'target_windows': []}, relic_ids=['rogue_6_relic_fight_1'])
        self.assertEqual(r['total_damage'], 0)
        self.assertFalse(any(c.get('first_damage_relic') for c in r['components']))

    def test_reference_only_collectible_cannot_make_secondary_events_known(self):
        r = evaluate(skill=2, relic_ids=['rogue_6_relic_fight_1'])
        self.assertFalse(any(c.get('first_damage_relic') for c in r['components']))
        self.assertIsNone(r['total_damage'])

    def test_continuous_reference_does_not_verify_randomness(self):
        r = evaluate(timing_mode='continuous')
        self.assertIsNone(r['total_damage'])
        self.assertIsNone(r['wisdel_secondary_reference']['secondary_hit_times_seconds'])

    def test_report_exposes_unknown_without_fabricated_expected_damage(self):
        text = format_estimate(evaluate(window_seconds=5))
        self.assertIn('好礼与余震 · 次生事件待核验', text)
        self.assertIn('实际爆炸期望次数：未知', text)
        self.assertIn('单次判定概率描述参数：15', text)
        self.assertIn('单次技能总伤：未知', text)
        self.assertNotIn('残影消耗后不重复爆炸', text)


if __name__ == '__main__':
    unittest.main()
