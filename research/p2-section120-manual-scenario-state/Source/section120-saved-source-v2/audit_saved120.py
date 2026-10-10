"""Source proposal only. Root executes saved evidence reads; no project imports."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import struct
import traceback
from native_evidence import read_record, assert_native_equal as same, source_map

HELPER_SHA='f040258eddbb7ad624e547e2c422a3d432f7ffeae025b2576b625683ea43fe9a'
RUNNER_SHA='20116467c8260f163de914dd707ffb314a2fab5a6e28d3c2ba82c3a37911387b'
A='mechanist';B='char_002_amiya';DEEP='char_110_deepcl';TOKEN='token_10001_deepcl_tentac';CARGO='rogue_6_relic_cargo_2'
A_TIMING='{ "windup_frames" : 0, "recovery_frames" : 0, "target_windows" : [] }\n'
A_RELIC='{ "parts_count" : 0, "unused" : "A 原文" }\n'
B_TIMING='{"windup_frames":0,"recovery_frames":0,"target_windows":[[0,5]]} '
B_RELIC='{"parts_count":3,"unused":"B 原文"} '
POISON_TIMING='{"windup_frames":0,"recovery_frames":0,"target_windows":[[0,2]]}'
POISON_RELIC='{"parts_count":1,"unused":"unsupported edit"}'
API_IDS=('mechanist_empty_target','amiya_empty_target','amiya_nonempty','deepcolor_token_independent','relic_parts_zero','relic_parts_three')
GROUP_IDS=('valid_owner_pair','profile_only_with_skill','profile_only_without_skill','empty_overview','no_current_skill',
    'skill_pair','bad_valid_owner_back','bad_relic_not_needed','ambiguous_target_duplicate','nested_unit_duplicate',
    'relic_duplicate','nonfinite_literals','strings_and_ordinary_JSON','empty_omission')
SNAPSHOT_IDS=tuple('legal-'+x for x in API_IDS)+('valid-owner-A-before','valid-owner-B','valid-owner-A-return')+tuple(
    x+y for x in GROUP_IDS[1:5] for y in ('-owner-before','-owner-return'))+(
    'skill-pair-S1-before','skill-pair-S3','skill-pair-S1-return','bad-owner-A-before','bad-owner-B-valid','bad-owner-A-return',
    'needed-bad-relic-before','not-needed-bad-relic-ignored','needed-bad-relic-restored','ambiguous-target-0','ambiguous-target-1',
    'nested-unit-duplicate','duplicate-relic-0','duplicate-relic-1','nonfinite-unused-NaN','nonfinite-unused-Infinity',
    'nonfinite-unused--Infinity','nonfinite-unused-1e309','ordinary-string-NAN','blank-timing-0','blank-timing-1')
KNOWN_BAD={'bad-owner-A-before':'战斗时序情景需要合法JSON对象。','bad-owner-A-return':'战斗时序情景需要合法JSON对象。',
    'needed-bad-relic-before':'藏品测试条件需要合法JSON对象。','needed-bad-relic-restored':'藏品测试条件需要合法JSON对象。'}
NEW_BAD={**{x:'战斗时序情景不接受重复字段：target_windows。' for x in ('ambiguous-target-0','ambiguous-target-1','nested-unit-duplicate')},
    **{x:'藏品测试条件不接受重复字段：parts_count。' for x in ('duplicate-relic-0','duplicate-relic-1')},
    **{x:'战斗时序情景不接受非有限JSON数值。' for x in ('nonfinite-unused-NaN','nonfinite-unused-Infinity','nonfinite-unused--Infinity','nonfinite-unused-1e309')}}

def sha(raw):return hashlib.sha256(raw).hexdigest()
def read_json(path):
    raw=Path(path).read_bytes();return json.loads(raw),raw

def load_bundle(folder,guard,guard_raw,phase,cases):
    folder=Path(folder).resolve();r,raw=read_json(folder/'receipt.json')
    assert r['kind']=='ROOT_ACTUAL_120_REAL_MAINWINDOW' and r['section']==120 and r['phase']==phase
    assert not r.get('failure') and r['Qt_errors']==[] and r['source_drift']==[]
    assert r['runner_sha256']==RUNNER_SHA and r['native_helper_sha256']==HELPER_SHA
    assert r['source_guard_sha256']==sha(guard_raw) and r['source_count']==len(guard['source_sha256']) and type(r['source_count']) is int
    for k in ('before','after'):
        same(r['source_'+k],guard['source_sha256'],'phase whole Source '+k)
        same(r['source_additional_'+k],guard['source_additional_sha256'],'phase CORE '+k)
    assert r['actual_windows']==1 and r['deadline_seconds']==900
    assert r['private_state_access'] is False and r['native_windows_verified'] is False and r['game_chat_sampling_executed'] is False
    if phase=='original':
        assert r['passed'] is False and r['workflow_complete'] is False and r['observation_complete'] is True and r['original_issue_observed'] is True
    else:
        assert r['passed'] is True and r['workflow_complete'] is True and r['observation_complete'] is False
    values={};positions={};refs={}
    for sequence,ref in enumerate(r['records'],1):
        assert ref['path']=='%06d.pickle.gz'%sequence and ref['path'] not in values
        value=read_record(folder/'records',ref)
        for k in ('kind','case','phase'):same(value[k],ref[k],'all native active metadata')
        values[ref['path']]=value;positions[ref['path']]=sequence;refs[ref['path']]=ref
    assert {p.name for p in (folder/'records').iterdir()}==set(values)
    def get(ref,kind):
        assert ref['path'] in refs;same(ref,refs[ref['path']],'whole ref/hash/length/native metadata binding')
        v=values[ref['path']];assert v['kind']==kind;return v
    initial_record=get(r['initial'],'actual_public_fixture_loaded');initial=initial_record['value']
    assert initial_record['case']=='bootstrap' and initial_record['phase']=='constructor'
    assert initial['disks']['run.json']==initial_record['run_bytes'] and initial['disks']['account.json']==initial_record['account_bytes']
    numeric=[v for v in values.values() if v['kind']=='actual_calculate_result']
    assert len(numeric)==r['actual_numeric_calls'] and len(numeric)>=6
    allowed={'actual_public_fixture_loaded','actual_calculate_result','actual_UI_step','actual_three_formatter_group',
        'actual_exact_public_API_snapshot','actual_valid_window_snapshot','actual_invalid_window_snapshot','actual_editor_workflow_group',
        'actual_invalid_selection','actual_PNG_bounded_editor_report_excerpt','actual_close_RunState_reload'}
    assert all(v['kind'] in allowed for v in values.values())
    for v in values.values():
        if v['kind']=='actual_calculate_result':
            same(v['after'],v['before'],'every complete numeric caller/context purity')
            if 'joint' in v['before']:same(v['before']['joint'],initial,'every numeric joint original state/disk')
        elif v['kind']=='actual_UI_step':
            same(v['before']['joint'],initial,'UI before complete original public context')
            same(v['after']['joint'],initial,'UI after complete original public context')
        elif v['kind']=='actual_three_formatter_group':
            same(v['after'],v['before'],'every three formatter whole numeric/editor/public context purity')
            same(v['before']['joint'],initial,'formatter original public context')
    assert [x['id'] for x in r['API_rows']]==list(API_IDS) and len(r['API_rows'])==6
    assert [x['id'] for x in r['rows']]==list(SNAPSHOT_IDS) and len(r['rows'])==38
    assert [x['id'] for x in r['groups']]==list(GROUP_IDS) and len(r['groups'])==14
    assert len(r['pngs'])==2 and r['pairs']==[]
    assert [x['path'] for x in r['records'] if x['kind'] in ('actual_valid_window_snapshot','actual_invalid_window_snapshot')]==[x['snapshot']['path'] for x in r['rows']]
    api={}
    for row,case in zip(r['API_rows'],cases):
        v=get(row['snapshot'],'actual_exact_public_API_snapshot');n=get(v['numeric'],'actual_calculate_result')
        assert v['case']==n['case']=='API-'+case['id'] and v['phase']==n['phase']=='exact_public_API'
        assert positions[v['numeric']['path']]<positions[row['snapshot']['path']]
        same(v['input'],case['input'],'exact public API sealed input')
        same(n['before']['args'],(v['input'],),'whole API typed caller tuple')
        same(n['before']['kwargs'],{},'whole API kwargs')
        same(n['result'],v['result'],'whole API numerical result ref')
        same({'input':n['after']['args'][0],'result':n['result']},{'input':v['input'],'result':v['result']},
            'API before-formatter/post-formatter whole input-result graph including cross-field aliases')
        assert tuple(v['texts'])==('estimate','default','technical') and v['texts']['estimate']==v['texts']['default']
        assert all(type(x) is str and x for x in v['texts'].values());api[row['id']]=v
    snapshots={};snapshot_refs={};bad={**KNOWN_BAD,**(NEW_BAD if phase=='candidate' else {})}
    for row in r['rows']:
        identity=row['id'];valid=identity not in bad;assert row['valid'] is valid
        v=get(row['snapshot'],'actual_valid_window_snapshot' if valid else 'actual_invalid_window_snapshot');x=v['value']
        assert v['case']==identity and v['phase']=='explicit_actual_snapshot'
        same(x['state_and_disks'],initial,'each snapshot original run/account/disk')
        e=x['editors'];assert e['timing_blocked'] is False and e['relic_blocked'] is False
        # Active case stays unchanged during later setters. Bind only the actual
        # explicit calculate callback, bounded by adjacent saved UI steps.
        steps=[(p,z) for p,z in values.items() if z['kind']=='actual_UI_step' and z['case']==identity and z['label']=='actual MainWindow.calculate']
        assert len(steps)==1;step_path,step=steps[0];end=positions[step_path]
        prior=[positions[p] for p,z in values.items() if z['kind']=='actual_UI_step' and positions[p]<end]
        assert prior;start=max(prior)
        assert start<end<positions[row['snapshot']['path']]
        same(step['before']['editors'],e,'explicit calculate entry editor graph')
        same(step['after']['editors'],e,'explicit calculate exit editor graph')
        same(step['after']['damage_result'],x['damage_result'],'explicit calculate exit exact snapshot result')
        interval=[(p,z) for p,z in values.items() if start<positions[p]<end]
        interval_numeric=[(p,z) for p,z in interval if z['kind']=='actual_calculate_result']
        if valid:
            n=get(v['numeric'],'actual_calculate_result');assert n['case']==identity
            assert [p for p,z in interval_numeric]==[v['numeric']['path']]
            assert positions[v['numeric']['path']]<positions[row['snapshot']['path']]
            same(x['caller'],n['before']['args'][0],'full GUI caller/numeric link')
            same(x['damage_result']['scenario'],x['caller'],'full GUI scenario/caller')
            same(x['damage_result']['result'],n['result'],'full GUI result/numeric link')
            same(n['before']['kwargs'],{},'GUI kwargs empty')
            c=x['caller'];assert c['operator']==e['operator'] and c['skill']==e['skill'] and e['key']==(e['operator'],e['skill'])
            assert c['timing_mode']=='frames' and c['window_seconds']==5 and c['enemy_defense']==0 and c['enemy_resistance']==0
            assert c['healing_targets']==1 and c['continuous_attacks'] is True and c['potential']==1 and c['trust']==0
            assert c['module_id'] is None and c['module_level']==0 and 'base_attack' not in c and 'target_enemy' not in c
            assert tuple(x['texts'])==('estimate','default','technical') and x['texts']['estimate']==x['texts']['default']
            assert all(type(z) is str and z for z in x['texts'].values())
            assert x['displayed_damage']==x['texts']['default'].replace(chr(160),' ')
            fmt=[(p,z) for p,z in values.items() if z['kind']=='actual_three_formatter_group' and z['case']==identity]
            assert len(fmt)==1 and positions[v['numeric']['path']]<positions[fmt[0][0]]<positions[row['snapshot']['path']]
            same(fmt[0][1]['before']['damage_result'],x['damage_result'],'complete formatter/snapshot numerical graph')
            same(fmt[0][1]['before']['editors'],e,'complete formatter/snapshot editor graph')
            same(fmt[0][1]['texts'],x['texts'],'all complete formatter/snapshot text strings')
        else:
            assert x['damage_result'] is None and v['error_fragment']==bad[identity] and bad[identity] in x['displayed_error']
            assert interval_numeric==[]
            assert not any(z['kind']=='actual_three_formatter_group' and end<positions[p]<positions[row['snapshot']['path']] for p,z in values.items())
        snapshots[identity]=x;snapshot_refs[identity]=row['snapshot']
    return {'folder':folder,'receipt':r,'raw':raw,'values':values,'positions':positions,'get':get,'initial':initial,
        'API':api,'snapshots':snapshots,'snapshot_refs':snapshot_refs,'numeric_count':len(numeric)}

def audit_workflows(bundle,phase):
    r=bundle['receipt'];get=bundle['get'];sn=bundle['snapshots'];refs=bundle['snapshot_refs']
    def snapshot(ref,identity):
        same(ref,refs[identity],'group intended snapshot complete ref identity');return sn[identity]
    def restoration(before,after,label):
        same(after['damage_result'],before['damage_result'],label+' whole caller/result')
        same(after['texts'],before['texts'],label+' all three whole formatter strings')
    for row in r['groups']:
        identity=row['id'];g=get(row['record'],'actual_editor_workflow_group');assert g['id']==identity
        if identity=='valid_owner_pair':
            a=snapshot(g['before'],'valid-owner-A-before');b=snapshot(g['after'],'valid-owner-A-return');restoration(a,b,identity)
            assert b['editors']['timing_text']==A_TIMING and b['editors']['relic_text']==A_RELIC
        elif identity in GROUP_IDS[1:5]:
            a=snapshot(g['before'],identity+'-owner-before');b=snapshot(g['after'],identity+'-owner-return')
            invalid=get(g['invalid'],'actual_invalid_selection');e=invalid['value']
            assert invalid['case']==identity+'-owner-before'
            assert g['original_pollution_observed'] is (phase=='original') and g['candidate_restoration_checked'] is (phase=='candidate')
            assert a['editors']['timing_text']==A_TIMING and a['editors']['relic_text']==A_RELIC
            if phase=='original':
                assert e['key']==(B if identity=='no_current_skill' else A,1) and e['timing_enabled'] is True and e['relic_enabled'] is True
                assert e['timing_text']==A_TIMING and e['relic_text']==A_RELIC
                assert b['editors']['timing_text']==POISON_TIMING and b['editors']['relic_text']==POISON_RELIC
                same(b['caller']['timing'],json.loads(POISON_TIMING),'actual original stale/poison timing')
                assert b['caller']['relic_context']=={'parts_count':1}
            else:
                assert e['key'] is None and e['timing_text']=='' and e['relic_text']==''
                assert e['timing_enabled'] is False and e['relic_enabled'] is False
                assert b['editors']['timing_text']==A_TIMING and b['editors']['relic_text']==A_RELIC;restoration(a,b,identity)
            if identity=='profile_only_with_skill':assert e['operator']=='char_120_hibisc'
            elif identity=='profile_only_without_skill':assert e['operator']=='char_285_medic2'
            elif identity=='empty_overview':assert e['operator'] is None
            else:assert e['operator']==B and e['skill'] is None
        elif identity=='skill_pair':
            a=snapshot(g['before'],'skill-pair-S1-before');b=snapshot(g['after'],'skill-pair-S1-return');restoration(a,b,identity)
            assert b['editors']['timing_text']==B_TIMING and b['editors']['relic_text']==B_RELIC
        elif identity=='bad_valid_owner_back':
            a=snapshot(g['before'],'bad-owner-A-before');b=snapshot(g['after'],'bad-owner-A-return')
            assert a['editors']['timing_text']==b['editors']['timing_text']=='{'
            assert a['displayed_error']==b['displayed_error']
        elif identity=='bad_relic_not_needed':
            a=snapshot(g['active_before'],'needed-bad-relic-before');u=snapshot(g['ignored'],'not-needed-bad-relic-ignored');b=snapshot(g['active_after'],'needed-bad-relic-restored')
            assert a['editors']['relic_text']==u['editors']['relic_text']==b['editors']['relic_text']=='{'
            assert u['caller']['relic_context']=={} and u['editors']['relic_row_visible'] is False
        elif identity in ('ambiguous_target_duplicate','relic_duplicate','nonfinite_literals','empty_omission'):
            names={'ambiguous_target_duplicate':('ambiguous-target-0','ambiguous-target-1'),
                'relic_duplicate':('duplicate-relic-0','duplicate-relic-1'),
                'nonfinite_literals':('nonfinite-unused-NaN','nonfinite-unused-Infinity','nonfinite-unused--Infinity','nonfinite-unused-1e309'),
                'empty_omission':('blank-timing-0','blank-timing-1')}[identity]
            assert len(g['snapshots'])==len(names)
            for ref,name in zip(g['snapshots'],names):
                x=snapshot(ref,name);e=x['editors']
                if identity=='empty_omission':
                    assert e['timing_text']==('' if name.endswith('0') else '   ') and e['relic_text']==''
                    assert 'timing' not in x['caller'] and x['caller']['relic_context']=={}
                elif phase=='original':
                    key='relic_context' if identity=='relic_duplicate' else 'timing';editor='relic_text' if identity=='relic_duplicate' else 'timing_text'
                    same(x['caller'][key],json.loads(e[editor]),'actual original ambiguous/nonfinite admitted dict')
        elif identity=='nested_unit_duplicate':
            x=snapshot(g['snapshot'],'nested-unit-duplicate')
            if phase=='original':same(x['caller']['timing'],json.loads(x['editors']['timing_text']),'actual original nested last duplicate')
        elif identity=='strings_and_ordinary_JSON':
            x=snapshot(g['snapshot'],'ordinary-string-NAN');assert x['caller']['timing']['unrelated']=='NaN' and x['caller']['relic_context']=={'parts_count':0}
            assert x['editors']['relic_text']==A_RELIC and g['unknown_relic_key_filtered_by_existing_needed_gate'] is True
        else:raise AssertionError('uncovered workflow '+identity)
        # Actual final editors belong to the final snapshot named by the group.
        final_ref=g.get('after',g.get('active_after',g.get('snapshot')))
        if final_ref is None:final_ref=g['snapshots'][-1]
        final=get(final_ref,'actual_valid_window_snapshot' if final_ref['kind']=='actual_valid_window_snapshot' else 'actual_invalid_window_snapshot')
        assert g['case']==final['case'] and g['phase']==final['phase']=='explicit_actual_snapshot'
        same(g['final_editors'],final['value']['editors'],identity+' full final editor link')
    return {'groups':len(r['groups']),'original_pollution_groups':4 if phase=='original' else 0,'candidate_restoration_groups':4 if phase=='candidate' else 0}

def audit_png_close(bundle):
    r=bundle['receipt'];get=bundle['get'];pictures=[]
    for row,name in zip(r['pngs'],('legal-context-editor','profile-only-editor-scope')):
        assert row['path']==name+'.png' and Path(row['path']).name==row['path']
        p=bundle['folder']/row['path'];assert not p.is_symlink();raw=p.read_bytes()
        assert len(raw)==row['bytes'] and sha(raw)==row['sha256'] and raw[:8]==b'\x89PNG\r\n\x1a\n' and raw[12:16]==b'IHDR'
        width,height=struct.unpack('>II',raw[16:24]);assert width>0 and height>0
        v=get(row['visual'],'actual_PNG_bounded_editor_report_excerpt');assert v['entire_long_report_visible'] is False
        if name=='legal-context-editor':
            x=bundle['snapshots']['valid-owner-A-before'];assert v['case']=='valid-owner-A-before'
            same(v['editors'],x['editors'],'legal PNG full editor graph');same(v['displayed_text'],x['displayed_damage'],'legal PNG complete displayed string')
            block=next(b for b in x['damage_result']['result']['report']['sections'] if b['id']=='calculation_context')
            assert v['title']=='【'+block['title']+'】';lines=v['displayed_text'].split('\n');start=lines.index(v['title'])
            finish=next(i for i in range(start,len(lines)) if lines[i].startswith(block['metrics'][-1]['label']+'：'))
            same(v['visible_report_blocks'],lines[start:finish+1],'PNG exact consecutive title through last context metric')
        else:
            invalid=[x for x in bundle['values'].values() if x['kind']=='actual_invalid_selection' and x['value']['operator']=='char_120_hibisc']
            assert len(invalid)==1 and v['case']=='profile_only_with_skill-owner-before' and v['title'] is None
            prior=[(p,z) for p,z in bundle['values'].items() if z['kind']=='actual_UI_step' and bundle['positions'][p]<bundle['positions'][row['visual']['path']]]
            assert prior;last=max(prior,key=lambda item:bundle['positions'][item[0]])[1]
            same(v['editors'],last['after']['editors'],'profile-only PNG exact current post-UI-step full editor graph')
            if r['phase']=='original':
                assert v['editors']['timing_text']==POISON_TIMING and v['editors']['relic_text']==POISON_RELIC
                assert v['editors']['key']==(A,1) and v['editors']['timing_enabled'] is True and v['editors']['relic_enabled'] is True
            else:same(v['editors'],invalid[0]['value'],'candidate PNG actual disabled editor graph')
            same(v['displayed_text'],invalid[0]['displayed'],'profile-only PNG actual complete stale/disabled display')
            same(v['visible_report_blocks'],v['displayed_text'].split('\n')[:4],'profile-only PNG consecutive first four-or-less blocks')
        x,y,w,h=v['report_viewport'];assert w>0 and h>0 and len(v['cursor_rects'])==2*len(v['visible_report_blocks'])
        for a,b,c,d in v['cursor_rects']:assert c>0 and d>0 and x<=a and y<=b and a+c<=x+w and b+d<=y+h
        assert len(v['timing_control_rect'])==4 and v['timing_control_rect'][2]>0 and v['timing_control_rect'][3]>0
        pictures.append({'path':row['path'],'sha256':row['sha256'],'width':width,'height':height})
    close=get(r['close_reload'],'actual_close_RunState_reload');initial=bundle['initial']
    same(close['live_before'],initial,'real close original live run/account/disk')
    same(close['restart_state'],initial['run'],'direct accepted RunState original graph')
    same(close['account_restart_records'],initial['account'],'direct accepted AccountCache original graph')
    same(close['disks_after'],initial['disks'],'close/direct reload all original file bytes')
    same(close['persisted_json'],json.loads(initial['disks']['run.json']),'exact persisted public JSON graph')
    assert len([v for v in bundle['values'].values() if v['kind']=='actual_close_RunState_reload'])==1
    return pictures

def compare_legal(old,new):
    for identity in API_IDS:
        keys=('input','result','texts')
        same({k:new['API'][identity][k] for k in keys},{k:old['API'][identity][k] for k in keys},'old/new legal API joint complete graph '+identity)
        a=old['snapshots']['legal-'+identity];b=new['snapshots']['legal-'+identity]
        keys=('caller','damage_result','texts','displayed_damage')
        same({k:b[k] for k in keys},{k:a[k] for k in keys},'old/new legal GUI joint complete graph '+identity)
    return {'public_API_cases':6,'real_GUI_cases':6,'all_three_complete_texts_equal':True,'full_typed_callers_results_equal':True}

def main():
    parser=argparse.ArgumentParser()
    for name in ('root','guard','original-guard','original-window','candidate-window','out'):parser.add_argument('--'+name,required=True)
    args=parser.parse_args();root=Path(args.root).resolve();out=Path(args.out).resolve();artifact=Path(__file__).resolve().parent
    assert not out.exists() and out!=root and root not in out.parents and artifact!=root and root not in artifact.parents
    assert sha((artifact/'native_evidence.py').read_bytes())==HELPER_SHA
    cases,case_raw=read_json(artifact/'api-cases.json');assert [c['id'] for c in cases]==list(API_IDS)
    pin,pin_raw=read_json(artifact/'source-pins.json');assert pin['window120.py']['sha256']==RUNNER_SHA and pin['api-cases.json']['sha256']==sha(case_raw)
    guard,guard_raw=read_json(args.guard);original_guard,original_raw=read_json(args.original_guard)
    assert guard['section']==original_guard['section']==120
    assert set(guard['source_additional_sha256'])==set(original_guard['source_additional_sha256'])=={'CORE_0.70_VERIFICATION.json'}
    result={'kind':'ROOT_ACTUAL_INDEPENDENT_SAVED_120_TWO_PHASE_MAINWINDOW_AUDIT','passed':False,'workflow_complete':False,
        'auditor_sha256':sha(Path(__file__).read_bytes()),'native_helper_sha256':HELPER_SHA,
        'candidate_guard_sha256':sha(guard_raw),'original_guard_sha256':sha(original_raw),
        'project_API_formatter_reexecution':False,'PNG_pixels_visually_reviewed_by_this_auditor':False,
        'native_Windows_verified':False,'private_state_access':False}
    try:
        same(source_map(root),guard['source_sha256'],'current whole candidate Source')
        for name,want in guard['source_additional_sha256'].items():assert sha((root/name).read_bytes())==want
        old=load_bundle(args.original_window,original_guard,original_raw,'original',cases)
        new=load_bundle(args.candidate_window,guard,guard_raw,'candidate',cases)
        result['original_workflows']=audit_workflows(old,'original');result['candidate_workflows']=audit_workflows(new,'candidate')
        result['legal_identity']=compare_legal(old,new)
        result['original_PNGs']=audit_png_close(old);result['candidate_PNGs']=audit_png_close(new)
        result['native_record_counts']={'original':len(old['values']),'candidate':len(new['values'])}
        receipt_pins=[]
        for bundle in (old,new):
            path=bundle['folder']/'receipt.json';assert path.read_bytes()==bundle['raw']
            receipt_pins.append({'path':str(path),'bytes':len(bundle['raw']),'sha256':sha(bundle['raw'])})
        same(source_map(root),guard['source_sha256'],'current maintained Source after saved audit')
        for name,want in guard['source_additional_sha256'].items():assert sha((root/name).read_bytes())==want
        assert Path(args.guard).read_bytes()==guard_raw and Path(args.original_guard).read_bytes()==original_raw
        assert (artifact/'api-cases.json').read_bytes()==case_raw and (artifact/'source-pins.json').read_bytes()==pin_raw
        result.update(passed=True,workflow_complete=True,actual_receipt_pins=receipt_pins)
    except BaseException as error:result['failure']={'type':type(error).__name__,'message':str(error),'traceback':traceback.format_exc()}
    out.parent.mkdir(parents=True,exist_ok=True)
    with out.open('x',encoding='utf-8') as stream:stream.write(json.dumps(result,ensure_ascii=False,indent=2)+'\n');stream.flush();os.fsync(stream.fileno())
    print(json.dumps({'passed':result['passed'],'out':str(out)}));return 0 if result['passed'] else 1

if __name__=='__main__':raise SystemExit(main())
