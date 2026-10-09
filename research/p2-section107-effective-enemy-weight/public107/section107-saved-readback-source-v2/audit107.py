"""Root-only pure Saved107 audit; no project API/formatter/Qt execution.

Bindings become usable only after actual legacy Gold, compatible Candidate, API replay,
raw exits and Root image inspection exist. Native decoding is Root-only runtime.
"""
import argparse
import ast
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import sys
import time
import traceback

from native_evidence import assert_native_equal, read_record, source_map

HELPER='f040258eddbb7ad624e547e2c422a3d432f7ffeae025b2576b625683ea43fe9a'
GOLD_WINDOW='9762693bc8088837122758f4c3893ac17b47414ced0c484942cb0754e31472e8'
CANDIDATE_WINDOW='9ab0acdc117ab545386261006e341aabc1763ee679dcf3be36eae3eb032e6207'
GOLD_RECEIPT='f543d873cbc9ab3c629e8d0815df3438a82c15fe459e463870f757bef9396634'
GOLD_GUARD='0eea8377cec0b48efa72b9885e5668b6e518e1802c49f8d57de12b962ad0a442'
GOLD_PRIMARY='9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa'
OLD_TEST='62766f1d8cae2b4ef4618ae4f90dddb0c1e9ce8d165f272f1d0fc9caa3b87e8c'
ORIGINAL='0a38276dda0ee3e6640f203cc61397686b6e83c365656578b6896dc461563d00'
ORIGINAL_RUNNER='8fa11731de96d589f8b36ccddd9fd16f0a8c5b4551efa9974628a2d7bd282218'
ORIGINAL_MANIFEST='4765d0b9e0e47244b53c3dcaa32af45307f1ce7c176d798be859a9299500fa81'
API_RUNNER='9f90e0cd544b31f1b4f7e2ece6919f5da5e48b425ca1452a4c95bfd0a2ea8913'
API_MANIFEST='7806e9e567b2ec0687ebdff1e8e9d7fc13f4250c55951863bf3ca84d8fb744c1'
TRANSPORT='6066dce8003d68a58ad71fc4210a9beb9495225b05b392f2d9ae57eeb9624522'
FACTS='c65213bc16625fed8f404e8cd1024d09c0b3e89d3c16443579a0b0f529f2090b'
TEST='2c5eab4be5f484ca3eaf45d19eeb1f1067661a36c42ea41297a5ad1ec22ecc51'
CORE='a75d9497ce34f68de787e3ba99704741f2c873c2c5fa9b5de01e6620b1f00f89'
OP='char_1015_aglna2'
TALENT='飘浮大地之上'
GRAVITY='rogue_6_relic_legacy_56'
PHASES=('plain','gravity-base','gravity-manual100',
        'manual-light-original-oracle','restored-plain','actual-fresh-save-view')
API_ORACLES={
    'fixed4-aglna-gravity-manual0':'manual2-bear-compatible-control',
    'fixed4-aglna-gravity-manual100':'manual2-bear-compatible-control',
    'fixed5-aglna-gravity-manual0':'manual3-round-compatible-control',
    'fixed5-aglna-gravity-manual100':'manual3-round-compatible-control'}
TEMP=b'public107-original-temporary-must-not-be-rewritten\n'


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


def runner_compatibility(gold_source,candidate_source,metadata):
    """Prove only declared metadata changed; never relabel actual old Gold."""
    assert len(gold_source)==39470 and sha(gold_source)==GOLD_WINDOW
    assert len(candidate_source)==43210 and sha(candidate_source)==CANDIDATE_WINDOW
    recovered=candidate_source
    for tag,indent in (('01',''),('02','    '),('03','        '),('04','    ')):
        begin=(indent+'# BEGIN107_META_'+tag+'\n').encode()
        end=(indent+'# END107_META_'+tag+'\n').encode()
        assert recovered.count(begin)==recovered.count(end)==1
        first=recovered.index(begin);last=recovered.index(end,first)+len(end)
        recovered=recovered[:first]+recovered[last:]
    newer=("TEST_SHA='"+TEST+"'\n").encode()
    older=("TEST_SHA='"+OLD_TEST+"'\n").encode()
    assert recovered.count(newer)==1;recovered=recovered.replace(newer,older)
    newer=b"gold['runner_sha256']==GOLD_RUNNER_SHA and gold['original_receipt_sha256']==ORIGINAL_SHA"
    older=b"gold['runner_sha256']==sha(Path(__file__).read_bytes()) and gold['original_receipt_sha256']==ORIGINAL_SHA"
    assert recovered.count(newer)==1;recovered=recovered.replace(newer,older)
    assert recovered==gold_source and sha(recovered)==GOLD_WINDOW
    expected={'kind':'ROOT107_METADATA_ONLY_GOLD_ADMISSION_V1',
              'Gold_runner_sha256':GOLD_WINDOW,'candidate_runner_sha256':CANDIDATE_WINDOW,
              'legacy_Gold_receipt_sha256':GOLD_RECEIPT,
              'legacy_Gold_source_guard_sha256':GOLD_GUARD,
              'legacy_Gold_primary_sha256':GOLD_PRIMARY,
              'functional_source_inverse_sha256':GOLD_WINDOW,'candidate_test_sha256':TEST,
              'legacy_Gold_source_count':749,'candidate_source_count':750,
              'legacy_Gold_contains_107_test':False,'Window_imports_107_test':False,
              'old_and_new_runners_are_identical':False,'legacy_Gold_values_rewritten':False}
    same(metadata,expected,'Actual distinct-runner admission metadata and exact Source inverse')
    return expected


def remaining(value,excluded):
    assert type(value) is dict and set(excluded)<=set(value)
    return {key:item for key,item in value.items() if key not in excluded}


def talent(result):
    selected=[c for c in result['components'] if c['name']==TALENT]
    assert len(selected)==1
    return selected[0]


def damage_block(result):
    selected=[s for s in result['report']['sections'] if s['id']=='damage']
    assert len(selected)==1
    return selected[0]


def cloud_prepend(before_raw,after_raw):
    before=ast.parse(before_raw.decode('utf-8'));after=ast.parse(after_raw.decode('utf-8'))
    def assignment(tree):
        rows=[node for node in tree.body if isinstance(node,ast.Assign)
              and any(isinstance(t,ast.Name) and t.id=='MODULES' for t in node.targets)]
        assert len(rows)==1
        return rows[0]
    left=assignment(before);right=assignment(after)
    a=ast.literal_eval(left.value);b=ast.literal_eval(right.value)
    assert type(a) is type(b) and type(a) in (list,tuple)
    assert b==type(a)(['tests.test_aglna_gravity_weight_107'])+a
    right.value=left.value
    assert ast.dump(after,include_attributes=False)==ast.dump(before,include_attributes=False)


def changed_result(actual,old,manual):
    """Cover complete outputs by explicitly qualified native comparison domains.

    Never import a calculator or manufacture a numerical formula. Read manual
    numbers from the independent old original result with matching DEF/MR.
    """
    same(list(actual),list(old),'Changed result complete top-level field order')
    same(actual['components'],manual['components'],'All corrected components equal actual old manual light')
    same(actual['estimate']['skill'],manual['estimate']['skill'],'Complete corrected skill estimate equals old manual light')
    same(actual['total_damage'],manual['total_damage'],'Corrected complete total equals old manual light')
    same(remaining(actual,{'components','estimate','total_damage','report'}),
         remaining(old,{'components','estimate','total_damage','report'}),
         'All other original complete result fields retained')
    same(list(actual['estimate']),list(old['estimate']),'Complete estimate key order retained')
    same(remaining(actual['estimate'],{'skill'}),remaining(old['estimate'],{'skill'}),
         'Complete base/training/notes/warnings and other estimate graph retained')
    same(list(actual['report']),list(old['report']),'Complete report key order retained')
    same(remaining(actual['report'],{'sections'}),remaining(old['report'],{'sections'}),
         'Complete non-section report metadata retained')
    same([s for s in actual['report']['sections'] if s['id']!='damage'],
         [s for s in old['report']['sections'] if s['id']!='damage'],
         'Every other complete original report section retained')
    same(damage_block(actual),damage_block(manual),'Complete damage metric block equals original manual light')
    assert talent(actual)['per_hit']>talent(old)['per_hit']
    same([c for c in actual['components'] if c['name']!=TALENT],
         [c for c in old['components'] if c['name']!=TALENT],
         'Every non-talent original component retained')


def metric_line(row):
    """Bound S1 damage-row grammar; this is not a project formatter invocation."""
    assert list(row)==['key','label','value','unit']
    assert row['key'] in {'per_cast','active_dps','window_damage','window_seconds','window_dps'}
    value=row['value'];unit=row['unit'];label=row['label']
    assert type(value) in (int,float) and type(unit) is str and type(label) is str
    text=f'{value:.2f}' if unit=='秒' else f'{value:,.2f}'.rstrip('0').rstrip('.')
    line=label+'：'+text+(' '+unit if unit else '')
    for old,new in (('DPS/HPS','每秒伤害 / 每秒治疗'),('DPS','每秒伤害'),('HPS','每秒治疗')):
        line=line.replace(old,new)
    return re.sub(r' (?=每秒伤害|每秒治疗)','',line).strip()


def changed_text(actual,old,old_result,new_result):
    """Only exact full damage-block rows may change in an original S1 text."""
    assert type(actual) is type(old) is str and actual and old
    before=damage_block(old_result);after=damage_block(new_result)
    same(remaining(after,{'metrics'}),remaining(before,{'metrics'}),'Damage text section identity/notes unchanged')
    assert len(before['metrics'])==len(after['metrics'])
    for left,right in zip(before['metrics'],after['metrics']):
        same(remaining(left,{'value'}),remaining(right,{'value'}),'Damage metric labels/keys/units unchanged')
    lines=old.split('\n');assert lines.count('【伤害输出】')==1
    first=lines.index('【伤害输出】')+1;count=len(before['metrics'])
    assert lines[first:first+count]==[metric_line(row) for row in before['metrics']]
    lines[first:first+count]=[metric_line(row) for row in after['metrics']]
    same(actual,'\n'.join(lines),'Entire original text retained except independently qualified damage rows')
    assert actual!=old


def ui_cases(facts):
    fixed=facts['healthy_unique_fixed_weight0_to5']
    def item(name,weight,skill=1,elite=2,potential=1,owner=OP):
        r=fixed[str(weight)] if weight is not None else None
        return {'id':name,'owner':owner,'skill':skill,'elite':elite,'potential':potential,
                'weight':weight,'crossing':owner==OP and elite>0 and weight in (4,5),
                'target':None if r is None else {k:r[k] for k in ('stage_id','enemy_id','level')},
                'reference':None if r is None else r['reference_stats']}
    rows=[item('fixed'+str(w)+'-S'+str(s),w,s) for w in (4,5) for s in (1,2,3)]
    rows += [item('fixed0-signed-boundary',0),item('fixed1-signed-boundary',1),
             item('fixed4-E0-talent-locked',4,elite=0),item('fixed4-E1-talent-selected',4,elite=1),
             item('fixed4-E2-potential3',4,potential=3),item('fixed4-mechanist-nonzero',4,owner='mechanist'),
             item('manual-no-target',None)]
    assert len(rows)==13 and sum(r['crossing'] for r in rows)==8
    return rows


def disk_initial(snapshot):
    disks=snapshot['disks']
    assert list(disks)==['run','account','run_tmp','account_tmp']
    assert disks['run']['exists'] is disks['account']['exists'] is True
    same(disks['run_tmp'],{'exists':True,'bytes':TEMP},'Initial original temporary sentinel')
    same(disks['account_tmp'],{'exists':False,'bytes':None},'Initial account temporary absent')


def main():
    parser=argparse.ArgumentParser()
    for name in ('root','bindings','bindings-sha256','out'):parser.add_argument('--'+name,required=True)
    args=parser.parse_args();root=Path(args.root).resolve();out=Path(args.out).resolve()
    packet=Path(__file__).resolve().parent
    assert not out.exists() and out.parent.is_dir() and out!=root and root not in out.parents
    assert packet!=root and root not in packet.parents
    assert CANDIDATE_WINDOW is not None and TEST is not None
    assert sha((packet/'native_evidence.py').read_bytes())==HELPER
    bpath=Path(args.bindings);assert not bpath.is_symlink()
    braw=bpath.read_bytes();assert sha(braw)==args.bindings_sha256
    bindings=load(braw)
    assert bindings['kind']=='ROOT_ACTUAL107_SAVED_ARTIFACT_BINDINGS_V2'
    assert bindings['actual_runtime_ready'] is True
    started=time.perf_counter();active={'dataset':'bindings','case':None,'record':None}
    report={'kind':'ROOT_ACTUAL_107_PURE_SAVED_READBACK','passed':False,'workflow_complete':False,
            'audit_Source_sha256':sha(Path(__file__).read_bytes()),'bindings_sha256':sha(braw),
            'native_helper_sha256':HELPER,'decoded_records':[],'API_pure_checks':[],
            'API_pair_checks':[],'calculator_caller_checks':[],'UI_pure_checks':[],
            'formatter_group_checks':[],'snapshot_checks':[],'normal_plan_checks':[],
            'Gold_points':[],'restart_checks':[],'PNG_checks':[],
            'project_API_formatter_numeric_Qt_tests_Wine_Git_executed':False,
            'saved_inputs_written':False,'native_windows_verified':False,
            'natural_OCR_producer_verified':False,'second_MainWindow_reopen_verified':False,
            'individual_formatter_prepost_saved_verified':False,
            'cross_separate_freeze_live_alias_verified':False,
            'changed_API_scope':'Complete independent old manual components/skill/total and damage metric block; all other complete old fixed subgraphs retained. Four S1 cases, not UI thirteen-case ledger.',
            'changed_text_scope':'Full original text exact except damage-block rows with independent native manual metric values and fixed Source-bound display grammar.',
            'restart_scope':'Complete actual persisted JSON versus direct RunState reload; no live-memory JSON alias claim.'}
    current=None;additional=None
    try:
        source_pins={'gold_window_runner':GOLD_WINDOW,'candidate_window_runner':CANDIDATE_WINDOW,
                     'original_runner':ORIGINAL_RUNNER,
                     'candidate_API_runner':API_RUNNER,'transport':TRANSPORT,'facts':FACTS,
                     'original_manifest':ORIGINAL_MANIFEST,'candidate_API_manifest':API_MANIFEST}
        assert sha(bound(bindings['audit_Source']))==sha(Path(__file__).read_bytes())
        source_raws={}
        for key,want in source_pins.items():
            source_raws[key]=bound(bindings[key]);assert sha(source_raws[key])==want
        transport=load(bound(bindings['transport']));facts=load(bound(bindings['facts']))
        original_manifest=load(bound(bindings['original_manifest']))
        candidate_manifest=load(bound(bindings['candidate_API_manifest']))
        for field in ('cases','previews','catalog_operator_bindings'):
            same(candidate_manifest[field],original_manifest[field],'Both actual API probe public fixtures identical '+field)
        assert sha(bound(bindings['gold_receipt']))==GOLD_RECEIPT
        assert bindings['gold_guard']['sha256']==GOLD_GUARD
        assert bindings['gold_primary']['sha256']==GOLD_PRIMARY
        gold_guard=load(bound(bindings['gold_guard']));candidate_guard=load(bound(bindings['candidate_guard']))
        old=gold_guard['source_sha256'];current=candidate_guard['source_sha256']
        additional=candidate_guard['source_additional_sha256']
        assert len(old)==749 and len(current)==750
        assert additional==gold_guard['source_additional_sha256']=={'CORE_0.70_VERIFICATION.json':CORE}
        assert set(current)-set(old)=={'tests/test_aglna_gravity_weight_107.py'} and not set(old)-set(current)
        assert current['tests/test_aglna_gravity_weight_107.py']==TEST
        assert {p for p in old if old[p]!=current[p]}=={'rouge/operator_engine.py','scripts/verify_cloud.py'}
        assert len(transport['changes'])==1
        change=transport['changes'][0];assert change['path']=='rouge/operator_engine.py'
        assert old[change['path']]==change['sha256_before']
        assert current[change['path']]==change['sha256_after_source_composition']
        report['source_before']=source_map(root);assert report['source_before']==current
        report['source_additional_before']={p:sha((root/p).read_bytes()) for p in additional}
        assert report['source_additional_before']==additional
        api={}
        for phase in ('original','candidate_API'):
            active.update(dataset=phase,case=None,record=None)
            assert bound(bindings[phase+'_primary'])==b'0\n'
            raw=bound(bindings[phase+'_receipt']);receipt=load(raw)
            if phase=='original':assert sha(raw)==ORIGINAL
            expected=receipt['source_before']
            assert receipt['source_after']==expected and len(expected)==(748 if phase=='original' else 750)
            assert phase=='original' or expected==current
            assert receipt['observation_only'] is True and receipt['product_pass'] is False
            assert receipt['observation_complete'] is True and receipt['source_and_CORE_unchanged'] is True
            assert receipt['CORE_before']==receipt['CORE_after']==CORE
            assert receipt['planned_calculation_cases']==14 and receipt['planned_previews']==2
            assert receipt['actual_explicit_consumer_calls']==74 and receipt['actual_explicit_public_loader_calls']==1
            assert receipt['actual_native_records']==89 and receipt['consumer_error_count']==receipt['blocked_phase_count']==0
            assert receipt['native_helper_sha256']==HELPER
            assert receipt['kind']==('ROOT_ACTUAL_ORIGINAL105_WEIGHT_CONSUMERS_FOR107' if phase=='original' else 'ROOT_ACTUAL_CANDIDATE107_WEIGHT_CONSUMERS')
            api_guard=load(bound(bindings[phase+'_guard']))
            assert api_guard['source_sha256']==expected
            assert api_guard['source_additional_sha256']==additional
            assert receipt['source_guard_sha256']==bindings[phase+'_guard']['sha256']
            assert receipt['runner_sha256']==(ORIGINAL_RUNNER if phase=='original' else API_RUNNER)
            assert receipt['fixture_manifest_sha256']==(ORIGINAL_MANIFEST if phase=='original' else API_MANIFEST)
            for flag in ('native_windows_verified','Qt_executed','ocr_executed','game_chat_sampling_executed','private_state_access'):
                assert receipt[flag] is False
            values={};meta={};indexed={};kinds=Counter()
            directory=Path(bindings[phase+'_receipt']['path']).resolve().parent/'native'
            assert not directory.is_symlink()
            assert {p.name for p in directory.iterdir()}=={r['path'] for r in receipt['native_records']}
            for seq,row in enumerate(receipt['native_records'],1):
                active.update(case=row['case'],record=row['path'])
                assert row['path']=='%06d.pickle.gz'%seq
                value=read_record(directory,row);values[row['path']]=value;meta[row['path']]=row;kinds[row['kind']]+=1
                if row['kind'] in ('original-public-consumer','whole-case-caller-input'):
                    same(value['after'],value['before'],'Complete original/current actual API caller graph conserved')
                    if row['kind']=='original-public-consumer':assert value['error'] is None
                    report['API_pure_checks'].append({'dataset':phase,'case':row['case'],'phase':row['phase'],'record':row['path']})
                else:assert row['kind']=='original-public-profile-inputs'
                report['decoded_records'].append({'dataset':phase,**row,'safe_native_hash_decode_verified':True})
            assert kinds=={'original-public-consumer':74,'whole-case-caller-input':14,'original-public-profile-inputs':1}
            for call in receipt['calls']:
                ref=call['native'];assert ref==meta[ref['path']]
                assert call['returned'] is True and call['error'] is None and call['caller_unchanged'] is True
                key=(call['case'],call['phase']);assert key not in indexed
                indexed[key]=values[ref['path']]
            expected_rows=[r['id'] for r in original_manifest['cases']+original_manifest['previews']]
            assert [r['id'] for r in receipt['rows']]==expected_rows
            api[phase]={'receipt':receipt,'values':values,'meta':meta,'calls':indexed}
        before_api=api['original'];after_api=api['candidate_API']
        assert list(before_api['calls'])==list(after_api['calls']) and len(before_api['calls'])==74
        changed_count=0
        for key,actual in after_api['calls'].items():
            cid,stage=key;active.update(dataset='API-comparison',case=cid)
            previous=before_api['calls'][key]
            changed=cid in API_ORACLES and stage in ('calculate_damage','format_estimate','format_report','format_report_technical')
            changed_formatter=changed and stage!='calculate_damage'
            if not changed_formatter:
                same(actual['before'],previous['before'],'Old/current entire API input including original profiles')
                same(actual['after'],previous['after'],'Old/current entire preserved API argument graph')
            if changed:
                old_calc=before_api['calls'][(cid,'calculate_damage')]['result']
                new_calc=after_api['calls'][(cid,'calculate_damage')]['result']
                manual=before_api['calls'][(API_ORACLES[cid],'calculate_damage')]['result']
                if stage=='calculate_damage':changed_result(actual['result'],old_calc,manual)
                else:
                    same(previous['before'][0][0],old_calc,'Original formatter received its actual old complete result')
                    same(actual['before'][0][0],new_calc,'Changed formatter receives the actual complete new result')
                    assert len(actual['before'][0])==len(previous['before'][0])==1
                    same(actual['before'][1],previous['before'][1],'Changed formatter retains full original keyword graph')
                    changed_text(actual['result'],previous['result'],old_calc,new_calc)
                changed_count+=1
            else:same(actual['result'],previous['result'],'Complete unchanged original/current API output')
            report['API_pair_checks'].append({'case':cid,'phase':stage,'intended_changed_branch':changed,
                                              'complete_old_output_equal':not changed})
        assert changed_count==14
        # Both complete catalog profile input graphs are compared, not a projection.
        for old_meta,new_meta in zip(before_api['receipt']['native_records'],after_api['receipt']['native_records']):
            assert (old_meta['kind'],old_meta['case'],old_meta['phase'])==(new_meta['kind'],new_meta['case'],new_meta['phase'])
            if old_meta['kind']=='original-public-profile-inputs':
                same(after_api['values'][new_meta['path']],before_api['values'][old_meta['path']],
                     'Complete unchanged public profile input graph')
        datasets={};definitions=ui_cases(facts);ids=[r['id'] for r in definitions]
        for phase in ('gold','candidate'):
            active.update(dataset=phase,case=None,record=None)
            assert bound(bindings[phase+'_primary'])==b'0\n'
            receipt=load(bound(bindings[phase+'_receipt']))
            assert receipt['kind']=='ROOT_ACTUAL_107_REAL_MAINWINDOW' and receipt['phase']==phase
            assert receipt['passed'] is receipt['workflow_complete'] is True
            assert receipt['runner_sha256']==(GOLD_WINDOW if phase=='gold' else CANDIDATE_WINDOW)
            assert receipt['original_receipt_sha256']==ORIGINAL
            assert receipt['original_raw_exit_sha256']==bindings['original_primary']['sha256']
            assert receipt['source_before']==receipt['source_after']==(old if phase=='gold' else current)
            assert receipt['source_guard_sha256']==bindings[phase+'_guard']['sha256']
            assert receipt['source_additional_before']==receipt['source_additional_after']==additional
            assert receipt['source_drift']==[] and receipt['Qt_errors']==[]
            assert receipt['deadline_seconds']==450 and 0<receipt['elapsed_seconds']<450
            assert receipt['qt']=='6.9.3'
            for flag in ('native_windows_verified','private_state_access','game_chat_sampling_executed','natural_OCR_producer_verified'):
                assert receipt[flag] is False
            assert [r['id'] for r in receipt['rows']]==ids
            if phase=='gold':assert 'Gold_runner_compatibility' not in receipt
            else:
                assert receipt['actual_gold_receipt_sha256']==GOLD_RECEIPT
                report['Gold_runner_compatibility']=runner_compatibility(
                    source_raws['gold_window_runner'],source_raws['candidate_window_runner'],
                    receipt['Gold_runner_compatibility'])
            directory=Path(bindings[phase+'_receipt']['path']).resolve().parent
            assert directory!=root and root not in directory.parents
            record_dir=directory/'records';assert not record_dir.is_symlink()
            assert {p.name for p in record_dir.iterdir()}=={r['path'] for r in receipt['records']}
            values={};meta={};latest={};predecessor={};formatters={};plans={};kinds=Counter()
            for seq,row in enumerate(receipt['records'],1):
                active.update(case=row['case'],record=row['path'])
                assert row['path']=='%06d.pickle.gz'%seq and row['case'] in ids
                value=read_record(record_dir,row)
                for label in ('kind','case','phase'):assert value[label]==row[label]
                values[row['path']]=value;meta[row['path']]=row;kinds[row['kind']]+=1
                if row['kind']=='actual_calculate_result':
                    same(value['after'],value['before'],'Actual UI full numeric caller conserved')
                    assert list(value['before'])==['args','kwargs'] and len(value['before']['args'])==1 and not value['before']['kwargs']
                    latest[row['case']]=row['path']
                    report['calculator_caller_checks'].append({'dataset':phase,'case':row['case'],'record':row['path']})
                elif row['kind']=='pure_actual_UI_step':
                    same(value['after'],value['before'],'Every saved real UI group joint durable state and disk conserved')
                    assert list(value['before'])==['durable','disks']
                    report['UI_pure_checks'].append({'dataset':phase,'case':row['case'],'record':row['path'],'label':value['label']})
                elif row['kind']=='pure_actual_three_formatter_group':
                    same(value['after'],value['before'],'Every saved common three-formatter result/state/disk joint graph conserved')
                    assert list(value['before'])==['result','durable','disks']
                    key=(row['case'],row['phase']);assert key not in formatters;formatters[key]=row['path']
                    report['formatter_group_checks'].append({'dataset':phase,'case':row['case'],'phase':row['phase'],'record':row['path']})
                elif row['kind']=='actual_normal_plan_result':
                    assert list(value['before'])==list(value['after'])==['scenario','attributes','args','kwargs']
                    assert value['before']['kwargs'].get('normal') is True
                    key=(row['case'],row['phase']);assert key not in plans;plans[key]=row['path']
                    report['normal_plan_checks'].append({'dataset':phase,'case':row['case'],'phase':row['phase'],'record':row['path'],
                                                       'mutable_Combat_scenario_purity_claimed':False})
                elif row['kind']=='actual_window_snapshot':
                    assert row['case'] in latest;predecessor[row['path']]=latest[row['case']]
                elif row['kind']=='actual_public_fixed_fixture_qualification':
                    assert value['consumer_source']=='rouge/data/previews.json'
                    same(value['actual_entry']['reference_stats'],value['declared_reference'],'Actual fixed source qualification complete reference')
                else:assert row['kind']=='actual_close_RunState_reload'
                report['decoded_records'].append({'dataset':phase,**row,'safe_native_hash_decode_verified':True})
            assert kinds['actual_window_snapshot']==kinds['pure_actual_three_formatter_group']==78
            assert kinds['actual_close_RunState_reload']==13 and kinds['actual_public_fixed_fixture_qualification']==12
            assert kinds['actual_normal_plan_result']==12 and kinds['actual_calculate_result']==receipt['actual_numeric_calls']
            assert receipt['actual_captured_normal_plans']==12 and sum(kinds.values())==len(receipt['records'])
            datasets[phase]={'receipt':receipt,'directory':directory,'values':values,'meta':meta,
                             'predecessor':predecessor,'formatters':formatters,'plans':plans,'kinds':dict(kinds)}
        for name in ('verify_cloud.py','verify_full_available.py'):
            path='scripts/'+name
            left=datasets['gold']['directory']/'public-Source'/name
            right=datasets['candidate']['directory']/'public-Source'/name
            assert not left.is_symlink() and not right.is_symlink()
            a=left.read_bytes();b=right.read_bytes()
            assert sha(a)==old[path] and sha(b)==current[path] and b==(root/path).read_bytes()
            if name=='verify_cloud.py':cloud_prepend(a,b)
            else:assert a==b
        for phase,data in datasets.items():
            for item,row in zip(definitions,data['receipt']['rows']):
                cid=item['id'];active.update(dataset=phase,case=cid)
                assert row['crossing'] is item['crossing']
                same(row['target'],item['target'],'Declared case target metadata')
                assert list(row['snapshots'])==list(PHASES)
                initial=None;snapshots={}
                for name in PHASES:
                    ref=row['snapshots'][name];assert ref==data['meta'][ref['path']]
                    value=data['values'][ref['path']];view=value['view'];result=view['damage_result']['result']
                    assert (value['kind'],value['case'],value['phase'])==('actual_window_snapshot',cid,name)
                    calc=data['values'][data['predecessor'][ref['path']]]
                    assert calc['phase']==name and calc['case']==cid
                    caller=calc['before']['args'][0]
                    same(caller,view['damage_result']['scenario'],'Every complete actual UI argument equals saved scenario')
                    same(result,calc['result'],'Every complete actual callee result equals saved window result')
                    assert caller['operator']==item['owner'] and caller['skill']==item['skill']
                    assert caller['elite']==item['elite'] and caller['potential']==item['potential']
                    assert caller['level']==(50,80,90)[item['elite']] and caller['skill_rank']==(1,7,10)[item['elite']]
                    same(caller['run_config'],value['durable']['run']['config'],'Actual full raw run config reaches numeric argument')
                    assert caller['run_config']['zone']['name']=='玻利瓦尔肤层'
                    f=data['values'][data['formatters'][(cid,name)]]
                    same(f['before']['result'],result,'Saved complete formatter input equals complete actual numeric result')
                    same(f['before']['durable'],value['durable'],'Saved formatter group durable graph equals snapshot')
                    same(f['before']['disks'],value['disks'],'Saved formatter group exact disk graph equals snapshot')
                    texts=view['three_texts'];same(texts,f['texts'],'Snapshot retains three full actual formatter texts')
                    assert list(texts)==['estimate','default','technical']
                    assert all(type(t) is str and t for t in texts.values()) and texts['estimate']==texts['default']
                    assert view['displayed_damage']==texts['default'].replace(chr(160),' ')
                    if name=='plain':initial=value;disk_initial(value)
                    if name!='actual-fresh-save-view':same(value['disks'],initial['disks'],'Every pure phase retains original JSON and sentinel bytes')
                    if item['owner']==OP and item['skill']==3:
                        p=data['values'][data['plans'][(cid,name)]]
                        assert len(view['normal_refs'])==len(view['normal_plans'])==1
                        assert view['normal_refs'][0]==data['meta'][data['plans'][(cid,name)]]
                        same(view['normal_plans'][0],p['result'],'Full saved plan equals actual normal-method return')
                        same(result['timing']['recharge_streams'],p['result']['timing']['streams'],'Complete real normal recharge stream graph')
                        assert result['estimate']['skill']['cycle_seconds'] is not None and p['result']['damage']>0
                    else:
                        assert view['normal_refs']==view['normal_plans']==[] and (cid,name) not in data['plans']
                        if item['owner']==OP and item['skill']==2:
                            for field in ('duration_seconds','recharge_seconds','cycle_seconds'):assert result['estimate']['skill'][field] is None
                    if name in ('gravity-base','gravity-manual100'):
                        effects=result['relic_resolution']['enemy_effects']
                        if item['target']:
                            assert result['run_resolution']['enemy']['reference_stats']['massLevel']==item['weight']
                            assert result['run_resolution']['enemy']['stats']['massLevel']==item['weight']-2
                            assert effects['weight_delta']==-2.0
                        else:
                            assert effects['weight_delta']==0
                            assert not result['relic_resolution']['records'][0]['applied']
                            assert 'target_enemy' in result['relic_resolution']['records'][0]['missing_conditions']
                    snapshots[name]=value
                    report['snapshot_checks'].append({'dataset':phase,'case':cid,'phase':name,'record':ref['path'],
                                                     'complete_actual_caller_result_three_texts_saved_groups_verified':True})
                same(snapshots['gravity-manual100']['view']['damage_result']['result'],
                     snapshots['gravity-base']['view']['damage_result']['result'],'Fixed identity/manual-heavy precedence entire numeric result')
                same(snapshots['restored-plain']['view']['damage_result']['result'],
                     snapshots['plain']['view']['damage_result']['result'],'Actual original entire numeric result recovery')
                fresh=snapshots['actual-fresh-save-view'];ref=row['restart'];assert ref==data['meta'][ref['path']]
                restart=data['values'][ref['path']]
                assert restart['kind']=='actual_close_RunState_reload' and restart['case']==cid
                same(restart['observation_before'],restart['observation_after'],'Actual fresh observation complete caller preserved')
                same(restart['observation_after'],({'operators':[{'id':item['owner'],'fields':{'selected_skill':item['skill']}}],
                                                   'selected_operator':item['owner']},1001.0),'Genuine selected-skill observation shape')
                same(restart['live_before']['durable'],fresh['durable'],'Actual close retained full current durable phase')
                same(restart['live_before']['disks'],fresh['disks'],'Actual close retained current JSON and tmp phase')
                same(restart['disks_after'],fresh['disks'],'Accepted direct reload did not rewrite any disk')
                persisted=load(fresh['disks']['run']['bytes'])
                same(restart['persisted_json'],persisted,'Reload oracle exactly actual saved JSON')
                same(restart['restart_state'],persisted,'Complete restarted JSON graph without live alias guarantee')
                same(fresh['durable']['account'],initial['durable']['account'],'Authorized run save keeps account graph')
                same(fresh['disks']['account'],initial['disks']['account'],'Authorized run save keeps original account bytes')
                assert persisted['last_read']==1001.0 and persisted['operators'][item['owner']]['fields']['selected_skill']==item['skill']
                same(fresh['disks']['run_tmp'],{'exists':False,'bytes':None},'Actual atomic run save consumed old sentinel')
                report['restart_checks'].append({'dataset':phase,'case':cid,'record':ref['path'],'actual_JSON_graph_verified':True})
        old_rows={r['id']:r for r in datasets['gold']['receipt']['rows']}
        for item,new_row in zip(definitions,datasets['candidate']['receipt']['rows']):
            old_row=old_rows[item['id']]
            for name in PHASES:
                old_value=datasets['gold']['values'][old_row['snapshots'][name]['path']]
                actual=datasets['candidate']['values'][new_row['snapshots'][name]['path']]
                def comparison(value):
                    return {'view':remaining(value['view'],{'normal_refs'}),'durable':value['durable'],'disks':value['disks']}
                changed=item['crossing'] and name in ('gravity-base','gravity-manual100')
                if not changed:same(comparison(actual),comparison(old_value),'Full same-input actual UI Gold native graph and three texts')
                else:
                    manual=datasets['gold']['values'][old_row['snapshots']['manual-light-original-oracle']['path']]
                    result=actual['view']['damage_result']['result'];old_result=old_value['view']['damage_result']['result']
                    oracle=manual['view']['damage_result']['result']
                    same(result['components'],oracle['components'],'Full corrected UI components equal original manual-light Gold')
                    same(result['estimate']['skill'],oracle['estimate']['skill'],'Complete corrected UI estimate skill equal original manual-light Gold')
                    same(actual['view']['normal_plans'],manual['view']['normal_plans'],'Entire actual S3 normal output equals original UI manual Gold')
                    for field in ('run_resolution','relic_resolution','applied_effects','inapplicable_relics','complete','scope'):
                        same(result[field],old_result[field],'Complete unchanged fixed metadata '+field)
                    same([c for c in result['components'] if c['name']!=TALENT],
                         [c for c in old_result['components'] if c['name']!=TALENT],'Every old non-talent UI component retained')
                    same(actual['durable'],old_value['durable'],'Changed UI point retains entire durable graph')
                    same(actual['disks'],old_value['disks'],'Changed UI point retains entire original disk graph')
                    assert talent(result)['per_hit']>talent(old_result)['per_hit']
                report['Gold_points'].append({'case':item['id'],'phase':name,'complete_same_input_Gold_equal':not changed,
                                              'independent_original_manual_branch_equal':changed})
        assert sum(r['complete_same_input_Gold_equal'] for r in report['Gold_points'])==62
        assert sum(r['independent_original_manual_branch_equal'] for r in report['Gold_points'])==16
        visual=load(bound(bindings['visual']))
        assert visual['passed'] is visual['workflow_complete'] is True
        assert visual['native_windows_game_chat_verified'] is False
        pngs=datasets['candidate']['receipt']['pngs'];assert datasets['gold']['receipt']['pngs']==[]
        assert len(pngs)==len(visual['pngs'])==4
        png_order=[('01-healthy-fixed4-plain.png','fixed4-S1','plain',False),
                   ('02-fixed4-gravity-light.png','fixed4-S1','gravity-base',False),
                   ('03-signed-negative-reference.png','fixed0-signed-boundary','gravity-base',True),
                   ('04-legal-manual-light-control.png','manual-no-target','manual-light-original-oracle',False)]
        for png,seen,expected in zip(pngs,visual['pngs'],png_order):
            assert (png['file'],png['case'],png['phase'],png['technical'])==expected and png['tab_index']==1
            same({k:seen[k] for k in png},png,'Actual image row matches Root visual ledger')
            assert seen['actually_viewed'] is True and type(seen['visual_observation']) is str and seen['visual_observation']
            path=datasets['candidate']['directory']/png['file'];assert Path(png['file']).name==png['file'] and not path.is_symlink()
            raw=path.read_bytes();assert len(raw)==png['bytes'] and sha(raw)==png['sha256'] and raw.startswith(b'\x89PNG\r\n\x1a\n')
            report['PNG_checks'].append({**png,'actual_Root_visual_ledger_bound':True})
        report.update(passed=True,workflow_complete=True,
                      decoded_record_count=len(report['decoded_records']),
                      API_original_and_current_records_checked=178,
                      API_output_pairs_checked=74,API_intended_changed_consumer_pairs=changed_count,
                      API_complete_unchanged_consumer_pairs=74-changed_count,
                      saved_UI_snapshot_count=len(report['snapshot_checks']),
                      saved_UI_group_count=len(report['UI_pure_checks']),
                      saved_common_formatter_group_count=len(report['formatter_group_checks']),
                      saved_actual_normal_plan_count=len(report['normal_plan_checks']),
                      complete_same_input_UI_Gold_points=62,intended_changed_UI_points=16,
                      actual_close_direct_RunState_count=len(report['restart_checks']),
                      phase_record_counts={p:len(d['receipt']['records']) for p,d in datasets.items()},
                      phase_record_kinds={p:d['kinds'] for p,d in datasets.items()},
                      window_per_UI_step_prepost_saved_verified=True,
                      common_three_formatter_group_prepost_saved_verified=True)
    except BaseException as error:
        report['failure']={'active':dict(active),'type':type(error).__name__,'message':str(error),
                           'traceback':''.join(traceback.format_exception(type(error),error,error.__traceback__))}
    finally:
        report['bindings']=bindings
        if current is not None:
            report['source_after']=source_map(root)
            report['source_drift']=[p for p in set(current)|set(report['source_after']) if current.get(p)!=report['source_after'].get(p)]
            report['source_additional_after']={p:sha((root/p).read_bytes()) for p in additional}
            if report['source_drift'] or report['source_additional_after']!=additional:report.update(passed=False,workflow_complete=False)
        report['elapsed_seconds']=time.perf_counter()-started
        with out.open('x',encoding='utf-8') as stream:stream.write(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'passed':report['passed'],'decoded_records':len(report['decoded_records']),
                      'API_pairs':len(report['API_pair_checks']),'UI_snapshots':len(report['snapshot_checks'])}))
    return 0 if report['passed'] else 1


if __name__=='__main__':sys.exit(main())
