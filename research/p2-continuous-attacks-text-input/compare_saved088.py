"""Strict saved full native trees, public JSON, texts and errors; zero new API."""
from pathlib import Path
import gzip,hashlib,json,struct
OUT=Path(__file__).resolve().parent
def native(v):
    if isinstance(v,dict):return {'type':'dict','items':[[native(k),native(x)] for k,x in v.items()]}
    if isinstance(v,(list,tuple)):return {'type':type(v).__name__,'items':[native(x) for x in v]}
    if isinstance(v,float):return {'type':'float','hex':v.hex()}
    return {'type':type(v).__name__,'value':v}
def decode(t):
    typ=t['type']
    if typ=='dict':return {decode(k):decode(v) for k,v in t['items']}
    if typ in ('list','tuple'):
        values=[decode(v) for v in t['items']];return tuple(values) if typ=='tuple' else values
    if typ=='float':return float.fromhex(t['hex'])
    assert typ in ('int','bool','str','NoneType'),typ
    value=t['value'];assert type(value).__name__==typ;return value
def canon(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)
def typed_json(x):
    if isinstance(x,dict):return [(k,typed_json(v)) for k,v in x.items()]
    if isinstance(x,list):return [typed_json(v) for v in x]
    return (type(x).__name__,x.hex() if isinstance(x,float) else x)
records={}
for side in ('baseline','draft'):
    summary=json.loads((OUT/(side+'-public60-summary.json')).read_text())
    p=OUT/(side+'-public60.jsonl.gz');raw=p.read_bytes();data=gzip.decompress(raw)
    assert (len(raw),hashlib.sha256(raw).hexdigest())==(summary['gzip_bytes'],summary['gzip_sha256'])
    assert (len(data),hashlib.sha256(data).hexdigest())==(summary['decoded_bytes'],summary['decoded_sha256'])
    rows=[json.loads(line) for line in data.splitlines()];assert len(rows)==60
    for r in rows:
        assert r['input_typed_before']==r['input_typed_after']
        assert r['input_typed_before']==native(r['input'])
        assert r['catalog_native_sha256_before']==r['catalog_native_sha256_after']
        if r['outcome']=='accepted':
            decoded=decode(r['result_typed']);assert native(decoded)==r['result_typed']
            json_encoded=json.loads(json.dumps(decoded,ensure_ascii=False,allow_nan=False))
            assert typed_json(json_encoded)==typed_json(r['result'])
            assert set(r['reports'])=={'estimate','user','technical'}
    records[side]=rows
changed=[];same=[];olderrors=[];pairs=[]
for old,new in zip(records['baseline'],records['draft']):
    assert old['case']==new['case'] and native(old['input'])==native(new['input'])
    if old['outcome']=='error':
        assert new['outcome']=='error'
        assert (old['error_type'],old['error_message'])==(new['error_type'],new['error_message'])
        oldererrors={'case':old['case'],'label':old['label'],'error_type':old['error_type'],'error_message':old['error_message']}
        olderrors.append(oldererrors);category='preserved_old_error'
    elif new['outcome']=='error':
        assert isinstance(new['input']['continuous_attacks'],str)
        assert (new['error_type'],new['error_message'])==('ValueError','continuous_attacks 不接受文本条件；请使用布尔值。')
        assert any(r['pending'] is True for r in new['actual_observer_return_trace'])
        changed.append(new['case']);category='actual_consumer_text_rejected'
    else:
        assert old['result_typed']==new['result_typed'],new['case']
        assert typed_json(old['result'])==typed_json(new['result']),new['case']
        assert old['reports']==new['reports'],new['case']
        assert not any(r['pending'] is True for r in new['actual_observer_return_trace'])
        same.append(new['case']);category='whole_native_JSON_three_reports_same'
    pairs.append({'case':old['case'],'label':old['label'],'category':category,
                  'draft_actual_trace':new['actual_observer_return_trace']})
receipt={'status':'PASS_STRICT_SAVED_FULL_COMPARISON','pairs':60,'new_project_calls':0,
    'text_rejections':len(changed),'whole_same':len(same),'exact_old_errors':len(olderrors),
    'changed_cases':changed,'same_cases':same,'old_errors':olderrors,'pair_receipts':pairs,
    'native_decode_reencode_and_strict_JSON_types_bound':True,'three_reports_whole_compared':True,
    'normalization':None,'caller_catalog_unchanged':True,'scope':'Existing software consumers only, no native clock conclusion.'}
(OUT/'saved-comparison088.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in receipt.items() if k not in ('pair_receipts','changed_cases','same_cases','old_errors')},ensure_ascii=False))
