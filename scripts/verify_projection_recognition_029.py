"""Paired current/0.28 image replay; no screenshots, game input, or state writes."""
import copy
import hashlib
import importlib.util
import json
import statistics
import sys
import time
from collections import Counter
from pathlib import Path
from unittest.mock import patch

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from rouge import relic_recognition as current
from rouge.recognition import ScreenReader
from rouge.recognition_cache import ExactImageCache
from rouge import run_recognition

DEST = ROOT / '.cache/recognition-029'
BASELINE = ROOT / '.cache/batch-029-before/rouge/relic_recognition.py'


def load_baseline():
    spec = importlib.util.spec_from_file_location('rouge._relic_baseline_029', BASELINE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    # Source is the saved 0.28 file; both implementations read the same
    # immutable icon assets beside the production file, not copied assets.
    module.__file__ = str(ROOT / 'rouge/relic_recognition.py')
    return module


def clear_templates(module):
    for name in ('templates', 'prepared_templates', '_reference_image', '_refined_template', 'artwork_families'):
        getattr(module, name).cache_clear()


def counted(module, image, anchor, count):
    stats = Counter()
    original = module._can_match
    def verify(*args):
        stats['rgb_screen_calls'] += 1
        return original(*args)
    if hasattr(module, 'ProjectionScreen'):
        projection = module.ProjectionScreen.possible
        def projected(self, *args):
            stats['projection_calls'] += 1
            answer = projection(self, *args)
            stats['projection_rejections'] += int(not answer)
            stats['peak_window_cache_bytes'] = max(stats['peak_window_cache_bytes'], self.cache_bytes)
            stats['peak_window_cache_entries'] = max(stats['peak_window_cache_entries'], len(self.windows))
            return answer
        context = patch.object(module.ProjectionScreen, 'possible', projected)
    else:
        from contextlib import nullcontext
        context = nullcontext()
    with patch.object(module, '_can_match', verify), context:
        started = time.perf_counter()
        records = module.match_held_icons(image, anchor, count)
        elapsed = (time.perf_counter() - started) * 1000
    return records, elapsed, dict(stats)


def variants(fixture, image):
    yield fixture['file'] + ':native', image, fixture['anchor']
    if fixture['file'] != 'run-relic-multicard-closed.png':
        return
    for width in (1009, 1280, 1337, 1600, 1771, 2560):
        resized = cv2.resize(image, (width, round(image.shape[0] * width / image.shape[1])))
        yield fixture['file'] + ':width=' + str(width), resized, fixture['anchor']
    shifted = cv2.copyMakeBorder(image, 75, 110, 137, 90, cv2.BORDER_CONSTANT)
    anchor = copy.deepcopy(fixture['anchor'])
    anchor['box'] = [[(p[0] * image.shape[1] + 137) / shifted.shape[1],
                      (p[1] * image.shape[0] + 75) / shifted.shape[0]] for p in anchor['box']]
    yield fixture['file'] + ':translated', shifted, anchor
    yield fixture['file'] + ':blank', np.zeros_like(image), fixture['anchor']
    obscured = image.copy()
    obscured[1010:1120, 300:900] = 0
    yield fixture['file'] + ':obscured', obscured, fixture['anchor']


def main():
    DEST.mkdir(exist_ok=True)
    start = time.perf_counter()
    baseline = load_baseline()
    fixtures = json.loads((ROOT / '.cache/relic-recognition-fixtures-022.json').read_text(encoding='utf-8'))
    rows = []
    source_hash = hashlib.sha256((ROOT / 'rouge/relic_recognition.py').read_bytes()).hexdigest()
    for fixture in fixtures:
        path = ROOT / 'samples/native-client' / fixture['file']
        assert hashlib.sha256(path.read_bytes()).hexdigest() == fixture['sample_sha256']
        image = cv2.imdecode(np.fromfile(path, dtype=np.uint8), 1)
        for case, variant, anchor in variants(fixture, image):
            clear_templates(baseline)
            clear_templates(current)
            old, old_ms, old_counts = counted(baseline, variant, anchor, fixture['count'])
            new, new_ms, new_counts = counted(current, variant, anchor, fixture['count'])
            assert old == new, case
            assert new_counts.get('peak_window_cache_bytes', 0) <= current.ProjectionScreen.max_cache_bytes
            assert new_counts.get('peak_window_cache_entries', 0) <= current.ProjectionScreen.max_cache_entries
            row = {'case': case, 'sample_sha256': fixture['sample_sha256'], 'size': list(variant.shape[:2]),
                'identical_records_scores_centers': True, 'records': new,
                'before_cold_ms': old_ms, 'after_cold_ms': new_ms,
                'before_counts': old_counts, 'after_counts': new_counts}
            if case.endswith(':native') and fixture['file'] in ('run-relic-multicard-closed.png', 'run-relic-multicard.png'):
                times = {False: [], True: []}
                for after in (False, True, True, False, False, True):
                    module = current if after else baseline
                    begun = time.perf_counter()
                    found = module.match_held_icons(variant, anchor, fixture['count'])
                    times[after].append((time.perf_counter() - begun) * 1000)
                    assert found == new, case
                row['before_warm_ms'] = times[False]
                row['after_warm_ms'] = times[True]
                row['before_median_ms'] = statistics.median(times[False])
                row['after_median_ms'] = statistics.median(times[True])
                row['speedup'] = row['before_median_ms'] / row['after_median_ms']
                assert row['speedup'] > 1.05, (case, row['speedup'])
            # Exact-image cache still clones outputs; a changed bar is recomputed.
            cache = ExactImageCache()
            first = current.match_held_icons(variant, anchor, fixture['count'], cache=cache)
            second = current.match_held_icons(variant, anchor, fixture['count'], cache=cache)
            assert first == second == new
            assert cache.hits == 1
            if first:
                first[0]['candidates'].append('caller_mutation')
                assert current.match_held_icons(variant, anchor, fixture['count'], cache=cache) == new
            rows.append(row)
            print(json.dumps({'case': case, 'equal': True,
                'before_cold_ms': round(old_ms, 1), 'after_cold_ms': round(new_ms, 1),
                'rgb_before': old_counts.get('rgb_screen_calls', 0),
                'rgb_after': new_counts.get('rgb_screen_calls', 0)}, ensure_ascii=False), flush=True)
    public = []
    reader = ScreenReader(cache_enabled=False)
    for fixture in fixtures:
        image = cv2.imdecode(np.fromfile(ROOT / 'samples/native-client' / fixture['file'], dtype=np.uint8), 1)
        with patch.object(run_recognition, 'match_held_icons', baseline.match_held_icons):
            before = reader.read(image)
        after = reader.read(image)
        assert before['run'] == after['run'], fixture['file']
        assert before['page'] == after['page'], fixture['file']
        public.append({'sample': fixture['file'], 'identical_public_run_and_page': True,
            'before_total_ms': before['performance']['total_ms'], 'after_total_ms': after['performance']['total_ms']})
        print(json.dumps({'public_sample': fixture['file'], 'same_run': True,
            'before_total_ms': before['performance']['total_ms'],
            'after_total_ms': after['performance']['total_ms']}, ensure_ascii=False), flush=True)
    assert len(rows) == 14 and len(public) == 5
    proofs = {'rows': rows, 'public': public, 'source_sha256': source_hash,
        'baseline_source_sha256': hashlib.sha256(BASELINE.read_bytes()).hexdigest()}
    (DEST / 'paired-replay.json').write_text(json.dumps(proofs, ensure_ascii=False, indent=2), encoding='utf-8')
    benchmark = [{key: row[key] for key in ('case', 'before_median_ms', 'after_median_ms', 'speedup')}
        for row in rows if 'speedup' in row]
    receipt = {'version': '0.29.0', 'passed': True, 'verified_at': time.time(),
        'seconds': round(time.perf_counter() - start, 3), 'paired_visual_cases': len(rows),
        'public_reader_cases': len(public), 'exact_records_scores_centers_preserved': True,
        'warm_comparison_repeats_per_version': 3, 'benchmarks': benchmark,
        'max_projection_cache_bytes': max(r['after_counts'].get('peak_window_cache_bytes', 0) for r in rows),
        'max_projection_cache_entries': max(r['after_counts'].get('peak_window_cache_entries', 0) for r in rows),
        'source_sha256': source_hash, 'baseline_source_sha256': proofs['baseline_source_sha256'],
        'evidence': '.cache/recognition-029/paired-replay.json', 'new_game_captures': 0,
        'game_actions': 0, 'chat_requests': 0,
        'limits': ['Development replays, not an independent full-inventory accuracy set.',
            'Transformed bars carry the recorded label geometry; five public reads rediscover current anchors.',
            'Only held-icon matching improved; OCR text, maps and full cultivation fields still use existing readers.',
            'No previous-frame approximate pixel reuse or relaxed identity/ambiguity thresholds.',
            'Timings depend on hardware and load; warm medians reuse templates but not image results.',
            'Public reader times are single ordered reads with OCR warmup differences; only semantics are accepted there.',
            'Coarse projection is a lower bound only; final identities and refinements use original RGB scores.']}
    (ROOT / 'RECOGNITION_0.29_VERIFICATION.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({k: receipt[k] for k in ('passed', 'paired_visual_cases', 'public_reader_cases', 'benchmarks', 'seconds')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
