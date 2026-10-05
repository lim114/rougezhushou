"""Public calculations for bounded, source-backed 0.25 collectible rules."""
import copy
import math
import unittest
from unittest.mock import patch

from rouge.catalog import stage_previews
from rouge.damage import calculate_damage
from rouge.reporting import format_report


FIRE = 'rogue_6_relic_cargo_11'
COOKIE = 'rogue_6_relic_assign_15'
COOKIE_BUFF = 'rogue_6_from_relic_15'
GRAVITY = 'rogue_6_relic_legacy_56'
TARGET = {'stage_id': 'ro6_n_1_2', 'enemy_id': 'enemy_2137_shsdgo', 'level': 0}


class RelicCandidates025Tests(unittest.TestCase):
    def test_fire_rod_never_guesses_stacks_from_floor_or_victories(self):
        result = calculate_damage({'operator': 'mechanist', 'skill': 3,
            'relic_ids': [FIRE], 'run_config': {'zone': {'id': 'zone_3'}},
            'relic_context': {'battle_wins': 8}, 'target_enemy': TARGET})
        record = result['relic_resolution']['records'][0]
        self.assertEqual(result['estimate']['base_stats']['attack_speed'], 100)
        self.assertIn('fire_rod_stacks', record['missing_conditions'])
        self.assertFalse(result['relic_resolution']['complete'])
        self.assertEqual(result['run_resolution']['enemy']['stats']['maxHp'], 18000)

    def test_fire_rod_zero_and_confirmed_counts_are_additive_and_bounded(self):
        base = {'operator': 'mechanist', 'skill': 3, 'relic_ids': [FIRE]}
        for count, speed, reference in ((0, 100, 100), (3, 130, 130),
                (50, 600, 600), (99, 600, 1090), (100, 600, 1090)):
            with self.subTest(count=count):
                result = calculate_damage({**base, 'relic_context': {'fire_rod_stacks': count}})
                stats = result['estimate']['base_stats']
                self.assertEqual(stats['attack_speed'], speed)
                self.assertEqual(stats['attack_speed_reference'], reference)
                self.assertNotIn('fire_rod_stacks',result['relic_resolution']['records'][0]['missing_conditions'])
                # HP requires a selected stage enemy, independently of AS.
                self.assertIn('target_enemy',result['relic_resolution']['records'][0]['missing_conditions'])
        capped = [calculate_damage({**base, 'relic_context': {'fire_rod_stacks': n}})
                  for n in (50, 99)]
        self.assertEqual(capped[0]['total_damage'], capped[1]['total_damage'])
        self.assertEqual(capped[0]['estimate']['skill']['cycle_seconds'],
                         capped[1]['estimate']['skill']['cycle_seconds'])

    def test_fire_rod_requires_an_explicit_finite_integer_count(self):
        for value in (True, -1, .5, math.inf, math.nan, '3'):
            with self.subTest(value=value), self.assertRaises(ValueError):
                calculate_damage({'operator': 'mechanist', 'skill': 3, 'relic_ids': [FIRE],
                    'relic_context': {'fire_rod_stacks': value}})

    def test_fire_rod_eight_profession_selector_excludes_ordinary_tokens(self):
        args = {'operator': 'char_110_deepcl', 'skill': 1}
        plain = calculate_damage(args)
        result = calculate_damage({**args, 'relic_ids': [FIRE],
            'relic_context': {'fire_rod_stacks': 3}})
        self.assertEqual(result['estimate']['base_stats']['attack_speed'], 130)
        self.assertFalse(result['relic_resolution']['token_effects'])
        tokens = lambda r: [c for c in r['components'] if c.get('source_unit') == 'token']
        self.assertEqual(tokens(result), tokens(plain))

    def test_reports_keep_attribute_as_separate_from_timing_cap_in_both_engines(self):
        for op in ('mechanist', 'kaltsit', 'char_151_myrtle'):
            with self.subTest(operator=op):
                result = calculate_damage({'operator': op, 'skill': 1, 'relic_ids': [FIRE],
                    'relic_context': {'fire_rod_stacks': 99}})
                self.assertEqual(result['estimate']['base_stats']['attack_speed_reference'], 1090)
                text = format_report(result)
                self.assertIn('攻速：1,090', text)
                self.assertIn('攻击间隔', text)
                self.assertIn('600', text)
        result = calculate_damage({'operator': 'kaltsit', 'skill': 1, 'relic_ids': [FIRE],
            'relic_context': {'fire_rod_stacks': 99}})
        self.assertEqual(result['estimate']['skill']['skill_attack_speed_reference'], 1140)

    def test_cookie_possession_does_not_assign_recipients(self):
        args = {'operator': 'char_151_myrtle', 'skill': 1}
        plain = calculate_damage(args)
        held = calculate_damage({**args, 'relic_ids': [COOKIE]})
        for key in ('initial_seconds', 'recharge_seconds', 'cycle_seconds', 'cycle_dps'):
            self.assertEqual(held['estimate']['skill'][key], plain['estimate']['skill'][key])
        self.assertFalse(held['relic_resolution']['complete'])
        self.assertFalse(held['relic_resolution']['records'][0]['applied'])

    def test_cookie_binding_gives_point_eight_natural_sp_once(self):
        args = {'operator': 'char_151_myrtle', 'skill': 1}
        for ids in ([COOKIE_BUFF], [COOKIE_BUFF, COOKIE_BUFF]):
            result = calculate_damage({**args, 'char_buff_ids': ids})
            skill = result['estimate']['skill']
            self.assertAlmostEqual(skill['sp_recovery_per_second'], 1.8)
            self.assertEqual(skill['initial_seconds'], 5)
            self.assertAlmostEqual(skill['recharge_seconds'], 367 / 30)
            self.assertEqual(len(result['relic_resolution']['records']), 1)
            self.assertTrue(result['relic_resolution']['complete'])

    def test_cookie_does_not_change_attack_or_damage_recovery(self):
        for op, skill in (('mechanist', 1), ('char_1044_hsgma2', 1)):
            with self.subTest(operator=op):
                args = {'operator': op, 'skill': skill, 'incoming_attack_interval': 2}
                plain = calculate_damage(args)
                result = calculate_damage({**args, 'char_buff_ids': [COOKIE_BUFF]})
                self.assertEqual(result['estimate']['skill'], plain['estimate']['skill'])
                self.assertEqual(result['total_damage'], plain['total_damage'])
                self.assertFalse(result['relic_resolution']['records'][0]['applied'])
                self.assertIn(COOKIE_BUFF, result['relic_resolution']['inapplicable'])

    def test_cookie_uses_existing_sp_lockout_timeline_and_not_token_binding(self):
        for op in ('kaltsit', 'char_110_deepcl'):
            with self.subTest(operator=op):
                args = {'operator': op, 'skill': 1,
                        'timing': {'sp_lockout_extra_seconds': 2}}
                bound = calculate_damage({**args, 'char_buff_ids': [COOKIE_BUFF]})
                reference = calculate_damage({**args, 'effects': [{'kind': 'sp_recovery', 'value': .8}]})
                self.assertEqual(bound['estimate']['skill'], reference['estimate']['skill'])
                self.assertFalse(bound['relic_resolution']['token_effects'])
                unlocked = calculate_damage({**args, 'timing': {'sp_lockout_extra_seconds': 0},
                                             'char_buff_ids': [COOKIE_BUFF]})
                self.assertAlmostEqual(bound['estimate']['skill']['cycle_seconds'],
                                       unlocked['estimate']['skill']['cycle_seconds'] + 2)
                self.assertEqual(bound['estimate']['skill']['duration_seconds'],
                                 unlocked['estimate']['skill']['duration_seconds'])

    def test_cookie_natural_sp_adds_to_other_explicit_recovery_modifiers(self):
        args = {'operator': 'char_151_myrtle', 'skill': 1}
        result = calculate_damage({**args, 'char_buff_ids': [COOKIE_BUFF],
            'effects': [{'kind': 'sp_recovery', 'value': .5}]})
        reference = calculate_damage({**args, 'effects': [{'kind': 'sp_recovery', 'value': 1.3}]})
        self.assertAlmostEqual(result['estimate']['skill']['sp_recovery_per_second'], 2.3)
        self.assertEqual(result['estimate']['skill'], reference['estimate']['skill'])

    def test_gravity_changes_only_verified_weight_and_allows_negative_values(self):
        for enemy_id, initial, expected in (('enemy_2137_shsdgo', 3, 1), ('enemy_1093_ccsbr', 1, -1)):
            with self.subTest(enemy=enemy_id):
                args = {'operator': 'mechanist', 'skill': 3,
                        'target_enemy': {**TARGET, 'enemy_id': enemy_id}}
                plain = calculate_damage(args)
                result = calculate_damage({**args, 'relic_ids': [GRAVITY, GRAVITY]})
                enemy = result['run_resolution']['enemy']
                self.assertEqual(enemy['reference_stats']['massLevel'], initial)
                self.assertEqual(enemy['stats']['massLevel'], expected)
                expected_stats = {**plain['run_resolution']['enemy']['stats'], 'massLevel': expected}
                self.assertEqual(enemy['stats'], expected_stats)
                self.assertEqual(result['total_damage'], plain['total_damage'])
                self.assertEqual(result['estimate']['skill'], plain['estimate']['skill'])
                self.assertTrue(result['relic_resolution']['complete'])
                self.assertEqual(enemy['steps'][-1]['deltas'], {'massLevel': -2})
                text = format_report(result)
                self.assertIn('预计重量', text)
                self.assertIn('不据此计算位移', text)

    def test_gravity_zero_weight_is_known_and_becomes_minus_two(self):
        target = {'stage_id': 'ro6_n_1_1', 'enemy_id': 'enemy_2133_shdopl', 'level': 0}
        result = calculate_damage({'operator': 'mechanist', 'skill': 3,
            'target_enemy': target, 'enemy_weight': 999, 'relic_ids': [GRAVITY]})
        enemy = result['run_resolution']['enemy']
        self.assertEqual(enemy['reference_stats']['massLevel'], 0)
        self.assertEqual(enemy['stats']['massLevel'], -2)
        self.assertTrue(result['relic_resolution']['complete'])

    def test_gravity_retains_unknown_weight_instead_of_defaulting_to_zero(self):
        preview = copy.deepcopy(stage_previews()['ro6_n_1_2'])
        next(e for e in preview['possible_enemies'] if e['id'] == TARGET['enemy_id'])['reference_stats']['massLevel'] = None
        with patch('rouge.enemy_environment.stage_previews', return_value={'ro6_n_1_2': preview}):
            result = calculate_damage({'operator': 'mechanist', 'skill': 3,
                'target_enemy': TARGET, 'relic_ids': [GRAVITY]})
        record = result['relic_resolution']['records'][0]
        self.assertIn('enemy_weight', record['missing_conditions'])
        self.assertFalse(record['applied'])
        self.assertIsNone(result['run_resolution']['enemy']['stats']['massLevel'])
        self.assertFalse(result['relic_resolution']['complete'])

    def test_gravity_without_target_requires_identity_and_ignores_manual_weight(self):
        result = calculate_damage({'operator': 'mechanist', 'skill': 3,
            'enemy_weight': 3, 'relic_ids': [GRAVITY]})
        self.assertIn('target_enemy', result['relic_resolution']['records'][0]['missing_conditions'])
        self.assertFalse(result['relic_resolution']['records'][0]['applied'])
        self.assertNotIn('enemy_environment', [s['id'] for s in result['report']['sections']])


if __name__ == '__main__':
    unittest.main()
