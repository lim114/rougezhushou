from pathlib import Path
from hashlib import sha256
import ast,json,shutil
ROOT=Path(__file__).resolve().parents[1];source=ROOT/'.cache/p3-309-model/revision2-flight-inline'
h=source/'HANDOFF.json';assert sha256(h.read_bytes()).hexdigest()=='fe6120295ac425072d63130212fed81c21ccf65dbb0b9a40f4a1f15785679cbb'
meta=json.loads(h.read_bytes());base=ROOT/meta['candidate_root']
for name,pin in meta['promotion_files'].items():
    p=ROOT/name;assert sha256(p.read_bytes()).hexdigest()==meta['required_before'][name]['sha256']
    data=(base/name).read_bytes();assert sha256(data).hexdigest()==pin['sha256'] and len(data)==pin['bytes']
    if name.endswith('.py'):ast.parse(data)
    p.write_bytes(data)
out=ROOT/'verification/sections/309-preparation/flight-inline-refinement';out.mkdir()
for name in ['HANDOFF.json','correction.json']:shutil.copyfile(source/name,out/name)
(out/'execution-promotion.py').write_bytes(Path(__file__).read_bytes())
print(json.dumps({'five_files_promoted':True,'source_data_original_bytes_changed':False,'tests_not_yet_rerun':True}))
