"""Moving plant documentation reaches existing player views without totals."""
from copy import deepcopy
import unittest

from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication

from rouge.battle_reward_planning import MOVING, reward_data, stage_reward_sources, reward_source_text
from rouge.battle_preview import battle_data
from rouge.battle_view import BattlePreviewPanel
from rouge.node_catalog_view import NodeCatalogPanel


HIGHER = {'ro6_n_4_3', 'ro6_e_4_3', 'ro6_n_4_6', 'ro6_e_4_6',
          'ro6_n_5_3', 'ro6_e_5_3', 'ro6_n_6_1', 'ro6_e_6_1'}


class MovingRewardIntegration287Tests(unittest.TestCase):
    def test_all_fixed_higher_level_stages_receive_conditional_reference(self):
        old = deepcopy(reward_data())
        covered = set()
        for sid in battle_data()['stages']:
            result = stage_reward_sources(sid)
            for row in result['rows']:
                if row['entity_id'] != MOVING:
                    continue
                rule = row['rule']
                self.assertEqual([o['quantity'] for o in rule['outcomes']], [10, -10], sid)
                self.assertTrue(rule['all_fixed_level_candidates_documented'], sid)
                self.assertIsNone(row['actual_reward'])
                self.assertIsNone(row['actual_outcome'])
                self.assertFalse(row['quantity_is_total'])
                self.assertFalse(rule['current_rogue6_server_script_verified'])
                if rule['referenced_levels'] == [2]:
                    covered.add(sid)
            self.assertIsNone(result['actual_reward_total'])
            self.assertIsNone(result['probability'])
        self.assertEqual(covered, HIGHER)
        self.assertEqual(reward_data(), old)

    def test_other_devices_keep_frozen_rules_and_cannot_be_added_twice(self):
        for sid in battle_data()['stages']:
            result = stage_reward_sources(sid)
            for row in result['rows']:
                if row['kind'] == 'predefined_device':
                    self.assertEqual(row['rule'], reward_data()['rules'][row['entity_id']])
                    self.assertIsNone(row['actual_reward'])
                    self.assertFalse(row['quantity_is_total'])
        result = stage_reward_sources('ro6_n_1_1')
        text = reward_source_text(result)
        self.assertIn('不能把两条来源各算一次10', text)
        self.assertIn('两个结果互斥', text)
        self.assertIn('不能相加', text)


class MovingRewardView287Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qt = QApplication.instance() or QApplication([])

    def test_battle_reward_selection_reaches_higher_reference_and_preserves_reading(self):
        panel = BattlePreviewPanel()
        self.addCleanup(panel.close)
        panel.resize(1050, 760)
        panel.show()
        panel.set_stage('ro6_n_5_3')
        self.qt.processEvents()
        index = next(i for i in range(1, panel.reward_combo.count())
                     if panel.reward_combo.itemData(i)['entity_id'] == MOVING)
        panel.reward_combo.setCurrentIndex(index)
        self.qt.processEvents()
        row_id = panel.reward_combo.currentData()['id']
        text = panel.spawn_detail.toPlainText()
        self.assertIn('+10源石锭', text)
        self.assertIn('-10源石锭', text)
        self.assertIn('战斗结束', text)
        self.assertIn('未确认', text)
        self.assertNotIn('https://', text)
        self.assertNotIn(MOVING, text)
        self.assertIsNone(panel.grid.reference_cell)
        self.assertIsNone(panel.original.reference_cell)
        cursor = panel.spawn_detail.textCursor()
        cursor.setPosition(3)
        cursor.setPosition(12, QTextCursor.MoveMode.KeepAnchor)
        panel.spawn_detail.setTextCursor(cursor)
        bar = panel.spawn_detail.verticalScrollBar()
        self.assertGreater(bar.maximum(), 0)
        bar.setValue(min(25, bar.maximum()))
        selected, scroll = cursor.selectedText(), bar.value()
        panel.render_rows()
        self.qt.processEvents()
        self.assertEqual(panel.reward_combo.currentData()['id'], row_id)
        self.assertEqual(panel.spawn_detail.toPlainText(), text)
        self.assertEqual(panel.spawn_detail.textCursor().selectedText(), selected)
        self.assertEqual(bar.value(), scroll)
        panel.technical.setChecked(True)
        self.assertIn('435751', panel.spawn_detail.toPlainText())
        self.assertIn(MOVING, panel.spawn_detail.toPlainText())

    def test_node_player_page_has_the_same_gain_loss_conditions_and_battle_entry(self):
        panel = NodeCatalogPanel()
        self.addCleanup(panel.close)
        for sid in sorted(HIGHER):
            panel.list.setCurrentRow(next(i for i, entry in enumerate(panel.entries)
                if entry['kind'] == 'battle' and entry['record'].get('id') == sid))
            self.qt.processEvents()
            text = panel.player_detail.toPlainText()
            self.assertIn('10源石锭', text, sid)
            self.assertIn('-10源石锭', text, sid)
            self.assertIn('击倒收益和漏过损失', text, sid)
            self.assertIn('实际出现及领取总量：未知', text, sid)
            self.assertNotIn('https://', text, sid)
            self.assertNotIn(MOVING, text, sid)
            self.assertTrue(panel.battle_button.isEnabled())


if __name__ == '__main__':
    unittest.main()
