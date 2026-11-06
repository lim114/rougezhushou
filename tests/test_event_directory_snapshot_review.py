from pathlib import Path
from unittest import TestCase
from unittest.mock import patch
from rouge import current_event_directory as model


class EventDirectorySnapshotTests(TestCase):
    def test_each_source_read_once_per_load_and_refreshed_next_load(self):
        original = Path.read_bytes
        reads = []
        def read(path):
            reads.append(path)
            return original(path)
        with patch.object(Path, 'read_bytes', read):
            self.assertIsNotNone(model.packet())
            first = list(reads)
            self.assertEqual(len(first), len(set(first)))
            self.assertEqual(first.count(model.ROOT / model.NOTES), 1)
            reads.clear()
            self.assertIsNotNone(model.packet())
            self.assertEqual(reads, first)

    def test_changed_notes_rejected_on_next_load(self):
        original = Path.read_bytes
        changed = False
        def read(path):
            raw = original(path)
            return raw + b' ' if changed and path == model.ROOT / model.NOTES else raw
        with patch.object(Path, 'read_bytes', read):
            self.assertIsNotNone(model.packet())
            changed = True
            self.assertIsNone(model.packet())
