import copy
import json
import math
import os
from pathlib import Path
import random
import unittest
from unittest.mock import patch

from rouge.recipient_native_ratio import (ONE, MAX_RAW, MAX_INTEGER_HP, OPERATORS,
    native_positive_ratio_division, recipient_native_ratio_diagnostic,
    public_recipient_ratio_payload, format_recipient_ratio_diagnostic)


def original(label, hp, maximum, unit='integer_hp', after=None):
    return {'label': label, 'hp': hp, 'max_hp': maximum, 'unit': unit,
        'post_clamp_ratio_raw': after, 'evidence': {'kind': 'formula_reference', 'source': '独立整数算术参考'}}


class RecipientNativeRatioTests(unittest.TestCase):
    def test_positive_midpoints_round_up_and_do_not_use_truncation_or_ties_even(self):
        for hp, maximum, expected in [(0, ONE, 0), (1, 2 * ONE, 1), (3, 2 * ONE, 2),
                                      (5, 2 * ONE, 3), (ONE, ONE, ONE), (MAX_RAW, MAX_RAW, ONE)]:
            self.assertEqual(native_positive_ratio_division(hp, maximum), expected)
        self.assertEqual(native_positive_ratio_division(1, 2 * ONE, trace=True)['quotient_33_fractional_raw'], 1)
        self.assertEqual(native_positive_ratio_division(0, ONE, trace=True)['numeric_steps'], [])

    def test_saved_numeric_path_matches_independent_integer_oracle_across_large_and_nibble_divisors(self):
        vectors = [(0, 1), (1, 1), (MAX_RAW - 1, MAX_RAW), (1, MAX_RAW),
                   (12345 * ONE, 80000 * ONE), (ONE // 3, ONE), (1, 16), (7, 128),
                   ((1 << 60) - 1, 1 << 60), ((1 << 61), (1 << 62))]
        rng = random.Random(255)
        vectors.extend((rng.randrange(denominator + 1), denominator) for denominator in
                       [rng.randint(1, MAX_RAW) for _ in range(128)])
        for numerator, denominator in vectors:
            with self.subTest(numerator=numerator, denominator=denominator):
                expected = ((numerator * (1 << 33) // denominator) + 1) // 2
                self.assertEqual(native_positive_ratio_division(numerator, denominator), expected)

    def test_three_module_midpoint_witnesses_flip_the_division_gate_relative_to_truncation(self):
        for operator in OPERATORS:
            result = recipient_native_ratio_diagnostic(public_recipient_ratio_payload(operator))
            row = result['rows'][1]
            boundary = 2147440698 if operator == 'char_196_sunbr' else 2147526598
            self.assertEqual(result['comparison_boundary_raw'], boundary)
            self.assertEqual(row['native_division_ratio_raw'], boundary)
            self.assertEqual(row['exact_rational_truncated_ratio_raw'], boundary - 1)
            self.assertFalse(row['division_stage_gate_reference'])
            self.assertTrue(row['exact_truncation_gate_reference'])
            self.assertEqual(row['native_minus_exact_truncation_raw'], 1)
            self.assertIsNone(row['declared_post_clamp_gate_reference'])
            self.assertIsNone(row['conditional_direct_healing_factor_from_declared_post_ratio'])

    def test_independent_post_ratio_controls_its_gate_without_substituting_the_native_quotient(self):
        query = public_recipient_ratio_payload()
        result = recipient_native_ratio_diagnostic(query)
        first, second = result['rows'][1:]
        self.assertFalse(second['post_clamp_matches_division_reference'])
        self.assertFalse(second['division_stage_gate_reference'])
        self.assertTrue(second['declared_post_clamp_gate_reference'])
        self.assertEqual(second['conditional_direct_healing_factor_from_declared_post_ratio'], 1.15)
        self.assertIsNone(first['declared_post_clamp_gate_reference'])
        self.assertFalse(result['division_output_used_as_post_clamp_ratio'])
        self.assertFalse(result['Clamp01_body_verified'])
        for row in result['rows']:
            self.assertIsNone(row['actual_get_hpRatio_raw'])
            self.assertIsNone(row['actual_recipient_qualification'])
        self.assertIsNone(result['actual_healing_total'])

    def test_integer_hp_is_shifted_exactly_and_boundary_search_reports_both_neighbors(self):
        query = public_recipient_ratio_payload()
        query['observations'] = [original('整数生命', 49998, 100000), original('极限整数生命', 1, MAX_INTEGER_HP)]
        result = recipient_native_ratio_diagnostic(query)
        for row in result['rows']:
            declaration = row['original_declaration']
            self.assertEqual(row['hp_raw_reference'], declaration['hp'] << 32)
            self.assertEqual(row['max_hp_raw_reference'], declaration['max_hp'] << 32)
            last = row['last_hp_value_under_division_stage_gate']
            following = row['first_hp_value_outside_division_stage_gate']
            self.assertEqual(following, last + 1)
            self.assertLess(native_positive_ratio_division(last << 32, declaration['max_hp'] << 32), result['comparison_boundary_raw'])
            self.assertGreaterEqual(native_positive_ratio_division(following << 32, declaration['max_hp'] << 32), result['comparison_boundary_raw'])
        self.assertEqual(result['rows'][0]['last_hp_value_under_division_stage_gate'], 49998)
        self.assertEqual(result['rows'][0]['first_hp_value_outside_division_stage_gate'], 49999)

    def test_raw_boundary_and_declared_observation_changes_are_explicit_witnesses(self):
        query = public_recipient_ratio_payload('char_2025_shu')
        boundary = ONE // 2 + 42950
        query['observations'] = [original('门前', boundary - 1, ONE, 'fp_raw', boundary - 1),
            original('门上', boundary, ONE, 'fp_raw', boundary)]
        result = recipient_native_ratio_diagnostic(query)
        self.assertTrue(result['rows'][0]['declared_post_clamp_gate_reference'])
        self.assertFalse(result['rows'][1]['declared_post_clamp_gate_reference'])
        witness = result['rows'][1]['transition_witness']
        self.assertEqual(witness['division_stage_raw_difference'], 1)
        self.assertTrue(witness['division_stage_gate_changed'])
        self.assertTrue(witness['declared_post_clamp_gate_changed'])
        self.assertFalse(witness['actual_runtime_transition_verified'])
        self.assertIsNone(witness['native_HP_trajectory_or_event_order'])
        self.assertEqual(result['rows'][1]['conditional_direct_healing_factor_from_declared_post_ratio'], 1)

    def test_locked_none_and_wrong_operator_modules_do_not_gain_qualification_factors(self):
        for cultivation in [{'elite': 1, 'level': 1, 'potential': 1, 'module_id': 'uniequip_002_sunbr', 'module_level': 1},
                            {'elite': 2, 'level': 39, 'potential': 1, 'module_id': 'uniequip_002_sunbr', 'module_level': 3},
                            {'elite': 2, 'level': 40, 'potential': 1, 'module_id': None, 'module_level': 0}]:
            query = public_recipient_ratio_payload()
            query['cultivation'] = cultivation
            result = recipient_native_ratio_diagnostic(query)
            self.assertFalse(result['cultivation']['module_unlock_reference'])
            self.assertIsNone(result['rows'][-1]['conditional_direct_healing_factor_from_declared_post_ratio'])
        query = public_recipient_ratio_payload()
        query['cultivation']['module_id'] = 'uniequip_002_shu'
        with self.assertRaises(ValueError):
            recipient_native_ratio_diagnostic(query)

    def test_all_module_stages_select_exact_source_trait_and_keep_HP_evidence_unverified(self):
        for operator in OPERATORS:
            for stage in (1, 2, 3):
                query = public_recipient_ratio_payload(operator)
                query['cultivation']['module_level'] = stage
                query['observations'][0]['evidence'] = {'kind': 'game_panel_declaration', 'source': '调用方声称的面板观察'}
                result = recipient_native_ratio_diagnostic(query)
                self.assertTrue(result['cultivation']['matching_source_trait_selected'])
                self.assertFalse(result['rows'][0]['source_HP_values_verified'])
                self.assertFalse(result['cultivation']['actual_module_attachment_verified'])

    def test_strict_original_value_and_source_declaration_validation(self):
        invalid = []
        for hp in [True, '1', 1.0, -1, math.inf, math.nan, MAX_INTEGER_HP + 1]:
            query = public_recipient_ratio_payload()
            query['observations'][0]['hp'] = hp
            invalid.append(query)
        for maximum in [0, True, 1.0, MAX_INTEGER_HP + 1]:
            query = public_recipient_ratio_payload()
            query['observations'][0]['max_hp'] = maximum
            invalid.append(query)
        for ratio in [True, 0.0, '0', -1, ONE + 1, math.nan]:
            query = public_recipient_ratio_payload()
            query['observations'][0]['post_clamp_ratio_raw'] = ratio
            invalid.append(query)
        for kind, source in [('unknown', 'source'), ('formula_reference', ''), ('formula_reference', '\n')]:
            query = public_recipient_ratio_payload()
            query['observations'][0]['evidence'] = {'kind': kind, 'source': source}
            invalid.append(query)
        for field, value in [('elite', True), ('level', 0), ('potential', 7), ('module_level', False)]:
            query = public_recipient_ratio_payload()
            query['cultivation'][field] = value
            invalid.append(query)
        query = public_recipient_ratio_payload()
        query['observations'][1]['label'] = query['observations'][0]['label']
        invalid.append(query)
        invalid.extend([None, {}, {**public_recipient_ratio_payload(), 'operator': 'mechanist'},
                        {**public_recipient_ratio_payload(), 'observations': []}])
        for query in invalid:
            with self.subTest(query=str(query)[:100]), self.assertRaises(ValueError):
                recipient_native_ratio_diagnostic(query)
        for hp, maximum in [(True, ONE), (0, 0), (ONE + 1, ONE), (0, MAX_RAW + 1)]:
            with self.assertRaises(ValueError):
                native_positive_ratio_division(hp, maximum)

    def test_source_unavailable_returns_unknown_quotient_and_post_gate_without_defaulting(self):
        with patch('rouge.recipient_native_ratio._source', return_value=None):
            result = recipient_native_ratio_diagnostic(public_recipient_ratio_payload())
        self.assertFalse(result['source_available'])
        self.assertIsNone(result['comparison_boundary_raw'])
        for row in result['rows']:
            self.assertIsNone(row['native_division_ratio_raw'])
            self.assertIsNone(row['division_stage_gate_reference'])
            self.assertIsNone(row['declared_post_clamp_gate_reference'])
            self.assertIsNone(row['conditional_direct_healing_factor_from_declared_post_ratio'])

    def test_declarations_results_and_observation_order_do_not_mutate_other_values(self):
        query = public_recipient_ratio_payload()
        before = copy.deepcopy(query)
        result = recipient_native_ratio_diagnostic(query)
        result['declaration']['observations'][0]['evidence']['source'] = 'changed'
        result['rows'][0]['original_declaration']['hp'] = 0
        self.assertEqual(query, before)
        self.assertEqual(recipient_native_ratio_diagnostic(query)['rows'][0]['original_declaration']['hp'], 49998)
        report = format_recipient_ratio_diagnostic(recipient_native_ratio_diagnostic(query))
        self.assertIn('独立后置原值未知', report)
        self.assertIn('仅除法阶段门参考', report)
        self.assertIn('实际get_hpRatio、受疗资格、HP轨迹和完整治疗：未知', report)


class RecipientRatioOriginalSourceTests(unittest.TestCase):
    def test_every_saved_division_instruction_and_integer_conversion_match_same_version_packet(self):
        import rouge
        root = Path(rouge.__file__).resolve().parents[1]
        candidate = Path(__file__).resolve().parents[1]
        source = json.loads((candidate / 'rouge/data/recipient-native-ratio-source.json').read_text())
        original = json.loads((root / 'research/p2-guardian-healing-gates-current/native-proof.json').read_text())
        self.assertEqual(source['game_dll_sha256'], original['game_dll_sha256'])
        methods = {m['method']['metadata_method_index']: m for m in original['methods']}
        for key, index in [('native_division', 220475), ('integer_to_FP_conversion', 220503)]:
            expected = [{k: i[k] for k in ['address', 'bytes', 'mnemonic', 'operands']} for i in methods[index]['instructions']]
            self.assertEqual(source[key]['instructions'], expected)
            self.assertFalse(methods[index]['limits'])
        self.assertEqual(len(source['native_division']['instructions']), 125)
        numeric = {i['address']: i for i in source['native_division']['instructions']}
        self.assertEqual(numeric['0x1866fd783']['operands'], 'ebp, 0x21')
        self.assertEqual(numeric['0x1866fd861']['operands'], 'rax, [r15 + 1]')
        self.assertEqual(numeric['0x1866fd865']['operands'], 'rax, 1')
        conversion = source['integer_to_FP_conversion']['instructions']
        self.assertIn('rax, 0x20', [i['operands'] for i in conversion if i['mnemonic'] == 'shl'])
        self.assertFalse(source['Clamp01_body_verified'])


os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
from PySide6.QtWidgets import QApplication
from rouge.recipient_native_ratio_view import RecipientNativeRatioPanel


class RecipientNativeRatioViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.panel = RecipientNativeRatioPanel()

    def tearDown(self):
        self.panel.close()
        self.panel.deleteLater()
        self.app.processEvents()

    def test_complete_integer_HP_input_and_independent_post_ratio_workflow(self):
        panel = self.panel
        panel.load_template.click()
        panel.label.setText('新整数面板参考')
        panel.hp.setText('50000')
        panel.maximum.setText('100000')
        panel.evidence_source.setText('独立整数面板参考声明')
        panel.append_observation.click()
        self.assertIsNone(panel.current_query()['observations'][-1]['post_clamp_ratio_raw'])
        panel.calculate_button.click()
        result = panel.result_snapshot()
        self.assertIsNone(result['rows'][-1]['conditional_direct_healing_factor_from_declared_post_ratio'])
        panel.label.setText('独立后置资格声明')
        panel.post_known.setChecked(True)
        panel.post_raw.setText(str(ONE // 2 - 42951))
        panel.append_observation.click()
        self.assertIsNone(panel.result_snapshot())
        panel.calculate_button.click()
        self.assertEqual(panel.result_snapshot()['rows'][-1]['conditional_direct_healing_factor_from_declared_post_ratio'], 1.15)
        self.assertIn('实际get_hpRatio', panel.result_view.toPlainText())
        panel.result_snapshot()['rows'].clear()
        self.assertEqual(len(panel.result_snapshot()['rows']), 5)

    def test_context_changes_preserve_edited_values_and_cross_operator_append_is_rejected(self):
        panel = self.panel
        panel.load_template.click()
        panel.calculate_button.click()
        before = (panel.editor.toPlainText(), panel.result_snapshot(), panel.result_view.toPlainText())
        panel.set_context({'operator': 'char_2025_shu'})
        self.assertEqual(before, (panel.editor.toPlainText(), panel.result_snapshot(), panel.result_view.toPlainText()))
        panel.append_observation.click()
        self.assertIn('作用域不符', panel.status.text())
        self.assertEqual(panel.editor.toPlainText(), before[0])

    def test_duplicate_nonfinite_and_invalid_original_values_clear_stale_outputs(self):
        panel = self.panel
        for text in ['{"operator":"char_196_sunbr","operator":"char_2025_shu"}',
                     '{"operator":"char_196_sunbr","cultivation":NaN,"observations":[]}',
                     json.dumps({**public_recipient_ratio_payload(), 'observations': []})]:
            panel.load_template.click()
            panel.calculate_button.click()
            self.assertIsNotNone(panel.result_snapshot())
            panel.editor.setPlainText(text)
            panel.calculate_button.click()
            self.assertIsNone(panel.result_snapshot())
            self.assertEqual(panel.result_view.toPlainText(), '')
        panel.load_template.click()
        panel.hp.setText('1.1')
        before = panel.editor.toPlainText()
        panel.append_observation.click()
        self.assertEqual(panel.editor.toPlainText(), before)
        self.assertIn('整数原文', panel.status.text())
