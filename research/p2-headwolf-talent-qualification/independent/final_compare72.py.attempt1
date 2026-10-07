from pathlib import Path
import sys,json,gzip,hashlib,copy
sys.dont_write_bytecode=True
OUT=Path(__file__).parent
BASE=OUT/'frozen70-public';DRAFT=OUT/'draft72-independent'
freeze=json.loads((OUT/'freeze70-public.json').read_text())
for name,r in freeze['files'].items():
 b=(BASE/name).read_bytes();assert len(b)==r['bytes'] and hashlib.sha256(b).hexdigest()==r['sha256'],name
oldreceipt=json.loads((OUT/'headwolf-public-receipt.json').read_text())
packed=(OUT/'headwolf-public-cases.json.gz').read_bytes();raw=gzip.decompress(packed)
assert hashlib.sha256(raw).hexdigest()==oldreceipt['compression']['raw_sha256']
assert hashlib.sha256(packed).hexdigest()==oldreceipt['compression']['gzip_sha256']
baselines=json.loads(raw)
sys.path.insert(0,str(DRAFT))
from rouge.damage import calculate_damage
from rouge.estimate import format_estimate
strict=lambda x:json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)
results=[];unexpected=[];qualified_drift=[];e0_prethreshold_drift=[];post_e0_invalid=[];draft_age_groups={}
for row in baselines:
 scenario=row['scenario']
 try:
  r=calculate_damage(copy.deepcopy(scenario));outcome={'result':r,'report':format_estimate(r)}
 except Exception as e:outcome={'error':{'type':type(e).__name__,'message':str(e)}}
 changed=strict(row['outcome'])!=strict(outcome)
 expectation='unchanged qualified or no-bonus case'
 if scenario['elite']==0 and scenario['deployment_elapsed_seconds']>=60:
  expectation='remove ineligible E0 headwolf bonus only'
  if 'result' not in outcome:unexpected.append(scenario)
 elif changed:unexpected.append(scenario)
 if scenario['elite']>0 and changed:qualified_drift.append(scenario)
 if scenario['elite']==0:
  key=strict({k:v for k,v in scenario.items() if k!='deployment_elapsed_seconds'})
  draft_age_groups.setdefault(key,[]).append(outcome)
  if 'result' in outcome:
   drones=[c for c in outcome['result']['components'] if c['name']=='浮游单元']
   if any(c['hits']!=2 for c in drones):post_e0_invalid.append(scenario)
 results.append({'scenario':scenario,'expectation':expectation,'changed':changed,'baseline_outcome':row['outcome'],'draft_outcome':outcome})
age_invariance=all(all(strict(o)==strict(values[0]) for o in values[1:]) for values in draft_age_groups.values())
raw=strict(results).encode();packed=gzip.compress(raw,mtime=0)
(OUT/'final72-paired-outcomes.json.gz').write_bytes(packed)
receipt={'baseline_head':freeze['head'],'patch_sha256':'b92662a951f4dc66389f582c33438aa1229639e6d4b4b05bb440f9ab2d2e50eb','scenarios':len(results),
 'actual_public_calls':{'discovery_baseline_reused_after_source_and_bytes_recheck':len(baselines),'final_draft':len(results),'matrix_total':len(baselines)+len(results)},
 'strict_json_outcome_changed':sum(r['changed'] for r in results),'strict_json_outcome_unchanged':sum(not r['changed'] for r in results),
 'qualified_e1_e2_pairs':sum(r['scenario']['elite']>0 for r in results),'qualified_drift':qualified_drift,'unexpected_change_or_error':unexpected,
 'e0_reference_units_still_2':not post_e0_invalid,'e0_post_invalid':post_e0_invalid,'e0_age_groups':len(draft_age_groups),'draft_whole_outcome_age_invariance_e0':age_invariance,
 'comparison':'Strict sorted JSON serialization including int/float, all result fields, report strings and complete exception type/message',
 'compression':{'file':'final72-paired-outcomes.json.gz','gzip_sha256':hashlib.sha256(packed).hexdigest(),'gzip_bytes':len(packed),'raw_sha256':hashlib.sha256(raw).hexdigest(),'raw_bytes':len(raw),'gzip_roundtrip_verified':gzip.decompress(packed)==raw},
 'new_independent_clock_claim':False,'private_or_native_data_used':False}
(OUT/'final72-matrix-receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(receipt,ensure_ascii=False))
assert not unexpected and not qualified_drift and not post_e0_invalid and age_invariance
