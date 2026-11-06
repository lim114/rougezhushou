import json
import unittest
from unittest.mock import patch
from rouge import current_spawn_candidates as model


class SpawnCandidateErrorBoundaryTests(unittest.TestCase):
    def test_internal_derivation_errors_propagate(self):
        for error in (ValueError('internal'), TypeError('internal'), KeyError('internal'), IndexError('internal')):
            with self.subTest(error=type(error).__name__), patch.object(model, '_build', side_effect=error):
                with self.assertRaises(type(error)):
                    model.stage_reference('ro6_n_1_1')

    def test_internal_manifest_errors_propagate(self):
        for error in (ValueError('internal'), TypeError('internal'), KeyError('internal')):
            with self.subTest(error=type(error).__name__), patch.object(json, 'loads', side_effect=error):
                with self.assertRaises(type(error)):
                    model._packet()
        with patch.object(json, 'loads', return_value={}):
            with self.assertRaises(KeyError):
                model._packet()

    def test_expected_read_and_parse_errors_remain_unavailable(self):
        for error in (OSError('read'), ValueError('path refused')):
            with self.subTest(error=type(error).__name__), patch.object(model.battle.version, '_file', side_effect=error):
                self.assertIsNone(model._packet())
        with patch.object(json, 'loads', side_effect=json.JSONDecodeError('invalid', '', 0)):
            self.assertIsNone(model._packet())
