from unittest import TestCase
from unittest.mock import patch
from rouge import timing_calibration, bounded_calibration


class CalibrationNumberBoundaryTests(TestCase):
    def test_builtin_invalid_numbers_keep_input_errors(self):
        for module in (timing_calibration, bounded_calibration):
            for value in (10**1000, True, -1, float('inf'), float('nan'), '1', None):
                with self.subTest(module=module.__name__, value_type=type(value).__name__), self.assertRaises(ValueError):
                    module._number(value, '测试值')
            self.assertEqual(module._number(0, '测试值'), 0)
            self.assertEqual(module._number(3, '测试值'), 3)

    def test_internal_value_error_is_not_relabelled_as_input_error(self):
        for module in (timing_calibration, bounded_calibration):
            failure = ValueError('internal numeric failure')
            with self.subTest(module=module.__name__), patch.object(module.math, 'isfinite', side_effect=failure):
                with self.assertRaises(ValueError) as caught:
                    module._number(1, '测试值')
                self.assertIs(caught.exception, failure)
