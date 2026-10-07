"""Run independent enum/control cases on the requested external package."""
import copy
import hashlib
import json
import sys
from pathlib import Path

PACKAGE = Path(sys.argv[1]).resolve()
OUT = Path(sys.argv[2]).resolve()
sys.dont_write_bytecode = True
sys.path.insert(0, str(PACKAGE))
from rouge.damage import calculate_damage
from rouge.relics import context_value, mechanics

RID='rogue_6_relic_cargo_10'
OTHER='rogue_6_relic_legacy_2'
VALUES=[('absent',...),('null',None),('legal_zero','non_emergency'),('legal_one','emergency_hire'),
        ('unknown','unknown'),('short','emergency'),('empty',''),('padded',' emergency_hire'),
        ('upper','EMERGENCY_HIRE'),('true',True),('false',False),('zero',0),('one',1),
        ('zero_float',0.0),('one_float',1.0),('list',[]),('dict',{}),('nested',['emergency_hire'])]
OPERATORS=[('silverash',3),('mechanist',2),('mechanist',3),('char_002_amiya',1),
           ('char_1037_amiya3',2),('char_4087_ines',2),('char_298_susuro',2),('char_151_myrtle',2)]
groups=[('cargo_only',[RID]),('no_relic',[]),('other_only',[OTHER]),('cargo_plus_other',[RID,OTHER])]
mechanics_before=copy.deepcopy(mechanics())
rows=[]
for operator,skill in OPERATORS:
    for mode in ('frames','continuous'):
        for group,relics in groups:
            for label,value in VALUES:
                args={'operator':operator,'skill':skill,'base_attack':1000,
                      'enemy_defense':0,'enemy_resistance':0,'window_seconds':3,
                      'timing_mode':mode,'relic_ids':relics[:],
                      'relic_context':{'emergency_hire':1}}
                if value is not ...:args['recruitment_kind']=copy.deepcopy(value)
                before=copy.deepcopy(args)
                try: outcome={'accepted':True,'result':calculate_damage(args)}
                except Exception as error:
                    outcome={'accepted':False,'error_type':type(error).__name__,'error':str(error)}
                assert args==before, (operator,skill,mode,group,label,'input mutation')
                rows.append({'key':f'{operator}:{skill}:{mode}:{group}:{label}',
                             'group':group,'label':label,'input':before,'outcome':outcome})
assert mechanics()==mechanics_before, 'cached mechanics mutation'

# These Python-only sentinels prove exact built-in string treatment. They are not
# game identities or new enum values and are never passed to stored run state.
class StringSubclass(str): pass
class EqualityTrap:
    def __eq__(self,other): raise RuntimeError('recruitment identity equality must not be consulted')
sentinels=[('str_subclass_non',StringSubclass('non_emergency')),
           ('str_subclass_emergency',StringSubclass('emergency_hire')),
           ('bytes',b'emergency_hire'),('set',{'emergency_hire'}),('tuple',('emergency_hire',)),
           ('eq_trap',EqualityTrap())]
direct=[]
for label,value in sentinels:
    try: outcome={'accepted':True,'value':context_value({'condition':'emergency_hire'},{'recruitment_kind':value})}
    except Exception as error: outcome={'accepted':False,'error_type':type(error).__name__,'error':str(error)}
    direct.append({'label':label,'outcome':outcome})
files=['rouge/relics.py','rouge/damage.py','rouge/data/relic-mechanics.json']
receipt={'package':str(PACKAGE),'source_hashes':{p:hashlib.sha256((PACKAGE/p).read_bytes()).hexdigest() for p in files},
         'public_case_count':len(rows),'public_cases':rows,'direct_python_controls':direct,
         'public_input_unchanged':True,'cached_mechanics_unchanged':True,
         'private_state_read':False,'game_actions':0,'native_attachment_proven':False}
OUT.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'public_cases':len(rows),'direct_python_controls':len(direct),'package':str(PACKAGE),
                  'input_unchanged':True,'cached_mechanics_unchanged':True},ensure_ascii=False))
