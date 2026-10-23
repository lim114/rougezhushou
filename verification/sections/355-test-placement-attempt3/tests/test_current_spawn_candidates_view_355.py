"""Candidate UI selection/readback tests; run only after authorized installation."""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

from copy import deepcopy
import unittest
from unittest.mock import patch

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QPlainTextEdit
from rouge import current_spawn_candidates as model
from rouge.current_spawn_candidates_view import CurrentSpawnCandidatesPanel


class CurrentSpawnCandidatesView355Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])
        cls.reference = model.stage_reference('ro6_n_1_1')
        if cls.reference is None:
            raise AssertionError('Installed current source is required; no skipped acceptance.')

    def setUp(self):
        self.query = patch.object(model, 'stage_reference', side_effect=lambda *args: deepcopy(self.reference))
        self.query.start()
        self.widget = CurrentSpawnCandidatesPanel('ro6_n_1_1')
        self.widget.resize(740, 460)
        self.widget.show(); self.app.processEvents()

    def tearDown(self):
        self.widget.close(); self.widget.deleteLater(); self.app.processEvents()
        self.query.stop()

    def select_member(self, predicate=lambda m: True):
        for relation in self.reference['groups']:
            for member in relation['members']:
                if predicate(member):
                    self.widget.relation_combo.setCurrentIndex(self.widget.relation_combo.findData(relation['key']))
                    self.widget.member_combo.setCurrentIndex(self.widget.member_combo.findData(member['action_key']))
                    self.app.processEvents()
                    return relation, member
        self.fail('Required concrete member is missing from the fixed test stage.')

    def test_initial_state_is_a_directory_without_silent_member_selection(self):
        self.assertIsNone(self.widget.relation_combo.currentData())
        self.assertIsNone(self.widget.member_combo.currentData())
        self.assertFalse(self.widget.action_button.isEnabled())
        self.assertFalse(self.widget.position_button.isEnabled())
        self.assertIn('本条不提供地图位置入口', self.widget.player.toPlainText())
        self.assertNotIn('可用下方按钮', self.widget.player.toPlainText())
        self.assertIn('请手动选择', self.widget.player.toPlainText())

    def test_source_member_and_origin_action_navigation_emit_exact_action_keys(self):
        relation, member = self.select_member(lambda m: m['action_type'] == 'SPAWN')
        received = []; self.widget.actionSelected.connect(received.append)
        with patch.object(model, 'resolve_member', return_value={
                'reference': deepcopy(self.reference), 'relation': deepcopy(relation),
                'member': deepcopy(member)}):
            self.assertTrue(self.widget.follow_action())
        self.assertEqual(received, [member['action_key']])
        self.assertIn(member['name'], self.widget.player.toPlainText())
        self.assertIn(member['source_selector'], self.widget.technical.toPlainText())

    def test_position_navigation_delegates_and_does_not_open_a_new_window(self):
        relation, member = self.select_member(lambda m: m['can_request_position'])
        before = set(self.app.topLevelWidgets())
        received = []; self.widget.actionPositionRequested.connect(received.append)
        resolved = {'reference': deepcopy(self.reference), 'relation': deepcopy(relation), 'member': deepcopy(member)}
        with patch.object(model, 'resolve_member', return_value=resolved), patch.object(
                model, 'position_reference', return_value={'action_key': member['action_key']}) as positions:
            self.assertTrue(self.widget.follow_position())
            positions.assert_called_once_with(self.widget.result, relation['key'], member['action_key'])
        self.assertEqual(received, [member['action_key']])
        self.assertEqual(set(self.app.topLevelWidgets()), before)

    def test_empty_and_unnamed_device_have_different_reading_and_map_availability(self):
        _, empty = self.select_member(lambda m: m['action_type'] == 'EMPTY')
        self.assertIn('空白记录', self.widget.player.toPlainText())
        self.assertFalse(self.widget.position_button.isEnabled())
        _, device = self.select_member(lambda m: m['action_type'] == 'ACTIVATE_PREDEFINED' and not m['action']['raw'].get('key'))
        self.assertNotEqual(empty['name'], device['name'])
        self.assertIn('未指定启用目标', self.widget.player.toPlainText())
        self.assertTrue(self.widget.position_button.isEnabled())

    def test_same_source_refresh_preserves_selection_tab_two_nonzero_readings(self):
        relation, member = self.select_member(lambda m: m['action_type'] == 'SPAWN')
        self.widget.player.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.widget.technical.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.widget.resize(500, 310); self.app.processEvents()
        readings = []
        for tab, reader in enumerate((self.widget.player, self.widget.technical)):
            self.widget.tabs.setCurrentIndex(tab); self.app.processEvents()
            bar = reader.verticalScrollBar()
            self.assertGreater(bar.maximum(), 0)
            bar.setValue(max(1, bar.maximum() // 2))
            cursor = reader.textCursor(); cursor.setPosition(3); cursor.setPosition(12, cursor.MoveMode.KeepAnchor)
            reader.setTextCursor(cursor)
            # Set scroll after changing cursor, which can reveal its position.
            bar.setValue(max(1, bar.maximum() // 2))
            readings.append((bar.value(), reader.textCursor().selectionStart(), reader.textCursor().selectionEnd()))
        self.assertEqual(self.widget.tabs.currentIndex(), 1)
        self.assertTrue(self.widget.refresh_reference()); self.app.processEvents()
        self.assertEqual(self.widget.relation_combo.currentData(), relation['key'])
        self.assertEqual(self.widget.member_combo.currentData(), member['action_key'])
        self.assertEqual(self.widget.tabs.currentIndex(), 1)
        for reader, expected in zip((self.widget.player, self.widget.technical), readings):
            self.assertEqual((reader.verticalScrollBar().value(), reader.textCursor().selectionStart(),
                              reader.textCursor().selectionEnd()), expected)

    def test_relation_and_queue_filters_are_real_branches_and_clear_inapplicable_members(self):
        self.select_member()
        self.widget.queue_kind.setCurrentIndex(self.widget.queue_kind.findData('branch'))
        self.assertIsNone(self.widget.relation_combo.currentData())
        self.assertFalse(self.widget.member_combo.isEnabled())
        self.assertFalse(self.widget.position_button.isEnabled())
        self.widget.queue_kind.setCurrentIndex(0)
        self.assertIsNone(self.widget.relation_combo.currentData())
        self.assertTrue(self.widget.relation_combo.isEnabled())
        self.widget.relation_kind.setCurrentIndex(self.widget.relation_kind.findData('package'))
        self.assertFalse(self.widget.relation_combo.isEnabled())  # This exact stage has no packages.
        self.assertIsNone(self.widget.member_combo.currentData())

    def test_source_loss_clears_all_stale_content_and_recovery_requires_manual_choice(self):
        self.select_member(lambda m: m['action_type'] == 'SPAWN')
        invalidated = []; self.widget.sourceInvalidated.connect(lambda: invalidated.append(True))
        with patch.object(model, 'stage_reference', return_value=None):
            self.assertFalse(self.widget.refresh_reference())
        self.assertIsNone(self.widget.result)
        self.assertFalse(self.widget.action_button.isEnabled())
        self.assertFalse(self.widget.position_button.isEnabled())
        self.assertTrue(self.widget.portrait.isHidden())
        self.assertEqual(self.widget.technical.toPlainText(), '')
        self.assertEqual(self.widget.player.toPlainText(), model.UNAVAILABLE)
        self.assertEqual(invalidated, [True])
        self.assertTrue(self.widget.refresh_reference())
        self.assertIsNone(self.widget.relation_combo.currentData())
        self.assertIsNone(self.widget.member_combo.currentData())

    def test_bad_fresh_navigation_clears_instead_of_emitting_old_keys(self):
        self.select_member()
        received = []; self.widget.actionSelected.connect(received.append)
        with patch.object(model, 'resolve_member', return_value=None):
            self.assertFalse(self.widget.follow_action())
        self.assertEqual(received, [])
        self.assertIsNone(self.widget.result)


if __name__ == '__main__':
    unittest.main()
