"""Source-only preparation; Root solely reads saved native 110 window evidence."""
import argparse
import hashlib
import json
from pathlib import Path
import time
import traceback

from native_evidence import assert_native_equal, read_record, source_map

HELPER_SHA='f040258eddbb7ad624e547e2c422a3d432f7ffeae025b2576b625683ea43fe9a'
WINDOW_SHA='8b27e5e5579b9bee9c48e091ae347bd1a1c9b502ce18bbacd96d4596bf6e3b12'
OP='char_4182_oblvns'
CLOCK_KEYS=('initial_seconds','recharge_seconds','cycle_seconds','duration_seconds','sp_recovery_per_second','mode')

def sha(raw):return hashlib.sha256(raw).hexdigest()

def file_pin(path):
    assert path.is_file() and not path.is_symlink()
    raw=path.read_bytes();return {'path':str(path),'bytes':len(raw),'sha256':sha(raw)}

def sp_fields(result):
    skill=result['estimate']['skill']
    return {'skill':{key:skill[key] for key in CLOCK_KEYS},
        'estimate_fields':{key:value for key,value in result['estimate'].items() if key=='sp_events'},
        'timing_report':next(section for section in result['report']['sections'] if section['id']=='timing')}

def main():
    parser=argparse.ArgumentParser()
    for key in ('root','guard','window-dir','window-exit','runner','out'):parser.add_argument('--'+key,required=True)
    args=parser.parse_args();root=Path(args.root).resolve();guard_path=Path(args.guard).resolve()
    window_dir=Path(args.window_dir).resolve();exit_path=Path(args.window_exit).resolve()
    runner=Path(args.runner).resolve();out=Path(args.out).resolve();artifact=Path(__file__).resolve().parent
    assert not out.exists() and root not in out.parents and root!=out and out!=window_dir
    assert root not in artifact.parents and root!=artifact
    assert file_pin(artifact/'native_evidence.py')['sha256']==HELPER_SHA
    assert file_pin(runner)['sha256']==WINDOW_SHA and exit_path.read_bytes()==b'0\n'
    guard_raw=guard_path.read_bytes();guard=json.loads(guard_raw)
    expected=guard['source_sha256'];extra=guard['source_additional_sha256']
    assert guard['section']==110 and len(expected)==753 and source_map(root)==expected
    assert set(extra)=={'CORE_0.70_VERIFICATION.json'}
    assert {name:sha((root/name).read_bytes()) for name in extra}==extra
    input_path=window_dir/'receipt.json';raw=input_path.read_bytes();window=json.loads(raw)
    assert window['kind']=='ROOT_ACTUAL_110_REAL_MAINWINDOW' and window['phase']=='candidate'
    assert window['passed'] is True and window['workflow_complete'] is True and window['Qt_errors']==[]
    assert window['runner_sha256']==WINDOW_SHA and window['native_helper_sha256']==HELPER_SHA
    assert window['source_guard_sha256']==sha(guard_raw) and window['source_count']==753
    assert window['source_before']==window['source_after']==expected and not window['source_drift']
    assert window['source_additional_before']==window['source_additional_after']==extra
    assert window['actual_windows']==1 and len(window['rows'])==12 and len(window['pairs'])==6 and len(window['pngs'])==2
    assert window['deadline_seconds']==450 and 0<=window['elapsed_seconds']<450
    out.mkdir();started=time.perf_counter()
    receipt={'kind':'ROOT_ACTUAL_110_REAL_WINDOW_SAVED_READBACK','passed':False,'workflow_checks_passed':False,
        'audit_source_sha256':sha(Path(__file__).read_bytes()),'native_helper_sha256':HELPER_SHA,
        'source_before':expected,'source_additional_before':extra,'source_guard_sha256':sha(guard_raw),
        'window_receipt':file_pin(input_path),'window_runner':file_pin(runner),'window_exit':file_pin(exit_path),
        'scope':'Saved one real window, twelve states and six current baseline/empty pairs; prior original public API evidence is separate.',
        'no_project_API_formatter_Qt_Wine_execution':True,'private_state_access':False,
        'native_Windows_verified':False,'actual_PNG_visual_view_by_this_auditor':False,
        'formatter_scope':'Complete saved three-text groups and their joint purity; no formatter rerun or isolated-purity claim.',
        'restart_scope':'Saved original close and direct RunState reload; no second MainWindow or live JSON alias preservation claim.'}
    try:
        metadata=window['records'];names=[ref['path'] for ref in metadata]
        assert len(names)==len(set(names)) and names==[f'{i:06d}.pickle.gz' for i in range(1,len(names)+1)]
        record_dir=window_dir/'records';assert not record_dir.is_symlink()
        assert {p.name for p in record_dir.iterdir()}==set(names)
        ledger={ref['path']:ref for ref in metadata};decoded={};indices={name:i for i,name in enumerate(names)}
        for ref in metadata:
            value=read_record(record_dir,ref)
            for field in ('kind','case','phase'):assert_native_equal(value[field],ref[field],'saved metadata binding '+field)
            decoded[ref['path']]=value
        def record(ref):
            assert_native_equal(ref,ledger[ref['path']],'complete JSON metadata reference')
            return decoded[ref['path']]
        numeric_count=0;ui_count=0;formatter_count=0;snapshot_count=0;png_record_count=0;reload_count=0;initial=None
        for name in names:
            value=decoded[name];kind=value['kind']
            if kind=='actual_calculate_result':
                numeric_count+=1;assert_native_equal(value['after'],value['before'],'full numeric caller purity')
            elif kind=='actual_UI_step':
                ui_count+=1;assert_native_equal(value['after'],value['before'],'full live account/state/disk UI purity')
                if initial is None:initial=value['before']
                assert_native_equal(value['before'],initial,'all UI steps preserve initial public state/disks')
            elif kind=='actual_three_formatter_group':
                formatter_count+=1;assert_native_equal(value['after'],value['before'],'complete formatter group purity')
                assert set(value['texts'])=={'estimate','default','technical'} and all(type(v) is str for v in value['texts'].values())
                assert value['texts']['estimate']==value['texts']['default']
                assert_native_equal(value['before']['joint'],initial,'formatter state/account/disk')
            elif kind=='actual_window_snapshot':snapshot_count+=1
            elif kind=='actual_PNG_visible_damage_rows':png_record_count+=1
            elif kind=='actual_close_RunState_reload':reload_count+=1
            else:raise AssertionError('Unexpected saved record kind: '+kind)
        assert initial is not None and numeric_count==window['actual_numeric_calls']
        assert formatter_count==snapshot_count==12 and png_record_count==2 and reload_count==1
        wanted=[f's{skill}-{mode}-{phase}' for skill in (1,2,3) for mode in ('frames','continuous') for phase in ('baseline','empty')]
        assert [row['id'] for row in window['rows']]==wanted
        snapshots={};snapshot_refs={}
        for row in window['rows']:
            saved=record(row['snapshot']);numeric=record(row['numeric']);snapshot=saved['value']
            assert saved['kind']=='actual_window_snapshot' and saved['case']==row['id'] and saved['phase']=='explicit_snapshot'
            assert numeric['kind']=='actual_calculate_result' and numeric['case']==row['id'] and numeric['phase']=='explicit_snapshot'
            index=indices[row['snapshot']['path']];assert index>=3 and names[index-3]==row['numeric']['path']
            step=decoded[names[index-2]];group=decoded[names[index-1]]
            assert step['kind']=='actual_UI_step' and step['label']=='MainWindow.calculate' and step['case']==row['id']
            assert group['kind']=='actual_three_formatter_group' and group['case']==row['id']
            caller=snapshot['caller'];result=snapshot['damage_result']['result']
            assert len(numeric['before']['args'])==1 and numeric['before']['kwargs']=={}
            assert_native_equal(caller,numeric['before']['args'][0],'full original calculator caller')
            assert_native_equal(snapshot['damage_result']['scenario'],caller,'full actual UI caller')
            assert_native_equal(result,numeric['result'],'full original numeric return and UI result')
            assert_native_equal(group['before']['result'],result,'full formatter input result')
            assert_native_equal(snapshot['texts'],group['texts'],'three complete saved formatter strings')
            assert snapshot['displayed_damage']==snapshot['texts']['default'].replace(chr(160),' ')
            assert_native_equal(snapshot['state_and_disks'],initial,'whole snapshot state/account/disks')
            assert_native_equal(saved['sp'],sp_fields(result),'all saved SP fields/report derive from complete result')
            assert caller['operator']==OP and caller['skill']==row['skill'] and caller['timing_mode']==row['mode']
            assert caller['elite']==2 and caller['level']==90 and caller['skill_rank']==10
            assert caller['module_id'] is None and caller['module_level']==0 and caller['relic_ids']==[]
            assert caller['window_seconds']==10 and caller['continuous_attacks'] is True
            assert ('timing' in caller)==row['empty']
            if row['empty']:assert_native_equal(caller['timing'],{'target_windows':[]},'exact declared empty supply')
            if row['skill']==2:assert caller['organ_mode'] is False and caller['fever'] is False
            snapshots[row['id']]=snapshot;snapshot_refs[row['id']]=row['snapshot']
        assert [(pair['skill'],pair['mode']) for pair in window['pairs']]==[(s,m) for s in (1,2,3) for m in ('frames','continuous')]
        for pair in window['pairs']:
            skill=pair['skill'];prefix=f"s{skill}-{pair['mode']}-";before=snapshots[prefix+'baseline'];after=snapshots[prefix+'empty']
            assert_native_equal(pair['baseline_snapshot'],snapshot_refs[prefix+'baseline'],'pair baseline binding')
            assert_native_equal(pair['empty_snapshot'],snapshot_refs[prefix+'empty'],'pair empty binding')
            assert pair['native_SP_fields_preserved'] is True and pair['independent_S1_unknown_preserved']==(skill==1)
            old=before['damage_result']['result'];new=after['damage_result']['result']
            assert_native_equal(sp_fields(new),sp_fields(old),'all six complete native SPclock/report pairs')
            stripped={key:value for key,value in after['caller'].items() if key!='timing'}
            assert_native_equal(stripped,before['caller'],'same pair caller except explicit empty timing')
            if skill==1:
                for result in (old,new):
                    assert result['total_damage'] is None and result['complete'] is False
                    assert result['unbound_cast_reference']['actual_hit_times_seconds'] is None
                    assert result['unbound_cast_reference']['actual_end_seconds'] is None
                assert_native_equal({'components':new['components'],'reference':new['unbound_cast_reference']},
                    {'components':old['components'],'reference':old['unbound_cast_reference']},'whole independent S1 notes and unknown reference')
            else:
                assert old['total_damage']>0 and new['total_damage']==0
                assert len(new['components'])==len(old['components'])
                assert all(c['hits']==0 and c['total']==0 and c['times_seconds']==[] for c in new['components'])
                for old_c,new_c in zip(old['components'],new['components'],strict=True):assert_native_equal(new_c['per_hit'],old_c['per_hit'],'cultivated per-hit reference')
                if skill==3:
                    for key in ('total_damage','phase_damage','cycle_damage'):assert new['estimate']['skill'][key]==0
        closed=record(window['close_reload']);assert closed['kind']=='actual_close_RunState_reload'
        assert_native_equal(closed['live_before'],initial,'close original full state/account/disks')
        assert_native_equal(closed['restart_state'],initial['run'],'direct original accepted graph reload')
        assert_native_equal(closed['disks_after'],initial['disks'],'close/direct reload disk purity')
        assert_native_equal(closed['persisted_json'],json.loads(initial['disks']['run.json']),'saved original JSON graph')
        assert [png['path'] for png in window['pngs']]==['s3-frames-baseline.png','s3-frames-empty.png']
        for png in window['pngs']:
            name=png['path'];assert Path(name).name==name
            pin=file_pin(window_dir/name);assert pin['bytes']==png['bytes'] and pin['sha256']==png['sha256']
            assert (window_dir/name).read_bytes().startswith(b'\x89PNG\r\n\x1a\n')
            visual=record(png['visual']);assert visual['kind']=='actual_PNG_visible_damage_rows' and visual['case']==name[:-4]
            assert visual['anchor']=='【伤害输出】' and visual['displayed_text']==snapshots[name[:-4]]['displayed_damage']
            assert len(visual['visible_blocks'])==len(visual['cursor_rects'])==4 and visual['visible_blocks'][0]=='【伤害输出】'
            vx,vy,vw,vh=visual['viewport_rect'];assert vw>0 and vh>0
            for x,y,w,h in visual['cursor_rects']:
                assert w>0 and h>0 and vx<=x and vy<=y and x+w<=vx+vw and y+h<=vy+vh
        receipt.update(passed=True,workflow_checks_passed=True,actual_native_records_decoded=len(names),
            actual_numeric_returns=numeric_count,actual_UI_steps=ui_count,actual_snapshots=12,
            actual_complete_formatter_groups=12,actual_complete_formatter_strings=36,
            actual_full_SPclock_report_pairs=6,actual_close_direct_reload=1,actual_PNG_hash_viewport_gates=2,
            actual_decoded_record_metadata=metadata)
    except BaseException as error:
        receipt['failure']={'type':type(error).__name__,'message':str(error),'traceback':traceback.format_exc()}
    receipt['source_after']=source_map(root)
    receipt['source_additional_after']={name:sha((root/name).read_bytes()) for name in extra}
    if receipt['source_after']!=expected or receipt['source_additional_after']!=extra or guard_path.read_bytes()!=guard_raw:
        receipt.update(passed=False,workflow_checks_passed=False)
    receipt['elapsed_seconds']=time.perf_counter()-started
    with (out/'receipt.json').open('x',encoding='utf-8') as stream:stream.write(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'passed':receipt['passed'],'decoded':receipt.get('actual_native_records_decoded',0)}))
    return 0 if receipt['passed'] else 1

if __name__=='__main__':raise SystemExit(main())
