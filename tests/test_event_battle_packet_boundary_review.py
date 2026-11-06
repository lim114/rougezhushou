import unittest
from pathlib import Path
from unittest.mock import patch
from rouge import current_event_battles


class EventBattlePacketBoundaryTests(unittest.TestCase):
    def test_upstream_internal_errors_propagate(self):
        for model in (current_event_battles,):
            for error in (ValueError('internal'), KeyError('internal'), TypeError('internal'), AttributeError('internal'), RecursionError('internal')):
                with self.subTest(module=model.__name__, error=type(error).__name__), patch.object(model.version, 'packet', side_effect=error):
                    with self.assertRaises(type(error)):
                        model.packet()

    def test_incomplete_upstream_contract_propagates(self):
        for model in (current_event_battles,):
            with self.subTest(module=model.__name__), patch.object(model.version, 'packet', return_value={}):
                with self.assertRaises(KeyError):
                    model.packet()

    def test_unavailable_upstream_remains_unavailable(self):
        for model in (current_event_battles,):
            with self.subTest(module=model.__name__), patch.object(model.version, 'packet', return_value=None):
                self.assertIsNone(model.packet())

    def test_file_failure_remains_unavailable(self):
        for model in (current_event_battles,):
            with self.subTest(module=model.__name__), patch.object(Path, 'read_bytes', side_effect=OSError('unreadable')):
                self.assertIsNone(model.packet())

    def test_member_links_still_rejected(self):
        original = Path.is_symlink
        for model in (current_event_battles,):
            with self.subTest(module=model.__name__), patch.object(Path, 'is_symlink', lambda path: path == model.ROOT / model.DATA or original(path)):
                self.assertIsNone(model.packet())
