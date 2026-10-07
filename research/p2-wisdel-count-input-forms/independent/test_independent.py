from copy import deepcopy
from pathlib import Path
import sys
import unittest
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(sys.argv.pop(1)).resolve()))
from rouge.catalog import catalog
from rouge.damage import calculate_damage
from rouge.relics import mechanics
from rouge.reporting import format_report

OP = 'char_1035_wisdel'


def calculate(ghosts=0, casts=0, *, skill=2, mode='frames', **extra):
    return calculate_damage({'operator': OP, 'skill': skill, 'base_attack': 1000,
                             'window_seconds': 10, 'timing_mode': mode,
                             'ghost_count': ghosts, 'ghost_casts': casts, **extra})


class IndependentWisdelInputTests(unittest.TestCase):
    def test_zero_count_aliases_ignore_entire_inactive_cast_field(self):
        for skill in (1, 2, 3):
            for mode in ('frames', 'continuous'):
                expected = calculate(0, 0, skill=skill, mode=mode)
                for ghosts in (0, 0.0, '0', '0.0', '-0', '0e0'):
                    for casts in (0, '0.0', '1.0', -1, 'bad', {}, [], None, True, False):
                        with self.subTest(skill=skill, mode=mode, ghosts=ghosts, casts=casts):
                            result = calculate(ghosts, casts, skill=skill, mode=mode)
                            self.assertEqual(result, expected)
                            self.assertEqual(format_report(result), format_report(expected))
                            self.assertEqual(result['wisdel_secondary_reference']['ghost_casts_requested'], 0)
                            self.assertIsNone(result['wisdel_secondary_reference']['ghost_per_cast_damage_reference'])

    def test_present_count_forms_and_window_cast_forms_match_complete_integers(self):
        for skill in (1, 2, 3):
            for mode in ('frames', 'continuous'):
                for rank in (1, 7, 10):
                    for ghosts, parsed_ghosts in (('1.0', 1), ('1e0', 1), ('3.0', 3)):
                        for casts, parsed_casts in (('0.0', 0), ('0e0', 0), ('1.0', 1), ('1e0', 1), ('1e3', 1000)):
                            with self.subTest(skill=skill, mode=mode, rank=rank, ghosts=ghosts, casts=casts):
                                result = calculate(ghosts, casts, skill=skill, mode=mode, skill_rank=rank)
                                expected = calculate(parsed_ghosts, parsed_casts, skill=skill, mode=mode, skill_rank=rank)
                                self.assertEqual(result, expected)
                                self.assertEqual(format_report(result), format_report(expected))

    def test_raw_bool_is_rejected_only_when_existing_integer_query_is_active(self):
        for skill in (1, 2, 3):
            for mode in ('frames', 'continuous'):
                for raw in (True, False):
                    with self.subTest(skill=skill, mode=mode, raw=raw):
                        with self.assertRaisesRegex(ValueError, 'ghost_count需要范围内的有限非负整数'):
                            calculate(raw, 0, skill=skill, mode=mode)
                        with self.assertRaisesRegex(ValueError, 'ghost_casts需要范围内的有限非负整数'):
                            calculate(1, raw, skill=skill, mode=mode)
                        self.assertEqual(calculate(0, raw, skill=skill, mode=mode), calculate(0, 0, skill=skill, mode=mode))

    def test_existing_application_integer_ranges_and_bad_type_errors_remain(self):
        for mode in ('frames', 'continuous'):
            for raw in (-1, .5, '0.5', 4, '4.0', 'NaN', 'Infinity'):
                with self.subTest(mode=mode, field='ghost_count', raw=raw):
                    with self.assertRaises(ValueError):
                        calculate(raw, 0, mode=mode)
            for raw in (-1, .5, '0.5', 1001, '1001.0', 'NaN', 'Infinity'):
                with self.subTest(mode=mode, field='ghost_casts', raw=raw):
                    with self.assertRaises(ValueError):
                        calculate(1, raw, mode=mode)
            for raw in (None, {}, []):
                with self.assertRaises(TypeError):
                    calculate(raw, 0, mode=mode)
                with self.assertRaises(TypeError):
                    calculate(1, raw, mode=mode)

    def test_positive_zero_window_hits_keep_original_error_and_zero_casts_are_valid(self):
        for skill in (1, 2, 3):
            for mode in ('frames', 'continuous'):
                for casts in (1, '1.0', '1e0'):
                    with self.subTest(skill=skill, mode=mode, casts=casts):
                        with self.assertRaisesRegex(ValueError, '零长度观察窗口不能声明魂灵施放命中'):
                            calculate('1.0', casts, skill=skill, mode=mode, window_seconds=0)
                result = calculate('1.0', '0.0', skill=skill, mode=mode, window_seconds=0)
                self.assertEqual(result, calculate(1, 0, skill=skill, mode=mode, window_seconds=0))
                self.assertEqual(result['total_damage'], 0)
                self.assertEqual(calculate('0.0', {}, skill=skill, mode=mode, window_seconds=0)['total_damage'], 0)

    def test_declared_hits_keep_conditional_damage_and_unknown_clock(self):
        for skill in (1, 2, 3):
            for mode in ('frames', 'continuous'):
                result = calculate('1.0', '2.0', skill=skill, mode=mode)
                ref = result['wisdel_secondary_reference']
                self.assertEqual(ref['ghost_casts_requested'], 2)
                self.assertEqual(ref['ghost_declared_count_damage_reference'], 2*ref['ghost_per_cast_damage_reference'])
                self.assertIsNone(ref['ghost_cast_times_seconds'])
                self.assertFalse(ref['ghost_full_cast_attribution_verified'])
                self.assertIsNone(result['total_damage'])
                self.assertFalse(ref['random_independence_verified'])
                ghost = next(c for c in result['components'] if c['name']=='魂灵之影施放')
                self.assertEqual(ghost['hits'], 0)
                self.assertNotIn('times_seconds', ghost)

    def test_other_owners_ignore_both_options_without_new_validation(self):
        for operator, skill in (('mechanist', 3), ('silverash', 2), ('char_1042_phatm2', 2)):
            for mode in ('frames', 'continuous'):
                base = {'operator': operator, 'skill': skill, 'base_attack': 1000,
                        'window_seconds': 10, 'timing_mode': mode}
                self.assertEqual(calculate_damage({**base, 'ghost_count': {}, 'ghost_casts': None}), calculate_damage(base))

    def test_public_input_and_parameter_caches_are_preserved(self):
        before_catalog, before_mechanics = deepcopy(catalog()), deepcopy(mechanics())
        for ghosts, casts in (('0.0', {}), ('1.0', '1.0'), ('3.0', '1e3'), (True, False)):
            scenario = {'operator': OP, 'skill': 2, 'ghost_count': ghosts, 'ghost_casts': casts}
            original = deepcopy(scenario)
            try:
                calculate_damage(scenario)
            except (ValueError, TypeError):
                pass
            self.assertEqual(scenario, original)
        self.assertEqual(catalog(), before_catalog)
        self.assertEqual(mechanics(), before_mechanics)


if __name__ == '__main__':
    unittest.main()
