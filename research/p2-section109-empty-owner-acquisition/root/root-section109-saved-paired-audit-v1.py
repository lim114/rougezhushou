"""Root-only stdlib Saved evidence readback; imports no project code."""
import hashlib,importlib.util,json,pathlib
B=pathlib.Path('/workspace/.continuation'); HP=B/'section109-empty-target-original-probe-source-v1/native_evidence.py'
assert hashlib.sha256(HP.read_bytes()).hexdigest()=='f040258eddbb7ad624e547e2c422a3d432f7ffeae025b2576b625683ea43fe9a'
s=importlib.util.spec_from_file_location('saved_native',HP);h=importlib.util.module_from_spec(s);s.loader.exec_module(h)
proof={'kind':'ROOT_ACTUAL109_SAVED_PUBLIC_API_PAIRED_AUDIT','passed':False,'workflow_complete':False,'project_runtime_executed':False,'domains':[]}
for name in ['focused','permanent','instant']:
 dirs=[B/f'section109-{phase}-{name}-actual-v1' for phase in ['original','candidate']];receipts=[json.loads((d/'observations.json').read_text()) for d in dirs]
 for d,r in zip(dirs,receipts):
  assert (B/(d.name+'.exit-code')).read_text().strip()=='0' and r['source_and_CORE_unchanged'] and r['consumer_error_count']==0
  records=r.get('records',r.get('native_records'));assert len(records)==r['actual_native_records'];assert len(set(x['path'] for x in records))==len(records)
  index=[json.loads(line) for line in (d/'native/index.jsonl').read_text().splitlines()];assert index==records
 saved=[]
 for d,r in zip(dirs,receipts):saved.append([h.read_record(d/'native',m) for m in r.get('records',r.get('native_records'))])
 assert len(saved[0])==len(saved[1]);changed=[];same=[];callers=0
 for o,c,om,cm in zip(saved[0],saved[1],receipts[0].get('records',receipts[0].get('native_records')),receipts[1]['records']):
  assert om['case']==cm['case']; phase=om['phase'];case=om['case']
  if phase in ('calculate_damage','format_estimate','format_report'):
   assert phase==cm['phase'];assert o['error'] is None and c['error'] is None
   for v in (o,c):h.assert_native_equal(v['after'],v['before'],'full caller purity')
   h.assert_native_equal(o['before'],c['before'],'paired full caller graph');callers+=1
   if 'kwargs_before' in o:h.assert_native_equal(o['kwargs_before'],o['kwargs_after'],'original kwargs purity')
   try:h.assert_native_equal(o['result'],c['result'],'paired full returned value')
   except AssertionError:
    assert name!='permanent','109 must preserve permanent release/SP reference';changed.append({'case':case,'phase':phase})
   else:same.append({'case':case,'phase':phase})
  else:
   assert set(o)==set(c)
   h.assert_native_equal(o,c,'paired whole raw case caller')
 proof['domains'].append({'name':name,'cases':receipts[1]['actual_completed_cases'],'native_records_decoded':sum(map(len,saved)), 'full_callers_paired':callers,'whole_returned_values_identical':same,'whole_returned_values_changed':changed,'original_extra_kwargs_metadata_scope':name=='permanent','source_unchanged':True})
proof.update(passed=True,workflow_complete=True)
out=B/'root-section109-saved-paired-audit-v1.json'
with out.open('x') as f:json.dump(proof,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({x['name']:{'cases':x['cases'],'calls':x['full_callers_paired'],'same':len(x['whole_returned_values_identical']),'changed':x['whole_returned_values_changed']} for x in proof['domains']},ensure_ascii=False))
