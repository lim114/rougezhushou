"""Small independent public boundary matrix, no GUI/Wine/private state."""
import copy,hashlib,json,sys
from pathlib import Path

P=Path(__file__).resolve().parent
package=Path(sys.argv[1]); output=Path(sys.argv[2])
sys.path.insert(0,str(package))
from rouge.damage import calculate_damage
from rouge.reporting import format_report
from rouge.catalog import catalog

rows=[]
def add(label,**extra):
    rows.append({'label':label,'request':{'operator':'char_1015_aglna2','skill':1,'skill_rank':1,
                'elite':0,'level':1,'base_attack':1000,'window_seconds':10,**extra}})
for mode in ('frames','continuous'):
    for potential in (1,3):
        for weight in (0,3,4,100):
            add('locked_E0_weight_potential',timing_mode=mode,potential=potential,enemy_weight=weight)
    for extra in ({'window_seconds':0},{'timing':{'target_disappears_seconds':0}},
                  {'timing':{'target_windows':[]}},{'base_attack':0},
                  {'relic_ids':['rogue_6_relic_fight_5']},
                  {'effects':[{'kind':'sp_recovery','value':.2}],
                   'target_enemy':{'stage_id':'ro6_n_1_1','enemy_id':'enemy_2133_shdopl','level':0},
                   'run_config':{'difficulty':{'value':4}},'enemy_weight':100}):
        add('locked_E0_empty_resource_or_retired_reference',timing_mode=mode,**extra)
    for elite in (1,2):
        for potential in (1,3):
            for weight in (3,4):
                add('qualified_E1_E2',timing_mode=mode,elite=elite,potential=potential,enemy_weight=weight)
        add('qualified_zero_attack',timing_mode=mode,elite=elite,base_attack=0)
    add('qualified_S2_natural_sp',timing_mode=mode,elite=1,skill=2,
        effects=[{'kind':'sp_recovery','value':.2}])
    add('qualified_S3_unknown_target_clock',timing_mode=mode,elite=2,skill=3)
for raw in (True,'4',None,-1,101,3.5):
    add('prior_weight_errors',enemy_weight=raw)
for extra in ({'skill':2,'enemy_weight':True},{'skill':3,'enemy_weight':True},
              {'skill_rank':10,'enemy_weight':True},{'level':0,'enemy_weight':True},
              {'module_id':'uniequip_002_mm','module_level':1},
              {'timing':{'target_disappears_seconds':-1}}):
    add('prior_qualification_module_timing_error_order',**extra)
for owner in ('char_133_mm','char_1029_yato2'):
    add('other_owner_control',operator=owner,elite=2)
cached=json.dumps(catalog(),ensure_ascii=False,sort_keys=True)
results=[]
for row in rows:
    request=row['request']; caller=copy.deepcopy(request)
    try:
        result=calculate_damage(request)
        value={**row,'result':result,'human_report':format_report(result)}
    except Exception as exc:
        value={**row,'error':{'type':type(exc).__name__,'message':str(exc)}}
    assert request==caller
    results.append(value)
assert json.dumps(catalog(),ensure_ascii=False,sort_keys=True)==cached
output.write_text(json.dumps({'scope':'Independent fresh public calls only','package':str(package),
                  'public_calls':len(results),'caller_and_cache_preserved':True,'records':results},
                 ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'scenarios':len(results),'successes':sum('result' in r for r in results),
                  'errors':sum('error' in r for r in results),'sha256':hashlib.sha256(output.read_bytes()).hexdigest()}))
