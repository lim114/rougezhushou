"""Explicit run settings must not acquire eligibility through truthiness."""
import unittest

from rouge.damage import calculate_damage


class RunConfigValidationTests(unittest.TestCase):
    def calculate(self, config):
        return calculate_damage({
            'operator': 'mechanist', 'skill': 1, 'elite': 2, 'level': 90,
            'trust': 100, 'potential': 1, 'skill_rank': 10,
            'module_id': None, 'module_level': 0, 'timing_mode': 'frames',
            'run_config': config,
        })

    def test_effect_verification_requires_an_actual_boolean(self):
        for value in ('false', 'true', 0, 1, None, [], {}):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, '确认标记需要布尔值'):
                self.calculate({'squad': {'id': 'rogue_6_band_6', 'effect_verified': value}})

    def test_false_and_omitted_verification_keep_squad_stats_pending(self):
        plain = self.calculate({})
        for supplied in ({}, {'effect_verified': False}):
            with self.subTest(supplied=supplied):
                result = self.calculate({'squad': {'id': 'rogue_6_band_6', **supplied}})
                self.assertEqual(result['estimate']['base_stats'], plain['estimate']['base_stats'])
                self.assertEqual(result['run_resolution']['applied'], [])
                self.assertTrue(result['run_resolution']['pending'])
                self.assertFalse(result['complete'])

    def test_squad_identity_rejects_non_string_values_with_a_clear_error(self):
        for value in ([], {}, False, 1, None):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, '分队身份与固定档案不符'):
                self.calculate({'squad': {'id': value, 'effect_verified': True}})

    def test_verified_squad_preserves_pinned_fifteen_percent_attributes(self):
        result = self.calculate({'squad': {'id': 'rogue_6_band_6', 'effect_verified': True}})
        stats = result['estimate']['base_stats']
        self.assertEqual((stats['attack'], stats['hp'], stats['defense']), (659, 4176, 880))
        self.assertEqual(len(result['run_resolution']['applied']), 3)

    def test_nested_settings_reject_non_objects_even_when_falsy(self):
        for field, label in (('squad', '分队'), ('difficulty', '保密等级')):
            for value in (False, 0, '', [], ['unexpected'], 'unexpected'):
                with self.subTest(field=field, value=value), self.assertRaisesRegex(ValueError, label+'配置需要对象'):
                    self.calculate({field: value})

    def test_none_and_empty_nested_settings_preserve_absent_configuration(self):
        plain = self.calculate({})
        for value in (None, {}):
            with self.subTest(value=value):
                result = self.calculate({'squad': value, 'difficulty': value})
                self.assertEqual(result['estimate']['base_stats'], plain['estimate']['base_stats'])
                self.assertEqual(result['total_damage'], plain['total_damage'])
                self.assertIsNone(result['run_resolution']['squad'])
                self.assertIsNone(result['run_resolution']['difficulty'])

    def test_outer_settings_reject_non_objects_even_when_falsy(self):
        for value in (False, 0, '', [], ['unexpected'], 'unexpected'):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, '本局配置需要对象'):
                self.calculate(value)

    def test_none_outer_settings_remain_equivalent_to_omitted(self):
        plain = self.calculate({})
        result = self.calculate(None)
        self.assertEqual(result['estimate']['base_stats'], plain['estimate']['base_stats'])
        self.assertEqual(result['total_damage'], plain['total_damage'])
        self.assertEqual(result['run_resolution'], plain['run_resolution'])

    def test_monthly_zero_never_acquires_normal_difficulty_modifiers(self):
        for field in ('modeDifficulty', 'mode'):
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, '其他模式不能套用常规难度修正'):
                self.calculate({'difficulty': {'value': 0, field: 'MONTH_TEAM'}})

    def test_unsupported_explicit_modes_are_rejected_before_enemy_scaling(self):
        for value in ('UNKNOWN', '', None, False, 0):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, '仅支持NORMAL模式'):
                calculate_damage({
                    'operator': 'mechanist', 'skill': 1,
                    'target_enemy': {'stage_id': 'ro6_n_1_2', 'enemy_id': 'enemy_1093_ccsbr', 'level': 0},
                    'run_config': {'difficulty': {'value': 0, 'modeDifficulty': value}},
                })

    def test_conflicting_mode_fields_do_not_silently_choose_normal(self):
        for fields in (
            {'modeDifficulty': 'NORMAL', 'mode': 'MONTH_TEAM'},
            {'modeDifficulty': 'MONTH_TEAM', 'mode': 'NORMAL'},
        ):
            with self.subTest(fields=fields), self.assertRaisesRegex(ValueError, '仅支持NORMAL模式'):
                self.calculate({'difficulty': {'value': 0, **fields}})

    def test_explicit_normal_mode_preserves_known_low_grade_enemy_values(self):
        for fields in ({}, {'modeDifficulty': 'NORMAL'}, {'mode': 'NORMAL'},
                       {'modeDifficulty': 'NORMAL', 'mode': 'NORMAL'}):
            with self.subTest(fields=fields):
                result = calculate_damage({
                    'operator': 'mechanist', 'skill': 1,
                    'target_enemy': {'stage_id': 'ro6_n_1_2', 'enemy_id': 'enemy_1093_ccsbr', 'level': 0},
                    'run_config': {'difficulty': {'value': 0, **fields}},
                })
                enemy = result['run_resolution']['enemy']
                self.assertEqual(result['run_resolution']['difficulty']['mode'], 'NORMAL')
                self.assertEqual(enemy['stats']['maxHp'], 1560)
                self.assertEqual(enemy['stats']['atk'], 203)
                self.assertEqual(enemy['stats']['def'], 60)


if __name__ == '__main__':
    unittest.main()
