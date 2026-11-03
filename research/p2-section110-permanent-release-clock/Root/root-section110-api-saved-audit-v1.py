"""Root-only complete Saved public API readback, no project import."""
import hashlib,importlib.util,json,pathlib
B=pathlib.Path('/workspace/.continuation');P=B/'section109-empty-target-original-probe-source-v1/native_evidence.py';assert hashlib.sha256(P.read_bytes()).hexdigest()=='f040258eddbb7ad624e547e2c422a3d432f7ffeae025b2576b625683ea43fe9a'
s=importlib.util.spec_from_file_location('saved_native',P);h=importlib.util.module_from_spec(s);s.loader.exec_module(h)
proof={'kind':'ROOT_ACTUAL110_COMPLETE_PUBLIC_API_SAVED_PAIRS','passed':False,'workflow_complete':False,'source_drift':[],'project_runtime_executed':False,'domains':[]}
for domain,oname in [('permanent','section110-original-permanent-actual-v2'),('supplement','section110-original-supplement-actual-v1')]:
 ds=[B/oname,B/f'section110-candidate-{domain}-actual-v1'];receipts=[json.loads((d/'observations.json').read_text()) for d in ds]
 data=[]
 for d,r in zip(ds,receipts):
  assert (B/(d.name+'.exit-code')).read_bytes()==b'0\n';assert r['source_and_CORE_unchanged'] and r['consumer_error_count']==0 and r['observation_complete']
  assert [json.loads(x) for x in (d/'native/index.jsonl').read_text().splitlines()]==r['records'];data.append([h.read_record(d/'native',m) for m in r['records']])
 equal=changed=0;calcs=0;sp=0;notes=0
 for old,new,om,nm in zip(*data,receipts[0]['records'],receipts[1]['records']):
  assert om['case']==nm['case'] and om['phase']==nm['phase']
  if nm['phase'] in ('calculate_damage','format_estimate','format_report'):
   assert old['error'] is None and new['error'] is None
   for v in (old,new):h.assert_native_equal(v['before'],v['after'],'caller purity')
   try:h.assert_native_equal(old['result'],new['result'],'whole returned value')
   except AssertionError:changed+=1
   else:equal+=1
   if nm['phase']=='calculate_damage':
    calcs+=1;h.assert_native_equal(old['before'],new['before'],'paired whole numeric caller');o=old['result'];n=new['result'];caller=new['before'][0]
    for key in ['initial_seconds','recharge_seconds','duration_seconds','cycle_seconds']:
     h.assert_native_equal(o['estimate']['skill'][key],n['estimate']['skill'][key],'whole original SP clock scalar')
    assert ('sp_events' in o['estimate'])==('sp_events' in n['estimate'])
    if 'sp_events' in o['estimate']:h.assert_native_equal(o['estimate']['sp_events'],n['estimate']['sp_events'],'whole SP reference')
    sp+=1
    if caller['timing_mode']=='frames' or caller.get('timing',{}).get('target_windows')!=[]:h.assert_native_equal(o,n,'outside110 impact change domain')
    if caller['skill']==1:
     h.assert_native_equal(o['components'],n['components'],'independent note components retained');h.assert_native_equal(o['unbound_cast_reference'],n['unbound_cast_reference'],'whole unbound note reference');assert n['total_damage'] is None;notes+=1
    elif caller.get('timing',{}).get('target_windows')==[]:
     assert n['total_damage']==0 and all(c['total']==0 and c['hits']==0 for c in n['components'])
  else:h.assert_native_equal(old,new,'whole raw caller input')
 proof['domains'].append({'domain':domain,'cases':calcs,'SP_clock_pairs':sp,'S1_note_full_reference_pairs':notes,'whole_returned_values_equal':equal,'whole_returned_values_changed':changed,'native_decoded':sum(map(len,data)),'classified_callbacks_scope':'Current offline_scope keeps received_sp/event_sp relics reference-only; these literal inputs do not activate public callbacks'})
proof.update(passed=True,workflow_complete=True)
with (B/'root-section110-api-saved-audit-v1.json').open('x') as f:json.dump(proof,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps(proof,ensure_ascii=False))
