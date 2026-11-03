import unittest

from rouge.damage import calculate_damage
from rouge.timing import AttackTimeline


def evaluate(**extra):
    return calculate_damage({'operator': 'char_196_sunbr', 'skill': 2,
                             'base_attack': 1000, **extra})


class GummyCookingClockTests(unittest.TestCase):
    def test_healing_occurs_after_cooking_on_the_skill_clock(self):
        r = evaluate(window_seconds=11)
        self.assertEqual(r['total_healing'], 1800)
        self.assertAlmostEqual(r['components'][0]['times_seconds'][0], 10 + 16/30)
        self.assertEqual(r['timing']['streams'][0]['start_frames'], [300])

    def test_no_healing_during_cooking_in_both_references(self):
        for mode in ('frames', 'continuous'):
            for window in (0, 1, 9, 10):
                self.assertEqual(evaluate(window_seconds=window, timing_mode=mode)['total_healing'], 0)

    def test_default_full_healing_and_resource_clock_are_preserved(self):
        for mode in ('frames', 'continuous'):
            r = evaluate(timing_mode=mode)
            skill = r['estimate']['skill']
            self.assertEqual(skill['total_healing'], 14400)
            self.assertEqual(skill['duration_seconds'], 30)
            self.assertTrue(all(t >= 10 for t in r['components'][0]['times_seconds']))

    def test_recipient_disappearing_during_cooking_has_no_heal(self):
        r = evaluate(timing={'target_disappears_seconds': 5})
        self.assertEqual(r['total_healing'], 0)
        self.assertEqual(r['estimate']['skill']['total_healing'], 0)

    def test_supply_window_during_cooking_cannot_create_healing(self):
        self.assertEqual(evaluate(timing={'target_windows': [[0, 5]]})['total_healing'], 0)
        self.assertEqual(evaluate(window_seconds=11, timing={'target_windows': [[10, 11]]})['total_healing'], 1800)

    def test_cooking_phase_interrupt_does_not_shift_post_cooking_heal(self):
        r = evaluate(window_seconds=11, timing={'interrupt_windows': [[0, 5]]})
        self.assertAlmostEqual(r['components'][0]['times_seconds'][0], 10 + 16/30)

    def test_blocked_healing_phase_defers_reference_until_target_available(self):
        r = evaluate(window_seconds=13, timing={'movement_windows': [[10, 12]]})
        self.assertAlmostEqual(r['components'][0]['times_seconds'][0], 12 + 16/30)

    def test_zero_recipients_have_empty_heal_events(self):
        r = evaluate(healing_targets=0)
        self.assertEqual(r['total_healing'], 0)
        self.assertEqual(r['components'][0]['times_seconds'], [])

    def test_continuous_timeline_start_delay_is_counted_once(self):
        timeline = AttackTimeline({'operator': 'char_196_sunbr', 'skill': 2,
                                   'timing_mode': 'continuous'})
        stream = timeline.attacks(30, 2.5, start_delay=10)
        self.assertEqual(stream['times_seconds'], [12.5, 15, 17.5, 20, 22.5, 25, 27.5, 30])


if __name__ == '__main__':
    unittest.main()
