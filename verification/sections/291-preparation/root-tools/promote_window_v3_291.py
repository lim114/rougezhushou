from pathlib import Path
from hashlib import sha256
import json
ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'.cache/p3-291-window-v3/verify_peace_guardian_window_291.py'
target=ROOT/'scripts/verify_peace_guardian_window_291.py'
sha=lambda raw:sha256(raw).hexdigest()
assert sha(source.read_bytes())=='291b7004ae1a40245ecc3693d4301d8eb0904c10d88596ddea0b9d984899ee28'
assert sha(target.read_bytes())=='e14e68e4f994677c205c90220d6ae2f3e593b89b62a13d6468ae7a09b00ab003'
archive=ROOT/'verification/sections/291-preparation/window-v3-source';archive.mkdir()
with (archive/'before-v2.py').open('xb') as f:f.write(target.read_bytes())
for name in ('first-static-prepare.run.json','first-static-prepare.stdout.log','first-static-prepare.stderr.log'):
 p=source.parent/name
 if p.is_file():
  with (archive/name).open('xb') as f:f.write(p.read_bytes())
target.write_bytes(source.read_bytes())
print(json.dumps({'canonical_window_v3_promoted':True,'GUI_executed':False,'sha256':sha(target.read_bytes())}))
