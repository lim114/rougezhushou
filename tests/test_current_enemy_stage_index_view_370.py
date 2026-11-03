import unittest
from copy import deepcopy
from unittest.mock import patch
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication
from rouge import current_enemy_stage_index as model
from rouge.current_enemy_stage_index_view import CurrentEnemyStageIndexPanel, CurrentEnemyStageIndexDialog


class CurrentEnemyStageIndexView370Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.app = QApplication.instance() or QApplication([])

    def panel(self):
        widget = CurrentEnemyStageIndexPanel(); widget.resize(1080, 570); widget.show()
        self.addCleanup(widget.close); self.app.processEvents(); return widget

    def test_chinese_search_category_branches_unknown_and_flag_filter(self):
        p = self.panel(); self.assertEqual(p.entries.count(), 2060); self.assertIsNone(p.result)
        p.search.setText('空植体'); p.tier.setCurrentIndex(p.tier.findData('UNKNOWN'))
        self.assertEqual(p.entries.count(), 8)
        p.search.clear(); p.tier.setCurrentIndex(p.tier.findData(None))
        p.scope.setCurrentIndex(p.scope.findData('not_counted'))
        self.assertEqual(p.entries.count(), 10)
        p.entries.setCurrentRow(0); self.assertIn('不计入总敌人数', p.player.toPlainText())
        self.assertIn('不是实际出场数量', p.count.text())

    def test_exact_selection_opens_actual_child_on_same_stage_and_reference(self):
        p = self.panel(); self.assertTrue(p.select_target('ro6_t_6', '0'))
        self.assertTrue(p.open_battle()); self.app.processEvents()
        child = p.battle_dialog; self.assertTrue(child.isVisible())
        self.assertEqual(child.panel.stage_id, 'ro6_t_6'); self.assertEqual(child.panel.enemy_combo.currentData(), '0')
        self.assertEqual(child.panel.tabs.currentIndex(), 1)
        self.assertIn('坎诺特', child.panel.enemy_player.toPlainText())
        self.assertTrue(child.panel.map_image.pixmap() and not child.panel.map_image.pixmap().isNull())
        self.assertTrue(p.open_battle()); self.app.processEvents()
        self.assertFalse(child.isVisible()); self.assertIsNot(p.battle_dialog, child)

    def test_nonzero_reading_and_child_selection_survive_real_source_refresh(self):
        p = self.panel(); self.assertTrue(p.select_target('ro6_t_6', '0')); self.assertTrue(p.open_battle())
        self.app.processEvents(); child = p.battle_dialog
        p.tabs.setCurrentIndex(1); cursor = p.technical.textCursor(); cursor.setPosition(4)
        cursor.setPosition(15, QTextCursor.MoveMode.KeepAnchor); p.technical.setTextCursor(cursor)
        self.assertGreater(p.technical.verticalScrollBar().maximum(), 0); p.technical.verticalScrollBar().setValue(3)
        expected = (p.selected_key, p.search.text(), p.tabs.currentIndex(), p.technical.textCursor().selectedText(), p.technical.verticalScrollBar().value())
        self.assertTrue(p.refresh_reference()); self.app.processEvents()
        self.assertEqual(expected, (p.selected_key, p.search.text(), p.tabs.currentIndex(), p.technical.textCursor().selectedText(), p.technical.verticalScrollBar().value()))
        self.assertIs(p.battle_dialog, child); self.assertTrue(child.isVisible())
        self.assertEqual(child.panel.enemy_combo.currentData(), '0'); self.assertEqual(child.panel.tabs.currentIndex(), 1)

    def test_source_loss_closes_owned_tree_and_recovery_requires_manual_selection(self):
        p = self.panel(); p.select_target('ro6_t_6', '0'); self.assertTrue(p.open_battle()); child = p.battle_dialog
        with patch.object(model, 'packet', return_value=None):
            self.assertFalse(p.refresh_reference()); self.app.processEvents()
            self.assertFalse(child.isVisible()); self.assertIsNone(p.result); self.assertEqual(p.entries.count(), 0)
            self.assertFalse(p.open_button.isEnabled()); self.assertEqual(p.technical.toPlainText(), '')
        self.assertTrue(p.refresh_reference()); self.assertIsNone(p.result); self.assertIsNone(p.entries.currentItem())
        self.assertTrue(p.select_target('ro6_t_6', '0'))

    def test_filter_selection_change_and_parent_close_close_children(self):
        p = self.panel(); p.select_target('ro6_t_6', '0'); self.assertTrue(p.open_battle()); child = p.battle_dialog
        p.search.setText('不存在的名称'); self.app.processEvents()
        self.assertFalse(child.isVisible()); self.assertIsNone(p.result); self.assertFalse(p.open_button.isEnabled())
        dialog = CurrentEnemyStageIndexDialog(stage_id='ro6_t_6', enemy_key='0'); self.addCleanup(dialog.close)
        dialog.show(); self.assertTrue(dialog.panel.open_battle()); child = dialog.panel.battle_dialog
        dialog.close(); self.app.processEvents(); self.assertFalse(child.isVisible())

    def test_forged_selection_never_opens_a_different_stage(self):
        p = self.panel(); p.select_target('ro6_t_6', '0')
        p.result['row']['stage_id'] = 'ro6_t_7'
        self.assertFalse(p.open_battle()); self.assertIsNone(p.battle_dialog); self.assertIsNone(p.result)
        self.assertFalse(p.select_target('ro6_t_6', 0)); self.assertFalse(p.select_target('no-stage', '0'))

    def test_overview_and_partial_constructor_keep_reference_distinct_from_selected_result(self):
        overview = CurrentEnemyStageIndexDialog(); self.addCleanup(overview.close)
        self.assertIsNotNone(overview.panel.reference); self.assertIsNone(overview.panel.result)
        self.assertIsNone(overview.panel.selected_key); self.assertFalse(overview.panel.open_button.isEnabled())
        partial = CurrentEnemyStageIndexDialog(stage_id='ro6_t_6'); self.addCleanup(partial.close)
        self.assertIsNotNone(partial.panel.reference); self.assertIsNone(partial.panel.result)
        self.assertIsNone(partial.panel.selected_key); self.assertIn('指定', partial.panel.player.toPlainText())

    def test_invalid_target_selection_clears_previous_battle_and_owned_map(self):
        p = self.panel(); self.assertTrue(p.select_target('ro6_t_6', '0')); self.assertTrue(p.open_battle())
        child = p.battle_dialog; self.assertTrue(child.panel.open_map_positions()); mapped = child.panel.position_dialog
        self.assertFalse(p.select_target('no-stage', '0')); self.app.processEvents()
        self.assertIsNotNone(p.reference); self.assertIsNone(p.result); self.assertIsNone(p.selected_key)
        self.assertIsNone(p.entries.currentItem()); self.assertFalse(p.open_button.isEnabled())
        self.assertIsNone(p.battle_dialog); self.assertFalse(child.isVisible()); self.assertIsNone(child.panel.result)
        self.assertFalse(mapped.isVisible()); self.assertIsNone(mapped.panel.result)
        self.assertIsNone(mapped.panel.image_raw); self.assertTrue(mapped.panel.original.pixmap.isNull())

    def test_swapping_valid_detail_without_selected_pair_cannot_open_another_target(self):
        p = self.panel(); self.assertTrue(p.select_target('ro6_t_6', '0'))
        other = next(row for row in p.reference['data']['rows'] if row['stage_id'] != 'ro6_t_6')
        p.result = model.detail(other['stage_id'], other['enemy_key'], reference=p.reference)
        self.assertIsNotNone(model.exact_target(p.result))
        self.assertFalse(p.open_battle()); self.assertIsNone(p.result); self.assertIsNone(p.battle_dialog)

    def test_malformed_selection_pair_clears_previous_detail_instead_of_unpacking_it(self):
        p = self.panel(); self.assertTrue(p.select_target('ro6_t_6', '0'))
        item = p.entries.currentItem(); item.setData(Qt.ItemDataRole.UserRole, 'not-an-exact-pair')
        p._selected(item)
        self.assertIsNone(p.result); self.assertIsNone(p.selected_key); self.assertIsNone(p.entries.currentItem())
        self.assertFalse(p.open_button.isEnabled())

    def test_dialog_close_or_rejection_clears_directory_battle_and_map_contents(self):
        for method in ('close', 'reject'):
            dialog = CurrentEnemyStageIndexDialog(stage_id='ro6_t_6', enemy_key='0'); self.addCleanup(dialog.close)
            dialog.show(); self.assertTrue(dialog.panel.open_battle()); child = dialog.panel.battle_dialog
            self.assertTrue(child.panel.open_map_positions()); mapped = child.panel.position_dialog
            getattr(dialog, method)(); self.app.processEvents()
            self.assertFalse(dialog.isVisible()); self.assertIsNone(dialog.panel.reference); self.assertIsNone(dialog.panel.result)
            self.assertIsNone(dialog.panel.selected_key); self.assertEqual(dialog.panel.entries.count(), 0)
            self.assertEqual(dialog.panel.technical.toPlainText(), ''); self.assertIsNone(dialog.panel.battle_dialog)
            self.assertFalse(child.isVisible()); self.assertIsNone(child.panel.result)
            self.assertFalse(mapped.isVisible()); self.assertIsNone(mapped.panel.result)
            self.assertIsNone(mapped.panel.image_raw); self.assertTrue(mapped.panel.original.pixmap.isNull())

    def test_direct_battle_close_or_rejection_clears_child_tree_but_keeps_directory_selection(self):
        p = self.panel(); self.assertTrue(p.select_target('ro6_t_6', '0'))
        for method in ('close', 'reject'):
            self.assertTrue(p.open_battle()); child = p.battle_dialog
            self.assertTrue(child.panel.open_map_positions()); mapped = child.panel.position_dialog
            getattr(child, method)(); self.app.processEvents()
            self.assertIsNone(p.battle_dialog); self.assertFalse(child.isVisible()); self.assertIsNone(child.panel.result)
            self.assertFalse(mapped.isVisible()); self.assertIsNone(mapped.panel.result)
            self.assertIsNotNone(p.reference); self.assertIsNotNone(p.result); self.assertEqual(p.selected_key, ('ro6_t_6', '0'))

    def test_foreign_child_after_refresh_is_cleared_without_losing_valid_directory(self):
        p = self.panel(); self.assertTrue(p.select_target('ro6_t_6', '0')); self.assertTrue(p.open_battle())
        child = p.battle_dialog; child.panel.result = deepcopy(child.panel.result)
        child.panel.result['level_key'] = 'foreign-level'
        with patch.object(child.panel, 'refresh_reference', return_value=True):
            self.assertTrue(p.refresh_reference())
        self.assertIsNotNone(p.reference); self.assertIsNotNone(p.result); self.assertTrue(p.open_button.isEnabled())
        self.assertIsNone(p.battle_dialog); self.assertFalse(child.isVisible()); self.assertIsNone(child.panel.result)


if __name__ == '__main__': unittest.main()
