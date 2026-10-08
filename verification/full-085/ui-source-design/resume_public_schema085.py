"""Strictly reuse saved69; calculate only1085 unrun case requests; no Qt/Wine."""
import gzip
import hashlib
import json
import sys
import traceback
from collections import Counter
from copy import deepcopy
from pathlib import Path

HERE=Path(__file__).resolve().parent
PACKAGE=HERE/'public-schema-085'
freeze=json.loads((HERE/'public-source-freeze-085.json').read_bytes())
assert freeze['base_commit']=='2dfd9fa2c9a62db0112bc0fb98cd23123dd3b48b'and not freeze['patches']
sys.path[:0]=[str(PACKAGE),str(HERE)];sys.dont_write_bytecode=True
from rouge.catalog import catalog
from rouge.damage import calculate_damage
from rouge.operator_engine import selected_talents
from rouge.operator_options import OPTIONS
import rouge.reporting as reporting_module
import rouge.estimate as estimate_module
from cases085 import cases085
from public_contracts import (canonical085,require_warning_order085,require_susuro_checkbox085,
    require_neural_checkbox085,require_repeat_checkbox085,require_nearby_checkbox085)

def hashes():
    return {p.relative_to(PACKAGE).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted((PACKAGE/'rouge').rglob('*'))if p.is_file()and p.suffix in ('.py','.json')}

failure=HERE/'public-schema-final-085-failure.json.gz'
failure_raw=failure.read_bytes()
assert hashlib.sha256(failure_raw).hexdigest()=='513bb64717654c5c8b31cd69b437c66bf7b575377502520d7f74f39f8e142894'
saved=json.loads(gzip.decompress(failure_raw));before=hashes()
assert before==saved['source_hashes_before']==saved['source_hashes_after']==freeze['source_sha256']
cases=cases085();assert len(cases)==1154 and saved['fresh_public_calls']==69
assert Counter(r['section']for r in cases)=={81:136,82:216,83:450,84:88,85:264}
assert len(saved['completed_records'])==68 and cases[68]==saved['current_case']
rows=deepcopy(saved['completed_records']);controls={};counts=Counter();qualification_helper_calls=0

def prepared_input(case):
    requested=case['input']
    args={key:default for key,label,default,maximum,numbers in OPTIONS.get(requested['operator'],[])if requested['skill']in numbers}
    args.update(requested);return args

def require_contract(case,args,result,text):
    global qualification_helper_calls
    if case['section']==81:
        require_warning_order085(result,args,text,case.get('technical',False))
    elif case['section']==82:
        key=canonical085({k:v for k,v in args.items()if k!='low_cost_healing_target'})
        if not args['low_cost_healing_target']:controls[key]=result
        qualification_helper_calls+=1;talents,_=selected_talents(catalog()['operators'][args['operator']],args)
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
        qualification_helper_calls+=1;talents,_=selected_talents(catalog()['operators'][args['operator']],args)
        bonus=next((t['values']['atk']for t in talents if t['name']=='翔虫机动'),0.0)
        require_nearby_checkbox085(result,args,text,controls[key],bonus)
    else:raise AssertionError('Section source not sealed')

for index,row in enumerate(rows):
    case=cases[index];assert case['section']==row['section']and case['context']==row['context']
    assert canonical085(prepared_input(case))==canonical085(row['input'])
    before_row=canonical085(row)
    texts=row['report_texts'];assert set(texts)=={'estimate','default','technical'}
    assert all(type(v)is str for v in texts.values())and texts['estimate']==texts['default']
    assert row['visible_report']==texts['technical'if case.get('technical',False)else 'default']
    require_contract(case,row['input'],row['result'],row['visible_report'])
    assert canonical085(row)==before_row
    counts[row['section']]+=1
case=saved['current_case'];args=saved['current_input'];result=saved['current_result'];texts=saved['current_report_texts']
assert canonical085(prepared_input(case))==canonical085(args)
assert set(texts)=={'estimate','default','technical'}and texts['estimate']==texts['default']
text=texts['technical'if case.get('technical',False)else 'default'];assert text==saved['current_visible_report']
current_before=canonical085(result);require_contract(case,args,result,text);assert canonical085(result)==current_before
rows.append({'section':case['section'],'context':case['context'],'input':args,'result':result,'visible_report':text,
    'report_texts':texts,'all_three_texts_preserve_result_bytes':True})
counts[case['section']]+=1
assert len(rows)==69 and qualification_helper_calls==0
reassert={'status':'PASS_STRICT_SAVED_69_NO_NEW_API_OR_FORMATTER',
    'first_failure_sha256':hashlib.sha256(failure_raw).hexdigest(),'saved_passed_records_reasserted':68,
    'saved_counterexample_reasserted':1,'all_68_record_JSON_unchanged':True,
    'counterexample_result_JSON_unchanged':True,'saved_three_texts_unchanged':True,
    'scope_fix':'Only mechanist S3 zero window: top healing field absent; exact estimate window_healing0. Other fields/None rules unchanged.',
    'application_API_calls':0,'formatter_calls':0,'qualification_helper_calls':0,
    'source_hashes_before':before,'source_hashes_after':hashes(),'Qt_executed':False,'Wine_executed':False}
with (HERE/'saved69-reassertion085.json').open('x')as out:json.dump(reassert,out,ensure_ascii=False,indent=2);out.write('\n')

fresh_calls=0;formatter_requests=0;expected_errors=0;formatter_entry_counts=Counter()
original_format_report=reporting_module.format_report
original_format_estimate=estimate_module.format_estimate
def format_report(result,*,technical=False):
    formatter_entry_counts['format_report_technical'if technical else 'format_report_default']+=1
    return original_format_report(result,technical=technical)
def format_estimate(result):
    formatter_entry_counts['format_estimate']+=1
    return original_format_estimate(result)
reporting_module.format_report=format_report;estimate_module.format_estimate=format_estimate

def preserve_failure(error_type,error,trace):
    payload={'scope':'Preserved remaining-only085 API preflight failure; no Qt/Wine execution',
        'fresh_public_calls_in_resume':fresh_calls,'previous_saved_public_calls':69,
        'completed_asserted_cases':len(rows),'completed_section_counts':dict(counts),
        'formatter_text_requests_in_resume':formatter_requests,'formatter_entries_in_resume':dict(formatter_entry_counts),
        'expected_existing_errors_completed':expected_errors,
        'source_hashes_before':before,'source_hashes_after':hashes(),
        'current_case':globals().get('case'),'current_input':globals().get('args'),
        'current_result':globals().get('result'),'current_visible_report':globals().get('text'),
        'current_report_texts':globals().get('report_texts'),'completed_records':rows,
        'error_type':error_type.__name__,'error':str(error),
        'traceback':''.join(traceback.format_exception(error_type,error,trace)),
        'GUI_executed':False,'Wine_executed':False}
    raw=gzip.compress(json.dumps(payload,ensure_ascii=False,allow_nan=False).encode(),mtime=0)
    with (HERE/'public-schema-resume085-failure.json.gz').open('xb')as out:out.write(raw)
    sys.__excepthook__(error_type,error,trace)

sys.excepthook=preserve_failure
for case in cases[69:]:
    args=prepared_input(case);original=canonical085(args);result=None;text=None;report_texts=None;fresh_calls+=1
    try:result=calculate_damage(args)
    except ValueError as error:
        assert case.get('expected_error')==str(error),(case,str(error))
        assert canonical085(args)==original
        expected_errors+=1;counts[case['section']]+=1
        rows.append({'section':case['section'],'context':case['context'],'input':args,
            'expected_error':case['expected_error'],'actual_error_type':'ValueError','actual_error':str(error),
            'result':None,'visible_report':str(error),'report_texts':None})
        continue
    assert not case.get('expected_error'),(case,result)
    assert canonical085(args)==original
    result_before_texts=canonical085(result)
    formatter_requests+=1;estimate_text=format_estimate(result)
    formatter_requests+=1;default_text=format_report(result)
    formatter_requests+=1;technical_text=format_report(result,technical=True)
    report_texts={'estimate':estimate_text,'default':default_text,'technical':technical_text}
    assert estimate_text==default_text and canonical085(result)==result_before_texts
    text=report_texts['technical'if case.get('technical',False)else 'default']
    require_contract(case,args,result,text)
    rows.append({'section':case['section'],'context':case['context'],'input':args,'result':result,'visible_report':text,
        'report_texts':report_texts,'all_three_texts_preserve_result_bytes':True})
    counts[case['section']]+=1
assert hashes()==before and fresh_calls==1085 and len(rows)==1154 and expected_errors==24
assert formatter_requests==3183 and formatter_entry_counts=={
    'format_estimate':1061,'format_report_default':2122,'format_report_technical':1061}
assert qualification_helper_calls==480
all_formatter_entries=Counter(saved['formatter_entry_counts'])+formatter_entry_counts
receipt={'scope':'1154 new085 design records; first69 saved reused exactly and only1085 unrun requests called; no GUI/Wine proof',
    'calls':1154,'case_design_records':1154,'unique_requested_calculation_inputs':1086,
    'intentional_technical_checkbox_state_pairs_with_equal_API_input':68,
    'sections':dict(counts),'successful_result_rows':1130,'expected_existing_error_rows':24,
    'formatter_text_requests':saved['formatter_text_requests']+formatter_requests,
    'formatter_entry_counts':dict(all_formatter_entries),'actual_formatter_function_entries':sum(all_formatter_entries.values()),
    'estimate_dispatcher_delegates_to_default_report':True,
    'saved_report_texts_per_successful_result':['estimate','default','technical'],
    'external_contract_qualification_helper_calls':qualification_helper_calls,
    'source_drift':[],'source_hashes':before,'records':rows,'GUI_executed':False,'Wine_executed':False,
    'root_commit':freeze['base_commit'],
    'first_preflight_candidate_runner_sha256':saved['candidate_runner_sha256'],
    'corrected_pending_runner_sha256':hashlib.sha256((HERE/'wine-ui-smoke-085.py').read_bytes()).hexdigest(),
    'actual_API_call_attribution':{'first_preflight_calls':69,'remaining_only_resume_calls':1085,
        'total_actual_calls':1154,'saved_completed_passed_reused':68,'saved_counterexample_reasserted_without_API':1,
        'previous_completed_case_request_repeated_for_retry':0,'old3063_cases_repeated':0,
        'first_failure_retained':True},
    'strict_saved_result_reuse_proof_sha256':hashlib.sha256((HERE/'saved69-reassertion085.json').read_bytes()).hexdigest()}
assert receipt['formatter_text_requests']==3390 and receipt['actual_formatter_function_entries']==4520
raw=gzip.compress(json.dumps(receipt,ensure_ascii=False,allow_nan=False).encode(),mtime=0)
with (HERE/'public-schema-final-085.json.gz').open('xb')as out:out.write(raw)
summary={k:v for k,v in receipt.items()if k not in ('source_hashes','records')};summary['full_receipt_sha256']=hashlib.sha256(raw).hexdigest()
with (HERE/'public-schema-final-085-summary.json').open('x')as out:json.dump(summary,out,ensure_ascii=False,indent=2)
print(json.dumps(summary,ensure_ascii=False))
