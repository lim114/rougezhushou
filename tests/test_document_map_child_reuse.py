import unittest
from unittest.mock import patch
from PySide6.QtWidgets import QApplication
from rouge import current_map_position_view as maps
from rouge import current_sun_boss_view as sun, current_boss_documents_view as boss


class DocumentMapChildReuseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.qt = QApplication.instance() or QApplication([])

    def test_parent_refresh_reads_map_once(self):
        for cls, stage, key in ((sun.CurrentSunBossPanel, 'ro6_b_7', '0'), (boss.CurrentBossDocumentsPanel, 'ro6_b_5', '0')):
            with self.subTest(stage=stage):
                panel = cls(stage, key)
                self.addCleanup(panel.close)
                with patch.object(maps.model, 'stage_reference', wraps=maps.model.stage_reference) as read:
                    self.assertTrue(panel.open_map())
                    read.assert_called_once_with(stage)
                with patch.object(maps.model, 'stage_reference', wraps=maps.model.stage_reference) as read:
                    self.assertTrue(panel.refresh_reference())
                    read.assert_called_once_with(stage)
                self.assertIsNotNone(panel.map_dialog)
                self.assertEqual(panel.map_dialog.panel.result['stage_id'], stage)
                panel.close()

    def test_independent_map_refresh_still_reads(self):
        panel = maps.CurrentMapPositionPanel('ro6_b_7')
        self.addCleanup(panel.close)
        with patch.object(maps.model, 'stage_reference', wraps=maps.model.stage_reference) as read:
            self.assertTrue(panel.refresh_reference())
            read.assert_called_once_with('ro6_b_7')
