"""Read-only public API observations: do not choose a validation policy here."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parent
FROZEN=ROOT/'frozen-worktree-060'
sys.path.insert(0,str(FROZEN))
from rouge.catalog import catalog
from rouge.damage import calculate_damage
from rouge.operator_options import OPTIONS
from rouge.estimate import format_estimate

def canonical(value):
    return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'))
def hashed(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()
VALUES=[('absent',None),('false_bool',False),('true_bool',True),('null',None),
        ('int0',0),('int1',1),('float0',0.0),('float1',1.0),
        ('false_text','false'),('unknown_text','unknown'),('zero_text','0'),
        ('true_text','true'),('empty_text',''),('int2',2),('negative_int',-1),
        ('empty_list',[]),('nonempty_list',[0]),('empty_dict',{})]
boolean_options=[]
for operator,entries in OPTIONS.items():
    for field,label,default,maximum,skills in entries:
        if isinstance(default,bool):
            boolean_options.append({'operator':operator,'field':field,'label':label,
                                    'default':default,'skills':list(skills)})
boolean_options.extend([
    {'operator':'silverash','field':'cooperative','label':'协同攻击持续覆盖同一目标','default':False,'skills':[3]},
    {'operator':'silverash','field':'preexisting_fragile','label':'全程计该技能脆弱','default':False,'skills':[3]}])

rows={}
full={}
for definition in boolean_options:
    for skill in definition['skills']:
        for mode in ('frames','continuous'):
            outcomes={}
            for label,value in VALUES:
                args={'operator':definition['operator'],'skill':skill,
                      'timing_mode':mode,'base_attack':1000,'window_seconds':10}
                if label!='absent':args[definition['field']]=value
                original=deepcopy(args)
                try:
                    result=calculate_damage(args)
                    output={'result_sha256':hashed(result),'attack':result.get('attack'),
                            'total_damage':result.get('total_damage'),'total_healing':result.get('total_healing'),
                            'base_stats':result.get('estimate',{}).get('base_stats'),
                            'initial_seconds':result['estimate']['skill']['initial_seconds'],
                            'recharge_seconds':result['estimate']['skill']['recharge_seconds'],
                            'cycle_seconds':result['estimate']['skill']['cycle_seconds'],
                            'shu_periodic_sp_reference':result.get('shu_periodic_sp_reference'),
                            'error':None}
                except Exception as exc:
                    result=None
                    output={'error_type':type(exc).__name__,'error':str(exc)}
                assert args==original
                outcomes[label]=output
                if definition['field'] in ('four_sui','preexisting_fragile','cooperative') and label in (
                        'absent','false_bool','true_bool','null','int0','int1','false_text','unknown_text','zero_text'):
                    name=f"{definition['operator']}:{skill}:{mode}:{definition['field']}:{label}"
                    full[name]={'scenario':args,'result':result,
                                'report':format_estimate(result) if result is not None else None,'error':output['error']}
            for label,output in outcomes.items():
                if 'result_sha256' in output:
                    output['whole_output_matches_true']=output['result_sha256']==outcomes['true_bool'].get('result_sha256')
                    output['whole_output_matches_false']=output['result_sha256']==outcomes['false_bool'].get('result_sha256')
                    output['whole_output_matches_absent']=output['result_sha256']==outcomes['absent'].get('result_sha256')
            key=f"{definition['operator']}:{skill}:{mode}:{definition['field']}"
            rows[key]={'definition':definition,'values':outcomes}

# Different owner and an inapplicable skill are distinct inactivity controls.
inactive={}
for definition in boolean_options:
    requests=[('mechanist',1)]
    unused=[i for i in range(1,len(catalog()['operators'][definition['operator']]['skills'])+1)
            if i not in definition['skills']]
    if unused:requests.append((definition['operator'],unused[0]))
    for operator,skill in requests:
        for mode in ('frames','continuous'):
            args={'operator':operator,'skill':skill,'base_attack':1000,'window_seconds':10,'timing_mode':mode}
            absent=calculate_damage(args)
            for label,value in VALUES:
                if label=='absent':continue
                request={**args,definition['field']:value}
                before=deepcopy(request)
                try:
                    r=calculate_damage(request)
                    record={'whole_output_matches_absent':r==absent,'result_sha256':hashed(r),'error':None}
                except Exception as exc:
                    record={'error_type':type(exc).__name__,'error':str(exc)}
                assert before==request
                inactive[f'{operator}:{skill}:{mode}:{definition["field"]}:{label}']=record

(ROOT/'boolean-input-matrix.json').write_text(json.dumps({'freeze_receipt':'freeze-receipt.json',
    'options':boolean_options,'active_calls':len(rows)*len(VALUES),'rows':rows,
    'inactive_calls':len(inactive),'inactive':inactive,
    'all_caller_inputs_preserved':True,'policy_selected':False},ensure_ascii=False,indent=2)+'\n')
(ROOT/'public-counterexamples.json').write_text(json.dumps({'freeze_receipt':'freeze-receipt.json',
    'full_public_outputs':full},ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'boolean_option_definitions':len(boolean_options),'active_cases':len(rows),
                  'active_calls':len(rows)*len(VALUES),'inactive_calls':len(inactive),
                  'full_public_outputs':len(full),'policy_selected':False},ensure_ascii=False))
