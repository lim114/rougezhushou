import unittest

from rouge.damage import calculate_damage
from rouge.estimate import format_estimate


def evaluate(skill, **extra):
    return calculate_damage({'operator': 'char_206_gnosis', 'skill': skill,
                             'base_attack': 1000, **extra})


class GnosisTargetLifetimeTests(unittest.TestCase):
    def test_s2_requires_a_target_at_instant_reference(self):
        for timing in ({'target_windows': []}, {'target_windows': [[1, 2]]},
                       {'target_disappears_seconds': 0},
                       {'movement_windows': [[0, 1]]}, {'interrupt_windows': [[0, 1]]}):
            with self.subTest(timing=timing):
                r = evaluate(2, timing=timing)
                self.assertEqual(r['total_damage'], 0)
                self.assertEqual(r['estimate']['skill']['total_damage'], 0)

    def test_s2_available_source_keeps_independent_damage(self):
        for mode in ('frames', 'continuous'):
            r = evaluate(2, timing_mode=mode)
            self.assertEqual(r['total_damage'], 2000)
            self.assertTrue(r['components'][0]['instant_event'])

    def test_s2_zero_window_has_no_observed_damage(self):
        r = evaluate(2, window_seconds=0)
        self.assertEqual(r['total_damage'], 0)
        self.assertEqual(r['estimate']['skill']['total_damage'], 2000)

    def test_target_disappearing_before_end_cannot_receive_terminal_hit(self):
        for disappears in (0, .1, 12.9):
            r = evaluate(3, timing={'target_disappears_seconds': disappears})
            c = next(c for c in r['components'] if c['name'] == '失温症终结')
            self.assertEqual(c['hits'], 0)
            self.assertFalse(r['gnosis_terminal_reference']['source_possible']['cast'])
            self.assertEqual(r['total_damage'],
                             sum(c['total'] for c in r['components'] if c['name'] != '失温症终结'))

    def test_same_end_frame_disappearance_remains_unknown(self):
        r = evaluate(3, timing={'target_disappears_seconds': 13})
        self.assertTrue(r['gnosis_terminal_reference']['same_frame_disappearance_unresolved'])
        self.assertIsNone(r['total_damage'])
        self.assertIsNone(r['estimate']['skill']['total_damage'])
        self.assertEqual(r['known_damage_subtotals']['window_damage'], 19000)

    def test_same_frame_disappearance_keeps_earlier_window_known(self):
        r = evaluate(3, window_seconds=1, timing={'target_disappears_seconds': 13})
        self.assertEqual(r['total_damage'], 2000)
        self.assertFalse(r['gnosis_terminal_reference']['source_possible']['window'])

    def test_persistent_target_retains_conditional_terminal_reference(self):
        r = evaluate(3)
        self.assertEqual(next(c for c in r['components'] if c['name'] == '失温症终结')['total'], 6000)
        self.assertFalse(r['gnosis_terminal_reference']['terminal_clock_verified'])
        self.assertFalse(r['gnosis_terminal_reference']['freeze_removal_order_verified'])

    def test_range_exit_is_not_assumed_to_remove_frozen_terminal_source(self):
        r = evaluate(3, timing={'target_windows': [[0, 1]]})
        self.assertTrue(r['gnosis_terminal_reference']['source_possible']['cast'])

    def test_no_end_freeze_preserves_body_only_case(self):
        r = evaluate(3, frozen_at_skill_end=False)
        self.assertNotIn('gnosis_terminal_reference', r)
        self.assertFalse(any(c['name'] == '失温症终结' for c in r['components']))

    def test_report_discloses_terminal_clock_boundary(self):
        text = format_estimate(evaluate(3))
        self.assertIn('失温症 · 终结条件参考', text)
        self.assertIn('实际结束当帧：未知', text)


if __name__ == '__main__':
    unittest.main()
