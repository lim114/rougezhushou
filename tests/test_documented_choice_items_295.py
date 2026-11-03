"""Exact documented item identities, actual unknowns and fresh source guards."""
from copy import deepcopy
import inspect
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
from rouge import documented_choice_items as model


class DocumentedChoiceItemsTests(unittest.TestCase):
    def refs(self):return model.event_item_references(model.EVENT)
    def details(self):return model.item_details(model.EVENT,model.SCENE,model.CHOICE,model.ITEM)

    def clone(self,root):
        manifest=json.loads((model.ROOT/model.MANIFEST).read_text(encoding='utf-8'))
        for relative in [model.MANIFEST,*manifest['files']]:
            target=root/relative;target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(model.ROOT/relative,target)

    def test_one_exact_documented_item_is_not_a_typed_grant(self):
        result=self.refs();self.assertEqual(result['status'],'documented_reference');self.assertTrue(result['source_valid'])
        self.assertEqual(len(result['items']),1);ref=result['items'][0]
        self.assertEqual((ref['event_id'],ref['scene_key'],ref['choice_key'],ref['item_id']),
            (model.EVENT,model.SCENE,model.CHOICE,model.ITEM))
        self.assertEqual((ref['name'],ref['item_type'],ref['item_kind_name']),('沙盘α','RELIC','收藏品'))
        self.assertEqual(ref['reference_kind'],'documented_named_item')
        self.assertFalse(ref['original_item_pointer_present']);self.assertFalse(ref['original_choice_entry_bound'])
        self.assertIsNone(ref['quantity_reference']);self.assertIsNone(ref['actual_reward'])

    def test_null_original_pointer_is_preserved_not_filled_from_document(self):
        data=model.source_data();self.assertEqual(data['expected_event']['scenes'][0]['choices'][0]['game_choice_ids'],[])
        manifest=json.loads((model.ROOT/model.MANIFEST).read_text(encoding='utf-8'))
        path=next(name for name in manifest['files'] if name.endswith('/original-records.json'))
        original=json.loads((model.ROOT/path).read_text(encoding='utf-8'))
        self.assertIsNone(original['choice']['displayData']['itemId'])
        self.assertEqual(original['choice']['displayData']['type'],'NORMAL')
        self.assertEqual(original['item']['id'],model.ITEM)
        self.assertEqual(data['reference']['original_choice_content_reference'],'choice_ro6_bomb1_1')
        self.assertFalse(data['source_reference']['source_scene_link_verified'])

    def test_complete_item_details_retain_usage_description_and_unlock_original(self):
        result=self.details();self.assertEqual(result['status'],'documented_reference')
        item=result['item'];self.assertEqual(item['id'],model.ITEM);self.assertEqual(item['type'],'RELIC')
        self.assertEqual(item['usage'],'我方单位部署费用+2，让探索开启不同的方向，同时持有【沙盘β】可以揭示源阶方的所在位置')
        self.assertIn('来自梅兰德基金会',item['description'])
        self.assertEqual(item['unlockCondDesc'],'完成游戏结局')
        self.assertIn('不等于本事件的完整出现条件',result['unlock_notice'])
        self.assertIsNone(result['actual_selectable'])

    def test_both_complete_prts_versions_explicitly_name_and_identify_the_item(self):
        data=model.source_data();bindings=data['source_reference']['dom_bindings']
        self.assertEqual([b['revision'] for b in bindings],['427904','440271','349818'])
        for binding in bindings[:2]:
            evidence=binding['evidence'];self.assertEqual(evidence['choice_attributes']['data-iconid'],model.ITEM)
            self.assertIn('获得收藏品沙盘α',evidence['choice_description'])
            self.assertEqual(evidence['event_notes'],['本事件在未进入时会在同一局探索中重复出现。'])
            self.assertIsNone(evidence['choice_condition'])
            self.assertFalse(evidence['full_game_and_prts_descriptions_identical'])
        self.assertTrue(bindings[2]['evidence']['full_original_title_and_result_match'])
        self.assertTrue(all(not b['source_scene_link_verified'] for b in bindings))

    def test_actual_quantity_eligibility_current_server_and_inventory_remain_unknown(self):
        for result in (self.refs(),self.details()):
            for key in ('quantity_reference','actual_reward','actual_quantity','actual_selectable'):self.assertIsNone(result[key])
            self.assertFalse(result['source_scene_link_verified']);self.assertFalse(result['current_server_verified'])
            self.assertFalse(result['inventory_updated'])
            self.assertNotIn('can_claim',result);self.assertNotIn('grant',result)

    def test_non_target_and_typed_subclass_skip_every_source_read(self):
        class Text(str):pass
        with patch.object(model,'_validated_packet',side_effect=AssertionError('Do not scan unrelated sources')):
            for event in (None,False,21,{},'线人','community_group_007',Text(model.EVENT)):
                self.assertIsNone(model.event_item_references(event))
                self.assertIsNone(model.item_details(event,model.SCENE,model.CHOICE,model.ITEM))

    def test_cross_choice_scene_or_item_never_falls_back_to_this_item(self):
        class Text(str):pass
        cases=[(model.SCENE,model.SCENE+':choice:1',model.ITEM),
            (model.EVENT+':scene:1',model.CHOICE,model.ITEM),(model.SCENE,model.CHOICE,'沙盘α'),
            (model.SCENE,model.CHOICE,'rogue_6_relic_final_2'),(False,model.CHOICE,model.ITEM),
            (model.SCENE,Text(model.CHOICE),model.ITEM),(model.SCENE,model.CHOICE,Text(model.ITEM))]
        with patch.object(model,'_validated_packet',side_effect=AssertionError('Validate full identity first')):
            for scene,choice,item in cases:
                with self.subTest(scene=scene,choice=choice,item=item),self.assertRaises(ValueError):
                    model.item_details(model.EVENT,scene,choice,item)

    def test_every_bound_file_is_rehashed_after_a_warm_call_and_tamper_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);self.clone(root)
            with patch.object(model,'ROOT',root):
                self.assertEqual(self.refs()['status'],'documented_reference')
                manifest=json.loads((root/model.MANIFEST).read_text(encoding='utf-8'))
                for relative in [model.MANIFEST,*manifest['files']]:
                    path=root/relative;raw=path.read_bytes()
                    with self.subTest(relative=relative):
                        path.write_bytes(bytes([raw[0]^1])+raw[1:])
                        result=self.refs();self.assertEqual(result['status'],'unknown');self.assertFalse(result['source_valid'])
                        self.assertEqual(result['items'],[])
                        details=self.details();self.assertIsNone(details['item']);self.assertIsNone(details['icon_reference'])
                        path.write_bytes(raw)
                        self.assertEqual(self.refs()['status'],'documented_reference')

    def test_missing_bound_files_never_keep_old_details_or_icon(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);self.clone(root)
            with patch.object(model,'ROOT',root):
                self.assertEqual(self.details()['status'],'documented_reference')
                manifest=json.loads((root/model.MANIFEST).read_text(encoding='utf-8'))
                for relative in [model.MANIFEST,*manifest['files']]:
                    path=root/relative;raw=path.read_bytes();path.unlink()
                    with self.subTest(relative=relative):
                        self.assertIsNone(model.source_data());self.assertEqual(self.refs()['items'],[])
                        self.assertIsNone(self.details()['item']);self.assertIsNone(self.details()['sources'])
                    path.write_bytes(raw)

    def test_nested_result_mutations_do_not_pollute_later_queries(self):
        refs=self.refs();before=deepcopy(refs);refs['items'][0]['name']='changed'
        refs['items'][0]['icon_reference']['file']='other.png';refs['sources']['documents'].clear()
        details=self.details();details['item']['usage']='changed';details['reference']['choice_title']='changed'
        self.assertEqual(self.refs(),before);self.assertIn('部署费用+2',self.details()['item']['usage'])
        self.assertEqual(self.details()['reference']['choice_title'],'我受雇于梅兰德')

    def test_source_data_returns_defensive_copy(self):
        data=model.source_data();before=deepcopy(data);data['reference'].clear();data['expected_event']['scenes'].clear()
        self.assertEqual(model.source_data(),before)

    def test_parser_cache_never_caches_source_authenticity_or_reads_full_game_table(self):
        self.refs();manifest=json.loads((model.ROOT/model.MANIFEST).read_text(encoding='utf-8'))
        expected={model.ROOT/relative for relative in [model.MANIFEST,*manifest['files']]}
        seen=[];original=Path.read_bytes
        def read(path):seen.append(path);return original(path)
        with patch.object(Path,'read_bytes',new=read):
            self.assertEqual(self.refs()['status'],'documented_reference')
            self.assertEqual(self.details()['status'],'documented_reference')
        self.assertEqual(set(seen),expected)
        self.assertTrue(all(seen.count(path)==2 for path in expected))
        self.assertFalse(any('fixed-game-topic' in str(path) or 'roguelike_topic_table' in str(path) for path in seen))

    def test_icon_reference_binds_actual_existing_file_not_inferred_filename(self):
        ref=self.details()['icon_reference'];self.assertEqual(ref['item_id'],model.ITEM)
        self.assertEqual(ref['file'],'rouge/data/relic-icons/rogue_6_relic_final_1.png')
        self.assertEqual(ref['sha256'],'1d07a123253172ede9a4585abdcd1b301350e096b245bc046539c48f6c6fb825')
        self.assertEqual(ref['git_blob_sha1'],'874eb15d491afc7cd4c292816bff9e334eb2dab6')
        self.assertEqual(ref['bytes'],36076)

    def test_public_apis_do_not_accept_evaluator_or_source_payload_overrides(self):
        self.assertEqual(list(inspect.signature(model.event_item_references).parameters),['event_id'])
        self.assertEqual(list(inspect.signature(model.item_details).parameters),['event_id','scene_key','choice_key','item_id'])
        with self.assertRaises(TypeError):model.event_item_references(model.EVENT,source={})
        with self.assertRaises(TypeError):model.item_details(model.EVENT,model.SCENE,model.CHOICE,model.ITEM,data={})


if __name__=='__main__':unittest.main()
