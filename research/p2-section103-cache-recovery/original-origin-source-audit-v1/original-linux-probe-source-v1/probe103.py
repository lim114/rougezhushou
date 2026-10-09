"""Root-only original743 RunState observations, never executed by Source author.

This is an observation probe, not product verification. Exceptions are recorded
with real traces; success does not claim all cases safe. Only public fixtures
under a fresh output directory are loaded. No UI, screenshots, game or chat.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys
import threading
import time
import traceback

NATIVE_SHA = 'f040258eddbb7ad624e547e2c422a3d432f7ffeae025b2576b625683ea43fe9a'
RUNSTATE_SHA = '1b6f66e7f864238880c5214f431da042e94c7fd7def8103352439609bbfd35d9'
CORE_SHA = 'a75d9497ce34f68de787e3ba99704741f2c873c2c5fa9b5de01e6620b1f00f89'
AUDIT_SHA = '47184b3663a65ee63dc78b62bcfa951bb13905b7c33dc20f11a8a23e40ba84e3'
CASES = [{'id': 'cached-source-null-fresh-known', 'captured_at': 1002, 'saved_file': 'cached-source-null-fresh-known.saved.json', 'saved_sha256': 'c41f9ea8c5c580e4b299b725213fc014aae065f3c7398bfce6575547023fe277', 'observed_file': 'cached-source-null-fresh-known.observed.json', 'observed_sha256': '11ddafc2f0c2affab095f8df86f10f45696a1f48c05ac328438f717b385e0cdb'}, {'id': 'cached-source-list-fresh-known', 'captured_at': 1002, 'saved_file': 'cached-source-list-fresh-known.saved.json', 'saved_sha256': '8bacdeeef7cbc9a4a570f1844842b4a4c15ca8bd0e37daba21bb4956762c9bf6', 'observed_file': 'cached-source-list-fresh-known.observed.json', 'observed_sha256': '11ddafc2f0c2affab095f8df86f10f45696a1f48c05ac328438f717b385e0cdb'}, {'id': 'cached-source-text-fresh-known', 'captured_at': 1002, 'saved_file': 'cached-source-text-fresh-known.saved.json', 'saved_sha256': '6e00e46f16f9e9a624294db4ade4cfe0885d55281f47eaadfa918c2615a15ca8', 'observed_file': 'cached-source-text-fresh-known.observed.json', 'observed_sha256': '11ddafc2f0c2affab095f8df86f10f45696a1f48c05ac328438f717b385e0cdb'}, {'id': 'cached-source-number-fresh-known', 'captured_at': 1002, 'saved_file': 'cached-source-number-fresh-known.saved.json', 'saved_sha256': 'a190d55eb02da72db8d725bf15e7f1a31c02c79c4a56e4f91350ece004181216', 'observed_file': 'cached-source-number-fresh-known.observed.json', 'observed_sha256': '11ddafc2f0c2affab095f8df86f10f45696a1f48c05ac328438f717b385e0cdb'}, {'id': 'healthy-source-missing-fresh-discovery', 'captured_at': 1002, 'saved_file': 'healthy-source-missing-fresh-discovery.saved.json', 'saved_sha256': 'a6ec71472fe84a7217d6e7c252a4b032a1647179ff2eff1185686ce13e7b2920', 'observed_file': 'healthy-source-missing-fresh-discovery.observed.json', 'observed_sha256': '11ddafc2f0c2affab095f8df86f10f45696a1f48c05ac328438f717b385e0cdb'}, {'id': 'healthy-source-empty-fresh-discovery', 'captured_at': 1002, 'saved_file': 'healthy-source-empty-fresh-discovery.saved.json', 'saved_sha256': '22868b679a9e35642f6eef297e6a3ef9bf132a06e9cf945782ebae2d334c544f', 'observed_file': 'healthy-source-empty-fresh-discovery.observed.json', 'observed_sha256': '11ddafc2f0c2affab095f8df86f10f45696a1f48c05ac328438f717b385e0cdb'}, {'id': 'healthy-source-valid-fresh-discovery', 'captured_at': 1002, 'saved_file': 'healthy-source-valid-fresh-discovery.saved.json', 'saved_sha256': '11271c1a9d254284b7fd86658efd3dba28d6e30f65cc15e4cab3c62055640836', 'observed_file': 'healthy-source-valid-fresh-discovery.observed.json', 'observed_sha256': '11ddafc2f0c2affab095f8df86f10f45696a1f48c05ac328438f717b385e0cdb'}, {'id': 'bad-source-null-real-origin-change', 'captured_at': 1002, 'saved_file': 'bad-source-null-real-origin-change.saved.json', 'saved_sha256': '1f472c41d0e3d2334898f0faf6de619f6566058bf57542998568fe938f31a15e', 'observed_file': 'bad-source-null-real-origin-change.observed.json', 'observed_sha256': '11ddafc2f0c2affab095f8df86f10f45696a1f48c05ac328438f717b385e0cdb'}, {'id': 'healthy-source-valid-real-origin-change', 'captured_at': 1002, 'saved_file': 'healthy-source-valid-real-origin-change.saved.json', 'saved_sha256': 'f489427029bb6d8917b4dbdff501c0db2eb58221e2498baa3ca1b3a7c84630c3', 'observed_file': 'healthy-source-valid-real-origin-change.observed.json', 'observed_sha256': '11ddafc2f0c2affab095f8df86f10f45696a1f48c05ac328438f717b385e0cdb'}, {'id': 'healthy-legacy-gold-correction', 'captured_at': 1002, 'saved_file': 'healthy-legacy-gold-correction.saved.json', 'saved_sha256': '92bcdec34dbf96af17e5f853cfaa6d6138ddbc1680d615a3a626c53d52687779', 'observed_file': 'healthy-legacy-gold-correction.observed.json', 'observed_sha256': '11ddafc2f0c2affab095f8df86f10f45696a1f48c05ac328438f717b385e0cdb'}, {'id': 'safe-unused-null-source-origin-absent', 'captured_at': 1002, 'saved_file': 'safe-unused-null-source-origin-absent.saved.json', 'saved_sha256': 'c41f9ea8c5c580e4b299b725213fc014aae065f3c7398bfce6575547023fe277', 'observed_file': 'safe-unused-null-source-origin-absent.observed.json', 'observed_sha256': '87340fa1f8a9ac327937046e36e1bd3f787cb4cbf5ca614644bfb049bcfafcb2'}, {'id': 'safe-unused-null-source-origin-null', 'captured_at': 1002, 'saved_file': 'safe-unused-null-source-origin-null.saved.json', 'saved_sha256': 'c41f9ea8c5c580e4b299b725213fc014aae065f3c7398bfce6575547023fe277', 'observed_file': 'safe-unused-null-source-origin-null.observed.json', 'observed_sha256': '776ddcae7fb7c04e2f734ee68c45318fbd0a82b4f53ec33e09860747b0037e66'}, {'id': 'safe-stale-null-source-fresh-known', 'captured_at': 1000, 'saved_file': 'safe-stale-null-source-fresh-known.saved.json', 'saved_sha256': 'c41f9ea8c5c580e4b299b725213fc014aae065f3c7398bfce6575547023fe277', 'observed_file': 'safe-stale-null-source-fresh-known.observed.json', 'observed_sha256': '11ddafc2f0c2affab095f8df86f10f45696a1f48c05ac328438f717b385e0cdb'}, {'id': 'safe-source-dict-opaque-leaves', 'captured_at': 1002, 'saved_file': 'safe-source-dict-opaque-leaves.saved.json', 'saved_sha256': '8a0fd1862fd3d703edf1e06ff6e0140bf4b1b054efe0b56e3e0b9b1b8dbbadfa', 'observed_file': 'safe-source-dict-opaque-leaves.observed.json', 'observed_sha256': '11ddafc2f0c2affab095f8df86f10f45696a1f48c05ac328438f717b385e0cdb'}]


def sha(value):
    return hashlib.sha256(value).hexdigest()


def write_json(path, value):
    temporary=path.with_suffix(path.suffix+'.tmp')
    temporary.write_text(json.dumps(value,ensure_ascii=False,allow_nan=False,indent=2)+'\n',encoding='utf-8')
    os.replace(temporary,path)


def disk_snapshot(path):
    return {name: {'exists':p.exists(),'bytes':p.read_bytes() if p.exists() else None}
            for name,p in [('run',path),('temporary',path.with_suffix('.tmp'))]}


def exception_record(error):
    return {'type':type(error).__name__,'message':str(error),
            'traceback':''.join(traceback.format_exception(type(error),error,error.__traceback__))}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--root',required=True)
    parser.add_argument('--guard',required=True)
    parser.add_argument('--fixtures',required=True)
    parser.add_argument('--out',required=True)
    args=parser.parse_args()
    root=Path(args.root).resolve();guard_path=Path(args.guard).resolve()
    fixtures=Path(args.fixtures).resolve();output=Path(args.out).resolve()
    assert not output.exists() and output!=root and root not in output.parents
    assert fixtures!=root and root not in fixtures.parents
    guard_raw=guard_path.read_bytes();guard=json.loads(guard_raw)
    expected=guard.get('source_sha256',guard.get('source_sha256_after'))
    assert type(expected) is dict and len(expected)==743
    assert expected['rouge/run_state.py']==RUNSTATE_SHA
    extra=guard.get('source_additional_sha256')
    assert type(extra) is dict and extra=={'CORE_0.70_VERIFICATION.json':CORE_SHA}
    assert sha((root/'CORE_0.70_VERIFICATION.json').read_bytes())==CORE_SHA
    assert sha((fixtures.parent/'audit-origin-provenance.json').read_bytes())==AUDIT_SHA
    native_path=Path(__file__).with_name('native_evidence.py')
    assert not native_path.is_symlink() and sha(native_path.read_bytes())==NATIVE_SHA
    sys.dont_write_bytecode=True
    from native_evidence import source_map,freeze,assert_native_equal,write_record
    assert source_map(root)==expected
    for case in CASES:
        for key in ('saved','observed'):
            path=fixtures/case[key+'_file']
            assert not path.is_symlink() and path.is_file()
            assert sha(path.read_bytes())==case[key+'_sha256']
    output.mkdir(parents=True);(output/'public-state').mkdir();(output/'native').mkdir()
    rows=[];native_rows=[];finished=threading.Event();active={'case':'preimport'}
    receipt={'kind':'ROOT_ACTUAL_ORIGINAL743_RECRUITMENT_PROVENANCE_OBSERVATIONS',
             'observation_only':True,'product_pass':False,'observation_complete':False,
             'author_Source_only':True,'runner_sha256':sha(Path(__file__).read_bytes()),
             'native_helper_sha256':NATIVE_SHA,'fixture_audit_sha256':AUDIT_SHA,
             'source_guard_path':str(guard_path),'source_guard_sha256':sha(guard_raw),
             'source_before':expected,'CORE_before':CORE_SHA,
             'started_at_UTC':datetime.now(timezone.utc).isoformat(),
             'rows':rows,'native_records':native_rows,'deadline_seconds':120,
             'private_state_access':False,'game_chat_sampling_executed':False,
             'native_windows_verified':False}
    start=time.perf_counter()
    def deadline():
        if not finished.wait(120):
            write_json(output/'timeout.json',{'product_pass':False,'active_case':active['case'],
                        'elapsed_seconds':time.perf_counter()-start,'reason':'Root120sLinuxProbeBudget'})
            os._exit(124)
    def save_native(kind,case_id,value):
        metadata=write_record(output/'native',len(native_rows),value)
        metadata.update({'kind':kind,'case':case_id});native_rows.append(metadata);return metadata
    threading.Thread(target=deadline,daemon=True).start()
    sys.path.insert(0,str(root))
    try:
        from rouge.run_state import RunState
        for case in CASES:
            active['case']=case['id']
            directory=output/'public-state'/case['id'];directory.mkdir()
            path=directory/'run.json';raw=(fixtures/case['saved_file']).read_bytes()
            path.write_bytes(raw);path.with_suffix('.tmp').write_bytes(b'public-section103-preexisting-temporary-sentinel\n')
            observed=json.loads((fixtures/case['observed_file']).read_bytes());at=case['captured_at']
            caller_before=freeze((observed,at));original_disks=freeze(disk_snapshot(path))
            row={'id':case['id'],'input_json_sha256':sha(raw),'captured_at':at,
                 'loader_accepted':None,'loader_error':None,'summary_error':None,
                 'apply_result':None,'apply_error':None,'restart_error':None}
            rows.append(row)
            try:run=RunState(path)
            except Exception as error:
                row['loader_error']=exception_record(error)
                row['loader_evidence']=save_native('loader-exception',case['id'],
                    {'caller_before':caller_before,'caller_after':(observed,at),
                     'disks_before':original_disks,'disks_after':disk_snapshot(path)})
                assert_native_equal((observed,at),caller_before,'loader does not mutate caller')
                continue
            row['loader_accepted']=not run.preserve_unreadable
            row['loaded_run_id']=run.state['id']
            row['loader_disk_unchanged']=disk_snapshot(path)==original_disks
            state_before=freeze(run.state);before_disks=freeze(disk_snapshot(path))
            try:row['summary_before']=run.summary()
            except Exception as error:row['summary_error']=exception_record(error)
            assert_native_equal(run.state,state_before,'summary does not edit state')
            assert_native_equal(disk_snapshot(path),before_disks,'summary does not edit disk')
            try:row['apply_result']=run.apply(observed,at)
            except Exception as error:row['apply_error']=exception_record(error)
            caller_after=(observed,at)
            assert_native_equal(caller_after,caller_before,'actual RunState.apply caller input preserved')
            after_disks=disk_snapshot(path);after_state=freeze(run.state)
            row['disk_unchanged_after_apply']=after_disks==original_disks
            row['state_unchanged_after_apply']=run.state==state_before
            row['native_evidence']=save_native('actual-direct-RunState.apply',case['id'],
                {'caller_before':caller_before,'caller_after':caller_after,
                 'state_before':state_before,'state_after':after_state,
                 'disks_before':original_disks,'disks_after':after_disks,
                 'apply_result':row['apply_result'],'apply_error':row['apply_error']})
            restart_disk_before=freeze(disk_snapshot(path))
            try:
                restarted=RunState(path)
                row['restart_loader_accepted']=not restarted.preserve_unreadable
                row['restart_run_id']=restarted.state['id']
                row['restart_evidence']=save_native('actual-direct-restart',case['id'],
                    {'state':restarted.state,'disks_before':restart_disk_before,'disks_after':disk_snapshot(path)})
            except Exception as error:row['restart_error']=exception_record(error)
            # apply(True) is an explicit public observation/save phase. Its disk
            # is not falsely compared with original bytes as a pure view.
            row['disk_phase']='authorized_observation_save' if row['apply_result'] is True else 'no_successful_observation_save'
            write_json(output/'observations.json',receipt)
        receipt['source_after']=source_map(root)
        assert receipt['source_after']==expected
        receipt['CORE_after']=sha((root/'CORE_0.70_VERIFICATION.json').read_bytes())
        assert receipt['CORE_after']==CORE_SHA and guard_path.read_bytes()==guard_raw
        receipt['observation_complete']=True
    except BaseException as error:
        receipt['fatal']=exception_record(error)
        raise
    finally:
        finished.set();receipt['elapsed_seconds']=time.perf_counter()-start
        receipt['ended_at_UTC']=datetime.now(timezone.utc).isoformat()
        write_json(output/'observations.json',receipt)
    print(json.dumps({'observation_complete':receipt['observation_complete'],'product_pass':False,
                      'rows':len(rows),'native_records':len(native_rows)},ensure_ascii=False))


if __name__=='__main__':
    main()
