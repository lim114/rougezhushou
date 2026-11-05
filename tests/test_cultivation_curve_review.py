"""Reuse identical cultivation inputs within one offline query only."""
from copy import deepcopy
from importlib import import_module
from unittest.mock import patch
import unittest
from rouge import calibration as c


class CultivationCurveReviewTests(unittest.TestCase):
    def test_curve_evaluates_each_distinct_cultivation_once(self):
        source = {'operator': 'mechanist', 'skill': 3, 'level': 60,
                  'trust': 0, 'potential': 1}
        before = deepcopy(source)
        with patch.object(c, 'operator_attributes', wraps=c.operator_attributes) as attributes:
            result = c.cultivation_curve(source, levels=[59, 60])
        self.assertEqual(attributes.call_count, 2)
        self.assertEqual(source, before)
        self.assertTrue(all(value['trust_increment'] == value['potential_increment'] == value['module_increment'] == 0
                            for row in result['rows'] for value in row['contributions'].values()))
        result['rows'][0]['cultivated']['attack'] = -1
        self.assertGreater(result['rows'][1]['cultivated']['attack'], 0)
        self.assertGreater(c.cultivation_curve(source, levels=[59])['rows'][0]['cultivated']['attack'], 0)

    def test_talent_times_reuse_cultivation_but_keep_time_dependent_results(self):
        catalog = import_module('rouge.catalog')
        source = {'operator': 'silverash', 'skill': 3}
        before = deepcopy(source)
        with patch.object(catalog, 'operator_attributes', wraps=catalog.operator_attributes) as attributes, \
                patch.object(c, 'operator_attributes', attributes):
            result = c.talent_states(source, elapsed_seconds=[14.9, 15])
        self.assertEqual(attributes.call_count, 1)
        self.assertEqual(source, before)
        self.assertEqual([r['base_stats']['defense'] for r in result['rows']], [497, 557])


if __name__ == '__main__':
    unittest.main()
