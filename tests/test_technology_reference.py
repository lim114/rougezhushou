from collections import Counter
import unittest
from rouge.damage import calculate_damage
from rouge.technology import format_technology, technology_gates, technology_labels, technology_node, technology_nodes


class TechnologyReferenceTests(unittest.TestCase):
    def test_pinned_catalog_keeps_all_node_types(self):
        nodes = technology_nodes()
        self.assertEqual(len(nodes), 57)
        self.assertEqual(len({n['buffId'] for n in nodes}), 57)
        self.assertEqual(Counter(n['nodeType'] for n in nodes),
                         {'NORMAL': 33, 'KEY': 21, 'DIFFICULTY': 3})

    def test_display_edges_and_gate_mapping_have_no_missing_ids(self):
        ids = {n['buffId'] for n in technology_nodes()}
        for node in technology_nodes():
            self.assertTrue(set(node['frontNodeId']+node['nextNodeId']) <= ids)
        for key, gate in technology_gates().items():
            self.assertIn(key, ids)
            for edge in gate['nodeMap']:
                self.assertTrue(set(edge['frontNodes']+[edge['nextNode']]) <= ids)

    def test_raw_grade_gates_and_key_effect_text_are_preserved(self):
        self.assertEqual([g['enableGrade'] for g in technology_gates().values()], [3, 6, 9])
        for number, grade in enumerate((3, 6, 9), 1):
            text = format_technology(f'rogue_6_difficulty_{number}')
            self.assertIn(f'<保密等级{grade}>及以上难度进行探索时生效', text)
        self.assertEqual(technology_node('rogue_6_outbuff_7')['rawDesc'],
                         ['探险中会出现“误入奇境”节点'])

    def test_duplicate_names_remain_separate_and_searchable(self):
        nodes = technology_nodes('颊囊')
        self.assertEqual({n['buffId'] for n in nodes}, {'rogue_6_outbuff_25', 'rogue_6_outbuff_35'})
        labels = technology_labels()
        self.assertNotEqual(labels['rogue_6_outbuff_25'], labels['rogue_6_outbuff_35'])

    def test_search_matches_effect_text_and_no_match_is_empty(self):
        self.assertTrue(any(n['buffId']=='rogue_6_outbuff_1' for n in technology_nodes('初始护盾值')))
        self.assertEqual(technology_nodes('不存在的科技xyz'), [])

    def test_returned_records_cannot_modify_cached_source(self):
        nodes = technology_nodes(); nodes[0]['rawDesc'].append('changed')
        gate = technology_gates(); gate['rogue_6_difficulty_1']['enableGrade'] = 99
        self.assertNotIn('changed', technology_node('rogue_6_outbuff_1')['rawDesc'])
        self.assertEqual(technology_gates()['rogue_6_difficulty_1']['enableGrade'], 3)
        with self.assertRaises(ValueError): technology_node('unknown')

    def test_reference_does_not_apply_account_effects_or_infer_unlock_logic(self):
        args = {'operator': 'mechanist', 'skill': 1, 'base_attack': 1000}
        before = calculate_damage(args)
        for node in technology_nodes():
            text = format_technology(node['buffId'])
            self.assertIn('账户解锁状态：未知', text)
            self.assertIn('未将效果加入本局计算', text)
            self.assertIn('解锁判定仍待核验', text)
            self.assertNotIn('原件SHA256', text)
        self.assertEqual(calculate_damage(args), before)
        self.assertIn('原件SHA256', format_technology('rogue_6_outbuff_1', technical=True))


if __name__ == '__main__': unittest.main()
