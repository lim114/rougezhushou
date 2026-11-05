"""Material-to-stage navigation crosses one host-validation entry."""
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch
from PySide6.QtWidgets import QApplication, QWidget
from rouge import player_reference_links as links
from rouge.player_reference_window import ReferenceWindow


class ReferenceHostEntryReview(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qt = QApplication.instance() or QApplication([])

    def test_material_stage_reads_host_once_before_reusing_ancestor(self):
        owner = QWidget()
        host = ReferenceWindow(owner)
        self.addCleanup(owner.close)
        self.addCleanup(host.close)
        panel = SimpleNamespace(window=Mock(return_value=host))
        with patch.object(links, '_return_to_ancestor', return_value=True):
            self.assertTrue(links.open_material_source(panel, {'kind': 'battle', 'stage_id': 'ro6_t_12'}))
        self.assertEqual(panel.window.call_count, 1)

    def test_standalone_material_stage_keeps_existing_dialog_dispatch(self):
        owner = QWidget()
        self.addCleanup(owner.close)
        panel = SimpleNamespace(window=Mock(return_value=owner))
        self.assertIsNone(links.open_material_source(panel, {'kind': 'battle', 'stage_id': 'ro6_t_12'}))
        self.assertEqual(panel.window.call_count, 1)


if __name__ == '__main__':
    unittest.main()
