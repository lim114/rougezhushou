from pathlib import Path
from hashlib import sha256,sha1
import urllib.request,json,io
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'.cache/p3-313-dlc2-research/prepared';PACK=BASE/'research/p3-expansion-313'
def enc(v):return(json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode('utf8')
p=PACK/'map-images.json';raw=p.read_bytes();(PACK/'map-images-first-attempt.json').write_bytes(raw);data=json.loads(raw);remaining=[]
for failure in data['failures']:
 ids=failure['stage_ids'];url=f"https://raw.githubusercontent.com/fexli/ArknightsResource/{data['resource_commit']}/mapreview/{ids[0]}.png"
 try:
  with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'rougezhushou-readonly-map-retry'}),timeout=30)as response:content=response.read();assert response.status==200
  digest=sha1(b'blob '+str(len(content)).encode()+b'\0'+content).hexdigest();assert digest==failure['blob']
  image=Image.open(io.BytesIO(content));image.load();assert image.format=='PNG'
  file='rouge/data/expansion-maps/'+digest+'.png';target=BASE/file;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(content)
  for sid in ids:data['images'][sid]={'file':file,'resource_commit':data['resource_commit'],'url':url.replace(ids[0]+'.png',sid+'.png'),'git_blob_sha1':digest,'sha256':sha256(content).hexdigest(),'bytes':len(content),'width':image.width,'height':image.height,'method':'Idempotent second HTTP read after preserved incomplete first response','level_geometry_or_position_calibration_verified':False}
  print('recovered',ids,flush=True)
 except Exception as ex:remaining.append({**failure,'second_error':type(ex).__name__+': '+str(ex)});print('still unavailable',ids,type(ex).__name__,flush=True)
data['failures']=remaining;data['entry_count']=len(data['images']);data['first_failure_record_preserved']='research/p3-expansion-313/map-images-first-attempt.json';p.write_bytes(enc(data))
collection=PACK/'collection.json';(PACK/'collection-first-attempt.json').write_bytes(collection.read_bytes());c=json.loads(collection.read_bytes());c.update(image_entries_available=len(data['images']),failed_images=remaining,first_attempt_preserved=True);collection.write_bytes(enc(c))
print('available',len(data['images']),'of',len(data['stage_ids_requested']))
