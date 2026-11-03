"""Unconfirmed recruitment identity cannot settle 同行者's recipient condition.

Pinned cargo_10 parameters and the public producer's two names are already
researched. These tests do not establish native attachment or lifecycle.
"""
import copy
import unittest

from rouge.damage import calculate_damage
from rouge.relics import context_value, mechanics


RID = 'rogue_6_relic_cargo_10'
BASE = {'operator': 'silverash', 'skill': 3, 'base_attack': 1000,
        'enemy_defense': 0, 'window_seconds': 3, 'relic_ids': [RID]}
UNKNOWN_VALUES = ('unknown', 'emergency', '', 'EMERGENCY_HIRE',
                  ' emergency_hire ', False, True, 0, 1, 0.0, 1.0,
                  [], ['emergency_hire'], {}, {'kind': 'emergency_hire'})


def record(result):
    return next(row for row in result['relic_resolution']['records']
                if row['id'] == RID)


class EmergencyRecruitmentConditionTests(unittest.TestCase):
    def test_unrecognized_names_preserve_unknown_and_all_three_missing_effects(self):
        for mode in ('frames', 'continuous'):
            args = {**BASE, 'timing_mode': mode}
            pending = calculate_damage({**args, 'recruitment_kind': None})
            for kind in ('unknown', 'emergency', '', 'EMERGENCY_HIRE', ' emergency_hire '):
                with self.subTest(mode=mode, kind=kind):
                    actual = calculate_damage({**args, 'recruitment_kind': kind})
                    self.assertEqual(actual, pending)
                    row = record(actual)
                    self.assertEqual(row['missing_conditions'], ['emergency_hire'])
                    self.assertEqual(row['applied'], [])
                    self.assertEqual(row['status'], 'incomplete')
                    self.assertFalse(actual['relic_resolution']['complete'])
                    self.assertFalse(actual['complete'])
                    self.assertTrue(any('emergency_hire' in warning
                                        for warning in actual['warnings']))

    def test_exact_confirmed_names_keep_pinned_positive_and_confirmed_zero(self):
        for mode in ('frames', 'continuous'):
            args = {**BASE, 'timing_mode': mode}
            for kind, factor in (('non_emergency', 0), ('emergency_hire', 1)):
                with self.subTest(mode=mode, kind=kind):
                    result = calculate_damage({**args, 'recruitment_kind': kind})
                    row = record(result)
                    self.assertEqual(row['missing_conditions'], [])
                    self.assertEqual(row['status'], 'applied')
                    self.assertEqual([(effect['kind'], effect['value'])
                                      for effect in row['applied']],
                                     [('attack_pct', .4 * factor),
                                      ('hp_pct', .4 * factor),
                                      ('defense_pct', .4 * factor)])
                    self.assertEqual(result['estimate']['base_stats']['attack'],
                                     1000 if not factor else 1400)
                    self.assertTrue(result['relic_resolution']['complete'])
                    self.assertFalse(any('emergency_hire' in warning
                                         for warning in result['warnings']))

    def test_absent_and_none_remain_the_same_pending_result(self):
        for mode in ('frames', 'continuous'):
            args = {**BASE, 'timing_mode': mode}
            self.assertEqual(calculate_damage(args),
                             calculate_damage({**args, 'recruitment_kind': None}))

    def test_wrong_json_types_remain_pending_without_new_input_errors(self):
        for mode in ('frames', 'continuous'):
            args = {**BASE, 'timing_mode': mode}
            pending = calculate_damage({**args, 'recruitment_kind': None})
            for kind in UNKNOWN_VALUES[5:]:
                with self.subTest(mode=mode, kind=kind):
                    self.assertEqual(calculate_damage({**args, 'recruitment_kind': kind}), pending)

    def test_no_applicable_emergency_effect_preserves_complete_public_output(self):
        for mode in ('frames', 'continuous'):
            for relic_ids, context in (([], {}),
                    (['rogue_6_relic_cargo_2'], {'parts_count': 0}),
                    (['rogue_6_relic_legacy_60'], {'gold': 25})):
                args = {**BASE, 'timing_mode': mode, 'relic_ids': relic_ids,
                        'relic_context': context}
                ordinary = calculate_damage(args)
                for kind in UNKNOWN_VALUES:
                    with self.subTest(mode=mode, relic_ids=relic_ids, kind=kind):
                        self.assertEqual(calculate_damage({**args, 'recruitment_kind': kind}), ordinary)

    def test_context_flags_and_zero_observation_cannot_confirm_source(self):
        for mode in ('frames', 'continuous'):
            for context_flag in (0, 1):
                args = {**BASE, 'timing_mode': mode, 'window_seconds': 0,
                        'relic_context': {'emergency_hire': context_flag}}
                pending = calculate_damage({**args, 'recruitment_kind': None})
                actual = calculate_damage({**args, 'recruitment_kind': 'unknown'})
                self.assertEqual(actual, pending)
                self.assertEqual(actual['total_damage'], 0)
                self.assertEqual(record(actual)['missing_conditions'], ['emergency_hire'])
                self.assertFalse(actual['relic_resolution']['complete'])

    def test_only_builtin_strings_can_establish_identity_without_custom_equality(self):
        class StringLike(str):
            def __eq__(self, other):
                raise AssertionError('untrusted equality must not run')

        class OtherLike:
            def __eq__(self, other):
                raise AssertionError('untrusted equality must not run')

        effect = {'condition': 'emergency_hire'}
        for value in (StringLike('emergency_hire'), OtherLike()):
            with self.subTest(value_type=type(value).__name__):
                self.assertIsNone(context_value(effect, {'recruitment_kind': value}))

    def test_caller_and_shared_mechanics_are_unchanged(self):
        original_mechanics = copy.deepcopy(mechanics())
        for value in (None, 'non_emergency', 'emergency_hire', *UNKNOWN_VALUES):
            args = {**BASE, 'recruitment_kind': copy.deepcopy(value),
                    'relic_context': {'emergency_hire': 1}}
            original = copy.deepcopy(args)
            calculate_damage(args)
            self.assertEqual(args, original)
        self.assertEqual(mechanics(), original_mechanics)


if __name__ == '__main__':
    unittest.main()
