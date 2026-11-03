from pathlib import Path
from hashlib import sha256
import ast,json,shutil
ROOT=Path(__file__).resolve().parents[1];source=ROOT/'.cache/p3-309-model';out=ROOT/'verification/sections/309-preparation'
h=source/'HANDOFF_FINAL.json';assert sha256(h.read_bytes()).hexdigest()=='eb4452b97e2505df0885d69712464589e8f90b68f8fdb320d30ca8edfdd3dffc'
meta=json.loads(h.read_bytes());base=ROOT/meta['candidate_root'];unchanged=[]
for name,pin in meta['promotion_files'].items():
    data=(base/name).read_bytes();assert sha256(data).hexdigest()==pin['sha256'] and len(data)==pin['bytes']
    dest=ROOT/name
    if dest.exists():
        assert dest.read_bytes()==data,'Never overwrite the frozen promoted original: '+name
        unchanged.append(name)
    else:
        dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
    if name.endswith('.py'):ast.parse(data)
for name in ['HANDOFF_FINAL.json','rendering-correction.json','UNBOUND_DRAFT_NOTICE.json','static-preparation.json']:
    shutil.copyfile(source/name,out/('backend-'+name))
sourcebuild=out/'candidate-first-source-build';shutil.copytree(source/'source-build-first',sourcebuild)
(out/'execution-promote-model.py').write_bytes(Path(__file__).read_bytes())
print(json.dumps({'promoted_files':len(meta['promotion_files']),'previously_promoted_originals_unchanged':len(unchanged),'tests_run':False}))
