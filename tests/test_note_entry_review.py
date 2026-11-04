"""Notebook lifecycle checks using an isolated note folder and public contexts."""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest
from PySide6.QtWidgets import QApplication
from rouge.player_inline_notes import InlineNotesPanel
from rouge.player_notes import NotesDialog
from rouge.run_state import RunState
from tests.test_inline_notebook_review import rows


class NoteEntryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qt = QApplication.instance() or QApplication([])

    def test_refresh_during_control_construction_waits_until_all_controls_exist(self):
        original = InlineNotesPanel.compact_controls
        states = []

        def construct(panel):
            states.append(panel.inline_ready)
            panel.refresh(force=True)
            original(panel)
            states.append(panel.inline_ready)

        with TemporaryDirectory() as folder, patch('rouge.player_note_selector.catalogue_snapshot', return_value={'rows': rows(), 'unavailable': []}):
            editor = NotesDialog(Path(folder) / 'notes')
            self.addCleanup(editor.deleteLater)
            with patch.object(InlineNotesPanel, 'compact_controls', construct):
                panel = InlineNotesPanel(RunState(Path(folder) / 'run.json'), editor)
            self.addCleanup(panel.deleteLater)
            panel.timer.stop()
            editor.autosave_timer.stop()
            self.assertEqual(states, [False, False])
            self.assertTrue(panel.inline_ready)
            panel.refresh(force=True)
            self.assertTrue(panel.save_state.text())
            panel.close()

    def test_timer_refreshes_only_visible_notebook(self):
        with TemporaryDirectory() as folder, patch('rouge.player_note_selector.catalogue_snapshot', return_value={'rows': rows(), 'unavailable': []}):
            editor = NotesDialog(Path(folder) / 'notes')
            panel = InlineNotesPanel(RunState(Path(folder) / 'run.json'), editor)
            self.addCleanup(panel.deleteLater)
            panel.timer.stop()
            editor.autosave_timer.stop()
            with patch.object(panel, 'refresh') as refresh:
                panel.timer.timeout.emit()
                refresh.assert_not_called()
                panel.show()
                self.qt.processEvents()
                refresh.reset_mock()
                panel.timer.timeout.emit()
                refresh.assert_called_once_with()
                panel.hide()
                refresh.reset_mock()
                panel.timer.timeout.emit()
                refresh.assert_not_called()
            panel.close()
