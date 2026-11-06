import json
from pathlib import Path
from unittest.mock import patch
import unittest
from rouge import current_hanko, current_sun_boss


class DocumentaryErrorBoundaryTests(unittest.TestCase):
    def test_dependency_errors_propagate(self):
        for model in (current_hanko, current_sun_boss):
            for cls in (ValueError, TypeError, KeyError, IndexError, AttributeError, RecursionError, OSError):
                with self.subTest(error=cls.__name__), patch.object(model.battle, 'packet', side_effect=cls('internal')):
                    with self.assertRaises(cls):
                        model.packet()

    def test_file_path_and_json_failures_remain_unavailable(self):
        for model in (current_hanko, current_sun_boss):
            with patch.object(model.battle.version, '_file', side_effect=ValueError('unsafe')):
                self.assertIsNone(model.packet())
            with patch.object(Path, 'read_bytes', side_effect=OSError('read')):
                self.assertIsNone(model.packet())
            with patch.object(model.json, 'loads', side_effect=json.JSONDecodeError('invalid', '', 0)):
                self.assertIsNone(model.packet())

    def test_internal_parser_contract_failure_propagates(self):
        for model in (current_hanko, current_sun_boss):
            with patch.object(model.json, 'loads', return_value={}):
                with self.assertRaises(KeyError):
                    model.packet()
            with patch.object(model.json, 'loads', side_effect=TypeError('internal')):
                with self.assertRaises(TypeError):
                    model.packet()

    def test_unavailable_dependency_and_valid_packet(self):
        for model in (current_hanko, current_sun_boss):
            with patch.object(model.battle, 'packet', return_value=None):
                self.assertIsNone(model.packet())
            self.assertIsNotNone(model.packet())
