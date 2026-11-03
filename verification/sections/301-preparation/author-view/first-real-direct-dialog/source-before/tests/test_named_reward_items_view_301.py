"""Public direct-dialog checks, without MainWindow, sampling, chat or run state."""
from copy import deepcopy
import json
from pathlib import Path
import shutil
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication, QPushButton

from rouge import named_reward_items as results
from rouge.named_reward_items_view import NamedRewardItemsPanel


EVENTS = tuple('community_group_' + n for n in ('005', '006', '007', '008', '010',
                                               '011', '019', '020', '022', '025'))
SCOPE = ('public-node', 'public-epoch')


class NamedRewardItemsViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qt = QApplication.instance() or QApplication([])

    def setUp(self):
        self.panel = NamedRewardItemsPanel()
        self.panel.set_reference(EVENTS[0], scope_key=SCOPE)
        self.panel.show()
        self.qt.processEvents()
        self.assertIs(self.panel.packet['source_valid'], True)

    def tearDown(self):
        self.panel.close()
        self.panel.deleteLater()
        self.qt.processEvents()

    def choose(self, index=0):
        self.assertGreater(self.panel.choice.count(), index)
        self.panel.choice.setCurrentIndex(index)
        self.qt.processEvents()
        self.assertEqual(self.panel.choice.currentIndex(), index)
        self.assertIsNotNone(self.panel._view_key)
        self.assertFalse(self.panel.icon.isHidden())
        self.assertIsNotNone(self.panel.icon.pixmap())
        self.assertFalse(self.panel.icon.pixmap().isNull())
        return self.panel.packet['choices'][index]

    def assert_cleared(self):
        self.assertEqual(self.panel.choice.count(), 0)
        self.assertEqual(self.panel.choice.currentIndex(), -1)
        self.assertIsNone(self.panel.packet)
        self.assertIsNone(self.panel._view_key)
        self.assertIsNone(self.panel._reading_key)
        self.assertTrue(self.panel.icon.isHidden())
        self.assertTrue(self.panel.icon.pixmap().isNull())
        for reader in (self.panel.player_text, self.panel.source_text):
            text = reader.toPlainText()
            self.assertIn('已清除', text)
            for old in ('choice_ro6_', 'rogue_6_', '所有干员部署费用-50%'):
                self.assertNotIn(old, text)

    @staticmethod
    def state(reader):
        c = reader.textCursor()
        return c.anchor(), c.position(), reader.verticalScrollBar().value(), reader.horizontalScrollBar().value()

    def select_and_scroll(self, reader):
        self.panel.reading_tabs.setCurrentWidget(reader)
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

    def clone_public_sources(self, root):
        original = Path(results.ROOT)
        manifest = json.loads((original / results.MANIFEST).read_bytes())
        for relative in set(manifest['files']) | {results.MANIFEST, results.DATA}:
            source = original / relative
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)

    def test_default_unselected_no_second_button_and_unsupported_event_clears(self):
        self.assertEqual(self.panel.choice.count(), 3)
        self.assertEqual(self.panel.choice.currentIndex(), -1)
        self.assertIsNone(self.panel._view_key)
        self.assertTrue(self.panel.icon.isHidden())
        self.assertIn('请手动选择', self.panel.player_text.toPlainText())
        self.assertEqual(self.panel.findChildren(QPushButton), [])
        self.choose()
        for event in ('community_group_021', 'community_group_024', 'community_group_009', None):
            self.panel.set_reference(event, scope_key=SCOPE)
            self.assert_cleared()

    def test_all16_complete_choices_show13_real_images_and_separate_relic_and_scrap(self):
        identities, items, kinds = set(), set(), set()
        for event in EVENTS:
            self.panel.set_reference(event, scope_key=SCOPE)
            self.assertEqual(self.panel.choice.currentIndex(), -1)
            for i in range(self.panel.choice.count()):
                row = self.choose(i)
                identity = (row['event_id'], row['scene_key'], row['choice_key'])
                self.assertNotIn(identity, identities)
                identities.add(identity)
                items.add(row['item_id'])
                kinds.add(row['item_kind'])
                self.assertEqual(row['reference_id'], row['choice_key'])
                text = self.panel.player_text.toPlainText()
                self.assertIn(row['name'] + ' · ' + row['item_kind_name'], text)
                evidence = json.loads(self.panel.source_text.toPlainText())
                details = evidence['selected_item_details']
                self.assertEqual(details['reference'], row)
                self.assertEqual(details['item']['id'], row['item_id'])
                self.assertEqual(details['icon_reference']['item_id'], row['item_id'])
                self.assertEqual(details['item']['type'], row['item_kind'])
                self.assertIn(row['name'], self.panel.icon.accessibleName())
        self.assertEqual(len(identities), 16)
        self.assertEqual(len(items), 13)
        self.assertEqual(kinds, {'RELIC', 'SCRAP'})

    def test_repeated_item_choices_have_distinct_labels_and_costs_without_merging(self):
        cases = [('community_group_007', ('消耗2目标生命值', '消耗8源石锭')),
                 ('community_group_011', ('消耗3行动力', '消耗随机2件加工品', '消耗源私钥'))]
        for event, costs in cases:
            self.panel.set_reference(event, scope_key=SCOPE)
            labels = [self.panel.choice.itemText(i) for i in range(self.panel.choice.count())]
            self.assertEqual(len(labels), len(set(labels)))
            self.assertEqual(len(labels), len(costs))
            for i, expected in enumerate(costs):
                row = self.choose(i)
                text = self.panel.player_text.toPlainText()
                self.assertIn(f'流程1 · 选项{i + 1}：', labels[i])
                block = text.split('【这个选项的条件资料】', 1)[1].split('【物品用途】', 1)[0]
                self.assertIn(expected, block)
                for other in costs:
                    if other != expected:
                        self.assertNotIn(other, block)
                self.assertIn(row['original_choice_id'], self.panel.source_text.toPlainText())

    def test_complete_effect_description_unlock_and_unknown_quantity_are_distinct(self):
        self.choose(0)
        text = self.panel.player_text.toPlainText()
        for literal in ('部署费用-50%', '部署后损失70%的当前生命', '退场前仅生效一次',
                        '它却在为这片土地复仇', '未明确本次奖励数量；不默认1件',
                        '是否领取或持有、是否已生效：尚未确认'):
            self.assertIn(literal, text)
        self.panel.set_reference('community_group_022', scope_key=SCOPE)
        self.choose()
        text = self.panel.player_text.toPlainText()
        condition = text.split('【这个选项的条件资料】', 1)[1].split('【物品用途】', 1)[0]
        unlock = text.split('【图鉴解锁说明】', 1)[1].split('【数量与本局情况】', 1)[0]
        self.assertIn('消耗全部源石锭', condition)
        self.assertNotIn('完成游戏结局', condition)
        self.assertIn('完成游戏结局', unlock)
        self.assertIn('不能直接当作当前选项', unlock)
        self.assertIn('首次释放', text)

    def test_player_reading_hides_raw_ids_and_urls_and_does_not_mark_actual_or_inventory(self):
        for event in EVENTS:
            self.panel.set_reference(event, scope_key=SCOPE)
            for i in range(self.panel.choice.count()):
                self.choose(i)
                player = self.panel.player_text.toPlainText()
                for raw in ('community_group_', 'rogue_6_', 'choice_ro6_', 'https://',
                            'reference_id', 'source_valid', 'None', 'null', '<@'):
                    self.assertNotIn(raw, player)
                packet = json.loads(self.panel.source_text.toPlainText())
                for value in (packet['packet'], packet['selected_item_details'],
                              packet['selected_item_details']['reference']):
                    for key in ('actual_reward', 'actual_quantity', 'actual_claimed',
                                'actual_held', 'actual_effect', 'actual_eligible'):
                        self.assertIsNone(value[key])
                self.assertIs(packet['packet']['inventory_updated'], False)
                self.assertIs(packet['selected_item_details']['inventory_updated'], False)

    def test_same_scope_selected_and_unselected_reading_preserves_tab_cursor_and_real_scroll(self):
        self.panel.resize(640, 380)
        self.choose()
        states = {reader: self.select_and_scroll(reader)
                  for reader in (self.panel.player_text, self.panel.source_text)}
        selected, key = self.panel.choice.currentData(), self.panel._view_key
        for _ in range(2):
            self.panel.set_reference(EVENTS[0], scope_key=SCOPE)
            self.qt.processEvents()
            self.assertEqual(self.panel.choice.currentData(), selected)
            self.assertEqual(self.panel._view_key, key)
            self.assertIs(self.panel.reading_tabs.currentWidget(), self.panel.source_text)
            for reader, expected in states.items():
                self.assertEqual(self.state(reader), expected)
        self.panel.choice.setCurrentIndex(-1)
        expected = self.select_and_scroll(self.panel.source_text)
        for _ in range(2):
            self.panel.set_reference(EVENTS[0], scope_key=SCOPE)
            self.qt.processEvents()
            self.assertIsNone(self.panel._view_key)
            self.assertEqual(self.panel.choice.currentIndex(), -1)
            self.assertIs(self.panel.reading_tabs.currentWidget(), self.panel.source_text)
            self.assertEqual(self.state(self.panel.source_text), expected)

    def test_parent_scope_event_change_or_manual_deselect_clears_previous_image(self):
        self.choose()
        self.panel.reading_tabs.setCurrentWidget(self.panel.source_text)
        self.panel.set_reference(EVENTS[0], scope_key=('another-node', 'another-epoch'))
        self.assertEqual(self.panel.choice.currentIndex(), -1)
        self.assertTrue(self.panel.icon.isHidden())
        self.assertEqual(self.panel.reading_tabs.currentIndex(), 0)
        self.choose()
        self.panel.choice.setCurrentIndex(-1)
        self.assertTrue(self.panel.icon.isHidden())
        self.assertNotIn('所有干员部署费用-50%', self.panel.player_text.toPlainText())
        self.assertIn('请手动选择', self.panel.player_text.toPlainText())
        self.panel.set_reference('community_group_007', scope_key=SCOPE)
        self.assertEqual(self.panel.choice.currentIndex(), -1)
        self.assertTrue(self.panel.icon.isHidden())

    def test_event_source_failure_and_exception_clear_all_then_recover_without_selection(self):
        for kwargs in ({'return_value': None}, {'side_effect': OSError('public source failure')},
                       {'return_value': {'target': True, 'status': 'source_unavailable',
                                         'source_valid': False, 'choices': []}}):
            self.choose()
            with patch.object(results, 'event_reference', **kwargs):
                self.panel.refresh_reference()
            self.assert_cleared()
            self.panel.refresh_reference()
            self.assertEqual(self.panel.choice.count(), 3)
            self.assertEqual(self.panel.choice.currentIndex(), -1)
            self.assertTrue(self.panel.icon.isHidden())

    def test_details_failure_or_same_item_other_choice_is_rejected_and_old_text_cleared(self):
        self.panel.set_reference('community_group_007', scope_key=SCOPE)
        self.choose()
        other = results.item_details('community_group_007', 'community_group_007:scene:0',
                                     'community_group_007:scene:0:choice:1')
        for kwargs in ({'return_value': other}, {'side_effect': OSError('public detail failure')},
                       {'return_value': None}):
            self.panel.refresh_reference()
            self.choose()
            with patch.object(results, 'item_details', **kwargs):
                self.panel.refresh_reference()
            self.assert_cleared()
        self.panel.refresh_reference()
        self.assertEqual(self.panel.choice.currentIndex(), -1)

    def test_real_warm_public_data_and_unrelated_icon_tamper_clear_then_restore_unselected(self):
        with TemporaryDirectory(prefix='rouge301-public-view-') as temp:
            clone = Path(temp)
            self.clone_public_sources(clone)
            with patch.object(results, 'ROOT', clone):
                self.panel.set_reference(EVENTS[0], scope_key=SCOPE)
                self.choose()
                unrelated = results.item_details('community_group_025', 'community_group_025:scene:9',
                                                'community_group_025:scene:9:choice:0')
                for relative in (results.DATA, unrelated['icon_reference']['file']):
                    path = clone / relative
                    original = path.read_bytes()
                    path.write_bytes(original + b'\n')
                    self.panel.refresh_reference()
                    self.assert_cleared()
                    path.write_bytes(original)
                    self.panel.refresh_reference()
                    self.assertEqual(self.panel.choice.currentIndex(), -1)
                    self.assertTrue(self.panel.icon.isHidden())
                    self.choose()

    def test_one_fresh_event_query_and_one_selected_details_query_and_forged_combo_rejected(self):
        with patch.object(results, 'event_reference', wraps=results.event_reference) as event_query, \
             patch.object(results, 'item_details', wraps=results.item_details) as item_query:
            self.panel.refresh_reference()
            event_query.assert_called_once_with(EVENTS[0])
            item_query.assert_not_called()
        row = self.choose()
        with patch.object(results, 'event_reference', wraps=results.event_reference) as event_query, \
             patch.object(results, 'item_details', wraps=results.item_details) as item_query:
            self.panel.refresh_reference()
            event_query.assert_called_once_with(EVENTS[0])
            item_query.assert_called_once_with(row['event_id'], row['scene_key'], row['choice_key'])
        self.panel.choice.addItem('伪造的旧选项', 'not-a-public-choice')
        self.panel.choice.setCurrentIndex(self.panel.choice.count() - 1)
        self.assertEqual(self.panel.choice.count(), 3)
        self.assertEqual(self.panel.choice.currentIndex(), -1)
        self.assertTrue(self.panel.icon.isHidden())
        self.assertNotIn('所有干员部署费用-50%', self.panel.player_text.toPlainText())

    def test_valid_new_source_scope_does_not_silently_reselect_old_reward(self):
        self.choose()
        packet = deepcopy(self.panel.packet)
        packet['scope_key'] += '-new-source-scope'
        self.panel.reading_tabs.setCurrentWidget(self.panel.source_text)
        with patch.object(results, 'event_reference', return_value=packet), \
             patch.object(results, 'item_details', wraps=results.item_details) as item_query:
            self.panel.refresh_reference()
            item_query.assert_not_called()
        self.assertEqual(self.panel.choice.currentIndex(), -1)
        self.assertIsNone(self.panel._view_key)
        self.assertTrue(self.panel.icon.isHidden())
        self.assertEqual(self.panel.reading_tabs.currentIndex(), 0)


if __name__ == '__main__':
    unittest.main()
