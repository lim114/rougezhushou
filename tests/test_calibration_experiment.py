from copy import deepcopy
from fractions import Fraction
import json
import math
import unittest

from rouge.calibration_experiment import calibration_experiment, public_experiment_payload, _intersection
from rouge.bounded_calibration import _interval
from rouge.calibration import panel_layers


class CalibrationExperimentTests(unittest.TestCase):
    def setUp(self):
        self.payload = public_experiment_payload()

    def compare(self, payload=None):
        return calibration_experiment(**(self.payload if payload is None else payload))

    def sample(self, index):
        return self.payload['experiment']['records'][index]

    def attack(self, index, lo, hi=None):
        self.sample(index)['data']['observation']['values']['attack'] = [lo, lo if hi is None else hi]

    def test_three_operators_panel_and_three_skill_formula_experiments(self):
        for operator in ('kaltsit', 'silverash', 'mechanist'):
            for kind, offset in (('panel', 5), ('timing', 2)):
                with self.subTest(operator=operator, kind=kind):
                    result = self.compare(public_experiment_payload(operator, kind))
                    self.assertEqual(result['training_state'], 'compatible')
                    self.assertEqual(result['training_hypothesis_range']['lower'], offset)
                    self.assertEqual(result['training_hypothesis_range']['upper'], offset)
                    self.assertEqual(result['overall_state'], 'compatible_on_declared_ranges')
                    self.assertEqual(result['held_out_checks'][0]['state'], 'all_training_candidates_allowed')
                    self.assertFalse(result['native_verified'])
                    self.assertIsNone(result['engine_correction'])
                    self.assertIsNone(result['actual_cause_of_difference'])
                    self.assertEqual(result['source']['commit'], 'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add')
                    self.assertTrue(all(record['evidence_version'] == result['evidence_version'] for record in result['records']))

    def test_training_contradiction_gives_two_actual_record_ids_as_witness(self):
        self.attack(0, 548)
        self.attack(1, 565)
        result = self.compare()
        self.assertEqual(result['training_state'], 'contradicted')
        self.assertIsNone(result['training_hypothesis_range'])
        self.assertEqual(set(result['training_contradiction_witness']['record_ids']), {'level60', 'level75'})
        self.assertEqual(result['held_out_checks'][0]['state'], 'training_unavailable')

    def test_held_out_contradiction_does_not_retrain_or_hide_failure(self):
        result = self.compare(public_experiment_payload(variant='held_out_conflict'))
        self.assertEqual(result['training_hypothesis_range']['lower'], 5)
        self.assertEqual(result['training_state'], 'compatible')
        self.assertEqual(result['held_out_checks'][0]['state'], 'no_overlap')
        self.assertIsNone(result['held_out_checks'][0]['remaining_hypothesis_range'])
        self.assertIn('level90', result['held_out_checks'][0]['contradiction_witness']['record_ids'])
        self.assertEqual(result['overall_state'], 'contradicted')
        self.assertIsNone(result['overall_hypothesis_range'])
        self.assertIsNone(result['engine_correction'])

    def test_partial_holdout_overlap_refines_hypothesis_only(self):
        self.attack(0, 547, 549)
        self.attack(1, 562, 564)
        self.attack(2, 578, 580)
        result = self.compare()
        self.assertEqual((result['training_hypothesis_range']['lower'], result['training_hypothesis_range']['upper']), (4, 6))
        check = result['held_out_checks'][0]
        self.assertEqual(check['state'], 'possible_overlap_only')
        self.assertEqual((check['remaining_hypothesis_range']['lower'], check['remaining_hypothesis_range']['upper']), (5, 6))
        self.assertEqual(result['overall_hypothesis_range']['lower'], 5)

    def test_multiple_individually_overlapping_holdouts_can_still_jointly_conflict(self):
        self.attack(0, 543, 553)
        self.attack(1, 558, 568)
        self.attack(2, 573, 577)
        extra = deepcopy(self.sample(2))
        extra['id'] = 'level90-second'
        extra['data']['observation']['values']['attack'] = [579, 583]
        self.payload['experiment']['records'].append(extra)
        result = self.compare()
        self.assertEqual([check['state'] for check in result['held_out_checks']], ['possible_overlap_only', 'possible_overlap_only'])
        self.assertEqual(result['overall_state'], 'contradicted')
        self.assertEqual(set(result['overall_contradiction_witness']['record_ids']), {'level90', 'level90-second'})

    def test_open_endpoint_common_residual_intersection_has_no_guessed_epsilon(self):
        a = _interval(Fraction(0), Fraction(1), False, True)
        b = _interval(Fraction(0), Fraction(0))
        shared, witness = _intersection([('strict', a), ('point', b)])
        self.assertIsNone(shared)
        self.assertEqual(set(witness['record_ids']), {'strict', 'point'})
        c = _interval(Fraction(1, 3), Fraction(2, 3), True, False)
        shared, witness = _intersection([('open', a), ('rational', c)])
        self.assertIsNone(witness)
        self.assertEqual(shared['lower_exact'], '1/3')
        self.assertEqual(shared['upper_exact'], '2/3')
        self.assertFalse(shared['upper_inclusive'])

    def test_undeclared_control_change_blocks_record_and_whole_combined_claim(self):
        result = self.compare(public_experiment_payload(variant='control_drift'))
        self.assertEqual(result['training_state'], 'compatible')
        self.assertEqual(result['overall_state'], 'blocked')
        held = result['records'][2]
        self.assertIn('undeclared_control_change', held['blocking_reasons'])
        potential = next(r for r in held['changed_controls'] if r['field'] == 'potential')
        self.assertFalse(potential['allowed_to_vary'])
        self.assertEqual(result['held_out_checks'][0]['state'], 'record_blocked')
        self.assertIsNone(result['overall_hypothesis_range'])

    def test_blocked_training_is_never_silently_dropped(self):
        self.sample(0)['evidence_version'] = 'different declared version'
        result = self.compare()
        self.assertEqual(result['training_state'], 'blocked')
        self.assertEqual(result['blocked_training_record_ids'], ['level60'])
        self.assertIsNone(result['training_hypothesis_range'])
        self.assertEqual(len(result['records']), 3)
        self.assertIn('caller_evidence_version_mismatch', result['records'][0]['blocking_reasons'])

    def test_mixed_evidence_category_blocks_experiment_without_relabeling_sources(self):
        self.sample(1)['data']['observation']['evidence_kind'] = 'game_panel'
        self.sample(1)['data']['observation']['source'] = 'caller declared game panel sample'
        result = self.compare()
        self.assertEqual(result['training_state'], 'blocked')
        self.assertEqual(result['records'][1]['source'], 'caller declared game panel sample')
        self.assertIn('evidence_kind_mismatch', result['records'][1]['blocking_reasons'])
        self.assertFalse(result['native_verified'])

    def test_bad_context_or_numeric_data_stays_visible_and_blocks_training(self):
        for change in ('token', 'nonfinite', 'source'):
            payload = deepcopy(self.payload)
            observation = payload['experiment']['records'][0]['data']['observation']
            if change == 'token':
                observation['context_token'] = 'wrong'
            elif change == 'nonfinite':
                observation['values']['attack'] = [548, math.nan]
            else:
                observation['source'] = ' '
            with self.subTest(change=change):
                result = self.compare(payload)
                self.assertEqual(result['training_state'], 'blocked')
                self.assertIn('record_validation_error', result['records'][0]['blocking_reasons'])
                self.assertTrue(result['records'][0]['validation_error'])
                self.assertIsNone(result['training_hypothesis_range'])

    def test_missing_field_and_unknown_model_do_not_become_zero_residual(self):
        self.sample(0)['data']['observation']['values'] = {'defense': [543, 543]}
        result = self.compare()
        self.assertIn('selected_field_not_recorded', result['records'][0]['blocking_reasons'])
        self.assertIsNone(result['records'][0]['residual_interval'])
        self.payload = public_experiment_payload(channel_kind='timing')
        self.payload['experiment']['channel']['metric'] = 'active_duration'
        result = self.compare()
        self.assertEqual(result['training_state'], 'blocked')
        self.assertTrue(all(record['residual_interval'] is None for record in result['records']))

    def test_same_context_repeated_conflicting_values_are_retained_and_explainable(self):
        repeated = deepcopy(self.sample(0))
        repeated['id'] = 'repeat-level60'
        repeated['role'] = 'held_out'
        repeated['data']['observation']['values']['attack'] = [550, 550]
        self.payload['experiment']['records'].append(repeated)
        result = self.compare()
        self.assertEqual(result['overall_state'], 'contradicted')
        first = result['records'][0]
        repeat = result['records'][-1]
        self.assertEqual(first['same_context_repeat_ids'], ['repeat-level60'])
        self.assertIn('level60', repeat['same_context_repeat_ids'])
        self.assertEqual(repeat['observed_interval']['lower'], 550)

    def test_without_holdout_training_claim_is_marked_missing_review(self):
        self.payload['experiment']['records'].pop()
        result = self.compare()
        self.assertTrue(result['held_out_evidence_missing'])
        self.assertEqual(result['held_out_record_count'], 0)
        self.assertEqual(result['held_out_checks'], [])
        self.assertFalse(result['native_verified'])

    def test_role_counts_duplicate_ids_invalid_headers_and_channels_are_rejected(self):
        variants = []
        for key, value in (('hypothesis', 'fit_any_mechanism'), ('varying_fields', ['operator']),
                           ('varying_fields', ['level', 'level']), ('evidence_version', ' '), ('operator', 'other')):
            payload = deepcopy(self.payload)
            payload['experiment'][key] = value
            variants.append(payload)
        payload = deepcopy(self.payload)
        payload['experiment']['records'][1]['id'] = 'level60'
        variants.append(payload)
        payload = deepcopy(self.payload)
        payload['experiment']['records'][1]['role'] = 'held_out'
        variants.append(payload)
        payload = deepcopy(self.payload)
        payload['experiment']['channel']['field'] = 'private_guess'
        variants.append(payload)
        for payload in variants:
            with self.assertRaises(ValueError):
                self.compare(payload)

    def test_actual_game_declarations_remain_unauthenticated_and_record_sources_are_distinct(self):
        experiment = self.payload['experiment']
        experiment['evidence_kind'] = 'game_panel'
        experiment['evidence_version'] = 'caller-current-build'
        for index, record in enumerate(experiment['records']):
            record['evidence_version'] = 'caller-current-build'
            record['data']['observation'].update(evidence_kind='game_panel', source='independent caller recording ' + str(index))
        result = self.compare()
        self.assertEqual(result['overall_state'], 'compatible_on_declared_ranges')
        self.assertEqual(len({r['source'] for r in result['records']}), 3)
        self.assertTrue(result['version_is_caller_declaration'])
        self.assertFalse(result['native_verified'])

    def test_inputs_results_and_source_snapshots_are_isolated(self):
        before = deepcopy(self.payload)
        a, b = self.compare(), self.compare()
        self.assertEqual(before, self.payload)
        a['records'][0]['declared_observation'].clear()
        a['source']['files'].clear()
        self.assertTrue(b['records'][0]['declared_observation'])
        self.assertTrue(b['source']['files'])


class CalibrationExperimentViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from PySide6.QtWidgets import QApplication
        cls.qt = QApplication.instance() or QApplication([])

    def setUp(self):
        from rouge.calibration_experiment_view import CalibrationExperimentPanel
        self.panel = CalibrationExperimentPanel()
        self.panel.resize(1200, 920)
        self.panel.show()
        self.qt.processEvents()

    def tearDown(self):
        self.panel.close()
        self.panel.deleteLater()
        self.qt.processEvents()

    def test_actual_widget_runs_and_renders_joint_hypothesis_roles_and_limits(self):
        self.panel.run_button.click()
        result = self.panel.result_snapshot()
        self.assertIsNotNone(result, self.panel.status.text())
        text = self.panel.result_view.toPlainText()
        for phrase in ('多记录实验共同残差假设与留出复核', '[5, 5]', '训练', '留出', '原生认证：否', '没有拟合或回写修正'):
            self.assertIn(phrase, text)
        result['records'].clear()
        self.assertTrue(self.panel.result_snapshot()['records'])

    def test_record_drafts_survive_switching_and_enter_calculation_only_after_explicit_save(self):
        draft = json.loads(self.panel.record_editor.toPlainText())
        draft['data']['observation']['values']['attack'] = [551, 551]
        entered = json.dumps(draft, ensure_ascii=False)
        self.panel.record_editor.setPlainText(entered)
        self.panel.record_choice.setCurrentIndex(1)
        self.panel.record_choice.setCurrentIndex(0)
        self.assertEqual(self.panel.record_editor.toPlainText(), entered)
        self.panel.run_button.click()
        self.assertEqual(self.panel.result_snapshot()['training_state'], 'compatible')
        self.assertIn('未保存草稿', self.panel.status.text())
        self.panel.save_record_button.click()
        self.assertIsNone(self.panel.result_snapshot())
        self.panel.run_button.click()
        self.assertEqual(self.panel.result_snapshot()['training_state'], 'contradicted')

    def test_explicit_role_change_preserves_record_data_and_cannot_hide_insufficient_training(self):
        before = json.loads(self.panel.record_editor.toPlainText())
        self.panel.role_choice.setCurrentIndex(1)
        self.panel.apply_role_button.click()
        after = json.loads(self.panel.editor.toPlainText())['experiment']['records'][0]
        self.assertEqual(after['data'], before['data'])
        self.assertEqual(after['role'], 'held_out')
        self.panel.run_button.click()
        self.assertIsNone(self.panel.result_snapshot())
        self.assertIn('至少需两个', self.panel.status.text())

    def test_current_context_refresh_and_template_selection_leave_experiment_and_record_unchanged(self):
        self.panel.run_button.click()
        before = (self.panel.editor.toPlainText(), self.panel.record_editor.toPlainText(), self.panel.result_snapshot())
        self.panel.set_scenario({'operator': 'kaltsit', 'skill': 3})
        self.panel.operator.setCurrentIndex(1)
        self.panel.channel.setCurrentIndex(1)
        self.panel.variant.setCurrentIndex(1)
        self.assertEqual(before, (self.panel.editor.toPlainText(), self.panel.record_editor.toPlainText(), self.panel.result_snapshot()))

    def test_import_and_context_binding_preserve_record_evidence_until_explicit_save(self):
        record = json.loads(self.panel.record_editor.toPlainText())
        scenario = {'operator': 'mechanist', 'skill': 1, 'level': 60, 'relic_ids': [], 'potential': 4}
        self.panel.set_scenario(scenario)
        scenario['potential'] = 1
        self.panel.import_button.click()
        imported = json.loads(self.panel.record_editor.toPlainText())
        self.assertEqual(imported['data']['scenario']['potential'], 4)
        self.assertEqual(imported['data']['observation'], record['data']['observation'])
        self.panel.bind_button.click()
        bound = json.loads(self.panel.record_editor.toPlainText())
        self.assertEqual(bound['data']['observation']['values'], record['data']['observation']['values'])
        self.assertEqual(bound['data']['observation']['source'], record['data']['observation']['source'])
        self.assertNotEqual(bound['data']['observation']['context_token'], record['data']['observation']['context_token'])
        self.panel.save_record_button.click()
        self.panel.run_button.click()
        self.assertEqual(self.panel.result_snapshot()['training_state'], 'blocked')

    def test_conflict_template_witness_locates_the_original_independent_record(self):
        self.panel.variant.setCurrentIndex(1)
        self.panel.load_template.click()
        self.panel.run_button.click()
        self.assertEqual(self.panel.result_snapshot()['overall_state'], 'contradicted')
        self.assertTrue(self.panel.locate_witness_button.isEnabled())
        key = self.panel.witness_choice.currentData()
        self.panel.locate_witness_button.click()
        self.assertEqual(self.panel.record_choice.currentData(), key)
        self.assertEqual(json.loads(self.panel.record_editor.toPlainText())['id'], key)
        self.assertEqual(self.panel.tabs.currentIndex(), 1)

    def test_three_skill_template_and_source_escaping_and_invalid_json(self):
        self.panel.channel.setCurrentIndex(1)
        self.panel.load_template.click()
        self.panel.run_button.click()
        self.assertEqual(self.panel.result_snapshot()['channel']['metric'], 'initial_ready')
        self.assertEqual(self.panel.result_snapshot()['training_hypothesis_range']['lower'], 2)
        from rouge.calibration_experiment_view import experiment_html
        payload = public_experiment_payload()
        payload['experiment']['records'][0]['data']['observation']['source'] = '<script>source</script>'
        rendered = experiment_html(calibration_experiment(**payload))
        self.assertNotIn('<script>', rendered)
        self.assertIn('&lt;script&gt;', rendered)
        self.panel.editor.setPlainText('{bad json')
        self.panel.run_button.click()
        self.assertIsNone(self.panel.result_snapshot())
        self.assertEqual(self.panel.editor.toPlainText(), '{bad json')


if __name__ == '__main__':
    unittest.main()
