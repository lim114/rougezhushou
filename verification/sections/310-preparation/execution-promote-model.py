from pathlib import Path
from hashlib import sha256
import ast,json,shutil
ROOT=Path(__file__).resolve().parents[1];source=ROOT/'.cache/p3-310-model/revision2-reading';h=source/'HANDOFF_FINAL.json'
assert sha256(h.read_bytes()).hexdigest()=='57a2f63a6a836f51d8e35e2e8250ce27a026f8437350f33aceafa72e2e66a136'
meta=json.loads(h.read_bytes());base=ROOT/meta['candidate_root'];existing=[]
for name,pin in meta['promotion_files'].items():
    raw=(base/name).read_bytes();assert sha256(raw).hexdigest()==pin['sha256']and len(raw)==pin['bytes']
    target=ROOT/name
    if target.exists():assert target.read_bytes()==raw,name;existing.append(name)
    else:target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
    if name.endswith('.py'):ast.parse(raw);assert not raw.endswith(b'\n\n')and not raw.endswith(b'\r\n\r\n'),name
out=ROOT/'verification/sections/310-preparation';(out/'backend-final-handoff.json').write_bytes(h.read_bytes())
for p in source.iterdir():
    if p.is_file()and p.name!='HANDOFF_FINAL.json':shutil.copyfile(p,out/('backend-final-'+p.name))
shutil.copytree(ROOT/'.cache/p3-310-model/source-build-first',out/'candidate-first-source-build')
(out/'execution-promote-model.py').write_bytes(Path(__file__).read_bytes())
print(json.dumps({'promoted_files':len(meta['promotion_files']),'frozen_existing_source_files_unchanged':len(existing),'tests_or_Qt_run':False}))
