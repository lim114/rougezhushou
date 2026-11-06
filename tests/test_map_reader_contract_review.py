from unittest import TestCase
from unittest.mock import patch
from PySide6.QtWidgets import QApplication
from rouge.player_map_reader import make_reader


class MapReaderContractTests(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_battle_title_is_loaded_from_verified_source(self):
        dialog = make_reader('battle', {'id': 'ro6_n_1_2'}, None)
        self.assertIsNotNone(dialog)
        self.addCleanup(dialog.close)
        self.assertIn('遗忘时间', dialog.windowTitle())

    def test_missing_internal_battle_identity_is_exposed(self):
        with self.assertRaises(KeyError):
            make_reader('battle', {}, None)

    def test_event_record_is_validated_by_binding_entry(self):
        record = {'id': 'community_group_001'}
        with patch('rouge.current_node_readers.binding_for', return_value=None) as binding:
            self.assertIsNone(make_reader('event', record, None))
            binding.assert_called_once_with(record)

    def test_unsupported_kind_remains_unavailable(self):
        self.assertIsNone(make_reader('unknown', {}, None))
