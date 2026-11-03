"""Actual public-input counterexamples on the original promoted 285 candidate."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import sys
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from rouge import calibration as c

OUT=Path(__file__).resolve().parent/'original-scope-counterexamples'
OUT.mkdir(exist_ok=False)
PINS=['rouge/calibration.py','rouge/offline_tools_view.py','tests/test_extended_calibration_285.py',
      'rouge/animation_reference.py','rouge/timing.py','rouge/relics.py',
      'rouge/data/original-animation-references.json','rouge/data/native-static-action-bindings.json',
      'rouge/data/relic-mechanics.json']
before={rel:sha256((ROOT/rel).read_bytes()).hexdigest() for rel in PINS}
for rel in PINS:
    dest=OUT/'source'/rel;dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_bytes((ROOT/rel).read_bytes())
cases=[
 {'id':'skill_scoped_animation',
  'scenario':{'operator':'char_1037_amiya3','skill':2,
      'timing':{'animation_reference':'char_1037_amiya3:Front:Skill_2_Attack','target_windows':[[0,30]]}}},
 {'id':'medic_recipient_profession',
  'scenario':{'operator':'kaltsit','skill':2,'char_buff_ids':['rogue_6_from_relic_6']}},
 {'id':'snack_recipient_leaks_to_foreign_owner',
  'scenario':{'operator':'kaltsit','skill':2,'char_buff_ids':['rogue_6_from_relic_13']}},
]
records=[]
for case in cases:
    scenario=deepcopy(case['scenario']);record={'id':case['id'],'input':scenario}
    try:
        selected=c.calculate_damage(c._scenario(scenario,all_operators=True))
        record['selected_main']={'normal_return':True,'operator':selected['scenario']['operator'] if 'scenario' in selected else scenario['operator'],
            'estimate':selected['estimate']}
    except Exception as error:
        record['selected_main']={'normal_return':False,'error_type':type(error).__name__,'message':str(error)}
    calls=[];calculate=c.calculate_damage
    def capture(s):
        calls.append(deepcopy(s));return calculate(s)
    try:
        with patch.object(c,'calculate_damage',side_effect=capture):result=c.skill_matrix(scenario)
        record['matrix']={'normal_return':True,'result':result}
    except Exception as error:
        record['matrix']={'normal_return':False,'error_type':type(error).__name__,'message':str(error)}
    record['actual_matrix_inputs']=calls
    records.append(record)
after={rel:sha256((ROOT/rel).read_bytes()).hexdigest() for rel in PINS}
receipt={'kind':'ACTUAL_ORIGINAL_285_PUBLIC_COUNTEREXAMPLES_NOT_PASS',
    'source_before_sha256':before,'source_after_sha256':after,'sources_unchanged':before==after,
    'cases':records,'actual_script_exit_code':0,
    'scope':'Script completion is not application acceptance; caught matrix failures remain failures.'}
(OUT/'receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'sources_unchanged':before==after,'cases':[
    {'id':r['id'],'selected_main':r['selected_main']['normal_return'],'matrix':{k:v for k,v in r['matrix'].items() if k!='result'},
     'called_owner_and_buff':[(s['operator'],s['skill'],s.get('char_buff_ids')) for s in r['actual_matrix_inputs']]} for r in records]},ensure_ascii=False,indent=2))
