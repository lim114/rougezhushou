"""Read the specific camera-config value type identified by GetCameraConfig's signature."""
from hashlib import sha256
import json
from pathlib import Path
import struct
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
reader=ROOT/'.cache/research/p2-native-current-263/read_metadata_static.py'
source=reader.read_bytes();prefix=source.decode().split('selected=[]\n')[0]
ns={'__file__':str(reader)}
exec(compile(prefix,str(reader),'exec'),ns)
out=[]
for ti,td in enumerate(ns['types']):
 name=ns['type_def_name'](ti)
 if name not in {'Torappu.Battle.MapGraphic+CameraConfig','Torappu.Battle.MapGraphic+CameraView'}:continue
 fp=ns['reg']['fields'][ti]
 offsets=struct.unpack_from('<'+str(td[19])+'i',ns['binary'],ns['offset'](fp))if fp and td[19]else[]
 fields=[{'index':fi,'name':ns['string'](ns['fields'][fi][0]),'type':ns['typename'](ns['fields'][fi][1]),
  'native_offset':offsets[j]if offsets else None}for j,fi in enumerate(range(td[8],td[8]+td[19]))]
 out.append({'type_index':ti,'name':name,'fields':fields})
result={'kind':'ORIGINAL_CAMERA_CONFIG_VALUE_TYPE_NOT_CAPTURE_MATRIX','types':out,
 'dll_sha256':sha256(ns['binary']).hexdigest(),'metadata_sha256':sha256(ns['meta']).hexdigest(),
 'reader_sha256':sha256(source).hexdigest(),'game_or_process_or_Qt_or_fit_operations':False}
(HERE/'camera-config-value-type.json').write_bytes((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode())
print(json.dumps(result,ensure_ascii=False,indent=2))
