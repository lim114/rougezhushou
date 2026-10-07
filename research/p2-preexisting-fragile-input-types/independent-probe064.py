"""Independent bounded public guard probes over committed section60 snapshots."""
from pathlib import Path
from copy import deepcopy
import sys, json, hashlib, datetime
sys.path.insert(0,sys.argv[1])
from rouge.damage import calculate_damage
from rouge.catalog import catalog

def cases():
    for mode in ('frames','continuous'):
        for value in ('false','False','true','0','1','',' ','unknown',False,True,None,0,1,0.0,1.0,-0.0):
            yield {'operator':'silverash','skill':3,'timing_mode':mode,'preexisting_fragile':value}
        yield {'operator':'silverash','skill':3,'timing_mode':mode}
        for rank in (1,4,7):
            for flag in (False,True):
                yield {'operator':'silverash','skill':3,'timing_mode':mode,'skill_rank':rank,'preexisting_fragile':flag,
                       'cooperative':True,'window_seconds':10,
                       'effects':[{'kind':'damage_taken','damage_type':'physical','value':.5}]}
        for scope in ({'window_seconds':0},{'timing':{'target_disappears_seconds':0}},{'timing':{'target_windows':[]}}):
            for flag in ('false',False):
                yield {'operator':'silverash','skill':3,'timing_mode':mode,'preexisting_fragile':flag,**scope}
    for qualification in ({'elite':0,'skill_rank':7},{'elite':1,'skill_rank':7},{'skill':True},
                          {'skill_rank':True},{'skill_rank':0},{'skill_rank':'10'},{'level':True},
                          {'potential':False},{'elite':True}):
        yield {'operator':'silverash','skill':3,'preexisting_fragile':'false',**qualification}
    for operator, skill in (('silverash',1),('silverash',2),('mechanist',2),('kaltsit',3),('char_2025_shu',2)):
        for mode in ('frames','continuous'):
            yield {'operator':operator,'skill':skill,'timing_mode':mode,'preexisting_fragile':'false'}

records=[]; public=deepcopy(catalog()); sha=lambda x:hashlib.sha256(x.read_bytes()).hexdigest()
source_before=sha(Path(sys.argv[1])/'rouge/damage.py')
for request in cases():
    original=deepcopy(request)
    try: record={'request':original,'result':calculate_damage(request)}
    except Exception as error: record={'request':original,'error':{'type':type(error).__name__,'message':str(error)}}
    assert request==original
    records.append(record)
assert catalog()==public
assert sha(Path(sys.argv[1])/'rouge/damage.py')==source_before
result={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'package':sys.argv[1],
        'calls':len(records),'source_sha256':source_before,'source_drift':False,
        'caller_and_catalog_unchanged':True,'records':records}
Path(sys.argv[2]).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='records'}))
