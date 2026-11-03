from copy import deepcopy
import json
import math
import unittest

from rouge.calibration import panel_layers
from rouge.paired_calibration import compare_paired_panels, public_paired_payload


def field(result, name):
    return next(row for row in result['rows'] if row['field'] == name)


class PairedCalibrationTests(unittest.TestCase):
    def setUp(self):
        self.payload = public_paired_payload()

    def compare(self, payload=None):
        return compare_paired_panels(**(self.payload if payload is None else payload))

    def test_three_source_qualified_formula_pairs_keep_literal_oracles_and_limits(self):
        expected = {'mechanist': ('attack', 143), 'kaltsit': ('hp', 1325), 'silverash': ('defense', 60)}
        for operator, (key, delta) in expected.items():
            with self.subTest(operator=operator):
                result = self.compare(public_paired_payload(operator))
                row = field(result, key)
                self.assertEqual(row['observed_after_minus_before'], delta)
                self.assertEqual(row['model_after_minus_before'], delta)
                self.assertEqual(row['delta_residual'], 0)
                self.assertTrue(result['all_paired_absolute_values_match'])
                self.assertEqual(result['evidence_kind'], 'formula_reference')
                self.assertEqual(result['source']['commit'], 'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add')
                self.assertFalse(result['native_verified'])
                self.assertIsNone(result['actual_causal_attribution'])

    def test_signed_observation_difference_and_residual_locate_changed_offset(self):
        self.payload['before']['observation']['values']['attack'] = 580
        self.payload['after']['observation']['values']['attack'] = 700
        row = field(self.compare(), 'attack')
        self.assertEqual((row['observed_after_minus_before'], row['model_after_minus_before'], row['delta_residual']), (120, 143, -23))
        self.assertEqual((row['before_observation_minus_model'], row['after_observation_minus_model']), (7, -16))
        self.assertEqual(row['diagnostic_status'], 'delta_mismatch')
        self.assertIsNone(row['actual_cause_of_residual'])

    def test_matching_delta_does_not_hide_equal_absolute_errors(self):
        for side in ('before', 'after'):
            self.payload[side]['observation']['values']['attack'] += 10
        result = self.compare()
        self.assertTrue(result['all_compared_deltas_match'])
        self.assertFalse(result['all_paired_absolute_values_match'])
        self.assertEqual(field(result, 'attack')['diagnostic_status'], 'delta_matches_but_absolute_panels_differ')

    def test_only_shared_observed_fields_are_compared_without_zero_filling(self):
        del self.payload['after']['observation']['values']['defense']
        self.payload['after']['observation']['values']['hp'] = 3422
        result = self.compare()
        self.assertEqual([row['field'] for row in result['rows']], ['attack'])
        self.assertEqual(result['before_only_fields'], ['defense'])
        self.assertEqual(result['after_only_fields'], ['hp'])
        self.assertEqual(result['shared_field_count'], 1)

    def test_common_unknown_model_field_retains_observed_delta_but_unknown_residual(self):
        for side, value in (('before', 10), ('after', 12)):
            record = self.payload[side]
            record['observation']['panel'] = '技能期间参考'
            record['observation']['values'] = {'hp': value}
        result = self.compare()
        row = field(result, 'hp')
        self.assertEqual(row['observed_after_minus_before'], 2)
        self.assertIsNone(row['model_after_minus_before'])
        self.assertIsNone(row['delta_residual'])
        self.assertIsNone(row['delta_matches_declared_tolerance'])
        self.assertIsNone(row['both_absolute_values_match_declared_tolerance'])
        self.assertEqual(result['known_model_delta_count'], 0)
        self.assertFalse(result['all_compared_deltas_match'])
        self.assertEqual(row['diagnostic_status'], 'model_field_unknown')

    def test_removed_relic_has_negative_delta_and_existing_diagnostic_link(self):
        self.payload['before'], self.payload['after'] = self.payload['after'], self.payload['before']
        result = self.compare()
        self.assertEqual(field(result, 'attack')['observed_after_minus_before'], -143)
        transition = result['relic_transition']
        self.assertTrue(transition['available'])
        self.assertEqual(transition['removed_relic_ids'], ['rogue_6_relic_legacy_16'])
        self.assertIsNone(transition['after_diagnostics'])
        row = next(r for r in transition['before_diagnostics']['combination_rows']
                   if r['panel'] == result['panel'] and r['field'] == 'attack')
        self.assertEqual(row['combined_model_difference'], 143)
        self.assertIsNone(row['actual_combination_effect'])

    def test_relic_transition_reuses_diagnostics_and_preserves_independent_targeted_buffs(self):
        for side in ('before', 'after'):
            record = self.payload[side]
            record['scenario']['char_buff_ids'] = ['rogue_6_from_relic_13']
            record['scenario']['char_buffs_complete'] = True
            record['observation']['context_token'] = panel_layers(record['scenario'])['context_token']
        transition = self.compare()['relic_transition']
        self.assertTrue(transition['available'])
        self.assertEqual(transition['after_diagnostics']['preserved_targeted_buff_ids'], ['rogue_6_from_relic_13'])
        self.assertIsNone(transition['actual_causal_attribution'])

    def test_other_condition_changes_block_relic_only_attribution(self):
        record = self.payload['after']
        record['scenario']['potential'] = 4
        record['observation']['context_token'] = panel_layers(record['scenario'])['context_token']
        result = self.compare()
        self.assertEqual([r['field'] for r in result['changed_conditions']], ['potential', 'relic_ids'])
        self.assertFalse(result['relic_transition']['available'])
        self.assertEqual(result['relic_transition']['reason'], 'other_declared_conditions_changed')
        self.assertIsNone(result['actual_causal_attribution'])

    def test_tolerance_applies_to_residual_without_summing_two_absolute_tolerances(self):
        self.payload['tolerance'] = 1
        self.payload['before']['observation']['values']['attack'] -= 1
        self.payload['after']['observation']['values']['attack'] += 1
        row = field(self.compare(), 'attack')
        self.assertTrue(row['both_absolute_values_match_declared_tolerance'])
        self.assertFalse(row['delta_matches_declared_tolerance'])
        self.payload['after']['observation']['values']['attack'] -= 1
        self.assertTrue(field(self.compare(), 'attack')['delta_matches_declared_tolerance'])

    def test_both_observation_tokens_must_match_their_own_conditions(self):
        for side in ('before', 'after'):
            payload = deepcopy(self.payload)
            payload[side]['observation']['context_token'] = payload['after' if side == 'before' else 'before']['observation']['context_token']
            with self.subTest(side=side), self.assertRaises(ValueError):
                self.compare(payload)

    def test_cross_operator_cross_panel_and_cross_evidence_kind_are_rejected(self):
        for change in ('operator', 'panel', 'kind'):
            payload = deepcopy(self.payload)
            if change == 'operator':
                payload['after'] = public_paired_payload('kaltsit')['after']
            elif change == 'panel':
                payload['after']['observation']['panel'] = '培养与模组'
            else:
                payload['after']['observation']['evidence_kind'] = 'game_panel'
            with self.subTest(change=change), self.assertRaises(ValueError):
                self.compare(payload)

    def test_public_case_and_declared_game_sources_remain_unverified(self):
        for kind in ('public_case', 'game_panel'):
            payload = deepcopy(self.payload)
            for side in ('before', 'after'):
                payload[side]['observation']['evidence_kind'] = kind
                payload[side]['observation']['source'] = 'independent ' + side + ' source'
            result = self.compare(payload)
            self.assertEqual(result['evidence_kind'], kind)
            self.assertFalse(result['native_verified'])
            self.assertEqual(result['before']['comparison']['source'], 'independent before source')
            self.assertEqual(result['after']['comparison']['source'], 'independent after source')

    def test_no_common_fields_empty_records_and_missing_sources_fail(self):
        variants = []
        a = deepcopy(self.payload)
        a['after']['observation']['values'] = {'hp': 3000}
        variants.append(a)
        for side in ('before', 'after'):
            a = deepcopy(self.payload)
            a[side]['observation']['values'] = {}
            variants.append(a)
            a = deepcopy(self.payload)
            a[side]['observation']['source'] = '  '
            variants.append(a)
        for payload in variants:
            with self.assertRaises(ValueError):
                self.compare(payload)

    def test_invalid_one_sided_numbers_are_validated_before_intersection(self):
        for value in (True, '765', None, -1, math.nan, math.inf):
            payload = deepcopy(self.payload)
            del payload['after']['observation']['values']['defense']
            payload['before']['observation']['values']['defense'] = value
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.compare(payload)
        for tolerance in (True, -1, math.inf, math.nan):
            with self.subTest(tolerance=tolerance), self.assertRaises(ValueError):
                compare_paired_panels(self.payload['before'], self.payload['after'], tolerance)

    def test_record_contract_internal_inputs_and_unknown_fields_fail(self):
        for mutate in ('extra', 'missing', 'internal', 'field'):
            payload = deepcopy(self.payload)
            if mutate == 'extra':
                payload['before']['private_state'] = {}
            elif mutate == 'missing':
                del payload['before']['observation']
            elif mutate == 'internal':
                payload['before']['scenario']['_attribute_runes'] = []
            else:
                payload['before']['observation']['values']['mystery'] = 1
            with self.subTest(mutate=mutate), self.assertRaises(ValueError):
                self.compare(payload)

    def test_same_context_keeps_two_independent_observations_and_detached_outputs(self):
        self.payload['after'] = deepcopy(self.payload['before'])
        self.payload['after']['observation']['source'] = 'independent second source'
        initial = deepcopy(self.payload)
        first, second = self.compare(), self.compare()
        self.assertEqual(initial, self.payload)
        self.assertEqual(field(first, 'attack')['observed_after_minus_before'], 0)
        self.assertEqual(first['changed_conditions'], [])
        self.assertEqual(first['relic_transition']['reason'], 'no_declared_condition_change')
        first['before']['model']['panels'].clear()
        self.assertTrue(second['before']['model']['panels'])
        self.assertEqual(first['after']['comparison']['source'], 'independent second source')


class PairedCalibrationViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from PySide6.QtWidgets import QApplication
        cls.qt = QApplication.instance() or QApplication([])

    def setUp(self):
        from rouge.paired_calibration_view import PairedCalibrationPanel
        self.panel = PairedCalibrationPanel()
        self.panel.resize(1100, 850)
        self.panel.show()
        self.qt.processEvents()

    def tearDown(self):
        self.panel.close()
        self.panel.deleteLater()
        self.qt.processEvents()

    def test_actual_widget_runs_and_renders_signed_delta_unknown_cause_and_two_sources(self):
        self.panel.run_button.click()
        result = self.panel.result_snapshot()
        self.assertIsNotNone(result, self.panel.status.text())
        text = self.panel.result_view.toPlainText()
        for label in ('首批三名前后成对面板校准', '前组来源', '后组来源', '+143', '差值残差',
                      '前组绝对偏差', '非相加模型残差', '未知', '未认证实机'):
            self.assertIn(label, text)
        self.assertFalse(result['native_verified'])
        result['rows'].clear()
        self.assertTrue(self.panel.result_snapshot()['rows'])

    def test_scenario_refresh_and_layer_query_preserve_all_observations_and_results(self):
        self.panel.run_button.click()
        initial = (self.panel.before_editor.toPlainText(), self.panel.after_editor.toPlainText(), self.panel.result_snapshot())
        self.panel.set_scenario({'operator': 'kaltsit', 'skill': 2})
        self.panel.before_layers_button.click()
        self.panel.after_layers_button.click()
        self.assertEqual(initial, (self.panel.before_editor.toPlainText(), self.panel.after_editor.toPlainText(), self.panel.result_snapshot()))
        self.assertIn('context_token', self.panel.context_view.toPlainText())

    def test_explicit_import_keeps_observation_then_explicit_binding_keeps_values_and_source(self):
        before = json.loads(self.panel.before_editor.toPlainText())
        scenario = {'operator': 'mechanist', 'skill': 3, 'charge_count': 0, 'potential': 4}
        self.panel.set_scenario(scenario)
        scenario['potential'] = 1
        self.panel.before_import_button.click()
        imported = json.loads(self.panel.before_editor.toPlainText())
        self.assertEqual(imported['scenario']['potential'], 4)
        self.assertEqual(imported['observation'], before['observation'])
        self.panel.run_button.click()
        self.assertIsNone(self.panel.result_snapshot())
        self.assertIn('条件不一致', self.panel.status.text())
        self.panel.before_bind_button.click()
        bound = json.loads(self.panel.before_editor.toPlainText())
        self.assertEqual(bound['observation']['values'], before['observation']['values'])
        self.assertEqual(bound['observation']['source'], before['observation']['source'])
        self.assertNotEqual(bound['observation']['context_token'], before['observation']['context_token'])
        self.panel.run_button.click()
        self.assertIsNotNone(self.panel.result_snapshot(), self.panel.status.text())

    def test_public_template_selection_does_not_replace_evidence_until_explicit_load(self):
        previous = self.panel.before_editor.toPlainText()
        self.panel.template.setCurrentIndex(1)
        self.assertEqual(self.panel.before_editor.toPlainText(), previous)
        self.panel.load_template.click()
        self.panel.run_button.click()
        self.assertEqual(field(self.panel.result_snapshot(), 'hp')['observed_after_minus_before'], 1325)
        self.panel.template.setCurrentIndex(2)
        self.panel.load_template.click()
        self.panel.run_button.click()
        self.assertEqual(field(self.panel.result_snapshot(), 'defense')['observed_after_minus_before'], 60)

    def test_failure_clears_old_result_and_does_not_change_entered_evidence(self):
        self.panel.run_button.click()
        record = json.loads(self.panel.after_editor.toPlainText())
        record['observation']['evidence_kind'] = 'game_panel'
        entered = json.dumps(record, ensure_ascii=False)
        self.panel.after_editor.setPlainText(entered)
        self.panel.run_button.click()
        self.assertIsNone(self.panel.result_snapshot())
        self.assertEqual(self.panel.result_view.toPlainText(), '')
        self.assertEqual(self.panel.after_editor.toPlainText(), entered)
        self.assertIn('来源类别必须一致', self.panel.status.text())

    def test_renderer_escapes_source_markup_and_highlights_offset_cancellation(self):
        from rouge.paired_calibration_view import paired_calibration_html
        payload = public_paired_payload()
        for side in ('before', 'after'):
            payload[side]['observation']['values']['attack'] += 10
            payload[side]['observation']['source'] = '<script>private?</script>'
        rendered = paired_calibration_html(compare_paired_panels(**payload))
        self.assertNotIn('<script>', rendered)
        self.assertIn('&lt;script&gt;', rendered)
        self.assertIn('差值相符，但两端绝对面板存在偏差', rendered)


if __name__ == '__main__':
    unittest.main()
