import unittest
import sys
from rouge.player_personal_statistics import complete_inventory, nonnegative_integer
from rouge.player_history_store import canonical_state


class StatisticsInventoryContractTests(unittest.TestCase):
    def test_quantity_boundary_retains_exact_integer_unknown_semantics(self):
        for value in (True, False, None, '1', -1, 1.0, float('inf'), 10**1000):
            self.assertFalse(nonnegative_integer(value))
        for value in (0, 1, int(sys.float_info.max)):
            self.assertTrue(nonnegative_integer(value))

    def test_archive_permitted_opaque_inventory_cannot_enter_complete_denominator(self):
        for extra in ({'tactical_tools': []}, {'relics': {'bad': None}},
                      {'relics': {'unknown': {'held': True}}}, {'relics': {'unknown': {'held': 'true'}}}):
            state = {'id': 'isolated-inventory', 'inventory_verified': True, 'relic_count': 0, **extra}
            canonical_state(state)
            self.assertFalse(complete_inventory(state))

    def test_known_empty_is_distinct_from_unconfirmed(self):
        self.assertTrue(complete_inventory({'inventory_verified': True, 'relic_count': 0}))
        self.assertFalse(complete_inventory({'relic_count': 0}))
        self.assertFalse(complete_inventory({'inventory_verified': True, 'relic_count': 1}))
