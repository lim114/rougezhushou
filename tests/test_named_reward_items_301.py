"""Exact fixed public item reading only; no Qt, game, account or run state."""
from copy import deepcopy
from hashlib import sha256,sha1
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
    explicit=os.environ.get('ROUGE_NAMED_REWARD_ITEMS_MODULE')
    if explicit:
        spec=importlib.util.spec_from_file_location('rouge._candidate_named_reward_items301',explicit)
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
    return importlib.import_module('rouge.named_reward_items')


class NamedRewardItemsTests(unittest.TestCase):
    subject=None

    @classmethod
    def setUpClass(cls):
        if cls.subject is None:cls.subject=load_subject()

    def setUp(self):
        self.subject._parsed_packet=None
        self.addCleanup(setattr,self.subject,'_parsed_packet',None)

    def event(self,event='community_group_005'):return self.subject.event_reference(event)

    def detail(self,event='community_group_005',choice=0,scene=0):
        scene_key=event+':scene:'+str(scene)
        return self.subject.item_details(event,scene_key,scene_key+':choice:'+str(choice))

    def clone(self,root):
        manifest=json.loads((self.subject.ROOT/self.subject.MANIFEST).read_bytes())
        for relative in(self.subject.MANIFEST,*manifest['files']):
            target=root/relative;target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(self.subject.ROOT/relative,target)
        return manifest

    def actual_unknown(self,result):
        expected={'actual_reward','actual_quantity','actual_claimed','actual_held','actual_effect','actual_eligible'}
        self.assertEqual({k for k in result if k.startswith('actual_')},expected)
        for key in expected:self.assertIsNone(result[key])

    def test_all_sixteen_exact_choices_cover_ten_events_and_thirteen_items(self):
        choices=[];items=set()
        for event in self.subject.EVENT_IDS:
            packet=self.event(event);self.assertTrue(packet['source_valid'])
            self.assertEqual([r['choice_key']for r in packet['choices']],list(self.subject.CHOICE_KEYS[event]))
            for row in packet['choices']:
                details=self.subject.item_details(event,row['scene_key'],row['choice_key'])
                self.assertTrue(details['source_valid']);self.assertEqual(details['reference'],row)
                self.assertEqual(details['item']['id'],row['item_id'])
                self.assertEqual(details['icon_reference']['icon_id'],details['item']['iconId'])
                choices.append((event,row['scene_key'],row['choice_key']));items.add(row['item_id'])
        self.assertEqual(len(choices),16);self.assertEqual(len(set(choices)),16)
        self.assertEqual(len(items),13);self.assertEqual(len(self.subject.EVENT_IDS),10)

    def test_literal_item_identities_and_scrap_kind_are_not_name_guesses(self):
        expected={'rogue_6_relic_fight_11':'他缚','rogue_6_relic_legacy_142':'“剑锤”','rogue_6_relic_legacy_141':'一串钱伥',
            'rogue_6_relic_fight_18':'翱翼','rogue_6_relic_fight_19':'虬蜕','rogue_6_scrap_G_12':'笼控器',
            'rogue_6_relic_cargo_12':'猎印','rogue_6_relic_artifact_4':'犬植浆','rogue_6_relic_artifact_5':'追忆',
            'rogue_6_relic_cargo_11':'厄运火杆','rogue_6_relic_cargo_10':'同行者',
            'rogue_6_relic_final_4':'击坠“神明”','rogue_6_relic_final_6':'焚毁“文明”'}
        actual={r['item_id']:r['name']for event in self.subject.EVENT_IDS for r in self.event(event)['choices']}
        self.assertEqual(actual,expected)
        scrap=self.detail('community_group_007');self.assertIsNone(scrap['relic'])
        self.assertEqual(scrap['reference']['item_kind'],'SCRAP');self.assertEqual(scrap['reference']['item_kind_name'],'零件')

    def test_complete_items_relics_and_original_choices_equal_fixed_primary(self):
        source=json.loads((self.subject.ROOT/'research/p3-future-region-effects-300/game-topic-complete.json').read_bytes())['details']['rogue_6']
        for event in self.subject.EVENT_IDS:
            for row in self.event(event)['choices']:
                details=self.subject.item_details(event,row['scene_key'],row['choice_key'])
                self.assertEqual(details['item'],source['items'][row['item_id']])
                self.assertEqual(details['relic'],source['relics'].get(row['item_id']))
                self.assertEqual(row['original_choice'],source['choices'][row['original_choice_id']])
                self.assertTrue(details['item']['usage']);self.assertTrue(details['item']['description'])

    def test_same_item_different_conditions_and_full_choices_are_not_merged(self):
        cage=self.event('community_group_007')['choices']
        self.assertEqual(len(cage),2);self.assertEqual(len({r['item_id']for r in cage}),1)
        self.assertNotEqual(cage[0]['condition_text'],cage[1]['condition_text'])
        self.assertEqual([r['catalog_choice']['game_choice_ids']for r in cage],[[],[]])
        memory=self.event('community_group_011')['choices']
        self.assertEqual(len(memory),3);self.assertEqual(len({r['item_id']for r in memory}),1)
        self.assertEqual(len({r['condition_text']for r in memory}),3)
        self.assertEqual(len({r['reference_id']for r in memory}),3)

    def test_noninitial_scene_seventeen_and_nine_are_exactly_addressable(self):
        resin=self.detail('community_group_010',scene=17)
        civilization=self.detail('community_group_025',scene=9)
        self.assertEqual(resin['item']['name'],'犬植浆');self.assertEqual(civilization['item']['name'],'焚毁“文明”')
        self.assertIsNone(self.detail('community_group_010',scene=0))
        self.assertIsNone(self.detail('community_group_025',scene=0))

    def test_quantities_actual_eligibility_claim_inventory_and_effect_remain_unknown(self):
        for event in self.subject.EVENT_IDS:
            packet=self.event(event);self.actual_unknown(packet);self.assertFalse(packet['inventory_updated'])
            for row in packet['choices']:
                self.assertIsNone(row['quantity_reference']);self.actual_unknown(row)
                details=self.subject.item_details(event,row['scene_key'],row['choice_key'])
                self.actual_unknown(details);self.assertFalse(details['inventory_updated'])
                self.assertIn('不证明当前选项',details['unlock_notice'])

    def test_unbound_ticket_and_old_special_readers_are_excluded_without_source_io(self):
        with patch.object(self.subject,'_verified_packet',side_effect=AssertionError('Unexpected source I/O')):
            for event in('community_group_003','community_group_021','community_group_024','金色凝滞',None,{},True):
                self.assertIsNone(self.subject.event_reference(event))
            self.assertIsNone(self.subject.item_details('community_group_003','choice_ro6_rest_4','choice_ro6_rest_4'))

    def test_invalid_full_tuples_titles_aliases_cross_event_and_types_return_none(self):
        event='community_group_005';scene=event+':scene:0';choice=scene+':choice:0'
        with patch.object(self.subject,'_verified_packet',side_effect=AssertionError('Invalid tuple performed I/O')):
            for args in((event,scene,'他缚'),(event,scene,'choice_ro6_relic1_1'),(event,'scene0',choice),
                    ('community_group_006',scene,choice),(event,scene,True),(event,None,choice),(False,scene,choice)):
                self.assertIsNone(self.subject.item_details(*args))

    def test_no_source_data_evaluator_context_or_item_id_injection(self):
        for field in('source','data','evaluator','context','item_id','source_valid'):
            with self.assertRaises(TypeError):self.subject.event_reference('community_group_005',**{field:{}})
            with self.assertRaises(TypeError):self.subject.item_details('community_group_005','x','x',**{field:{}})

    def test_all_thirteen_original_icons_match_sha_and_git_blob(self):
        seen=set()
        for event in self.subject.EVENT_IDS:
            for row in self.event(event)['choices']:
                details=self.subject.item_details(event,row['scene_key'],row['choice_key']);icon=details['icon_reference']
                raw=(self.subject.ROOT/icon['file']).read_bytes()
                self.assertEqual(sha256(raw).hexdigest(),icon['sha256'])
                self.assertEqual(sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest(),icon['git_blob_sha1'])
                self.assertEqual(Path(icon['file']).name,details['item']['iconId']+'.png')
                self.assertEqual(icon['source']['commit'],'d0b5af0b004b044d322397ce5ae79632b6d9fcdd')
                seen.add(icon['item_id'])
        self.assertEqual(len(seen),13)

    def test_event_and_details_are_defensive_copies(self):
        first=self.event();first['choices'][0]['catalog_choice']['description']='bad'
        first['source']['game_commit']='bad'
        details=self.detail();details['item']['usage']='bad';details['relic']['buffs']=[]
        details['icon_reference']['source']['url']='bad';details['reference']['conditions'].append({'fake':True})
        self.assertNotEqual(self.detail()['item']['usage'],'bad')
        self.assertNotEqual(self.event()['choices'][0]['catalog_choice']['description'],'bad')
        self.assertNotIn({'fake':True},self.detail()['reference']['conditions'])

    def test_complete_current_catalog_event_including_unselected_last_scene_is_checked(self):
        from rouge import node_catalog
        event='community_group_010';changed=deepcopy(node_catalog._event(event))
        changed['scenes'][-1]['attributes']['data-name']='wrong unselected scene'
        with patch.object(node_catalog,'_event',return_value=changed):
            self.assertFalse(self.event(event)['source_valid'])

    def test_complete_current_typed17_including_unbound_ticket_is_checked(self):
        from rouge import node_rewards
        changed=deepcopy(node_rewards._reference())
        changed['event_rewards']['choice_ro6_rest_4']['description']='corrupt unrelated original record'
        with patch.object(node_rewards,'_reference',return_value=changed):
            self.assertFalse(self.event()['source_valid'])

    def test_current_reward_query_complete_object_is_not_replaced_by_title_match(self):
        from rouge import node_catalog
        changed=deepcopy(node_catalog.event_reward_options('community_group_005'))
        changed['notice']='corrupt extra field'
        with patch.object(node_catalog,'event_reward_options',return_value=changed):
            self.assertFalse(self.event()['source_valid'])

    def test_typed_comparison_rejects_false_replaced_by_integer_zero(self):
        from rouge import node_catalog
        changed=deepcopy(node_catalog.event_reward_options('community_group_005'))
        self.assertIs(changed['inventory_updated'],False);changed['inventory_updated']=0
        with patch.object(node_catalog,'event_reward_options',return_value=changed):
            self.assertFalse(self.event()['source_valid'])

    def test_warm_cache_choice_icon_source_and_expected_snapshots_are_guarded(self):
        for mutate in(lambda p:p['choices'][0].update(name='wrong'),
                lambda p:p['icons']['rogue_6_relic_fight_11'].update(file='wrong.png'),
                lambda p:p['source'].update(game_commit='wrong'),
                lambda p:p['expected_reward_queries']['community_group_005'].update(notice='wrong')):
            self.subject._parsed_packet=None;self.assertTrue(self.event()['source_valid'])
            mutate(self.subject._parsed_packet[2])
            result=self.event();self.assertFalse(result['source_valid']);self.assertEqual(result['choices'],[])

    def test_coordinated_cached_expected_event_and_legacy_mutation_cannot_self_validate(self):
        from rouge import node_catalog
        self.assertTrue(self.event()['source_valid'])
        cache=self.subject._parsed_packet[2]
        cache['expected_events']['community_group_005']['description']='coordinated'
        changed=deepcopy(cache['expected_events']['community_group_005'])
        with patch.object(node_catalog,'_event',return_value=changed):
            self.assertFalse(self.event()['source_valid'])

    def test_every_runtime_file_mutation_fails_closed_after_valid_full_clone(self):
        with tempfile.TemporaryDirectory(prefix='rouge-named301-')as directory:
            root=Path(directory);manifest=self.clone(root)
            with patch.object(self.subject,'ROOT',root):
                self.subject._parsed_packet=None;self.assertTrue(self.event()['source_valid'])
                for relative in(self.subject.MANIFEST,*manifest['runtime_files']):
                    with self.subTest(file=relative):
                        file=root/relative;original=file.read_bytes();file.write_bytes(original+b' ')
                        self.assertFalse(self.event()['source_valid']);self.assertIsNone(self.detail()['item'])
                        file.write_bytes(original);self.assertTrue(self.event()['source_valid'])

    def test_every_runtime_missing_file_fails_closed_and_recovers_without_old_contents(self):
        with tempfile.TemporaryDirectory(prefix='rouge-named301-')as directory:
            root=Path(directory);manifest=self.clone(root)
            with patch.object(self.subject,'ROOT',root):
                self.subject._parsed_packet=None;self.assertTrue(self.event()['source_valid'])
                for relative in(self.subject.MANIFEST,*manifest['runtime_files']):
                    with self.subTest(file=relative):
                        file=root/relative;original=file.read_bytes();file.unlink()
                        result=self.detail();self.assertFalse(result['source_valid'])
                        for key in('reference','item','relic','icon_reference','source','source_reference','unlock_notice'):self.assertIsNone(result[key])
                        file.write_bytes(original);self.assertTrue(self.event()['source_valid'])

    def test_each_of_thirteen_icons_invalidates_whole_package_not_just_one_event(self):
        with tempfile.TemporaryDirectory(prefix='rouge-named301-')as directory:
            root=Path(directory);self.clone(root)
            data=json.loads((root/self.subject.DATA).read_bytes())
            with patch.object(self.subject,'ROOT',root):
                self.subject._parsed_packet=None;self.assertTrue(self.event()['source_valid'])
                for icon in data['icons'].values():
                    file=root/icon['file'];raw=file.read_bytes();file.write_bytes(raw+b'x')
                    for event in self.subject.EVENT_IDS:self.assertFalse(self.event(event)['source_valid'])
                    file.write_bytes(raw);self.assertTrue(self.event()['source_valid'])

    def test_runtime_never_reads_complete_primary_or_build_only_authorities(self):
        manifest=json.loads((self.subject.ROOT/self.subject.MANIFEST).read_bytes());seen=[];original=self.subject._source_path
        def tracked(name):
            seen.append(name)
            if name in manifest['build_authority_files']:raise AssertionError('Build-only hot-path read')
            return original(name)
        with patch.object(self.subject,'_source_path',side_effect=tracked):
            self.assertTrue(self.event()['source_valid']);self.assertTrue(self.detail()['source_valid'])
        self.assertEqual(set(seen),set(manifest['runtime_files'])|{self.subject.MANIFEST})

    def test_all_thirtyeight_original_reward_queries_and_original17_remain_equal(self):
        from rouge import node_catalog,node_rewards
        baseline=json.loads((self.subject.ROOT/'research/p3-named-reward-items-301/prior-38-reward-query-baseline.json').read_bytes())
        self.assertEqual(len(baseline['queries']),38);self.assertEqual(len(node_rewards._reference()['event_rewards']),17)
        before={event:node_catalog.event_reward_options(event)for event in baseline['queries']}
        self.event();self.detail('community_group_007')
        after={event:node_catalog.event_reward_options(event)for event in baseline['queries']}
        self.assertEqual(before,baseline['queries']);self.assertEqual(after,before)

    def test_default_readonly_builder_recreates_all_three_outputs_without_modification(self):
        root=self.subject.ROOT;paths=[root/self.subject.DATA,root/self.subject.MANIFEST,root/self.subject.SELECTED_AUTHORITY]
        before=[p.read_bytes()for p in paths]
        result=subprocess.run([sys.executable,'-B','-X','utf8',str(root/'scripts/build_named_reward_items_301.py')],cwd=root,capture_output=True,check=False)
        self.assertEqual(result.returncode,0,result.stderr.decode('utf8'))
        self.assertEqual([p.read_bytes()for p in paths],before)
        report=json.loads(result.stdout);self.assertFalse(report['write']);self.assertTrue(report['prior38_query_values_reconstructed_unchanged'])
        self.assertEqual(report['data_sha256'],self.subject.DATA_SHA256)

    def test_scope_is_source_and_event_bound_not_reward_title_or_item_name(self):
        first=self.event('community_group_005');second=self.event('community_group_006')
        self.assertNotEqual(first['scope_key'],second['scope_key'])
        self.assertIn(self.subject.DATA_SHA256,first['scope_key']);self.assertIn(self.subject.MANIFEST_SHA256,first['scope_key'])
        self.assertEqual(self.event('community_group_005')['scope_key'],first['scope_key'])


if __name__=='__main__':unittest.main(verbosity=2)
