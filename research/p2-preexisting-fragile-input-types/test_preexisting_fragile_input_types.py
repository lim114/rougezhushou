"""Keep the legacy S3 condition explicit without interpreting text as a tick."""
from copy import deepcopy
import unittest
from rouge.catalog import catalog
from rouge.damage import calculate_damage


class PreexistingFragileInputTypes(unittest.TestCase):
    def test_active_strings_cannot_confirm_or_deny_skill_fragile(self):
        for mode in ('frames', 'continuous'):
            for rank in range(1, 11):
                for value in ('false', 'False', 'true', '0', '1', '', ' ', 'unknown'):
                    with self.subTest(mode=mode, rank=rank, value=value):
                        with self.assertRaisesRegex(ValueError, 'preexisting_fragile不接受字符串'):
                            calculate_damage({'operator': 'silverash', 'skill': 3, 'skill_rank': rank,
                                              'timing_mode': mode, 'preexisting_fragile': value})

    def test_numeric_zero_one_null_and_absent_keep_existing_boolean_behavior(self):
        for mode in ('frames', 'continuous'):
            for rank in range(1, 11):
                args = {'operator': 'silverash', 'skill': 3, 'timing_mode': mode, 'skill_rank': rank}
                false = calculate_damage({**args, 'preexisting_fragile': False})
                true = calculate_damage({**args, 'preexisting_fragile': True})
                self.assertEqual(calculate_damage(args), false)
                for value in (None, 0, 0.0, -0.0):
                    self.assertEqual(calculate_damage({**args, 'preexisting_fragile': value}), false)
                for value in (1, 1.0):
                    self.assertEqual(calculate_damage({**args, 'preexisting_fragile': value}), true)

    def test_string_guard_does_not_expand_to_other_skill_or_operator(self):
        for op, profile in catalog()['operators'].items():
            for number in range(1, len(profile['skills']) + 1):
                if op == 'silverash' and number == 3:
                    continue
                args = {'operator': op, 'skill': number}
                self.assertEqual(calculate_damage({**args, 'preexisting_fragile': 'false'}), calculate_damage(args))

    def test_prior_training_and_skill_qualification_errors_are_preserved(self):
        for elite in (0, 1):
            for value in (False, True, 'false', '', None):
                with self.assertRaisesRegex(ValueError, '当前精英阶段尚未开放所选技能或专精'):
                    calculate_damage({'operator': 'silverash', 'skill': 3, 'skill_rank': 7,
                                      'elite': elite, 'preexisting_fragile': value})

    def test_string_guard_does_not_disappear_at_zero_enemy_or_window(self):
        for mode in ('frames', 'continuous'):
            for scope in ({'window_seconds': 0}, {'timing': {'target_disappears_seconds': 0}},
                          {'timing': {'target_windows': []}}):
                with self.assertRaisesRegex(ValueError, 'preexisting_fragile不接受字符串'):
                    calculate_damage({'operator': 'silverash', 'skill': 3, 'timing_mode': mode,
                                      'preexisting_fragile': 'false', **scope})
                valid = calculate_damage({'operator': 'silverash', 'skill': 3, 'timing_mode': mode,
                                          'preexisting_fragile': False, **scope})
                if scope.get('window_seconds') == 0 or scope.get('timing', {}).get('target_disappears_seconds') == 0:
                    self.assertEqual(valid['total_damage'], 0)
                else:
                    default = calculate_damage({'operator': 'silverash', 'skill': 3, 'timing_mode': mode, **scope})
                    self.assertEqual(valid, default)

    def test_cooperation_and_manual_damage_source_controls_keep_typed_flag_contract(self):
        for mode in ('frames', 'continuous'):
            for dtype in ('physical', 'magic', 'true'):
                args = {'operator': 'silverash', 'skill': 3, 'timing_mode': mode, 'window_seconds': 10,
                        'cooperative': True, 'effects': [{'kind': 'damage_taken', 'damage_type': dtype, 'value': .5}]}
                for boolean, number in ((False, 0), (True, 1)):
                    self.assertEqual(calculate_damage({**args, 'preexisting_fragile': boolean}),
                                     calculate_damage({**args, 'preexisting_fragile': number}))
                with self.assertRaisesRegex(ValueError, 'preexisting_fragile不接受字符串'):
                    calculate_damage({**args, 'preexisting_fragile': 'false'})

    def test_failure_preserves_caller_and_cached_source_catalog(self):
        request = {'operator': 'silverash', 'skill': 3, 'preexisting_fragile': 'false',
                   'timing': {'target_windows': [[0, 10]]}}
        original = deepcopy(request); public = deepcopy(catalog())
        with self.assertRaisesRegex(ValueError, 'preexisting_fragile不接受字符串'):
            calculate_damage(request)
        self.assertEqual(request, original)
        self.assertEqual(catalog(), public)


if __name__ == '__main__':
    unittest.main()
