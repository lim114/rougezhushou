"""Exact documented phase separation, identities and fresh fail-closed guards."""
from copy import deepcopy
import hashlib
import inspect
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from rouge import expedition_results as model


class ExpeditionResultsTests(unittest.TestCase):
    def setUp(self):
        self.previous_cache = model._parsed_packet
        model._parsed_packet = None
        self.addCleanup(setattr, model, '_parsed_packet', self.previous_cache)

    def event(self): return model.event_reference('community_group_024')
    def root_choice(self): return model.choice_reference(model.EVENT, model.SCENE, model.ROOT_CHOICE)
    def item(self): return model.item_details(model.EVENT, model.SCENE, model.ROOT_CHOICE)

    def clone(self, root):
        manifest = json.loads((model.ROOT / model.MANIFEST).read_bytes())
        for name in [model.MANIFEST, *manifest['files']]:
            target = root / name; target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(model.ROOT / name, target)
        return manifest

    def test_three_actual_choices_keep_full_identity_and_original_order(self):
        result = self.event()
        self.assertEqual(result['status'], 'documented_reference'); self.assertTrue(result['source_valid'])
        self.assertEqual([(r['choice_key'], r['original_choice_id'], r['choice_title']) for r in result['rows']], [
            ('community_group_024:scene:0:choice:0', 'choice_ro6_scout_1', '尝试探索树的内部'),
            ('community_group_024:scene:0:choice:1', 'choice_ro6_scout_3', '尝试探索树的源头'),
            ('community_group_024:scene:0:choice:2', 'choice_ro6_scout_2', '休息')])
        self.assertTrue(all(r['is_actual_button_reference'] for r in result['rows']))

    def test_immediate_rest_and_delayed_source_hope_are_never_combined(self):
        inside, source, rest = self.event()['rows']
        self.assertEqual(inside['immediate_resource_references'], [])
        self.assertEqual(inside['return_resource_references'], [])
        self.assertEqual(source['immediate_resource_references'], [])
        self.assertEqual(source['return_resource_references'], [{'resource':'hope','quantity_reference':2}])
        self.assertEqual(rest['immediate_resource_references'], [{'resource':'hope','quantity_reference':2}])
        self.assertEqual(rest['return_resource_references'], [])
        self.assertEqual([r['effect_phase_reference'] for r in (inside,source,rest)], ['on_return','on_return','on_choice'])

    def test_dispatch_reference_keeps_both_native_return_wordings_and_community_scope(self):
        for row in self.event()['rows'][:2]:
            dispatch = row['dispatch_reference']
            self.assertEqual(dispatch['operator_count_reference'], 1)
            self.assertIs(type(dispatch['operator_count_reference']), int)
            self.assertIs(dispatch['temporarily_unavailable_for_squad'], True)
            self.assertEqual(dispatch['native_unavailable_wording'], '该干员已深入树海展开先行探索，不可编入队伍')
            self.assertEqual(dispatch['native_return_wordings'], [
                '干员{0}将会在本区域探索结束后归来，并带回一些物资。',
                '干员{0}将会在进入新区域时归来，并带回一些物资。'])
            self.assertEqual(dispatch['community_return_when'], '下一层开始时')
            self.assertIsNone(dispatch['special_region_equivalence'])

    def test_source_return_names_one_identity_without_inventing_quantity_or_actual_grant(self):
        row = self.root_choice(); item = row['documented_return_item']
        self.assertEqual(item['item_id'], 'rogue_6_relic_final_3'); self.assertEqual(item['name'], '怦然信标')
        self.assertIsNone(item['quantity_reference']); self.assertEqual(item['effect_phase_reference'], 'on_return')
        self.assertEqual(item['original_pointer_field'], 'gameConst.expedEndingRelic')
        self.assertIn('回归时，仅获得2希望与收藏品', row['return_explanation'])
        self.assertIs(row['promotion_reference'], False); self.assertIsNone(row['actual_reward'])

    def test_normal_promotion_and_complete_return_pool_stay_unknown(self):
        row = self.event()['rows'][0]
        self.assertIsNone(row['promotion_reference']); self.assertFalse(row['complete_return_rewards_known'])
        self.assertIsNone(row['documented_return_item']); self.assertIsNone(row['actual_advanced'])
        self.assertTrue(any('普通内部探索是否必然进阶' in text for text in self.event()['unknowns']))

    def test_rest_has_no_dispatch_promotion_or_delayed_item(self):
        row = self.event()['rows'][2]
        self.assertIsNone(row['dispatch_reference']); self.assertIsNone(row['beak_reference'])
        self.assertIsNone(row['promotion_reference']); self.assertIsNone(row['documented_return_item'])
        self.assertIsNone(row['explanatory_choice_key']); self.assertIsNone(row['return_explanation'])

    def test_beak_reference_does_not_override_source_only_wording(self):
        for row in self.event()['rows'][:2]:
            beak = row['beak_reference']
            self.assertEqual(beak['source_text'], '在点亮【生命游戏】的“喙”节点后，干员归来时还可获得随机加工品。')
            self.assertIsNone(beak['applies_to_root_branch']); self.assertIsNone(beak['current_technology_active'])
            self.assertIsNone(beak['quantity_reference']); self.assertIsNone(beak['complete_item_pool'])
            self.assertIn('不额外加算', beak['notice'])

    def test_return_annotation_is_full_exact_explanatory_identity_not_fourth_choice(self):
        result = self.event(); annotation = result['return_explanatory_reference']
        self.assertEqual(len(result['rows']), 3)
        self.assertEqual((annotation['event_id'],annotation['scene_key'],annotation['choice_key']),
            ('community_group_024','community_group_024:scene:2','community_group_024:scene:2:choice:1'))
        self.assertEqual(annotation['presentation_role'], 'explanatory_text'); self.assertIs(annotation['is_actual_button'], False)
        self.assertEqual(annotation['effect_phase'], 'on_return'); self.assertEqual(annotation['game_choice_ids'], [])
        self.assertEqual(annotation['source_dispatch_choice_key'], model.ROOT_CHOICE)
        self.assertEqual(annotation['return_resource_references'], [{'resource':'hope','quantity_reference':2}])
        self.assertEqual(annotation['documented_return_item'], result['rows'][1]['documented_return_item'])

    def test_annotation_api_returns_same_bound_description_in_an_independent_copy(self):
        annotation = model.annotation_reference(model.EVENT,model.ANNOTATION_SCENE,model.ANNOTATION_CHOICE)
        expected = self.event()['return_explanatory_reference']
        for key,value in expected.items(): self.assertEqual(annotation[key], value)
        annotation['documented_return_item']['name'] = '污染'
        again = model.annotation_reference(model.EVENT,model.ANNOTATION_SCENE,model.ANNOTATION_CHOICE)
        self.assertEqual(again['documented_return_item']['name'], '怦然信标')

    def test_return_item_details_retain_exact_usage_description_unlock_and_icon_provenance(self):
        result = self.item(); item = result['item']; icon = result['icon_reference']
        self.assertEqual(item['id'], 'rogue_6_relic_final_3'); self.assertEqual(item['type'], 'RELIC')
        self.assertEqual(item['usage'], '所有敌人的生命+20%，我方单位的生命-40%，让探索开启不同的方向')
        self.assertEqual(item['description'], '一颗被时刻监测着的心脏，似乎正在夺走你的力量。调整至某个方向后，它微弱地跳动了起来。')
        self.assertEqual(item['unlockCondDesc'], '完成游戏结局')
        self.assertIn('不等于源头选项或本局完整出现条件', result['unlock_notice'])
        self.assertEqual(icon['file'], 'rouge/data/relic-icons/rogue_6_relic_final_3.png')
        self.assertEqual(hashlib.sha256((model.ROOT/icon['file']).read_bytes()).hexdigest(), icon['sha256'])
        self.assertEqual(icon['source']['git_blob_sha1'], 'dd45ebe3386d5556799ac62b603d0a8f141e3f09')

    def test_original_choice_item_pointer_remains_null_and_global_return_pointer_is_explicit(self):
        primary = json.loads((model.ROOT/'research/p3-expedition-results-297/original-records.json').read_bytes())
        self.assertIsNone(primary['choices']['choice_ro6_scout_3']['displayData']['itemId'])
        self.assertEqual(primary['gameConst']['expedEndingRelic'], 'rogue_6_relic_final_3')
        self.assertEqual(primary['choices']['choice_ro6_scout_4']['displayData']['itemId'], 'rogue_6_hp')
        self.assertIsNone(primary['choices']['choice_ro6_scout_4']['nextSceneId'])
        self.assertIsNone(self.root_choice()['actual_reward'])

    def test_all_actual_outputs_stay_unknown_and_no_inventory_or_eligibility_is_changed(self):
        result = self.event()
        for flag in ('current_server_verified','inventory_updated','eligibility_evaluated'): self.assertIs(result[flag], False)
        for row in result['rows']:
            for key in ('actual_dispatched_operator','actual_returned','actual_reward','actual_quantity',
                        'actual_advanced','actual_return_clock','actual_selectable'):
                self.assertIsNone(row[key], key)
        for key in ('actual_reward','actual_quantity','actual_selectable','actual_returned','actual_advanced'):
            self.assertIsNone(self.item()[key])

    def test_two_complete_dom_versions_bind_the_same_return_explanation_and_not_a_button(self):
        bindings = self.event()['source_reference']['event_dom_bindings']
        self.assertEqual([binding['revision'] for binding in bindings], ['427904','440271'])
        for binding in bindings:
            self.assertEqual(len(binding['scenes']), 4)
            explanation = binding['scenes'][2]['choices'][1]
            self.assertEqual(explanation['attributes']['data-type'], 'desc')
            self.assertIn('不会被进阶', explanation['description'])
            self.assertIn('回归时，仅获得2希望', explanation['description'])

    def test_non_target_values_never_scan_sources(self):
        class StringSubclass(str): pass
        with patch.object(model,'_verified_packet',side_effect=AssertionError('Must not scan')):
            for value in (None,True,1,[],{},'未涉足之树','community_group_023',StringSubclass(model.EVENT)):
                self.assertIsNone(model.event_reference(value))

    def test_wrong_scene_choice_and_title_fallback_are_rejected_before_source_scan(self):
        cases = [(model.EVENT,model.ANNOTATION_SCENE,model.ANNOTATION_CHOICE),
            (model.EVENT,model.SCENE,'尝试探索树的源头'), (model.EVENT,model.SCENE,True),
            (model.EVENT,model.SCENE,[]), (model.EVENT,True,model.ROOT_CHOICE),
            ('community_group_023',model.SCENE,model.ROOT_CHOICE),
            (model.EVENT,model.SCENE,model.SCENE+':choice:3')]
        with patch.object(model,'_verified_packet',side_effect=AssertionError('Must not scan')):
            for args in cases: self.assertIsNone(model.choice_reference(*args))

    def test_annotation_never_accepts_actual_dispatch_or_leave_choices(self):
        with patch.object(model,'_verified_packet',side_effect=AssertionError('Must not scan')):
            for key in (*model.CHOICES,model.ANNOTATION_SCENE+':choice:0',None,True):
                self.assertIsNone(model.annotation_reference(model.EVENT,model.ANNOTATION_SCENE,key))
            self.assertIsNone(model.annotation_reference(model.EVENT,model.SCENE,model.ANNOTATION_CHOICE))

    def test_item_details_only_accepts_source_choice_not_internal_or_rest(self):
        with patch.object(model,'_verified_packet',side_effect=AssertionError('Must not scan')):
            for key in (model.CHOICES[0],model.CHOICES[2],model.ANNOTATION_CHOICE,None,True):
                self.assertIsNone(model.item_details(model.EVENT,model.SCENE,key))

    def test_event_and_source_data_deepcopies_protect_full_expected_objects(self):
        packet = model.source_data(); packet['expected_event']['scenes'][0]['choices'][0]['title'] = '污染'
        packet['source_reference']['event_dom_bindings'][0]['scenes'].clear()
        packet['rows'][1]['dispatch_reference']['native_return_wordings'].clear()
        actual = self.event()
        self.assertEqual(actual['rows'][0]['choice_title'], '尝试探索树的内部')
        self.assertEqual(len(actual['source_reference']['event_dom_bindings'][0]['scenes']), 4)
        self.assertEqual(len(actual['rows'][1]['dispatch_reference']['native_return_wordings']), 2)

    def test_choice_and_item_copies_cannot_pollute_later_reads(self):
        row = self.root_choice(); row['source']['primary']['commit'] = '污染'
        row['documented_return_item']['name'] = '污染'
        details = self.item(); details['item']['usage'] = '污染'; details['icon_reference']['file'] = 'other.png'
        self.assertEqual(self.root_choice()['documented_return_item']['name'], '怦然信标')
        self.assertEqual(self.item()['item']['usage'], '所有敌人的生命+20%，我方单位的生命-40%，让探索开启不同的方向')

    def test_cached_full_object_mutation_fails_closed_instead_of_reusing_mutation(self):
        self.assertEqual(self.event()['status'], 'documented_reference')
        model._parsed_packet[2]['expected_event']['scenes'][0]['choices'][0]['sort_id'] = 1
        self.assertIsNone(model.source_data())
        self.assertEqual(self.event()['status'], 'source_unavailable')
        self.assertIsNone(self.item()['icon_reference'])

    def test_warm_manifest_failure_clears_every_public_target_and_recovers_without_old_data(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); self.clone(root)
            with patch.object(model,'ROOT',root):
                self.assertEqual(self.event()['status'], 'documented_reference')
                path = root/model.MANIFEST; original = path.read_bytes(); path.write_bytes(original+b' ')
                self.assertIsNone(model.source_data())
                failed = [self.event(),self.root_choice(),self.item(),
                    model.annotation_reference(model.EVENT,model.ANNOTATION_SCENE,model.ANNOTATION_CHOICE)]
                for result in failed:
                    self.assertEqual(result['status'], 'source_unavailable'); self.assertFalse(result['source_valid'])
                    self.assertEqual(result['rows'], []); self.assertIsNone(result['source'])
                    self.assertIsNone(result['item']); self.assertIsNone(result['icon_reference'])
                path.write_bytes(original)
                self.assertEqual(self.event()['status'], 'documented_reference')

    def test_warm_each_bound_source_file_is_rechecked_even_when_parsing_is_cached(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); manifest = self.clone(root)
            with patch.object(model,'ROOT',root):
                for name in manifest['files']:
                    with self.subTest(name=name):
                        self.assertEqual(self.event()['status'], 'documented_reference')
                        path = root/name; original = path.read_bytes()
                        path.write_bytes(original[:-1]+bytes([original[-1] ^ 1]))
                        self.assertEqual(self.event()['status'], 'source_unavailable')
                        self.assertIsNone(self.item()['icon_reference'])
                        path.write_bytes(original)
                self.assertEqual(self.event()['status'], 'documented_reference')

    def test_catalog_typed_mutation_is_not_accepted_after_warm_read(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); self.clone(root)
            with patch.object(model,'ROOT',root):
                self.assertEqual(self.event()['status'], 'documented_reference')
                path = root/'rouge/data/node-catalog.json'; packet = json.loads(path.read_bytes())
                event = next(row for row in packet['events'] if row['id']==model.EVENT)
                event['scenes'][0]['choices'][0]['game_choice_ids'] = ['choice_ro6_scout_3']
                path.write_text(json.dumps(packet,ensure_ascii=False),encoding='utf8')
                self.assertEqual(self.event()['status'], 'source_unavailable')
        self.assertFalse(model._same_json(True,1)); self.assertFalse(model._same_json([True],[1]))

    def test_runtime_does_not_read_large_primary_table_or_accept_override_evaluators(self):
        self.event()
        accessed = []
        original = model._source_path
        def observe(relative): accessed.append(relative); return original(relative)
        with patch.object(model,'_source_path',side_effect=observe): self.event()
        self.assertFalse(any('.cache' in path or 'roguelike_topic_table' in path for path in accessed))
        manifest = json.loads((model.ROOT/model.MANIFEST).read_bytes())
        self.assertEqual(set(accessed), {model.MANIFEST,*manifest['files']})
        self.assertFalse(manifest['runtime_reads_primary_table'])
        for function in (model.event_reference,model.choice_reference,model.annotation_reference,model.item_details,model.source_data):
            self.assertNotIn('data',inspect.signature(function).parameters)
            self.assertNotIn('evaluator',inspect.signature(function).parameters)
        with self.assertRaises(TypeError): model.event_reference(model.EVENT,data={})


if __name__ == '__main__': unittest.main()
