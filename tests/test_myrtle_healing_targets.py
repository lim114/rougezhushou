import unittest

from rouge.damage import calculate_damage
from rouge.estimate import format_estimate


def evaluate(**extra):
    return calculate_damage({'operator': 'char_151_myrtle', 'skill': 2,
                             'base_attack': 1000, **extra})


class MyrtleHealingTargetsTests(unittest.TestCase):
    def test_zero_recipients_have_no_skill_healing_in_both_references(self):
        for mode in ('frames', 'continuous'):
            r = evaluate(healing_targets=0, timing_mode=mode)
            self.assertEqual(r['total_healing'], 0)
            self.assertEqual(r['estimate']['skill']['total_healing'], 0)
            self.assertEqual(r['estimate']['skill']['cycle_healing'], 0)
            self.assertEqual(r['components'][0]['hits'], 0)

    def test_one_recipient_preserves_independent_eight_thousand_reference(self):
        for count in (1, 2, 100):
            r = evaluate(healing_targets=count)
            self.assertEqual(r['total_healing'], 8000)
            self.assertEqual(r['components'][0]['per_hit'], 500)
            self.assertEqual(r['components'][0]['hits'], 16)

    def test_partial_window_caps_recipient_count_at_one(self):
        self.assertEqual(evaluate(window_seconds=5.5, healing_targets=100)['total_healing'], 2500)
        self.assertEqual(evaluate(window_seconds=5.5, healing_targets=0)['total_healing'], 0)

    def test_enemy_supply_windows_do_not_remove_friendly_healing(self):
        r = evaluate(healing_targets=1, timing={'target_windows': []})
        self.assertEqual(r['total_healing'], 8000)

    def test_no_healing_recipients_do_not_change_fee_or_resource_clock(self):
        no = evaluate(healing_targets=0)
        one = evaluate(healing_targets=1)
        for key in ('initial_seconds', 'recharge_seconds', 'cycle_seconds',
                    'duration_seconds', 'total_damage'):
            self.assertEqual(no['estimate']['skill'][key], one['estimate']['skill'][key])
        fee = lambda r: next(s for s in r['report']['sections'] if s['id'] == 'dp')
        self.assertEqual(fee(no), fee(one))

    def test_report_discloses_one_friendly_target_limit(self):
        text = format_estimate(evaluate(healing_targets=0))
        self.assertIn('至多治疗一名友方', text)
        self.assertIn('零受疗目标不产生治疗', text)


if __name__ == '__main__':
    unittest.main()
