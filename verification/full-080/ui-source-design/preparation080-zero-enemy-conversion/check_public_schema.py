"""API-only preview of future actual Qt contracts; not GUI/Wine execution."""
import gzip,hashlib,json,sys,traceback
from collections import Counter
from pathlib import Path
P=Path(__file__).resolve().parent;PACKAGE=Path(sys.argv[1]);LABEL=sys.argv[2]
sys.path.insert(0,str(PACKAGE));sys.dont_write_bytecode=True
from rouge.damage import calculate_damage
from rouge.operator_options import OPTIONS
from rouge.reporting import format_report
from cases080 import cases080
from public_contracts import canonical080,require_haruka080,require_aglna080,require_aglna_selected080,require_mantra080,require_medical_amiya080,require_medical_trait080
def hashes():
 return {p.relative_to(PACKAGE).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
  for p in sorted((PACKAGE/'rouge').rglob('*'))if p.is_file()and p.suffix in('.py','.json')}
before=hashes();rows=[];counts=Counter();controls={};fresh_calls=0
def save_failed_preflight(error_type,error,trace):
 payload={'scope':'Preserved failed API-only design preflight; no Qt/Wine execution',
  'gui_executed':False,'wine_executed':False,'fresh_public_calls':fresh_calls,
  'completed_asserted_cases':len(rows),'completed_section_counts':dict(counts),
  'source_hashes_before':before,'source_hashes_after':hashes(),
  'current_case':globals().get('case'),'current_input':globals().get('args'),
  'current_result':globals().get('result'),'completed_records':rows,
  'error_type':error_type.__name__,'error':str(error),
  'traceback':''.join(traceback.format_exception(error_type,error,trace))}
 raw=gzip.compress(json.dumps(payload,ensure_ascii=False,allow_nan=False).encode(),mtime=0)
 with (P/f'public-schema-{LABEL}-failure.json.gz').open('xb')as out:out.write(raw)
 summary={k:v for k,v in payload.items()if k not in('source_hashes_before','source_hashes_after','current_result','completed_records')}
 summary['full_receipt_sha256']=hashlib.sha256(raw).hexdigest()
 with (P/f'public-schema-{LABEL}-failure-summary.json').open('x')as out:json.dump(summary,out,ensure_ascii=False,indent=2)
 sys.__excepthook__(error_type,error,trace)
sys.excepthook=save_failed_preflight
for case in cases080():
 requested=case['input'];args={k:default for k,label,default,maximum,skills in OPTIONS.get(requested['operator'],[])if requested['skill']in skills}
 args.update(requested);original=canonical080(args)
 fresh_calls+=1;result=None
 result=calculate_damage(args);text=format_report(result);assert canonical080(args)==original
 if case['section']==76:
  key=canonical080({k:v for k,v in args.items()if k!='bubble_bursts'})
  if args['bubble_bursts']==0:controls[key]=result
  assert key in controls
  require_haruka080(result,args,text,controls[key])
 elif case['section']==77:
  key=canonical080({k:v for k,v in args.items()if k!='enemy_weight'})
  if args.get('target_enemy'):
   if args['enemy_weight']==0:controls[key]=result
   require_aglna_selected080(result,args,text,controls[key],case['expected_reference_mass'])
  else:
   control=controls.setdefault(key,{})
   if args['enemy_weight']==0:control['light']=result
   if args['enemy_weight']==4:control['heavy']=result
   require_aglna080(result,args,text,control)
 elif case['section']==78:
  key=canonical080({k:v for k,v in args.items()if k!='palsy_triggers'})
  if args['palsy_triggers']==0:controls[key]=result
  require_mantra080(result,args,text,controls[key])
 elif case['section']==79:
  require_medical_amiya080(result,args,text)
 elif case['section']==80:
  require_medical_trait080(result,args,text,case['expected_trait_ratio'])
 else:raise AssertionError('Unsealed section')
 rows.append({'section':case['section'],'context':case['context'],'input':args,'result':result,'visible_report':text})
 counts[case['section']]+=1
assert hashes()==before
receipt={'scope':'Public API-only planned Qt contracts; no GUI/Wine proof','gui_executed':False,'wine_executed':False,
 'calls':len(rows),'sections':dict(counts),'source_drift':[],'source_hashes':before,'records':rows}
raw=gzip.compress(json.dumps(receipt,ensure_ascii=False,allow_nan=False).encode(),mtime=0)
(P/f'public-schema-{LABEL}.json.gz').write_bytes(raw)
summary={k:v for k,v in receipt.items()if k not in('source_hashes','records')};summary['full_receipt_sha256']=hashlib.sha256(raw).hexdigest()
(P/f'public-schema-{LABEL}-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(summary,ensure_ascii=False))
