"""Offline worksheets reuse the same inputs and predictions they expose."""
from copy import deepcopy
from unittest.mock import patch
import unittest
from rouge import calibration as c


class CalibrationConsumerReviewTests(unittest.TestCase):
    def test_packet_prepares_once_without_mutating_scenario(self):
        source = {'operator': 'mechanist', 'skill': 3, 'enemy_defense': 100,
                  'relic_ids': ['rogue_6_relic_legacy_16']}
        before = deepcopy(source)
        from rouge import damage
        with patch.object(damage, '_prepare_damage', wraps=damage._prepare_damage) as prepare, \
                patch.object(c, '_prepare_damage', prepare):
            result = c.packet_worksheet(source)
        self.assertEqual(prepare.call_count, 1)
        self.assertEqual(source, before)
        self.assertEqual(len(result['rows']), 2)

    def test_worksheet_uses_one_prediction_and_retains_context_rejection(self):
        case = {'id': 'cultivation', 'scenario': {'operator': 'mechanist', 'skill': 3},
                'panel': '培养与模组', 'values': {'attack': 573},
                'source': 'fixed public calculation', 'evidence_kind': 'formula_reference'}
        before = deepcopy(case)
        with patch.object(c, 'panel_layers', wraps=c.panel_layers) as predict:
            result = c.calibration_worksheets([case])
        self.assertEqual(predict.call_count, 1)
        self.assertEqual(case, before)
        self.assertEqual(result['matching_reference_cases'], 1)
        with self.assertRaisesRegex(ValueError, '观察值与预测条件不一致'):
            c.calibration_worksheets([{**case, 'context_token': 'different'}])


if __name__ == '__main__':
    unittest.main()
