"""UNEXECUTED formal draft: canonical public source helper; no GUI or private state."""
from copy import deepcopy
import importlib.util
from rouge import peace_guardian_results as model
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
# Formal draft: canonical module import above; source packet must be promoted first.


class PeaceGuardianCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog=json.loads((ROOT/'rouge/data/node-catalog.json').read_text(encoding='utf-8'))
        cls.event=next(e for e in cls.catalog['events'] if e['id']=='community_group_019')
        cls.scene=cls.event['scenes'][1]
        cls.move=cls.scene['choices'][0]
        cls.mark=cls.scene['choices'][1]
        cls.manifest=json.loads((ROOT/model.MANIFEST).read_text(encoding='utf-8'))

    def call(self,event=None,scene=None,choice=None):
        return model.choice_result_reference(deepcopy(self.event) if event is None else event,
            deepcopy(self.scene) if scene is None else scene,deepcopy(self.move) if choice is None else choice)

    def clone(self,target):
        for relative in [model.MANIFEST,*self.manifest['files']]:
            path=target/relative
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_bytes((ROOT/relative).read_bytes())

    def test_source_and_helper_root_are_canonical_public_project(self):
        self.assertEqual(model.ROOT,ROOT)
        self.assertEqual(model.__name__,'rouge.peace_guardian_results')
        self.assertNotIn('rouge.node_catalog',model.__dict__)
        self.assertEqual(model.__file__,str(ROOT/'rouge/peace_guardian_results.py'))

    def test_literal_move_result_is_exact_and_only_one_way(self):
        result=self.call()
        self.assertEqual(result['status'],'documented_reference')
        self.assertEqual(result['annotation_role'],'selection_result')
        self.assertEqual(result['base_action_reference']['description'],'立即前往最近的“居民”据点')
        exception=result['completion_exception_reference']
        self.assertEqual(exception['condition_text'],'若已完成当前层的【“居民”据点】作战则不会移动')
        self.assertTrue(exception['one_way_implication'])
        self.assertFalse(exception['documented_movement_if_condition_matches'])
        self.assertIsNone(exception['condition_matches'])
        self.assertFalse(exception['converse_verified'])
        self.assertFalse(exception['negation_implies_successful_movement_verified'])

    def test_actual_completion_position_move_and_battle_remain_unknown(self):
        result=self.call()
        for field in ('actual_current_floor_completion','actual_target_node_id','actual_moved',
                      'actual_battle_triggered','actual_position_after'):
            self.assertIsNone(result[field])
        self.assertFalse(result['source_scene_link_verified'])
        self.assertFalse(result['complete_movement_result_known'])
        self.assertNotIn('probability',result)
        self.assertNotIn('target_candidates',result)
        self.assertFalse(result['base_action_reference']['nearest_selection_algorithm_known'])

    def test_mark_option_is_separate_and_does_not_inherit_exception(self):
        result=self.call()
        mark=result['related_option_reference']
        self.assertEqual(mark['choice_key'],'community_group_019:scene:1:choice:1')
        self.assertEqual(mark['action_kind'],'mark_nearest_resident_post')
        self.assertEqual(mark['description'],'仅标记地图上最近的“居民”据点，暂不前往')
        self.assertEqual(mark['original_record']['type'],'VISION')
        self.assertFalse(mark['move_exception_inherited'])
        with patch.object(model,'_validated_packet',side_effect=AssertionError('Only MOVE applies')):
            self.assertIsNone(self.call(choice=deepcopy(self.mark)))

    def test_prts_exception_evidence_is_not_mislabeled_as_bwiki_or_official(self):
        result=self.call()
        reference=result['source_reference']
        self.assertEqual(set(reference['prts_dom_bindings']),{'427904','440271'})
        self.assertFalse(reference['exception_in_bwiki'])
        self.assertFalse(reference['exception_in_original_choices'])
        self.assertEqual(result['source']['bwiki']['role'],'two_base_results_only')
        self.assertIn('same-family',result['completion_exception_reference']['evidence_scope'])

    def test_complete_dom_and_independent_two_base_results_are_retained(self):
        result=self.call()
        for dom in result['source_reference']['prts_dom_bindings'].values():
            self.assertEqual(dom['scene_attributes']['data-index'],'106')
            self.assertEqual(dom['scene_attributes'],self.scene['attributes'])
            self.assertEqual(dom['scene_description'],self.scene['description'])
            self.assertEqual([r['attributes'] for r in dom['choices']],
                             [self.move['attributes'],self.mark['attributes']])
            self.assertEqual(dom['choices'][0]['desc2'],self.move['conditional'])
            self.assertIsNone(dom['choices'][1]['desc2'])
        matches=result['source_reference']['bwiki_base_result_bindings']
        self.assertEqual([m['original_choice_id'] for m in matches],['choice_ro6_task1_3','choice_ro6_task1_4'])
        self.assertFalse(result['source_reference']['source_scene_inferred_from_destination'])

    def test_raw_null_destinations_do_not_create_entry_or_fixed_stage(self):
        data=model.source_data()
        self.assertEqual(data['original_record']['id'],'choice_ro6_task1_3')
        self.assertEqual(data['original_record']['type'],'MOVE')
        self.assertIsNone(data['original_record']['nextSceneId'])
        self.assertIsNone(data['related_option_reference']['original_record']['nextSceneId'])
        result=self.call()
        self.assertNotIn('stage_id',result)
        self.assertIsNone(result['actual_target_node_id'])

    def test_non_target_ids_and_subclasses_do_not_scan_sources(self):
        class S(str):pass
        class D(dict):pass
        inputs=[({'id':'other'},self.scene,self.move),(self.event,{'key':'other'},self.move),
            (self.event,self.scene,{'key':'other'}),(D(self.event),self.scene,self.move),
            ({**self.event,'id':S(model.EVENT)},self.scene,self.move),
            (self.event,self.scene,{**self.move,'key':S(model.CHOICE)})]
        with patch.object(model,'_validated_packet',side_effect=AssertionError('Not applicable')):
            for event,scene,choice in inputs:
                self.assertIsNone(model.choice_result_reference(event,scene,choice))

    def test_all_other_choices_are_not_reclassified(self):
        count=0
        with patch.object(model,'_validated_packet',side_effect=AssertionError('Unrelated source read')):
            for event in self.catalog['events']:
                for scene in event['scenes']:
                    for choice in scene['choices']:
                        if choice['key']==model.CHOICE:continue
                        self.assertIsNone(model.choice_result_reference(event,scene,choice))
                        count+=1
        self.assertGreater(count,200)

    def test_full_event_and_scene_mutations_cannot_use_same_keys(self):
        event=deepcopy(self.event)
        event['scenes'][0]['description']+='changed'
        scene=deepcopy(self.scene)
        scene['description']+='changed'
        for result in (self.call(event=event),self.call(scene=scene)):
            self.assertEqual(result['status'],'unknown')
            self.assertTrue(result['source_valid'])
            self.assertIsNone(result['annotation_role'])
            self.assertIsNone(result['completion_exception_reference'])

    def test_changed_condition_or_base_result_cannot_be_normalized_back(self):
        for field,value in [('conditional','若未完成当前层据点则一定移动'),
                            ('description','立即前往最近居民据点'),('title','守卫和平')]:
            choice=deepcopy(self.move)
            choice[field]=value
            result=self.call(choice=choice)
            self.assertEqual(result['reason_codes'],['catalog_content_mismatch'])
            self.assertIsNone(result['annotation_role'])

    def test_typed_bool_int_and_nested_object_subclass_rejected(self):
        class D(dict):pass
        first=deepcopy(self.move)
        first['nested']=0
        second=deepcopy(self.move)
        second['attributes']=D(second['attributes'])
        for choice in (first,second):
            self.assertIsNone(self.call(choice=choice)['annotation_role'])

    def test_declaration_fields_cannot_be_inserted_into_choice(self):
        for field in ('completed_declared','visited','battle_completed','actual_moved'):
            choice=deepcopy(self.move)
            choice[field]=True
            result=self.call(choice=choice)
            self.assertEqual(result['status'],'unknown')
            self.assertIsNone(result['actual_current_floor_completion'])
            self.assertIsNone(result['actual_moved'])

    def test_no_public_state_map_source_or_evaluator_override(self):
        for key in ('completion','completion_declaration','graph','source','data','evaluator'):
            with self.subTest(key=key),self.assertRaises(TypeError):
                model.choice_result_reference(self.event,self.scene,self.move,**{key:True})

    def test_input_catalog_and_existing_original_ids_are_not_changed(self):
        event,scene,choice=deepcopy(self.event),deepcopy(self.scene),deepcopy(self.move)
        before=deepcopy((event,scene,choice))
        model.choice_result_reference(event,scene,choice)
        self.assertEqual((event,scene,choice),before)
        self.assertEqual(choice['game_choice_ids'],['choice_ro6_task1_3'])

    def test_result_and_source_copies_cannot_pollute_next_call(self):
        result=self.call()
        result['completion_exception_reference']['condition_matches']=True
        result['source_reference']['exception_in_bwiki']=True
        result['related_option_reference']['original_record']['type']='MOVE'
        again=self.call()
        self.assertIsNone(again['completion_exception_reference']['condition_matches'])
        self.assertFalse(again['source_reference']['exception_in_bwiki'])
        self.assertEqual(again['related_option_reference']['original_record']['type'],'VISION')
        packet=model.source_data()
        packet['expected_choice']['conditional']='changed'
        self.assertEqual(model.source_data()['expected_choice']['conditional'],self.move['conditional'])

    def test_warm_calls_recheck_every_cached_public_file(self):
        for relative in self.manifest['files']:
            with self.subTest(relative=relative),tempfile.TemporaryDirectory(prefix='rouge-291-cache-') as directory:
                clone=Path(directory)
                self.clone(clone)
                with patch.object(model,'ROOT',clone):
                    self.assertEqual(self.call()['status'],'documented_reference')
                    path=clone/relative
                    path.write_bytes(path.read_bytes()+b' ')
                    result=self.call()
                    self.assertEqual(result['status'],'unknown')
                    self.assertFalse(result['source_valid'])
                    self.assertIsNone(result['annotation_role'])
                    self.assertIsNone(result['completion_exception_reference'])
                    self.assertIsNone(model.source_data())

    def test_missing_cached_source_or_invalid_manifest_rejects_warm_parse(self):
        for failure in ('missing_original','invalid_manifest'):
            with tempfile.TemporaryDirectory(prefix='rouge-291-cache-') as directory:
                clone=Path(directory)
                self.clone(clone)
                with patch.object(model,'ROOT',clone):
                    self.assertEqual(self.call()['status'],'documented_reference')
                    if failure=='missing_original':
                        (clone/'research/p3-peace-guardian-results-291/original-records.json').unlink()
                    else:
                        (clone/model.MANIFEST).write_bytes(b'invalid manifest')
                    result=self.call()
                    self.assertEqual(result['reason_codes'],['fixed_source_unverified'])
                    self.assertIsNone(result['source'])
                    self.assertIsNone(result['annotation_role'])

    def test_builder_reproduces_cached_outputs_only(self):
        path=ROOT/'scripts/build_peace_guardian_results_291.py'
        spec=importlib.util.spec_from_file_location('cache_peace_builder',path)
        builder=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(builder)
        outputs=builder.build(ROOT)
        self.assertEqual(set(outputs),{'rouge/data/peace-guardian-results.json',
            'research/p3-peace-guardian-results-291/extraction.json',
            'research/p3-peace-guardian-results-291/source-manifest.json'})
        for relative,raw in outputs.items():self.assertEqual((ROOT/relative).read_bytes(),raw)


if __name__=='__main__':unittest.main()
