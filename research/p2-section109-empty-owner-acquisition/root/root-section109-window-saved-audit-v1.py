"""Root Saved readback of actual completed prefixes, not full GUI acceptance."""
import hashlib,importlib.util,json,pathlib
B=pathlib.Path('/workspace/.continuation');P=B/'section109-empty-target-original-probe-source-v1/native_evidence.py'
assert hashlib.sha256(P.read_bytes()).hexdigest()=='f040258eddbb7ad624e547e2c422a3d432f7ffeae025b2576b625683ea43fe9a'
s=importlib.util.spec_from_file_location('native_saved',P);h=importlib.util.module_from_spec(s);s.loader.exec_module(h)
proof={'kind':'ROOT_ACTUAL109_WINDOW_PREFIX_SAVED_READBACK','passed':False,'workflow_complete':False,'full_candidate_window_workflow_passed':False,'source_drift':[],'project_runtime_executed':False,'windows':[]};data=[]
for name,expected_rows,primary in [('resume109-window-gold-v1',18,0),('resume109-window-candidate-v1',6,1),('resume109-window-candidate-v2',15,1)]:
 d=B/name;r=json.loads((d/'receipt.json').read_text());assert (B/(name+'.exit-code')).read_text().strip()==str(primary)
 assert r['source_drift']==[] and r['Qt_errors']==[] and r['source_before']==r['source_after'] and r['source_additional_before']==r['source_additional_after'] and len(r['rows'])==expected_rows
 if primary==0:assert r['passed'] and r['workflow_complete'] and len(r['windows'])==1
 else:assert not r['passed'] and not r['workflow_complete'] and r['failure']['type']=='AssertionError'
 decoded={m['path']:h.read_record(d/'records',m) for m in r['records']};assert len(decoded)==len(r['records']);assert set(decoded)=={p.name for p in (d/'records').iterdir() if p.is_file()}
 kinds={}
 for v in decoded.values():
  k=v['kind'];kinds[k]=kinds.get(k,0)+1
  if k in ['actual_calculate_result','actual_UI_step','actual_three_formatter_group']:h.assert_native_equal(v['after'],v['before'],k+' joint caller/state purity')
  assert k!='actual_calculate_exception'
 snap={row['id']:decoded[row['snapshot']['path']]['value'] for row in r['rows']};data.append((r,snap,decoded))
 for png in r['pngs']:
  raw=(d/png['path']).read_bytes();assert len(raw)==png['bytes'] and hashlib.sha256(raw).hexdigest()==png['sha256']
 proof['windows'].append({'name':name,'completed_rows':expected_rows,'completed_close_reload_records':len(r['windows']),'saved_records_decoded':len(decoded),'kind_counts':kinds,'original_primary_exit':primary,'source_unchanged':True})
old=data[0];new=data[2];paired=healthy=0
for row in new[0]['rows']:
 a=old[1][row['id']];b=new[1][row['id']];h.assert_native_equal(a['caller'],b['caller'],'paired full raw caller');h.assert_native_equal(a['state_and_disks'],b['state_and_disks'],'paired full state/disk');paired+=1
 if row['kind']=='healthy':h.assert_native_equal(a,b,'whole healthy Gold');healthy+=1
assert paired==15 and healthy==5
m=next(m for m in reversed(new[0]['records']) if m['case']=='empty-generic-snow' and m['kind']=='actual_calculate_result');v=new[2][m['path']];assert type(v['before']['args'][0]['snow_entries']) is int and v['before']['args'][0]['snow_entries']==0
skill=v['result']['estimate']['skill'];assert skill['total_damage']==0 and all(skill[k] is None for k in ['phase_damage','cycle_damage','recharge_seconds','cycle_seconds']);assert next(c for c in v['result']['components'] if c['name']=='施放伤害')['total']==0
assert len(new[0]['pngs'])==3
root=pathlib.Path('/workspace/rougezhushou');guard=json.loads((B/'resume109-applied-source-v1.json').read_text());assert h.source_map(root)==guard['source_sha256']
for name,sha in guard['source_additional_sha256'].items():assert hashlib.sha256((root/name).read_bytes()).hexdigest()==sha
third=B/'resume109-window-candidate-v3';assert not (third/'receipt.json').exists() and not (B/(third.name+'.exit-code')).exists();log=(B/(third.name+'.log')).read_text();assert 'X connection' in log and 'page fault' in log
proof.update(passed=True,workflow_complete=True,acceptance_scope='Strict Saved prefix readback only; full candidate UI workflow deferred after three attempts',full_healthy_Gold_pairs=healthy,full_raw_caller_and_state_disk_pairs=paired,png_hashes_verified=3,native_windows_verified=False,attempt3={'primary_exit':None,'completion_receipt':None,'native_records':len(list((third/'records').glob('*.pickle.gz'))),'reason':'exec-server transport disconnected; X display terminated; Wine page fault; no completion evidence'},deferred=['remaining gnosis and independent-token actual UI snapshots','candidate real close/direct RunState reload','fourth visual PNG','18-case complete candidate acceptance'])
with (B/'root-section109-window-saved-audit-v1.json').open('x') as f:json.dump(proof,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps(proof,ensure_ascii=False))
