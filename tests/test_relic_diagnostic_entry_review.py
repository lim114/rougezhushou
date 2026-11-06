from copy import deepcopy
from unittest import TestCase
from unittest.mock import patch
from rouge import calibration
from rouge.relic_panel_diagnostics import relic_panel_diagnostics


class RelicDiagnosticEntryTests(TestCase):
    def test_diagnostic_normalizes_once_and_calculates_each_distinct_subset(self):
        scenario = {'operator': 'mechanist', 'skill': 3, 'relic_ids': ['rogue_6_relic_legacy_16', 'rogue_6_relic_legacy_17']}
        original = deepcopy(scenario)
        with patch.object(calibration, '_scenario', wraps=calibration._scenario) as normalize, patch.object(calibration, '_normalized_panel_calculation', wraps=calibration._normalized_panel_calculation) as calculate:
            relic_panel_diagnostics(scenario)
        normalize.assert_called_once_with(scenario)
        subsets = [tuple(call.args[0]['relic_ids']) for call in calculate.call_args_list]
        self.assertEqual(len(subsets), 4)
        self.assertEqual(len(set(subsets)), 4)
        self.assertEqual(scenario, original)

    def test_public_panel_entry_keeps_validation(self):
        with self.assertRaises(ValueError):
            calibration.panel_layers({'operator': 'mechanist', '_internal': True})

    def test_diagnostics_keep_first_three_operator_scope(self):
        with self.assertRaises(ValueError):
            relic_panel_diagnostics({'operator': 'char_002_amiya', 'relic_ids': ['rogue_6_relic_legacy_16']})
