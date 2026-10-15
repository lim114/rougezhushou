"""UNEXECUTED formal draft: pure boundaries from archived existing public map fixtures."""
import ast
from copy import deepcopy
import hashlib
from rouge import resident_location_references as model
import json
from pathlib import Path
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / 'verification/sections/291-preparation/location-fixtures'


class ResidentLocationCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = json.loads((FIXTURES / 'fixtures/readable-map-047-graph.json').read_text(encoding='utf-8'))
        cls.navigation = json.loads((FIXTURES / 'fixtures/node-map-navigation-graph.json').read_text(encoding='utf-8'))

    def graph(self):
        # Explicit evidence variants of an existing fixture, not a new graph schema.
        graph = deepcopy(self.original)
        graph['nodes'][0]['observed_type'] = '“居民”据点'
        graph['nodes'][1]['remembered_type'] = '“居民”据点'
        return graph

    def call(self, graph, **context):
        return model.resident_location_references(graph, epoch=context.get('epoch', 'public-run'),
                                                   historical=context.get('historical', False))

    def matches(self, graph, binding, **context):
        return model.resident_binding_matches(graph, binding, epoch=context.get('epoch', 'public-run'),
                                             historical=context.get('historical', False))

    def assert_unknown(self, graph, **context):
        result = self.call(graph, **context)
        self.assertEqual(result['status'], 'unknown')
        self.assertEqual(result['rows'], [])
        self.assertIsNone(result['default_binding'])
        self.assertTrue(result['reason_codes'])

    def test_fixtures_are_exact_existing_AST_literals_not_imported_Qt_tests(self):
        evidence = json.loads((FIXTURES / 'SCHEMA_EVIDENCE.json').read_text(encoding='utf-8'))
        for record in evidence['fixtures']:
            raw = (FIXTURES / 'schema-source' / record['original_path']).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), record['original_pin']['sha256'])
            function = next(node for node in ast.parse(raw).body if isinstance(node, ast.FunctionDef) and node.name == 'graph')
            literal = ast.literal_eval(next(node.value for node in function.body if isinstance(node, ast.Return)))
            stored = json.loads((FIXTURES / record['fixture']).read_text(encoding='utf-8'))
            self.assertEqual(stored, literal)

    def test_unmodified_public_fixtures_do_not_create_resident_posts(self):
        for graph in (self.original, self.navigation):
            result = self.call(deepcopy(graph))
            self.assertEqual(result['status'], 'available')
            self.assertEqual(result['rows'], [])
            self.assertIn('这不证明地图中没有据点', result['notice'])

    def test_literal_current_and_past_positions_use_correct_exploration_row_order(self):
        result = self.call(self.graph())
        self.assertEqual([row['node_id'] for row in result['rows']], ['0,2', '1,1'])
        self.assertEqual([row['label'] for row in result['rows']],
            ['上排 · 第3列 · 已读据点', '中排 · 第2列 · 以前读到的据点'])
        self.assertEqual([row['type_evidence_role'] for row in result['rows']],
            ['current_observed', 'historical_remembered'])
        self.assertFalse(result['rows'][0]['map_historical'])
        self.assertIsNone(result['default_binding'])

    def test_all_actual_results_remain_unknown_for_zero_one_and_multiple_references(self):
        graphs = [deepcopy(self.original), self.graph()]
        one = self.graph(); one['nodes'].pop(1); graphs.append(one)
        for graph in graphs:
            result = self.call(graph)
            for key in ('actual_target_node_id', 'actual_moved', 'actual_current_floor_completion',
                        'actual_battle_triggered', 'actual_position_after', 'actual_route'):
                self.assertIsNone(result[key])
            self.assertNotIn('probability', result)
            self.assertNotIn('route', result)
            self.assertNotIn('target_candidates', result)

    def test_exact_resident_type_only_no_quotation_or_whitespace_normalization(self):
        for text in ('居民据点', '"居民"据点', '“居民”据点 ', '流窜“居民”', '“居民”据点候选', '未知的诡秘'):
            with self.subTest(text=text):
                graph = deepcopy(self.original)
                graph['nodes'][0]['observed_type'] = text
                self.assertEqual(self.call(graph)['rows'], [])

    def test_template_prediction_content_and_visits_are_not_read_type_evidence(self):
        graph = deepcopy(self.original)
        graph['nodes'][2].update(template_type='“居民”据点',
            prediction={'candidates': ['“居民”据点']}, content={'title': '“居民”据点'},
            visited=True, visited_at='public-time', battle_completed=True)
        result = self.call(graph)
        self.assertEqual(result['rows'], [])
        self.assertIsNone(result['actual_current_floor_completion'])

    def test_same_observed_and_remembered_type_produces_one_current_reference(self):
        graph = self.graph()
        graph['nodes'][0]['remembered_type'] = '“居民”据点'
        row = self.call(graph)['rows'][0]
        self.assertEqual(row['type_evidence_role'], 'current_observed')
        self.assertEqual(len([item for item in self.call(graph)['rows'] if item['node_id'] == '0,2']), 1)

    def test_remembered_post_is_kept_under_each_other_valid_current_type(self):
        for text in (None, '', '未知的诡秘', '林间空地', '作战', '诡意行商'):
            graph = deepcopy(self.original)
            graph['nodes'][1].update(observed_type=text, remembered_type='“居民”据点')
            row = self.call(graph)['rows'][0]
            self.assertEqual(row['node_id'], '1,1')
            self.assertEqual(row['type_evidence_role'], 'historical_remembered')
            self.assertEqual(row['binding']['observed_type'], text)

    def test_historical_map_labels_current_field_as_record_time_only(self):
        result = self.call(self.graph(), historical=True)
        self.assertEqual(result['rows'][0]['label'], '上排 · 第3列 · 记录时读到的据点 · 历史地图记录')
        self.assertEqual(result['rows'][1]['label'], '中排 · 第2列 · 以前读到的据点 · 历史地图记录')
        self.assertTrue(all(row['binding']['map_historical'] is True for row in result['rows']))

    def test_no_graph_and_valid_empty_nodes_do_not_claim_absence_or_completion(self):
        result = self.call(None)
        self.assertEqual(result['status'], 'no_graph')
        self.assertEqual(result['rows'], [])
        self.assertIsNone(result['actual_current_floor_completion'])
        graph = self.graph(); graph['nodes'] = []
        empty = self.call(graph)
        self.assertEqual(empty['status'], 'available')
        self.assertEqual(empty['rows'], [])
        self.assertIn('这不证明地图中没有据点', empty['notice'])

    def test_graph_mapping_and_context_types_are_strict(self):
        for graph in ([], False, 1, 'graph'):
            self.assert_unknown(graph)
        for epoch in (None, '', '  ', 123, True, [], {}):
            self.assert_unknown(self.graph(), epoch=epoch)
        for historical in (None, 0, 1, 'false', [], {}):
            self.assert_unknown(self.graph(), historical=historical)

    def test_zone_and_template_identity_do_not_accept_missing_or_coerced_values(self):
        for key in ('zone_id', 'template_id'):
            for value in (None, '', '  ', 0, True, [], {}):
                graph = self.graph(); graph[key] = value
                self.assert_unknown(graph)
        graph = self.graph(); graph['zone_id'] = 'unrecognized-portal-zone'
        self.assertEqual(self.call(graph)['status'], 'available')

    def test_grid_requires_existing_rows_cols_positive_exact_integers(self):
        for grid in (None, [], {}, {'rows': 3}, {'cols': 5}):
            graph = self.graph(); graph['grid'] = grid
            self.assert_unknown(graph)
        for key in ('rows', 'cols'):
            for value in (0, -1, True, 3.0, '3', None):
                graph = self.graph(); graph['grid'][key] = value
                self.assert_unknown(graph)

    def test_entire_node_collection_is_validated_before_partial_rows_are_exposed(self):
        for nodes in (None, {}, (), [None], [False]):
            graph = self.graph(); graph['nodes'] = nodes
            self.assert_unknown(graph)
        graph = self.graph(); graph['nodes'][2]['id'] = ''
        self.assert_unknown(graph)

    def test_duplicate_ids_anywhere_reject_all_rows_not_first_match(self):
        graph = self.graph(); graph['nodes'][2]['id'] = '0,2'
        self.assert_unknown(graph)
        self.assertEqual(self.call(graph)['reason_codes'], ['duplicate_node_id'])

    def test_duplicate_positions_with_different_ids_reject_all_rows(self):
        graph = self.graph(); graph['nodes'][2].update(row=0, col=2)
        self.assert_unknown(graph)
        self.assertEqual(self.call(graph)['reason_codes'], ['duplicate_node_position'])

    def test_each_position_is_in_bounds_and_true_integer_including_unrelated_nodes(self):
        for key, values in (('row', (-1, 3, True, 0.0, None, '0')),
                            ('col', (-1, 5, False, 3.0, None, '3'))):
            for value in values:
                graph = self.graph(); graph['nodes'][2][key] = value
                self.assert_unknown(graph)
        graph = self.graph(); del graph['nodes'][2]['row']
        self.assert_unknown(graph)

    def test_invalid_type_evidence_is_not_silently_promoted_from_memory(self):
        for key in ('observed_type', 'remembered_type'):
            for value in (True, 0, [], {}):
                graph = self.graph(); graph['nodes'][1][key] = value
                self.assert_unknown(graph)

    def test_other_grid_heights_use_numbered_rows_without_fixed_three_row_assumption(self):
        graph = self.graph(); graph['grid']['rows'] = 4
        self.assertEqual([row['location'] for row in self.call(graph)['rows']],
                         ['第1排 · 第3列', '第2排 · 第2列'])
        graph['nodes'] = [graph['nodes'][0]]; graph['grid']['rows'] = 1
        self.assertEqual(self.call(graph)['rows'][0]['location'], '第1排 · 第3列')

    def test_centers_grid_origin_edges_and_distance_do_not_reposition_or_rank_rows(self):
        graph = self.graph(); graph['nodes'].reverse()
        for node in graph['nodes']:
            node.update(center=['not', 'logical coordinates'], distance=-100, visible=False)
        graph['grid'].update(origin=None, pitch='unused')
        graph['edges'] = 'not used for position references'
        self.assertEqual([row['location'] for row in self.call(graph)['rows']],
                         ['上排 · 第3列', '中排 · 第2列'])

    def test_binding_exact_match_keeps_the_existing_App_guard_fields(self):
        graph = self.graph(); binding = self.call(graph)['rows'][0]['binding']
        self.assertEqual({key: binding[key] for key in ('epoch', 'zone_id', 'template_id', 'node_id', 'row', 'col')},
            {'epoch': 'public-run', 'zone_id': 'zone_1', 'template_id': '1a', 'node_id': '0,2', 'row': 0, 'col': 2})
        self.assertTrue(self.matches(graph, deepcopy(binding)))

    def test_binding_rejects_partial_extra_subclass_and_numerically_equal_bool_fields(self):
        class D(dict): pass
        graph = self.graph(); original = self.call(graph)['rows'][0]['binding']
        bad = [None, [], D(original)]
        binding = deepcopy(original); del binding['row']; bad.append(binding)
        binding = deepcopy(original); binding['extra'] = True; bad.append(binding)
        binding = deepcopy(original); binding['row'] = False; bad.append(binding)
        binding = deepcopy(original); binding['map_historical'] = 0; bad.append(binding)
        binding = deepcopy(original); binding['grid']['rows'] = 3.0; bad.append(binding)
        for binding in bad:
            self.assertFalse(self.matches(graph, binding))

    def test_changed_context_map_identity_and_position_reject_old_binding(self):
        original = self.graph(); binding = self.call(original)['rows'][0]['binding']
        self.assertFalse(self.matches(original, binding, epoch='another-run'))
        self.assertFalse(self.matches(original, binding, historical=True))
        for key in ('zone_id', 'template_id'):
            graph = deepcopy(original); graph[key] += '-new'
            self.assertFalse(self.matches(graph, binding))
        graph = deepcopy(original); graph['nodes'][0]['id'] = 'same-position-new-id'
        self.assertFalse(self.matches(graph, binding))
        graph = deepcopy(original); graph['nodes'][0]['col'] = 4
        self.assertFalse(self.matches(graph, binding))

    def test_changed_evidence_and_grid_shape_reject_old_binding_without_guessing_completion(self):
        original = self.graph(); binding = self.call(original)['rows'][0]['binding']
        graph = deepcopy(original); graph['nodes'][0].update(observed_type='林间空地', remembered_type='“居民”据点')
        self.assertFalse(self.matches(graph, binding))
        self.assertEqual(self.call(graph)['rows'][0]['type_evidence_role'], 'historical_remembered')
        graph = deepcopy(original); graph['nodes'][0]['remembered_type'] = '紧急作战'
        self.assertFalse(self.matches(graph, binding))
        for key in ('rows', 'cols'):
            graph = deepcopy(original); graph['grid'][key] += 1
            self.assertFalse(self.matches(graph, binding))

    def test_timestamps_current_marker_and_unrelated_content_do_not_clear_valid_position(self):
        graph = self.graph(); binding = self.call(graph)['rows'][0]['binding']
        graph.update(captured_at='later-public-time', current_node='2,3', last_confirmed_current_node=None)
        graph['nodes'][0].update(content={'title': 'new public detail'}, revealed_at='new public time', visible=False)
        self.assertTrue(self.matches(graph, binding))

    def test_input_and_returned_nested_grid_copies_do_not_pollute_next_reference(self):
        graph = self.graph(); before = deepcopy(graph)
        result = self.call(graph); binding = result['rows'][0]['binding']
        binding['grid']['rows'] = 99
        result['rows'][0]['label'] = 'changed'
        self.assertEqual(graph, before)
        again = self.call(graph)
        self.assertEqual(again['rows'][0]['binding']['grid'], {'rows': 3, 'cols': 5})
        self.assertEqual(again['rows'][0]['label'], '上排 · 第3列 · 已读据点')

    def test_no_public_floor_completion_distance_or_evaluator_input(self):
        for key in ('floor', 'completion', 'visited', 'evaluator', 'source', 'distance', 'current_route'):
            with self.subTest(key=key), self.assertRaises(TypeError):
                model.resident_location_references(self.graph(), epoch='public-run', historical=False, **{key: True})

    def test_mapping_list_string_and_integer_subclasses_are_not_typed_JSON(self):
        class D(dict): pass
        class L(list): pass
        class S(str): pass
        class I(int): pass
        self.assert_unknown(D(self.graph()))
        graph = self.graph(); graph['nodes'] = L(graph['nodes']); self.assert_unknown(graph)
        graph = self.graph(); graph['grid'] = D(graph['grid']); self.assert_unknown(graph)
        graph = self.graph(); graph['nodes'][2] = D(graph['nodes'][2]); self.assert_unknown(graph)
        graph = self.graph(); graph['nodes'][2]['row'] = I(2); self.assert_unknown(graph)
        graph = self.graph(); graph['nodes'][0]['observed_type'] = S('“居民”据点'); self.assert_unknown(graph)
        self.assert_unknown(self.graph(), epoch=S('public-run'))

    def test_functions_do_not_need_files_or_project_runtime_modules(self):
        graph = self.graph(); binding = self.call(graph)['rows'][0]['binding']
        with patch('builtins.open', side_effect=AssertionError('No I/O in pure functions')):
            self.assertEqual(self.call(graph)['status'], 'available')
            self.assertTrue(self.matches(graph, binding))
        self.assertEqual(Path(model.__file__).resolve(), (ROOT / 'rouge/resident_location_references.py').resolve())
        for name in ('catalog', 'run_state', 'capture', 'app', 'desktop_backend', 'route_reference'):
            self.assertNotIn(name, model.__dict__)


if __name__ == '__main__':
    unittest.main()
