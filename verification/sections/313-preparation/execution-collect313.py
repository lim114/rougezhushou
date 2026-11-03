from pathlib import Path
from hashlib import sha256,sha1
from datetime import datetime,timezone
from concurrent.futures import ThreadPoolExecutor
import urllib.request,urllib.parse,json,io
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
CACHE=ROOT/'.cache/p3-313-dlc2-research';OUT=CACHE/'prepared';OUT.mkdir(exist_ok=True)
PACK='research/p3-expansion-313'
OLD='a550f5e048bb94e7cdefc6eb97a4091f0c4c7add';NEW='bee3f83c5d60590b5e1cd42b8d09d00ce32ab10d';RESOURCE='de6cfb30ed1d41d9102d93e8ea400fc0cefc8ff7'
def enc(v):return(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode('utf8')
def pin(raw):return{'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}
def save(name,raw):
 p=OUT/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
def blob(raw):return sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
full={};records=[]
for label,path,commit,expected in [('baseline',ROOT/'.cache/game-data/roguelike_topic_table.json',OLD,'f5867e55d09472253083486174aa47bd94dd48b07684b74b60a5b29ca00eda86'),('current',CACHE/'roguelike-topic.json',NEW,'3a67f5acd4b3daa935b1a9a63c9e4db0a56c86d71b90ffe1568ce6cbc364f091')]:
 raw=path.read_bytes();assert sha256(raw).hexdigest()==expected;obj=json.loads(raw);full[label]=obj
 selected={k:obj[k]['rogue_6']for k in ('topics','details','modules','customizeData')}
 save(PACK+'/'+label+'-topic.json',enc(selected))
 records.append({'role':label,'commit':commit,'url':f'https://raw.githubusercontent.com/Kengxxiao/ArknightsGameData/{commit}/zh_CN/gamedata/excel/roguelike_topic_table.json',**pin(raw),'exact_selection':'Four complete $.{topics,details,modules,customizeData}.rogue_6 objects','selected_file':PACK+'/'+label+'-topic.json'})
for label,url in [('official-name','https://ak.hypergryph.com/news/7366'),('community-current','https://prts.wiki/w/'+urllib.parse.quote('沉沦者的黑流树海'))]:
 req=urllib.request.Request(url,headers={'User-Agent':'rougezhushou-readonly-version-reference/1.0'})
 try:
  with urllib.request.urlopen(req,timeout=20)as r:raw=r.read();status=r.status
  save(PACK+'/'+label+'.html',raw);records.append({'role':label,'url':url,'status':status,**pin(raw),'file':PACK+'/'+label+'.html'})
 except Exception as ex:
  records.append({'role':label,'url':url,'local_download_available':False,'error':type(ex).__name__+': '+str(ex),'facts_checked_separately_in_actual_web_tool':True,'web_tool_scope':'Official producer note69 calls it content expansion one and schedules mid October. Community page identifies October16 and first expansion. No raw HTTP success claimed.'})
save(PACK+'/sources.json',enc({'records':records,'source_publisher_distinction':'Kengxxiao game-data and fexli resource mirrors are extracted community mirrors, not official APIs. Official website supports expansion name; community page and enroll timestamp support the observed October16 release. The previously linked TapTap AI-four account is a repost, not primary official evidence.','user_called_it_DLC2':True,'DLC2_as_official_name_verified':False,'official_label':'内容拓展·一','observed_release_Beijing':'2026-10-16T16:00:00+08:00','client_commit_message':'Client:2.7.81 Data:26-10-14-13-45-10-99469376','current_server_or_installed_client_verified':False}))
save(PACK+'/resource-commit.json',(CACHE/'map-resource-commit.json').read_bytes())
save(PACK+'/mapreview-tree.json',(CACHE/'mapreview-tree.json').read_bytes())
tree=json.loads((CACHE/'mapreview-tree.json').read_bytes());assert not tree['truncated']
blobs={r['path']:r for r in tree['tree']};old=full['baseline']['details']['rogue_6']['stages'];new=full['current']['details']['rogue_6']['stages']
targets=[sid for sid in new if old.get(sid)!=new[sid]]
assert len(targets)==80
existing={}
for p in(ROOT/'rouge/data/battle-maps').glob('*.png'):
 raw=p.read_bytes();existing[blob(raw)]=p
groups={}
for sid in targets:groups.setdefault(blobs[sid+'.png']['sha'],[]).append(sid)
def get(entry):
 sha,ids=entry;name=ids[0]+'.png';url=f'https://raw.githubusercontent.com/fexli/ArknightsResource/{RESOURCE}/mapreview/{name}'
 try:
  if sha in existing:raw=existing[sha].read_bytes();file=existing[sha].relative_to(ROOT).as_posix();how='Exact existing local public blob equals the current resource-tree blob'
  else:
   req=urllib.request.Request(url,headers={'User-Agent':'rougezhushou-readonly-map-download/1.0'})
   with urllib.request.urlopen(req,timeout=30)as response:raw=response.read();assert response.status==200
   file='rouge/data/expansion-maps/'+sha+'.png';save(file,raw);how='Downloaded fixed current commit blob'
  assert blob(raw)==sha
  image=Image.open(io.BytesIO(raw));image.load();assert image.format=='PNG'
  return{sid:{'file':file,'resource_commit':RESOURCE,'url':f'https://raw.githubusercontent.com/fexli/ArknightsResource/{RESOURCE}/mapreview/{sid}.png','git_blob_sha1':sha,**pin(raw),'width':image.width,'height':image.height,'method':how,'level_geometry_or_position_calibration_verified':False}for sid in ids},None
 except Exception as ex:return{}, {'blob':sha,'stage_ids':ids,'error':type(ex).__name__+': '+str(ex),'source_only_no_image_pass':True}
images={};failures=[]
with ThreadPoolExecutor(max_workers=4)as pool:
 for rows,error in pool.map(get,groups.items()):
  images.update(rows)
  if error:failures.append(error)
save(PACK+'/map-images.json',enc({'resource_commit':RESOURCE,'stage_ids_requested':targets,'images':images,'failures':failures,'distinct_requested_blobs':len(groups),'entry_count':len(images),'no_coordinate_mapping_added':True,'exact_same_version_geometry_verified':False}))
save(PACK+'/collection.json',enc({'kind':'source_only_not_section_acceptance','created_utc':datetime.now(timezone.utc).isoformat(),'source_records':records,'requested_stage_entries':len(targets),'image_entries_available':len(images),'unique_blobs':len(groups),'failed_images':failures,'no_game_chat_or_private_state_used':True}))
print(json.dumps({'exact_stage_entries':len(targets),'distinct_image_blobs':len(groups),'available_image_entries':len(images),'failed_images':failures,'prepared_source_only':True},ensure_ascii=False))
