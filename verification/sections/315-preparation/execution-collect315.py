from pathlib import Path
from hashlib import sha256,sha1
from datetime import datetime,timezone
from concurrent.futures import ThreadPoolExecutor
import urllib.request,json
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'.cache/p3-current-rewards-315';OUT.mkdir(exist_ok=True)
COMMIT='bee3f83c5d60590b5e1cd42b8d09d00ce32ab10d'
def enc(v):return(json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode()
def fetch(name):
 url=f'https://raw.githubusercontent.com/Kengxxiao/ArknightsGameData/{COMMIT}/zh_CN/gamedata/excel/{name}.json';attempts=[]
 for attempt in range(1,4):
  try:
   with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'rougezhushou-readonly-current-reward-rules/1.0'}),timeout=40)as r:
    assert r.status==200;raw=r.read()
   assert isinstance(json.loads(raw),dict);(OUT/(name+'.json')).write_bytes(raw)
   attempts.append({'attempt':attempt,'success':True})
   return name,{'url':url,'sha256':sha256(raw).hexdigest(),'git_blob_sha1':sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest(),'bytes':len(raw),'HTTP_status':200,'attempts':attempts},None
  except Exception as e:attempts.append({'attempt':attempt,'success':False,'error':type(e).__name__+': '+str(e)})
 return name,None,{'url':url,'attempts':attempts,'deferred':True,'restart_condition':'new usable source or independent evidence of resolved transport'}
files={};failures={}
with ThreadPoolExecutor(max_workers=2)as pool:
 for name,record,error in pool.map(fetch,['character_table','skill_table']):
  if error:failures[name]=error
  else:files[name]=record
result={'commit':COMMIT,'files':files,'failures':failures,'observedUTC':datetime.now(timezone.utc).isoformat(),'max_total_attempts_per_file':3,'source_only':True}
(OUT/'collection.json').write_bytes(enc(result));print(json.dumps({'files':{n:{'bytes':v['bytes'],'attempts':len(v['attempts'])}for n,v in files.items()},'failures':failures,'source_only':True},ensure_ascii=False),flush=True)
