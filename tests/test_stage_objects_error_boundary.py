import unittest
from unittest.mock import patch
from rouge import current_stage_objects as model


class StageObjectsErrorBoundaryTests(unittest.TestCase):
    def test_internal_derive_errors_propagate(self):
        current = model.battle.stage_reference('ro6_n_1_1')
        for error in (ValueError('internal'), KeyError('internal'), TypeError('internal'), IndexError('internal')):
            with self.subTest(error=type(error).__name__), patch.object(model, '_derive', side_effect=error):
                with self.assertRaises(type(error)):
                    model.from_battle(current)

    def test_manifest_internal_errors_propagate(self):
        for error in (ValueError('internal'), KeyError('internal'), TypeError('internal')):
            with self.subTest(error=type(error).__name__), patch.object(model.json, 'loads', side_effect=error):
                with self.assertRaises(type(error)):
                    model.packet()

    def test_read_and_parse_failures_remain_unavailable(self):
        for error in (OSError('read'), ValueError('path refused')):
            with self.subTest(error=type(error).__name__), patch.object(model.battle.version, '_file', side_effect=error):
                self.assertIsNone(model.packet())
        with patch.object(model.json, 'loads', side_effect=model.json.JSONDecodeError('invalid', '', 0)):
            self.assertIsNone(model.packet())

    def test_missing_verified_manifest_field_propagates(self):
        with patch.object(model.json, 'loads', return_value={}):
            with self.assertRaises(KeyError):
                model.packet()
