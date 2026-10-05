"""Extract only the actual S1 unmove template from its pinned public bundle."""
from pathlib import Path
import runpy,json,hashlib
OUT=Path(__file__).resolve().parent
BASE=Path('D:/Hypergryph Launcher/games/Arknights/Arknights_Data/StreamingAssets/AB/Windows')
SOURCE='config/buff_template_holder.ab'
prior=next(x for x in json.loads((OUT.parent/'p1-runtime-source-054/stdlib-bundles-3.json').read_text(encoding='utf-8')) if x['name']==SOURCE)
raw=(BASE/SOURCE).read_bytes();assert hashlib.sha256(raw).hexdigest()==prior['source_sha256']
r=runpy.run_path(str(OUT.parent/'p1-runtime-source-054/read_unity_stdlib.py'));info,files=r['bundle'](raw);matches=[]
def walk(x,path=()):
 if isinstance(x,dict):
  if x.get('templateKey')=='phatm2_s_1[unmove]' and 'eventToActions' in x:matches.append({'json_path':list(path),'template':x})
  for k,v in x.items():walk(v,path+(k,))
 elif isinstance(x,list):
  for i,v in enumerate(x):walk(v,path+(i,))
for fname,data in files:
 if '.resS' in fname or '.resource' in fname:continue
 v=r['serialized'](data);assert all(o.get('read_exact') for o in v['objects'])
 for o in v['objects']:walk(o.get('data'),(fname,'path_id',o['path_id'],'data'))
assert len(matches)==1
result={'source_name':SOURCE,'source_bytes':len(raw),'source_sha256':hashlib.sha256(raw).hexdigest(),'matches':matches,'game_dll_executed':False,'process_memory_read':False,'private_files_read':False}
(OUT/'s1-unmove-template.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=False))
