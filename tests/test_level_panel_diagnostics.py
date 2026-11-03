from copy import deepcopy
from fractions import Fraction
import json
import unittest
from unittest.mock import patch

from rouge.calibration import panel_layers
from rouge.level_panel_diagnostics import diagnose_panel_levels, level_ranges
from rouge.paired_calibration import public_paired_payload


def record(operator='mechanist', level=90, values=None, panel='培养与模组', **conditions):
    scenario = {'operator': operator, 'elite': 2, 'level': level, 'skill': 1,
                'skill_rank': 7, **conditions}
    return {'scenario': scenario, 'observation': {
        'context_token': panel_layers(scenario)['context_token'], 'panel': panel,
        'evidence_kind': 'formula_reference', 'source': '固定培养表的独立算术参考，不是游戏实录',
        'values': values or {'hp': 3288, 'attack': 543, 'defense': 701}}}


class LevelPanelTests(unittest.TestCase):
    def test_three_literal_level60_panels_and_declared_unique_candidate(self):
        # Independent half-up integer interpolation of pinned E2 first/last frames.
        cases = {'mechanist': {'hp': 3288, 'attack': 543, 'defense': 701},
                 'kaltsit': {'hp': 2043, 'attack': 476, 'defense': 287},
                 'silverash': {'hp': 2094, 'attack': 616, 'defense': 410}}
        for operator, values in cases.items():
            with self.subTest(operator=operator):
                r = diagnose_panel_levels(**record(operator, values=values))
                self.assertEqual(r['compatible_levels'], [60])
                self.assertEqual(r['unique_model_level'], 60)
                self.assertEqual(r['conclusion'], 'unique_model_candidate')
                self.assertEqual(len(r['rows']), 90)
                self.assertIsNone(r['actual_level'])
                self.assertIsNone(r['actual_cause_of_residual'])
                self.assertFalse(r['native_verified'])

    def test_all_e2_rows_against_independent_fraction_oracle(self):
        frames = {'kaltsit': ((1393, 408, 220), (1620, 510, 276), (500, 0, 30)),
                  'silverash': ((1552, 507, 317), (2218, 618, 397), (100, 35, 40)),
                  'mechanist': ((2614, 425, 514), (3631, 513, 705), (0, 60, 60))}
        for operator, (first, last, trust) in frames.items():
            r = diagnose_panel_levels(**record(operator))
            for row in r['rows']:
                for i, field in enumerate(('hp', 'attack', 'defense')):
                    value = Fraction(first[i]) + Fraction(row['level'] - 1, 89) * (last[i] - first[i])
                    rounded = (value + Fraction(1, 2)).numerator // (value + Fraction(1, 2)).denominator
                    predicted = next(f['predicted'] for f in row['fields'] if f['field'] == field)
                    self.assertEqual(predicted, rounded + trust[i], (operator, row['level'], field))

    def test_phase_bounds_are_not_always90_and_partial_fields_are_ambiguous(self):
        for elite, maximum in ((0, 50), (1, 80), (2, 90)):
            r = diagnose_panel_levels(**record(elite=elite, level=1, values={'resistance': 0}))
            self.assertEqual(r['compatible_levels'], list(range(1, maximum + 1)))
            self.assertEqual(r['compatible_ranges'], [{'first': 1, 'last': maximum}])
            self.assertIsNone(r['unique_model_level'])
            self.assertEqual(r['conclusion'], 'multiple_model_candidates')

    def test_conflicting_fields_keep_their_individual_level_constraints(self):
        r = diagnose_panel_levels(**record(values={'hp': 3288, 'attack': 573}))
        self.assertEqual(r['compatible_levels'], [])
        self.assertEqual(r['conclusion'], 'no_compatible_level_in_declared_model')
        fields = {f['field']: f for f in r['field_constraints']}
        self.assertEqual(fields['hp']['compatible_levels'], [60])
        self.assertIn(90, fields['attack']['compatible_levels'])
        self.assertNotIn(60, fields['attack']['compatible_levels'])
        self.assertIsNone(r['actual_cause_of_residual'])

    def test_tolerance_is_applied_to_each_field_without_summing_residuals(self):
        r = diagnose_panel_levels(**record(values={'hp': 3289, 'defense': 700}), tolerance=1)
        self.assertIn(60, r['compatible_levels'])
        row = r['rows'][59]
        self.assertEqual([f['difference'] for f in row['fields']], [1, -1])
        self.assertTrue(all(f['matches_declared_tolerance'] for f in row['fields']))

    def test_model_unknown_keeps_unresolved_levels_but_known_conflict_excludes(self):
        source = record(values={'hp': 3288, 'attack': 543})
        def unknown(s):
            r = panel_layers(s)
            r['panels']['培养与模组']['hp'] = None
            return r
        with patch('rouge.level_panel_diagnostics.panel_layers', side_effect=unknown):
            r = diagnose_panel_levels(**source)
        self.assertEqual(r['conclusion'], 'incomplete_model_search')
        self.assertIn(60, r['unresolved_levels'])
        self.assertEqual(r['rows'][89]['status'], 'excluded')
        self.assertIsNone(r['unique_model_level'])
        self.assertIsNone(r['rows'][59]['fields'][0]['difference'])

    def test_candidate_failure_not_reported_as_model_exclusion(self):
        source = record(values={'hp': 3288})
        def incomplete(s):
            if s.get('level') == 60:
                raise ValueError('独立测试：该候选模型不可用')
            return panel_layers(s)
        with patch('rouge.level_panel_diagnostics.panel_layers', side_effect=incomplete):
            r = diagnose_panel_levels(**source)
        self.assertEqual(r['unresolved_levels'], [60])
        self.assertEqual(r['rows'][59]['status'], 'unavailable')
        self.assertEqual(r['conclusion'], 'incomplete_model_search')

    def test_skills_unknown_fields_are_never_filled_by_cultivation_fields(self):
        r = diagnose_panel_levels(**record(values={'hp': 10}, panel='技能期间参考'))
        self.assertEqual(r['unresolved_ranges'], [{'first': 1, 'last': 90}])
        self.assertEqual(r['compatible_levels'], [])
        self.assertTrue(all(row['fields'][0]['predicted'] is None for row in r['rows']))

    def test_runes_and_talent_time_are_preserved_and_candidates_never_rebind_observation(self):
        for operator in ('mechanist', 'kaltsit', 'silverash'):
            source = public_paired_payload(operator)['after']
            saved = deepcopy(source)
            r = diagnose_panel_levels(**source)
            self.assertIn(90, r['compatible_levels'])
            self.assertEqual(source, saved)
            self.assertEqual(r['observation']['context_token'], saved['observation']['context_token'])
            self.assertNotEqual(r['rows'][0]['candidate_context_token'], r['observation']['context_token'])
            for key, value in source['scenario'].items():
                if key != 'level':
                    self.assertEqual(r['fixed_conditions'][key], value)

    def test_explicit_module_and_trust_conditions_remain_fixed(self):
        scenario = record(level=60, module_id='uniequip_002_mcnist', module_level=3, trust=50)
        model = panel_layers(scenario['scenario'])['panels']['培养与模组']
        scenario['observation']['values'] = {f: model[f] for f in ('hp', 'attack', 'defense')}
        r = diagnose_panel_levels(**scenario)
        self.assertIn(60, r['compatible_levels'])
        self.assertEqual(r['fixed_conditions']['module_level'], 3)
        self.assertEqual(r['fixed_conditions']['trust'], 50)
        self.assertIsNone(r['actual_level'])

    def test_bad_context_invalid_numeric_and_white_override_rejected(self):
        source = record()
        for field, value in (('context_token', 'wrong'), ('values', {'hp': float('nan')}),
                             ('values', {'hp': True}), ('values', {'hp': -1})):
            changed = deepcopy(source); changed['observation'][field] = value
            with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                diagnose_panel_levels(**changed)
        for value in (-1, True, float('inf')):
            with self.assertRaises(ValueError):
                diagnose_panel_levels(**source, tolerance=value)
        overridden = record(base_attack=600)
        with self.assertRaisesRegex(ValueError, '白值覆盖'):
            diagnose_panel_levels(**overridden)
        self.assertEqual(level_ranges([1, 2, 4, 7, 8]),
                         [{'first': 1, 'last': 2}, {'first': 4, 'last': 4}, {'first': 7, 'last': 8}])


class LevelPanelWindowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from PySide6.QtWidgets import QApplication
        cls.app = QApplication.instance() or QApplication([])

    def test_entry_keeps_evidence_refresh_selection_and_pair_result_unchanged(self):
        from rouge.paired_calibration_view import PairedCalibrationPanel
        panel = PairedCalibrationPanel()
        try:
            panel.run_button.click()
            previous = panel.result_snapshot()
            evidence = panel.before_editor.toPlainText()
            panel.before_levels_button.click()
            dialog = panel.level_dialog
            self.assertEqual(dialog.table.rowCount(), 90)
            self.assertIn(90, dialog.result['compatible_levels'])
            dialog.filter.setCurrentIndex(dialog.filter.findData('compatible'))
            count = dialog.table.rowCount()
            panel.set_scenario({'operator': 'silverash', 'skill': 2})
            self.assertEqual(dialog.table.rowCount(), count)
            self.assertEqual(dialog.filter.currentData(), 'compatible')
            self.assertEqual(panel.result_snapshot(), previous)
            self.assertEqual(panel.before_editor.toPlainText(), evidence)
            dialog.close()
        finally:
            panel.close()

    def test_error_does_not_open_new_window_or_overwrite_snapshot(self):
        from rouge.paired_calibration_view import PairedCalibrationPanel
        panel = PairedCalibrationPanel()
        try:
            panel.before_levels_button.click()
            original = panel.level_dialog
            before = json.loads(panel.after_editor.toPlainText())
            before['observation']['context_token'] = 'wrong'
            entered = json.dumps(before, ensure_ascii=False)
            panel.after_editor.setPlainText(entered)
            panel.after_levels_button.click()
            self.assertIs(panel.level_dialog, original)
            self.assertEqual(panel.after_editor.toPlainText(), entered)
            self.assertIn('等级排查未完成', panel.status.text())
            original.close()
        finally:
            panel.close()


if __name__ == '__main__': unittest.main()
