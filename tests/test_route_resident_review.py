from copy import deepcopy
import unittest

from rouge.route_resident_review import review_resident_routes


def graph():
    return {'current_node': 's', 'zone_id': 'zone_2', 'template_id': 'public-resident-review',
            'nodes': [{'id': key, 'row': row, 'col': col, 'base_node_type': kind}
                      for key, row, col, kind in [('s', 0, 0, 'EMPTY'), ('a', 0, 1, 'EMPTY'),
                          ('b', 1, 0, 'EMPTY'), ('g', 1, 1, 'FINAL'),
                          ('r', 0, 2, 'EMPTY'), ('p', 1, 2, 'BATTLE_SAVAGE')]],
            'edges': [['s', 'a'], ['a', 'g'], ['s', 'b'], ['b', 'g'], ['r', 'a'], ['r', 'p']]}


def plans():
    return [{'id': 'a-route', 'name': '经甲路径', 'steps': [{'mode': 'walking', 'target': 'a'}, {'mode': 'walking', 'target': 'g'}]},
            {'id': 'b-route', 'name': '经乙路径', 'steps': [{'mode': 'walking', 'target': 'b'}, {'mode': 'walking', 'target': 'g'}]}]


class RouteResidentReviewTests(unittest.TestCase):
    def test_pre_entry_and_post_move_candidates_are_distinct_and_source_exclusions_retained(self):
        row = review_resident_routes(graph(), plans(), [{'id': 'r1', 'node_id': 'r'}], action_points=8)
        first = row['routes'][0]['phase_rows'][0]
        self.assertEqual(first['pre_entry_reference']['possible_occupied_union'], ['r'])
        self.assertFalse(first['pre_entry_reference']['target_candidate_overlap'])
        self.assertEqual(first['post_move_reference']['possible_occupied_union'], ['a'])
        self.assertTrue(first['post_move_reference']['target_candidate_overlap'])
        navigation = first['resident_navigation_references'][0]
        self.assertEqual(navigation['source_excluded_transitions'][0]['to'], 'p')
        self.assertIsNone(first['actual_collision_or_blockage']); self.assertIsNone(first['actual_safe'])
        self.assertFalse(row['move_entry_battle_order_verified'])

    def test_candidate_overlap_policy_is_explicit_and_retains_unknown_actual_safety(self):
        all_rows = review_resident_routes(graph(), plans(), [{'node_id': 'r'}], action_points=8)
        self.assertEqual(all_rows['policy_retained_route_ids'], ['a-route', 'b-route'])
        filtered = review_resident_routes(graph(), plans(), [{'node_id': 'r'}], action_points=8, risk_policy='avoid_candidate_overlap')
        self.assertEqual(filtered['policy_excluded_route_ids'], ['a-route'])
        self.assertEqual(filtered['policy_retained_route_ids'], ['b-route'])
        self.assertEqual(filtered['routes'][1]['candidate_overlap_steps'], [])
        self.assertIsNone(filtered['routes'][1]['actual_safe'])
        self.assertIsNone(filtered['actual_best_route']); self.assertIsNone(filtered['actual_failure_probability'])

    def test_no_neighbor_fallback_stays_unknown_on_every_later_step(self):
        data = graph(); data['edges'].remove(['r', 'a'])
        row = review_resident_routes(data, plans(), [{'id': 'r1', 'node_id': 'r'}], action_points=8)
        phases = row['routes'][0]['phase_rows']
        self.assertEqual(phases[0]['post_move_reference']['possible_occupied_union'], [])
        self.assertEqual(phases[0]['post_move_reference']['status'], 'navigation_position_unknown')
        self.assertTrue(phases[0]['resident_navigation_references'][0]['unresolved_fallbacks'])
        self.assertEqual(phases[1]['pre_entry_reference']['position_unknown_residents'], ['r1'])
        self.assertEqual(phases[1]['post_move_reference']['status'], 'navigation_position_unknown')
        self.assertTrue(phases[1]['resident_navigation_references'][0]['prior_position_unknown'])
        self.assertEqual(row['routes'][0]['navigation_unknown_steps'], [1, 2])

    def test_one_fallback_branch_does_not_disappear_when_another_branch_has_candidates(self):
        data = graph(); data['nodes'][4]['base_node_type'] = 'FINAL'
        data['edges'] = [['s', 'a'], ['a', 'g'], ['s', 'b'], ['b', 'g'], ['r', 'a'], ['r', 'p']]
        data['nodes'][5]['base_node_type'] = 'EMPTY'
        # r -> a/p; a has s admissible; p has only r, which is source-excluded FINAL.
        row = review_resident_routes(data, plans(), [{'id': 'r1', 'node_id': 'r'}], action_points=8)
        second = row['routes'][0]['phase_rows'][1]
        self.assertIn('s', second['post_move_reference']['possible_occupied_union'])
        self.assertEqual(second['post_move_reference']['position_unknown_residents'], ['r1'])
        self.assertEqual(second['resident_navigation_references'][0]['unresolved_fallbacks'][0]['from'], 'p')

    def test_multiple_residents_are_independent_candidate_unions_not_joint_collision_resolution(self):
        row = review_resident_routes(graph(), plans(), [{'id': 'one', 'node_id': 'r'}, {'id': 'two', 'node_id': 'a'}], action_points=8)
        first = row['routes'][0]['phase_rows'][0]
        self.assertTrue(first['pre_entry_reference']['target_candidate_overlap'])
        self.assertEqual(len(first['resident_navigation_references']), 2)
        self.assertFalse(row['joint_collision_resolution_verified'])
        self.assertTrue(all(candidate['probability'] is None for resident in first['resident_navigation_references'] for candidate in resident['navigation_candidates']))

    def test_payment_zero_or_unknown_ap_disables_post_move_and_tail_instead_of_declaring_safe(self):
        for ap in [1, None, 0]:
            row = review_resident_routes(graph(), plans(), [{'node_id': 'r'}], action_points=ap)
            phases = row['routes'][0]['phase_rows']
            self.assertEqual(row['routes'][0]['movement_stop_step'], 1)
            self.assertIsNotNone(phases[0]['pre_entry_reference'])
            self.assertIsNone(phases[0]['post_move_reference'])
            self.assertEqual(phases[1]['status'], 'not_evaluated_after_movement_stop')
            self.assertIsNone(phases[1]['pre_entry_reference']); self.assertIsNone(phases[1]['actual_safe'])

    def test_random_item_and_unknown_light_arrival_do_not_authorize_resident_tick(self):
        data = graph(); routes = [{'id': 'random', 'steps': [{'mode': 'random', 'target': 'a'}, {'mode': 'walking', 'target': 'g'}]}]
        row = review_resident_routes(data, routes, [{'node_id': 'r'}], action_points=8,
            inventory=[{'instance_id': 'random', 'item_id': 'rogue_6_scrap_M_07', 'remaining_uses': 1}])
        self.assertEqual(row['routes'][0]['movement_stop_step'], 1)
        data['nodes'][1]['base_node_type'] = 'LIGHT'
        row = review_resident_routes(data, plans(), [{'node_id': 'r'}], action_points=8)
        self.assertEqual(row['routes'][0]['movement_stop_step'], 1)
        self.assertIsNone(row['routes'][0]['phase_rows'][0]['post_move_reference'])

    def test_explicit_post_victory_eviction_is_separate_conditional_phase_not_inferred_from_arrival(self):
        data = graph(); data['edges'].append(['s', 'p']); data['edges'].append(['p', 'g'])
        routes = [{'id': 'post', 'steps': [{'mode': 'walking', 'target': 'p'}, {'mode': 'walking', 'target': 'g'}]}]
        before = review_resident_routes(data, routes, [{'node_id': 'r'}], action_points=8)
        self.assertFalse(before['routes'][0]['conditional_post_eviction_steps'])
        self.assertIsNone(before['routes'][0]['phase_rows'][0]['after_declared_post_victory_reference'])
        after = review_resident_routes(data, routes, [{'node_id': 'r'}], action_points=8, resident_post_victories={'post': [1]})
        first, second = after['routes'][0]['phase_rows']
        self.assertEqual(first['post_move_reference']['possible_occupied_union'], ['a'])
        eviction = first['after_declared_post_victory_reference']
        self.assertTrue(eviction['all_residents_evicted_if_declared_post_victory'])
        self.assertEqual(eviction['possible_occupied_union'], []); self.assertIsNone(eviction['actual_eviction'])
        self.assertEqual(second['pre_entry_reference']['possible_occupied_union'], [])
        self.assertEqual(after['routes'][0]['conditional_post_eviction_steps'], [1])
        self.assertNotIn('completed_declared', data['nodes'][5])

    def test_blocked_arrival_cannot_execute_a_declared_future_post_eviction(self):
        data = graph(); data['edges'].extend([['s', 'p'], ['p', 'g']])
        routes = [{'id': 'post', 'steps': [{'mode': 'walking', 'target': 'p'}, {'mode': 'walking', 'target': 'g'}]}]
        row = review_resident_routes(data, routes, [{'node_id': 'r'}], action_points=1, resident_post_victories={'post': [1]})
        self.assertTrue(row['routes'][0]['phase_rows'][0]['resident_post_victory_declared'])
        self.assertIsNone(row['routes'][0]['phase_rows'][0]['after_declared_post_victory_reference'])
        self.assertEqual(row['routes'][0]['conditional_post_eviction_steps'], [])

    def test_navigation_unknown_can_clear_only_in_separate_explicit_post_victory_phase(self):
        data = graph(); data['edges'].remove(['r', 'a']); data['edges'].extend([['a', 'p'], ['p', 'g']])
        routes = [{'id': 'post', 'steps': [{'mode': 'walking', 'target': 'a'}, {'mode': 'walking', 'target': 'p'}, {'mode': 'walking', 'target': 'g'}]}]
        row = review_resident_routes(data, routes, [{'id': 'r1', 'node_id': 'r'}], action_points=8, resident_post_victories={'post': [2]})
        first, victory, last = row['routes'][0]['phase_rows']
        self.assertEqual(first['post_move_reference']['position_unknown_residents'], ['r1'])
        self.assertEqual(victory['post_move_reference']['position_unknown_residents'], ['r1'])
        self.assertEqual(victory['after_declared_post_victory_reference']['position_unknown_residents'], [])
        self.assertEqual(last['pre_entry_reference']['position_unknown_residents'], [])
        self.assertIsNone(last['actual_safe'])

    def test_review_never_reduces_base_reward_or_ap_reference_from_possible_overlap(self):
        row = review_resident_routes(graph(), plans(), [{'node_id': 'r'}], action_points=8)
        comparison = row['movement_and_base_comparison']['routes']
        self.assertTrue(row['routes'][0]['candidate_overlap_steps'])
        self.assertEqual(comparison[0]['net_ap_consumption_reference'], 2)
        self.assertEqual(comparison[0]['known_base_subtotal']['experience'], 0)
        self.assertEqual(comparison[0]['known_base_subtotal'], comparison[1]['known_base_subtotal'])

    def test_explicit_zero_snapshot_is_distinct_from_invalid_unknown_snapshot(self):
        row = review_resident_routes(graph(), plans(), [], action_points=8)
        self.assertEqual(row['residents_snapshot_declaration'], [])
        self.assertTrue(all(not route['candidate_overlap_steps'] for route in row['routes']))
        self.assertTrue(all(route['actual_safe'] is None for route in row['routes']))
        with self.assertRaises(ValueError):
            review_resident_routes(graph(), plans(), None, action_points=8)

    def test_input_isolation_and_invalid_route_snapshot_and_eviction_boundaries(self):
        data, routes, residents = graph(), plans(), [{'node_id': 'r'}]
        originals = deepcopy((data, routes, residents))
        first = review_resident_routes(data, routes, residents, action_points=8)
        second = review_resident_routes(data, routes, residents, action_points=8)
        self.assertEqual(first, second); self.assertEqual((data, routes, residents), originals)
        first['routes'][0]['phase_rows'][0]['pre_entry_reference']['possible_occupied_union'].append('mutation')
        self.assertNotEqual(first, second)
        for declarations in [None, [{'node_id': 'missing'}], [{'node_id': 'r', 'extra': 1}], [{'id': 'x', 'node_id': 'r'}, {'id': 'x', 'node_id': 'a'}], [{'node_id': 'r'}] * 4]:
            with self.assertRaises(ValueError):
                review_resident_routes(data, routes, declarations, action_points=8)
        for events in [{'a-route': [1]}, {'missing': [1]}, {'a-route': [True]}, {'a-route': [0]}, {'a-route': [1, 1]}]:
            with self.assertRaises(ValueError):
                review_resident_routes(data, routes, residents, resident_post_victories=events)
        with self.assertRaises(ValueError):
            review_resident_routes(data, [{'id': 'macro', 'steps': [{'mode': 'walking', 'target': 'g'}]}], residents, action_points=8)
        with self.assertRaises(ValueError):
            review_resident_routes(data, [{'id': 'too-long', 'steps': routes[0]['steps'] * 6}], residents, action_points=8)


if __name__ == '__main__':
    unittest.main()
