import copy
import json
import math
import os
from pathlib import Path
import unittest

from rouge.attack_state_sequence import (sequence_choices, project_attack_state_sequence,
    public_sequence_payload, format_attack_state_sequence)


def candidate(operator='kaltsit', scope='1', animation='Attack_Loop', face='Front'):
    return next(r['id'] for r in sequence_choices(operator, scope)
                if r['animation'] == animation and r['orientation'] == face)


def step(state, identity=None, period=2.55, **extra):
    return {'state': state, 'reference_id': identity or candidate(),
            'cooldown_seconds': period, **extra}


def payload(steps, operator='kaltsit', scope='1', **extra):
    return {'operator': operator, 'scope': scope, 'steps': steps, **extra}


class AttackStateSequenceTests(unittest.TestCase):
    def test_entry_and_continuation_change_scaling_and_independent_segment_waits(self):
        result = project_attack_state_sequence(payload([step('entry'), step('continue'), step('continue')]))
        self.assertEqual([r['first_attack_bool_under_declared_path'] for r in result['rows']], [True, False, False])
        self.assertEqual([[s['requested_wait_ticks'] for s in r['segments']] for r in result['rows']],
                         [[8, 69, 0], [0, 76, 0], [0, 76, 0]])
        self.assertEqual(result['requested_wait_ticks_total'], 229)
        self.assertEqual(result['all_entry_comparison_wait_ticks_total'], 231)
        self.assertEqual(result['declared_minus_all_entry_wait_ticks_total'], -2)
        self.assertEqual([r['declared_entry_ordinal'] for r in result['rows']], [1, 1, 1])
        self.assertEqual([r['cumulative_requested_wait_ticks_after'] for r in result['rows']], [77, 153, 229])

    def test_random_candidate_changes_forward_false_and_explicit_entry_reopens_gate(self):
        a = candidate('silverash', 'normal', 'Attack_A')
        b = candidate('silverash', 'normal', 'Attack_B')
        c = candidate('silverash', 'normal', 'Attack_C')
        result = project_attack_state_sequence(payload([step('entry', a), step('continue', b),
            step('continue', c), step('entry', c)], 'silverash', 'normal'))
        self.assertEqual([r['requested_wait_ticks'] for r in result['rows']], [40, 36, 36, 40])
        self.assertEqual(result['requested_wait_ticks_total'], 152)
        self.assertEqual([r['declared_entry_ordinal'] for r in result['rows']], [1, 1, 1, 4])
        self.assertEqual([r['candidate_changed'] for r in result['rows']], [False, True, True, False])
        for row in result['rows']:
            self.assertFalse(row['candidate_change_reopens_first_gate'])
            self.assertIsNone(row['random_selection']['sequence'])
            self.assertIsNone(row['random_selection']['probabilities'])
        self.assertEqual(result['all_entry_comparison_wait_ticks_total'], 160)

    def test_movement_and_target_gaps_do_not_supply_state_entries_or_elapsed_time(self):
        plain = project_attack_state_sequence(payload([step('entry'), step('continue')]))
        gaps = project_attack_state_sequence(payload([step('entry'), step('continue',
            movement_gap_seconds=3599, target_gap_seconds=3600)]))
        self.assertEqual(gaps['requested_wait_ticks_total'], plain['requested_wait_ticks_total'])
        row = gaps['rows'][1]
        self.assertFalse(row['first_attack_bool_under_declared_path'])
        self.assertEqual(row['declared_entry_ordinal'], 1)
        self.assertFalse(row['gaps_used_to_infer_state_or_schedule'])
        self.assertIsNone(gaps['actual_elapsed_sequence_seconds'])

    def test_first_continuation_keeps_earlier_entry_unknown(self):
        result = project_attack_state_sequence(payload([step('continue'), step('entry'), step('continue')]))
        self.assertEqual([r['declared_entry_ordinal'] for r in result['rows']], [None, 2, 2])
        self.assertEqual([r['prior_entry_not_declared'] for r in result['rows']], [True, False, False])
        self.assertEqual([r['requested_wait_ticks'] for r in result['rows']], [76, 77, 76])

    def test_all_source_candidates_and_scopes_are_closed_independent_records(self):
        counts = []
        for operator, scope in [('kaltsit', 'normal'), ('kaltsit', '1'), ('silverash', 'normal')]:
            choices = sequence_choices(operator, scope)
            counts.append(len(choices))
            for choice in choices:
                result = project_attack_state_sequence(payload([
                    step('entry', choice['id']), step('continue', choice['id'])], operator, scope))
                self.assertEqual(result['rows'][0]['orientation'], choice['orientation'])
                self.assertEqual(result['rows'][0]['mode_indices'], choice['mode_indices'])
                self.assertTrue(result['rows'][0]['segments'][0]['played_under_declared_gate'])
                self.assertFalse(result['rows'][1]['segments'][0]['played_under_declared_gate'])
        self.assertEqual(counts, [3, 3, 6])

    def test_grid_is_declared_float_wait_reference_and_zero_present_wait_is_not_skipped(self):
        result = project_attack_state_sequence(payload([step('entry', period=.001)], grid_fps=1))
        row = result['rows'][0]
        self.assertEqual([s['requested_wait_ticks'] for s in row['segments']], [1, 1, 0])
        self.assertEqual(row['requested_wait_ticks'], 2)
        self.assertIsNone(result['actual_first_callback_seconds'])
        self.assertIsNone(result['actual_last_end_seconds'])
        self.assertIsNone(result['actual_cycle_seconds'])
        self.assertFalse(result['runtime_binding_verified'])

    def test_full_payload_validation_rejects_stale_operator_scope_candidates_and_nonfinite_values(self):
        invalid = [None, [], {}, payload([]), payload([step('entry')] * 65),
            payload([step('entry')], 'mechanist', '1'), payload([step('entry')], 'kaltsit', '2'),
            payload([step('entry')], 'silverash', 'normal'), payload([step('first')]),
            payload([step(True)]), payload([{**step('entry'), 'operator': 'silverash'}]),
            payload([{**step('entry'), 'reference_id': True}]), payload([step('entry')], unexpected=1)]
        for value in [None, True, False, '2.55', math.nan, math.inf, -1, 0, 3601, 1e-320, 10 ** 400]:
            invalid.append(payload([step('entry', period=value)]))
        for value in [True, '30', 0, 241, math.nan]:
            invalid.append(payload([step('entry')], grid_fps=value))
        for value in [True, '0', math.nan, math.inf, -1, 3601]:
            invalid.append(payload([step('entry', target_gap_seconds=value)]))
        for data in invalid:
            with self.subTest(data=str(data)[:150]), self.assertRaises(ValueError):
                project_attack_state_sequence(data)

    def test_inputs_candidates_and_results_do_not_share_mutable_history(self):
        data = payload([step('entry'), step('continue')])
        before = copy.deepcopy(data)
        result = project_attack_state_sequence(data)
        result['declared_sequence']['steps'][0]['state'] = 'continue'
        result['rows'][0]['random_selection']['sequence'] = ['fake']
        self.assertEqual(data, before)
        fresh = project_attack_state_sequence(data)
        self.assertNotIn('sequence', fresh['rows'][0]['random_selection'])
        self.assertTrue(fresh['rows'][0]['first_attack_bool_under_declared_path'])
        changed = sequence_choices('kaltsit', '1')
        changed[0]['static_action_binding']['three_part_reference']['begin']['duration_seconds'] = 99
        self.assertNotEqual(sequence_choices('kaltsit', '1')[0]['static_action_binding']['three_part_reference']['begin']['duration_seconds'], 99)

    def test_public_examples_and_report_preserve_unknown_boundaries(self):
        for operator, scope in [('kaltsit', 'normal'), ('kaltsit', '1'), ('silverash', 'normal')]:
            data = public_sequence_payload(operator, scope)
            result = project_attack_state_sequence(data)
            report = format_attack_state_sequence(result)
            self.assertIn('等待分项之和', report)
            self.assertIn('进入组=', report)
            self.assertIn('firstAttack=false', report)
            self.assertIn('不据此重开门', report)
            self.assertIn('实际首击/末段结束/整串攻击耗时/完整循环：未知', report)
            self.assertIsNone(result['actual_fsm_path'])
            self.assertIsNone(result['actual_random_draws'])


class AttackStateSequenceSourceTests(unittest.TestCase):
    def test_same_version_complete_original_gate_and_wait_methods_are_present(self):
        root = Path(__file__).resolve().parents[1]
        proofs = [json.loads((root / 'research' / name / 'native-proof.json').read_text()) for name in
                  ('p2-three-part-wait-current', 'p2-three-part-static-current')]
        self.assertEqual(proofs[0]['game_dll_sha256'], proofs[1]['game_dll_sha256'])
        self.assertEqual(proofs[0]['metadata_sha256'], proofs[1]['metadata_sha256'])
        by_index = {r['method']['metadata_method_index']: r for r in proofs[0]['method_records']}
        for index in [76192, 76195, 76196, 91665, 91666, 64127, 64149]:
            row = by_index[index]
            self.assertTrue(row['cfg_bounded_traversal_finished'])
            self.assertEqual(row['limits'], [])
            self.assertTrue(row['instructions'])
        self.assertFalse(proofs[0]['current_hotfix_equivalence_proven'])
        self.assertFalse(proofs[1]['hotfix_equivalence_proven'])


os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
from PySide6.QtWidgets import QApplication
from rouge.attack_state_sequence_view import AttackStateSequencePanel


class AttackStateSequenceViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.panel = AttackStateSequencePanel()

    def tearDown(self):
        self.panel.close()
        self.panel.deleteLater()
        self.app.processEvents()

    def test_real_panel_adds_explicit_steps_and_calculates_without_run_state(self):
        panel = self.panel
        panel.load_template.click()
        panel.calculate_button.click()
        self.assertIsNotNone(panel.result_snapshot(), panel.status.text())
        panel.add_continue.click()
        self.assertIsNone(panel.result_snapshot())
        self.assertEqual(panel.current_query()['steps'][-1]['state'], 'continue')
        panel.calculate_button.click()
        result = panel.result_snapshot()
        self.assertFalse(result['rows'][-1]['first_attack_bool_under_declared_path'])
        self.assertEqual(result['rows'][-1]['declared_entry_ordinal'], 3)
        result['rows'].clear()
        self.assertEqual(len(panel.result_snapshot()['rows']), 4)
        self.assertIn('整串攻击耗时/完整循环：未知', panel.result_view.toPlainText())

    def test_context_change_preserves_json_and_result_and_rejects_cross_identity_append(self):
        panel = self.panel
        panel.load_template.click()
        panel.calculate_button.click()
        before = (panel.editor.toPlainText(), panel.result_snapshot(), panel.result_view.toPlainText())
        panel.set_context({'operator': 'silverash'})
        self.assertEqual(before, (panel.editor.toPlainText(), panel.result_snapshot(), panel.result_view.toPlainText()))
        panel.add_entry.click()
        self.assertEqual(panel.editor.toPlainText(), before[0])
        self.assertIn('作用域不符', panel.status.text())
        panel.set_context({'operator': 'mechanist'})
        self.assertEqual(panel.editor.toPlainText(), before[0])
        self.assertIn('没有此三段状态门原件', panel.status.text())

    def test_duplicate_nonfinite_and_wrong_candidates_clear_result_without_writes(self):
        panel = self.panel
        for text in ['{"operator":"kaltsit","operator":"silverash","scope":"normal","steps":[]}',
                     '{"operator":"kaltsit","scope":"1","steps":NaN}',
                     json.dumps(payload([step('entry')], 'silverash', 'normal'))]:
            panel.load_template.click()
            panel.calculate_button.click()
            self.assertIsNotNone(panel.result_snapshot())
            panel.editor.setPlainText(text)
            panel.calculate_button.click()
            self.assertIsNone(panel.result_snapshot())
            self.assertEqual(panel.result_view.toPlainText(), '')
            self.assertNotEqual(panel.status.text(), '')
