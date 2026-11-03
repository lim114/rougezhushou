"""Read actual saved evidence only; no application imports or calls."""
import gzip
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

ROOT=Path('/workspace/rougezhushou')
LOCAL=Path('/workspace/.continuation')
OUT=Path('/workspace/.compat')
sha=lambda b:hashlib.sha256(b).hexdigest()

def native_decode(node):
    kind=node['type']
    if kind in ('NoneType','bool','int','str'):
        assert set(node)=={'type','value'}
        value=node['value'];expected={'NoneType':type(None),'bool':bool,'int':int,'str':str}[kind]
        assert type(value) is expected
        return value
    if kind=='float':
        assert set(node)=={'type','hex'} and type(node['hex']) is str
        value=float.fromhex(node['hex']);assert value.hex()==node['hex']
        return value
    assert set(node)=={'type','items'} and type(node['items']) is list
    if kind in ('list','tuple'):
        values=[native_decode(v) for v in node['items']]
        return values if kind=='list' else tuple(values)
    assert kind=='dict'
    result={}
    for pair in node['items']:
        assert type(pair) is list and len(pair)==2
        key,value=map(native_decode,pair);assert key not in result
        result[key]=value
    return result

def load_actual(name):
    path=OUT/name;receipt=json.loads(path.read_bytes());lossless=receipt['lossless_records']
    raw=(OUT/lossless['file']).read_bytes();decoded=gzip.decompress(raw)
    assert len(raw)==lossless['bytes'] and sha(raw)==lossless['sha256']
    assert len(decoded)==lossless['decoded_bytes'] and sha(decoded)==lossless['decoded_sha256']
    payload=json.loads(decoded)
    for row in payload['states']:
        if not row['passed']:continue
        if row['planned'].get('numerical_result_expected',True):
            for field in ('scenario','result'):
                restored=native_decode(row[field+'_native_before'])
                assert json.loads(json.dumps(restored,ensure_ascii=False,allow_nan=False))==row[field]
            assert set(row['reports'])=={'estimate','default','technical'}
            assert all(type(v) is str and v for v in row['reports'].values())
    for event in payload['API_events']:
        assert event['input_native_before']==event['input_native_after'] and event['caller_native_unchanged']
        native_decode(event['input_native_before'])
    assert receipt['source_drift']==[]
    return receipt,payload

phase=sys.argv[1]
old,first=load_actual('wine-focused-mainwindow-091.json')
assert old['passed'] is False and old['failure']['type']=='KeyError' and old['failure']['message']=="'id'"
assert len(first['states'])==17 and len(old['checks'])==16
assert all(r['passed'] for r in first['states'][:16]) and first['states'][16]['passed'] is False
assert first['states'][15]['id']=='amiya-natural-return-retains-false'
assert len(first['API_events'])==60 and Counter(a['outcome'] for a in first['API_events'])=={'returned_dict':60}
expected=json.loads((LOCAL/'root-source-091.json').read_bytes())['source_sha256_after']
current={p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for folder in ('rouge','tests','scripts') for p in sorted((ROOT/folder).rglob('*')) if p.is_file() and p.suffix in ('.py','.json') and '__pycache__' not in p.parts}
assert current==expected==old['source_sha256_after'] and len(current)==730
report={'format_version':1,'phase':phase,'passed_prefix_states':16,'initial_actual_run_passed':False,'initial_actual_failure_preserved':old['failure'],'initial_main_thread_API_entries':60,'initial_API_returned_dict':60,'initial_explicit_text_requests':48,'initial_lossless':old['lossless_records'],'all730_maintained_sources_exact':True,'new_project_calls':0,'native_windows_certified':False}
if phase=='prefix':
    name='root-focused091-prefix-verification.json'
elif phase=='aggregate':
    second,rest=load_actual(sys.argv[2])
    assert second['passed'] and second['source_sha256_after']==current
    warm=rest['warm_recovery']
    assert second['warm_recovery_native_exact_passed'] and warm['passed']
    assert warm['scenario_native']==first['states'][15]['scenario_native_before']
    assert warm['result_native']==first['states'][15]['result_native_before']
    assert len(rest['states'])==8 and all(r['passed'] for r in rest['states'])
    states=first['states'][:16]+rest['states'];assert len(states)==24 and len({r['id'] for r in states})==24
    numeric=[r for r in states if r['planned'].get('numerical_result_expected',True)]
    assert len(numeric)==21 and sum(len(r['reports']) for r in numeric)==63
    report.update(complete_focused_acceptance_across_initial_prefix_and_resume=True,states=24,numeric_states=21,early_None_states=3,explicit_texts=63,warm_native_input_and_result_exact_original_passed=True,resume_receipt=sys.argv[2],resume_lossless=second['lossless_records'],resume_main_thread_API_outcomes=dict(Counter(a['outcome'] for a in rest['API_events'])),scope='Two real isolated windows: original16 PASS plus restored remaining8, no rerun of16. Counts are actual main-thread entries; talent traces are action-level. Initial full-run failure is retained.')
    name='root-focused091-aggregate-verification.json'
else:raise ValueError(phase)
with (LOCAL/name).open('xb') as f:f.write((json.dumps(report,ensure_ascii=False,indent=2)+'\n').encode())
print(json.dumps({k:v for k,v in report.items() if k not in ('initial_actual_failure_preserved','initial_lossless','resume_lossless')},ensure_ascii=False))
