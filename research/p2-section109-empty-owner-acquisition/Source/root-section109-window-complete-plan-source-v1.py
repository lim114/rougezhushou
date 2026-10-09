"""Root-only Saved window evidence readback, no project imports or runtime."""
import hashlib,importlib.util,json,pathlib
B=pathlib.Path('/workspace/.continuation');P=B/'section109-empty-target-original-probe-source-v1/native_evidence.py'
assert hashlib.sha256(P.read_bytes()).hexdigest()=='f040258eddbb7ad624e547e2c422a3d432f7ffeae025b2576b625683ea43fe9a'
s=importlib.util.spec_from_file_location('native_saved',P);h=importlib.util.module_from_spec(s);s.loader.exec_module(h)
proof={'kind':'ROOT_ACTUAL109_WINDOW_SAVED_READBACK','passed':False,'workflow_complete':False,'source_drift':[],'project_runtime_executed':False,'windows':[]}
results=[]
for name in ['resume109-window-gold-v1','resume109-window-candidate-v3']:
 d=B/name; r=json.loads((d/'receipt.json').read_text());assert (B/(name+'.exit-code')).read_bytes()==b'0\n'
 assert r['passed'] and r['workflow_complete'] and r['Qt_errors']==[] and r['source_drift']==[]
 assert r['source_before']==r['source_after'] and r['source_additional_before']==r['source_additional_after']
 assert len(r['rows'])==18 and len(r['windows'])==1
 decoded={m['path']:h.read_record(d/'records',m) for m in r['records']};assert len(decoded)==len(r['records'])
 assert set(decoded)=={p.name for p in (d/'records').iterdir() if p.is_file()}
 kinds={}
 for v in decoded.values():
  k=v['kind'];kinds[k]=kinds.get(k,0)+1
  if k in ['actual_calculate_result','actual_UI_step','actual_three_formatter_group']:h.assert_native_equal(v['after'],v['before'],k+' joint caller/state purity')
  assert k!='actual_calculate_exception'
 snapshots={row['id']:decoded[row['snapshot']['path']]['value'] for row in r['rows']}
 proof['windows'].append({'name':name,'rows':len(r['rows']),'windows':len(r['windows']),'saved_records_decoded':len(decoded),'kind_counts':kinds,'source_unchanged':True})
 results.append((r,snapshots))
old,new=results
paired=0;healthy=0
for row in new[0]['rows']:
 a=old[1][row['id']];b=new[1][row['id']]
 h.assert_native_equal(a['caller'],b['caller'],'paired whole raw numeric caller')
 h.assert_native_equal(a['state_and_disks'],b['state_and_disks'],'paired whole accepted state/disk');paired+=1
 if row['kind']=='healthy':h.assert_native_equal(a,b,'whole healthy Gold');healthy+=1
assert paired==18 and healthy==5
snow=new[1]['empty-generic-snow'];assert snow['caller']['snow_entries']==0
skill=snow['damage_result']['result']['estimate']['skill'];assert skill['total_damage']==0 and skill['phase_damage'] is None and skill['cycle_damage'] is None and skill['recharge_seconds'] is None
for png in new[0]['pngs']:
 raw=(B/'resume109-window-candidate-v3'/png['path']).read_bytes();assert len(raw)==png['bytes'] and hashlib.sha256(raw).hexdigest()==png['sha256']
assert len(new[0]['pngs'])==4
root=pathlib.Path('/workspace/rougezhushou');guard=json.loads((B/'resume109-applied-source-v1.json').read_text());assert h.source_map(root)==guard['source_sha256']
for name,sha in guard['source_additional_sha256'].items():assert hashlib.sha256((root/name).read_bytes()).hexdigest()==sha
proof.update(passed=True,workflow_complete=True,full_healthy_Gold_pairs=healthy,full_raw_caller_and_state_disk_pairs=paired,png_hashes_verified=4,native_windows_verified=False)
with (B/'root-section109-window-saved-audit-v1.json').open('x') as f:json.dump(proof,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps(proof,ensure_ascii=False))
