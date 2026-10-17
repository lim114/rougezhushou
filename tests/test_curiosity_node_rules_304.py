"""Choice-specific fixed documents; no Qt, network, live game or run writes."""
from copy import deepcopy
import importlib
import importlib.util
import inspect
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

PROJECT_ROOT = next(path for path in Path(__file__).resolve().parents if (path / 'rouge/app.py').is_file())


def load_subject():
    explicit = os.environ.get('ROUGE_CURIOSITY_NODE_RULES_MODULE')
    if explicit:
        spec = importlib.util.spec_from_file_location('rouge._candidate_curiosity304', explicit)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    return importlib.import_module('rouge.curiosity_node_rules')


class CuriosityNodeRulesTests(unittest.TestCase):
    subject = None
    IDENTITIES = (
        ('community_group_030', 'community_group_030:scene:0', 'community_group_030:scene:0:choice:0'),
        ('community_group_030', 'community_group_030:scene:0', 'community_group_030:scene:0:choice:1'),
        ('community_group_031', 'community_group_031:scene:0', 'community_group_031:scene:0:choice:0'),
        ('community_group_031', 'community_group_031:scene:0', 'community_group_031:scene:0:choice:1'),
        ('community_group_031', 'community_group_031:scene:2', 'community_group_031:scene:2:choice:0'),
    )

    @classmethod
    def setUpClass(cls):
        if cls.subject is None: cls.subject = load_subject()

    def setUp(self):
        from rouge import node_catalog
        self.catalog = node_catalog
        self.catalog._data.cache_clear()
        self.addCleanup(self.catalog._data.cache_clear)

    def row(self, index):
        result = self.subject.choice_reference(*self.IDENTITIES[index])
        self.assertTrue(result['source_valid'])
        return result['reference']

    def rules(self, index):
        return {row['rule_id']: row for row in self.row(index)['documented_rules']}

    def actual_unknown(self, value):
        expected = {'actual_choice', 'actual_node_id', 'actual_marker', 'actual_transformation', 'actual_revisit',
                    'actual_consumed', 'actual_reward', 'actual_quantity', 'actual_eligible'}
        self.assertEqual({key for key in value if key.startswith('actual_')}, expected)
        for key in expected: self.assertIsNone(value[key])
        for key in ('inventory_updated', 'calculation_applied', 'run_state_updated'):
            self.assertIs(value[key], False)

    def clone(self, root):
        manifest = json.loads((self.subject.ROOT / self.subject.MANIFEST).read_bytes())
        for relative in (self.subject.MANIFEST, *manifest['runtime_files']):
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(self.subject.ROOT / relative, target)
        return manifest

    def assert_failed(self):
        for event_id in ('community_group_030', 'community_group_031'):
            result = self.subject.event_reference(event_id)
            self.assertEqual(result['status'], 'source_unavailable')
            self.assertFalse(result['source_valid'])
            self.assertEqual(result['choices'], [])
            for key in ('event_title', 'scope_key', 'node_context_reference', 'source', 'source_reference', 'source_identity'):
                self.assertIsNone(result[key])
            self.actual_unknown(result)
        for identity in self.IDENTITIES:
            result = self.subject.choice_reference(*identity)
            self.assertEqual(result['status'], 'source_unavailable')
            for key in ('reference', 'related_stage_reference', 'node_context_reference', 'source', 'source_reference', 'source_identity'):
                self.assertIsNone(result[key])
            self.actual_unknown(result)
        self.assertIsNone(self.subject.source_data())

    def test_five_complete_choices_six_primary_candidates_no_prefix_resolution(self):
        expected = [['choice_ro6_end1_1'], ['choice_ro6_end1_2'], ['choice_ro6_end2_1', 'choice_ro6_end2_4'],
                    ['choice_ro6_end2_2'], ['choice_ro6_end2_3']]
        self.assertEqual([self.row(index)['original_choice_ids'] for index in range(5)], expected)
        self.assertEqual([len(self.subject.event_reference(key)['choices']) for key in ('community_group_030', 'community_group_031')], [2, 3])
        for identity, originals in zip(self.IDENTITIES, expected):
            row = self.subject.choice_reference(*identity)['reference']
            self.assertEqual((row['event_id'], row['scene_key'], row['choice_key']), identity)
            self.assertEqual(row['reference_id'], identity[2])
            self.assertEqual(list(row['original_choices']), originals)

    def test_protection_retains_different_original_types_and_optional_item(self):
        row = self.row(2)
        self.assertTrue(row['original_choice_candidate_selection_unknown'])
        first, second = row['original_choices']['choice_ro6_end2_1'], row['original_choices']['choice_ro6_end2_4']
        self.assertEqual((first['type'], second['type']), ('TRADE', 'NEXT'))
        self.assertEqual(first['displayData']['itemId'], 'rogue_6_end_2_change')
        self.assertIsNone(second['displayData']['itemId'])
        self.assertEqual(first['title'], second['title'])
        self.assertIsNone(row['actual_choice'])

    def test_scene_and_choice_numbers_come_from_complete_source_order(self):
        self.assertEqual([(self.row(i)['scene_number'], self.row(i)['choice_number']) for i in range(5)],
                         [(1, 1), (1, 2), (1, 1), (1, 2), (3, 1)])
        for index in range(5):
            row = self.row(index)
            self.assertEqual(row['choice_title'], row['catalog_choice']['title'])
            self.assertEqual(row['choice_description'], row['catalog_choice']['description'])
            self.assertEqual(row['condition_text'], row['catalog_choice']['conditional'])

    def test_marker_purchase_keeps_fifty_cost_and_existing_two_sandbox_or_visited_condition(self):
        row = self.row(0)
        self.assertEqual(set(self.rules(0)), {'marker_purchase_reference'})
        self.assertIn('50源石锭', self.rules(0)['marker_purchase_reference']['text'])
        self.assertIn('尚未标记', self.rules(0)['marker_purchase_reference']['text'])
        self.assertIn('沙盘α', row['condition_text'])
        self.assertIn('沙盘β', row['condition_text'])
        self.assertIn('或访问过', row['condition_text'])
        self.assertIsNone(row['related_stage_reference'])

    def test_one_unnamed_relic_does_not_borrow_marker_or_convert_rule(self):
        row = self.row(1)
        self.assertEqual(set(self.rules(1)), {'unnamed_relic_reward_reference'})
        text = self.rules(1)['unnamed_relic_reward_reference']['text']
        self.assertIn('1件收藏品', text)
        self.assertIn('完整候选池', text)
        self.assertIn('未确认', text)
        self.assertNotIn('50', text)
        self.assertIsNone(row['related_stage_reference'])
        self.assertIsNone(row['original_choices']['choice_ro6_end1_2']['displayData']['itemId'])

    def test_conversion_restriction_and_node_effect_exception_are_only_protection_rules(self):
        entries = self.rules(2)
        self.assertEqual(set(entries), {'node_becomes_fixed_battle', 'cannot_leave_after_conversion', 'not_normal_battle_node_effect'})
        self.assertIn('混沌源阶理论', entries['node_becomes_fixed_battle']['text'])
        self.assertIn('变化后不能离开', entries['cannot_leave_after_conversion']['text'])
        self.assertIn('作战节点', entries['not_normal_battle_node_effect']['text'])
        self.assertIn('概念体', entries['not_normal_battle_node_effect']['text'])
        for index in (0, 1, 3, 4):
            self.assertTrue(set(self.rules(index)).isdisjoint(entries))

    def test_temporary_leave_is_completed_node_reference_and_revisit_not_boss_completion(self):
        entries = self.rules(3)
        self.assertEqual(set(entries), {'temporary_leave_completes_node', 'documented_revisit'})
        self.assertIn('暂离并完成该节点', entries['temporary_leave_completes_node']['text'])
        text = entries['documented_revisit']['text']
        for literal in ('可重复', '被标记', '再次访问', '未知'): self.assertIn(literal, text)
        self.assertNotIn('首领已完成', text)
        self.assertIsNone(self.row(3)['related_stage_reference'])

    def test_only_two_explicit_related_fixed_stage_references_are_exposed(self):
        expected = {'stage_id': 'ro6_b_5', 'title': '混沌源阶理论', 'reference_only': True, 'immediate_transition': None}
        for index in range(5):
            details = self.subject.choice_reference(*self.IDENTITIES[index])
            self.assertEqual(details['related_stage_reference'], expected if index in (2, 4) else None)
            self.assertEqual(details['reference']['related_stage_reference'], details['related_stage_reference'])
        self.assertEqual(set(self.rules(4)), {'existing_battle_decision_reference'})
        self.assertIn('这里只提供固定作战资料', self.rules(4)['existing_battle_decision_reference']['text'])
        self.assertIn('不代表本局已经进入战斗', self.rules(4)['existing_battle_decision_reference']['text'])

    def test_fifth_floor_three_two_one_and_two_sandboxes_remain_document_context(self):
        result = self.subject.event_reference('community_group_030')
        context = result['node_context_reference']
        self.assertEqual(context['documented_main_floor'], 5)
        self.assertIs(type(context['documented_main_floor']), int)
        self.assertIsNone(context['actual_node_ids'])
        text = '\n'.join(context['texts'])
        self.assertIn('这份结局流程先要求解锁相关选项，并取得一个或多个沙盘；随后描述抵达第Ⅴ层会出现3个命运所指（2个好奇心与死、1个窥视箱中）。这不表示所有第五层无条件出现这些节点。', text)
        for literal in ('沙盘α', '沙盘β', '谜题与谜底'):
            self.assertIn(literal, text)
        paragraph_five = [ref for ref in context['source_refs'] if ref.get('paragraph_index') == 5]
        self.assertEqual(len(paragraph_five), 1)
        self.assertIn('获取一个或多个【沙盘】收藏品', paragraph_five[0]['text'])
        authority = json.loads((self.subject.ROOT / self.subject.SELECTED_AUTHORITY).read_bytes())
        self.assertIn(paragraph_five[0]['text'], authority['complete_ending_documentation']['text'])
        self.assertIn('3个命运所指无法从外观分辨', authority['complete_ending_documentation']['text'])
        self.assertEqual(context, self.subject.event_reference('community_group_031')['node_context_reference'])

    def test_all_outputs_leave_actual_state_unknown_and_never_update_inventory(self):
        packet = self.subject.source_data()
        self.actual_unknown(packet)
        self.assertIs(packet['original_entry_restored'], False)
        self.assertIs(packet['current_server_verified'], False)
        for row in packet['choices']: self.actual_unknown(row)
        for event_id in ('community_group_030', 'community_group_031'):
            self.actual_unknown(self.subject.event_reference(event_id))
        for identity in self.IDENTITIES: self.actual_unknown(self.subject.choice_reference(*identity))

    def test_complete_primary_choices_scenes_features_and_stage_are_not_synthesized(self):
        primary = json.loads((PROJECT_ROOT / 'research/p3-future-region-effects-300/game-topic-complete.json').read_bytes())['details']['rogue_6']
        packet = self.subject.source_data()
        for key, value in packet['complete_original_choices'].items(): self.assertEqual(value, primary['choices'][key])
        for key, value in packet['complete_original_scenes'].items(): self.assertEqual(value, primary['choiceScenes'][key])
        configuration = packet['configuration_references']
        self.assertEqual(len(configuration['items']), 14)
        for key, value in configuration['items'].items(): self.assertEqual(value, primary['items'][key])
        for key, value in configuration['relics'].items(): self.assertEqual(value, primary['relics'][key])
        self.assertEqual(configuration['related_stage'], primary['stages']['ro6_b_5'])

    def test_rule_source_references_keep_verbatim_paragraphs_and_exact_choice_identity(self):
        authority = json.loads((self.subject.ROOT / self.subject.SELECTED_AUTHORITY).read_bytes())
        document = authority['complete_ending_documentation']['text']
        for row in self.subject.source_data()['choices']:
            for entry in row['documented_rules']:
                self.assertEqual(set(entry), {'rule_id', 'title', 'text', 'source_refs'})
                self.assertTrue(entry['source_refs'])
                for reference in entry['source_refs']:
                    if reference['selector'] == 'main_complete_ending_blocks.end2.text':
                        self.assertIn(reference['text'], document)
                    else:
                        self.assertEqual(reference['selector'], 'exact_five_choice_rows')
                        self.assertEqual(reference['choice_key'], row['choice_key'])

    def test_invalid_event_is_non_applicable_without_source_access(self):
        with patch.object(self.subject, '_verified_packet', side_effect=AssertionError('No source read for non-target')):
            for value in (None, True, False, 30, 30.0, [], {}, '', 'community_group_030x', 'community_group_032', 'COMMUNITY_GROUP_030'):
                self.assertIsNone(self.subject.event_reference(value))

    def test_invalid_or_cross_event_complete_tuple_is_rejected_without_fallback(self):
        event_id, scene_key, choice_key = self.IDENTITIES[0]
        variants = [(event_id, scene_key, choice_key + 'x'), ('community_group_031', scene_key, choice_key),
                    (event_id, 'community_group_030:scene:1', choice_key), (event_id, scene_key, 'choice_ro6_end1_1'),
                    (event_id, scene_key, choice_key + ':documented-node-result'),
                    (event_id, None, choice_key), (True, scene_key, choice_key), (event_id, scene_key, {})]
        with patch.object(self.subject, '_verified_packet', side_effect=AssertionError('No fallback source read')):
            for identity in variants: self.assertIsNone(self.subject.choice_reference(*identity))

    def test_event_and_choice_outputs_are_independent_deep_copies(self):
        before = self.row(2)
        returned = self.subject.event_reference('community_group_031')
        returned['choices'][0]['original_choices']['choice_ro6_end2_4']['displayData']['itemId'] = 'wrong'
        returned['choices'][0]['documented_rules'].clear()
        self.assertEqual(self.row(2), before)
        choice = self.subject.choice_reference(*self.IDENTITIES[2])
        choice['related_stage_reference']['stage_id'] = 'wrong'
        self.assertEqual(self.row(2), before)

    def test_source_packet_and_nested_expected_objects_cannot_pollute_later_queries(self):
        before = self.subject.source_data()
        returned = self.subject.source_data()
        returned['expected_events']['community_group_030']['scenes'][0]['description'] = 'wrong'
        returned['complete_original_choices'].clear()
        returned['configuration_references']['items'].clear()
        self.assertEqual(self.subject.source_data(), before)

    def test_warm_legacy_catalog_mutation_is_detected_and_clear_recovers(self):
        self.assertTrue(self.subject.event_reference('community_group_030')['source_valid'])
        self.catalog._event('community_group_030')['scenes'][0]['description'] = 'Changed warm object only'
        self.assert_failed()
        self.catalog._data.cache_clear()
        self.assertTrue(self.subject.event_reference('community_group_030')['source_valid'])

    def test_every_runtime_file_byte_change_fails_closed_after_warm_valid_clone(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); manifest = self.clone(root)
            with patch.object(self.subject, 'ROOT', root):
                self.assertTrue(self.subject.event_reference('community_group_030')['source_valid'])
                for relative in manifest['runtime_files']:
                    with self.subTest(relative=relative):
                        target = root / relative; original = target.read_bytes()
                        target.write_bytes(original + b' ')
                        try: self.assert_failed()
                        finally: target.write_bytes(original)
                        self.assertTrue(self.subject.event_reference('community_group_031')['source_valid'])

    def test_every_runtime_file_missing_fails_closed_and_exact_restore_recovers(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); manifest = self.clone(root)
            with patch.object(self.subject, 'ROOT', root):
                self.assertIsNotNone(self.subject.source_data())
                for relative in manifest['runtime_files']:
                    with self.subTest(relative=relative):
                        target = root / relative; original = target.read_bytes(); target.unlink()
                        try: self.assert_failed()
                        finally: target.write_bytes(original)
                        self.assertTrue(self.subject.event_reference('community_group_030')['source_valid'])

    def test_manifest_byte_change_and_missing_are_not_hidden_by_a_warm_result(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); self.clone(root)
            target = root / self.subject.MANIFEST; original = target.read_bytes()
            with patch.object(self.subject, 'ROOT', root):
                self.assertIsNotNone(self.subject.source_data())
                target.write_bytes(original + b' ')
                self.assert_failed()
                target.unlink(); self.assert_failed()
                target.write_bytes(original)
                self.assertIsNotNone(self.subject.source_data())

    def test_hot_query_reads_all_runtime_members_but_not_large_build_only_sources(self):
        manifest = json.loads((self.subject.ROOT / self.subject.MANIFEST).read_bytes())
        reads = []; original = self.subject._source_path
        def observe(relative):
            reads.append(relative)
            return original(relative)
        with patch.object(self.subject, '_source_path', side_effect=observe):
            self.assertTrue(self.subject.event_reference('community_group_030')['source_valid'])
        self.assertEqual(set(reads), {self.subject.MANIFEST, *manifest['runtime_files']})
        self.assertTrue(set(reads).isdisjoint(manifest['build_authority_files']))

    def test_scope_is_stable_source_identity_and_not_current_time_or_state(self):
        first = self.subject.event_reference('community_group_030')
        second = self.subject.event_reference('community_group_030')
        self.assertEqual(first['scope_key'], second['scope_key'])
        self.assertNotEqual(first['scope_key'], self.subject.event_reference('community_group_031')['scope_key'])
        self.assertIn(self.subject.DATA_SHA256, first['scope_key'])
        self.assertIn(self.subject.MANIFEST_SHA256, first['scope_key'])

    def test_public_api_does_not_accept_evaluator_source_state_or_extra_context(self):
        self.assertEqual(str(inspect.signature(self.subject.event_reference)), '(event_id)')
        self.assertEqual(str(inspect.signature(self.subject.choice_reference)), '(event_id, scene_key, choice_key)')
        self.assertEqual(str(inspect.signature(self.subject.source_data)), '()')
        with self.assertRaises(TypeError): self.subject.event_reference('community_group_030', data={})
        with self.assertRaises(TypeError): self.subject.choice_reference(*self.IDENTITIES[0], inventory={})
        with self.assertRaises(TypeError): self.subject.source_data(source={})

    def test_fixed_source_paths_reject_absolute_traversal_and_windows_paths(self):
        for value in ('../private.json', '/tmp/anything', 'C:/anything', 'rouge\\data\\node-catalog.json', True, None):
            with self.subTest(value=value), self.assertRaises(ValueError): self.subject._source_path(value)


if __name__ == '__main__': unittest.main()
