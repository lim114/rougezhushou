import copy
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import unittest
from unittest.mock import patch
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
from rouge import current_legacy as model
from rouge.current_legacy_view import CurrentLegacyPanel


class CurrentLegacyView361Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])
        cls.base = model.reference()
        assert cls.base is not None, 'Install the candidate before execution.'

    def setUp(self):
        self.provider = patch.object(model, 'reference', side_effect=lambda: copy.deepcopy(self.base)); self.provider.start()
        self.panel = CurrentLegacyPanel(); self.panel.resize(740, 470); self.panel.show(); self.app.processEvents()

    def tearDown(self): self.panel.close(); self.app.processEvents(); self.provider.stop()

    def select(self, key):
        for i in range(self.panel.entries.count()):
            if self.panel.entries.item(i).data(Qt.ItemDataRole.UserRole) == key:
                self.panel.entries.setCurrentRow(i); self.app.processEvents(); return
        self.fail('missing original ' + key)

    def set_data(self, control, value): control.setCurrentIndex(control.findData(value)); self.app.processEvents()

    def test_five_branches_default_unselected_and_no_hidden_inputs_elsewhere(self):
        self.assertEqual(self.panel.entries.count(), 14); self.assertIsNone(self.panel.selected_key)
        self.assertTrue(self.panel.conditions.isHidden())
        for group, count in (('cat', 3), ('dog', 3), ('cerberus', 1), ('feather', 6), ('hidden', 1)):
            self.set_data(self.panel.group, group); self.assertEqual(self.panel.entries.count(), count)
        self.select(model.HIDDEN); self.assertFalse(self.panel.conditions.isHidden())
        self.set_data(self.panel.group, 'cat'); self.select('rogue_6_legacy_01')
        self.assertTrue(self.panel.conditions.isHidden())
        self.assertNotIn('产生助力的那局', self.panel.player.toPlainText())

    def test_origin_and_receipt_controls_are_independent_and_other_modes_hide_grade(self):
        self.select(model.HIDDEN)
        self.set_data(self.panel.origin_grade, 3); self.set_data(self.panel.next_grade, 4)
        self.assertEqual(self.panel.origin_grade.currentData(), 3)
        self.assertEqual(self.panel.next_grade.currentData(), 4)
        self.set_data(self.panel.next_mode, 'OTHER')
        self.assertTrue(self.panel.next_grade.isHidden()); self.assertIsNone(self.panel.next_grade.currentData())
        self.assertEqual(self.panel.origin_grade.currentData(), 3)

    def test_difficulty_reverse_entry_selects_hidden_without_assigning_either_run(self):
        with patch.object(model, 'packet', return_value=self.base):
            target = model.locate('difficulty', 'NORMAL|3')
            other = CurrentLegacyPanel(target); other.show(); self.app.processEvents()
            self.assertEqual(other.selected_key, model.HIDDEN)
            self.assertIsNone(other.origin_grade.currentData()); self.assertIsNone(other.next_grade.currentData())
            other.close()

    def test_same_refresh_preserves_selection_inputs_tab_and_two_reading_positions(self):
        self.select(model.HIDDEN)
        self.set_data(self.panel.origin_mode, 'NORMAL'); self.set_data(self.panel.origin_grade, 3)
        self.set_data(self.panel.origin_failed, True); self.set_data(self.panel.next_grade, 4)
        self.app.processEvents()
        positions = []
        for index, area in enumerate((self.panel.player, self.panel.technical)):
            self.panel.tabs.setCurrentIndex(index); self.app.processEvents()
            area.verticalScrollBar().setValue(min(9, area.verticalScrollBar().maximum()))
            positions.append(area.verticalScrollBar().value())
        self.assertTrue(all(value > 0 for value in positions))
        self.panel.refresh_reference(); self.app.processEvents()
        self.assertEqual(self.panel.selected_key, model.HIDDEN); self.assertEqual(self.panel.tabs.currentIndex(), 1)
        self.assertEqual(self.panel.origin_grade.currentData(), 3); self.assertEqual(self.panel.next_grade.currentData(), 4)
        self.assertEqual([a.verticalScrollBar().value() for a in (self.panel.player, self.panel.technical)], positions)

    def test_source_failure_closes_owned_original_window_and_manual_recovery(self):
        self.select(model.HIDDEN)
        for i in range(self.panel.source_combo.count()):
            link = self.panel.source_combo.itemData(i)
            if link and link['kind'] == 'item' and link['key'] == model.TARGET:
                self.panel.source_combo.setCurrentIndex(i); break
        with patch.object(model, 'packet', return_value=self.base): self.assertTrue(self.panel.open_source())
        child = self.panel.link_dialog; self.assertTrue(child.isVisible())
        with patch.object(model, 'reference', return_value=None): self.panel.refresh_reference()
        self.app.processEvents(); self.assertFalse(child.isVisible()); self.assertIsNone(self.panel.link_dialog)
        self.assertEqual(self.panel.entries.count(), 0); self.assertIn('旧条目', self.panel.player.toPlainText())
        self.panel.refresh_reference(); self.app.processEvents()
        self.assertEqual(self.panel.entries.count(), 14); self.assertIsNone(self.panel.selected_key)
        self.assertIsNone(self.panel.origin_grade.currentData())

    def test_invalid_target_does_not_borrow_same_named_legacy(self):
        target = {'group': 'feather', 'legacy_id': 'rogue_6_legacy_04',
                  'source_request': {'category': 'relics', 'key': 'rogue_6_legacy_05'}}
        with patch.object(model, 'packet', return_value=self.base):
            other = CurrentLegacyPanel(target); self.assertIsNone(other.selected_key); other.close()

    def test_switching_selected_original_closes_child_and_clears_hidden_declarations(self):
        self.select(model.HIDDEN); self.set_data(self.panel.origin_grade, 3)
        self.select('rogue_6_legacy_01')
        self.assertIsNone(self.panel.origin_grade.currentData()); self.assertTrue(self.panel.conditions.isHidden())
        self.assertIsNone(self.panel.link_dialog)


if __name__ == '__main__': unittest.main()
