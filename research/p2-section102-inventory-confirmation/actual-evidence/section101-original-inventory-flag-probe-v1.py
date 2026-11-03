from pathlib import Path
import json,tempfile,sys,hashlib
sys.path.insert(0,'/workspace/rougezhushou')
from rouge.run_state import RunState
b=Path('/workspace/.continuation');g=json.loads((b/'full100-completed-source-guard-v1.json').read_text());repo=Path('/workspace/rougezhushou')
for k,v in g['source_sha256'].items():assert hashlib.sha256((repo/k).read_bytes()).hexdigest()==v
rows=[]
with tempfile.TemporaryDirectory(prefix='public-flag101-original-') as d:
 for i,value in enumerate((True,False,None,'false',[1],1,0)):
  p=Path(d)/f'{i}.json';raw=json.dumps({'operators':{},'relics':{},'relic_count':0,'inventory_verified':value}).encode();p.write_bytes(raw);r=RunState(p);s=r.inventory_status();rows.append({'saved_verified':value,'native_type':type(value).__name__,'accepted':not r.preserve_unreadable,'status':s,'disk_unchanged':p.read_bytes()==raw,'tmp_absent':not p.with_suffix('.tmp').exists()})
for k,v in g['source_sha256'].items():assert hashlib.sha256((repo/k).read_bytes()).hexdigest()==v
p=b/'section101-original-inventory-flag-observations-v1.json';p.open('x').write(json.dumps({'kind':'ROOT_ACTUAL_ORIGINAL_JSON_INVENTORY_FLAG_ONLY','product_pass':False,'source_files':743,'source_drift':[],'cases':rows},ensure_ascii=False,indent=2)+'\n');print(json.dumps([{'saved':x['saved_verified'],'complete':x['status']['complete'],'accepted':x['accepted']} for x in rows],ensure_ascii=False))
