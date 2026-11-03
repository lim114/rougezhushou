import copy
import hashlib
import json
import sys
from pathlib import Path

OUT=Path(__file__).parent
source=Path(sys.argv[1]).resolve()
destination=Path(sys.argv[2]).resolve()
sys.path.insert(0,str(source))
from rouge.catalog import catalog
from rouge.damage import calculate_damage
from rouge.estimate import format_estimate
from rouge.reporting import format_report
from rouge.operator_engine import selected_talents

def typed(value):
    if value is None:return ['none']
    if isinstance(value,bool):return ['bool',value]
    if isinstance(value,int):return ['int',value]
    if isinstance(value,float):return ['float',repr(value)]
    if isinstance(value,str):return ['str',value]
    if isinstance(value,list):return ['list',[typed(v) for v in value]]
    if isinstance(value,tuple):return ['tuple',[typed(v) for v in value]]
    if isinstance(value,dict):return ['dict',[[typed(k),typed(v)] for k,v in value.items()]]
    raise TypeError(type(value))

FIELD='low_cost_healing_target'
rows=[]
seen=set()
def add(label,extra=None,value=None,omit=False):
    scenario={'operator':'char_298_susuro','skill':1,'elite':2,'level':70,
              'potential':1,'skill_rank':10,'base_attack':1000,
              'window_seconds':12,'timing_mode':'frames',**(extra or {})}
    if not omit:scenario[FIELD]=value
    key=json.dumps(typed(scenario),ensure_ascii=False,separators=(',',':'))
    if key in seen:return
    seen.add(key)
    rows.append({'label':label,'scenario':scenario})

states=({'elite':1,'level':1,'potential':1,'skill_rank':1},
        {'elite':1,'level':60,'potential':4,'skill_rank':7},
        {'elite':1,'level':60,'potential':5,'skill_rank':7},
        {'elite':2,'level':1,'potential':1,'skill_rank':7},
        {'elite':2,'level':70,'potential':4,'skill_rank':10},
        {'elite':2,'level':70,'potential':5,'skill_rank':10})
for state in states:
    for skill in (1,2):
        for mode in ('frames','continuous'):
            for value in (False,True,'false',''):
                add('cultivation-potential-skill',dict(state,skill=skill,timing_mode=mode),value)
for potential,level,stage in ((4,39,3),(5,39,3),(4,40,1),(5,40,1),
                              (4,40,2),(5,40,2),(4,40,3),(5,40,3)):
    for mode in ('frames','continuous'):
        for value in (False,True,'false'):
            add('qualified-module-boundary',{'potential':potential,'level':level,'module_id':'uniequip_002_susuro',
                                            'module_level':stage,'timing_mode':mode},value)
for skill in (1,2):
    for mode in ('frames','continuous'):
        context={'skill':skill,'timing_mode':mode}
        add('absent-condition',context,omit=True)
        for value in (False,True,None,0,1,0.0,1.0,2,-1,[],{},[False],{'enabled':False}):
            add('preserved-nontext',context,value)
        for value in ('false','False','0','true','1',' 未知 ','\t',''):
            add('literal-text-no-decoding',context,value)
        for condition in ({'window_seconds':0},{'base_attack':0},{'healing_targets':0},
                          {'timing':{'target_disappears_seconds':0}},
                          {'timing':{'target_windows':[]}}):
            for value in (False,True,'false'):
                add('zero-observation-still-qualified',dict(context,**condition),value)
        for relics in (['rogue_6_relic_legacy_81'],
                       ['rogue_6_relic_legacy_81','rogue_6_relic_legacy_82'],
                       ['rogue_6_relic_legacy_81','rogue_6_relic_legacy_81']):
            for value in (False,True,'false'):
                add('existing-relic-resolution',dict(context,relic_ids=relics),value)
for mode in ('frames','continuous'):
    for value in (False,True,'','false','False','0','true','1',' 未知 ','\t'):
        add('unselected-e0-talent',{'elite':0,'level':1,'skill_rank':1,'timing_mode':mode},value)
for operator,skill in (('char_196_sunbr',1),('char_2025_shu',3),('kaltsit',1),
                       ('char_110_deepcl',1),('char_002_amiya',2),('char_1037_amiya3',1)):
    for mode in ('frames','continuous'):
        for value in ('','false',True):
            add('inactive-other-owner',{'operator':operator,'skill':skill,'level':50,'timing_mode':mode},value)
invalid=({'skill':2,'elite':0,'skill_rank':1},{'elite':1,'skill_rank':10},
         {'elite':True},{'skill':True},{'skill_rank':0},{'potential':7},
         {'healing_targets':True},{'healing_targets':-1},
         {'skill':2,'casts_used':True},{'skill':2,'casts_used':2},
         {'skill':2,'casts_used':3},{'timing_mode':'unknown'},
         {'timing':[]},{'timing':{'target_windows':[[2,1]]}},{'window_seconds':-1},
         {'module_id':'uniequip_002_susuro','module_level':0},
         {'module_id':'uniequip_002_susuro','module_level':4},
         {'module_id':'uniequip_002_amiya','module_level':1})
for changes in invalid:
    for value in (False,'false'):
        add('existing-validation-priority',changes,value)
for mode in ('frames','continuous'):
    for value in (False,True,'false'):
        add('s2-last-cast-reference',{'skill':2,'timing_mode':mode,'casts_used':1},value)

cached=copy.deepcopy(catalog())
for row in rows:
    args=row['scenario']
    before=copy.deepcopy(args)
    try:
        result=calculate_damage(args)
        row.update(result=result,typed_result=typed(result),estimate_text=format_estimate(result),
                   report_text=format_report(result),technical_report_text=format_report(result,technical=True))
        selected,parts=selected_talents(catalog()['operators'][args['operator']],args)
        row['actual_source_selection']={'selected_talents':selected,'module_parts':parts}
    except (ValueError,TypeError) as exc:
        row['error']={'type':type(exc).__name__,'message':str(exc)}
    assert typed(args)==typed(before)
assert typed(catalog())==typed(cached)
data=(json.dumps(rows,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode()
with destination.open('xb') as f:f.write(data)
receipt={'passed':True,'baseline_commit':'c950fbc800245f7f784d6070f7126890352ffcc9',
         'source_tree':str(source),'file':str(destination),'sha256':hashlib.sha256(data).hexdigest(),
         'bytes':len(data),'calculate_damage_calls':len(rows),'successes':sum('result' in r for r in rows),
         'errors':sum('error' in r for r in rows),'typed_result_saved_before_json_encoding':True,
         'three_actual_reports_saved':True,'caller_and_catalog_unchanged':True,'python_hash_seed':'0',
         'gui_executed':False,'wine_executed':False}
destination.with_suffix('.receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(receipt,ensure_ascii=False))
