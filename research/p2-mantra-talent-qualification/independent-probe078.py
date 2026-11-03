"""Independent compact public before/after cases; no GUI or Wine execution."""
import copy,hashlib,json,sys
from pathlib import Path
P=Path(__file__).resolve().parent
package=Path(sys.argv[1]);output=Path(sys.argv[2]);sys.path.insert(0,str(package))
from rouge.catalog import catalog
from rouge.damage import calculate_damage
from rouge.reporting import format_report
rows=[]
def add(label,**extra):
    rows.append({'label':label,'request':{'operator':'char_4204_mantra','skill':1,'skill_rank':1,
      'elite':0,'level':1,'base_attack':1000,'window_seconds':10,**extra}})
contexts=({}, {'window_seconds':0}, {'timing':{'target_disappears_seconds':0}},
          {'timing':{'target_windows':[]}}, {'initial_neural_buildup':999},
          {'enemy_in_neural_break':True,'relic_ids':['rogue_6_relic_fight_22']})
for mode in ('frames','continuous'):
    for context in contexts:
        for count in (0,1):add('locked_with_identical_zero_control',timing_mode=mode,palsy_triggers=count,**context)
    for elite in (1,2):
        for potential in (1,5):
            for count in (0,1):add('qualified_source_candidates',timing_mode=mode,elite=elite,potential=potential,palsy_triggers=count)
        for condition in ({'base_attack':0},{'enemy_elemental_resistance':100}):
            add('qualified_zero_damage_stays_unknown',timing_mode=mode,elite=elite,palsy_triggers=1,**condition)
    add('qualified_S2',timing_mode=mode,elite=1,skill=2,palsy_triggers=1)
    add('qualified_S2_module',timing_mode=mode,elite=2,level=60,skill=2,palsy_triggers=1,
        module_id='uniequip_002_mantra',module_level=3)
    for overflow in (0,2):
        for count in (0,1):add('independent_S3_overflow',timing_mode=mode,elite=2,skill=3,
            palsy_overflow_hits=overflow,palsy_triggers=count)
for count in (1.0,'1','1.0','1e0',10000):
    add('raw_positive_alias_and_gui_max',timing_mode='frames',palsy_triggers=count)
for count in (0.0,'0','0.0'):
    add('raw_zero_alias',timing_mode='frames',palsy_triggers=count)
for count in (True,False,-1,.5,10001,None):
    add('raw_count_error',palsy_triggers=count)
for extra in ({'skill':2},{'skill':3},{'skill_rank':10},{'level':0},
              {'module_id':'uniequip_002_mm','module_level':1},
              {'timing':{'target_disappears_seconds':-1}}):
    add('prior_qualification_module_timing_error_precedence',palsy_triggers=True,**extra)
for owner,skill in (('silverash',3),('char_133_mm',2)):
    add('inactive_other_owner',operator=owner,skill=skill,elite=2,palsy_triggers=False,palsy_overflow_hits='unused')
original=json.dumps(catalog(),ensure_ascii=False,sort_keys=True)
records=[]
for row in rows:
    caller=copy.deepcopy(row['request'])
    try:
        result=calculate_damage(row['request'])
        value={**row,'result':result,'human_report':format_report(result)}
    except Exception as exc:value={**row,'error':{'type':type(exc).__name__,'message':str(exc)}}
    assert caller==row['request'];records.append(value)
assert original==json.dumps(catalog(),ensure_ascii=False,sort_keys=True)
output.write_text(json.dumps({'scope':'Fresh independent public API only','package':str(package),
  'public_calls':len(records),'caller_and_cache_preserved':True,'records':records},ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'scenarios':len(records),'successes':sum('result'in r for r in records),
 'errors':sum('error'in r for r in records),'sha256':hashlib.sha256(output.read_bytes()).hexdigest()}))
