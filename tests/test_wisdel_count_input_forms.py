"""Declared shadow casts use the existing parsed-count gate and references."""
import copy
import unittest

from rouge.catalog import catalog
from rouge.damage import calculate_damage
from rouge.relics import mechanics
from rouge.reporting import format_report


OP = 'char_1035_wisdel'


def calculate(ghosts=0, casts=0, skill=1, mode='frames', **extra):
    return calculate_damage({'operator': OP, 'skill': skill, 'base_attack': 1000,
                             'window_seconds': 10, 'timing_mode': mode,
                             'ghost_count': ghosts, 'ghost_casts': casts, **extra})


class WisdelCountInputFormsTests(unittest.TestCase):
    def test_parsed_zero_ghosts_ignore_casts_and_match_full_numeric_zero(self):
        for skill in (1, 2, 3):
            for mode in ('frames', 'continuous'):
                expected = calculate(0, 0, skill, mode)
                for ghosts in (0, 0.0, '0', '0.0', '0e0', '-0'):
                    for casts in (1, '1.0', True, False, None, {}, [], 'bad', -1, '1001'):
                        with self.subTest(skill=skill, mode=mode, ghosts=ghosts, casts=casts):
                            result = calculate(ghosts, casts, skill, mode)
                            self.assertEqual(result, expected)
                            self.assertEqual(format_report(result), format_report(expected))
                            reference = result['wisdel_secondary_reference']
                            self.assertEqual(reference['ghost_casts_requested'], 0)
                            self.assertEqual(reference['ghost_declared_count_damage_reference'], 0)

    def test_active_aliases_match_full_integer_results_at_every_skill_rank(self):
        for skill in (1, 2, 3):
            for mode in ('frames', 'continuous'):
                for rank in range(1, 11):
                    for ghosts, raw_ghosts in ((1, '1.0'), (3, '3e0')):
                        for casts, forms in ((0, ('0', '0.0')), (1, ('1.0', '1e0')),
                                             (1000, ('1000.0', '1e3'))):
                            expected = calculate(ghosts, casts, skill, mode, skill_rank=rank)
                            for raw_casts in forms:
                                with self.subTest(skill=skill, mode=mode, rank=rank,
                                                  ghosts=raw_ghosts, casts=raw_casts):
                                    result = calculate(raw_ghosts, raw_casts, skill, mode,
                                                       skill_rank=rank)
                                    self.assertEqual(result, expected)
                                    self.assertEqual(format_report(result), format_report(expected))

    def test_positive_casts_stay_conditional_without_clock_or_phase_attribution(self):
        for skill in (1, 2, 3):
            for mode in ('frames', 'continuous'):
                result = calculate('1.0', '2.0', skill, mode)
                reference = result['wisdel_secondary_reference']
                self.assertEqual(reference['ghost_casts_requested'], 2)
                self.assertIsNone(reference['ghost_cast_times_seconds'])
                self.assertFalse(reference['ghost_full_cast_attribution_verified'])
                self.assertIsNone(reference['secondary_hit_times_seconds'])
                self.assertFalse(reference['shadow_lifecycle_verified'])
                self.assertFalse(reference['random_independence_verified'])
                self.assertIsNone(result['total_damage'])
                ghost = next(c for c in result['components'] if c['name'] == '魂灵之影施放')
                self.assertEqual(ghost['hits'], 0)
                self.assertNotIn('times_seconds', ghost)

    def test_positive_casts_in_zero_observation_keep_existing_error(self):
        for skill in (1, 2, 3):
            for mode in ('frames', 'continuous'):
                for casts in (1, '1', '1.0', '1e0'):
                    with self.subTest(skill=skill, mode=mode, casts=casts):
                        with self.assertRaisesRegex(ValueError, '^零长度观察窗口不能声明魂灵施放命中。$'):
                            calculate('1.0', casts, skill, mode, window_seconds=0)
                self.assertEqual(calculate('1.0', '0.0', skill, mode, window_seconds=0),
                                 calculate(1, 0, skill, mode, window_seconds=0))
                self.assertEqual(calculate('0.0', 'bad', skill, mode, window_seconds=0),
                                 calculate(0, 0, skill, mode, window_seconds=0))

    def test_active_integer_bool_and_range_errors_keep_existing_contract(self):
        for mode in ('frames', 'continuous'):
            for value in (True, False, -1, .5, '0.5', 4, '4.0', 'NaN', 'Infinity'):
                with self.subTest(mode=mode, field='ghost_count', value=value):
                    with self.assertRaisesRegex(ValueError, 'ghost_count需要范围内的有限非负整数'):
                        calculate(value, 0, mode=mode)
            for value in (True, False, -1, .5, '0.5', 1001, '1001.0', 'NaN', 'Infinity'):
                with self.subTest(mode=mode, field='ghost_casts', value=value):
                    with self.assertRaisesRegex(ValueError, 'ghost_casts需要范围内的有限非负整数'):
                        calculate(1, value, mode=mode)
            for value in (None, {}, []):
                with self.assertRaises(TypeError):
                    calculate(1, value, mode=mode)
            with self.assertRaises(ValueError):
                calculate(1, 'bad', mode=mode)

    def test_missing_fields_and_unrelated_operators_keep_complete_results(self):
        for mode in ('frames', 'continuous'):
            plain = {'operator': OP, 'skill': 1, 'base_attack': 1000,
                     'window_seconds': 10, 'timing_mode': mode}
            self.assertEqual(calculate_damage(plain), calculate(0, 0, mode=mode))
            for operator, skill in (('silverash', 3), ('mechanist', 3), ('char_1042_phatm2', 2)):
                args = {**plain, 'operator': operator, 'skill': skill}
                for ghosts, casts in ((True, 'bad'), (None, {}), ([], '1.0')):
                    with self.subTest(operator=operator, mode=mode, ghosts=ghosts, casts=casts):
                        self.assertEqual(calculate_damage({**args, 'ghost_count': ghosts,
                                                          'ghost_casts': casts}), calculate_damage(args))

    def test_enemy_and_range_boundaries_keep_corresponding_numeric_references(self):
        for skill in (1, 2, 3):
            for mode in ('frames', 'continuous'):
                for timing in ({'target_windows': []}, {'target_disappears_seconds': 0}):
                    for ghosts, casts in ((0, 0), (1, 0), (1, 2)):
                        with self.subTest(skill=skill, mode=mode, timing=timing, ghosts=ghosts, casts=casts):
                            self.assertEqual(calculate(str(float(ghosts)), str(float(casts)), skill, mode,
                                                       timing=timing), calculate(ghosts, casts, skill, mode, timing=timing))

    def test_public_inputs_and_shared_parameter_caches_are_unchanged(self):
        before_catalog = copy.deepcopy(catalog())
        before_mechanics = copy.deepcopy(mechanics())
        for ghosts, casts in (('0.0', {}), ('1.0', '1.0'), (True, 0), (1, None)):
            args = {'operator': OP, 'skill': 1, 'ghost_count': ghosts, 'ghost_casts': casts}
            before = copy.deepcopy(args)
            try:
                calculate_damage(args)
            except (ValueError, TypeError):
                pass
            self.assertEqual(args, before)
        self.assertEqual(catalog(), before_catalog)
        self.assertEqual(mechanics(), before_mechanics)


if __name__ == '__main__':
    unittest.main()
