"""Named document references must not become source-scene or actual grants."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from rouge import event_named_reward_links as links

ROOT = Path(__file__).resolve().parents[1]
KEYS = ['community_group_007:scene:0:choice:0','community_group_007:scene:0:choice:1']
CIDS = ['choice_ro6_normal1_1','choice_ro6_normal1_2']


class EventNamedRewardLinkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.event = next(row for row in json.loads((ROOT/'rouge/data/node-catalog.json').read_text(encoding='utf-8'))['events']
                         if row['id'] == 'community_group_007')
        cls.rewards = json.loads((ROOT/'rouge/data/node-reward-reference.json').read_text(encoding='utf-8'))['event_rewards']
        cls.manifest = json.loads((ROOT/links.MANIFEST).read_text(encoding='utf-8'))

    def call(self,event=None,rewards=None):
        return links.event_named_reward_links(deepcopy(self.event) if event is None else event,
                                             deepcopy(self.rewards) if rewards is None else rewards)

    def clone(self, target):
        for relative in [links.MANIFEST,*self.manifest['files']]:
            path = target/relative
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_bytes((ROOT/relative).read_bytes())

    def test_two_documented_scrap_references_keep_all_actuals_unknown(self):
        result = self.call()
        self.assertEqual(result['status'],'documented_reference')
        self.assertTrue(result['source_valid'])
        self.assertEqual(list(result['links']),KEYS)
        for index,key in enumerate(KEYS):
            reference = result['links'][key]
            self.assertEqual(reference['original_choice_id'],CIDS[index])
            self.assertEqual(reference['reward_reference'],self.rewards[CIDS[index]])
            self.assertEqual(reference['reward_reference']['reward'],{
                'item_id':'rogue_6_scrap_G_12','name':'笼控器','type':'SCRAP',
                'quantity':None,'quantity_status':'not_serialized_in_display_data'})
            self.assertTrue(reference['content_link_verified'])
            self.assertFalse(reference['source_scene_link_verified'])
            self.assertFalse(reference['full_reward_pool_known'])
            for field in ('actual_claim_eligible','actual_reward','probability'):
                self.assertIsNone(reference[field])

    def test_different_options_keep_two_hp_and_eight_gold_separate(self):
        result = self.call()
        self.assertEqual([result['links'][key]['documented_cost_reference'] for key in KEYS],
            [{'resource':'hp','quantity':2,'actual_payment':None},
             {'resource':'gold','quantity':8,'actual_payment':None}])

    def test_unrelated_event_immediately_skips_source_without_io(self):
        class StringSubclass(str):
            pass
        class DictSubclass(dict):
            pass
        for event in ({'id':'community_group_008'},None,{},DictSubclass(self.event),
                      {'id':StringSubclass('community_group_007')},{'id':True}):
            with self.subTest(event=event),patch.object(links,'_validated_packet',side_effect=AssertionError('No source scan allowed')):
                result=links.event_named_reward_links(event,object())
                self.assertEqual(result['status'],'not_applicable')
                self.assertEqual(result['links'],{})
                self.assertIsNone(result['source_valid'])

    def test_target_name_without_complete_event_does_not_link(self):
        result=self.call({'id':'community_group_007','title':'沉寂之屋'})
        self.assertEqual(result['status'],'unknown')
        self.assertEqual(result['links'],{})
        self.assertEqual(result['reason_codes'],['catalog_event_content_mismatch'])

    def test_modified_scene_full_prose_rejects_both_rewards(self):
        event=deepcopy(self.event)
        event['scenes'][0]['description'] += '。'
        self.assertEqual(self.call(event)['links'],{})

    def test_modified_choice_result_does_not_strip_words_or_parentheses(self):
        event=deepcopy(self.event)
        event['scenes'][0]['choices'][0]['description']='消耗2目标生命值，获得笼控器'
        self.assertEqual(self.call(event)['links'],{})

    def test_modified_choice_key_or_scene_key_cannot_borrow_same_title(self):
        for field in ('choice','scene'):
            event=deepcopy(self.event)
            if field=='choice':
                event['scenes'][0]['choices'][0]['key']='other:choice'
            else:
                event['scenes'][0]['key']='other:scene'
            with self.subTest(field=field):
                self.assertEqual(self.call(event)['links'],{})

    def test_same_json_rejects_boolean_integer_aliases(self):
        event=deepcopy(self.event)
        event['scenes'][0]['choices'][0]['nested']=0
        self.assertEqual(self.call(event)['links'],{})

    def test_same_json_rejects_nested_object_subclasses(self):
        class DictSubclass(dict):
            pass
        event=deepcopy(self.event)
        event['scenes'][0]['choices'][0]=DictSubclass(event['scenes'][0]['choices'][0])
        self.assertEqual(self.call(event)['links'],{})

    def test_unrelated_future_scene_mutation_keeps_whole_event_unqualified(self):
        event=deepcopy(self.event)
        event['scenes'][-1]['description']+='额外未核对内容'
        self.assertEqual(self.call(event)['links'],{})

    def test_original_reward_item_type_quantity_or_id_mismatch_rejects_all(self):
        for field,value in [('type','RELIC'),('quantity',1),('item_id','another_item')]:
            rewards=deepcopy(self.rewards)
            rewards[CIDS[0]]['reward'][field]=value
            with self.subTest(field=field):
                result=self.call(rewards=rewards)
                self.assertEqual(result['links'],{})
                self.assertEqual(result['reason_codes'],['existing_reward_content_mismatch'])

    def test_missing_original_reward_and_mapping_subclass_reject(self):
        class DictSubclass(dict):
            pass
        missing=deepcopy(self.rewards)
        del missing[CIDS[1]]
        for rewards in (missing,DictSubclass(self.rewards),None,[]):
            with self.subTest(rewards_type=type(rewards).__name__):
                self.assertEqual(links.event_named_reward_links(deepcopy(self.event),rewards)['links'],{})

    def test_other_reward_does_not_affect_these_two_fixed_content_links(self):
        rewards=deepcopy(self.rewards)
        rewards['unrelated']={'reward':'unrelated'}
        self.assertEqual(self.call(rewards=rewards)['status'],'documented_reference')

    def test_no_input_or_existing_game_choice_id_mutation(self):
        event,rewards=deepcopy(self.event),deepcopy(self.rewards)
        before=(deepcopy(event),deepcopy(rewards))
        self.call(event,rewards)
        self.assertEqual((event,rewards),before)
        self.assertEqual([c['game_choice_ids'] for c in event['scenes'][0]['choices'][:2]],[[],[]])

    def test_returned_links_are_isolated_from_later_calls(self):
        result=self.call()
        result['links'][KEYS[0]]['reward_reference']['reward']['quantity']=100
        result['links'][KEYS[1]]['documented_cost_reference']['quantity']=100
        result['source']['bwiki']['revision']='changed'
        again=self.call()
        self.assertIsNone(again['links'][KEYS[0]]['reward_reference']['reward']['quantity'])
        self.assertEqual(again['links'][KEYS[1]]['documented_cost_reference']['quantity'],8)
        self.assertEqual(again['source']['bwiki']['revision'],'349818')

    def test_public_source_data_is_a_defensive_copy(self):
        data=links.source_data()
        data['expected_event']['title']='changed'
        data['expected_existing_rewards'][CIDS[0]]['reward']['type']='RELIC'
        self.assertEqual(links.source_data()['expected_event']['title'],'沉寂之屋')
        self.assertEqual(self.call()['status'],'documented_reference')

    def test_warm_call_does_not_hide_changes_in_any_manifest_file(self):
        for relative in self.manifest['files']:
            with self.subTest(relative=relative),tempfile.TemporaryDirectory(prefix='rouge-289-public-') as tmp:
                clone=Path(tmp)
                self.clone(clone)
                with patch.object(links,'ROOT',clone):
                    self.assertEqual(self.call()['status'],'documented_reference')
                    path=clone/relative
                    path.write_bytes(path.read_bytes()+b' ')
                    result=self.call()
                    self.assertEqual(result['status'],'unknown')
                    self.assertEqual(result['links'],{})
                    self.assertFalse(result['source_valid'])
                    self.assertIsNone(links.source_data())

    def test_missing_source_file_does_not_use_previous_valid_parse(self):
        with tempfile.TemporaryDirectory(prefix='rouge-289-public-') as tmp:
            clone=Path(tmp)
            self.clone(clone)
            with patch.object(links,'ROOT',clone):
                self.assertEqual(self.call()['status'],'documented_reference')
                (clone/'research/p3-event-named-rewards-289/original-records.json').unlink()
                result=self.call()
                self.assertEqual(result['links'],{})
                self.assertEqual(result['reason_codes'],['fixed_source_unverified'])

    def test_invalid_manifest_after_warm_read_is_unknown(self):
        with tempfile.TemporaryDirectory(prefix='rouge-289-public-') as tmp:
            clone=Path(tmp)
            self.clone(clone)
            with patch.object(links,'ROOT',clone):
                self.assertEqual(self.call()['status'],'documented_reference')
                (clone/links.MANIFEST).write_bytes(b'{invalid')
                result=self.call()
                self.assertFalse(result['source_valid'])
                self.assertIsNone(result['source'])
                self.assertEqual(result['links'],{})

    def test_source_and_evaluator_cannot_be_injected_through_public_api(self):
        for keyword in ('source','source_data','evaluator','actual_reward'):
            with self.subTest(keyword=keyword),self.assertRaises(TypeError):
                links.event_named_reward_links(self.event,self.rewards,**{keyword:{'forged':True}})

    def test_selected_original_pointer_and_literal_result_are_source_bound(self):
        data=links.source_data()
        self.assertEqual(data['sources']['bwiki']['revision'],'349818')
        self.assertEqual(data['sources']['fixed_catalog']['revision'],'427904')
        for index,key in enumerate(KEYS):
            ref=data['links'][key]['source_reference']
            self.assertEqual(ref['original_item_pointer'],f'$.details.rogue_6.choices.{CIDS[index]}.displayData.itemId')
            self.assertFalse(ref['original_source_scene_pointer_verified'])
            self.assertFalse(ref['destination_used_to_infer_origin'])

    def test_builder_reproduces_saved_package_without_writing(self):
        path=ROOT/'scripts/build_event_named_reward_links_289.py'
        spec=importlib.util.spec_from_file_location('event_named_289_builder',path)
        builder=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(builder)
        outputs=builder.build(ROOT)
        self.assertEqual(set(outputs),{'rouge/data/event-named-reward-links.json',
            'research/p3-event-named-rewards-289/extraction.json',
            'research/p3-event-named-rewards-289/source-manifest.json'})
        for relative,raw in outputs.items():
            self.assertEqual((ROOT/relative).read_bytes(),raw)


if __name__ == '__main__':
    unittest.main()
