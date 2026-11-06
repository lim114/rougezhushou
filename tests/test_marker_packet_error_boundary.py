from pathlib import Path
from unittest.mock import patch
import unittest
from rouge import current_map_markers, boss_map_markers


class MarkerPacketErrorBoundaryTests(unittest.TestCase):
    def test_mapping_internal_errors_propagate(self):
        for model in (current_map_markers, boss_map_markers):
            for error in (ValueError('internal'), TypeError('internal'), KeyError('internal'), IndexError('internal')):
                with self.subTest(model=model.__name__, error=type(error).__name__), patch.object(model, 'packet', side_effect=error):
                    with self.assertRaises(type(error)):
                        model.mapping_for(model.STAGES[0], {})
            with self.subTest(model=model.__name__), self.assertRaises(KeyError):
                model.mapping_for(model.STAGES[0], {})

    def test_file_failure_and_unavailable_source(self):
        for model in (current_map_markers, boss_map_markers):
            with patch.object(Path, 'read_bytes', side_effect=OSError('read')):
                self.assertIsNone(model.packet())
            with patch.object(model, 'packet', return_value=None):
                self.assertIsNone(model.mapping_for(model.STAGES[0], {}))

    def test_root_resolved_once_and_member_link_rejected(self):
        original_resolve, original_link = Path.resolve, Path.is_symlink
        for model in (current_map_markers, boss_map_markers):
            roots = []
            def resolve(path, *args, **kwargs):
                if path == model.ROOT:
                    roots.append(path)
                return original_resolve(path, *args, **kwargs)
            with self.subTest(model=model.__name__), patch.object(Path, 'resolve', resolve):
                self.assertIsNotNone(model.packet())
                self.assertEqual(len(roots), 1)
            with patch.object(Path, 'is_symlink', lambda p: p == model.ROOT / model.DATA or original_link(p)):
                self.assertIsNone(model.packet())
