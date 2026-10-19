from pathlib import Path
from hashlib import sha256,sha1
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
import urllib.request,json,sys,io
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];CACHE=ROOT/'.cache/p3-expansion-314';OUT=CACHE/'prepared';PACK='research/p3-current-battle-314'
COMMIT='bee3f83c5d60590b5e1cd42b8d09d00ce32ab10d';RESOURCE='de6cfb30ed1d41d9102d93e8ea400fc0cefc8ff7'
def enc(v):return(json.dumps(v,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n').encode()
def save(n,raw):
 p=OUT/n;p.parent.mkdir(exist_ok=True,parents=True);p.write_bytes(raw)
def blob(raw):return sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
def download(url):
 with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'rougezhushou-readonly-current-enemy-pictures/1.0'}),timeout=35)as r:
  assert r.status==200;chunks=[]
  while True:
   b=r.read(8192)
   if not b:break
   chunks.append(b)
  raw=b''.join(chunks)
  if r.headers.get('Content-Length'):assert len(raw)==int(r.headers['Content-Length'])
  return raw
r=json.loads((CACHE/'collection-final.json').read_bytes());assert not r['failures']and len(r['files'])==115
tree={x['path'].split('/gamedata/',1)[1]:x for name in('level-root-tree','level-dlc1-tree')for x in json.loads((CACHE/(name+'.json')).read_bytes())if x['type']=='file'}
levels={}
for name,pin in r['files'].items():
 raw=(CACHE/name).read_bytes();assert len(raw)==pin['bytes']and sha256(raw).hexdigest()==pin['sha256']and blob(raw)==pin['git_blob_sha1']
 if name.startswith('levels/obt/'):
  assert name in tree and tree[name]['sha']==blob(raw)and tree[name]['size']==len(raw),name
  levels[name]=json.loads(raw)
db={e['Key']:e['Value']for e in json.loads((CACHE/'levels/enemydata/enemy_database.json').read_bytes())['enemies']};hand=json.loads((CACHE/'excel/enemy_handbook_table.json').read_bytes())['enemyData']
refs={ref['id']for level in levels.values()for ref in level['enemyDbRefs']};assert len(levels)==113 and len(refs)==387
selected={'levels':levels,'enemy_definitions':{k:db[k]for k in sorted(refs)if k in db},'handbook':{k:hand[k]for k in sorted(refs)if k in hand}}
save(PACK+'/source-inputs.json',enc(selected))
save(PACK+'/collection-first-attempt.json',(CACHE/'collection-attempt1.json').read_bytes());save(PACK+'/collection-final.json',(CACHE/'collection-final.json').read_bytes())
for name in('level-root-tree','level-dlc1-tree'):save(PACK+'/'+name+'.json',(CACHE/(name+'.json')).read_bytes())
image_tree_path=CACHE/'enemy-images-tree.json'
if not image_tree_path.exists():image_tree_path.write_bytes(download('https://api.github.com/repos/fexli/ArknightsResource/git/trees/d311bf00c24fe2ad71675fbcb025f0136cc60e89'))
image_tree=json.loads(image_tree_path.read_bytes());assert image_tree['truncated']is False
save(PACK+'/enemy-images-tree.json',image_tree_path.read_bytes());nodes={x['path']:x for x in image_tree['tree']}
prefabs=set(refs)
for level in levels.values():
 for ref in level['enemyDbRefs']:
  rows=sorted(db.get(ref['id'],[]),key=lambda x:x['level'])if ref['useDb']else[];prefab=None
  for value in [x['enemyData']for x in rows if x['level']<=ref['level']]+[ref.get('overwrittenData')or{}]:
   field=value.get('prefabKey')or{}
   if field.get('m_defined')is True:prefab=field['m_value']
  if prefab:prefabs.add(prefab)
existing={}
for folder in('rouge/data/portraits','rouge/data/current-enemies'):
 for p in(ROOT/folder).glob('*.png'):
  raw=p.read_bytes();existing[blob(raw)]=p
targets={p:nodes[p+'.png']for p in sorted(prefabs)if p+'.png'in nodes};records={};failures=[]
def get(entry):
 key,node=entry;url=f'https://raw.githubusercontent.com/fexli/ArknightsResource/{RESOURCE}/enemy/{key}.png'
 try:
  if node['sha']in existing:raw=existing[node['sha']].read_bytes();name=existing[node['sha']].relative_to(ROOT).as_posix();method='exact existing public blob equals current resource tree'
  else:raw=download(url);name='rouge/data/current-enemies/'+node['sha']+'.png';save(name,raw);method='downloaded exact current resource blob'
  assert len(raw)==node['size']and blob(raw)==node['sha'];im=Image.open(io.BytesIO(raw));im.load();assert im.format=='PNG'
  return key,{'file':name,'url':url,'git_blob_sha1':node['sha'],'sha256':sha256(raw).hexdigest(),'bytes':len(raw),'width':im.width,'height':im.height,'method':method},None
 except Exception as e:return key,None,{'identity':key,'error':type(e).__name__+': '+str(e)}
with ThreadPoolExecutor(max_workers=4)as pool:
 for key,row,error in pool.map(get,targets.items()):
  if error:failures.append(error)
  else:records[key]=row
save(PACK+'/enemy-images.json',enc({'resource_commit':RESOURCE,'tree_sha':'d311bf00c24fe2ad71675fbcb025f0136cc60e89','images':records,'failures':failures,'missing_exact_ids':sorted(prefabs-set(targets)),'requested':list(targets)}))
save(PACK+'/source-selection.json',enc({'commit':COMMIT,'resource_commit':RESOURCE,'original_sources':r['files'],'selected_level_objects_complete':True,'selected_enemy_ids':sorted(refs),'enemy_ids_missing_database':sorted(refs-set(db)),'handbook_missing':sorted(refs-set(hand)),'original_bytes_and113_tree_blobs_checked':True,'selected_cache_originals_checked_utc':datetime.now(timezone.utc).isoformat(),'private_game_chat_access':False,'runtime_server_match_verified':False}))
print(json.dumps({'source_only':True,'levels':len(levels),'enemy_ids':len(refs),'image_records':len(records),'image_failures':failures,'missing_image_keys':sorted(prefabs-set(targets))},ensure_ascii=False),flush=True)
