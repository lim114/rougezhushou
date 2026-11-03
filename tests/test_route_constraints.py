from copy import deepcopy
import unittest

from rouge.route_constraints import constrained_routes


def graph():
    return {'current_node': 's', 'nodes': [
        {'id': key, 'row': row, 'col': col, 'base_node_type': 'EMPTY'}
        for key, row, col in [('s', 0, 0), ('a', 0, 1), ('b', 1, 0), ('c', 1, 1), ('g', 0, 2)]],
        'edges': [['s', 'a'], ['a', 'g'], ['s', 'b'], ['b', 'c'], ['c', 'g'], ['a', 'c']]}


def paths(result):
    return [[step['target'] for step in plan['steps']] for plan in result['plans']]


class RouteConstraintsTests(unittest.TestCase):
    def test_required_visits_are_search_state_not_filter_on_capped_unconstrained_results(self):
        row = constrained_routes(graph(), 'g', action_points=8, required_nodes=['b'], max_results=1)
        self.assertEqual(paths(row), [['b', 'c', 'g']])
        self.assertTrue(any(item['reason'] == 'declared_goal_prerequisites_missing' for item in row['policy_exclusions']))
        self.assertEqual(row['comparison']['routes'][0]['net_ap_consumption_reference'], 3)
        self.assertEqual(row['policy']['required_nodes'], ['b'])

    def test_avoid_and_order_prune_paths_before_they_consume_the_result_limit(self):
        row = constrained_routes(graph(), 'g', action_points=8, avoid_nodes=['a'], checkpoints=['b', 'c'])
        self.assertEqual(paths(row), [['b', 'c', 'g']])
        self.assertTrue(any(item['reason'] == 'declared_avoided_node' for item in row['policy_exclusions']))
        row = constrained_routes(graph(), 'g', action_points=8, checkpoints=['c', 'a'])
        self.assertEqual(paths(row), [['b', 'c', 'a', 'g']])
        self.assertTrue(any(item['reason'] == 'declared_checkpoint_order_mismatch' for item in row['policy_exclusions']))
        self.assertTrue(row['declared_policy_search_complete'])

    def test_start_and_final_checkpoint_are_satisfied_at_their_declared_positions(self):
        row = constrained_routes(graph(), 'g', action_points=8, required_nodes=['s', 'b', 'g'], checkpoints=['s', 'b', 'g'])
        self.assertTrue(row['plans'])
        self.assertTrue(all(path[0] == 'b' and path[-1] == 'g' for path in paths(row)))

    def test_unknown_qualification_preserves_frontier_and_cannot_fund_descendants(self):
        row = constrained_routes(graph(), 'g', action_points=8, required_nodes=['b'], avoid_nodes=['a'],
                                 qualifications={'c': {'matches': None, 'reason': '入口未确认'}})
        self.assertFalse(row['plans']); self.assertIsNone(row['comparison'])
        unknown = [item for item in row['frontier'] if item['reason'] == 'declared_entry_qualification_unknown']
        self.assertEqual([step['target'] for step in unknown[0]['steps']], ['b', 'c'])
        self.assertEqual(unknown[0]['qualification_declaration']['reason'], '入口未确认')
        self.assertTrue(unknown[0]['movement_reference']['complete_declared_conditions'])
        self.assertIsNone(unknown[0]['actual_continuation'])
        self.assertFalse(row['declared_policy_search_complete'])
        self.assertFalse(any(item['node_id'] == 'g' and len(item['steps']) > 2 for item in row['frontier']))

    def test_goal_unknown_or_false_is_never_accepted_as_completed_eligible_plan(self):
        for state in [False, None]:
            row = constrained_routes(graph(), 'g', action_points=8, qualifications={'g': {'matches': state}})
            self.assertFalse(row['plans']); self.assertIsNone(row['comparison'])
            records = row['frontier'] if state is None else row['policy_exclusions']
            expected = 'declared_entry_qualification_unknown' if state is None else 'declared_entry_qualification_failed'
            self.assertTrue(any(item['node_id'] == 'g' and item['reason'] == expected for item in records))
        row = constrained_routes(graph(), 'g', action_points=8, qualifications={'g': {'matches': True}})
        self.assertTrue(row['plans']); self.assertIsNone(row['actual_goal_reachable'])

    def test_zero_or_unknown_ap_and_random_item_stop_independent_dependency_chains(self):
        for ap in [None, 0, 1]:
            row = constrained_routes(graph(), 'g', action_points=ap)
            self.assertFalse(row['plans']); self.assertTrue(row['frontier'])
        row = constrained_routes(graph(), 'g', action_points=8, inventory=[
            {'instance_id': 'random', 'item_id': 'rogue_6_scrap_M_07', 'remaining_uses': 1}])
        self.assertTrue(any(item['steps'][-1]['mode'] == 'random' for item in row['frontier']))
        self.assertFalse(any(step['mode'] == 'random' for plan in row['plans'] for step in plan['steps']))

    def test_light_ap_unknown_and_independent_first_entry_declaration(self):
        data = graph(); data['nodes'][2]['base_node_type'] = 'LIGHT'
        row = constrained_routes(data, 'g', action_points=8, required_nodes=['b'])
        self.assertFalse(row['plans']); self.assertTrue(any(item['reason'] == 'node_arrival_ap_condition_unknown' for item in row['frontier']))
        data['nodes'][2]['light_arrival_declaration'] = {'first_entry': True, 'reward_received': False}
        row = constrained_routes(data, 'g', action_points=8, required_nodes=['b'], avoid_nodes=['a'])
        self.assertEqual(paths(row), [['b', 'c', 'g']])
        self.assertEqual(row['comparison']['routes'][0]['net_ap_consumption_reference'], 2)
        self.assertFalse(data['nodes'][2]['light_arrival_declaration']['reward_received'])

    def test_item_instance_ledgers_remain_branch_local_and_avoid_applies_to_entry_only(self):
        stock = [{'instance_id': 'jet', 'item_id': 'rogue_6_scrap_M_08', 'remaining_uses': 1}]
        before = deepcopy(stock)
        row = constrained_routes(graph(), 'g', action_points=8, avoid_nodes=['a'], required_nodes=['b'], inventory=stock)
        self.assertTrue(row['plans'])
        self.assertTrue(any(step['mode'] == 'jet' for plan in row['plans'] for step in plan['steps']))
        self.assertTrue(all(sum(step['mode'] == 'jet' for step in plan['steps']) <= 1 for plan in row['plans']))
        self.assertFalse(any(step['target'] == 'a' for plan in row['plans'] for step in plan['steps']))
        self.assertEqual(stock, before); self.assertFalse(row['inventory_updated'])

    def test_battle_rewards_require_independent_identity_and_victory_declarations(self):
        data = graph(); data['nodes'][2]['base_node_type'] = 'BATTLE_NORMAL'
        arguments = {'required_nodes': ['b'], 'avoid_nodes': ['a'], 'action_points': 8}
        unknown = constrained_routes(data, 'g', **arguments)
        self.assertIsNone(unknown['comparison']['routes'][0]['conditional_base_total'])
        battle = {'stage_id': 'ro6_n_1_1', 'battle_floor': 1, 'entry_context': 'map_battle',
                  'special_region': False, 'victory_declared': True}
        known = constrained_routes(data, 'g', battle_declarations={'b': battle}, **arguments)
        self.assertEqual(known['comparison']['routes'][0]['conditional_base_total']['experience'], 10)
        battle['victory_declared'] = False
        failed = constrained_routes(data, 'g', battle_declarations={'b': battle}, **arguments)
        self.assertEqual(failed['comparison']['routes'][0]['known_base_subtotal']['experience'], 0)
        self.assertIsNone(failed['comparison']['routes'][0]['conditional_base_total'])
        self.assertNotIn('completed_declared', data['nodes'][2])

    def test_step_lower_bound_and_depth_frontiers_preserve_remaining_requirements(self):
        row = constrained_routes(graph(), 'g', action_points=8, required_nodes=['b', 'c'], max_steps=2)
        self.assertFalse(row['plans']); self.assertEqual(row['examined_transitions'], 0)
        self.assertEqual(row['frontier'][0]['reason'], 'remaining_constraints_exceed_step_budget')
        self.assertEqual(row['frontier'][0]['remaining_required_nodes'], ['b', 'c'])
        self.assertFalse(row['declared_policy_search_complete'])
        row = constrained_routes(graph(), 'g', action_points=8, max_steps=1)
        self.assertTrue(any(item['reason'] == 'depth_limit' for item in row['frontier']))

    def test_transition_and_result_caps_preserve_pending_prefixes_and_siblings(self):
        row = constrained_routes(graph(), 'g', action_points=8, max_transitions=1)
        self.assertEqual(row['examined_transitions'], 1)
        self.assertEqual(row['limit_reason'], 'transition_limit')
        self.assertGreater(row['pending_sibling_options_at_limit'] + row['pending_prefixes_at_limit'], 0)
        row = constrained_routes(graph(), 'g', action_points=8, max_results=1)
        self.assertEqual(len(row['plans']), 1)
        self.assertEqual(row['limit_reason'], 'result_limit')
        self.assertFalse(row['declared_policy_search_complete'])
        self.assertFalse(row['all_actual_routes_enumerated']); self.assertIsNone(row['probability'])

    def test_inputs_and_nested_results_are_isolated_and_deterministic(self):
        data = graph(); before = deepcopy(data)
        declarations = {'c': {'matches': True, 'reason': '独立声明'}}; original = deepcopy(declarations)
        first = constrained_routes(data, 'g', action_points=8, qualifications=declarations)
        second = constrained_routes(data, 'g', action_points=8, qualifications=declarations)
        self.assertEqual(first, second); self.assertEqual(data, before); self.assertEqual(declarations, original)
        first['policy']['qualifications']['c']['reason'] = 'mutation'
        self.assertNotEqual(first, second)

    def test_invalid_policy_and_qualification_inputs_are_rejected_even_before_reachability(self):
        cases = [{'required_nodes': ['missing']}, {'avoid_nodes': ['s']}, {'avoid_nodes': ['g']},
                 {'required_nodes': ['a'], 'avoid_nodes': ['a']}, {'checkpoints': ['g', 'b']},
                 {'checkpoints': ['b', 's']}, {'checkpoints': ['b', 'b']},
                 {'required_nodes': 'b'}, {'qualifications': {'c': {'matches': 1}}},
                 {'qualifications': {'c': {'matches': True, 'effect': 100}}},
                 {'qualifications': {'missing': {'matches': None}}},
                 {'qualifications': {'c': {'reason': 'missing status'}}},
                 {'qualifications': {'c': {'matches': None, 'reason': []}}}]
        for fields in cases:
            with self.subTest(fields=fields), self.assertRaises(ValueError):
                constrained_routes(graph(), 'g', action_points=0, **fields)
        with self.assertRaises(ValueError):
            constrained_routes(graph(), 'g', battle_declarations={'b': {'stage_id': 'not-a-stage'}}, action_points=0)
        for field in ['max_steps', 'max_results', 'max_transitions']:
            for value in [0, True, 1.5, 1001]:
                with self.assertRaises(ValueError):
                    constrained_routes(graph(), 'g', **{field: value})


if __name__ == '__main__':
    unittest.main()
