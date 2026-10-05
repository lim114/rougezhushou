from tests.offline_scope_retirement import historical_combat_test
"""Independent source examples and public boundary checks for batch 0.27."""
import copy
import json
import math
import unittest
from pathlib import Path

from rouge.catalog import stage_previews
from rouge.damage import calculate_damage
from rouge.reporting import format_report
from rouge.relics import mechanics

FIRE = 'rogue_6_relic_cargo_11'
BIND = 'rogue_6_relic_fight_11'
EMPTY = 'rogue_6_relic_cargo_3'
ONE_COIN = 'rogue_6_relic_legacy_141'
PICTURE = 'rogue_6_relic_legacy_84'
STAGES = ('ro6_t_8', 'ro6_t_8_b', 'ro6_t_8_c', 'ro6_t_9', 'ro6_t_9_b',
          'ro6_t_9_c', 'ro6_t_10', 'ro6_t_11')


def target(stage):
    e = stage_previews()[stage]['possible_enemies'][0]
    return {'stage_id': stage, 'enemy_id': e['id'], 'level': e['level']}


def scenario(**extra):
    return {'operator': 'mechanist', 'skill': 3, **extra}


class DeploymentRelics027Tests(unittest.TestCase):
    def test_pinned_raw_selectors_amounts_and_resident_whitelist(self):
        raw = json.loads(Path('.cache/game-data/roguelike_topic_table.json').read_text(encoding='utf-8'))['details']['rogue_6']
        board = lambda b: {x['key']: x['valueStr'] if x.get('valueStr') is not None else x['value'] for x in b['blackboard']}
        bind = [board(b) for b in raw['relics'][BIND]['buffs']]
        self.assertEqual(bind[0]['cost'], -.5)
        self.assertEqual(bind[1]['hp_ratio'], .7)
        self.assertNotIn('token', bind[1]['selector.profession'].lower().split('|'))
        stages = next(board(b)['stage_ids'].split(',') for b in raw['relics'][FIRE]['buffs'] if b['key'] == 'layer_pass_stage')
        self.assertEqual(stages, list(STAGES))
        hp = next(e for e in mechanics()['relics'][FIRE]['effects'] if e['kind'] == 'enemy_hp_factor')
        self.assertEqual(hp['eligible_stage_ids'], list(STAGES))
        self.assertEqual(hp['value'], .6)

    @historical_combat_test
    def test_deployment_does_not_change_maximum_hp_skill_damage_or_recovery(self):
        base = calculate_damage(scenario())
        args = scenario(relic_ids=[BIND], relic_context={'deployment_hp_ratio': .65, 'deployment_loss_unused': 1})
        old = copy.deepcopy(args)
        result = calculate_damage(args)
        self.assertEqual(args, old)
        self.assertEqual(result['estimate']['base_stats'], base['estimate']['base_stats'])
        self.assertEqual(result['estimate']['skill'], base['estimate']['skill'])
        loss = result['deployment_reference']['hp_loss'][0]
        self.assertEqual(loss['max_hp_reference'], 3631)
        self.assertAlmostEqual(loss['hp_before_loss'], 2360.15)
        self.assertAlmostEqual(loss['lost_hp'], 1652.105)
        self.assertAlmostEqual(loss['hp_after_loss'], 708.045)
        self.assertFalse(loss['changes_max_hp'])
        self.assertFalse(loss['advances_lifecycle'])
        self.assertEqual(calculate_damage(args)['deployment_reference'], result['deployment_reference'])

    @historical_combat_test
    def test_already_consumed_deployment_and_new_deployment_are_distinct(self):
        args = scenario(relic_ids=[BIND], relic_context={'deployment_hp_ratio': .3, 'deployment_loss_unused': 0})
        used = calculate_damage(args)['deployment_reference']['hp_loss'][0]
        self.assertEqual(used['lost_hp'], 0)
        self.assertEqual(used['hp_before_loss'], used['hp_after_loss'])
        again = calculate_damage({**args, 'relic_context': {'deployment_hp_ratio': .3, 'deployment_loss_unused': 1}})
        self.assertAlmostEqual(again['deployment_reference']['hp_loss'][0]['hp_after_loss'], 326.79)

    @historical_combat_test
    def test_missing_current_hp_or_deployment_state_is_never_guessed(self):
        for context, missing in (({}, ['deployment_hp_ratio', 'deployment_loss_unused']),
                ({'deployment_hp_ratio': 1}, ['deployment_loss_unused']),
                ({'deployment_loss_unused': 0}, ['deployment_hp_ratio'])):
            with self.subTest(context=context):
                result = calculate_damage(scenario(relic_ids=[BIND], relic_context=context,
                    activation_count=1, deployment_stacks=2))
                loss = result['deployment_reference']['hp_loss'][0]
                if context.get('deployment_loss_unused') == 0:
                    self.assertEqual(loss['lost_hp'], 0)
                else:
                    self.assertIsNone(loss['lost_hp'])
                self.assertIsNone(loss['hp_after_loss'])
                self.assertEqual(loss['missing_conditions'], sorted(missing))
                self.assertFalse(result['relic_resolution']['complete'])
                self.assertIsNone(result['deployment_cost'])

    @historical_combat_test
    def test_zero_and_full_hp_are_valid_but_not_defaults(self):
        for ratio, before, after in ((0, 0, 0), (1, 3631, 1089.3)):
            result = calculate_damage(scenario(relic_ids=[BIND], relic_context={
                'deployment_hp_ratio': ratio, 'deployment_loss_unused': 1}))
            loss = result['deployment_reference']['hp_loss'][0]
            self.assertEqual(loss['hp_before_loss'], before)
            self.assertAlmostEqual(loss['hp_after_loss'], after)

    @historical_combat_test
    def test_loss_ratio_and_flag_are_strictly_validated(self):
        for name, values in (('deployment_hp_ratio', (True, -1, 1.1, math.inf, math.nan, '1')),
                             ('deployment_loss_unused', (True, -1, .5, 2, math.inf, '1'))):
            for value in values:
                with self.subTest(name=name, value=value), self.assertRaises(ValueError):
                    calculate_damage(scenario(relic_ids=[BIND], relic_context={name: value}))

    def test_unrelated_operators_have_no_loss_reference_or_validation(self):
        result = calculate_damage(scenario(relic_context={'deployment_hp_ratio': 'irrelevant'}))
        self.assertNotIn('deployment_reference', result)
        text = format_report(result)
        self.assertNotIn('他缚', text)
        self.assertNotIn('实际部署扣费', text)

    def test_ordinary_tokens_do_not_inherit_deployment_loss_or_discount(self):
        args = {'operator': 'char_110_deepcl', 'skill': 1}
        base = calculate_damage(args)
        result = calculate_damage({**args, 'relic_ids': [BIND], 'relic_context': {
            'deployment_hp_ratio': .65, 'deployment_loss_unused': 1}})
        tokens = lambda r: [c for c in r['components'] if c.get('source_unit') == 'token']
        self.assertEqual(tokens(result), tokens(base))
        self.assertFalse(result['relic_resolution']['token_effects'])
        self.assertFalse(result['relic_token_stats'])
        self.assertFalse([r for r in result['relic_resolution']['rules'] if r.get('token_only')])

    def test_cost_rune_additions_precede_relative_multiplier(self):
        result = calculate_damage(scenario(relic_ids=[BIND, ONE_COIN]))
        cost = result['deployment_reference']['cost']
        self.assertEqual(cost['cultivation_cost'], 23)
        self.assertEqual(cost['rune_addition'], -1)
        self.assertEqual(cost['rune_factor'], .5)
        self.assertEqual(cost['unrounded_rune_reference'], 11)
        self.assertEqual(cost['combined_reference'], 11)
        self.assertIsNone(cost['actual_cost'])
        self.assertTrue(cost['rounding_verified'])
        self.assertNotEqual(cost['unrounded_rune_reference'], 23 * .5 - 1)

    def test_native_half_even_cost_rounding_and_potential_precede_card_cost(self):
        one = calculate_damage(scenario(relic_ids=[BIND]))
        six = calculate_damage(scenario(relic_ids=[BIND], potential=6))
        self.assertEqual(one['deployment_reference']['cost']['unrounded_rune_reference'], 11.5)
        self.assertEqual(six['deployment_reference']['cost']['unrounded_rune_reference'], 10.5)
        # Native AttributesData int field writes round3.5/11.5 up to even,
        # while10.5 rounds down to10, before the card's separate floor stage.
        self.assertEqual(one['deployment_cost'],12)
        self.assertEqual(six['deployment_cost'],10)
        self.assertIsNone(one['deployment_reference']['cost']['actual_cost'])
        self.assertIsNone(six['deployment_reference']['cost']['actual_cost'])
        self.assertTrue(six['relic_resolution']['complete'])

    def test_proved_inventory_card_delta_keeps_missing_condition_unknown(self):
        for context, expected, missing in (({}, None, ['empty_slots']),
                ({'empty_slots': 4}, 6, []), ({'empty_slots': 3}, 12, [])):
            result = calculate_damage(scenario(relic_ids=[BIND, EMPTY], relic_context=context))
            cost = result['deployment_reference']['cost']
            self.assertEqual(cost['excluded_script_discounts'], [])
            self.assertEqual(cost['missing_conditions'], missing)
            self.assertEqual(cost['unrounded_rune_reference'], 11.5)
            # Native empty-bed card delta applies after round(23*.5)=12.
            self.assertEqual(cost['combined_reference'], expected)
            self.assertIsNone(cost['actual_cost'])

    def test_duplicate_ids_do_not_stack_or_deduct_again(self):
        args = scenario(relic_ids=[BIND], relic_context={'deployment_hp_ratio': .65, 'deployment_loss_unused': 1})
        once = calculate_damage(args)
        twice = calculate_damage({**args, 'relic_ids': [BIND, BIND]})
        self.assertEqual(twice['deployment_reference'], once['deployment_reference'])
        self.assertEqual(len(twice['relic_resolution']['records']), 1)

    @historical_combat_test
    def test_hp_reference_follows_cultivation_and_confirmed_max_hp_bonus(self):
        args = scenario(relic_ids=[BIND], relic_context={'deployment_hp_ratio': .5, 'deployment_loss_unused': 1})
        for extra in ({'level': 1}, {'potential': 6}, {'effects': [{'kind': 'hp_pct', 'value': .2}]}):
            result = calculate_damage({**args, **extra})
            stats = calculate_damage(scenario(**extra))['estimate']['base_stats']
            self.assertEqual(result['estimate']['base_stats'], stats)
            self.assertAlmostEqual(result['deployment_reference']['hp_loss'][0]['hp_after_loss'], stats['hp'] * .15)

    @historical_combat_test
    def test_damage_and_low_hp_buffs_are_not_inferred_from_deployment_loss(self):
        # Hot cocoa is conditional on the current skill scenario's HP, not
        # proof that a previously modelled deployment determines that HP.
        cocoa = 'rogue_6_relic_fight_14'
        result = calculate_damage(scenario(relic_ids=[BIND, cocoa],
            relic_context={'deployment_hp_ratio': 1, 'deployment_loss_unused': 1}))
        self.assertNotIn('current_hp_ratio', result['relic_resolution']['context'])
        record = next(r for r in result['relic_resolution']['records'] if r['id'] == cocoa)
        self.assertIn('current_hp_ratio', record['missing_conditions'])
        base = calculate_damage(scenario())
        self.assertEqual(result['estimate']['base_stats']['attack'], base['estimate']['base_stats']['attack'])
        confirmed = calculate_damage(scenario(relic_ids=[BIND, cocoa], relic_context={
            'deployment_hp_ratio': 1, 'deployment_loss_unused': 1, 'current_hp_ratio': .3}))
        self.assertGreater(confirmed['estimate']['base_stats']['attack'], base['estimate']['base_stats']['attack'])

    def test_all_eight_resident_stage_variants_apply_one_factor(self):
        for stage in STAGES:
            with self.subTest(stage=stage):
                args = scenario(target_enemy=target(stage), run_config={'difficulty': {'value': 0}})
                base = calculate_damage(args)
                result = calculate_damage({**args, 'relic_ids': [FIRE], 'relic_context': {'fire_rod_stacks': 0}})
                self.assertAlmostEqual(result['run_resolution']['enemy']['stats']['maxHp'],
                                       base['run_resolution']['enemy']['stats']['maxHp'] * .6)
                self.assertEqual(result['total_damage'], base['total_damage'])
                self.assertTrue(result['relic_resolution']['enemy_effects']['resident_hp_applied'])
                self.assertFalse(result['relic_resolution']['records'][0]['missing_conditions'])
                self.assertEqual(result['estimate']['base_stats']['attack_speed'], 100)

    def test_resident_stage_is_independent_of_attack_speed_stack_count(self):
        for count, speed in ((0, 100), (3, 130)):
            r = calculate_damage(scenario(target_enemy=target('ro6_t_8'), relic_ids=[FIRE],
                relic_context={'fire_rod_stacks': count}))
            self.assertEqual(r['run_resolution']['enemy']['stats']['maxHp'], 1500)
            self.assertEqual(r['estimate']['base_stats']['attack_speed'], speed)
        missing = calculate_damage(scenario(target_enemy=target('ro6_t_8'), relic_ids=[FIRE]))
        self.assertEqual(missing['run_resolution']['enemy']['stats']['maxHp'], 1500)
        self.assertIn('fire_rod_stacks', missing['relic_resolution']['records'][0]['missing_conditions'])

    def test_normal_stage_and_floor_hint_never_imply_resident_hp_loss(self):
        args = scenario(target_enemy=target('ro6_n_1_2'), run_config={'zone': {'id': 'zone_3'}})
        base = calculate_damage(args)
        result = calculate_damage({**args, 'relic_ids': [FIRE], 'relic_context': {'fire_rod_stacks': 3}})
        self.assertEqual(result['run_resolution']['enemy']['stats']['maxHp'], base['run_resolution']['enemy']['stats']['maxHp'])
        self.assertFalse(result['relic_resolution']['enemy_effects']['resident_hp_applied'])
        self.assertFalse(result['relic_resolution']['records'][0]['missing_conditions'])

    def test_manual_target_cannot_claim_the_resident_modifier(self):
        result = calculate_damage(scenario(relic_ids=[FIRE], enemy_defense=100,
            relic_context={'fire_rod_stacks': 3, 'resident_battle': 1},
            run_config={'zone': {'id': 'zone_3'}}))
        self.assertFalse(result['relic_resolution']['enemy_effects']['hp_factors'])
        self.assertIn('target_enemy', result['relic_resolution']['records'][0]['missing_conditions'])

    def test_verified_resident_and_other_final_hp_scalers_multiply(self):
        args = scenario(target_enemy=target('ro6_t_8'), relic_ids=[PICTURE])
        base = calculate_damage(args)
        result = calculate_damage({**args, 'relic_ids': [PICTURE, FIRE], 'relic_context': {'fire_rod_stacks': 3}})
        self.assertAlmostEqual(result['run_resolution']['enemy']['stats']['maxHp'],
                               base['run_resolution']['enemy']['stats']['maxHp']*.6)
        self.assertEqual(result['relic_resolution']['enemy_effects']['hp_composition_pending'], [])
        self.assertTrue(result['relic_resolution']['complete'])
        record = next(r for r in result['relic_resolution']['records'] if r['id'] == FIRE)
        self.assertFalse(record['pending'])
        self.assertTrue([e for e in record['applied'] if e['kind'] == 'enemy_hp_factor'])

    def test_identity_hp_modifier_does_not_block_independent_resident_reference(self):
        result = calculate_damage(scenario(target_enemy=target('ro6_t_8'), relic_ids=[FIRE, 'rogue_6_start_3'],
            relic_context={'fire_rod_stacks': 0, 'entered_zone_count': 3}))
        self.assertTrue(result['relic_resolution']['enemy_effects']['resident_hp_applied'])
        self.assertEqual(result['run_resolution']['enemy']['stats']['maxHp'], 1500)

    def test_missing_other_hp_condition_remains_unknown_without_discarding_proven_resident_factor(self):
        result = calculate_damage(scenario(target_enemy=target('ro6_t_8'), relic_ids=[FIRE, 'rogue_6_start_3'],
            relic_context={'fire_rod_stacks': 0}))
        effects = result['relic_resolution']['enemy_effects']
        self.assertEqual(effects['hp_composition_pending'], [])
        self.assertTrue(effects['resident_hp_applied'])
        self.assertEqual(result['run_resolution']['enemy']['stats']['maxHp'], 1500)
        self.assertFalse(result['relic_resolution']['complete'])
        dragon=next(r for r in result['relic_resolution']['records'] if r['id']=='rogue_6_start_3')
        self.assertIn('entered_zone_count',dragon['missing_conditions'])

    def test_unverified_defense_pair_keeps_hp_instances_but_does_not_claim_complete(self):
        result = calculate_damage(scenario(target_enemy=target('ro6_t_8'), relic_ids=[FIRE, PICTURE, 'rogue_6_relic_legacy_85'],
            relic_context={'fire_rod_stacks': 0}))
        effects = result['relic_resolution']['enemy_effects']
        self.assertEqual(sorted(effects['hp_factors']),[.6,.9,.95])
        self.assertEqual(effects['hp_composition_pending'], [])
        self.assertAlmostEqual(result['run_resolution']['enemy']['stats']['maxHp'],2500*.6*.95*.9)
        self.assertFalse(result['relic_resolution']['complete'])
        self.assertTrue(any('enemy_def_down' in x for x in result['warnings']))

    def test_higher_difficulty_is_resolved_before_resident_reference(self):
        args = scenario(target_enemy=target('ro6_t_8'), run_config={
            'difficulty': {'value': 15}, 'zone': {'id': 'zone_3'}})
        base = calculate_damage(args)
        result = calculate_damage({**args, 'relic_ids': [FIRE], 'relic_context': {'fire_rod_stacks': 0}})
        self.assertAlmostEqual(result['run_resolution']['enemy']['stats']['maxHp'],
                               base['run_resolution']['enemy']['stats']['maxHp'] * .6)

    @historical_combat_test
    def test_report_marks_fractional_cost_and_lifecycle_limits(self):
        result = calculate_damage(scenario(relic_ids=[BIND], relic_context={'deployment_hp_ratio': .65, 'deployment_loss_unused': 1}))
        text = format_report(result)
        self.assertIn('未取整符文费用参考：11.5', text)
        self.assertIn('实际部署扣费：未知', text)
        self.assertIn('重算不推进状态', text)
        self.assertIn('不改生命上限', text)
        self.assertIn('不将事件后的生命比例自动套给低血量增益', text)


if __name__ == '__main__':
    unittest.main()
