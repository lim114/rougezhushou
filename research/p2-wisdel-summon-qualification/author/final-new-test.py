"""Original summon-route qualification is separate from declared ghost sources."""
from copy import deepcopy
import unittest

from rouge.damage import calculate_damage
from rouge.reporting import format_report


KEY = 'wisdel_summon_qualification_reference'


def evaluate(**extra):
    return calculate_damage({'operator': 'char_1035_wisdel', 'skill': 1,
                             'skill_rank': 7, 'window_seconds': 3,
                             'ghost_count': 1, 'ghost_casts': 2, **extra})


class WisdelSummonQualificationReferenceTests(unittest.TestCase):
    def test_e0_e1_e2_original_routes_have_separate_qualification_data(self):
        for elite in (0, 1, 2):
            for potential in (1, 6):
                ref = evaluate(elite=elite, level=1, potential=potential)[KEY]
                self.assertEqual(ref['talent_route']['cultivation_qualified'], elite == 2)
                self.assertEqual(ref['skill_route']['cultivation_qualified'], elite == 2)
                self.assertEqual(ref['current_cultivation']['level'], 1)
                self.assertFalse(ref['actual_presence_verified'])
                self.assertIsNone(ref['actual_source_provenance'])

    def test_e0_e1_positive_declarations_remain_accepted_and_unplaced(self):
        for elite in (0, 1):
            result = evaluate(elite=elite)
            self.assertEqual(result['wisdel_secondary_reference']['ghost_casts_requested'], 2)
            self.assertGreater(result['wisdel_secondary_reference']['ghost_declared_count_damage_reference'], 0)
            self.assertIsNone(result['wisdel_secondary_reference']['ghost_cast_times_seconds'])
            ghost = next(c for c in result['components'] if c['name'] == '魂灵之影施放')
            self.assertEqual(ghost['hits'], 0)
            self.assertIsNone(ghost['actual_total'])
            self.assertFalse(result[KEY]['declared_counts_reinterpreted'])

    def test_only_selected_s3_binds_a_rank_specific_original_description(self):
        for skill in (1, 2, 3):
            ref = evaluate(skill=skill)[KEY]['skill_route']
            self.assertTrue(ref['cultivation_qualified'])
            self.assertEqual(ref['currently_selected'], skill == 3)
            if skill == 3:
                self.assertEqual(ref['selected_level_source']['rank'], 7)
                self.assertEqual(ref['selected_level_source']['values']['max_cnt'], 2)
            else:
                self.assertIsNone(ref['selected_level_source'])
                self.assertIn('最多存在3个', ref['original_common_fragments'][1])

    def test_route_token_keys_and_original_identity_are_separate_from_live_state(self):
        ref = evaluate()[KEY]
        self.assertEqual(ref['talent_route']['name'], '死魂灵的余息')
        self.assertEqual(ref['talent_route']['token_key'], 'token_10035_wisdel_wward')
        self.assertEqual(ref['skill_route']['override_token_key'], 'token_10035_wisdel_wward')
        self.assertFalse(ref['covers_all_routes'])
        self.assertFalse(ref['actual_cast_clock_verified'])
        self.assertEqual(ref['talent_route']['source_selector'],
                         'character_table.char_1035_wisdel.talents[1].candidates[0]')

    def test_module_and_window_declarations_do_not_rewrite_original_route_gates(self):
        for stage in range(4):
            for ghosts in (0, 3):
                result = evaluate(module_id='uniequip_002_wisdel' if stage else None,
                                  module_level=stage, ghost_count=ghosts, ghost_casts=0,
                                  window_seconds=0)
                self.assertTrue(result[KEY]['talent_route']['cultivation_qualified'])
                self.assertTrue(result[KEY]['skill_route']['cultivation_qualified'])
                self.assertEqual(result['wisdel_secondary_reference']['ghost_casts_requested'], 0)

    def test_existing_zero_window_and_active_boolean_count_errors_are_preserved(self):
        with self.assertRaisesRegex(ValueError, '零长度观察窗口不能声明魂灵施放命中'):
            evaluate(window_seconds=0)
        for field in ('ghost_count', 'ghost_casts'):
            with self.assertRaisesRegex(ValueError, field+'需要范围内的有限非负整数'):
                evaluate(**{field: True})
        result = evaluate(ghost_count=0, ghost_casts={'unused': True})
        self.assertEqual(result['wisdel_secondary_reference']['ghost_casts_requested'], 0)

    def test_report_distinguishes_cultivation_routes_from_actual_sources(self):
        text = format_report(evaluate(elite=0))
        self.assertIn('魂灵之影 · 本体召唤途径培养资料', text)
        self.assertIn('未达原表培养门槛', text)
        self.assertIn('未确定其来源归属', text)
        self.assertIn('第三技能各级原文共通部分（省略数量）', text)
        self.assertIn('本资料不涵盖模组或藏品', text)

    def test_result_reference_is_isolated_and_unrelated_owner_has_no_section(self):
        first = evaluate()
        expected = deepcopy(evaluate())
        first[KEY]['talent_route']['token_key'] = 'mutated'
        first[KEY]['skill_route']['original_common_fragments'].clear()
        self.assertEqual(evaluate(), expected)
        other = calculate_damage({'operator': 'char_328_cammou', 'skill': 1,
                                  'skill_rank': 7, 'window_seconds': 3})
        self.assertNotIn(KEY, other)
        self.assertNotIn('wisdel_summon_qualification', [s['id'] for s in other['report']['sections']])


if __name__ == '__main__':
    unittest.main()
