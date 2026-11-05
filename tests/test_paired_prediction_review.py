"""Existing panel predictions are shared by independent observation comparisons."""
from copy import deepcopy
from unittest.mock import patch
import unittest
from rouge import calibration as c, paired_calibration as paired
from rouge.calibration_experiment import calibration_experiment, public_experiment_payload


class PairedPredictionReviewTests(unittest.TestCase):
    def test_pair_predicts_each_side_once_and_validates_tolerance_once(self):
        payload = paired.public_paired_payload('silverash')
        before = deepcopy(payload)
        with patch.object(c, 'panel_layers', wraps=c.panel_layers) as predict, \
                patch.object(paired, 'panel_layers', predict), \
                patch.object(c, '_number', wraps=c._number) as number, \
                patch.object(paired, '_number', number):
            result = paired.compare_paired_panels(**payload)
        self.assertEqual(predict.call_count, 2)
        self.assertEqual(sum(call.args[1] == 'tolerance' for call in number.call_args_list), 1)
        self.assertEqual(payload, before)
        self.assertEqual(result['rows'][0]['model_after_minus_before'], 60)

    def test_panel_experiment_predicts_control_and_each_sample_once(self):
        payload = public_experiment_payload('mechanist', 'panel')
        before = deepcopy(payload)
        with patch.object(c, 'panel_layers', wraps=c.panel_layers) as predict:
            result = calibration_experiment(**payload)
        self.assertEqual(predict.call_count, 4)
        self.assertEqual(payload, before)
        self.assertEqual(len(result['records']), 3)


if __name__ == '__main__':
    unittest.main()
