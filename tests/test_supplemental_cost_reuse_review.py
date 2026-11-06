import unittest
from copy import deepcopy

from rouge import supplemental_cost as subject


class SupplementalCostReuseReviewTests(unittest.TestCase):
    def test_unresolved_cost_stays_unknown_after_entry_classification(self):
        for verified in (True, False):
            with self.subTest(verified=verified):
                rule = {'kind': 'deployment_cost_pct',
                        'relic_id': 'rogue_6_relic_fight_11',
                        'value': -.5, '_verified_rule': verified}
                original = deepcopy(rule)
                layer = subject.cost_layer(rule)
                selected = [(layer,rule)] if layer is not None else []
                unresolved = [] if selected else [rule]
                result = subject.cost_reference({'deployment_cost': 11}, [], selected, unresolved, [])
                self.assertEqual(result['estimated_cost'], 6 if verified else None)
                self.assertEqual(rule, original)
