from collections import Counter
from copy import deepcopy
import unittest
from unittest.mock import patch
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication
from rouge import seed_cultivation_planning as seeds, node_catalog
from rouge.seed_cultivation_view import SeedCultivationPanel


class SeedTests(unittest.TestCase):
    context = {'node_type': '秘境行商', 'exploration_mode': 'NORMAL'}

    def test_complete_fixed_catalogue_and_documented_yellow_ids_keep_original_aliases(self):
        result = seeds.seed_cultivation_reference()
        counts = Counter(row['membership_status'] for row in result['rows'])
        self.assertEqual(len(result['rows']), 43)
        self.assertEqual(counts, {'explicit_seed_marker': 14, 'documented_class_match': 6,
            'special_acquisition_unbound': 2, 'documented_class_mismatch': 8,
            'documented_yellow_id': 4, 'original_yellow_group_variant': 9})
        self.assertEqual(set(result['yellow_documented_source_ids']),
            {'rogue_6_legacy_01', 'rogue_6_legacy_02', 'rogue_6_legacy_03', 'rogue_6_legacy_04'})
        legacy = [r for r in result['rows'] if r['kind'] == 'future_yellow_legacy']
        self.assertEqual(Counter(r['name'] for r in legacy),
            {'襁褓中的猫': 3, '襁褓中的狗': 3, '襁褓三头犬': 1, '襁褓羽蛇': 6})
        self.assertEqual(len({r['item_id'] for r in legacy}), 13)
        self.assertEqual(result['original_legacy_total'], 14)
        self.assertEqual(result['unlisted_original_legacy_ids'], ['rogue_6_legacy_10'])
        self.assertNotIn('rogue_6_legacy_10', {r['item_id'] for r in result['rows']})

    def test_seed_markers_and_grade_candidates_do_not_prove_actual_membership(self):
        result = seeds.seed_cultivation_reference()
        marker = [r for r in result['rows'] if r['membership_status'] == 'explicit_seed_marker']
        self.assertEqual({r['name'] for r in marker}, {'重弹簧', '小八界', '一次性喷气背包', '老妈妈的融雪',
            '坎诺特的触须', '结构性原理', '“简易遥控器”', '雾滚草', '回声玉米', '浪花',
            '霜晶树', '多生苔藓', '板藤', '恋家果'})
        unmarked = [r for r in result['rows'] if r['membership_status'] == 'documented_class_match']
        self.assertEqual({r['name'] for r in unmarked}, {'白模鸟', '白模狗', '白模鱼', '涂装黎博利', '涂装佩洛', '涂装阿戈尔'})
        self.assertEqual({r['name'] for r in result['unresolved_members'] if r['kind'] == 'current_scrap'}, {'光彩松露', '笼控器'})
        self.assertTrue(all(r['actual_pool_membership'] is None for r in result['rows']))
        self.assertFalse(result['complete_server_reward_pool_known'])
        self.assertEqual(len(result['documented_candidates']), 24)
        self.assertEqual(len(result['unresolved_members']), 11)
        self.assertEqual(len(result['documented_excluded']), 8)

    def test_blue_relics_are_not_immediate_seed_rewards_and_six_direct_original_pointers_are_preserved(self):
        result = seeds.seed_cultivation_reference()
        direct = [r for r in result['rows'] if r.get('direct_blue_support_reference')]
        self.assertEqual(len(direct), 6)
        initial = {r['legacy_id']: r for r in node_catalog._original_entries()['startup']['legacy_choices']}
        for row in direct:
            self.assertEqual(row['direct_blue_support_reference'], initial[row['item_id']])
            self.assertEqual(row['legacy_group_id'], 'rogue_6_legacy_04')
            self.assertIsNone(row['actual_next_blue_choice_displayed'])
            self.assertFalse(row['buff_applied_to_current_run'])
            self.assertFalse(row['inherited_legacy_created'])
            self.assertNotIn(initial[row['item_id']]['choice']['displayData']['itemId'], {r['item_id'] for r in result['rows']})
        self.assertEqual({r['direct_blue_support_reference']['choice']['title'] for r in direct},
            {'襁褓天马', '襁褓骏鹰', '襁褓巨龙', '襁褓九头蛇', '襁褓白泽', '襁褓金乌'})

    def test_current_shop_completion_and_yellow_only_mode_gate_are_separate(self):
        key = 'rogue_6_scrap_G_01'
        context = {**self.context, 'item_quantities': {key: 1}}
        result = seeds.seed_cultivation_reference(context, cultivation_completed=True)
        self.assertEqual(result['documented_condition_status'], 'matched')
        self.assertEqual(result['yellow_cultivation_condition_status'], 'matched')
        other_mode = seeds.seed_cultivation_reference({**context, 'exploration_mode': 'MONTH_TEAM'}, cultivation_completed=True)
        self.assertEqual(other_mode['documented_condition_status'], 'matched')
        self.assertEqual(other_mode['yellow_cultivation_condition_status'], 'excluded')
        self.assertTrue(all(r['cultivation_condition_status'] == 'matched' for r in other_mode['rows'] if r['kind'] == 'current_scrap'))
        self.assertTrue(all(r['cultivation_condition_status'] == 'excluded' for r in other_mode['rows'] if r['kind'] == 'future_yellow_legacy'))
        for changed in ({**context, 'node_type': '诡意行商'}, {**context, 'item_quantities': {key: 0}}):
            self.assertEqual(seeds.seed_cultivation_reference(changed, cultivation_completed=True)['documented_condition_status'], 'excluded')
        self.assertEqual(seeds.seed_cultivation_reference(context, cultivation_completed=False)['documented_condition_status'], 'excluded')
        self.assertEqual(len(other_mode['rows']), 43)

    def test_next_resources_are_independent_conditional_outcomes_and_regions_not_highest_floor(self):
        result = seeds.seed_cultivation_reference({**self.context, 'floor': 6}, next_normal_exploration=True)
        rows = {r['item_id']: r for r in result['rows']}
        self.assertEqual(rows['rogue_6_legacy_01']['next_effect'],
            {'kind': 'next_initial_resource', 'resource': 'gold', 'quantity': 5, 'minimum_completed_regions': None})
        self.assertEqual(rows['rogue_6_legacy_02']['next_effect'],
            {'kind': 'next_initial_resource', 'resource': 'hope', 'quantity': 1, 'minimum_completed_regions': None})
        self.assertEqual(rows['rogue_6_legacy_01']['next_effect_condition_status'], 'matched')
        self.assertEqual(rows['rogue_6_legacy_03']['next_effect_condition_status'], 'unknown')
        self.assertEqual(rows['rogue_6_legacy_04']['next_effect_condition_status'], 'unknown')
        for regions, expected in ((0, 'excluded'), (1, 'excluded'), (2, 'matched'), (3, 'matched')):
            rows = {r['item_id']: r for r in seeds.seed_cultivation_reference(next_normal_exploration=True, completed_regions=regions)['rows']}
            self.assertEqual(rows['rogue_6_legacy_03']['next_effect_condition_status'], expected)
            self.assertEqual(rows['rogue_6_legacy_04']['next_effect_condition_status'], expected)
            self.assertEqual(rows['rogue_6_legacy_01']['next_effect_condition_status'], 'matched')
        rows = {r['item_id']: r for r in seeds.seed_cultivation_reference(next_normal_exploration=False, completed_regions=2)['rows']}
        self.assertTrue(all(r['next_effect_condition_status'] == 'excluded' for r in rows.values() if r['kind'] == 'future_yellow_legacy'))

    def test_presence_never_becomes_quantity_and_success_never_becomes_received_or_seed_cost(self):
        key = 'rogue_6_scrap_G_01'
        context = {**self.context, 'item_presence': {key: True}}
        before = deepcopy(context)
        result = seeds.seed_cultivation_reference(context, cultivation_completed=True, next_normal_exploration=True, completed_regions=2)
        self.assertIsNone(result['seed_quantity_declared'])
        self.assertIsNone(result['documented_seed_cost_quantity'])
        self.assertEqual(context, before)
        for field in ('actual_seed_consumed', 'actual_cultivation_success', 'actual_result_item_id',
                'actual_reward_quantity', 'actual_current_resource_total', 'actual_next_resource_total', 'actual_server_eligible'):
            self.assertIsNone(result[field])
        self.assertFalse(result['inventory_updated'])
        self.assertFalse(result['run_memory_updated'])
        self.assertFalse(result['next_run_state_created'])
        self.assertIsNone(result['generation_probability'])
        with self.assertRaises(ValueError):
            seeds.seed_cultivation_reference(context, seed_quantity=0)

    def test_invalid_types_context_conflicts_and_changed_direct_source_fail_without_guessing(self):
        for arguments in ({'seed_quantity': True}, {'completed_regions': True}, {'completed_regions': -1},
                {'cultivation_completed': 1}, {'next_normal_exploration': 'yes'},
                {'context': {'exploration_mode': 'UNKNOWN_OTHER'}},
                {'context': self.context, 'current_normal_exploration': False}):
            with self.assertRaises(ValueError):
                seeds.seed_cultivation_reference(**arguments)
        changed = deepcopy(seeds.reference_data())
        changed['original_entry_reference_sha256'] = '0' * 64
        with patch.object(seeds, 'reference_data', return_value=changed), self.assertRaises(ValueError):
            seeds.seed_cultivation_reference()
        result = seeds.seed_cultivation_reference()
        result['rows'][0]['item']['name'] = 'modified'
        self.assertNotEqual(seeds.seed_cultivation_reference()['rows'][0]['item']['name'], 'modified')

    def test_text_has_clear_current_future_scope_and_unknown_alias(self):
        result = seeds.seed_cultivation_reference(next_normal_exploration=True, completed_regions=2)
        text = seeds.cultivation_text(result, 'rogue_6_legacy_05')
        self.assertIn('原同组变体·种子资格待证', text)
        self.assertIn('本局不加资源、不加蓝色收藏品', text)
        self.assertIn('襁褓骏鹰', text)
        self.assertNotIn('rogue_6_legacy_', text)
        self.assertIn('rogue_6_legacy_05', seeds.cultivation_text(result, 'rogue_6_legacy_05', True))
        self.assertIn('明确标记', seeds.cultivation_text(result, 'rogue_6_scrap_M_07'))
        with self.assertRaises(ValueError):
            seeds.cultivation_text(result, 'rogue_6_start_1')


class SeedViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qt = QApplication.instance() or QApplication([])

    def setUp(self):
        self.panel = SeedCultivationPanel()
        self.panel.show()
        self.qt.processEvents()

    def tearDown(self):
        self.panel.close()
        self.panel.deleteLater()
        self.qt.processEvents()

    def test_same_name_variants_and_actual_reference_click_do_not_merge_or_create_current_buff(self):
        self.panel.set_reference('rogue_6_legacy_05', SeedTests.context)
        self.panel.search.setText('襁褓羽蛇')
        leaves = [self.panel.items.topLevelItem(i).child(j)
            for i in range(self.panel.items.topLevelItemCount()) for j in range(self.panel.items.topLevelItem(i).childCount())]
        self.assertEqual(len(leaves), 6)
        self.assertEqual(len({i.data(0, Qt.ItemDataRole.UserRole) for i in leaves}), 6)
        emitted = []
        self.panel.originalChoiceSelected.connect(emitted.append)
        self.assertTrue(self.panel.blue_button.isVisible())
        self.panel.blue_button.click()
        self.assertEqual(emitted, ['choice_ro6_startbuff_8'])
        self.assertFalse(next(r for r in self.panel.result['rows'] if r['item_id'] == 'rogue_6_legacy_05')['buff_applied_to_current_run'])
        self.panel.search.clear()
        self.panel.set_reference('rogue_6_scrap_M_07', SeedTests.context)
        self.assertFalse(self.panel.blue_button.isVisible())
        with self.assertRaises(ValueError):
            self.panel.set_reference('rogue_6_start_1')
        self.assertEqual(self.panel.selected_id(), 'rogue_6_scrap_M_07')

    def test_declared_future_boundary_controls_and_refresh_retention(self):
        self.panel.set_reference('rogue_6_legacy_03', SeedTests.context)
        self.panel.seed_quantity.setValue(1)
        self.panel.completed.setCurrentIndex(self.panel.completed.findData(True))
        self.panel.next_normal.setCurrentIndex(self.panel.next_normal.findData(True))
        self.panel.regions.setValue(1)
        row = next(r for r in self.panel.result['rows'] if r['item_id'] == 'rogue_6_legacy_03')
        self.assertEqual(row['next_effect_condition_status'], 'excluded')
        self.panel.regions.setValue(2)
        self.panel.search.setText('襁褓三头犬')
        self.panel.items.collapseAll()
        cursor = self.panel.detail.textCursor()
        cursor.setPosition(3)
        cursor.setPosition(10, QTextCursor.MoveMode.KeepAnchor)
        self.panel.detail.setTextCursor(cursor)
        self.panel.detail.verticalScrollBar().setValue(35)
        before = (self.panel.detail.textCursor().selectedText(), self.panel.detail.verticalScrollBar().value())
        self.panel.refresh()
        self.assertEqual(self.panel.selected_id(), 'rogue_6_legacy_03')
        self.assertEqual(self.panel.regions.value(), 2)
        self.assertEqual(self.panel.seed_quantity.value(), 1)
        self.assertIs(self.panel.completed.currentData(), True)
        self.assertEqual((self.panel.detail.textCursor().selectedText(), self.panel.detail.verticalScrollBar().value()), before)
        self.assertFalse(self.panel.items.topLevelItem(0).isExpanded())
        self.panel.set_context({**SeedTests.context, 'node_type': '诡意行商'})
        self.assertEqual(self.panel.result['documented_condition_status'], 'excluded')
        self.assertEqual(self.panel.selected_id(), 'rogue_6_legacy_03')
        self.panel.technical.setChecked(True)
        self.assertIn('rogue_6_legacy_03', self.panel.detail.toPlainText())
        self.assertFalse(self.panel.isModal())


if __name__ == '__main__':
    unittest.main()


class SeedEntryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance() or QApplication([])
    def test_secret_merchant_entry_preserves_cross_exploration_declarations(self):
        from rouge.node_catalog_view import NodeCatalogPanel
        panel=NodeCatalogPanel();panel.show()
        index=next(i for i,e in enumerate(panel.entries) if e['kind']=='function' and e['record']['node_type']=='秘境行商')
        panel.list.setCurrentRow(index);panel.seed_button.click();self.qt.processEvents()
        window=panel.seed_window;self.assertTrue(window.isVisible());window.seed_quantity.setValue(2)
        window.current_normal.setCurrentIndex(window.current_normal.findData(True));window.regions.setValue(2)
        panel.refresh();self.qt.processEvents()
        self.assertEqual(window.seed_quantity.value(),2);self.assertEqual(window.regions.value(),2)
        self.assertTrue(window.current_normal.currentData())
        self.assertIsNone(window.result['actual_seed_consumed'])
        panel.close();window.close();panel.deleteLater();self.qt.processEvents()
