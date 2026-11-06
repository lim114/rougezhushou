import unittest
from unittest.mock import patch
from PySide6.QtWidgets import QApplication
from rouge import current_elbert_view as view


class ElbertSelectionReuseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qt = QApplication.instance() or QApplication([])

    def test_entity_and_later_topic_each_resolve_once(self):
        panel = view.CurrentElbertPanel('ro6_b_3')
        self.addCleanup(panel.close)
        with patch.object(view.model, 'entity', wraps=view.model.entity) as resolve:
            panel.entity_combo.setCurrentIndex(1)
            resolve.assert_called_once()
        self.assertEqual(panel.result['selected']['key'], panel.selected_key)
        self.assertIsNotNone(panel.result['selected'])
        with patch.object(view.model, 'entity', wraps=view.model.entity) as resolve:
            panel.topic.setCurrentIndex(1)
            resolve.assert_called_once()
        self.assertEqual(panel.result['card'], panel.topic.currentData())
        with patch.object(view.model, 'entity', wraps=view.model.entity) as resolve:
            panel.entity_combo.setCurrentIndex(0)
            resolve.assert_called_once()
        self.assertIsNone(panel.result['selected'])
