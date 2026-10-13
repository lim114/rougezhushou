"""Public tier quantities, source coverage, exception identity and real controls."""
from copy import deepcopy
import json
from pathlib import Path
import unittest
from unittest.mock import patch
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication
from rouge import duel_reward_planning as rewards
from rouge.duel_reward_view import DuelRewardPanel
from scripts.build_duel_reward_reference import build, cards

ROOT = Path(__file__).resolve().parents[1]


class DuelRewardTests(unittest.TestCase):
    def test_all_30_original_ids_and_explicit_document_grades_match_bidirectionally(self):
        primary = json.loads((ROOT/'research/p3-event-continuation/selected-original.json').read_text(encoding='utf8'))
        public = cards((ROOT/'research/p3-event-continuation/parts-source.wiki').read_text(encoding='utf8'))
        data = rewards.reference_data()
        self.assertEqual(set(public), set(primary['scrap_module']['scrapItemToType']))
        self.assertEqual(set(public), set(data['items']))
        self.assertEqual(len(public), 30)
        for key, row in data['items'].items():
            self.assertEqual(row['item'], primary['items'][key])
            self.assertEqual(row['documented_grade'], public[key]['grade'])
            self.assertEqual(row['original_rarity'], primary['items'][key]['rarity'])
            self.assertEqual(row['kind'], primary['scrap_module']['scrapItemToType'][key])
        self.assertEqual(build(), data)

    def test_left_quantity_and_complete_class_partition_are_not_an_actual_pool(self):
        result = rewards.duel_rewards('ro6_duel_1', 'left')
        self.assertEqual(result['documented_quantity_reference'],
            {'resource': 'scrap', 'quantity': 1, 'recruit_tickets': 2})
        self.assertEqual(len(result['rows']), 30)
        self.assertEqual(len(result['documented_class_candidates']), 24)
        self.assertEqual(len(result['documented_class_excluded']), 6)
        self.assertEqual(result['unresolved_members'], [])
        self.assertEqual({r['name'] for r in result['documented_class_excluded']},
            {'结构性原理', '“简易遥控器”', '板藤', '恋家果', '光彩松露', '笼控器'})
        self.assertFalse(result['complete_server_reward_pool_known'])
        self.assertTrue(all(r['actual_pool_membership'] is None for r in result['rows']))
        self.assertIsNone(result['actual_reward_quantity'])

    def test_middle_preserves_low_named_exceptions_and_two_special_origin_unknowns(self):
        result = rewards.duel_rewards(tier='middle')
        exceptions = [r for r in result['rows'] if r['membership_status'] == 'named_exception']
        self.assertEqual({r['name'] for r in exceptions}, {'浪花', '雾滚草', '小八界'})
        self.assertTrue(all(r['documented_grade'] == 0 and not r['documented_grade_matches'] for r in exceptions))
        self.assertEqual({r['name'] for r in result['unresolved_members']}, {'笼控器', '光彩松露'})
        self.assertEqual(len(result['documented_class_candidates']), 20)
        self.assertEqual(len(result['documented_class_excluded']), 8)
        self.assertNotIn('笼控器', {r['name'] for r in result['documented_class_candidates']})
        self.assertEqual(len(result['rows']), 30)

    def test_right_original_relic_catalogue_preserves_each_id_but_no_member_or_ticket_pool(self):
        result = rewards.duel_rewards(tier='right')
        primary = json.loads((ROOT/'research/p3-event-continuation/selected-original.json').read_text(encoding='utf8'))
        ids = {key for key, row in primary['items'].items() if row['type'] == 'RELIC'}
        self.assertEqual({r['item_id'] for r in result['rows']}, ids)
        self.assertEqual(len(result['rows']), 272)
        self.assertEqual(result['documented_class_candidates'], [])
        self.assertEqual(len(result['unresolved_members']), 272)
        self.assertEqual(result['documented_quantity_reference']['quantity'], 1)
        self.assertEqual(result['documented_quantity_reference']['recruit_tickets'], 2)
        self.assertFalse(result['recruit_ticket_profession_pool_known'])
        self.assertTrue(all(r['documented_reward_class_matches'] is None for r in result['rows']))
        self.assertEqual(len({r['item_id'] for r in result['rows']}), len(result['rows']))

    def test_declared_success_never_writes_results_and_does_not_turn_failure_into_zero(self):
        context = {'floor': 3, 'node_type': '狭路相逢', 'entry_mode': 'natural', 'gold': 0}
        before = deepcopy(context)
        for value, status in ((None, 'unknown'), (True, 'matched'), (False, 'excluded')):
            result = rewards.duel_rewards('ro6_duel_1', context=context, success_declared=value)
            self.assertEqual(result['documented_condition_status'], status)
            self.assertEqual(result['documented_quantity_reference']['quantity'], 1)
            self.assertIsNone(result['actual_timely_victory'])
            self.assertIsNone(result['actual_reward'])
            self.assertIsNone(result['actual_server_eligible'])
            self.assertFalse(result['inventory_updated'])
            self.assertFalse(result['map_binding_created'])
            self.assertIsNone(result['generation_probability'])
            self.assertEqual(len(result['rows']), 30)
        self.assertEqual(context, before)

    def test_natural_floor_exclusions_do_not_remove_preview_or_apply_to_special_forced_entry(self):
        context = {'floor': 1, 'node_type': '狭路相逢', 'entry_mode': 'natural'}
        result = rewards.duel_rewards(context=context, success_declared=True)
        self.assertEqual(result['documented_condition_status'], 'excluded')
        self.assertEqual([r['stage_id'] for r in result['stage_candidates']], ['ro6_duel_1', 'ro6_duel_2'])
        self.assertEqual(len(result['documented_class_candidates']), 24)
        for amended in ({**context, 'entry_mode': 'content'}, {**context, 'special_region': True}):
            self.assertEqual(rewards.duel_rewards(context=amended, success_declared=True)['documented_condition_status'], 'unknown')

    def test_invalid_identity_and_input_fail_before_guessing_and_source_guard_detects_change(self):
        for arguments in ({'stage_id': '搏杀'}, {'stage_id': 'ro6_n_1_1'}, {'tier': 'LEFT'},
                {'success_declared': 1}, {'context': {'floor': True}}, {'context': {'difficulty': 16}}):
            with self.assertRaises(ValueError):
                rewards.duel_rewards(**arguments)
        changed = deepcopy(rewards.reference_data())
        changed['runtime_source_sha256']['node-events.json'] = '0' * 64
        with patch.object(rewards, 'reference_data', return_value=changed), self.assertRaises(ValueError):
            rewards.duel_rewards()
        first = rewards.duel_rewards()
        first['rows'][0]['item']['name'] = 'changed'
        self.assertNotEqual(rewards.duel_rewards()['rows'][0]['item']['name'], 'changed')

    def test_product_text_explains_complete_fixed_coverage_without_technical_default_fields(self):
        result = rewards.duel_rewards(tier='middle')
        text = rewards.reward_text(result, 'rogue_6_scrap_M_07')
        self.assertIn('文档具名例外', text)
        self.assertIn('低稀有度', text)
        self.assertIn('相符项尚未证明属于当前实际随机池', text)
        self.assertNotIn('rogue_6_scrap_', text)
        self.assertNotIn('NORMAL', text)
        self.assertIn('rogue_6_scrap_M_07', rewards.reward_text(result, 'rogue_6_scrap_M_07', True))
        self.assertIn('有独立获取方式', rewards.reward_text(result, 'rogue_6_scrap_G_12'))
        with self.assertRaises(ValueError):
            rewards.reward_text(result, 'made-up-id')


class DuelRewardViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qt = QApplication.instance() or QApplication([])

    def setUp(self):
        self.panel = DuelRewardPanel()
        self.panel.show()
        self.qt.processEvents()

    def tearDown(self):
        self.panel.close()
        self.panel.deleteLater()
        self.qt.processEvents()

    def find_item(self, key):
        for number in range(self.panel.items.topLevelItemCount()):
            group = self.panel.items.topLevelItem(number)
            for index in range(group.childCount()):
                item = group.child(index)
                if item.data(0, Qt.ItemDataRole.UserRole) == key:
                    return item
        self.fail('Missing exact original item ID ' + key)

    def test_real_tier_change_named_exception_search_and_complete_counts(self):
        self.panel.tier.setCurrentIndex(self.panel.tier.findData('middle'))
        self.panel.search.setText('小八界')
        self.qt.processEvents()
        self.assertEqual(self.panel.selected_id(), 'rogue_6_scrap_M_07')
        self.assertIn('文档具名例外', self.panel.detail.toPlainText())
        self.assertEqual(len(self.panel.result['rows']), 30)
        self.panel.search.clear()
        self.panel.items.setCurrentItem(self.find_item('rogue_6_scrap_G_12'))
        self.assertIn('特殊来源资格待证', self.panel.detail.toPlainText())
        self.panel.tier.setCurrentIndex(self.panel.tier.findData('right'))
        self.assertEqual(len(self.panel.result['unresolved_members']), 272)
        self.assertIn('1件收藏品 + 2张招募券', self.panel.detail.toPlainText())

    def test_fixed_battle_preview_signal_keeps_two_ids_and_no_unrelated_stage_fallback(self):
        emitted = []
        self.panel.stageSelected.connect(emitted.append)
        self.assertFalse(self.panel.battle_button.isEnabled())
        for identity in ('ro6_duel_1', 'ro6_duel_2'):
            self.panel.set_reference(identity)
            self.panel.battle_button.click()
        self.assertEqual(emitted, ['ro6_duel_1', 'ro6_duel_2'])
        with self.assertRaises(ValueError):
            self.panel.set_reference('ro6_n_1_1')
        self.assertEqual(self.panel.stage.currentData(), 'ro6_duel_2')
        self.assertFalse(self.panel.isModal())

    def test_refresh_retains_declared_scenario_search_selection_reading_and_collapsed_groups(self):
        self.panel.set_reference('ro6_duel_2', {'floor': 3, 'node_type': '狭路相逢', 'entry_mode': 'natural'})
        self.panel.tier.setCurrentIndex(self.panel.tier.findData('middle'))
        self.panel.success.setCurrentIndex(self.panel.success.findData(True))
        self.panel.items.setCurrentItem(self.find_item('rogue_6_scrap_M_07'))
        self.panel.items.collapseAll()
        cursor = self.panel.detail.textCursor()
        cursor.setPosition(4)
        cursor.setPosition(12, QTextCursor.MoveMode.KeepAnchor)
        self.panel.detail.setTextCursor(cursor)
        self.panel.detail.verticalScrollBar().setValue(30)
        before = (self.panel.detail.textCursor().selectedText(), self.panel.detail.verticalScrollBar().value())
        self.panel.refresh()
        self.assertEqual(self.panel.selected_id(), 'rogue_6_scrap_M_07')
        self.assertEqual(self.panel.stage.currentData(), 'ro6_duel_2')
        self.assertIs(self.panel.success.currentData(), True)
        self.assertEqual((self.panel.detail.textCursor().selectedText(), self.panel.detail.verticalScrollBar().value()), before)
        self.assertTrue(all(not self.panel.items.topLevelItem(i).isExpanded() for i in range(self.panel.items.topLevelItemCount())))
        self.panel.set_context({'floor': 1, 'node_type': '狭路相逢', 'entry_mode': 'natural'})
        self.assertEqual(self.panel.result['documented_condition_status'], 'excluded')
        self.assertEqual(self.panel.selected_id(), 'rogue_6_scrap_M_07')
        self.panel.technical.setChecked(True)
        self.assertIn('rogue_6_scrap_M_07', self.panel.detail.toPlainText())


if __name__ == '__main__':
    unittest.main()


class DuelRewardEntryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qt = QApplication.instance() or QApplication([])

    def test_battle_entry_preserves_fixed_stage_without_importing_enemy_context(self):
        from rouge.battle_view import BattlePreviewPanel
        panel = BattlePreviewPanel()
        panel.show()
        panel.set_context({'difficulty': 4, 'relics': ['not-an-event-context']})
        panel.set_stage('ro6_duel_2')
        self.qt.processEvents()
        self.assertFalse(panel.duel_reward_button.isHidden())
        panel.duel_reward_button.click()
        window = panel.duel_reward_window
        self.assertEqual(window.stage.currentData(), 'ro6_duel_2')
        self.assertEqual(window.context, {})
        self.assertIsNone(window.result['actual_server_eligible'])
        emitted = []
        panel.stageSelected.connect(emitted.append)
        window.battle_button.click()
        self.assertEqual(emitted, ['ro6_duel_2'])
        panel.set_stage('ro6_n_1_1')
        self.assertTrue(panel.duel_reward_button.isHidden())
        panel.open_duel_rewards()
        self.assertEqual(window.stage.currentData(), 'ro6_duel_2')
        panel.close();window.close();panel.deleteLater()
        self.qt.processEvents()

    def test_directory_battle_entry_retains_tier_and_independent_victory_declaration(self):
        from rouge.node_catalog_view import NodeCatalogPanel
        panel = NodeCatalogPanel()
        panel.show()
        index = next(i for i,e in enumerate(panel.entries)
            if e['kind']=='battle' and e['record'].get('id')=='ro6_duel_1')
        panel.list.setCurrentRow(index)
        self.qt.processEvents()
        self.assertFalse(panel.duel_reward_button.isHidden())
        panel.duel_reward_button.click()
        window = panel.duel_reward_window
        self.assertEqual(window.stage.currentData(), 'ro6_duel_1')
        window.tier.setCurrentIndex(window.tier.findData('middle'))
        window.success.setCurrentIndex(window.success.findData(True))
        panel.show_selected()
        self.assertEqual(window.tier.currentData(), 'middle')
        self.assertTrue(window.success.currentData())
        emitted = []
        panel.stageSelected.connect(emitted.append)
        window.stage.setCurrentIndex(window.stage.findData('ro6_duel_1'))
        window.battle_button.click()
        self.assertEqual(emitted, ['ro6_duel_1'])
        other = next(i for i,e in enumerate(panel.entries)
            if e['kind']=='function' and e['record']['node_type']!='狭路相逢')
        panel.list.setCurrentRow(other)
        self.assertTrue(panel.duel_reward_button.isHidden())
        self.assertEqual(window.tier.currentData(), 'middle')
        panel.close();window.close();panel.deleteLater()
        self.qt.processEvents()
