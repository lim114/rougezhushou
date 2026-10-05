"""File-only rel32 call candidates for two exact dataflow functions."""
from pathlib import Path
import bisect,hashlib,json,struct
OUT=Path(__file__).resolve().parent
verification=json.loads((OUT.parent/'p1-native-mapping-054/mapping-verification.json').read_text(encoding='utf-8'))
game=Path(verification['source_game_dll']);binary=game.read_bytes()
assert hashlib.sha256(binary).hexdigest()==verification['game_dll_sha256']
methods=json.loads((OUT.parent/'p1-native-mapping-054/script.json').read_text(encoding='utf-8'))['ScriptMethod']
base=verification['image_base'];sections=verification['sections']
pe=struct.unpack_from('<I',binary,60)[0];opt=pe+24
er,es=struct.unpack_from('<II',binary,opt+112+3*8)
eo=next(s['offset']+er-s['rva'] for s in sections if s['rva']<=er<s['rva']+s['raw_size'])
functions=list(struct.iter_unpack('<III',binary[eo:eo+es]));starts=[f[0] for f in functions]
targets={0x180ac6c40:'UnitDataFlowConfig.Init',0x180ac6990:'UnitDataFlowConfig.GetDelta'}
rows=[]
for s in sections:
 if not s['characteristics']&0x20000000:continue
 start=s['offset'];end=start+s['raw_size'];cursor=start
 while True:
  hit=binary.find(b'\xe8',cursor,end)
  if hit<0:break
  cursor=hit+1
  if hit+5>end:continue
  rva=s['rva']+hit-start;address=base+rva
  target=address+5+struct.unpack_from('<i',binary,hit+1)[0]
  if target not in targets:continue
  index=bisect.bisect_right(starts,rva)-1
  pdata=functions[index] if index>=0 and functions[index][0]<=rva<functions[index][1] else None
  containing=[{'name':m['Name'],'address':hex(m['Address']),'index':m['metadata_method_index']} for m in methods if pdata and m['rva']==pdata[0]]
  rows.append({'candidate_call':hex(address),'bytes':binary[hit:hit+5].hex(),'target':hex(target),'target_name':targets[target],'pdata':list(pdata) if pdata else None,'containing_methods':containing,'candidate_only_until_cfg_verifies_instruction':True})
(OUT/'dataflow-call-candidates.json').write_text(json.dumps({'dll_sha256':hashlib.sha256(binary).hexdigest(),'calls':rows,'file_only':True},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(rows,ensure_ascii=False,indent=2))
