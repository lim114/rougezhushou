from copy import deepcopy
import hashlib
import itertools
import json
from pathlib import Path
import sys

P=Path(__file__).parent
sys.path.insert(0,str(P/sys.argv[1]))
from rouge.battle_preview import battle_data,enemy_preview,enemy_text
from rouge.catalog import catalog
from rouge.damage import calculate_damage
from rouge.run_config import config_data


def canonical(value):return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'))


def cases():
    stages=battle_data()['stages']
    for sid,enemy,context in itertools.product(('ro6_e_3_6','ro6_n_3_6'),stages['ro6_e_3_6']['enemies'][:3],
             (None,{'difficulty':{'value':0}},{'difficulty':{'value':15},'zone':{'id':'zone_3'}},['bad'])):
        yield 'enemy_preview',{'stage_id':sid,'enemy_id':enemy['id'],'level':enemy['level'],'run_config':context}
    for sid in ('ro6_n_1_2','ro6_e_4_1'):
        enemy=stages[sid]['enemies'][0]
        yield 'enemy_preview',{'stage_id':sid,'enemy_id':enemy['id'],'level':enemy['level']}
    for skill,mode,horizon,flag in itertools.product((1,2,3),('frames','continuous'),(0,10),(False,True)):
        yield 'calculate_damage',{'operator':'char_2025_shu','skill':skill,'four_sui':flag,'timing_mode':mode,
            'window_seconds':horizon,'effects':[{'kind':'sp_recovery','value':.2}],
            'target_enemy':{'stage_id':'ro6_e_3_6','enemy_id':'enemy_10107_mjcdog_2','level':0},
            'run_config':{'difficulty':{'value':4}}}
    for op,mode,sid in itertools.product(('mechanist','char_133_mm'),('frames','continuous'),('ro6_n_3_6','ro6_e_3_6')):
        yield 'calculate_damage',{'operator':op,'skill':1,'timing_mode':mode,'window_seconds':10,
            'target_enemy':{'stage_id':sid,'enemy_id':'enemy_10107_mjcdog_2','level':0}}
    for sid,enemy,level in (('missing','missing',0),('ro6_e_3_6','missing',0),('ro6_e_3_6','enemy_10107_mjcdog_2',999),('ro6_n_3_6','enemy_10107_mjcdog_2',999)):
        yield 'enemy_preview',{'stage_id':sid,'enemy_id':enemy,'level':level}
    for fields in ({'elite':0,'skill':2},{'skill':True},{'effects':[{'kind':'sp_per_second','value':.2}]}):
        yield 'calculate_damage',{'operator':'char_2025_shu','skill':2,'four_sui':True,
            'target_enemy':{'stage_id':'ro6_e_3_6','enemy_id':'enemy_10107_mjcdog_2','level':0},**fields}


snapshot=[canonical(battle_data()),canonical(catalog()),canonical(config_data())]
records=[]
for api,request in cases():
    original=deepcopy(request)
    row={'api':api,'request':original}
    try:
        if api=='enemy_preview':
            preview=enemy_preview(request['stage_id'],request['enemy_id'],request['level'],request.get('run_config'))
            result={'preview':preview,'default_text':enemy_text(preview),'technical_text':enemy_text(preview,technical=True)}
        else:result=calculate_damage(request)
        result=json.loads(canonical(result));row['full_result']=result
        row['full_result_sha256']=hashlib.sha256(canonical(result).encode()).hexdigest()
    except Exception as error:row['error']={'type':type(error).__name__,'message':str(error)}
    assert request==original;records.append(row)
assert snapshot==[canonical(battle_data()),canonical(catalog()),canonical(config_data())]
out=P/sys.argv[2]
out.write_text(json.dumps({'calls':len(records),'records':records,'caller_and_caches_unchanged':True},ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'calls':len(records),'successes':sum('full_result'in r for r in records),'errors':sum('error'in r for r in records),'output_sha256':hashlib.sha256(out.read_bytes()).hexdigest()}))
