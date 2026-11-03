from copy import deepcopy
import unittest

from rouge.route_resource_ledger import route_resource_ledger


def payload():
    return {'graph': {'current_node': 's', 'nodes': [
        {'id': key, 'row': 0, 'col': ordinal, 'base_node_type': kind, 'scrap_category': 'EVENTS'}
        for ordinal, (key, kind) in enumerate([('s', 'EMPTY'), ('a', 'BATTLE_SHOP'), ('b', 'SCRAP_SHOP'), ('g', 'FINAL')])],
        'edges': [['s', 'a'], ['a', 'b'], ['b', 'g']]}, 'action_points': 8,
        'inventory': [{'instance_id': 'gold', 'item_id': 'rogue_6_scrap_M_10', 'remaining_uses': 2},
                      {'instance_id': 'hope', 'item_id': 'rogue_6_scrap_M_09', 'remaining_uses': 1},
                      {'instance_id': 'spring', 'item_id': 'rogue_6_scrap_M_04', 'remaining_uses': 1}],
        'passive_items': [{'item_id': 'rogue_6_scrap_P_02', 'remaining_activations': 1}, {'item_id': 'rogue_6_scrap_P_03', 'remaining_activations': 1}],
        'routes': [{'id': 'grants', 'steps': [{'mode': 'gold', 'target': 'a'}, {'mode': 'gold', 'target': 'b'}, {'mode': 'hope', 'target': 'g'}]},
                   {'id': 'walk', 'steps': [{'mode': 'walking', 'target': 'a'}, {'mode': 'walking', 'target': 'b'}, {'mode': 'walking', 'target': 'g'}]}],
        'activation_declarations': {'grants': {'1': {'rogue_6_scrap_P_02': True, 'rogue_6_scrap_P_03': True}}},
        'terminals': {key: {'transition': 'main_region_advance', 'exit_node_type': 'FINAL', 'success_declared': True} for key in ['grants', 'walk']}}


class RouteResourceLedgerTests(unittest.TestCase):
    def test_complete_conditional_flow_combines_movement_passive_base_and_final_grants(self):
        data = payload(); row = route_resource_ledger(**data); first = row['routes'][0]
        self.assertEqual(first['known_source_grant_subtotal'], {'hope': 7, 'gold': 8, 'shield': 3, 'random_relic': 1, 'random_move_item': 1})
        self.assertEqual(first['known_combined_component_subtotal']['gold'], {'minimum': 8, 'maximum': 8})
        self.assertTrue(first['complete_modeled_grant_conditions']); self.assertIsNotNone(first['conditional_combined_component_total'])
        self.assertFalse(first['complete_reward_pool_known']); self.assertIsNone(first['actual_final_resources'])
        self.assertEqual(first['terminal_phase']['conditional_expired_instances'], ['spring'])
        self.assertIsNone(row['actual_best_route']); self.assertFalse(row['inventory_updated'])

    def test_quantity_differences_are_conditioned_on_same_goal_terminal_and_not_reward_value(self):
        row = route_resource_ledger(**payload()); pair = row['pairwise_component_differences'][0]
        self.assertEqual(pair['conditional_component_difference']['hope_grant_quantity'], 2)
        self.assertEqual(pair['conditional_component_difference']['shield_grant_quantity'], 3)
        self.assertEqual(pair['conditional_component_difference']['gold_interval'], {'minimum': 8, 'maximum': 8})
        self.assertFalse(pair['random_item_value_comparable']); self.assertIsNone(pair['actual_better_route'])
        data = payload(); data['terminals']['walk'] = {'transition': 'portal_return', 'success_declared': True}
        pair = route_resource_ledger(**data)['pairwise_component_differences'][0]
        self.assertIsNone(pair['conditional_component_difference'])

    def test_no_activation_is_inferred_from_eligible_processed_move(self):
        data = payload(); data['activation_declarations'] = {}; data['terminals'] = {}
        first = route_resource_ledger(**data)['routes'][0]
        self.assertEqual(first['known_source_grant_subtotal']['shield'], 0)
        self.assertEqual(first['known_source_grant_subtotal']['random_relic'], 0)
        self.assertTrue(first['unknown_grant_components'])
        self.assertIsNone(first['conditional_combined_component_total'])
        self.assertTrue(all(row['remaining_activations'] is None for row in first['passive_availability_reference_state']))

    def test_unknown_possible_activation_invalidates_later_single_use_availability(self):
        data = payload(); data['graph']['nodes'][1].pop('scrap_category'); data['terminals'] = {}
        data['activation_declarations']['grants']['2'] = {'rogue_6_scrap_P_02': True}
        first = route_resource_ledger(**data)['routes'][0]
        second = next(row for row in first['grant_rows'] if row['step'] == 2 and row.get('item_id') == 'rogue_6_scrap_P_02')
        self.assertIsNone(second['availability_before_reference']); self.assertIsNone(second['condition_matches'])
        self.assertEqual(first['known_source_grant_subtotal']['random_relic'], 0)

    def test_explicit_nonactivation_preserves_single_use_for_later_move(self):
        data = payload(); data['terminals'] = {}; data['activation_declarations'] = {'grants': {
            '1': {'rogue_6_scrap_P_02': False, 'rogue_6_scrap_P_03': False},
            '2': {'rogue_6_scrap_P_02': True, 'rogue_6_scrap_P_03': True}}}
        first = route_resource_ledger(**data)['routes'][0]
        self.assertEqual(first['known_source_grant_subtotal']['random_relic'], 1)
        self.assertEqual(first['known_source_grant_subtotal']['shield'], 3)
        rows = [row for row in first['grant_rows'] if row.get('item_id') == 'rogue_6_scrap_P_03']
        self.assertEqual([row['condition_matches'] for row in rows], [False, True, False])

    def test_declared_second_activation_conflicting_with_spent_budget_does_not_close_total(self):
        data = payload(); data['terminals'] = {}; data['activation_declarations']['grants']['2'] = {'rogue_6_scrap_P_03': True}
        first = route_resource_ledger(**data)['routes'][0]
        self.assertEqual(first['known_source_grant_subtotal']['shield'], 3)
        self.assertEqual(first['declaration_conflicts'][0]['step'], 2)
        self.assertFalse(first['complete_modeled_grant_conditions']); self.assertIsNone(first['conditional_combined_component_total'])

    def test_branch_local_passive_budget_is_independent_from_existing_automatic_movement_ledger(self):
        data = payload(); data['routes'][1] = deepcopy(data['routes'][0]); data['routes'][1]['id'] = 'second'
        data['activation_declarations']['second'] = deepcopy(data['activation_declarations']['grants'])
        data['terminals'] = {}
        row = route_resource_ledger(**data)
        self.assertEqual(row['routes'][0]['known_source_grant_subtotal'], row['routes'][1]['known_source_grant_subtotal'])
        self.assertEqual(row['routes'][0]['known_source_grant_subtotal']['shield'], 3)

    def test_battle_end_phase_is_independent_of_activation_and_generic_victory(self):
        data = payload(); data['graph']['nodes'][1].update(base_node_type='BATTLE_NORMAL', scrap_category='BATTLES')
        data['inventory'] = [{'instance_id': 'jet', 'item_id': 'rogue_6_scrap_M_08', 'remaining_uses': 1}]
        data['routes'] = [{'id': 'battle', 'steps': [{'mode': 'jet', 'target': 'a'}]}]
        data['passive_items'] = [{'item_id': 'rogue_6_scrap_P_01', 'remaining_activations': 1}]
        data['activation_declarations'] = {'battle': {'1': {'rogue_6_scrap_P_01': True}}}; data['terminals'] = {}
        first = route_resource_ledger(**data)['routes'][0]
        self.assertEqual(first['known_source_grant_subtotal']['random_relic'], 0)
        self.assertEqual(first['passive_availability_reference_state'][0]['remaining_activations'], 0)
        self.assertTrue(any(row['reason'] == 'after_battle_completion_not_declared' for row in first['unknown_grant_components']))
        data['after_battle_declarations'] = {'battle': {'1': True}}
        first = route_resource_ledger(**data)['routes'][0]
        self.assertEqual(first['known_source_grant_subtotal']['random_relic'], 1)
        self.assertFalse(any(row['resource'] == 'battle_attack_speed_reference' for row in first['grant_rows']))
        self.assertIsNone(first['conditional_combined_component_total'])  # Base battle identity/victory remains independently unknown.

    def test_payment_zero_or_unknown_movement_never_funds_tail_or_terminal(self):
        for ap in [1, None, 0]:
            data = payload(); data['action_points'] = ap; first = route_resource_ledger(**data)['routes'][0]
            self.assertEqual(sum(first['known_source_grant_subtotal'].values()), 0)
            self.assertIsNone(first['conditional_combined_component_total'])
            self.assertFalse(first['terminal_phase']['admitted_to_conditional_terminal_phase'])
            self.assertEqual(first['terminal_phase']['conditional_expired_instances'], [])

    def test_final_success_unknown_false_and_boss_ratio_keep_exact_unknown_quantities(self):
        for success in [None, False]:
            data = payload(); data['terminals']['grants']['success_declared'] = success
            first = route_resource_ledger(**data)['routes'][0]
            self.assertEqual(first['known_source_grant_subtotal']['hope'], 2)
            self.assertFalse(first['terminal_phase']['admitted_to_conditional_terminal_phase'])
        data = payload(); data['graph']['nodes'][-1]['base_node_type'] = 'BATTLE_BOSS'
        data['terminals'] = {'grants': {'transition': 'main_region_advance', 'exit_node_type': 'BATTLE_BOSS', 'success_declared': True}}
        data['routes'] = [data['routes'][0]]
        first = route_resource_ledger(**data)['routes'][0]
        conversion = next(row for row in first['grant_rows'] if row['origin'] == 'terminal_conversion')
        self.assertIsNone(conversion['source_stated_quantity']); self.assertIsNone(conversion['condition_matches'])
        self.assertIsNone(conversion['conversion_ratio_reference'])

    def test_portal_exception_and_depleted_items_are_separate_from_main_region_expiry(self):
        data = payload(); data['terminals'] = {'grants': {'transition': 'portal_return', 'success_declared': True}}
        first = route_resource_ledger(**data)['routes'][0]
        self.assertEqual(first['terminal_phase']['conditional_portal_preserved_instances'], ['spring'])
        self.assertEqual(first['terminal_phase']['conditional_expired_instances'], [])
        data['inventory'][-1]['remaining_uses'] = 0
        first = route_resource_ledger(**data)['routes'][0]
        self.assertFalse(first['terminal_phase']['conditional_portal_preserved_instances'])
        self.assertFalse(any(row['instance_id'] == 'spring' for row in first['terminal_phase']['reference']['inventory_conditions']))

    def test_m07_enter_exception_does_not_prove_return_disposition(self):
        data = payload(); data['inventory'].append({'instance_id': 'eight', 'item_id': 'rogue_6_scrap_M_07', 'remaining_uses': 1})
        data['terminals'] = {'grants': {'transition': 'portal_return', 'success_declared': True}}
        first = route_resource_ledger(**data)['routes'][0]
        self.assertEqual(first['terminal_phase']['conditional_portal_preserved_instances'], ['spring'])
        self.assertEqual(first['terminal_phase']['unresolved_inventory_dispositions'][0]['instance_id'], 'eight')
        item = next(row for row in first['terminal_phase']['reference']['inventory_conditions'] if row['instance_id'] == 'eight')
        self.assertIsNone(item['preserved_by_portal_exception']); self.assertFalse(first['complete_modeled_grant_conditions'])
        data['terminals']['grants']['transition'] = 'portal_enter'
        first = route_resource_ledger(**data)['routes'][0]
        self.assertEqual(first['terminal_phase']['conditional_portal_preserved_instances'], ['spring', 'eight'])
        self.assertTrue(first['complete_modeled_grant_conditions'])

    def test_synthetic_passive_terminal_ids_do_not_collide_with_caller_inventory_ids(self):
        data = payload(); data['inventory'][-1]['instance_id'] = 'passive:rogue_6_scrap_P_03'
        first = route_resource_ledger(**data)['routes'][0]
        ids = [row['instance_id'] for row in first['terminal_phase']['reference']['inventory_conditions']]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertIn('passive:rogue_6_scrap_P_03:2', ids)
        self.assertEqual(first['terminal_phase']['conditional_expired_instances'], ['passive:rogue_6_scrap_P_03'])

    def test_input_isolation_and_strict_phase_terminal_validation(self):
        data = payload(); before = deepcopy(data)
        first = route_resource_ledger(**data); second = route_resource_ledger(**data)
        self.assertEqual(first, second); self.assertEqual(data, before)
        first['routes'][0]['passive_availability_reference_state'][0]['remaining_activations'] = 99
        self.assertNotEqual(first, second)
        for field, value in [('activation_declarations', {'missing': {}}), ('activation_declarations', {'grants': {'01': {}}}),
                             ('activation_declarations', {'grants': {'1': {'unknown': True}}}), ('activation_declarations', {'grants': {'1': {'rogue_6_scrap_P_02': 1}}}),
                             ('after_battle_declarations', {'grants': {'1': 'yes'}}), ('terminals', {'grants': {'transition': 'main_region_advance', 'exit_node_type': 'BATTLE_BOSS', 'success_declared': True}}),
                             ('terminals', {'grants': {'transition': 'portal_return', 'success_declared': 1}})]:
            invalid = deepcopy(data); invalid[field] = value
            with self.subTest(field=field, value=value), self.assertRaises(ValueError): route_resource_ledger(**invalid)


if __name__ == '__main__': unittest.main()
