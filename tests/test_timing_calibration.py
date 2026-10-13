from copy import deepcopy
import json
import math
import unittest

from rouge.timing_calibration import compare_timing_observation, public_timing_payload, timing_reference


def metric(result, name, cycle='A'):
    return next(r for r in result['comparisons'] if r['metric'] == name and r['cycle_id'] == cycle)


class TimingCalibrationTests(unittest.TestCase):
    def setUp(self):
        self.payload = public_timing_payload()

    def compare(self, payload=None):
        return compare_timing_observation(**(self.payload if payload is None else payload))

    def stamp(self, value):
        return {'clock_id': self.payload['observation']['clock']['id'], 'value': value}

    def rebind(self):
        self.payload['observation']['context_token'] = timing_reference(self.payload['scenario'])['context_token']

    def test_first_nine_skill_compatibility_matrix_uses_existing_conditional_channels(self):
        expected = {
            'kaltsit': [(7, 35, 70), (7, 35, 63.7), (15, 50, 85)],
            'silverash': [(6, 29, 29), (4, 17, 17), (5, 55, 103)],
            'mechanist': [(253 / 30, 253 / 30, 503 / 30), (15, 50, None), (10, 35, 75)],
        }
        for operator, triples in expected.items():
            for number, triple in enumerate(triples, 1):
                with self.subTest(operator=operator, skill=number):
                    reference = timing_reference({'operator': operator, 'skill': number})
                    channels = reference['conditional_references']
                    for name, expected_value in zip(('initial_ready', 'recharge', 'cycle_to_ready'), triple):
                        if expected_value is None:
                            self.assertIsNone(channels[name])
                        else:
                            self.assertAlmostEqual(channels[name], expected_value)
                    self.assertEqual(reference['skill_identity']['skill'], number)
                    self.assertIsNone(reference['actual_end_seconds'])
                    self.assertIsNone(reference['actual_first_release_seconds'])
                    self.assertIsNone(reference['actual_unblocked_seconds'])
                    self.assertFalse(reference['native_verified'])

    def test_three_literal_formula_ledgers_separate_manual_wait_and_recast(self):
        for operator, initial, recharge, cycle in (('kaltsit', 7, 35, 70), ('silverash', 5, 55, 103), ('mechanist', 10, 35, 75)):
            with self.subTest(operator=operator):
                result = self.compare(public_timing_payload(operator))
                self.assertEqual(metric(result, 'initial_ready')['observed_seconds'], initial)
                self.assertEqual(metric(result, 'recharge')['observed_seconds'], recharge)
                self.assertEqual(metric(result, 'cycle_to_ready')['observed_seconds'], cycle)
                self.assertEqual(metric(result, 'activation_wait')['observed_seconds'], 2)
                self.assertEqual(metric(result, 'activation_wait', 'B')['observed_seconds'], 3)
                repeat = result['repeat_cycle_rows'][0]
                self.assertEqual(repeat['observed_seconds'], cycle + 3)
                self.assertEqual(repeat['previous_start_to_next_ready_seconds'], cycle)
                self.assertEqual(repeat['next_ready_to_current_start_seconds'], 3)
                self.assertIsNone(repeat['conditional_reference_seconds'])
                self.assertEqual(result['mismatching_conditional_clock_count'], 0)

    def test_same_model_lockout_policy_matches_end_origin_only(self):
        self.payload['scenario']['timing'] = {'sp_lockout_extra_seconds': 2}
        self.rebind()
        self.payload['observation']['cycles'] = self.payload['observation']['cycles'][:1]
        record = self.payload['observation']['cycles'][0]
        record['unblocked'] = self.stamp(146)
        record['next_ready'] = self.stamp(181)
        result = self.compare()
        self.assertEqual(metric(result, 'recharge')['observed_seconds'], 37)
        self.assertEqual(metric(result, 'recharge')['conditional_reference_seconds'], 37)
        self.assertEqual(metric(result, 'cycle_to_ready')['observed_seconds'], 72)
        self.assertEqual(metric(result, 'unblocked_recharge')['observed_seconds'], 35)
        self.assertIsNone(metric(result, 'unblocked_recharge')['conditional_reference_seconds'])
        self.assertIsNone(metric(result, 'unlock_delay')['conditional_reference_seconds'])

    def test_measured_first_end_unlock_phases_remain_without_native_predictions(self):
        cycle = self.payload['observation']['cycles'][0]
        cycle.update(first_release=self.stamp(111), last_release=self.stamp(140), unblocked=self.stamp(145))
        result = self.compare()
        for name, value in (('first_release', 2), ('release_span', 29), ('active_duration', 35), ('unlock_delay', 1)):
            row = metric(result, name)
            self.assertEqual(row['observed_seconds'], value)
            self.assertIsNone(row['conditional_reference_seconds'])
            self.assertIsNone(row['actual_native_reference_seconds'])
            self.assertIsNone(row['actual_cause_of_difference'])

    def test_selected_impacts_and_summon_events_do_not_become_body_cadence(self):
        for kind, recording in (('body_impact', 'all_consecutive'), ('summon_impact', 'all_consecutive'), ('body_attack_release', 'selected')):
            payload = deepcopy(self.payload)
            payload['observation']['release_kind'] = kind
            cycle = payload['observation']['cycles'][0]
            cycle['release_recording'] = recording
            cycle['release_stamps'] = [self.stamp(112), self.stamp(116)]
            result = self.compare(payload)
            interval = result['release_interval_rows'][0]
            self.assertEqual(interval['observed_seconds'], 4)
            self.assertIsNone(interval['conditional_reference_seconds'])

    def test_consecutive_body_release_records_compare_only_existing_conditional_cadence(self):
        self.payload['observation']['release_kind'] = 'body_attack_release'
        cycle = self.payload['observation']['cycles'][0]
        cycle['release_recording'] = 'all_consecutive'
        cycle['release_stamps'] = [self.stamp(112), self.stamp(114), self.stamp(116)]
        result = self.compare()
        self.assertEqual(len(result['release_interval_rows']), 2)
        row = result['release_interval_rows'][0]
        self.assertEqual(row['observed_seconds'], 2)
        self.assertAlmostEqual(row['conditional_reference_seconds'], 1.9)
        self.assertAlmostEqual(row['observed_minus_conditional_reference'], .1)
        self.assertIsNone(row['actual_native_reference_seconds'])
        self.assertEqual(metric(result, 'first_release')['observed_seconds'], 3)
        self.assertEqual(metric(result, 'release_span')['observed_seconds'], 4)

    def test_frames_use_declared_video_fps_and_absolute_origin_without_native_resampling(self):
        payload = deepcopy(self.payload)
        clock = payload['observation']['clock']
        clock.update(unit='frames', fps=60, origin_stamp=6000)
        for cycle in payload['observation']['cycles']:
            for name in ('ready', 'start', 'end', 'next_ready'):
                cycle[name]['value'] *= 60
        result = self.compare(payload)
        self.assertEqual(result['clock']['fps'], 60)
        self.assertEqual(metric(result, 'initial_ready')['observed_seconds'], 7)
        self.assertEqual(metric(result, 'recharge')['observed_seconds'], 35)
        self.assertEqual(result['reference']['model_fps'], 30)
        payload['observation']['cycles'][0]['ready']['value'] += 1
        result = self.compare(payload)
        self.assertAlmostEqual(metric(result, 'initial_ready')['observed_minus_conditional_reference'], 1 / 60)

    def test_multicharge_or_unknown_charge_basis_retains_measured_refill_without_false_comparison(self):
        for basis in ('precharged_or_partial', 'unknown'):
            payload = deepcopy(self.payload)
            payload['observation']['cycles'][0]['recharge_basis'] = basis
            result = self.compare(payload)
            self.assertEqual(metric(result, 'recharge')['observed_seconds'], 35)
            self.assertIsNone(metric(result, 'recharge')['conditional_reference_seconds'])
            self.assertIsNone(metric(result, 'cycle_to_ready')['conditional_reference_seconds'])
        self.assertEqual(timing_reference({'operator': 'silverash', 'skill': 2})['max_charges'], 2)

    def test_intermediate_capture_cannot_claim_initial_readiness(self):
        self.payload['observation']['first_cycle_is_initial'] = False
        result = self.compare()
        self.assertEqual(metric(result, 'initial_ready')['observed_seconds'], 7)
        self.assertIsNone(metric(result, 'initial_ready')['conditional_reference_seconds'])
        self.assertEqual(metric(result, 'initial_ready')['reference_unavailable_reason'], 'not_declared_first_readiness_after_deployment')

    def test_unknown_model_cycle_is_not_filled_from_source_duration_or_observations(self):
        self.payload['scenario'] = {'operator': 'mechanist', 'skill': 2}
        reference = timing_reference(self.payload['scenario'])
        observation = self.payload['observation']
        observation.update(operator='mechanist', skill_id=reference['skill_identity']['skill_id'], context_token=reference['context_token'])
        result = self.compare()
        self.assertIsNone(result['reference']['source_duration_parameter_seconds'])
        self.assertIsNone(result['reference']['model_duration_reference_seconds'])
        self.assertEqual(metric(result, 'active_duration')['observed_seconds'], 35)
        self.assertIsNone(metric(result, 'cycle_to_ready')['conditional_reference_seconds'])
        self.assertEqual(metric(result, 'cycle_to_ready')['reference_unavailable_reason'], 'existing_model_clock_unknown')

    def test_repeat_variability_keeps_independent_phases_and_no_cause(self):
        cycle_b = self.payload['observation']['cycles'][1]
        cycle_b['next_ready'] = self.stamp(254)
        self.payload['observation']['cycles'].append({'id': 'C', 'ready': self.stamp(254), 'start': self.stamp(258),
            'end': self.stamp(293), 'next_ready': self.stamp(328), 'recharge_basis': 'model_depleted_requirement'})
        result = self.compare()
        summary = result['variation']['recharge']
        self.assertEqual((summary['recorded_count'], summary['minimum_seconds'], summary['maximum_seconds'], summary['range_seconds']), (3, 35, 37, 2))
        self.assertEqual(result['repeat_variation']['range_seconds'], 3)
        self.assertEqual(result['variation']['activation_wait']['range_seconds'], 2)
        self.assertEqual(metric(result, 'recharge', 'B')['observed_minus_conditional_reference'], 2)
        self.assertIsNone(summary['actual_cause_of_variation'])

    def test_attack_speed_is_independent_attribute_and_never_inferred_from_video(self):
        self.payload['observation']['attack_speed_attribute'] = 155
        result = self.compare()
        self.assertEqual(result['attack_speed_comparison']['observed_minus_reference'], 5)
        del self.payload['observation']['attack_speed_attribute']
        result = self.compare()
        self.assertIsNone(result['attack_speed_comparison']['observed_attribute'])
        self.assertIsNone(result['attack_speed_comparison']['observed_minus_reference'])

    def test_source_categories_preserved_with_no_native_certification(self):
        for kind in ('game_timing', 'public_case', 'formula_reference'):
            payload = deepcopy(self.payload)
            payload['observation']['evidence_kind'] = kind
            payload['observation']['source'] = 'independent source: ' + kind
            result = self.compare(payload)
            self.assertEqual(result['evidence_kind'], kind)
            self.assertEqual(result['source'], payload['observation']['source'])
            self.assertFalse(result['native_verified'])
            self.assertIsNone(result['actual_cause_of_difference'])

    def test_context_operator_and_skill_must_match_the_same_independent_record(self):
        for key, value in (('context_token', 'wrong'), ('operator', 'silverash'), ('skill_id', 'skchr_kalts2_2')):
            payload = deepcopy(self.payload)
            payload['observation'][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                self.compare(payload)

    def test_clock_units_fps_origin_and_cross_clock_identity_are_strict(self):
        variants = []
        for change in ({'unit': 'ms'}, {'fps': 60}, {'origin_event': 'video_start'}, {'origin_stamp': -1}, {'origin_stamp': math.inf}):
            payload = deepcopy(self.payload)
            payload['observation']['clock'].update(change)
            variants.append(payload)
        for fps in (None, 0, True, -1, math.nan, math.inf, 1001):
            payload = deepcopy(self.payload)
            payload['observation']['clock'].update(unit='frames', fps=fps)
            variants.append(payload)
        payload = deepcopy(self.payload)
        payload['observation']['cycles'][0]['ready']['clock_id'] = 'other-video'
        variants.append(payload)
        for payload in variants:
            with self.assertRaises(ValueError):
                self.compare(payload)

    def test_invalid_nonfinite_boolean_and_malformed_unknown_inputs_rejected(self):
        for value in (True, -1, '127', math.nan, math.inf, 10 ** 1000):
            payload = deepcopy(self.payload)
            payload['observation']['cycles'][0]['ready']['value'] = value
            with self.subTest(value=str(value)[:15]), self.assertRaises(ValueError):
                self.compare(payload)
        for value in (True, math.nan, math.inf, -1):
            payload = deepcopy(self.payload)
            payload['tolerance_seconds'] = value
            with self.assertRaises(ValueError):
                self.compare(payload)
        for key, value in (('first_cycle_is_initial', 'true'), ('attack_speed_attribute', math.nan), ('source', ' '), ('evidence_kind', 'game_panel')):
            payload = deepcopy(self.payload)
            payload['observation'][key] = value
            with self.assertRaises(ValueError):
                self.compare(payload)

    def test_sequence_reverse_repeat_overlap_duplicate_and_bounds_mismatch_rejected(self):
        variants = []
        payload = deepcopy(self.payload)
        payload['observation']['cycles'][0]['end'] = self.stamp(108)
        variants.append(payload)
        payload = deepcopy(self.payload)
        payload['observation']['cycles'][1]['start'] = self.stamp(170)
        variants.append(payload)
        payload = deepcopy(self.payload)
        payload['observation']['cycles'][1]['id'] = 'A'
        variants.append(payload)
        payload = deepcopy(self.payload)
        payload['observation']['cycles'].reverse()
        variants.append(payload)
        for releases in ([self.stamp(112), self.stamp(112)], [self.stamp(114), self.stamp(112)], [None]):
            payload = deepcopy(self.payload)
            payload['observation']['cycles'][0]['release_stamps'] = releases
            variants.append(payload)
        payload = deepcopy(self.payload)
        payload['observation']['cycles'][0].update(first_release=self.stamp(111), release_stamps=[self.stamp(112)])
        variants.append(payload)
        for payload in variants:
            with self.assertRaises(ValueError):
                self.compare(payload)

    def test_empty_unknown_only_unsupported_or_injected_records_rejected(self):
        variants = []
        for cycles in ([], [{}], [{'id': 'A'}], self.payload['observation']['cycles'] * 11):
            payload = deepcopy(self.payload)
            payload['observation']['cycles'] = cycles
            variants.append(payload)
        payload = deepcopy(self.payload)
        payload['scenario']['_deployment_skill_start_seconds'] = 0
        variants.append(payload)
        payload = deepcopy(self.payload)
        payload['observation']['private_state'] = {}
        variants.append(payload)
        for payload in variants:
            with self.assertRaises(ValueError):
                self.compare(payload)

    def test_inputs_outputs_and_source_are_isolated(self):
        original = deepcopy(self.payload)
        first, second = self.compare(), self.compare()
        self.assertEqual(original, self.payload)
        first['reference']['source']['files'].clear()
        first['cycles'][0]['events_seconds'].clear()
        self.assertTrue(second['reference']['source']['files'])
        self.assertTrue(second['cycles'][0]['events_seconds'])
        self.assertEqual(second['reference']['source']['commit'], 'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add')


class TimingCalibrationViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from PySide6.QtWidgets import QApplication
        cls.qt = QApplication.instance() or QApplication([])

    def setUp(self):
        from rouge.timing_calibration_view import TimingCalibrationPanel
        self.panel = TimingCalibrationPanel()
        self.panel.resize(1150, 850)
        self.panel.show()
        self.qt.processEvents()

    def tearDown(self):
        self.panel.close()
        self.panel.deleteLater()
        self.qt.processEvents()

    def test_actual_widget_renders_event_differences_repeated_waits_and_unknown_phases(self):
        self.panel.run_button.click()
        result = self.panel.result_snapshot()
        self.assertIsNotNone(result, self.panel.status.text())
        text = self.panel.result_view.toPlainText()
        for phrase in ('首批三人技能事件与回转成对核对', '公式参考', '就绪到实际开启等待',
                       '相邻两次开启间隔', '73', '原生参考', '未知', '未认证实机'):
            self.assertIn(phrase, text)
        result['comparisons'].clear()
        self.assertTrue(self.panel.result_snapshot()['comparisons'])

    def test_refresh_template_selection_and_reference_read_keep_independent_records(self):
        self.panel.run_button.click()
        before = (self.panel.scenario_editor.toPlainText(), self.panel.observation_editor.toPlainText(), self.panel.result_snapshot())
        self.panel.set_scenario({'operator': 'silverash', 'skill': 3})
        self.panel.template.setCurrentIndex(1)
        self.panel.reference_button.click()
        self.assertEqual(before, (self.panel.scenario_editor.toPlainText(), self.panel.observation_editor.toPlainText(), self.panel.result_snapshot()))
        self.assertIn('actual_end_seconds', self.panel.reference_view.toPlainText())

    def test_explicit_import_and_binding_preserve_clock_source_and_skill_identity(self):
        observation = json.loads(self.panel.observation_editor.toPlainText())
        scenario = {'operator': 'kaltsit', 'skill': 1, 'potential': 4}
        self.panel.set_scenario(scenario)
        scenario['potential'] = 1
        self.panel.import_button.click()
        self.assertEqual(json.loads(self.panel.scenario_editor.toPlainText())['potential'], 4)
        self.assertEqual(json.loads(self.panel.observation_editor.toPlainText()), observation)
        self.panel.run_button.click()
        self.assertIsNone(self.panel.result_snapshot())
        self.panel.bind_button.click()
        bound = json.loads(self.panel.observation_editor.toPlainText())
        for key in ('clock', 'cycles', 'source', 'operator', 'skill_id'):
            self.assertEqual(bound[key], observation[key])
        self.assertNotEqual(bound['context_token'], observation['context_token'])
        self.panel.run_button.click()
        self.assertIsNotNone(self.panel.result_snapshot(), self.panel.status.text())

    def test_editing_records_or_tolerance_invalidates_old_result(self):
        self.panel.run_button.click()
        self.assertIsNotNone(self.panel.result_snapshot())
        self.panel.tolerance.setValue(.1)
        self.assertIsNone(self.panel.result_snapshot())
        self.assertEqual(self.panel.result_view.toPlainText(), '')
        self.panel.run_button.click()
        self.panel.observation_editor.appendPlainText(' ')
        self.assertIsNone(self.panel.result_snapshot())

    def test_explicit_load_three_templates_runs_without_guessing_unknown_release_events(self):
        for index in range(3):
            self.panel.template.setCurrentIndex(index)
            self.panel.load_template.click()
            self.panel.run_button.click()
            result = self.panel.result_snapshot()
            self.assertIsNotNone(result, self.panel.status.text())
            self.assertIsNone(metric(result, 'first_release')['observed_seconds'])
            self.assertIsNone(metric(result, 'unlock_delay')['observed_seconds'])
            self.assertFalse(result['native_verified'])

    def test_invalid_record_keeps_entered_text_and_renderer_escapes_markup(self):
        self.panel.observation_editor.setPlainText('{bad json')
        self.panel.run_button.click()
        self.assertIsNone(self.panel.result_snapshot())
        self.assertEqual(self.panel.observation_editor.toPlainText(), '{bad json')
        self.assertIn('未完成时钟对照', self.panel.status.text())
        from rouge.timing_calibration_view import timing_calibration_html
        payload = public_timing_payload()
        payload['observation']['source'] = '<script>source</script>'
        rendered = timing_calibration_html(compare_timing_observation(**payload))
        self.assertNotIn('<script>', rendered)
        self.assertIn('&lt;script&gt;', rendered)


if __name__ == '__main__':
    unittest.main()
