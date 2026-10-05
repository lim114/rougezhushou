"""One bounded public global prefab plus actual character/S1 receipt search."""
from pathlib import Path
import runpy,json,hashlib
OUT=Path(__file__).resolve().parent
BASE=Path('D:/Hypergryph Launcher/games/Arknights/Arknights_Data/StreamingAssets/AB/Windows')
SOURCE='battle/prefabs/[uc]globalbuffs.ab'
r=runpy.run_path(str(OUT.parent/'p1-runtime-source-054/read_unity_stdlib.py'))
prior=json.loads((OUT.parent/'sp-attributes-066/globals-prefabs.json').read_text(encoding='utf-8'))
raw=(BASE/SOURCE).read_bytes()
assert hashlib.sha256(raw).hexdigest()==prior['source_sha256']
info,files=r['bundle'](raw);results=[]
def pp(x):
 if isinstance(x,dict):
  if 'm_FileID' in x and 'm_PathID' in x:yield x
  for v in x.values():yield from pp(v)
 elif isinstance(x,list):
  for v in x:yield from pp(v)
for fname,data in files:
 if '.resS' in fname or '.resource' in fname:continue
 v=r['serialized'](data);assert all(o.get('read_exact') for o in v['objects'])
 om={o['path_id']:o for o in v['objects']}
 assets=[o for o in v['objects'] if o['class_id']==142];assert len(assets)==1
 choices=[a for a in assets[0]['data']['m_Container'] if a['first']=='dyn/battle/prefabs/[uc]globalbuffs/ep_damage_scale.prefab']
 assert len(choices)==1
 for a in choices:
  root=a['second']['asset'];assert root['m_FileID']==0
  todo=[root['m_PathID']];seen=set();os=[]
  while todo:
   oid=todo.pop()
   if oid==0 or oid in seen:continue
   seen.add(oid);assert oid in om
   o=om[oid];os.append(o)
   todo.extend(p['m_PathID'] for p in pp(o['data']) if p['m_FileID']==0)
  results.append({'asset_path':a['first'],'root_id':root['m_PathID'],'objects':os})
search=[]
for name in ['character-prefabs.json','skill-prefabs.json']:
 p=OUT.parent/'phatm2-s1-069'/name;receipt=json.loads(p.read_text(encoding='utf-8'))
 graphs=receipt.get('selected_prefabs') or [f['serialized'] for s in receipt['sources'] for f in s['files']]
 found=[]
 for g in graphs:
  for o in g['objects']:
   text=json.dumps(o.get('data'),ensure_ascii=False)
   if 'EpDamageScale' in text or 'ep_damage_scale' in text:found.append({'path_id':o['path_id'],'data':o['data']})
 search.append({'receipt':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'matches':found})
result={'source_name':SOURCE,'source_bytes':len(raw),'source_sha256':hashlib.sha256(raw).hexdigest(),'base_version':prior['base_version'],'selected_prefabs':results,'actual_char_s1_search':search,'game_dll_executed':False,'process_memory_read':False,'private_files_read':False}
(OUT/'global-ep-scale-prefab.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=1))
