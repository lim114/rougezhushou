"""Public numeric inputs preserve consumer qualification and caller types.

This external Source draft has not been imported or executed. Root must bind
the actual original observations before applying it to the project.
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

    def test_common_numeric_zero_fraction_and_numeric_text_remain_accepted(self):
        for operator, skill, level in ROUTES:
            for field in COMMON_FIELDS:
                for value in (0, 2.5, '0', '2.5'):
                    with self.subTest(operator=operator, field=field, value=value):
                        self.evaluate(scenario(operator, skill, level, **{field: value}))

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
        invalid = ({'elite': False},
                   {'target_enemy': {'stage_id': 'missing', 'enemy_id': 'missing', 'level': 0}},
                   {'char_buff_ids': True})
        for operator, skill, level in ROUTES:
            for extra in invalid:
                caller = scenario(operator, skill, level, base_attack=True, **deepcopy(extra))
                control = scenario(operator, skill, level, base_attack=1000, **deepcopy(extra))
                with self.subTest(operator=operator, invalid=extra):
                    self.assertEqual(self.error_outcome(caller), self.error_outcome(control))

    def test_companion_bool_is_rejected_when_deployment_trigger_consumes_it(self):
        for value in (False, True):
            with self.subTest(value=value):
                self.reject(scenario('silverash', 2, 90, deployment_stacks=1,
                                     companion_attack=value), 'companion_attack')

    def test_inactive_companion_preserves_boolean_numeric_compatibility(self):
        routes = (*ROUTES, ('silverash', 2, 90))
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
        for value in (0, '0'):
            self.evaluate(scenario('char_1044_hsgma2', 1, 90, current_hp_ratio=value))
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

    def test_active_and_inactive_elapsed_keep_zero_fraction_and_numeric_text(self):
        routes = (*ROUTES, ('silverash', 2, 90), ('char_1038_whitw2', 2, 90))
        for operator, skill, level in routes:
            for value in (0, 2.5, '0', '2.5'):
                with self.subTest(operator=operator, value=value):
                    self.evaluate(scenario(operator, skill, level, deployment_elapsed_seconds=value))

    def test_none_preserves_existing_parser_errors_and_generic_unused_exception(self):
        for operator, skill, level in ROUTES:
            for field in COMMON_FIELDS:
                with self.subTest(operator=operator, field=field):
                    self.assertIs(self.error_outcome(
                        scenario(operator, skill, level, **{field: None}))[0], TypeError)
        for field in ('companion_attack', 'deployment_elapsed_seconds',
                      'initial_sp_bonus', 'sp_recovery_bonus'):
            with self.subTest(legacy_field=field):
                self.assertIs(self.error_outcome(scenario(**{field: None}))[0], TypeError)
        self.same_public_output(scenario('char_002_amiya', 1, 80, companion_attack=None),
                                scenario('char_002_amiya', 1, 80))


if __name__ == '__main__':
    unittest.main()
