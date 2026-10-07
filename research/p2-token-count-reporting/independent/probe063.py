"""Independent real public calls on one fixed package; strict JSON retains numeric dtype."""
from contextlib import nullcontext
import copy
import hashlib
import json
import math
from pathlib import Path
import sys
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
PACKAGE = Path(sys.argv[1]).resolve()
OUT = Path(sys.argv[2]).resolve()
sys.dont_write_bytecode = True
sys.path.insert(0, str(PACKAGE))
from rouge.catalog import catalog
from rouge.damage import calculate_damage
from rouge.summons import module_rules

OP='char_110_deepcl'; TOKEN='token_10001_deepcl_tentac'; MOD='uniequip_002_deepcl'
def safe(v):
    if type(v) is float and not math.isfinite(v):
        return {'__nonfinite__': 'nan' if math.isnan(v) else ('inf' if v>0 else '-inf')}
    if isinstance(v,dict): return {k:safe(x) for k,x in v.items()}
    if isinstance(v,(tuple,list)): return [safe(x) for x in v]
    return v
def canon(v): return json.dumps(safe(v),ensure_ascii=False,sort_keys=True,separators=(',', ':'),allow_nan=False)
def digest(v):return hashlib.sha256(canon(v).encode()).hexdigest()
def hashes():
    return {p.relative_to(PACKAGE).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted((PACKAGE/'rouge').rglob('*')) if p.is_file() and p.suffix in ('.py','.json')}
def base(skill=1,mode='frames',**extra):
    return {'operator':OP,'skill':skill,'elite':2,'level':70,'module_id':MOD,'module_level':3,
            'window_seconds':10,'timing_mode':mode,**extra}

cases=[]
def add(label,args,group='preserved',equivalent=None,synthetic=False):
    cases.append({'id':label,'input':args,'group':group,'equivalent':equivalent,'synthetic':synthetic})
for mode in ('frames','continuous'):
    for skill in (1,2):
        tag=f'{skill}-{mode}'
        add('default-'+tag,base(skill,mode))
        for label,value in [('int0',0),('int1',1),('int2',2),('float0',0.0),('float1',1.0),('float2',2.0)]:
            add(label+'-'+tag,base(skill,mode,summon_count=value))
        for label,value,n in [('text0','0.0',0),('text1','1e0',1),('text2','2.0',2)]:
            add(label+'-'+tag,base(skill,mode,summon_count=value),'legal_text', 'int'+str(n)+'-'+tag)
        for label,value in [('bool0',False),('bool1',True),('fraction','0.5'),('negative','-1'),
                            ('overcap','8'),('nan','nan'),('none',None),('list',[]),('dict',{})]:
            add('invalid-'+label+'-'+tag,base(skill,mode,summon_count=value),'invalid')
    training=[('E0',1,dict(elite=0,level=45,skill_rank=4,module_id=None,module_level=0),2),
              ('E1',2,dict(elite=1,level=60,skill_rank=7),3),
              ('E2locked',1,dict(level=39),4),('E2open',2,dict(level=40),7)]
    for name,skill,fields,cap in training:
        tag=name+'-'+mode
        add('cap-int-'+tag,base(skill,mode,summon_count=cap,**fields))
        add('cap-text-'+tag,base(skill,mode,summon_count=str(cap)+'.0',**fields),'legal_text','cap-int-'+tag)
        add('cap-invalid-'+tag,base(skill,mode,summon_count=str(cap+1),**fields),'invalid')
    for op in ('mechanist','char_151_myrtle'):
        args={'operator':op,'skill':1,'window_seconds':10,'timing_mode':mode}
        tag=op+'-'+mode
        add('inactive-default-'+tag,args)
        for label,value in [('bool',True),('text','1.0'),('nan',float('nan'))]:
            add('inactive-'+label+'-'+tag,{**args,'summon_count':value},'inactive','inactive-default-'+tag)
    for obs,fields in [('zero',{'window_seconds':0}),('noenemy',{'timing':{'target_windows':[]}})]:
        tag=obs+'-'+mode
        add('obs-int-'+tag,base(mode=mode,summon_count=2,**fields))
        add('obs-text-'+tag,base(mode=mode,summon_count='2.0',**fields),'legal_text','obs-int-'+tag)
    for skill in (1,2):
        for stage in (1,2,3):
            tag=f'hp-{skill}-{stage}-{mode}'
            args=base(skill,mode,module_level=stage,relic_ids=['rogue_6_relic_legacy_91'],
                effects=[{'kind':'hp_pct','value':.5,'target_scope':'all_units'}])
            add('int-'+tag,{**args,'summon_count':2},synthetic=True)
            add('text-'+tag,{**args,'summon_count':'2.0'},'legal_text','int-'+tag,synthetic=True)

before=hashes(); cached_catalog=digest(catalog()); cached_rules=digest(module_rules())
rows=[]
for case in cases:
    args=copy.deepcopy(case['input']); incoming=canon(args)
    rules=copy.deepcopy(module_rules()); rules[MOD]['hp_composition_verified']=False
    fixture=patch('rouge.summons.module_rules',return_value=rules) if case['synthetic'] else nullcontext()
    row={k:safe(v) for k,v in case.items()}
    with fixture:
        try:
            value=calculate_damage(args); row['outcome']={'status':'returned','result':safe(value)}
        except Exception as err:
            row['outcome']={'status':'raised','exception':{'type':type(err).__name__,'message':str(err)}}
    assert canon(args)==incoming,case['id']
    rows.append(row)
after=hashes()
assert before==after
assert cached_catalog==digest(catalog()) and cached_rules==digest(module_rules())
receipt={'scope':'Independent real public calculate_damage calls on fixed post61 package; no mocked report',
    'package':str(PACKAGE),'strict_json_numeric_dtype':True,'source_before':before,'source_after':after,
    'source_drift':[],'caller_and_catalog_and_module_rules_unchanged':True,'calls':len(rows),
    'synthetic_hp_fixture':'Existing unknown-composition guard only, not a native module finding',
    'Wine_executed':False,'GUI_executed':False,'records':rows}
OUT.write_text(json.dumps(receipt,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
print(json.dumps({'calls':len(rows),'returned':sum(r['outcome']['status']=='returned' for r in rows),
                  'raised':sum(r['outcome']['status']=='raised' for r in rows),'source_drift':[]}))
