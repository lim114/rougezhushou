from copy import deepcopy
import json
from pathlib import Path
import unittest
from unittest.mock import patch
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication
from rouge import scrap_exchange_planning as exchange
from rouge.scrap_exchange_view import ScrapExchangePanel


class ExchangeTests(unittest.TestCase):
    context = {'floor': 3, 'node_type': '失与得', 'entry_mode': 'natural'}

    def test_three_complete_documented_pools_with_exact_exception_and_forbidden_sets(self):
        cases = {
            'rogue_6_scrap_M_01': {'报废轮子', '报废假肢', '标准引擎', '气垫底座', '试作外骨骼', '小八界', '血蕈', '雾滚草', '浪花'},
            'rogue_6_scrap_M_04': {'重弹簧', '老妈妈的融雪', '坎诺特的触须', '回声玉米', '霜晶树', '多生苔藓', '白模鸟', '白模狗', '白模鱼'},
            'rogue_6_scrap_M_11': {'一次性喷气背包', '结构性原理', '“简易遥控器”', '板藤', '恋家果', '光彩松露', '涂装黎博利', '涂装佩洛', '涂装阿戈尔'}}
        for offered, expected in cases.items():
            result = exchange.exchange_candidates(offered)
            self.assertEqual({r['name'] for r in result['documented_candidates']}, expected)
            self.assertEqual(len(result['rows']), 30)
            self.assertEqual(len(result['documented_candidates']), 9)
            self.assertEqual(len(result['documented_excluded']), 21)
            forbidden = [r for r in result['rows'] if r['membership_status'] == 'forbidden_reward']
            self.assertEqual({r['name'] for r in forbidden}, {'种子', '枯苔藓球', '笼控器'})
            self.assertTrue(result['complete_documented_fixed_catalogue_pool_known'])
            self.assertFalse(result['complete_current_server_pool_known'])

    def test_all_30_offered_references_preserve_output_universe_and_unknown_server(self):
        identities = set(exchange.reference_data()['item_ids'])
        for offered in identities:
            result = exchange.exchange_candidates(offered)
            self.assertEqual({r['item_id'] for r in result['rows']}, identities)
            self.assertTrue(all(r['actual_pool_membership'] is None for r in result['rows']))
            self.assertIsNone(result['actual_offered_consumed'])
            self.assertIsNone(result['actual_selection'])
            self.assertIsNone(result['actual_reward_quantity'])
            self.assertEqual(result['documented_reward_quantity'], 1)
            self.assertFalse(result['inventory_updated'])
            self.assertFalse(result['map_binding_created'])
            self.assertIsNone(result['generation_probability'])

    def test_high_only_four_retains_original_middle_grade_and_can_return_an_eligible_self(self):
        high = exchange.exchange_candidates('rogue_6_scrap_M_11')
        exceptions = [r for r in high['rows'] if r['membership_status'] == 'high_only_exception']
        self.assertEqual({r['name'] for r in exceptions}, {'一次性喷气背包', '涂装黎博利', '涂装佩洛', '涂装阿戈尔'})
        self.assertTrue(all(r['documented_grade'] == 1 for r in exceptions))
        self.assertTrue(high['same_item_return_documented'])
        self.assertEqual(next(r for r in high['rows'] if r['same_as_offered_item'])['name'], '结构性原理')
        # The text's own preceding conditions still govern same-item returns.
        offered_exception = exchange.exchange_candidates('rogue_6_scrap_M_08')
        self.assertFalse(offered_exception['same_item_return_documented'])
        for offered in ('rogue_6_scrap_G_01', 'rogue_6_scrap_G_08', 'rogue_6_scrap_G_12'):
            self.assertFalse(exchange.exchange_candidates(offered)['same_item_return_documented'])

    def test_voice_gate_ownership_and_natural_floor_are_independent_of_candidates(self):
        for voice, count, floor, expected in ((None, None, 3, 'unknown'), (False, 1, 3, 'excluded'),
                (True, 0, 3, 'excluded'), (True, 1, 3, 'matched'), (True, 1, 1, 'excluded')):
            result = exchange.exchange_candidates('rogue_6_scrap_M_01', {**self.context, 'floor': floor},
                vocal_cords_unlocked=voice, owned_quantity=count)
            self.assertEqual(result['documented_condition_status'], expected)
            self.assertEqual(len(result['documented_candidates']), 9)
        for context in ({**self.context, 'entry_mode': 'content', 'floor': 1},
                {**self.context, 'special_region': True, 'floor': 1}):
            result = exchange.exchange_candidates('rogue_6_scrap_M_01', context,
                vocal_cords_unlocked=True, owned_quantity=1)
            self.assertEqual(result['documented_condition_status'], 'unknown')

    def test_second_exchange_needs_palm_and_first_scrap_type_not_scrap_subtype(self):
        for palm, first, expected in ((None, None, 'unknown'), (False, 'SCRAP', 'excluded'),
                (True, 'RELIC', 'excluded'), (True, 'SCRAP', 'matched')):
            result = exchange.exchange_candidates('rogue_6_scrap_G_02', self.context,
                vocal_cords_unlocked=True, owned_quantity=1, exchange_index=2,
                palm_unlocked=palm, first_exchange_item_type=first)
            self.assertEqual(result['documented_condition_status'], expected)
            self.assertEqual(len(result['checks']), 5)
        first = exchange.exchange_candidates('rogue_6_scrap_G_02', self.context,
            vocal_cords_unlocked=True, owned_quantity=1, palm_unlocked=False,
            first_exchange_item_type='RELIC')
        self.assertEqual(first['documented_condition_status'], 'matched')
        self.assertEqual(len(first['checks']), 3)
        with self.assertRaises(ValueError):
            exchange.exchange_candidates('rogue_6_scrap_G_02', first_exchange_item_type='GOODS')

    def test_boolean_presence_never_becomes_quantity_and_explicit_count_conflicts_fail(self):
        key = 'rogue_6_scrap_M_01'
        context = {**self.context, 'item_presence': {key: True}}
        before = deepcopy(context)
        result = exchange.exchange_candidates(key, context, vocal_cords_unlocked=True)
        self.assertIsNone(result['owned_quantity_declared'])
        self.assertTrue(result['item_presence_declared'])
        self.assertEqual(result['documented_condition_status'], 'matched')
        self.assertEqual(context, before)
        with self.assertRaises(ValueError):
            exchange.exchange_candidates(key, context, owned_quantity=0)
        counted = exchange.exchange_candidates(key, {**context, 'item_quantities': {key: 2}})
        self.assertEqual(counted['owned_quantity_declared'], 2)
        absent = exchange.exchange_candidates(key, {**self.context, 'item_presence': {key: False}})
        self.assertIsNone(absent['owned_quantity_declared'])
        self.assertEqual(absent['documented_condition_status'], 'excluded')

    def test_invalid_identity_boolean_counts_types_and_index_fail_without_guessing(self):
        for offered, arguments in [('种子', {}), ('rogue_6_scrap_G_99', {}),
                ('rogue_6_scrap_G_01', {'exchange_index': True}),
                ('rogue_6_scrap_G_01', {'exchange_index': 3}),
                ('rogue_6_scrap_G_01', {'owned_quantity': True}),
                ('rogue_6_scrap_G_01', {'owned_quantity': -1}),
                ('rogue_6_scrap_G_01', {'vocal_cords_unlocked': 1}),
                ('rogue_6_scrap_G_01', {'palm_unlocked': 'yes'})]:
            with self.assertRaises(ValueError):
                exchange.exchange_candidates(offered, **arguments)
        changed = deepcopy(exchange.reference_data())
        changed['part_reference_sha256'] = '0' * 64
        with patch.object(exchange, 'reference_data', return_value=changed), self.assertRaises(ValueError):
            exchange.exchange_candidates('rogue_6_scrap_M_01')
        result = exchange.exchange_candidates('rogue_6_scrap_M_01')
        result['rows'][0]['item']['name'] = 'modified'
        self.assertNotEqual(exchange.exchange_candidates('rogue_6_scrap_M_01')['rows'][0]['item']['name'], 'modified')

    def test_text_separates_full_documented_pool_and_game_eligibility(self):
        result = exchange.exchange_candidates('rogue_6_scrap_M_11')
        text = exchange.exchange_text(result, 'rogue_6_scrap_M_08')
        self.assertIn('高档交换具名例外', text)
        self.assertIn('中稀有度', text)
        self.assertIn('实际消耗、陈列数、领取', text)
        self.assertNotIn('rogue_6_scrap_', text)
        self.assertIn('rogue_6_scrap_M_08', exchange.exchange_text(result, 'rogue_6_scrap_M_08', True))


class ExchangeViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qt = QApplication.instance() or QApplication([])

    def setUp(self):
        self.panel = ScrapExchangePanel()
        self.panel.show()
        self.qt.processEvents()

    def tearDown(self):
        self.panel.close()
        self.panel.deleteLater()
        self.qt.processEvents()

    def test_real_offered_pool_switch_search_forbidden_and_capability_gate_controls(self):
        self.assertIsNone(self.panel.result)
        self.panel.set_reference('rogue_6_scrap_M_11', ExchangeTests.context)
        self.assertEqual(len(self.panel.result['documented_candidates']), 9)
        self.panel.search.setText('一次性喷气背包')
        self.assertEqual(self.panel.selected_id(), 'rogue_6_scrap_M_08')
        self.assertIn('高档交换具名例外', self.panel.detail.toPlainText())
        self.panel.offered.setCurrentIndex(self.panel.offered.findData('rogue_6_scrap_M_04'))
        self.assertIn('文档档次不符', self.panel.detail.toPlainText())
        self.panel.search.setText('笼控器')
        self.assertIn('文档不可交换得到', self.panel.detail.toPlainText())
        self.panel.vocal_cords.setCurrentIndex(self.panel.vocal_cords.findData(True))
        self.panel.quantity.setValue(1)
        self.assertEqual(self.panel.result['documented_condition_status'], 'matched')
        self.panel.exchange_index.setCurrentIndex(self.panel.exchange_index.findData(2))
        self.assertTrue(self.panel.first_type.isEnabled())
        self.assertEqual(self.panel.result['documented_condition_status'], 'unknown')
        self.panel.palm.setCurrentIndex(self.panel.palm.findData(True))
        self.panel.first_type.setCurrentIndex(self.panel.first_type.findData('RELIC'))
        self.assertEqual(self.panel.result['documented_condition_status'], 'excluded')
        self.panel.first_type.setCurrentIndex(self.panel.first_type.findData('SCRAP'))
        self.assertEqual(self.panel.result['documented_condition_status'], 'matched')
        self.assertFalse(self.panel.isModal())

    def test_refresh_retains_declarations_search_selection_and_reading_without_writes(self):
        self.panel.set_reference('rogue_6_scrap_M_01', ExchangeTests.context)
        self.panel.quantity.setValue(2)
        self.panel.vocal_cords.setCurrentIndex(self.panel.vocal_cords.findData(True))
        self.panel.search.setText('报废轮子')
        self.panel.items.collapseAll()
        cursor = self.panel.detail.textCursor()
        cursor.setPosition(3)
        cursor.setPosition(10, QTextCursor.MoveMode.KeepAnchor)
        self.panel.detail.setTextCursor(cursor)
        self.panel.detail.verticalScrollBar().setValue(25)
        selected = self.panel.detail.textCursor().selectedText()
        scroll = self.panel.detail.verticalScrollBar().value()
        self.panel.refresh()
        self.assertEqual(self.panel.selected_id(), 'rogue_6_scrap_M_01')
        self.assertEqual(self.panel.search.text(), '报废轮子')
        self.assertEqual(self.panel.quantity.value(), 2)
        self.assertIs(self.panel.vocal_cords.currentData(), True)
        self.assertEqual(self.panel.detail.textCursor().selectedText(), selected)
        self.assertEqual(self.panel.detail.verticalScrollBar().value(), scroll)
        self.assertFalse(self.panel.items.topLevelItem(0).isExpanded())
        self.panel.set_context({**ExchangeTests.context, 'floor': 1})
        self.assertEqual(self.panel.result['documented_condition_status'], 'excluded')
        self.assertEqual(self.panel.quantity.value(), 2)
        self.assertFalse(self.panel.result['inventory_updated'])
        with self.assertRaises(ValueError):
            self.panel.set_reference('guess')
        self.assertEqual(self.panel.offered.currentData(), 'rogue_6_scrap_M_01')


if __name__ == '__main__':
    unittest.main()


class ExchangeEntryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qt = QApplication.instance() or QApplication([])

    def test_actual_event_entry_retains_offered_quantity_and_account_declarations(self):
        from rouge.node_catalog_view import NodeCatalogPanel
        panel = NodeCatalogPanel()
        panel.show()
        index = next(i for i,e in enumerate(panel.entries)
            if e['kind']=='event' and e['record']['id']=='community_group_025')
        panel.list.setCurrentRow(index)
        self.qt.processEvents()
        self.assertFalse(panel.exchange_button.isHidden())
        panel.exchange_button.click()
        window = panel.exchange_window
        window.offered.setCurrentIndex(window.offered.findData('rogue_6_scrap_M_01'))
        window.quantity.setValue(2)
        window.vocal_cords.setCurrentIndex(window.vocal_cords.findData(True))
        panel.refresh()
        self.qt.processEvents()
        self.assertEqual(window.offered.currentData(), 'rogue_6_scrap_M_01')
        self.assertEqual(window.quantity.value(), 2)
        self.assertTrue(window.vocal_cords.currentData())
        self.assertEqual(len(window.result['documented_candidates']), 9)
        self.assertIsNone(window.result['actual_offered_consumed'])
        other = next(i for i,e in enumerate(panel.entries)
            if e['kind']=='event' and e['record']['id']!='community_group_025')
        panel.list.setCurrentRow(other)
        self.assertTrue(panel.exchange_button.isHidden())
        self.assertEqual(window.quantity.value(), 2)
        panel.close();window.close();panel.deleteLater()
        self.qt.processEvents()
