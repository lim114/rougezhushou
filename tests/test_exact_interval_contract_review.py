from fractions import Fraction
from unittest import TestCase
from rouge.bounded_calibration import _bounds, _interval, _subtract


class ExactIntervalContractTests(TestCase):
    def test_exact_values_are_used_without_rounded_display_endpoints(self):
        self.assertEqual(_bounds({'lower_exact': '1/3', 'upper_exact': '2/3'}), (Fraction(1, 3), Fraction(2, 3)))
        value = _interval(Fraction(1, 3), Fraction(2, 3))
        value['lower'] = 99
        value['upper'] = 100
        self.assertEqual(_bounds(value), (Fraction(1, 3), Fraction(2, 3)))

    def test_missing_exact_endpoint_is_not_float_compatibility(self):
        for missing in ('lower_exact', 'upper_exact'):
            value = _interval(Fraction(1, 3), Fraction(2, 3))
            del value[missing]
            with self.subTest(missing=missing), self.assertRaises(KeyError):
                _bounds(value)

    def test_arithmetic_retains_exact_results(self):
        a = _interval(Fraction(1, 3), Fraction(2, 3))
        b = _interval(Fraction(1, 7), Fraction(2, 7))
        self.assertEqual(_bounds(_subtract(a, b)), (Fraction(1, 21), Fraction(11, 21)))
