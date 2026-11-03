"""Root-only pure Saved108 readback; author performs Source preparation only.

No project/calculator/formatter/GUI/test/Git import. Existing restricted native
decoding is Root's runtime operation. Actual Window record counts stay dynamic.
"""
import argparse
import ast
from collections import Counter
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys
import time
import traceback

from native_evidence import assert_native_equal, read_record, source_map

HELPER='f040258eddbb7ad624e547e2c422a3d432f7ffeae025b2576b625683ea43fe9a'
WINDOW='c4404868fec6c81d09eea18a33603b0ed1ca3c2dcabcab6f183f039494a08bc5'
WINDOW_REVIEW='e51565c93b0fc523ba9009b0b1a38515f416f81cc854af0fb870f733d9278884'
FACTS='af66d1b06a98b46660a501c67144a074c330213d05c11c0241d28be63dda42d9'
TRANSPORT='7df1d49d0927c33b59a67dc005cad7ef0fb300d92f7c75327f2839c4b2cfbb2c'
TEST='da7a739664f19e55186a8e12581bbb72c85a08a4d1640c9299bcd51943ba8b59'
TEST107='2c5eab4be5f484ca3eaf45d19eeb1f1067661a36c42ea41297a5ad1ec22ecc51'
ORIGINAL='caadc9ecfd748e1172820abe460735b0563210e1c25312482e0d2a541ac5a790'
ORIGINAL_GUARD='409249b384daf8c38d1b7576de70ce8b5e0a4c3a387bba3da07cdb84a5f75de0'
ORIGINAL_RUNNER='16396e96ad48b151932977eaa5fe95d3414c058aa1b0cde3a90648ecb9611ad2'
ORIGINAL_MANIFEST='cc7140da9b2c3828281a612285be43898942a3879f1c4a2a0c8c8cea6d58e165'
CORE='a75d9497ce34f68de787e3ba99704741f2c873c2c5fa9b5de01e6620b1f00f89'
OP='mechanist'
TARGET={'enemy_id':'enemy_1093_ccsbr','level':0,'stage_id':'ro6_n_1_2'}
SENTINEL=b'public108-original-temporary-must-not-be-rewritten\n'
WINDOW_IDS=('accepted-cache-and-memory-matrix','legal-observation-recovery')
RECORD_KINDS={'actual_public_fixture_qualification','actual_calculate_result',
    'actual_calculate_exception','pure_actual_UI_step','pure_actual_three_formatter_group',
    'actual_independent_enemy_preview','pure_actual_preview_formatter',
    'actual_window_snapshot','public_memory_consumer_admission','actual_candidate_pending_panel',
    'actual_PNG_visible_report_anchor','actual_legal_observation_save','actual_close_RunState_reload',
    'actual_cross_API_identity_order_boundary'}


def sha(raw):return hashlib.sha256(raw).hexdigest()


def same(actual,expected,label):assert_native_equal(actual,expected,label)


def bound(pin):
    assert type(pin) is dict and type(pin['path']) is str
    assert type(pin['bytes']) is int and pin['bytes']>=0
    assert type(pin['sha256']) is str and len(pin['sha256'])==64
    path=Path(pin['path']);assert not path.is_symlink()
    raw=path.read_bytes();assert len(raw)==pin['bytes'] and sha(raw)==pin['sha256'],str(path)
    return raw


def load(raw):
    assert type(raw) is bytes
    return json.loads(raw.decode('utf-8'))


def json_metadata(value):
    """Compare only the producer's JSON view; it cannot preserve native aliases."""
    return json.loads(json.dumps(value,ensure_ascii=False,allow_nan=False))


def cloud_prepend(before_raw,after_raw):
    before=ast.parse(before_raw.decode('utf-8'));after=ast.parse(after_raw.decode('utf-8'))
    def assignment(tree):
        rows=[node for node in tree.body if isinstance(node,ast.Assign)
              and any(isinstance(t,ast.Name) and t.id=='MODULES' for t in node.targets)]
        assert len(rows)==1;return rows[0]
    old=assignment(before);new=assignment(after)
    left=ast.literal_eval(old.value);right=ast.literal_eval(new.value)
    assert type(left) is type(right) and type(left) in (list,tuple)
    assert right==type(left)(['tests.test_zone_environment_input_108'])+left
    new.value=deepcopy(old.value)
    assert ast.dump(before,include_attributes=False)==ast.dump(after,include_attributes=False)


# FIXTURE_SOURCE_FUNCTIONS: inserted verbatim from the sealed Window Source.

def profile():
    return {'id':OP,'scope':'operator_profile','fields':{'elite':2,'level':90,
        'trust':100,'potential':1,'module_id':None,'module_level':0,'selected_skill':1},
        'skill_ranks':{'1':10,'2':10,'3':10},'captured_at':1000.0,
        'sources':{},'field_times':{},'skill_times':{}}

def difficulty(grade=10):
    return {'value':grade,'modeDifficulty':'NORMAL','mode':'NORMAL',
            'captured_at':1000.0,'source':'public108-normal-consumer-control'}

def zone(facts,identity,**extra):
    return {'id':identity,'name':facts['zones'][identity]['name'],
            'captured_at':1000.0,'source':'public108-fixed-zone-control',**extra}

def fixture(facts,recovery=False):
    member=profile();member.update(scope='run',present=True,recruitment_kind='non_emergency',
        char_buff_ids=[],char_buffs_complete=True,char_buff_absent_ids=[],char_buff_pending_ids=[],
        invalid_fields=[],invalid_skill_ranks=[],missing_fields=[],sources={'public_opaque':[None,{'nullable':None}]})
    return {'id':'public108-zone-window','started_at':0.0,'last_read':1000.0,
        'operators':{OP:member},'crew_count':1,'selected_operator':OP,'relics':{},
        'tactical_tools':{},'relic_count':0,'inventory_verified':True,
        'inventory_confirmed_at':1000.0,'bar_signature':[],'relic_icon_memory':None,
        'history':[],'resources':{},'config':{'difficulty':difficulty(),
            'zone':{} if recovery else zone(facts,'zone_4_1',main_zone_index=[6])},
        'maps':{},'last_node_content':None,'node_contents':[],
        'public_opaque':{'signed_zero':-0.0,'nullable':None}}

def cases(facts):
    rows=[]
    def add(identity,value=None,*,absent=False,grade=10,target=True,active=True,changed=False,kind=None):
        config={'difficulty':difficulty(grade)} if active else {}
        if not absent:config['zone']=deepcopy(value)
        rows.append({'id':identity,'config':config,'target':target,'changed':changed,
                     'error_kind':kind,'admission':'public_in_memory_consumer_after_healthy_constructor'})
    for identity in ('zone_1','zone_2','zone_3','zone_4','zone_4_1','zone_5','zone_6'):
        add('known-'+identity,zone(facts,identity))
    for label,value in (('bool',True),('text','2'),('list',[6]),('float',2.0)):
        add('known-4_1-stale-'+label,zone(facts,'zone_4_1',main_zone_index=value))
    portal={'id':None,'name':facts['zones']['zone_portal_normal_1_1']['name'],
            'hidden':True,'candidates':['zone_portal_normal_1_1','zone_portal_normal_1_2'],
            'captured_at':1000.0,'source':'public108-ambiguous-portal-control'}
    add('known-portal-no-derived-main',zone(facts,'zone_portal_normal_1_1'))
    add('ambiguous-portal-no-main',portal)
    add('ambiguous-portal-inherited2',{**portal,'main_zone_index':2})
    add('unknown-id-explicit2',{'id':'public108-unknown-zone','main_zone_index':2})
    add('unknown-id-float-depth',{'id':'public108-unknown-zone','main_zone_index':2.0})
    add('absent-zone',absent=True)
    for label,value in (('none',None),('dict',{}),('false',False),('zero',0),('text',''),('list',[])):
        add('safe-falsey-'+label,value)
    for label,value in (('true',True),('int',1),('float',1.5)):
        add('safe-hashable-id-'+label,{'id':value,'main_zone_index':2})
    add('unused-bad-zone-no-target','zone_2',target=False)
    add('unused-bad-id-no-difficulty',{'id':[]},active=False)
    for grade in (0,4):add('healthy-zero-rate-grade'+str(grade),zone(facts,'zone_2'),grade=grade)
    for label,value in (('text','zone_2'),('true',True),('one',1),('float',1.5),('list',['zone_2'])):
        add('truthy-zone-'+label,value,changed=True,kind='container')
    for label,value in (('empty-list',[]),('dict',{}),('list',['zone_2'])):
        add('unhashable-id-'+label,{'id':value},changed=True,kind='id')
    add('active-zero-rate-text','zone_2',grade=0,changed=True,kind='container')
    add('active-zero-rate-list-id',{'id':[]},grade=0,changed=True,kind='id')
    assert len(rows)==40 and len({row['id'] for row in rows})==40
    assert sum(row['changed'] for row in rows)==10
    return rows


def error_brief(error):
    return None if error is None else {key:error[key] for key in ('type','message')}


def disk_initial(value,facts,recovery=False):
    disks=value['disks']
    assert list(disks)==['run','account','run_tmp','account_tmp']
    raw=(json.dumps(fixture(facts,recovery),ensure_ascii=False,allow_nan=False,indent=2)+'\n').encode()
    account=(json.dumps({OP:profile()},ensure_ascii=False,allow_nan=False,indent=2)+'\n').encode()
    same(disks,{'run':{'exists':True,'bytes':raw},'account':{'exists':True,'bytes':account},
                'run_tmp':{'exists':True,'bytes':SENTINEL},'account_tmp':{'exists':False,'bytes':None}},
         'Actual initial original disk and tmp graphs against sealed healthy fixture')


def main():
    parser=argparse.ArgumentParser()
    for name in ('root','bindings','bindings-sha256','out'):parser.add_argument('--'+name,required=True)
    args=parser.parse_args();root=Path(args.root).resolve();out=Path(args.out).resolve()
    packet=Path(__file__).resolve().parent
    assert not out.exists() and out.parent.is_dir() and out!=root and root not in out.parents
    assert packet!=root and root not in packet.parents
    assert WINDOW is not None
    assert sha((packet/'native_evidence.py').read_bytes())==HELPER
    binding_path=Path(args.bindings);assert not binding_path.is_symlink()
    binding_raw=binding_path.read_bytes();assert sha(binding_raw)==args.bindings_sha256
    bindings=load(binding_raw)
    assert bindings['kind']=='ROOT_ACTUAL108_SAVED_ARTIFACT_BINDINGS_V1'
    assert bindings['actual_runtime_ready'] is True
    started=time.perf_counter();active={'dataset':'bindings','case':None,'record':None}
    report={'kind':'ROOT_ACTUAL_108_PURE_SAVED_READBACK','passed':False,'workflow_complete':False,
        'audit_Source_sha256':sha(Path(__file__).read_bytes()),'bindings_sha256':sha(binding_raw),
        'native_helper_sha256':HELPER,'decoded_records':[],'original_API_checks':[],
        'calculator_caller_checks':[],'UI_pure_checks':[],'formatter_group_checks':[],
        'preview_checks':[],'cross_API_boundary_checks':[],'snapshot_checks':[],'memory_admission_checks':[],
        'legal_observation_checks':[],'Gold_points':[],'restart_checks':[],'PNG_checks':[],
        'project_API_formatter_numeric_Qt_tests_Wine_Git_executed':False,'saved_inputs_written':False,
        'native_windows_verified':False,'natural_OCR_producer_verified':False,
        'malformed_saved_cache_admission_verified':False,'individual_three_formatter_prepost_verified':False,
        'cross_separate_freeze_live_alias_verified':False,'JSON_preserves_live_aliases_verified':False,
        'second_MainWindow_reopen_verified':False,
        'comparison_scope':'33 complete actual healthy Gold view/result/three-text/preview/caller/durable/disk points; ten error-kind/pending changes retain entire raw callers/durable/disks.',
        'restart_scope':'One original loaded-state oracle and one actual persisted-JSON oracle after real close; no second MainWindow or live JSON alias claim.'}
    current=None;additional=None
    try:
        pins={'window_runner':WINDOW,'window_independent_review':WINDOW_REVIEW,'original_runner':ORIGINAL_RUNNER,
              'original_manifest':ORIGINAL_MANIFEST,'facts':FACTS,'transport':TRANSPORT}
        assert sha(bound(bindings['audit_Source']))==sha(Path(__file__).read_bytes())
        for key,want in pins.items():assert sha(bound(bindings[key]))==want
        facts=load(bound(bindings['facts']));transport=load(bound(bindings['transport']))
        manifest=load(bound(bindings['original_manifest']))
        assert bound(bindings['original_primary'])==b'0\n'
        original_raw=bound(bindings['original_receipt']);assert len(original_raw)==640662 and sha(original_raw)==ORIGINAL
        original=load(original_raw)
        original_guard_raw=bound(bindings['original_guard']);assert sha(original_guard_raw)==ORIGINAL_GUARD
        original_guard=load(original_guard_raw)
        assert original['kind']=='ROOT_ACTUAL_ORIGINAL108_ZONE_CONSUMERS'
        assert original['runner_sha256']==ORIGINAL_RUNNER and original['fixture_manifest_sha256']==ORIGINAL_MANIFEST
        assert original['native_helper_sha256']==HELPER
        assert original['observation_only'] is True and original['product_pass'] is False
        assert original['observation_complete'] is original['source_and_CORE_unchanged'] is True
        assert original['source_guard_sha256']==ORIGINAL_GUARD
        old=original_guard['source_sha256'];additional={'CORE_0.70_VERIFICATION.json':CORE}
        assert len(old)==750 and old['tests/test_aglna_gravity_weight_107.py']==TEST107
        assert original['source_before']==original['source_after']==old
        assert original_guard['source_additional_sha256']==additional
        assert original['CORE_before']==original['CORE_after']==CORE
        for flag in ('native_windows_verified','Qt_executed','ocr_executed','game_chat_sampling_executed','private_state_access'):
            assert original[flag] is False
        assert original['planned_calculation_cases']==47 and original['planned_previews']==8
        assert original['actual_explicit_consumer_calls']==178 and original['actual_native_records']==225
        assert original['consumer_error_count']==22 and original['blocked_phase_count']==10
        gold_guard_raw=bound(bindings['gold_guard']);gold_guard=load(gold_guard_raw)
        candidate_guard_raw=bound(bindings['candidate_guard']);candidate_guard=load(candidate_guard_raw)
        current=candidate_guard['source_sha256']
        assert gold_guard['source_sha256']==old and len(current)==751
        assert gold_guard['source_additional_sha256']==candidate_guard['source_additional_sha256']==additional
        assert set(current)-set(old)=={'tests/test_zone_environment_input_108.py'} and not set(old)-set(current)
        assert {name for name in old if old[name]!=current[name]}=={'rouge/enemy_environment.py','scripts/verify_cloud.py'}
        assert current['tests/test_zone_environment_input_108.py']==TEST
        assert current['tests/test_aglna_gravity_weight_107.py']==TEST107
        assert len(transport['replacements'])==2
        for change in transport['replacements']:
            assert old[change['path']]==change['before_sha256'] and current[change['path']]==change['after_sha256']
        for name,pin in facts['public_source_sha256'].items():assert old[name]==current[name]==pin
        report['source_before']=source_map(root);assert report['source_before']==current
        report['source_additional_before']={name:sha((root/name).read_bytes()) for name in additional}
        assert report['source_additional_before']==additional

        # Original observations are read completely, not treated as a candidate PASS.
        active.update(dataset='original',case=None,record=None)
        original_dir=Path(bindings['original_receipt']['path']).resolve().parent
        assert original_dir!=root and root not in original_dir.parents
        native_dir=original_dir/'native';assert not native_dir.is_symlink()
        metas=original['native_records'];assert len(metas)==225
        assert len({row['path'] for row in metas})==len(metas)
        assert {p.name for p in native_dir.iterdir()}=={row['path'] for row in metas}
        original_values={};original_meta={};kind_counts=Counter()
        for seq,row in enumerate(metas,1):
            active.update(case=row['case'],record=row['path'])
            assert row['path']=='%06d.pickle.gz'%seq
            assert row['kind'] in ('original-public-consumer','whole-case-caller-input')
            value=read_record(native_dir,row);same(value['after'],value['before'],'Original whole actual caller preserved')
            original_values[row['path']]=value;original_meta[row['path']]=row;kind_counts[row['kind']]+=1
            report['decoded_records'].append({'dataset':'original',**row,'safe_native_hash_decode_verified':True})
        assert kind_counts=={'original-public-consumer':178,'whole-case-caller-input':47}
        definitions_api=manifest['cases'];definitions_preview=manifest['previews']
        assert len(definitions_api)==47 and len(definitions_preview)==8
        assert [row['id'] for row in original['rows']]==[c['id'] for c in definitions_api]+[c['id'] for c in definitions_preview]
        calls={};calcs={};errors_count=0
        for row in original['calls']:
            cid=row['case'];phase=row['phase'];ref=row['native'];assert ref==original_meta[ref['path']]
            assert ref['kind']=='original-public-consumer' and (ref['case'],ref['phase'])==(cid,phase)
            assert (cid,phase) not in calls;calls[cid,phase]=ref
            value=original_values[ref['path']]
            assert list(value)==['before','after','result','error']
            assert type(value['before']) is tuple and len(value['before'])==2
            same(row['error'],value['error'],'Original complete actual API error metadata')
            assert row['api']=={'prepare_run':'rouge.run_modifiers.prepare_run',
                'calculate_damage':'rouge.damage.calculate_damage','format_estimate':'rouge.estimate.format_estimate',
                'format_report':'rouge.reporting.format_report','format_report_technical':'rouge.reporting.format_report',
                'enemy_preview':'rouge.battle_preview.enemy_preview'}[phase]
            assert row['returned'] is (value['error'] is None) and row['caller_unchanged'] is True
            if value['error'] is not None:
                assert value['result'] is None;errors_count+=1
                assert value['error']['type'] in ('AttributeError','TypeError')
            elif phase=='calculate_damage':
                assert type(value['result']) is dict and value['result']['components']
                calcs[cid]=value['result']
                for name in ('total_damage','complete'):same(row[name],value['result'][name],'Original actual calculation metadata '+name)
                same(row['total_healing'],value['result'].get('total_healing'),'Original optional healing metadata remains absent or actual')
                same(row['returned_keys'],list(value['result']),'Original actual complete result key order')
                same(row['original_components'],json_metadata(value['result']['components']),'Original serialized components metadata, no native-alias claim')
                same(row['run_resolution'],json_metadata(value['result']['run_resolution']),'Original serialized run-resolution metadata, no native-alias claim')
                same(row['relic_enemy_effects'],json_metadata(value['result'].get('relic_resolution',{}).get('enemy_effects')),'Original serialized complete relic enemy effects')
                same(row['relic_records'],json_metadata(value['result'].get('relic_resolution',{}).get('records')),'Original serialized complete relic records')
                environment=value['result'].get('run_resolution',{}).get('enemy')
                if type(environment) is dict:
                    same(row['fixed_reference_weight'],environment['reference_stats'].get('massLevel'),'Original actual fixed-reference weight metadata')
                    same(row['reported_environment_weight'],environment['stats'].get('massLevel'),'Original actual reported environment weight metadata')
            elif phase in ('format_estimate','format_report','format_report_technical'):
                text=value['result'];assert type(text) is str and text
                assert row['text_bytes']==len(text.encode()) and row['text_sha256']==sha(text.encode())
            elif phase=='prepare_run':
                assert type(value['result']) is tuple and len(value['result'])==2 and type(value['result'][0]) is dict
                same(row['prepared_weight'],value['result'][0].get('enemy_weight'),'Original actual prepared weight metadata')
                assert row['prepared_weight_present'] is ('enemy_weight' in value['result'][0])
                same(row['prepared_run_resolution'],json_metadata(value['result'][1]),'Original serialized prepared resolution metadata')
            elif phase=='enemy_preview':assert type(value['result']) is dict
            else:raise AssertionError('Unexpected original public consumer phase')
            report['original_API_checks'].append({'case':cid,'phase':phase,'record':ref['path'],'complete_original_caller_and_output_retained':True,'observation_only':True})
        assert len(calls)==178 and errors_count==22
        for definition,row in zip(definitions_api,original['rows'][:47]):
            cid=definition['id']
            same(row['group'],definition['group'],'Original declared group')
            same(row['scope_note'],definition['scope_note'],'Original declared scope')
            for phase in ('prepare_run','calculate_damage'):
                value=original_values[calls[cid,phase]['path']]
                same(value['before'],((definition['scenario'],),{}),'Original full public fixture caller '+phase)
            caller_rows=[r for r in metas if r['kind']=='whole-case-caller-input' and r['case']==cid]
            assert len(caller_rows)==1 and caller_rows[0]['phase']=='case-caller'
            same(original_values[caller_rows[0]['path']]['before'],definition['scenario'],'Original whole-case fixture graph')
            bad=original_values[calls[cid,'calculate_damage']['path']]['error'] is not None
            if bad:
                assert len(row['blocked_phases'])==1
                assert not any((cid,p) in calls for p in ('format_estimate','format_report','format_report_technical'))
            else:
                assert row['blocked_phases']==[]
                for phase in ('format_estimate','format_report')+ (('format_report_technical',) if definition['technical_report'] else ()):
                    value=original_values[calls[cid,phase]['path']]
                    same(value['before'],((calcs[cid],),{'technical':True} if phase=='format_report_technical' else {}),
                         'Original formatter complete actual corresponding callee result')
        for definition in definitions_preview:
            target=definition['target'];value=original_values[calls[definition['id'],'enemy_preview']['path']]
            same(value['before'],((target['stage_id'],target['enemy_id'],target['level'],definition['run_config']),{}),
                 'Original standalone preview complete declared caller')

        # Every Window artifact uses the same frozen Source, with real phase guards.
        matrix=cases(facts);matrix_by_id={row['id']:row for row in matrix}
        expected_ids=['accepted-cached-known4_1-legacy-list-main']+[row['id'] for row in matrix]+[
            'actual-fresh-main4_1-save','actual-fresh-portal-inherits4-save']
        datasets={}
        for phase in ('gold','candidate'):
            active.update(dataset=phase,case=None,record=None)
            assert bound(bindings[phase+'_primary'])==b'0\n'
            receipt_raw=bound(bindings[phase+'_receipt']);receipt=load(receipt_raw)
            assert receipt['kind']=='ROOT_ACTUAL_108_REAL_MAINWINDOW' and receipt['phase']==phase
            assert receipt['passed'] is receipt['workflow_complete'] is True
            assert receipt['runner_sha256']==WINDOW and receipt['fixture_facts_sha256']==FACTS
            assert receipt['transport_sha256']==TRANSPORT
            assert receipt['original_receipt_sha256']==ORIGINAL and receipt['original_guard_sha256']==ORIGINAL_GUARD
            assert receipt['original_raw_exit_sha256']==bindings['original_primary']['sha256']
            assert receipt['source_before']==receipt['source_after']==(old if phase=='gold' else current)
            assert receipt['source_guard_sha256']==bindings[phase+'_guard']['sha256']
            assert receipt['source_additional_before']==receipt['source_additional_after']==additional
            assert receipt['source_drift']==[] and receipt['Qt_errors']==[]
            assert receipt['deadline_seconds']==450 and 0<receipt['elapsed_seconds']<450 and receipt['qt']=='6.9.3'
            for flag in ('native_windows_verified','private_state_access','game_chat_sampling_executed',
                         'natural_OCR_producer_verified','malformed_saved_cache_admission_claimed'):
                assert receipt[flag] is False
            assert [row['id'] for row in receipt['rows']]==expected_ids
            assert [row['id'] for row in receipt['windows']]==list(WINDOW_IDS)
            if phase=='candidate':assert receipt['actual_gold_receipt_sha256']==bindings['gold_receipt']['sha256']
            directory=Path(bindings[phase+'_receipt']['path']).resolve().parent
            assert directory!=root and root not in directory.parents
            record_dir=directory/'records';assert not record_dir.is_symlink()
            metas=receipt['records'];assert metas and len({r['path'] for r in metas})==len(metas)
            assert {p.name for p in record_dir.iterdir()}=={row['path'] for row in metas}
            values={};metadata={};kinds=Counter();formats={};previews={};preview_formats={};boundaries={};installs={};saves={};anchors=[];pending=[]
            for seq,row in enumerate(metas,1):
                active.update(case=row['case'],record=row['path'])
                assert row['path']=='%06d.pickle.gz'%seq and row['kind'] in RECORD_KINDS
                value=read_record(record_dir,row)
                for key in ('kind','case','phase'):assert value[key]==row[key]
                values[row['path']]=value;metadata[row['path']]=row;kinds[row['kind']]+=1
                kind=row['kind'];cid=row['case']
                if kind in ('actual_calculate_result','actual_calculate_exception'):
                    same(value['after'],value['before'],'Every complete real Window calculator caller conserved')
                    assert list(value['before'])==['args','kwargs'] and len(value['before']['args'])==1 and value['before']['kwargs']=={}
                    if kind=='actual_calculate_result':assert type(value['result']) is dict
                    else:assert value['error']['type'] in ('AttributeError','TypeError','ValueError')
                    report['calculator_caller_checks'].append({'dataset':phase,'case':cid,'record':row['path'],'kind':kind})
                elif kind=='pure_actual_UI_step':
                    assert list(value['before'])==['durable','disks']
                    same(value['after'],value['before'],'Every actual UI group joint state/all-file graph conserved')
                    report['UI_pure_checks'].append({'dataset':phase,'case':cid,'record':row['path'],'label':value['label']})
                elif kind=='pure_actual_three_formatter_group':
                    assert list(value['before'])==['result','durable','disks']
                    same(value['after'],value['before'],'Every common three-formatter result/state/all-file group conserved')
                    assert cid not in formats;formats[cid]=row
                    assert list(value['texts'])==['estimate','default','technical']
                    assert all(type(t) is str and t for t in value['texts'].values())
                    report['formatter_group_checks'].append({'dataset':phase,'case':cid,'record':row['path']})
                elif kind=='actual_independent_enemy_preview':
                    same(value['after'],value['before'],'Every actual independent preview whole caller conserved')
                    assert cid not in previews;previews[cid]=row
                elif kind=='pure_actual_preview_formatter':
                    same(value['after'],value['before'],'Every actual preview formatter complete input conserved')
                    assert cid not in preview_formats;preview_formats[cid]=row
                elif kind=='actual_cross_API_identity_order_boundary':
                    assert cid not in boundaries;boundaries[cid]=row
                    assert row['phase']=='explicit-consumer-snapshot'
                    assert list(value['before'])==['numeric_environment','preview_environment','damage_result','durable','disks']
                    same(value['after'],value['before'],'Explicit cross-API boundary preserves complete original joint graphs')
                    numeric_environment=value['before']['numeric_environment'];preview_environment=value['before']['preview_environment']
                    assert type(numeric_environment) is type(preview_environment) is dict
                    assert numeric_environment is value['before']['damage_result']['result']['run_resolution']['enemy']
                    numeric_keys=list(numeric_environment);preview_keys=list(preview_environment)
                    same(value['numeric_keys'],numeric_keys,'Actual numerical original full insertion order retained')
                    same(value['preview_keys'],preview_keys,'Actual preview original full insertion order retained')
                    assert numeric_keys[:3]==['enemy_id','level','stage_id']
                    assert preview_keys[:3]==['stage_id','enemy_id','level']
                    assert numeric_keys[3:]==preview_keys[3:]
                    for key in TARGET:
                        same(numeric_environment[key],TARGET[key],'Boundary numerical scalar identity '+key)
                        same(preview_environment[key],TARGET[key],'Boundary preview scalar identity '+key)
                    # Compare copies only in this declared interface boundary.
                    # Original environment order and all full same-input Gold domains stay strict.
                    numeric_comparison={key:numeric_environment[key] for key in numeric_keys}
                    preview_comparison={key:preview_environment[key] for key in numeric_keys}
                    same(value['numeric_comparison'],numeric_comparison,'Saved numerical separate complete shallow comparison graph')
                    same(value['preview_comparison'],preview_comparison,'Saved preview separate complete shallow comparison graph')
                    same(value['preview_comparison'],value['numeric_comparison'],'Declared identity-prefix adapter only; complete native remainder unchanged')
                    assert value['scope']=='Only declared three scalar identity keys reordered in separate comparison copies; original results/callers/text/raw cache never normalized'
                    report['cross_API_boundary_checks'].append({'dataset':phase,'case':cid,'record':row['path'],
                        'only_identity_prefix_projection':True,'original_joint_graphs_unchanged':True})
                elif kind=='public_memory_consumer_admission':
                    assert cid in matrix_by_id and cid not in installs;installs[cid]=row
                    same(value['fixture'],matrix_by_id[cid],'Complete explicit public memory fixture')
                    same(value['disks_after'],value['disks_before'],'Raw matrix installs never write original caches')
                    same(value['after']['account'],value['before']['account'],'Raw matrix keeps account graph')
                    expected_run=deepcopy(value['before']['run']);expected_run['config']=deepcopy(matrix_by_id[cid]['config'])
                    same(value['after']['run'],expected_run,'Only explicit raw config changes during matrix admission')
                    assert value['saved_schema_admission'] is value['natural_OCR_producer'] is value['save_permitted'] is False
                elif kind=='actual_legal_observation_save':
                    assert cid not in saves;saves[cid]=row
                    same(value['caller_after'],value['caller_before'],'Actual legal observation whole caller conserved')
                    same(value['after']['durable']['account'],value['before']['durable']['account'],'Authorized run save keeps complete account')
                    for key in ('account','account_tmp'):same(value['after']['disks'][key],value['before']['disks'][key],'Authorized run save keeps account disk phase')
                    same(value['after']['durable']['run']['config']['zone']['main_zone_index'],4,'Actual legal main and portal consumer retain integer4')
                elif kind=='actual_PNG_visible_report_anchor':anchors.append(row)
                elif kind=='actual_candidate_pending_panel':pending.append(row)
                elif kind=='actual_public_fixture_qualification':
                    assert value['numeric_getter_source']=='rouge/data/previews.json'
                    assert value['independent_preview_getter_source']=='rouge/data/battle-previews.json'
                    same(value['zone_names'],facts['zones'],'Actual complete supplied zone-name qualification')
                    same(value['bossValue'],facts['bossValue'],'Actual fixed coefficient-source qualification')
                    for field in ('numeric_entry','preview_entry'):
                        assert value[field]['id']==TARGET['enemy_id'] and value[field]['level']==TARGET['level']
                        for key,v in facts['target_reference'].items():same(value[field]['reference_stats'][key],v,'Qualified actual public reference '+key)
                elif kind not in ('actual_window_snapshot','actual_close_RunState_reload'):
                    raise AssertionError('Unhandled Window native record kind')
                report['decoded_records'].append({'dataset':phase,**row,'safe_native_hash_decode_verified':True})
            assert kinds['actual_public_fixture_qualification']==1 and kinds['actual_window_snapshot']==43
            assert kinds['public_memory_consumer_admission']==40 and kinds['actual_legal_observation_save']==2
            assert kinds['actual_close_RunState_reload']==2 and kinds['pure_actual_three_formatter_group']==33
            assert kinds['actual_calculate_result']+kinds['actual_calculate_exception']==receipt['actual_numeric_calls']
            assert kinds['actual_PNG_visible_report_anchor']==len(anchors)==(4 if phase=='candidate' else 0)
            assert kinds['actual_candidate_pending_panel']==len(pending)==(1 if phase=='candidate' else 0)
            datasets[phase]={'receipt':receipt,'values':values,'metadata':metadata,'kinds':dict(kinds),
                'directory':directory,'formats':formats,'previews':previews,'preview_formats':preview_formats,'boundaries':boundaries,
                'installs':installs,'saves':saves,'anchors':anchors,'pending':pending}

        for filename in ('verify_cloud.py','verify_full_available.py'):
            path='scripts/'+filename
            before=datasets['gold']['directory']/'public-Source'/filename
            after=datasets['candidate']['directory']/'public-Source'/filename
            assert not before.is_symlink() and not after.is_symlink()
            left=before.read_bytes();right=after.read_bytes()
            assert sha(left)==old[path] and sha(right)==current[path] and right==(root/path).read_bytes()
            if filename=='verify_cloud.py':cloud_prepend(left,right)
            else:assert left==right
        for phase,data in datasets.items():
            active.update(dataset=phase,case=None,record=None)
            base_value=None;recovery_initial=None;snapshots={}
            for row in data['receipt']['rows']:
                cid=row['id'];active.update(case=cid)
                ref=row['snapshot'];assert ref==data['metadata'][ref['path']]
                value=data['values'][ref['path']];assert value['kind']=='actual_window_snapshot' and value['case']==cid
                assert value['phase']=='explicit-consumer-snapshot'
                view=value['view'];changed=cid in matrix_by_id and matrix_by_id[cid]['changed']
                assert row['changed'] is changed
                assert row['window']==(WINDOW_IDS[1] if cid.startswith('actual-fresh-') else WINDOW_IDS[0])
                if cid in matrix_by_id:assert row['error_kind']==matrix_by_id[cid]['error_kind']
                numeric=row['actual_numeric_ref'];assert numeric==data['metadata'][numeric['path']]
                actual=data['values'][numeric['path']]
                assert actual['case']==cid and actual['phase']==value['phase']
                same(view['numeric_caller'],actual['before']['args'][0],'Complete real numerical caller linked to snapshot')
                caller=view['numeric_caller']
                assert caller['operator']==OP and caller['skill']==1 and caller['elite']==2 and caller['level']==90 and caller['skill_rank']==10
                same(caller['run_config'],value['durable']['run']['config'],'Snapshot caller retains complete raw config')
                if changed:
                    expected_type='ValueError' if phase=='candidate' else ('AttributeError' if row['error_kind']=='container' else 'TypeError')
                    assert actual['kind']=='actual_calculate_exception' and actual['error']['type']==expected_type
                    same(view['numeric_error'],error_brief(actual['error']),'Actual numeric brief error exactly retained')
                    assert view['damage_result'] is view['three_texts'] is None
                    assert view['displayed_damage']==actual['error']['message'].replace(chr(160),' ')
                    if phase=='candidate':
                        message='本局区域配置需要对象。' if row['error_kind']=='container' else '本局区域ID不能用于固定区域查询。'
                        assert actual['error']['message']==message
                else:
                    assert actual['kind']=='actual_calculate_result' and view['numeric_error'] is None
                    same(view['damage_result']['scenario'],caller,'Actual complete UI scenario equals observed caller')
                    same(view['damage_result']['result'],actual['result'],'Actual complete UI result equals actual callee return')
                    f=data['values'][data['formats'][cid]['path']]
                    same(f['before']['result'],actual['result'],'Three formatters bind complete actual callee result')
                    same(f['before']['durable'],value['durable'],'Three formatters bind actual durable graph')
                    same(f['before']['disks'],value['disks'],'Three formatters bind actual file phase')
                    same(view['three_texts'],f['texts'],'All three complete actual text values retained')
                    assert view['three_texts']['estimate']==view['three_texts']['default']
                    assert view['displayed_damage']==view['three_texts']['default'].replace(chr(160),' ')
                targeted=matrix_by_id[cid]['target'] if cid in matrix_by_id else True
                if targeted:
                    preview_ref=row['actual_preview_ref'];assert preview_ref==data['metadata'][preview_ref['path']]
                    assert preview_ref==data['previews'][cid]
                    preview=data['values'][preview_ref['path']]
                    same(view['preview_caller'],preview['before'],'Complete actual independent preview caller retained')
                    same(view['preview_caller'],(TARGET['stage_id'],TARGET['enemy_id'],TARGET['level'],value['durable']['run']['config']),
                         'Actual independent preview called with same full raw config')
                    same(view['preview'],preview['result'],'Complete actual independent preview return retained')
                    same(view['preview_error'],error_brief(preview['error']),'Actual independent preview brief error retained')
                    if changed and phase=='gold':
                        assert view['preview'] is view['preview_text'] is None
                        assert preview['error']['type']==actual['error']['type']
                    else:
                        assert preview['error'] is None and type(preview['result']) is dict
                        text=data['values'][data['preview_formats'][cid]['path']]
                        same(text['before'],preview['result'],'Actual complete preview formatter input binds real return')
                        same(view['preview_text'],text['text'],'Actual complete preview text retained')
                        if changed:
                            assert view['preview']['environment'] is None
                            same(view['preview']['context_pending'],['本局环境无法确认：'+actual['error']['message']],
                                 'Changed preview stays unknown with exact actual ValueError explanation')
                            assert '预计生命值：未知' in view['preview_text'] and '【面板待确认】' in view['preview_text']
                        else:
                            boundary=data['values'][data['boundaries'][cid]['path']]
                            same(boundary['before']['numeric_environment'],actual['result']['run_resolution']['enemy'],'Complete original numerical environment links to actual return')
                            same(boundary['before']['preview_environment'],view['preview']['environment'],'Complete original preview environment links to actual return')
                            same(boundary['before']['damage_result'],view['damage_result'],'Cross-API joint proof binds complete original damage_result')
                            same(boundary['before']['durable'],value['durable'],'Cross-API joint proof binds complete current durable state')
                            same(boundary['before']['disks'],value['disks'],'Cross-API joint proof binds complete current disk phase')
                else:
                    assert row['actual_preview_ref'] is None
                    for key in ('preview','preview_error','preview_text','preview_caller'):assert view[key] is None
                if cid=='accepted-cached-known4_1-legacy-list-main':
                    base_value=value;disk_initial(value,facts)
                    same(value['durable']['run']['config']['zone']['main_zone_index'],[6],'Loaded raw legacy list is preserved')
                elif cid in matrix_by_id:
                    install=data['values'][data['installs'][cid]['path']]
                    same(install['before'],base_value['durable'],'Every independent raw case starts from actual loaded baseline')
                    same(install['disks_before'],base_value['disks'],'Every raw case starts with exact original disks')
                    same(install['after'],value['durable'],'Actual raw installed graph reaches complete snapshot unchanged')
                    same(value['disks'],base_value['disks'],'Raw matrix snapshot never saves any cache')
                    report['memory_admission_checks'].append({'dataset':phase,'case':cid,'record':data['installs'][cid]['path'],'config_only_memory_change_and_no_save_verified':True})
                else:
                    saved=data['values'][data['saves'][cid]['path']]
                    same(saved['after']['durable'],value['durable'],'Legal observation exact accepted durable graph reaches snapshot')
                    same(saved['after']['disks'],value['disks'],'Legal observation actual new file phase reaches snapshot')
                    observation,at=saved['caller_before']
                    if cid=='actual-fresh-main4_1-save':
                        same((observation,at),({'config':{'zone':zone(facts,'zone_4_1')}},1001.0),'Actual first legal known-main observation')
                        recovery_initial=saved['before'];disk_initial({'disks':saved['before']['disks']},facts,True)
                        assert value['durable']['run']['config']['zone']['id']=='zone_4_1'
                    else:
                        same((observation,at),({'config':{'zone':{'id':None,'name':facts['zones']['zone_portal_normal_1_1']['name'],
                            'hidden':True,'candidates':['zone_portal_normal_1_1','zone_portal_normal_1_2'],
                            'main_zone_index':6,'source':'public108-fresh-hidden-zone-observation'}}},1002.0),
                             'Actual legal ambiguous portal preserves original incoming stale6 caller')
                        previous=snapshots['actual-fresh-main4_1-save']
                        same(saved['before']['durable'],previous['durable'],'Portal observes actual previous main4 graph')
                        same(saved['before']['disks'],previous['disks'],'Portal writes after real first main save')
                        assert value['durable']['run']['config']['zone']['id'] is None
                    accepted=value['durable']['run']['config']['zone']
                    same(accepted['main_zone_index'],4,'Actual producer/consumer establishes then retains integer4')
                    same(accepted['captured_at'],at,'Actual accepted zone capture timestamp')
                    same(value['durable']['run']['last_read'],at,'Actual legal whole-run capture timestamp')
                    same(value['durable']['account'],recovery_initial['durable']['account'],'Legal save retains complete account')
                    same(value['disks']['account'],recovery_initial['disks']['account'],'Legal save retains exact account bytes')
                    same(value['disks']['run_tmp'],{'exists':False,'bytes':None},'Actual atomic save consumes old run tmp sentinel')
                    persisted=load(value['disks']['run']['bytes'])
                    same(persisted['config']['zone'],accepted,'Actual JSON stores complete accepted current zone')
                    report['legal_observation_checks'].append({'dataset':phase,'case':cid,'record':data['saves'][cid]['path'],'authorized_write_phase_verified':True})
                snapshots[cid]=value
                report['snapshot_checks'].append({'dataset':phase,'case':cid,'record':ref['path'],'complete_actual_outputs_callers_texts_bound':True,'intended_error_change':changed})
            targeted_ids={
                cid for cid in expected_ids if (matrix_by_id[cid]['target'] if cid in matrix_by_id else True)}
            healthy_targeted_ids={cid for cid in targeted_ids if not (cid in matrix_by_id and matrix_by_id[cid]['changed'])}
            assert set(data['previews'])==targeted_ids
            assert set(data['boundaries'])==healthy_targeted_ids
            assert set(data['preview_formats'])==(targeted_ids if phase=='candidate' else healthy_targeted_ids)
            for row in data['receipt']['windows']:
                identity=row['id'];ref=row['restart'];assert ref==data['metadata'][ref['path']]
                restarted=data['values'][ref['path']]
                assert restarted['kind']=='actual_close_RunState_reload' and restarted['case']==identity
                assert row['constructor_saved_schema_accepted'] is True and row['matrix_invalid_inputs_saved'] is False
                if identity==WINDOW_IDS[0]:
                    oracle=base_value['durable']['run'];assert row['oracle']==restarted['oracle']=='original-loaded-state'
                    same(restarted['live_before']['durable'],base_value['durable'],'Read-only close restores full actual loaded graph')
                    same(restarted['live_before']['disks'],base_value['disks'],'Read-only close retains original four-file phase')
                    assert row['legal_observation_refs']==[]
                else:
                    last=snapshots['actual-fresh-portal-inherits4-save']
                    assert row['oracle']==restarted['oracle']=='actual-persisted-JSON'
                    oracle=load(last['disks']['run']['bytes'])
                    same(restarted['live_before']['durable'],last['durable'],'Real fresh close retains final accepted durable graph')
                    same(restarted['live_before']['disks'],last['disks'],'Real fresh close retains authorized file phase')
                    assert row['legal_observation_refs']==[data['saves'][c] for c in ('actual-fresh-main4_1-save','actual-fresh-portal-inherits4-save')]
                same(restarted['persisted_json'],load(restarted['live_before']['disks']['run']['bytes']),'Actual serialized JSON oracle')
                same(restarted['restart_state'],oracle,'Complete direct RunState restart follows declared actual oracle')
                same(restarted['disks_after'],restarted['live_before']['disks'],'Actual accepted direct reload never rewrites current disk phase')
                report['restart_checks'].append({'dataset':phase,'window':identity,'record':ref['path'],'oracle':row['oracle']})
            data['snapshots']=snapshots

        for cid in expected_ids:
            previous=datasets['gold']['snapshots'][cid];value=datasets['candidate']['snapshots'][cid]
            changed=cid in matrix_by_id and matrix_by_id[cid]['changed']
            old_value={k:previous[k] for k in ('view','durable','disks')}
            actual_value={k:value[k] for k in ('view','durable','disks')}
            if not changed:same(actual_value,old_value,'Whole same-input real healthy Gold graph/math/three texts/preview/callers/state/disks')
            else:
                for key in ('durable','disks'):same(actual_value[key],old_value[key],'Changed failure retains whole raw Gold '+key)
                for key in ('numeric_caller','preview_caller','run_summary_widget'):
                    same(actual_value['view'][key],old_value['view'][key],'Changed failure retains whole raw Gold '+key)
                assert previous['view']['damage_result'] is previous['view']['preview'] is None
            report['Gold_points'].append({'case':cid,'complete_same_input_Gold_equal':not changed,'changed_error_preserves_raw_Gold':changed})
        assert sum(row['complete_same_input_Gold_equal'] for row in report['Gold_points'])==33
        assert sum(row['changed_error_preserves_raw_Gold'] for row in report['Gold_points'])==10
        candidate=datasets['candidate'];assert len(candidate['pending'])==1
        panel=candidate['values'][candidate['pending'][0]['path']]
        bad=candidate['snapshots']['truthy-zone-text']['view']
        same(panel['context'],matrix_by_id['truthy-zone-text']['config'],'Actual pending panel keeps full raw context')
        same(panel['shown_enemy'],(TARGET['stage_id'],TARGET['enemy_id'],TARGET['level']),'Actual panel qualifies exact preview identity')
        same(panel['expected_preview'],bad['preview_text'],'Actual pending panel binds complete independent preview text')
        assert panel['displayed_preview']==bad['preview_text'].replace(chr(160),' ') and panel['original_panel_success_claimed'] is False

        visual=load(bound(bindings['visual']))
        assert visual['passed'] is visual['workflow_complete'] is True
        assert visual['native_windows_game_chat_verified'] is False
        pngs=candidate['receipt']['pngs'];assert datasets['gold']['receipt']['pngs']==[]
        assert len(pngs)==len(visual['pngs'])==4
        expected_pngs=[('01-healthy-known-main-cache.png','accepted-cached-known4_1-legacy-list-main',1,'预计生命值'),
            ('02-clear-active-zone-error.png','truthy-zone-text',1,'本局区域配置需要对象。'),
            ('03-real-preview-pending.png','truthy-zone-text',4,'本局环境无法确认：本局区域配置需要对象。'),
            ('04-legal-portal-recovery-summary.png','actual-fresh-portal-inherits4-save',0,'未萌生的摇篮')]
        for png,seen,expected in zip(pngs,visual['pngs'],expected_pngs):
            assert (png['file'],png['case'],png['tab_index'],png['visible_anchor'])==expected
            assert png['Root_visual_verified'] is False  # Source runner never fabricates Root viewing.
            ref=png['anchor_native'];assert ref==candidate['metadata'][ref['path']]
            anchor=candidate['values'][ref['path']]
            assert anchor['kind']=='actual_PNG_visible_report_anchor' and anchor['case']==png['case'] and anchor['phase']==png['phase']
            assert anchor['anchor']==png['visible_anchor'] and anchor['anchor'] in anchor['actual_text']
            if png['tab_index'] in (1,4):
                assert anchor['selection']==anchor['anchor'] and type(anchor['cursor_position']) is int
                x,y,width,height=anchor['cursor_rect'];vx,vy,vwidth,vheight=anchor['viewport_rect']
                assert all(type(v) is int for v in (x,y,width,height,vx,vy,vwidth,vheight))
                assert width>0 and height>0 and vwidth>0 and vheight>0
                sx=2*x+width-1;sy=2*y+height-1
                cx=sx//2 if sx>=0 else -((-sx)//2)
                cy=sy//2 if sy>=0 else -((-sy)//2)
                assert vx<=cx<vx+vwidth and vy<=cy<vy+vheight
                expected_text=(candidate['snapshots'][png['case']]['view']['displayed_damage'] if png['tab_index']==1 else panel['displayed_preview'])
                same(anchor['actual_text'],expected_text,'Actual visible PNG anchor belongs to real current complete report')
            else:
                same(anchor['actual_text'],candidate['snapshots'][png['case']]['view']['run_summary_widget'],'Actual visible portal QLabel complete summary')
                assert 'widget_rect' in anchor and 'scope' in anchor
            same({key:seen[key] for key in png},png,'Root actual visual ledger binds entire Source runner image row')
            assert seen['actually_viewed'] is True and type(seen['visual_observation']) is str and seen['visual_observation']
            path=candidate['directory']/png['file'];assert not path.is_symlink()
            raw=path.read_bytes();assert len(raw)==png['bytes'] and sha(raw)==png['sha256'] and raw.startswith(b'\x89PNG\r\n\x1a\n')
            report['PNG_checks'].append({'file':png['file'],'sha256':png['sha256'],'actual_native_visible_anchor_verified':True,'Root_actually_viewed':True})
        report['actual_decoded_records_by_dataset']={phase:sum(row['dataset']==phase for row in report['decoded_records']) for phase in ('original','gold','candidate')}
        report['actual_Window_records_by_phase']={phase:len(data['receipt']['records']) for phase,data in datasets.items()}
        report['actual_Window_numeric_calls_by_phase']={phase:data['receipt']['actual_numeric_calls'] for phase,data in datasets.items()}
        report.update(passed=True,workflow_complete=True)
    except BaseException as error:
        report['failure']={'type':type(error).__name__,'message':str(error),
            'traceback':''.join(traceback.format_exception(type(error),error,error.__traceback__)),'active':active.copy()}
    finally:
        report['source_after']=source_map(root)
        report['source_additional_after']={name:sha((root/name).read_bytes()) for name in (additional or {})}
        report['source_drift']=[] if current is not None and report['source_after']==current else ['Current Source differs or bindings did not reach Source gate']
        if report['source_drift'] or additional is None or report['source_additional_after']!=additional:
            report.update(passed=False,workflow_complete=False)
        report['elapsed_seconds']=time.perf_counter()-started
        with out.open('x',encoding='utf-8') as stream:json.dump(report,stream,ensure_ascii=False,indent=2);stream.write('\n')
    print(json.dumps({'passed':report['passed'],'decoded_records':len(report['decoded_records']),
        'Gold_points':len(report['Gold_points']),'Root_viewed_PNGs':len(report['PNG_checks'])}))
    return 0 if report['passed'] else 1


if __name__=='__main__':raise SystemExit(main())
