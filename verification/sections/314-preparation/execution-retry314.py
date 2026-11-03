from pathlib import Path
from hashlib import sha256,sha1
from datetime import datetime,timezone
from concurrent.futures import ThreadPoolExecutor,as_completed
import urllib.request,json
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'.cache/p3-expansion-314'
COMMIT='bee3f83c5d60590b5e1cd42b8d09d00ce32ab10d'
def enc(v):return(json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode()
def download(url):
 with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'rougezhushou-readonly-current-level-reference/1.0'}),timeout=40)as r:
  assert r.status==200;data=[]
  while True:
   chunk=r.read(8192)
   if not chunk:break
   data.append(chunk)
  raw=b''.join(data)
  if r.headers.get('Content-Length'):assert len(raw)==int(r.headers['Content-Length'])
  json.loads(raw);return raw
r=json.loads((OUT/'collection-attempt1.json').read_bytes());files=r['files'];history=[]
for attempt in range(2,5):
 todo=[n for n in r['requested']if n not in files]
 if not todo:break
 def fetch(n):
  url=f'https://raw.githubusercontent.com/Kengxxiao/ArknightsGameData/{COMMIT}/zh_CN/gamedata/{n}'
  try:
   raw=download(url);(OUT/n).write_bytes(raw)
   return n,{'url':url,'sha256':sha256(raw).hexdigest(),'bytes':len(raw),'git_blob_sha1':sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest(),'HTTP_status':200},None
  except Exception as e:return n,None,{'path':n,'error':type(e).__name__+': '+str(e)}
 failures=[]
 with ThreadPoolExecutor(max_workers=3)as pool:
  for n,row,error in pool.map(fetch,todo):
   if error:failures.append(error)
   else:files[n]=row
 history.append({'attempt':attempt,'requested':len(todo),'failures':failures});print(json.dumps({'attempt':attempt,'available':len(files),'failures':len(failures)}),flush=True)
for label,url in [('level-root-tree',f'https://api.github.com/repos/Kengxxiao/ArknightsGameData/contents/zh_CN/gamedata/levels/obt/roguelike/ro6?ref={COMMIT}'),('level-dlc1-tree',f'https://api.github.com/repos/Kengxxiao/ArknightsGameData/contents/zh_CN/gamedata/levels/obt/roguelike/ro6/dlc1?ref={COMMIT}'),('enemy-images-tree','https://api.github.com/repos/fexli/ArknightsResource/git/trees/d311bf00c24fe2ad71675fbcb025f0136cc60e89')]:
 try:raw=download(url);(OUT/(label+'.json')).write_bytes(raw)
 except Exception as e:history.append({'source':label,'error':str(e)})
r.update(files=files,failures=[n for n in r['requested']if n not in files],retry_history=history,observed_utc=datetime.now(timezone.utc).isoformat());(OUT/'collection-final.json').write_bytes(enc(r));print(json.dumps({'source_only':True,'files':len(files),'failures':r['failures'],'extra_trees':[p.name for p in OUT.glob('*tree.json')]},ensure_ascii=False),flush=True)
