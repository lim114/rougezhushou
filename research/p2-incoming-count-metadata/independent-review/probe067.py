"""Bounded independent public metadata probes, using only pinned code snapshots."""
from pathlib import Path
from copy import deepcopy
import sys,json,hashlib,datetime
sys.path.insert(0,sys.argv[1])
from rouge.damage import calculate_damage
from rouge.catalog import catalog

OP='char_1042_phatm2'

def cases():
    for skill in (1,2,3):
        for mode in ('frames','continuous'):
            root={'operator':OP,'skill':skill,'base_attack':1000,'timing_mode':mode}
            extras=({}, {'window_seconds':0}, {'timing':{'target_disappears_seconds':0}},
                    {'timing':{'target_windows':[]}}, {'enemy_buildup_resistance':100})
            for i,extra in enumerate(extras):
                for label,count in (('int',20),('alias','2e1')):
                    yield f's{skill}:{mode}:scope{i}:{label}',{**root,**extra,'enemy_attack_count':count}
            for label,count in (('zero_int',0),('zero_alias','0.0')):
                yield f's{skill}:{mode}:{label}',{**root,'enemy_attack_count':count}
            for count in (False,True):
                yield f's{skill}:{mode}:bool{count}',{**root,'enemy_attack_count':count}
            if skill in (1,2):
                for label,count in (('int',1),('alias','1.0')):
                    yield f's{skill}:{mode}:e1:{label}',{**root,'elite':1,'level':80,'skill_rank':7,'enemy_attack_count':count}
    yield 'bait_error_first',{'operator':OP,'skill':2,'base_attack':1000,'bait_triggers':True,'enemy_attack_count':True}
    yield 'locked_s3_first',{'operator':OP,'skill':3,'elite':1,'skill_rank':7,'enemy_attack_count':True}
    for op,skill in (('mechanist',1),('silverash',3),('char_002_amiya',1),('char_2025_shu',3)):
        for mode in ('frames','continuous'):
            yield f'inactive:{op}:{mode}',{'operator':op,'skill':skill,'base_attack':1000,'timing_mode':mode,'enemy_attack_count':'1e0'}

rows={};before_catalog=deepcopy(catalog());path=Path(sys.argv[1])/'rouge/operator_engine.py'
source_hash=hashlib.sha256(path.read_bytes()).hexdigest()
for name,request in cases():
    original=deepcopy(request)
    try:out={'result':calculate_damage(request),'error':None}
    except Exception as error:out={'result':None,'error':{'type':type(error).__name__,'message':str(error)}}
    assert request==original
    rows[name]={'request':original,'outcome':out}
assert catalog()==before_catalog
assert hashlib.sha256(path.read_bytes()).hexdigest()==source_hash
data={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'package':sys.argv[1],
      'calls':len(rows),'source_sha256':source_hash,'source_drift':False,
      'caller_and_catalog_unchanged':True,'cases':rows}
Path(sys.argv[2]).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in data.items() if k!='cases'}))
