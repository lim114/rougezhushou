import copy,json,sys,math
from pathlib import Path
sys.path.insert(0,sys.argv[1])
from rouge.damage import calculate_damage
from rouge.estimate import format_estimate
from rouge.reporting import format_report
from rouge.catalog import catalog

out=Path(__file__).parent
if sys.argv[2]=='make-cases':
    cases=[]
    cultivation=[(0,1,7),(1,1,7),(2,49,10),(2,50,10),(2,80,10)]
    for mode in ('frames','continuous'):
        for skill in (1,2):
            for elite,level,rank in cultivation:
                for module in range(4):
                    for window in (None,0,.1,10):
                        for recipients in (0,1):
                            s={'operator':'char_1037_amiya3','skill':skill,'elite':elite,'level':level,'skill_rank':rank,
                               'base_attack':1000,'timing_mode':mode,'healing_targets':recipients}
                            if module:s.update(module_id='uniequip_002_amiya3',module_level=module)
                            if window is not None:s['window_seconds']=window
                            cases.append(s)
    for mode in ('frames','continuous'):
        for skill in (1,2):
            for stage in (1,2,3):
                for options in (
                    {'base_attack':0},{'healing_targets':100},{'enemy_resistance':100},
                    {'enemy_resistance':40,'effects':[{'kind':'damage_taken','damage_type':'magic','value':.3}]},
                    {'relic_ids':['rogue_6_relic_legacy_81']},
                    {'relic_ids':['rogue_6_relic_legacy_81','rogue_6_relic_legacy_82']},
                    {'timing':{'target_disappears_seconds':0}},
                    {'timing':{'target_windows':[]}},
                    {'timing':{'target_disappears_seconds':.1}},
                    {'timing':{'target_windows':[[0,.1]]}},
                    {'potential':6,'skill_rank':1},
                    {'effects':[{'kind':'attack_speed','value':100}]},
                    {'skill':2,'amiya_hit_targets':100},
                ):
                    cases.append({'operator':'char_1037_amiya3','skill':skill,'elite':2,'level':50,'skill_rank':10,
                                  'base_attack':1000,'timing_mode':mode,'module_id':'uniequip_002_amiya3','module_level':stage,
                                  'window_seconds':10,**options})
    for bad in ({'module_level':0},{'module_level':4},{'module_level':True},{'module_id':'uniequip_002_amiya2'},
                {'healing_targets':True},{'healing_targets':1.5},{'healing_targets':101},{'amiya_hit_targets':0},
                {'amiya_hit_targets':True},{'potential':0},{'level':0},{'skill_rank':True}):
        cases.append({'operator':'char_1037_amiya3','skill':2,'elite':2,'level':50,'skill_rank':10,
                      'base_attack':1000,'module_id':'uniequip_002_amiya3','module_level':1,**bad})
    for op in ('char_002_amiya','char_1001_amiya2','char_4202_haruka','char_298_susuro'):
        for mode in ('frames','continuous'):
            for skill in (1,2):
                cases.append({'operator':op,'skill':skill,'base_attack':1000,'timing_mode':mode,'window_seconds':10})
    unique={json.dumps(s,sort_keys=True,ensure_ascii=False):s for s in cases}
    (out/'public-cases80.json').write_text(json.dumps(list(unique.values()),ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'unique_cases':len(unique)}));sys.exit(0)

results=[]
original_catalog=copy.deepcopy(catalog())
for i,s in enumerate(json.loads((out/'public-cases80.json').read_text())):
    original=copy.deepcopy(s)
    try:
        r=calculate_damage(s)
        results.append({'index':i,'scenario':s,'result':r,'estimate_text':format_estimate(r),
                        'report_text':format_report(r),'technical_report_text':format_report(r,technical=True)})
    except (ValueError,TypeError) as exc:
        results.append({'index':i,'scenario':s,'error':{'type':type(exc).__name__,'message':str(exc)}})
    assert s==original,('input mutation',i)
assert catalog()==original_catalog,'catalog mutation'
path=out/f'public-{sys.argv[2]}80.json'
path.write_text(json.dumps(results,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
print(json.dumps({'cases':len(results),'accepted':sum('result' in x for x in results),'errors':sum('error' in x for x in results),'input_catalog_unchanged':True}))
