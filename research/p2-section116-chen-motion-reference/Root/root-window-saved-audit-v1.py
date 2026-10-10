"""Root Saved native audit; no project calls, no UI result reconstruction."""
import argparse,hashlib,json,sys
from pathlib import Path
p=argparse.ArgumentParser()
for key in ('guard','actual','out'):p.add_argument('--'+key,required=True)
a=p.parse_args();G=Path(a.guard);D=Path(a.actual);O=Path(a.out);B=Path('/workspace/.continuation')
H=B/'section109-empty-target-original-probe-source-v1/native_evidence.py'
assert hashlib.sha256(H.read_bytes()).hexdigest()=='f040258eddbb7ad624e547e2c422a3d432f7ffeae025b2576b625683ea43fe9a'
sys.path.insert(0,str(H.parent))
from native_evidence import read_record,assert_native_equal,source_map
g=json.loads(G.read_text());r=json.loads((D/'receipt.json').read_text())
assert not O.exists() and r['passed'] is True and r['workflow_complete'] is True and not r['source_drift']
assert source_map('/workspace/rougezhushou')==g['source_sha256']==r['source_before']==r['source_after']
assert r['source_additional_before']==r['source_additional_after']==g['source_additional_sha256']
assert r['source_guard_sha256']==hashlib.sha256(G.read_bytes()).hexdigest()
decoded={};checked=0
for m in r['records']:
    assert m['path'] not in decoded
    v=read_record(D/'records',m);assert v['kind']==m['kind'];decoded[m['path']]=v
    k=v['kind']
    if k=='actual_calculate_result':assert_native_equal(v['after'],v['before'],'saved numeric caller+joint');checked+=1
    elif k=='actual_calculate_exception':raise AssertionError('unexpected recorded numeric exception')
    elif k=='actual_UI_step':assert_native_equal(v['after']['joint'],v['before']['joint'],'saved UI public state+disk');checked+=1
    elif k=='actual_three_formatter_group':
        assert_native_equal(v['after'],v['before'],'saved full formatter joint');assert v['texts']['estimate']==v['texts']['default'];checked+=1
    elif k=='actual_window_snapshot':
        s=v['value'];assert s['displayed_damage']==s['texts']['default'].replace(chr(160),' ');checked+=1
    elif k=='actual_close_RunState_AccountCache_reload':
        assert_native_equal(v['restart_state'],v['live_before']['run'],'saved real RunState reload')
        assert_native_equal(v['account_restart_records'],v['live_before']['account'],'saved real account reload')
        assert_native_equal(v['disks_after'],v['live_before']['disks'],'saved reload disk bytes');checked+=1
assert len(decoded)==len(r['records']) and not r['Qt_errors']
for row in r['rows']:
    v=decoded[row['snapshot']['path']]['value'];n=decoded[row['numeric']['path']]
    assert_native_equal(v['damage_result']['result'],n['result'],'saved full snapshot/numeric graph')
    assert_native_equal(v['caller'],n['before']['args'][0],'saved full snapshot caller')
for png in r['pngs']:
    f=D/png['path'];assert f.name==png['path'] and not f.is_symlink();b=f.read_bytes()
    assert len(b)==png['bytes'] and hashlib.sha256(b).hexdigest()==png['sha256'] and b.startswith(b'\x89PNG\r\n\x1a\n')
    assert png['visual']['path'] in decoded
assert source_map('/workspace/rougezhushou')==g['source_sha256']
out={'kind':'ROOT_ACTUAL_SAVED_MAINWINDOW_NATIVE_AUDIT','passed':True,'workflow_complete':True,'source_drift':[],'section':g['section'],'native_records_decoded':len(decoded),'strict_checks':checked,'actual_snapshots':len(r['rows']),'actual_png_byte_checked':len(r['pngs']),'actual_png_visual_review_pending':True,'no_project_formatter_UI_reexecution':True,'native_windows_game_chat_verified':False}
O.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(out))
