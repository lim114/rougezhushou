"""One exact metadata literal and file-backed RIP references, never native execution."""
from pathlib import Path
import json,struct,re
OUT=Path(__file__).resolve().parent
reader=OUT.parent/'p1-native-runtime-054/read_metadata_static.py'
scope={'__file__':str(reader),'__name__':'_bounded_metadata'}
exec(compile(reader.read_text(encoding='utf-8').split('selected=[]\n')[0],str(reader),'exec'),scope)
rows=[]
for idx,(size,pos) in enumerate(scope['records']('stringLiteral','II')):
 start=scope['header']['stringLiteralData'][0]+pos
 if scope['meta'][start:start+size]==b'ep_damage_scale':rows.append({'index':idx,'encoded':(5<<29)|(idx<<1)|1})
verification=json.loads((OUT.parent/'p1-native-mapping-054/mapping-verification.json').read_text(encoding='utf-8'))
base=verification['image_base'];binary=scope['binary'];sections=verification['sections']
mapping=json.loads((OUT.parent/'p1-native-mapping-054/script.json').read_text(encoding='utf-8'))['ScriptMethod']
for row in rows:
 pointer_bytes=struct.pack('<Q',row['encoded']);ptrs=[]
 for s in sections:
  if s['characteristics']&0x20000000:continue
  cursor=s['offset'];end=cursor+s['raw_size']
  while True:
   hit=binary.find(pointer_bytes,cursor,end)
   if hit<0:break
   ptrs.append(base+s['rva']+hit-s['offset']);cursor=hit+1
 row['global_addresses']=[hex(x) for x in ptrs];refs=[]
 for s in sections:
  if not s['characteristics']&0x20000000:continue
  start=s['offset'];end=start+s['raw_size']
  for match in re.finditer(b'[\x48\x4c]\x8b[\x05\x0d\x15\x1d\x25\x2d\x35\x3d]|[\x48\x4c]\x8d[\x05\x0d\x15\x1d\x25\x2d\x35\x3d]',binary[start:end]):
   off=start+match.start();address=base+s['rva']+off-start
   dest=address+7+struct.unpack_from('<i',binary,off+3)[0]
   if dest not in ptrs:continue
   before=[m for m in mapping if m['Address']<=address];nearest=max(before,key=lambda m:m['Address'])
   refs.append({'candidate_instruction':hex(address),'global':hex(dest),'bytes':binary[off:off+7].hex(),'nearest_preceding_mapping':{'address':hex(nearest['Address']),'name':nearest['Name']},'candidate_only_until_cfg_verifies_instruction':True})
 row['references']=refs
(OUT/'ep-scale-literal-candidates.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(rows,ensure_ascii=False,indent=2))
