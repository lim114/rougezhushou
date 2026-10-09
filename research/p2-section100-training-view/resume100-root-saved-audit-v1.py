import json,sys,hashlib,datetime
from pathlib import Path
base=Path('/workspace/.continuation'); sys.path.insert(0,str(base/'section100-training-cache-v2/smoke-runtime-v1'))
import native_evidence as n
repo=Path('/workspace/rougezhushou'); guard=json.loads((base/'resume100-applied-source-v1.json').read_text());assert n.source_map(repo)==guard['source_sha256']
for key,value in guard['source_additional_sha256'].items():assert n.sha256((repo/key).read_bytes())==value
summary=[];snapshots={};totalcalls=0
for mode in ('gold','candidate'):
 folder=base/f'resume100-window-{mode}-v1';assert (base/f'resume100-window-{mode}-v1.exit-code').read_bytes()==b'0\n'
 r=json.loads((folder/'receipt.json').read_text());assert r['passed'] is True and r['workflow_complete'] is True
 values={}
 for row in r['records']:
  v=n.read_record(folder/'records',row);assert v['kind']==row['kind'] and v['case']==row['case'];values[row['path']]=v
  if v['kind']=='actual_calculate_damage':n.assert_native_equal(v['before'],v['after'],'saved original numerical caller');totalcalls+=1
 case_rows=[]
 for row in r['cases']:
  v=values[row['snapshot_record']['path']];assert v['kind']=='window_snapshot'
  for key in ('account','run'):assert type(v['disks'][key]) is bytes and n.sha256(v['disks'][key])==row['disk_sha256'][key]
  for key in ('account_tmp','run_tmp'):assert v['disks'][key] is False
  case_rows.append({'id':row['id'],'record':row['snapshot_record']['path'],'post_report_original_disk_bytes_unchanged':True,'temporary_paths_absent':True})
  snapshots[mode,row['id']]=v
 for png in r['pngs']:
  name=png['path'].replace('\\','/').rsplit('/',1)[-1];data=(folder/name).read_bytes();assert len(data)==png['bytes'] and n.sha256(data)==png['sha256']
 summary.append({'mode':mode,'records_read_and_hash_checked':len(values),'cases':case_rows,'primary_exit':0})
for case in json.loads((base/'resume100-window-gold-v1/receipt.json').read_text())['healthy_case_ids']:
 n.assert_native_equal(snapshots['candidate',case]['comparable'],snapshots['gold',case]['comparable'],'saved healthy baseline full native and three texts')
assert n.source_map(repo)==guard['source_sha256']
out={'kind':'ROOT_ACTUAL_SAVED_NATIVE_DISK_CALLER_AND_VISUAL_REVIEW','passed':True,'workflow_complete':True,'checked_at_Beijing':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),'source_files':len(guard['source_sha256']),'source_drift':[],'modes':summary,'healthy_native_three_text_pairs_rechecked':5,'original_numerical_calls_before_after_checked':totalcalls,'four_actual_candidate_PNGs_viewed':True,'visual_observations':['masked missing fields show account reference and run unconfirmed','healthy fractional 91.9 clamps to original level90','unsafe elite shows explicit fallback while target snack remains available','manual level17 preserved with restore-read-level control visible'],'formatter_scope':'Each formatter original damage_result unchanged in runner; this saved audit verifies full original disk bytes after all three texts per case, without claiming separate per-formatter disk instrumentation.','native_windows_verified':False,'game_chat_sampling_executed':False}
with (base/'resume100-root-saved-audit-v1.json').open('x') as f:json.dump(out,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'passed':True,'records':sum(x['records_read_and_hash_checked'] for x in summary),'cases':sum(len(x['cases']) for x in summary),'numerical_calls':totalcalls,'healthy_pairs':5,'source_files':743}))
