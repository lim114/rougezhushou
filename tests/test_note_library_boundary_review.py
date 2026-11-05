"""File scan errors stay distinct from failures while updating the interface."""
import unittest
from tempfile import TemporaryDirectory
from unittest.mock import patch
from PySide6.QtWidgets import QApplication
from rouge.player_note_library import NoteLibraryPanel


class NoteLibraryBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qt = QApplication.instance() or QApplication([])

    def test_notice_failure_is_not_relabelled_as_a_scan_failure(self):
        with TemporaryDirectory() as folder:
            panel = NoteLibraryPanel(folder, defer_population=True)
            self.addCleanup(panel.close)
            with patch.object(panel.library, 'rows', return_value=[]):
                with patch.object(panel.notice, 'setText', side_effect=[ValueError('internal display failure'), None]):
                    with self.assertRaisesRegex(ValueError, 'internal display failure'):
                        panel.refresh()

    def test_query_widget_failure_does_not_enter_file_scan(self):
        with TemporaryDirectory() as folder:
            panel = NoteLibraryPanel(folder, defer_population=True)
            self.addCleanup(panel.close)
            with patch.object(panel.library, 'rows') as scan:
                with patch.object(panel.search, 'text', side_effect=ValueError('internal query failure')):
                    with self.assertRaisesRegex(ValueError, 'internal query failure'):
                        panel.refresh()
                scan.assert_not_called()


if __name__ == '__main__':
    unittest.main()
