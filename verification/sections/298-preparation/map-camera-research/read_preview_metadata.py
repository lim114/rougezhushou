"""Reuse only the pure-file metadata reader prefix for exact preview signatures."""
from hashlib import sha256
import json
from pathlib import Path
import struct

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
reader=ROOT/'.cache/research/p2-native-current-263/read_metadata_static.py'
raw=reader.read_bytes()
prefix=raw.decode('utf8').split('selected=[]\n')[0]
assert len(prefix)<len(raw.decode('utf8'))
ns={'__file__':str(reader)}
exec(compile(prefix,str(reader),'exec'),ns)
proof=json.loads((ROOT/'.cache/research/p2-native-current-263/mapping-verification.json').read_bytes())
assert sha256(ns['binary']).hexdigest()==proof['game_dll_sha256']
assert sha256(ns['meta']).hexdigest()==proof['metadata_sha256']
parameters=ns['records']('parameters','Iii')
cfg=json.loads((HERE/'preview-camera-cfg.json').read_bytes())
wanted={r['method']['metadata_method_index']for r in cfg['methods']}
methods=[]
for index in sorted(wanted):
 m=ns['methods'][index]
 methods.append({'index':index,'owner':ns['type_def_name'](m[1]),'method':ns['string'](m[0]),
  'return_type':ns['typename'](m[2]),'flags':hex(m[6]),
  'parameters':[{'name':ns['string'](p[0]),'type':ns['typename'](p[2])}for p in parameters[m[3]:m[3]+m[9]]]})
types=[]
for ti,td in enumerate(ns['types']):
 name=ns['type_def_name'](ti)
 if name not in {'Torappu.UI.CommonMapPreviewDlg','Torappu.Battle.MapGraphic','Torappu.Battle.Map','Torappu.UI.Roguelike.RL06.RL06FocusViewPlugin'}:continue
 fp=ns['reg']['fields'][ti]
 offsets=struct.unpack_from('<'+str(td[19])+'i',ns['binary'],ns['offset'](fp))if fp and td[19]else[]
 fields=[{'index':fi,'name':ns['string'](ns['fields'][fi][0]),'type':ns['typename'](ns['fields'][fi][1]),
  'native_offset':offsets[j]if offsets else None}for j,fi in enumerate(range(td[8],td[8]+td[19]))]
 types.append({'type_index':ti,'name':name,'fields':fields})
spans=[]
for method in cfg['methods']:
 for instruction in method['instructions']:
  offset=int(instruction['physical_offset'],0);blob=bytes.fromhex(instruction['bytes'])
  assert ns['binary'][offset:offset+len(blob)]==blob
  spans.append({'address':instruction['address'],'physical_offset':offset,'raw_hex':blob.hex()})
result={'kind':'FRESH_ORIGINAL_STATIC_PREVIEW_SIGNATURES_AND_FIELDS_NOT_CAPTURE_PROOF',
 'reader_sha256':sha256(raw).hexdigest(),'dll_sha256':proof['game_dll_sha256'],'metadata_sha256':proof['metadata_sha256'],
 'methods':methods,'types':types,'fresh_checked_method_instruction_rows':len(spans),
 'whole_dynamic_graph_or_current_runtime_instance_proven':False,
 'game_or_process_or_Qt_or_fit_operations':False}
(HERE/'preview-signatures-fields.json').write_bytes((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode())
print(json.dumps({'methods':methods,'common_preview_fields':next(t['fields']for t in types if t['name']=='Torappu.UI.CommonMapPreviewDlg'),
 'fresh_checked_method_instruction_rows':len(spans)},ensure_ascii=False,indent=2))
