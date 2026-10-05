"""Inspect the installed public original-art bundle without game execution."""
from pathlib import Path
import hashlib,json,runpy,struct
OUT=Path(__file__).resolve().parent
BASE=Path('D:/Hypergryph Launcher/games/Arknights/Arknights_Data/StreamingAssets/AB/Windows')
source='chararts/char_1042_phatm2.ab'
manifest=json.loads((BASE/'hot_update_list.json').read_text(encoding='utf-8'))
entry=next(x for x in manifest['abInfos'] if x['name']==source)
raw=(BASE/source).read_bytes()
assert len(raw)==entry['abSize'] and hashlib.md5(raw).hexdigest()==entry['md5']
r=runpy.run_path(str(OUT.parent/'p1-runtime-source-054/read_unity_stdlib.py'))
info,files=r['bundle'](raw);rows=[]
for name,data in files:
 if '.resS' in name or '.resource' in name:continue
 v=r['serialized'](data)
 assert all(o.get('read_exact') for o in v['objects'] if o['class_id'] in (1,4,114,142))
 components=[];textassets=[];exact=sum(bool(o.get('read_exact')) for o in v['objects'])
 for o in v['objects']:
  if o['class_id']==114:
   components.append({k:vv for k,vv in o.items() if k not in ('raw_tail',)})
  elif o['class_id']==49:
   # TextAsset serialized object preserves its binary script payload.
   pos=o['byte_start'];size=struct.unpack_from('<I',data,pos)[0]
   asset_name=data[pos+4:pos+4+size].decode('utf-8');p=(pos+4+size+3)&~3
   n=struct.unpack_from('<I',data,p)[0];payload=data[p+4:p+4+n]
   assert len(payload)==n
   assert p+4+n<=pos+o['byte_size']
   assert (p+4+n+3)&~3==pos+o['byte_size']
   filename=asset_name.replace('/','_').replace('\\','_')
   if 'Front' in asset_name or 'Back' in asset_name:
    (OUT/(filename+'.bin')).write_bytes(payload)
   textassets.append({'path_id':o['path_id'],'name':asset_name,'bytes':n,'sha256':hashlib.sha256(payload).hexdigest(),
      'saved':(filename+'.bin') if 'Front' in asset_name or 'Back' in asset_name else None})
 rows.append({'name':name,'engine':v['engine'],'objects':len(v['objects']),'read_exact':exact,
   'types':[{k:t[k] for k in ('class_id','script_id','old_type_hash')} for t in v['types']],
   'externals':v['externals'],'components':components,'textassets':textassets,
   'gameobjects':[o for o in v['objects'] if o['class_id']==1],
   'transforms':[o for o in v['objects'] if o['class_id']==4],
   'assetbundle':[o for o in v['objects'] if o['class_id']==142]})
report={'source_name':source,'source_bytes':len(raw),'source_sha256':hashlib.sha256(raw).hexdigest(),
 'installed_base_version':manifest['versionId'],'bundle':info,'files':rows,
 'dll_executed':False,'process_memory_read':False,'private_state_read':False}
(OUT/'art.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'sha256':report['source_sha256'],'files':[{'name':r['name'],'objects':r['objects'],'exact':r['read_exact'],
   'components':len(r['components']),'textassets':r['textassets']} for r in rows]},ensure_ascii=False))
