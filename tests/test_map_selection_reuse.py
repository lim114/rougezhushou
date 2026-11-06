import unittest
from unittest.mock import patch
from PySide6.QtWidgets import QApplication
from rouge import current_map_position_view as view


class MapSelectionReuseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qt = QApplication.instance() or QApplication([])

    def test_selection_resolves_cell_once_and_preserves_display(self):
        panel = view.CurrentMapPositionPanel('ro6_n_6_2')
        self.addCleanup(panel.close)
        point = panel.result['points'][0]
        with patch.object(view.model, 'cell_reference', wraps=view.model.cell_reference) as resolve:
            self.assertTrue(panel.select_cell(point['row'], point['col']))
            resolve.assert_called_once_with(panel.result, point['row'], point['col'])
        self.assertEqual(panel.selected, (point['row'], point['col']))
        self.assertIn('第'+str(point['row']+1)+'行', panel.player.toPlainText())
        with patch.object(view.model, 'cell_reference', wraps=view.model.cell_reference) as resolve:
            self.assertFalse(panel.select_cell(-1, -1))
            resolve.assert_called_once()
        self.assertEqual(panel.selected, (point['row'], point['col']))
        panel.clear_reference()
        self.assertFalse(panel.select_cell(0, 0))
