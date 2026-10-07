"""Preserve every declared case from the read-only audit, then add the narrow text boundary."""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parent
AUDIT=ROOT.parent/'p2-boolean-option-audit-062'
m=json.loads((AUDIT/'boolean-input-matrix.json').read_text())
c=json.loads((AUDIT/'narrow-four-sui-controls.json').read_text())
VALUES={'absent':None,'false_bool':False,'true_bool':True,'null':None,'int0':0,'int1':1,
    'float0':0.0,'float1':1.0,'false_text':'false','unknown_text':'unknown','zero_text':'0',
    'true_text':'true','empty_text':'','int2':2,'negative_int':-1,'empty_list':[],
    'nonempty_list':[0],'empty_dict':{}}
cases={}
for key,row in m['rows'].items():
    operator,skill,mode,field=key.split(':')
    for label,value in VALUES.items():
        args={'operator':operator,'skill':int(skill),'base_attack':1000,
              'window_seconds':10,'timing_mode':mode}
        if label!='absent':args[field]=value
        cases['audit-active:'+key+':'+label]=args
for key,row in m['inactive'].items():
    operator,skill,mode,field,label=key.split(':')
    cases['audit-inactive:'+key]={'operator':operator,'skill':int(skill),'base_attack':1000,
        'window_seconds':10,'timing_mode':mode,field:VALUES[label]}
for prefix,field in (('audit-ineligible','ineligible'),('audit-other-owner','other_owner')):
    absent={}
    for key,row in c[field].items():
        args=row['request']
        cases[prefix+':'+key]=args
        clean={k:v for k,v in args.items() if k!='four_sui'}
        absent[json.dumps(clean,sort_keys=True)]=clean
    for i,args in enumerate(absent.values()):cases[prefix+f':absent:{i}']=args
assert len(cases)==4552,len(cases)
TEXTS=('false','unknown','0','1','true','False','True','',' false ','\t','未知','是','否')
TRAINING=(
    {'elite':2,'level':1,'potential':1,'skill_rank':1},
    {'elite':2,'level':90,'potential':6,'skill_rank':7},
    {'elite':2,'level':59,'potential':6,'skill_rank':10,'module_id':'uniequip_002_shu','module_level':3},
    {'elite':2,'level':60,'potential':1,'skill_rank':10,'module_id':'uniequip_002_shu','module_level':1},
    {'elite':2,'level':90,'potential':6,'skill_rank':10,'module_id':'uniequip_002_shu','module_level':3})
for skill in (1,2,3):
    for mode in ('frames','continuous'):
        for i,training in enumerate(TRAINING):
            for j,text in enumerate(TEXTS):
                cases[f'qualified-text:S{skill}:{mode}:training{i}:text{j}']={
                    'operator':'char_2025_shu','skill':skill,'timing_mode':mode,
                    'base_attack':1000,'window_seconds':10,'four_sui':text,**training}
        for i,training in enumerate(TRAINING):
            for label,value in (('absent',None),('false',False),('true',True),('zero',0),
                                ('one',1),('null',None),('float0',0.0),('float1',1.0)):
                args={'operator':'char_2025_shu','skill':skill,'timing_mode':mode,
                      'base_attack':1000,'window_seconds':10,**training}
                if label!='absent':args['four_sui']=value
                cases[f'qualified-compat:S{skill}:{mode}:training{i}:{label}']=args
for i,args in enumerate((
    {'operator':'char_2025_shu','skill':2,'elite':0,'skill_rank':1,'four_sui':'false'},
    {'operator':'char_2025_shu','skill':1,'elite':1,'skill_rank':10,'four_sui':'unknown'},
    {'operator':'char_2025_shu','skill':False,'four_sui':'false'},
    {'operator':'char_2025_shu','skill':1,'skill_rank':True,'four_sui':'unknown'},
    {'operator':'char_2025_shu','skill':1,'level':0,'four_sui':'false'},
    {'operator':'char_2025_shu','skill':3,'potential':0,'four_sui':'0'},
    {'operator':'char_2025_shu','skill':3,'healing_targets':True,'four_sui':'1'})):
    cases[f'prior-validation-error:{i}']=args
(ROOT/'requests.json').write_text(json.dumps({'prior_audit_cases_reused':4552,'cases':cases},
    ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print({'public_pairs_requested':len(cases),'prior_audit_cases_retained':4552})
