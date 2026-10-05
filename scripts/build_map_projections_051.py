"""Build a reviewed candidate only; never overwrite production map data.

Floor-frame corners enter each fit. Frozen center observations are independent
holdouts. The original 4-source-pixel gate and every previous calibration remain
unchanged. Rejected observations remain evidence instead of being tuned to pass.
"""
import copy
import hashlib
import json
import math
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from rouge.battle_preview import DATA, battle_data
from rouge.map_projection import grid_digest

BASE = ROOT / '.cache/research/map-projection-051'
PRIOR = BASE / 'prior-projections.json'
TARGET = BASE / 'battle-map-projections-candidate.json'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def fit(entry):
    anchors = entry['anchors']
    assert len(anchors) >= 4 and len(entry['checks']) >= 5
    assert not {(r, c) for r, c, *_ in anchors}.intersection(
        {(r, c) for r, c, *_ in entry['checks']}), 'Holdout coordinates entered the fit.'
    # Only anchor coordinates are supplied to findHomography. No error-driven
    # search, robust inlier exclusion, or center reuse is permitted.
    matrix, _ = cv2.findHomography(
        np.array([[c, r] for r, c, x, y in anchors], float),
        np.array([[x, y] for r, c, x, y in anchors], float), method=0)
    assert matrix is not None and np.isfinite(matrix).all()
    checks = []
    for r, c, x, y, cue in entry['checks']:
        vector = matrix @ np.array([c, r, 1.0])
        px, py = vector[:2] / vector[2]
        error = math.hypot(px - x, py - y)
        assert error <= 4, (entry['id'], cue, error)
        checks.append({'row': r, 'col': c, 'observed_pixel': [x, y],
                       'projected_pixel': [float(px), float(py)],
                       'error_px': error, 'cue': cue})
    return matrix, checks


def draw_landmarks(entry, stage, checks):
    scale = 4
    picture = Image.open(DATA / stage['image']['file']).convert('RGB')
    picture = picture.resize((picture.width * scale, picture.height * scale),
                             Image.Resampling.NEAREST)
    draw = ImageDraw.Draw(picture)
    for kind, points, color in (
        ('A', entry['anchors'], (255, 64, 220)),
        ('C', entry['checks'], (64, 255, 100)),
    ):
        for number, (r, c, x, y, *_rest) in enumerate(points, 1):
            xx, yy = x * scale, y * scale
            draw.line((xx - 7, yy, xx + 7, yy), fill=color, width=2)
            draw.line((xx, yy - 7, xx, yy + 7), fill=color, width=2)
            draw.text((xx + 8, yy - 8), f'{kind}{number} ({r:g},{c:g})', fill=color,
                      stroke_width=1, stroke_fill=(0, 0, 0))
    for check in checks:
        x, y = check['projected_pixel']
        draw.ellipse((x * scale - 3, y * scale - 3, x * scale + 3, y * scale + 3),
                     outline=(64, 220, 255), width=1)
    picture.save(BASE / (entry['id'] + '-numbered-ground-landmarks.png'))


def source_record(sid, stage):
    image = stage['image']
    image_file = DATA / image['file']
    image_bytes = image_file.read_bytes()
    assert digest(image_file) == image['sha256']
    assert len(image_bytes) == image['bytes']
    assert hashlib.sha1(b'blob ' + str(len(image_bytes)).encode() + b'\0' + image_bytes).hexdigest() == image['source_blob_sha1']
    with Image.open(image_file) as picture:
        assert picture.size == (image['width'], image['height'])
    level_file = ROOT / '.cache/game-data/levels' / stage['level_source']['url'].split('/gamedata/levels/')[1]
    assert digest(level_file) == stage['level_source']['sha256']
    assert level_file.stat().st_size == stage['level_source']['bytes']
    raw = read(level_file)['mapData']
    assert raw['map'] == stage['map'] and raw['tiles'] == stage['tiles']
    return {'stage': sid, 'image': image, 'level': stage['level_source'],
            'grid_sha256': grid_digest(stage),
            'cached_level_file': str(level_file.relative_to(ROOT))}


def build(write=False):
    inputs_path = BASE / 'calibration-input.json'
    inputs = read(inputs_path)
    assert inputs['pixel_tolerance'] == 4
    prior_receipt = read(BASE / 'prior-receipt.json')
    assert digest(PRIOR) == prior_receipt['sha256']
    old = read(PRIOR)
    assert len(old['calibrations']) == 8 and len(old['stages']) == 16
    assert sum(len(c['checks']) for c in old['calibrations'].values()) == 49
    for frozen in inputs['frozen_observations']:
        path = ROOT / frozen['file']
        assert digest(path) == frozen['sha256']
    output = copy.deepcopy(old)
    records = []
    new_errors = []
    stages = battle_data()['stages']
    for entry in inputs['calibrations']:
        sid = entry['id']
        stage = stages[sid]
        initial = read(BASE / (sid + '-initial-fit.json'))
        assert initial['input'] == entry and initial['accepted'] is True
        matrix, checks = fit(entry)
        assert matrix.ravel().tolist() == initial['matrix']
        assert checks == initial['checks']
        for check in checks:
            assert isinstance(check['row'], int) and isinstance(check['col'], int)
            tile = stage['tiles'][stage['map'][check['row']][check['col']]]
            assert (tile['tileKey'], tile['heightType']) == ('tile_floor', 'LOWLAND')
            new_errors.append(check['error_px'])
        image = stage['image']
        assert sid not in output['calibrations']
        output['calibrations'][sid] = {
            'anchors': entry['anchors'], 'checks': checks,
            'matrix': matrix.ravel().tolist(), 'inverse': np.linalg.inv(matrix).ravel().tolist(),
            'tolerance_px': 4, 'bitmap_sha256': image['sha256'],
            'grid_sha256': grid_digest(stage), 'width': image['width'], 'height': image['height'],
            'rows': len(stage['map']), 'cols': len(stage['map'][0]), 'base_stage_id': sid,
            'landmarks_sha256': digest(inputs_path),
            'scope': inputs['scope'], 'grid_correspondence': entry['grid_correspondence'],
        }
        calibration = output['calibrations'][sid]
        for alias in [sid, *entry['aliases']]:
            target = stages[alias]
            record = source_record(alias, target)
            assert record['grid_sha256'] == calibration['grid_sha256']
            assert target['image']['sha256'] == calibration['bitmap_sha256']
            assert alias not in output['stages']
            output['stages'][alias] = {'calibration': sid,
                'level_sha256': target['level_source']['sha256'], 'image_file': target['image']['file']}
            records.append(record)
        if write:
            draw_landmarks(entry, stage, checks)
    rejected = []
    for probe in inputs['rejected_probes']:
        path = ROOT / probe['file']
        assert digest(path) == probe['sha256']
        source = read(path)
        assert source['accepted'] is False
        assert source['pixel_tolerance'] == 4
        maximum = max(c['error_px'] for c in source['checks'])
        assert maximum > 4 and maximum == probe['max_probe_error_px']
        assert source['input']['id'] not in output['calibrations']
        rejected.append({**probe, 'source': source_record(source['input']['id'], stages[source['input']['id']])})
    assert all(output['calibrations'][k] == v for k, v in old['calibrations'].items())
    assert all(output['stages'][k] == v for k, v in old['stages'].items())
    output['version'] = '0.51.0'
    output['source']['added_landmarks_051'] = {
        'file': str(inputs_path.relative_to(ROOT)), 'sha256': digest(inputs_path),
        'evidence': '.cache/research/map-projection-051/evidence.json'}
    content = json.dumps(output, ensure_ascii=False, indent=2).encode('utf-8')
    receipt = {'version': '0.51.0', 'implemented': False, 'candidate_written': write,
        'candidate_file': str(TARGET.relative_to(ROOT)),
        'new_calibrations': len(inputs['calibrations']), 'total_calibrations': len(output['calibrations']),
        'new_bound_stages': len(output['stages']) - len(old['stages']), 'total_bound_stages': len(output['stages']),
        'new_independent_checks': len(new_errors), 'max_new_independent_error_px': max(new_errors),
        'new_checks_by_stage': {sid: {'count': len(output['calibrations'][sid]['checks']),
            'max_error_px': max(c['error_px'] for c in output['calibrations'][sid]['checks'])}
            for sid in [e['id'] for e in inputs['calibrations']]},
        'tolerance_px': 4, 'prior_49_checks_and_8_calibrations_16_bindings_unchanged': True,
        'prior_file_sha256': digest(PRIOR), 'output_sha256': hashlib.sha256(content).hexdigest(),
        'inputs_sha256': digest(inputs_path), 'sources': records,
        'rejected_probes_retained': rejected, 'preexisting_failed_probes_unchanged': True,
        'scope': inputs['scope'], 'game_actions': 0, 'live_battle_captures': 0, 'chat_requests': 0,
        'remaining_stage_count_if_integrated': len(stages) - len(output['stages']),
        'remaining_distinct_bitmap_count_if_integrated': len({s['image']['sha256'] for s in stages.values()}) - len(output['calibrations'])}
    if write:
        TARGET.write_bytes(content)
        (BASE / 'evidence.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2), encoding='utf-8')
    return output, receipt


if __name__ == '__main__':
    _, receipt = build(write=True)
    print(json.dumps({k: receipt[k] for k in ('implemented', 'candidate_written', 'new_calibrations',
        'new_bound_stages', 'total_calibrations', 'total_bound_stages', 'new_independent_checks',
        'max_new_independent_error_px', 'remaining_stage_count_if_integrated',
        'remaining_distinct_bitmap_count_if_integrated')}))
