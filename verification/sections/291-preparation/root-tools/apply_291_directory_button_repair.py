from pathlib import Path
from hashlib import sha256
import json
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'.cache/p3-291-directory-button-repro'
DEST=ROOT/'verification/sections/291-preparation/directory-button-repair'
assert not DEST.exists()
plan=json.loads((ROOT/'.cache/p3-291-promotion-readiness/PROMOTION_FILES.json').read_bytes())
previous={r['destination']:r['candidate']['sha256'] for r in plan['files']}
names={'rouge/app.py':'3aec0d31082ceba9541ae854c5aa1cb17ef43a013546514e8f1b0302c754c491',
 'tests/test_resident_reference_signals_291.py':'6a180d74ddadda6033a79a8e2e46191e3194bbdb02c9aad0a2d4e44f688f2f6c'}
def sha(raw):return sha256(raw).hexdigest()
for name,value in names.items():
 assert sha((ROOT/name).read_bytes())==previous[name]
 assert sha((BASE/'candidate'/name).read_bytes())==value
copies={}
for folder in ('first-actual','second-actual','candidate'):
 for p in (BASE/folder).rglob('*'):
  assert not p.is_symlink()
  if p.is_file():
   assert p.suffix in {'.py','.json','.txt','.log','.exit','.diff'}
   copies[p.relative_to(BASE).as_posix()]=p.read_bytes()
for name in names:copies['before-repair/'+name]=(ROOT/name).read_bytes()
DEST.mkdir(parents=True)
for name,raw in copies.items():
 p=DEST/name;p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('xb') as f:f.write(raw)
for name in names:(ROOT/name).write_bytes((BASE/'candidate'/name).read_bytes())
manifest={'kind':'291_ACTUAL_DIRECTORY_BUTTON_FAILURE_AND_MINIMAL_REPAIR_PUBLIC_ONLY',
 'files':{n:{'bytes':len(v),'sha256':sha(v)} for n,v in copies.items()},
 'initial_setup_failure_not_a_test_failure':True,'second_actual_single_test_failures':1,
 'after_repair_tests_not_run':True,'private_state_copied':False}
with (DEST/'archive-manifest.json').open('xb') as f:f.write((json.dumps(manifest,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
print(json.dumps({'files_repaired':len(names),'public_failure_and_preimages_archived':len(copies),'tests_pending':True}))
