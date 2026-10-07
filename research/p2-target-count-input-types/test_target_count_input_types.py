import copy
import json
import re
import unittest

from rouge.catalog import catalog
from rouge.damage import calculate_damage
from rouge.reporting import has_healing


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


class TargetCountInputTypesTests(unittest.TestCase):
    errors = {
        'healing_targets': '治疗目标数需要为 0–100 的整数。',
        'amiya_hit_targets': 'amiya_hit_targets需要1到100之间的整数。',
        'stolen_enemy_count': 'stolen_enemy_count需要范围内的有限非负整数。',
    }
    active_healers = tuple((operator, number) for operator, profile in catalog()['operators'].items()
                          for number in range(1, len(profile['skills']) + 1)
                          if has_healing(operator, number))

    def evaluate(self, operator, skill, mode='frames', **extra):
        return calculate_damage({'operator': operator, 'skill': skill, 'base_attack': 1000,
                                 'window_seconds': 10, 'timing_mode': mode, **extra})

    def assert_rejected(self, operator, skill, field, value, mode='frames', **extra):
        scenario = {'operator': operator, 'skill': skill, 'base_attack': 1000,
                    'window_seconds': 10, 'timing_mode': mode, field: value, **extra}
        before = canonical(scenario)
        with self.assertRaisesRegex(ValueError, '^' + re.escape(self.errors[field]) + '$'):
            calculate_damage(scenario)
        self.assertEqual(canonical(scenario), before)

    def test_visible_healing_counts_reject_bools_in_both_engines_and_modes(self):
        self.assertIn(('kaltsit', 1), self.active_healers)
        self.assertIn(('char_151_myrtle', 2), self.active_healers)
        for operator, skill in self.active_healers:
            for mode in ('frames', 'continuous'):
                for value in (False, True):
                    with self.subTest(operator=operator, skill=skill, mode=mode, value=value):
                        self.assert_rejected(operator, skill, 'healing_targets', value, mode)

    def test_medical_amiya_opening_count_rejects_both_bools(self):
        for mode in ('frames', 'continuous'):
            for value in (False, True):
                with self.subTest(mode=mode, value=value):
                    self.assert_rejected('char_1037_amiya3', 2, 'amiya_hit_targets', value, mode)

    def test_ines_stolen_enemy_count_rejects_bools_for_all_skills(self):
        for skill in (1, 2, 3):
            for mode in ('frames', 'continuous'):
                for value in (False, True):
                    with self.subTest(skill=skill, mode=mode, value=value):
                        self.assert_rejected('char_4087_ines', skill, 'stolen_enemy_count', value, mode)

    def test_zero_counts_keep_their_existing_distinct_meanings(self):
        for mode in ('frames', 'continuous'):
            no_healing = self.evaluate('char_151_myrtle', 2, mode, healing_targets=0)
            self.assertEqual(no_healing['total_healing'], 0)
            one_healing = self.evaluate('char_151_myrtle', 2, mode, healing_targets=1)
            for key in ('initial_seconds', 'recharge_seconds', 'cycle_seconds'):
                self.assertEqual(no_healing['estimate']['skill'][key], one_healing['estimate']['skill'][key])
            no_steal = self.evaluate('char_4087_ines', 2, mode, stolen_enemy_count=0)
            one_steal = self.evaluate('char_4087_ines', 2, mode, stolen_enemy_count=1)
            self.assertEqual(no_steal['attack'], 2100)
            self.assertEqual(one_steal['attack'], 2190)
            self.assert_rejected('char_1037_amiya3', 2, 'amiya_hit_targets', 0, mode)

    def test_convertible_numeric_types_defaults_and_boundaries_are_preserved(self):
        cases = (('kaltsit', 2, 'healing_targets', (0, 1, 100)),
                 ('char_151_myrtle', 2, 'healing_targets', (0, 1, 100)),
                 ('char_4202_haruka', 2, 'healing_targets', (0, 1, 100)),
                 ('char_1037_amiya3', 2, 'amiya_hit_targets', (1, 5, 100)),
                 ('char_4087_ines', 2, 'stolen_enemy_count', (0, 1, 100)))
        for operator, skill, field, values in cases:
            for mode in ('frames', 'continuous'):
                self.assertEqual(canonical(self.evaluate(operator, skill, mode)),
                                 canonical(self.evaluate(operator, skill, mode, **{field: 1})))
                for value in values:
                    expected = canonical(self.evaluate(operator, skill, mode, **{field: value}))
                    for converted in (float(value), str(value)):
                        with self.subTest(operator=operator, field=field, mode=mode, value=converted):
                            self.assertEqual(canonical(self.evaluate(operator, skill, mode, **{field: converted})), expected)

    def test_inactive_target_fields_keep_existing_boolean_compatibility(self):
        cases = (('mechanist', 1, 'healing_targets'),
                 ('silverash', 3, 'healing_targets'),
                 ('char_151_myrtle', 1, 'healing_targets'),
                 ('char_1044_hsgma2', 1, 'healing_targets'),
                 ('char_1037_amiya3', 1, 'amiya_hit_targets'),
                 ('char_151_myrtle', 2, 'amiya_hit_targets'),
                 ('char_151_myrtle', 2, 'stolen_enemy_count'))
        for operator, skill, field in cases:
            for mode in ('frames', 'continuous'):
                for value in (False, True):
                    with self.subTest(operator=operator, skill=skill, field=field, mode=mode, value=value):
                        self.assertEqual(canonical(self.evaluate(operator, skill, mode, **{field: value})),
                                         canonical(self.evaluate(operator, skill, mode, **{field: int(value)})))

    def test_true_boolean_controls_remain_supported(self):
        cases = (('char_298_susuro', 2, 'low_cost_healing_target'),
                 ('char_4202_haruka', 2, 'haruka_repeat'),
                 ('char_206_gnosis', 3, 'frozen_at_skill_end'),
                 ('char_4087_ines', 3, 'ines_first_deployment'))
        for operator, skill, field in cases:
            for mode in ('frames', 'continuous'):
                for value in (False, True):
                    with self.subTest(operator=operator, field=field, mode=mode, value=value):
                        result = self.evaluate(operator, skill, mode, **{field: value})
                        self.assertEqual(result['report']['operator']['id'], operator)

    def test_other_integer_options_are_outside_this_target_count_change(self):
        cases = (('char_110_deepcl', 1, 'summon_count'),
                 ('char_206_gnosis', 2, 'cold_state'),
                 ('char_4202_haruka', 1, 'bubble_bursts'),
                 ('char_1035_wisdel', 1, 'ghost_casts'),
                 ('mechanist', 3, 'charge_count'),
                 ('silverash', 2, 'activation_count'))
        for operator, skill, field in cases:
            for mode in ('frames', 'continuous'):
                for value in (False, True):
                    with self.subTest(operator=operator, field=field, mode=mode, value=value):
                        actual = self.evaluate(operator, skill, mode, **{field: value})
                        expected = self.evaluate(operator, skill, mode, **{field: int(value)})
                        # Some existing report rows retain the raw parameter type.
                        self.assertEqual(canonical({key: val for key, val in actual.items() if key != 'report'}),
                                         canonical({key: val for key, val in expected.items() if key != 'report'}))

    def test_empty_observation_does_not_bypass_raw_count_validation(self):
        cases = (('kaltsit', 2, 'healing_targets'),
                 ('char_4202_haruka', 2, 'healing_targets'),
                 ('char_1037_amiya3', 2, 'amiya_hit_targets'),
                 ('char_4087_ines', 3, 'stolen_enemy_count'))
        for operator, skill, field in cases:
            for mode in ('frames', 'continuous'):
                for value in (False, True):
                    for extra in ({'window_seconds': 0}, {'timing': {'target_disappears_seconds': 0}}):
                        with self.subTest(operator=operator, field=field, mode=mode, value=value, extra=extra):
                            self.assert_rejected(operator, skill, field, value, mode, **extra)

    def test_existing_non_boolean_range_rejections_are_preserved(self):
        cases = (('kaltsit', 1, 'healing_targets'),
                 ('char_151_myrtle', 2, 'healing_targets'),
                 ('char_1037_amiya3', 2, 'amiya_hit_targets'),
                 ('char_4087_ines', 2, 'stolen_enemy_count'))
        for operator, skill, field in cases:
            for value in (-1, .5, 101, float('nan'), float('inf')):
                with self.subTest(operator=operator, field=field, value=value), self.assertRaises(ValueError):
                    self.evaluate(operator, skill, **{field: value})

    def test_catalog_and_nested_input_are_isolated_on_rejection(self):
        before_catalog = canonical(catalog())
        scenario = {'operator': 'char_4202_haruka', 'skill': 2,
                    'healing_targets': False, 'timing': {'target_windows': [[0, 5]]},
                    'effects': [{'kind': 'attack_pct', 'value': .2}]}
        before = copy.deepcopy(scenario)
        with self.assertRaisesRegex(ValueError, re.escape(self.errors['healing_targets'])):
            calculate_damage(scenario)
        self.assertEqual(canonical(scenario), canonical(before))
        self.assertEqual(canonical(catalog()), before_catalog)


if __name__ == '__main__':
    unittest.main()
