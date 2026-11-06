import unittest
from PySide6.QtWidgets import QApplication
from rouge.player_resource_history import ResourceHistoryPage
from tests.test_player_resource_history_404 import reads


class ResourceHistoryStateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_same_run_keeps_selection_new_run_clears_it(self):
        page = ResourceHistoryPage();self.addCleanup(page.close)
        self.assertIsNone(page.run_id)
        first = {'id': 'first', **reads([('gold', 2), ('gold', 4)])}
        page.refresh(first);page.entries.setCurrentRow(1)
        changed = {'id': 'first', **reads([('gold', 2), ('gold', 4), ('gold', 5)])}
        page.refresh(changed)
        self.assertEqual(page.entries.currentRow(), 1)
        page.refresh({'id': 'second', **reads([('gold', 7), ('gold', 9)])})
        self.assertEqual(page.run_id, 'second')
        self.assertEqual(page.entries.currentRow(), -1)
        self.assertIn('选择一条', page.detail.toPlainText())

    def test_initial_empty_state_then_first_run(self):
        page = ResourceHistoryPage();self.addCleanup(page.close)
        page.refresh({})
        self.assertIsNone(page.run_id)
        self.assertEqual(page.entries.count(), 0)
        page.refresh({'id': 'first', **reads([('gold', 0)])})
        self.assertEqual(page.entries.count(), 1)
        self.assertEqual(page.rows[0]['value'], 0)
