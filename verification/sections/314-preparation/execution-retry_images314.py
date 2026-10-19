from pathlib import Path
from hashlib import sha256,sha1
from concurrent.futures import ThreadPoolExecutor
import json,urllib.request,io
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];CACHE=ROOT/'.cache/p3-expansion-314';OUT=CACHE/'prepared';PACK='research/p3-current-battle-314'
def enc(v):return(json.dumps(v,ensure_ascii=False,separators=(',',':'))+'\n').encode()
p=OUT/PACK/'enemy-images.json';record=json.loads(p.read_bytes());(OUT/PACK/'enemy-images-first-attempt.json').write_bytes(p.read_bytes())
nodes={x['path']:x for x in json.loads((CACHE/'enemy-images-tree.json').read_bytes())['tree']};history=[]
for attempt in range(2,5):
 todo=[x for x in record['requested']if x not in record['images']]
 if not todo:break
 def get(key):
  node=nodes[key+'.png'];url=f'https://raw.githubusercontent.com/fexli/ArknightsResource/{record["resource_commit"]}/enemy/{key}.png'
  try:
   with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'rougezhushou-readonly-retry/1.0'}),timeout=35)as r:assert r.status==200;raw=r.read()
   assert len(raw)==node['size']and sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==node['sha'];im=Image.open(io.BytesIO(raw));im.load();assert im.format=='PNG'
   name='rouge/data/current-enemies/'+node['sha']+'.png';target=OUT/name;target.parent.mkdir(exist_ok=True,parents=True);target.write_bytes(raw)
   return key,{'file':name,'url':url,'git_blob_sha1':node['sha'],'sha256':sha256(raw).hexdigest(),'bytes':len(raw),'width':im.width,'height':im.height,'method':'downloaded exact current resource blob'},None
  except Exception as e:return key,None,{'identity':key,'error':type(e).__name__+': '+str(e)}
 failures=[]
 with ThreadPoolExecutor(max_workers=3)as pool:
  for key,row,error in pool.map(get,todo):
   if error:failures.append(error)
   else:record['images'][key]=row
 history.append({'attempt':attempt,'failures':failures});print(json.dumps({'attempt':attempt,'images':len(record['images']),'failures':len(failures)}),flush=True)
 record['failures']=failures
record['retry_history']=history;p.write_bytes(enc(record));print(json.dumps({'all_available_exact_images_downloaded':not record['failures'],'images':len(record['images']),'missing_exact_keys':len(record['missing_exact_ids'])}),flush=True)
