from copy import deepcopy
import unittest
from rouge.route_continuation import continue_route_plan


def payload():
    graph = {'current_node': 's', 'map_instance_id': 'public-map-instance-1', 'zone_id': 'zone_1', 'template_id': 'public-continuation',
             'nodes': [{'id': key, 'row': row, 'col': col, 'base_node_type': kind} for key, row, col, kind in [
                 ('s', 0, 0, 'EMPTY'), ('a', 0, 1, 'BATTLE_NORMAL'), ('b', 1, 0, 'EMPTY'), ('c', 1, 1, 'EMPTY'), ('g', 0, 2, 'FINAL')]],
             'edges': [['s', 'a'], ['a', 'g'], ['s', 'b'], ['b', 'c'], ['a', 'c'], ['c', 'g']]}
    before = {'graph': graph, 'action_points': 6, 'inventory': [{'instance_id': 'jet', 'item_id': 'rogue_6_scrap_M_08', 'remaining_uses': 1}], 'passive_items': []}
    after = deepcopy(before); after['graph']['current_node'] = 'a'; after['action_points'] = 4
    return {'before': before, 'after': after, 'plan': {'id': 'original', 'steps': [{'mode': 'walking', 'target': 'a'}, {'mode': 'walking', 'target': 'g'}]},
            'progress': [{'step': 1, 'target': 'a', 'mode': 'walking', 'movement_completed_declared': True, 'battle_result_declared': 'won'}],
            'objectives': {'required_nodes': ['a'], 'checkpoints': ['a', 'g']}, 'max_steps': 4, 'max_results': 10}


class RouteContinuationTests(unittest.TestCase):
    def test_explicit_matching_prefix_reduces_manual_requirements_using_fresh_independent_ap(self):
        data = payload(); before = deepcopy(data); row = continue_route_plan(**data)
        self.assertEqual(row['matched_completed_prefix_count'], 1); self.assertEqual(row['anchor_status'], 'matched')
        self.assertEqual(row['remaining_objectives']['required_nodes'], [])
        self.assertEqual(row['remaining_objectives']['checkpoints'], ['g'])
        self.assertEqual(row['state_differences']['action_points'], {'predicted_reference': 5, 'after_declared': 4, 'delta': -1, 'reason': None})
        self.assertEqual(row['alternatives']['start'], 'a'); self.assertTrue(row['alternatives']['plans'])
        self.assertEqual(data, before); self.assertNotIn('completed_declared', data['after']['graph']['nodes'][1])
        self.assertIsNone(row['actual_goal_completed']); self.assertFalse(row['inventory_updated'])

    def test_winning_does_not_fill_unknown_movement_or_current_anchor(self):
        data = payload(); data['progress'][0]['movement_completed_declared'] = None
        row = continue_route_plan(**data)
        self.assertEqual(row['matched_completed_prefix_count'], 0); self.assertEqual(row['anchor_status'], 'mismatch')
        self.assertIsNone(row['alternatives']); self.assertIsNone(row['remaining_objectives'])
        self.assertEqual(row['progress_rows'][0]['reason'], 'movement_completion_unknown')
        self.assertIsNone(row['state_differences']['action_points']['delta'])

    def test_unknown_scope_or_changed_anchor_coordinates_prevent_old_goal_reuse(self):
        for change in ['scope', 'position', 'unknown']:
            data = payload()
            if change == 'scope': data['after']['graph']['zone_id'] = 'zone_2'
            elif change == 'position': data['after']['graph']['nodes'][1]['row'] = 5
            else: data['after']['graph'].pop('template_id')
            row = continue_route_plan(**data)
            self.assertEqual(row['anchor_status'], 'unknown'); self.assertIsNone(row['alternatives'])
            self.assertIsNone(row['state_differences']['action_points']['delta'])
            self.assertEqual(row['state_differences']['inventory'][0]['kind'], 'unknown')

    def test_independent_new_goal_and_complete_manual_policy_enable_new_scope_without_old_completion(self):
        data = payload(); data['after']['graph']['zone_id'] = 'zone_2'; data['goal_after'] = 'g'; data['objectives_after'] = {}
        row = continue_route_plan(**data)
        self.assertFalse(row['scope_identity_match']); self.assertEqual(row['replanning_origin'], 'explicit_new_goal_and_objectives')
        self.assertTrue(row['alternatives']['plans']); self.assertIsNone(row['actual_goal_completed'])
        self.assertEqual(row['remaining_objectives']['checkpoints'], [])

    def test_same_template_new_or_undeclared_instance_never_reuses_old_progress_goals(self):
        for instance in [None, 'public-map-instance-2']:
            data = payload()
            if instance is None: data['after']['graph'].pop('map_instance_id')
            else: data['after']['graph']['map_instance_id'] = instance
            row = continue_route_plan(**data)
            self.assertIsNone(row['alternatives']); self.assertIsNone(row['remaining_objectives'])
            self.assertEqual(row['anchor_status'], 'unknown')

    def test_removed_walking_edge_is_not_silently_replaced_with_multiedge_macro_in_old_suffix(self):
        data = payload(); data['after']['graph']['edges'].remove(['a', 'g']); row = continue_route_plan(**data)
        issue = row['remaining_plan_review']['blocked_or_unknown_rows'][0]
        self.assertEqual(issue, {'step': 2, 'node_id': 'g', 'reason': 'planned_walking_edge_removed'})
        self.assertIsNone(row['remaining_plan_review']['ledger'])
        walks = [plan for plan in row['alternatives']['plans'] if all(step['mode'] == 'walking' for step in plan['steps'])]
        self.assertTrue(walks); self.assertTrue(all(len(plan['steps']) >= 2 for plan in walks))
        self.assertEqual(row['state_differences']['edges']['removed'], [['a', 'g']])

    def test_missing_suffix_item_is_diagnosed_and_fresh_stock_alternatives_remain_available(self):
        data = payload(); data['plan']['steps'][1]['mode'] = 'jet'; data['after']['inventory'] = []
        row = continue_route_plan(**data)
        self.assertEqual(row['remaining_plan_review']['blocked_or_unknown_rows'][0]['reason'], 'planned_item_instance_missing')
        self.assertTrue(row['alternatives']['plans']); self.assertFalse(any(step['mode'] == 'jet' for plan in row['alternatives']['plans'] for step in plan['steps']))
        self.assertEqual(row['state_differences']['inventory'][0]['kind'], 'missing')
        self.assertFalse(row['state_differences']['inventory'][0]['cause_verified'])

    def test_instance_identity_conflict_never_becomes_a_numeric_usage_difference(self):
        data = payload(); data['after']['inventory'][0]['item_id'] = 'rogue_6_scrap_M_01'
        row = continue_route_plan(**data); change = row['state_differences']['inventory'][0]
        self.assertEqual(change['kind'], 'identity_conflict'); self.assertIsNone(change['delta'])
        self.assertFalse(change['cause_verified'])

    def test_failed_battle_requires_separate_continue_qualification_and_never_changes_resources(self):
        data = payload(); data['progress'][0]['battle_result_declared'] = 'lost'; before = deepcopy(data)
        unknown = continue_route_plan(**data)
        self.assertIsNone(unknown['alternatives'])
        self.assertTrue(any(row['reason'] == 'failed_battle_continuation_not_declared' for row in unknown['replanning_frontier']))
        data['continue_after_failure_declared'] = False
        blocked = continue_route_plan(**data); self.assertIsNone(blocked['alternatives'])
        data['continue_after_failure_declared'] = True
        admitted = continue_route_plan(**data); self.assertTrue(admitted['alternatives']['plans'])
        self.assertEqual(data['before'], before['before']); self.assertEqual(data['after'], before['after'])
        self.assertFalse(admitted['remaining_plan_review']['actual_continuation_verified'])

    def test_unknown_fresh_stock_or_passive_snapshot_is_not_filled_from_nominal_prefix(self):
        for field in ['inventory', 'passive_items']:
            data = payload(); data['after'][field] = None; row = continue_route_plan(**data)
            self.assertIsNone(row['alternatives'])
            self.assertTrue(any(item['reason'] == 'fresh_inventory_or_passive_snapshot_unknown' for item in row['replanning_frontier']))
            self.assertIsNone(row['after_snapshot'][field])

    def test_original_battle_identities_are_not_moved_into_new_suffix(self):
        data = payload(); data['before']['graph']['nodes'][-1]['base_node_type'] = 'BATTLE_NORMAL'
        data['plan']['steps'][-1]['battle'] = {'stage_id': 'ro6_n_1_1', 'battle_floor': 1, 'entry_context': 'map_battle', 'special_region': False, 'victory_declared': True}
        row = continue_route_plan(**data)
        self.assertFalse(row['remaining_plan_review']['old_battle_declarations_reused'])
        self.assertFalse(any('battle' in step for step in row['remaining_plan_review']['steps']))
        self.assertFalse(any('battle' in step for plan in row['alternatives']['plans'] for step in plan['steps']))

    def test_goal_binding_or_checkpoint_order_conflict_keeps_frontier_and_limits_stay_truthful(self):
        data = payload(); data['after']['graph']['nodes'][-1]['row'] = 5
        row = continue_route_plan(**data); self.assertIsNone(row['alternatives'])
        self.assertTrue(any(item['reason'] == 'residual_goal_or_policy_binding_unknown' for item in row['replanning_frontier']))
        data = payload(); data['objectives']['checkpoints'] = ['b', 'a', 'g']
        row = continue_route_plan(**data); self.assertIsNone(row['alternatives'])
        self.assertTrue(any(item['reason'] == 'declared_checkpoint_progress_order_conflict' for item in row['replanning_frontier']))
        data = payload(); data['max_steps'] = 1; data['after']['graph']['edges'].remove(['a', 'g']); data['after']['inventory'] = []
        row = continue_route_plan(**data); self.assertFalse(row['alternatives']['plans']); self.assertTrue(row['alternatives']['frontier'])

    def test_actual_declared_target_arrival_never_proves_ending_or_full_reward_completion(self):
        data = payload(); data['progress'].append({'step': 2, 'target': 'g', 'mode': 'walking', 'movement_completed_declared': True, 'battle_result_declared': None})
        data['after']['graph']['current_node'] = 'g'; row = continue_route_plan(**data)
        self.assertEqual(row['replanning_status'], 'declared_target_reached'); self.assertIsNone(row['alternatives'])
        self.assertIsNone(row['actual_goal_completed']); self.assertIsNone(row['actual_best_route'])

    def test_input_isolation_and_strict_invalid_progress_policy_snapshot_validation(self):
        data = payload(); original = deepcopy(data); first = continue_route_plan(**data); second = continue_route_plan(**data)
        self.assertEqual(first, second); self.assertEqual(data, original)
        first['after_snapshot']['inventory'][0]['remaining_uses'] = 0; self.assertNotEqual(first, second)
        for change in ['step', 'bool', 'result', 'scope_policy', 'ap', 'cap', 'macro']:
            invalid = payload()
            if change == 'step': invalid['progress'][0]['step'] = 2
            elif change == 'bool': invalid['progress'][0]['movement_completed_declared'] = 1
            elif change == 'result': invalid['progress'][0]['battle_result_declared'] = 'maybe'
            elif change == 'scope_policy': invalid['objectives_after'] = {}
            elif change == 'ap': invalid['after']['action_points'] = True
            elif change == 'cap': invalid['max_results'] = 0
            elif change == 'macro': invalid['plan']['steps'] = [{'mode': 'walking', 'target': 'g'}]
            with self.subTest(change=change), self.assertRaises(ValueError): continue_route_plan(**invalid)


if __name__ == '__main__': unittest.main()
