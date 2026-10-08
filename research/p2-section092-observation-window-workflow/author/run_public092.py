"""One variant, four authorized public entries; profile observations add no API calls."""
import argparse
from copy import deepcopy
import gzip
import hashlib
import json
import sys
import traceback
from pathlib import Path

sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
REPO=Path('/workspace/rougezhushou')
sys.path.insert(0,str(HERE))
from native_codec092 import canonical,decode,encode


def sha(raw):return hashlib.sha256(raw).hexdigest()


def dump_gzip(path,obj):
    raw=(json.dumps(obj,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n').encode()
    path.write_bytes(gzip.compress(raw,mtime=0))
    return {'path':str(path),'compressed_bytes':path.stat().st_size,'compressed_sha256':sha(path.read_bytes()),
            'decoded_bytes':len(raw),'decoded_sha256':sha(raw)}


parser=argparse.ArgumentParser();parser.add_argument('--variant',choices=('baseline','draft'),required=True)
args=parser.parse_args();variant=args.variant
inventory=json.loads((HERE/'maintained730-git-and-current-hashes092.json').read_text())
assert inventory['file_count']==730
for item in inventory['files']:
    raw=Path(item['source_path']).read_bytes();assert len(raw)==item['bytes'] and sha(raw)==item['sha256'],item['source_path']
config=json.loads((HERE/'public-inputs092.json').read_text());cases=config['cases'];assert len(cases)==4
saved=HERE/'saved';saved.mkdir(exist_ok=True)
context={'phase':'bootstrap','case_id':None,'external_formatter_request':None}
ledger={'actual_public_entries':0,'external_formatter_requests':[],
        'actual_formatter_entries':[],'observed_cached_function_returns':[],
        'explicit_external_project_helper_calls':0,'Qt':0,'Wine':0,'tests':0}
caches={}


def observer(frame,event,arg):
    module=frame.f_globals.get('__name__','');name=frame.f_code.co_name
    if not module.startswith('rouge.'):return
    if event=='call':
        if module=='rouge.damage' and name=='calculate_damage':
            ledger['actual_public_entries']+=1
            ledger.setdefault('public_entry_trace',[]).append({'case_id':context['case_id'],'phase':context['phase']})
        if (module,name) in (('rouge.estimate','format_estimate'),('rouge.reporting','format_report')):
            ledger['actual_formatter_entries'].append({'case_id':context['case_id'],
                'request':context['external_formatter_request'],'module':module,'function':name,
                'technical':frame.f_locals.get('technical') if name=='format_report' else None})
    elif event=='return' and isinstance(arg,(dict,list)):
        function=frame.f_globals.get(name)
        underlying=getattr(function,'__wrapped__',None)
        if (hasattr(function,'cache_info') and getattr(underlying,'__code__',None) is frame.f_code):
            key=module+'.'+name
            ledger['observed_cached_function_returns'].append({'cache':key,'case_id':context['case_id'],'phase':context['phase']})
            if key not in caches:caches[key]={'object':arg,'first':encode(arg),'first_phase':context['phase'],'first_case_id':context['case_id']}


sys.setprofile(observer)
sys.path.insert(0,str(REPO))
import rouge.reporting as reporting
if variant=='draft':
    candidate=HERE/'candidate/rouge/reporting.py'
    exec(compile(candidate.read_bytes(),str(candidate),'exec'),reporting.__dict__)
from rouge.damage import calculate_damage
from rouge.estimate import format_estimate

receipts=[]
status='PASS'
for case in cases:
    scenario=deepcopy(case['input']);context.update(phase='public',case_id=case['id'],external_formatter_request=None)
    before=encode(scenario);input_json_before=json.dumps(scenario,ensure_ascii=False,separators=(',',':'),allow_nan=False)
    record={'variant':variant,'case_id':case['id'],'input_before':before,'input_JSON_before':input_json_before,
            'result_native_tree':None,'result_JSON':None,'texts':{},'error':None}
    try:
        result=calculate_damage(scenario)
        native=encode(result);assert encode(decode(native))==native
        record['result_native_tree']=native
        record['result_JSON']=json.dumps(result,ensure_ascii=False,separators=(',',':'),allow_nan=False)
        for mode in ('estimate','default','technical'):
            context.update(phase='formatter',external_formatter_request=mode)
            ledger['external_formatter_requests'].append({'case_id':case['id'],'mode':mode})
            if mode=='estimate':text=format_estimate(result)
            elif mode=='default':text=reporting.format_report(result)
            else:text=reporting.format_report(result,technical=True)
            record['texts'][mode]=text
        record['result_after_formatters_native_tree']=encode(result)
        assert record['result_after_formatters_native_tree']==native
    except Exception as error:
        status='FAIL'
        record['error']={'type':type(error).__module__+'.'+type(error).__qualname__,
                         'message':str(error),'traceback':traceback.format_exc()}
    finally:
        context.update(phase='save',external_formatter_request=None)
        record['input_after']=encode(scenario)
        record['input_JSON_after']=json.dumps(scenario,ensure_ascii=False,separators=(',',':'),allow_nan=False)
        record['caller_unchanged']=record['input_after']==before and record['input_JSON_after']==input_json_before
        cache_state={key:{'native_tree_sha256':sha(canonical(encode(v['object'])).encode()),
                          'equal_first_native_tree':encode(v['object'])==v['first']} for key,v in caches.items()}
        record['observed_cache_state_after_call']=cache_state
        record['ledger_after_call']={'actual_public_entries':ledger['actual_public_entries'],
                                   'external_formatter_requests':len(ledger['external_formatter_requests']),
                                   'actual_formatter_entries':len(ledger['actual_formatter_entries'])}
        receipt=dump_gzip(saved/(variant+'-'+case['id']+'.json.gz'),record);receipts.append(receipt)
        if not record['caller_unchanged'] or any(not v['equal_first_native_tree'] for v in cache_state.values()):status='FAIL'
    if status!='PASS':break

sys.setprofile(None)
cache_complete={key:{'first_native_tree':v['first'],'final_native_tree':encode(v['object']),
                     'first_phase':v['first_phase'],'first_case_id':v['first_case_id'],
                     'equal_complete_native_tree':encode(v['object'])==v['first']} for key,v in caches.items()}
cache_receipt=dump_gzip(saved/(variant+'-observed-cache-complete.json.gz'),cache_complete)
ledger.update({'variant':variant,'status':status,'saved_records':receipts,'saved_cache':cache_receipt,
               'source_current_730_verified_before_run':True,
               'cache_scope':'First actual return of observed lru-cached dict/list data through bootstrap/public imports and calls; complete first/final native tree plus per-case equality. Cold initialization recorded, not claimed absent; no outside cache/helper calls. Cache-hit entry counts not measured.',
               'API_budget_maximum':4,'external_formatter_budget_maximum':12,
               'no_actual_Qt_or_app_import':True})
assert ledger['actual_public_entries']<=4 and len(ledger['external_formatter_requests'])<=12
(HERE/(variant+'-actual-ledger092.json')).write_text(json.dumps(ledger,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'variant':variant,'status':status,'actual_public_entries':ledger['actual_public_entries'],
                  'external_formatter_requests':len(ledger['external_formatter_requests']),
                  'actual_formatter_entries':len(ledger['actual_formatter_entries']),
                  'observed_cache_objects':len(caches),'saved_records':len(receipts)},ensure_ascii=False))
raise SystemExit(0 if status=='PASS' else 1)
