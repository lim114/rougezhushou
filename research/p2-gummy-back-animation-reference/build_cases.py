import copy
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
OP='char_196_sunbr'; FRONT=OP+':Front:Attack'; BACK=OP+':Back:Attack'
cases=[]
def add(label,scenario,expect='unchanged'):
    cases.append({'label':label,'scenario':scenario,'expect':expect})
for skill in (1,2):
    base={'operator':OP,'skill':skill,'base_attack':1000}
    add(f's{skill}_default',base)
    add(f's{skill}_zero_window',{**base,'window_seconds':0})
    add(f's{skill}_continuous',{**base,'timing_mode':'continuous','window_seconds':11})
    add(f's{skill}_zero_recipient',{**base,'healing_targets':0,'window_seconds':11})
    add(f's{skill}_front_skill',{**base,'window_seconds':11,'timing':{'animation_reference':FRONT}})
    add(f's{skill}_front_normal',{**base,'window_seconds':11,'timing':{'normal_animation_reference':FRONT}})
    add(f's{skill}_back_skill',{**base,'window_seconds':11,'timing':{'animation_reference':BACK}},'new_back_success')
    add(f's{skill}_back_normal',{**base,'timing':{'normal_animation_reference':BACK}},'new_back_success')
    add(f's{skill}_generic_skill',{**base,'timing':{'animation_reference':OP+':Back:Skill'}},'exact_error')
add('default_s2_11',{'operator':OP,'skill':2,'base_attack':1000,'window_seconds':11})
add('back_s2_both',{'operator':OP,'skill':2,'base_attack':1000,'window_seconds':11,'timing':{'animation_reference':BACK,'normal_animation_reference':BACK}},'new_back_success')
add('back_s2_manual',{'operator':OP,'skill':2,'window_seconds':11,'timing':{'animation_reference':BACK,'windup_frames':6,'recovery_frames':9}},'new_back_success')
add('back_s2_half_open',{'operator':OP,'skill':2,'window_seconds':316/30,'timing':{'animation_reference':BACK}},'new_back_success')
add('back_s2_empty_enemy',{'operator':OP,'skill':2,'window_seconds':11,'timing':{'animation_reference':BACK,'target_windows':[]}},'new_back_success')
add('back_s2_no_friend',{'operator':OP,'skill':2,'healing_targets':0,'timing':{'animation_reference':BACK}},'new_back_success')
add('back_s2_continuous',{'operator':OP,'skill':2,'timing_mode':'continuous','window_seconds':11,'timing':{'animation_reference':BACK}},'new_back_success')
for name in ('Default','Idle','Start','Die','Skill_2_Loop'):
    add('back_reject_'+name,{'operator':OP,'skill':2,'timing':{'animation_reference':OP+':Back:'+name}},'exact_error')
add('other_owner_reject',{'operator':'kaltsit','skill':3,'timing':{'animation_reference':BACK}},'exact_error')
add('old_invalid_training_first',{'operator':OP,'skill':2,'elite':4,'timing':{'animation_reference':BACK}},'exact_error')
for op,skill in (('kaltsit',3),('mechanist',1),('char_2025_shu',1)):
    add('other_default_'+op,{'operator':op,'skill':skill,'window_seconds':11})
unique=set()
for item in cases:
    identity=json.dumps(item['scenario'],sort_keys=True,ensure_ascii=False)
    assert identity not in unique,item['label']
    unique.add(identity)
(ROOT/'matrix-cases.json').write_text(json.dumps({'version':1,'count':len(cases),'cases':cases},ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'unique_cases':len(cases)}))
