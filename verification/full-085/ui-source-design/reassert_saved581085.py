"""Strictly reassert all581 saved requests; zero API/formatter,216 data helpers."""
import ast
import gzip
import hashlib
import json
import sys
from collections import Counter
from copy import deepcopy
from pathlib import Path

HERE=Path(__file__).resolve().parent;PACKAGE=HERE/'public-schema-085'
sys.path[:0]=[str(PACKAGE),str(HERE)];sys.dont_write_bytecode=True
from rouge.catalog import catalog
from rouge.operator_engine import selected_talents
from rouge.operator_options import OPTIONS
from cases085 import cases085
from public_contracts import (canonical085,require_warning_order085,require_susuro_checkbox085,
    require_neural_checkbox085,require_repeat_checkbox085,require_nearby_checkbox085)
def hashes():
    return {p.relative_to(PACKAGE).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted((PACKAGE/'rouge').rglob('*'))if p.is_file()and p.suffix in ('.py','.json')}

f1=HERE/'public-schema-final-085-failure.json.gz';f2=HERE/'public-schema-resume085-failure.json.gz'
raw1=f1.read_bytes();raw2=f2.read_bytes()
assert hashlib.sha256(raw1).hexdigest()=='513bb64717654c5c8b31cd69b437c66bf7b575377502520d7f74f39f8e142894'
assert hashlib.sha256(raw2).hexdigest()=='e64c99c83dff40e262ee616ca7b50cb54945c26674e24b1dafb903d107e0f7f8'
first=json.loads(gzip.decompress(raw1));saved=json.loads(gzip.decompress(raw2));before=hashes()
assert before==first['source_hashes_before']==first['source_hashes_after']==saved['source_hashes_before']==saved['source_hashes_after']
assert before==json.loads((HERE/'public-source-freeze-085.json').read_bytes())['source_sha256']
assert saved['fresh_public_calls_in_resume']==512 and len(saved['completed_records'])==580
assert saved['completed_records'][:68]==first['completed_records']
assert saved['completed_records'][68]['result']==first['current_result']
assert saved['completed_records'][68]['report_texts']==first['current_report_texts']
tree=ast.parse((HERE/'resume_public_schema085.py').read_bytes())
functions=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in ('prepared_input','require_contract')]
assert len(functions)==2
namespace=globals().copy();namespace.update({'controls':{},'qualification_helper_calls':0})
exec(compile(ast.Module(body=functions,type_ignores=[]),'unchanged-pure-contract-dispatch085','exec'),namespace)
prepare=namespace['prepared_input'];require=namespace['require_contract']
cases=cases085();assert cases[580]==saved['current_case']
records=deepcopy(saved['completed_records']);current=saved['current_case']
records.append({'section':current['section'],'context':current['context'],'input':saved['current_input'],
    'result':saved['current_result'],'visible_report':saved['current_visible_report'],
    'report_texts':saved['current_report_texts'],'all_three_texts_preserve_result_bytes':True})
fingerprints=[];errors=0
for index,row in enumerate(records):
    case=cases[index];assert row['section']==case['section']and row['context']==case['context']
    assert canonical085(row['input'])==canonical085(prepare(case))
    prior=canonical085(row)
    if case.get('expected_error'):
        errors+=1
        assert row['actual_error_type']=='ValueError'and row['actual_error']==row['expected_error']==case['expected_error']
        assert row['result']is None and row['report_texts']is None and row['visible_report']==case['expected_error']
    else:
        texts=row['report_texts'];assert set(texts)=={'estimate','default','technical'}
        assert all(type(v)is str for v in texts.values())and texts['estimate']==texts['default']
        assert row['visible_report']==texts['technical'if case.get('technical',False)else 'default']
        require(case,row['input'],row['result'],row['visible_report'])
    assert canonical085(row)==prior
    fingerprints.append({'case_index':index,'section':row['section'],'record_canonical_sha256':hashlib.sha256(prior.encode()).hexdigest()})
assert len(records)==581 and errors==8 and namespace['qualification_helper_calls']==216 and hashes()==before
receipt={'status':'PASS_STRICT_SAVED_581_NO_NEW_API_OR_FORMATTER',
    'root_commit':'2dfd9fa2c9a62db0112bc0fb98cd23123dd3b48b',
    'saved_passed_records_reasserted':580,'current_saved_counterexample_reasserted':1,
    'saved_expected_old_errors':8,'saved_successful_results':573,
    'all580_record_JSON_unchanged':True,'current_result_and_all_three_texts_unchanged':True,
    'first68_and_first_counterexample_unchanged_again':True,
    'API_calls':0,'formatter_calls':0,'external_contract_selected_talents_data_helper_calls':216,
    'source_hashes_before':before,'source_hashes_after':hashes(),'record_fingerprints':fingerprints,
    'first_failure_sha256':hashlib.sha256(raw1).hexdigest(),'second_failure_sha256':hashlib.sha256(raw2).hexdigest(),
    'remaining_requests':573,'Qt_executed':False,'Wine_executed':False}
with (HERE/'saved581-reassertion085.json').open('x')as out:json.dump(receipt,out,ensure_ascii=False,indent=2);out.write('\n')
print(json.dumps({k:v for k,v in receipt.items()if k not in ('source_hashes_before','source_hashes_after','record_fingerprints')},ensure_ascii=False))
