from unittest import TestCase
from unittest.mock import patch
from rouge.supplemental_comparison import comparison_rows


class UnknownBaselineTests(TestCase):
    def test_no_baseline_keeps_both_reference_and_delta_unknown(self):
        measured = [{'key': 'x', 'name': '数值', 'value': 5, 'unit': '点'}]
        with patch('rouge.supplemental_comparison.metrics', return_value=measured) as project:
            rows = comparison_rows({'fixture': True}, None)
        project.assert_called_once_with({'fixture': True})
        self.assertIsNone(rows[0]['base_value'])
        self.assertIsNone(rows[0]['delta'])

    def test_prepared_baseline_is_reused_and_zero_is_a_value(self):
        measured = [{'key': 'x', 'name': '数值', 'value': 5, 'unit': '点'},
                    {'key': 'y', 'name': '未知分项', 'value': None, 'unit': '点'}]
        prepared = {'x': 0, 'y': 1}
        with patch('rouge.supplemental_comparison.metrics', return_value=measured) as project:
            rows = comparison_rows({'fixture': True}, {'baseline': True}, baseline_values=prepared)
        project.assert_called_once_with({'fixture': True})
        self.assertEqual(rows[0]['delta'], 5)
        self.assertIsNone(rows[1]['delta'])
        self.assertEqual(prepared, {'x': 0, 'y': 1})
