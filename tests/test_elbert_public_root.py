from pathlib import Path
from unittest.mock import patch
import unittest
from rouge import current_elbert_reference as model


class ElbertPublicRootTests(unittest.TestCase):
    def test_packet_resolves_its_root_once(self):
        original = Path.resolve
        roots = []
        def resolve(path, *args, **kwargs):
            if path == model.ROOT: roots.append(path)
            return original(path, *args, **kwargs)
        # Scope the measurement to this packet; the dependency owns its own root.
        current = model.battle.packet()
        with patch.object(model.battle, 'packet', return_value=current), patch.object(Path, 'resolve', resolve):
            self.assertIsNotNone(model.packet())
        self.assertEqual(len(roots), 1)

    def test_public_reader_still_rejects_unsafe_paths_and_links(self):
        for name in ('../outside', '/absolute', 'C:/outside', 'a/../b'):
            with self.subTest(name=name), self.assertRaises(ValueError): model._read_public(name)
        original = Path.is_symlink
        for target in (model.ROOT / model.DATA, (model.ROOT / model.DATA).parent):
            with self.subTest(target=target), patch.object(Path, 'is_symlink', lambda p: p == target or original(p)):
                with self.assertRaises(ValueError): model._read_public(model.DATA)

    def test_independent_reads_resolve_each_time(self):
        original = Path.resolve
        roots = []
        def resolve(path, *args, **kwargs):
            if path == model.ROOT: roots.append(path)
            return original(path, *args, **kwargs)
        with patch.object(Path, 'resolve', resolve):
            a = model._read_public(model.DATA)
            b = model._read_public(model.DATA)
        self.assertEqual(a, b)
        self.assertEqual(len(roots), 2)
