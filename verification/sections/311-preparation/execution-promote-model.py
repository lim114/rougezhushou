from pathlib import Path
from hashlib import sha256
import json
ROOT = Path(__file__).resolve().parents[1]
origin = ROOT / '.cache/p3-311-model'
raw = (origin / 'HANDOFF_FINAL.json').read_bytes()
assert sha256(raw).hexdigest() == '742f3b96d723129a143f96fff9bdb7f5d27b0c8cd93c8ba15651622aced042cd'
h = json.loads(raw)
assert h['actual_backend_final']['tests'] == h['actual_backend_final']['passed'] == 26
assert h['actual_backend_final']['skipped'] == h['actual_backend_final']['errors'] == h['actual_backend_final']['failed'] == 0
for name, pin in h['promotion_files'].items():
    target = ROOT / name
    assert target.resolve().is_relative_to(ROOT.resolve()) and not target.exists(), name
    content = (origin / 'candidate' / name).read_bytes()
    assert sha256(content).hexdigest() == pin['sha256'] and len(content) == pin['bytes'], name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(content)
out = ROOT / 'verification/sections/311-preparation'
(out / 'backend-final-handoff.json').write_bytes(raw)
(out / 'execution-promote-model.py').write_bytes(Path(__file__).read_bytes())
print(json.dumps({'section': 311, 'promoted_files': len(h['promotion_files']),
                  'root_product_or_native_acceptance': False}, ensure_ascii=False))
