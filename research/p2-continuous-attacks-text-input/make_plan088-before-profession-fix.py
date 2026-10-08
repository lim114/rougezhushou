from pathlib import Path
import copy,json,hashlib

OUT=Path(__file__).resolve().parent
BASE={'elite':2,'level':60,'skill_rank':10,'potential':4,'base_attack':1287,'window_seconds':12.5}
rows=[]
def add(label,op,skill,value,**extra):
    s={**BASE,'operator':op,'skill':skill,'continuous_attacks':copy.deepcopy(value),**extra}
    rows.append({'case':len(rows)+1,'label':label,'input':s})
for mode in ('frames','continuous'):
    for value in (False,True,'false',''):
        add('legacy Attack-SP '+mode,'mechanist',1,value,timing_mode=mode)
for module,mode in ((False,'frames'),(True,'frames'),(True,'continuous')):
    for value in ('false',''):
        add('extended actual normal/module '+mode,'char_4182_oblvns',3,value,timing_mode=mode,
            **({'module_id':'uniequip_002_oblvns','module_level':3} if module else {}))
for elite,level,rank in ((0,30,4),(1,40,7)):
    for value in ('false',''):
        add('restricted Amiya reference E'+str(elite),'char_002_amiya',1,value,
            elite=elite,level=level,skill_rank=rank,timing_mode='continuous',timing={'target_disappears_seconds':.75})
for value in (False,True,'false',''):
    add('natural next-attack event tail','char_196_sunbr',1,value,relic_ids=['rogue_6_relic_legacy_118'],
        timing={'sp_events':{'initial':[{'at_seconds':.5,'type':'damage'}],'cycle':[]}})
for mode in ('frames','continuous'):
    for value in (True,False,'false',''):
        add('inactive natural legacy '+mode,'silverash',3,value,timing_mode=mode)
for mode,values in (('frames',('false','')),('continuous',(False,True))):
    for value in values:
        add('natural hidden real Attack-SP source '+mode,'char_4087_ines',3,value,timing_mode=mode,
            relic_ids=['rogue_6_relic_legacy_67'])
for mode in ('frames','continuous'):
    for value in ('false',''):
        add('periodic/deployment attack '+mode,'mechanist',1,value,timing_mode=mode,relic_ids=['rogue_6_relic_legacy_97'])
for value in ('false',''):
    add('periodic incoming-only native defensive','char_1044_hsgma2',1,value,
        incoming_attack_interval=2,relic_ids=['rogue_6_relic_legacy_97'])
for mode in ('frames','continuous'):
    for value in ('false',''):
        add('event incoming-only natural '+mode,'mechanist',3,value,timing_mode=mode,
            relic_ids=['rogue_6_relic_legacy_118'],timing={'sp_events':{
                'initial':[{'at_seconds':.5,'type':'damage'}],
                'cycle':[{'at_seconds':45,'type':'damage'}]}})
for value in ('false',''):
    add('event positive outgoing Attack-SP','mechanist',1,value,relic_ids=['rogue_6_relic_legacy_118'],
        timing={'sp_events':{'initial':[],'cycle':[]}})
for value in (0,1,None,[],{},[1],{'yes':1},1.5):
    add('preserved non-string alias','mechanist',1,value,timing_mode='continuous')
for label,op,skill,extra in (
    ('old numeric error','mechanist',1,{'base_attack':-1}),
    ('old count error','mechanist',1,{'healing_targets':True}),
    ('old mastery error','mechanist',1,{'skill_rank':11}),
    ('old timing error','mechanist',1,{'timing':{'target_windows':'invalid'}}),
    ('old 83 guard priority','char_1042_phatm2',1,{'enemy_is_boss':'false'}),
    ('old 86 guard priority','char_4182_oblvns',3,{'ranged_attack':'false'}),
):add(label,op,skill,'false',**extra)
assert len(rows)==60,len(rows)
canonical=lambda x:json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'))
assert len({canonical(r['input']) for r in rows})==60
old=json.loads(Path('/workspace/.continuation/p2-section088-candidate-audit/continuous-public-plan16.json').read_text())
assert not {canonical(r['input']) for r in old}&{canonical(r['input']) for r in rows}
data=json.dumps(rows,ensure_ascii=False,indent=2)+'\n'
(OUT/'matrix-plan088.json').write_text(data)
print(json.dumps({'unique_pairs':60,'maximum_public_calls':120,'source16_exact_duplicates':0,'plan_sha256':hashlib.sha256(data.encode()).hexdigest()}))
