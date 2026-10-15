"""Public fixed-source presentation checks; no Qt, live run, capture or chat."""
from copy import deepcopy
import re
import unittest
from unittest.mock import patch

from rouge import event_planning, node_catalog
from rouge.player_node_information import node_information_text


def event_entry(title, **extra):
    record = next(row for row in node_catalog.all_events(include_indirect=True)['rows'] if row['title'] == title)
    return {'kind': 'event', 'record': record, **extra}


def context_for(entry, **extra):
    event = entry['record']
    return {'node_type': event['node_types'][0] if event['node_types'] else None,
            'floor': event['floors'][0] if event['floors'] else None, 'entry_mode': 'content', **extra}


def battle_entry(stage_id):
    record = next(row for row in node_catalog.battle_candidates(context='all')['rows'] if row['id'] == stage_id)
    return {'kind': 'battle', 'record': record}


class PlayerNodeInformationTests(unittest.TestCase):
    def test_base_settlement_and_extra_rewards_are_separate_conditional_sections(self):
        text = node_information_text(battle_entry('ro6_n_1_2'))
        self.assertLess(text.index('【战后基础奖励】'), text.index('【可能获得的额外奖励】'))
        self.assertIn('条件：主层作战、第1层；基础指挥经验：10；源石锭：1', text)
        self.assertIn('条件：秘境、第1层；基础指挥经验：10；源石锭：1', text)
        self.assertIn('不同入口的候选奖励不能相加', text)
        self.assertNotIn('源石锭：2', text)

    def test_unrelated_resources_do_not_erase_a_function_nodes_known_floor_limit(self):
        record = node_catalog.function_nodes('曲折密道', floor=1)['rows'][0]
        original = deepcopy(record)
        entry = {'kind': 'function', 'record': record}
        for context in ({'gold': 999}, {'difficulty': 3}):
            with self.subTest(context=context):
                text = node_information_text(entry, context=context)
                self.assertIn('已列层数条件：不符', text)
                self.assertEqual(record, original)

    def test_missing_entry_and_unsupported_kind_are_not_zero_or_impossible(self):
        for entry in (None, {}, {'kind': 'event'}, {'kind': 'event', 'record': None}):
            self.assertIn('资料不足不等于不可能出现', node_information_text(entry))
        self.assertIn('不能据此判断没有事件或奖励', node_information_text({'kind': 'future', 'record': {}}))

    def test_every_fixed_event_preserves_each_scene_option_and_conditional_in_source_order(self):
        for event in node_catalog.all_events(include_indirect=True)['rows']:
            with self.subTest(event=event['title'], identity=event['id']):
                text = node_information_text({'kind': 'event', 'record': event})
                self.assertNotIn('资料暂时无法整理', text)
                previous = -1
                for number, scene in enumerate(node_catalog.event_details(event['id'])['rows'], 1):
                    current = text.index(f'【场景 {number}】')
                    self.assertGreater(current, previous)
                    previous = current
                    for choice in scene['choices']:
                        self.assertIn(choice['title'], text)
                        if choice.get('conditional'):
                            self.assertIn(choice['conditional'], text)
                self.assertIn('实际领取及本局变化未知', text)

    def test_budget_three_states_are_visible_without_changing_event_eligibility(self):
        entry = event_entry('货从口出')
        for resources, expected in (({}, '能否付清这项费用：未知'), ({'gold': 3}, '已知资源不足这项费用'),
                                    ({'gold': 4}, '已知资源够付这项费用')):
            context = context_for(entry, **resources)
            original = deepcopy(context)
            before = event_planning.event_eligibility(entry['record']['id'], context)['status']
            text = node_information_text(entry, context=context)
            self.assertIn('费用：4源石锭', text)
            self.assertIn(expected, text)
            self.assertIn('不等于游戏按钮能否选择', text)
            self.assertIn('出现条件：' + {'matched': '已列条件相符', 'unknown': '条件尚未确认', 'excluded': '已列条件不符'}[before], text)
            self.assertEqual(context, original)

    def test_cage_ownership_requirement_is_not_an_item_payment(self):
        entry = event_entry('黑诞')
        for held, label in ((True, '符合'), (False, '不符'), (None, '未知')):
            text = node_information_text(entry, context=context_for(entry, item_presence={'rogue_6_scrap_G_12': held}))
            self.assertIn(f'条件核对（{label}）：仅在持有笼控器时出现', text)
            self.assertIn('不据此认定会消耗该物品', text)
            self.assertIn('具名奖励：猎印；数量未确认', text)
            self.assertNotIn('物品费用：笼控器', text)

    def test_fraction_and_minimum_retained_hp_do_not_invent_integer_payment(self):
        entry = event_entry('沉重的契约')
        text = node_information_text(entry, context=context_for(entry, resources={'hp': 5}))
        self.assertIn('按已知数量的一半为2.5', text)
        self.assertIn('整数取整方式、实际扣除量和能否付清：未知', text)
        entry = event_entry('黑诞')
        text = node_information_text(entry, context=context_for(entry, resources={'hp': 2}))
        self.assertIn('至少保留1目标生命值', text)
        self.assertIn('实际扣除量未知', text)

    def test_partial_category_inventory_does_not_falsely_report_insufficient(self):
        entry = event_entry('回滚文明')
        context = context_for(entry, item_quantities={'rogue_6_scrap_G_01': 1})
        text = node_information_text(entry, context=context)
        self.assertIn('物品费用：2件自然物', text)
        self.assertIn('相关库存尚未读全', text)
        self.assertIn('能否付清这项费用：未知', text)
        full = node_information_text(entry, context={**context, 'inventory_complete': True})
        self.assertIn('相关库存已声明完整', full)
        self.assertIn('已知资源不足这项费用', full)

    def test_relic_description_is_not_promoted_to_immediate_resource_grant(self):
        text = node_information_text(event_entry('安眠一隅'))
        first_scene = text.split('【场景 1】', 1)[1].split('【场景 2】', 1)[0]
        self.assertIn('源私钥', first_scene)
        self.assertNotIn('获得或回复：99源石锭', first_scene)
        self.assertIn('获得或回复：99源石锭', text)
        self.assertIn('获得或回复：20希望', text)
        self.assertIn('不是普通自然出现的候选', text)

    def test_version_difference_keeps_pre_entry_snapshot_separate_from_current_inventory(self):
        entry = event_entry('被歌颂的影子')
        context = context_for(entry, item_quantities={'rogue_6_relic_artifact_3': 0, 'rogue_6_relic_artifact_4': 0}, inventory_complete=True)
        unknown = node_information_text(entry, context=context)
        self.assertIn('较新文档与旧资料不同', unknown)
        self.assertIn('现在持有不能替代', unknown)
        self.assertIn('较新文档奖励：犬植浆 × 1；条件尚未确认', unknown)
        checked = node_information_text(entry, context={**context, 'pre_entry_inventory_complete': True})
        self.assertIn('较新文档奖励：犬植浆 × 1；已列条件相符', checked)
        self.assertIn('较新文档奖励：1行动力；已列条件不符', checked)

    def test_exact_choice_battle_name_and_followup_remain_available_without_raw_ids(self):
        entry = event_entry('思乡心切')
        text = node_information_text(entry, context=context_for(entry))
        self.assertIn('强行驱赶', text)
        self.assertIn('对应作战：陌生旅伴', text)
        self.assertIn('可用下方作战入口查看固定地图', text)
        self.assertIn('后续：场景', text)
        self.assertNotIn('ro6_t_1', text)
        self.assertNotIn('community_group_', text)

    def test_next_floor_pool_uses_all_fixed_names_and_does_not_fill_unknown_region(self):
        entry = event_entry('洞中宝')
        context = context_for(entry, floor=3)
        rows = event_planning.event_battle_links(entry['record']['id'], context=context)['rows']
        pool = next(row['generic_pool_requirement']['fixed_named_pool'] for row in rows if row['generic_pool_requirement'])
        text = node_information_text(entry, context=context)
        for stage in pool:
            self.assertIn(stage['title'], text)
        self.assertIn('完整候选池及实际选中关卡未知', text)
        for extra in ({'floor': None}, {'floor': 6}, {'floor': 3, 'special_region': True}):
            with self.subTest(context=extra):
                text = node_information_text(entry, context={**context, **extra})
                self.assertIn('暂没有可绑定的地图入口', text)

    def test_historical_event_never_reuses_current_gold_inventory_or_pre_entry_data(self):
        entry = event_entry('货从口出', history_read=True)
        context = context_for(entry, gold=999, resources={'gold': 999}, inventory_complete=True,
                              item_quantities={'rogue_6_scrap_G_01': 9}, pre_entry_inventory_complete=True)
        original = deepcopy(context)
        text = node_information_text(entry, context=context)
        self.assertIn('历史已读内容', text)
        self.assertIn('能否付清这项费用：未知', text)
        self.assertNotIn('已知资源够付这项费用', text)
        self.assertEqual(context, original)
        entry.pop('history_read')
        entry['record']['historical_read_reference'] = True
        self.assertEqual(node_information_text(entry, context=context), text)

    def test_same_named_groups_are_rendered_by_identity_without_merging(self):
        records = [row for row in node_catalog.all_events(include_indirect=True)['rows'] if row['title'] == '三重身']
        self.assertEqual(len(records), 3)
        rendered = [node_information_text({'kind': 'event', 'record': row}) for row in records]
        self.assertEqual(len(set(rendered)), 3)
        for row, text in zip(records, rendered):
            self.assertEqual(text.count('【场景 '), len(node_catalog.event_details(row['id'])['rows']))

    def test_function_rules_preserve_angle_bracket_game_conditions_and_no_urls(self):
        record = node_catalog.function_nodes('羽瞰点')['rows'][0]
        text = node_information_text({'kind': 'function', 'record': record})
        self.assertIn('<保密等级·3+>', text)
        self.assertIn('获得1行动力', text)
        self.assertNotIn('https://', text)
        self.assertIn('本局是否解锁、已生效或可再次使用：未知', text)
        record = node_catalog.function_nodes('曲折密道')['rows'][0]
        text = node_information_text({'kind': 'function', 'record': record}, context={'floor': 1})
        self.assertIn('已列层数条件：不符', text)

    def test_battle_reward_conditions_do_not_become_total_or_actual_rewards(self):
        text = node_information_text(battle_entry('ro6_n_1_1'))
        self.assertNotIn('资料暂时无法整理', text)
        self.assertIn('【可能获得的额外奖励】', text)
        self.assertIn('数量参考', text)
        self.assertIn('实际出现及领取总量：未知', text)
        self.assertIn('各条件奖励不能直接相加', text)
        self.assertNotRegex(text, r'(?:enemy_|trap_|ro6_[net]_)')

    def test_map_current_clearing_and_history_remain_distinct_and_immutable(self):
        node = {'id': 'a', 'row': 1, 'col': 2, 'observed_type': '林间空地',
                'remembered_type': '不期而遇', 'remembered_content': {'kind': 'event', 'title': '思乡心切'}}
        graph = {'zone_id': 'zone_1', 'template_id': 'public', 'nodes': [node]}
        context = (graph, {'floor': 1}, 'public-run', False)
        before = deepcopy(context)
        text = node_information_text({'kind': 'map', 'record': node}, map_context=context)
        self.assertIn('第2行、第3列', text)
        self.assertIn('当前类型：林间空地', text)
        self.assertIn('过去读取：思乡心切', text)
        self.assertIn('过去事件不当作现在仍可发生', text)
        self.assertIn('过去已读事件：思乡心切', text)
        self.assertIn('不自动选路', text)
        self.assertEqual(context, before)
        historical = node_information_text({'kind': 'map', 'record': node}, map_context=(*context[:3], True))
        self.assertIn('历史资料', historical)
        self.assertIn('当时类型：林间空地', historical)

    def test_unclassified_original_preserves_plain_text_and_destination_without_origin_claim(self):
        scene = node_catalog.original_references(record_type='scene')['rows'][0]
        text = node_information_text({'kind': 'original', 'record': {'record': scene}})
        self.assertIn(scene['title'], text)
        self.assertIn('尚未找到完整来源入口', text)
        choice = next(row for row in node_catalog.original_references(record_type='choice')['rows'] if row.get('nextSceneId'))
        text = node_information_text({'kind': 'original', 'record': {'record': choice}})
        self.assertIn('原文注明的后续', text)
        self.assertIn('明确后续不证明从哪里进入', text)
        self.assertNotRegex(text, r'(?:choice_ro6_|scene_ro6_|https?://|<@|"nextSceneId")')

    def test_invalid_source_is_unknown_not_a_complete_empty_event(self):
        entry = event_entry('思乡心切')
        with patch('rouge.player_node_information.event_planning.event_eligibility', side_effect=ValueError('source mismatch')):
            text = node_information_text(entry)
        self.assertIn('资料暂时无法整理', text)
        self.assertIn('条件、奖励和后续均不能据此确认', text)
        self.assertNotIn('没有事件', text)

    def test_public_summary_has_no_technical_source_fields_and_keeps_input_intact(self):
        entries = [event_entry('黑诞'), battle_entry('ro6_t_1'),
                   {'kind': 'function', 'record': node_catalog.function_nodes('羽瞰点')['rows'][0]}]
        before = deepcopy(entries)
        for entry in entries:
            text = node_information_text(entry)
            self.assertNotRegex(text, r'(?:https?://|sha256|community_group_|choice_ro6_|scene_ro6_|"raw"\s*:|\$\.details)')
            self.assertNotIn('资料暂时无法整理', text)
        self.assertEqual(entries, before)


if __name__ == '__main__':
    unittest.main()
