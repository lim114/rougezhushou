"""Exact whole-JSON/error comparison, with qualification derived from source and input, not a result flag."""
import gzip
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
ERROR={'type':'ValueError','message':'four_sui 不接受文本条件；请使用布尔值。'}
def read(name):
    with gzip.open(ROOT/name,'rt',encoding='utf-8') as source:return json.load(source)
base=read('baseline-matrix.json.gz')
draft=read('draft-matrix.json.gz')
assert base['cases'].keys()==draft['cases'].keys()
changed={};unchanged=0;old_errors=0
for name,before in base['cases'].items():
    after=draft['cases'][name]
    assert before['scenario']==after['scenario'],name
    args=before['scenario']
    is_qualified_text=(args['operator']=='char_2025_shu' and args.get('elite',2)==2
                       and isinstance(args.get('four_sui'),str))
    # Existing upstream validation retains its exact earlier errors.
    if is_qualified_text and before['outcome']['error'] is None:
        assert after['outcome']=={'result':None,'error':ERROR},name
        changed[name]={'scenario':args,'baseline_had_full_result':True,'new_error':ERROR}
    else:
        assert before==after,name
        unchanged+=1
        if before['outcome']['error'] is not None:old_errors+=1
assert len(changed)+unchanged==len(base['cases'])
receipt={'passed':True,'public_pairs':len(base['cases']),'public_calls_both_packages':2*len(base['cases']),
         'qualified_text_changed_to_explicit_errors':len(changed),'unchanged_complete_JSON_or_errors':unchanged,
         'preserved_old_error_outcomes':old_errors,'changed_cases':changed,
         'compatibility_policy':'Only raw str with actual qualified Shu E2 talent; every other full outcome identical.',
         'no_result_reference_flag_used_as_validation_oracle':True,
         'baseline_gzip_sha256':hashlib.sha256((ROOT/'baseline-matrix.json.gz').read_bytes()).hexdigest(),
         'draft_gzip_sha256':hashlib.sha256((ROOT/'draft-matrix.json.gz').read_bytes()).hexdigest()}
(ROOT/'matrix-comparison.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in receipt.items() if k!='changed_cases'},ensure_ascii=False))
