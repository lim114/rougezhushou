from copy import deepcopy
import unittest
from unittest.mock import patch

from rouge import calibration
from rouge.calibration_experiment import calibration_experiment, public_experiment_payload


class ExperimentTimingPredictionReviewTests(unittest.TestCase):
    def test_control_and_three_timing_samples_each_calculate_once(self):
        for operator in ('kaltsit', 'silverash', 'mechanist'):
            with self.subTest(operator=operator):
                payload = public_experiment_payload(operator, 'timing')
                original = deepcopy(payload)
                with patch.object(calibration, '_calculate_prepared', wraps=calibration._calculate_prepared) as calculate:
                    report = calibration_experiment(**payload)
                self.assertEqual(calculate.call_count, 4)
                self.assertEqual(report['training_state'], 'compatible')
                self.assertEqual(report['overall_hypothesis_range']['lower'], 2)
                self.assertEqual(payload, original)

    def test_bad_timing_observation_remains_blocked_with_its_source(self):
        payload = public_experiment_payload('mechanist', 'timing')
        original_source = payload['experiment']['records'][0]['data']['observation']['source']
        payload['experiment']['records'][0]['data']['observation']['clock']['unit'] = 'unsupported'
        with patch.object(calibration, '_calculate_prepared', wraps=calibration._calculate_prepared) as calculate:
            report = calibration_experiment(**payload)
        self.assertEqual(calculate.call_count, 4)
        self.assertEqual(report['training_state'], 'blocked')
        self.assertEqual(report['records'][0]['source'], original_source)
        self.assertIn('record_validation_error', report['records'][0]['blocking_reasons'])
