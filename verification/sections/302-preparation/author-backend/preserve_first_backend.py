"""Preserve first actual24/F1 source before the DOM-location test correction."""
from hashlib import sha256
import json
from pathlib import Path
import shutil

HERE = Path(__file__).resolve().parent
CANDIDATE = HERE / 'candidate'
target = HERE / 'backend-first/source'
target.mkdir(exist_ok=False)
names = ['rouge/ritual_weakening.py', 'tests/test_ritual_weakening_302.py',
         'scripts/build_ritual_weakening_302.py', 'rouge/data/ritual-weakening.json']
names += [p.relative_to(CANDIDATE).as_posix() for p in (CANDIDATE / 'research/p3-ritual-weakening-302').iterdir() if p.is_file()]
manifest = {'kind': 'EXACT_FIRST_24_API_SOURCE_BEFORE_ONE_TEST_PREMISE_CORRECTION', 'files': {}}
for name in names:
    source = CANDIDATE / name
    destination = target / name
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)
    raw = destination.read_bytes()
    manifest['files'][name] = {'sha256': sha256(raw).hexdigest(), 'bytes': len(raw)}
(target / 'source-manifest.json').write_bytes((json.dumps(manifest, ensure_ascii=False, indent=2) + '\n').encode('utf8'))
print(json.dumps({'preserved_first_sources': len(names), 'product_or_live_modified': False}))
