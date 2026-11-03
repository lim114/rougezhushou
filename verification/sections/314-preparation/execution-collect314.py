from pathlib import Path
from hashlib import sha256,sha1
from datetime import datetime,timezone
from concurrent.futures import ThreadPoolExecutor,as_completed
import urllib.request,json
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'.cache/p3-expansion-314';OUT.mkdir(exist_ok=True)
COMMIT='bee3f83c5d60590b5e1cd42b8d09d00ce32ab10d'
stages=json.loads((ROOT/'research/p3-expansion-313/current-topic.json').read_bytes())['details']['stages']
paths=sorted(set('levels/'+s['levelId'].lower()+'.json'for s in stages.values()))+['levels/enemydata/enemy_database.json','excel/enemy_handbook_table.json']
def enc(v):return(json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode()
def fetch(name):
 p=OUT/name;p.parent.mkdir(exist_ok=True,parents=True)
 url=f'https://raw.githubusercontent.com/Kengxxiao/ArknightsGameData/{COMMIT}/zh_CN/gamedata/{name}'
 try:
  with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'rougezhushou-readonly-current-level-reference/1.0'}),timeout=35)as response:
   assert response.status==200;raw=response.read()
  obj=json.loads(raw);assert isinstance(obj,dict);p.write_bytes(raw)
  return name,{'url':url,'sha256':sha256(raw).hexdigest(),'bytes':len(raw),'git_blob_sha1':sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest(),'HTTP_status':200},None
 except Exception as e:return name,None,{'path':name,'url':url,'error':type(e).__name__+': '+str(e)}
files={};failures=[]
with ThreadPoolExecutor(max_workers=4)as pool:
 futures=[pool.submit(fetch,n)for n in paths]
 for future in as_completed(futures):
  name,row,error=future.result()
  if error:failures.append(error)
  else:files[name]=row
  if(len(files)+len(failures))%20==0:print(json.dumps({'fetched':len(files),'failed':len(failures),'requested':len(paths)}),flush=True)
result={'commit':COMMIT,'files':files,'failures':failures,'requested':paths,'observed_utc':datetime.now(timezone.utc).isoformat(),'private_or_game_used':False}
(OUT/'collection-attempt1.json').write_bytes(enc(result))
print(json.dumps({'source_only':True,'files':len(files),'failed':failures},ensure_ascii=False),flush=True)
