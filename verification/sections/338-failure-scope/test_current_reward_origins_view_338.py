from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication
from rouge import current_reward_origins as model
from rouge.current_reward_origins_view import CurrentRewardOriginsDialog
from rouge.expansion_view import ExpansionUpdatePanel
from tests.test_current_reward_origins_338 import ITEMS, clone

class CurrentRewardOriginsView338Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.qt = QApplication.instance() or QApplication([])
    def dialog(self, index=0):
        d = CurrentRewardOriginsDialog(*ITEMS[index][:2]); d.show(); self.qt.processEvents(); self.addCleanup(d.close); return d
    def version_panel(self, index=0):
        p = ExpansionUpdatePanel(); p.show(); self.addCleanup(p.close); category, key, _ = ITEMS[index]
        p.scope.setCurrentIndex(p.scope.findData(False)); p.category.setCurrentIndex(p.category.findData(category))
        p.entries.setCurrentRow(next(i for i in range(p.entries.count()) if p.entries.item(i).data(Qt.ItemDataRole.UserRole) == key)); return p
    def test_overview_no_default_claim_or_auto_selection(self):
        p = self.dialog().panel; self.assertEqual(p.entries.count(), 3); self.assertIsNone(p.entries.currentItem()); self.assertFalse(p.open_button.isEnabled()); self.assertIsNone(p.event_dialog)
    def test_all_six_open_exact_event_scene_choice_without_unrelated_inputs(self):
        for index in range(3):
            p = self.dialog(index).panel
            for i, row in enumerate(p.result['rows']):
                p.entries.setCurrentRow(i); self.assertTrue(p.open_event()); child = p.event_dialog.panel
                self.assertEqual((child.event_id, child.scene_id, child.choice_id), (row['event_id'], row['scene_id'], row['choice_id']))
                self.assertIsNone(child.result['actual_eligible'])
                if index == 1: self.assertFalse(hasattr(child, 'action_points')); self.assertFalse(hasattr(child, 'gold'))
    def test_same_source_refresh_keeps_choice_two_real_nonzero_readers_and_child(self):
        d = self.dialog(); d.resize(720, 390); p = d.panel; p.entries.setCurrentRow(1); self.assertTrue(p.open_event()); child = p.event_dialog; child.panel.processed_parts.setValue(2)
        for reader in (p.player, p.technical):
            p.tabs.setCurrentWidget(reader); self.qt.processEvents(); cursor = reader.textCursor(); cursor.setPosition(3); cursor.setPosition(15, QTextCursor.MoveMode.KeepAnchor); reader.setTextCursor(cursor)
            bar = reader.verticalScrollBar(); self.assertGreater(bar.maximum(), 0); bar.setValue(min(3, bar.maximum()))
            old = (cursor.anchor(), cursor.position(), bar.value(), p.tabs.currentIndex(), p.entries.currentRow())
            self.assertTrue(p.refresh_reference()); cursor = reader.textCursor(); self.assertEqual(old, (cursor.anchor(), cursor.position(), bar.value(), p.tabs.currentIndex(), p.entries.currentRow()))
        self.assertIs(p.event_dialog, child); self.assertTrue(child.isVisible()); self.assertEqual(child.panel.processed_parts.value(), 2)
    def test_changed_choice_and_repeated_open_close_owned_child(self):
        p = self.dialog().panel; p.entries.setCurrentRow(0); p.open_event(); old = p.event_dialog; p.open_event(); self.assertFalse(old.isVisible()); old = p.event_dialog; p.entries.setCurrentRow(2); self.assertFalse(old.isVisible()); self.assertIsNone(p.event_dialog)
    def test_real_source_damage_clears_tree_and_recovery_requires_reselection(self):
        p = self.dialog().panel; p.entries.setCurrentRow(0); p.open_event(); old = p.event_dialog
        with TemporaryDirectory() as folder:
            root = Path(folder); clone(root); file = root / model.DATA; raw = file.read_bytes()
            with patch.object(model, 'ROOT', root):
                file.write_bytes(raw + b' '); self.assertFalse(p.refresh_reference()); self.assertFalse(old.isVisible()); self.assertIsNone(p.result); self.assertEqual(p.entries.count(), 0); self.assertEqual(p.technical.toPlainText(), '')
                file.write_bytes(raw); self.assertTrue(p.refresh_reference()); self.assertIsNone(p.entries.currentItem()); self.assertFalse(p.open_event())
    def test_forged_selected_result_is_rejected_before_open(self):
        p = self.dialog().panel; p.entries.setCurrentRow(0); p.result['rows'][0]['choice']['title'] = 'changed'; self.assertFalse(p.open_event()); self.assertIsNone(p.result)
    def test_all_three_item_categories_expose_real_version_entry(self):
        for i in range(3):
            p = self.version_panel(i); self.assertFalse(p.origins_button.isHidden()); self.assertTrue(p.open_reward_origins()); self.assertEqual(p.origins_dialog.panel.item_id, ITEMS[i][1])
    def test_parent_refresh_keeps_tree_then_entry_change_closes_entire_tree(self):
        p = self.version_panel(); p.open_reward_origins(); d = p.origins_dialog; d.panel.entries.setCurrentRow(0); d.panel.open_event(); child = d.panel.event_dialog
        self.assertTrue(p.refresh_reference()); self.assertIs(p.origins_dialog, d); self.assertTrue(child.isVisible()); p.entries.setCurrentRow(-1); self.assertFalse(d.isVisible()); self.assertFalse(child.isVisible())
    def test_parent_loss_and_actual_dialog_close_clear_nested_children(self):
        p = self.version_panel(2); p.open_reward_origins(); d = p.origins_dialog; d.panel.entries.setCurrentRow(0); d.panel.open_event(); child = d.panel.event_dialog; p._unavailable(); self.assertFalse(d.isVisible()); self.assertFalse(child.isVisible())
        d = self.dialog(1); d.panel.entries.setCurrentRow(0); d.panel.open_event(); child = d.panel.event_dialog; d.close(); self.assertFalse(child.isVisible())
    def test_consumer_item_has_no_acquisition_button(self):
        p = self.version_panel(); key = 'rogue_6_relic_cargo_13'; p.entries.setCurrentRow(next(i for i in range(p.entries.count()) if p.entries.item(i).data(Qt.ItemDataRole.UserRole) == key)); self.assertTrue(p.origins_button.isHidden()); self.assertFalse(p.open_reward_origins())
if __name__ == '__main__': unittest.main()
