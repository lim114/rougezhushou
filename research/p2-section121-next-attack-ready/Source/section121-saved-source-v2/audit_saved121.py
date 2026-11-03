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
GUI_RUNNER_SHA='e14494e1ff2c21bce7ee58959917a7ad4436393cb7a12ca7e15cbad098d52fd6'
API_FIXTURE_SHA='8b38f4901ac9afb8a21cdcb0c3e0d23550aab2408fdf5aa4211cc32cf622c42d'
API_FIXTURE_BYTES=3795
GUI_FIXTURE_SHA='0f363a23a6b5cd1639e27a8ba4492059401fd54c3ec003bcefeb92ff9565e561'
GUI_FIXTURE_BYTES=3085
RUN_FIXTURE_SHA='8325efd6180807b682faf2117c8102c43cc5689ab0dcb5775721498628991c30'
RUN_FIXTURE_BYTES=1550
ACCOUNT_FIXTURE_SHA='21b585cf85edd6c6f7c26d70fb721fc2e0f6b57a9fe2b0f00e48e6aaaba2423b'
ACCOUNT_FIXTURE_BYTES=402
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


def numerical(mode,relics,seconds,base,result):
    skill=result['estimate']['skill'];initial=0.0 if relics else 144/30 if mode=='frames' else 3*1.6
    hits=0 if mode=='continuous' and seconds==1 else 1;per=base*2.75
    near(skill['initial_seconds'],initial,'independent ready/charging slot math')
    near(result['estimate']['base_stats']['attack'],base,'fixed public actual profile attack')
    near(result['total_damage'],hits*per,'known magic current skill damage')
    near(skill.get('window_damage',result['total_damage']),hits*per,'known magic observation damage')
    near(skill['total_damage'],per,'complete single skill release amount')
    near(skill['window_seconds'],seconds,'actual requested observation')
    assert skill['mode']=='next_attack'
    damage=[c for c in result['components'] if c['name']=='共鸣溃缩']
    assert len(damage)==hits
    for component in damage:
        assert component['damage_type']=='magic' and component['hits']==1
        near(component['per_hit'],per,'single magic release amount');near(component['total'],per,'one magic release total')
    buildup=sum(c['total'] for c in result['components'] if c['damage_type']=='buildup')
    near(buildup,per*.2*hits,'independent potential buildup separate from life damage')
    assert not any(c['name']=='神经损伤爆发' and c['hits'] for c in result['components'])
    assert not any(c['damage_type']=='elemental' and c['hits'] for c in result['components'])
    return {'initial_seconds':initial,'window_damage':per*hits,'full_damage':per,
        'window_buildup':per*.2*hits,'base_attack':base,'known_single_hit_magic_damage':per,'buildup_ratio':.2,'hits':hits}

def restore_only_initial(consumer,phase):
    """Rebuild only the independently proved two scalar sites + one rendered line."""
    normalized=freeze(consumer);seen=set();count=0
    def visit(value):
        nonlocal count
        if type(value) not in (dict,list,tuple) or id(value) in seen:return
        seen.add(id(value))
        if type(value) is dict:
            if type(value.get('estimate')) is dict and type(value.get('report')) is dict:
                skill=value['estimate']['skill'];same(skill['initial_seconds'],0.0,'new ready initial exactly float zero')
                skill['initial_seconds']=1.6
                block=next(b for b in value['report']['sections'] if b['id']=='timing')
                rows=[m for m in block['metrics'] if m['key']=='initial'];assert len(rows)==1
                same(rows[0]['value'],0.0,'new report ready initial exactly float zero');rows[0]['value']=1.6;count+=1
            for item in value.values():visit(item)
        else:
            for item in value:visit(item)
    visit(normalized)
    assert count==(1 if phase=='calculate_damage' else 2)
    if phase!='calculate_damage':
        lines=normalized['result'].split('\n');assert lines.count('预计初动：0.00 秒')==1
        lines[lines.index('预计初动：0.00 秒')]='预计初动：1.60 秒';normalized['result']='\n'.join(lines)
    return normalized

def audit_api(old,new,cases):
    changes=[];healthy=[]
    for case in cases:
        identity=case['id'];caller=case['scenario'];result=new['calls'][identity,'calculate_damage']['result'];prior=old['calls'][identity,'calculate_damage']['result']
        numerical(caller['timing_mode'],caller['relic_ids'],3,1000,result)
        changed=caller['timing_mode']=='continuous' and bool(caller['relic_ids'])
        if changed:
            same(prior['estimate']['skill']['initial_seconds'],1.6,'actual old illegal zero-cost wait');same(result['estimate']['skill']['initial_seconds'],0.0,'actual new ready legal slot')
            changes.append(identity)
        else:healthy.append(identity)
        for phase in PHASES:
            actual=new['calls'][identity,phase]
            if changed:actual=restore_only_initial(actual,phase)
            same(actual,old['calls'][identity,phase],identity+' complete actual consumer graph/string with only proved initial reconstruction')
    assert len(changes)==2 and len(healthy)==4
    return {'cases':6,'changed_ids':changes,'whole_healthy_consumer_ids':healthy,
        'native_records_decoded':len(old['values'])+len(new['values']),
        'scope':'All four unchanged API cases compare complete calculate+three formatter consumer graphs/texts exactly. Two ready continuous cases reconstruct only estimate.skill.initial_seconds, timing.initial report metric and single formatted initial line after proving old1.6/new0.0. No other field or string difference is allowed.'}
def load_window(folder,guard,guard_raw,cases):
    folder=Path(folder).resolve();r,raw=load_json(folder/'receipt.json')
    assert r['kind']=='ROOT_ACTUAL_121_REAL_MAINWINDOW' and r['phase']=='candidate'
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
        'actual_three_formatter_group','actual_window_snapshot','actual_PNG_complete_timing_damage','actual_close_RunState_reload'}
    assert all(v['kind'] in permitted for v in values.values())
    numeric=[v for v in values.values() if v['kind']=='actual_calculate_result']
    assert len(numeric)==r['actual_numeric_calls'] and len(numeric)>=len(cases)
    for v in values.values():
        if v['kind']=='actual_calculate_result':same(v['after'],v['before'],'every numeric complete caller/context purity')
        elif v['kind']=='actual_UI_step':same(v['after']['joint'],v['before']['joint'],'every UI state/account/disk purity')
        elif v['kind']=='actual_three_formatter_group':same(v['after'],v['before'],'every three formatter whole graph/context purity')
    assert [row['id'] for row in r['rows']]==[case['id'] for case in cases]
    assert len(r['rows'])==8 and len(r['pairs'])==6 and len(r['pngs'])==2
    assert [m['path'] for m in r['records'] if m['kind']=='actual_window_snapshot']==[row['snapshot']['path'] for row in r['rows']]
    return {'folder':folder,'receipt':r,'raw':raw,'get':get,'values':values,'positions':positions,'numeric':numeric}


def audit_window(bundle,cases):
    receipt=bundle['receipt'];get=bundle['get'];fixture=get(receipt['initial'],'actual_public_fixture_loaded');initial=fixture['value'];snapshots={};ref_ids={}
    assert (len(fixture['run_bytes']),sha(fixture['run_bytes']))==(RUN_FIXTURE_BYTES,RUN_FIXTURE_SHA)
    assert (len(fixture['account_bytes']),sha(fixture['account_bytes']))==(ACCOUNT_FIXTURE_BYTES,ACCOUNT_FIXTURE_SHA)
    same(initial['disks'],{'account.json':fixture['account_bytes'],'run.json':fixture['run_bytes']},'complete original public fixture disk bytes/order')
    lifecycle=('duration_seconds','total_damage','total_healing','phase_damage','phase_healing','recharge_seconds','cycle_seconds','cycle_damage','cycle_healing','cycle_dps','cycle_hps')
    positions=bundle['positions'];values=bundle['values']
    for row,case in zip(receipt['rows'],cases):
        identity=case['id'];saved=get(row['snapshot'],'actual_window_snapshot');value=saved['value'];numeric=get(row['numeric'],'actual_calculate_result')
        same(saved['case_definition'],case,'complete sealed real GUI case definition')
        assert (row['operator'],row['mode'],row['shape'],row['window_seconds'])==(case['operator'],case['mode'],case['shape'],case['seconds'])
        assert saved['case']==numeric['case']==identity and numeric['phase']=='explicit_snapshot'
        numeric_position=positions[row['numeric']['path']]
        # Bind exactly this direct calculate step, not every later numeric call
        # that happens to inherit the currently active case label.
        direct_meta=receipt['records'][numeric_position]
        direct=get(direct_meta,'actual_UI_step')
        assert direct['case']==identity and direct['phase']=='explicit_snapshot' and direct['label']=='MainWindow.calculate'
        same(direct['after']['damage_result'],value['damage_result'],'direct real MainWindow.calculate post-state equals complete snapshot result')
        caller=value['caller'];result=value['damage_result']['result']
        same(caller,numeric['before']['args'][0],'whole numeric public caller/UI link');same(numeric['before']['kwargs'],{},'direct GUI numeric kwargs empty')
        same(value['damage_result']['scenario'],caller,'whole saved GUI scenario');same(result,numeric['result'],'whole GUI numeric return link')
        assert (caller['operator'],caller['skill'],caller['elite'],caller['level'],caller['skill_rank'],caller['trust'],caller['potential'])==('char_4204_mantra',1,2,1,7,0,1)
        assert caller['timing_mode']==case['mode'] and caller['module_id'] is None and caller['module_level']==0
        same(caller['relic_ids'],case['relic_ids'],'actual birthSP selected relic list')
        same(caller['inventory_status'],{'source':'manual_test','complete':True,'recognized':len(case['relic_ids']),'expected_count':None},'actual manual caller inventory qualification')
        assert 'relic_history_context' not in caller and 'base_attack' not in caller and 'target_enemy' not in caller
        assert caller['continuous_attacks'] is True and caller['healing_targets']==0
        assert caller['enemy_defense']==0 and caller['enemy_resistance']==0
        assert caller['initial_neural_buildup']==0 and caller['enemy_in_neural_break'] is False and caller['enemy_is_boss'] is False and caller['palsy_triggers']==0
        same(caller['timing'],case['timing'],'actual advanced manual reference');assert caller['window_seconds']==case['seconds']
        want=numerical(case['mode'],case['relic_ids'],case['seconds'],583,result)
        same(saved['manual_oracle'],want,'producer whole manual oracle independently derived');same(row['manual_oracle'],want,'row whole manual oracle metadata')
        same(value['state_and_disks'],initial,'snapshot entire accepted Run/Account/public-disk graph')
        same(numeric['before']['joint'],initial,'direct numeric whole joint input context');same(direct['after']['joint'],initial,'direct UI-step accepted context')
        assert tuple(value['texts'])==('estimate','default','technical') and all(type(t) is str and t for t in value['texts'].values())
        assert value['texts']['estimate']==value['texts']['default'] and value['displayed_damage']==value['texts']['default'].replace(chr(160),' ')
        if case['relic_ids']:
            for text in value['texts'].values():assert text.split('\n').count('预计初动：0.00 秒')==1
        group=[(path,v) for path,v in values.items() if v['kind']=='actual_three_formatter_group' and v['case']==identity]
        assert len(group)==1;group_path,formatter=group[0]
        assert numeric_position<positions[direct_meta['path']]<positions[group_path]<positions[row['snapshot']['path']]
        same(formatter['before'],{'damage_result':value['damage_result'],'joint':value['state_and_disks']},'entire formatter input/context with cross-container aliases')
        same(formatter['before']['joint'],initial,'whole formatter joint equals original accepted public graph')
        same(formatter['texts'],value['texts'],'all three complete texts exactly bound to their formatter group')
        same(saved['technical_timing_excerpt'],{'initial_seconds':result['estimate']['skill']['initial_seconds'],'timing':result['timing'],
            'report_blocks':[b for b in result['report']['sections'] if b['id'] in ('timing','damage')]},'complete saved technical excerpt')
        snapshots[identity]=value;ref_ids[row['snapshot']['path']]=identity
    expected=[]
    for mode in ('frames','continuous'):
        expected.extend([(mode,'noSP_vs_ready',mode+'-98'),(mode,'noSP_vs_ready',mode+'-99'),(mode,'ready_complete_vs_short',mode+'-98-short')])
    assert [(pair['mode'],pair['type'],ref_ids.get((pair.get('ready_snapshot') or pair.get('short_snapshot'))['path'],'').removeprefix('mantra-')) for pair in receipt['pairs']]==expected
    used=set()
    for pair in receipt['pairs']:
        mode=pair['mode'];short=pair['type']=='ready_complete_vs_short'
        prior_ref=pair['complete_snapshot'] if short else pair['without_SP_snapshot'];other_ref=pair['short_snapshot'] if short else pair['ready_snapshot']
        assert (prior_ref['path'],other_ref['path']) not in used and positions[prior_ref['path']]<positions[other_ref['path']];used.add((prior_ref['path'],other_ref['path']))
        prior=get(prior_ref,'actual_window_snapshot')['value'];other=get(other_ref,'actual_window_snapshot')['value'];normalized=freeze(other['caller'])
        if short:
            assert ref_ids[prior_ref['path']]=='mantra-'+mode+'-98' and ref_ids[other_ref['path']]=='mantra-'+mode+'-98-short'
            normalized['window_seconds']=prior['caller']['window_seconds'];fields=(*lifecycle,'initial_seconds')
            assert pair['all_lifecycle_fields_equal'] is True
        else:
            assert ref_ids[prior_ref['path']]=='mantra-'+mode+'-none' and ref_ids[other_ref['path']] in ('mantra-'+mode+'-98','mantra-'+mode+'-99')
            normalized['relic_ids']=prior['caller']['relic_ids'];normalized['inventory_status']=prior['caller']['inventory_status'];fields=lifecycle
            same(other['damage_result']['result']['components'],prior['damage_result']['result']['components'],'birthSP no current output graph change')
            assert pair['complete_current_caller_only_relic_selection_changes'] is True and pair['full_component_graph_equal'] is True and pair['all_noninitial_lifecycle_fields_equal'] is True
        same(normalized,prior['caller'],'entire actual paired caller with exact independently qualified changed inputs')
        same(other['state_and_disks'],prior['state_and_disks'],'paired entire public state/disk graph')
        same({k:other['damage_result']['result']['estimate']['skill'][k] for k in fields},{k:prior['damage_result']['result']['estimate']['skill'][k] for k in fields},'entire actual pair complete lifecycle projection')
        assert pair['state_account_disks_preserved'] is True
    assert len(used)==6
    pictures=[]
    for row,case in zip(receipt['pngs'],[c for c in cases if c['png']]):
        assert row['path']==case['id']+'.png' and Path(row['path']).name==row['path']
        path=bundle['folder']/row['path'];assert not path.is_symlink();raw=path.read_bytes();assert len(raw)==row['bytes'] and sha(raw)==row['sha256']
        assert raw[:8]==b'\x89PNG\r\n\x1a\n' and raw[12:16]==b'IHDR';width,height=struct.unpack('>II',raw[16:24]);assert width>0 and height>0
        visual=get(row['visual'],'actual_PNG_complete_timing_damage');snapshot=snapshots[case['id']];result=snapshot['damage_result']['result']
        assert visual['case']==case['id'] and visual['technical_view'] is case['technical_png'];same(visual['section_ids'],('timing','damage'),'bounded visual actual report section IDs')
        displayed=snapshot['texts']['technical' if case['technical_png'] else 'default'].replace(chr(160),' ')
        same(visual['displayed_text'],displayed,'actual PNG complete display bound to exact default/technical saved text')
        timing=next(b for b in result['report']['sections'] if b['id']=='timing');damage=next(b for b in result['report']['sections'] if b['id']=='damage')
        same(visual['full_timing_block'],timing,'complete actual PNG timing block');same(visual['full_damage_block'],damage,'complete actual PNG damage block')
        lines=displayed.split('\n');first='【'+timing['title']+'】';second='【'+damage['title']+'】'
        assert lines.count(first)==lines.count(second)==1;start=lines.index(first);damage_start=lines.index(second);assert start<damage_start
        end=next((i for i in range(damage_start+1,len(lines)) if lines[i].startswith('【') and lines[i].endswith('】')),len(lines))
        same(visual['visible_blocks'],lines[start:end],'exact contiguous full timing-through-damage document blocks, including the original blank separator')
        for block,lo,hi in [(timing,start,damage_start),(damage,damage_start,end)]:
            offsets=[]
            for metric in block['metrics']:
                prefix=visible_metric_label(metric['label'])+'：';matches=[i for i in range(lo+1,hi) if lines[i].startswith(prefix)];assert len(matches)==1;offsets.append(matches[0])
            assert offsets==sorted(offsets) and len(set(offsets))==len(offsets)
        assert '预计初动：0.00 秒' in visual['visible_blocks']
        x,y,w,h=visual['viewport_rect'];assert w>0 and h>0 and len(visual['cursor_rects'])==2*len(visual['visible_blocks'])
        for a,b,c,d in visual['cursor_rects']:assert c>0 and d>0 and x<=a and y<=b and a+c<=x+w and b+d<=y+h
        assert positions[row['visual']['path']]>positions[next(r['snapshot']['path'] for r in receipt['rows'] if r['id']==case['id'])]
        pictures.append({'path':row['path'],'sha256':row['sha256'],'width':width,'height':height,'technical_view':case['technical_png']})
    close=get(receipt['close_reload'],'actual_close_RunState_reload')
    assert positions[receipt['close_reload']['path']]>max(positions[row['snapshot']['path']] for row in receipt['rows'])
    same(close['live_before'],initial,'real close complete accepted live context');same(close['restart_state'],initial['run'],'direct RunState accepted graph')
    same(close['account_restart_records'],initial['account'],'direct AccountCache accepted graph');same(close['disks_after'],initial['disks'],'real close/direct reload entire public diskbytes')
    same(close['persisted_json'],json.loads(initial['disks']['run.json']),'persisted public run graph from original exact fixture bytes')
    assert len([v for v in values.values() if v['kind']=='actual_close_RunState_reload'])==1
    return {'states':8,'paired_actual_snapshots':6,'native_records_decoded':len(values),'actual_numeric_records':len(bundle['numeric']),'PNGs':pictures,
        'scope':'Every complete caller/result/UI/native/three-text/joint graph and producer reference verified, exact direct calculate boundary distinguished from other legitimate active-case calls; six full lifecycle pairs and actual close/direct dual reload. PNG metadata bounds checked; pixels require Root visual review.'}
def main():
    parser=argparse.ArgumentParser()
    for name in ('root','guard','original-guard','original-api','candidate-api','window','out'):
        parser.add_argument('--'+name,required=True)
    args=parser.parse_args();root=Path(args.root).resolve();out=Path(args.out).resolve();artifact=Path(__file__).resolve().parent
    assert not out.exists() and out!=root and root not in out.parents
    assert sha((artifact/'native_evidence.py').read_bytes())==HELPER_SHA
    assert (len((artifact/'expected-run.json').read_bytes()),sha((artifact/'expected-run.json').read_bytes()))==(RUN_FIXTURE_BYTES,RUN_FIXTURE_SHA)
    assert (len((artifact/'expected-account.json').read_bytes()),sha((artifact/'expected-account.json').read_bytes()))==(ACCOUNT_FIXTURE_BYTES,ACCOUNT_FIXTURE_SHA)
    api,api_raw=load_json(artifact/'api-cases.json');gui,gui_raw=load_json(artifact/'gui-cases.json')
    assert (len(api_raw),sha(api_raw))==(API_FIXTURE_BYTES,API_FIXTURE_SHA)
    assert (len(gui_raw),sha(gui_raw))==(GUI_FIXTURE_BYTES,GUI_FIXTURE_SHA)
    assert len(api['cases'])==6 and len(gui['cases'])==8
    guard,guard_raw=load_json(args.guard);original_guard,original_raw=load_json(args.original_guard)
    assert guard['section']==original_guard['section']==121
    assert set(guard['source_additional_sha256'])==set(original_guard['source_additional_sha256'])=={'CORE_0.70_VERIFICATION.json'}
    result={'kind':'ROOT_ACTUAL_INDEPENDENT_SAVED_121_API_GUI_AUDIT','passed':False,'workflow_complete':False,
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
        assert (artifact/'api-cases.json').read_bytes()==api_raw and (artifact/'gui-cases.json').read_bytes()==gui_raw
        result.update(passed=True,workflow_complete=True,actual_receipt_pins=receipt_pins)
    except BaseException as error:
        result['failure']={'type':type(error).__name__,'message':str(error),'traceback':traceback.format_exc()}
    out.parent.mkdir(parents=True,exist_ok=True)
    with out.open('x',encoding='utf-8') as stream:
        stream.write(json.dumps(result,ensure_ascii=False,indent=2)+'\n');stream.flush();os.fsync(stream.fileno())
    print(json.dumps({'passed':result['passed'],'out':str(out)}))
    return 0 if result['passed'] else 1

if __name__=='__main__':raise SystemExit(main())
