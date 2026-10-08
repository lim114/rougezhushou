import json
from pathlib import Path

OUT=Path(__file__).parent
rows=[];seen=set()
def typed(v):
    if v is None:return ['none']
    if isinstance(v,bool):return ['bool',v]
    if isinstance(v,int):return ['int',v]
    if isinstance(v,float):return ['float',repr(v)]
    if isinstance(v,str):return ['str',v]
    if isinstance(v,list):return ['list',[typed(x) for x in v]]
    if isinstance(v,dict):return ['dict',[[typed(k),typed(x)] for k,x in v.items()]]
    raise TypeError(type(v))
def add(label,extra=None,value=None,omit=False):
    s={'operator':'char_4202_haruka','skill':2,'elite':2,'level':70,'potential':1,
       'skill_rank':10,'base_attack':1000,'window_seconds':12,'timing_mode':'frames',**(extra or {})}
    if not omit:s['haruka_repeat']=value
    key=json.dumps(typed(s),ensure_ascii=False)
    if key in seen:return
    seen.add(key);rows.append({'label':label,'scenario':s})
for rank in range(1,11):
    for mode in ('frames','continuous'):
        for value in (False,True,'false'):
            add('s2-e1-unlocked-rank-parameter',{'elite':1 if rank<=7 else 2,'level':1,
                                             'skill_rank':rank,'timing_mode':mode},value)
for mode in ('frames','continuous'):
    add('absent-repeat',{'timing_mode':mode},omit=True)
    for value in (False,True,None,0,1,0.0,1.0,2,-1,[],{},[False],{'enabled':False},
                  '','false','False','0','true','1',' 未知 ','\t'):
        add('boolean-nontext-alias-and-literal-no-decoding',{'timing_mode':mode},value)
    for potential,level,stage in ((4,59,3),(5,59,3),(4,60,1),(5,60,2),(5,60,3)):
        for value in (False,True,'false'):
            add('existing-blsy-unknown-and-potential',{'potential':potential,'level':level,
                'module_id':'uniequip_002_haruka','module_level':stage,'timing_mode':mode,'healing_targets':3},value)
    for zero in ({'window_seconds':0},{'base_attack':0},{'healing_targets':0},
                  {'timing':{'target_disappears_seconds':0}},{'timing':{'target_windows':[]}},
                  {'bubble_bursts':2}):
        for value in (False,True,'false'):
            add('actual-read-despite-zero-or-unplaced-source',dict(zero,timing_mode=mode),value)
    for context in ({'relic_ids':['rogue_6_relic_legacy_97']},
                    {'relic_ids':['rogue_6_relic_legacy_105','rogue_6_relic_legacy_97']},
                    {'relic_ids':['rogue_6_relic_legacy_97'],
                     'timing':{'initial_target_windows':[[2,1]]}}):
        for value in (False,True,'false'):
            add('outer-deployment-wine-report-and-inactive-initial-field',dict(context,timing_mode=mode),value)
for operator,skill in (('char_4202_haruka',1),('char_4202_haruka',3),
                       ('char_298_susuro',2),('char_2025_shu',3),('mechanist',1)):
    for mode in ('frames','continuous'):
        add('inactive-skill-owner',{'operator':operator,'skill':skill,'timing_mode':mode},'false')
invalid=({'bubble_bursts':True},{'bubble_bursts':-1},{'bubble_bursts':10001},
         {'bubble_bursts':0.5},{'bubble_bursts':'unknown'},
         {'timing_mode':'unknown'},{'timing':[]},{'timing':{'target_windows':[[2,1]]}},
         {'timing':{'windup_frames':-1}},{'elite':0,'skill_rank':1},
         {'elite':1,'skill_rank':10},{'healing_targets':True},
         {'healing_targets':-1},{'module_id':'uniequip_002_haruka','module_level':4},
         {'operator':'char_4228_closur','skill':1,'closure_prior_casts':True})
for error in invalid:
    add('exact-old-error-priority',error,'false')
for error in ({'bubble_bursts':True},{'timing':{'target_windows':[[2,1]]}},
              {'bubble_bursts':'unknown'}):
    add('outer-deployment-wine-old-error-priority',dict(error,relic_ids=[
        'rogue_6_relic_legacy_105','rogue_6_relic_legacy_97']),'false')
(OUT/'public-cases84.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'passed':True,'unique_typed_cases':len(rows)}))
