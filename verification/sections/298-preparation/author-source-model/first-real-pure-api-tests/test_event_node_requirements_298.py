"""Literal source restrictions and scope/unknown/freshness boundaries."""
from copy import deepcopy
import hashlib
import inspect
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
from rouge import event_node_requirements as model


class EventNodeRequirementsTests(unittest.TestCase):
    def setUp(self):
        self.previous=model._parsed_packet;model._parsed_packet=None
        self.addCleanup(setattr,model,'_parsed_packet',self.previous)

    def query(self,event='community_group_024',**context):return model.event_requirements(event,**context)
    def clone(self,root):
        manifest=json.loads((model.ROOT/model.MANIFEST).read_bytes())
        for path in [model.MANIFEST,*manifest['files']]:
            destination=root/path;destination.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(model.ROOT/path,destination)
        return manifest

    def test_six_exact_identities_with_literal_node_types_and_restrictions(self):
        gold={
            'community_group_024':('未涉足之树','先行一步',[1,5,6]),
            'community_group_025':('回滚文明','失与得',[1,6]),
            'community_group_027':('溯源','误入奇境',[1,2,6]),
            'community_group_028':('原始娱乐','狭路相逢',[1,2,6]),
            'community_group_029':('掠夺成性','狭路相逢',[1,2,6]),
            'community_group_037':('金色凝滞','安全的角落',[1])}
        self.assertEqual(set(model.source_data()['events']),set(gold))
        for identity,(name,kind,excluded) in gold.items():
            result=self.query(identity)
            self.assertEqual((result['event_name'],result['node_type'],result['documented_excluded_main_floors']),
                             (name,kind,excluded));self.assertEqual(result['status'],'documented_reference')

    def test_complete_six_by_six_main_floor_matrix_uses_literal_expected_exclusion(self):
        forbidden={'community_group_024':{1,5,6},'community_group_025':{1,6},'community_group_027':{1,2,6},
                   'community_group_028':{1,2,6},'community_group_029':{1,2,6},'community_group_037':{1}}
        for event,excluded in forbidden.items():
            for floor in range(1,7):
                with self.subTest(event=event,floor=floor):
                    result=self.query(event,floor=floor,entry_mode='natural')
                    self.assertIs(result['context_applicable'],True)
                    self.assertIs(result['documented_floor_match'],floor not in excluded)
                    self.assertIs(result['check']['matches'],floor not in excluded)
                    self.assertEqual(result['qualification_status_reference'],'excluded' if floor in excluded else 'unknown')
                    self.assertIsNone(result['actual_server_eligible'])

    def test_default_unknown_entry_does_not_apply_a_floor_exclusion(self):
        result=self.query(floor=6)
        self.assertFalse(result['context_applicable']);self.assertIsNone(result['documented_floor_match'])
        self.assertIsNone(result['check']['matches']);self.assertEqual(result['qualification_status_reference'],'unknown')
        self.assertEqual(result['documented_excluded_main_floors'],[1,5,6])

    def test_unknown_floor_is_not_the_first_or_sixth_main_floor(self):
        result=self.query(entry_mode='natural')
        self.assertTrue(result['context_applicable']);self.assertIsNone(result['documented_floor_match'])
        self.assertIsNone(result['context']['floor']);self.assertEqual(result['qualification_status_reference'],'unknown')

    def test_content_processed_unknown_and_history_modes_preserve_references_without_constraint(self):
        for event in model.EVENT_RULES:
            for mode in ('content','processed_item','unknown','history'):
                with self.subTest(event=event,mode=mode):
                    result=self.query(event,floor=1,entry_mode=mode)
                    self.assertFalse(result['context_applicable']);self.assertIsNone(result['documented_floor_match'])
                    self.assertIsNone(result['check']['matches']);self.assertTrue(result['source_valid'])
                    self.assertTrue(result['source_reference']['source_text'])

    def test_special_region_does_not_inherit_main_floor_rules(self):
        for event in model.EVENT_RULES:
            result=self.query(event,floor=1,entry_mode='natural',special_region=True)
            self.assertFalse(result['context_applicable']);self.assertIsNone(result['documented_floor_match'])
            self.assertIsNone(result['check']['matches']);self.assertEqual(result['qualification_status_reference'],'unknown')

    def test_explicit_history_flag_prevents_natural_constraint_without_losing_source(self):
        result=self.query(floor=6,entry_mode='natural',historical=True)
        self.assertFalse(result['context_applicable']);self.assertIsNone(result['documented_floor_match'])
        self.assertEqual(result['documented_excluded_main_floors'],[1,5,6]);self.assertIsNotNone(result['source'])

    def test_allowed_main_floor_never_becomes_an_overall_matched_eligibility(self):
        result=self.query(floor=2,entry_mode='natural')
        self.assertTrue(result['documented_floor_match']);self.assertEqual(result['qualification_status_reference'],'unknown')
        self.assertIsNone(result['actual_server_eligible']);self.assertIsNone(result['actual_node'])
        self.assertIsNone(result['probability']);self.assertFalse(result['current_server_verified'])
        self.assertFalse(result['original_entry_restored']);self.assertFalse(result['inventory_updated'])

    def test_two_exact_technology_objects_are_enabling_paths_not_negative_gates(self):
        gold={'community_group_024':('rogue_6_outbuff_9','眼睛','探险中会出现“先行一步”节点'),
              'community_group_027':('rogue_6_outbuff_7','育儿袋','探险中会出现“误入奇境”节点')}
        for event,(identity,name,description) in gold.items():
            reference=self.query(event,floor=3,entry_mode='natural')['technology_enabling_reference']
            self.assertEqual((reference['development_id'],reference['name'],reference['rawDesc']),(identity,name,[description]))
            self.assertEqual(reference['role'],'known_enabling_path_only')
            self.assertFalse(reference['necessary_negative_gate_proven']);self.assertFalse(reference['inactive_hard_exclusion_supported'])
            self.assertIsNone(reference['actual_account_active'])
        self.assertIsNone(self.query('community_group_025')['technology_enabling_reference'])
        with self.assertRaises(TypeError):self.query(technology_active=False)

    def test_complete_native_node_and_development_records_are_preserved(self):
        primary=json.loads((model.ROOT/'research/p3-event-node-requirements-298/original-records.json').read_bytes())
        self.assertEqual(set(primary['developments']),{'rogue_6_outbuff_7','rogue_6_outbuff_9'})
        self.assertEqual(len(primary['nodeTypeData']),5)
        eyes=primary['developments']['rogue_6_outbuff_9']
        self.assertEqual(eyes['frontNodeId'],['rogue_6_outbuff_6']);self.assertEqual(eyes['nodeType'],'KEY')
        self.assertEqual(eyes['effectType'],'RAW_TEXT_EFFECT');self.assertIsNone(eyes['enrollId'])

    def test_029_missing_own_type_is_not_faked_as_a_direct_declared_type(self):
        result=self.query('community_group_029');expected=result['expected_event']
        self.assertNotIn('data-etype',expected['scenes'][0]['attributes'])
        for binding in result['source_reference']['event_dom_bindings']:
            proof=binding['node_type_binding']
            self.assertEqual(proof['kind'],'inherited_previous_declared_type')
            self.assertEqual(proof['declaring_scene_complete_attributes']['data-name'],'原始娱乐')
            self.assertEqual(proof['declaring_scene_complete_attributes']['data-index'],'152')
            self.assertEqual(proof['declaring_scene_complete_attributes']['data-etype'],'狭路相逢')
            self.assertFalse(proof['source_scene_entry_script_proven'])

    def test_other_five_event_groups_have_direct_declared_dom_type_and_two_full_versions(self):
        for identity in ('community_group_024','community_group_025','community_group_027','community_group_028','community_group_037'):
            row=self.query(identity);bindings=row['source_reference']['event_dom_bindings']
            self.assertEqual([r['revision'] for r in bindings],['427904','440271'])
            for binding in bindings:
                self.assertEqual(binding['node_type_binding']['kind'],'direct_declared_type')
                self.assertEqual(binding['node_type_binding']['declaring_scene_complete_attributes']['data-etype'],row['node_type'])
                self.assertEqual(binding['scene_count'],len(row['expected_event']['scenes']))

    def test_each_floor_rule_keeps_exact_own_heading_and_full_description_list(self):
        groups=model.source_data()['main_node_groups']
        self.assertEqual(len(groups),5)
        gold={'安全的角落':'※该节点不会在第I层出现','先行一步':'※该节点不会在第I，V，VI层出现。',
              '失与得':'※该节点不会在第I，VI层出现。','狭路相逢':'※该节点不会在第I，II，VI层出现。',
              '误入奇境':'※该节点不会在第I，II，VI层出现。'}
        for group in groups:
            self.assertEqual(group['header']['tag'],'ul');self.assertEqual(group['complete_description_list']['tag'],'dl')
            self.assertIn(gold[group['node_type']],group['paragraphs'])
            self.assertEqual(group['restriction_wording'],gold[group['node_type']])

    def test_non_target_values_never_scan_source_even_with_irrelevant_invalid_context(self):
        class Subclass(str):pass
        with patch.object(model,'_verified_packet',side_effect=AssertionError('Must not read sources')):
            for value in (None,True,1,[],{},'未涉足之树','community_group_023','community_group_031',Subclass('community_group_024')):
                self.assertIsNone(model.event_requirements(value,floor=True,special_region=1))

    def test_target_context_rejects_bool_numeric_floor_and_untyped_region_history(self):
        invalid=[{'floor':True},{'floor':False},{'floor':1.0},{'floor':'1'},{'floor':0},{'floor':7},
                 {'special_region':1},{'special_region':None},{'historical':1},{'historical':None},
                 {'entry_mode':None},{'entry_mode':True},{'entry_mode':'NATURAL'},{'entry_mode':'other'}]
        with patch.object(model,'_verified_packet',side_effect=AssertionError('Context validation precedes source reads')):
            for context in invalid:
                with self.subTest(context=context),self.assertRaises(ValueError):self.query(**context)

    def test_public_outputs_are_deep_independent_full_objects(self):
        packet=model.source_data();packet['expected_events']['community_group_024']['scenes'][0]['description']='污染'
        packet['main_node_groups'][0]['paragraphs'].clear()
        result=self.query();result['expected_event']['scenes'][0]['choices'].clear()
        result['source_reference']['event_dom_bindings'][0]['complete_group']['children'].clear()
        again=self.query();self.assertEqual(len(again['expected_event']['scenes'][0]['choices']),3)
        self.assertTrue(again['source_reference']['event_dom_bindings'][0]['complete_group']['children'])
        self.assertTrue(model.source_data()['main_node_groups'][0]['paragraphs'])

    def test_mutated_internal_cached_full_event_fails_closed(self):
        self.assertEqual(self.query()['status'],'documented_reference')
        model._parsed_packet[2]['expected_events']['community_group_024']['scenes'][0]['description']='污染'
        self.assertIsNone(model.source_data());failed=self.query(floor=6,entry_mode='natural')
        self.assertEqual(failed['status'],'source_unavailable');self.assertIsNone(failed['check'])
        self.assertIsNone(failed['documented_floor_match']);self.assertEqual(failed['qualification_status_reference'],'unknown')

    def test_warm_manifest_failure_discards_old_exclusion_and_restoration_is_source_only(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);self.clone(root)
            with patch.object(model,'ROOT',root):
                self.assertFalse(self.query(floor=6,entry_mode='natural')['documented_floor_match'])
                path=root/model.MANIFEST;original=path.read_bytes();path.write_bytes(original+b' ')
                failed=self.query(floor=6,entry_mode='natural')
                self.assertEqual(failed['status'],'source_unavailable');self.assertIsNone(failed['source'])
                self.assertIsNone(failed['expected_event']);self.assertIsNone(failed['check'])
                self.assertEqual(failed['documented_excluded_main_floors'],[])
                self.assertIsNone(failed['documented_floor_match']);self.assertIsNone(model.source_data())
                path.write_bytes(original);self.assertFalse(self.query(floor=6,entry_mode='natural')['documented_floor_match'])

    def test_all_bound_files_are_rehashed_after_a_warm_query(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);manifest=self.clone(root)
            with patch.object(model,'ROOT',root):
                for name in manifest['files']:
                    with self.subTest(file=name):
                        self.assertEqual(self.query()['status'],'documented_reference')
                        path=root/name;original=path.read_bytes();path.write_bytes(original[:-1]+bytes([original[-1]^1]))
                        failed=self.query(floor=1,entry_mode='natural')
                        self.assertEqual(failed['status'],'source_unavailable');self.assertIsNone(failed['documented_floor_match'])
                        path.write_bytes(original)

    def test_changed_catalog_identity_does_not_reuse_current_parsed_reference(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);self.clone(root)
            with patch.object(model,'ROOT',root):
                self.assertEqual(self.query()['status'],'documented_reference')
                path=root/'rouge/data/node-catalog.json';data=json.loads(path.read_bytes())
                event=next(r for r in data['events'] if r['id']=='community_group_024');event['node_types']=['安全的角落']
                path.write_text(json.dumps(data,ensure_ascii=False),encoding='utf8')
                self.assertEqual(self.query()['status'],'source_unavailable')
        self.assertFalse(model._same_json([1],[True]));self.assertFalse(model._same_json(1,1.0))

    def test_no_catalog_import_no_evaluator_or_data_override_and_no_large_table_runtime_read(self):
        source=Path(model.__file__).read_text(encoding='utf8')
        self.assertNotIn('import node_catalog',source);self.assertNotIn('from .node_catalog',source)
        self.query();accessed=[];original=model._source_path
        def observe(name):accessed.append(name);return original(name)
        with patch.object(model,'_source_path',side_effect=observe):self.query(floor=3,entry_mode='natural')
        manifest=json.loads((model.ROOT/model.MANIFEST).read_bytes())
        self.assertEqual(set(accessed),{model.MANIFEST,*manifest['files']})
        self.assertFalse(any('.cache/' in name or 'roguelike_topic_table' in name for name in accessed))
        self.assertNotIn('data',inspect.signature(model.event_requirements).parameters)
        with self.assertRaises(TypeError):self.query(data={})
        with self.assertRaises(TypeError):self.query(evaluator=lambda x:True)


if __name__=='__main__':unittest.main()
