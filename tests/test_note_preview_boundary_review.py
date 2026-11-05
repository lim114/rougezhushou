"""Preview cache completion and Qt resource/anchor entry points."""
import unittest
from unittest.mock import patch
from PySide6.QtCore import QByteArray, QUrl
from PySide6.QtGui import QTextDocument
from PySide6.QtWidgets import QApplication
from rouge import player_note_preview as module


class NotePreviewBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qt = QApplication.instance() or QApplication([])

    def test_failed_render_is_not_cached_as_a_completed_update(self):
        for boundary in ('render', 'setHtml', 'reading_state'):
            with self.subTest(boundary=boundary):
                view = module.NotePreview()
                self.addCleanup(view.close)
                view.read_markdown('原文字')
                owner, name = {
                    'render': (module, 'render_note'),
                    'setHtml': (view, 'setHtml'),
                    'reading_state': (module, '_restore_reading'),
                }[boundary]
                with patch.object(owner, name, side_effect=ValueError('isolated failure')):
                    with self.assertRaisesRegex(ValueError, 'isolated failure'):
                        view.read_markdown('新文字')
                with patch.object(module, 'render_note', wraps=module.render_note) as render:
                    view.read_markdown('新文字')
                    render.assert_called_once_with('新文字')
                self.assertIn('新文字', view.toPlainText())
                with patch.object(module, 'render_note', wraps=module.render_note) as render:
                    view.read_markdown('新文字')
                    render.assert_not_called()

    def test_page_anchor_scrolls_without_blocked_link_notice(self):
        view = module.NotePreview()
        self.addCleanup(view.close)
        blocked = []
        view.linkBlocked.connect(lambda: blocked.append(True))
        with patch.object(view, 'scrollToAnchor') as scroll:
            view.anchorClicked.emit(QUrl('#details'))
            scroll.assert_called_once_with('details')
        self.assertEqual(blocked, [])

    def test_custom_protocol_resource_is_not_requested(self):
        view = module.NotePreview()
        self.addCleanup(view.close)
        url = QUrl('custom-app:style.css')
        resource = view.loadResource(QTextDocument.ResourceType.StyleSheetResource, url)
        self.assertIsInstance(resource, QByteArray)
        self.assertTrue(resource.isEmpty())
        self.assertEqual(view._pending,set())

    def test_render_does_not_open_browser_and_non_web_click_stays_manual(self):
        view = module.NotePreview()
        self.addCleanup(view.close)
        blocked = []
        view.linkBlocked.connect(lambda: blocked.append(True))
        with patch.object(module.QDesktopServices, 'openUrl', return_value=True) as opened:
            view.read_markdown('[网页](https://example.invalid/notes)')
            opened.assert_not_called()
            for url in ('file:///C:/not-opened.txt', 'mailto:nobody@example.invalid'):
                view.anchorClicked.emit(QUrl(url))
            opened.assert_not_called()
        self.assertEqual(blocked, [True, True])


if __name__ == '__main__':
    unittest.main()
