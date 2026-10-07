"""Text does not confirm the existing offline cooperative coverage condition."""
from copy import deepcopy
import re
import unittest

from rouge.catalog import catalog
from rouge.damage import calculate_damage


TEXTS = ('false', 'False', 'true', '0', '1', '', ' ', 'unknown')
ERROR = 'cooperative不接受字符串，请提供明确的布尔条件。'


def scenario(mode='frames', **extra):
    return {'operator': 'silverash', 'skill': 3, 'base_attack': 1000,
            'window_seconds': 10, 'timing_mode': mode, **extra}


class CooperativeInputTypesTests(unittest.TestCase):
    def test_qualified_s3_strings_cannot_confirm_or_deny_cooperative_coverage(self):
        for mode in ('frames', 'continuous'):
            for rank in range(1, 11):
                for value in TEXTS:
                    with self.subTest(mode=mode, rank=rank, value=repr(value)):
                        with self.assertRaisesRegex(ValueError, '^' + re.escape(ERROR) + '$'):
                            calculate_damage(scenario(mode, skill_rank=rank, cooperative=value))

    def test_bool_numeric_null_absent_and_other_nontext_keep_old_full_outputs(self):
        for mode in ('frames', 'continuous'):
            for rank in (1, 7, 10):
                args = scenario(mode, skill_rank=rank)
                off = calculate_damage({**args, 'cooperative': False})
                on = calculate_damage({**args, 'cooperative': True})
                self.assertEqual(calculate_damage(args), off)
                for value in (None, 0, 0.0, -0.0, [], {}):
                    self.assertEqual(calculate_damage({**args, 'cooperative': value}), off)
                for value in (1, 1.0, 2, -1, [False], {'enabled': False}):
                    self.assertEqual(calculate_damage({**args, 'cooperative': value}), on)

    def test_inactive_s1_s2_and_other_owners_ignore_text_without_a_global_policy(self):
        for operator, profile in catalog()['operators'].items():
            for skill in range(1, len(profile['skills']) + 1):
                if operator == 'silverash' and skill == 3:
                    continue
                for mode in ('frames', 'continuous'):
                    args = scenario(mode, operator=operator, skill=skill)
                    absent = calculate_damage(args)
                    for text in ('false', 'unknown', '0', '1', ''):
                        self.assertEqual(calculate_damage({**args, 'cooperative': text}), absent)

    def test_existing_training_and_skill_qualification_errors_precede_text_guard(self):
        for elite in (0, 1):
            for mode in ('frames', 'continuous'):
                for value in TEXTS:
                    with self.assertRaisesRegex(ValueError, '^' + re.escape(
                            '当前精英阶段尚未开放所选技能或专精。') + '$'):
                        calculate_damage(scenario(mode, elite=elite, skill_rank=7,
                            cooperative=value, preexisting_fragile='false'))
        for args, message in (({'skill': True}, '请选择该干员的有效技能。'),
                              ({'skill_rank': True}, '技能等级需要为1–10的整数。')):
            with self.assertRaisesRegex(ValueError, '^' + re.escape(message) + '$'):
                calculate_damage(scenario(cooperative='unknown', **args))

    def test_section64_fragile_text_guard_retains_error_priority(self):
        for mode in ('frames', 'continuous'):
            for text in TEXTS:
                with self.assertRaisesRegex(ValueError, '^' + re.escape(
                        'preexisting_fragile不接受字符串，请提供明确的布尔条件。') + '$'):
                    calculate_damage(scenario(mode, preexisting_fragile=text,
                                              cooperative='unknown'))

    def test_string_guard_is_not_hidden_by_empty_observation_or_enemy_lifetime(self):
        for mode in ('frames', 'continuous'):
            for extra in ({'window_seconds': 0}, {'timing': {'target_disappears_seconds': 0}},
                          {'timing': {'target_windows': []}}):
                for text in ('false', ''):
                    with self.assertRaisesRegex(ValueError, '^' + re.escape(ERROR) + '$'):
                        calculate_damage(scenario(mode, cooperative=text, **extra))
                for boolean, numeric in ((False, 0), (True, 1)):
                    expected = calculate_damage(scenario(mode, cooperative=boolean, **extra))
                    self.assertEqual(calculate_damage(scenario(mode, cooperative=numeric, **extra)), expected)
                    if extra.get('window_seconds') == 0 or extra.get('timing', {}).get('target_disappears_seconds') == 0:
                        self.assertEqual(expected['total_damage'], 0)

    def test_existing_fragile_and_external_damage_formula_remains_typed_compatibility(self):
        for mode in ('frames', 'continuous'):
            for fragile in (False, True):
                for dtype in ('physical', 'magic', 'true'):
                    args = scenario(mode, preexisting_fragile=fragile,
                        effects=[{'kind': 'damage_taken', 'damage_type': dtype, 'value': .5}])
                    for boolean, number in ((False, 0), (True, 1)):
                        self.assertEqual(calculate_damage({**args, 'cooperative': boolean}),
                                         calculate_damage({**args, 'cooperative': number}))

    def test_rejection_and_accepted_boolean_leave_caller_and_catalog_unchanged(self):
        original_catalog = deepcopy(catalog())
        for value in ('false', '', True, False):
            args = scenario(cooperative=value, timing={'target_windows': [[0, 10]]})
            original = deepcopy(args)
            if isinstance(value, str):
                with self.assertRaisesRegex(ValueError, '^' + re.escape(ERROR) + '$'):
                    calculate_damage(args)
            else:
                calculate_damage(args)
            self.assertEqual(args, original)
        self.assertEqual(catalog(), original_catalog)


if __name__ == '__main__':
    unittest.main()
