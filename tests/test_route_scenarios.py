from copy import deepcopy
import unittest

from rouge.route_scenarios import scenario_route_matrix


def payload():
    graph = {'current_node': 's', 'zone_id': 'zone_1', 'template_id': 'public-scenario-tests',
             'nodes': [{'id': key, 'row': 0, 'col': ordinal, 'base_node_type': kind, 'scrap_category': 'EVENTS'}
                       for ordinal, (key, kind) in enumerate([('s', 'EMPTY'), ('a', 'BATTLE_SHOP'), ('b', 'SCRAP_SHOP'), ('g', 'FINAL')])],
             'edges': [['s', 'a'], ['a', 'b'], ['b', 'g']]}
    routes = [{'id': 'grants', 'steps': [{'mode': 'gold', 'target': 'a'}, {'mode': 'gold', 'target': 'b'}, {'mode': 'hope', 'target': 'g'}]},
              {'id': 'walk', 'steps': [{'mode': 'walking', 'target': 'a'}, {'mode': 'walking', 'target': 'b'}, {'mode': 'walking', 'target': 'g'}]}]
    case = {'id': 'case8', 'action_points': 8, 'inventory': [
        {'instance_id': 'gold', 'item_id': 'rogue_6_scrap_M_10', 'remaining_uses': 2},
        {'instance_id': 'hope', 'item_id': 'rogue_6_scrap_M_09', 'remaining_uses': 1},
        {'instance_id': 'spring', 'item_id': 'rogue_6_scrap_M_04', 'remaining_uses': 1}],
        'passive_items': [{'item_id': 'rogue_6_scrap_P_02', 'remaining_activations': 1}, {'item_id': 'rogue_6_scrap_P_03', 'remaining_activations': 1}],
        'residents': [], 'risk_policy': 'show_all',
        'activation_declarations': {'grants': {'1': {'rogue_6_scrap_P_02': True, 'rogue_6_scrap_P_03': True}}},
        'terminals': {key: {'transition': 'main_region_advance', 'exit_node_type': 'FINAL', 'success_declared': True} for key in ['grants', 'walk']}}
    return {'graph': graph, 'routes': routes, 'scenarios': [case]}


class RouteScenarioTests(unittest.TestCase):
    def test_closed_scenario_envelope_and_pair_rule_never_become_true_utility_or_probability(self):
        data = payload(); second = deepcopy(data['scenarios'][0]); second.update(id='case9', action_points=9); data['scenarios'].append(second)
        row = scenario_route_matrix(**data); first = row['route_summaries'][0]
        self.assertTrue(first['all_declared_compound_conditions_closed'])
        self.assertEqual(first['closed_quantity_envelope']['hope_grant_quantity'], {'minimum': 7, 'maximum': 8})
        self.assertEqual(first['closed_quantity_envelope']['gold'], {'minimum': 8, 'maximum': 8})
        self.assertEqual(first['sensitivity_witnesses'][0]['changed_fields'], ['known_component_subtotal'])
        comparison = row['pairwise_robust_component_comparisons'][0]
        self.assertTrue(comparison['declared_component_nonworse_across_all_cases'])
        self.assertFalse(comparison['random_item_value_comparable']); self.assertIsNone(comparison['actual_better_route'])
        self.assertIsNone(row['probability']); self.assertIsNone(row['actual_best_route']); self.assertIsNone(first['actual_safe'])

    def test_compound_ap_zero_and_spent_stock_remain_independent_stopped_cases(self):
        data = payload(); low = deepcopy(data['scenarios'][0]); low.update(id='ap2', action_points=2)
        spent = deepcopy(data['scenarios'][0]); spent['id'] = 'spent'; spent['inventory'][0]['remaining_uses'] = 0
        data['scenarios'].extend([low, spent]); row = scenario_route_matrix(**data)
        self.assertEqual(row['cases'][1]['routes'][0]['movement_status'], 'unknown_movement_reference')
        self.assertEqual(row['cases'][1]['routes'][0]['movement_stop_reason'], 'zero_ap_callback_order_unverified')
        self.assertEqual(row['cases'][2]['routes'][0]['movement_status'], 'blocked_movement_reference')
        self.assertIsNone(row['route_summaries'][0]['closed_quantity_envelope'])
        self.assertIsNone(row['pairwise_robust_component_comparisons'][0]['declared_component_nonworse_across_all_cases'])
        self.assertEqual(row['cases'][0]['routes'][0]['resource_reference']['routes'][0]['known_source_grant_subtotal']['gold'], 8)

    def test_missing_planned_instance_blocks_only_that_route_and_keeps_exact_case_input(self):
        data = payload(); case = data['scenarios'][0]; case['inventory'] = case['inventory'][1:]
        row = scenario_route_matrix(**data); planned, walking = row['cases'][0]['routes']
        self.assertEqual(planned['movement_status'], 'blocked_declared_inventory')
        self.assertEqual(planned['movement_stop_reason'], 'planned_instance_absent_from_explicit_snapshot')
        self.assertEqual(planned['missing_planned_instances'], ['gold'])
        self.assertIsNone(planned['resource_reference'])
        self.assertEqual(walking['movement_status'], 'closed'); self.assertTrue(walking['quantity_conditions_closed'])
        self.assertEqual(row['cases'][0]['scenario_input'], case)

    def test_known_prefix_before_missing_later_instance_preserves_source_without_full_total(self):
        data = payload(); data['scenarios'][0]['inventory'].pop(1)
        first = scenario_route_matrix(**data)['cases'][0]['routes'][0]
        self.assertEqual(first['evaluated_prefix_step_count'], 2)
        self.assertEqual(first['missing_mode_steps'], [{'step': 3, 'instance_id': 'hope'}])
        source = first['resource_reference']; self.assertTrue(source['prefix_only']); self.assertEqual(source['planned_full_goal'], 'g')
        self.assertEqual(source['routes'][0]['known_source_grant_subtotal']['gold'], 8)
        self.assertIsNone(source['routes'][0]['conditional_combined_component_total'])
        self.assertTrue(first['resident_reference']['prefix_only'])

    def test_inventory_and_passive_unknown_never_become_an_empty_complete_snapshot(self):
        data = payload(); case = data['scenarios'][0]; case['inventory'] = None; case['passive_items'] = None
        row = scenario_route_matrix(**data); planned, walking = row['cases'][0]['routes']
        self.assertEqual(planned['movement_status'], 'unknown_declared_inventory')
        self.assertEqual(planned['movement_stop_reason'], 'planned_instance_not_confirmed')
        self.assertIsNone(planned['resource_reference'])
        self.assertEqual(walking['movement_status'], 'closed'); self.assertFalse(walking['quantity_conditions_closed'])
        source = walking['resource_reference']['routes'][0]
        self.assertFalse(source['complete_modeled_grant_conditions']); self.assertIsNone(source['conditional_combined_component_total'])
        self.assertEqual(source['unknown_snapshot_components'], ['inventory_snapshot_unknown', 'passive_snapshot_unknown'])
        self.assertTrue(all(summary['closed_quantity_envelope'] is None for summary in row['route_summaries']))

    def test_explicit_empty_snapshot_is_distinct_from_unknown_snapshot(self):
        data = payload(); data['routes'] = [data['routes'][1]]; case = data['scenarios'][0]
        case.update(inventory=[], passive_items=[], residents=[], activation_declarations={}, terminals={})
        row = scenario_route_matrix(**data)
        self.assertTrue(row['route_summaries'][0]['all_declared_compound_conditions_closed'])
        self.assertEqual(row['route_summaries'][0]['closed_quantity_envelope']['hope_grant_quantity'], {'minimum': 0, 'maximum': 0})
        self.assertIsNone(row['route_summaries'][0]['actual_feasible'])

    def test_resident_snapshot_unknown_is_independent_of_quantity_and_policy_requirements(self):
        data = payload(); data['scenarios'][0].update(residents=None, risk_policy='avoid_candidate_overlap')
        row = scenario_route_matrix(**data); first = row['cases'][0]['routes'][0]
        self.assertTrue(first['quantity_conditions_closed']); self.assertIsNone(first['risk_policy_match'])
        self.assertFalse(row['route_summaries'][0]['all_declared_compound_conditions_closed'])
        self.assertIsNone(row['pairwise_robust_component_comparisons'][0]['declared_component_nonworse_across_all_cases'])
        self.assertEqual(row['pairwise_robust_component_comparisons'][0]['case_relations'][0]['reason'], 'declared_risk_policy_not_matched')

    def test_candidate_overlap_and_fallback_unknown_are_distinct_policy_outcomes_not_safety(self):
        data = payload(); data['scenarios'][0].update(residents=[{'node_id': 'a'}], risk_policy='avoid_candidate_overlap')
        row = scenario_route_matrix(**data)
        self.assertFalse(row['cases'][0]['routes'][0]['risk_policy_match'])
        self.assertEqual(row['route_summaries'][0]['policy_rejected_scenario_ids'], ['case8'])
        data = payload(); data['graph']['nodes'].extend([
            {'id': 'r', 'row': 1, 'col': 0, 'base_node_type': 'EMPTY'},
            {'id': 'p', 'row': 1, 'col': 1, 'base_node_type': 'BATTLE_SAVAGE'}])
        data['graph']['edges'].append(['r', 'p']); data['scenarios'][0].update(residents=[{'node_id': 'r'}], risk_policy='avoid_candidate_overlap')
        row = scenario_route_matrix(**data); first = row['cases'][0]['routes'][0]
        self.assertIsNone(first['risk_policy_match']); self.assertIn('resident_navigation_unknown', first['unknown_reasons'])
        self.assertIsNone(row['route_summaries'][0]['actual_safe'])

    def test_terminal_difference_and_unknown_activation_disable_cross_case_order_relation(self):
        data = payload(); case = data['scenarios'][0]; case['terminals']['walk'] = {'transition': 'portal_return', 'success_declared': True}
        relation = scenario_route_matrix(**data)['pairwise_robust_component_comparisons'][0]['case_relations'][0]
        self.assertIsNone(relation['relation']); self.assertEqual(relation['reason'], 'different_goal_or_terminal_declaration')
        data = payload(); data['scenarios'][0]['activation_declarations'] = {}
        row = scenario_route_matrix(**data)
        self.assertIsNone(row['route_summaries'][0]['closed_quantity_envelope'])
        self.assertIsNone(row['pairwise_robust_component_comparisons'][0]['declared_component_nonworse_across_all_cases'])

    def test_all_input_snapshots_outputs_and_branch_budgets_are_isolated(self):
        data = payload(); before = deepcopy(data); first = scenario_route_matrix(**data); second = scenario_route_matrix(**data)
        self.assertEqual(first, second); self.assertEqual(data, before)
        first['cases'][0]['scenario_input']['inventory'][0]['remaining_uses'] = 99
        self.assertEqual(first['cases'][0]['routes'][0]['resource_reference']['routes'][0]['movement_and_base_reference']['movement_reference']['inventory_reference_state'][0]['remaining_uses'], 0)
        self.assertNotEqual(first, second)

    def test_invalid_case_declarations_validate_even_when_missing_stock_blocks_every_item_plan(self):
        cases = [{'id': 'x', 'action_points': True, 'inventory': [], 'passive_items': []},
                 {'id': 'x', 'action_points': 1, 'inventory': [], 'passive_items': [], 'probability': .5},
                 {'id': 'x', 'action_points': 1, 'inventory': [], 'passive_items': [], 'residents': [{'node_id': 'missing'}]},
                 {'id': 'x', 'action_points': 1, 'inventory': [], 'passive_items': [], 'after_battle_declarations': {'grants': {'0': True}}},
                 {'id': 'x', 'action_points': 1, 'inventory': [], 'passive_items': [], 'terminals': {'grants': {'transition': 'main_region_advance', 'exit_node_type': 'BATTLE_BOSS', 'success_declared': True}}}]
        for case in cases:
            data = payload(); data['scenarios'] = [case]
            with self.subTest(case=case), self.assertRaises(ValueError): scenario_route_matrix(**data)
        data = payload(); data['scenarios'] *= 2
        with self.assertRaises(ValueError): scenario_route_matrix(**data)
        data = payload(); data['routes'][1]['steps'] = [{'mode': 'walking', 'target': 'g'}]
        with self.assertRaises(ValueError): scenario_route_matrix(**data)


if __name__ == '__main__': unittest.main()
