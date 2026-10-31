from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication
from rouge import current_action_positions as model
from rouge.current_action_positions_view import CurrentActionPositionsPanel
from rouge.current_battle_view import CurrentBattleDialog
from tests import test_current_map_position_319 as source_tests


class CurrentActionPositionsView320Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.qt = QApplication.instance() or QApplication([])

    def panel(self, sid='ro6_n_2_3', key='1'):
        p = CurrentActionPositionsPanel(sid, key); p.resize(950, 500); p.show(); self.addCleanup(p.close); self.qt.processEvents(); return p

    def test_exact_action_choice_marks_same_grid_and_verified_original_center(self):
        p = self.panel(); self.assertIsNone(p.grid.selected); self.assertIsNone(p.original.point_center())
        p.combo.setCurrentIndex(1); self.assertEqual(p.entry_key, '0'); self.assertEqual(p.grid.selected, (6, 2)); self.assertIsNotNone(p.original.point_center()); self.assertIn('预置装置', p.player.toPlainText())
        selected = p.grid.selected; QTest.mouseClick(p.grid, Qt.MouseButton.LeftButton, pos=p.grid.center(0, 0).toPoint()); self.assertEqual(p.grid.selected, selected)
        QTest.mouseClick(p.original, Qt.MouseButton.LeftButton, pos=p.original.image_rect().center().toPoint()); self.assertEqual(p.grid.selected, selected)

    def test_unmapped_base_cells_still_select_grid_without_guessed_original(self):
        p = self.panel('ro6_n_1_1', '10'); p.combo.setCurrentIndex(1)
        self.assertIsNotNone(p.grid.selected); self.assertIsNone(p.original.point_center()); self.assertFalse(p.original.pixmap.isNull()); self.assertIn('不猜位置', p.player.toPlainText())
        p.combo.setCurrentIndex(0); self.assertIsNone(p.grid.selected); self.assertIsNone(p.original.point_center())

    def test_branch_and_unbound_activation_keep_map_but_no_false_markers(self):
        for key in ('38', '0'):
            p = self.panel('ro6_n_1_1', key); self.assertEqual(p.combo.count(), 1); self.assertFalse(p.combo.isEnabled()); self.assertIsNone(p.grid.selected); self.assertIsNone(p.original.point_center()); self.assertFalse(p.original.pixmap.isNull()); self.assertIn('尚无能够绑定', p.player.toPlainText())

    def test_refresh_keeps_real_choice_tab_and_both_nonzero_readers(self):
        p = self.panel(); p.resize(850, 410); p.combo.setCurrentIndex(1)
        for reader in (p.player, p.technical):
            p.tabs.setCurrentWidget(reader); self.qt.processEvents(); cursor = reader.textCursor(); cursor.setPosition(2); cursor.setPosition(10, QTextCursor.MoveMode.KeepAnchor); reader.setTextCursor(cursor)
            bar = reader.verticalScrollBar(); self.assertGreater(bar.maximum(), 0); bar.setValue(min(3, bar.maximum())); before = (cursor.anchor(), cursor.position(), bar.value(), p.tabs.currentIndex(), p.combo.currentIndex(), p.grid.selected)
            self.assertTrue(p.refresh_reference()); self.qt.processEvents(); cursor = reader.textCursor(); self.assertEqual(before, (cursor.anchor(), cursor.position(), bar.value(), p.tabs.currentIndex(), p.combo.currentIndex(), p.grid.selected))

    def test_actual_map_source_damage_clears_everything_and_recovery_requires_choice(self):
        p = self.panel(); p.combo.setCurrentIndex(1)
        with TemporaryDirectory() as folder:
            root = Path(folder); source_tests.CurrentMapPosition319Tests().clone(root); file = root / model.positions.DATA; raw = file.read_bytes()
            with patch.object(model.positions, 'ROOT', root):
                file.write_bytes(raw + b' '); self.assertFalse(p.refresh_reference()); self.assertIsNone(p.result); self.assertIsNone(p.grid.result); self.assertTrue(p.original.pixmap.isNull()); self.assertEqual(p.technical.toPlainText(), '')
                file.write_bytes(raw); self.assertTrue(p.refresh_reference()); self.assertEqual(p.combo.currentIndex(), 0); self.assertIsNone(p.original.point_center()); self.assertIsNone(p.grid.selected)

    def test_parent_actual_button_refresh_selection_change_and_owned_close(self):
        d = CurrentBattleDialog('ro6_n_2_3'); d.show(); self.addCleanup(d.close); p = d.panel; p.tabs.setCurrentIndex(2)
        row = next(i for i in range(p.actions.count()) if p.actions.item(i).data(Qt.ItemDataRole.UserRole) == '1'); p.actions.setCurrentRow(row)
        self.assertTrue(p.action_position_button.isEnabled()); QTest.mouseClick(p.action_position_button, Qt.MouseButton.LeftButton); child = p.action_position_dialog; self.assertTrue(child.isVisible()); child.panel.combo.setCurrentIndex(1)
        self.assertTrue(p.refresh_reference()); self.assertTrue(child.isVisible()); self.assertEqual(child.panel.combo.currentIndex(), 1)
        p.actions.setCurrentRow(row + 1); self.assertFalse(child.isVisible()); p.actions.setCurrentRow(row); self.assertTrue(p.open_action_positions()); child = p.action_position_dialog
        self.assertTrue(p.open_action_positions()); self.assertIs(p.action_position_dialog,child); self.assertTrue(child.isVisible()); d.close(); self.assertFalse(child.isVisible())

    def test_parent_failure_and_bad_image_decode_cannot_keep_previous_markers(self):
        d = CurrentBattleDialog('ro6_n_2_3'); d.show(); self.addCleanup(d.close); p = d.panel
        self.assertFalse(p.open_action_positions()); p.actions.setCurrentRow(1); self.assertTrue(p.open_action_positions()); child = p.action_position_dialog
        with patch.object(model.battle, 'stage_reference', return_value=None): self.assertFalse(p.refresh_reference()); self.assertFalse(p.action_position_button.isEnabled()); self.assertFalse(child.isVisible())
        p = self.panel(); p.combo.setCurrentIndex(1)
        with patch.object(model.positions.battle.version, 'image_bytes', return_value=b'not PNG'): self.assertFalse(p.refresh_reference()); self.assertIsNone(p.result); self.assertTrue(p.original.pixmap.isNull())


if __name__ == '__main__': unittest.main()
