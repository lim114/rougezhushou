"""Unchanged source refresh and invalidation of a local scene reader."""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
from copy import deepcopy
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication, QWidget
from rouge import player_note_reference as subject


class NoteReferenceEntryReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qt = QApplication.instance() or QApplication([])

    def test_normal_start_without_library_has_explicit_empty_page_state(self):
        from rouge.player_compact import CompactAssistant
        owner = QWidget()
        owner.run = SimpleNamespace(state={})
        owner.closing = True
        owner.map_overlay_reference = None
        owner.session_recorder = None
        owner.node_statistics_source = lambda: None
        owner.compact_window = None
        self.addCleanup(owner.deleteLater)
        self.assertIsNone(subject.open_shared(owner, {}, ('stages', 'public-id')))
        bar = CompactAssistant(owner)
        owner.compact_window = bar
        self.addCleanup(bar.close)
        self.assertIsNone(bar.note_library_page)
        self.assertIsNone(subject.open_shared(owner, {}, ('stages', 'public-id')))
        bar.reference_window.pages.addWidget(QWidget())
        self.assertIsNone(subject.open_shared(owner, {}, ('stages', 'public-id')))

    def test_unchanged_source_rechecks_without_reformatting_and_keeps_selection(self):
        result = {'row': {'label': '公开情景', 'value': {'description': '原文说明'}}, 'player_text': '来源说明'}
        with patch.object(subject.model, 'detail', return_value=deepcopy(result)) as detail:
            panel = subject.NoteScenePanel('public-scene')
            self.addCleanup(panel.deleteLater)
            cursor = panel.text.textCursor()
            cursor.setPosition(0)
            cursor.setPosition(2, QTextCursor.MoveMode.KeepAnchor)
            panel.text.setTextCursor(cursor)
            with patch.object(subject.model, '_plain', wraps=subject.model._plain) as formatting:
                for _ in range(3):
                    self.assertTrue(panel.refresh_reference())
                formatting.assert_not_called()
            self.assertEqual(detail.call_count, 4)
            self.assertEqual(panel.text.textCursor().selectedText(), '原文')
            self.assertEqual(panel.details.toPlainText(), '来源说明')

    def test_changed_or_missing_source_clears_stale_text(self):
        result = {'row': {'label': '公开情景', 'value': {'description': '原文说明'}}, 'player_text': '来源说明'}
        for fresh in (None, {**result, 'player_text': '已更新来源'}):
            with self.subTest(fresh=fresh), patch.object(subject.model, 'detail', return_value=result):
                panel = subject.NoteScenePanel('public-scene')
                self.addCleanup(panel.deleteLater)
                with patch.object(subject.model, 'detail', return_value=fresh):
                    self.assertFalse(panel.refresh_reference())
                self.assertIsNone(panel.result)
                self.assertEqual(panel.title.text(), '')
                self.assertEqual(panel.text.toPlainText(), '')
                self.assertEqual(panel.details.toPlainText(), '')
