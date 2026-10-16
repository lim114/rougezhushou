"""Public-panel integration contracts for 299; no private state or MainWindow.

Prepared from pinned complete stage/action identities. These tests must be run
by the root task after assembling the reviewed backend, view and parent panel.
The preparation step does not execute Qt or claim runtime/native acceptance.
"""
from copy import deepcopy
import unittest
from unittest.mock import patch

from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication

from rouge import spawn_candidates as model
from rouge.battle_preview import spawn_rows
from rouge.battle_reward_planning import stage_reward_sources
from rouge.battle_view import BattlePreviewPanel


NORMAL = 'ro6_n_2_1'
EMERGENCY = 'ro6_e_2_1'
PREDEFINED_STAGE = 'ro6_n_1_1'
ENTRY_STAGE = 'ro6_t_2'
ENTRY_REFERENCE = 'battle-event:c9ea7e97a1d6ed9ff9c4989e0b3bb7739e14b975f48801a654fe17ba4612aede'
ORIGIN = 'w1.f4.a1'
OTHER_CANDIDATE = 'w1.f4.a8'
REAL_BRANCH = 'branch:shsbox_1.p1.a1'


def reading(widget):
    cursor = widget.textCursor()
    return (widget.toPlainText(), cursor.anchor(), cursor.position(),
            cursor.selectedText(), widget.verticalScrollBar().value())


class SpawnCandidatesParentIntegration299Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qt = QApplication.instance() or QApplication([])

    def setUp(self):
        self.panel = BattlePreviewPanel()
        self.panel.resize(1120, 760)
        self.panel.show()
        self.panel.set_stage(NORMAL)
        self.qt.processEvents()

    def tearDown(self):
        for name in ('candidate_preview_window', 'spawn_candidates_window',
                     'entry_reference_window', 'duel_reward_window', 'highland_top_dialog'):
            child = getattr(self.panel, name, None)
            if child is not None:
                child.close()
        self.panel.close()
        self.panel.deleteLater()
        self.qt.processEvents()

    def choose(self, control, value):
        index = control.findData(value)
        self.assertGreaterEqual(index, 0, repr(value))
        control.setCurrentIndex(index)
        self.qt.processEvents()

    def select_parent_action(self, action_id):
        matches = [(i, row) for i, row in enumerate(self.panel.rows)
                   if row['id'] == action_id]
        self.assertEqual(len(matches), 1, action_id)
        index, expected = matches[0]
        self.panel.spawn_list.setCurrentRow(index)
        self.qt.processEvents()
        current = self.panel.spawn_list.currentItem().data(Qt.ItemDataRole.UserRole)
        self.assertEqual(current['id'], action_id)
        self.assertEqual(current['action'], expected['action'])
        return current

    def dialog_member(self, kind, queue_id, relation_key, action_id):
        """Choose one complete relation identity, then one exact action identity."""
        dialog = self.panel.spawn_candidates_window
        self.assertIsNotNone(dialog)
        self.assertEqual(dialog.stage_id, self.panel.current_stage)
        self.choose(dialog.relation_kind, kind)
        relations = dialog.packet['groups' if kind == 'group' else 'packages']
        field = 'group_key' if kind == 'group' else 'package_key'
        matches = [row for row in relations
                   if row['kind'] == kind and row['queue_id'] == queue_id
                   and row[field] == relation_key]
        self.assertEqual(len(matches), 1, (self.panel.current_stage, kind, queue_id, relation_key))
        relation = matches[0]
        self.choose(dialog.relation, relation['reference_id'])
        members = [row for row in relation['members'] if row['action_id'] == action_id]
        self.assertEqual(len(members), 1, action_id)
        member = members[0]
        self.assertEqual(member['queue_id'], queue_id)
        self.choose(dialog.member, member['reference_id'])
        self.assertEqual(dialog._selected()[1]['action_id'], action_id)
        return deepcopy(member)

    def open_other_candidate(self, *, current=False):
        self.select_parent_action(ORIGIN)
        opened = self.panel.open_current_spawn_candidates() if current else self.panel.open_spawn_candidates()
        self.assertTrue(opened)
        return self.dialog_member('group', 'w1.f4', 'g1', OTHER_CANDIDATE)

    def seed_reading(self, reader):
        reader.setFixedHeight(82)
        self.qt.processEvents()
        self.assertGreater(len(reader.toPlainText()), 60)
        cursor = QTextCursor(reader.document())
        cursor.setPosition(7)
        cursor.setPosition(39, QTextCursor.MoveMode.KeepAnchor)
        reader.setTextCursor(cursor)
        bar = reader.verticalScrollBar()
        self.assertGreater(bar.maximum(), 0)
        bar.setValue(max(1, bar.maximum() // 2))
        self.qt.processEvents()
        self.assertGreater(bar.value(), 0)
        self.assertTrue(reader.textCursor().selectedText())

    def parent_state(self):
        p = self.panel
        item = p.spawn_list.currentItem()
        return deepcopy({
            'stage': p.current_stage, 'stage_choice': p.stage_combo.currentData(),
            'wave': p.wave_combo.currentData(), 'enemy': p.enemy_combo.currentData(),
            'enemy_branch': p.enemy_choices.branch.currentData(),
            'include_branches': p.include_branches.isChecked(),
            'technical': p.technical.isChecked(),
            'row': item.data(Qt.ItemDataRole.UserRole)['id'] if item else None,
            'list_scroll': p.spawn_list.verticalScrollBar().value(),
            'ordinal': p.occurrence.value(), 'ordinal_max': p.occurrence.maximum(),
            'ordinal_text': p.occurrence_label.text(),
            'tile': p._tile_cell, 'branch_marker': p._branch_marker,
            'detail_key': p._detail_key, 'shown_enemy': p._shown_enemy,
            'grid_row': p.grid.selected, 'grid_cell': p.grid.reference_cell,
            'grid_ordinal': p.grid.selected_ordinal, 'grid_branches': p.grid.branch_positions,
            'original_row': p.original.selected, 'original_cell': p.original.reference_cell,
            'original_ordinal': p.original.selected_ordinal,
            'original_branches': p.original.branch_positions,
            'image_sha': p.original.image_sha256,
            'image_size': (p.original.pixmap.width(), p.original.pixmap.height()),
            'caption': p.map_caption.text(), 'context': p.context,
            'reward_choice': p.reward_combo.currentData(), 'reward_result': p.reward_result,
            'source': p.source_label.text(),
            'spawn_reading': reading(p.spawn_detail), 'enemy_reading': reading(p.enemy_detail),
        })

    def assert_preview_target(self, stage, action, enemy, route):
        child = self.panel.candidate_preview_window
        self.assertIsNotNone(child)
        self.assertIsNot(child, self.panel)
        self.assertTrue(child.isWindow())
        self.assertTrue(child.windowFlags() & Qt.WindowType.Window)
        self.assertEqual(child.current_stage, stage)
        row = child.spawn_list.currentItem().data(Qt.ItemDataRole.UserRole)
        self.assertEqual((row['id'], row['action']['key'], row['action']['routeIndex']),
                         (action, enemy, route))
        self.assertEqual(child.grid.selected['id'], action)
        self.assertEqual(child.original.selected['id'], action)
        return child

    def test_real_all_catalog_button_opens_manual_unselected_reader_without_a_preview(self):
        before = self.parent_state()
        self.assertTrue(self.panel.spawn_candidates_button.isVisible())
        self.assertTrue(self.panel.spawn_candidates_button.isEnabled())
        self.panel.spawn_candidates_button.click()
        self.qt.processEvents()
        dialog = self.panel.spawn_candidates_window
        self.assertIsNone(dialog.origin_action_id)
        self.assertEqual(dialog.relation.currentIndex(), -1)
        self.assertEqual(dialog.member.currentIndex(), -1)
        self.assertFalse(dialog.open_spawn_button.isEnabled())
        self.assertIsNone(self.panel.candidate_preview_window)
        self.assertEqual(self.parent_state(), before)

    def test_current_row_button_uses_exact_origin_and_only_its_queue_relations(self):
        self.select_parent_action(ORIGIN)
        self.assertTrue(self.panel.spawn_group_button.isEnabled())
        self.panel.spawn_group_button.click()
        self.qt.processEvents()
        dialog = self.panel.spawn_candidates_window
        self.assertEqual(dialog.origin_action_id, ORIGIN)
        self.assertEqual(dialog.packet['selected_action']['action_id'], ORIGIN)
        relations = dialog.packet['groups'] + dialog.packet['packages']
        self.assertEqual({(r['kind'], r['queue_id'], r['group_key'], r['package_key']) for r in relations},
                         {('group', 'w1.f4', 'g1', None), ('package', 'w1.f4', None, 'a')})
        self.assertTrue(all(any(m['action_id'] == ORIGIN for m in r['members']) for r in relations))
        self.assertIsNone(dialog.relation.currentData())
        self.assertIsNone(dialog.member.currentData())

    def test_manual_other_spawn_is_freshly_resolved_into_a_separate_exact_preview(self):
        member = self.open_other_candidate(current=True)
        self.assertIsNone(self.panel.candidate_preview_window)
        token = deepcopy(member['token'])
        before = self.parent_state()
        with patch.object(model, 'resolve_reference', wraps=model.resolve_reference) as resolve:
            self.panel.spawn_candidates_window.open_spawn_button.click()
            self.qt.processEvents()
            resolve.assert_any_call(token)
        self.assert_preview_target(NORMAL, OTHER_CANDIDATE, 'enemy_1352_eslime', 19)
        self.assertEqual(self.panel._candidate_preview_token, token)
        self.assertEqual(self.parent_state(), before)

    def test_candidate_window_keeps_parent_filters_ordinal_and_nonzero_reading_state(self):
        self.panel.technical.setChecked(True)
        self.choose(self.panel.wave_combo, 1)
        self.assertTrue(self.panel.enemy_choices.select_branch('普通'))
        self.assertTrue(self.panel.enemy_choices.select_value(('enemy_1246_aslime', 0)))
        self.panel.include_branches.setChecked(False)
        self.select_parent_action('w1.f4.a2')
        self.panel.occurrence.setValue(2)
        self.seed_reading(self.panel.spawn_detail)
        self.seed_reading(self.panel.enemy_detail)
        before = self.parent_state()
        self.assertEqual((before['wave'], before['enemy_branch'], before['ordinal']), (1, '普通', 2))
        self.assertTrue(self.panel.open_spawn_candidates())
        self.dialog_member('group', 'w1.f4', 'g1', OTHER_CANDIDATE)
        self.panel.spawn_candidates_window.open_spawn_button.click()
        self.qt.processEvents()
        self.assert_preview_target(NORMAL, OTHER_CANDIDATE, 'enemy_1352_eslime', 19)
        self.assertEqual(self.parent_state(), before)

    def test_candidate_window_keeps_parent_manual_tile_and_original_map_reference(self):
        self.panel.technical.setChecked(True)
        self.panel._cell_selected({'row': 0, 'col': 0})
        self.qt.processEvents()
        self.assertEqual(self.panel._tile_cell, {'row': 0, 'col': 0})
        self.assertIsNone(self.panel.grid.selected)
        before = self.parent_state()
        self.assertTrue(self.panel.open_spawn_candidates())
        self.dialog_member('group', 'w1.f4', 'g1', OTHER_CANDIDATE)
        self.panel.spawn_candidates_window.open_spawn_button.click()
        self.qt.processEvents()
        self.assert_preview_target(NORMAL, OTHER_CANDIDATE, 'enemy_1352_eslime', 19)
        self.assertEqual(self.parent_state(), before)

    def test_same_stage_refresh_keeps_dialog_and_child_manual_reading_without_reopening(self):
        self.open_other_candidate()
        dialog = self.panel.spawn_candidates_window
        dialog.open_spawn_button.click()
        self.qt.processEvents()
        child = self.assert_preview_target(NORMAL, OTHER_CANDIDATE, 'enemy_1352_eslime', 19)
        child.technical.setChecked(True)
        dialog.reading_tabs.setCurrentWidget(dialog.source_text)
        self.seed_reading(dialog.source_text)
        self.seed_reading(child.spawn_detail)
        selected = (dialog.relation_kind.currentData(), dialog.relation.currentData(),
                    dialog.member.currentData(), reading(dialog.source_text), reading(child.spawn_detail))
        before = self.parent_state()
        self.panel.render_rows()
        self.qt.processEvents()
        self.assertIs(self.panel.spawn_candidates_window, dialog)
        self.assertIs(self.panel.candidate_preview_window, child)
        self.assertEqual((dialog.relation_kind.currentData(), dialog.relation.currentData(),
                          dialog.member.currentData(), reading(dialog.source_text), reading(child.spawn_detail)), selected)
        self.assertIs(dialog.reading_tabs.currentWidget(), dialog.source_text)
        self.assertEqual(self.parent_state(), before)

    def test_normal_emergency_stage_change_clears_targets_and_rejects_old_stage_token(self):
        member = self.open_other_candidate()
        normal_scope = deepcopy(member['token']['scope_key'])
        self.panel.spawn_candidates_window.open_spawn_button.click()
        self.qt.processEvents()
        self.assertIsNotNone(self.panel.candidate_preview_window)
        self.panel.set_stage(EMERGENCY)
        self.qt.processEvents()
        dialog = self.panel.spawn_candidates_window
        self.assertIsNone(self.panel.candidate_preview_window)
        self.assertIsNone(self.panel._candidate_preview_token)
        self.assertEqual(dialog.stage_id, EMERGENCY)
        self.assertEqual(dialog.packet['stage_id'], EMERGENCY)
        self.assertNotEqual(dialog.packet['scope_key'], normal_scope)
        self.assertIsNone(dialog.relation.currentData())
        self.assertIsNone(dialog.member.currentData())
        self.assertFalse(self.panel._request_spawn_candidate(member['token']))
        self.assertIsNone(self.panel.candidate_preview_window)
        emergency = self.dialog_member('group', 'w1.f4', 'g1', OTHER_CANDIDATE)
        self.assertEqual(emergency['token']['stage_id'], EMERGENCY)
        self.assertNotEqual(emergency['token'], member['token'])

    def test_source_failure_clears_reader_and_child_and_recovery_does_not_reselect(self):
        member = self.open_other_candidate()
        dialog = self.panel.spawn_candidates_window
        dialog.open_spawn_button.click()
        self.qt.processEvents()
        before = self.parent_state()
        with patch.object(model, 'MANIFEST', 'research/missing-parent-spawn-299.json'):
            self.panel.render_rows()
            self.qt.processEvents()
            self.assertFalse(self.panel.spawn_candidates_button.isEnabled())
            self.assertIsNone(dialog.packet)
            self.assertIsNone(dialog.relation.currentData())
            self.assertIsNone(dialog.member.currentData())
            self.assertIsNone(self.panel.candidate_preview_window)
            self.assertIsNone(self.panel._candidate_preview_token)
            self.assertFalse(dialog.open_spawn_button.isEnabled())
            self.assertNotIn('manifest_sha256', dialog.source_text.toPlainText())
            self.assertIn('已清除', dialog.source_text.toPlainText())
            self.assertEqual(self.parent_state(), before)
        self.panel.render_rows()
        self.qt.processEvents()
        self.assertTrue(self.panel.spawn_candidates_button.isEnabled())
        self.assertTrue(dialog.packet['source_valid'])
        self.assertIsNone(dialog.relation.currentData())
        self.assertIsNone(dialog.member.currentData())
        self.assertIsNone(self.panel.candidate_preview_window)
        self.assertFalse(dialog.open_spawn_button.isEnabled())
        # Restoring identical source bytes does not revive a previously queued
        # manual intent after its selected member was explicitly invalidated.
        self.assertFalse(self.panel._request_spawn_candidate(member['token']))
        self.assertIsNone(self.panel.candidate_preview_window)

    def test_forged_or_old_source_tokens_cannot_open_or_modify_parent(self):
        member = self.open_other_candidate(current=True)
        before = self.parent_state()
        wrong_source = deepcopy(member['token'])
        wrong_source['source_identity']['data_sha256'] = '0' * 64
        wrong_relation = deepcopy(member['token'])
        wrong_relation['relation_id'] = 'spawn-relation:' + '0' * 64
        added_field = deepcopy(member['token'])
        added_field['actual_selection'] = True
        for token in (wrong_source, wrong_relation, added_field, None, 'w1.f4.a8'):
            with self.subTest(token=token):
                self.assertFalse(self.panel._request_spawn_candidate(token))
                self.assertIsNone(self.panel.candidate_preview_window)
                self.assertEqual(self.parent_state(), before)

    def test_old_origin_token_does_not_borrow_same_named_group_from_another_queue(self):
        member = self.open_other_candidate(current=True)
        self.select_parent_action('w1.f6.a7')
        dialog = self.panel.spawn_candidates_window
        self.assertEqual(dialog.origin_action_id, 'w1.f6.a7')
        self.assertIsNone(dialog.relation.currentData())
        self.assertIsNone(dialog.member.currentData())
        before = self.parent_state()
        self.assertFalse(self.panel._request_spawn_candidate(member['token']))
        self.assertIsNone(self.panel.candidate_preview_window)
        self.assertEqual(self.parent_state(), before)

    def test_real_branch_and_explicit_synthetic_same_key_control_cannot_borrow_main_group(self):
        branch = self.select_parent_action(REAL_BRANCH)
        self.assertTrue(branch['branch'])
        self.assertFalse(self.panel.spawn_group_button.isEnabled())
        self.assertFalse(self.panel.open_current_spawn_candidates())
        # No real branch/main equal-key pair exists in the 38 fixed originals.
        # This adversarial widget-only control is explicitly not a game record.
        self.select_parent_action(ORIGIN)
        item = self.panel.spawn_list.currentItem()
        synthetic = deepcopy(item.data(Qt.ItemDataRole.UserRole))
        self.assertEqual(synthetic['action']['randomSpawnGroupKey'], 'g1')
        synthetic.update(id='branch:g1.p1.a1', branch='g1', wave=None)
        item.setData(Qt.ItemDataRole.UserRole, synthetic)
        self.panel._refresh_spawn_candidates()
        self.assertFalse(self.panel.spawn_group_button.isEnabled())
        self.assertFalse(self.panel.open_current_spawn_candidates())
        self.assertIsNone(self.panel.candidate_preview_window)

    def test_empty_and_exact_predefined_records_have_no_enemy_spawn_bridge(self):
        self.panel.set_stage(PREDEFINED_STAGE)
        self.assertTrue(self.panel.open_spawn_candidates())
        fixtures = [('w3.f1', 'c1', 'w3.f1.a5', 'EMPTY'),
                    ('w1.f1', 't1', 'w1.f1.a1', 'ACTIVATE_PREDEFINED'),
                    ('w1.f1', 't1', 'w1.f1.a2', 'ACTIVATE_PREDEFINED')]
        for queue, key, action, action_type in fixtures:
            with self.subTest(stage=PREDEFINED_STAGE, action=action):
                member = self.dialog_member('group', queue, key, action)
                self.assertEqual(member['action_type'], action_type)
                self.assertIsNone(member['spawn_reference'])
                if action == 'w1.f1.a2':
                    self.assertEqual(member['predefined_reference']['alias'], 'trap_321_shnbox#1')
                    self.assertEqual(member['predefined_reference']['status'], 'exact_alias')
                self.assertFalse(self.panel.spawn_candidates_window.open_spawn_button.isEnabled())
                before = self.parent_state()
                self.assertFalse(self.panel._request_spawn_candidate(member['token']))
                self.assertIsNone(self.panel.candidate_preview_window)
                self.assertEqual(self.parent_state(), before)

    def test_same_enemy_different_actions_keep_separate_details_and_routes(self):
        self.assertTrue(self.panel.open_spawn_candidates())
        observed = []
        for action, route, col in (('w1.f4.a2', 13, 3), ('w1.f4.a3', 14, 4)):
            member = self.dialog_member('package', 'w1.f4', 'a', action)
            self.assertEqual(member['raw_action']['key'], 'enemy_1246_aslime')
            self.panel.spawn_candidates_window.open_spawn_button.click()
            self.qt.processEvents()
            child = self.assert_preview_target(NORMAL, action, 'enemy_1246_aslime', route)
            child.technical.setChecked(True)
            self.qt.processEvents()
            self.assertEqual(child.grid.selected['route']['start']['col'], col)
            self.assertIn('条目标识：' + action, child.spawn_detail.toPlainText())
            observed.append((deepcopy(member['token']), child.spawn_detail.toPlainText(),
                             deepcopy(child.grid.selected['route'])))
        self.assertNotEqual(observed[0][0], observed[1][0])
        self.assertNotEqual(observed[0][1], observed[1][1])
        self.assertNotEqual(observed[0][2], observed[1][2])

    def test_existing_entry_reader_map_and_reward_interfaces_survive_candidate_navigation(self):
        self.panel.set_stage(ENTRY_STAGE)
        self.assertTrue(self.panel.open_entry_references())
        entry = self.panel.entry_reference_window
        self.choose(entry.event_choice, ENTRY_REFERENCE)
        entry.reading_tabs.setCurrentWidget(entry.source_text)
        self.seed_reading(entry.source_text)
        entry_before = (entry.stage_id, entry.event_choice.currentData(), reading(entry.source_text))
        rewards_before = deepcopy(stage_reward_sources(ENTRY_STAGE))
        rows_before = deepcopy(spawn_rows(ENTRY_STAGE))
        before = self.parent_state()
        self.assertTrue(self.panel.open_spawn_candidates())
        self.dialog_member('group', 'w1.f1', 'g1', 'w1.f1.a7')
        self.panel.spawn_candidates_window.open_spawn_button.click()
        self.qt.processEvents()
        self.assertIsNotNone(self.panel.candidate_preview_window)
        self.assertEqual((entry.stage_id, entry.event_choice.currentData(), reading(entry.source_text)), entry_before)
        self.assertIs(entry.reading_tabs.currentWidget(), entry.source_text)
        self.assertEqual(stage_reward_sources(ENTRY_STAGE), rewards_before)
        self.assertEqual(spawn_rows(ENTRY_STAGE), rows_before)
        self.assertEqual(self.parent_state(), before)


if __name__ == '__main__':
    unittest.main()
