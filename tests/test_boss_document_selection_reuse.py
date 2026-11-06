import unittest
from unittest.mock import patch
from PySide6.QtWidgets import QApplication
from rouge import current_boss_documents_view as view


class BossSelectionReuseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qt = QApplication.instance() or QApplication([])

    def test_same_snapshot_selection_reuses_row_but_renderer_revalidates(self):
        panel = view.CurrentBossDocumentsPanel('ro6_b_5')
        self.addCleanup(panel.close)
        with patch.object(view.model, 'entity', wraps=view.model.entity) as lookup:
            panel.enemies.select_value('0')
            self.assertEqual(lookup.call_count, 2)
        self.assertEqual(panel.selected_key, '0')
        self.assertTrue(panel.topic.count() > 1)
        with patch.object(view.model, 'entity', wraps=view.model.entity) as lookup:
            panel.topic.setCurrentIndex(1)
            self.assertEqual(lookup.call_count, 2)
        self.assertIn(panel.result['rows'][0]['enemy']['name'], panel.player.toPlainText())

    def test_independent_queries_still_resolve(self):
        result = view.model.reference('ro6_b_5')
        for query in (view.model.topics, view.model.related_entities):
            with patch.object(view.model, 'entity', wraps=view.model.entity) as lookup:
                query(result, '0')
                lookup.assert_called_once()
