"""Root readback of completed103 binary evidence, without project imports."""
import datetime
import hashlib
import json
from pathlib import Path
import sys

base=Path('/workspace/.continuation');root=Path('/workspace/rougezhushou');packet=base/'section103-window-source-v2'
assert hashlib.sha256((packet/'native_evidence.py').read_bytes()).hexdigest()=='f040258eddbb7ad624e547e2c422a3d432f7ffeae025b2576b625683ea43fe9a'
sys.path.insert(0,str(packet))
from native_evidence import assert_native_equal,read_record,source_map
guard=json.loads((base/'resume103-applied-source-v1.json').read_bytes());receipts={};saved={};counts={}
for phase,windows in (('gold',9),('candidate',19)):
    out=base/('resume103-window-'+phase+'-v2')
    assert (base/('resume103-window-'+phase+'-v2.exit-code')).read_bytes()==b'0\n'
    receipt=json.loads((out/'receipt.json').read_bytes());receipts[phase]=receipt
    assert receipt['passed'] is True and receipt['workflow_complete'] is True and not receipt['Qt_errors']
    assert len(receipt['rows'])==windows and not receipt['source_drift'] and receipt['source_before']==receipt['source_after']
    assert receipt['source_additional_before']==receipt['source_additional_after']==guard['source_additional_sha256']
    assert receipt['runner_sha256']=='c2eafe3f0aec05d2378b23d9f52160b243e3ee7ed0788a504bef2eaaa49f0074'
    local={};success=errors=initial=post=reloads=0
    for row in receipt['records']:
        value=read_record(out/'records',row);assert row['path'] not in local;local[row['path']]=value
        assert (value['kind'],value['case'],value['phase'])==(row['kind'],row['case'],row['phase'])
        if row['kind'] in ('actual_calculate_result','actual_calculate_exception'):
            assert_native_equal(value['after'],value['before'],'Saved actual original numeric caller exact')
            if row['kind']=='actual_calculate_result':success+=1
            else:
                errors+=1;assert value['error']['type']=='ValueError'
                assert value['error']['message']=='本局分队身份与固定档案不符。'
                assert row['case'].startswith('bad-squad-') or row['case']=='unused-squad-null-time'
        elif row['kind'] in ('actual_initial_window_snapshot','actual_observation_window_snapshot'):
            if row['kind']=='actual_initial_window_snapshot':initial+=1
            else:post+=1
            view=value['view'];disk=value['disks']
            assert disk['run']['exists'] is True and disk['account']['exists'] is True
            assert disk['run_tmp']['exists'] is False and disk['account_tmp']['exists'] is False
            if view['damage_result'] is None:
                assert row['kind']=='actual_initial_window_snapshot'
                assert view['three_texts']=={'pending':'本局分队身份与固定档案不符。'}
            else:
                texts=view['three_texts'];assert set(texts)=={'estimate','default','technical'}
                assert all(type(text) is str and text for text in texts.values()) and texts['default']==texts['estimate']
                assert view['displayed_damage']==texts['default'].replace(chr(160),' ')
        elif row['kind']=='actual_close_RunState_reload':
            reloads+=1;assert_native_equal(value['observation_caller_after'],value['observation_caller_before'],'Actual observation caller remains exact after reload')
            if row['case']=='healthy-stale-null':
                assert_native_equal(value['state'],value['live_state_before_close'],'Stale loaded native graph remains unchanged')
            else:
                assert_native_equal(value['state'],value['persisted_json'],'Reload follows complete actual saved JSON type/float/order graph')
                assert value['restart_oracle']=='Actual saved JSON graph; no live-alias preservation claim'
        else:raise AssertionError(row['kind'])
    assert initial==post==reloads==windows and success>=windows
    if phase=='gold':assert errors==0
    else:assert errors>0
    counts[phase]={'native_records':len(local),'actual_original_numeric_successes':success,
                   'original_numeric_ValueErrors':errors,'initial_snapshots':initial,'post_snapshots':post,'actual_close_RunState_reloads':reloads}
    saved[phase]=local
assert source_map(root)==receipts['candidate']['source_before']==guard['source_sha256']
for name,want in guard['source_additional_sha256'].items():assert hashlib.sha256((root/name).read_bytes()).hexdigest()==want
old={row['id']:row for row in receipts['gold']['rows']}
for row in receipts['candidate']['rows']:
    before=saved['candidate'][row['before']['path']];after=saved['candidate'][row['after']['path']];reload=saved['candidate'][row['restart']['path']]
    assert_native_equal(after['disks']['account'],before['disks']['account'],'Authorized run save leaves account disk exact')
    assert_native_equal(reload['disks'],after['disks'],'Actual close/reload does not rewrite current disk phase')
    if not row['apply_result']:
        assert row['id']=='healthy-stale-null'
        assert_native_equal(after['disks'],before['disks'],'Stale keeps original disks')
        assert_native_equal(after['durable'],before['durable'],'Stale keeps original state')
    if row['id'] in old:
        assert row['complete_healthy_initial_and_after_native_and_three_texts_equal'] is True
        for key in ('before','after'):
            actual=saved['candidate'][row[key]['path']];original=saved['gold'][old[row['id']][key]['path']]
            assert_native_equal({name:actual[name] for name in ('view','durable','disks')},
                                {name:original[name] for name in ('view','durable','disks')},'Root independent complete healthy initial/post Gold readback')
    if row['id'].startswith('bad-origin-'):
        member=after['durable']['run']['operators']['mechanist']
        assert member['recruitment_kind']=='non_emergency'
        assert member['sources']['recruitment_kind']['source']=='等级左侧区域未显示应急人形/时钟标识'
    if row['id'].startswith('bad-squad-'):
        assert before['view']['damage_result'] is None and after['view']['damage_result'] is not None
        assert after['durable']['run']['config']['squad']['id']=='rogue_6_band_6'
for row in receipts['candidate']['pngs']:
    raw=(base/'resume103-window-candidate-v2'/row['file']).read_bytes()
    assert raw.startswith(b'\x89PNG\r\n\x1a\n') and len(raw)==row['bytes'] and hashlib.sha256(raw).hexdigest()==row['sha256']
visual=json.loads((base/'resume103-visual-audit-v1.json').read_bytes());assert visual['actually_viewed_images']==4
receipt={'kind':'ROOT_ACTUAL_103_SAVED_NATIVE_VISUAL_READBACK','passed':True,'workflow_complete':True,
         'at_Beijing':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),
         'phase_counts':counts,'healthy_full_native_initial_and_post_pairs':9,'actual_candidate_windows':19,
         'authorized_candidate_saves':18,'stale_no_save':1,'actually_viewed_pngs':4,'source_files':747,'source_drift':[],
         'reload_scope':'All28 close/direct RunState loads; actual JSON type/float/order oracle, live alias graphs separately retained; no full MainWindow reopen claim',
         'native_windows_game_chat_naturalOCR_verified':False}
with (base/'root-resume103-saved-audit-v1.json').open('x') as stream:json.dump(receipt,stream,ensure_ascii=False,indent=2);stream.write('\n')
print(json.dumps(receipt,ensure_ascii=False))
