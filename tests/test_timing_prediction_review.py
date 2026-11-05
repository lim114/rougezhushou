from copy import deepcopy
import unittest
from unittest.mock import patch

from rouge import calibration, damage
from rouge.timing_calibration import timing_reference


class TimingPredictionReviewTests(unittest.TestCase):
    def test_timing_reference_calculates_each_skill_once(self):
        for operator in ('kaltsit', 'silverash', 'mechanist'):
            for skill in (1, 2, 3):
                with self.subTest(operator=operator, skill=skill):
                    scenario = {'operator': operator, 'skill': skill}
                    original = deepcopy(scenario)
                    with patch.object(calibration, '_calculate_prepared', wraps=damage._calculate_prepared) as calculate:
                        with patch.object(damage, '_calculate_prepared', new=calculate):
                            result = timing_reference(scenario)
                    self.assertEqual(calculate.call_count, 1)
                    self.assertEqual(result['skill_identity']['skill'], skill)
                    self.assertEqual(result['context']['scenario']['operator'], operator)
                    self.assertEqual(scenario, original)

    def test_panel_and_timing_results_keep_independent_mutable_state(self):
        scenario = {'operator': 'kaltsit', 'skill': 1, 'relic_ids': []}
        panel = calibration.panel_layers(scenario)
        timing = timing_reference(scenario)
        token = timing['context_token']
        panel['context']['scenario']['relic_ids'].append('test-only')
        timing['context']['scenario']['relic_ids'].append('another-test')
        again = timing_reference(scenario)
        self.assertEqual(again['context_token'], token)
        self.assertEqual(again['context']['scenario']['relic_ids'], [])
        self.assertEqual(scenario['relic_ids'], [])
