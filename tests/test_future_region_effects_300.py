"""Public fixed-source/conditional API contracts; no game, state, Qt or network."""
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
    explicit = os.environ.get('ROUGE_FUTURE_REGION_MODULE')
    if explicit:
        spec = importlib.util.spec_from_file_location('rouge._candidate_future_region_effects_300', explicit)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    return importlib.import_module('rouge.future_region_effects')


class FutureRegionEffectsTests(unittest.TestCase):
    subject = None

    @classmethod
    def setUpClass(cls):
        if cls.subject is None: cls.subject = load_subject()

    def setUp(self):
        self.subject._parsed_packet = None
        self.addCleanup(setattr, self.subject, '_parsed_packet', None)

    def query(self, **context):
        return self.subject.event_reference('community_group_009', **context)

    def clone(self, root):
        manifest = json.loads((self.subject.ROOT/self.subject.MANIFEST).read_bytes())
        for relative in [self.subject.MANIFEST, *manifest['files']]:
            target = root/relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(self.subject.ROOT/relative, target)
        return manifest

    def assert_unknown_actual(self, packet):
        exact = {'actual_choice','actual_weather','actual_phase','actual_affected_nodes','actual_reward','actual_quantity'}
        self.assertEqual({k for k in packet if k.startswith('actual_')}, exact)
        for key in exact: self.assertIsNone(packet[key])

    def test_exact_two_choices_preserve_full_identity_and_absent_original_entry(self):
        result = self.query()
        self.assertTrue(result['source_valid'])
        self.assertEqual(result['status'], 'documented_reference')
        self.assertEqual(result['event_title'], '呼吸的红苔')
        self.assertEqual([r['choice_key'] for r in result['choices']], [
            'community_group_009:scene:0:choice:0','community_group_009:scene:0:choice:1'])
        self.assertEqual([r['reference_id'] for r in result['choices']], [r['choice_key'] for r in result['choices']])
        self.assertEqual(result['choices'][0]['game_choice_ids'], [])
        self.assertEqual(result['choices'][1]['game_choice_ids'], ['choice_ro6_normal3_2'])
        self.assertEqual([r['primary_choice_id'] for r in result['choices']], ['choice_ro6_normal3_1','choice_ro6_normal3_2'])
        self.assertTrue(all(r['entry_restored'] is False for r in result['choices']))
        self.assertIsNone(result['documented_phase'])

    def test_three_alternatives_have_literal_attack_hp_and_complete_raw_records(self):
        result = self.query()
        self.assertEqual([(p['phase'],p['attack_percent'],p['max_hp_percent']) for p in result['phases']],
            [('early',10,10),('middle',15,20),('late',20,30)])
        self.assertEqual([(p['normal_difficulty_min'],p['normal_difficulty_max']) for p in result['phases']], [(2,5),(6,11),(12,15)])
        for phase in result['phases']:
            self.assertEqual(phase['raw']['functionDesc'], phase['source_text'])
            self.assertEqual(phase['raw']['name'], '“希望的沃土”')
            self.assertIn('sound', phase['raw'])
        for row in result['choices']:
            self.assertEqual(row['future_region_reference']['phases'], result['phases'])
            self.assertEqual(row['future_region_reference']['effect_phase'], 'next_region')
        self.assertIn('不相加',result['notice'])

    def test_immediate_gold_and_seed_are_separate_from_future_and_victory_reward(self):
        first,second = self.query()['choices']
        self.assertEqual({k:first['direct_resources'][0][k] for k in ('resource','quantity_reference','action','effect_phase')},
            {'resource':'gold','quantity_reference':30,'action':'gain','effect_phase':'on_choice'})
        self.assertEqual({k:second['direct_resources'][0][k] for k in ('resource','quantity_reference','action','effect_phase')},
            {'resource':'seed','quantity_reference':1,'action':'sow','effect_phase':'on_choice'})
        for row in (first,second):
            reward=row['conditional_victory_reward']
            self.assertEqual(reward['resource'],'random_scrap')
            self.assertIn('战斗胜利后',reward['condition'])
            for key in ('quantity_reference','complete_pool','actual_received'): self.assertIsNone(reward[key])

    def test_NORMAL_all_sixteen_difficulties_use_documented_ranges_only(self):
        expected=[None,None,'early','early','early','early','middle','middle','middle','middle','middle','middle','late','late','late','late']
        for grade,phase in enumerate(expected):
            with self.subTest(grade=grade):
                result=self.query(mode='NORMAL',difficulty=grade)
                self.assertEqual(result['documented_phase'],phase)
                self.assertEqual(len(result['choices']),2)
                self.assertEqual(len(result['phases']),3)
                self.assert_unknown_actual(result)

    def test_non_NORMAL_modes_do_not_borrow_normal_phase(self):
        for mode in ('MONTH_TEAM','CAMPAIGN','normal','',None,True,1,{}):
            with self.subTest(mode=mode):
                result=self.query(mode=mode,difficulty=12)
                self.assertIsNone(result['documented_phase'])
                self.assertEqual(result['context']['mode'],mode if type(mode)is str else None)
                self.assertEqual(len(result['phases']),3)

    def test_invalid_difficulty_is_unknown_without_calling_user_equality(self):
        class Hostile:
            def __eq__(self,other): raise AssertionError('Caller equality must not run.')
        for value in (None,True,False,2.0,15.0,'2',-1,16,{},[],Hostile()):
            with self.subTest(value=type(value).__name__):
                result=self.query(mode='NORMAL',difficulty=value)
                self.assertIsNone(result['documented_phase'])
                self.assertEqual(result['context']['difficulty'],value if type(value)is int else None)

    def test_scope_identity_is_source_bound_and_context_independent(self):
        base=self.query()
        for mode,grade in (('NORMAL',2),('NORMAL',12),('MONTH_TEAM',9),(None,None)):
            result=self.query(mode=mode,difficulty=grade)
            self.assertEqual(result['scope_key'],base['scope_key'])
            self.assertEqual(result['source_identity']['data_sha256'],self.subject.DATA_SHA256)
        self.assertIn(self.subject.MANIFEST_SHA256,base['scope_key'])

    def test_actual_fields_and_state_or_calculation_are_never_claimed(self):
        result=self.query(mode='NORMAL',difficulty=15)
        self.assert_unknown_actual(result)
        for row in result['choices']: self.assert_unknown_actual(row)
        self.assertFalse(result['calculation_applied'])
        self.assertFalse(result['run_state_updated'])
        self.assertTrue(result['context']['phase_reference_only'])

    def test_supplemental_pairing_and_limit_are_not_execution_or_gate(self):
        result=self.query(mode='NORMAL',difficulty=0)
        supplement=result['supplemental_documentation']
        self.assertEqual(supplement['source_role'],'supplemental_documentation_only')
        self.assertTrue(supplement['community_pairing_documented'])
        self.assertFalse(supplement['execution_pair_binding_proven'])
        self.assertFalse(supplement['force_limit_semantics_verified'])
        self.assertFalse(supplement['fixed_full_HTML_acquired'])
        self.assertEqual(len(result['choices']),2)
        self.assertIsNone(result['documented_phase'])
        self.assertNotIn('eligible',result)

    def test_non_targets_return_before_source_or_catalog_io(self):
        with patch.object(self.subject,'_verified_packet',side_effect=AssertionError('Unexpected source read')):
            for event_id in (None,True,9,{},'呼吸的红苔','community_group_023','community_group_009:scene:0'):
                self.assertIsNone(self.subject.event_reference(event_id))

    def test_public_api_rejects_source_data_or_evaluator_injection(self):
        for key in ('source','data','evaluator','source_valid','phase','context'):
            with self.subTest(key=key):
                with self.assertRaises(TypeError): self.subject.event_reference('community_group_009',**{key:{}})

    def test_public_results_and_source_packet_are_defensive_copies(self):
        result=self.query()
        result['choices'][0]['catalog_choice']['description']='corrupt'
        result['choices'][0]['future_region_reference']['phases'][0]['raw']['name']='corrupt'
        result['source']['game']['commit']='corrupt'
        raw=self.subject.source_data()
        raw['expected_event']['scenes'][0]['choices'][0]['description']='corrupt'
        fresh=self.query()
        self.assertEqual(fresh['phases'][0]['raw']['name'],'“希望的沃土”')
        self.assertIn('30源石锭',fresh['choices'][0]['catalog_choice']['description'])
        self.assertEqual(fresh['source']['game']['commit'],'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add')

    def test_complete_live_cached_catalog_object_is_independently_checked(self):
        from rouge import node_catalog
        original=node_catalog._event('community_group_009')
        poisoned=deepcopy(original)
        poisoned['scenes'][3]['attributes']['data-name']='wrong-last-scene'
        with patch.object(node_catalog,'_event',return_value=poisoned):
            self.assertFalse(self.query()['source_valid'])
        self.assertTrue(self.query()['source_valid'])

    def test_typed_catalog_match_rejects_false_to_integer_zero(self):
        from rouge import node_catalog
        poisoned=deepcopy(node_catalog._event('community_group_009'))
        self.assertIs(poisoned['scenes'][0]['choices'][0]['server_option_availability_verified'],False)
        poisoned['scenes'][0]['choices'][0]['server_option_availability_verified']=0
        with patch.object(node_catalog,'_event',return_value=poisoned):
            self.assertFalse(self.query()['source_valid'])

    def test_warm_internal_choice_and_source_snapshot_corruption_fails_closed(self):
        for mutate in (
                lambda p:p['choices'][0].update(choice_title='wrong'),
                lambda p:p['source']['events'][0].update(revision='wrong'),
                lambda p:p['source_reference']['complete_primary_weather'][2].update(sound='wrong')):
            self.subject._parsed_packet=None
            self.assertTrue(self.query()['source_valid'])
            mutate(self.subject._parsed_packet[2])
            result=self.query()
            self.assertFalse(result['source_valid'])
            self.assertEqual(result['choices'],[])
            self.assertIsNone(result['source'])

    def test_internal_expected_event_plus_legacy_co_tamper_is_rejected(self):
        from rouge import node_catalog
        self.assertTrue(self.query()['source_valid'])
        packet=self.subject._parsed_packet[2]
        packet['expected_event']['description']='coordinated wrong value'
        poisoned=deepcopy(packet['expected_event'])
        with patch.object(node_catalog,'_event',return_value=poisoned):
            self.assertFalse(self.query()['source_valid'])

    def test_every_runtime_bound_file_byte_mutation_is_rejected_after_valid_clone(self):
        with tempfile.TemporaryDirectory(prefix='rouge-future300-') as temporary:
            root=Path(temporary)
            manifest=self.clone(root)
            with patch.object(self.subject,'ROOT',root):
                self.subject._parsed_packet=None
                self.assertTrue(self.query()['source_valid'])
                for relative in [self.subject.MANIFEST,*manifest['runtime_files']]:
                    with self.subTest(file=relative):
                        file=root/relative
                        original=file.read_bytes()
                        file.write_bytes(original+b' ')
                        result=self.query()
                        self.assertFalse(result['source_valid'])
                        self.assertEqual(result['choices'],[])
                        self.assertEqual(result['phases'],[])
                        self.assertIsNone(result['scope_key'])
                        file.write_bytes(original)
                        self.assertTrue(self.query()['source_valid'])

    def test_every_runtime_bound_missing_file_is_rejected_and_restored_without_stale_result(self):
        with tempfile.TemporaryDirectory(prefix='rouge-future300-') as temporary:
            root=Path(temporary)
            manifest=self.clone(root)
            with patch.object(self.subject,'ROOT',root):
                self.subject._parsed_packet=None
                self.assertTrue(self.query()['source_valid'])
                for relative in [self.subject.MANIFEST,*manifest['runtime_files']]:
                    with self.subTest(file=relative):
                        file=root/relative;original=file.read_bytes();file.unlink()
                        result=self.query(mode='NORMAL',difficulty=12)
                        self.assertFalse(result['source_valid'])
                        self.assertIsNone(result['documented_phase'])
                        self.assertIsNone(result['source_reference'])
                        file.write_bytes(original)
                        self.assertTrue(self.query()['source_valid'])

    def test_source_fail_shape_clears_all_earlier_readable_content(self):
        self.assertTrue(self.query()['source_valid'])
        with patch.object(self.subject,'_verified_packet',return_value=None):
            result=self.query(mode='NORMAL',difficulty=12)
            self.assertEqual(result['status'],'source_unavailable')
            for key in ('event_title','scope_key','source','source_reference','source_identity','supplemental_documentation','documented_phase'):
                self.assertIsNone(result[key])
            self.assertEqual(result['choices'],[])
            self.assertEqual(result['phases'],[])
            self.assert_unknown_actual(result)
            self.assertFalse(result['run_state_updated'])

    def test_primary_complete_objects_match_pinned_whole_source(self):
        whole=json.loads((self.subject.ROOT/'research/p3-future-region-effects-300/game-topic-complete.json').read_bytes())
        result=self.query()
        primary=whole['details']['rogue_6']
        for index,row in enumerate(result['choices'],1):
            self.assertEqual(row['original_choice'],primary['choices']['choice_ro6_normal3_'+str(index)])
        for phase in result['phases']:
            self.assertEqual(phase['raw'],whole['modules']['rogue_6']['weather']['mainWeatherData'][phase['id']])
        self.assertEqual(result['source_reference']['complete_NORMAL_difficulties'],[r for r in primary['difficulties'] if r['modeDifficulty']=='NORMAL'])

    def test_readonly_rebuilder_reproduces_data_and_manifest_without_writing(self):
        root=self.subject.ROOT
        paths=[root/self.subject.DATA,root/self.subject.MANIFEST,root/self.subject.SELECTED_AUTHORITY]
        before=[p.read_bytes() for p in paths]
        result=subprocess.run([sys.executable,'-B','-X','utf8',str(root/'scripts/build_future_region_effects_300.py')],
            cwd=root,capture_output=True,check=False)
        self.assertEqual(result.returncode,0,result.stderr.decode('utf8'))
        self.assertEqual([p.read_bytes() for p in paths],before)
        receipt=json.loads(result.stdout)
        self.assertFalse(receipt['write'])
        self.assertEqual(receipt['data_sha256'],self.subject.DATA_SHA256)
        self.assertEqual(receipt['manifest_sha256'],self.subject.MANIFEST_SHA256)

    def test_runtime_does_not_read_build_only_whole_table_or_HTML(self):
        manifest=json.loads((self.subject.ROOT/self.subject.MANIFEST).read_bytes())
        runtime=set(manifest['runtime_files'])
        build=set(manifest['build_authority_files'])
        self.assertEqual(len(runtime),5)
        self.assertEqual(len(build),7)
        self.assertTrue(runtime.isdisjoint(build))
        observed=[]
        original=self.subject._source_path
        def tracked(relative):
            observed.append(relative)
            if relative in build: raise AssertionError('Runtime read a build-only original.')
            return original(relative)
        with patch.object(self.subject,'_source_path',side_effect=tracked):
            self.assertTrue(self.query()['source_valid'])
            self.assertTrue(self.query(mode='NORMAL',difficulty=12)['source_valid'])
        self.assertEqual(set(observed),runtime|{self.subject.MANIFEST})

    def test_build_original_mutation_is_detected_by_rebuild_not_claimed_by_runtime(self):
        with tempfile.TemporaryDirectory(prefix='rouge-future300-') as temporary:
            root=Path(temporary)
            manifest=self.clone(root)
            builder=root/'scripts/build_future_region_effects_300.py'
            builder.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(self.subject.ROOT/'scripts/build_future_region_effects_300.py',builder)
            original=root/'research/p3-future-region-effects-300/game-topic-complete.json'
            original.write_bytes(original.read_bytes()+b' ')
            with patch.object(self.subject,'ROOT',root):
                self.subject._parsed_packet=None
                self.assertTrue(self.query()['source_valid'])
            rebuilt=subprocess.run([sys.executable,'-B','-X','utf8',str(builder)],cwd=root,capture_output=True,check=False)
            self.assertNotEqual(rebuilt.returncode,0)
            self.assertIn('Fixed source mismatch',rebuilt.stderr.decode('utf8'))
            self.assertFalse(manifest['runtime_verifies_complete_original_bytes'])


if __name__=='__main__': unittest.main(verbosity=2)
