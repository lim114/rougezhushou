import unittest
from unittest.mock import patch
from PySide6.QtWidgets import QApplication, QWidget
from rouge.player_reference_window import ReferenceWindow, ToolPage
from rouge import current_sun_boss_view as sun, current_boss_documents_view as boss
from rouge import current_map_position as maps


class DocumentSharedMapPreflightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.qt = QApplication.instance() or QApplication([])

    def test_shared_entry_checks_document_map_once(self):
        for view, cls, stage in ((sun, sun.CurrentSunBossPanel, 'ro6_b_7'), (boss, boss.CurrentBossDocumentsPanel, 'ro6_b_5')):
            with self.subTest(stage=stage):
                owner = QWidget(); host = ReferenceWindow(owner)
                owner.reference_window = host; owner.present = host.present
                panel = cls(stage, '0'); source = ToolPage('source', panel, owner)
                self.addCleanup(owner.close); self.addCleanup(host.close)
                self.assertTrue(host.present(source))
                with patch.object(view.model, 'map_reference', wraps=view.model.map_reference) as read, patch.object(maps, 'stage_reference', wraps=maps.stage_reference) as map_read:
                    self.assertTrue(panel.open_map())
                    read.assert_called_once_with(panel.result)
                    map_read.assert_called_once_with(stage)
                self.assertEqual(host.pages.currentWidget().panel.result['stage_id'], stage)
                host.present(source)
                with patch.object(view.model, 'map_reference', return_value=None) as read:
                    self.assertFalse(panel.open_map())
                    read.assert_called_once_with(panel.result)
                self.assertIs(host.pages.currentWidget(), source)
                self.assertFalse(host.linked_pages)
                host.close(); owner.close()
