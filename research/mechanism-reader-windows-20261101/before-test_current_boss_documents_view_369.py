"""UI state/lifecycle candidates. Parent runs actual native validation later."""
import os
from copy import deepcopy
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
from unittest.mock import patch
import unittest
from PySide6.QtWidgets import QApplication
from rouge import current_boss_documents as model
from rouge.current_boss_documents_view import CurrentBossDocumentsPanel, CurrentBossDocumentsDialog


class CurrentBossDocumentsView369Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def tearDown(self):
        if hasattr(self, 'panel'): self.panel.close(); self.panel.deleteLater()
        self.app.processEvents()

    def test_same_source_refresh_keeps_enemy_branch_topic_tab_and_two_reading_positions(self):
        self.panel = CurrentBossDocumentsPanel('ro6_b_6', '0'); self.panel.resize(1000, 800); self.panel.show()
        self.app.processEvents()
        self.panel.enemies.select_branch(model.LABELS['phase'])
        self.panel.topic.setCurrentIndex(1); self.app.processEvents()
        positions = []
        for area in (self.panel.player, self.panel.technical):
            scroll = area.verticalScrollBar(); self.assertGreater(scroll.maximum(), 0)
            scroll.setValue(max(1, scroll.maximum() // 2)); positions.append(scroll.value())
        self.panel.tabs.setCurrentIndex(1)
        expected = (self.panel.enemy_combo.currentData(), self.panel.enemies.branch.currentData(), self.panel.topic.currentData())
        self.assertTrue(self.panel.refresh_reference()); self.app.processEvents()
        self.assertEqual((self.panel.enemy_combo.currentData(), self.panel.enemies.branch.currentData(), self.panel.topic.currentData()), expected)
        self.assertEqual(self.panel.tabs.currentIndex(), 1)
        self.assertEqual([a.verticalScrollBar().value() for a in (self.panel.player, self.panel.technical)], positions)

    def test_bad_source_clears_content_and_recovery_requires_manual_selection(self):
        self.panel = CurrentBossDocumentsPanel('ro6_b_5', '0')
        with patch.object(model, 'reference', return_value=None): self.assertFalse(self.panel.refresh_reference())
        self.assertIsNone(self.panel.result); self.assertIsNone(self.panel.selected_key)
        self.assertEqual(self.panel.player.toPlainText(), model.UNAVAILABLE)
        self.assertEqual(self.panel.technical.toPlainText(), '')
        self.assertFalse(self.panel.map_button.isEnabled()); self.assertFalse(self.panel.related_button.isEnabled())
        self.assertTrue(self.panel.refresh_reference()); self.assertIsNone(self.panel.enemy_combo.currentData())
        self.assertTrue(self.panel.enemies.select_value('1')); self.assertEqual(self.panel.selected_key, '1')

    def test_related_request_emits_exact_key_without_game_or_cross_stage_action(self):
        self.panel = CurrentBossDocumentsPanel('ro6_b_5', '0'); observed = []
        self.panel.enemy_requested.connect(observed.append)
        request = next(r for r in model.related_entities(self.panel.result, '0') if r['key'] == '1')
        self.panel.related.setCurrentIndex(self.panel.related.findData(request))
        self.assertTrue(self.panel.follow_entity()); self.assertEqual(observed, ['1'])

    def test_owned_map_child_closed_on_source_failure_or_parent_close(self):
        class ChildPanel:
            cleared = False
            def clear_reference(self): self.cleared = True
        class Child:
            closed = False
            def __init__(self): self.panel = ChildPanel()
            def close(self): self.closed = True
        self.panel = CurrentBossDocumentsPanel('ro6_b_2', '1')
        one = Child(); self.panel.map_dialog = one
        with patch.object(model, 'reference', return_value=None): self.panel.refresh_reference()
        self.assertTrue(one.closed); self.assertTrue(one.panel.cleared); self.assertIsNone(self.panel.map_dialog)
        self.panel.refresh_reference(); two = Child(); self.panel.map_dialog = two
        self.panel.close(); self.assertTrue(two.closed); self.assertTrue(two.panel.cleared); self.assertIsNone(self.panel.result)

    def test_direct_dialog_close_clears_document_and_actual_owned_map_contents(self):
        dialog = CurrentBossDocumentsDialog('ro6_b_5', '0'); dialog.show(); self.app.processEvents()
        self.assertTrue(dialog.panel.open_map()); child = dialog.panel.map_dialog
        dialog.close(); self.app.processEvents()
        self.assertFalse(dialog.isVisible()); self.assertIsNone(dialog.panel.result); self.assertIsNone(dialog.panel.selected_key)
        self.assertIsNone(dialog.panel.map_dialog); self.assertEqual(dialog.panel.technical.toPlainText(), '')
        self.assertFalse(child.isVisible()); self.assertIsNone(child.panel.result); self.assertIsNone(child.panel.image_raw)
        self.assertTrue(child.panel.original.pixmap.isNull()); self.assertEqual(dialog.panel.topic.count(), 0)

    def test_dialog_rejection_clears_document_and_actual_owned_map_without_parent_refresh(self):
        dialog = CurrentBossDocumentsDialog('ro6_b_5', '0'); dialog.show(); self.app.processEvents()
        self.assertTrue(dialog.panel.open_map()); child = dialog.panel.map_dialog
        dialog.reject(); self.app.processEvents()
        self.assertFalse(dialog.isVisible()); self.assertIsNone(dialog.panel.result); self.assertIsNone(dialog.panel.selected_key)
        self.assertIsNone(dialog.panel.map_dialog); self.assertEqual(dialog.panel.technical.toPlainText(), '')
        self.assertFalse(child.isVisible()); self.assertIsNone(child.panel.result); self.assertIsNone(child.panel.image_raw)
        self.assertTrue(child.panel.original.pixmap.isNull()); self.assertEqual(dialog.panel.related.count(), 0)

    def test_foreign_map_result_after_refresh_clears_only_map_and_retains_document(self):
        self.panel = CurrentBossDocumentsPanel('ro6_b_5', '0'); self.assertTrue(self.panel.open_map())
        child = self.panel.map_dialog; child.panel.result = deepcopy(child.panel.result)
        child.panel.result['source_identity'] = ('foreign-map-source',)
        with patch.object(child.panel, 'refresh_reference', return_value=True):
            self.assertTrue(self.panel.refresh_reference())
        self.assertIsNotNone(self.panel.result); self.assertIsNone(self.panel.map_dialog)
        self.assertFalse(child.isVisible()); self.assertIsNone(child.panel.result)
        self.assertIn('与本关不一致', self.panel.status.text())

    def test_direct_owned_map_close_or_rejection_clears_map_but_keeps_document(self):
        self.panel = CurrentBossDocumentsPanel('ro6_b_5', '0')
        for method in ('close', 'reject'):
            self.assertTrue(self.panel.open_map()); child = self.panel.map_dialog
            getattr(child, method)(); self.app.processEvents()
            self.assertIsNone(self.panel.map_dialog); self.assertFalse(child.isVisible())
            self.assertIsNone(child.panel.result); self.assertIsNone(child.panel.image_raw)
            self.assertTrue(child.panel.original.pixmap.isNull()); self.assertIsNotNone(self.panel.result)
            self.assertEqual(self.panel.selected_key, '0')


if __name__ == '__main__':
    unittest.main()
