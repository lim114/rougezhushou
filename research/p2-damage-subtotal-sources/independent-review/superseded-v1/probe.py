"""Small independent public probes of reporting-source attribution."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys

PACKAGE=Path(sys.argv[1]).resolve()
OUT=Path(sys.argv[2]).resolve()
sys.dont_write_bytecode=True
sys.path.insert(0,str(PACKAGE))
from rouge.damage import calculate_damage
from rouge.estimate import format_estimate

VIN='char_1042_phatm2'; RIVER='rogue_6_relic_fight_22'
templates=[
    ('binding_only',{'operator':VIN,'skill':1}),
    ('incoming_only',{'operator':VIN,'skill':2,'enemy_attack_count':20}),
    ('binding_and_incoming',{'operator':VIN,'skill':1,'enemy_attack_count':20}),
    ('binding_and_river',{'operator':VIN,'skill':1,'relic_ids':[RIVER]}),
    ('binding_incoming_river',{'operator':VIN,'skill':1,'enemy_attack_count':20,'relic_ids':[RIVER]}),
    ('bait_only',{'operator':VIN,'skill':2,'bait_triggers':1}),
    ('bait_incoming_river',{'operator':VIN,'skill':2,'bait_triggers':1,'enemy_attack_count':20,'relic_ids':[RIVER]}),
    ('s3_only',{'operator':VIN,'skill':3}),
    ('s3_incoming_river',{'operator':VIN,'skill':3,'enemy_attack_count':20,'relic_ids':[RIVER]}),
    ('river_only',{'operator':VIN,'skill':2,'relic_ids':[RIVER],'initial_neural_buildup':999}),
    ('body_and_river',{'operator':'char_4204_mantra','skill':2,'relic_ids':[RIVER],'initial_neural_buildup':999,'window_seconds':1}),
    ('fallback_without_river',{'operator':'char_133_mm','skill':1}),
    ('shield_without_river',{'operator':'mechanist','skill':2,'shield_break_count':2}),
    ('healing_control',{'operator':'char_1037_amiya3','skill':2,'relic_ids':['rogue_6_relic_legacy_81']}),
    ('empty_enemy_scope',{'operator':VIN,'skill':1,'timing':{'target_windows':[]}}),
    ('zero_enemy_lifetime',{'operator':VIN,'skill':1,'timing':{'target_disappears_seconds':0}}),
    ('no_incoming_events',{'operator':VIN,'skill':2,'enemy_attack_count':0}),
    ('zero_observation',{'operator':VIN,'skill':1,'window_seconds':0}),
]
rows={}
for mode in ('frames','continuous'):
    for name,extra in templates:
        args={'base_attack':1000,'relic_ids':[],'timing_mode':mode,**deepcopy(extra)}
        before=deepcopy(args)
        result=calculate_damage(args)
        assert args==before,(name,mode,'input mutated')
        rows[f'{name}:{mode}']={'input':before,'result':result,'formatted':format_estimate(result)}
payload={'package':str(PACKAGE),'public_calls':len(rows),'cases':rows,'caller_inputs_preserved':True,
         'source_hashes':{name:hashlib.sha256((PACKAGE/name).read_bytes()).hexdigest() for name in
                          ('rouge/reporting.py','rouge/damage.py','rouge/elemental_relics.py')},
         'private_state_read':False,'game_actions':0,'native_execution_proven':False}
OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'public_calls':len(rows),'caller_inputs_preserved':True,'package':str(PACKAGE)},ensure_ascii=False))
