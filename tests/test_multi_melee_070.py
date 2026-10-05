import copy
import unittest

from rouge.animation_reference import choices
from rouge.damage import calculate_damage
from rouge.multi_melee import relative_wait


OP = 'char_1042_phatm2'


def evaluate(**kwargs):
    return calculate_damage({'operator': OP, 'skill': 1, 'base_attack': 1000, **kwargs})


class MultiMeleeTests(unittest.TestCase):
    def test_native_relative_wait_uses_raw_period_not_rounded_cadence(self):
        # Raw period .60795... gives scale .37997... and a 4.559... frame
        # wait -> 5. Rounding the period to18 frames first gives4.5 ->4.
        _, _, frames = relative_wait(1.6 * 100 / 263.18)
        self.assertEqual(frames, 5)
        self.assertEqual(relative_wait(.6)[2], 4)

    def test_native_float_wait_has_minimum_one_frame(self):
        scale, _, gap = relative_wait(.001)
        self.assertAlmostEqual(scale, .1)
        self.assertEqual(gap, 1)
        self.assertEqual(relative_wait(8)[2], 12)

    def test_two_hit_reference_scales_with_attack_speed(self):
        for bonus, releases, gap in ((0, [15, 27], 12), (30, [12, 21], 9),
                                    (100, [8, 14], 6), (500, [3, 5], 2)):
            with self.subTest(bonus=bonus):
                r = evaluate(effects=[{'kind': 'attack_speed', 'value': bonus}])
                s = r['timing']['streams'][0]
                self.assertEqual(s['release_frames'], releases)
                self.assertEqual(s['multi_melee_reference']['relative_wait_frames'], gap)
                self.assertFalse(s['exact_binding'])
                self.assertFalse(s['multi_melee_reference']['first_damage_phase_verified'])
                self.assertEqual(r['total_damage'], 9000)

    def test_window_excludes_both_end_boundaries(self):
        for seconds, hits, total in ((.5, 0, 0), (.51, 1, 1500),
                                    (.9, 1, 1500), (.91, 2, 9000)):
            with self.subTest(seconds=seconds):
                r = evaluate(window_seconds=seconds)
                self.assertEqual(r['components'][0]['hits'], hits)
                self.assertEqual(r['total_damage'], total)
                self.assertEqual(r['estimate']['skill']['total_damage'], 9000)
                self.assertEqual(r['estimate']['skill']['window_seconds'], seconds)

    def test_buildup_and_burst_follow_the_two_reference_events(self):
        r = evaluate()
        hit = r['components'][0]
        burst = next(c for c in r['components'] if c['name'] == '神经损伤爆发')
        self.assertEqual(hit['times_seconds'], [.5, .9])
        self.assertEqual(burst['times_seconds'], [.9])
        self.assertEqual(burst['total'], 6000)

    def test_current_cast_end_and_cycle_remain_explicitly_unknown(self):
        for mode in ('frames', 'continuous'):
            with self.subTest(mode=mode):
                r = evaluate(timing_mode=mode)
                skill = r['estimate']['skill']
                for field in ('duration_seconds', 'recharge_seconds', 'cycle_seconds',
                              'phase_damage', 'cycle_damage', 'cycle_dps'):
                    self.assertIsNone(skill[field], field)
                self.assertFalse(r['estimate']['complete'])
                self.assertEqual(skill['initial_seconds'],0)
                block = next(s for s in r['report']['sections'] if s['id'] == 'multi_melee')
                self.assertIn('实际相位', ' '.join(block['notes']))

    def test_insufficient_initial_sp_does_not_invent_a_normal_attack_clock(self):
        r=evaluate(skill_rank=1)
        self.assertIsNone(r['estimate']['skill']['initial_seconds'])

    def test_disappearance_between_hits_cancels_second_damage(self):
        r = evaluate(timing={'target_disappears_seconds': .8})
        self.assertEqual(r['components'][0]['hits'], 1)
        self.assertEqual(r['total_damage'], 1500)
        self.assertEqual(r['estimate']['skill']['total_damage'], 1500)

    def test_leaving_range_does_not_choose_a_different_second_target(self):
        r = evaluate(timing={'target_windows': [[0, .6]]})
        self.assertEqual(r['components'][0]['times_seconds'], [.5, .9])
        self.assertEqual(r['total_damage'], 9000)

    def test_no_target_or_later_acquisition_respects_observation_window(self):
        empty = evaluate(timing={'target_windows': []})
        self.assertEqual(empty['total_damage'], 0)
        delayed = evaluate(window_seconds=2, timing={'target_windows': [[1, 3]]})
        self.assertEqual(delayed['components'][0]['times_seconds'], [1.5, 1.9])
        self.assertEqual(delayed['total_damage'], 9000)

    def test_movement_before_cast_delays_acquisition_without_extra_gap_frame(self):
        r = evaluate(window_seconds=2, timing={'movement_windows': [[0, .3]]})
        self.assertEqual(r['components'][0]['times_seconds'], [.8, 1.2])
        self.assertEqual(r['timing']['streams'][0]['multi_melee_reference']['relative_wait_frames'], 12)

    def test_unverified_interrupt_during_cast_is_not_silently_ignored(self):
        for key, ranges in (('interrupt_windows', [[.3, .8]]),
                            ('interrupt_windows', [[.7, 1]]),
                            ('movement_windows', [[.1, .2]])):
            with self.subTest(key=key, ranges=ranges):
                with self.assertRaisesRegex(ValueError, '移动/打断机制尚未核验'):
                    evaluate(timing={key: ranges})

    def test_first_damage_relic_remains_reference_only_in_offline_scope(self):
        r = evaluate(relic_ids=['rogue_6_relic_fight_1'],
                     relic_context={'enemy_first_damage_unused': 1})
        self.assertEqual(r['total_damage'], 9000)
        self.assertNotIn('first_damage_relic', r['components'][0])

    def test_explicit_back_resource_and_windup_preview_are_preserved(self):
        back = next(r for r in choices(OP, 1) if r['animation'] == 'Skill_1' and r['orientation'] == 'Back')
        args = {'operator': OP, 'skill': 1, 'base_attack': 1000,
                'timing': {'animation_reference': back['id'], 'windup_frames': 6}}
        before = copy.deepcopy(args)
        r = calculate_damage(args)
        self.assertEqual(args, before)
        self.assertEqual(r['components'][0]['times_seconds'], [.2, .6])
        s = r['timing']['streams'][0]
        self.assertTrue(s['original_animation_reference']['overridden_by_preview'])
        self.assertFalse(s['multi_melee_reference']['automatic_original_reference'])

    def test_special_reference_section_is_absent_on_other_skills_and_operators(self):
        for op, skill in ((OP, 2), (OP, 3), ('mechanist', 1), ('silverash', 1)):
            r = calculate_damage({'operator': op, 'skill': skill})
            self.assertFalse(any(s['id'] == 'multi_melee' for s in r['report']['sections']))


if __name__ == '__main__':
    unittest.main()
