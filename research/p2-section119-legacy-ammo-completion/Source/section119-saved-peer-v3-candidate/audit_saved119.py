"""Source-only candidate. Root alone executes the saved native audit; no project import."""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import struct
import sys
import traceback
from native_evidence import read_record, assert_native_equal as same, freeze, source_map

HELPER_SHA='f040258eddbb7ad624e547e2c422a3d432f7ffeae025b2576b625683ea43fe9a'
GUI_RUNNER_SHA='ac66f11d297dd6531295c18e835c562d5d42738feb49fe4eb0a9e8b55db12527'
API_FIXTURE_SHA='5dada56bfde891803f5dc60031a1407433aab74e76a81a386134a7a0fb901542'
API_FIXTURE_BYTES=8917
API_RUNNER_SHA='b4e574e54d7798d06707ad7f80a2efe268209a5b8e22645f9d976ac86dd7e1d3'
API_RUNNER_BYTES=6415
PHASES=('calculate_damage','format_estimate','format_report','format_report_technical')
LIFECYCLE=('initial_seconds','recharge_seconds','cycle_seconds','duration_seconds',
    'total_damage','total_healing','phase_damage','phase_healing','cycle_damage',
    'cycle_healing','cycle_dps','cycle_hps')


def sha(raw):return hashlib.sha256(raw).hexdigest()
def load_json(path):
    raw=Path(path).read_bytes();return json.loads(raw),raw

def receipt_name(path):
    """Digest bytes identify the file; basename accepts Windows/Linux receipt spelling."""
    assert type(path) is str and path
    return path.replace('\\','/').rsplit('/',1)[-1]

def near(actual,wanted,label):
    assert type(actual) in (int,float) and math.isfinite(actual)
    assert abs(actual-wanted)<=max(1e-8,abs(wanted)*1e-12),(label,actual,wanted)

def visible_metric_label(label):
    """Only the verified ordinary-report label translations used by these cases."""
    assert type(label) is str
    for raw,shown in (('DPS/HPS','每秒伤害 / 每秒治疗'),('DPS','每秒伤害'),('HPS','每秒治疗')):
        label=label.replace(raw,shown)
    return re.sub(r' (?=每秒伤害|每秒治疗)','',label).strip()

def expected(case,base):
    """Independent literal profile/rank math; no production helper or saved oracle."""
    op=case['operator'];shape=case['shape'];frames=case['mode']=='frames'
    partial=shape in ('limited_windows','positive_lifetime','interrupted_tail','empty_control') if frames else shape=='empty_control'
    if op=='mechanist':
        per=base*1.1
        if shape in ('limited_windows','interrupted_tail'):count=10
        elif shape=='positive_lifetime':count=5
        elif shape=='short_control':count=4 if frames else 0
        elif shape in ('empty_control','late_complete_control'):count=0
        else:count=15
        window_damage=per*count;window_healing=0
        full_damage=0 if shape=='empty_control' else None if partial else per*15
        full_healing=0;duration=None if partial else 175/30 if frames else 7.5
    else:
        per=base*2.25*3.5;heal=base*2.25*1.7*case['healing_targets']
        if shape in ('limited_windows','positive_lifetime','interrupted_tail'):count=2
        elif shape=='short_control':count=1 if frames else 0
        elif shape in ('empty_control','late_complete_control'):count=0
        else:count=4 if frames else 3
        window_damage=0 if shape=='friendly_complete_control' else per*count
        window_healing=heal*count
        full_damage=0 if shape in ('empty_control','friendly_complete_control') else None if partial else per*10
        full_healing=0 if shape=='empty_control' else None if partial else heal*10
        duration=None if partial else 775/30 if frames else 28.5
    return {'window_damage':window_damage,'window_healing':window_healing,
        'full_damage':full_damage,'full_healing':full_healing,'duration':duration,'partial':partial}

def numerical(case,base,result,caller):
    want=expected(case,base);s=result['estimate']['skill']
    near(result['total_damage'],want['window_damage'],case['id']+' top windowdamage')
    near(s['window_damage'],want['window_damage'],case['id']+' explicit windowdamage')
    near(s['window_healing'],want['window_healing'],case['id']+' explicit windowhealing')
    assert s['window_seconds']==case['seconds']
    for field,oracle in [('total_damage','full_damage'),('total_healing','full_healing'),('duration_seconds','duration')]:
        if want[oracle] is None:assert s[field] is None,(case['id'],field,s[field])
        else:near(s[field],want[oracle],case['id']+' '+field)
    if want['partial']:
        for field in ('cycle_seconds','cycle_damage','cycle_healing','cycle_dps','cycle_hps'):
            assert s[field] is None,(case['id'],field,s[field])
        if want['full_damage'] is None:assert s['phase_damage'] is None
        if want['full_healing'] is None:assert s['phase_healing'] is None
    if case['operator']=='kaltsit':
        # Only the sealed no-bonus R7 fixtures, never arbitrary Kaltsit callers.
        assert (caller['operator'],caller['skill'],caller['elite'],caller['level'],
            caller['skill_rank'],caller['trust'],caller['potential'])==('kaltsit',2,2,1,7,0,1)
        assert caller.get('module_id') is None and caller.get('module_level',0)==0
        for key in ('relic_ids','char_buff_ids','char_buff_absent_ids','char_buff_pending_ids'):
            same(caller.get(key,[]),[],'sealed Kaltsit no selected relic or buff '+key)
        for key in ('run_config','relic_context'):
            same(caller.get(key,{}),{},'sealed Kaltsit empty '+key)
        assert not {'initial_sp_bonus','sp_recovery_bonus','_relic_rules','_relic_final_attack_factor'} & set(caller)
        same(caller['timing'],case['timing'],'sealed Kaltsit timing without SP lock/event additions')
        assert s['sp_type']=='INCREASE_WITH_TIME'
        near(s['sp_cost'],35,'sealed Kaltsit R7 SP cost')
        near(s['initial_sp'],20,'sealed Kaltsit R7 initial SP')
        near(s['sp_recovery_per_second'],1,'sealed Kaltsit natural SP rate')
        near(s['initial_seconds'],15,'sealed Kaltsit known initial time')
        near(s['recharge_seconds'],35,'sealed Kaltsit known natural recharge even when cast incomplete')
    return want

def load_api(folder,guard,guard_raw,guard_path,phase,cases):
    folder=Path(folder).resolve();o,raw=load_json(folder/'observations.json')
    assert o['kind']=='ROOT_ACTUAL_PUBLIC_API_THREE_FORMATTER_OBSERVATION'
    assert o['phase']==phase and o['observation_complete'] is True
    assert o['observation_only'] is True and o['product_pass'] is False
    assert o['consumer_error_count']==0 and o['source_and_CORE_unchanged'] is True and not o.get('fatal_error')
    assert o['private_state_access'] is False and o['native_windows_game_chat_verified'] is False
    for digest in (o['fixture'],o['runner']):
        assert set(digest)=={'path','bytes','sha256'} and type(digest['path']) is str and digest['path']
        assert type(digest['bytes']) is int and type(digest['sha256']) is str
    assert (o['fixture']['bytes'],o['fixture']['sha256'])==(API_FIXTURE_BYTES,API_FIXTURE_SHA)
    assert receipt_name(o['runner']['path'])=='root-public-probe-v2.py'
    assert (o['runner']['bytes'],o['runner']['sha256'])==(API_RUNNER_BYTES,API_RUNNER_SHA)
    assert receipt_name(o['guard']['path'])==Path(guard_path).name
    same(o['guard'],{'path':o['guard']['path'],'bytes':len(guard_raw),
        'sha256':sha(guard_raw)},'API exact actual guard receipt digest')
    same(o['source_before'],guard['source_sha256'],'API Source before')
    same(o['source_after'],guard['source_sha256'],'API Source after')
    same(o['CORE_before'],guard['source_additional_sha256'],'API CORE before')
    same(o['CORE_after'],guard['source_additional_sha256'],'API CORE after')
    assert (o['actual_completed_cases'],o['actual_public_calls'],o['actual_native_records'])==(len(cases),4*len(cases),5*len(cases))
    calls={};whole={};values={}
    for sequence,m in enumerate(o['records'],1):
        assert set(m)=={'path','bytes','sha256','decoded_bytes','decoded_sha256','pickle_protocol','kind','case','phase'}
        assert m['path']=='%06d.pickle.gz'%sequence and m['path'] not in values
        index,slot=divmod(sequence-1,5);assert index<len(cases)
        assert m['case']==cases[index]['id']
        assert (m['kind'],m['phase'])==(('actual-public-consumer',PHASES[slot]) if slot<4 else ('whole-case-caller','caller'))
        v=read_record(folder/'native',m);same(v['after'],v['before'],'every saved API caller purity')
        values[m['path']]=v
        if m['kind']=='actual-public-consumer':
            assert set(v)=={'before','after','result','error'}
            assert m['phase'] in PHASES and v['error'] is None and (m['case'],m['phase']) not in calls
            calls[m['case'],m['phase']]=v
        else:
            assert set(v)=={'before','after'}
            assert m['kind']=='whole-case-caller' and m['phase']=='caller' and m['case'] not in whole
            whole[m['case']]=v
    expected_names={c['id'] for c in cases}
    assert set(whole)==expected_names and set(calls)=={(n,p) for n in expected_names for p in PHASES}
    assert len(values)==o['actual_native_records']
    assert {p.name for p in (folder/'native').iterdir()}==set(values)|{'index.jsonl'}
    ledger=[json.loads(line) for line in (folder/'native/index.jsonl').read_text().splitlines()]
    same(ledger,o['records'],'API full ledger metadata')
    expected_calls=[{'case':m['case'],'phase':m['phase'],'native':m,'error':None,'caller_unchanged':True}
        for m in o['records'] if m['kind']=='actual-public-consumer']
    same(o['calls'],expected_calls,'all API call metadata and complete native references in producer order')
    same(o['rows'],[{'id':c['id'],'calculate_error':None,'formatters_blocked':False} for c in cases],
        'all API row completion/error metadata')
    for c in cases:
        n=c['id'];numeric=calls[n,'calculate_damage']
        same(numeric['before'],(c['scenario'],),'whole API fixture/native typed caller')
        same(whole[n]['before'],c['scenario'],'whole case original fixture caller')
        result=numeric['result'];assert type(result) is dict
        for name in PHASES[1:]:
            formatter=calls[n,name]
            same(formatter['before'],(result,),'complete saved formatter input graph')
            assert type(formatter['result']) is str and formatter['result']
        assert calls[n,'format_estimate']['result']==calls[n,'format_report']['result']
    return {'folder':folder,'raw':raw,'receipt':o,'calls':calls,'values':values}

EMPTY_NOTE='供靶情景未耗尽本次弹药；已排程观察输出保留，完整施放持续、非零总量及完整周期保持未知。'

# Exactly the original/candidate differences in the sealed public 119 fixtures.
# op, target_scope, ammo rounds, interval, observed starts/releases, pellets,
# pellet spacing, original resume, candidate observation-horizon resume.
RESUME_CASES={
    'mechanist-limited_windows':('mechanist','enemy',3,75,(0,75),5,6,50,0),
    'mechanist-positive_lifetime':('mechanist','enemy',3,75,(0,75),5,6,50,0),
    'mechanist-interrupted_tail':('mechanist','enemy',3,75,(0,75),5,6,50,0),
    'kaltsit-limited_windows':('kaltsit','enemy',10,86,(0,86),1,0,85,0),
    'kaltsit-positive_lifetime':('kaltsit','enemy',10,86,(0,86),1,0,85,0),
    'kaltsit-interrupted_tail':('kaltsit','enemy',10,86,(0,86),1,0,85,0),
    'kaltsit-complete_control':('kaltsit','enemy',10,86,(0,86,172,258),1,0,85,44),
    'kaltsit-empty-enemy-friendly-complete-control':('kaltsit','friendly',10,86,(0,86,172,258),1,0,85,44),
}
FULL_OBSERVATION_CONTROLS=('kaltsit-complete_control','kaltsit-empty-enemy-friendly-complete-control')


def checked_observed_resume(identity,scenario,original,candidate):
    """Positive frame formula proof for one fixed case; no project-clock execution."""
    assert identity in RESUME_CASES
    op,scope,ammo,interval,starts,pellets,spacing,old_resume,new_resume=RESUME_CASES[identity]
    assert scenario['operator']==op and scenario['timing_mode']=='frames'
    assert scenario['skill']==(1 if op=='mechanist' else 2)
    same(scenario['window_seconds'],10,'fixed explicit API observation horizon')
    assert scenario['timing']['windup_frames']==scenario['timing']['recovery_frames']==0
    original_streams=original['timing']['streams'];candidate_streams=candidate['timing']['streams']
    assert type(original_streams) is list and type(candidate_streams) is list
    assert len(original_streams)==len(candidate_streams)==1
    expected_frames=list(starts)
    for result,streams in ((original,original_streams),(candidate,candidate_streams)):
        same(result['ammo_rounds'],ammo,'fixed actual ammunition limit')
        stream=streams[0]
        assert stream['unit']==op and stream['target_scope']==scope
        assert stream['known_animation'] is True and stream['temporary_attack_speed'] is False
        same(stream['windup_frames'],0,'fixed manual windup frames')
        same(stream['recovery_frames'],0,'fixed manual recovery frames')
        same(stream['start_frames'],expected_frames,'whole actual fixed observed attack starts')
        same(stream['release_frames'],expected_frames,'whole actual fixed observed attack releases')
        same(stream['interval_frames'],interval,'fixed actual cadence frames')
        same(stream['interval_seconds'],interval/30,'fixed actual cadence seconds')
        same(stream['interval_frames_by_attack'],[interval]*len(starts),'whole actual per-attack cadence')
        assert len(stream['release_frames'])<result['ammo_rounds']
    horizon_frames=math.ceil(scenario['window_seconds']*30-1e-9)
    assert horizon_frames==300
    old_end_frames=original_streams[0]['release_frames'][-1]+(pellets-1)*spacing+1
    old_execution=old_end_frames/30
    same(original['execution_seconds'],old_execution,'exact original placed-release end scalar')
    assert math.ceil(original['execution_seconds']*30-1e-9)==old_end_frames
    assert candidate['execution_seconds'] is None
    derived_old=max(0,original_streams[0]['start_frames'][-1]+interval-old_end_frames)
    derived_new=max(0,candidate_streams[0]['start_frames'][-1]+interval-horizon_frames)
    same(derived_old,old_resume,'independent original post-execution resume formula')
    same(derived_new,new_resume,'independent retained observation-horizon resume formula')
    same(original_streams[0]['resume_frame'],derived_old,'exact actual original resume')
    same(candidate_streams[0]['resume_frame'],derived_new,'exact actual candidate resume')
    reconstructed=freeze(candidate_streams)
    reconstructed[0]['resume_frame']=derived_old
    same(reconstructed,original_streams,'every other whole stream field/order/type/float/alias exactly preserved')
    if identity in FULL_OBSERVATION_CONTROLS:
        full_starts=[index*interval for index in range(ammo)]
        full_end=full_starts[-1]+(pellets-1)*spacing+1
        assert full_starts==[0,86,172,258,344,430,516,602,688,774] and full_end==775
        for result in (original,candidate):
            same(result['estimate']['skill']['duration_seconds'],full_end/30,
                'independent complete-cast duration remains distinct from four-release observation')
        same(candidate['estimate']['skill'],original['estimate']['skill'],'entire full-control lifecycle exact')
    return {'case':identity,'old_execution_seconds':old_execution,'old_derived_end_frames':old_end_frames,
        'observation_horizon_frames':horizon_frames,'actual_start_release_frames':expected_frames,
        'interval_frames':interval,'ammo_rounds':ammo,'actual_observed_release_count':len(starts),
        'original_resume_frame':derived_old,'candidate_resume_frame':derived_new,
        'admitted_stream_leaf':'timing.streams[0].resume_frame',
        'scope':'Only this fixed positive-validated resume leaf differs; every other complete observed-stream field including impact/emitted event arrays is exact.'}


def reconstruct_full_observation_consumer(identity,scenario,phase,original_consumer,candidate_consumer):
    """Rebuild only two proven raw leaves, then require complete consumer equality."""
    assert identity in FULL_OBSERVATION_CONTROLS and phase in PHASES
    if phase=='calculate_damage':
        old_roots=[original_consumer['result']];new_roots=[candidate_consumer['result']]
    else:
        assert type(candidate_consumer['result']) is str
        same(candidate_consumer['result'],original_consumer['result'],identity+' '+phase+' complete text remains exactly identical')
        old_roots=[original_consumer['before'][0],original_consumer['after'][0]]
        new_roots=[candidate_consumer['before'][0],candidate_consumer['after'][0]]
    proofs=[checked_observed_resume(identity,scenario,old_root,new_root) for old_root,new_root in zip(old_roots,new_roots)]
    normalized=freeze(candidate_consumer)
    roots=([normalized['result']] if phase=='calculate_damage' else [normalized['before'][0],normalized['after'][0]])
    seen=set()
    for root,proof in zip(roots,proofs):
        if id(root) in seen:continue
        seen.add(id(root))
        assert root['execution_seconds'] is None
        same(root['timing']['streams'][0]['resume_frame'],44,'fixed full-control raw observation resume before reconstruction')
        root['execution_seconds']=proof['old_execution_seconds']
        root['timing']['streams'][0]['resume_frame']=proof['original_resume_frame']
    return normalized

def zero_note_only(consumer):
    normalized=freeze(consumer);seen=set();count=0
    def remove(graph):
        nonlocal count
        if type(graph) not in (dict,list,tuple) or id(graph) in seen:return
        seen.add(id(graph))
        if type(graph) is dict:
            estimate=graph.get('estimate')
            if type(estimate) is dict and type(estimate.get('notes')) is list:
                assert estimate['notes'].count(EMPTY_NOTE)==1
                estimate['notes'].remove(EMPTY_NOTE);count+=1
            for value in graph.values():remove(value)
        else:
            for value in graph:remove(value)
    remove(normalized)
    assert count in (1,2)
    if type(normalized.get('result')) is str:
        lines=normalized['result'].split('\n');line='• '+EMPTY_NOTE
        assert lines.count(line)==1;lines.remove(line);normalized['result']='\n'.join(lines)
    return normalized


def audit_api(old,new,cases):
    changes=[];negative=[];resume_admissions=[];full_observation_admissions=[]
    for case in cases:
        identity=case['id'];scenario=case['scenario'];op=scenario['operator']
        shape='friendly_complete_control' if identity=='kaltsit-empty-enemy-friendly-complete-control' else identity.split('-',1)[1]
        hand={'id':identity,'operator':op,'shape':shape,'mode':'frames','seconds':scenario['window_seconds'],
            'healing_targets':scenario.get('healing_targets',1),'timing':scenario['timing']}
        result=new['calls'][identity,'calculate_damage']['result'];prior=old['calls'][identity,'calculate_damage']['result']
        want=numerical(hand,1000,result,scenario)
        if op=='kaltsit':
            for field in ('initial_seconds','recharge_seconds','sp_type','sp_cost','initial_sp','sp_recovery_per_second'):
                same(result['estimate']['skill'][field],prior['estimate']['skill'][field],identity+' unchanged known SP field '+field)
        near(result['total_damage'],case['expected_window_damage'],'independently reviewed public hand fixture')
        for field,key in [('total_healing','expected_total_healing'),('duration_seconds','expected_duration_seconds')]:
            if key in case:near(result['estimate']['skill'][field],case[key],identity+' fixed hand control')
        if 'expected_window_healing' in case:near(result['estimate']['skill']['window_healing'],case['expected_window_healing'],identity+' hand windowhealing')
        same(new['calls'][identity,'calculate_damage']['before'],old['calls'][identity,'calculate_damage']['before'],'old/new whole API caller')
        for field in ('total_damage','components'):
            same(result[field],prior[field],identity+' complete unchanged observed '+field)
        if identity in RESUME_CASES:
            resume_admissions.append(checked_observed_resume(identity,scenario,prior,result))
        else:
            same(result['timing']['streams'],prior['timing']['streams'],identity+' entire observed stream graph unchanged')
        same(result['estimate']['base_stats'],prior['estimate']['base_stats'],identity+' base attributes unchanged')
        if not case['expected_nonzero_complete_totals_unknown']:
            for phase in PHASES:
                actual=new['calls'][identity,phase]
                # Zero-total empty streams retain every old value, but the new
                # exact retained-ammunition explanation applies there as well.
                if shape=='empty_control':actual=zero_note_only(actual)
                elif identity in FULL_OBSERVATION_CONTROLS:
                    actual=reconstruct_full_observation_consumer(identity,scenario,phase,old['calls'][identity,phase],actual)
                same(actual,old['calls'][identity,phase],identity+' whole negative control consumer '+phase)
            if identity in FULL_OBSERVATION_CONTROLS:
                full_observation_admissions.append({'case':identity,
                    'only_reconstructed_raw_result_leaves':['execution_seconds','timing.streams[0].resume_frame'],
                    'all_three_complete_formatter_strings_exact':True,
                    'whole_consumer_graph_except_two_proven_raw_leaves_exact':True,
                    'full_cast_lifecycle_remains_exact':True})
            negative.append(identity)
        else:
            assert prior['estimate']['skill']['duration_seconds'] is not None
            assert prior['estimate']['skill']['total_damage'] is not None
            assert result['estimate']['skill']['duration_seconds'] is None and result['estimate']['skill']['total_damage'] is None
            for phase in PHASES[1:]:
                text=new['calls'][identity,phase]['result']
                assert '单次技能总伤：未知' in text
                if op=='kaltsit':assert '单次技能总治疗：未知' in text
            changes.append(identity)
    assert len(changes)==6 and len(negative)==5
    assert [row['case'] for row in resume_admissions]==list(RESUME_CASES)
    assert [row['case'] for row in full_observation_admissions]==list(FULL_OBSERVATION_CONTROLS)
    return {'cases':len(cases),'changed_partial_case_ids':changes,'negative_case_ids':negative,'empty_zero_controls_exact_added_note_removed_only':True,
        'fixed_eight_observed_resume_admissions':resume_admissions,
        'two_full_observation_raw_leaf_admissions':full_observation_admissions,
        'native_records_decoded':len(old['values'])+len(new['values']),
        'scope':'Six partial lifecycles retain whole caller/components/base attributes; only their fixed positively proven resume leaf changes within observed streams. Mechanical complete control compares the entire consumer exactly. Two Kaltsit complete/friendly controls independently retain full-cast lifecycle and all three complete strings; only fixed raw observation execution_seconds and streams[0].resume_frame are reconstructed to the original proven values before whole consumer comparison, preserving every other field and alias. Two zero-empty controls allow only the exact single added estimate note and its rendered bullet removal. Raw whole identity and partial entire graph/text identity are not claimed.'}

def load_window(folder,guard,guard_raw,cases):
    folder=Path(folder).resolve();r,raw=load_json(folder/'receipt.json')
    assert r['kind']=='ROOT_ACTUAL_119_REAL_MAINWINDOW' and r['phase']=='candidate'
    assert r['passed'] is True and r['workflow_complete'] is True and not r.get('failure')
    assert r['Qt_errors']==[] and r['source_drift']==[]
    assert r['runner_sha256']==GUI_RUNNER_SHA and r['native_helper_sha256']==HELPER_SHA
    assert r['source_guard_sha256']==sha(guard_raw)
    same(r['source_before'],guard['source_sha256'],'GUI Source before')
    same(r['source_after'],guard['source_sha256'],'GUI Source after')
    same(r['source_additional_before'],guard['source_additional_sha256'],'GUI CORE before')
    same(r['source_additional_after'],guard['source_additional_sha256'],'GUI CORE after')
    assert r['source_count']==len(guard['source_sha256']) and type(r['source_count']) is int
    assert r['actual_windows']==1 and r['private_state_access'] is False
    assert r['native_windows_verified'] is False and r['game_chat_sampling_executed'] is False
    values={};positions={}
    for sequence,m in enumerate(r['records'],1):
        assert m['path']=='%06d.pickle.gz'%sequence and m['path'] not in values
        v=read_record(folder/'records',m);assert v['kind']==m['kind']
        for key in ('case','phase'):same(v[key],m[key],'saved active metadata')
        values[m['path']]=v;positions[m['path']]=sequence
    assert {p.name for p in (folder/'records').iterdir()}==set(values)
    def get(ref,kind):
        name=ref['path'];assert name in positions
        same(ref,r['records'][positions[name]-1],'full linked ledger metadata')
        value=values[name];assert value['kind']==kind;return value
    permitted={'actual_calculate_result','actual_UI_step','actual_public_fixture_loaded',
        'actual_three_formatter_group','actual_window_snapshot','actual_PNG_complete_current_breakdown','actual_close_RunState_reload'}
    assert all(v['kind'] in permitted for v in values.values())
    numeric=[v for v in values.values() if v['kind']=='actual_calculate_result']
    assert len(numeric)==r['actual_numeric_calls'] and len(numeric)>=len(cases)
    for v in values.values():
        if v['kind']=='actual_calculate_result':same(v['after'],v['before'],'every numeric complete caller/context purity')
        elif v['kind']=='actual_UI_step':same(v['after']['joint'],v['before']['joint'],'every UI state/account/disk purity')
        elif v['kind']=='actual_three_formatter_group':same(v['after'],v['before'],'every three formatter whole graph/context purity')
    assert [row['id'] for row in r['rows']]==[case['id'] for case in cases]
    assert len(r['rows'])==22 and len(r['pairs'])==4 and len(r['pngs'])==2
    assert [m['path'] for m in r['records'] if m['kind']=='actual_window_snapshot']==[row['snapshot']['path'] for row in r['rows']]
    return {'folder':folder,'receipt':r,'raw':raw,'get':get,'values':values,'positions':positions,'numeric':numeric}

def audit_window(bundle,cases):
    r=bundle['receipt'];get=bundle['get'];initial=get(r['initial'],'actual_public_fixture_loaded')['value']
    snapshots={};ref_ids={}
    for row,case in zip(r['rows'],cases):
        identity=case['id'];saved=get(row['snapshot'],'actual_window_snapshot');value=saved['value']
        assert (row['operator'],row['mode'],row['shape'],row['window_seconds'])==(
            case['operator'],case['mode'],case['shape'],case['seconds'])
        same(saved['case_definition'],case,'whole sealed GUI case definition')
        numeric=get(row['numeric'],'actual_calculate_result')
        assert saved['case']==numeric['case']==identity and bundle['positions'][row['numeric']['path']]<bundle['positions'][row['snapshot']['path']]
        caller=value['caller'];result=value['damage_result']['result']
        same(caller,numeric['before']['args'][0],'whole GUI caller/numeric link')
        same(value['damage_result']['scenario'],caller,'whole saved UI scenario')
        same(result,numeric['result'],'whole saved numeric/UI result link')
        assert (caller['operator'],caller['skill'],caller['timing_mode'])==(case['operator'],case['skill'],case['mode'])
        assert (caller['elite'],caller['level'],caller['skill_rank'],caller['trust'],caller['potential'])==(2,1,7,0,1)
        assert caller['module_id'] is None and caller['module_level']==0 and caller['relic_ids']==[]
        assert caller['continuous_attacks'] is True and caller['healing_targets']==case['healing_targets']
        assert caller['enemy_defense']==0 and caller['enemy_resistance']==0
        assert 'base_attack' not in caller and 'target_enemy' not in caller
        same(caller['timing'],case['timing'],'actual declared timing')
        assert caller['window_seconds']==case['seconds']
        base=425 if case['operator']=='mechanist' else 408
        near(result['estimate']['base_stats']['attack'],base,'independent pinned native profile baseattack')
        want=numerical(case,base,result,caller)
        producer_oracle={key:want[key] for key in ('window_damage','window_healing','duration','full_damage','full_healing')}
        producer_oracle.update(incomplete=want['partial'],literal_base_attack=base)
        same(saved['manual_oracle'],producer_oracle,'saved GUI manual expectation independently derived')
        same(row['manual_oracle'],producer_oracle,'GUI row complete manual expectation metadata')
        same(value['state_and_disks'],initial,'every GUI snapshot retains all loaded run/account/public file bytes')
        assert tuple(value['texts'])==('estimate','default','technical')
        assert all(type(t) is str and t for t in value['texts'].values())
        assert value['texts']['estimate']==value['texts']['default']
        assert value['displayed_damage']==value['texts']['default'].replace(chr(160),' ')
        group=[(path,v) for path,v in bundle['values'].items() if v['kind']=='actual_three_formatter_group' and v['case']==identity]
        assert len(group)==1;group_path,formatter=group[0]
        assert bundle['positions'][row['numeric']['path']]<bundle['positions'][group_path]<bundle['positions'][row['snapshot']['path']]
        same(formatter['before'],{'damage_result':value['damage_result'],'joint':value['state_and_disks']},
            'entire formatter input graph and snapshot context, including cross-container aliases')
        same(formatter['before']['joint'],initial,'formatter input complete initial public context')
        same(formatter['texts'],value['texts'],'complete snapshot/formatter text link')
        snapshots[identity]=value;ref_ids[row['snapshot']['path']]=identity
    expected_pair_keys=[(op,mode) for op in ('mechanist','kaltsit') for mode in ('frames','continuous')]
    assert [(p['operator'],p['mode']) for p in r['pairs']]==expected_pair_keys
    seen_pair_refs=set()
    for pair in r['pairs']:
        complete_id=pair['operator']+'-'+pair['mode']+'-complete_control'
        short_id=pair['operator']+'-'+pair['mode']+'-short_control'
        complete_ref=pair['complete_snapshot']['path'];short_ref=pair['short_snapshot']['path']
        assert ref_ids.get(complete_ref)==complete_id and ref_ids.get(short_ref)==short_id
        assert complete_ref!=short_ref and (complete_ref,short_ref) not in seen_pair_refs
        seen_pair_refs.add((complete_ref,short_ref))
        assert bundle['positions'][complete_ref]<bundle['positions'][short_ref]
        complete=get(pair['complete_snapshot'],'actual_window_snapshot')['value']
        short=get(pair['short_snapshot'],'actual_window_snapshot')['value']
        normalized=freeze(short['caller']);normalized['window_seconds']=complete['caller']['window_seconds']
        same(normalized,complete['caller'],'entire complete/short GUI caller except exact window')
        same(short['state_and_disks'],complete['state_and_disks'],'complete/short state/account/disk')
        same({k:short['damage_result']['result']['estimate']['skill'][k] for k in LIFECYCLE},
            {k:complete['damage_result']['result']['estimate']['skill'][k] for k in LIFECYCLE},'all twelve unchanged full lifecycle fields')
        assert pair['all_lifecycle_fields_equal'] is True and pair['state_account_disks_preserved'] is True
    assert len(seen_pair_refs)==4
    pictures=[]
    for row,case in zip(r['pngs'],[c for c in cases if c['png']]):
        assert row['path']==case['id']+'.png' and Path(row['path']).name==row['path']
        path=bundle['folder']/row['path'];assert not path.is_symlink();raw=path.read_bytes()
        assert len(raw)==row['bytes'] and sha(raw)==row['sha256']
        assert raw[:8]==b'\x89PNG\r\n\x1a\n' and raw[12:16]==b'IHDR'
        width,height=struct.unpack('>II',raw[16:24]);assert width>0 and height>0
        visual=get(row['visual'],'actual_PNG_complete_current_breakdown')
        assert visual['case']==case['id'];value=snapshots[case['id']]
        same(visual['displayed_text'],value['displayed_damage'],'PNG complete captured report/native snapshot')
        block=next(b for b in value['damage_result']['result']['report']['sections'] if b['id']==('damage' if case['operator']=='mechanist' else 'healing'))
        assert visual['section']==block['id'] and visual['title']=='【'+block['title']+'】'
        assert visual['visible_blocks'][0]==visual['title']
        lines=value['displayed_damage'].split('\n');title=visual['title']
        assert lines.count(title)==1;start=lines.index(title)
        end=next((i for i in range(start+1,len(lines)) if lines[i].startswith('【') and lines[i].endswith('】')),len(lines))
        metric_positions=[]
        for metric in block['metrics']:
            prefix=visible_metric_label(metric['label'])+'：'
            hits=[i for i in range(start+1,end) if lines[i].startswith(prefix)]
            assert len(hits)==1;metric_positions.append(hits[0])
        assert metric_positions==sorted(metric_positions) and len(set(metric_positions))==len(metric_positions)
        same(visual['visible_blocks'],lines[start:metric_positions[-1]+1],
            'PNG exact contiguous title-through-final-metric excerpt of full saved displayed text')
        for m in block['metrics']:assert any(text.startswith(visible_metric_label(m['label'])+'：') for text in visual['visible_blocks'])
        x,y,w,h=visual['viewport_rect'];assert w>0 and h>0
        for a,b,c,d in visual['cursor_rects']:assert c>0 and d>0 and x<=a and y<=b and a+c<=x+w and b+d<=y+h
        assert len(visual['cursor_rects'])==2*len(visual['visible_blocks'])
        pictures.append({'path':row['path'],'sha256':row['sha256'],'width':width,'height':height,'section':block['id']})
    close=get(r['close_reload'],'actual_close_RunState_reload')
    same(close['live_before'],initial,'live public context before actual close')
    same(close['restart_state'],initial['run'],'direct RunState full accepted loaded graph')
    same(close['account_restart_records'],initial['account'],'direct AccountCache full accepted loaded graph')
    same(close['disks_after'],initial['disks'],'real close/direct reload public disk bytes')
    same(close['persisted_json'],json.loads(initial['disks']['run.json']),
        'real close persisted JSON exactly derived from original public file bytes')
    assert len([v for v in bundle['values'].values() if v['kind']=='actual_close_RunState_reload'])==1
    return {'states':len(snapshots),'lifecycle_pairs':len(r['pairs']),'native_records_decoded':len(bundle['values']),
        'actual_numeric_records':len(bundle['numeric']),'PNGs':pictures,
        'scope':'22 complete typed caller/result/UI/report saved states, four exact twelve-field lifecycle pairs, all numerical/UI/formatter joint purity, real close and two direct reloads. PNG bytes/metadata bounds checked; pixels require separate Root visual review.'}

def main():
    parser=argparse.ArgumentParser()
    for name in ('root','guard','original-guard','original-api','candidate-api','window','out'):
        parser.add_argument('--'+name,required=True)
    args=parser.parse_args();root=Path(args.root).resolve();out=Path(args.out).resolve();artifact=Path(__file__).resolve().parent
    assert not out.exists() and out!=root and root not in out.parents
    assert sha((artifact/'native_evidence.py').read_bytes())==HELPER_SHA
    api,api_raw=load_json(artifact/'api-cases.json');gui,gui_raw=load_json(artifact/'gui-cases.json')
    assert sha(api_raw)==API_FIXTURE_SHA and len(api['cases'])==11 and len(gui['cases'])==22
    guard,guard_raw=load_json(args.guard);original_guard,original_raw=load_json(args.original_guard)
    assert guard['section']==original_guard['section']==119
    assert set(guard['source_additional_sha256'])==set(original_guard['source_additional_sha256'])=={'CORE_0.70_VERIFICATION.json'}
    result={'kind':'ROOT_ACTUAL_INDEPENDENT_SAVED_119_API_GUI_AUDIT','passed':False,'workflow_complete':False,
        'auditor_sha256':sha(Path(__file__).read_bytes()),'native_helper_sha256':HELPER_SHA,
        'source_guard_sha256':sha(guard_raw),'original_guard_sha256':sha(original_raw),
        'project_API_formatter_reexecution':False,'PNG_pixels_visually_reviewed_by_this_auditor':False,
        'native_Windows_verified':False,'private_state_access':False,'source_drift':[]}
    receipt_pins=[]
    try:
        same(source_map(root),guard['source_sha256'],'current maintained candidate Source')
        for name,want in guard['source_additional_sha256'].items():assert sha((root/name).read_bytes())==want
        old=load_api(args.original_api,original_guard,original_raw,args.original_guard,'original',api['cases'])
        new=load_api(args.candidate_api,guard,guard_raw,args.guard,'candidate',api['cases'])
        result['API']=audit_api(old,new,api['cases'])
        window=load_window(args.window,guard,guard_raw,gui['cases']);result['GUI']=audit_window(window,gui['cases'])
        for path,raw in [(old['folder']/'observations.json',old['raw']),(new['folder']/'observations.json',new['raw']),
                         (window['folder']/'receipt.json',window['raw'])]:
            assert path.read_bytes()==raw;receipt_pins.append({'path':str(path),'bytes':len(raw),'sha256':sha(raw)})
        same(source_map(root),guard['source_sha256'],'current maintained Source after Saved audit')
        for name,want in guard['source_additional_sha256'].items():assert sha((root/name).read_bytes())==want
        assert Path(args.guard).read_bytes()==guard_raw and Path(args.original_guard).read_bytes()==original_raw
        result.update(passed=True,workflow_complete=True,actual_receipt_pins=receipt_pins)
    except BaseException as error:
        result['failure']={'type':type(error).__name__,'message':str(error),'traceback':traceback.format_exc()}
    out.parent.mkdir(parents=True,exist_ok=True)
    with out.open('x',encoding='utf-8') as stream:
        stream.write(json.dumps(result,ensure_ascii=False,indent=2)+'\n');stream.flush();os.fsync(stream.fileno())
    print(json.dumps({'passed':result['passed'],'out':str(out)}))
    return 0 if result['passed'] else 1

if __name__=='__main__':raise SystemExit(main())
