"""Root-authorized 16 calls once; original values, native trees and three texts."""
import copy
import gzip
import hashlib
import json
import sys
from pathlib import Path

OUT=Path(__file__).resolve().parent
REPO=Path('/workspace/rougezhushou')
canon=lambda v:json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)


def typed(v):
    if isinstance(v,dict):return {'type':'dict','items':[[typed(k),typed(x)] for k,x in v.items()]}
    if isinstance(v,(list,tuple)):return {'type':type(v).__name__,'items':[typed(x) for x in v]}
    if isinstance(v,float):return {'type':'float','hex':v.hex()}
    return {'type':type(v).__name__,'value':v}


def same_sources():
    static=json.loads((OUT/'continuous-condition-static088.json').read_bytes())
    for row in static['source_index']+static['curated_profile_sources']:
        data=Path(row['source_path']).read_bytes()
        assert len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['sha256'],row['source_path']


same_sources()
cases=json.loads((OUT/'continuous-public-plan16.json').read_bytes());assert len(cases)==16
assert len({canon(typed(r['input'])) for r in cases})==16
sys.path.insert(0,str(REPO))
from rouge.catalog import catalog
from rouge.damage import calculate_damage
from rouge.estimate import format_estimate
from rouge.reporting import format_report

old_catalog=hashlib.sha256(canon(typed(catalog())).encode()).hexdigest()
calls=accepted=errors=requests=0;decoded=hashlib.sha256();rawbytes=0
path=OUT/'public-source16.jsonl.gz'
with path.open('xb') as raw,gzip.GzipFile(fileobj=raw,mode='wb',mtime=0) as stream:
    for case in cases:
        args=copy.deepcopy(case['input']);before=typed(args);row=copy.deepcopy(case)
        row['input_typed_before']=before
        calls+=1
        try:result=calculate_damage(args)
        except Exception as exc:
            errors+=1;row.update(outcome='error',error_type=type(exc).__name__,error_message=str(exc))
        else:
            accepted+=1;native=typed(result)
            reports={'estimate':format_estimate(result),'user':format_report(result),'technical':format_report(result,technical=True)}
            requests+=3;row.update(outcome='accepted',result=result,result_typed=native,reports=reports)
        row['input_typed_after']=typed(args)
        row['catalog_native_sha256_before']=old_catalog
        row['catalog_native_sha256_after']=hashlib.sha256(canon(typed(catalog())).encode()).hexdigest()
        assert canon(before)==canon(row['input_typed_after']) and row['catalog_native_sha256_after']==old_catalog
        data=json.dumps(row,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode()+b'\n'
        stream.write(data);decoded.update(data);rawbytes+=len(data)
assert calls==16
same_sources()
receipt={'status':'CAPTURED_SOURCE_ONLY','actual_public_calls':calls,'accepted':accepted,'old_errors':errors,
         'explicit_report_requests':requests,'explicit_format_estimate_requests':accepted,'explicit_format_report_requests':accepted*2,
         'formatter_function_entries_or_internal_delegation_instrumented':False,'derived_entry_count_claimed_measured':False,
         'explicit_catalog_native_isolation_cache_reads':17,'new_explicit_prepare_core_selected_talents_calls':0,
         'whole_native_tree_before_JSON':True,'caller_catalog_native_unchanged':True,'source_hashes_before_after_unchanged':True,
         'gzip_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'gzip_bytes':path.stat().st_size,
         'decoded_sha256':decoded.hexdigest(),'decoded_bytes':rawbytes,'remaining_failed_cases_refilled':False,
         'scope':'Existing current86 product source reproduction only; no product draft, clock or mechanics changes.',
         'tests':0,'Qt':0,'Wine':0,'tracked_edits':0}
(OUT/'public-source16-summary.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(receipt,ensure_ascii=False))
