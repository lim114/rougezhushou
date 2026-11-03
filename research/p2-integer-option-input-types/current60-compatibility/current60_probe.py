"""Small full-output probes on fixed HEAD60 before/after external final61."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys

PACKAGE=Path(sys.argv[1]).resolve();OUT=Path(sys.argv[2]).resolve()
sys.dont_write_bytecode=True
sys.path.insert(0,str(PACKAGE))
from rouge.damage import calculate_damage
from rouge.estimate import format_estimate

rows={};RIVER='rogue_6_relic_fight_22';CARGO='rogue_6_relic_cargo_10'
templates={
 '59_binding_only':{'operator':'char_1042_phatm2','skill':1,'relic_ids':[]},
 '59_binding_incoming':{'operator':'char_1042_phatm2','skill':1,'enemy_attack_count':20,'relic_ids':[]},
 '59_binding_incoming_river':{'operator':'char_1042_phatm2','skill':1,'enemy_attack_count':20,'relic_ids':[RIVER]},
 '59_shield_held_river_no_reference':{'operator':'mechanist','skill':2,'shield_break_count':2,'relic_ids':[RIVER]},
 '58_pending_unknown':{'operator':'silverash','skill':3,'relic_ids':[CARGO],'recruitment_kind':'unknown'},
 '58_pending_null':{'operator':'silverash','skill':3,'relic_ids':[CARGO],'recruitment_kind':None},
 '58_pending_wrong_type':{'operator':'silverash','skill':3,'relic_ids':[CARGO],'recruitment_kind':True},
 '58_known_positive':{'operator':'silverash','skill':3,'relic_ids':[CARGO],'recruitment_kind':'emergency_hire'},
 '58_known_zero':{'operator':'silverash','skill':3,'relic_ids':[CARGO],'recruitment_kind':'non_emergency'},
}
for elite in (1,2):
    for skill in (1,2) if elite==1 else (1,2,3):
        for four in (False,True):
            for observation in (0,10):
                key=f'60_shu_elite{elite}_skill{skill}_four{int(four)}_window{observation}'
                templates[key]={'operator':'char_2025_shu','skill':skill,'elite':elite,'level':50,
                    'skill_rank':7 if elite==1 else 10,'four_sui':four,'three_professions':True,
                    'three_same_profession':True,'window_seconds':observation,'relic_ids':[]}
for mode in ('frames','continuous'):
    for name,extra in templates.items():
        args={'base_attack':1000,'window_seconds':10,'timing_mode':mode,**deepcopy(extra)}
        original=deepcopy(args)
        result=calculate_damage(args)
        assert args==original
        rows[name+':'+mode]={'input':original,'result':result,'formatted':format_estimate(result)}
payload={'fixed_source_head':'c3ccf25d59144227dd0f8f5ca9ef6c8bf81ad8cf','package':str(PACKAGE),
    'public_cases':rows,'public_calls':len(rows),'caller_inputs_preserved':True,
    'operator_engine_sha256':hashlib.sha256((PACKAGE/'rouge/operator_engine.py').read_bytes()).hexdigest(),
    'private_state_read':False,'Wine_run':False,'actual_GUI_run':False,'native_Windows_run':False}
OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'public_calls':len(rows),'package':str(PACKAGE)},ensure_ascii=False))
