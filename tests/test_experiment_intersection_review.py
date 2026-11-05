from copy import deepcopy
from fractions import Fraction
import unittest
from unittest.mock import patch

from rouge import calibration_experiment as experiment
from rouge.bounded_calibration import _interval


class ExperimentIntersectionReviewTests(unittest.TestCase):
    def test_parse_each_record_once_and_preserve_exact_open_bounds(self):
        entries = [('wide', _interval(Fraction(0), Fraction(1))),
                   ('lower', _interval(Fraction(1, 3), Fraction(1), False)),
                   ('upper', _interval(Fraction(0), Fraction(2, 3), True, False))]
        original = deepcopy(entries)
        with patch.object(experiment, '_bounds', wraps=experiment._bounds) as read:
            shared, witness = experiment._intersection(entries)
        self.assertEqual(read.call_count, len(entries))
        self.assertEqual(shared, _interval(Fraction(1, 3), Fraction(2, 3), False, False))
        self.assertIsNone(witness)
        self.assertEqual(entries, original)

    def test_tied_endpoint_witness_preserves_order_and_owns_its_data(self):
        entries = [('closed', _interval(Fraction(1), Fraction(2))),
                   ('strict', _interval(Fraction(1), Fraction(3), False)),
                   ('point', _interval(Fraction(0), Fraction(1)))]
        with patch.object(experiment, '_bounds', wraps=experiment._bounds) as read:
            shared, witness = experiment._intersection(entries)
        self.assertEqual(read.call_count, len(entries))
        self.assertIsNone(shared)
        self.assertEqual(witness['record_ids'], ['strict', 'point'])
        witness['lower_witness_residual']['lower'] = 99
        self.assertEqual(entries[1][1]['lower'], 1)
