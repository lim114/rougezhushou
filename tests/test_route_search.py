from copy import deepcopy
import unittest
from rouge.route_search import search_routes


def graph():
    return {'current_node': 's', 'nodes': [
        {'id': key, 'row': r, 'col': c, 'base_node_type': 'EMPTY'}
        for key, r, c in [('s', 0, 0), ('a', 0, 1), ('b', 1, 0), ('g', 1, 1)]],
        'edges': [['s', 'a'], ['a', 'g'], ['s', 'b'], ['b', 'g']]}


class RouteSearchTests(unittest.TestCase):
    def test_generates_both_adjacent_simple_routes_and_compares_declared_components(self):
        result = search_routes(graph(), 'g', action_points=6)
        self.assertEqual([[s['target'] for s in p['steps']] for p in result['plans']],
                         [['a', 'g'], ['b', 'g']])
        self.assertTrue(result['bounded_queue_exhausted'])
        self.assertEqual(result['comparison']['component_nondominated_candidates'], ['plan:1', 'plan:2'])
        self.assertTrue(all(p['net_ap_consumption_reference'] == 2 for p in result['comparison']['routes']))
        self.assertIsNone(result['actual_best_route']);self.assertIsNone(result['actual_goal_reachable'])
        self.assertFalse(result['all_actual_routes_enumerated']);self.assertIsNone(result['probability'])

    def test_limits_are_truthful_and_no_return_to_visited_start(self):
        result = search_routes(graph(), 'g', action_points=6, max_steps=1)
        self.assertFalse(result['plans']);self.assertEqual(result['depth_limited_prefixes'], 2)
        self.assertTrue(all(r['reason'] == 'depth_limit' for r in result['frontier']))
        for limit, value in [('max_results', 1), ('max_transitions', 1)]:
            row = search_routes(graph(), 'g', action_points=6, **{limit: value})
            self.assertIsNotNone(row['limit_reason'])
            self.assertFalse(row['all_actual_routes_enumerated'])
        result = search_routes(graph(), 'g', action_points=6)
        self.assertFalse(any(s['target'] == 's' for p in result['plans'] for s in p['steps']))

    def test_zero_ap_unknown_ap_and_light_arrival_stop_without_funding_future(self):
        for ap in (None, 0, 1):
            result = search_routes(graph(), 'g', action_points=ap)
            self.assertFalse(result['plans']);self.assertTrue(result['frontier'])
            self.assertTrue(all(r['actual_continuation'] is None for r in result['frontier']))
        g = graph();g['nodes'][1]['base_node_type'] = 'LIGHT'
        result = search_routes(g, 'g', action_points=3)
        self.assertEqual(len(result['plans']), 1)
        self.assertTrue(any(r['reason'] == 'node_arrival_ap_condition_unknown' for r in result['frontier']))
        g['nodes'][1]['light_arrival_declaration'] = {'first_entry': True, 'reward_received': False}
        result = search_routes(g, 'g', action_points=3)
        self.assertEqual(len(result['plans']), 2)
        self.assertEqual(result['comparison']['routes'][0]['net_ap_consumption_reference'], 1)
        self.assertFalse(g['nodes'][1]['light_arrival_declaration']['reward_received'])

    def test_explicit_battle_source_and_victory_are_not_invented_from_traversal(self):
        g = graph();g['nodes'][1]['base_node_type'] = 'BATTLE_NORMAL'
        result = search_routes(g, 'g', action_points=6)
        first = result['comparison']['routes'][0]
        self.assertIsNone(first['conditional_base_total'])
        self.assertEqual(first['known_base_subtotal']['experience'], 0)
        battle = {'stage_id': 'ro6_n_1_1', 'battle_floor': 1, 'entry_context': 'map_battle',
                  'special_region': False, 'victory_declared': True}
        result = search_routes(g, 'g', action_points=6, battle_declarations={'a': battle})
        first = result['comparison']['routes'][0]
        self.assertEqual(first['known_base_subtotal']['experience'], 10)
        self.assertTrue(first['closed_declared_component_reference'])
        self.assertNotIn('completed_declared', g['nodes'][1])
        with self.assertRaises(ValueError):
            search_routes(g, 'g', action_points=0, battle_declarations={'a': {'stage_id': 'wrong'}})

    def test_declared_item_instances_are_not_shared_across_generated_branches(self):
        stock = [{'instance_id': 'jet', 'item_id': 'rogue_6_scrap_M_08', 'remaining_uses': 1}]
        before = deepcopy(stock)
        result = search_routes(graph(), 'g', action_points=6, inventory=stock)
        jets = [p for p in result['plans'] if p['steps'][0]['mode'] == 'jet']
        self.assertTrue(jets)
        self.assertTrue(all(sum(s['mode'] == 'jet' for s in p['steps']) <= 1 for p in result['plans']))
        self.assertEqual(stock, before);self.assertFalse(result['inventory_updated'])

    def test_random_item_destinations_remain_unresolved_frontier_not_successful_chain(self):
        stock = [{'instance_id': 'random', 'item_id': 'rogue_6_scrap_M_07', 'remaining_uses': 1}]
        result = search_routes(graph(), 'g', action_points=6, inventory=stock)
        random_frontier = [r for r in result['frontier'] if r['steps'][-1]['mode'] == 'random']
        self.assertTrue(random_frontier)
        self.assertTrue(all(r['reason'] == 'eligibility_or_inventory_condition_unknown' for r in random_frontier))
        self.assertFalse(any(any(s['mode'] == 'random' for s in p['steps'][:-1]) for p in result['plans']))
        self.assertTrue(all(r['conditional_base_total'] is None for r in result['comparison']['routes']
                            if r['declared_steps'][-1]['mode'] == 'random'))

    def test_known_exhausted_instances_excluded_and_unknown_uses_preserved(self):
        for count in (0, None):
            result = search_routes(graph(), 'g', action_points=6,
                inventory=[{'instance_id': 'jet', 'item_id': 'rogue_6_scrap_M_08', 'remaining_uses': count}])
            if count == 0:
                self.assertFalse(any(s['mode'] == 'jet' for p in result['plans'] for s in p['steps']))
                self.assertGreater(result['known_type_or_use_exclusions'], 0)
            else:
                self.assertTrue(any(r['steps'][-1]['mode'] == 'jet' for r in result['frontier']))

    def test_inputs_unchanged_and_source_graph_and_bounds_validated(self):
        g = graph();before = deepcopy(g)
        a = search_routes(g, 'g', action_points=6);b = search_routes(g, 'g', action_points=6)
        self.assertEqual(a, b);self.assertEqual(g, before)
        a['plans'][0]['steps'][0]['target'] = 'mutation'
        self.assertNotEqual(a, b)
        for field in ('max_steps', 'max_results', 'max_transitions'):
            for value in (0, True, 1.5, 1001):
                with self.assertRaises(ValueError):search_routes(g, 'g', **{field:value})
        with self.assertRaises(ValueError):search_routes(g, 's')
        with self.assertRaises(ValueError):search_routes(g, 'unknown')
        g['edges'].append(['s','s'])
        with self.assertRaises(ValueError):search_routes(g, 'g')

if __name__ == '__main__':unittest.main()
