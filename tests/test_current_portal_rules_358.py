"""Source identity, six fogs/nine rules, refresh exceptions and original links."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from rouge import current_portal_rules as model


class CurrentPortalRules358Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = model.reference()
        if cls.result is None: raise AssertionError('Installed source package is required, not skipped.')

    def test_all_nine_exact_rules_six_fogs_nineteen_zones_and_three_tables(self):
        d = self.result['data']; current = model.version.packet()['current']['details']
        self.assertEqual(len(d['rules']), 9); self.assertEqual(len(d['fogs']), 6)
        self.assertEqual(len(d['original_enter_scenes']), 19)
        self.assertEqual(len(d['original_portal_zones']), 19)
        self.assertEqual(len(d['original_roll_node_data']), 3)
        for key, row in d['rules'].items():
            self.assertEqual(row['original'], current['variationData'][key])
            self.assertEqual(row['documentation']['title'], row['name'])
            self.assertEqual(row['documentation']['complete_table_DOM']['tag'], 'table')
        self.assertEqual(d['original_roll_node_data'], current['rollNodeData'])
        for row in d['original_roll_node_data'].values():
            self.assertEqual(list(row['groups']), ['INCIDENT', 'BATTLE_NORMAL', 'BATTLE_ELITE', 'BATTLE_SHOP', 'WISH'])
            self.assertTrue(all(set(x) == {'nodeType'} for x in row['groups'].values()))

    def test_red_fog_preserves_four_candidates_and_never_decodes_a_scene_suffix(self):
        rows = model.rows(self.result, '红雾')
        self.assertEqual([r['id'] for r in rows], ['variation_1', 'variation_2', 'variation_3', 'variation_4'])
        originals = self.result['data']['original_enter_scenes']
        for key, row in originals.items():
            target = model.locate('scenes', key)
            self.assertEqual(target['fog'], row['fog'])
            self.assertIsNone(target['rule_id'])
            self.assertIsNone(target['zone_id'])
        self.assertIn('四种候选之一', model.player_text(self.result, fog='红雾'))
        self.assertEqual(model.rows(self.result, 'not-a-fog'), [])

    def test_same_named_zone_never_infers_fog_rule_or_main_floor(self):
        for key in self.result['data']['original_portal_zones']:
            target = model.locate('regions', key)
            self.assertEqual(target['zone_id'], key)
            self.assertEqual(target['branch'], 'refresh')
            self.assertIsNone(target['fog']); self.assertIsNone(target['rule_id'])
            text = model.refresh_table_text(self.result, key)
            if key not in self.result['data']['original_roll_node_data']:
                self.assertIn('未列独立刷新表', text)
            else:
                self.assertIn('不期而遇', text); self.assertIn('具体事件', text)
                self.assertIn('不是所有乌托邦的通用节点池', text)

    def test_floor_restrictions_are_documentary_partial_conditions(self):
        rules = self.result['data']['rules']
        for key, allowed in [('variation_7', [4, 5]), ('variation_8', [4, 5]), ('variation_9', [3])]:
            for floor in range(1, 6):
                condition = model.listed_floor_condition(rules[key], floor)
                self.assertEqual(condition['matches_listed_floor'], floor in allowed)
                self.assertIsNone(condition['actual_server_eligible'])
            self.assertIsNone(model.listed_floor_condition(rules[key])['matches_listed_floor'])
        self.assertIsNone(model.listed_floor_condition(rules['variation_1'], 3)['matches_listed_floor'])
        for value in [True, False, 0, 6, -1, 3.0, '3']:
            self.assertIsNone(model.listed_floor_condition(rules['variation_9'], value))

    def test_completed_shop_exception_and_passed_nodes_are_distinct(self):
        r = model.refresh_condition(self.result, 'BATTLE_SHOP', moved=True, passed=False, completed_shop=True)
        self.assertEqual(r['status'], 'documented_completed_shop_exception')
        self.assertIsNone(r['actual_will_refresh']); self.assertFalse(r['nodes_changed'])
        passed = model.refresh_condition(self.result, 'BATTLE_NORMAL', moved=True, passed=True)
        self.assertEqual(passed['status'], 'outside_unpassed_wording')
        match = model.refresh_condition(self.result, 'BATTLE_SHOP', moved=True, passed=False, completed_shop=False)
        self.assertEqual(match['status'], 'matches_listed_conditions_only')
        self.assertIsNone(match['actual_event_after'])
        self.assertFalse(match['complete_refresh_type_scope_verified'])

    def test_refresh_unknown_missing_and_nonboolean_declarations_never_become_actual_results(self):
        self.assertEqual(model.refresh_condition(self.result, 'BATTLE_SHOP', moved=True, passed=False)['status'], 'unknown')
        self.assertEqual(model.refresh_condition(self.result)['status'], 'unknown')
        self.assertEqual(model.refresh_condition(self.result, 'BATTLE_NORMAL', moved=False, passed=False)['status'], 'movement_trigger_not_declared')
        for value in [0, 1, 'true', [], {}]:
            self.assertIsNone(model.refresh_condition(self.result, 'BATTLE_NORMAL', moved=value))
        self.assertIsNone(model.refresh_condition(self.result, 'not-a-node', moved=True))
        self.assertIsNone(model.refresh_condition(self.result, 'BATTLE_NORMAL', completed_shop=True))

    def test_consumption_original_and_community_disambiguation_remain_separate(self):
        row = self.result['data']['rules']['variation_8']
        self.assertEqual(row['original']['functionDesc'], '每名干员仅可在一场狭路相逢中出战')
        self.assertIn('获胜的', row['documentation']['visible_text'])
        self.assertIn('正式', row['documentation']['visible_text'])
        text = model.player_text(self.result, 'variation_8')
        self.assertIn('社区', text); self.assertIn('原文有歧义', text)
        self.assertIn('未获胜', text)
        self.assertFalse(row['calculation_applied'])

    def test_accurate_node_marker_and_fog_links_without_invented_relics(self):
        rows = model.links(self.result, 'variation_6')
        marker = next(row for row in rows if row['kind'] == 'item')
        self.assertEqual(marker['key'], 'rogue_6_bubble_01')
        self.assertEqual(self.result['data']['original_items'][marker['key']]['type'], 'NODE_BUOY')
        self.assertIn('原标志', marker['label'])
        self.assertEqual(model.locate('items', marker['key'])['rule_id'], 'variation_6')
        self.assertIsNone(model.locate('relics', 'rogue_6_relic_final_4'))
        self.assertTrue(any(row['kind'] == 'node_type' and row['key'] == 'BATTLE_SHOP'
                            for row in model.links(self.result, 'variation_5')))

    def test_fresh_link_rejects_foreign_or_mutated_snapshot(self):
        request = model.links(self.result, 'variation_6')[-1]
        with patch.object(model, 'packet', return_value=deepcopy(self.result)):
            valid = model.resolve_link(self.result, request, rule_id='variation_6')
            self.assertEqual(valid['original']['id'], 'rogue_6_bubble_01')
            self.assertIsNone(valid['actual_held']); self.assertFalse(valid['run_updated'])
            self.assertIsNone(model.resolve_link(self.result, request, rule_id='variation_9'))
            changed = deepcopy(self.result); changed['actual_rewards'] = []
            self.assertIsNone(model.resolve_link(changed, request, rule_id='variation_6'))

    def test_bad_own_source_is_unavailable_without_modifying_project_files(self):
        original_file = model.version._file
        with tempfile.TemporaryDirectory() as folder:
            invalid = Path(folder) / 'manifest.json'; invalid.write_bytes(b'{}')
            with patch.object(model.version, '_file', side_effect=lambda name: invalid if name == model.MANIFEST else original_file(name)):
                self.assertIsNone(model.packet()); self.assertIsNone(model.locate('variations', 'variation_1'))
        self.assertIsNotNone(model.packet())

    def test_current_original_field_drift_is_rejected(self):
        current = model.version.packet()
        changed = deepcopy(current)
        changed['current']['details']['variationData']['variation_8']['functionDesc'] = 'a different rule'
        with patch.object(model.version, 'packet', return_value=changed): self.assertIsNone(model.packet())


if __name__ == '__main__': unittest.main()
