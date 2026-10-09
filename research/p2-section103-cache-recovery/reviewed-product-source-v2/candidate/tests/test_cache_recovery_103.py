"""Current-run cache consumers can resume from fresh public evidence.

This coherent group protects origin-correction proof consumption and squad
reuse eligibility. It does not define a full saved-state schema or new rules.
Only disposable public JSON is loaded; natural image recognition is outside
this test's scope. Source prepared only; Root performs all actual executions.
"""
import copy
import json
import tempfile
import unittest
from pathlib import Path

from rouge.run_config import confirmed_config
from rouge.run_state import RunState
from rouge.damage import calculate_damage

OWNER='char_151_myrtle'
BUFFS=['rogue_6_from_relic_1','rogue_6_from_relic_13']
SQUAD='rogue_6_band_6'
SQUAD_NAME='矛头分队'
START=1000
LAST=1001
FRESH=1002
MISSING=object()
MARKER={'kind':'non_emergency','version':2,'score':0,
        'source':'等级左侧区域未显示应急人形/时钟标识'}


def saved_run():
    return {'id':'public-cache-recovery-103','started_at':START,'last_read':LAST,
            'operators':{},'relics':{},'config':{},'resources':{},'maps':{},
            'tactical_tools':{},'history':[],'relic_icon_memory':None,
            'relic_count':None,'inventory_verified':False,'inventory_confirmed_at':None}


def owned_member(source=MISSING,origin=MISSING):
    member={'id':OWNER,'scope':'run','present':True,
            'fields':{'elite':2,'level':20},'skill_ranks':{'1':10,'2':10},
            'char_buff_ids':list(BUFFS),'char_buffs_complete':False,
            'invalid_fields':[],'invalid_skill_ranks':[],
            'field_times':{'elite':LAST,'level':LAST},'skill_times':{'1':LAST,'2':LAST},
            'sources':{'public_opaque':[None,{'nullable':None}]},
            'public_nested':{'nullable':None}}
    if source is not MISSING:member['sources']['recruitment_kind']=copy.deepcopy(source)
    if origin is not MISSING:member['recruitment_kind']=origin
    return member


def origin_observation(origin=MISSING,marker=MISSING,fields=None,ranks=None):
    member={'id':OWNER,'scope':'run','fields':dict(fields or {}),'skill_ranks':dict(ranks or {})}
    if origin is not MISSING:member['recruitment_kind']=origin
    if marker is not MISSING:member['sources']={'recruitment_kind':copy.deepcopy(marker)}
    return {'operators':[member]}


def squad_record(identity=SQUAD,captured=LAST,name=SQUAD_NAME,**extra):
    record={'id':copy.deepcopy(identity),'name':name,'level':None,
            'effect_verified':False,'source':'探索界面分队图标；基础与强化共用图案，效果未确认',**extra}
    if captured is not MISSING:record['captured_at']=captured
    return record


class CacheRecovery103Tests(unittest.TestCase):
    def setUp(self):
        self.directory=tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.file=Path(self.directory.name)/'run.json'

    def load(self,saved):
        raw=(json.dumps(saved,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
        self.file.write_bytes(raw)
        sentinel=b'public-103-preexisting-temporary-sentinel\n'
        self.file.with_suffix('.tmp').write_bytes(sentinel)
        run=RunState(self.file)
        self.assertFalse(run.preserve_unreadable)
        self.assertEqual(run.state['id'],saved['id'])
        self.assertEqual(self.file.read_bytes(),raw)
        self.assertEqual(self.file.with_suffix('.tmp').read_bytes(),sentinel)
        return run,raw,sentinel

    def with_origin(self,source=MISSING,origin=MISSING):
        saved=saved_run();saved['operators'][OWNER]=owned_member(source,origin)
        return self.load(saved)

    def apply(self,run,observation,at=FRESH):
        caller=copy.deepcopy(observation)
        self.assertIs(run.apply(observation,at),True)
        self.assertEqual(observation,caller)
        self.assertFalse(run.file.with_suffix('.tmp').exists())
        return run.state['operators'].get(OWNER)

    def restart(self,run):
        raw=run.file.read_bytes();restored=RunState(run.file)
        self.assertFalse(restored.preserve_unreadable)
        self.assertEqual(restored.state['id'],run.state['id'])
        self.assertEqual(restored.file.read_bytes(),raw)
        self.assertFalse(restored.file.with_suffix('.tmp').exists())
        return restored

    def assert_origin_discovery(self,member):
        self.assertEqual(member['recruitment_kind'],'non_emergency')
        self.assertEqual(member['char_buff_ids'],BUFFS)
        self.assertIs(member['char_buffs_complete'],False)
        self.assertEqual(member['fields'],{'elite':2,'level':20})
        self.assertEqual(member['skill_ranks'],{'1':10,'2':10})
        self.assertEqual(member['invalid_fields'],[])
        self.assertEqual(member['invalid_skill_ranks'],[])

    def events(self,run,kind):
        return [e for e in run.state['history'] if e.get('kind')==kind]

    def reuse(self,run):
        state=copy.deepcopy(run.state);raw=run.file.read_bytes()
        temporary=run.file.with_suffix('.tmp')
        prior_tmp=temporary.read_bytes() if temporary.exists() else None
        context=run.recognition_context();caller=copy.deepcopy(context)
        result=confirmed_config(context)
        self.assertEqual(context,caller)
        self.assertEqual(run.state,state)
        self.assertEqual(run.file.read_bytes(),raw)
        self.assertEqual(temporary.read_bytes() if temporary.exists() else None,prior_tmp)
        return result

    def test_damaged_origin_leaf_does_not_block_first_discovery_or_new_marker_recovery(self):
        for source in (None,[],'public-opaque',1):
            with self.subTest(source=source):
                run,raw,_=self.with_origin(source)
                self.assertEqual(run.state['operators'][OWNER]['sources']['recruitment_kind'],source)
                member=self.apply(run,origin_observation('non_emergency',MARKER))
                self.assert_origin_discovery(member)
                self.assertEqual(member['sources']['recruitment_kind'],MARKER)
                self.assertEqual(member['sources']['public_opaque'],[None,{'nullable':None}])
                self.assertEqual(self.events(run,'recruitment_changed'),[])
                self.assertEqual(self.events(run,'classification_corrected'),[])
                self.assertNotEqual(run.file.read_bytes(),raw)
                self.assert_origin_discovery(self.restart(run).state['operators'][OWNER])

    def test_missing_empty_and_valid_origin_proofs_keep_first_discovery_behavior(self):
        for source in (MISSING,{},MARKER):
            with self.subTest(source=source is MISSING):
                run,_,_=self.with_origin(source)
                member=self.apply(run,origin_observation('non_emergency',MARKER))
                self.assert_origin_discovery(member)
                self.assertEqual(self.events(run,'recruitment_changed'),[])
                self.assertEqual(self.events(run,'classification_corrected'),[])

    def test_origin_absent_keeps_damaged_proof_unused_and_raw_until_explicit_new_evidence(self):
        for source in (None,[],'public-opaque',1):
            with self.subTest(source=source):
                run,_,_=self.with_origin(source)
                member=self.apply(run,origin_observation())
                self.assertEqual(member['sources']['recruitment_kind'],source)
                self.assertEqual(member['char_buff_ids'],BUFFS)
                self.assertNotIn('recruitment_kind',member)
                self.assertEqual(self.restart(run).state['operators'][OWNER]['sources']['recruitment_kind'],source)

    def test_origin_none_keeps_damaged_proof_unused_without_confirming_unknown(self):
        run,_,_=self.with_origin(None)
        member=self.apply(run,origin_observation(None))
        self.assertIsNone(member['sources']['recruitment_kind'])
        self.assertIsNone(member['recruitment_kind'])
        self.assertEqual(member['char_buff_ids'],BUFFS)
        self.assertEqual(self.events(run,'classification_corrected'),[])

    def test_stale_fresh_origin_does_not_consume_or_replace_damaged_proof(self):
        run,raw,sentinel=self.with_origin(None)
        before=copy.deepcopy(run.state);observed=origin_observation('non_emergency',MARKER)
        caller=copy.deepcopy(observed)
        self.assertIs(run.apply(observed,START),False)
        self.assertEqual(run.state,before);self.assertEqual(observed,caller)
        self.assertEqual(run.file.read_bytes(),raw)
        self.assertEqual(run.file.with_suffix('.tmp').read_bytes(),sentinel)

    def test_valid_map_with_opaque_source_leaf_is_not_a_legacy_gold_proof(self):
        source={'source':None,'extra':[]}
        run,_,_=self.with_origin(source)
        member=self.apply(run,origin_observation('non_emergency'))
        self.assert_origin_discovery(member)
        self.assertEqual(member['sources']['recruitment_kind'],source)
        self.assertEqual(self.events(run,'classification_corrected'),[])

    def test_damaged_provenance_cannot_hide_a_real_known_recruitment_change(self):
        run,_,_=self.with_origin(None,'emergency_hire')
        member=self.apply(run,origin_observation('non_emergency',MARKER))
        self.assertEqual(member['char_buff_ids'],[])
        self.assertIs(member['char_buffs_complete'],False)
        self.assertEqual(member['invalid_fields'],['elite','level'])
        self.assertEqual(member['invalid_skill_ranks'],['1','2'])
        event=self.events(run,'recruitment_changed')[-1]
        self.assertEqual((event['previous_kind'],event['kind_now']),('emergency_hire','non_emergency'))
        self.assertEqual(self.events(run,'classification_corrected'),[])
        self.assertEqual(self.restart(run).state['operators'][OWNER]['char_buff_ids'],[])

    def test_healthy_known_recruitment_change_keeps_same_lifecycle_and_fresh_fields(self):
        run,_,_=self.with_origin({'source':'等级左侧人形与时钟应急标识'},'emergency_hire')
        member=self.apply(run,origin_observation('non_emergency',MARKER,fields={'level':21},ranks={'1':7}))
        self.assertEqual(member['char_buff_ids'],[])
        self.assertEqual(member['invalid_fields'],['elite'])
        self.assertEqual(member['invalid_skill_ranks'],['2'])
        self.assertEqual(member['fields']['level'],21)
        self.assertEqual(member['skill_ranks']['1'],7)
        self.assertEqual(self.events(run,'classification_corrected'),[])

    def test_proven_legacy_gold_correction_keeps_special_behavior_and_owned_buffs(self):
        run,_,_=self.with_origin({'source':'金色应急雇佣标记'},'emergency_hire')
        member=self.apply(run,origin_observation('non_emergency',MARKER))
        self.assert_origin_discovery(member)
        self.assertEqual(self.events(run,'recruitment_changed'),[])
        event=self.events(run,'classification_corrected')[-1]
        self.assertEqual((event['previous_kind'],event['kind_now']),('emergency_hire','non_emergency'))
        restored=self.restart(run)
        self.assertEqual(len(self.events(restored,'classification_corrected')),1)
        self.assert_origin_discovery(restored.state['operators'][OWNER])

    def test_marker_repair_survives_restart_and_another_missing_page(self):
        run,_,_=self.with_origin([])
        self.apply(run,origin_observation('non_emergency',MARKER))
        restored=self.restart(run)
        member=self.apply(restored,origin_observation(),at=FRESH+1)
        self.assert_origin_discovery(member)
        self.assertEqual(member['sources']['recruitment_kind'],MARKER)
        self.assertEqual(member['field_times'],{'elite':LAST,'level':LAST})
        self.assertEqual(member['skill_times'],{'1':LAST,'2':LAST})
        self.assertEqual(self.events(restored,'classification_corrected'),[])

    def test_no_fresh_source_does_not_delete_raw_proof_or_other_opaque_records(self):
        run,_,_=self.with_origin('public-opaque')
        member=self.apply(run,origin_observation('non_emergency'))
        self.assert_origin_discovery(member)
        self.assertEqual(member['sources']['recruitment_kind'],'public-opaque')
        self.assertEqual(member['public_nested'],{'nullable':None})
        self.assertEqual(self.restart(run).state['operators'][OWNER]['sources']['recruitment_kind'],'public-opaque')

    def test_returned_member_still_requires_new_training_and_buff_confirmation(self):
        saved=saved_run();saved['operators'][OWNER]=owned_member(None)
        saved['operators'][OWNER]['present']=False
        run,_,_=self.load(saved)
        member=self.apply(run,origin_observation('non_emergency',MARKER))
        self.assertEqual(member['char_buff_ids'],[])
        self.assertEqual(member['invalid_fields'],['elite','level'])
        self.assertEqual(member['invalid_skill_ranks'],['1','2'])
        self.assertEqual(self.events(run,'recruitment_changed')[-1]['previous_kind'],None)

    def test_cached_unhashable_squad_id_is_kept_and_not_reused(self):
        for identity in ([],{}):
            with self.subTest(identity=identity):
                saved=saved_run();saved['config']['squad']=squad_record(identity)
                run,_,_=self.load(saved)
                self.assertEqual(self.reuse(run),{})
                self.assertEqual(run.state['config']['squad']['id'],identity)

    def test_safe_unknown_or_nonstring_squad_ids_stay_unconfirmed_without_rewriting(self):
        for identity in ('public-unknown-squad',None,False,0,1):
            with self.subTest(identity=identity):
                saved=saved_run();saved['config']['squad']=squad_record(identity)
                run,_,_=self.load(saved)
                self.assertEqual(self.reuse(run),{})
                self.assertIs(type(run.state['config']['squad']['id']),type(identity))
                self.assertEqual(run.state['config']['squad']['id'],identity)

    def test_known_name_and_timestamp_keep_healthy_squad_reuse(self):
        saved=saved_run();saved['config']['squad']=squad_record()
        run,_,_=self.load(saved);result=self.reuse(run)
        self.assertEqual(result['squad']['id'],SQUAD)
        self.assertEqual(result['squad']['name'],SQUAD_NAME)
        self.assertEqual(result['squad']['captured_at'],LAST)
        self.assertEqual(result['squad']['reused_from_run'],saved['id'])
        self.assertIs(result['squad']['effect_verified'],False)

    def test_known_squad_name_mismatch_stays_unconfirmed(self):
        saved=saved_run();saved['config']['squad']=squad_record(name='public-wrong-name')
        run,_,_=self.load(saved);self.assertEqual(self.reuse(run),{})

    def test_missing_or_none_squad_timestamp_keeps_bad_identity_unused(self):
        for at in (MISSING,None):
            with self.subTest(timestamp_missing=at is MISSING):
                saved=saved_run();saved['config']['squad']=squad_record([],captured=at)
                run,_,_=self.load(saved);self.assertEqual(self.reuse(run),{})

    def test_invalid_run_identity_keeps_bad_squad_lookup_unreached(self):
        for run_id in (None,'',0,False,[],{}):
            with self.subTest(run_id=run_id):
                context={'run_id':run_id,'config':{'squad':squad_record([])}}
                caller=copy.deepcopy(context)
                self.assertEqual(confirmed_config(context),{})
                self.assertEqual(context,caller)

    def test_reuse_removes_old_badge_geometry_only_from_copy(self):
        record=squad_record(badge={'box':[1,2,3,4]})
        saved=saved_run();saved['config']['squad']=record
        run,_,_=self.load(saved);result=self.reuse(run)
        self.assertNotIn('badge',result['squad'])
        self.assertEqual(run.state['config']['squad']['badge'],{'box':[1,2,3,4]})
        result['squad']['name']='public-caller-edit'
        self.assertEqual(run.state['config']['squad']['name'],SQUAD_NAME)

    def test_safe_zero_and_boolean_timestamp_semantics_remain_accepted_for_reuse(self):
        for at in (0,False,True):
            with self.subTest(at=at):
                saved=saved_run();saved['config']['squad']=squad_record(captured=at)
                run,_,_=self.load(saved);result=self.reuse(run)
                self.assertIs(type(result['squad']['captured_at']),type(at))
                self.assertEqual(result['squad']['captured_at'],at)

    def test_bad_squad_does_not_discard_independent_healthy_difficulty_evidence(self):
        saved=saved_run();saved['config']={'squad':squad_record([]),
                                        'difficulty':{'value':10,'captured_at':LAST,'source':'public-badge'}}
        run,_,_=self.load(saved);result=self.reuse(run)
        self.assertEqual(set(result),{'difficulty'})
        self.assertEqual(result['difficulty']['value'],10)
        self.assertEqual(result['difficulty']['captured_at'],LAST)

    def test_fresh_squad_replaces_bad_identity_then_restart_can_reuse_true_current_record(self):
        for identity in ([],{}):
            with self.subTest(identity=identity):
                saved=saved_run();saved['config']['squad']=squad_record(identity)
                run,_,_=self.load(saved);self.assertEqual(self.reuse(run),{})
                fresh=squad_record(captured=MISSING)
                self.apply(run,{'operators':[],'config':{'squad':fresh}})
                self.assertEqual(run.state['config']['squad']['captured_at'],FRESH)
                self.assertIs(run.state['config']['squad']['effect_verified'],False)
                self.assertEqual(self.reuse(self.restart(run))['squad']['id'],SQUAD)

    def test_fresh_verified_squad_keeps_actual_verified_flag_and_new_owned_timestamp(self):
        saved=saved_run();saved['config']['squad']=squad_record([])
        run,_,_=self.load(saved)
        fresh=squad_record(captured=MISSING,effect_verified=True,level=0)
        self.apply(run,{'operators':[],'config':{'squad':fresh}})
        result=self.reuse(self.restart(run))['squad']
        self.assertIs(result['effect_verified'],True)
        self.assertEqual(result['level'],0)
        self.assertEqual(result['captured_at'],FRESH)

    def test_missing_page_keeps_recovered_squad_identity_and_original_observation_time(self):
        saved=saved_run();saved['config']['squad']=squad_record([])
        run,_,_=self.load(saved)
        self.apply(run,{'operators':[],'config':{'squad':squad_record(captured=MISSING)}})
        self.apply(run,{'operators':[]},at=FRESH+1)
        reused=self.reuse(self.restart(run))['squad']
        self.assertEqual(reused['id'],SQUAD);self.assertEqual(reused['captured_at'],FRESH)

    def test_stale_new_squad_does_not_overwrite_unknown_cached_identity(self):
        saved=saved_run();saved['config']['squad']=squad_record([])
        run,raw,sentinel=self.load(saved);before=copy.deepcopy(run.state)
        observed={'operators':[],'config':{'squad':squad_record(captured=MISSING)}}
        caller=copy.deepcopy(observed)
        self.assertIs(run.apply(observed,START),False)
        self.assertEqual(run.state,before);self.assertEqual(observed,caller)
        self.assertEqual(run.file.read_bytes(),raw)
        self.assertEqual(run.file.with_suffix('.tmp').read_bytes(),sentinel)

    def test_reused_config_payload_keeps_newer_original_record_and_does_not_refresh_timestamp(self):
        saved=saved_run();saved['config']['squad']=squad_record()
        run,_,_=self.load(saved);reused=self.reuse(run)
        self.apply(run,{'operators':[],'config':reused})
        self.assertEqual(run.state['config']['squad']['captured_at'],LAST)
        self.assertNotIn('reused_from_run',run.state['config']['squad'])

    def test_bad_old_verified_true_identity_cannot_block_valid_unverified_badge_recovery(self):
        for identity in ([],{},'public-unknown-squad'):
            with self.subTest(identity=identity):
                saved=saved_run();saved['config']['squad']=squad_record(identity,effect_verified=True,level=0)
                run,_,_=self.load(saved);self.assertEqual(self.reuse(run),{})
                self.apply(run,{'operators':[],'config':{'squad':squad_record(captured=MISSING)}})
                result=self.reuse(self.restart(run))['squad']
                self.assertEqual(result['id'],SQUAD)
                self.assertIs(result['effect_verified'],False)
                self.assertEqual(result['captured_at'],FRESH)

    def test_valid_previous_verified_true_is_not_downgraded_by_same_name_badge(self):
        saved=saved_run();saved['config']['squad']=squad_record(effect_verified=True,level=0)
        run,_,_=self.load(saved);original=copy.deepcopy(run.state['config']['squad'])
        self.apply(run,{'operators':[],'config':{'squad':squad_record(captured=MISSING)}})
        self.assertEqual(run.state['config']['squad'],original)
        reused=self.reuse(self.restart(run))['squad']
        self.assertIs(reused['effect_verified'],True)
        self.assertEqual(reused['captured_at'],LAST)

    def test_valid_strengthened_trade_is_not_replaced_by_same_name_basic_badge(self):
        saved=saved_run();saved['config']['squad']=squad_record('rogue_6_band_20',name='多边贸易分队',
                                                             effect_verified=True,level=1)
        run,_,_=self.load(saved);original=copy.deepcopy(run.state['config']['squad'])
        basic=squad_record('rogue_6_band_19',captured=MISSING,name='多边贸易分队',level=None)
        self.apply(run,{'operators':[],'config':{'squad':basic}})
        self.assertEqual(run.state['config']['squad'],original)
        result=self.reuse(self.restart(run))['squad']
        self.assertEqual(result['id'],'rogue_6_band_20')
        self.assertIs(result['effect_verified'],True)
        self.assertEqual(result['level'],1)
        self.assertEqual(result['captured_at'],LAST)

    def test_bad_old_true_identity_still_allows_fresh_true_repair_without_weaking_fact(self):
        saved=saved_run();saved['config']['squad']=squad_record([],effect_verified=True,level=0)
        run,_,_=self.load(saved)
        fresh=squad_record(captured=MISSING,effect_verified=True,level=0)
        self.apply(run,{'operators':[],'config':{'squad':fresh}})
        result=self.reuse(self.restart(run))['squad']
        self.assertEqual(result['id'],SQUAD)
        self.assertIs(result['effect_verified'],True)
        self.assertEqual(result['captured_at'],FRESH)

    def test_known_old_id_with_mismatched_name_is_not_a_stronger_valid_fact(self):
        saved=saved_run();saved['config']['squad']=squad_record(SQUAD,name='多边贸易分队',
                                                             effect_verified=True,level=0)
        run,_,_=self.load(saved);self.assertEqual(self.reuse(run),{})
        fresh=squad_record('rogue_6_band_19',captured=MISSING,name='多边贸易分队',level=None)
        self.apply(run,{'operators':[],'config':{'squad':fresh}})
        result=self.reuse(self.restart(run))['squad']
        self.assertEqual(result['id'],'rogue_6_band_19')
        self.assertIs(result['effect_verified'],False)

    def test_unusable_old_verification_flag_stays_raw_until_new_valid_badge_replaces_it(self):
        for flag in ('false',1,None,[],{}):
            with self.subTest(flag=flag):
                saved=saved_run();saved['config']['squad']=squad_record(effect_verified=flag)
                run,_,_=self.load(saved)
                result=self.reuse(run)['squad']
                self.assertIs(type(result['effect_verified']),type(flag))
                self.assertEqual(result['effect_verified'],flag)
                self.apply(run,{'operators':[]})
                self.assertIs(type(run.state['config']['squad']['effect_verified']),type(flag))
                self.assertEqual(run.state['config']['squad']['effect_verified'],flag)
                self.apply(run,{'operators':[],'config':{'squad':squad_record(captured=MISSING)}},at=FRESH+1)
                recovered=self.reuse(self.restart(run))['squad']
                self.assertIs(recovered['effect_verified'],False)
                self.assertEqual(recovered['captured_at'],FRESH+1)

    def test_existing_true_fact_remains_when_fresh_confirmation_is_missing_or_null(self):
        for flag in (MISSING,None):
            with self.subTest(flag_missing=flag is MISSING):
                saved=saved_run();saved['config']['squad']=squad_record(effect_verified=True,level=0)
                run,_,_=self.load(saved);original=copy.deepcopy(run.state['config']['squad'])
                fresh=squad_record(captured=MISSING)
                if flag is MISSING:fresh.pop('effect_verified')
                else:fresh['effect_verified']=None
                self.apply(run,{'operators':[],'config':{'squad':fresh}})
                self.assertEqual(run.state['config']['squad'],original)
                self.assertIs(self.reuse(self.restart(run))['squad']['effect_verified'],True)

    def test_bad_squad_reuse_guard_does_not_relax_original_explicit_numeric_api(self):
        for identity in ([],{},False,1,None):
            with self.subTest(identity=identity):
                with self.assertRaisesRegex(ValueError,'分队身份与固定档案不符'):
                    calculate_damage({'operator':'mechanist','skill':1,
                                      'run_config':{'squad':{'id':identity,'effect_verified':True}}})


if __name__=='__main__':
    unittest.main()
