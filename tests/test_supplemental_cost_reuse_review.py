import unittest
from copy import deepcopy
from unittest.mock import patch

from rouge import supplemental_cost as subject


class SupplementalCostReuseReviewTests(unittest.TestCase):
    def test_each_rule_is_classified_once_and_unknown_cost_stays_unknown(self):
        for verified in (True, False):
            with self.subTest(verified=verified):
                rule = {'kind': 'deployment_cost_pct',
                        'relic_id': 'rogue_6_relic_fight_11',
                        'value': -.5, '_verified_rule': verified}
                original = deepcopy(rule)
                with patch.object(subject, 'supported_cost', wraps=subject.supported_cost) as classify:
                    result = subject.cost_reference({'deployment_cost': 11}, [], [rule], [])
                self.assertEqual(classify.call_count, 1)
                self.assertEqual(result['estimated_cost'], 6 if verified else None)
                self.assertEqual(rule, original)
