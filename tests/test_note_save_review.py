"""Scoped save decisions and real editor action wiring, using temporary files."""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest
from PySide6.QtWidgets import QApplication
from rouge.player_notes import NotesDialog, NoteStore


class NoteSaveReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qt = QApplication.instance() or QApplication([])

    def test_metadata_type_error_is_visible_after_body_was_saved(self):
        with TemporaryDirectory() as folder:
            editor = NotesDialog(folder)
            self.addCleanup(editor.deleteLater)
            editor.autosave.setChecked(False)
            editor.set_context({'kind': 'battle', 'title': '公开测试场景'})
            editor.editor.setPlainText('本机隔离测试正文')
            with patch('rouge.player_note_library.NoteLibrary.record', side_effect=TypeError('internal defect')):
                with self.assertRaisesRegex(TypeError, 'internal defect'):
                    editor.save()
            self.assertFalse(editor.dirty)
            self.assertEqual(editor.store.read(editor.key)[0], '本机隔离测试正文')
            editor.close()

    def test_metadata_io_and_value_errors_keep_saved_body_with_warning(self):
        with TemporaryDirectory() as folder:
            editor = NotesDialog(folder)
            self.addCleanup(editor.deleteLater)
            editor.autosave.setChecked(False)
            editor.set_context({'kind': 'battle', 'title': '公开测试场景'})
            for error in (OSError('metadata IO'), ValueError('metadata mismatch')):
                with self.subTest(error=type(error).__name__):
                    editor.editor.setPlainText(str(error))
                    with patch('rouge.player_note_library.NoteLibrary.record', side_effect=error):
                        self.assertTrue(editor.save())
                    self.assertFalse(editor.dirty)
                    self.assertEqual(editor.store.read(editor.key)[0], str(error))
                    self.assertIn('场景标签未能更新', editor.status.text())
            editor.close()

    def test_cleanup_errors_after_publication_report_saved_content(self):
        @contextmanager
        def lock_cleanup_failure(destination):
            yield
            raise OSError('lock cleanup')

        with TemporaryDirectory() as folder:
            store = NoteStore(folder)
            key = 'isolated-key'
            expected = store.read(key)[1]
            with patch.object(Path, 'unlink', side_effect=OSError('temporary cleanup')):
                expected = store.save(key, 'first', expected)
            self.assertEqual(store.read(key), ('first', expected))
            self.assertIn('临时副本', store.save_warning)
            with patch('rouge.persistence_install.record_save_lock', lock_cleanup_failure):
                expected = store.save(key, 'second', expected)
            self.assertEqual(store.read(key), ('second', expected))
            self.assertIn('保存占用标记', store.save_warning)

    def test_failure_before_publication_keeps_original_and_raises(self):
        with TemporaryDirectory() as folder:
            store = NoteStore(folder)
            key = 'isolated-key'
            expected = store.save(key, 'original', store.read(key)[1])
            with patch('rouge.player_notes.os.replace', side_effect=OSError('publish failed')):
                with self.assertRaisesRegex(OSError, 'publish failed'):
                    store.save(key, 'replacement', expected)
            self.assertEqual(store.read(key), ('original', expected))
            self.assertIsNone(store.save_warning)

    def test_export_button_calls_existing_export_ui_with_same_editor(self):
        with TemporaryDirectory() as folder, patch('rouge.player_note_export_ui.export_editor') as export:
            editor = NotesDialog(folder)
            self.addCleanup(editor.deleteLater)
            editor.export_button.click()
            export.assert_called_once_with(editor)
            editor.close()
