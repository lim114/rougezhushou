"""One new-case API preflight after exact final source freeze; never Qt/Wine."""
import gzip
import hashlib
import json
import sys
import traceback
from collections import Counter
from pathlib import Path

HERE=Path(__file__).resolve().parent
READY=HERE/'final-source-085-ready.json'
if not READY.is_file():
    raise RuntimeError('Final root85 public source is pending; no API preflight is permitted')
ready=json.loads(READY.read_text())
assert ready['status']=='FINAL_ROOT085_FROZEN_FOR_SINGLE_NEW_API_PREFLIGHT'
PACKAGE=HERE/'public-schema-085'
FREEZE=HERE/'public-source-freeze-085.json'
assert hashlib.sha256(FREEZE.read_bytes()).hexdigest()==ready['public_freeze_sha256']
freeze=json.loads(FREEZE.read_text());assert freeze['base_commit']==ready['root_commit']and not freeze['patches']
assert hashlib.sha256((HERE/'wine-ui-smoke-085.py').read_bytes()).hexdigest()==ready['runner_sha256']
assert not (HERE/'public-schema-final-085.json.gz').exists()
assert not (HERE/'public-schema-final-085-failure.json.gz').exists()
sys.path[:0]=[str(PACKAGE),str(HERE)];sys.dont_write_bytecode=True
from rouge.catalog import catalog
from rouge.damage import calculate_damage
from rouge.operator_engine import selected_talents
from rouge.operator_options import OPTIONS
from rouge.reporting import format_report
from cases085 import cases085
from public_contracts import (canonical085,require_warning_order085,require_susuro_checkbox085,
    require_neural_checkbox085,require_repeat_checkbox085,require_nearby_checkbox085)

def hashes():
    return {p.relative_to(PACKAGE).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted((PACKAGE/'rouge').rglob('*'))if p.is_file()and p.suffix in ('.py','.json')}

before=hashes();assert before==freeze['source_sha256']
cases=cases085();assert Counter(r['section']for r in cases)=={81:136,82:216,83:450,84:88,85:264}
assert len(cases)==1154
rows=[];counts=Counter();controls={};fresh_calls=0;formatter_calls=0;expected_errors=0

def preserve_failure(error_type,error,trace):
    payload={'scope':'Preserved failed new085 API-only preflight; no Qt/Wine execution',
        'fresh_public_calls':fresh_calls,'formatter_calls':formatter_calls,
        'completed_asserted_cases':len(rows),'completed_section_counts':dict(counts),
        'expected_existing_errors_completed':expected_errors,
        'source_hashes_before':before,'source_hashes_after':hashes(),
        'current_case':globals().get('case'),'current_input':globals().get('args'),
        'current_result':globals().get('result'),'current_visible_report':globals().get('text'),
        'completed_records':rows,'error_type':error_type.__name__,'error':str(error),
        'traceback':''.join(traceback.format_exception(error_type,error,trace)),
        'candidate_runner_sha256':ready['runner_sha256'],'root_commit':ready['root_commit'],
        'GUI_executed':False,'Wine_executed':False}
    raw=gzip.compress(json.dumps(payload,ensure_ascii=False,allow_nan=False).encode(),mtime=0)
    with (HERE/'public-schema-final-085-failure.json.gz').open('xb')as out:out.write(raw)
    summary={k:v for k,v in payload.items()if k not in ('source_hashes_before','source_hashes_after','current_result','completed_records')}
    summary['full_receipt_sha256']=hashlib.sha256(raw).hexdigest()
    with (HERE/'public-schema-final-085-failure-summary.json').open('x')as out:json.dump(summary,out,ensure_ascii=False,indent=2)
    sys.__excepthook__(error_type,error,trace)

sys.excepthook=preserve_failure
for case in cases:
    requested=case['input']
    args={key:default for key,label,default,maximum,numbers in OPTIONS.get(requested['operator'],[])if requested['skill']in numbers}
    args.update(requested);original=canonical085(args);result=None;text=None;fresh_calls+=1
    try:result=calculate_damage(args)
    except ValueError as error:
        assert case.get('expected_error')==str(error),(case,str(error))
        assert canonical085(args)==original
        expected_errors+=1;counts[case['section']]+=1
        rows.append({'section':case['section'],'context':case['context'],'input':args,
            'expected_error':case['expected_error'],'actual_error_type':'ValueError','actual_error':str(error),
            'result':None,'visible_report':str(error)})
        continue
    assert not case.get('expected_error'),(case,result)
    assert canonical085(args)==original
    technical=case.get('technical',False);formatter_calls+=1;text=format_report(result,technical=technical)
    if case['section']==81:
        require_warning_order085(result,args,text,technical)
    elif case['section']==82:
        key=canonical085({k:v for k,v in args.items()if k!='low_cost_healing_target'})
        if not args['low_cost_healing_target']:controls[key]=result
        talents,_=selected_talents(catalog()['operators'][args['operator']],args)
        factor=next((t['values']['heal_scale']for t in talents if t['name']=='微创治疗'),1.0)
        require_susuro_checkbox085(result,args,text,controls[key],factor)
    elif case['section']==83:
        require_neural_checkbox085(result,args,text)
    elif case['section']==84:
        bonus=catalog()['operators'][args['operator']]['skills'][args['skill']-1]['levels'][args['skill_rank']-1]['values'].get('atk',0.0)
        if args['skill']==2:
            key=canonical085({k:v for k,v in args.items()if k!='haruka_repeat'})
            if not args['haruka_repeat']:controls[key]=result
            plain=controls[key]
        else:plain=result
        require_repeat_checkbox085(result,args,text,plain,bonus)
    elif case['section']==85:
        key=canonical085({k:v for k,v in args.items()if k!='near_previous_deployment'})
        if not args['near_previous_deployment']:controls[key]=result
        talents,_=selected_talents(catalog()['operators'][args['operator']],args)
        bonus=next((t['values']['atk']for t in talents if t['name']=='翔虫机动'),0.0)
        require_nearby_checkbox085(result,args,text,controls[key],bonus)
    else:raise AssertionError('Section source not sealed')
    rows.append({'section':case['section'],'context':case['context'],'input':args,'result':result,'visible_report':text})
    counts[case['section']]+=1
assert before==hashes()and fresh_calls==len(rows)==1154 and expected_errors==24 and formatter_calls==1130
receipt={'scope':'New085 public API-only planned Qt contracts; no GUI/Wine proof',
    'calls':1154,'sections':dict(counts),'expected_existing_error_rows':expected_errors,
    'formatter_calls':formatter_calls,'source_drift':[],'source_hashes':before,'records':rows,
    'GUI_executed':False,'Wine_executed':False,'root_commit':ready['root_commit'],
    'candidate_runner_sha256':ready['runner_sha256'],
    'actual_API_call_attribution':{'new_distinct_cases':1154,'old3063_cases_repeated':0,
        'previous_completed_API_repeated':0,'first_preflight_calls':fresh_calls,'total_actual_calls':fresh_calls}}
raw=gzip.compress(json.dumps(receipt,ensure_ascii=False,allow_nan=False).encode(),mtime=0)
with (HERE/'public-schema-final-085.json.gz').open('xb')as out:out.write(raw)
summary={k:v for k,v in receipt.items()if k not in ('source_hashes','records')};summary['full_receipt_sha256']=hashlib.sha256(raw).hexdigest()
with (HERE/'public-schema-final-085-summary.json').open('x')as out:json.dump(summary,out,ensure_ascii=False,indent=2)
print(json.dumps(summary,ensure_ascii=False))
