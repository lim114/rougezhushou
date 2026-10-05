"""Observable offline behavior after withdrawing battle-dependent relic inputs."""
import copy
import unittest

from rouge.damage import calculate_damage
from rouge.relics import mechanics


class OfflineScopeTests(unittest.TestCase):
    def assert_output_equal(self, actual, expected):
        self.assertEqual(actual['estimate']['base_stats'], expected['estimate']['base_stats'])
        self.assertEqual(actual['estimate']['skill'], expected['estimate']['skill'])
        self.assertEqual(actual['total_damage'], expected['total_damage'])

    def test_kill_recovery_and_kill_sp_are_description_only(self):
        s = {'operator': 'mechanist', 'skill': 3}
        base = calculate_damage(s)
        r = calculate_damage({**s, 'relic_ids': ['rogue_6_relic_fight_6', 'rogue_6_relic_fight_5']})
        self.assert_output_equal(r, base)
        self.assertTrue(r['relic_resolution']['complete'])
        self.assertNotIn('kill_recovery', r)
        self.assertNotIn('sp_events', r['estimate'])
        self.assertEqual({x['status'] for x in r['relic_resolution']['records']}, {'reference_only'})
        descriptions = next(x for x in r['report']['sections'] if x['id'] == 'relic_combat_reference')
        self.assertTrue(any('渴血钳兽' in n and '10%' in n for n in descriptions['notes']))

    def test_old_event_tables_cannot_restore_excluded_callbacks(self):
        s = {'operator': 'mechanist', 'skill': 3, 'relic_ids': ['rogue_6_relic_fight_5']}
        default = calculate_damage(s)
        for events in ({'initial': [{'at_seconds': 1, 'type': 'kill'}], 'cycle': []}, {'initial': [], 'cycle': []}):
            r = calculate_damage({**s, 'timing': {'sp_events': events}})
            self.assert_output_equal(r, default)
            self.assertNotIn('relic_sp_events', r)

    def test_received_damage_and_bound_tank_sp_cannot_change_charge(self):
        from rouge.catalog import catalog
        op = next(op for op,p in catalog()['operators'].items() if p['profession'] == 'tank')
        s = {'operator': op, 'skill': 1}
        base = calculate_damage(s)
        r = calculate_damage({**s, 'relic_ids': ['rogue_6_relic_legacy_118'],
                              'char_buff_ids': ['rogue_6_from_relic_4']})
        self.assert_output_equal(r, base)
        self.assertFalse(r['relic_resolution']['rules'])
        self.assertFalse(r['relic_resolution']['timing_unresolved'])

    def test_shields_first_damage_and_placement_inputs_are_not_required(self):
        s = {'operator': 'mechanist', 'skill': 3}
        base = calculate_damage(s)
        ids = ['rogue_6_relic_legacy_58', 'rogue_6_relic_legacy_63', 'rogue_6_relic_fight_1',
               'rogue_6_relic_fight_2', 'rogue_6_relic_fight_7', 'rogue_6_relic_legacy_101']
        for context in ({}, {'near_protection_point': 1, 'deployed_seconds': 100, 'enemy_first_damage_unused': 1}):
            r = calculate_damage({**s, 'relic_ids': ids, 'relic_context': context})
            self.assert_output_equal(r, base)
            self.assertTrue(r['relic_resolution']['complete'])
            self.assertFalse(r['relic_protection'])
            self.assertTrue(all(not record['missing_conditions'] for record in r['relic_resolution']['records']))

    def test_other_bindings_keep_stable_attack_and_speed(self):
        s = {'operator': 'mechanist', 'skill': 3}
        base = calculate_damage(s)['estimate']['base_stats']
        foam = calculate_damage({**s, 'char_buff_ids': ['rogue_6_from_relic_12']})
        self.assertEqual(foam['estimate']['base_stats']['attack'], 1261) # rune writer: round-even(573*2.2)
        self.assertEqual(foam['estimate']['base_stats']['attack_speed'], 50)
        cookie = calculate_damage({**s, 'char_buff_ids': ['rogue_6_from_relic_15']})
        self.assertEqual(cookie['estimate']['skill']['sp_recovery_per_second'], 1.8)

    def test_mixed_pioneer_hand_keeps_cost_and_sp_discount(self):
        s = {'operator': 'silverash', 'skill': 3}
        base = calculate_damage(s)
        r = calculate_damage({**s, 'relic_ids': ['rogue_6_relic_hand_1']})
        self.assertEqual(r['deployment_cost'], max(0, base['deployment_cost'] - 6))
        self.assertEqual(r['estimate']['skill']['sp_cost'], base['estimate']['skill']['sp_cost'] * .5)
        self.assertEqual(r['estimate']['base_stats'], base['estimate']['base_stats'])
        self.assertTrue(r['relic_resolution']['complete'])
        self.assertFalse(r['relic_resolution']['records'][0]['pending'])
        self.assertNotIn('sp_events', r['estimate'])
        other = {'operator': 'char_151_myrtle', 'skill': 1}
        self.assert_output_equal(calculate_damage({**other,'relic_ids':['rogue_6_relic_hand_1']}),calculate_damage(other))

    def test_mixed_redeployment_device_keeps_half_redeploy(self):
        s = {'operator': 'char_1029_yato2', 'skill': 2}
        base = calculate_damage(s)
        r = calculate_damage({**s, 'relic_ids': ['rogue_6_relic_artifact_6']})
        self.assertEqual(r['estimate']['base_stats']['redeploy_seconds'],
                         base['estimate']['base_stats']['redeploy_seconds'] * .5)
        self.assertEqual(r['total_damage'], base['total_damage'])
        self.assertTrue(r['relic_resolution']['complete'])

    def test_mixed_other_bound_cost_has_native_integer_estimate_without_hp_loss(self):
        s = {'operator': 'mechanist', 'skill': 3}
        base = calculate_damage(s)
        r = calculate_damage({**s, 'relic_ids': ['rogue_6_relic_fight_11'],
                              'relic_context': {'deployment_hp_ratio': .5, 'deployment_loss_unused': 1}})
        self.assert_output_equal(r, base)
        reference = r['deployment_reference']
        self.assertEqual(reference['cost']['unrounded_rune_reference'], base['deployment_cost'] * .5)
        # Native ObscuredInt writer rounds 23 * .5 to the even integer 12.
        self.assertEqual(r['deployment_cost'], 12)
        self.assertEqual(reference['cost']['estimated_cost'], 12)
        self.assertIsNone(reference['cost']['actual_cost'])
        self.assertFalse(reference['live_state_verified'])
        self.assertNotIn('hp_loss', reference)
        record = r['relic_resolution']['records'][0]
        self.assertFalse(record['missing_conditions'])
        self.assertEqual(record['pending'], [])  # The static native cost chain is proved.
        self.assertFalse(any(x['id'] == 'deployment_hp_loss' for x in r['report']['sections']))

    def test_stable_counts_and_condition_notes_remain_separate_from_references(self):
        r = calculate_damage({'operator': 'mechanist', 'skill': 3,
                              'relic_ids': ['rogue_6_relic_fight_6', 'rogue_6_relic_cargo_11'],
                              'relic_context': {'fire_rod_stacks': 3}})
        evidence = next(x for x in r['report']['sections'] if x['id'] == 'relic_evidence')
        reference = next(x for x in r['report']['sections'] if x['id'] == 'relic_combat_reference')
        self.assertTrue(any('条件参考' in n and '=3' in n for n in evidence['notes']))
        self.assertFalse(any('条件参考' in n for n in reference['notes']))

    def test_bound_sniper_penetration_does_not_apply_to_other_professions(self):
        s = {'operator': 'char_133_mm', 'skill': 1, 'base_attack': 1000, 'enemy_defense': 100}
        base = calculate_damage(s)
        r = calculate_damage({**s, 'char_buff_ids': ['rogue_6_from_relic_5']})
        self.assertEqual(r['components'][0]['per_hit'] - base['components'][0]['per_hit'], 50)
        with self.assertRaisesRegex(ValueError, '职业不符'):
            calculate_damage({'operator': 'mechanist', 'skill': 3, 'char_buff_ids': ['rogue_6_from_relic_5']})

    def test_native_wine_clock_does_not_need_kill_or_received_event_input(self):
        s = {'operator': 'mechanist', 'skill': 1, 'timing_mode': 'frames', 'relic_ids': ['rogue_6_relic_legacy_97']}
        base = calculate_damage(s)
        r = calculate_damage({**s, 'relic_ids': s['relic_ids'] + ['rogue_6_relic_fight_5', 'rogue_6_relic_legacy_118']})
        self.assert_output_equal(r, base)
        self.assertIsNotNone(r['estimate']['skill']['cycle_seconds'])
        self.assertNotIn('cycle_seconds_range', r['estimate']['skill'])
        self.assertFalse(r['relic_resolution']['timing_unresolved'])
        self.assertNotIn('sp_events', r['estimate'])

    def test_recalculation_does_not_change_inputs_or_pinned_mechanics(self):
        data = copy.deepcopy(mechanics())
        s = {'operator': 'mechanist', 'skill': 3, 'relic_ids': ['rogue_6_relic_fight_6'],
             'relic_context': {'current_hp_ratio': .2}}
        before = copy.deepcopy(s)
        one = calculate_damage(s)
        two = calculate_damage(s)
        self.assert_output_equal(one, two)
        self.assertEqual(s, before)
        self.assertEqual(mechanics(), data)
