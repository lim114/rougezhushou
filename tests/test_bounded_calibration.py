from copy import deepcopy
from fractions import Fraction
from itertools import product
import json
import math
import unittest

from rouge.bounded_calibration import bounded_calibration, public_bounded_payload, _OrderBounds, _classify
from rouge.paired_calibration import compare_paired_panels, public_paired_payload
from rouge.timing_calibration import compare_timing_observation, public_timing_payload, timing_reference


def row(result, key, cycle='A'):
    return next(r for r in result['timing']['comparisons'] if r['metric'] == key and r['cycle_id'] == cycle)


class BoundedCalibrationTests(unittest.TestCase):
    def setUp(self):
        self.payload = public_bounded_payload()

    def compare(self, payload=None):
        return bounded_calibration(**(self.payload if payload is None else payload))

    def stamp(self, lo, hi=None):
        return {'clock_id': self.payload['timing']['observation']['clock']['id'], 'bounds': [lo, lo if hi is None else hi]}

    def test_degenerate_bounds_reproduce_exact_three_operator_tools(self):
        for operator in ('kaltsit', 'silverash', 'mechanist'):
            with self.subTest(operator=operator):
                result = self.compare(public_bounded_payload(operator))
                exact_panel = compare_paired_panels(**public_paired_payload(operator))
                exact_clock = compare_timing_observation(**public_timing_payload(operator))
                for bounded, exact in zip(result['panel']['rows'], exact_panel['rows']):
                    self.assertEqual(bounded['observed_after_minus_before_interval']['lower'], exact['observed_after_minus_before'])
                    self.assertEqual(bounded['observed_after_minus_before_interval']['upper'], exact['observed_after_minus_before'])
                    self.assertEqual(bounded['classification'], 'all_compatible')
                for bounded, exact in zip(result['timing']['comparisons'], exact_clock['comparisons']):
                    interval = bounded['observed_interval_seconds']
                    if exact['observed_seconds'] is None:
                        self.assertIsNone(interval)
                    else:
                        self.assertAlmostEqual(interval['lower'], exact['observed_seconds'])
                        self.assertAlmostEqual(interval['upper'], exact['observed_seconds'])
                    self.assertIsNone(bounded['actual_native_reference_seconds'])
                self.assertFalse(result['native_verified'])

    def test_panel_overlap_all_compatible_and_disjoint_are_distinct(self):
        self.payload = public_bounded_payload('mechanist')
        self.payload['panel']['before']['observation']['values']['attack'] = [572, 574]
        self.payload['panel']['after']['observation']['values']['attack'] = [715, 717]
        attack = next(r for r in self.compare()['panel']['rows'] if r['field'] == 'attack')
        self.assertEqual(attack['observed_after_minus_before_interval']['lower'], 141)
        self.assertEqual(attack['observed_after_minus_before_interval']['upper'], 145)
        self.assertEqual(attack['classification'], 'possible_overlap')
        self.payload['panel_tolerance'] = 2
        self.assertEqual(next(r for r in self.compare()['panel']['rows'] if r['field'] == 'attack')['classification'], 'all_compatible')
        self.payload['panel']['after']['observation']['values']['attack'] = [720, 722]
        self.assertEqual(next(r for r in self.compare()['panel']['rows'] if r['field'] == 'attack')['classification'], 'no_overlap')

    def test_matching_difference_bounds_do_not_hide_absolute_offsets(self):
        self.payload = public_bounded_payload('mechanist')
        for side in ('before', 'after'):
            values = self.payload['panel'][side]['observation']['values']
            values['attack'] = [value + 10 for value in values['attack']]
        attack = next(r for r in self.compare()['panel']['rows'] if r['field'] == 'attack')
        self.assertEqual(attack['classification'], 'all_compatible')
        self.assertEqual(attack['before_absolute_classification'], 'no_overlap')
        self.assertEqual(attack['after_absolute_classification'], 'no_overlap')

    def test_unknown_model_and_one_sided_fields_never_fill_zero(self):
        for side in ('before', 'after'):
            observation = self.payload['panel'][side]['observation']
            observation['panel'] = '技能期间参考'
            observation['values'] = {'hp': [10, 12] if side == 'before' else [15, 16]}
        self.payload['panel']['before']['observation']['values']['defense'] = [10, 20]
        result = self.compare()['panel']
        self.assertEqual(result['before_only_fields'], ['defense'])
        self.assertEqual(result['rows'][0]['classification'], 'model_unknown')
        self.assertIsNone(result['rows'][0]['delta_residual_interval'])
        self.assertEqual(result['rows'][0]['observed_after_minus_before_interval']['lower'], 3)

    def test_normal_chain_joint_constraints_tighten_overlapping_stamp_bounds(self):
        observation = self.payload['timing']['observation']
        observation['cycles'] = observation['cycles'][:1]
        observation['cycles'][0].update(ready=self.stamp(107), start=self.stamp(109, 120),
            first_release=self.stamp(118, 119), last_release=self.stamp(120, 121), end=self.stamp(120, 125))
        result = self.compare()
        bounds = result['timing']['feasible_readings_seconds']
        self.assertEqual(bounds['A.start']['upper'], 119)
        span = row(result, 'first_release')['observed_interval_seconds']
        self.assertEqual((span['lower'], span['upper']), (0, 10))
        self.assertTrue(span['lower_inclusive'])
        self.assertTrue(result['timing']['ordering_is_caller_declaration'])

    def test_joint_conflict_is_rejected_as_declared_protocol_conflict(self):
        observation = self.payload['timing']['observation']
        observation['cycles'][0].update(first_release=self.stamp(150, 151), end=self.stamp(144))
        with self.assertRaisesRegex(ValueError, '声明.*协议|声明.*排序'):
            self.compare()

    def test_explicit_constraints_allow_post_end_impact_without_guessed_native_order(self):
        observation = self.payload['timing']['observation']
        observation.update(ordering_protocol='explicit_constraints', release_kind='body_impact', ordering_constraints=[
            {'before': 'A.start', 'after': 'A.first_release', 'strict': False},
            {'before': 'A.first_release', 'after': 'A.last_release', 'strict': False}])
        observation['cycles'][0].update(first_release=self.stamp(150, 151), last_release=self.stamp(153, 154))
        result = self.compare()
        self.assertEqual(row(result, 'first_release')['observed_interval_seconds']['lower'], 41)
        self.assertEqual(row(result, 'release_span')['observed_interval_seconds']['lower'], 2)
        self.assertEqual(row(result, 'first_release')['classification'], 'model_unknown')
        self.assertEqual(len(result['timing']['declared_constraints']), 2)
        self.assertIsNone(result['timing']['reference']['actual_end_seconds'])

    def test_strict_release_order_preserves_open_zero_bound_without_epsilon(self):
        observation = self.payload['timing']['observation']
        observation['release_kind'] = 'body_attack_release'
        observation['cycles'][0].update(release_recording='all_consecutive', release_stamps=[self.stamp(110, 112), self.stamp(110, 112)])
        result = self.compare()
        interval = result['timing']['release_interval_rows'][0]['observed_interval_seconds']
        self.assertEqual((interval['lower'], interval['upper']), (0, 2))
        self.assertFalse(interval['lower_inclusive'])
        self.assertTrue(interval['upper_inclusive'])
        self.assertEqual(_classify(interval, 0, Fraction(0)), 'no_overlap')
        self.assertEqual(_classify(interval, 1, Fraction(0)), 'possible_overlap')

    def test_equal_degenerate_release_stamps_conflict_with_declared_strict_protocol(self):
        self.payload['timing']['observation']['cycles'][0]['release_stamps'] = [self.stamp(110), self.stamp(110)]
        with self.assertRaisesRegex(ValueError, '声明.*协议|声明.*排序'):
            self.compare()

    def test_same_boundary_and_release_readings_intersect_instead_of_choosing_midpoint(self):
        cycle = self.payload['timing']['observation']['cycles'][0]
        cycle.update(first_release=self.stamp(111, 113), release_stamps=[self.stamp(110, 112), self.stamp(115, 116)])
        result = self.compare()['timing']
        self.assertEqual(result['event_aliases']['A.first_release'], 'A.release.0')
        self.assertEqual(result['feasible_readings_seconds']['A.release.0']['lower'], 111)
        self.assertEqual(result['feasible_readings_seconds']['A.release.0']['upper'], 112)
        self.assertEqual(result['original_readings_seconds']['A.first_release']['upper'], 113)
        self.assertEqual(result['original_readings_seconds']['A.release.0']['lower'], 110)
        self.assertEqual(result['feasible_readings_seconds']['A.first_release']['lower'], 111)
        cycle['first_release'] = self.stamp(117, 118)
        with self.assertRaisesRegex(ValueError, '共同值'):
            self.compare()

    def test_uncertain_deployment_origin_and_readiness_share_joint_order(self):
        observation = self.payload['timing']['observation']
        observation['clock']['origin_stamp'] = [100, 101]
        observation['cycles'][0]['ready'] = self.stamp(100, 108)
        interval = row(self.compare(), 'initial_ready')['observed_interval_seconds']
        self.assertEqual((interval['lower'], interval['upper']), (0, 8))
        self.assertTrue(interval['lower_inclusive'])

    def test_explicit_nonstrict_cycle_means_equality_and_strict_cycle_is_conflict(self):
        observation = self.payload['timing']['observation']
        observation.update(ordering_protocol='explicit_constraints', ordering_constraints=[
            {'before': 'A.ready', 'after': 'A.start', 'strict': False},
            {'before': 'A.start', 'after': 'A.ready', 'strict': False}])
        observation['cycles'][0].update(ready=self.stamp(110, 112), start=self.stamp(111, 113))
        result = self.compare()
        interval = row(result, 'activation_wait')['observed_interval_seconds']
        self.assertEqual((interval['lower'], interval['upper']), (0, 0))
        observation['ordering_constraints'][0]['strict'] = True
        with self.assertRaisesRegex(ValueError, '严格先后形成闭环'):
            self.compare()

    def test_video_frame_bounds_use_declared_60fps_separate_from_model_30hz(self):
        observation = self.payload['timing']['observation']
        observation['clock'].update(unit='frames', fps=60, origin_stamp=[6000, 6001])
        for cycle in observation['cycles']:
            for key in ('ready', 'start', 'end', 'next_ready'):
                cycle[key]['bounds'] = [value * 60 for value in cycle[key]['bounds']]
        observation['cycles'][0]['ready']['bounds'] = [6420, 6421]
        result = self.compare()
        interval = row(result, 'initial_ready')['observed_interval_seconds']
        self.assertAlmostEqual(interval['lower'], 7 - 1 / 60)
        self.assertAlmostEqual(interval['upper'], 7 + 1 / 60)
        self.assertEqual(row(result, 'initial_ready')['classification'], 'possible_overlap')
        self.assertEqual(result['timing']['reference']['model_fps'], 30)
        self.assertEqual(result['timing']['clock']['fps'], 60)

    def test_unknown_model_clock_or_precharged_basis_keeps_observed_bounds(self):
        self.payload['timing']['observation']['cycles'][0]['recharge_basis'] = 'precharged_or_partial'
        result = self.compare()
        self.assertEqual(row(result, 'recharge')['classification'], 'model_unknown')
        self.assertEqual(row(result, 'recharge')['observed_interval_seconds']['lower'], 35)
        timing = self.payload['timing']
        timing['scenario'] = {'operator': 'mechanist', 'skill': 2}
        reference = timing_reference(timing['scenario'])
        timing['observation'].update(operator='mechanist', skill_id=reference['skill_identity']['skill_id'], context_token=reference['context_token'])
        self.assertEqual(row(self.compare(), 'cycle_to_ready', 'B')['classification'], 'model_unknown')

    def test_missing_measurement_stays_unknown_and_independent_speed_bounds_are_not_inferred(self):
        result = self.compare()
        self.assertEqual(row(result, 'first_release')['classification'], 'measurement_unknown')
        self.assertIsNone(row(result, 'first_release')['observed_interval_seconds'])
        observation = self.payload['timing']['observation']
        observation['attack_speed_attribute'] = [149, 151]
        self.assertEqual(self.compare()['timing']['attack_speed_comparison']['classification'], 'possible_overlap')
        del observation['attack_speed_attribute']
        self.assertEqual(self.compare()['timing']['attack_speed_comparison']['classification'], 'measurement_unknown')

    def test_interval_difference_extrema_match_independent_finite_enumeration(self):
        graph = _OrderBounds()
        domains = {'a': (0, 3), 'b': (1, 4), 'c': (2, 5)}
        for name, bounds in domains.items():
            graph.add(name, tuple(Fraction(value) for value in bounds))
        graph.order('a', 'b')
        graph.order('b', 'c')
        graph.solve()
        feasible = [dict(zip(domains, values)) for values in product(*(range(lo, hi + 1) for lo, hi in domains.values()))
                    if values[0] <= values[1] <= values[2]]
        for a in domains:
            for b in domains:
                expected = [sample[b] - sample[a] for sample in feasible]
                interval = graph.difference(a, b)
                self.assertEqual((interval['lower'], interval['upper']), (min(expected), max(expected)))

    def test_rational_strict_endpoint_does_not_round_away_a_possible_overlap(self):
        graph = _OrderBounds()
        graph.add('a', (Fraction(0), Fraction(0)))
        graph.add('b', (Fraction(0), Fraction(1, 3)))
        graph.add('c', (Fraction(1, 3), Fraction(1, 3)))
        graph.order('a', 'b', True)
        graph.order('b', 'c', True)
        graph.solve()
        interval = graph.difference('a', 'b')
        self.assertEqual(interval['upper_exact'], '1/3')
        self.assertFalse(interval['upper_inclusive'])
        self.assertEqual(_classify(interval, .3333333333333333, Fraction(0)), 'possible_overlap')

    def test_context_operator_panel_evidence_and_clock_mismatch_rejected(self):
        variants = []
        for key, value in (('context_token', 'other'), ('panel', '技能期间参考'), ('evidence_kind', 'game_panel')):
            payload = deepcopy(self.payload)
            payload['panel']['after']['observation'][key] = value
            variants.append(payload)
        for key, value in (('context_token', 'other'), ('operator', 'silverash'), ('skill_id', 'other')):
            payload = deepcopy(self.payload)
            payload['timing']['observation'][key] = value
            variants.append(payload)
        payload = deepcopy(self.payload)
        payload['timing']['observation']['cycles'][0]['ready']['clock_id'] = 'other-clock'
        variants.append(payload)
        for payload in variants:
            with self.assertRaises(ValueError):
                self.compare(payload)

    def test_invalid_numeric_bounds_scalar_precision_and_protocols_rejected(self):
        for bounds in ([2, 1], [True, 3], [0, math.inf], [0, math.nan], [-1, 1], [0, '1'], 7, [1], [0, 10 ** 1000]):
            payload = deepcopy(self.payload)
            payload['panel']['before']['observation']['values']['hp'] = bounds
            with self.subTest(bounds=str(bounds)[:20]), self.assertRaises(ValueError):
                self.compare(payload)
        for changes in ({'ordering_protocol': None}, {'ordering_protocol': 'native_verified'},
                        {'ordering_constraints': [{'before': 'A.ready', 'after': 'A.start', 'strict': False}]}):
            payload = deepcopy(self.payload)
            payload['timing']['observation'].update(changes)
            with self.assertRaises(ValueError):
                self.compare(payload)

    def test_explicit_missing_event_and_invalid_constraint_or_fps_are_rejected(self):
        variants = []
        for constraint in ({'before': 'A.first_release', 'after': 'A.start', 'strict': False},
                           {'before': 'A.ready', 'after': 'A.start', 'strict': 'yes'}):
            payload = deepcopy(self.payload)
            payload['timing']['observation'].update(ordering_protocol='explicit_constraints', ordering_constraints=[constraint])
            variants.append(payload)
        for fps in (0, True, math.inf, None, 1001):
            payload = deepcopy(self.payload)
            payload['timing']['observation']['clock'].update(unit='frames', fps=fps)
            variants.append(payload)
        for payload in variants:
            with self.assertRaises(ValueError):
                self.compare(payload)

    def test_one_workspace_can_compare_only_one_evidence_group_and_preserves_sources(self):
        for selected in ('panel', 'timing'):
            payload = deepcopy(self.payload)
            payload['timing' if selected == 'panel' else 'panel'] = None
            result = self.compare(payload)
            self.assertIsNone(result['timing' if selected == 'panel' else 'panel'])
            self.assertFalse(result['native_verified'])
        for group, observation in (('panel', self.payload['panel']['before']['observation']), ('timing', self.payload['timing']['observation'])):
            observation['source'] = 'independent bounded source / ' + group
        result = self.compare()
        self.assertEqual(result['panel']['before_source'], 'independent bounded source / panel')
        self.assertEqual(result['timing']['source'], 'independent bounded source / timing')
        self.assertEqual(result['timing']['reference']['source']['commit'], 'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add')

    def test_outputs_inputs_and_returns_are_isolated(self):
        original = deepcopy(self.payload)
        a, b = self.compare(), self.compare()
        self.assertEqual(original, self.payload)
        a['timing']['feasible_readings_seconds'].clear()
        a['panel']['rows'].clear()
        self.assertTrue(b['timing']['feasible_readings_seconds'])
        self.assertTrue(b['panel']['rows'])


class BoundedCalibrationViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from PySide6.QtWidgets import QApplication
        cls.qt = QApplication.instance() or QApplication([])

    def setUp(self):
        from rouge.bounded_calibration_view import BoundedCalibrationPanel
        self.panel = BoundedCalibrationPanel()
        self.panel.resize(1150, 900)
        self.panel.show()
        self.qt.processEvents()

    def tearDown(self):
        self.panel.close()
        self.panel.deleteLater()
        self.qt.processEvents()

    def test_actual_widget_renders_bounds_statuses_and_declared_protocol(self):
        self.panel.run_button.click()
        result = self.panel.result_snapshot()
        self.assertIsNotNone(result, self.panel.status.text())
        text = self.panel.result_view.toPlainText()
        for phrase in ('面板与时刻界限成对核对', '[1325, 1325]', '所有可行值均相符', '原生参考',
                       '调用方声明正常链录入协议', '未知', '不视为置信度'):
            self.assertIn(phrase, text)

    def test_explicit_widening_shows_possible_overlap_without_auto_uncertainty(self):
        payload = json.loads(self.panel.panel_editor.toPlainText())
        payload['after']['observation']['values']['hp'] = [3974, 3976]
        self.panel.panel_editor.setPlainText(json.dumps(payload))
        self.panel.run_button.click()
        self.assertIn('仅可能重叠', self.panel.result_view.toPlainText())
        self.assertEqual(json.loads(self.panel.panel_editor.toPlainText()), payload)

    def test_refresh_reference_read_and_template_choice_preserve_all_bounds_and_results(self):
        self.panel.run_button.click()
        before = (self.panel.panel_editor.toPlainText(), self.panel.timing_editor.toPlainText(), self.panel.result_snapshot())
        self.panel.set_scenario({'operator': 'mechanist', 'skill': 3})
        self.panel.template.setCurrentIndex(2)
        self.panel.reference_button.click()
        self.assertEqual(before, (self.panel.panel_editor.toPlainText(), self.panel.timing_editor.toPlainText(), self.panel.result_snapshot()))

    def test_explicit_import_and_binding_preserve_bounds_sources_protocol_and_identity(self):
        initial = json.loads(self.panel.timing_editor.toPlainText())
        self.panel.set_scenario({'operator': 'kaltsit', 'skill': 1, 'potential': 4})
        self.panel.import_target.setCurrentIndex(2)
        self.panel.import_button.click()
        imported = json.loads(self.panel.timing_editor.toPlainText())
        self.assertEqual(imported['observation'], initial['observation'])
        self.panel.bind_button.click()
        bound = json.loads(self.panel.timing_editor.toPlainText())
        for key in ('clock', 'cycles', 'source', 'operator', 'skill_id', 'ordering_protocol'):
            self.assertEqual(bound['observation'][key], initial['observation'][key])
        self.assertNotEqual(bound['observation']['context_token'], initial['observation']['context_token'])
        self.panel.run_button.click()
        self.assertIsNotNone(self.panel.result_snapshot(), self.panel.status.text())

    def test_joint_conflict_clears_old_result_and_keeps_independent_input(self):
        self.panel.run_button.click()
        timing = json.loads(self.panel.timing_editor.toPlainText())
        timing['observation']['cycles'][0]['first_release'] = {'clock_id': timing['observation']['clock']['id'], 'bounds': [150, 151]}
        entered = json.dumps(timing)
        self.panel.timing_editor.setPlainText(entered)
        self.assertIsNone(self.panel.result_snapshot())
        self.panel.run_button.click()
        self.assertIsNone(self.panel.result_snapshot())
        self.assertIn('声明', self.panel.status.text())
        self.assertIn('协议', self.panel.status.text())
        self.assertEqual(self.panel.timing_editor.toPlainText(), entered)

    def test_public_templates_and_single_group_controls_and_source_escaping(self):
        for index in range(3):
            self.panel.template.setCurrentIndex(index)
            self.panel.load_template.click()
            self.panel.run_button.click()
            self.assertIsNotNone(self.panel.result_snapshot(), self.panel.status.text())
        self.panel.use_panel.setChecked(False)
        self.panel.run_button.click()
        self.assertIsNone(self.panel.result_snapshot()['panel'])
        from rouge.bounded_calibration_view import bounded_calibration_html
        payload = public_bounded_payload()
        payload['timing']['observation']['source'] = '<script>source</script>'
        rendered = bounded_calibration_html(bounded_calibration(**payload))
        self.assertNotIn('<script>', rendered)
        self.assertIn('&lt;script&gt;', rendered)


if __name__ == '__main__':
    unittest.main()
