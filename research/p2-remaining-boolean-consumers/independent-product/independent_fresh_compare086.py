"""Strict complete comparison of the 12 different independent inputs."""
import gzip
import hashlib
import json
from collections import Counter
from pathlib import Path

OUT=Path(__file__).resolve().parent
canon=lambda v:json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)


def typed(v):
    if isinstance(v,dict):return {'type':'dict','items':[[typed(k),typed(x)] for k,x in v.items()]}
    if isinstance(v,(list,tuple)):return {'type':type(v).__name__,'items':[typed(x) for x in v]}
    if isinstance(v,float):return {'type':'float','hex':v.hex()}
    return {'type':type(v).__name__,'value':v}


def decode(t):
    kind=t['type']
    if kind=='dict':v={decode(k):decode(x) for k,x in t['items']}
    elif kind in ('list','tuple'):
        v=[decode(x) for x in t['items']]
        if kind=='tuple':v=tuple(v)
    elif kind=='float':v=float.fromhex(t['hex'])
    else:
        assert kind in ('NoneType','str','bool','int')
        v=t['value'];assert type(v).__name__==kind
    assert canon(typed(v))==canon(t)
    return v


def without_marker(trace):
    return [{k:v for k,v in row.items() if k not in ('ranged_signal_present','ranged_signal')} for row in trace]


rows=[];bindings=[]
for name in ('independent-public-baseline086.json.gz','independent-public-draft086.json.gz'):
    path=OUT/name;data=path.read_bytes();raw=gzip.decompress(data)
    rows.append(json.loads(raw));bindings.append({'source_path':str(path),'sha256':hashlib.sha256(data).hexdigest(),
                                               'bytes':len(data),'decoded_sha256':hashlib.sha256(raw).hexdigest()})
assert len(rows[0])==len(rows[1])==12
counts=Counter();actual=[]
output={'outcome','result','result_typed','reports','error_type','error_message','actual_internal_trace'}
for a,b in zip(*rows,strict=True):
    assert canon({k:v for k,v in a.items() if k not in output})==canon({k:v for k,v in b.items() if k not in output})
    for row in (a,b):
        assert canon(row['input_typed_before'])==canon(row['input_typed_after'])
        assert canon(decode(row['input_typed_before']))==canon(row['input'])
        assert row['catalog_native_sha256_before']==row['catalog_native_sha256_after']
        if row['outcome']=='accepted':
            assert canon(decode(row['result_typed']))==canon(row['result'])
            assert set(row['reports'])=={'estimate','user','technical'} and all(type(v) is str for v in row['reports'].values())
    if a['expect']=='same':
        assert a['outcome']==b['outcome']=='accepted'
        assert canon(a['result_typed'])==canon(b['result_typed'])
        assert canon({k:v for k,v in a.items() if k!='actual_internal_trace'})==canon({k:v for k,v in b.items() if k!='actual_internal_trace'})
        assert canon(without_marker(a['actual_internal_trace']))==canon(without_marker(b['actual_internal_trace']))
        counts['whole_success_same']+=1
    elif a['expect']=='old_error':
        assert a['outcome']==b['outcome']=='error'
        assert canon({k:v for k,v in a.items() if k!='actual_internal_trace'})==canon({k:v for k,v in b.items() if k!='actual_internal_trace'})
        assert canon(without_marker(a['actual_internal_trace']))==canon(without_marker(b['actual_internal_trace']))
        counts['old_errors_exact']+=1
    else:
        assert a['outcome']=='accepted' and b['outcome']=='error'
        assert b['error_type']=='ValueError' and b['error_message']==a['expect']+' 不接受文本条件；请使用布尔值。'
        assert type(decode(a['input_typed_before'])[a['expect']]) is str
        counts['qualified_text_rejected']+=1
    actual.append({'index':a['index'],'label':a['label'],'old_outcome':a['outcome'],'new_outcome':b['outcome'],
                   'new_error_message':b.get('error_message'),'draft_actual_internal_trace':b['actual_internal_trace']})
assert dict(counts)=={'whole_success_same':6,'qualified_text_rejected':5,'old_errors_exact':1}
for index in (0,1,2):
    traces=rows[1][index]['actual_internal_trace'];assert traces
    assert all(t['operator']=='char_4182_oblvns' and t['ranged_signal_present'] and t['ranged_signal'] is False for t in traces)
    assert not any(p['normal'] for t in traces for p in t['actual_plan_calls'])
t=rows[1][3]['actual_internal_trace'][0]
assert t['ranged_signal'] is True and any(p['normal'] for p in t['actual_plan_calls'])
assert '反移情' not in rows[1][4]['actual_internal_trace'][0]['selected_talent_names']
assert '反移情' in rows[1][5]['actual_internal_trace'][0]['selected_talent_names']
assert decode(rows[0][9]['input_typed_before'])['double_charge']==(False,)
assert type(decode(rows[0][9]['input_typed_before'])['double_charge']) is tuple
assert rows[0][10]['actual_internal_trace']==rows[1][10]['actual_internal_trace']==[]
assert rows[0][11]['error_message']==rows[1][11]['error_message']=='near_previous_deployment 不接受文本条件；请使用布尔值。'
receipt={'status':'PASS','different_unique_inputs':12,'fresh_public_calls':24,'new_explicit_project_helper_calls':0,
         'counts':dict(counts),'full_native_trees_before_JSON_full_public_three_reports':True,
         'distinct_from_author268':True,'caller_and_cached_catalog_native_type_isolation':True,
         'read_only_actual_internal_traces':actual,'trace_wrapper_scope':'Calls original methods exactly once and returns original values; external trace only, no object/scenario assignments.',
         'compressed_bindings':bindings,'normalization':None,'older_error_scope':'Actual prior near_previous_deployment guard with two simultaneous new active textual fields; no universal outer-error guarantee.',
         'native_clock_and_attachment':'unknown; not validated','Qt':0,'Wine':0,'tracked_edits':0}
(OUT/'independent-fresh-comparison086.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'status':'PASS','fresh_public_calls':24,'counts':dict(counts),'normalization':None,'actual_normal_and_selected_talent_trace_checked':True},ensure_ascii=False))
