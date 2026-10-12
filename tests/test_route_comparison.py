from copy import deepcopy
import unittest

from rouge.route_comparison import compare_routes


def sample():
    graph = {'current_node': 's', 'nodes': [
        {'id': 's', 'row': 0, 'col': 0, 'base_node_type': 'EMPTY'},
        {'id': 'a', 'row': 0, 'col': 1, 'base_node_type': 'BATTLE_NORMAL',
         'completed_declared': True, 'occupied_declared': False,
         'other_blocked_declared': False},
        {'id': 'g', 'row': 0, 'col': 2, 'base_node_type': 'FINAL'},
        {'id': 'q', 'row': 1, 'col': 0, 'base_node_type': 'EMPTY'}],
        'edges': [['s', 'a'], ['a', 'g'], ['s', 'q'], ['q', 'a']]}
    fight = {'stage_id': 'ro6_n_1_1', 'battle_floor': 1,
             'entry_context': 'map_battle', 'special_region': False,
             'victory_declared': True}
    direct = {'id': 'direct', 'name': '短路声明', 'steps': [
        {'mode': 'walking', 'target': 'a', 'battle': fight},
        {'mode': 'walking', 'target': 'g'}]}
    detour = {'id': 'detour', 'name': '绕路声明', 'steps': [
        {'mode': 'walking', 'target': 'q'},
        {'mode': 'walking', 'target': 'a', 'battle': deepcopy(fight)},
        {'mode': 'walking', 'target': 'g'}]}
    return graph, [direct, detour]


class RouteComparisonTests(unittest.TestCase):
    def test_same_goal_component_dominance_and_resource_grants_are_independent_per_plan(self):
        graph, routes = sample()
        result = compare_routes(graph, routes, action_points=6)
        self.assertEqual(result['component_nondominated_candidates'], ['direct'])
        for row, cost in zip(result['routes'], (2, 3)):
            self.assertTrue(row['closed_declared_component_reference'])
            self.assertEqual(row['net_ap_consumption_reference'], cost)
            self.assertEqual(row['known_base_subtotal'],
                {'experience': 10, 'gold': {'minimum': 1, 'maximum': 1}})
            self.assertIsNone(row['actual_feasible'])
            self.assertIsNone(row['actual_final_resources'])
        self.assertEqual(result['routes'][1]['component_dominated_by'], ['direct'])
        self.assertIsNone(result['actual_best_route'])
        self.assertFalse(result['inventory_updated'])
        self.assertIsNone(result['probability'])

    def test_failed_or_zero_payment_prefix_does_not_admit_tail_rewards(self):
        graph, routes = sample()
        for ap in (0, 1):
            result = compare_routes(graph, routes, action_points=ap)
            self.assertFalse(result['component_nondominated_candidates'])
            for row in result['routes']:
                self.assertIsNone(row['conditional_base_total'])
                self.assertEqual(row['known_base_subtotal']['experience'], 0)
                self.assertEqual(len(row['battle_reward_rows']), 1)
                self.assertFalse(row['battle_reward_rows'][0]['admitted_to_known_base_subtotal'])
                self.assertIsNone(row['battle_reward_rows'][0]['actual_received'])

    def test_later_zero_boundary_preserves_known_prefix_but_masks_complete_reference(self):
        graph, routes = sample()
        row = compare_routes(graph, routes[:1], action_points=2)['routes'][0]
        self.assertEqual(row['known_base_subtotal']['experience'], 10)
        self.assertIsNone(row['conditional_base_total'])
        self.assertFalse(row['closed_declared_component_reference'])
        self.assertEqual(row['movement_reference']['stopped_reason'], 'zero_ap_callback_order_unverified')

    def test_unfunded_conditions_do_not_become_zero_cost_or_claimed_reward(self):
        graph, routes = sample()
        for ap in (None,):
            result = compare_routes(graph, routes, action_points=ap)
            self.assertFalse(result['component_nondominated_candidates'])
            self.assertTrue(all(row['conditional_base_total'] is None for row in result['routes']))
            self.assertTrue(all(row['net_ap_consumption_reference'] is None for row in result['routes']))
            self.assertTrue(all(p['component_dominates'] is None for p in result['pairwise_comparisons']))

    def test_exact_identity_and_victory_are_required_and_known_parts_stay_visible(self):
        graph, routes = sample()
        route = routes[0]
        route['steps'][0]['battle']['victory_declared'] = None
        row = compare_routes(graph, [route], action_points=6)['routes'][0]
        self.assertEqual(row['battle_reward_rows'][0]['base_reward_reference']['conditional_base_experience'], 10)
        self.assertEqual(row['known_base_subtotal']['experience'], 0)
        self.assertIsNone(row['conditional_base_total'])
        self.assertIn('victory_not_declared', row['unknown_or_failed_conditions'][0]['reasons'])
        del route['steps'][0]['battle']
        row = compare_routes(graph, [route], action_points=6)['routes'][0]
        self.assertIsNone(row['conditional_base_total'])
        self.assertIn('no_exact_current_or_declared_stage_identity', row['unknown_or_failed_conditions'][0]['reasons'])

    def test_duplicate_node_rewards_are_not_recollected(self):
        graph, routes = sample()
        route = routes[0]
        route['steps'].insert(1, {'mode': 'walking', 'target': 's'})
        route['steps'].insert(2, deepcopy(route['steps'][0]))
        row = compare_routes(graph, [route], action_points=8)['routes'][0]
        self.assertEqual(row['known_base_subtotal']['experience'], 10)
        self.assertEqual(len(row['battle_reward_rows']), 2)
        self.assertFalse(row['battle_reward_rows'][1]['admitted_to_known_base_subtotal'])
        self.assertIn('repeated_battle_reward_eligibility_unknown',
                      row['battle_reward_rows'][1]['unknown_or_failed_conditions'])
        self.assertIsNone(row['conditional_base_total'])

    def test_different_goals_and_tied_routes_are_not_dominated(self):
        graph, routes = sample()
        routes[1] = deepcopy(routes[0]); routes[1]['id'] = 'tie'
        result = compare_routes(graph, routes, action_points=6)
        self.assertEqual(result['component_nondominated_candidates'], ['direct', 'tie'])
        self.assertTrue(all(p['component_dominates'] is False for p in result['pairwise_comparisons']))
        routes[1]['steps'].pop()
        result = compare_routes(graph, routes, action_points=6)
        self.assertTrue(all(p['unresolved_reason'] == 'different_declared_goal'
                            for p in result['pairwise_comparisons']))
        self.assertTrue(all(p['component_dominates'] is None for p in result['pairwise_comparisons']))

    def test_stopped_tail_is_still_schema_and_source_validated(self):
        graph, routes = sample()
        routes[0]['steps'][0]['battle']['stage_id'] = 'unlisted'
        with self.assertRaises(ValueError): compare_routes(graph, routes, action_points=0)

    def test_interval_gold_does_not_use_midpoint_or_worst_to_worst_dominance(self):
        graph, routes = sample()
        for route in routes:
            fight=next(step['battle'] for step in route['steps'] if 'battle' in step)
            fight.update(stage_id='ro6_t_1', battle_floor=None, entry_context='event_battle')
        result=compare_routes(graph,routes,action_points=6)
        self.assertEqual(result['component_nondominated_candidates'],['direct','detour'])
        for row in result['routes']:
            self.assertEqual(row['known_base_subtotal']['gold'],{'minimum':2,'maximum':3})
        self.assertTrue(all(row['component_dominates'] is False for row in result['pairwise_comparisons']))

    def test_first_light_grant_changes_net_cost_without_changing_base_payment(self):
        graph,routes=sample();node=graph['nodes'][3]
        node['base_node_type']='LIGHT'
        node['light_arrival_declaration']={'first_entry':True,'reward_received':False}
        before=deepcopy(graph);result=compare_routes(graph,routes,action_points=6)
        self.assertEqual([r['base_cost_reference'] for r in result['routes']],[2,3])
        self.assertEqual([r['net_ap_consumption_reference'] for r in result['routes']],[2,2])
        self.assertEqual(result['component_nondominated_candidates'],['direct','detour'])
        self.assertEqual(graph,before)
        self.assertTrue(graph['nodes'][3]['light_arrival_declaration']['first_entry'])

    def test_unwon_battle_and_shop_are_not_automatic_success_or_combat_reward(self):
        graph,routes=sample();routes[0]['steps'][0]['battle']['victory_declared']=False
        row=compare_routes(graph,routes[:1],action_points=6)['routes'][0]
        self.assertEqual(row['known_base_subtotal']['experience'],0)
        self.assertIsNone(row['conditional_base_total'])
        self.assertIn('declared_battle_not_won',row['unknown_or_failed_conditions'][0]['reasons'])
        graph['nodes'][1]['base_node_type']='BATTLE_SHOP';del routes[0]['steps'][0]['battle']
        row=compare_routes(graph,routes[:1],action_points=6)['routes'][0]
        self.assertTrue(row['closed_declared_component_reference'])
        self.assertEqual(row['battle_reward_rows'],[])
        self.assertIsNone(row['actual_final_resources'])

    def test_unknown_node_type_does_not_become_noncombat_zero_reward(self):
        graph, routes = sample()
        del graph['nodes'][1]['base_node_type']; del routes[0]['steps'][0]['battle']
        row = compare_routes(graph, routes[:1], action_points=6)['routes'][0]
        self.assertIsNone(row['conditional_base_total'])
        self.assertTrue(row['unknown_or_failed_conditions'])

    def test_caller_inputs_and_returns_do_not_share_mutable_state(self):
        graph, routes = sample(); before = deepcopy((graph, routes))
        result = compare_routes(graph, routes, action_points=6)
        self.assertEqual((graph, routes), before)
        result['routes'][0]['declared_steps'][0]['battle']['stage_id'] = 'x'
        result['routes'][0]['movement_reference']['steps'][0]['target'] = 'x'
        self.assertEqual((graph, routes), before)

    def test_bounded_and_strict_plan_input(self):
        graph, routes = sample()
        bad = [None, [], routes * 11, [routes[0], routes[0]],
               [{'id': 'a', 'steps': []}], [{'id': 'a', 'steps': routes[0]['steps'] * 51}],
               [{'id': True, 'steps': routes[0]['steps']}],
               [{**routes[0], 'probability': .5}],
               [{**routes[0], 'steps': [{'mode': 'walking', 'target': 'a', 'battle': None}]}],
               [{**routes[0], 'steps': [{'mode': 'walking', 'target': 'a', 'rewards': 10}]}],
               [{**routes[0], 'steps': [{'mode': 'walking', 'target': 'a', 'battle': {'target': 'g'}}]}]]
        for value in bad:
            with self.subTest(value=str(value)[:100]), self.assertRaises(ValueError):
                compare_routes(graph, value, action_points=6)
