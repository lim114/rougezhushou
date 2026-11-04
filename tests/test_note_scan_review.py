"""Single-refresh file handling with temporary, synthetic notes."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest
from rouge.player_note_library import NoteLibrary
from rouge.player_notes import NoteStore, content_key


class NoteScanReviewTests(unittest.TestCase):
    def test_failed_indexed_body_is_read_once_then_recovers_next_refresh(self):
        with TemporaryDirectory() as folder:
            content = {'kind': 'event', 'title': '公开测试'}
            library = NoteLibrary(folder)
            store = NoteStore(folder)
            key = content_key(content)
            store.save(key, '恢复后的正文', store.read(key)[1])
            library.record(content)
            target = store.path(key)
            original = Path.read_text
            attempts = []

            def unreadable(path, *args, **kwargs):
                if path == target:
                    attempts.append(path)
                    raise PermissionError('file temporarily unavailable')
                return original(path, *args, **kwargs)

            with patch.object(Path, 'read_text', unreadable):
                self.assertEqual(library.rows(), [])
            self.assertEqual(library.issues, [target.name])
            self.assertEqual(len(attempts), 1)
            rows = library.rows()
            self.assertEqual(rows[0]['text'], '恢复后的正文')
            self.assertFalse(rows[0]['legacy'])
            self.assertEqual(library.issues, [])

    def test_temporary_cleanup_tolerates_file_removed_just_before_unlink(self):
        with TemporaryDirectory() as folder:
            library = NoteLibrary(folder)
            content = {'kind': 'event', 'title': '公开测试'}
            # A new metadata file is published with os.link, leaving the temp name.
            original = Path.unlink

            def removed_elsewhere(path, *args, **kwargs):
                if path.name.startswith('.index-'):
                    original(path)
                return original(path, *args, **kwargs)

            with patch.object(Path, 'unlink', removed_elsewhere):
                library.record(content)
            self.assertEqual(library.records()[content_key(content)]['content'], content)
            self.assertEqual(list(Path(folder).glob('.index-*')), [])

    def test_cleanup_permission_failure_still_propagates_after_publication(self):
        with TemporaryDirectory() as folder:
            library = NoteLibrary(folder)
            content = {'kind': 'event', 'title': '公开测试'}
            with patch.object(Path, 'unlink', side_effect=PermissionError('cleanup denied')):
                with self.assertRaisesRegex(PermissionError, 'cleanup denied'):
                    library.record(content)
            self.assertEqual(library.records()[content_key(content)]['content'], content)
