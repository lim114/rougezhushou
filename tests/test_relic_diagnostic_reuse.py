from copy import deepcopy
import unittest
from unittest.mock import patch

from rouge import calibration
from rouge.relic_panel_diagnostics import relic_panel_diagnostics


class RelicDiagnosticReuseTests(unittest.TestCase):
    def test_each_ordered_relic_combination_is_calculated_once_per_query(self):
        ids = ['rogue_6_relic_legacy_27', 'rogue_6_relic_legacy_29', 'rogue_6_relic_legacy_12']
        scenario = {'operator': 'mechanist', 'skill': 1, 'relic_ids': ids}
        original = deepcopy(scenario)
        for count, expected in ((1, 2), (2, 4), (3, 8)):
            with self.subTest(audited=count):
                with patch.object(calibration, 'panel_layers', wraps=calibration.panel_layers) as predict:
                    first = relic_panel_diagnostics(scenario, ids[:count])
                    self.assertEqual(predict.call_count, expected)
                    combinations = [tuple(call.args[0]['relic_ids']) for call in predict.call_args_list]
                    self.assertEqual(len(set(combinations)), expected)
                    second = relic_panel_diagnostics(scenario, ids[:count])
                    self.assertEqual(predict.call_count, expected * 2)
                self.assertEqual(first, second)
                first['source_rows'][0]['fields'].clear()
                self.assertTrue(second['source_rows'][0]['fields'])
        self.assertEqual(scenario, original)
