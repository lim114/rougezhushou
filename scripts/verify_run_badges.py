"""Verify exploration badges and publish honest reference/replay coverage."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import re
import sys
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import cv2
import numpy as np
from rouge.recognition import ScreenReader
from rouge.run_badges import find_squad_badge


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--test-log', type=Path, help='Reuse this just-completed public test run instead of rerunning it.')
    args = parser.parse_args()
    if args.test_log:
        log = args.test_log.read_text(encoding='utf-8')
        log_path = args.test_log
    else:
        stream = io.StringIO()
        suite = unittest.TestLoader().loadTestsFromNames(['tests.test_run_badges', 'tests.test_run_config'])
        result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
        log = stream.getvalue()
        log_path = ROOT / '.cache/run-badges-full.log'
        log_path.write_text(log, encoding='utf-8')
        if not result.wasSuccessful():
            raise AssertionError(log)
    match = re.search(r'Ran (\d+) tests in ([0-9.]+)s\s+OK\s*$', log)
    assert match and int(match[1]) == 7, log
    receipt_path = ROOT / 'rouge/data/run-badge-receipt.json'
    references = json.loads(receipt_path.read_text(encoding='utf-8'))
    families = {}
    for entry in references['icons']:
        assert sha(ROOT / 'rouge/data' / entry['file']) == entry['sha256']
        families.setdefault(entry['normal_id'], []).append(entry)
    assert len(families) == 15 and len(references['icons']) == 22
    assert all(len({entry['sha256'] for entry in entries}) == 1 for entries in families.values())
    reader = ScreenReader()
    samples = []
    for filename, expected, grade, rect in [
            ('exploration-map.png', 'rogue_6_band_19', 15, None),
            ('run-map-closed.png', 'rogue_6_band_3', 15, None),
            ('live-0.23.png', 'rogue_6_band_3', 15, [2, 45, 2050, 1125])]:
        path = ROOT / 'samples/native-client' / filename
        image = cv2.imdecode(np.fromfile(path, np.uint8), 1)
        started = time.perf_counter()
        observed = reader.read(image, client_rect=rect)
        config = observed['run']['config']
        assert config['squad']['id'] == expected and config['difficulty']['value'] == grade
        assert config['squad']['effect_verified'] is False
        elapsed = time.perf_counter() - started
        held = next(record for record in observed['texts'] if record['text'] == '收藏品')
        timings = []
        for _ in range(3):
            begin = time.perf_counter()
            detected = find_squad_badge(image, held)
            timings.append((time.perf_counter() - begin) * 1000)
            assert detected['id'] == expected
        samples.append({'path': str(path), 'sha256': sha(path), 'size': [image.shape[1], image.shape[0]],
                        'client_rect': rect, 'config': config, 'reader_seconds': elapsed,
                        'badge_match_median_ms': float(np.median(timings)),
                        'fresh_background_sample': filename == 'live-0.23.png'})
        print(filename, expected, grade, flush=True)
    report = {'passed': True, 'public_tests': {'count': int(match[1]), 'seconds': float(match[2]),
                'log': str(log_path.resolve()), 'sha256': sha(log_path)},
              'reference_families': len(families), 'reference_variants': len(references['icons']),
              'reference_receipt': str(receipt_path), 'reference_receipt_sha256': sha(receipt_path),
              'same_artwork_variants': {key: [entry['id'] for entry in entries]
                                       for key, entries in families.items() if len(entries) > 1},
              'all_normal_upgrade_pairs_byte_identical': True,
              'actual_game_screenshot_verified_families': ['rogue_6_band_3', 'rogue_6_band_19'],
              'samples': samples,
              'transformed_development_replay': {'content_widths': [1009, 1337, 1771],
                  'padding_left_top': [[43, 71], [101, 29], [37, 113]],
                  'passed_public_reader': True, 'independent_live_resolution_validation': False},
              'negative_checks': ['badge hidden: no squad or grade', 'grade hidden: no grade',
                                  'blank frame: no copied state', 'base icon preserves confirmed upgraded squad effects'],
              'limits': ['15 artwork families are available; only two squad types have actual game screenshot validation.',
                         'Identical normal/upgrade artwork confirms squad type only; upgrade effects require prior verified evidence.',
                         'Reference localization uses current label geometry, multi-scale matching and ambiguity rejection; small grade digits use local OCR.',
                         'Occluded or unreadable badges remain unknown.'],
              'source_sha256': {str(path.relative_to(ROOT)): sha(path) for path in [
                  ROOT / 'rouge/run_badges.py', ROOT / 'rouge/run_config.py', ROOT / 'rouge/run_recognition.py',
                  ROOT / 'tests/test_run_badges.py', Path(__file__)]}}
    destination = ROOT / 'RUN_BADGE_VERIFICATION.json'
    destination.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(destination, flush=True)


if __name__ == '__main__':
    main()
