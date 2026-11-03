"""Small actual public API probes of the final integer-query guard."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
AUTHOR=Path('/workspace/.continuation/p2-integer-option-audit-061')
PACKAGE=Path(sys.argv[1]).resolve()
OUTPUT=Path(sys.argv[2]).resolve()
sys.dont_write_bytecode=True
sys.path.insert(0,str(PACKAGE))
from rouge.catalog import catalog
from rouge.damage import calculate_damage
from rouge.relics import mechanics

rows={};templates=[]
def add(label,operator,skill,extra,expect_change=False):
    templates.append((label,operator,skill,extra,expect_change))
for label,value in [('false',False),('true',True),('zero',0),('one',1),('one_float',1.0),('one_string','1')]:
    add('summon_'+label,'char_110_deepcl',1,{'summon_count':value},type(value)is bool)
for label,value in [('false',False),('true',True),('string_float','1.0'),('one',1)]:
    add('bubble_'+label,'char_4202_haruka',1,{'bubble_bursts':value},type(value)is bool)
for label,value in [('false',False),('true',True),('two',2)]:
    add('cold_'+label,'char_206_gnosis',2,{'cold_state':value},type(value)is bool)
for label,value in [('false',False),('true',True)]:
    add('ghost_casts_active_'+label,'char_1035_wisdel',1,{'ghost_count':1,'ghost_casts':value},True)
    add('ghost_casts_unqueried_'+label,'char_1035_wisdel',1,{'ghost_count':0,'ghost_casts':value})
    add('healing_inactive_'+label,'silverash',3,{'healing_targets':value})
    add('healing_active_existing_error_'+label,'char_151_myrtle',2,{'healing_targets':value})
    add('noninteger_hp_'+label,'char_1044_hsgma2',1,{'current_hp_ratio':value})
    add('noninteger_initial_buildup_'+label,'char_1042_phatm2',1,{'initial_neural_buildup':value})
    add('checkbox_low_cost_'+label,'char_298_susuro',2,{'low_cost_healing_target':value})
    add('checkbox_frozen_end_'+label,'char_206_gnosis',3,{'frozen_at_skill_end':value})
    add('old_enemy_weight_error_'+label,'char_1015_aglna2',2,{'enemy_weight':value})
    add('inactive_bait_wrong_skill_'+label,'char_1042_phatm2',1,{'bait_triggers':value})
    add('inactive_levitate_wrong_skill_'+label,'char_4202_haruka',2,{'levitate_triggers':value})
    add('inactive_trap_dot_wrong_skill_'+label,'char_2027_wang',2,{'trap_dot_ticks':value})
    add('inactive_casts_wrong_skill_'+label,'char_298_susuro',1,{'casts_used':value})
    add('inactive_summon_other_owner_'+label,'silverash',3,{'summon_count':value})
    add('legacy_charge_inactive_'+label,'mechanist',1,{'charge_count':value})
add('default_without_count','char_4202_haruka',1,{})
add('empty_window_bool','char_4202_haruka',1,{'window_seconds':0,'bubble_bursts':False},True)
add('empty_enemy_bool','char_4202_haruka',1,{'timing':{'target_disappears_seconds':0},'bubble_bursts':True},True)
add('ghost_count_bool','char_1035_wisdel',1,{'ghost_count':False},True)
source_catalog=deepcopy(catalog());source_mechanics=deepcopy(mechanics())
for mode in ('frames','continuous'):
    for label,operator,skill,extra,expect_change in templates:
        args={'operator':operator,'skill':skill,'base_attack':1000,'timing_mode':mode,'window_seconds':10,**deepcopy(extra)}
        before=deepcopy(args)
        try:outcome={'accepted':True,'result':calculate_damage(args)}
        except Exception as error:outcome={'accepted':False,'error_type':type(error).__name__,'error':str(error)}
        assert args==before,label
        rows[label+':'+mode]={'input':before,'outcome':outcome,'new_bool_error_expected':expect_change}
assert catalog()==source_catalog and mechanics()==source_mechanics

# One preserved failed-comparator case independently exposes runtime tuple vs
# saved JSON list shape while retaining exactly the same serialized public value.
original=json.loads((AUTHOR/'baseline-public-results.json').read_text())['complete_public_cases']
failed=json.loads((AUTHOR/'matrix-comparison-v1-preparation-failure.json').read_text())['failures']
index=failed[0]['index'];saved=original[index]
args=deepcopy(saved['scenario'])
try:raw={'accepted':True,'result':calculate_damage(args)}
except Exception as error:raw={'accepted':False,'error_type':type(error).__name__,'error':str(error)}
canonical=lambda value:json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':'))
assert canonical(raw)==canonical(saved['outcome'])
differences=[]
def tuple_diffs(before,after,path):
    if isinstance(before,dict) and isinstance(after,dict):
        for key in before:tuple_diffs(before[key],after[key],path+'.'+key)
    elif isinstance(before,(list,tuple)) and isinstance(after,(list,tuple)):
        if type(before)is not type(after):differences.append({'path':path,'runtime_type':type(before).__name__,'saved_JSON_type':type(after).__name__})
        for i,(a,b) in enumerate(zip(before,after)):tuple_diffs(a,b,path+f'[{i}]')
tuple_diffs(raw,saved['outcome'],'outcome')
assert differences and raw!=saved['outcome']
payload={'package':str(PACKAGE),'public_calls':len(rows)+1,'cases':rows,
         'runtime_tuple_diagnostic':{'original_failed_index':index,'runtime_vs_saved_Python_equality':raw==saved['outcome'],
             'strict_serialized_public_JSON_equal':True,'tuple_vs_list_paths':differences},
         'caller_inputs_unchanged':True,'catalog_and_mechanics_unchanged':True,
         'production_source_sha256':hashlib.sha256((PACKAGE/'rouge/operator_engine.py').read_bytes()).hexdigest(),
         'private_state_read':False,'game_actions':0,'native_validation':False}
OUTPUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'public_calls':len(rows)+1,'tuple_diagnostic_paths':len(differences),'package':str(PACKAGE)},ensure_ascii=False))
