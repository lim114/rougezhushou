"""Cast attribution uses emitted token impacts; observation and normal stay bounded.

Fixed counts below are arithmetic for a deliberately supplied manual reference:
E2/L70 tentacle interval1.25s/100AS =>38 frames, explicit windup1/recovery0;
S1M3 nominal30s=900frames and S2M3 nominal55s=1650frames.
This does not prove the game's actual token animation or projectile/lifetime.
"""
import copy
import unittest
from rouge.damage import calculate_damage

OP = 'char_110_deepcl'
TOKEN = 'token_10001_deepcl_tentac'
MODULE = 'uniequip_002_deepcl'


def scenario(skill=1, travel=10, mode='frames', count=1, window=None,
             lifetime=None, unit_extra=None, **extra):
    unit = {'windup_frames': 1, 'recovery_frames': 0}
    if travel is not None:
        unit['projectile_travel_seconds'] = travel
    unit.update(unit_extra or {})
    timing = {'windup_frames': 1, 'recovery_frames': 0, 'units': {TOKEN: unit}}
    if lifetime is not None:
        timing['target_disappears_seconds'] = lifetime
    result = {'operator': OP, 'skill': skill, 'elite': 2, 'level': 70,
              'skill_rank': 10, 'trust': 100, 'potential': 1,
              'module_id': None, 'module_level': 0, 'summon_count': count,
              'enemy_defense': 0, 'enemy_resistance': 0,
              'relic_ids': [], 'effects': [], 'timing_mode': mode, 'timing': timing}
    if window is not None:
        result['window_seconds'] = window
    result.update(extra)
    return result


def token_component(result):
    return next(c for c in result['components'] if c['name'] == '触手')


def owner_component(result):
    return next(c for c in result['components'] if c['name'] == '本体普攻')


def token_stream(result, normal=False):
    key = 'recharge_streams' if normal else 'streams'
    return next(s for s in result['timing'][key] if s['unit'] == TOKEN)


class TokenFullCastTailTests(unittest.TestCase):
    def test_fixed_full_cast_keeps_tail_but_public_components_are_nominal_observation(self):
        for skill, cast_hits, window_hits in ((1, 24, 16), (2, 44, 36)):
            with self.subTest(skill=skill):
                result = calculate_damage(scenario(skill))
                cast = result['estimate']['skill']
                token = token_component(result)
                stream = token_stream(result)
                self.assertEqual(cast['hit_counts']['触手'], cast_hits)
                self.assertEqual(token['hits'], window_hits)
                self.assertEqual(len(stream['emitted_times_seconds']), cast_hits)
                self.assertEqual(len(stream['times_seconds']), window_hits)
                self.assertGreater(stream['emitted_times_seconds'][-1], cast['duration_seconds'])
                self.assertAlmostEqual(cast['total_damage'] - result['total_damage'],
                                       (cast_hits - window_hits) * token['per_hit'])
                self.assertAlmostEqual(cast['phase_damage'], result['total_damage'])
                self.assertEqual(token['times_seconds'], stream['times_seconds'])

    def test_short_and_zero_observation_do_not_cut_the_independent_full_cast(self):
        for skill in (1, 2):
            full = calculate_damage(scenario(skill))
            for window in (0, 5):
                with self.subTest(skill=skill, window=window):
                    result = calculate_damage(scenario(skill, window=window))
                    self.assertEqual(result['estimate']['skill']['total_damage'],
                                     full['estimate']['skill']['total_damage'])
                    self.assertEqual(result['estimate']['skill']['hit_counts'],
                                     full['estimate']['skill']['hit_counts'])
                    self.assertEqual(token_component(result)['hits'], 0)
                    self.assertEqual(result['estimate']['skill']['window_seconds'], window)
                    self.assertTrue(all(t < window for c in result['components']
                                        for t in c.get('times_seconds', [])))
                    if window == 0:
                        self.assertEqual(result['total_damage'], 0)

    def test_late_tail_is_not_promoted_into_phase_or_this_cycle(self):
        for skill, cast_hits in ((1, 24), (2, 44)):
            with self.subTest(skill=skill):
                baseline = calculate_damage(scenario(skill, travel=0))
                result = calculate_damage(scenario(skill, travel=200))
                cast = result['estimate']['skill']
                stream = token_stream(result)
                self.assertEqual(cast['hit_counts']['触手'], cast_hits)
                self.assertEqual(cast['total_damage'], baseline['estimate']['skill']['total_damage'])
                self.assertEqual(token_component(result)['hits'], 0)
                self.assertEqual(stream['times_seconds'], [])
                self.assertTrue(all(t > cast['cycle_seconds'] for t in stream['emitted_times_seconds']))
                self.assertAlmostEqual(cast['phase_damage'], owner_component(result)['total'])
                self.assertEqual(token_stream(result, normal=True)['times_seconds'], [])
                self.assertGreater(cast['total_damage'], cast['phase_damage'])

    def test_target_disappearance_cancels_impacts_including_potential_cast_tail(self):
        for skill in (1, 2):
            with self.subTest(skill=skill):
                result = calculate_damage(scenario(skill, lifetime=20))
                cast = result['estimate']['skill']
                self.assertEqual(cast['hit_counts']['触手'], 8)
                self.assertEqual(token_component(result)['hits'], 8)
                self.assertEqual(token_stream(result)['emitted_times_seconds'],
                                 token_stream(result)['times_seconds'])
                self.assertTrue(all(t < 20 for t in token_stream(result)['emitted_times_seconds']))
                empty = calculate_damage(scenario(skill, lifetime=0))
                self.assertEqual(empty['total_damage'], 0)
                self.assertEqual(empty['estimate']['skill']['total_damage'], 0)
                self.assertEqual(empty['estimate']['skill']['hit_counts']['触手'], 0)

    def test_independent_unit_range_exit_does_not_destroy_its_locked_tail(self):
        result = calculate_damage(scenario(1, unit_extra={'target_windows': [[28, 30]]}))
        cast = result['estimate']['skill']
        stream = token_stream(result)
        self.assertEqual(cast['hit_counts']['触手'], 2)
        self.assertEqual(token_component(result)['hits'], 0)
        self.assertEqual(stream['release_frames'], [841, 879])
        self.assertEqual(stream['emitted_impact_frames'], [1141, 1179])
        self.assertEqual(stream['times_seconds'], [])
        self.assertGreater(cast['total_damage'], cast['phase_damage'])

    def test_normal_recharge_reference_still_uses_window_impacts_not_its_emitted_tail(self):
        for skill in (1, 2):
            with self.subTest(skill=skill):
                result = calculate_damage(scenario(skill))
                cast = result['estimate']['skill']
                normal_token = token_stream(result, normal=True)
                normal_owner = next(s for s in result['timing']['recharge_streams'] if s['unit'] == OP)
                self.assertLess(len(normal_token['times_seconds']),
                                len(normal_token['emitted_times_seconds']))
                # Fixed E2/L70 token attack462 does not inherit trust or S1's +60% in normal.
                normal_damage = (len(normal_owner['times_seconds']) * owner_component(result)['per_hit']
                                 + len(normal_token['times_seconds']) * 462)
                # Every full-cast impact in this10s reference lands before the cycle ends.
                self.assertTrue(all(t < cast['cycle_seconds'] for t in token_stream(result)['emitted_times_seconds']))
                self.assertAlmostEqual(cast['cycle_damage'], cast['total_damage'] + normal_damage)
                self.assertTrue(all(t < cast['recharge_seconds'] for t in normal_token['times_seconds']))

    def test_continuous_and_zero_travel_keep_the_original_reference(self):
        for skill, hits in ((1, 24), (2, 44)):
            no_delay = calculate_damage(scenario(skill, travel=None))
            explicit_zero = calculate_damage(scenario(skill, travel=0))
            for result in (no_delay, explicit_zero):
                self.assertEqual(result['estimate']['skill']['hit_counts']['触手'], hits)
                self.assertEqual(token_component(result)['hits'], hits)
                self.assertAlmostEqual(result['total_damage'], result['estimate']['skill']['total_damage'])
            self.assertEqual(no_delay['estimate']['skill'], explicit_zero['estimate']['skill'])
            for window in (None, 0, 5):
                with self.subTest(skill=skill, window=window):
                    base = calculate_damage(scenario(skill, travel=0, mode='continuous', window=window))
                    delayed = calculate_damage(scenario(skill, travel=10, mode='continuous', window=window))
                    self.assertEqual(base, delayed)
                    self.assertEqual(delayed['estimate']['skill']['hit_counts']['触手'], hits)

    def test_count_module_and_manual_token_attributes_keep_the_same_cast_attribution(self):
        for skill, one_cast, one_window in ((1, 24, 16), (2, 44, 36)):
            for count in (0, 1, 4):
                for module in (0, 1, 2, 3):
                    with self.subTest(skill=skill, count=count, module=module):
                        extra = {'module_id': MODULE, 'module_level': module} if module else {}
                        result = calculate_damage(scenario(skill, count=count, **extra))
                        self.assertEqual(result['estimate']['skill']['hit_counts']['触手'], one_cast * count)
                        self.assertEqual(token_component(result)['hits'], one_window * count)
                        self.assertAlmostEqual(result['estimate']['skill']['total_damage'] - result['total_damage'],
                                               (one_cast - one_window) * count * token_component(result)['per_hit'])
            effect = {'kind': 'attack_pct', 'value': .25, 'target_scope': 'all_units'}
            result = calculate_damage(scenario(skill, effects=[effect]))
            token = token_component(result)
            self.assertEqual(result['estimate']['skill']['hit_counts']['触手'], one_cast)
            self.assertAlmostEqual(token['per_hit'], 462 * (1.25 + (.6 if skill == 1 else 0)))
            self.assertAlmostEqual(result['estimate']['skill']['total_damage'] - result['total_damage'],
                                   (one_cast - one_window) * token['per_hit'])


if __name__ == '__main__':
    unittest.main()
