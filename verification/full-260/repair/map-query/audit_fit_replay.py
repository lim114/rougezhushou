"""Read-only reproduction and canonical-output evidence for proposed repair."""
import hashlib
import importlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import scripts
scripts.__path__ = [str(HERE / 'candidate/scripts'), *scripts.__path__]
from scripts.map_fit_replay import verify_fit_replay
ground = importlib.import_module('scripts.extend_fixed_map_projections')
ground.ROOT = ROOT
ground.BASE = ROOT / 'research/p3-map-ground-current'
ground.CANONICAL_PATH = ROOT / 'research/p3-direct-ground-current/prior-regular-projections.json'
direct = importlib.import_module('scripts.build_fixed_landmark_references')
direct.ROOT = ROOT
direct.BASE = ROOT / 'research/p3-direct-ground-current'

def read(path): return json.loads(path.read_text(encoding='utf-8'))
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

protected = [p for folder in ('p3-map-ground-current', 'p3-direct-ground-current', 'p3-map-direct-continuation')
             for p in (ROOT / 'research' / folder).iterdir() if p.is_file()]
protected += [ROOT / 'rouge/data/battle-map-projections.json', ROOT / 'rouge/data/fixed-landmark-references.json']
before = {p.relative_to(ROOT).as_posix(): sha(p) for p in protected}
rows = []
for folder, count in (('p3-map-ground-current', 4), ('p3-direct-ground-current', 3)):
    base = ROOT / 'research' / folder
    for number in range(1, count + 1):
        observation = read(base / f'frozen-observation-{number}.json')['calibrations'][0]
        frozen = read(base / f'initial-fit-{number}.json')[0]
        current = ground.fit(observation)
        replay = verify_fit_replay(current, frozen)
        differences = replay['differing_computed_leaves']
        rows.append({'source': folder, 'observation': number,
                     'accepted_current': current['accepted'], 'accepted_frozen': frozen['accepted'],
                     'current_max_error_px': max(p['error_px'] for p in current['checks']),
                     'frozen_max_error_px': max(p['error_px'] for p in frozen['checks']),
                     'max_absolute_difference': max((p['difference'] for p in differences), default=0),
                     'max_fraction_of_allowed_replay': max((p['difference'] / p['allowed_numeric_difference'] for p in differences), default=0),
                     'replay': replay})
output, receipt = ground.build()
original_receipt = read(ground.BASE / 'build-receipt.json')
if receipt != original_receipt: raise AssertionError('Published ground receipt changed.')
if output != read(ground.CANONICAL_PATH): raise AssertionError('Published canonical ground values changed.')
_, direct_receipt = direct.build()
if direct_receipt != read(direct.BASE / 'verification.json'):
    raise AssertionError('Published direct baseline receipt changed.')
from scripts.extend_map_direct_continuation import build as continuation
extension, extension_receipt = continuation()
current = read(ROOT / 'rouge/data/fixed-landmark-references.json')
baseline, _ = direct.build()
for candidate in (baseline, extension):
    for group in ('references', 'stages'):
        for key, value in candidate[group].items():
            if current[group].get(key) != value:
                raise AssertionError('Original/section242 source-bound entry changed: ' + key)
after = {p.relative_to(ROOT).as_posix(): sha(p) for p in protected}
if before != after: raise AssertionError('Read-only audit mutated source or production.')
import cv2
import numpy as np
print(json.dumps({'cv2_version': cv2.__version__, 'numpy_version': np.__version__, 'rows': rows,
                  'canonical_output_sha256': receipt['output_sha256'],
                  'canonical_receipt_unchanged': True, 'direct_baseline_receipt_unchanged': True,
                  'section242_entries_exact': True, 'section242_counts': extension_receipt,
                  'protected_sources_sha256': before, 'read_only_hashes_unchanged': True}, ensure_ascii=False, indent=2))
