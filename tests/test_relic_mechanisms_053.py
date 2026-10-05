"""Public offline healing/deployment audit against pinned relic selectors.

No active run, game control, or guessed creation/tick rules are involved.
"""
import copy
import unittest

from rouge.damage import calculate_damage
from rouge.relics import mechanics


ROSE = 'rogue_6_relic_legacy_81'
CROWN = 'rogue_6_relic_legacy_82'
MEAL = 'rogue_6_relic_legacy_83'
MEAT = 'rogue_6_relic_legacy_22'
PERFUME = 'rogue_6_relic_legacy_91'
LIGHT = 'rogue_6_relic_book_3'
TIED = 'rogue_6_relic_fight_11'
BED = 'rogue_6_relic_cargo_3'


def scenario(operator='mechanist', skill=3, **values):
    return {'operator': operator, 'skill': skill, 'enemy_defense': 100,
            'timing': {'windup_frames': 6, 'recovery_frames': 9}, **values}


def section(result, identity):
    return next(row for row in result['report']['sections'] if row['id'] == identity)


class RelicMechanism053Tests(unittest.TestCase):
    def test_single_healing_multiplier_changes_no_damage_attributes_or_timing(self):
        for operator, number in (('kaltsit', 1), ('kaltsit', 2), ('kaltsit', 3),
                                 ('char_1037_amiya3', 1), ('char_1037_amiya3', 2),
                                 ('char_196_sunbr', 2), ('char_151_myrtle', 2)):
            for relic, factor in ((ROSE, 1.2), (CROWN, 1.3), (MEAL, 1.4)):
                with self.subTest(operator=operator, skill=number, relic=relic):
                    args = scenario(operator, number)
                    plain = calculate_damage(args)
                    actual = calculate_damage({**args, 'relic_ids': [relic]})
                    self.assertEqual(actual['estimate']['base_stats'], plain['estimate']['base_stats'])
                    self.assertEqual(actual['total_damage'], plain['total_damage'])
                    for key in ('duration_seconds', 'initial_seconds', 'recharge_seconds', 'cycle_seconds'):
                        self.assertEqual(actual['estimate']['skill'][key], plain['estimate']['skill'][key])
                    for key in ('total_healing', 'phase_healing', 'window_healing', 'cycle_healing', 'cycle_hps'):
                        before = plain['estimate']['skill'].get(key)
                        if before is not None:
                            self.assertAlmostEqual(actual['estimate']['skill'][key], before * factor)

    def test_healing_component_event_amounts_are_scaled_once(self):
        args = scenario('char_1037_amiya3', 1)
        plain = calculate_damage(args)
        actual = calculate_damage({**args, 'relic_ids': [ROSE, ROSE]})
        for before, after in zip(plain['components'], actual['components'], strict=True):
            factor = 1.2 if before['damage_type'] in ('healing', 'regeneration') else 1
            self.assertAlmostEqual(after['total'], before['total'] * factor)
            self.assertAlmostEqual(after['per_hit'], before['per_hit'] * factor)
            if before.get('event_amounts') is not None:
                self.assertEqual(after['event_amounts'], [value * factor for value in before['event_amounts']])
                self.assertAlmostEqual(sum(after['event_amounts']), after['total'])

    def test_two_raw_regeneration_channels_do_not_square_single_item_factor(self):
        args = scenario('char_110_deepcl', 1, relic_ids=[MEAT, PERFUME])
        plain = calculate_damage(args)
        actual = calculate_damage({**args, 'relic_ids': args['relic_ids'] + [ROSE]})
        self.assertEqual(len([rule for rule in mechanics()['relics'][ROSE]['effects']
                              if rule['kind'] == 'regeneration_factor']), 2)
        self.assertEqual(actual['relic_regeneration_multiplier'], 1.2)
        self.assertAlmostEqual(actual['relic_regeneration_rate'], plain['relic_regeneration_rate'] * 1.2)
        self.assertAlmostEqual(actual['relic_token_stats'][0]['regeneration_rate'],
                               plain['relic_token_stats'][0]['regeneration_rate'] * 1.2)
        self.assertEqual(actual['estimate']['skill']['total_healing'], 0)

    def test_multiple_healing_and_regeneration_items_keep_unknown_stacking(self):
        for items in ((ROSE, CROWN), (ROSE, MEAL), (CROWN, MEAL), (ROSE, CROWN, MEAL)):
            with self.subTest(items=items):
                args = scenario('char_1037_amiya3', 1)
                plain = calculate_damage(args)
                actual = calculate_damage({**args, 'relic_ids': list(items)})
                self.assertFalse(actual['relic_resolution']['complete'])
                self.assertEqual(actual['estimate']['skill']['total_healing'],
                                 plain['estimate']['skill']['total_healing'])
                self.assertFalse(any(rule['kind'] in ('healing_factor', 'regeneration_factor')
                                     for rule in actual['relic_resolution']['rules']))
                self.assertTrue(all(row['status'] == 'incomplete'
                                    for row in actual['relic_resolution']['records']))
                self.assertTrue(any('heal_scale' in text for text in actual['warnings']))
                self.assertTrue(any('received_regeneration' in text for text in actual['warnings']))

    def test_unknown_multipliers_preserve_fixed_and_ratio_single_source_references(self):
        args = scenario('char_110_deepcl', 1, relic_ids=[MEAT, PERFUME])
        plain = calculate_damage(args)
        actual = calculate_damage({**args, 'relic_ids': args['relic_ids'] + [ROSE, CROWN]})
        self.assertFalse(actual['relic_resolution']['complete'])
        self.assertEqual(actual['relic_regeneration_rate'], plain['relic_regeneration_rate'])
        self.assertEqual(actual['relic_token_stats'][0]['regeneration_rate'],
                         plain['relic_token_stats'][0]['regeneration_rate'])
        self.assertEqual(actual['estimate']['skill']['cycle_hps'], 0)

    def test_duplicate_ids_and_repeated_evaluation_do_not_accumulate_multipliers(self):
        args = scenario('char_1037_amiya3', 1, relic_ids=[ROSE, ROSE, MEAT, MEAT, PERFUME, PERFUME])
        before = copy.deepcopy(args)
        first = calculate_damage(args)
        self.assertEqual(first, calculate_damage(args))
        self.assertEqual(args, before)
        self.assertEqual(len(first['relic_resolution']['records']), 3)

    def test_no_healing_or_regeneration_section_from_multiplier_alone_on_nonhealer(self):
        actual = calculate_damage(scenario(relic_ids=[ROSE]))
        sections = {row['id'] for row in actual['report']['sections']}
        self.assertFalse(sections & {'healing', 'regeneration', 'relic_regeneration'})
        self.assertEqual(actual['total_damage'], calculate_damage(scenario())['total_damage'])

    def test_one_item_fixed_regeneration_is_never_direct_healing(self):
        actual = calculate_damage(scenario(relic_ids=[MEAT]))
        self.assertEqual(actual['relic_regeneration_rate'], 3)
        self.assertEqual(actual['estimate']['skill']['total_healing'], 0)
        self.assertEqual(actual['estimate']['skill']['cycle_hps'], 0)
        self.assertEqual(section(actual, 'relic_regeneration')['metrics'][0]['value'], 3)

    def test_token_only_modifiers_keep_summoner_cost_and_stats(self):
        args = scenario('char_110_deepcl', 1)
        plain = calculate_damage(args)
        actual = calculate_damage({**args, 'relic_ids': ['rogue_6_relic_legacy_134']})
        self.assertEqual(actual['deployment_cost'], plain['deployment_cost'])
        self.assertEqual(actual['estimate']['base_stats'], plain['estimate']['base_stats'])
        self.assertEqual(actual['relic_token_stats'][0]['deployment_cost'], 0)
        self.assertTrue(actual['relic_token_stats'][0]['free_deployment_slot'])
        self.assertNotIn('relic_deployment', {row['id'] for row in actual['report']['sections']})

    def test_cost_card_is_not_applied_to_non_tanks_or_summons(self):
        for operator in ('kaltsit', 'silverash', 'char_110_deepcl'):
            with self.subTest(operator=operator):
                plain = calculate_damage(scenario(operator, 1))
                actual = calculate_damage(scenario(operator, 1, relic_ids=[LIGHT]))
                self.assertNotIn('deployment_reference', actual)
                self.assertEqual(actual['deployment_cost'], plain['deployment_cost'])
                self.assertEqual(actual['relic_resolution']['records'][0]['status'], 'inapplicable')
                self.assertTrue(actual['relic_resolution']['complete'])

    def test_missing_cost_condition_keeps_combined_reference_unknown(self):
        actual = calculate_damage(scenario(relic_ids=[TIED, BED]))
        reference = actual['deployment_reference']['cost']
        self.assertIsNone(reference['combined_reference'])
        self.assertIn('empty_slots', reference['missing_conditions'])
        self.assertIsNone(actual['deployment_cost'])
        self.assertFalse(actual['relic_resolution']['complete'])

    def test_confirmed_zero_script_discount_allows_only_the_proved_native_cost(self):
        for items, key, expected in (([TIED, BED], 'cost', 12), ([LIGHT, BED], 'first_deployment_cost', 5)):
            with self.subTest(items=items):
                actual = calculate_damage(scenario(relic_ids=items, relic_context={'empty_slots': 0}))
                reference = actual['deployment_reference'][key]
                self.assertIsNotNone(reference['combined_reference'])
                self.assertEqual(actual['deployment_cost'],expected)
                self.assertTrue(actual['relic_resolution']['complete'])
                self.assertIsNone(reference['actual_cost'])
                self.assertFalse(actual['deployment_reference']['live_state_verified'])
                bed = next(row for row in actual['relic_resolution']['records'] if row['id'] == BED)
                self.assertEqual(bed['missing_conditions'], [])
                self.assertEqual(bed['applied'][0]['value'], 0)

    def test_proved_inventory_delta_combines_after_card_floor_and_keeps_live_state_unknown(self):
        for items, key, expected in (([TIED, BED], 'cost', 6), ([LIGHT, BED], 'first_deployment_cost', 0)):
            with self.subTest(items=items):
                actual = calculate_damage(scenario(relic_ids=items, relic_context={'empty_slots': 4}))
                self.assertEqual(actual['deployment_reference'][key]['combined_reference'], expected)
                self.assertEqual(actual['deployment_cost'], expected)
                # 057 native prefab/metadata/CFG proves integer -6 after
                # card scaling; runtime measurements are still not asserted.
                self.assertTrue(actual['relic_resolution']['complete'])
                reference=actual['deployment_reference'][key]
                self.assertIsNone(reference['actual_cost'])
                excluded=reference.get('excluded_discount_sources',reference.get('excluded_script_discounts',[]))
                self.assertNotIn(BED,excluded)
                self.assertEqual(reference['native_trace']['runtime_delta'],-6)

    def test_verified_redeploy_runes_multiply_before_integer_writer(self):
        args = scenario('char_1029_yato2', 2)
        plain = calculate_damage(args)
        actual = calculate_damage({**args, 'relic_ids': ['rogue_6_relic_legacy_77'],
                                   'char_buff_ids': ['rogue_6_from_relic_7']})
        self.assertEqual(actual['estimate']['base_stats']['redeploy_seconds'],6) # round-even(18*.65*.5)
        self.assertTrue(actual['relic_resolution']['complete'])
        self.assertFalse(any('char_attribute_final_scaler' in text for text in actual['warnings']))

    def test_combat_loss_input_never_changes_offline_cost_reference_or_healing(self):
        args = scenario(relic_ids=[TIED])
        plain = calculate_damage(args)
        actual = calculate_damage({**args, 'relic_context': {'deployment_hp_ratio': 0.5,
                                                           'deployment_loss_unused': 1}})
        self.assertEqual(actual['deployment_reference'], plain['deployment_reference'])
        self.assertEqual(actual['estimate']['skill'], plain['estimate']['skill'])
        self.assertEqual(actual['estimate']['base_stats'], plain['estimate']['base_stats'])
        self.assertFalse(any(rule['kind'] == 'deployment_hp_loss' for rule in actual['relic_resolution']['rules']))

    def test_kaltsit_zero_recipients_have_zero_public_healing_even_with_rose(self):
        for number in (1, 3):
            for relics in ([], [ROSE]):
                with self.subTest(skill=number, relics=relics):
                    actual = calculate_damage(scenario('kaltsit', number, healing_targets=0, relic_ids=relics))
                    self.assertEqual(actual['estimate']['skill']['window_healing'], 0)
                    self.assertEqual(actual['total_healing'], 0)

    def test_kaltsit_public_healing_matches_window_after_target_cap_and_rose(self):
        for number, cap in ((1, 1), (3, 2)):
            for targets in (1, 2, 100):
                with self.subTest(skill=number, targets=targets):
                    plain = calculate_damage(scenario('kaltsit', number, healing_targets=1, relic_ids=[ROSE]))
                    actual = calculate_damage(scenario('kaltsit', number, healing_targets=targets, relic_ids=[ROSE]))
                    self.assertAlmostEqual(actual['total_healing'], plain['total_healing'] * min(cap, targets))
                    self.assertAlmostEqual(actual['total_healing'], actual['estimate']['skill']['window_healing'])


if __name__ == '__main__':
    unittest.main()
