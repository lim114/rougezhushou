from copy import deepcopy
from unittest import TestCase
from rouge.supplemental_enemies import enemy_defaults, compare_fixed_enemies
from rouge.supplemental_skills import defaults
from tests.test_supplemental_run_141 import environment


class EnemyDefaultGradeTests(TestCase):
    def test_existing_invalid_grade_is_not_replaced_with_four(self):
        for value in (None, True, False, -1, 16, 4.0, '4', [], {}, 10**1000):
            env = environment()
            env['run_config'] = {'difficulty': {'value': value}}
            before = deepcopy(env)
            preview = enemy_defaults(env)
            self.assertEqual(preview['grades'], [])
            self.assertEqual(env, before)
            with self.assertRaisesRegex(ValueError, 'grades'):
                compare_fixed_enemies(defaults(), env, preview)

    def test_zero_and_upper_grade_remain_exact(self):
        for value in (0, 4, 15):
            self.assertEqual(enemy_defaults({'run_config': {'difficulty': {'value': value}}})['grades'], [value])

    def test_missing_setting_retains_manual_comparison_default(self):
        for env in ({}, {'run_config': None}, {'run_config': {}}, {'run_config': {'difficulty': {}}}):
            self.assertEqual(enemy_defaults(env)['grades'], [4])
