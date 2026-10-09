"""Root independent readback of actual102 native evidence; no project import."""
import datetime
import hashlib
import json
from pathlib import Path
import sys

base=Path('/workspace/.continuation');root=Path('/workspace/rougezhushou');packet=base/'section102-window-source-v2'
assert hashlib.sha256((packet/'native_evidence.py').read_bytes()).hexdigest()=='f040258eddbb7ad624e547e2c422a3d432f7ffeae025b2576b625683ea43fe9a'
sys.path.insert(0,str(packet))
from native_evidence import read_record,assert_native_equal,source_map
guard=json.loads((base/'resume102-applied-source-v1.json').read_bytes());candidate=base/'resume102-window-candidate-v1';gold=base/'resume102-window-gold-v1'
receipts={};saved={};counts={}
for phase,out,windows in (('gold',gold,6),('candidate',candidate,14)):
    assert (base/('resume102-window-'+phase+'-v1.exit-code')).read_bytes()==b'0\n'
    receipt=json.loads((out/'receipt.json').read_bytes());receipts[phase]=receipt
    assert receipt['passed'] is True and receipt['workflow_complete'] is True and not receipt['Qt_errors']
    assert len(receipt['rows'])==windows and not receipt['source_drift'] and receipt['source_before']==receipt['source_after']
    assert receipt['runner_sha256']==hashlib.sha256((packet/'window102.py').read_bytes()).hexdigest()
    assert receipt['source_additional_before']==receipt['source_additional_after']==guard['source_additional_sha256']
    local={};calls=snapshots=posts=0
    for row in receipt['records']:
        value=read_record(out/'records',row);assert row['path'] not in local;local[row['path']]=value
        assert value['kind']==row['kind'] and value['case']==row['case']
        if row['kind']=='actual_calculate_result':
            calls+=1;assert_native_equal(value['after'],value['before'],'Saved actual numeric caller type/float/order/alias equality')
        elif row['kind'] in ('actual_window_snapshot','actual_authorized_observation_save_restart'):
            if row['kind']=='actual_window_snapshot':snapshots+=1
            else:posts+=1
            view=value['view'];disk=value['disks'];durable=value['durable']
            assert disk['run_tmp'] is False and disk['account_tmp'] is False
            assert type(disk['run']) is bytes and type(disk['account']) is bytes
            texts=view['three_texts'];assert set(texts)=={'estimate','default','technical'}
            assert all(type(text) is str and text for text in texts.values()) and texts['default']==texts['estimate']
            assert_native_equal(json.loads(disk['run'])['inventory_verified'],durable['run']['inventory_verified'],'Saved raw flag exact loaded native type/value')
        else:raise AssertionError(row['kind'])
    assert calls>=windows and snapshots==windows and posts==(0 if phase=='gold' else 5)
    counts[phase]={'native_records':len(local),'actual_original_numeric_calls':calls,'snapshots':snapshots,'authorized_save_restart_phases':posts}
    saved[phase]=local
assert source_map(root)==receipts['candidate']['source_before']==guard['source_sha256']
for name,want in guard['source_additional_sha256'].items():assert hashlib.sha256((root/name).read_bytes()).hexdigest()==want
original={row['id']:saved['gold'][row['snapshot']['path']] for row in receipts['gold']['rows']}
for row in receipts['candidate']['rows']:
    value=saved['candidate'][row['snapshot']['path']]
    if row['id'] in original:
        assert row['complete_healthy_Gold_native_and_three_texts_equal'] is True
        assert_native_equal({key:value[key] for key in ('view','durable','disks')},
                            {key:original[row['id']][key] for key in ('view','durable','disks')},'Root independent complete healthy Gold comparison')
    else:
        assert value['view']['inventory']['complete'] is False
        assert '持有清单已核对（本局记录）' not in value['view']['summary']
    if 'after_observation' in row:
        post=saved['candidate'][row['after_observation']['path']]
        assert_native_equal(post['disks']['account'],value['disks']['account'],'Accepted run save leaves public account disk unchanged')
        if row['id'] in ('current-full','current-zero','valid-history-replay'):
            assert post['durable']['run']['inventory_verified'] is True and post['view']['inventory']['complete'] is True
        else:assert post['view']['inventory']['complete'] is False
        if row['id']=='valid-history-replay':assert post['view']['held']==['rogue_6_relic_legacy_24_c']
        if row['id']=='partial-no-history':assert_native_equal(post['durable']['run']['inventory_verified'],value['durable']['run']['inventory_verified'],'Partial observation cannot invent historical proof')
for row in receipts['candidate']['pngs']:
    raw=(candidate/row['file']).read_bytes();assert raw.startswith(b'\x89PNG\r\n\x1a\n')
    assert len(raw)==row['bytes'] and hashlib.sha256(raw).hexdigest()==row['sha256']
assert len(receipts['candidate']['pngs'])==4
visual=json.loads((base/'resume102-visual-audit-v1.json').read_bytes());assert visual['actually_viewed_images']==4
receipt={'passed':True,'workflow_complete':True,'kind':'ROOT_ACTUAL_102_SAVED_NATIVE_VISUAL_READBACK',
         'at_Beijing':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),
         'phase_counts':counts,'healthy_complete_native_and_three_full_text_pairs':6,'candidate_real_windows':14,
         'pngs_actually_viewed':4,'source_drift':[],'source_files':746,'source_additional_sha256':guard['source_additional_sha256'],
         'native_windows_game_chat_verified':False}
with (base/'root-resume102-saved-audit-v1.json').open('x') as stream:json.dump(receipt,stream,ensure_ascii=False,indent=2);stream.write('\n')
print(json.dumps(receipt,ensure_ascii=False))
