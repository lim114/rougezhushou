from copy import deepcopy
from importlib import import_module
import unittest
from unittest.mock import patch

from rouge import cultivation_comparison as comparison
from tests.test_cultivation_comparison_140 import proposal


class CultivationProposalReuseTests(unittest.TestCase):
    def test_strict_trust_is_checked_once_and_does_not_enter_legacy_validation(self):
        import math
        catalog = import_module('rouge.catalog')
        with patch.object(catalog, 'math', wraps=math) as numeric:
            comparison.compare_cultivation({'operator':'char_141_nights'}, {'proposals':[proposal('方案',trust=45)]})
            numeric.isfinite.assert_not_called()
            catalog.operator_attributes('char_141_nights',trust=45)
            numeric.isfinite.assert_called_once_with(45)

    def test_skill_calculation_reuses_each_proposals_validated_attributes(self):
        catalog = import_module('rouge.catalog')
        scenario = {'operator': 'mechanist', 'skill': 3, 'skill_rank': 7,
                    'relic_ids': ['rogue_6_relic_legacy_16']}
        preview = {'proposals': [proposal('低培养', elite=2, level=1, trust=0),
                                 proposal('满培养', elite=2, level=90)]}
        original = deepcopy((scenario, preview))
        with patch.object(catalog, '_attribute_values', wraps=catalog._attribute_values) as attributes:
            with patch.object(comparison, '_attribute_values', new=attributes):
                report = comparison.compare_cultivation(scenario, preview)
        self.assertEqual(attributes.call_count, 2)
        self.assertEqual((scenario, preview), original)
        for row in report['rows']:
            expected = catalog.operator_attributes('mechanist', **{k: v for k, v in row['proposal'].items() if k != 'name'})
            self.assertEqual(row['attributes'], expected)
            self.assertIsNotNone(row['window_damage'])
