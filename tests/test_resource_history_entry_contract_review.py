import unittest
from rouge.run_state import _validate_saved_containers
from rouge.player_resource_history import resource_rows


class ResourceHistoryEntryContractTests(unittest.TestCase):
    def test_saved_history_rejects_non_mapping_before_installation(self):
        with self.assertRaises(ValueError):
            _validate_saved_containers({'operators': {}, 'history': [None]})

    def test_resource_field_still_requires_qualification(self):
        state = {'operators': {}, 'history': [
            {'kind': 'resource_updated', 'resource': [], 'value': 5},
            {'kind': 'resource_updated', 'resource': 'gold', 'value': 0}]}
        _validate_saved_containers(state)
        rows = resource_rows(state)
        self.assertEqual(len(rows), 1)
        self.assertEqual((rows[0]['resource'], rows[0]['value']), ('gold', 0))

    def test_internal_history_contract_break_is_not_silent(self):
        with self.assertRaises(AttributeError):
            resource_rows({'history': [None]})
