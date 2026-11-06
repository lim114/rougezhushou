from pathlib import Path
from unittest.mock import patch
import unittest
from rouge import current_terrain as model


class TerrainBoundaryReviewTests(unittest.TestCase):
    def test_internal_manifest_errors_propagate(self):
        for error in (ValueError('internal'), TypeError('internal'), KeyError('internal')):
            with self.subTest(error=type(error).__name__), patch.object(model.json, 'loads', side_effect=error):
                with self.assertRaises(type(error)):
                    model.evidence_identity()

    def test_io_failure_and_root_once(self):
        with patch.object(Path, 'read_bytes', side_effect=OSError('read')):
            self.assertIsNone(model.evidence_identity())
        roots = []
        original = Path.resolve
        def resolve(path, *args, **kwargs):
            if path == model.ROOT:
                roots.append(path)
            return original(path, *args, **kwargs)
        with patch.object(Path, 'resolve', resolve):
            self.assertEqual(model.evidence_identity(), model.MANIFEST_SHA256)
        self.assertEqual(len(roots), 1)

    def test_number_contract(self):
        for value in (None, False, '1', 10**1000, float('inf'), float('nan')):
            self.assertFalse(model._number(value))
        for value in (0, 1, -1.5):
            self.assertTrue(model._number(value))
        with patch.object(model, 'isfinite', side_effect=TypeError('internal')):
            with self.assertRaises(TypeError):
                model._number(1)

    def test_duplicate_expected_and_extra_parameters_keep_unknown(self):
        unknowns = []
        rows = [{'key': key, 'value': value} for key, value in (
            ('a', 1), ('a', 2), ('a', 3), ('extra', 1), ('extra', 2), ('b', 4))]
        self.assertEqual(model._parameters({'blackboard': rows}, {'a', 'b'}, unknowns), {'b': 4})
        self.assertEqual(len(unknowns), 2)
