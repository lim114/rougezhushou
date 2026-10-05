"""Repeatable held-bar replay evidence; saved captures are development fixtures."""
import argparse
import copy
import hashlib
import json
import statistics
import sys
import time
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from rouge.recognition import ScreenReader
from rouge.relic_recognition import match_held_icons, templates
from rouge.recognition_cache import ExactImageCache


def semantic(records):
    return sorted(({
        'id': item['id'], 'candidates': item['candidates'],
        'confirmed': item['confirmed'], 'center': item['center'],
    } for item in records), key=lambda item: item['center'])


def identity(records):
    return sorted((i['id'],i['candidates'],i['confirmed']) for i in records)


def run(phase):
    source_sha256=hashlib.sha256((ROOT/'rouge/relic_recognition.py').read_bytes()).hexdigest()
    fixture_path = ROOT / '.cache/relic-recognition-fixtures-022.json'
    samples = ROOT / 'samples/native-client'
    names = ['run-relic-multicard-closed.png', 'run-relic-multicard.png',
             'run-map-closed.png', 'run-roster.png', 'run-emergency-mechanist.png']
    if phase == 'baseline':
        reader = ScreenReader(cache_enabled=False)
        fixtures = []
        for name in names:
            image = cv2.imdecode(np.fromfile(samples / name, dtype=np.uint8), 1)
            started = time.perf_counter()
            read = reader.read(image)
            anchor = next((t for t in read['texts'] if t['text'] == '收藏品'), None)
            anchor = anchor or next(t for t in read['texts'] if t['text'] == '收起')
            fixtures.append({'file': name, 'anchor': anchor, 'count': read['run']['relics']['count'],
                             'run': read['run'], 'page': read['page'],
                             'screen_reader_ms': (time.perf_counter() - started) * 1000,
                             'sample_sha256': hashlib.sha256((samples / name).read_bytes()).hexdigest()})
        fixture_path.parent.mkdir(exist_ok=True)
        fixture_path.write_text(json.dumps(fixtures, ensure_ascii=False, indent=2), encoding='utf8')
    else:
        fixtures = json.loads(fixture_path.read_text(encoding='utf8'))

    rows = []
    for fixture in fixtures:
        original = cv2.imdecode(np.fromfile(samples / fixture['file'], dtype=np.uint8), 1)
        variants = [(f"{fixture['file']}:native", original, fixture['anchor'])]
        if fixture['file'] == names[0]:
            for width in (1280, 1600, 2560):
                image = cv2.resize(original, (width, round(original.shape[0] * width / original.shape[1])))
                variants.append((f"{fixture['file']}:width={width}", image, fixture['anchor']))
            # Move the whole page and its detected label together: no absolute screen ROI.
            image = cv2.copyMakeBorder(original, 75, 110, 137, 90, cv2.BORDER_CONSTANT)
            anchor = copy.deepcopy(fixture['anchor'])
            anchor['box'] = [[(p[0]*original.shape[1]+137)/image.shape[1],
                              (p[1]*original.shape[0]+75)/image.shape[0]] for p in anchor['box']]
            variants.append((f"{fixture['file']}:translated", image, anchor))
            variants.append((f"{fixture['file']}:blank", np.zeros_like(original), fixture['anchor']))
            obscured = original.copy()
            # Controlled replay obstruction. This is not an additional captured game state.
            obscured[1010:1120, 300:900] = 0
            variants.append((f"{fixture['file']}:obscured", obscured, fixture['anchor']))
        for name, image, anchor in variants:
            templates.cache_clear()
            try:
                from rouge.relic_recognition import prepared_templates
                prepared_templates.cache_clear()
            except ImportError:
                pass
            if phase=='refined':
                from rouge.relic_recognition import _reference_image,_refined_template
                _reference_image.cache_clear();_refined_template.cache_clear()
            cache = ExactImageCache()
            start = time.perf_counter()
            first = match_held_icons(image, anchor, fixture['count'], cache=cache)
            cold = (time.perf_counter() - start) * 1000
            timings = []
            for _ in range(3):
                start = time.perf_counter()
                match_held_icons(image, anchor, fixture['count'])
                timings.append((time.perf_counter() - start) * 1000)
            start = time.perf_counter()
            hit = match_held_icons(image, anchor, fixture['count'], cache=cache)
            cached = (time.perf_counter() - start) * 1000
            assert first == hit
            row = {'case': name, 'cold_ms': cold, 'uncached_median_ms': statistics.median(timings),
                   'exact_cache_ms': cached, 'icons': first, 'semantic': semantic(first)}
            rows.append(row)
            print(json.dumps({k: row[k] for k in ('case', 'cold_ms', 'uncached_median_ms', 'exact_cache_ms')}) , flush=True)

    result = {'phase': phase, 'independent_validation_set': False,
              'source_sha256': source_sha256,
              'cases': rows,
              'limitations': [
                  'Development replays, not an independent accuracy set.',
                  'Widths 1280/1600/2560 and page translation are controlled transforms with the observed label geometry carried over; five native pages use ScreenReader.read end to end.',
                  'Only visible held-bar artwork is confirmed; absent pages, target recipient marks, and stack counters remain unsupported.',
                  'Runtime varies with CPU load. Cold includes template preparation; uncached median reuses template preparation but not image results; exact cache requires byte-identical image and geometry.',
              ]}
    if phase != 'baseline':
        baseline = json.loads((ROOT/'RELIC_RECOGNITION_022_BASELINE.json').read_text(encoding='utf8'))
        comparisons = []
        for before, after in zip(baseline['cases'], rows):
            assert before['case'] == after['case']
            new_item=(phase=='refined' and after['case'].endswith(':width=1600'))
            if new_item:
                assert {i['id'] for i in after['icons']}=={'rogue_6_relic_cargo_1','rogue_6_relic_fight_26','rogue_6_active_tool_5'}
                assert all(i['confirmed'] and i['score']>=.90 for i in after['icons'])
            elif phase=='refined':
                assert identity(before['icons'])==identity(after['icons']),after['case']
                for old in before['icons']:
                    new=next(i for i in after['icons'] if i['id']==old['id'])
                    assert new['score']>=old['score']-1e-7
                    assert np.allclose(new['center'],old['center'],atol=.002)
            else:
                assert before['semantic'] == after['semantic'], after['case']
                assert before['icons'] == after['icons'], after['case']
            comparisons.append({'case': after['case'], 'identical_output': before['icons']==after['icons'],
                                'identical_identity': not new_item,
                                'new_confirmed_item': 'rogue_6_active_tool_5' if new_item else None,
                                'uncached_speedup': before['uncached_median_ms']/after['uncached_median_ms']})
        # The top-level reader still returns the same owned identities and evidence.
        public_cases = []
        reader = ScreenReader(cache_enabled=False)
        for fixture in fixtures:
            image = cv2.imdecode(np.fromfile(samples/fixture['file'], dtype=np.uint8), 1)
            read = reader.read(image)
            current=json.loads(json.dumps(read['run']))
            expected=copy.deepcopy(fixture['run'])
            if phase=='refined':
                assert identity(current['relics']['icons'])==identity(expected['relics']['icons'])
                current['relics']['icons']=expected['relics']['icons']
            assert current == expected, fixture['file']
            assert read['page'] == fixture['page']
            public_cases.append({'sample': fixture['file'],
                                 'identical_run_output': json.loads(json.dumps(read['run']))==fixture['run'],
                                 'identical_except_refined_scores_and_centers': True,
                                 'screen_reader_ms': read['performance']['total_ms']})
        result.update(comparisons=comparisons, public_cases=public_cases)
    output = ROOT / f"RELIC_RECOGNITION_022_{phase.upper()}.json"
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf8')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('phase', choices=['baseline', 'optimized', 'refined'])
    run(parser.parse_args().phase)
