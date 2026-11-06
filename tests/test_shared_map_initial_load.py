import unittest
from unittest.mock import patch
from PySide6.QtWidgets import QApplication, QWidget
from rouge.player_reference_window import ReferenceWindow, ToolPage
from rouge.player_reference_links import open_fixed_map
from rouge import current_map_position_view as maps


class SharedMapInitialLoadTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.qt = QApplication.instance() or QApplication([])

    def setUp(self):
        self.owner = QWidget()
        self.host = ReferenceWindow(self.owner)
        self.owner.reference_window = self.host
        self.owner.present = self.host.present
        self.content = QWidget()
        self.source = ToolPage('source', self.content, self.owner)
        self.host.present(self.source)
        self.addCleanup(self.owner.close)
        self.addCleanup(self.host.close)

    def open(self):
        return open_fixed_map(self.content, 'ro6_b_7', context=lambda: ('stable',),
            verify=lambda reader: reader.result['stage_id'] == 'ro6_b_7')

    def test_first_open_and_later_reopen_each_load_once(self):
        for _ in range(2):
            with patch.object(maps.model, 'stage_reference', wraps=maps.model.stage_reference) as read:
                self.assertTrue(self.open())
                read.assert_called_once_with('ro6_b_7')
            self.assertIsNotNone(self.host.pages.currentWidget().panel.result)
            self.host.present(self.source)

    def test_failed_load_does_not_show_empty_page(self):
        with patch.object(maps.model, 'stage_reference', return_value=None) as read:
            self.assertFalse(self.open())
            read.assert_called_once()
        self.assertIs(self.host.pages.currentWidget(), self.source)
        self.assertFalse(self.host.linked_pages)

    def test_source_rejection_precedes_loading(self):
        self.source.prepare = lambda: False
        with patch.object(maps.model, 'stage_reference') as read:
            self.assertFalse(self.open())
            read.assert_not_called()
        self.assertFalse(self.host.linked_pages)
