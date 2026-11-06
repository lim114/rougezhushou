from pathlib import Path
from unittest.mock import patch
import unittest
from rouge import current_map_position as model, current_terrain as terrain


class MapPacketErrorBoundaryTests(unittest.TestCase):
    def test_upstream_internal_errors_propagate(self):
        for owner, name in ((terrain, 'evidence_identity'), (model.battle, 'packet')):
            for error in (ValueError('internal'), TypeError('internal'), KeyError('internal'), OSError('internal')):
                with self.subTest(entry=name, error=type(error).__name__), patch.object(owner, name, side_effect=error):
                    with self.assertRaises(type(error)):
                        model.packet()

    def test_unavailable_upstream_remains_unavailable(self):
        for owner, name in ((terrain, 'evidence_identity'), (model.battle, 'packet')):
            with self.subTest(entry=name), patch.object(owner, name, return_value=None):
                self.assertIsNone(model.packet())

    def test_own_file_failure_remains_unavailable(self):
        with patch.object(terrain, 'evidence_identity', return_value='verified'), patch.object(Path, 'read_bytes', side_effect=OSError('read')):
            self.assertIsNone(model.packet())

    def test_member_links_rejected_and_root_resolved_once(self):
        original_link, original_resolve = Path.is_symlink, Path.resolve
        member = model.ROOT / model.DATA
        with patch.object(terrain, 'evidence_identity', return_value='verified'), patch.object(Path, 'is_symlink', lambda path: path == member or original_link(path)):
            self.assertIsNone(model.packet())
        roots = []
        def resolve(path, *args, **kwargs):
            if path == model.ROOT:
                roots.append(path)
            return original_resolve(path, *args, **kwargs)
        current = model.battle.packet()
        with patch.object(terrain, 'evidence_identity', return_value='verified'), patch.object(model.battle, 'packet', return_value=current), patch.object(Path, 'resolve', resolve):
            self.assertIsNotNone(model.packet())
        self.assertEqual(len(roots), 1)
