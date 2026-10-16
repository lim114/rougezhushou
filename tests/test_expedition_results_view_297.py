"""Contracts for the manual three-choice expedition reference reader."""
from copy import deepcopy
import unittest
from unittest.mock import patch

from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication

from rouge import expedition_results as results
from rouge.expedition_results_view import ExpeditionResultsPanel


EVENT = 'community_group_024'
SCENE = EVENT + ':scene:0'
CHOICES = tuple(SCENE + ':choice:' + str(index) for index in range(3))


class ExpeditionResultsViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qt = QApplication.instance() or QApplication([])

    def setUp(self):
        self.assertEqual(results.event_reference(EVENT)['status'], 'documented_reference')
        self.panel = ExpeditionResultsPanel()
        self.panel.set_reference(EVENT, scope_key='public:expedition-node')
        self.panel.show()
        self.qt.processEvents()

    def tearDown(self):
        self.panel.close()
        self.panel.deleteLater()
        self.qt.processEvents()

    def choose(self, index=1):
        key = CHOICES[index] + ':expedition-result'
        combo_index = self.panel.choice.findData(key)
        self.assertGreaterEqual(combo_index, 0)
        self.panel.choice.setCurrentIndex(combo_index)
        self.qt.processEvents()
        self.assertEqual(self.panel.choice.currentData(), key)

    def open_source_item(self):
        self.choose(1)
        self.panel.open_item_button.click()
        self.qt.processEvents()

    def assert_cleared(self):
        self.assertEqual(self.panel.choice.count(), 0)
        self.assertIsNone(self.panel._details_identity)
        self.assertIsNone(self.panel._view_key)
        self.assertIsNone(self.panel.packet)
        self.assertFalse(self.panel.icon.isVisible())
        self.assertFalse(self.panel.open_item_button.isEnabled())
        self.assertFalse(self.panel.open_item_button.isVisible())
        for reader in (self.panel.result_text, self.panel.item_text, self.panel.source_text):
            self.assertIn('已清除', reader.toPlainText())
            self.assertNotIn('怦然信标', reader.toPlainText())

    def reader_state(self, reader):
        cursor = reader.textCursor()
        return (cursor.anchor(), cursor.position(), reader.verticalScrollBar().value(),
                reader.horizontalScrollBar().value())

    def test_three_complete_choices_default_none_and_no_automatic_item_open(self):
        self.assertEqual(self.panel.choice.count(), 3)
        self.assertEqual(self.panel.choice.currentIndex(), -1)
        self.assertIsNone(self.panel._details_identity)
        self.assertFalse(self.panel.open_item_button.isVisible())
        self.assertFalse(self.panel.icon.isVisible())
        self.assertEqual([self.panel.choice.itemData(index) for index in range(3)],
                         [key + ':expedition-result' for key in CHOICES])
        self.assertNotIn(':scene:2:choice:1', str([self.panel.choice.itemData(i) for i in range(3)]))
        with patch.object(results, 'item_details', wraps=results.item_details) as details:
            for index in (0, 1, 2):
                self.choose(index)
                self.panel.refresh_reference()
            details.assert_not_called()
        self.assertIn('尚未手动打开', self.panel.item_text.toPlainText())

    def test_rest_two_hope_is_immediate_without_dispatch_or_promotion_effects(self):
        self.choose(2)
        text = self.panel.result_text.toPlainText()
        immediate = text.split('【选择时】', 1)[1].split('【派出期间】', 1)[0]
        returned = text.split('【归来时】', 1)[1]
        self.assertIn('获得2希望', immediate)
        self.assertIn('这项是休息，不派出干员', text)
        self.assertNotIn('归来获得2希望', returned)
        self.assertNotIn('喙', text)
        self.assertNotIn('进阶', text)
        self.assertNotIn('派出对象', text)
        self.assertFalse(self.panel.open_item_button.isVisible())

    def test_root_two_hope_and_beacon_are_return_results_without_invented_count(self):
        self.choose(1)
        text = self.panel.result_text.toPlainText()
        immediate = text.split('【选择时】', 1)[1].split('【派出期间】', 1)[0]
        returned = text.split('【归来时】', 1)[1]
        self.assertNotIn('获得2希望', immediate)
        self.assertIn('归来获得2希望', returned)
        self.assertIn('怦然信标（数量未确认）', returned)
        self.assertIn('资料标明不进阶', returned)
        self.assertNotIn('1件怦然信标', text)
        self.assertIn('不能直接套用于探索源头', text)
        self.assertIn('收益不能相加', text)
        self.assertTrue(self.panel.open_item_button.isVisible())
        self.assertTrue(self.panel.open_item_button.isEnabled())
        self.assertFalse(self.panel.icon.isVisible())

    def test_internal_exploration_keeps_return_pool_and_promotion_unknown(self):
        self.choose(0)
        text = self.panel.result_text.toPlainText()
        self.assertIn('派出1名干员', text)
        self.assertIn('暂时不能编入队伍', text)
        self.assertIn('普通派出的进阶、等级及技能变化', text)
        self.assertIn('不能当作零收益', text)
        self.assertNotIn('归来获得2希望', text)
        self.assertNotIn('怦然信标', text)
        self.assertNotIn('资料标明不进阶', text)
        self.assertFalse(self.panel.open_item_button.isVisible())

    def test_player_text_has_three_phases_ordinary_return_wording_and_no_raw_ids(self):
        for index in range(3):
            with self.subTest(choice=index):
                self.choose(index)
                text = self.panel.result_text.toPlainText()
                for title in ('【选择时】', '【派出期间】', '【归来时】', '【尚未确认】'):
                    self.assertIn(title, text)
                for raw in ('community_group_', 'choice_ro6_', 'reference_id', 'EXPEDITION',
                            'None', 'null', 'status', '{0}'):
                    self.assertNotIn(raw, text)
                if index < 2:
                    self.assertIn('本区域探索结束后', text)
                    self.assertIn('进入新区域时', text)
                    self.assertIn('下一层开始时', text)
                    self.assertIn('特殊区域', text)
                    self.assertIn('不能据此给出倒计时', text)

    def test_manual_root_item_loads_actual_icon_full_item_and_unlock_distinction(self):
        with patch.object(results, 'item_details', wraps=results.item_details) as details:
            self.open_source_item()
            details.assert_called_once_with(EVENT, SCENE, CHOICES[1])
        self.assertTrue(self.panel.icon.isVisible())
        self.assertFalse(self.panel.icon.pixmap().isNull())
        self.assertEqual(self.panel.icon.pixmap().width(), 104)
        text = self.panel.item_text.toPlainText()
        for expected in ('怦然信标 · 归来藏品资料', '所有敌人的生命+20%', '我方单位的生命-40%',
                         '一颗被时刻监测着的心脏', '完成游戏结局', '不等于源头选项或本局完整出现条件',
                         '不是选择时立即领取', '实际归来与领取'):
            self.assertIn(expected, text)
        for irrelevant in ('沙盘α', '部署费用+2', 'rogue_6', 'https://'):
            self.assertNotIn(irrelevant, text)
        self.assertEqual(self.panel.reading_tabs.currentWidget(), self.panel.item_text)

    def test_evidence_keeps_exact_original_ids_annotation_and_return_placeholders(self):
        self.choose(1)
        text = self.panel.source_text.toPlainText()
        for raw in (CHOICES[1], 'choice_ro6_scout_3', EVENT + ':scene:2:choice:1',
                    '干员{0}', 'expedEndingRelic', 'applies_to_root_branch'):
            self.assertIn(raw, text)
        self.assertIn('尚未手动打开', self.panel.item_text.toPlainText())

    def test_same_full_scope_three_refreshes_preserve_item_tab_selection_and_nonzero_reading(self):
        self.open_source_item()
        self.panel.reading_tabs.setCurrentWidget(self.panel.source_text)
        reader = self.panel.source_text
        self.qt.processEvents()
        self.assertGreater(reader.verticalScrollBar().maximum(), 0)
        cursor = QTextCursor(reader.document())
        cursor.setPosition(4)
        cursor.setPosition(32, QTextCursor.MoveMode.KeepAnchor)
        reader.setTextCursor(cursor)
        reader.verticalScrollBar().setValue(max(1, reader.verticalScrollBar().maximum() // 2))
        self.qt.processEvents()
        state = self.reader_state(reader)
        self.assertGreater(state[2], 0)
        identity = self.panel._details_identity
        for _ in range(3):
            self.panel.set_reference(EVENT, scope_key='public:expedition-node')
            self.qt.processEvents()
            self.assertEqual(self.panel.choice.currentData(), CHOICES[1] + ':expedition-result')
            self.assertEqual(self.panel._details_identity, identity)
            self.assertEqual(self.reader_state(reader), state)
            self.assertEqual(self.panel.reading_tabs.currentWidget(), reader)
            self.assertTrue(self.panel.icon.isVisible())

    def test_scope_or_non_target_event_change_clears_and_does_not_reselect(self):
        self.open_source_item()
        self.panel.set_reference(EVENT, scope_key='another-public-node')
        self.assertEqual(self.panel.choice.count(), 3)
        self.assertIsNone(self.panel.choice.currentData())
        self.assertIsNone(self.panel._details_identity)
        self.assertFalse(self.panel.icon.isVisible())
        self.assertFalse(self.panel.open_item_button.isVisible())
        self.assertEqual(self.panel.reading_tabs.currentIndex(), 0)
        self.panel.set_reference('community_group_007', scope_key='non-target')
        self.assertEqual(self.panel.choice.count(), 0)
        for reader in (self.panel.result_text, self.panel.item_text, self.panel.source_text):
            self.assertNotIn('怦然信标', reader.toPlainText())
        self.panel.set_reference(EVENT, scope_key='public:expedition-node')
        self.assertEqual(self.panel.choice.currentIndex(), -1)

    def test_switch_or_deselect_drops_previous_item_without_opening_other_results(self):
        self.open_source_item()
        for index in (0, 2, -1):
            with self.subTest(index=index):
                if index >= 0:
                    self.choose(index)
                else:
                    self.panel.choice.setCurrentIndex(-1)
                self.assertIsNone(self.panel._details_identity)
                self.assertFalse(self.panel.icon.isVisible())
                self.assertFalse(self.panel.open_item_button.isVisible())
                self.assertIn('尚未手动打开', self.panel.item_text.toPlainText())

    def test_event_source_failure_clears_all_readers_and_recovery_is_unselected(self):
        for failure in ('exception', 'source_unavailable'):
            with self.subTest(failure=failure):
                self.open_source_item()
                kwargs = ({'side_effect': OSError('isolated public source failure')} if failure == 'exception'
                          else {'return_value': {'status': 'source_unavailable', 'source_valid': False}})
                with patch.object(results, 'event_reference', **kwargs):
                    self.panel.refresh_reference()
                self.assert_cleared()
                self.panel.refresh_reference()
                self.assertEqual(self.panel.choice.count(), 3)
                self.assertEqual(self.panel.choice.currentIndex(), -1)
                self.assertIsNone(self.panel._details_identity)
                self.assertFalse(self.panel.icon.isVisible())

    def test_open_item_warm_revalidation_failure_clears_old_details_and_all_pages(self):
        self.open_source_item()
        with patch.object(results, 'item_details', return_value={'status': 'source_unavailable', 'source_valid': False}):
            self.panel.refresh_reference()
        self.assert_cleared()

    def test_manual_click_rechecks_choice_and_clears_stale_packet_on_failure(self):
        self.choose(1)
        with patch.object(results, 'choice_reference', return_value={'status': 'source_unavailable', 'source_valid': False}):
            self.panel.open_selected_item()
        self.assert_cleared()

    def test_forged_combo_id_and_wrong_complete_detail_tuple_do_not_fall_back(self):
        self.choose(1)
        self.panel.choice.blockSignals(True)
        self.panel.choice.setItemData(self.panel.choice.currentIndex(), 'forged-expedition-reference')
        self.panel.choice.blockSignals(False)
        self.panel.open_selected_item()
        self.assert_cleared()
        self.panel.refresh_reference()
        self.choose(1)
        details = deepcopy(results.item_details(EVENT, SCENE, CHOICES[1]))
        details['reference']['choice_key'] = CHOICES[0]
        with patch.object(results, 'item_details', return_value=details):
            self.panel.open_selected_item()
        self.assert_cleared()

    def test_choice_reference_identity_mismatch_is_cleared_not_silently_replaced(self):
        self.choose(0)
        reference = deepcopy(results.choice_reference(EVENT, SCENE, CHOICES[0]))
        reference['event_id'] = 'community_group_025'
        with patch.object(results, 'choice_reference', return_value=reference):
            self.panel.refresh_reference()
        self.assert_cleared()

    def test_external_mutation_does_not_change_owned_scope_key(self):
        scope = {'node': {'id': 'public-node'}, 'floor': 3}
        self.panel.set_reference(EVENT, scope_key=scope)
        self.choose(1)
        scope['node']['id'] = 'different-node'
        self.assertEqual(self.panel.scope_key, {'node': {'id': 'public-node'}, 'floor': 3})
        self.panel.refresh_reference()
        self.assertEqual(self.panel.choice.currentData(), CHOICES[1] + ':expedition-result')


if __name__ == '__main__':
    unittest.main()
