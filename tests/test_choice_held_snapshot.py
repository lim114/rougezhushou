from copy import deepcopy
import unittest
from unittest.mock import patch
from rouge import choice_held_requirements as held


class ChoiceHeldSnapshotTests(unittest.TestCase):
    def test_original_lookup_uses_same_verified_snapshot(self):
        source = held.catalog._original()
        for identity in held.reference_data()['original_choices']:
            expected = held.original_reference(identity)
            with patch.object(held.catalog, '_original', side_effect=[source]) as read:
                self.assertEqual(held.original_reference(identity), expected)
                self.assertEqual(read.call_count, 1)

    def test_next_operation_rechecks_source_and_record(self):
        identity = next(iter(held.reference_data()['original_choices']))
        original = held.catalog._original()
        wrong_version = deepcopy(original)
        wrong_version['source']['game_data']['sha256'] = 'changed'
        with patch.object(held.catalog, '_original', return_value=wrong_version):
            with self.assertRaises(ValueError):
                held.original_reference(identity)
        changed = deepcopy(original)
        changed['choices'].pop(identity)
        with patch.object(held.catalog, '_original', return_value=changed):
            with self.assertRaises(ValueError):
                held.original_reference(identity)
        self.assertIsNotNone(held.original_reference(identity))

    def test_unknown_stays_absent_and_returned_row_is_independent(self):
        self.assertIsNone(held.original_reference('not-a-choice'))
        identity = next(iter(held.reference_data()['original_choices']))
        result = held.original_reference(identity)
        result['raw_record'].clear()
        self.assertTrue(held.original_reference(identity)['raw_record'])
