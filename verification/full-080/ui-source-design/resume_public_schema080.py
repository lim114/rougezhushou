"""Reuse unchanged-source saved1552 API results, execute only56 unrun designs."""
import gzip
import hashlib
import json
import sys
import traceback
from collections import Counter
from pathlib import Path

HERE=Path(__file__).resolve().parent
PACKAGE=HERE/'public-schema-080'
sys.path[:0]=[str(PACKAGE),str(HERE)]
sys.dont_write_bytecode=True
from rouge.damage import calculate_damage
from rouge.operator_options import OPTIONS
from rouge.reporting import format_report
from cases080 import cases080
from public_contracts import canonical080,require_medical_trait080

def hashes():
 return {p.relative_to(PACKAGE).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
  for p in sorted((PACKAGE/'rouge').rglob('*'))if p.is_file()and p.suffix in('.py','.json')}

saved_raw=(HERE/'public-schema-final-080-failure.json.gz').read_bytes()
assert hashlib.sha256(saved_raw).hexdigest()=='53e99996dcffe475f8074e7dbad4759da20c692fe457f2b95bc0eb86312f98cc'
saved=json.loads(gzip.decompress(saved_raw))
before=hashes()
assert before==saved['source_hashes_before']==saved['source_hashes_after']
assert before==json.loads((HERE/'public-source-freeze-080.json').read_text())['source_sha256']
designs=cases080();rows=saved['completed_records'];fresh_calls=0
assert len(rows)==1551 and saved['fresh_public_calls']==1552
assert designs[1551]==saved['current_case']
for index,row in enumerate(rows):
 case=designs[index];assert case['section']==row['section'] and case['context']==row['context']
 expected={k:default for k,label,default,maximum,skills in OPTIONS.get(case['input']['operator'],[])if case['input']['skill']in skills}
 expected.update(case['input']);assert canonical080(expected)==canonical080(row['input'])
case=saved['current_case'];args=saved['current_input'];result=saved['current_result']
text=format_report(result)
require_medical_trait080(result,args,text,case['expected_trait_ratio'])
rows.append({'section':case['section'],'context':case['context'],'input':args,'result':result,'visible_report':text})
counts=Counter(row['section']for row in rows)

def preserve_failure(error_type,error,trace):
 payload={'scope':'Resume API-only preflight failure; no Qt/Wine execution',
  'fresh_public_calls_in_resume':fresh_calls,'previous_saved_public_calls':1552,
  'completed_asserted_cases':len(rows),'current_case':globals().get('case'),
  'current_input':globals().get('args'),'current_result':globals().get('result'),
  'source_hashes_before':before,'source_hashes_after':hashes(),'completed_records':rows,
  'error_type':error_type.__name__,'error':str(error),
  'traceback':''.join(traceback.format_exception(error_type,error,trace))}
 raw=gzip.compress(json.dumps(payload,ensure_ascii=False,allow_nan=False).encode(),mtime=0)
 with (HERE/'public-schema-resume080-failure.json.gz').open('xb')as out:out.write(raw)
 sys.__excepthook__(error_type,error,trace)
sys.excepthook=preserve_failure
for case in designs[1552:]:
 requested=case['input'];args={k:default for k,label,default,maximum,skills in OPTIONS.get(requested['operator'],[])if requested['skill']in skills}
 args.update(requested);original=canonical080(args);result=None;fresh_calls+=1
 result=calculate_damage(args);text=format_report(result);assert canonical080(args)==original
 assert case['section']==80
 require_medical_trait080(result,args,text,case['expected_trait_ratio'])
 rows.append({'section':case['section'],'context':case['context'],'input':args,'result':result,'visible_report':text})
 counts[case['section']]+=1
assert hashes()==before and fresh_calls==56 and len(rows)==len(designs)==1608
receipt={'scope':'Public API-only planned Qt contracts;1551passed+1saved counterexample reasserted+56remaining new calls; no GUI/Wine proof',
 'gui_executed':False,'wine_executed':False,'calls':1608,'sections':dict(counts),
 'source_drift':[],'source_hashes':before,'records':rows,
 'actual_API_call_attribution':{'first_preflight':1552,'resume_unrun_only':56,'total_actual_calls':1608,
  'saved_completed_passed_reused':1551,'saved_counterexample_reasserted_without_API':1,
  'previous_completed_API_repeated':0,'first_failure_retained':True},
 'reuse_source_proof':'All125 package source hashes equal before/after first preflight and before/after resume and final clean root80 git blobs.'}
raw=gzip.compress(json.dumps(receipt,ensure_ascii=False,allow_nan=False).encode(),mtime=0)
with(HERE/'public-schema-final-080.json.gz').open('xb')as out:out.write(raw)
summary={k:v for k,v in receipt.items()if k not in('source_hashes','records')}
summary['full_receipt_sha256']=hashlib.sha256(raw).hexdigest()
with(HERE/'public-schema-final-080-summary.json').open('x')as out:json.dump(summary,out,ensure_ascii=False,indent=2)
print(json.dumps(summary,ensure_ascii=False))
