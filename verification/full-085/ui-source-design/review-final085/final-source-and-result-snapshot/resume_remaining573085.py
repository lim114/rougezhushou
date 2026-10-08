"""Use strict581 saved proof and execute only573 remaining085 requests."""
import ast
import gzip
import hashlib
import json
import sys
import traceback
from collections import Counter
from copy import deepcopy
from pathlib import Path

HERE=Path(__file__).resolve().parent;PACKAGE=HERE/'public-schema-085'
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

freeze=json.loads((HERE/'public-source-freeze-085.json').read_bytes());assert not freeze['patches']
proof=json.loads((HERE/'saved581-reassertion085.json').read_bytes())
assert proof['status']=='PASS_STRICT_SAVED_581_NO_NEW_API_OR_FORMATTER'and proof['API_calls']==proof['formatter_calls']==0
assert proof['external_contract_selected_talents_data_helper_calls']==216
audit=json.loads((HERE/'remaining-contract-field-audit085.json').read_bytes())
assert audit['status']=='PASS_REMAINING_RECEIVERS_MATCH_EXACT_FINAL_PUBLIC_PRODUCERS'
independent=json.loads((HERE/'review-final085/remaining-receiver-source-and-saved581-review085.json').read_bytes())
assert independent # Its exact hash/status are checked by the separate final independent receipt.
assert hashlib.sha256((HERE/'review-final085/remaining-receiver-source-and-saved581-review085.json').read_bytes()).hexdigest()=='e03c46623d2ce98e96bec096e1caa2f54a151d16738b9202e1fc99e1b6e5fd22'
f1=HERE/'public-schema-final-085-failure.json.gz';f2=HERE/'public-schema-resume085-failure.json.gz'
raw1=f1.read_bytes();raw2=f2.read_bytes()
assert hashlib.sha256(raw1).hexdigest()==proof['first_failure_sha256']and hashlib.sha256(raw2).hexdigest()==proof['second_failure_sha256']
first=json.loads(gzip.decompress(raw1));second=json.loads(gzip.decompress(raw2));before=hashes()
assert before==freeze['source_sha256']==proof['source_hashes_before']==proof['source_hashes_after']==second['source_hashes_before']==second['source_hashes_after']
cases=cases085();rows=deepcopy(second['completed_records']);current=second['current_case']
rows.append({'section':current['section'],'context':current['context'],'input':second['current_input'],
    'result':second['current_result'],'visible_report':second['current_visible_report'],
    'report_texts':second['current_report_texts'],'all_three_texts_preserve_result_bytes':True})
assert len(rows)==581
for index,row in enumerate(rows):
    assert index==proof['record_fingerprints'][index]['case_index']
    assert hashlib.sha256(canonical085(row).encode()).hexdigest()==proof['record_fingerprints'][index]['record_canonical_sha256']
controls={};qualification_helper_calls=0
tree=ast.parse((HERE/'resume_public_schema085.py').read_bytes())
functions=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in ('prepared_input','require_contract')]
assert len(functions)==2
exec(compile(ast.Module(body=functions,type_ignores=[]),'unchanged-pure-contract-dispatch085','exec'),globals())
counts=Counter(row['section']for row in rows);fresh_calls=0;formatter_requests=0
expected_errors=sum('expected_error'in row for row in rows);assert expected_errors==8
formatter_entry_counts=Counter()
original_format_report=reporting_module.format_report;original_format_estimate=estimate_module.format_estimate
def format_report(result,*,technical=False):
    formatter_entry_counts['format_report_technical'if technical else 'format_report_default']+=1
    return original_format_report(result,technical=technical)
def format_estimate(result):
    formatter_entry_counts['format_estimate']+=1
    return original_format_estimate(result)
reporting_module.format_report=format_report;estimate_module.format_estimate=format_estimate
def preserve_failure(error_type,error,trace):
    payload={'scope':'Third085 phase, remaining573 only; no Qt/Wine',
        'fresh_public_calls_in_phase3':fresh_calls,'previous_saved_public_calls':581,
        'completed_asserted_cases':len(rows),'completed_section_counts':dict(counts),
        'formatter_text_requests_in_phase3':formatter_requests,'formatter_entries_in_phase3':dict(formatter_entry_counts),
        'expected_existing_errors_completed':expected_errors,
        'source_hashes_before':before,'source_hashes_after':hashes(),
        'current_case':globals().get('case'),'current_input':globals().get('args'),
        'current_result':globals().get('result'),'current_visible_report':globals().get('text'),
        'current_report_texts':globals().get('report_texts'),'completed_records':rows,
        'error_type':error_type.__name__,'error':str(error),
        'traceback':''.join(traceback.format_exception(error_type,error,trace)),
        'GUI_executed':False,'Wine_executed':False}
    raw=gzip.compress(json.dumps(payload,ensure_ascii=False,allow_nan=False).encode(),mtime=0)
    with (HERE/'public-schema-remaining573085-failure.json.gz').open('xb')as out:out.write(raw)
    sys.__excepthook__(error_type,error,trace)
sys.excepthook=preserve_failure
for case in cases[581:]:
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
assert fresh_calls==573 and len(rows)==1154 and expected_errors==24 and hashes()==before
assert formatter_requests==1671 and formatter_entry_counts=={'format_estimate':557,'format_report_default':1114,'format_report_technical':557}
assert qualification_helper_calls==264
all_formatter_entries=Counter(first['formatter_entry_counts'])+Counter(second['formatter_entries_in_resume'])+formatter_entry_counts
receipt={'scope':'1154 new085 distinct UI-state design records,69+512+573 APIrequests; all earlier581 outputs reused strictly; no GUI/Wine proof',
    'calls':1154,'case_design_records':1154,'unique_requested_calculation_inputs':1086,
    'intentional_technical_checkbox_state_pairs_with_equal_API_input':68,
    'sections':dict(counts),'successful_result_rows':1130,'expected_existing_error_rows':24,
    'formatter_text_requests':first['formatter_text_requests']+second['formatter_text_requests_in_resume']+formatter_requests,
    'formatter_entry_counts':dict(all_formatter_entries),'actual_formatter_function_entries':sum(all_formatter_entries.values()),
    'estimate_dispatcher_delegates_to_default_report':True,'saved_report_texts_per_successful_result':['estimate','default','technical'],
    'external_contract_qualification_helper_calls_for_original_request_results':216+qualification_helper_calls,
    'saved581_reassertion_qualification_data_helper_calls':216,
    'source_drift':[],'source_hashes':before,'records':rows,'GUI_executed':False,'Wine_executed':False,
    'root_commit':freeze['base_commit'],
    'first_preflight_candidate_runner_sha256':first['candidate_runner_sha256'],
    'corrected_pending_runner_sha256':hashlib.sha256((HERE/'wine-ui-smoke-085.py').read_bytes()).hexdigest(),
    'actual_API_call_attribution':{'initial_system_interpreter_import_failure_calls':0,
        'first_preflight_calls':69,'remaining_only_phase2_calls':512,'remaining_only_phase3_calls':573,
        'total_actual_calls':1154,'saved69_reasserted_without_API':69,'saved581_reasserted_without_API':581,
        'previous_completed_case_request_repeated_for_retry':0,'old3063_cases_repeated':0,
        'two_distinct_contract_counterexamples_retained':True,
        'same_problem_retry_count':{'mechanist_top_healing_shape':1,'processed_enemy_id_key':1}},
    'strict_saved69_reuse_proof_sha256':hashlib.sha256((HERE/'saved69-reassertion085.json').read_bytes()).hexdigest(),
    'strict_saved581_reuse_proof_sha256':hashlib.sha256((HERE/'saved581-reassertion085.json').read_bytes()).hexdigest()}
assert receipt['formatter_text_requests']==3390 and receipt['actual_formatter_function_entries']==4520
assert Counter(row['section']for row in rows)=={81:136,82:216,83:450,84:88,85:264}
raw=gzip.compress(json.dumps(receipt,ensure_ascii=False,allow_nan=False).encode(),mtime=0)
with (HERE/'public-schema-final-085.json.gz').open('xb')as out:out.write(raw)
summary={k:v for k,v in receipt.items()if k not in ('source_hashes','records')};summary['full_receipt_sha256']=hashlib.sha256(raw).hexdigest()
with (HERE/'public-schema-final-085-summary.json').open('x')as out:json.dump(summary,out,ensure_ascii=False,indent=2)
print(json.dumps(summary,ensure_ascii=False))
