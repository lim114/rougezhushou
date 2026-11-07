import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import unittest
from unittest.mock import patch
from PySide6.QtWidgets import QApplication
from rouge import current_boss_documents as model
from rouge.current_boss_documents_view import CurrentBossDocumentsPanel


class BossRefreshSnapshotReview(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_refresh_reuses_verified_reference_but_later_render_rechecks(self):
        with patch.object(model, 'reference', wraps=model.reference) as read:
            panel = CurrentBossDocumentsPanel('ro6_b_6', '0')
            self.addCleanup(panel.close)
            self.assertEqual(read.call_count, 1)
            before = panel.player.toPlainText()
            read.reset_mock()
            self.assertTrue(panel.refresh_reference())
            self.assertEqual(read.call_count, 1)
            self.assertEqual(panel.player.toPlainText(), before)
        with patch.object(model, 'reference', return_value=None) as read:
            panel._render()
            read.assert_called_once()
            self.assertEqual(panel.player.toPlainText(), model.UNAVAILABLE)

    def test_document_family_dispatch_is_exact_and_unknown_is_error(self):
        from rouge import boss_phase_reference, boss_cycle_reference, boss_hunt_reference, gold_boss_reference
        for family, reader, renderer in (
            ('phase', boss_phase_reference.phase_reference, boss_phase_reference.reference_text),
            ('cycle', boss_cycle_reference.cycle_reference, boss_cycle_reference.reference_text),
            ('hunt', boss_hunt_reference.hunt_reference, boss_hunt_reference.reference_text),
            ('gold', gold_boss_reference.gold_reference, gold_boss_reference.reference_text),
        ):
            self.assertEqual(model._legacy(family), (reader, renderer))
        with self.assertRaisesRegex(ValueError, 'Unsupported documentary family'):
            model._legacy('invented')
