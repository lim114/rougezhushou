import unittest
from rouge.player_history_store import canonical_state
from rouge.player_personal_statistics import unique_archives


class StatisticsArchiveContractTests(unittest.TestCase):
    def test_store_boundary_rejects_invalid_state_or_identity(self):
        for state in (None, [], {}, {'id': None}, {'id': ''}, {'id': 7}):
            with self.subTest(state=state), self.assertRaises(ValueError):
                canonical_state(state)

    def test_internal_contract_error_is_not_counted_as_missing_sample(self):
        for record, error in ((None, TypeError), ({}, KeyError), ({'state': {}}, KeyError)):
            with self.subTest(record=record), self.assertRaises(error):
                unique_archives([record])

    def test_newest_record_per_run_is_preserved_without_copy_or_mutation(self):
        newest = {'state': {'id': 'a'}, 'created_at': 3}
        other = {'state': {'id': 'b'}, 'created_at': 2}
        older = {'state': {'id': 'a'}, 'created_at': 1}
        rows = [newest, other, older]
        result = unique_archives(rows)
        self.assertEqual(result, [newest, other])
        self.assertIs(result[0], newest)
        self.assertEqual(len(rows), 3)
