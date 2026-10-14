"""Public presentation checks; no capture, game interaction or persisted state."""
import copy
import unittest
from unittest.mock import patch

from rouge.map_reporting import format_map, format_node, format_rewards
from rouge.operator_summary import format_operator_observation


def graph():
    return {
        'status': 'matched', 'zone_id': 'zone_1', 'template_id': '1a',
        'grid': {'rows': 3, 'cols': 5}, 'current_node': '1,1',
        'nodes': [
            {'id': '0,2', 'row': 0, 'col': 2, 'distance': 2, 'visible': True,
             'observed_type': '作战', 'remembered_type': '作战',
             'content': {'kind': 'battle', 'title': '遗忘时间', 'variant_id': 'ro6_n_1_2'},
             'prediction': {'candidates': ['作战'], 'evidence': 'visible_history'}},
            {'id': '1,1', 'row': 1, 'col': 1, 'distance': 0, 'visible': True,
             'observed_type': '林间空地', 'template_type': '起点'},
            {'id': '2,3', 'row': 2, 'col': 3, 'distance': 3, 'visible': False,
             'observed_type': None,
             'prediction': {'candidates': ['作战', '紧急作战'], 'evidence': 'community_constraints',
                            'probability': None}},
        ],
        'edges': [['1,1', '0,2'], ['0,2', '2,3']],
        'source': {'url': 'https://arkrog.com/tool/blackflowmap'},
        'generation_budget': {'作战': {'fixed': 1, 'revealed_additional': 1, 'source_max': None,
                                  'known_total': 2, 'random_eligible': True}},
    }


class ReadableMapTests(unittest.TestCase):
    def test_map_shows_source_zone_name_and_human_position(self):
        g = graph()
        text = format_map(g, g)
        self.assertIn('区域：玻利瓦尔肤层', text)
        self.assertIn('当前节点：中排 · 第2列', text)
        self.assertIn('上排 · 第3列', text)
        self.assertNotIn('zone_1', text)
        self.assertNotIn('0,2', text)
        self.assertNotIn('https://', text)
        for title in ('地图概况', '节点列表', '资料依据与限制', '生成数量约束'):
            self.assertIn('【'+title+'】', text)

    def test_technical_map_keeps_ids_and_source(self):
        g = graph()
        text = format_map(g, g, technical=True)
        self.assertIn('区域引用：zone_1', text)
        self.assertIn('节点引用：0,2 → 上排 · 第3列', text)
        self.assertIn('https://arkrog.com/tool/blackflowmap', text)

    def test_unknown_zone_does_not_guess_from_a_prefix(self):
        g = graph()
        g['zone_id'] = 'zone_1_unverified'
        text = format_map(g, g)
        self.assertIn('区域名称未确认', text)
        self.assertNotIn('玻利瓦尔肤层', text)
        self.assertNotIn('zone_1_unverified', text)

    def test_historical_marker_is_explicit_and_uses_position(self):
        g = graph()
        g['current_node'] = None
        g['last_confirmed_current_node'] = '1,1'
        text = format_map({'reason': '本帧布局未确认'}, g)
        self.assertIn('历史参考', text)
        self.assertIn('最近确认位置：中排 · 第2列（历史', text)
        self.assertIn('当前节点：位置未确认', text)
        self.assertNotIn('当前节点：中排', text)

    def test_unknown_frame_enum_and_candidate_ids_stay_out_of_normal_text(self):
        g = graph()
        self.assertNotIn('insufficient', format_map({'status': 'insufficient'}, g))
        current = {'status': 'insufficient', 'candidate_templates': [{'id': '1a'}, {'id': '1b'}]}
        text = format_map(current, None)
        self.assertIn('布局候选：2种', text)
        self.assertNotIn('1a', text)
        self.assertIn('布局引用：1a、1b', format_map(current, None, technical=True))

    def test_constraints_remain_candidates_without_probabilities(self):
        g = graph()
        text = format_node(g, '2,3')
        self.assertIn('社区约束候选：作战 / 紧急作战', text)
        self.assertIn('候选没有统计概率', text)
        self.assertIn('来源总上限未知', text)
        self.assertNotIn('50%', text)
        self.assertIn('不是从当前位置出发', text)

    def test_confirmed_variant_uses_game_difficulty_name(self):
        g = graph()
        text = format_node(g, '0,2')
        self.assertIn('关卡变体：普通作战', text)
        self.assertIn('宝箱生成候选', text)
        self.assertIn('概率未核验', text)
        self.assertNotIn('ro6_n_1_2', text)
        self.assertNotIn('NORMAL', text)
        g['nodes'][0]['content']['variant_id'] = 'ro6_e_1_2'
        self.assertIn('关卡变体：紧急作战', format_node(g, '0,2'))

    def test_wrong_title_does_not_borrow_an_id_difficulty(self):
        g = graph()
        g['nodes'][0]['content']['title'] = '身份未确认'
        text = format_node(g, '0,2')
        self.assertIn('关卡变体：未唯一确认', text)
        self.assertNotIn('关卡变体：普通作战', text)

    def test_node_state_and_original_ids_are_available_without_mutation(self):
        g = graph()
        before = copy.deepcopy(g)
        text = format_node(g, '0,2', technical=True)
        self.assertIn('节点引用：0,2', text)
        self.assertIn('关卡引用：ro6_n_1_2', text)
        self.assertIn('本局已揭示记录：作战', text)
        self.assertEqual(g, before)
        self.assertEqual(format_node(g, 'missing'), '')

    def test_conflicts_do_not_expose_raw_references_in_normal_report(self):
        g = graph()
        g['constraint_conflicts'] = ['zone_1:template_raw_constraint']
        text = format_map(g, g)
        self.assertIn('暂停其他隐藏节点候选筛选', text)
        self.assertNotIn('template_raw_constraint', text)
        self.assertIn('冲突引用：zone_1:template_raw_constraint', format_map(g, g, technical=True))

    def test_unknown_spawn_name_does_not_turn_into_raw_id_or_zero_objects(self):
        preview = {
            'status': 'partial_reference', 'event_options': [], 'unresolved_pools': [],
            'variant_candidates': ['stage_reference'],
            'battle_variants': [{'difficulty': 'NORMAL', 'name': '测试关卡',
                'battle_chest_groups': [{'candidates': [{'entity_id': 'unknown_enemy_ref'}]}],
                'rare_enemy_groups': [{'candidates': [{'name': '空分支1'}]}],
                'level_evidence': {'url': 'https://example.org/pinned-source'}}],
        }
        before = copy.deepcopy(preview)
        with patch('rouge.map_reporting.preview_node_rewards', return_value=preview):
            text = format_rewards({'title': '测试关卡'})
            self.assertIn('宝箱生成候选组1：名称未确认的对象', text)
            self.assertIn('特殊敌人生成候选组1：不生成对象', text)
            self.assertNotIn('unknown_enemy_ref', text)
            self.assertNotIn('https://', text)
            technical = format_rewards({'title': '测试关卡'}, technical=True)
            self.assertIn('生成对象引用：unknown_enemy_ref', technical)
            self.assertIn('https://example.org/pinned-source', technical)
        self.assertEqual(preview, before)

    def test_formatters_do_not_update_graph_or_rewards(self):
        g = graph()
        before = copy.deepcopy(g)
        format_map(g, g)
        format_map({'reason': '暂时不可见'}, g, technical=True)
        format_node(g, '0,2')
        format_rewards(g['nodes'][0]['content'])
        self.assertEqual(g, before)
        self.assertEqual(format_rewards(None), '')


def operator():
    return {'id': 'mechanist', 'scope': 'run',
            'fields': {'elite': 2, 'level': 90, 'potential': 6, 'trust': 100,
                       'module_id': None, 'module_level': 0, 'selected_skill': 3},
            'skill_ranks': {'1': 7, '2': 8, '3': 10}}


class ReadableOperatorTests(unittest.TestCase):
    def test_selected_skill_and_all_skill_numbers_are_chinese(self):
        text = format_operator_observation(operator())
        self.assertIn('所选技能：第3技能 · 工程学十字星', text)
        self.assertIn('第2技能', text)
        self.assertIn('等级 7 · 专精 1', text)
        self.assertIn('等级 7 · 专精 3', text)
        self.assertNotIn('S3', text)
        self.assertIn('【培养信息】', text)
        self.assertIn('【技能信息】', text)

    def test_unknown_module_reference_is_technical_only(self):
        o = operator()
        o['fields']['module_id'] = 'uniequip_unknown_future'
        o['fields']['module_level'] = 2
        text = format_operator_observation(o)
        self.assertIn('名称未确认的装备模组 · 阶段 2', text)
        self.assertNotIn('uniequip_unknown_future', text)
        self.assertIn('模组引用：uniequip_unknown_future', format_operator_observation(o, technical=True))

    def test_invalid_selected_skill_keeps_unknown(self):
        o = operator()
        o['fields']['selected_skill'] = 9
        self.assertIn('所选技能：未确认', format_operator_observation(o))
        o['fields']['selected_skill'] = True
        self.assertIn('所选技能：未确认', format_operator_observation(o))
        o['fields']['selected_skill'] = 3
        o['invalid_fields'] = ['selected_skill']
        self.assertIn('所选技能：未确认', format_operator_observation(o))

    def test_missing_fields_use_chinese_and_keep_same_run_history(self):
        o = operator()
        o['missing_fields'] = ['skill_rank_3', 'module_id', 'unknown_future_field']
        o['merged_from_pages'] = ['training_page']
        text = format_operator_observation(o)
        self.assertIn('第3技能等级、装备模组、未确认的档案字段', text)
        self.assertNotIn('skill_rank_3', text)
        self.assertNotIn('unknown_future_field', text)
        self.assertIn('此前读取的同一干员档案', text)
        self.assertIn('暂时不可见的字段继续保留', text)
        self.assertIn('未读取字段引用：skill_rank_3', format_operator_observation(o, technical=True))

    def test_observation_report_preserves_training_and_excludes_white_values(self):
        o = operator()
        before = copy.deepcopy(o)
        text = format_operator_observation(o)
        self.assertIn('等级：90', text)
        self.assertIn('潜能：6', text)
        self.assertNotIn('攻击力：', text)
        self.assertNotIn('生命值：', text)
        self.assertNotIn('白值', text)
        self.assertEqual(o, before)

    def test_no_skill_operator_does_not_show_phantom_skill(self):
        o = {'id': 'char_285_medic2', 'fields': {'selected_skill': 1}}
        text = format_operator_observation(o)
        self.assertIn('所选技能：无技能', text)
        self.assertNotIn('第1技能', text)


if __name__ == '__main__':
    unittest.main()
