import unittest
from copy import deepcopy
from rouge.record_flags import record_flag, metadata_mask, projected_run_metadata, RUN_METADATA_KEYS
from rouge.run_state import _validate_saved_containers
from rouge.player_context import recent_content


class RecordProjectionContractTests(unittest.TestCase):
    def test_legacy_flag_and_explicit_unknown_are_distinct(self):
        self.assertIs(record_flag({}, 'held'), True)
        for raw in (True, False, None, 0, 1, 'true', [], {}):
            record = {'held': raw}
            before = deepcopy(record)
            self.assertIs(record_flag(record, 'held'), raw if type(raw) is bool else None)
            self.assertEqual(record, before)

    def test_opaque_bad_metadata_is_qualified_without_repairing_original(self):
        for mask in (None, 'advanced', [7]):
            member = {'unconfirmed_run_metadata': mask, 'qualified_char_buff_ids': [7],
                      'advanced': True, 'recruitment_kind': 'emergency_hire'}
            state = {'operators': {'mechanist': member}}
            _validate_saved_containers(state)
            before = deepcopy(member)
            self.assertEqual(metadata_mask(member), set(RUN_METADATA_KEYS))
            view = projected_run_metadata(member)
            self.assertIsNone(view['recruitment_kind'])
            self.assertNotIn('advanced', view)
            self.assertEqual(view['char_buff_ids'], [])
            self.assertFalse(view['char_buffs_complete'])
            self.assertEqual(member, before)

    def test_valid_mask_preserves_qualified_positive_ids(self):
        member = {'unconfirmed_run_metadata': ['char_buff_ids'], 'qualified_char_buff_ids': ['known']}
        self.assertEqual(projected_run_metadata(member)['char_buff_ids'], ['known'])
        healthy = {'advanced': True}
        self.assertIs(projected_run_metadata(healthy), healthy)

    def test_internal_missing_title_is_not_hidden_as_unread(self):
        with self.assertRaises(KeyError):
            recent_content({'last_node_content': {'kind': 'battle'}})
        for value in (None, {}):
            self.assertEqual(recent_content({'last_node_content': value}), '')
