"""Replay actual current frames; keep whole-source and local analysis limits separate."""
import hashlib
import json
from pathlib import Path
import sys
import time

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from rouge.recognition import ScreenReader
from verify_hybrid_059 import FIELDS, strict, differences


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    research = ROOT / '.cache/research/counter-reading-060'
    names = ('baseline-BV14aK26bEuP-curl-first-1791196081285290700.json',
             'baseline-gray_training-half-source-1791196090258445200.json')
    sources = [ROOT / 'rouge' / name for name in ('recognition.py', 'digit_counters.py',
        'counter_badges.py', 'local_counters.py', 'run_recognition.py', 'held_cards.py', 'held_footer.py')]
    sources.extend((Path(__file__), ROOT / 'scripts/verify_hybrid_059.py'))
    before = {p.relative_to(ROOT).as_posix(): sha(p) for p in sources}
    folder = research / ('actual-current-' + str(time.time_ns()))
    folder.mkdir()
    cases = []
    for name in names:
        old_path = research / name
        old = json.loads(old_path.read_text(encoding='utf-8'))
        path = ROOT / old['source']
        assert sha(path) == old['source_sha256']
        image = cv2.imdecode(np.fromfile(path, np.uint8), 1)
        started = time.perf_counter()
        current = ScreenReader().read(image)
        elapsed = time.perf_counter() - started
        diff = differences({k: strict(old['observation'].get(k)) for k in FIELDS},
                           {k: strict(current.get(k)) for k in FIELDS})
        row = {'source': old['source'], 'source_sha256': sha(path),
               'baseline': old_path.relative_to(ROOT).as_posix(), 'baseline_sha256': sha(old_path),
               'page': current['page'], 'elapsed_seconds': elapsed,
               'baseline_elapsed_seconds': old['elapsed_seconds'], 'differences': diff,
               'observation': current}
        target = folder / name.replace('baseline-', 'current-')
        target.write_text(json.dumps(row, ensure_ascii=False, indent=2), encoding='utf-8')
        cases.append({'path': target.relative_to(ROOT).as_posix(), 'sha256': sha(target),
                      'page': current['page'], 'differences': len(diff), 'elapsed_seconds': elapsed})
        print(json.dumps(cases[-1], ensure_ascii=False), flush=True)
    after = {p.relative_to(ROOT).as_posix(): sha(p) for p in sources}
    receipt = {'version': '0.60.0', 'passed': before == after and all(c['differences'] == 0 for c in cases),
               'cases': cases, 'source_sha256': before, 'source_sha256_after': after,
               'public_fields': FIELDS, 'excluded_nested_fields': ['elapsed_ms'],
               'whole_source_half_remains_unknown': cases[1]['page'] == 'unknown',
               'new_independent_positive': False, 'private_state_used': False, 'game_actions': 0,
               'scope': 'Full actual ScreenReader frame replay, separate from scaled analysis/local-counter recovery.'}
    target = folder / 'receipt.json'
    target.write_text(json.dumps(receipt, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'passed': receipt['passed'], 'receipt': target.relative_to(ROOT).as_posix()}), flush=True)
    return 0 if receipt['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
