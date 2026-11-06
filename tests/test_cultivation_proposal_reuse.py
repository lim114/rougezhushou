from copy import deepcopy
from importlib import import_module
import unittest
from unittest.mock import patch

from rouge import cultivation_comparison as comparison
from tests.test_cultivation_comparison_140 import proposal


class CultivationProposalReuseTests(unittest.TestCase):
    def test_skill_calculation_reuses_each_proposals_validated_attributes(self):
        catalog = import_module('rouge.catalog')
        scenario = {'operator': 'mechanist', 'skill': 3, 'skill_rank': 7,
                    'relic_ids': ['rogue_6_relic_legacy_16']}
        preview = {'proposals': [proposal('低培养', elite=2, level=1, trust=0),
                                 proposal('满培养', elite=2, level=90)]}
        original = deepcopy((scenario, preview))
        with patch.object(catalog, '_operator_attribute_reference', wraps=catalog._operator_attribute_reference) as attributes:
            with patch.object(comparison, '_operator_attribute_reference', new=attributes):
                report = comparison.compare_cultivation(scenario, preview)
        self.assertEqual(attributes.call_count, 2)
        self.assertEqual((scenario, preview), original)
        for row in report['rows']:
            expected = catalog.operator_attributes('mechanist', **{k: v for k, v in row['proposal'].items() if k != 'name'})
            self.assertEqual(row['attributes'], expected)
            self.assertIsNotNone(row['window_damage'])
