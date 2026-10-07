"""Independent raw-text/talent-gate probes; no result flag is an error oracle."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys

PACKAGE=Path(sys.argv[1]).resolve();OUT=Path(sys.argv[2]).resolve()
sys.dont_write_bytecode=True;sys.path.insert(0,str(PACKAGE))
from rouge.catalog import catalog
from rouge.damage import calculate_damage
from rouge.operator_engine import selected_talents
SHU='char_2025_shu'
values=[('absent',...),('false',False),('true',True),('zero',0),('one',1),('float_zero',0.0),
 ('float_one',1.0),('null',None),('empty_list',[]),('empty_object',{}),('true_list',[0]),
 ('true_object',{'declared':False}),('negative_number',-1),('two',2),
 ('false_text','false'),('unknown_text','unknown'),('zero_text','0'),('one_text','1'),
 ('empty_text',''),('padded_text',' false '),('whitespace_text','\t'),('unicode_text','未知')]
training=[('E0',{'elite':0,'level':1,'skill_rank':1},(1,)),
 ('E1',{'elite':1,'level':50,'skill_rank':7},(1,2)),
 ('E2_min',{'elite':2,'level':1,'potential':1,'skill_rank':10},(1,2,3)),
 ('E2_high_potential',{'elite':2,'level':90,'potential':6,'skill_rank':10},(1,2,3))]
rows={}
for mode in ('frames','continuous'):
    for training_name,params,skills in training:
        for skill in skills:
            selected,_=selected_talents(catalog()['operators'][SHU],params)
            qualified=any(t['name']=='天有四时' for t in selected)
            assert qualified==(params['elite']==2)
            for label,value in values:
                args={'operator':SHU,'skill':skill,'base_attack':1000,'window_seconds':10,'timing_mode':mode,**params}
                if value is not ...:args['four_sui']=deepcopy(value)
                original=deepcopy(args)
                try:outcome={'result':calculate_damage(args),'error':None}
                except Exception as error:outcome={'result':None,'error':{'type':type(error).__name__,'message':str(error)}}
                assert args==original
                rows[f'{training_name}:S{skill}:{mode}:{label}']={'input':original,'outcome':outcome,
                    'selected_talent_qualified_from_source_and_training':qualified,
                    'expected_new_text_error':qualified and type(value)is str}
    controls=[
      ('other_owner_four','silverash',3,{'four_sui':'false'}),
      ('other_owner_fragile','silverash',3,{'preexisting_fragile':'false'}),
      ('other_owner_cooperative','silverash',3,{'cooperative':'unknown'}),
      ('other_Shu_checkbox',SHU,3,{'three_professions':'false','three_same_profession':'unknown','four_sui':False}),
      ('prior_training_unopened_skill',SHU,2,{'elite':0,'level':1,'skill_rank':1,'four_sui':'false'}),
      ('prior_training_unopened_mastery',SHU,1,{'elite':1,'level':50,'skill_rank':10,'four_sui':'unknown'}),
      ('empty_observation_active_text',SHU,3,{'window_seconds':0,'four_sui':'false'}),
      ('empty_enemy_active_text',SHU,1,{'timing':{'target_disappears_seconds':0},'four_sui':''}),
      ('active_module_text',SHU,2,{'level':90,'module_id':'uniequip_002_shu','module_level':3,'four_sui':'false'}),
    ]
    for name,owner,skill,extra in controls:
        args={'operator':owner,'skill':skill,'base_attack':1000,'window_seconds':10,'timing_mode':mode,**deepcopy(extra)}
        original=deepcopy(args)
        try:outcome={'result':calculate_damage(args),'error':None}
        except Exception as error:outcome={'result':None,'error':{'type':type(error).__name__,'message':str(error)}}
        assert args==original
        rows[f'{name}:{mode}']={'input':original,'outcome':outcome,
            'expected_new_text_error':name in ('empty_observation_active_text','empty_enemy_active_text','active_module_text')}
payload={'package':str(PACKAGE),'baseline_head':'c3ccf25d59144227dd0f8f5ca9ef6c8bf81ad8cf',
    'public_calls':len(rows),'cases':rows,'caller_inputs_preserved':True,'no_result_flag_used_as_error_oracle':True,
    'engine_sha256':hashlib.sha256((PACKAGE/'rouge/operator_engine.py').read_bytes()).hexdigest(),
    'private_state_read':False,'native_validation':False}
OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'public_calls':len(rows),'package':str(PACKAGE)},ensure_ascii=False))
