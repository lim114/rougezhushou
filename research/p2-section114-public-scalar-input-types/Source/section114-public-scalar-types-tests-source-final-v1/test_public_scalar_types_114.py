"""Public numeric inputs preserve consumer qualification and caller types.

Frozen against Root actual original133 observations:99 returns and34 errors.
The 50 numeric controls below retain those observed values and unknowns.
The Source author has not imported this module or executed its tests.
"""
from copy import deepcopy
import re
import struct
import unittest

from rouge.damage import calculate_damage
from rouge.estimate import format_estimate
from rouge.reporting import format_report


COMMON_FIELDS = ('base_attack', 'enemy_defense', 'enemy_resistance', 'window_seconds')
ROUTES = (('mechanist', 3, 90), ('char_002_amiya', 1, 80))
TARGET = {'stage_id': 'ro6_n_1_2', 'enemy_id': 'enemy_1093_ccsbr', 'level': 0}


# Actual Root JSON projection, not a native type/alias proof. Root retains the
# original native snapshots for the full paired Saved audit. No tolerance is
# widened and existing unknowns remain None.
ORIGINAL_PROJECTION_FIELDS = ('attack', 'total_damage', 'component_hits',
                              'window_seconds', 'initial_seconds', 'recharge_seconds',
                              'duration_seconds', 'phase_damage', 'cycle_damage')
ORIGINAL_VALID_SCALARS = {
    'legacy-base_attack-numeric_zero': (0.0, 0.0, (1, 0), 3.0, 10.0, 35.0, 40.0, 0.0, 0.0),
    'legacy-base_attack-numeric_fraction': (9.5, 17.29, (1, 0), 3.0, 10.0, 35.0, 40.0, 207.48, 210.98),
    'legacy-base_attack-zero_text': (0.0, 0.0, (1, 0), 3.0, 10.0, 35.0, 40.0, 0.0, 0.0),
    'legacy-base_attack-fraction_text': (9.5, 17.29, (1, 0), 3.0, 10.0, 35.0, 40.0, 207.48, 210.98),
    'legacy-enemy_defense-numeric_zero': (3800.0, 6916.0, (1, 0), 3.0, 10.0, 35.0, 40.0, 82992.0, 110992.0),
    'legacy-enemy_defense-numeric_fraction': (3800.0, 6916.0, (1, 0), 3.0, 10.0, 35.0, 40.0, 82992.0, 110922.0),
    'legacy-enemy_defense-zero_text': (3800.0, 6916.0, (1, 0), 3.0, 10.0, 35.0, 40.0, 82992.0, 110992.0),
    'legacy-enemy_defense-fraction_text': (3800.0, 6916.0, (1, 0), 3.0, 10.0, 35.0, 40.0, 82992.0, 110922.0),
    'legacy-enemy_resistance-numeric_zero': (3800.0, 9880.0, (1, 0), 3.0, 10.0, 35.0, 40.0, 118560.0, 143760.0),
    'legacy-enemy_resistance-numeric_fraction': (3800.0, 9633.0, (1, 0), 3.0, 10.0, 35.0, 40.0, 115596.0, 140796.0),
    'legacy-enemy_resistance-zero_text': (3800.0, 9880.0, (1, 0), 3.0, 10.0, 35.0, 40.0, 118560.0, 143760.0),
    'legacy-enemy_resistance-fraction_text': (3800.0, 9633.0, (1, 0), 3.0, 10.0, 35.0, 40.0, 115596.0, 140796.0),
    'legacy-window_seconds-numeric_zero': (3800.0, 0.0, (0, 0), 0.0, 10.0, 35.0, 40.0, 82992.0, 108192.0),
    'legacy-window_seconds-numeric_fraction': (3800.0, 6916.0, (1, 0), 2.5, 10.0, 35.0, 40.0, 82992.0, 108192.0),
    'legacy-window_seconds-zero_text': (3800.0, 0.0, (0, 0), 0.0, 10.0, 35.0, 40.0, 82992.0, 108192.0),
    'legacy-window_seconds-fraction_text': (3800.0, 6916.0, (1, 0), 2.5, 10.0, 35.0, 40.0, 82992.0, 108192.0),
    'generic-base_attack-numeric_zero': (0.0, 0.0, (4,), 3.0, 6.433333333333334, 12.833333333333334, 30.0, 0.0, 0.0),
    'generic-base_attack-numeric_fraction': (2.5, 7.0, (4,), 3.0, 6.433333333333334, 12.833333333333334, 30.0, 63.0, 78.75),
    'generic-base_attack-zero_text': (0.0, 0.0, (4,), 3.0, 6.433333333333334, 12.833333333333334, 30.0, 0.0, 0.0),
    'generic-base_attack-fraction_text': (2.5, 7.0, (4,), 3.0, 6.433333333333334, 12.833333333333334, 30.0, 63.0, 78.75),
    'generic-enemy_defense-numeric_zero': (1000.0, 2800.0, (4,), 3.0, 6.433333333333334, 12.833333333333334, 30.0, 25200.0, 31500.0),
    'generic-enemy_defense-numeric_fraction': (1000.0, 2800.0, (4,), 3.0, 6.433333333333334, 12.833333333333334, 30.0, 25200.0, 31500.0),
    'generic-enemy_defense-zero_text': (1000.0, 2800.0, (4,), 3.0, 6.433333333333334, 12.833333333333334, 30.0, 25200.0, 31500.0),
    'generic-enemy_defense-fraction_text': (1000.0, 2800.0, (4,), 3.0, 6.433333333333334, 12.833333333333334, 30.0, 25200.0, 31500.0),
    'generic-enemy_resistance-numeric_zero': (1000.0, 4000.0, (4,), 3.0, 6.433333333333334, 12.833333333333334, 30.0, 36000.0, 45000.0),
    'generic-enemy_resistance-numeric_fraction': (1000.0, 3900.0, (4,), 3.0, 6.433333333333334, 12.833333333333334, 30.0, 35100.0, 43875.0),
    'generic-enemy_resistance-zero_text': (1000.0, 4000.0, (4,), 3.0, 6.433333333333334, 12.833333333333334, 30.0, 36000.0, 45000.0),
    'generic-enemy_resistance-fraction_text': (1000.0, 3900.0, (4,), 3.0, 6.433333333333334, 12.833333333333334, 30.0, 35100.0, 43875.0),
    'generic-window_seconds-numeric_zero': (1000.0, 0.0, (0,), 0.0, 6.433333333333334, 12.833333333333334, 30.0, 25200.0, 31500.0),
    'generic-window_seconds-numeric_fraction': (1000.0, 2100.0, (3,), 2.5, 6.433333333333334, 12.833333333333334, 30.0, 25200.0, 31500.0),
    'generic-window_seconds-zero_text': (1000.0, 0.0, (0,), 0.0, 6.433333333333334, 12.833333333333334, 30.0, 25200.0, 31500.0),
    'generic-window_seconds-fraction_text': (1000.0, 2100.0, (3,), 2.5, 6.433333333333334, 12.833333333333334, 30.0, 25200.0, 31500.0),
    'legacy-active-companion-numeric_zero': (1000.0, 3700.0, (1, 1), 0, 4.0, 17.0, 0.0, 3700.0, 17200.0),
    'legacy-active-companion-numeric_fraction': (1000.0, 3700.475, (1, 1), 0, 4.0, 17.0, 0.0, 3700.0, 17200.0),
    'legacy-active-companion-zero_text': (1000.0, 3700.0, (1, 1), 0, 4.0, 17.0, 0.0, 3700.0, 17200.0),
    'legacy-active-companion-fraction_text': (1000.0, 3700.475, (1, 1), 0, 4.0, 17.0, 0.0, 3700.0, 17200.0),
    'generic-consumed-ratio-numeric_zero': (2050.0, 2870.0, (2, 0.0), 3.0, None, None, None, None, None),
    'generic-consumed-ratio-zero_text': (2050.0, 2870.0, (2, 0.0), 3.0, None, None, None, None, None),
    'legacy_active_elapsed-zero': (1000.0, 3700.0, (1,), 0, 4.0, 17.0, 0.0, 3700.0, 17200.0),
    'legacy_active_elapsed-fraction': (1000.0, 3700.0, (1,), 0, 4.0, 17.0, 0.0, 3700.0, 17200.0),
    'legacy_active_elapsed-text_zero': (1000.0, 3700.0, (1,), 0, 4.0, 17.0, 0.0, 3700.0, 17200.0),
    'legacy_active_elapsed-text_fraction': (1000.0, 3700.0, (1,), 0, 4.0, 17.0, 0.0, 3700.0, 17200.0),
    'legacy_inactive_elapsed-zero': (3800.0, 6916.0, (1, 0), 3.0, 10.0, 35.0, 40.0, 82992.0, 108192.0),
    'legacy_inactive_elapsed-fraction': (3800.0, 6916.0, (1, 0), 3.0, 10.0, 35.0, 40.0, 82992.0, 108192.0),
    'legacy_inactive_elapsed-text_zero': (3800.0, 6916.0, (1, 0), 3.0, 10.0, 35.0, 40.0, 82992.0, 108192.0),
    'legacy_inactive_elapsed-text_fraction': (3800.0, 6916.0, (1, 0), 3.0, 10.0, 35.0, 40.0, 82992.0, 108192.0),
    'generic_active_elapsed-zero': (2200.0, 11088.0, (3, 4.0, 4.0, 4.0), 3.0, 5.0, 28.0, 22.0, 122645.6, 153935.6),
    'generic_active_elapsed-fraction': (2200.0, 11088.0, (3, 4.0, 4.0, 4.0), 3.0, 5.0, 28.0, 22.0, 124000.80000000002, 155290.80000000002),
    'generic_active_elapsed-text_zero': (2200.0, 11088.0, (3, 4.0, 4.0, 4.0), 3.0, 5.0, 28.0, 22.0, 122645.6, 153935.6),
    'generic_active_elapsed-text_fraction': (2200.0, 11088.0, (3, 4.0, 4.0, 4.0), 3.0, 5.0, 28.0, 22.0, 124000.80000000002, 155290.80000000002),
}


def scenario(operator='mechanist', skill=3, level=90, **extra):
    return {'operator': operator, 'skill': skill, 'elite': 2, 'level': level,
            'skill_rank': 10, 'trust': 100, 'potential': 1,
            'base_attack': 1000, 'enemy_defense': 100, 'enemy_resistance': 30,
            'window_seconds': 3, 'relic_ids': [], 'effects': [],
            'timing_mode': 'frames', 'timing': {'windup_frames': 0, 'recovery_frames': 0},
            **extra}


def typed(value):
    """Compare complete values without treating bool, int and float as equal."""
    if isinstance(value, dict):
        return ('dict', tuple((typed(k), typed(v)) for k, v in value.items()))
    if isinstance(value, list):
        return ('list', tuple(typed(v) for v in value))
    if isinstance(value, tuple):
        return ('tuple', tuple(typed(v) for v in value))
    if type(value) is float:
        return ('float', struct.pack('>d', value))
    return (type(value).__name__, value)


class PublicScalarTypes114Tests(unittest.TestCase):
    def evaluate(self, caller):
        before = typed(caller)
        result = calculate_damage(caller)
        self.assertEqual(typed(caller), before)
        result_before = typed(result)
        texts = (format_estimate(result), format_report(result),
                 format_report(result, technical=True))
        self.assertEqual(typed(result), result_before)
        self.assertEqual(typed(caller), before)
        self.assertEqual(texts[0], texts[1])
        return result, texts

    def reject(self, caller, field, *, generic=False):
        before = typed(caller)
        message = (field + '需要范围内的有限非负数。' if generic else
                   field + ' 不接受布尔值；请使用数值。')
        with self.assertRaisesRegex(ValueError, '^' + re.escape(message) + '$'):
            calculate_damage(caller)
        self.assertEqual(typed(caller), before)

    def same_public_output(self, first, second):
        self.assertEqual(typed(self.evaluate(first)), typed(self.evaluate(second)))

    def original_scalar_projection(self, caller, case_id):
        result, texts = self.evaluate(caller)
        skill = result['estimate']['skill']
        projection = (result['attack'], result['total_damage'],
                      tuple(c['hits'] for c in result['components']),
                      skill['window_seconds'], skill['initial_seconds'],
                      skill['recharge_seconds'], skill['duration_seconds'],
                      skill['phase_damage'], skill['cycle_damage'])
        self.assertEqual(typed(projection), typed(ORIGINAL_VALID_SCALARS[case_id]))
        return result, texts

    def error_outcome(self, caller):
        before = typed(caller)
        try:
            calculate_damage(caller)
        except Exception as error:
            self.assertEqual(typed(caller), before)
            return type(error), str(error)
        self.fail('This fixture must reach its separately invalid original input.')

    def test_common_numeric_bools_are_rejected_in_both_engines(self):
        for operator, skill, level in ROUTES:
            for field in COMMON_FIELDS:
                for value in (False, True):
                    with self.subTest(operator=operator, field=field, value=value):
                        self.reject(scenario(operator, skill, level, **{field: value}), field)

    def test_common_field_order_is_stable_when_multiple_bools_are_present(self):
        for operator, skill, level in ROUTES:
            for offset, field in enumerate(COMMON_FIELDS):
                caller = scenario(operator, skill, level,
                                  **{name: False for name in COMMON_FIELDS[offset:]})
                with self.subTest(operator=operator, first_field=field):
                    self.reject(caller, field)

    def test_empty_observation_or_enemy_does_not_hide_a_common_bool(self):
        for operator, skill, level in ROUTES:
            for empty in ({'window_seconds': 0},
                          {'timing': {'target_disappears_seconds': 0}},
                          {'timing': {'target_windows': []}}):
                for field in ('base_attack', 'enemy_defense', 'enemy_resistance'):
                    with self.subTest(operator=operator, field=field, empty=empty):
                        self.reject(scenario(operator, skill, level,
                                             **empty, **{field: False}), field)

    def test_common_numeric_values_and_original_range_errors_remain_unchanged(self):
        forms = ((0, 'numeric_zero'), (2.5, 'numeric_fraction'),
                 ('0', 'zero_text'), ('2.5', 'fraction_text'))
        for route, (operator, skill, level) in zip(('legacy', 'generic'), ROUTES):
            for field in COMMON_FIELDS:
                for value, suffix in forms:
                    with self.subTest(operator=operator, field=field, value=value):
                        self.original_scalar_projection(scenario(operator, skill, level, **{field: value}),
                                                        route + '-' + field + '-' + suffix)
            errors = (('base_attack', -1,
                       'base_attack 需要有限非负数；法抗范围为 0–100。' if route == 'legacy' else
                       '基础攻击需要范围内的有限非负数。'),
                      ('enemy_resistance', 101,
                       'enemy_resistance 需要有限非负数；法抗范围为 0–100。' if route == 'legacy' else
                       'enemy_resistance需要范围内的有限非负数。'),
                      ('window_seconds', 'NaN',
                       'window_seconds 需要有限非负数；法抗范围为 0–100。' if route == 'legacy' else
                       'window_seconds需要范围内的有限非负数。'))
            for field, value, message in errors:
                with self.subTest(operator=operator, invalid_field=field):
                    self.assertEqual(self.error_outcome(scenario(operator, skill, level, **{field: value})),
                                     (ValueError, message))

    def test_selected_enemy_overrides_old_boolean_defense_and_resistance(self):
        for operator, skill, level in ROUTES:
            for value in (False, True):
                caller = scenario(operator, skill, level, target_enemy=deepcopy(TARGET),
                                  enemy_defense=value, enemy_resistance=value)
                control = scenario(operator, skill, level, target_enemy=deepcopy(TARGET),
                                   enemy_defense=int(value), enemy_resistance=int(value))
                with self.subTest(operator=operator, value=value):
                    self.same_public_output(caller, control)

    def test_enemy_override_does_not_hide_boolean_attack_or_observation(self):
        for operator, skill, level in ROUTES:
            for field in ('base_attack', 'window_seconds'):
                caller = scenario(operator, skill, level, target_enemy=deepcopy(TARGET),
                                  enemy_defense=False, enemy_resistance=True, **{field: False})
                with self.subTest(operator=operator, field=field):
                    self.reject(caller, field)

    def test_defense_relic_cannot_wash_a_boolean_into_a_numeric_value(self):
        for operator, skill, level in ROUTES:
            for value in (False, True):
                with self.subTest(operator=operator, value=value):
                    self.reject(scenario(operator, skill, level, enemy_defense=value,
                                         relic_ids=['rogue_6_relic_legacy_84']), 'enemy_defense')

    def test_attack_rune_retains_its_original_native_error_priority(self):
        for operator, skill, level in ROUTES:
            for value in (False, True):
                caller = scenario(operator, skill, level, base_attack=value,
                                  relic_ids=['rogue_6_relic_legacy_24'])
                with self.subTest(operator=operator, value=value):
                    self.assertEqual(self.error_outcome(caller),
                                     (ValueError, '费用计算参数需要有限数值。'))

    def test_earlier_training_target_and_relic_errors_keep_priority(self):
        invalid = (({'elite': False}, '精英阶段需要为 0、1 或 2。'),
                   ({'target_enemy': {'stage_id': 'missing', 'enemy_id': 'missing', 'level': 0}},
                    '目标关卡没有固定敌人档案。'),
                   ({'char_buff_ids': True}, '干员定向强化需要已确认的ID列表。'))
        for operator, skill, level in ROUTES:
            for extra, message in invalid:
                caller = scenario(operator, skill, level, base_attack=True, **deepcopy(extra))
                control = scenario(operator, skill, level, base_attack=1000, **deepcopy(extra))
                with self.subTest(operator=operator, invalid=extra):
                    self.assertEqual(self.error_outcome(caller), (ValueError, message))
                    self.assertEqual(self.error_outcome(control), (ValueError, message))

    def test_consumed_companion_rejects_bool_and_preserves_numeric_output(self):
        for value in (False, True):
            with self.subTest(value=value):
                self.reject(scenario('silverash', 2, 90, deployment_stacks=1,
                                     companion_attack=value), 'companion_attack')
        for value, suffix in ((0, 'numeric_zero'), (2.5, 'numeric_fraction'),
                              ('0', 'zero_text'), ('2.5', 'fraction_text')):
            with self.subTest(value=value):
                self.original_scalar_projection(scenario('silverash', 2, 90, deployment_stacks=1,
                                                         companion_attack=value),
                                                'legacy-active-companion-' + suffix)

    def test_inactive_companion_preserves_boolean_numeric_compatibility(self):
        routes = ROUTES
        for operator, skill, level in routes:
            for value in (False, True):
                with self.subTest(operator=operator, value=value):
                    self.same_public_output(
                        scenario(operator, skill, level, deployment_stacks=0, companion_attack=value),
                        scenario(operator, skill, level, deployment_stacks=0, companion_attack=int(value)))

    def test_consumed_generic_hp_ratio_rejects_bool_and_keeps_numeric_bounds(self):
        for value in (False, True):
            self.reject(scenario('char_1044_hsgma2', 1, 90, current_hp_ratio=value),
                        'current_hp_ratio', generic=True)
        for value, suffix in ((0, 'numeric_zero'), ('0', 'zero_text')):
            self.original_scalar_projection(scenario('char_1044_hsgma2', 1, 90, current_hp_ratio=value),
                                            'generic-consumed-ratio-' + suffix)
        for value in (2.5, '2.5'):
            self.assertEqual(self.error_outcome(
                scenario('char_1044_hsgma2', 1, 90, current_hp_ratio=value)),
                (ValueError, 'current_hp_ratio需要范围内的有限非负数。'))

    def test_legacy_sp_scalar_bools_do_not_become_extra_points_or_rates(self):
        for field in ('initial_sp_bonus', 'sp_recovery_bonus'):
            for value in (False, True):
                with self.subTest(field=field, value=value):
                    self.reject(scenario(**{field: value}), field)

    def test_inactive_healing_bool_retains_the_original_numeric_compatibility(self):
        for operator, skill, level in ROUTES:
            for value in (False, True):
                with self.subTest(operator=operator, value=value):
                    self.same_public_output(scenario(operator, skill, level, healing_targets=value),
                                            scenario(operator, skill, level, healing_targets=int(value)))

    def test_selected_silverash_talent_and_drone_elapsed_reject_bools(self):
        for operator, skill, generic in (('silverash', 2, False), ('char_1038_whitw2', 2, True)):
            for value in (False, True):
                with self.subTest(operator=operator, value=value):
                    self.reject(scenario(operator, skill, 90, deployment_elapsed_seconds=value),
                                'deployment_elapsed_seconds', generic=generic)

    def test_unused_elapsed_bool_preserves_the_original_numeric_compatibility(self):
        for operator, skill, level in ROUTES:
            for value in (False, True):
                with self.subTest(operator=operator, value=value):
                    self.same_public_output(
                        scenario(operator, skill, level, deployment_elapsed_seconds=value),
                        scenario(operator, skill, level, deployment_elapsed_seconds=int(value)))

    def test_active_and_inactive_elapsed_keep_original_numeric_values_and_unknowns(self):
        routes = (('mechanist', 3, 90, 'legacy_inactive_elapsed'),
                  ('silverash', 2, 90, 'legacy_active_elapsed'),
                  ('char_1038_whitw2', 2, 90, 'generic_active_elapsed'))
        for operator, skill, level, prefix in routes:
            for value, suffix in ((0, 'zero'), (2.5, 'fraction'),
                                  ('0', 'text_zero'), ('2.5', 'text_fraction')):
                with self.subTest(operator=operator, value=value):
                    self.original_scalar_projection(
                        scenario(operator, skill, level, deployment_elapsed_seconds=value),
                        prefix + '-' + suffix)

    def test_none_preserves_existing_parser_errors_and_generic_unused_exception(self):
        for operator, skill, level in ROUTES:
            for field in COMMON_FIELDS:
                with self.subTest(operator=operator, field=field):
                    self.assertEqual(self.error_outcome(scenario(operator, skill, level, **{field: None})),
                                     (TypeError, "float() argument must be a string or a real number, not 'NoneType'"))
        for field in ('companion_attack', 'deployment_elapsed_seconds',
                      'initial_sp_bonus', 'sp_recovery_bonus'):
            with self.subTest(legacy_field=field):
                self.assertEqual(self.error_outcome(scenario(**{field: None})),
                                 (TypeError, "float() argument must be a string or a real number, not 'NoneType'"))
        for operator, skill, field in (('silverash', 2, 'companion_attack'),
                                       ('silverash', 2, 'deployment_elapsed_seconds'),
                                       ('char_1038_whitw2', 2, 'deployment_elapsed_seconds'),
                                       ('char_1044_hsgma2', 1, 'current_hp_ratio')):
            with self.subTest(operator=operator, null_field=field):
                extra = {'deployment_stacks': 1} if field == 'companion_attack' else {}
                self.assertEqual(self.error_outcome(scenario(operator, skill, 90, **extra, **{field: None})),
                                 (TypeError, "float() argument must be a string or a real number, not 'NoneType'"))
        self.same_public_output(scenario('char_002_amiya', 1, 80, companion_attack=None),
                                scenario('char_002_amiya', 1, 80))


if __name__ == '__main__':
    unittest.main()
