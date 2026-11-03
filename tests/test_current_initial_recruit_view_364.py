"""Temporary local widget checks; prepared, not run in the delegated cache task."""
from unittest.mock import patch
import unittest

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from rouge import current_initial_recruit as model
from rouge.current_initial_recruit_view import CurrentInitialRecruitPanel, CurrentInitialRecruitDialog


class CurrentInitialRecruitView364Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.panel = CurrentInitialRecruitPanel()
        self.panel.resize(1040, 810)
        self.panel.show()
        self.app.processEvents()

    def tearDown(self):
        self.panel.close()
        self.app.processEvents()

    def test_actual_filter_branches_and_only_random_special_control(self):
        panel = self.panel
        self.assertEqual(panel.entries.count(), 21)
        self.assertIsNone(panel.selected_target())
        self.assertFalse(panel.declaration_row.isVisible())
        self.assertEqual(panel.scope.findData('unlinked'), -1)
        panel.scope.setCurrentIndex(panel.scope.findData('monthly'))
        self.assertEqual(panel.entries.count(), 4)
        panel.search.setText('2026年10月')
        self.assertEqual(panel.entries.count(), 1)
        panel.kind.setCurrentIndex(panel.kind.findData('group'))
        panel.search.clear()
        self.assertEqual(panel.entries.count(), 14)
        self.assertGreaterEqual(panel.scope.findData('unlinked'), 0)
        panel.scope.setCurrentIndex(panel.scope.findData('unlinked'))
        self.assertEqual(panel.entries.count(), 4)
        panel.entries.setCurrentRow(0)
        self.assertFalse(panel.declaration_row.isVisible())
        self.assertEqual(panel.related.count(), 0)
        self.assertFalse(panel.open_related_button.isEnabled())
        self.assertTrue(panel.navigate_to({'kind': 'group', 'key': model.RANDOM}))
        self.assertTrue(panel.declaration_row.isVisible())
        panel.other_exploration.setCurrentIndex(1)
        self.assertIs(panel.selected_result['listed_unlock_description_matches'], True)
        self.assertIsNone(panel.selected_result['actual_unlocked'])
        self.assertTrue(panel.navigate_to({'kind': 'group', 'key': 'recruit_group_1'}))
        self.assertFalse(panel.declaration_row.isVisible())
        self.assertIsNone(panel.other_exploration.currentData())

    def test_exact_initial_group_forward_and_reverse_and_forged_link_rejection(self):
        panel = self.panel
        source = model.catalog('initial', 'monthly')['rows'][0]
        target = {'kind': 'initial', 'key': source['id']}
        self.assertTrue(panel.navigate_to(target))
        self.assertEqual(panel.related.count(), 1)
        group_target = panel.related.item(0).data(Qt.ItemDataRole.UserRole)
        self.assertFalse(panel.open_related({'kind': 'group', 'key': model.RANDOM}))
        panel.related.setCurrentRow(0)
        self.assertTrue(panel.open_related_button.isEnabled())
        self.assertTrue(panel.open_related())
        self.assertEqual(panel.selected_target(), group_target)
        self.assertEqual(panel.related.count(), 1)
        self.assertEqual(panel.related.item(0).data(Qt.ItemDataRole.UserRole), target)
        self.assertTrue(panel.open_related(target))
        self.assertEqual(panel.selected_target(), target)
        self.assertFalse(panel.navigate_to({'kind': 'initial', 'key': source['id'], 'extra': True}))
        self.assertFalse(panel.navigate_to({'kind': 'group', 'key': '支援作战'}))

    def test_same_source_refresh_preserves_choice_manual_declaration_tabs_and_reading(self):
        panel = self.panel
        target = {'kind': 'group', 'key': model.RANDOM}
        self.assertTrue(panel.navigate_to(target))
        panel.other_exploration.setCurrentIndex(1)
        panel.related.setCurrentRow(8)
        related = panel.related.currentItem().data(Qt.ItemDataRole.UserRole)
        panel.tabs.setCurrentIndex(1)
        self.app.processEvents()
        panel.technical.verticalScrollBar().setValue(18)
        technical_position = panel.technical.verticalScrollBar().value()
        self.assertGreater(technical_position, 0)
        self.assertTrue(panel.refresh_reference())
        self.assertEqual(panel.selected_target(), target)
        self.assertEqual(panel.tabs.currentIndex(), 1)
        self.assertEqual(panel.technical.verticalScrollBar().value(), technical_position)
        self.assertEqual(panel.related.currentItem().data(Qt.ItemDataRole.UserRole), related)
        self.assertIs(panel.selected_result['listed_unlock_description_matches'], True)
        panel.tabs.setCurrentIndex(0)
        self.app.processEvents()
        panel.player.verticalScrollBar().setValue(6)
        position = panel.player.verticalScrollBar().value()
        self.assertGreater(position, 0)
        self.assertTrue(panel.refresh_reference())
        self.assertEqual(panel.tabs.currentIndex(), 0)
        self.assertEqual(panel.player.verticalScrollBar().value(), position)

    def test_bad_source_deselection_recovery_and_dialog_close_clear_all(self):
        panel = self.panel
        panel.navigate_to({'kind': 'group', 'key': model.RANDOM})
        panel.other_exploration.setCurrentIndex(1)
        panel.related.setCurrentRow(0)
        with patch.object(model, 'packet', return_value=None):
            self.assertFalse(panel.open_related())
            self.assertIsNone(panel.result)
            self.assertIsNone(panel.selected_result)
            self.assertEqual(panel.entries.count(), 0)
            self.assertEqual(panel.related.count(), 0)
            self.assertFalse(panel.declaration_row.isVisible())
            self.assertFalse(panel.open_related_button.isEnabled())
            self.assertEqual(panel.technical.toPlainText(), '')
        self.assertTrue(panel.refresh_reference())
        self.assertIsNone(panel.selected_target())
        panel.navigate_to({'kind': 'group', 'key': model.RANDOM})
        panel.entries.setCurrentRow(-1)
        self.assertIsNone(panel.selected_result)
        self.assertIsNone(panel.other_exploration.currentData())
        self.assertFalse(panel.declaration_row.isVisible())
        self.assertEqual(panel.related.count(), 0)
        key = model.catalog('initial', 'monthly')['rows'][0]['id']
        dialog = CurrentInitialRecruitDialog(model.locate('initial', key))
        self.assertEqual(dialog.panel.selected_target(), {'kind': 'initial', 'key': key})
        dialog.close()
        self.assertIsNone(dialog.panel.result)
        self.assertEqual(dialog.panel.entries.count(), 0)
        self.assertEqual(dialog.panel.related.count(), 0)


if __name__ == '__main__':
    unittest.main()
