"""Summarize saved index/JSON shapes without dumping whole tables to the console."""
import collections
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent
a=json.loads((HERE/'narrow-name-candidates.json').read_bytes())
groups=collections.Counter(x['Name'].split('$$')[0] for x in a)
selected={k:v for k,v in groups.items()if not any(w in k for w in ('Arkvent','Sandbox','Activity','AVG','FlatBuffers'))}
o=json.loads((HERE/'original-input-inventory.json').read_bytes())
sample=o['sample_stage'][0]
if type(sample)is list and len(sample)==2:sample=sample[1]
stage={k:sample[k]for k in ('id','image','level_source')if k in sample}
result={'native_types':selected,'level_map_camera_variants':sorted({json.dumps(x['mapData_camera_fields'],sort_keys=True)for x in o['levels']}),
 'level_top_keys':o['levels'][0]['top_keys'],'level_mapData_keys':o['levels'][0]['mapData_keys'],
 'sample_stage_identity':stage}
(HERE/'compact-inventory.json').write_bytes((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode())
print(json.dumps(result,ensure_ascii=False,indent=2))
