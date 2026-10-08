"""Independent saved-only source reproduction proof, no project imports."""
import gzip
import hashlib
import json
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
        assert kind in ('str','bool','int','NoneType');v=t['value'];assert type(v).__name__==kind
    assert canon(typed(v))==canon(t)
    return v


path=OUT/'public-source16.jsonl.gz';compressed=path.read_bytes();raw=gzip.decompress(compressed)
summary=json.loads((OUT/'public-source16-summary.json').read_bytes())
assert summary['actual_public_calls']==16 and summary['accepted']==16 and summary['old_errors']==0
assert summary['gzip_sha256']==hashlib.sha256(compressed).hexdigest() and summary['gzip_bytes']==len(compressed)
assert summary['decoded_sha256']==hashlib.sha256(raw).hexdigest() and summary['decoded_bytes']==len(raw)
rows=[json.loads(line) for line in raw.splitlines()];assert len(rows)==16
for row in rows:
    assert row['outcome']=='accepted' and canon(decode(row['result_typed']))==canon(row['result'])
    assert canon(decode(row['input_typed_before']))==canon(row['input'])
    assert canon(row['input_typed_before'])==canon(row['input_typed_after'])
    assert row['catalog_native_sha256_before']==row['catalog_native_sha256_after']
    assert set(row['reports'])=={'estimate','user','technical'} and all(type(x) is str for x in row['reports'].values())
groups=[]
for start in range(0,16,4):
    group=rows[start:start+4];output=lambda r:canon({k:r[k] for k in ('result','result_typed','reports')})
    assert [r['input']['continuous_attacks'] for r in group]==[False,True,'false','']
    assert len({canon({k:v for k,v in r['input'].items() if k!='continuous_attacks'}) for r in group})==1
    assert output(group[2])==output(group[1]) and output(group[3])==output(group[0])
    differs=output(group[0])!=output(group[1]);assert differs==(start<12)
    if not differs:assert len({output(r) for r in group})==1
    groups.append({'label':group[0]['label'],'public_operator':group[0]['input']['operator'],'skill':group[0]['input']['skill'],
                   'bool_false_true_whole_difference':differs,'text_false_whole_true':True,'empty_text_whole_false':True,
                   'values':[{'input':r['input']['continuous_attacks'],'first_recharge_cycle':{
                       k:r['result']['estimate']['skill'][k] for k in ('initial_seconds','recharge_seconds','cycle_seconds')}} for r in group]})
result={'status':'PASS_SOURCE_REPRODUCTION_ONLY','saved_public_calls':16,'new_public_or_helper_calls_for_compare':0,
        'groups':groups,'whole_preencoding_native_public_and_three_report_equality':True,
        'native_trees_decode_reencode_and_JSON_bound':True,'caller_catalog_native_isolation':True,'normalization':None,
        'frozen_source_gzip_sha256':hashlib.sha256(compressed).hexdigest(),
        'candidate':'continuous_attacks active text truthiness changes established current output; contextual guard needed, inactive natural legacy input stays accepted.',
        'not_proven_by_these16':['all owners/skills','periodic-SP or received-SP path coverage','E0/E1 Amiya unknown-clock reference branch','older-error combinations','native timing or attachment'],
        'no_replacement_or_retries':True,'tests':0,'Qt':0,'Wine':0,'tracked_edits':0}
(OUT/'saved-source16-comparison.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'status':result['status'],'saved_public_calls':16,'active_groups':3,'inactive_groups':1,'new_API_helper_calls':0}))
