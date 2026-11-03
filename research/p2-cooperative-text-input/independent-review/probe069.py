from pathlib import Path
from copy import deepcopy
import sys,json,hashlib,datetime
sys.path.insert(0,sys.argv[1])
from rouge.damage import calculate_damage
from rouge.catalog import catalog

def cases():
    for mode in ('frames','continuous'):
        for value in ('false','0','',False,True,None,0,1,0.0,1.0):
            yield {'operator':'silverash','skill':3,'base_attack':1000,'window_seconds':10,'timing_mode':mode,'cooperative':value}
        for rank in (1,4,7):
            for flag in (False,True):
                yield {'operator':'silverash','skill':3,'base_attack':1000,'window_seconds':10,'timing_mode':mode,
                       'skill_rank':rank,'cooperative':flag,'preexisting_fragile':True,
                       'effects':[{'kind':'damage_taken','damage_type':'physical','value':.5}]}
        for scope in ({'window_seconds':0},{'timing':{'target_disappears_seconds':0}},{'timing':{'target_windows':[]}}):
            for flag in ('false',False,True):
                yield {'operator':'silverash','skill':3,'base_attack':1000,'timing_mode':mode,'cooperative':flag,**scope}
        yield {'operator':'silverash','skill':3,'timing_mode':mode}
        yield {'operator':'silverash','skill':3,'timing_mode':mode,'preexisting_fragile':'false','cooperative':'false'}
        for elite in (0,1):
            yield {'operator':'silverash','skill':3,'skill_rank':7,'elite':elite,'timing_mode':mode,'preexisting_fragile':'false','cooperative':'false'}
        for op,skill in (('silverash',1),('silverash',2),('mechanist',1),('char_2025_shu',2)):
            yield {'operator':op,'skill':skill,'timing_mode':mode,'cooperative':'false'}
    for invalid in ({'skill':True},{'skill_rank':True},{'level':0},{'potential':0}):
        yield {'operator':'silverash','skill':3,'cooperative':'false',**invalid}

source=Path(sys.argv[1])/'rouge/damage.py';h=hashlib.sha256(source.read_bytes()).hexdigest();cached=deepcopy(catalog());rows=[]
for request in cases():
    original=deepcopy(request)
    try:out={'result':calculate_damage(request),'error':None}
    except Exception as error:out={'result':None,'error':{'type':type(error).__name__,'message':str(error)}}
    assert request==original
    rows.append({'request':original,'outcome':out})
assert catalog()==cached and hashlib.sha256(source.read_bytes()).hexdigest()==h
result={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'package':sys.argv[1],'source_sha256':h,
        'calls':len(rows),'source_drift':False,'caller_and_catalog_unchanged':True,'records':rows}
Path(sys.argv[2]).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='records'}))
