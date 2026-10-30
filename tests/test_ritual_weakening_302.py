"""Fixed public ritual documents only; isolated source negatives, no Qt or run."""
from copy import deepcopy
from hashlib import sha256
import importlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


def load_subject():
    explicit = os.environ.get('ROUGE_RITUAL_WEAKENING_MODULE')
    if explicit:
        spec = importlib.util.spec_from_file_location('rouge._candidate_ritual_weakening302', explicit)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    return importlib.import_module('rouge.ritual_weakening')


class RitualWeakeningTests(unittest.TestCase):
    subject = None

    @classmethod
    def setUpClass(cls):
        if cls.subject is None: cls.subject = load_subject()

    def setUp(self):
        from rouge import node_catalog
        self.catalog = node_catalog
        self.catalog._data.cache_clear()
        self.addCleanup(self.catalog._data.cache_clear)

    def event(self): return self.subject.event_reference('community_group_032')

    def details(self, scene=2, choice=0):
        scene_key = 'community_group_032:scene:' + str(scene)
        return self.subject.weakening_details('community_group_032', scene_key, scene_key + ':choice:' + str(choice))

    def clone(self, root):
        manifest = json.loads((self.subject.ROOT / self.subject.MANIFEST).read_bytes())
        for relative in (self.subject.MANIFEST, *manifest['runtime_files']):
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(self.subject.ROOT / relative, target)
        return manifest

    def actual_unknown(self, result):
        expected = {'actual_choice', 'actual_weakening', 'actual_attached', 'actual_inventory',
                    'actual_consumed', 'actual_effect', 'actual_numeric_result', 'actual_eligible'}
        self.assertEqual({k for k in result if k.startswith('actual_')}, expected)
        for name in expected: self.assertIsNone(result[name])

    def assert_failed(self):
        packet = self.event()
        self.assertFalse(packet['source_valid'])
        self.assertEqual(packet['status'], 'source_unavailable')
        self.assertEqual(packet['choices'], [])
        self.assertEqual(packet['weakening_references'], [])
        for key in ('event_title', 'scope_key', 'related_stage_reference', 'source', 'source_reference', 'source_identity'):
            self.assertIsNone(packet[key])
        for scene in (2, 3, 4):
            for choice in (0, 1):
                details = self.details(scene, choice)
                self.assertFalse(details['source_valid'])
                self.assertEqual(details['status'], 'source_unavailable')
                for key in ('reference', 'weakening_reference', 'related_stage_reference', 'source', 'source_reference'):
                    self.assertIsNone(details[key])
                self.actual_unknown(details)
        self.assertIsNone(self.subject.source_data())

    def test_six_full_tuples_bind_literal_primary_ids_and_order_one_three_two(self):
        packet = self.event()
        self.assertTrue(packet['source_valid'])
        expected = [(2, 0, '3', '1'), (2, 1, '4', '1'), (3, 0, '6', '3'),
                    (3, 1, '7', '3'), (4, 0, '9', '2'), (4, 1, '10', '2')]
        actual = []
        for row in packet['choices']:
            details = self.subject.weakening_details(row['event_id'], row['scene_key'], row['choice_key'])
            self.assertTrue(details['source_valid'])
            self.assertEqual(details['reference'], row)
            self.assertEqual(row['reference_id'], row['choice_key'])
            actual.append((int(row['scene_key'].split(':')[-1]), int(row['choice_key'].split(':')[-1]),
                           row['original_choice_id'].rsplit('_', 1)[1], row['weakening_id'].rsplit('_', 1)[1]))
        self.assertEqual(actual, expected)
        self.assertEqual([e['weakening_id'] for e in packet['weakening_references']],
                         ['rogue_6_chimera_weaken_1', 'rogue_6_chimera_weaken_3', 'rogue_6_chimera_weaken_2'])

    def test_three_same_name_private_keys_remain_different_complete_options(self):
        rows = [r for r in self.event()['choices'] if r['choice_title'] == '用源私钥作弊']
        self.assertEqual(len(rows), 3)
        self.assertEqual(len({r['reference_id'] for r in rows}), 3)
        self.assertEqual(len({r['weakening_id'] for r in rows}), 3)
        self.assertEqual([r['ritual_step'] for r in rows], [1, 2, 3])
        self.assertEqual([r['submission_reference']['name'] for r in rows], ['源私钥'] * 3)
        self.assertTrue(all(r['submission_reference']['is_alternative'] for r in rows))
        self.assertIn('击坠“神明”', rows[0]['condition_text'])
        self.assertIn('焚毁“文明”', rows[1]['condition_text'])
        self.assertIn('湮没“光明”', rows[2]['condition_text'])

    def test_complete_choices_scenes_features_and_stage_equal_fixed_primary(self):
        path = self.subject.ROOT / 'research/p3-future-region-effects-300/game-topic-complete.json'
        primary = json.loads(path.read_bytes())['details']['rogue_6']
        packet = self.subject.source_data()
        authority = json.loads((self.subject.ROOT / self.subject.SELECTED_AUTHORITY).read_bytes())
        for row in packet['choices']:
            self.assertEqual(row['original_choice'], primary['choices'][row['original_choice_id']])
            feature = row['feature_reference']
            self.assertEqual(feature['item'], primary['items'][row['weakening_id']])
            self.assertEqual(feature['relic'], primary['relics'][row['weakening_id']])
            self.assertEqual(feature['blackboard'], feature['relic']['buffs'][0]['blackboard'])
        for identity, value in authority['complete_original_scenes'].items():
            self.assertEqual(value, primary['choiceScenes'][identity])
        self.assertEqual(packet['related_stage_reference']['original_stage'], primary['stages']['ro6_b_6'])

    def test_selector_and_blackboard_keys_do_not_merge_distinct_weakening(self):
        effects = self.event()['weakening_references']
        self.assertEqual([next(b['valueStr'] for b in e['feature_reference']['blackboard'] if b['key'] == 'key') for e in effects],
                         ['enemy_shchmr_no_fire_mode_1', 'enemy_shchmr_reborn_no_card', 'enemy_shchmr_reborn_damage'])
        self.assertTrue(all(e['feature_reference']['selector'] == 'enemy_2150_shchmr' for e in effects))
        self.assertTrue(all(e['feature_reference']['item']['type'] == 'FEATURE' for e in effects))

    def test_first_disaster_cast_limitation_is_preserved(self):
        first = self.event()['weakening_references'][0]
        self.assertIn('首次', first['effect_text'])
        self.assertIn('首次', first['effect_source_text'])
        self.assertIn('首次', first['feature_reference']['item']['usage'])
        self.assertIn('“危朽”', first['effect_text'])

    def test_other_effects_are_qualitative_and_damage_half_is_only_configuration(self):
        effects = self.event()['weakening_references']
        self.assertIn('待部署区', effects[1]['effect_text'])
        self.assertEqual(effects[2]['effect_text'], '灾厄之口的伤害降低。')
        config = effects[2]['configuration_reference']
        self.assertEqual(config['key'], 'damage_scale')
        self.assertEqual(config['value'], 0.5)
        self.assertFalse(config['numerical_execution_verified'])
        self.assertNotIn('50%', effects[2]['effect_text'])
        self.assertIsNone(effects[0]['configuration_reference'])
        self.assertIsNone(effects[1]['configuration_reference'])

    def test_related_stage_is_manual_reference_not_transition_or_enemy_level(self):
        related = self.event()['related_stage_reference']
        self.assertEqual(related['stage_id'], 'ro6_b_6')
        self.assertEqual(related['title'], '畸症')
        self.assertTrue(related['reference_only'])
        self.assertIsNone(related['immediate_transition'])
        self.assertEqual(related['enemy_selector'], 'enemy_2150_shchmr')
        self.assertIsNone(related['enemy_level_reference'])
        for row in self.event()['choices']:
            self.assertEqual(row['related_stage_reference'], related)
            self.assertNotEqual(row['original_choice']['nextSceneId'], 'ro6_b_6')

    def test_all_actual_outcomes_remain_unknown_and_no_calculation_or_run_write(self):
        packet = self.event()
        self.actual_unknown(packet)
        self.assertFalse(packet['calculation_applied'])
        self.assertFalse(packet['run_state_updated'])
        for row in packet['choices']:
            self.actual_unknown(row)
            self.assertIsNone(row['submission_reference']['quantity_reference'])
            self.assertFalse(row['calculation_applied'])
            self.assertFalse(row['run_state_updated'])
            self.actual_unknown(self.subject.weakening_details(row['event_id'], row['scene_key'], row['choice_key']))
        for effect in packet['weakening_references']: self.actual_unknown(effect)

    def test_non_target_and_wrong_types_return_none_before_io(self):
        with patch.object(self.subject, '_verified_packet', side_effect=AssertionError('Unexpected source query')):
            for identity in (None, True, 32, [], {}, '调谐仪式', 'community_group_031', 'community_group_032 '):
                self.assertIsNone(self.subject.event_reference(identity))

    def test_invalid_full_tuple_and_skip_options_do_not_borrow_effect(self):
        with patch.object(self.subject, '_verified_packet', side_effect=AssertionError('Unexpected source query')):
            for scene, choice in ((0, 0), (2, 2), (3, 2), (4, 2), (5, 0), (2, -1)):
                self.assertIsNone(self.details(scene, choice))
            self.assertIsNone(self.subject.weakening_details('community_group_032',
                              'community_group_032:scene:2', 'community_group_032:scene:3:choice:1'))
            self.assertIsNone(self.subject.weakening_details('community_group_031',
                              'community_group_032:scene:2', 'community_group_032:scene:2:choice:0'))
            self.assertIsNone(self.subject.weakening_details('community_group_032', True, 'community_group_032:scene:2:choice:0'))

    def test_outputs_and_details_are_independent_copies(self):
        initial = self.event()
        row = initial['choices'][0]
        row['original_choice']['description'] = 'changed'
        row['feature_reference']['relic']['buffs'][0]['blackboard'][0]['valueStr'] = 'changed'
        initial['source']['game']['commit'] = 'changed'
        second = self.event()
        self.assertTrue(second['source_valid'])
        self.assertNotEqual(second['choices'][0]['original_choice']['description'], 'changed')
        details = self.details()
        details['reference']['condition_text'] = 'changed'
        details['weakening_reference']['effect_text'] = 'changed'
        self.assertNotEqual(self.details()['reference']['condition_text'], 'changed')
        self.assertNotEqual(self.details()['weakening_reference']['effect_text'], 'changed')

    def test_no_backend_snapshot_cache_can_be_co_mutated(self):
        self.event()
        self.assertFalse(hasattr(self.subject, '_parsed_packet'))
        self.assertFalse(hasattr(self.subject, '_CACHE'))
        data = self.subject.source_data()
        data['expected_event']['title'] = 'co-mutated'
        data['choices'][0]['catalog_choice']['title'] = 'co-mutated'
        self.assertEqual(self.event()['event_title'], '调谐仪式')

    def test_warm_legacy_full_event_description_mismatch_fails_closed(self):
        self.assertTrue(self.event()['source_valid'])
        event = self.catalog._event('community_group_032')
        event['scenes'][0]['description'] += ' altered outside selected choices'
        self.assert_failed()

    def test_warm_legacy_same_value_different_json_type_fails_closed(self):
        self.assertTrue(self.event()['source_valid'])
        self.catalog._event('community_group_032')['scenes'][2]['choices'][0]['server_option_availability_verified'] = 0
        self.assert_failed()

    def test_current_event_and_expected_co_mutation_cannot_override_pinned_disk(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.clone(root)
            with patch.object(self.subject, 'ROOT', root):
                self.assertTrue(self.event()['source_valid'])
                path = root / self.subject.DATA
                packet = json.loads(path.read_bytes())
                packet['expected_event']['title'] = 'co-mutated'
                path.write_text(json.dumps(packet, ensure_ascii=False), encoding='utf8')
                self.catalog._event('community_group_032')['title'] = 'co-mutated'
                self.assert_failed()

    def test_every_runtime_member_is_fresh_and_failure_is_package_wide(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            manifest = self.clone(root)
            with patch.object(self.subject, 'ROOT', root):
                for relative in manifest['runtime_files']:
                    with self.subTest(source=relative):
                        self.assertTrue(self.event()['source_valid'])
                        target = root / relative
                        original = target.read_bytes()
                        target.write_bytes(original + b' ')
                        self.assert_failed()
                        target.write_bytes(original)
                        self.assertTrue(self.event()['source_valid'])

    def test_manifest_changed_or_missing_never_reuses_previous_packet(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.clone(root)
            with patch.object(self.subject, 'ROOT', root):
                self.assertTrue(self.event()['source_valid'])
                path = root / self.subject.MANIFEST
                original = path.read_bytes()
                path.write_bytes(original + b' ')
                self.assert_failed()
                path.unlink()
                self.assert_failed()
                path.write_bytes(original)
                self.assertTrue(self.event()['source_valid'])

    def test_missing_selected_record_is_unknown_after_warm_success(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.clone(root)
            with patch.object(self.subject, 'ROOT', root):
                self.assertTrue(self.event()['source_valid'])
                (root / self.subject.SELECTED_AUTHORITY).unlink()
                self.assert_failed()

    def test_runtime_does_not_read_complete_build_only_originals(self):
        manifest = json.loads((self.subject.ROOT / self.subject.MANIFEST).read_bytes())
        original = self.subject._source_path
        calls = []
        def observed(relative):
            calls.append(relative)
            self.assertNotIn(relative, manifest['build_authority_files'])
            return original(relative)
        with patch.object(self.subject, '_source_path', side_effect=observed):
            self.assertTrue(self.event()['source_valid'])
        self.assertEqual(set(calls), {self.subject.MANIFEST, *manifest['runtime_files']})
        self.assertEqual(len(calls), 1 + len(manifest['runtime_files']))
        self.assertLess(sum(p['bytes'] for p in manifest['runtime_files'].values()) +
                        (self.subject.ROOT / self.subject.MANIFEST).stat().st_size, 1_000_000)

    def test_complete_fixed_source_builder_replays_without_writes(self):
        script = self.subject.ROOT / 'scripts/replay_reference_recipe.py'
        result = subprocess.run([sys.executable, '-B', '-X', 'utf8', str(script), '--recipe', 'ritual'],
                                capture_output=True, timeout=60, check=False)
        self.assertEqual(result.returncode, 0, result.stderr.decode('utf8'))
        receipt = json.loads(result.stdout)
        self.assertFalse(receipt['write'])
        self.assertEqual(receipt['counts'], {'events': 1, 'choices': 6, 'weakening_references': 3, 'related_stages': 1})

    def test_complete_two_event_doms_and_fixed_ending_not_tool_snippet(self):
        authority = json.loads((self.subject.ROOT / self.subject.SELECTED_AUTHORITY).read_bytes())
        self.assertEqual(set(authority['event_complete_DOMs']), {'427904', '440271'})
        def choice_titles(node):
            if isinstance(node, str): return []
            return [node['attributes'].get('data-title')] + [title for child in node['children'] for title in choice_titles(child)]
        for dom in authority['event_complete_DOMs'].values():
            self.assertEqual(dom['complete_DOM']['tag'], 'div')
            self.assertIn('建立信仰抵御黑风', choice_titles(dom['complete_DOM']))
            self.assertIn('建立文化抵御黑焰', choice_titles(dom['complete_DOM']))
            self.assertIn('建立认同抵御黑流', choice_titles(dom['complete_DOM']))
            self.assertIn('交出击坠“神明”', dom['text'])
            self.assertIn('交出焚毁“文明”', dom['text'])
            self.assertIn('交出湮没“光明”', dom['text'])
        ending = authority['main_complete_ending_block']
        self.assertEqual(ending['revision'], '433770')
        self.assertTrue(ending['complete_DOM']['children'])
        self.assertIn('首次释放的灾厄之口', ending['text'])
        self.assertIn('使用【源私钥】可以作弊以替换上述任一需求。', ending['text'])

    def test_original_entry_and_quantity_gaps_are_not_filled(self):
        packet = self.subject.source_data()
        self.assertFalse(packet['original_entry_restored'])
        self.assertFalse(packet['current_server_verified'])
        self.assertEqual(packet['expected_event']['natural'], None)
        for row in packet['choices']:
            self.assertFalse(row['catalog_choice']['server_option_availability_verified'])
            self.assertIsNone(row['submission_reference']['quantity_reference'])
        self.assertNotIn('event_battle_links', packet)

    def test_public_api_rejects_source_or_evaluator_injection(self):
        for kwargs in ({'data': {}}, {'source': {}}, {'evaluator': lambda value: value}):
            with self.assertRaises(TypeError): self.subject.event_reference('community_group_032', **kwargs)
        with self.assertRaises(TypeError): self.subject.source_data({})
        with self.assertRaises(TypeError): self.subject.weakening_details('community_group_032',
                              'community_group_032:scene:2', 'community_group_032:scene:2:choice:0', data={})

    def test_queries_do_not_write_any_files(self):
        with patch.object(Path, 'write_bytes', side_effect=AssertionError('Unexpected write')):
            with patch.object(Path, 'write_text', side_effect=AssertionError('Unexpected write')):
                self.assertTrue(self.event()['source_valid'])
                self.assertTrue(self.details()['source_valid'])


if __name__ == '__main__': unittest.main()
