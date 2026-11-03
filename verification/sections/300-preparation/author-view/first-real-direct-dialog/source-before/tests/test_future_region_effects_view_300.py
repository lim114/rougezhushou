"""Necessary direct-dialog checks; never builds MainWindow or samples a game."""
import unittest
from unittest.mock import patch

from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication

from rouge import future_region_effects as results
from rouge.future_region_effects_view import FutureRegionEffectsPanel


EVENT = 'community_group_009'
SCENE = EVENT + ':scene:0'
CHOICES = (SCENE + ':choice:0', SCENE + ':choice:1')
SCOPE = ('public-test-node', 'public-test-epoch')


class FutureRegionEffectsViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qt = QApplication.instance() or QApplication([])

    def setUp(self):
        packet = results.event_reference(EVENT, mode='NORMAL', difficulty=5)
        self.assertIs(packet['source_valid'], True)
        self.assertEqual(packet['status'], 'documented_reference')
        self.references = {row['choice_key']: row['reference_id'] for row in packet['choices']}
        self.panel = FutureRegionEffectsPanel()
        self.panel.set_reference(EVENT, mode='NORMAL', difficulty=5, scope_key=SCOPE)
        self.panel.show()
        self.qt.processEvents()

    def tearDown(self):
        self.panel.close()
        self.panel.deleteLater()
        self.qt.processEvents()

    def choose(self, index=0):
        identity = self.references[CHOICES[index]]
        combo_index = self.panel.choice.findData(identity)
        self.assertGreaterEqual(combo_index, 0)
        self.panel.choice.setCurrentIndex(combo_index)
        self.qt.processEvents()
        self.assertEqual(self.panel.choice.currentData(), identity)

    def assert_cleared(self):
        self.assertEqual(self.panel.choice.count(), 0)
        self.assertEqual(self.panel.choice.currentIndex(), -1)
        self.assertIsNone(self.panel.packet)
        self.assertIsNone(self.panel._view_key)
        for reader in (self.panel.player_text, self.panel.source_text):
            text = reader.toPlainText()
            self.assertIn('已清除', text)
            self.assertNotIn('攻击力 +10%', text)
            self.assertNotIn('choice_ro6_normal3_', text)

    @staticmethod
    def reader_state(reader):
        cursor = reader.textCursor()
        return (cursor.anchor(), cursor.position(), reader.verticalScrollBar().value(),
                reader.horizontalScrollBar().value())

    def test_two_exact_choices_default_unselected_without_fast_escape_or_description(self):
        self.assertEqual(self.panel.choice.count(), 2)
        self.assertEqual(self.panel.choice.currentIndex(), -1)
        self.assertIsNone(self.panel._view_key)
        self.assertEqual([self.panel.choice.itemText(i) for i in range(2)],
                         ['尝试驱赶猎狗', '将种子埋在此处'])
        self.assertEqual([row['choice_key'] for row in self.panel.packet['choices']], list(CHOICES))
        self.assertEqual(self.panel.packet['choices'][0]['game_choice_ids'], [])
        self.assertIn('请手动选择', self.panel.player_text.toPlainText())
        self.assertNotIn('攻击力 +10%', self.panel.player_text.toPlainText())

    def test_literal_phase_values_and_direct_resources_are_separate_from_victory_reward(self):
        self.choose(0)
        text = self.panel.player_text.toPlainText()
        for expected in ('原文要求持有笼控器', '获得30源石锭', '希望的沃土',
                         '攻击力 +10%　生命值 +10%', '攻击力 +15%　生命值 +20%',
                         '攻击力 +20%　生命值 +30%', '受该实托邦影响的战斗胜利后',
                         '完整零件池、数量与本局实际领取：尚未确认', '不能按进入节点或整层统一加算',
                         '不是全队现在获得的加成'):
            self.assertIn(expected, text)
        direct = text.split('【选择时的直接变化】', 1)[1].split('【下一地区的条件效果】', 1)[0]
        reward = text.split('【战斗胜利后的奖励】', 1)[1].split('【仍需确认的实际情况】', 1)[0]
        self.assertIn('获得30源石锭', direct)
        self.assertNotIn('随机零件', direct)
        self.assertNotIn('30源石锭', reward)
        self.assertNotIn('1件随机零件', text)
        self.choose(1)
        text = self.panel.player_text.toPlainText()
        self.assertIn('种下1枚种子；不是领取种子', text)
        self.assertNotIn('获得30源石锭', text)

    def test_known_normal_difficulty_boundaries_change_documented_phase_only(self):
        self.choose(0)
        selected = self.panel.choice.currentData()
        for grade, phase, name in ((2, 'early', '早期'), (5, 'early', '早期'),
                                   (6, 'middle', '中期'), (11, 'middle', '中期'),
                                   (12, 'late', '晚期'), (15, 'late', '晚期')):
            with self.subTest(grade=grade):
                self.panel.set_reference(EVENT, mode='NORMAL', difficulty=grade, scope_key=SCOPE)
                self.assertEqual(self.panel.choice.currentData(), selected)
                self.assertEqual(self.panel.packet['documented_phase'], phase)
                text = self.panel.player_text.toPlainText()
                self.assertIn(f'保密等级{grade} → {name}', text)
                self.assertIn('▶ ' + name + '（当前难度的文献阶段）', text)
                self.assertEqual(text.count('（当前难度的文献阶段）'), 1)
                for field in ('actual_choice', 'actual_weather', 'actual_phase', 'actual_affected_nodes',
                              'actual_reward', 'actual_quantity'):
                    self.assertIsNone(self.panel.packet[field])
                self.assertIs(self.panel.packet['calculation_applied'], False)
                self.assertIs(self.panel.packet['run_state_updated'], False)

    def test_low_unknown_invalid_or_other_mode_keeps_all_phases_without_early_default(self):
        self.choose(1)
        selected = self.panel.choice.currentData()
        cases = [('NORMAL', value) for value in (0, 1, None, -1, 16, True, 2.0)]
        cases += [(mode, 5) for mode in (None, 'MONTH_TEAM', 'normal', '', True)]
        for mode, grade in cases:
            with self.subTest(mode=mode, grade=grade):
                self.panel.set_reference(EVENT, mode=mode, difficulty=grade, scope_key=SCOPE)
                self.assertEqual(self.panel.choice.currentData(), selected)
                self.assertIsNone(self.panel.packet['documented_phase'])
                text = self.panel.player_text.toPlainText()
                self.assertIn('当前没有可确定的文献阶段', text)
                self.assertIn('下面三档资料均可查阅', text)
                self.assertNotIn('▶ ', text)
                for literal in ('攻击力 +10%　生命值 +10%', '攻击力 +15%　生命值 +20%',
                                '攻击力 +20%　生命值 +30%'):
                    self.assertIn(literal, text)

    def test_player_words_hide_raw_ids_urls_and_do_not_include_excluded_special_rules(self):
        for index in (0, 1):
            self.choose(index)
            text = self.panel.player_text.toPlainText()
            for raw in ('community_group_', 'rogue_6_', 'choice_ro6_', 'reference_id', 'source_valid',
                        'NORMAL', 'None', 'null', 'https://', 'limit=', 'zone_into_force_weather'):
                self.assertNotIn(raw, text)
            for excluded in ('安眠一隅', '美丽新大地', '不可消除', '不会被消除', '方针：增益'):
                self.assertNotIn(excluded, text)
            self.assertIn('具体节点未知', text)
            self.assertIn('是否生成', text)
            self.assertIn('两个选项分开查阅', text)

    def test_same_scope_refresh_preserves_choice_tab_selection_and_real_nonzero_scroll(self):
        self.panel.resize(640, 380)
        self.choose(0)
        states = {}
        for reader in (self.panel.player_text, self.panel.source_text):
            self.panel.reading_tabs.setCurrentWidget(reader)
            self.qt.processEvents()
            self.assertGreater(reader.verticalScrollBar().maximum(), 0)
            cursor = QTextCursor(reader.document())
            cursor.setPosition(4)
            cursor.setPosition(28, QTextCursor.MoveMode.KeepAnchor)
            reader.setTextCursor(cursor)
            reader.verticalScrollBar().setValue(max(1, reader.verticalScrollBar().maximum() // 2))
            self.qt.processEvents()
            states[reader] = self.reader_state(reader)
            self.assertGreater(states[reader][2], 0)
        selected = self.panel.choice.currentData()
        key = self.panel._view_key
        for _ in range(3):
            self.panel.set_reference(EVENT, mode='NORMAL', difficulty=5, scope_key=SCOPE)
            self.qt.processEvents()
            self.assertEqual(self.panel.choice.currentData(), selected)
            self.assertEqual(self.panel._view_key, key)
            self.assertIs(self.panel.reading_tabs.currentWidget(), self.panel.source_text)
            for reader, expected in states.items():
                self.assertEqual(self.reader_state(reader), expected)
        self.panel.choice.setCurrentIndex(-1)
        self.panel.reading_tabs.setCurrentWidget(self.panel.source_text)
        self.qt.processEvents()
        reader = self.panel.source_text
        self.assertGreater(reader.verticalScrollBar().maximum(), 0)
        cursor = QTextCursor(reader.document())
        cursor.setPosition(4)
        cursor.setPosition(28, QTextCursor.MoveMode.KeepAnchor)
        reader.setTextCursor(cursor)
        reader.verticalScrollBar().setValue(max(1, reader.verticalScrollBar().maximum() // 2))
        self.qt.processEvents()
        unselected_state = self.reader_state(reader)
        self.assertGreater(unselected_state[2], 0)
        self.panel.set_reference(EVENT, mode='NORMAL', difficulty=5, scope_key=SCOPE)
        self.qt.processEvents()
        self.assertIsNone(self.panel._view_key)
        self.assertEqual(self.panel.choice.currentIndex(), -1)
        self.assertIs(self.panel.reading_tabs.currentWidget(), reader)
        self.assertEqual(self.reader_state(reader), unselected_state)

    def test_source_failure_or_exception_clears_both_readers_and_recovers_unselected(self):
        for failure in ('invalid', 'exception', 'none'):
            with self.subTest(failure=failure):
                self.choose(0)
                kwargs = ({'side_effect': OSError('isolated public source failure')} if failure == 'exception'
                          else {'return_value': None} if failure == 'none'
                          else {'return_value': {'status': 'source_unavailable', 'source_valid': False, 'choices': []}})
                with patch.object(results, 'event_reference', **kwargs):
                    self.panel.refresh_reference()
                self.assert_cleared()
                self.panel.refresh_reference()
                self.assertEqual(self.panel.choice.count(), 2)
                self.assertEqual(self.panel.choice.currentIndex(), -1)
                self.assertIsNone(self.panel._view_key)
                self.assertIn('请手动选择', self.panel.player_text.toPlainText())

    def test_scope_event_or_manual_deselect_drops_previous_reading(self):
        self.choose(0)
        self.panel.reading_tabs.setCurrentWidget(self.panel.source_text)
        self.panel.set_reference(EVENT, mode='NORMAL', difficulty=5, scope_key='another-public-node')
        self.assertEqual(self.panel.choice.currentIndex(), -1)
        self.assertIsNone(self.panel._view_key)
        self.assertEqual(self.panel.reading_tabs.currentIndex(), 0)
        self.choose(1)
        self.panel.choice.setCurrentIndex(-1)
        self.assertIn('请手动选择', self.panel.player_text.toPlainText())
        self.assertNotIn('种下1枚种子', self.panel.player_text.toPlainText())
        self.panel.set_reference('community_group_023', mode='NORMAL', difficulty=5, scope_key='not-target')
        self.assert_cleared()
        self.panel.set_reference(EVENT, mode='NORMAL', difficulty=5, scope_key=SCOPE)
        self.assertEqual(self.panel.choice.currentIndex(), -1)

    def test_context_change_rebuilds_current_phase_and_complete_evidence_without_clearing_choice(self):
        self.choose(0)
        identity = self.panel.choice.currentData()
        self.panel.reading_tabs.setCurrentWidget(self.panel.source_text)
        self.panel.set_reference(EVENT, mode='NORMAL', difficulty=12, scope_key=SCOPE)
        text = self.panel.player_text.toPlainText()
        self.assertEqual(self.panel.choice.currentData(), identity)
        self.assertIs(self.panel.reading_tabs.currentWidget(), self.panel.source_text)
        self.assertIn('▶ 晚期（当前难度的文献阶段）', text)
        self.assertNotIn('▶ 早期（当前难度的文献阶段）', text)
        evidence = self.panel.source_text.toPlainText()
        for literal in ('"packet"', 'choice_ro6_normal3_1', 'rogue_6_weather_8_a',
                        'rogue_6_weather_8_b', 'rogue_6_weather_8_c', '"actual_phase": null',
                        '"documented_phase": "late"', '"entry_restored": false'):
            self.assertIn(literal, evidence)
        self.panel.set_reference(EVENT, mode='NORMAL', difficulty=0, scope_key=SCOPE)
        self.assertEqual(self.panel.choice.currentData(), identity)
        self.assertNotIn('▶ ', self.panel.player_text.toPlainText())

    def test_one_fresh_query_each_refresh_and_unknown_combo_value_cannot_retain_old_result(self):
        self.choose(0)
        with patch.object(results, 'event_reference', wraps=results.event_reference) as query:
            self.panel.refresh_reference()
            query.assert_called_once_with(EVENT, mode='NORMAL', difficulty=5)
        self.panel.choice.addItem('伪造的旧选择', 'not-a-public-reference')
        self.panel.choice.setCurrentIndex(self.panel.choice.count() - 1)
        self.assertEqual(self.panel.choice.count(), 2)
        self.assertEqual(self.panel.choice.currentIndex(), -1)
        self.assertIsNone(self.panel._view_key)
        self.assertIn('请手动选择', self.panel.player_text.toPlainText())
        self.assertNotIn('获得30源石锭', self.panel.player_text.toPlainText())


if __name__ == '__main__':
    unittest.main()
