"""Root checks actual101 saved native evidence, without importing project code."""
import datetime
import hashlib
import json
from pathlib import Path, PureWindowsPath
import sys

base=Path('/workspace/.continuation');root=Path('/workspace/rougezhushou')
packet=base/'section101-candidate-window-source-v1';out=base/'resume101-window-candidate-v1'
helper=packet/'native_evidence.py'
assert hashlib.sha256(helper.read_bytes()).hexdigest()=='f040258eddbb7ad624e547e2c422a3d432f7ffeae025b2576b625683ea43fe9a'
sys.path.insert(0,str(packet))
from native_evidence import read_record, assert_native_equal, source_map
receipt=json.loads((out/'receipt.json').read_bytes());guard_raw=(base/'resume101-applied-source-v1.json').read_bytes();guard=json.loads(guard_raw)
assert (base/'resume101-window-candidate-v1.exit-code').read_bytes()==b'0\n'
assert receipt['passed'] is True and receipt['workflow_complete'] is True
assert not receipt['Qt_errors'] and len(receipt['rows'])==13 and len(receipt['pngs'])==4
assert source_map(root)==receipt['source_before']==guard['source_sha256']
assert receipt['source_guard_sha256']==hashlib.sha256(guard_raw).hexdigest()
original=json.loads((base/'section101-original-charbuff-actual-wine-v1/observations.json').read_bytes())
old={row['id']:row for row in original['rows']}
saved={}
success=exceptions=snapshots=post=0
for row in receipt['records']:
    value=read_record(out/'native',row);assert row['path'] not in saved;saved[row['path']]=value
    kind=row['kind']
    if kind in ('actual_calculate_result','actual_calculate_exception'):
        assert_native_equal(value['after'],value['before'],'Saved original numeric caller unchanged')
        if kind=='actual_calculate_result':success+=1
        else:
            exceptions+=1
            assert row['case'] in ('unknown-bound','unknown-pending') and row['exception_type']=='ValueError'
    elif kind in ('actual_window_snapshot','actual_after_authorized_observation'):
        view=value['view'];disks=value['disks'];durable=value['durable']
        assert disks['account_tmp'] is False and disks['run_tmp'] is False
        assert type(disks['account']) is bytes and type(disks['run']) is bytes
        loaded=json.loads(disks['run'])
        if kind=='actual_window_snapshot':snapshots+=1
        else:
            post+=1
            assert_native_equal(loaded['relic_count'],durable['run']['relic_count'],'Saved observation disk count retains native type/value')
        if row['case'] in ('unknown-bound','unknown-pending'):
            assert view['damage_result'] is None and view['three_texts'] is None
            assert '暂不可确认' in view['buff_status']
            assert_native_equal(view['run_metadata'],durable['run']['operators']['mechanist'],'Saved raw unknown metadata unchanged')
        else:
            texts=view['three_texts'];assert set(texts)=={'estimate','default','technical'}
            assert all(type(text) is str and text for text in texts.values())
            assert texts['estimate']==texts['default']
            assert view['damage_text']==texts['default'].replace(chr(160),' ')
        if row['case']=='healthy-snack':
            actual=json.loads(json.dumps(view['damage_result'],ensure_ascii=False,allow_nan=False))
            assert_native_equal(actual,old['healthy-snack']['damage_result'],'Original healthy JSON values equal (no original alias claim)')
            assert view['damage_text']==old['healthy-snack']['damage_text']
    else:raise AssertionError(kind)
assert (success,exceptions,snapshots,post)==(75,12,13,3)
for row in receipt['rows']:
    snapshot=saved[row['snapshot_record']['path']]
    for key in ('account','run'):
        assert hashlib.sha256(snapshot['disks'][key]).hexdigest()==row['original_disk_sha256'][key]
    if 'post_observation_record' in row:
        after=saved[row['post_observation_record']['path']]
        assert_native_equal(after['durable']['run']['relic_count'],snapshot['durable']['run']['relic_count'],'Old native count survives authorized observation')
        assert_native_equal(after['disks']['account'],snapshot['disks']['account'],'Authorized run observation leaves account disk unchanged')
for row in receipt['pngs']:
    name=PureWindowsPath(row['path']).name;raw=(out/name).read_bytes()
    assert raw.startswith(b'\x89PNG\r\n\x1a\n') and len(raw)==row['bytes']
    assert hashlib.sha256(raw).hexdigest()==row['sha256']
audit={'kind':'ROOT_ACTUAL_SAVED_101_NATIVE_AND_VISUAL_AUDIT',
       'verified_at_Beijing':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),
       'passed':True,'actual_windows':13,'native_records':len(saved),'original_numeric_successes':success,
       'original_ValueError_calls_retained':exceptions,'snapshots_with_original_disks':snapshots,
       'authorized_save_restart_phases':post,'three_full_texts_retained_for_successful_snapshots':True,
       'native_type_float_order_alias_caller_equal':True,'healthy_original_comparison_scope':'Actual original JSON values and UI text; no original native-alias Gold was saved.',
       'actually_viewed_pngs':4,'visual_scope':'Unknown bound/pending refusal messages and actual reference result windows visible; buff-status/summary labels checked in saved native views, not asserted visible in these PNGs.',
       'source_files':745,'source_drift':[],'native_windows_game_chat_verified':False}
with (base/'root-resume101-saved-audit-v1.json').open('x') as handle:
    json.dump(audit,handle,ensure_ascii=False,indent=2);handle.write('\n')
print(json.dumps(audit,ensure_ascii=False))
