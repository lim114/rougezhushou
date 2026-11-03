from collections import Counter
from copy import deepcopy
import importlib.util
from pathlib import Path
import runpy
import sys
import unittest
from unittest.mock import patch


ROOT = next(path for path in Path(__file__).resolve().parents if (path / 'rouge/__init__.py').is_file())
WORK = Path(__file__).resolve().parent
if (WORK / 'movement_source_planning.py').is_file():
    specification = importlib.util.spec_from_file_location('rouge.movement_source_planning', WORK / 'movement_source_planning.py')
    sources = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = sources
    specification.loader.exec_module(sources)
    sources.DATA = WORK / 'data'
    BUILDER = WORK / 'build_movement_source_reference.py'
    RESEARCH = WORK
else:
    from rouge import movement_source_planning as sources
    BUILDER = ROOT / 'scripts/build_movement_source_reference.py'
    RESEARCH = ROOT / 'research/p3-event-continuation/movement-sources'


M01 = 'rogue_6_scrap_M_01'
M04 = 'rogue_6_scrap_M_04'
M07 = 'rogue_6_scrap_M_07'
M08 = 'rogue_6_scrap_M_08'
M11 = 'rogue_6_scrap_M_11'
CHANNELS = {'battle_shop', 'scrap_shop', 'seed', 'final_exit', 'path_exit', 'boss_clear'}


def checks(row):
    return {check['kind']: check['matches'] for check in row['checks']}


def graph_node(key, row, col, observed=None, **fields):
    return {'id': key, 'row': row, 'col': col, 'observed_type': observed, **fields}


class MovementSourceTests(unittest.TestCase):
    def test_frozen_builder_reproduces_complete_twelve_items_and_six_channels(self):
        data = sources.reference_data()
        rebuilt = runpy.run_path(str(BUILDER))['build'](ROOT, RESEARCH)
        self.assertEqual(rebuilt, data)
        self.assertEqual(set(data['items']), {'rogue_6_scrap_M_' + str(i).zfill(2) for i in range(1, 13)})
        self.assertEqual(set(data['channels']), CHANNELS)
        self.assertEqual(data['coverage']['literal_channel_kinds'], 6)
        self.assertFalse(data['coverage']['source_origin_gap_closed'])
        self.assertTrue(all(item['kind'] == 'MOVE' and item['item']['type'] == 'SCRAP' for item in data['items'].values()))

    def test_literal_card_flags_are_documentary_and_cannot_become_game_flags_or_complete_pools(self):
        data = sources.reference_data()
        for flag, quantity in (('bossdrop', 5), ('pathdrop', 5), ('seedreward', 7), ('nosell', 2)):
            self.assertEqual(sum(item['documented_source_flags'][flag] for item in data['items'].values()), quantity)
        for item in data['items'].values():
            self.assertFalse(item['source_flags_are_game_data_flags'])
            self.assertEqual(len(item['source_card_sha256']), 64)
            self.assertEqual(item['original_base_sell_price'], 1)
        row = sources.movement_source(M01, 'final_exit', {'node_type': '险路尽头'},
            {'access_declared': True, 'transition_completed': True})
        self.assertEqual(row['status'], 'matched')
        for key in ('actual_source_pool_member', 'actual_current_stock', 'actual_node_reachable',
                'actual_reward_quantity', 'actual_received', 'actual_server_eligible', 'generation_probability'):
            self.assertIsNone(row[key])
        self.assertFalse(row['complete_server_reward_pool_known'])
        self.assertFalse(row['source_origin_scene_verified'])
        self.assertFalse(row['inventory_updated'])

    def test_both_shop_scopes_have_ten_documented_prices_and_two_explicit_exclusions(self):
        data = sources.reference_data()
        priced = [item for item in data['items'].values() if item['documented_card_price'] is not None]
        self.assertEqual(len(priced), 10)
        self.assertTrue(all(item['documented_card_price'] > item['original_base_sell_price'] for item in priced))
        for channel in ('battle_shop', 'scrap_shop'):
            rows = [sources.movement_source(key, channel) for key in data['items']]
            self.assertEqual(Counter(row['source_membership_matches'] for row in rows), {True: 10, False: 2})
            self.assertEqual({row['name'] for row in rows if row['source_membership_matches'] is False},
                {'结构性原理', '“简易遥控器”'})
            self.assertTrue(all(row['actual_current_stock'] is None for row in rows))

    def test_budget_uses_only_independent_price_or_explicit_unmodified_card_price(self):
        context = {'node_type': '秘境行商', 'gold': 5}
        declared = {'access_declared': True, 'stock_item_ids': [M04]}
        ordinary = sources.movement_source(M04, 'scrap_shop', context, declared)
        self.assertEqual(ordinary['original_base_sell_price'], 1)
        self.assertEqual(ordinary['documented_card_price'], 6)
        self.assertIsNone(ordinary['comparison_price_reference'])
        self.assertIsNone(ordinary['nominal_budget_covers'])
        self.assertEqual(ordinary['status'], 'unknown')
        unmodified = sources.movement_source(M04, 'scrap_shop', context,
            {**declared, 'unmodified_price_scenario': True})
        self.assertEqual(unmodified['comparison_price_reference'], 6)
        self.assertFalse(unmodified['nominal_budget_covers'])
        self.assertEqual(unmodified['status'], 'excluded')
        independent = sources.movement_source(M04, 'scrap_shop', context,
            {**declared, 'declared_prices': {M04: 5}})
        self.assertEqual(independent['comparison_price_source'], 'independent_declared_price')
        self.assertTrue(independent['nominal_budget_covers'])
        self.assertEqual(independent['status'], 'matched')
        self.assertIsNone(independent['actual_price'])
        with self.assertRaises(ValueError):
            sources.movement_source(M04, 'scrap_shop', context,
                {'unmodified_price_scenario': True, 'declared_prices': {M04: 5}})

    def test_gold_unknown_fallbacks_and_explicit_zero_are_independent(self):
        declared = {'unmodified_price_scenario': True, 'gold_declared': None}
        resources = sources.movement_source(M01, 'battle_shop', {'resources': {'gold': 2}}, declared)
        self.assertEqual(resources['gold_declared'], 2)
        self.assertTrue(resources['nominal_budget_covers'])
        zero = sources.movement_source(M01, 'battle_shop', {'gold': 20}, {**declared, 'gold_declared': 0})
        self.assertEqual(zero['gold_declared'], 0)
        self.assertFalse(zero['nominal_budget_covers'])
        unknown_price = sources.movement_source(M11, 'battle_shop', {'gold': 99}, declared)
        self.assertIsNone(unknown_price['comparison_price_reference'])
        self.assertIsNone(unknown_price['nominal_budget_covers'])

    def test_shop_unread_stock_is_unknown_and_only_explicit_complete_scope_excludes_missing(self):
        cases = [({}, None), ({'stock_item_ids': [M08]}, None),
            ({'stock_item_ids': [M08], 'stock_complete': False}, None),
            ({'stock_item_ids': [M08], 'stock_complete': True}, False),
            ({'stock_item_ids': [M04]}, True), ({'stock_presence': {M04: True}}, True),
            ({'stock_presence': {M04: False}}, False),
            ({'stock_presence': {M04: None}, 'stock_item_ids': [M04]}, True)]
        for declaration, expected in cases:
            with self.subTest(declaration=declaration):
                self.assertIs(sources.movement_source(M04, 'scrap_shop', declaration=declaration)['stock_presence_declared'], expected)
        for declaration in ({'stock_presence': {M04: False}, 'stock_item_ids': [M04]},
                {'stock_presence': {M04: True}, 'stock_complete': True, 'stock_item_ids': []}):
            with self.assertRaises(ValueError):
                sources.movement_source(M04, 'scrap_shop', declaration=declaration)

    def test_seed_seven_documented_candidates_and_five_class_exclusions_do_not_become_actual_membership(self):
        rows = [sources.movement_source(key, 'seed') for key in sources.reference_data()['items']]
        self.assertEqual(Counter(row['source_membership_matches'] for row in rows), {True: 7, False: 5})
        self.assertEqual({row['name'] for row in rows if row['source_membership_matches'] is True},
            {'重弹簧', '小八界', '一次性喷气背包', '老妈妈的融雪', '坎诺特的触须', '结构性原理', '“简易遥控器”'})
        self.assertEqual({row['source_membership_reference'] for row in rows if row['source_membership_matches'] is False},
            {'seed_class_mismatch'})
        self.assertTrue(all(row['actual_source_pool_member'] is None for row in rows))
        seed_id = sources.reference_data()['seed_item_id']
        row = sources.movement_source(M07, 'seed', {'node_type': '秘境行商', 'item_presence': {seed_id: True}},
            {'access_declared': True, 'cultivation_completed': True})
        self.assertEqual(row['status'], 'matched')
        self.assertTrue(checks(row)['seed_owned'])
        self.assertNotIn('item_quantities', row['context'])
        incomplete = sources.movement_source(M07, 'seed', {'node_type': '秘境行商'},
            {'access_declared': True, 'cultivation_completed': False, 'seed_presence': True})
        self.assertEqual(incomplete['status'], 'excluded')

    def test_unlisted_exit_and_boss_flags_remain_unknown_while_quantities_are_separate(self):
        expected = {'final_exit': ('险路尽头', 'transition_completed', 1),
            'path_exit': ('险路小径', 'transition_completed', 1),
            'boss_clear': ('险路恶敌', 'victory_declared', None)}
        for channel, (label, completion, quantity) in expected.items():
            rows = [sources.movement_source(key, channel, {'node_type': label},
                {'access_declared': True, completion: True}) for key in sources.reference_data()['items']]
            with self.subTest(channel=channel):
                self.assertEqual(Counter(row['source_membership_matches'] for row in rows), {True: 5, None: 7})
                self.assertEqual(Counter(row['status'] for row in rows), {'matched': 5, 'unknown': 7})
                self.assertTrue(all(row['quantity_reference'] == quantity for row in rows))
                self.assertTrue(all(row['actual_reward_quantity'] is None for row in rows))

    def test_same_title_path_groups_preserve_three_separate_ids_and_entry_keys(self):
        row = sources.movement_source(M08, 'path_exit')
        references = row['channel']['catalogue_refs']
        self.assertEqual([ref['title'] for ref in references], ['三重身'] * 3)
        self.assertEqual({ref['event_id'] for ref in references},
            {'community_group_034', 'community_group_035', 'community_group_036'})
        self.assertEqual(len({key for ref in references for key in ref['entry_scene_keys']}), 3)
        self.assertTrue(all(ref['source_origin_scene_verified'] is False for ref in references))

    def test_declared_node_type_conflicts_fail_and_directory_context_is_retained(self):
        with self.assertRaises(ValueError):
            sources.movement_source(M04, 'seed', {'node_type': '诡意行商', 'original_node_type': 'SCRAP_SHOP'})
        with self.assertRaises(ValueError):
            sources.movement_source(M04, 'seed', {'original_node_type': 'UNKNOWN_KIND'})
        review = sources.source_review([M04], context={'node_type': '秘境行商', 'gold': 8},
            declarations_by_node={'directory:scrap_shop': {'access_declared': True,
                'stock_item_ids': [M04], 'unmodified_price_scenario': True}})
        row = next(row for row in review['rows'] if row['channel_id'] == 'scrap_shop')
        self.assertEqual(row['status'], 'matched')
        self.assertEqual(row['context']['node_type'], '秘境行商')
        self.assertIsNone(row['position'])

    def test_map_opportunities_bind_exact_positions_and_do_not_plan_paths_or_cancel_held_targets(self):
        graph = {'zone_id': 'zone-reference', 'template_id': 'template-reference', 'nodes': [
            graph_node('shop', 0, 1, '秘境行商'), graph_node('exit', 2, 3, '险路小径')]}
        context = {'item_presence': {M08: True}}
        review = sources.source_review([M08], graph, context, epoch=17)
        self.assertEqual([(row['node_id'], row['channel_id']) for row in review['rows']],
            [('shop', 'scrap_shop'), ('shop', 'seed'), ('exit', 'path_exit')])
        for row in review['rows']:
            node = next(node for node in graph['nodes'] if node['id'] == row['node_id'])
            self.assertEqual(row['position'], {'node_id': node['id'], 'row': node['row'], 'col': node['col'],
                'zone_id': 'zone-reference', 'template_id': 'template-reference', 'epoch': 17})
        target = review['targets'][0]
        self.assertTrue(target['owned_presence_declared'])
        self.assertIsNone(target['owned_quantity_declared'])
        self.assertTrue(target['current_holdings_do_not_cancel_target'])
        self.assertEqual(review['target_item_ids'], [M08])
        self.assertFalse(review['actual_node_reachability_known'])
        self.assertIsNone(review['actual_route_selected'])
        self.assertIsNone(review['actual_reward_total'])
        self.assertFalse(review['source_totals_known'])
        self.assertFalse(review['source_origin_gap_closed'])
        self.assertFalse(review['run_state_updated'])

    def test_unknown_current_nodes_keep_all_six_while_raw_types_remain_declared_only(self):
        graph = {'nodes': [graph_node('unknown', 0, 0),
            graph_node('raw', 0, 1, base_node_type='SCRAP_SHOP')]}
        review = sources.source_review([M04], graph)
        unknown = [row for row in review['rows'] if row['node_id'] == 'unknown']
        self.assertEqual({row['channel_id'] for row in unknown}, CHANNELS)
        self.assertTrue(all(checks(row)['node_type'] is None for row in unknown))
        raw = [row for row in review['rows'] if row['node_id'] == 'raw']
        self.assertEqual({row['channel_id'] for row in raw}, {'scrap_shop', 'seed'})
        self.assertTrue(all(row['identity_basis'] == 'declared_original_type_only' for row in raw))
        self.assertTrue(all(row['actual_node_reachable'] is None for row in raw))
        self.assertIn('当前读取未证', sources.source_text(raw[0]))

    def test_known_current_clearing_overrides_old_shop_and_historical_rows_borrow_no_current_declarations(self):
        seed_id = sources.reference_data()['seed_item_id']
        declaration = {'access_declared': True, 'stock_item_ids': [M04], 'stock_complete': True,
            'unmodified_price_scenario': True, 'cultivation_completed': True, 'seed_presence': True, 'gold_declared': 99}
        graph = {'nodes': [graph_node('old-shop', 1, 2, '林间空地', remembered_type='秘境行商',
            base_node_type='SCRAP_SHOP', acquisition_declaration=declaration)]}
        context = {'gold': 99, 'resources': {'gold': 99}, 'floor': 3, 'item_quantities': {seed_id: 8, M04: 2}}
        review = sources.source_review([M04], graph, context, {'old-shop': declaration})
        self.assertEqual(len(review['rows']), 2)
        for row in review['rows']:
            self.assertTrue(row['historical_reference'])
            self.assertEqual(row['status'], 'history_only')
            self.assertEqual(row['declaration'], {})
            self.assertIsNone(row['gold_declared'])
            self.assertIsNone(row['stock_presence_declared'])
            self.assertIsNone(row['comparison_price_reference'])
            self.assertIsNone(row['nominal_budget_covers'])
            self.assertNotIn('item_quantities', row['context'])
            self.assertNotIn('resources', row['context'])
            self.assertEqual(row['context']['floor'], 3)
        seed_row = next(row for row in review['rows'] if row['channel_id'] == 'seed')
        self.assertIsNone(checks(seed_row)['seed_owned'])
        self.assertIsNone(checks(seed_row)['cultivation_completed'])

    def test_graph_identity_invalid_coordinates_and_foreign_declarations_fail_without_guessing(self):
        invalid_graphs = [
            {'nodes': [graph_node('same', 0, 0), graph_node('same', 0, 1)]},
            {'nodes': [graph_node('a', 0, 0), graph_node('b', 0, 0)]},
            {'nodes': [graph_node('a', True, 0)]},
            {'nodes': [graph_node('a', -1, 0)]},
            {'nodes': [graph_node('a', 0, 0, base_node_type='SCRAP_SHOP', node_type_raw='BATTLE_SHOP')]},
            {'nodes': [graph_node('a', 0, 0, base_node_type='UNKNOWN_KIND')]},
            {'nodes': [graph_node('a', 0, 0, remembered_type=1)]}]
        for graph in invalid_graphs:
            with self.subTest(graph=graph), self.assertRaises(ValueError):
                sources.source_review([M04], graph)
        with self.assertRaises(ValueError):
            sources.source_review([M04], {'nodes': [graph_node('a', 0, 0)]}, declarations_by_node={'b': {}})
        with self.assertRaises(ValueError):
            sources.source_review([M04], declarations_by_node={'scrap_shop': {}})

    def test_invalid_ids_quantities_booleans_and_declaration_fields_do_not_coerce(self):
        for item_id in ('重弹簧', 'rogue_6_scrap_G_01', 'rogue_6_scrap_M_13', 4):
            with self.subTest(item_id=item_id), self.assertRaises(ValueError):
                sources.movement_source(item_id, 'seed')
        for declaration in ({'access_declared': 1}, {'stock_complete': 'yes'}, {'seed_presence': 1},
                {'gold_declared': True}, {'gold_declared': -1}, {'declared_prices': {M04: True}},
                {'declared_prices': {M04: -1}}, {'stock_item_ids': [M04, M04]},
                {'stock_presence': {M04: 1}}, {'actual_received': True}):
            with self.subTest(declaration=declaration), self.assertRaises(ValueError):
                sources.movement_source(M04, 'seed', declaration=declaration)
        for target_ids in ([M04, M04], ['重弹簧'], 'rogue_6_scrap_M_04'):
            with self.assertRaises(ValueError):
                sources.source_review(target_ids)
        with self.assertRaises(ValueError):
            sources.source_review([M04], context={'item_quantities': {M04: True}})
        with self.assertRaises(ValueError):
            sources.source_review([M04], context={'item_quantities': {M04: 0}, 'item_presence': {M04: True}})

    def test_inputs_and_returned_rows_are_isolated_from_reference_and_no_inventory_is_changed(self):
        context = {'gold': 8, 'item_quantities': {M04: 1}}
        declaration = {'access_declared': True, 'stock_item_ids': [M04], 'unmodified_price_scenario': True}
        graph = {'nodes': [graph_node('shop', 0, 0, '秘境行商', acquisition_declaration=declaration)]}
        snapshots = deepcopy((context, declaration, graph))
        review = sources.source_review([M04], graph, context)
        self.assertEqual((context, declaration, graph), snapshots)
        row = next(row for row in review['rows'] if row['channel_id'] == 'scrap_shop')
        row['item']['item']['name'] = 'mutated'
        row['declaration']['stock_item_ids'].clear()
        row['context']['item_quantities'][M04] = 0
        self.assertEqual((context, declaration, graph), snapshots)
        self.assertEqual(sources.movement_source(M04, 'seed')['name'], '重弹簧')
        self.assertFalse(review['inventory_updated'])
        empty = sources.source_review([], graph, context)
        self.assertEqual(empty['rows'], [])
        self.assertEqual(empty['targets'], [])

    def test_changed_catalogue_or_part_reference_fails_until_sources_are_rebound(self):
        for key in ('catalogue_sha256', 'part_reference_sha256'):
            changed = deepcopy(sources.reference_data())
            changed[key] = '0' * 64
            with self.subTest(key=key), patch.object(sources, 'reference_data', return_value=changed), self.assertRaises(ValueError):
                sources.source_review([M04])

    def test_user_text_preserves_documentary_scope_and_technical_ids_are_optional(self):
        row = sources.movement_source(M04, 'scrap_shop', {'node_type': '秘境行商'})
        text = sources.source_text(row)
        self.assertIn('不是原游戏获取flags', text)
        self.assertIn('原基础估价：1', text)
        self.assertIn('报价未确认', text)
        self.assertIn('当前加工品陈列：未知', text)
        self.assertNotIn(M04, text)
        self.assertIn(M04, sources.source_text(row, technical=True))
        path = sources.source_text(sources.movement_source(M08, 'path_exit'), technical=True)
        for event_id in ('community_group_034', 'community_group_035', 'community_group_036'):
            self.assertIn(event_id, path)
        with self.assertRaises(ValueError):
            sources.source_text(row, technical=1)


if __name__ == '__main__':
    unittest.main()
