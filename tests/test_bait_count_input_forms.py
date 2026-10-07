"""Accepted integer aliases share the existing manual bait reference contract."""
import copy
import unittest

from rouge.catalog import catalog
from rouge.damage import calculate_damage
from rouge.relics import mechanics
from rouge.reporting import format_report


OP = 'char_1042_phatm2'


def calculate(count=0, mode='frames', skill=2, **extra):
    return calculate_damage({'operator': OP, 'skill': skill, 'base_attack': 1000,
                             'window_seconds': 10, 'timing_mode': mode,
                             'bait_triggers': count, **extra})


class BaitCountInputFormsTests(unittest.TestCase):
    def test_zero_aliases_keep_full_numeric_zero_result_and_report(self):
        for mode in ('frames', 'continuous'):
            expected = calculate(0, mode)
            for value in (0.0, '0', '0.0', '0e0', '-0', ' 0 '):
                with self.subTest(mode=mode, value=value):
                    result = calculate(value, mode)
                    self.assertEqual(result, expected)
                    self.assertEqual(format_report(result), format_report(expected))
                    self.assertNotIn('neural_bait_reference', result)

    def test_positive_aliases_match_full_integer_result_at_every_rank(self):
        for mode in ('frames', 'continuous'):
            for rank in range(1, 11):
                for count, forms in ((1, (1.0, '1', '1.0', '1e0', '+1', ' 1 ')),
                                     (100, (100.0, '100', '100.0', '1e2'))):
                    expected = calculate(count, mode, skill_rank=rank)
                    for value in forms:
                        with self.subTest(mode=mode, rank=rank, value=value):
                            result = calculate(value, mode, skill_rank=rank)
                            self.assertEqual(result, expected)
                            self.assertEqual(format_report(result), format_report(expected))
                            self.assertEqual(result['neural_bait_reference']['triggers_requested'], count)

    def test_missing_count_and_zero_observation_preserve_numeric_contract(self):
        for mode in ('frames', 'continuous'):
            plain = {'operator': OP, 'skill': 2, 'base_attack': 1000,
                     'window_seconds': 10, 'timing_mode': mode}
            self.assertEqual(calculate_damage(plain), calculate(0, mode))
            for extra in ({'window_seconds': 0}, {'timing': {'target_disappears_seconds': 0}},
                          {'timing': {'target_windows': []}}):
                for count, forms in ((0, ('0', '0.0')), (1, ('1.0', '1e0'))):
                    for value in forms:
                        with self.subTest(mode=mode, extra=extra, value=value):
                            self.assertEqual(calculate(value, mode, **extra),
                                             calculate(count, mode, **extra))

    def test_positive_count_keeps_snapshot_clock_and_event_schedule_unknown(self):
        for mode in ('frames', 'continuous'):
            result = calculate('1.0', mode)
            reference = result['neural_bait_reference']
            self.assertIsNone(reference['snapshot_attack'])
            self.assertIsNone(reference['first_tick_seconds'])
            self.assertFalse(reference['events_scheduled'])
            self.assertIsNone(result['total_damage'])
            self.assertIsNone(result['estimate']['skill']['window_dps'])
            self.assertFalse(result['complete'])

    def test_existing_finite_integer_range_and_bool_errors_are_preserved(self):
        for mode in ('frames', 'continuous'):
            for value in (True, False, -1, '-1', .5, '0.5', 101, '101.0',
                          'NaN', 'Infinity'):
                with self.subTest(mode=mode, value=value):
                    with self.assertRaisesRegex(ValueError, 'bait_triggers需要范围内的有限非负整数'):
                        calculate(value, mode)
            with self.assertRaises(ValueError):
                calculate('bad', mode)
            for value in (None, {}, []):
                with self.subTest(mode=mode, value=value):
                    with self.assertRaises(TypeError):
                        calculate(value, mode)

    def test_irrelevant_skills_and_operators_ignore_unused_field(self):
        for mode in ('frames', 'continuous'):
            for operator, skill in ((OP, 1), (OP, 3), ('silverash', 3), ('mechanist', 3)):
                plain = {'operator': operator, 'skill': skill, 'base_attack': 1000,
                         'window_seconds': 10, 'timing_mode': mode}
                expected = calculate_damage(plain)
                for value in ('0.0', '1.0', True, False, None, {}, []):
                    with self.subTest(mode=mode, operator=operator, skill=skill, value=value):
                        self.assertEqual(calculate_damage({**plain, 'bait_triggers': value}), expected)

    def test_resistance_and_river_contexts_match_existing_integer_reference(self):
        for mode in ('frames', 'continuous'):
            for extra in ({'enemy_buildup_resistance': 100},
                          {'relic_ids': ['rogue_6_relic_fight_22']}):
                for count, value in ((0, '0.0'), (1, '1.0')):
                    with self.subTest(mode=mode, extra=extra, value=value):
                        self.assertEqual(calculate(value, mode, **extra), calculate(count, mode, **extra))

    def test_public_input_and_shared_parameter_caches_are_unchanged(self):
        before_catalog = copy.deepcopy(catalog())
        before_mechanics = copy.deepcopy(mechanics())
        for value in ('0.0', '1.0', '1e2', True, {}, None):
            args = {'operator': OP, 'skill': 2, 'bait_triggers': value}
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
