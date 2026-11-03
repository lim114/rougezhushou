from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import unittest

from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication
from rouge import fruit_marker_planning as planning
from rouge.fruit_marker_view import FruitMarkerPanel

ROOT = Path(__file__).resolve().parents[1]


def node(kind='其它节点', marker='fruit'):
    return {'node_id': 'marked-A', 'map_id': 'explicit-map', 'node_type': kind,
            'marker': marker, 'paired_node_id': 'paired-B' if kind == '曲折密道' else None}


def placement(performed=True, covered=None):
    return {'kind': 'place', 'node_id': 'marked-A', 'performed': performed, 'covers_civilization': covered}


def visit(mode='explore', performed=True, other=None, after=None):
    return {'kind': 'visit', 'node_id': 'marked-A', 'mode': mode, 'performed': performed,
            'entry_node_id': 'paired-B' if mode == 'corridor' else None,
            'exit_node_id': 'marked-A' if mode == 'corridor' else None,
            'from_other_end': other, 'marker_after': after}


class MarkerFlowTests(unittest.TestCase):
    def test_fixed_original_reward_and_document_candidates_with_rebuild(self):
        spec = importlib.util.spec_from_file_location('fruit_builder', ROOT / 'scripts/build_fruit_marker_reference.py')
        builder = importlib.util.module_from_spec(spec); spec.loader.exec_module(builder)
        built = builder.build()
        self.assertEqual(built, json.loads((ROOT / 'rouge/data/fruit-marker-reference.json').read_text()))
        self.assertEqual(built['relic']['id'], 'rogue_6_relic_cargo_4')
        self.assertEqual([(i['id'], i['name']) for i in built['documented_reward_candidates']],
            [('rogue_6_scrap_G_10', '恋家果'), ('rogue_6_scrap_G_11', '光彩松露'), ('rogue_6_scrap_G_09', '板藤')])
        self.assertEqual(built['original_reward_quantity_reference'], 1)
        self.assertIn('一个较为稀有的随机自然物', built['original_quantity_quote'])

    def test_owned_and_new_region_are_not_marker_creation(self):
        result = planning.declared_marker_flow(node(marker='none'), relic_owned=True, new_region_entered=True)
        self.assertEqual(result['generation_condition_status'], 'matched')
        self.assertEqual(result['final_marker_reference'], 'none')
        self.assertIsNone(result['actual_final_marker']); self.assertEqual(result['rows'], [])

    def test_explicit_civilization_cover_has_separate_before_node_and_occurrence(self):
        for covered in (None, False):
            result = planning.declared_marker_flow(node('失与得', 'civilization'), [placement(covered=covered)])
            self.assertEqual(result['rows'][0]['condition_status'], 'unknown')
            self.assertEqual(result['final_marker_reference'], 'unknown')
        result = planning.declared_marker_flow(node('失与得', 'civilization'), [placement(covered=True)])
        self.assertEqual(result['final_marker_reference'], 'fruit')
        self.assertIsNone(result['rows'][0]['actual_marker_after'])
        for invalid_node in (node('其它节点', 'civilization'), node('失与得', 'none')):
            with self.assertRaises(ValueError): planning.declared_marker_flow(invalid_node, [placement(covered=True)])

    def test_not_performed_and_unknown_placement_preserve_their_own_scope(self):
        no = planning.declared_marker_flow(node('失与得', 'civilization'), [placement(False)])
        self.assertEqual(no['final_marker_reference'], 'civilization')
        unknown = planning.declared_marker_flow(node(marker='none'), [placement(None)])
        self.assertEqual(unknown['final_marker_reference'], 'unknown')

    def test_explore_gives_conditional_one_not_received_and_normal_retention_unknown(self):
        result = planning.declared_marker_flow(node(), [visit()]); row = result['rows'][0]
        self.assertEqual(row['condition_status'], 'matched')
        self.assertEqual(row['source_condition_reward_quantity'], 1)
        self.assertEqual(len(row['documented_reward_candidates']), 3)
        self.assertEqual(result['final_marker_reference'], 'unknown')
        self.assertIsNone(row['actual_reward_quantity']); self.assertIsNone(row['actual_reward_received'])
        self.assertFalse(result['run_state_written']); self.assertFalse(result['game_operated'])

    def test_no_marker_and_not_performed_exclude_this_condition_not_actual_state(self):
        for current, event in [(node(marker='none'), visit()), (node(), visit(performed=False))]:
            result = planning.declared_marker_flow(current, [event], relic_owned=True, new_region_entered=True)
            self.assertEqual(result['rows'][0]['condition_status'], 'excluded')
            self.assertIsNone(result['rows'][0]['source_condition_reward_quantity'])
            self.assertIsNone(result['rows'][0]['actual_triggered'])

    def test_positive_other_end_requires_exact_explicit_entry_and_emergence(self):
        result = planning.declared_marker_flow(node('曲折密道'), [visit('corridor', other=True)])
        row = result['rows'][0]
        self.assertEqual(row['condition_status'], 'matched')
        self.assertEqual(row['marker_after_reference'], 'fruit')
        self.assertEqual(result['final_marker_reference'], 'fruit')
        self.assertIsNone(row['actual_marker_after'])
        for field, replacement in [('entry_node_id', 'marked-A'), ('exit_node_id', 'paired-B')]:
            changed = visit('corridor', other=True); changed[field] = replacement
            with self.assertRaises(ValueError): planning.declared_marker_flow(node('曲折密道'), [changed])
        missing_pair = node('曲折密道'); missing_pair['paired_node_id'] = None
        with self.assertRaises(ValueError): planning.declared_marker_flow(missing_pair, [visit('corridor', other=True)])

    def test_different_ids_unknown_other_end_and_same_end_do_not_prove_trigger(self):
        for other in (None, False):
            result = planning.declared_marker_flow(node('曲折密道'), [visit('corridor', other=other)])
            row = result['rows'][0]
            self.assertEqual(row['condition_status'], 'unknown')
            self.assertIsNone(row['source_condition_reward_quantity'])
            self.assertEqual(result['final_marker_reference'], 'unknown')
            self.assertEqual(len(row['documented_reward_candidates']), 3)
        result = planning.declared_marker_flow(node('曲折密道'), [visit()])
        self.assertEqual(result['rows'][0]['condition_status'], 'unknown')

    def test_repeated_retained_marker_is_not_a_total_or_independent_random_trial(self):
        result = planning.declared_marker_flow(node('曲折密道'), [visit('corridor', other=True), visit('corridor', other=True)])
        self.assertEqual([r['source_condition_reward_quantity'] for r in result['rows']], [1, 1])
        self.assertIsNone(result['whole_reward_total']); self.assertIsNone(result['repeated_trigger_cap'])
        self.assertTrue(all(r['actual_reward_received'] is None for r in result['rows']))

    def test_after_marker_conflict_keeps_input_and_source_separate(self):
        events = [visit('corridor', other=True, after='none'), visit('corridor', other=True)]
        result = planning.declared_marker_flow(node('曲折密道'), events)
        first = result['rows'][0]
        self.assertEqual(first['condition_status'], 'conflict')
        self.assertEqual(first['marker_after_reference'], 'fruit')
        self.assertEqual(first['marker_after_declared'], 'none')
        self.assertEqual(result['rows'][1]['marker_before'], 'none')
        self.assertEqual(result['rows'][1]['condition_status'], 'excluded')
        self.assertIsNone(result['actual_final_marker'])

    def test_steps_are_exactly_bound_and_inputs_deeply_preserved(self):
        current = node('曲折密道'); events = [visit('corridor', other=True)]
        before = deepcopy((current, events)); result = planning.declared_marker_flow(current, events)
        self.assertEqual((current, events), before)
        result['node']['node_id'] = 'mutated-result'
        self.assertEqual(current['node_id'], 'marked-A')
        wrong = visit('corridor', other=True); wrong['node_id'] = 'foreign-node'
        with self.assertRaises(ValueError): planning.declared_marker_flow(current, [wrong])
        with self.assertRaises(ValueError): planning.declared_marker_flow({**current, 'paired_node_id': 'marked-A'})

    def test_false_text_and_extra_keys_are_never_confirmations(self):
        for raw in ('false', 0, 1, [], {}):
            with self.assertRaises(ValueError): planning.declared_marker_flow(node(), relic_owned=raw)
            with self.assertRaises(ValueError): planning.declared_marker_flow(node(), [visit(performed=raw)])
        with self.assertRaises(ValueError): planning.declared_marker_flow({**node(), 'rewards': 3})
        with self.assertRaises(ValueError): planning.declared_marker_flow(node(), [{**visit(), 'received': True}])


class MarkerPanelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.panel = FruitMarkerPanel(); self.panel.show(); self.app.processEvents()

    def tearDown(self):
        self.panel.close(); self.app.processEvents()

    def choose(self, combo, value):
        combo.setCurrentIndex(combo.findData(value)); self.app.processEvents()

    def test_actual_qt_cover_then_explore_and_frozen_candidate_reading(self):
        self.panel.set_reference(node('失与得', 'civilization'))
        self.choose(self.panel.performed, True)
        self.panel.place_button.click()
        self.assertEqual(self.panel.result['final_marker_reference'], 'unknown')
        self.panel.clear_button.click(); self.choose(self.panel.covered, True)
        self.panel.place_button.click(); self.panel.visit_button.click(); self.app.processEvents()
        self.assertEqual(len(self.panel.result['rows']), 2)
        self.assertEqual(self.panel.result['rows'][1]['source_condition_reward_quantity'], 1)
        self.assertIn('恋家果、光彩松露、板藤', self.panel.detail.toPlainText())
        self.assertNotIn('[[', self.panel.detail.toPlainText())
        self.assertIn('实际成员和领取数量未知', self.panel.detail.toPlainText())

    def test_actual_qt_other_end_fails_wrong_identity_then_emits_readonly_map_reference(self):
        self.panel.set_reference(node('曲折密道'))
        self.choose(self.panel.performed, True)
        self.panel.set_corridor_route(entry_node_id='marked-A', exit_node_id='paired-B', from_other_end=True)
        self.panel.visit_button.click(); self.assertEqual(self.panel.events, [])
        self.assertIn('此步骤未加入', self.panel.summary.text())
        self.panel.set_corridor_route(entry_node_id='paired-B', exit_node_id='marked-A', from_other_end=True)
        self.panel.visit_button.click(); self.app.processEvents()
        self.assertEqual(self.panel.result['final_marker_reference'], 'fruit')
        captured = []; self.panel.nodePreviewRequested.connect(captured.append); self.panel.node_button.click()
        self.assertEqual(captured, [{'map_id': 'explicit-map', 'node_id': 'marked-A',
            'source': 'explicit_offline_marker_declaration', 'actual_map_binding_verified': False}])
        self.assertFalse(self.panel.isModal()); self.assertTrue(self.panel.detail.isReadOnly())
        self.assertTrue(self.panel.isVisible())

    def test_refresh_preserves_inputs_steps_reading_and_old_binding_is_not_retargeted(self):
        self.panel.set_reference(node('曲折密道'))
        self.choose(self.panel.performed, True)
        self.panel.set_corridor_route(entry_node_id='paired-B', exit_node_id='marked-A', from_other_end=True)
        self.panel.visit_button.click(); self.panel.technical.setChecked(True); self.app.processEvents()
        self.panel.detail.moveCursor(QTextCursor.MoveOperation.End)
        prior_scroll = self.panel.detail.verticalScrollBar().value()
        prior_events = deepcopy(self.panel.events)
        self.panel.steps.setCurrentItem(self.panel.steps.topLevelItem(0)); self.panel.refresh(); self.app.processEvents()
        self.assertEqual(self.panel.events, prior_events); self.assertTrue(self.panel.technical.isChecked())
        self.assertEqual(self.panel.entry_id.text(), 'paired-B')
        self.assertEqual(self.panel.detail.verticalScrollBar().value(), prior_scroll)
        self.assertEqual(self.panel.steps.currentItem().data(0, Qt.ItemDataRole.UserRole), 1)
        changed = node('曲折密道'); changed['node_id'] = 'new-C'
        self.panel.set_reference(changed)
        self.assertIsNone(self.panel.result); self.assertFalse(self.panel.node_button.isEnabled())
        self.assertEqual(self.panel.events, prior_events)
