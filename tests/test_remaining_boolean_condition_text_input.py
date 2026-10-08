import copy
import unittest

from rouge.catalog import catalog
from rouge.damage import calculate_damage


ACTIVE = (
    ('char_4228_closur', 2, 'reinforcement_blocks_target'),
    ('char_437_mizuki', 2, 'enemy_below_half'),
    ('char_206_gnosis', 3, 'frozen_at_skill_end'),
    ('char_4087_ines', 3, 'ines_first_deployment'),
    ('char_4182_oblvns', 2, 'ranged_attack'),
    ('char_4182_oblvns', 2, 'organ_mode'),
    ('char_4182_oblvns', 2, 'fever'),
    ('char_1048_orchd2', 1, 'power_coating'),
    ('char_1048_orchd2', 1, 'double_charge'),
    ('char_1041_angel2', 2, 'steal_success'),
    ('char_1041_angel2', 3, 'delivery_coordinate'),
    ('char_1035_wisdel', 2, 'overload'),
)


def typed(value):
    if isinstance(value, dict):
        return ('dict', tuple((typed(k), typed(v)) for k, v in value.items()))
    if isinstance(value, (list, tuple)):
        return (type(value).__name__, tuple(typed(v) for v in value))
    return (type(value).__name__, value)


def scenario(operator, skill, **extra):
    return {'operator': operator, 'skill': skill, 'base_attack': 1020,
            'potential': 5, 'timing_mode': 'continuous', 'window_seconds': 7, **extra}


class RemainingBooleanConditionTextInputTests(unittest.TestCase):
    def test_each_active_control_preserves_distinct_bools_and_rejects_text(self):
        for operator, skill, field in ACTIVE:
            with self.subTest(field=field):
                false = calculate_damage(scenario(operator, skill, **{field: False}))
                true = calculate_damage(scenario(operator, skill, **{field: True}))
                self.assertNotEqual(typed(false), typed(true))
                with self.assertRaisesRegex(ValueError, field + ' 不接受文本条件；请使用布尔值。'):
                    calculate_damage(scenario(operator, skill, **{field: 'false'}))

    def test_empty_and_numeric_text_are_rejected_without_parsing(self):
        for operator, skill, field in ACTIVE:
            for text in ('', '0'):
                with self.subTest(field=field, text=text), self.assertRaisesRegex(ValueError, field):
                    calculate_damage(scenario(operator, skill, **{field: text}))

    def test_other_owners_keep_ignored_fields(self):
        expected = typed(calculate_damage(scenario('mechanist', 1)))
        for _, _, field in ACTIVE:
            with self.subTest(field=field):
                self.assertEqual(typed(calculate_damage(scenario('mechanist', 1, **{field: 'false'}))), expected)

    def test_same_owner_inactive_skills_and_unselected_talent_remain_ignored(self):
        inactive = (
            ('char_206_gnosis', 1, 'frozen_at_skill_end', {}),
            ('char_4087_ines', 2, 'ines_first_deployment', {}),
            ('char_4182_oblvns', 1, 'organ_mode', {}),
            ('char_4182_oblvns', 3, 'fever', {}),
            ('char_1048_orchd2', 2, 'double_charge', {}),
            ('char_1041_angel2', 1, 'steal_success', {}),
            ('char_1041_angel2', 2, 'delivery_coordinate', {}),
            ('char_1035_wisdel', 1, 'overload', {}),
            ('char_437_mizuki', 1, 'enemy_below_half', {'elite': 0, 'skill_rank': 7}),
            ('char_437_mizuki', 2, 'enemy_below_half', {'elite': 1, 'skill_rank': 7}),
        )
        for operator, skill, field, extra in inactive:
            expected = calculate_damage(scenario(operator, skill, **extra))
            actual = calculate_damage(scenario(operator, skill, **extra, **{field: 'false'}))
            with self.subTest(field=field, skill=skill, elite=extra.get('elite', 2)):
                self.assertEqual(typed(actual), typed(expected))

    def test_ranged_module_override_uses_actual_normal_plan_eligibility(self):
        common = {'elite': 2, 'level': 60, 'module_id': 'uniequip_002_oblvns',
                  'module_level': 2, 'timing_mode': 'frames'}
        for skill, continuous in ((1, False), (1, True), (2, True), (3, False)):
            with self.subTest(skill=skill, continuous=continuous):
                plain = calculate_damage(scenario('char_4182_oblvns', skill, **common,
                                                  continuous_attacks=continuous, ranged_attack=False))
                injected = calculate_damage(scenario('char_4182_oblvns', skill, **common,
                                                     continuous_attacks=continuous, ranged_attack='false',
                                                     _oblvns_ranged_attack_consumed=True))
                self.assertEqual(typed(plain), typed(injected))
        for skill in (3,):
            with self.subTest(skill=skill), self.assertRaisesRegex(ValueError, 'ranged_attack'):
                calculate_damage(scenario('char_4182_oblvns', skill, **common,
                                          continuous_attacks=True, ranged_attack='false',
                                          _oblvns_ranged_attack_consumed=False))
        with self.assertRaisesRegex(ValueError, 'ranged_attack'):
            calculate_damage(scenario('char_4182_oblvns', 2, **{**common, 'module_level': 1},
                                      ranged_attack='false', continuous_attacks=False))

    def test_existing_numeric_training_timing_and_prior_text_errors_win(self):
        cases = (
            (scenario('char_1048_orchd2', 3, power_coating='false', dragon_arrow_hits=False), 'dragon_arrow_hits'),
            (scenario('char_1035_wisdel', 2, overload='false', ghost_count=False), 'ghost_count'),
            (scenario('char_206_gnosis', 3, frozen_at_skill_end='false', cold_state=False), 'cold_state'),
            (scenario('char_4087_ines', 3, ines_first_deployment='false', stolen_enemy_count=False), 'stolen_enemy_count'),
            (scenario('char_4228_closur', 2, reinforcement_blocks_target='false', potential=True), '潜能'),
            (scenario('char_4182_oblvns', 2, organ_mode='false', timing={'windup_frames': float('nan')}), 'windup_frames'),
            (scenario('char_1048_orchd2', 1, double_charge='false', near_previous_deployment='false'), 'near_previous_deployment'),
        )
        for value, message in cases:
            with self.subTest(message=message), self.assertRaisesRegex(ValueError, message):
                calculate_damage(value)

    def test_nonstring_truthiness_stays_supported(self):
        for operator, skill, field in ACTIVE:
            for value, boolean in ((0, False), (1, True), (None, False)):
                with self.subTest(field=field, value=value):
                    actual = calculate_damage(scenario(operator, skill, **{field: value}))
                    expected = calculate_damage(scenario(operator, skill, **{field: boolean}))
                    self.assertEqual(typed(actual), typed(expected))

    def test_rejection_and_acceptance_leave_caller_and_catalog_unchanged(self):
        old_catalog = typed(catalog())
        for operator, skill, field, extra, rejects in (
                ('char_437_mizuki', 2, 'enemy_below_half', {}, True),
                ('char_437_mizuki', 1, 'enemy_below_half', {'elite': 0, 'skill_rank': 7}, False)):
            value = scenario(operator, skill, **extra, **{field: 'false'},
                             timing={'target_windows': [[0, 5]]},
                             effects=[{'kind': 'attack_pct', 'value': .2}])
            before = typed(copy.deepcopy(value))
            if rejects:
                with self.assertRaisesRegex(ValueError, field):calculate_damage(value)
            else:calculate_damage(value)
            self.assertEqual(typed(value), before)
            self.assertEqual(typed(catalog()), old_catalog)


if __name__ == '__main__':unittest.main()
