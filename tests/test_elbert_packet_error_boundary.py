import json
from unittest.mock import patch
import unittest
from rouge import current_elbert_reference as model


class ElbertPacketBoundaryTests(unittest.TestCase):
    def test_dependency_errors_propagate(self):
        for error in (ValueError, TypeError, KeyError, AttributeError, RecursionError, OSError):
            with self.subTest(error=error.__name__), patch.object(model.battle, 'packet', side_effect=error('internal')):
                with self.assertRaises(error): model.packet()

    def test_explicit_source_rejections_remain_unavailable(self):
        for error in (OSError, ValueError):
            with patch.object(model, '_read_public', side_effect=error('invalid')):
                self.assertIsNone(model.packet())
        with patch.object(model.json, 'loads', side_effect=json.JSONDecodeError('bad', '', 0)):
            self.assertIsNone(model.packet())
        with patch.object(model, 'source_rows', side_effect=ValueError('unreviewed constructor')):
            self.assertIsNone(model.packet())

    def test_internal_constructor_and_portrait_errors_surface(self):
        for error in (TypeError, KeyError, AttributeError):
            with self.subTest(error=error.__name__), patch.object(model, 'source_rows', side_effect=error('internal')):
                with self.assertRaises(error): model.packet()
        with patch.object(model.battle, 'enemy_records', side_effect=ValueError('internal')):
            with self.assertRaises(ValueError): model.packet()

    def test_valid_and_missing_dependency(self):
        self.assertIsNotNone(model.packet())
        with patch.object(model.battle, 'packet', return_value=None):
            self.assertIsNone(model.packet())
