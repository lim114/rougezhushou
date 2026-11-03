import sys,json,tempfile,hashlib,copy,datetime
from pathlib import Path
repo=Path('/workspace/rougezhushou');sys.path.insert(0,str(repo))
from rouge.run_state import RunState
base=Path('/workspace/.continuation');g=json.loads((base/'full100-completed-source-guard-v1.json').read_text())
for k,v in g['source_sha256'].items():assert hashlib.sha256((repo/k).read_bytes()).hexdigest()==v
out=base/'section101-original-json-actual-linux-v1';out.mkdir(exist_ok=False);rows=[]
with tempfile.TemporaryDirectory(prefix='public-original101-') as folder:
 folder=Path(folder)
 cases=[('stored-count-text',{'relic_count':'0'},'apply'),('stored-count-null',{'relic_count':None},'apply'),('stored-count-zero',{'relic_count':0},'apply'),('present-text',{'operators':{'mechanist':{'present':'yes'}}},'summary'),('present-true',{'operators':{'mechanist':{'present':True}}},'summary'),('present-null',{'operators':{'mechanist':{'present':None}}},'summary'),('resource-list-id',{'resources':{'public_counter':{'value':1,'captured_at':0,'source':'held_card_counter','counter_evidence':{'id':[]}}}},'summary'),('resource-unknown-text-id',{'resources':{'public_counter':{'value':1,'captured_at':0,'source':'held_card_counter','counter_evidence':{'id':'unknown-public-id'}}}},'summary')]
 for name,saved,op in cases:
  path=folder/(name+'.json');raw=json.dumps(saved,ensure_ascii=False).encode();path.write_bytes(raw);run=RunState(path);before=copy.deepcopy(run.state);row={'id':name,'saved_JSON':saved,'loaded_without_rejection':not run.preserve_unreadable,'input_disk_sha256':hashlib.sha256(raw).hexdigest(),'operation':op}
  assert not run.preserve_unreadable
  try:
   value=run.apply({'operators':[]},run.state['started_at']+1) if op=='apply' else run.summary()
   row['returned']=value
  except Exception as error:row['exception']={'type':type(error).__name__,'message':str(error)}
  row['after_disk_sha256']=hashlib.sha256(path.read_bytes()).hexdigest();row['disk_unchanged']=path.read_bytes()==raw;row['tmp_exists']=path.with_suffix('.tmp').exists();row['original_loaded_state']=before
  rows.append(row)
for k,v in g['source_sha256'].items():assert hashlib.sha256((repo/k).read_bytes()).hexdigest()==v
record={'kind':'ROOT_ACTUAL_ORIGINAL_ACCEPTED_JSON_REPRODUCTION_ONLY','checked_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'product_pass':False,'original_source_files':743,'source_drift':[],'private_state_access':False,'game_chat_executed':False,'native_windows_verified':False,'cases':rows}
with (out/'observations.json').open('x') as f:json.dump(record,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps([{k:r[k] for k in ('id','loaded_without_rejection','exception','disk_unchanged') if k in r} for r in rows],ensure_ascii=False))
