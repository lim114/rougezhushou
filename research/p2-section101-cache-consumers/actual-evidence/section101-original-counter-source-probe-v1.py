import json,sys,tempfile,hashlib,copy,datetime
from pathlib import Path
repo=Path('/workspace/rougezhushou');sys.path.insert(0,str(repo))
from rouge.run_state import RunState
from rouge.relic_counter_semantics import COUNTER_BINDINGS,counter_resources
from rouge.relics import mechanics
base=Path('/workspace/.continuation');g=json.loads((base/'full100-completed-source-guard-v1.json').read_text())
for k,v in g['source_sha256'].items():assert hashlib.sha256((repo/k).read_bytes()).hexdigest()==v
rid='rogue_6_relic_legacy_103';key=COUNTER_BINDINGS[rid][0]
proof={'id':rid,'title':mechanics()['relics'][rid]['name'],'value':1,'source':'held_full_name_usage_and_public_probe'}
original=counter_resources([proof])[key];rows=[]
with tempfile.TemporaryDirectory(prefix='public-counter-source101-') as folder:
 folder=Path(folder)
 for name,source in [('healthy-text',proof['source']),('source-null',None),('source-array',[]),('source-number',1)]:
  resource={**copy.deepcopy(original),'captured_at':0};resource['counter_evidence']['source']=source
  saved={'started_at':0,'last_read':1,'operators':{},'relics':{rid:{'held':True}},'resources':{key:resource}};raw=json.dumps(saved,ensure_ascii=False).encode();path=folder/(name+'.json');path.write_bytes(raw);run=RunState(path);assert not run.preserve_unreadable
  row={'id':name,'fixture_JSON':saved,'accepted_without_rejection':True}
  try:row['summary']=run.summary();row['usable_resources']=run.calculation_resources()
  except Exception as e:row['exception']={'type':type(e).__name__,'message':str(e)}
  row['disk_unchanged']=path.read_bytes()==raw;row['tmp_absent']=not path.with_suffix('.tmp').exists();assert row['disk_unchanged'] and row['tmp_absent'];rows.append(row)
for k,v in g['source_sha256'].items():assert hashlib.sha256((repo/k).read_bytes()).hexdigest()==v
receipt={'kind':'ROOT_ACTUAL_ORIGINAL_COUNTER_SOURCE_JSON_REPRODUCTION_ONLY','product_pass':False,'checked_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_files':743,'source_drift':[],'cases':rows,'private_state_access':False,'game_chat_executed':False}
with (base/'section101-original-counter-source-actual-linux-v1.json').open('x') as f:json.dump(receipt,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps([{k:r[k] for k in ('id','accepted_without_rejection','exception','disk_unchanged') if k in r} for r in rows],ensure_ascii=False))
