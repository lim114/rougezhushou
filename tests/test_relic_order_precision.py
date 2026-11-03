import copy
import importlib.util
import json
import math
import os
from pathlib import Path
import struct
import unittest
from unittest.mock import patch

from rouge.relic_order_precision import (IDS, precision_sources, supported_precision_sources,
    diagnose_relic_processing_order, public_relic_order_payload, format_relic_processing_order)


def family(result, key):
    return next(r for r in result['families'] if r['damage_family'] == key)


class RelicOrderPrecisionTests(unittest.TestCase):
    def test_magic_three_enumerates_exact_discrete_two_bit_outcomes_not_middle_bit(self):
        result = diagnose_relic_processing_order(public_relic_order_payload('magic'))
        row = family(result, 'magic')
        self.assertEqual(result['accepted_order_count'], 6)
        self.assertEqual(row['exact_decimal_reference_text'], '1.9')
        self.assertEqual(row['existing_decimal_model_reference'], 1.9)
        self.assertEqual([(v['bits'], v['accepted_order_count']) for v in row['discrete_outcomes']],
                         [('0x3ff33332', 4), ('0x3ff33334', 2)])
        self.assertEqual(row['minimum_f32'], 1.8999998569488525)
        self.assertEqual(row['maximum_f32'], 1.9000000953674316)
        self.assertEqual(row['bit_word_span'], 2)
        self.assertEqual(row['single_final_cast_of_exact_decimal_bits'], '0x3ff33333')
        self.assertNotIn(row['single_final_cast_of_exact_decimal_bits'], [v['bits'] for v in row['discrete_outcomes']])
        self.assertIsNone(result['declared_order_trace'])
        self.assertIsNone(result['actual_processing_order'])
        self.assertFalse(result['enumeration_counts_are_probabilities'])
        self.assertIsNone(result['actual_probability_by_order'])

    def test_physical_three_final_invariance_preserves_different_intermediate_bits(self):
        query = public_relic_order_payload('physical')
        result = diagnose_relic_processing_order(query)
        row = family(result, 'physical')
        self.assertEqual(row['distinct_outcome_count'], 1)
        self.assertEqual(row['minimum_bits'], '0x3fe00000')
        self.assertEqual(row['minimum_f32'], 1.75)
        self.assertEqual(row['range_width'], 0)
        self.assertEqual(row['discrete_outcomes'][0]['accepted_order_count'], 6)
        trace = diagnose_relic_processing_order({**query, 'declared_processing_order': list(IDS[:3])})['declared_order_trace']
        self.assertEqual(trace['steps'][1]['rounded_addition_bits'], '0x4019999a')
        self.assertEqual(trace['steps'][1]['group_result_bits'], '0x3fb33334')
        self.assertEqual(trace['steps'][1]['group_result_f32'], 1.4000000953674316)

    def test_first_source_is_copied_not_merged_against_implicit_one(self):
        result = diagnose_relic_processing_order({'relic_ids': [IDS[2]], 'declared_processing_order': [IDS[2]]})
        step = result['declared_order_trace']['steps'][0]
        self.assertTrue(step['first_group_record_is_copy'])
        self.assertIsNone(step['rounded_addition_f32'])
        self.assertIsNone(step['previous_group_f32'])
        self.assertEqual(step['group_result_bits'], '0x3faccccd')
        self.assertEqual(step['group_result_f32'], 1.350000023841858)
        self.assertEqual(family(result, 'physical')['distinct_outcome_count'], 1)

    def test_all_six_keep_two_exact_families_and_enumerate_every_accepted_permutation(self):
        result = diagnose_relic_processing_order(public_relic_order_payload('both'))
        self.assertEqual(result['accepted_order_count'], 720)
        self.assertEqual(result['unconstrained_distinct_order_count'], 720)
        self.assertEqual(len(result['order_outcomes']), 720)
        self.assertEqual(len({tuple(v['order']) for v in result['order_outcomes']}), 720)
        self.assertEqual(len(result['joint_outcomes']), 2)
        self.assertEqual(sorted(v['accepted_order_count'] for v in result['joint_outcomes']), [240, 480])
        self.assertEqual(family(result, 'physical')['minimum_f32'], 1.75)
        self.assertEqual([(v['bits'], v['accepted_order_count']) for v in family(result, 'magic')['discrete_outcomes']],
                         [('0x3ff33332', 480), ('0x3ff33334', 240)])
        self.assertNotIn('combined_family_factor', result)
        self.assertIsNone(result['actual_final_packet_factor'])
        self.assertIsNone(result['actual_damage'])

    def test_partial_order_constraints_close_family_range_without_claiming_probability(self):
        query = public_relic_order_payload('both')
        query['before_constraints'] = [[IDS[0], IDS[1]], [IDS[1], IDS[2]], [IDS[3], IDS[4]], [IDS[4], IDS[5]]]
        result = diagnose_relic_processing_order(query)
        self.assertEqual(result['accepted_order_count'], 20)
        self.assertEqual(family(result, 'magic')['minimum_bits'], '0x3ff33334')
        self.assertEqual(family(result, 'magic')['maximum_bits'], '0x3ff33334')
        self.assertEqual(len(result['joint_outcomes']), 1)
        self.assertFalse(result['runtime_acquisition_to_processing_order_verified'])
        for outcome in result['order_outcomes']:
            self.assertLess(outcome['order'].index(IDS[0]), outcome['order'].index(IDS[1]))
            self.assertLess(outcome['order'].index(IDS[3]), outcome['order'].index(IDS[4]))

    def test_explicit_trace_adds_and_subtracts_separately_in_selected_family(self):
        query = {'relic_ids': list(IDS[3:]), 'declared_processing_order': [IDS[3], IDS[5], IDS[4]]}
        result = diagnose_relic_processing_order(query)
        trace = result['declared_order_trace']
        self.assertEqual(trace['steps'][1]['rounded_addition_bits'], '0x40266666')
        self.assertEqual(trace['steps'][1]['group_result_bits'], '0x3fcccccc')
        self.assertEqual(trace['steps'][2]['rounded_addition_bits'], '0x40399999')
        self.assertEqual(trace['steps'][2]['group_result_bits'], '0x3ff33332')
        self.assertEqual(trace['steps'][2]['f32_minus_exact_decimal_text'], '-1.430511474609375E-7')
        self.assertTrue(all(row['actual_final_packet_factor'] is None for row in trace['steps']))

    def test_source_unavailable_keeps_count_but_no_factor_range_or_fake_zero(self):
        with patch('rouge.relic_order_precision.precision_sources', return_value=None):
            result = diagnose_relic_processing_order(public_relic_order_payload('magic'))
        self.assertFalse(result['source_available'])
        self.assertEqual(result['accepted_order_count'], 6)
        for key in ['families', 'order_outcomes', 'joint_outcomes', 'declared_order_trace']:
            self.assertIsNone(result[key])
        self.assertIn('参数数值及范围：未知', format_relic_processing_order(result))

    def test_changed_current_decimal_model_stays_unknown_without_changing_original_reference(self):
        with patch('rouge.relic_damage_factors.verified_rule', return_value=False):
            result = diagnose_relic_processing_order(public_relic_order_payload('magic'))
        row = family(result, 'magic')
        self.assertIsNone(row['existing_decimal_model_reference'])
        self.assertEqual(row['distinct_outcome_count'], 2)
        self.assertTrue(all(v['f32_minus_existing_decimal_model'] is None for v in row['discrete_outcomes']))

    def test_invalid_identity_duplicates_constraints_cycles_and_nonfinite_inputs_are_rejected(self):
        valid = public_relic_order_payload('magic')
        invalid = [None, [], {}, {**valid, 'damage_family': 'physical'}, {'relic_ids': []},
            {'relic_ids': list(IDS) + [IDS[0]]}, {'relic_ids': [IDS[0], IDS[0]]},
            {'relic_ids': [IDS[0], 'rogue_6_relic_legacy_11']}, {'relic_ids': ['unknown']},
            {'relic_ids': [True]}, {'relic_ids': [math.nan]}, {'relic_ids': [math.inf]},
            {**valid, 'declared_processing_order': [IDS[3]]},
            {**valid, 'declared_processing_order': [IDS[3], IDS[3], IDS[4]]},
            {**valid, 'declared_processing_order': [IDS[3], IDS[4], IDS[0]]},
            {**valid, 'declared_processing_order': True},
            {**valid, 'before_constraints': True}, {**valid, 'before_constraints': [[IDS[3], IDS[3]]]},
            {**valid, 'before_constraints': [[IDS[3], IDS[0]]]},
            {**valid, 'before_constraints': [[IDS[3], math.nan]]},
            {**valid, 'before_constraints': [[IDS[3], IDS[4]], [IDS[3], IDS[4]]]},
            {**valid, 'before_constraints': [[IDS[3], IDS[4]], [IDS[4], IDS[3]]]},
            {**valid, 'before_constraints': [[IDS[3], IDS[4]]], 'declared_processing_order': list(reversed(IDS[3:]))}]
        for query in invalid:
            with self.subTest(query=query), self.assertRaises(ValueError):
                diagnose_relic_processing_order(query)

    def test_declarations_and_fixed_source_records_are_not_mutated(self):
        query = public_relic_order_payload('magic')
        query['declared_processing_order'] = list(IDS[3:])
        before = copy.deepcopy(query)
        result = diagnose_relic_processing_order(query)
        result['declaration']['relic_ids'].clear()
        result['declared_order_trace']['steps'][0]['groups_after_step'].clear()
        self.assertEqual(query, before)
        fresh = diagnose_relic_processing_order(query)
        self.assertEqual(fresh['declared_order_trace']['steps'][0]['group_result_bits'], '0x3f99999a')
        sources = precision_sources()
        sources['records'][0]['parameter'] = 99
        self.assertEqual(supported_precision_sources()[0]['parameter'], 1.15)

    def test_public_report_exposes_full_precision_and_different_unknowns(self):
        result = diagnose_relic_processing_order(public_relic_order_payload('magic'))
        report = format_relic_processing_order(result)
        self.assertIn('1.8999998569488525', report)
        self.assertIn('0x3ff33332', report)
        self.assertIn('不替用户选择实际顺序', report)
        self.assertIn('不是概率', report)
        self.assertIn('物理与法术分别合并', report)
        self.assertIn('实际处理顺序、获取到处理顺序绑定、最终FP包及实际伤害：未知', report)


class RelicOrderPrecisionSourceTests(unittest.TestCase):
    def test_derived_source_rebuilds_from_sealed_six_specific_records(self):
        root = Path(__file__).resolve().parents[1]
        spec = importlib.util.spec_from_file_location('build_precision_source', root / 'scripts/build_relic_order_precision_source.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.assertEqual(module.build(), precision_sources())
        self.assertEqual([r['relic_id'] for r in precision_sources()['records']], list(IDS))
        self.assertEqual({r['damage_family'] for r in precision_sources()['records']}, {'physical', 'magic'})

    def test_complete_original_compositor_has_same_group_dispatch_and_two_single_precision_operations(self):
        root = Path(__file__).resolve().parents[1]
        proof = json.loads((root / 'research/p2-relic-damage-composition-current/native-proof.json').read_text())
        metadata = json.loads((root / 'research/p2-relic-damage-composition-current/selected-metadata.json').read_text())
        self.assertEqual(proof['game_dll_sha256'], precision_sources()['game_dll_sha256'])
        self.assertEqual(proof['metadata_sha256'], metadata['metadata_sha256'])
        methods = {r['method']['metadata_method_index']: r for r in proof['methods']}
        for index in [30846, 85907, 85522]:
            self.assertFalse(methods[index]['limits'])
        instructions = {r['address']: r for r in methods[30846]['instructions']}
        self.assertEqual((instructions['0x18231d668']['mnemonic'], instructions['0x18231d671']['mnemonic']), ('addss', 'subss'))
        literal = instructions['0x18231d527']['rip_data'][0]
        self.assertEqual(literal['bytes8'][:8], '0000803f')
        self.assertEqual(struct.unpack('<f', bytes.fromhex(literal['bytes8'][:8]))[0], 1)


os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
from PySide6.QtWidgets import QApplication
from rouge.relic_order_precision_view import RelicOrderPrecisionPanel


class RelicOrderPrecisionViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.panel = RelicOrderPrecisionPanel()

    def tearDown(self):
        self.panel.close()
        self.panel.deleteLater()
        self.app.processEvents()

    def test_enumeration_inspection_does_not_implicitly_write_a_processing_order(self):
        panel = self.panel
        panel.load_template.click()
        panel.calculate_button.click()
        self.assertEqual(panel.order_selector.count(), 6)
        before = panel.editor.toPlainText()
        panel.order_selector.setCurrentIndex(4)
        self.assertEqual(panel.editor.toPlainText(), before)
        self.assertIsNone(panel.result_snapshot()['declared_processing_order'])
        self.assertIn('逐步', panel.order_detail.accessibleName())
        self.assertIn('0x', panel.order_detail.toPlainText())
        chosen = panel.order_selector.currentData()
        panel.declare_viewed_order.click()
        self.assertEqual(panel.current_query()['declared_processing_order'], chosen)
        self.assertIsNone(panel.result_snapshot())
        panel.calculate_button.click()
        self.assertEqual(panel.result_snapshot()['declared_order_trace']['order'], chosen)

    def test_explicit_constraints_restrict_orders_and_context_preserves_user_work(self):
        panel = self.panel
        panel.load_template.click()
        panel.add_constraint.click()
        panel.calculate_button.click()
        self.assertEqual(panel.result_snapshot()['accepted_order_count'], 3)
        before = (panel.editor.toPlainText(), panel.result_snapshot(), panel.result_view.toPlainText())
        panel.set_context({'relic_ids': [IDS[0], IDS[1]]})
        self.assertEqual(before, (panel.editor.toPlainText(), panel.result_snapshot(), panel.result_view.toPlainText()))
        panel.before.setCurrentIndex(panel.before.findData(IDS[4]))
        panel.after.setCurrentIndex(panel.after.findData(IDS[3]))
        panel.add_constraint.click()
        self.assertEqual(panel.editor.toPlainText(), before[0])
        self.assertIn('循环冲突', panel.status.text())

    def test_invalid_or_duplicate_json_clears_numerical_results_and_source_unavailable_stays_unknown(self):
        panel = self.panel
        for text in ['{"relic_ids":[],"relic_ids":[]}', '{"relic_ids":NaN}', '{"relic_ids":["unknown"]}']:
            panel.load_template.click()
            panel.calculate_button.click()
            self.assertIsNotNone(panel.result_snapshot())
            panel.editor.setPlainText(text)
            panel.calculate_button.click()
            self.assertIsNone(panel.result_snapshot())
            self.assertEqual(panel.order_selector.count(), 0)
            self.assertEqual(panel.result_view.toPlainText(), '')
        panel.load_template.click()
        with patch('rouge.relic_order_precision.precision_sources', return_value=None):
            panel.calculate_button.click()
        self.assertFalse(panel.result_snapshot()['source_available'])
        self.assertEqual(panel.order_selector.count(), 0)
        self.assertFalse(panel.declare_viewed_order.isEnabled())
        self.assertIn('数值和范围保持未知', panel.status.text())
