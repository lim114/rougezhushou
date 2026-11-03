"""Content-linked scrap rewards, separate costs, and unchanged source identity."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import types
import json
import tempfile
import unittest
from unittest.mock import patch

from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication

from rouge import node_catalog as catalog, event_planning
from rouge.node_rewards import _reference
from rouge.node_catalog_view import NodeCatalogPanel, event_details_text
from rouge.player_node_information import node_information_text

ROOT = Path(__file__).resolve().parents[1]
EVENT = 'community_group_007'
SCENE = EVENT + ':scene:0'
CHOICES = (SCENE + ':choice:0', SCENE + ':choice:1')


def legacy_catalog():
    path = ROOT / 'verification/sections/289-preparation/prior-288/rouge/node_catalog.py'
    raw = path.read_bytes()
    if sha256(raw).hexdigest() != '10c81d879fd0e1691ceee8b503b1ec1caa91093aa22193f1fe04226e69df1cf9':
        raise AssertionError('The archived original288 query changed.')
    module = types.ModuleType('rouge._catalog_288_comparison')
    module.__package__ = 'rouge'
    # Both query versions intentionally read the same unchanged fixed data.
    module.__file__ = str(ROOT / 'rouge/node_catalog.py')
    exec(compile(raw, str(path), 'exec'), module.__dict__)
    return module


def entry(**extra):
    record = next(row for row in catalog.all_events(include_indirect=True)['rows']
                  if row['id'] == EVENT)
    return {'kind': 'event', 'record': record, **extra}


class EventRewardIntegration289Tests(unittest.TestCase):
    def test_warm_source_failure_is_visible_in_both_pages_without_losing_original_prose(self):
        from rouge import event_named_reward_links as model
        manifest = json.loads((ROOT / model.MANIFEST).read_text(encoding='utf8'))
        with tempfile.TemporaryDirectory(prefix='rouge-289-public-source-') as temporary:
            clone = Path(temporary)
            for relative in (model.MANIFEST, *manifest['files']):
                target = clone / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((ROOT / relative).read_bytes())
            with patch.object(model, 'ROOT', clone):
                self.assertEqual(catalog.event_reward_options(EVENT)['supplemental_reward_reference']['status'], 'documented_reference')
                target = clone / 'research/p3-event-named-rewards-289/bwiki-investigation.html'
                target.write_bytes(target.read_bytes() + b' ')
                result = catalog.event_reward_options(EVENT)
                self.assertEqual(result['supplemental_reward_reference']['status'], 'unknown')
                self.assertTrue(all(not row['rewards'] for row in result['rows'] if row['choice_id'] in CHOICES))
                text = node_information_text(entry())
                self.assertIn('补充奖励资料暂时无法核对', text)
                self.assertIn('清理门上的人形藤蔓', text)
                self.assertNotIn('具名奖励（零件）：笼控器', text)
                evidence = event_details_text(EVENT)
                self.assertIn('补充奖励来源未通过核对', evidence)
                self.assertIn('清理门上的人形藤蔓', evidence)
        self.assertEqual(catalog.event_reward_options(EVENT)['supplemental_reward_reference']['status'], 'documented_reference')

    def test_all_other_events_and_target_nonreward_fields_match_previous_query(self):
        previous = legacy_catalog()
        for event in catalog._data()['events']:
            old = previous.event_reward_options(event['id'])
            current = catalog.event_reward_options(event['id'])
            if event['id'] != EVENT:
                self.assertEqual(current, old, event['id'])
                continue
            current.pop('supplemental_reward_reference')
            old_rows = {row['choice_id']: row for row in old['rows']}
            for row in current['rows']:
                if row['choice_id'] in CHOICES:
                    self.assertEqual(len(row['rewards']), 1)
                    self.assertFalse(old_rows[row['choice_id']]['rewards'])
                    row['rewards'] = []
                    row['named_reward_found'] = False
            self.assertEqual(current, old)

    def test_two_existing_rewards_reach_the_exact_options_without_claiming_origin(self):
        result = catalog.event_reward_options(EVENT)
        rows = {row['choice_id']: row for row in result['rows']}
        for choice, original in zip(CHOICES, ('choice_ro6_normal1_1', 'choice_ro6_normal1_2')):
            reference = rows[choice]['rewards'][0]
            self.assertEqual(reference['choice_id'], original)
            self.assertEqual(reference['reward'], _reference()['event_rewards'][original]['reward'])
            self.assertEqual(reference['reward']['type'], 'SCRAP')
            self.assertEqual(reference['reward']['item_id'], 'rogue_6_scrap_G_12')
            self.assertIsNone(reference['reward']['quantity'])
            self.assertTrue(reference['content_link_verified'])
            self.assertFalse(reference['source_scene_link_verified'])
            self.assertIsNone(reference['actual_reward'])
            self.assertIsNone(rows[choice]['actual_claim_eligible'])
            self.assertFalse(rows[choice]['full_reward_pool_known'])
        source_choices = {c['key']: c for c in catalog._scene(EVENT, SCENE)['choices']}
        self.assertTrue(all(source_choices[key]['game_choice_ids'] == [] for key in CHOICES))
        self.assertFalse(result['inventory_updated'])

    def test_unknown_insufficient_exact_and_excess_budget_do_not_remove_rewards(self):
        for resources in ({}, {'hp': 1, 'gold': 7}, {'hp': 2, 'gold': 8}, {'hp': 3, 'gold': 9}):
            context = {'resources': resources}
            before = deepcopy(context)
            result = event_planning.choice_resources(EVENT, SCENE, context)
            choices = {row['choice_key']: row for row in result['rows']}
            rewards = {row['choice_id']: row for row in catalog.event_reward_options(EVENT)['rows']}
            for key, resource, amount in zip(CHOICES, ('hp', 'gold'), (2, 8)):
                costs = [r for r in choices[key]['resource_references'] if r['kind'] == 'nominal_cost']
                self.assertEqual(len(costs), 1)
                self.assertEqual((costs[0]['resource'], costs[0]['quantity_reference']), (resource, amount))
                expected = resources[resource] >= amount if resource in resources else None
                self.assertIs(costs[0]['nominal_budget_covers'], expected)
                self.assertIsNone(costs[0]['actual_changed'])
                self.assertEqual(len(rewards[key]['rewards']), 1)
                self.assertIsNone(rewards[key]['actual_claim_eligible'])
            self.assertEqual(context, before)

    def test_queries_are_copies_and_do_not_change_catalog_reward_data_or_inventory(self):
        old_catalog, old_rewards = deepcopy(catalog._data()), deepcopy(_reference())
        result = catalog.event_reward_options(EVENT)
        row = next(row for row in result['rows'] if row['choice_id'] == CHOICES[0])
        row['rewards'][0]['reward']['quantity'] = 999
        row['rewards'][0]['documented_cost_reference']['quantity'] = 999
        fresh = next(row for row in catalog.event_reward_options(EVENT)['rows'] if row['choice_id'] == CHOICES[0])
        self.assertIsNone(fresh['rewards'][0]['reward']['quantity'])
        self.assertEqual(fresh['rewards'][0]['documented_cost_reference']['quantity'], 2)
        self.assertEqual(catalog._data(), old_catalog)
        self.assertEqual(_reference(), old_rewards)

    def test_player_outputs_pair_each_cost_and_named_scrap_but_never_total_them(self):
        text = node_information_text(entry(), context={'resources': {'hp': 2, 'gold': 8}})
        self.assertEqual(text.count('具名奖励（零件）：笼控器；数量未确认；实际领取未知。'), 2)
        self.assertIn('费用：2目标生命值', text)
        self.assertIn('费用：8源石锭', text)
        self.assertNotIn('rogue_6_scrap_G_12', text)
        self.assertNotIn('https://', text)
        self.assertIn('完整奖励池、实际领取及本局变化未知', text)
        evidence = event_details_text(EVENT, {'resources': {'hp': 2, 'gold': 8}})
        self.assertIn('完整选项文字和物品指针相符', evidence)
        self.assertIn('不证明原入口脚本', evidence)
        self.assertIn('349818', evidence)

    def test_historical_reference_keeps_rewards_without_borrowing_current_budget(self):
        text = node_information_text(entry(history_read=True), context={'resources': {'hp': 999, 'gold': 999}})
        self.assertEqual(text.count('具名奖励（零件）：笼控器；数量未确认；实际领取未知。'), 2)
        self.assertIn('历史', text)
        self.assertIn('能否付清这项费用：未知', text)
        self.assertNotIn('已知资源够付这项费用', text)


class EventRewardView289Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qt = QApplication.instance() or QApplication([])

    def test_two_reading_pages_preserve_selection_and_real_scroll_after_refresh(self):
        panel = NodeCatalogPanel()
        self.addCleanup(panel.close)
        panel.resize(1050, 680)
        panel.show()
        panel.set_map_context(None, runtime_context={'resources': {'hp': 2, 'gold': 8}})
        panel.list.setCurrentRow(next(i for i, e in enumerate(panel.entries)
                                     if e['kind'] == 'event' and e['record']['id'] == EVENT))
        for widget in (panel.player_detail, panel.detail):
            panel.reading_tabs.setCurrentWidget(widget)
            self.qt.processEvents()
            self.assertIn('笼控器', widget.toPlainText())
            cursor = widget.textCursor()
            cursor.setPosition(3)
            cursor.setPosition(14, QTextCursor.MoveMode.KeepAnchor)
            widget.setTextCursor(cursor)
            bar = widget.verticalScrollBar()
            self.assertGreater(bar.maximum(), 0)
            bar.setValue(max(1, bar.maximum() // 2))
            old = (panel.detail_key, widget.toPlainText(), cursor.selectedText(), bar.value())
            panel.refresh()
            self.qt.processEvents()
            self.assertIs(panel.reading_tabs.currentWidget(), widget)
            self.assertEqual((panel.detail_key, widget.toPlainText(), widget.textCursor().selectedText(), bar.value()), old)


if __name__ == '__main__':
    unittest.main()
