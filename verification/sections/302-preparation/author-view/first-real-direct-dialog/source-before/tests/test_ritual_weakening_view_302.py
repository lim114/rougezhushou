"""Public direct-dialog checks for ritual reading and independent battle browsing."""
from copy import deepcopy
import json
from pathlib import Path
import shutil
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from rouge import ritual_weakening as results
from rouge.ritual_weakening_view import RitualWeakeningPanel


EVENT = 'community_group_032'
SCOPE = ('public-node', 'public-epoch')
KEYS = tuple(f'{EVENT}:scene:{s}:choice:{c}' for s in (2, 3, 4) for c in (0, 1))
ACTUAL_FIELDS = ('actual_choice', 'actual_weakening', 'actual_attached', 'actual_inventory',
                 'actual_consumed', 'actual_effect', 'actual_numeric_result', 'actual_eligible')


class RitualWeakeningViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qt = QApplication.instance() or QApplication([])

    def setUp(self):
        self.panel = RitualWeakeningPanel()
        self.panel.set_reference(EVENT, scope_key=SCOPE)
        self.panel.show()
        self.qt.processEvents()
        self.assertIs(self.panel.packet['source_valid'], True)

    def tearDown(self):
        self.panel._clear_battle()
        self.panel.close()
        self.panel.deleteLater()
        self.qt.processEvents()

    def choose(self, index=0):
        self.panel.choice.setCurrentIndex(index)
        self.qt.processEvents()
        self.assertEqual(self.panel.choice.currentIndex(), index)
        self.assertIsNotNone(self.panel._view_key)
        self.assertTrue(self.panel.open_stage_button.isEnabled())
        return self.panel.packet['choices'][index]

    @staticmethod
    def state(reader):
        c = reader.textCursor()
        return c.anchor(), c.position(), reader.verticalScrollBar().value(), reader.horizontalScrollBar().value()

    def scroll(self, reader):
        self.qt.processEvents()
        self.assertGreater(reader.verticalScrollBar().maximum(), 0)
        cursor = QTextCursor(reader.document())
        cursor.setPosition(4)
        cursor.setPosition(27, QTextCursor.MoveMode.KeepAnchor)
        reader.setTextCursor(cursor)
        reader.verticalScrollBar().setValue(max(1, reader.verticalScrollBar().maximum() // 2))
        self.qt.processEvents()
        self.assertGreater(reader.verticalScrollBar().value(), 0)
        return self.state(reader)

    def assert_cleared(self):
        self.assertEqual(self.panel.choice.count(), 0)
        self.assertEqual(self.panel.choice.currentIndex(), -1)
        self.assertIsNone(self.panel.packet)
        self.assertIsNone(self.panel._view_key)
        self.assertFalse(self.panel.open_stage_button.isEnabled())
        self.assertIsNone(self.panel.battle_preview)
        self.assertIsNone(self.panel.battle_window)
        for reader in (self.panel.player_text, self.panel.source_text):
            self.assertIn('已清除', reader.toPlainText())
            self.assertNotIn('rogue_6_chimera_weaken', reader.toPlainText())
            self.assertNotIn('choice_ro6_end3_', reader.toPlainText())

    def open_battle(self):
        QTest.mouseClick(self.panel.open_stage_button, Qt.MouseButton.LeftButton)
        self.qt.processEvents()
        self.assertIsNotNone(self.panel.battle_window)
        self.assertTrue(self.panel.battle_window.isVisible())
        self.assertEqual(self.panel.battle_preview.current_stage, 'ro6_b_6')
        return self.panel.battle_preview

    def test_six_exact_choices_default_unselected_skip_choices_not_added(self):
        self.assertEqual(self.panel.choice.count(), 6)
        self.assertEqual(self.panel.choice.currentIndex(), -1)
        self.assertEqual([self.panel.choice.itemData(i) for i in range(6)], list(KEYS))
        self.assertFalse(self.panel.open_stage_button.isEnabled())
        self.assertIsNone(self.panel.battle_window)
        self.assertIn('请手动选择', self.panel.player_text.toPlainText())
        self.assertEqual([row['original_choice_id'] for row in self.panel.packet['choices']],
                         ['choice_ro6_end3_' + str(i) for i in (3, 4, 6, 7, 9, 10)])
        for excluded in (f'{EVENT}:scene:{s}:choice:2' for s in (2, 3, 4)):
            self.assertEqual(self.panel.choice.findData(excluded), -1)

    def test_six_rows_three_effects_and_same_private_key_titles_keep_full_identity(self):
        ids, labels = [], []
        for i in range(6):
            row = self.choose(i)
            ids.append(row['weakening_id'])
            labels.append(self.panel.choice.itemText(i))
            evidence = json.loads(self.panel.source_text.toPlainText())
            self.assertEqual(evidence['selected_weakening_details']['reference'], row)
            self.assertIn(row['original_choice_id'], self.panel.source_text.toPlainText())
            self.assertIn(f'流程{(i // 2) + 3} · 选项{(i % 2) + 1}', labels[-1])
            self.assertIsNone(self.panel.battle_window)
        self.assertEqual(ids, ['rogue_6_chimera_weaken_' + str(i) for i in (1, 1, 3, 3, 2, 2)])
        self.assertEqual(len(set(labels)), 6)
        self.assertEqual(len({KEYS[i] for i in (1, 3, 5)}), 3)
        for i in (1, 3, 5):
            self.assertIn('源私钥', labels[i])

    def test_delivery_alternatives_and_weakening_limits_are_read_separately_without_applying(self):
        expected = (('首次', '危朽'), ('待部署区',), ('伤害降低',))
        for index, keywords in zip((0, 2, 4), expected):
            row = self.choose(index)
            text = self.panel.player_text.toPlainText()
            effect = text.split('【资料所述弱化效果】', 1)[1].split('【相关作战资料】', 1)[0]
            for word in keywords:
                self.assertIn(word, effect)
            self.assertIn('同一效果的另一种方式', text)
            self.assertIn('源私钥', text)
            self.assertIn('不表示两种物品必须同时交付', text)
            self.assertIn('不能把效果重复相加', text)
            self.assertIn('不表示一次替代全部三个步骤', text)
            self.assertIn('不表示提交这项物品后立即进入该战斗', text)
            self.assertIn('弱化是否已附着或生效：尚未确认', text)
            self.assertEqual(row['related_stage_reference']['immediate_transition'], None)
            for raw in ('community_group_', 'rogue_6_', 'choice_ro6_', 'reference_id',
                        'source_valid', 'https://', '<@', 'None', 'null'):
                self.assertNotIn(raw, text)
        self.assertIsNone(self.panel.battle_window)
        self.choose(4)
        self.assertIn('不能当作无伤或不再扣血', self.panel.player_text.toPlainText())

    def test_all_actual_fields_remain_unknown_and_no_computation_or_run_update(self):
        for index in range(6):
            self.choose(index)
            evidence = json.loads(self.panel.source_text.toPlainText())
            for value in (evidence['packet'], evidence['selected_weakening_details'],
                          evidence['selected_weakening_details']['reference']):
                for key in ACTUAL_FIELDS:
                    self.assertIsNone(value[key])
            for value in (evidence['packet'], evidence['selected_weakening_details']):
                self.assertIs(value['calculation_applied'], False)
                self.assertIs(value['run_state_updated'], False)

    def test_only_explicit_button_opens_real_separate_fixed_battle_and_reopen_preserves_object(self):
        self.choose()
        self.assertIsNone(self.panel.battle_preview)
        battle = self.open_battle()
        self.assertIs(battle.parent(), self.panel.battle_window)
        self.assertEqual(battle.grid.stage['id'], 'ro6_b_6')
        self.assertIsNotNone(battle.original.pixmap)
        self.assertFalse(battle.original.pixmap.isNull())
        self.assertEqual(battle.context, {})
        window = self.panel.battle_window
        window.close()
        self.assertFalse(window.isVisible())
        self.open_battle()
        self.assertIs(self.panel.battle_window, window)
        self.assertIs(self.panel.battle_preview, battle)
        self.assertEqual(self.panel.choice.currentData(), KEYS[0])

    def test_valid_refresh_preserves_battle_wave_enemy_reward_map_and_real_reader_state(self):
        self.panel.resize(640, 380)
        self.choose()
        parent_states = {}
        for reader in (self.panel.player_text, self.panel.source_text):
            self.panel.reading_tabs.setCurrentWidget(reader)
            parent_states[reader] = self.scroll(reader)
        battle = self.open_battle()
        battle.set_context({'difficulty': 8, 'public_manual_reference': True})
        battle.technical.setChecked(True)
        battle.wave_combo.setCurrentIndex(1)
        battle.enemy_combo.setCurrentIndex(0)
        self.qt.processEvents()
        self.assertGreater(battle.spawn_list.count(), 0)
        battle.spawn_list.setCurrentRow(min(2, battle.spawn_list.count() - 1))
        cell = battle.spawn_list.currentItem().data(Qt.ItemDataRole.UserRole)['route']['start']
        self.assertIsNotNone(cell)
        battle.grid.cellSelected.emit(cell)
        self.qt.processEvents()
        state = {'context': deepcopy(battle.context), 'wave': battle.wave_combo.currentData(),
                 'enemy': deepcopy(battle.enemy_combo.currentData()),
                 'reward': deepcopy(battle.reward_combo.currentData()),
                 'row': battle.spawn_list.currentItem().data(Qt.ItemDataRole.UserRole)['id'],
                 'tile': deepcopy(battle._tile_cell), 'detail': deepcopy(battle._detail_key)}
        reader_states = {reader: self.scroll(reader) for reader in (battle.spawn_detail, battle.enemy_detail)}
        window = self.panel.battle_window
        for _ in range(2):
            self.panel.set_reference(EVENT, scope_key=SCOPE)
            self.qt.processEvents()
            self.assertIs(self.panel.battle_preview, battle)
            self.assertIs(self.panel.battle_window, window)
            self.assertEqual(battle.context, state['context'])
            self.assertEqual(battle.wave_combo.currentData(), state['wave'])
            self.assertEqual(battle.enemy_combo.currentData(), state['enemy'])
            self.assertEqual(battle.reward_combo.currentData(), state['reward'])
            self.assertEqual(battle.spawn_list.currentItem().data(Qt.ItemDataRole.UserRole)['id'], state['row'])
            self.assertEqual(battle._tile_cell, state['tile'])
            self.assertEqual(battle._detail_key, state['detail'])
            for reader, saved in reader_states.items():
                self.assertEqual(self.state(reader), saved)
            for reader, saved in parent_states.items():
                self.assertEqual(self.state(reader), saved)
        self.panel.choice.setCurrentIndex(-1)
        self.panel.reading_tabs.setCurrentWidget(self.panel.source_text)
        saved = self.scroll(self.panel.source_text)
        self.panel.refresh_reference()
        self.qt.processEvents()
        self.assertEqual(self.panel.choice.currentIndex(), -1)
        self.assertEqual(self.state(self.panel.source_text), saved)
        self.assertIs(self.panel.battle_preview, battle)

    def test_source_failure_clears_open_battle_tree_and_restores_unselected(self):
        self.choose()
        self.open_battle()
        window = self.panel.battle_window
        with patch.object(results, 'event_reference', return_value={
                'target': True, 'status': 'source_unavailable', 'source_valid': False, 'choices': []}):
            self.panel.refresh_reference()
            self.assertFalse(window.isVisible())
            self.assert_cleared()
        self.panel.refresh_reference()
        self.qt.processEvents()
        self.assertEqual(self.panel.choice.count(), 6)
        self.assertEqual(self.panel.choice.currentIndex(), -1)
        self.assertFalse(self.panel.open_stage_button.isEnabled())
        self.assertIsNone(self.panel.battle_window)

    def test_button_fresh_details_failure_drops_old_battle_not_just_disables(self):
        self.choose(1)
        self.open_battle()
        with patch.object(results, 'weakening_details', side_effect=OSError('public source failure')):
            self.assertIs(self.panel.open_related_stage(), False)
            self.assert_cleared()

    def test_same_title_other_flow_or_wrong_related_stage_cannot_open_preview(self):
        self.choose(1)
        other = results.weakening_details(EVENT, f'{EVENT}:scene:3', KEYS[3])
        with patch.object(results, 'weakening_details', return_value=other):
            self.assertIs(self.panel.open_related_stage(), False)
            self.assert_cleared()
        self.panel.refresh_reference()
        row = self.choose(1)
        wrong = results.weakening_details(EVENT, row['scene_key'], row['choice_key'])
        wrong['related_stage_reference']['stage_id'] = 'ro6_b_5'
        with patch.object(results, 'weakening_details', return_value=wrong):
            self.assertIs(self.panel.open_related_stage(), False)
            self.assert_cleared()

    def test_scope_or_event_change_closes_preview_and_new_source_scope_does_not_reselect(self):
        self.choose()
        self.open_battle()
        self.panel.set_reference(EVENT, scope_key=('same-id-new-epoch',))
        self.assertIsNone(self.panel.battle_window)
        self.assertEqual(self.panel.choice.currentIndex(), -1)
        self.choose()
        packet = deepcopy(self.panel.packet)
        packet['scope_key'] += '-other-source'
        with patch.object(results, 'event_reference', return_value=packet):
            self.panel.refresh_reference()
        self.assertEqual(self.panel.choice.currentIndex(), -1)
        self.assertIsNone(self.panel._view_key)
        self.assertFalse(self.panel.open_stage_button.isEnabled())
        self.panel.set_reference('community_group_022', scope_key=SCOPE)
        self.assert_cleared()
        self.panel.set_reference(EVENT, scope_key=SCOPE)
        self.assertEqual(self.panel.choice.currentIndex(), -1)

    def test_real_warm_public_data_failure_clears_and_restores_without_stale_effect(self):
        with TemporaryDirectory(prefix='rouge302-public-view-') as temp:
            clone = Path(temp)
            manifest = json.loads((results.ROOT / results.MANIFEST).read_bytes())
            for relative in set(manifest['files']) | {results.MANIFEST, results.DATA}:
                target = clone / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(results.ROOT / relative, target)
            with patch.object(results, 'ROOT', clone):
                self.panel.set_reference(EVENT, scope_key=SCOPE)
                self.choose()
                path = clone / results.DATA
                raw = path.read_bytes()
                path.write_bytes(raw + b'\n')
                self.panel.refresh_reference()
                self.assert_cleared()
                path.write_bytes(raw)
                self.panel.refresh_reference()
                self.assertEqual(self.panel.choice.count(), 6)
                self.assertEqual(self.panel.choice.currentIndex(), -1)

    def test_each_refresh_queries_event_once_and_selected_details_once_and_forged_combo_clears(self):
        with patch.object(results, 'event_reference', wraps=results.event_reference) as event_query, \
             patch.object(results, 'weakening_details', wraps=results.weakening_details) as details_query:
            self.panel.refresh_reference()
            event_query.assert_called_once_with(EVENT)
            details_query.assert_not_called()
        row = self.choose()
        with patch.object(results, 'event_reference', wraps=results.event_reference) as event_query, \
             patch.object(results, 'weakening_details', wraps=results.weakening_details) as details_query:
            self.panel.refresh_reference()
            event_query.assert_called_once_with(EVENT)
            details_query.assert_called_once_with(EVENT, row['scene_key'], row['choice_key'])
        self.panel.choice.addItem('伪造的旧私钥选项', 'not-a-complete-choice')
        self.panel.choice.setCurrentIndex(self.panel.choice.count() - 1)
        self.assertEqual(self.panel.choice.count(), 6)
        self.assertEqual(self.panel.choice.currentIndex(), -1)
        self.assertFalse(self.panel.open_stage_button.isEnabled())
        self.assertIn('请手动选择', self.panel.player_text.toPlainText())


if __name__ == '__main__':
    unittest.main()
