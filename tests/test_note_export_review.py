"""Local export behavior, using temporary files and the real note editor."""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch
import unittest
from PySide6.QtWidgets import QApplication
from rouge.player_notes import NotesDialog
from rouge.player_note_export import publish_bytes
from rouge.player_note_export_acceptance import check


class NoteExportReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qt = QApplication.instance() or QApplication([])

    def test_real_editor_export_cancel_overwrite_and_modal_changes(self):
        with TemporaryDirectory() as folder:
            notes = NotesDialog(folder)
            self.addCleanup(notes.deleteLater)
            notes.autosave.setChecked(False)
            window = SimpleNamespace(player_notes=notes)
            check(window, self.qt, self.assertTrue)
            self.assertIs(window.player_validation_target, notes)
            notes.close()

    def test_shared_png_publisher_preserves_bytes_and_refuses_other_suffix(self):
        with TemporaryDirectory() as folder:
            raw = b'\x89PNG\r\n\x1a\npublic-test-payload'
            path = Path(folder) / 'card.png'
            result = publish_bytes(raw, path, suffixes=('.png',))
            self.assertEqual(path.read_bytes(), raw)
            self.assertEqual(result['bytes'], len(raw))
            with self.assertRaises(ValueError):
                publish_bytes(raw, Path(folder) / 'card.md', suffixes=('.png',))
            self.assertFalse((Path(folder) / 'card.md').exists())

    def test_failed_publish_and_cleanup_keep_original_publish_error(self):
        with TemporaryDirectory() as folder:
            path = Path(folder) / 'note.md'
            path.write_bytes(b'original')
            with patch('rouge.player_note_export.os.replace', side_effect=OSError('publication failed')), patch.object(Path, 'unlink', side_effect=OSError('cleanup failed')):
                with self.assertRaisesRegex(OSError, '^publication failed$'):
                    publish_bytes(b'replacement', path, overwrite=True)
            self.assertEqual(path.read_bytes(), b'original')
