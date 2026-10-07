from copy import deepcopy
from pathlib import Path
import sys
sys.dont_write_bytecode = True
import unittest

sys.path.insert(0, str(Path(sys.argv.pop(1)).resolve()))
from rouge.catalog import catalog
from rouge.damage import calculate_damage
from rouge.reporting import format_report

OP = 'char_1042_phatm2'


def calculate(raw=0, *, mode='frames', skill=2, **extra):
    return calculate_damage({'operator': OP, 'skill': skill, 'base_attack': 1000,
                             'window_seconds': 10, 'timing_mode': mode,
                             'bait_triggers': raw, **extra})


class IndependentBaitInputTests(unittest.TestCase):
    def test_zero_forms_match_complete_numeric_zero_result_and_report(self):
        for mode in ('frames', 'continuous'):
            for timing in ({}, {'target_windows': []}, {'target_disappears_seconds': 0}):
                expected = calculate(0, mode=mode, timing=timing)
                for raw in ('0', '0.0', '0e0', '-0', ' 0 ', 0.0):
                    with self.subTest(mode=mode, timing=timing, raw=raw):
                        result = calculate(raw, mode=mode, timing=timing)
                        self.assertEqual(result, expected)
                        self.assertEqual(format_report(result), format_report(expected))
                        self.assertNotIn('neural_bait_reference', result)

    def test_positive_forms_match_full_integer_result_including_report(self):
        for mode in ('frames', 'continuous'):
            for rank in (1, 7, 10):
                for parsed, forms in ((1, ('1', '1.0', '1e0', '+1', ' 1 ')),
                                      (100, ('100', '100.0', '1e2'))):
                    expected = calculate(parsed, mode=mode, skill_rank=rank)
                    for raw in forms:
                        with self.subTest(mode=mode, rank=rank, raw=raw):
                            result = calculate(raw, mode=mode, skill_rank=rank)
                            self.assertEqual(result, expected)
                            self.assertEqual(format_report(result), format_report(expected))
                            self.assertEqual(result['neural_bait_reference']['triggers_requested'], parsed)

    def test_application_range_and_integer_validation_remain(self):
        for mode in ('frames', 'continuous'):
            for raw in (-1, '-1.0', 0.5, '0.5', 101, '101.0', 'NaN', 'Infinity'):
                with self.subTest(mode=mode, raw=raw):
                    with self.assertRaises(ValueError):
                        calculate(raw, mode=mode)

    def test_other_phatm2_skills_ignore_arbitrary_inactive_field(self):
        for skill in (1, 3):
            for mode in ('frames', 'continuous'):
                base = {'operator': OP, 'skill': skill, 'base_attack': 1000,
                        'window_seconds': 10, 'timing_mode': mode}
                expected = calculate_damage(base)
                for raw in ('0.0', '1.0', {}, [], None, True, False):
                    with self.subTest(skill=skill, mode=mode, raw=raw):
                        self.assertEqual(calculate_damage({**base, 'bait_triggers': raw}), expected)

    def test_positive_count_does_not_invent_timing_or_snapshot(self):
        for mode in ('frames', 'continuous'):
            result = calculate('1.0', mode=mode)
            ref = result['neural_bait_reference']
            self.assertIsNone(result['total_damage'])
            self.assertFalse(result['complete'])
            self.assertIsNone(ref['snapshot_attack'])
            self.assertIsNone(ref['first_tick_seconds'])
            self.assertFalse(ref['events_scheduled'])
            self.assertIsNone(result['estimate']['skill']['window_dps'])

    def test_empty_ordinary_range_keeps_declared_positive_bait_unplaced(self):
        for mode in ('frames', 'continuous'):
            result = calculate('1e0', mode=mode, timing={'target_windows': []})
            self.assertIsNone(result['total_damage'])
            self.assertEqual(result, calculate(1, mode=mode, timing={'target_windows': []}))
            self.assertFalse(result['neural_bait_reference']['events_scheduled'])

    def test_zero_observation_and_zero_enemy_lifetime_keep_known_zero(self):
        for mode in ('frames', 'continuous'):
            for extra in ({'window_seconds': 0}, {'timing': {'target_disappears_seconds': 0}}):
                result = calculate('1.0', mode=mode, **extra)
                self.assertEqual(result, calculate(1, mode=mode, **extra))
                self.assertEqual(result['total_damage'], 0)
                self.assertFalse(result['neural_bait_reference']['affected_damage_phases']['window'])

    def test_public_callers_and_cached_catalog_are_preserved(self):
        cache = deepcopy(catalog())
        for raw in ('0.0', '1.0', '100.0'):
            scenario = {'operator': OP, 'skill': 2, 'base_attack': 1000,
                        'window_seconds': 10, 'bait_triggers': raw,
                        'timing_mode': 'continuous', 'timing': {'target_windows': [[0, 10]]}}
            original = deepcopy(scenario)
            calculate_damage(scenario)
            self.assertEqual(scenario, original)
        self.assertEqual(catalog(), cache)


if __name__ == '__main__':
    unittest.main()
