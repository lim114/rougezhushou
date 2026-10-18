from pathlib import Path
from hashlib import sha256
import ast,json,shutil
ROOT=Path(__file__).resolve().parents[1];source=ROOT/'.cache/p3-310-model/revision3-player-wording';h=source/'HANDOFF_FINAL.json'
assert sha256(h.read_bytes()).hexdigest()=='5d628685aa5af92b2d8c76964de1dd99ae7a2498fb74f000ec360904a116e8f1'
meta=json.loads(h.read_bytes());base=ROOT/meta['candidate_root'];data=ROOT/'rouge/data/boss-cycle-reference.json';original=data.read_bytes()
assert sha256(original).hexdigest()==meta['data_unchanged']['sha256']
for name,pin in meta['promotion_files'].items():
    p=ROOT/name;assert sha256(p.read_bytes()).hexdigest()==meta['required_before'][name]['sha256']
    raw=(base/name).read_bytes();assert sha256(raw).hexdigest()==pin['sha256']and len(raw)==pin['bytes']
    if name.endswith('.py'):ast.parse(raw)
    p.write_bytes(raw)
assert data.read_bytes()==original
out=ROOT/'verification/sections/310-preparation/player-wording-refinement';out.mkdir()
for name in('HANDOFF_FINAL.json','correction-final.json','HANDOFF.json'):(out/name).write_bytes((source/name).read_bytes())
(out/'execution-apply.py').write_bytes(Path(__file__).read_bytes())
print(json.dumps({'final_five_files_promoted':True,'data_and_original_sources_changed':False,'tests_or_native_pending':True}))
