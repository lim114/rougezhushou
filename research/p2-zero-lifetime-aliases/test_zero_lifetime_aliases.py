import copy
import json
import unittest

from rouge.catalog import catalog
from rouge.damage import calculate_damage


ALIASES = ('0', '0.0', '-0')


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def evaluate(operator, skill, mode='frames', lifetime=0, **extra):
    return calculate_damage({'operator': operator, 'skill': skill, 'base_attack': 1000,
        'enemy_defense': 0, 'enemy_resistance': 0, 'timing_mode': mode,
        'timing': {'target_disappears_seconds': lifetime}, **extra})


class ZeroLifetimeAliasesTests(unittest.TestCase):
    def test_all_supported_skills_match_existing_numeric_zero_in_both_modes(self):
        for operator, profile in catalog()['operators'].items():
            for skill in range(1, len(profile['skills']) + 1):
                for mode in ('frames', 'continuous'):
                    numeric = canonical(evaluate(operator, skill, mode))
                    for alias in ALIASES:
                        with self.subTest(operator=operator, skill=skill, mode=mode, lifetime=alias):
                            self.assertEqual(canonical(evaluate(operator, skill, mode, alias)), numeric)

    def test_amiya_natural_recharge_and_independent_initial_clock_are_preserved(self):
        for alias in ALIASES:
            result = evaluate('char_002_amiya', 1, 'continuous', alias)
            skill = result['estimate']['skill']
            self.assertEqual(result['total_damage'], 0)
            self.assertEqual(skill['recharge_seconds'], 30)
            self.assertEqual(skill['cycle_seconds'], 60)
            self.assertEqual(skill['initial_seconds'], 7)

    def test_independent_friendly_healing_is_not_cancelled_by_zero_alias(self):
        for operator, skill in (('kaltsit', 1), ('kaltsit', 3), ('char_298_susuro', 1),
                                ('char_2025_shu', 2), ('char_4202_haruka', 1)):
            for mode in ('frames', 'continuous'):
                numeric = evaluate(operator, skill, mode)
                self.assertGreater(numeric['total_healing'], 0)
                for alias in ALIASES:
                    with self.subTest(operator=operator, skill=skill, mode=mode, lifetime=alias):
                        result = evaluate(operator, skill, mode, alias)
                        self.assertEqual(result['total_healing'], numeric['total_healing'])
                        self.assertEqual(result['total_damage'], 0)

    def test_medical_attack_dependent_healing_has_no_enemy_source(self):
        for skill in (1, 2):
            for mode in ('frames', 'continuous'):
                for alias in ALIASES:
                    with self.subTest(skill=skill, mode=mode, lifetime=alias):
                        result = evaluate('char_1037_amiya3', skill, mode, alias)
                        self.assertEqual(result['total_damage'], 0)
                        self.assertEqual(result['total_healing'], 0)

    def test_medical_ammo_keeps_friendly_fallback_and_zero_recipient_boundary(self):
        for mode in ('frames', 'continuous'):
            for alias in ALIASES:
                positive = evaluate('kaltsit', 2, mode, alias, healing_targets=1)
                self.assertEqual(positive['total_damage'], 0)
                self.assertEqual(positive['estimate']['skill']['total_healing'], 50000)
                no_friend = evaluate('kaltsit', 2, mode, alias, healing_targets=0)
                self.assertEqual(no_friend['total_damage'], 0)
                self.assertEqual(no_friend['estimate']['skill']['total_healing'], 0)
                self.assertIsNone(no_friend['estimate']['skill']['duration_seconds'])

    def test_independent_declared_collision_and_counter_references_survive(self):
        for mode in ('frames', 'continuous'):
            for alias in ALIASES:
                charge = evaluate('mechanist', 3, mode, alias, charge_count=2)
                self.assertEqual(charge['total_damage'], 0)
                self.assertEqual(charge['charge_reference']['declared_count_damage'], 22800)
                counter = evaluate('char_1044_hsgma2', 1, mode, alias, incoming_hits=2)
                self.assertEqual(counter['total_damage'], 0)
                source = next(c for c in counter['components'] if c['name'] == '恶业苦果反击')
                self.assertEqual(source['conditional_hits_reference'], 2)
                self.assertEqual(source['conditional_damage_reference'], 5950)

    def test_other_accepted_zero_string_spellings_use_the_same_boundary(self):
        numeric = canonical(evaluate('kaltsit', 2))
        for alias in (' 0 ', '+0', '-0.0', '0e+10'):
            with self.subTest(lifetime=alias):
                self.assertEqual(canonical(evaluate('kaltsit', 2, lifetime=alias)), numeric)

    def test_raw_boolean_invalid_and_nonfinite_lifetimes_are_still_rejected(self):
        for mode in ('frames', 'continuous'):
            for value in (False, True, None, -1, float('nan'), float('inf'), '-1', 'nan', 'inf', 'unknown'):
                with self.subTest(mode=mode, value=value), self.assertRaisesRegex(ValueError, 'target_disappears_seconds'):
                    evaluate('kaltsit', 2, mode, value)

    def test_full_raw_timing_validation_is_not_bypassed_by_zero_alias(self):
        for mode in ('frames', 'continuous'):
            for invalid in ({'windup_frames': True}, {'target_windows': [[0, 0]]},
                            {'interrupt_windows': [[2, 1]]}, {'movement_windows': 'unknown'}):
                for lifetime in (0, '0'):
                    timing = {'target_disappears_seconds': lifetime, **invalid}
                    with self.subTest(mode=mode, lifetime=lifetime, invalid=invalid), self.assertRaises(ValueError):
                        evaluate('kaltsit', 2, mode, timing=timing)

    def test_caller_nested_timing_and_catalog_remain_isolated(self):
        before_catalog = canonical(catalog())
        for mode in ('frames', 'continuous'):
            scenario = {'operator': 'char_4202_haruka', 'skill': 1, 'base_attack': 1000,
                'timing_mode': mode, 'timing': {'target_disappears_seconds': '-0',
                    'target_windows': [[0, 10]], 'movement_windows': [[2, 3]],
                    'units': {'token_10001_deepcl_tentac': {'target_disappears_seconds': '2.5'}}}}
            before = copy.deepcopy(scenario)
            timing_identity = id(scenario['timing'])
            units_identity = id(scenario['timing']['units'])
            calculate_damage(scenario)
            self.assertEqual(canonical(scenario), canonical(before))
            self.assertEqual(id(scenario['timing']), timing_identity)
            self.assertEqual(id(scenario['timing']['units']), units_identity)
        self.assertEqual(canonical(catalog()), before_catalog)


if __name__ == '__main__':
    unittest.main()
