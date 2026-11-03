"""One source-bound result annotation must not become an eligibility rule."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from rouge import choice_recruitment_results as model

ROOT=Path(__file__).resolve().parents[1]


class ChoiceRecruitmentResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog=json.loads((ROOT/'rouge/data/node-catalog.json').read_text(encoding='utf-8'))
        cls.event=next(e for e in cls.catalog['events'] if e['id']=='community_group_018')
        cls.scene=cls.event['scenes'][0]
        cls.choice=cls.scene['choices'][1]
        cls.manifest=json.loads((ROOT/model.MANIFEST).read_text(encoding='utf-8'))

    def call(self,choice=None,**kwargs):
        return model.choice_reference('community_group_018',deepcopy(self.choice) if choice is None else choice,**kwargs)

    def clone(self,target):
        for relative in [model.MANIFEST,*self.manifest['files']]:
            path=target/relative
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_bytes((ROOT/relative).read_bytes())

    def test_four_complete_profession_pairs_keep_distinct_original_choices(self):
        result=self.call()
        self.assertEqual(result['status'],'documented_reference')
        self.assertEqual(result['annotation_role'],'selection_result')
        self.assertEqual([r['profession_pair'] for r in result['variants']],
            [['先锋','近卫'],['重装','辅助'],['医疗','狙击'],['术师','特种']])
        self.assertEqual([r['original_choice_id'] for r in result['variants']],
            ['choice_ro6_hire1_1','choice_ro6_hire1_4','choice_ro6_hire1_5','choice_ro6_hire1_6'])

    def test_two_hope_one_recruit_five_star_ceiling_is_single_reference(self):
        result=self.call()
        self.assertTrue(result['variants_are_alternatives'])
        self.assertEqual((result['hope_gain_reference'],result['recruit_count_reference'],
                          result['rarity_ceiling_reference'],result['upgrade_reference_text']),(2,1,5,'直升'))
        for row in result['variants']:
            self.assertEqual((row['hope_gain_reference'],row['recruit_count_reference'],
                              row['rarity_ceiling_reference'],row['upgrade_reference_text']),(2,1,5,'直升'))
        self.assertNotIn('total_hope_from_variants',result)

    def test_appearance_and_all_actual_result_fields_stay_unknown(self):
        result=self.call()
        for field in ('actual_selectable','actual_result_variant','actual_recruited_operator',
                      'actual_hope_gain','actual_cultivation','actual_granted','recruitment_cost'):
            self.assertIsNone(result[field])
        self.assertFalse(result['original_entry_scene_verified'])
        self.assertFalse(result['source_scene_link_verified'])
        self.assertFalse(result['full_recruitment_pool_known'])
        self.assertFalse(result['current_server_verified'])
        for row in result['variants']:
            self.assertFalse(row['original_entry_scene_verified'])
            for field in ('recruitment_cost','actual_granted','actual_operator','actual_cultivation'):
                self.assertIsNone(row[field])

    def test_raw_original_records_preserve_text_without_converting_upgrade(self):
        result=self.call()
        for row in result['variants']:
            self.assertEqual(row['original_record']['id'],row['original_choice_id'])
            self.assertIn('直升的5星及以下',row['description'])
            self.assertIn('<@ro6.get>2</>',row['original_record']['description'])
            self.assertNotIn('actual_level',row)
            self.assertNotIn('actual_elite',row)

    def test_input_choice_and_catalog_game_choice_ids_are_not_modified(self):
        choice=deepcopy(self.choice)
        before=deepcopy(choice)
        self.call(choice)
        self.assertEqual(choice,before)
        self.assertEqual(choice['game_choice_ids'],[])
        self.assertEqual(self.choice['game_choice_ids'],[])

    def test_explicit_correct_scene_matches_default_scene_localization(self):
        self.assertEqual(self.call(),self.call(scene_key='community_group_018:scene:0'))

    def test_wrong_identity_or_subclass_never_scans_source(self):
        class S(str):pass
        class D(dict):pass
        entries=[('other',self.choice),('community_group_018',{}),
                 (S('community_group_018'),self.choice),('community_group_018',D(self.choice)),
                 ('community_group_018',{**self.choice,'key':S(model.CHOICE)}),
                 ('community_group_018',{**self.choice,'key':'community_group_018:scene:0:choice:0'})]
        with patch.object(model,'_validated_packet',side_effect=AssertionError('Must skip source')):
            for event,choice in entries:
                with self.subTest(event=event,key=choice.get('key')):
                    self.assertIsNone(model.choice_reference(event,choice))

    def test_wrong_explicit_scene_immediately_returns_none(self):
        with patch.object(model,'_validated_packet',side_effect=AssertionError('Must skip source')):
            for key in ('community_group_018:scene:1',False,1,[]):
                with self.subTest(key=key):
                    self.assertIsNone(self.call(scene_key=key))

    def test_other_catalog_choices_do_not_read_source_or_gain_annotation(self):
        count=0
        with patch.object(model,'_validated_packet',side_effect=AssertionError('Unrelated source read')):
            for event in self.catalog['events']:
                for scene in event['scenes']:
                    for choice in scene['choices']:
                        if event['id']==model.EVENT and choice['key']==model.CHOICE:continue
                        self.assertIsNone(model.choice_reference(event['id'],choice))
                        count+=1
        self.assertGreater(count,200)

    def test_same_key_with_changed_condition_keeps_unparsed_role(self):
        choice=deepcopy(self.choice)
        choice['conditional']='仅在持有笼控器时出现'
        result=self.call(choice)
        self.assertEqual(result['status'],'unknown')
        self.assertIsNone(result['annotation_role'])
        self.assertEqual(result['variants'],[])
        self.assertIsNone(result['hope_gain_reference'])

    def test_changed_result_title_or_fields_cannot_borrow_target_key(self):
        for field,value in [('title','合格的帮手应当仔细挑选'),('description','免费招募两名6星干员'),
                            ('game_choice_ids',['choice_ro6_hire1_1']),('new_field','injected')]:
            choice=deepcopy(self.choice)
            choice[field]=value
            with self.subTest(field=field):
                self.assertEqual(self.call(choice)['status'],'unknown')

    def test_typed_equality_rejects_bool_integer_and_nested_subclass(self):
        class D(dict):pass
        first=deepcopy(self.choice)
        first['nested']=0
        second=deepcopy(self.choice)
        second['attributes']=D(second['attributes'])
        for choice in (first,second):
            self.assertIsNone(self.call(choice)['annotation_role'])

    def test_missing_choice_field_keeps_unknown(self):
        choice=deepcopy(self.choice)
        del choice['conditional']
        result=self.call(choice)
        self.assertEqual(result['reason_codes'],['catalog_content_mismatch'])
        self.assertEqual(result['variants'],[])

    def test_mutated_current_complete_event_rejects_content_reference(self):
        event=deepcopy(self.event)
        event['scenes'][-1]['description']+='未核对变化'
        with patch.object(model.catalog,'_event',return_value=event):
            result=self.call()
        self.assertEqual(result['status'],'unknown')
        self.assertTrue(result['source_valid'])
        self.assertIsNone(result['annotation_role'])

    def test_mutated_current_scene_cannot_be_hidden_by_unchanged_event(self):
        scene=deepcopy(self.scene)
        scene['key']='other:scene'
        with patch.object(model.catalog,'_scene',return_value=scene):
            self.assertEqual(self.call()['status'],'unknown')

    def test_current_catalog_lookup_failure_preserves_unknown_result(self):
        with patch.object(model.catalog,'_event',side_effect=ValueError('unknown current event')):
            result=self.call()
        self.assertIsNone(result['annotation_role'])
        self.assertEqual(result['reason_codes'],['catalog_content_mismatch'])

    def test_result_mutation_cannot_pollute_future_calls(self):
        result=self.call()
        result['variants'][0]['profession_pair'][0]='changed'
        result['variants'][1]['original_record']['description']='changed'
        result['source']['bwiki']['revision']='changed'
        result['source_reference']['prts_dom_bindings']['427904']['desc2']='changed'
        again=self.call()
        self.assertEqual(again['variants'][0]['profession_pair'],['先锋','近卫'])
        self.assertIn('重装或辅助',again['variants'][1]['original_record']['description'])
        self.assertEqual(again['source']['bwiki']['revision'],'349818')
        self.assertEqual(again['source_reference']['prts_dom_bindings']['427904']['desc2'],self.choice['conditional'])

    def test_public_source_data_is_a_defensive_copy(self):
        data=model.source_data()
        data['expected_event']['title']='changed'
        data['variants'].clear()
        self.assertEqual(model.source_data()['expected_event']['title'],'临时中介所')
        self.assertEqual(len(self.call()['variants']),4)

    def test_every_manifest_file_is_freshly_checked_after_warm_call(self):
        for relative in self.manifest['files']:
            with self.subTest(relative=relative),tempfile.TemporaryDirectory(prefix='rouge-290-public-') as tmp:
                clone=Path(tmp)
                self.clone(clone)
                with patch.object(model,'ROOT',clone):
                    self.assertEqual(self.call()['status'],'documented_reference')
                    path=clone/relative
                    path.write_bytes(path.read_bytes()+b' ')
                    result=self.call()
                    self.assertEqual(result['status'],'unknown')
                    self.assertFalse(result['source_valid'])
                    self.assertIsNone(result['annotation_role'])
                    self.assertEqual(result['variants'],[])
                    self.assertIsNone(model.source_data())

    def test_missing_original_source_does_not_reuse_warm_parse(self):
        with tempfile.TemporaryDirectory(prefix='rouge-290-public-') as tmp:
            clone=Path(tmp)
            self.clone(clone)
            with patch.object(model,'ROOT',clone):
                self.assertEqual(self.call()['status'],'documented_reference')
                (clone/'research/p3-choice-recruitment-290/original-records.json').unlink()
                result=self.call()
                self.assertEqual(result['reason_codes'],['fixed_source_unverified'])
                self.assertEqual(result['variants'],[])

    def test_invalid_manifest_after_valid_read_is_unknown(self):
        with tempfile.TemporaryDirectory(prefix='rouge-290-public-') as tmp:
            clone=Path(tmp)
            self.clone(clone)
            with patch.object(model,'ROOT',clone):
                self.assertEqual(self.call()['status'],'documented_reference')
                (clone/model.MANIFEST).write_bytes(b'not json')
                result=self.call()
                self.assertFalse(result['source_valid'])
                self.assertIsNone(result['source'])
                self.assertIsNone(result['annotation_role'])

    def test_source_and_evaluator_have_no_public_override(self):
        for key in ('source','data','source_data','evaluator','actual_result'):
            with self.subTest(key=key),self.assertRaises(TypeError):
                model.choice_reference(model.EVENT,self.choice,**{key:{}})

    def test_both_prts_versions_and_four_bwiki_full_cells_are_retained(self):
        result=self.call()
        self.assertEqual(set(result['source_reference']['prts_dom_bindings']),{'427904','440271'})
        for revision,dom in result['source_reference']['prts_dom_bindings'].items():
            self.assertEqual(dom['scene_attributes']['data-index'],'101')
            self.assertEqual(dom['choice_attributes'],self.choice['attributes'])
            self.assertEqual(dom['desc1'],self.choice['description'])
            self.assertEqual(dom['desc2'],self.choice['conditional'])
        for row in result['variants']:
            evidence=row['source_reference']['bwiki_full_text_match']
            self.assertEqual(' '.join(evidence['cell_text'].split()),
                row['original_record']['title']+' '+row['description'])
            self.assertFalse(row['source_reference']['source_scene_inferred_from_destination'])

    def test_original_entry_punctuation_difference_does_not_create_scene_edge(self):
        result=self.call()
        difference=result['source_reference']['entry_prose_difference_retained']
        self.assertNotEqual(difference['original'],difference['community'])
        self.assertIn('......',difference['original'])
        self.assertIn('……',difference['community'])
        self.assertFalse(difference['source_scene_edge_proven'])
        self.assertFalse(result['original_entry_scene_verified'])

    def test_builder_reproduces_all_saved_outputs_without_writing(self):
        script=ROOT/'scripts/build_choice_recruitment_results_290.py'
        spec=importlib.util.spec_from_file_location('choice_recruitment_builder',script)
        builder=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(builder)
        outputs=builder.build(ROOT)
        self.assertEqual(set(outputs),{'rouge/data/choice-recruitment-results.json',
            'research/p3-choice-recruitment-290/extraction.json',
            'research/p3-choice-recruitment-290/source-manifest.json'})
        for relative,raw in outputs.items():self.assertEqual((ROOT/relative).read_bytes(),raw)


if __name__=='__main__':unittest.main()
