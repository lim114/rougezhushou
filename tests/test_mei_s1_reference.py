import unittest
from rouge.damage import calculate_damage
from rouge.estimate import format_estimate


def evaluate(**extra):
    return calculate_damage({'operator': 'char_133_mm', 'skill': 1,
                             'base_attack': 1000, 'enemy_defense': 0, **extra})


class MeiS1ReferenceTests(unittest.TestCase):
    def test_declared_zero_short_and_long_observation_windows_are_preserved(self):
        for mode in ('frames', 'continuous'):
            for window in (0, 1, 20):
                with self.subTest(mode=mode, window=window):
                    r = evaluate(timing_mode=mode, window_seconds=window)
                    self.assertEqual(r['estimate']['skill']['window_seconds'], window)
                    self.assertEqual(r['components'][0]['hits'], int(window > 0))
                    self.assertEqual(r['components'][0]['per_hit'], 2140)
                    if window == 0:
                        self.assertEqual(r['total_damage'], 0)
                        self.assertFalse(r['mei_s1_reference']['source_possible']['window'])
                    else:
                        self.assertIsNone(r['total_damage'])
                        self.assertTrue(r['mei_s1_reference']['source_possible']['window'])

    def test_frame_release_on_observation_end_is_excluded(self):
        for window, possible in ((1 / 30, False), (2 / 30, True)):
            r = evaluate(window_seconds=window)
            self.assertEqual(r['mei_s1_reference']['source_possible']['window'], possible)
            self.assertEqual(r['components'][0]['hits'], int(possible))
            self.assertEqual(r['estimate']['skill']['window_seconds'], window)

    def test_continuous_reference_retains_its_interval_boundary(self):
        interval = 100 / 107
        for window, possible in ((interval - 1e-5, False), (interval, True), (interval + 1e-5, True)):
            r = evaluate(timing_mode='continuous', window_seconds=window)
            self.assertEqual(r['mei_s1_reference']['source_possible']['window'], possible)
            self.assertEqual(r['components'][0]['hits'], int(possible))

    def test_late_supply_is_acquired_once_in_a_long_observation(self):
        r = evaluate(window_seconds=20, timing={'target_windows': [[10, 20]]})
        ref = r['mei_s1_reference']
        self.assertTrue(ref['source_possible']['cast'])
        self.assertTrue(ref['source_possible']['window'])
        self.assertEqual(r['components'][0]['hits'], 1)
        self.assertEqual(ref['source_acquisition_times']['window'], [301 / 30])
        self.assertEqual(ref['parameter_clock_reference']['total_damage'], 2140)

    def test_supply_on_observation_end_is_not_observed_but_full_search_finds_it(self):
        r = evaluate(window_seconds=10, timing={'target_windows': [[10, 20]]})
        self.assertEqual(r['total_damage'], 0)
        self.assertFalse(r['mei_s1_reference']['source_possible']['window'])
        self.assertTrue(r['mei_s1_reference']['source_possible']['cast'])
        self.assertIsNone(r['estimate']['skill']['total_damage'])

    def test_full_single_attack_search_is_not_clipped_to_nominal_interval(self):
        r = evaluate(window_seconds=20, timing={'target_windows': [[1000, 1001]]})
        self.assertEqual(r['total_damage'], 0)
        ref = r['mei_s1_reference']
        self.assertTrue(ref['source_possible']['cast'])
        self.assertEqual(ref['source_acquisition_times']['cast'], [30001 / 30])
        self.assertEqual(ref['parameter_clock_reference']['total_damage'], 2140)

    def test_no_target_zero_lifetime_or_whole_horizon_blocking_is_known_zero(self):
        for mode in ('frames', 'continuous'):
            for timing in ({'target_windows': []}, {'target_disappears_seconds': 0},
                           {'interrupt_windows': [[0, 3600]]},
                           {'movement_windows': [[0, 1800]], 'interrupt_windows': [[1800, 3600]]}):
                with self.subTest(mode=mode, timing=timing):
                    r = evaluate(timing_mode=mode, window_seconds=20, timing=timing)
                    self.assertEqual(r['total_damage'], 0)
                    self.assertEqual(r['estimate']['skill']['total_damage'], 0)
                    self.assertFalse(r['mei_s1_reference']['source_possible']['cast'])
                    self.assertFalse(r['mei_s1_reference']['source_possible']['window'])

    def test_interrupt_windup_reacquires_after_blocking_ends(self):
        r = evaluate(window_seconds=20, timing={'windup_frames': 6, 'recovery_frames': 9,
                     'interrupt_windows': [[.1, 10]]})
        self.assertEqual(r['mei_s1_reference']['source_acquisition_times']['window'], [10.2])
        self.assertEqual(r['components'][0]['hits'], 1)

    def test_projectile_release_and_observed_impact_are_separate_references(self):
        timing = {'projectile_travel_seconds': 2}
        for window, possible in ((1, False), (61 / 30, False), (62 / 30, True)):
            r = evaluate(window_seconds=window, timing=timing)
            ref = r['mei_s1_reference']
            self.assertTrue(ref['source_possible']['cast'])
            self.assertEqual(ref['source_possible']['window'], possible)
            self.assertEqual(ref['source_acquisition_times']['window'], [1 / 30])
            self.assertEqual(ref['impact_times_reference']['cast'], [61 / 30])
            self.assertEqual(ref['impact_times_reference']['window'], [61 / 30] if possible else [])

    def test_target_disappearing_on_projectile_impact_suppresses_damage(self):
        r = evaluate(window_seconds=3, timing={'projectile_travel_seconds': 2,
                     'target_disappears_seconds': 61 / 30})
        self.assertEqual(r['total_damage'], 0)
        self.assertEqual(r['estimate']['skill']['total_damage'], 0)
        self.assertFalse(r['mei_s1_reference']['source_possible']['cast'])

    def test_known_talent_relic_and_mitigation_parameters_are_preserved(self):
        r = evaluate(enemy_defense=200, effects=[{'kind': 'attack_pct', 'value': .5}])
        self.assertEqual(r['mei_s1_reference']['per_hit_damage_reference'], 2940)
        self.assertEqual(r['mei_s1_reference']['parameter_clock_reference']['total_damage'], 2940)
        self.assertEqual(r['estimate']['base_stats']['attack_speed'], 107)
        self.assertEqual(r['mei_s1_reference']['attack_scale_parameter'], 2)
        self.assertEqual(r['mei_s1_reference']['sluggish_duration_parameter_seconds'], 2.5)

    def test_potential_and_attack_speed_change_only_their_verified_parameters(self):
        potential = evaluate(potential=5)
        self.assertEqual(potential['mei_s1_reference']['per_hit_damage_reference'], 2160)
        self.assertEqual(potential['attack_speed'], 108)
        faster = evaluate(effects=[{'kind': 'attack_speed', 'value': 25}])
        self.assertEqual(faster['mei_s1_reference']['per_hit_damage_reference'], 2140)
        self.assertEqual(faster['attack_speed'], 132)
        clock = faster['mei_s1_reference']['parameter_clock_reference']
        # ceil(30*100/132)=23 frames; three charging slots, then one next attack.
        self.assertEqual(clock['initial_seconds'], 69 / 30)
        self.assertAlmostEqual(clock['cycle_seconds'], 92 / 30)
        self.assertIsNone(faster['estimate']['skill']['cycle_seconds'])

    def test_default_attack_loop_clock_is_retained_as_a_parameter_example(self):
        r = evaluate()
        clock = r['mei_s1_reference']['parameter_clock_reference']
        self.assertEqual(clock['initial_seconds'], 84 / 30)
        self.assertEqual(clock['duration_seconds'], 2 / 30)
        self.assertEqual(clock['cycle_seconds'], 112 / 30)
        self.assertEqual(clock['total_damage'], 2140)
        self.assertTrue(clock['recharge_streams'])
        self.assertEqual(r['timing']['recharge_streams'], [])

    def test_preview_overrides_do_not_prove_actual_end_or_complete_cycle(self):
        for timing in ({}, {'windup_frames': 0, 'recovery_frames': 0},
                       {'windup_frames': 6, 'recovery_frames': 9}):
            r = evaluate(timing=timing)
            ref = r['mei_s1_reference']
            self.assertFalse(ref['skill_binding_verified'])
            self.assertFalse(ref['parameter_clock_binding_verified'])
            self.assertFalse(r['timing']['resource_and_damage_shared_clock'])
            self.assertIsNone(ref['actual_cast_end_seconds'])
            for key in ('initial_seconds', 'duration_seconds', 'recharge_seconds',
                        'cycle_seconds', 'cycle_damage', 'cycle_dps'):
                self.assertIsNone(r['estimate']['skill'][key])
            self.assertIsNone(r['total_damage'])
            self.assertIsNone(r['components'][0]['actual_total'])
            self.assertNotIn('times_seconds', r['components'][0])
            self.assertNotIn('instant_event', r['components'][0])

    def test_wine_initial_ready_and_six_frame_end_reference_are_preserved(self):
        r = evaluate(relic_ids=['rogue_6_relic_legacy_97'],
                     timing={'windup_frames': 6, 'recovery_frames': 9})
        skill = r['estimate']['skill']
        clock = r['mei_s1_reference']['parameter_clock_reference']
        self.assertEqual(skill['initial_seconds'], 0)
        self.assertEqual(clock['duration_seconds'], 7 / 30)
        self.assertAlmostEqual(clock['cycle_seconds'], 84 / 30)
        self.assertIsNone(skill['cycle_seconds'])

    def test_report_distinguishes_conditional_damage_clock_example_and_actual_unknown(self):
        text = format_estimate(evaluate(window_seconds=20))
        self.assertIn('麻痹弹 · 下次攻击与结束待核验', text)
        self.assertIn('单次物理伤害条件参考：2,140', text)
        self.assertIn('常规动作算例回转', text)
        self.assertIn('实际技能结束：未知', text)
        self.assertIn('单次技能总伤：未知', text)
        self.assertIn('观察窗口保持声明值', text)


if __name__ == '__main__':
    unittest.main()
