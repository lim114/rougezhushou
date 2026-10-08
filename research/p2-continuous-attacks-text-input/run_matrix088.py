"""One captured side of the fixed 60-pair plan; no repeat or random replacement."""
from pathlib import Path
import argparse,copy,gzip,hashlib,json,sys
parser=argparse.ArgumentParser();parser.add_argument('side',choices=('baseline','draft'));a=parser.parse_args()
OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(OUT/a.side))
def typed(v):
    if isinstance(v,dict):return {'type':'dict','items':[[typed(k),typed(x)] for k,x in v.items()]}
    if isinstance(v,(list,tuple)):return {'type':type(v).__name__,'items':[typed(x) for x in v]}
    if isinstance(v,float):return {'type':'float','hex':v.hex()}
    return {'type':type(v).__name__,'value':v}
def canon(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)
def native_sha(v):return hashlib.sha256(canon(typed(v)).encode()).hexdigest()
from rouge.catalog import catalog
from rouge.damage import calculate_damage
from rouge.estimate import format_estimate
from rouge.reporting import format_report
calls=0;accepted=0;requests=0;entries={'format_estimate':0,'format_report':0};trace=[]
def profile(frame,event,arg):
    code=frame.f_code
    if event=='call':
        if code is format_estimate.__code__:entries['format_estimate']+=1
        elif code is format_report.__code__:entries['format_report']+=1
    elif event=='return' and code.co_name=='observe_continuous_attacks' and code.co_filename.endswith('/rouge/condition_inputs.py'):
        value=frame.f_locals['value']
        trace.append({'caller_function':frame.f_back.f_code.co_name,'caller_line':frame.f_back.f_lineno,
                      'value':typed(value),'pending':frame.f_globals['_pending'].get()})
plan=json.loads((OUT/'matrix-plan088.json').read_text());assert len(plan)==60
cat_before=native_sha(catalog());decoded=hashlib.sha256();decoded_bytes=0
path=OUT/(a.side+'-public60.jsonl.gz')
sys.setprofile(profile)
with path.open('xb') as raw,gzip.GzipFile(fileobj=raw,mode='wb',mtime=0) as stream:
    for case in plan:
        args=copy.deepcopy(case['input']);before=typed(args);row=copy.deepcopy(case);trace=[]
        calls+=1
        try:result=calculate_damage(args)
        except Exception as exc:row.update(outcome='error',error_type=type(exc).__name__,error_message=str(exc))
        else:
            accepted+=1;native=typed(result)
            reports={'estimate':format_estimate(result),'user':format_report(result),'technical':format_report(result,technical=True)}
            requests+=3;row.update(outcome='accepted',result=result,result_typed=native,reports=reports)
        row.update(input_typed_before=before,input_typed_after=typed(args),actual_observer_return_trace=trace,
                   catalog_native_sha256_before=cat_before,catalog_native_sha256_after=native_sha(catalog()))
        assert row['input_typed_before']==row['input_typed_after']
        assert row['catalog_native_sha256_before']==row['catalog_native_sha256_after']
        data=json.dumps(row,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode()+b'\n'
        decoded.update(data);decoded_bytes+=len(data);stream.write(data)
sys.setprofile(None)
summary={'status':'CAPTURED_ONCE','side':a.side,'unique_inputs':60,'actual_public_calls':calls,'accepted':accepted,
    'errors':calls-accepted,'explicit_report_requests':requests,'explicit_format_estimate_requests':accepted,
    'explicit_format_report_requests':accepted*2,'instrumented_format_function_entries':entries,
    'format_estimate_internal_default_format_report_delegation_included_in_entries':True,
    'caller_catalog_native_unchanged':True,'explicit_catalog_native_isolation_cache_reads':61,
    'explicit_prepare_core_selected_talents_calls':0,'tests':0,'Qt':0,'Wine':0,
    'gzip_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'gzip_bytes':path.stat().st_size,
    'decoded_sha256':decoded.hexdigest(),'decoded_bytes':decoded_bytes,
    'plan_sha256':hashlib.sha256((OUT/'matrix-plan088.json').read_bytes()).hexdigest(),
    'formatter_derived_unmeasured_entries_claimed':False,'new_phase_inputs_injected':False}
(OUT/(a.side+'-public60-summary.json')).write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(summary,ensure_ascii=False))
