import unittest
from unittest.mock import patch

from PySide6.QtCore import QByteArray, QBuffer, QIODevice
from PySide6.QtGui import QImage
from PySide6.QtWidgets import QApplication

from rouge import battle_enemy_readers as shared
from rouge import current_hanko, current_elbert_reference, current_sun_boss, current_boss_documents
from rouge.current_hanko_view import CurrentHankoPanel
from rouge.current_elbert_view import CurrentElbertPanel
from rouge.current_sun_boss_view import CurrentSunBossPanel
from rouge.current_boss_documents_view import CurrentBossDocumentsPanel


class EnemyPortraitRefreshTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qt = QApplication.instance() or QApplication([])
        data = QByteArray()
        buffer = QBuffer(data)
        buffer.open(QIODevice.OpenModeFlag.WriteOnly)
        picture = QImage(5, 7, QImage.Format.Format_RGB32)
        picture.fill(0xff123456)
        assert picture.save(buffer, 'PNG')
        cls.png = bytes(data)

    def test_refresh_decodes_one_portrait_per_entry_and_later_selection_reads_again(self):
        for panel_type, provider, stage, rows_field, key_field, combo_name, handler in (
                (CurrentHankoPanel, current_hanko, 'ro6_b_1', 'rows', 'key', 'entity_combo', '_entity_changed'),
                (CurrentElbertPanel, current_elbert_reference, 'ro6_b_3', 'entities', 'key', 'entity_combo', '_entity_changed'),
                (CurrentSunBossPanel, current_sun_boss, 'ro6_b_7', 'rows', 'key', 'form_combo', '_form_changed'),
                (CurrentBossDocumentsPanel, current_boss_documents, 'ro6_b_6', 'rows', 'enemy_key', 'enemy_combo', '_enemy_changed')):
            with self.subTest(stage=stage):
                rows = provider.reference(stage)[rows_field]
                key = rows[0][key_field]
                with patch.object(shared.battle, 'picture_bytes', return_value=self.png) as read:
                    panel = panel_type(stage, key)
                    try:
                        combo = getattr(panel, combo_name)
                        self.assertEqual(combo.currentData(), key)
                        self.assertEqual(read.call_count, len(rows))
                        for raw in (None, b'invalid PNG', self.png):
                            read.reset_mock()
                            read.return_value = raw
                            self.assertTrue(panel.refresh_reference())
                            self.assertEqual(read.call_count, len(rows))
                            self.assertEqual(combo.currentData(), key)
                            missing = raw != self.png
                            self.assertEqual(combo.itemIcon(combo.currentIndex()).isNull(), missing)
                            self.assertEqual(panel.portrait.pixmap().isNull(), missing)
                            self.assertEqual(bool(panel.portrait.text()), missing)
                            if not missing:
                                edge = 74 if panel_type is CurrentHankoPanel else 70
                                self.assertEqual(panel.portrait.pixmap().height(), edge)
                        read.reset_mock()
                        read.return_value = None
                        getattr(panel, handler)()
                        self.assertEqual(read.call_count, 1)
                        self.assertTrue(panel.portrait.pixmap().isNull())
                    finally:
                        panel.close()
                        panel.deleteLater()
