import unittest
from rouge.damage import calculate_damage
from rouge.estimate import format_estimate


def evaluate(**extra):
    return calculate_damage({'operator': 'char_1035_wisdel', 'skill': 2,
                             'base_attack': 1000, 'ghost_count': 1,
                             'ghost_casts': 2, **extra})


class WisdelGhostClockTests(unittest.TestCase):
    def test_zero_window_cannot_declare_ghost_hits(self):
        for skill in (1, 2, 3):
            with self.assertRaisesRegex(ValueError, '零长度观察窗口不能声明魂灵'):
                evaluate(skill=skill, window_seconds=0)

    def test_given_count_remains_conditional_without_cast_phase_attribution(self):
        r = evaluate()
        ref = r['wisdel_secondary_reference']
        self.assertEqual(ref['ghost_casts_requested'], 2)
        self.assertEqual(ref['ghost_declared_count_damage_reference'], 1554)
        self.assertEqual(ref['ghost_per_cast_damage_reference'], 777)
        self.assertIsNone(ref['ghost_cast_times_seconds'])
        self.assertFalse(ref['ghost_full_cast_attribution_verified'])
        self.assertIsNone(r['total_damage'])

    def test_casts_are_not_duplicated_in_full_and_recharge_subtotals(self):
        r = evaluate()
        base = evaluate(ghost_casts=0)
        self.assertEqual(r['known_damage_subtotals'], base['known_damage_subtotals'])
        self.assertIsNone(r['estimate']['skill']['cycle_damage'])
        ghost = next(c for c in r['components'] if c['name'] == '魂灵之影施放')
        self.assertEqual(ghost['hits'], 0)
        self.assertIsNone(ghost['actual_total'])
        self.assertNotIn('times_seconds', ghost)

    def test_zero_count_can_use_zero_window(self):
        r = evaluate(window_seconds=0, ghost_casts=0)
        self.assertEqual(r['total_damage'], 0)

    def test_ghost_source_is_independent_of_owner_range(self):
        r = evaluate(timing={'target_windows': []})
        self.assertIsNone(r['total_damage'])
        self.assertEqual(r['known_damage_subtotals']['window_damage'], 0)

    def test_report_exposes_given_count_without_a_clock(self):
        text = format_estimate(evaluate())
        self.assertIn('指定魂灵之影施放次数参考：2', text)
        self.assertIn('指定次数条件伤害参考：1,554', text)
        self.assertIn('魂灵之影施放时刻：未知', text)
        self.assertIn('当前情景召唤/协同分项伤害：未知', text)


if __name__ == '__main__':
    unittest.main()
