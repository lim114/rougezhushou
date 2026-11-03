from pathlib import Path
import json,collections,datetime
base=Path(__file__).parent
before=json.loads((base/'baseline-matrix060.json').read_text());after=json.loads((base/'draft-matrix060.json').read_text())
assert len(before['records'])==len(after['records'])
counts=collections.Counter();changes=[];errors=[];bad=[]
for a,b in zip(before['records'],after['records']):
 assert a['group']==b['group'] and a['request']==b['request']
 group=a['group'];counts[group]+=1
 if 'error' in a or 'error' in b:
  if a.get('error')!=b.get('error'):bad.append({'problem':'error mismatch','before':a,'after':b})
  errors.append({'request':a['request'],'same_error':a.get('error')==b.get('error'),'error':a.get('error')});continue
 eligible=group.startswith('eligible')
 if not eligible:
  if a['full_result_sha256']!=b['full_result_sha256']:bad.append({'problem':'control output changed','before':a,'after':b})
  assert b['reference'] is None
 else:
  changes.append({'request':a['request'],'before':a['resource_values'],'after':b['resource_values']})
  if a['direct_values']!=b['direct_values']:bad.append({'problem':'skill/window/static changed','before':a,'after':b})
  assert a['relic_resolution_sha256']==b['relic_resolution_sha256']
  ref=b['reference'];assert ref['interval_seconds_parameter']==4 and ref['sp_per_pulse_parameter']==1
  assert b['resource_values']['sp_recovery_per_second']==a['resource_values']['sp_recovery_per_second']-.25
  for field in ('recharge_seconds','cycle_seconds','cycle_damage','cycle_healing','cycle_dps','cycle_hps'):assert b['resource_values'][field] is None
  full=a['resource_values']['initial_seconds']==0
  if full:assert b['resource_values']['initial_seconds']==0
  else:assert b['resource_values']['initial_seconds'] is None
  assert b['recharge_streams']==[] and b['scope_synced']
report={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'paired_scenarios':len(before['records']),'public_calls':before['calls']+after['calls'],
 'groups':counts,'same_prior_errors':errors,'counterexamples':bad,'eligible_resource_changes':changes,
 'all_controls_full_json_unchanged':not bad,'all_direct_skill_window_static_values_unchanged':not bad}
(base/'matrix-comparison060.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ('eligible_resource_changes','same_prior_errors')},ensure_ascii=False));assert not bad
