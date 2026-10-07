from copy import deepcopy
import hashlib
import itertools
import json
from pathlib import Path
import sys

sys.path.insert(0, sys.argv[1])
from rouge.catalog import catalog
from rouge.damage import calculate_damage


def cases():
    base={'operator':'char_133_mm','skill':1,'skill_rank':10,'elite':2,'level':40,
          'module_id':'uniequip_002_mm','module_level':1,'base_attack':1000,'window_seconds':10}
    for stage,skill,mode,potential in itertools.product((1,2,3),(1,2),('frames','continuous'),(1,6)):
        yield {**base,'module_level':stage,'skill':skill,'timing_mode':mode,'potential':potential,'enemy_defense':200}
    for stage,mode,edge in itertools.product((1,2,3),('frames','continuous'),
        ({'window_seconds':0},{'timing':{'target_disappears_seconds':0}},{'timing':{'target_windows':[]}})):
        yield {**base,'skill':2,'module_level':stage,'timing_mode':mode,**edge}
    for stage,mode,training in itertools.product((1,2,3),('frames','continuous'),
        ({'elite':1,'level':60,'skill_rank':7},{'elite':2,'level':39})):
        yield {**base,'module_level':stage,'timing_mode':mode,**training}
    for skill,mode in itertools.product((1,2),('frames','continuous')):
        yield {**base,'skill':skill,'timing_mode':mode,'module_id':None,'module_level':0}
    for mode,field in itertools.product(('frames','continuous'),
        ({'enemy_weight':0},{'enemy_name':'飞行目标'},{'enemy_is_airborne':True},{'enemy_is_airborne':'false'})):
        yield {**base,'timing_mode':mode,**field}
    for op,skill in (('char_328_cammou',1),('char_328_cammou',2),('mechanist',1),('char_2025_shu',2)):
        yield {'operator':op,'skill':skill,'window_seconds':10}
    for field in ({'module_level':True},{'module_level':4},{'elite':True},{'potential':True},
                  {'elite':1,'level':60},{'skill_rank':True},{'level':0},{'module_id':'foreign'},
                  {'skill':True},{'module_level':'1'}):
        yield {**base,**field}


snapshot=deepcopy(catalog())
rows=[]
for request in cases():
    original=deepcopy(request)
    try:
        result=calculate_damage(request)
        outcome={'result':json.loads(json.dumps(result,ensure_ascii=False,sort_keys=True))}
    except Exception as error:
        outcome={'error':{'type':type(error).__name__,'message':str(error)}}
    assert request==original
    rows.append({'scenario':original,'outcome':outcome})
assert catalog()==snapshot
out=Path(sys.argv[2])
out.write_text(json.dumps({'package':sys.argv[1],'calls':len(rows),'caller_and_catalog_unchanged':True,
                           'records':rows},ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'calls':len(rows),'successes':sum('result'in r['outcome']for r in rows),
                  'errors':sum('error'in r['outcome']for r in rows),'output_sha256':hashlib.sha256(out.read_bytes()).hexdigest()}))
