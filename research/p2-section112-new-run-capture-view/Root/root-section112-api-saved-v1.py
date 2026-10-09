"""Root reads both saved healthy API cells and all three complete formatters."""
import hashlib,json,sys
from pathlib import Path
B=Path('/workspace/.continuation');R=Path('/workspace/rougezhushou')
sys.path.insert(0,str(B/'section109-empty-target-original-probe-source-v1'))
from native_evidence import read_record,assert_native_equal as same,source_map
g=json.loads((B/'resume112-applied-source-v1.json').read_bytes());old=None;total=0
for phase in ('original','candidate'):
 d=B/f'section112-{phase}-api-actual-v1';assert (B/(d.name+'.exit-code')).read_bytes()==b'0\n'
 r=json.loads((d/'observations.json').read_bytes());assert r['phase']==phase and r['observation_complete'] and r['source_and_CORE_unchanged'] and r['consumer_error_count']==0
 assert r['actual_completed_cases']==2 and r['actual_public_calls']==8 and r['actual_native_records']==10
 values={}
 for ref in r['records']:
  v=read_record(d/'native',ref);same(v['before'],v['after'],'whole saved caller purity');total+=1
  if ref['kind']=='actual-public-consumer':assert v['error'] is None
  values[(ref['case'],ref['phase'])]=v
 for identity in ('mechanist-e1-level20','mechanist-e1-level30'):
  result=values[(identity,'calculate_damage')]['result']
  for fmt in ('format_estimate','format_report','format_report_technical'):same(values[(identity,fmt)]['before'],(result,),'whole formatter input')
 if old is not None:same(values,old,'complete original/candidate callers/results/errors/three full texts')
 old=values
assert source_map(R)==g['source_sha256']
for name,pin in g['source_additional_sha256'].items():assert hashlib.sha256((R/name).read_bytes()).hexdigest()==pin
p=B/'root-section112-api-saved-actual-v1.json';assert not p.exists();p.write_text(json.dumps({'passed':True,'workflow_complete':True,'source_drift':[],'native_records_decoded':total,'cases_per_phase':2,'three_full_texts_per_cell':True,'complete_return_and_callers_unchanged':True,'scope':'Healthy public cultivation API preservation; actual reset lifecycle is separately verified in the real window.'},indent=2)+'\n')
print(json.dumps({'passed':True,'native_records_decoded':total}))
