"""Append independent LOWLAND metal-ground landmarks to pinned PNG references.

Only the new source bitmap / grid / level identities are bound. Existing
calibrations and all failed observations are retained unchanged.
"""
import argparse
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
from rouge.battle_preview import battle_data, DATA
from rouge.map_projection import grid_digest

BASE = ROOT / '.cache/research/map-projection-049'
PRIOR = ROOT / '.cache/batch-049-before/rouge/data/battle-map-projections.json'
TARGET = DATA / 'battle-map-projections.json'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fit(entry):
    anchors = entry['anchors']
    assert not {(r, c) for r, c, *_ in anchors}.intersection(
        {(r, c) for r, c, *_ in entry['checks']}), 'Holdout coordinates entered the fit.'
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
    picture = picture.resize((picture.width * scale, picture.height * scale), Image.Resampling.NEAREST)
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


def build(write=False):
    inputs_path = BASE / 'calibration-input.json'
    inputs = json.loads(inputs_path.read_text(encoding='utf-8'))
    assert inputs['pixel_tolerance'] == 4
    old = json.loads(PRIOR.read_text(encoding='utf-8'))
    assert len(old['calibrations']) == 6 and len(old['stages']) == 12
    assert sum(len(c['checks']) for c in old['calibrations'].values()) == 34
    output = copy.deepcopy(old)
    source_records = []
    new_errors = []
    stages = battle_data()['stages']
    for entry in inputs['calibrations']:
        sid = entry['id']
        stage = stages[sid]
        matrix, checks = fit(entry)
        image = stage['image']
        raw_file = ROOT / '.cache/game-data/levels' / stage['level_source']['url'].split('/gamedata/levels/')[1]
        assert digest(raw_file) == stage['level_source']['sha256']
        raw = json.loads(raw_file.read_text(encoding='utf-8'))['mapData']
        assert raw['map'] == stage['map'] and raw['tiles'] == stage['tiles']
        for check in checks:
            assert isinstance(check['row'], int) and isinstance(check['col'], int)
            tile = stage['tiles'][stage['map'][check['row']][check['col']]]
            assert tile['tileKey'] == 'tile_floor' and tile['heightType'] == 'LOWLAND'
            new_errors.append(check['error_px'])
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
            assert grid_digest(target) == calibration['grid_sha256']
            assert target['image']['sha256'] == calibration['bitmap_sha256']
            image_file = DATA / target['image']['file']
            assert digest(image_file) == target['image']['sha256']
            assert image_file.stat().st_size == target['image']['bytes']
            assert hashlib.sha1(b'blob ' + str(image_file.stat().st_size).encode() + b'\0' + image_file.read_bytes()).hexdigest() == target['image']['source_blob_sha1']
            assert alias not in output['stages']
            output['stages'][alias] = {'calibration': sid,
                'level_sha256': target['level_source']['sha256'], 'image_file': target['image']['file']}
            source_records.append({'stage': alias, 'image': target['image'],
                'level': target['level_source'], 'grid_sha256': grid_digest(target),
                'cached_level_file': str(raw_file.relative_to(ROOT))})
        draw_landmarks(entry, stage, checks)
    assert all(output['calibrations'][k] == v for k, v in old['calibrations'].items())
    assert all(output['stages'][k] == v for k, v in old['stages'].items())
    output['version'] = '0.49.0'
    output['source']['added_landmarks_049'] = {
        'file': str(inputs_path.relative_to(ROOT)), 'sha256': digest(inputs_path),
        'evidence': '.cache/research/map-projection-049/evidence.json'}
    content = json.dumps(output, ensure_ascii=False, indent=2).encode('utf-8')
    if write:
        assert TARGET.read_bytes() in (PRIOR.read_bytes(), content), 'Unreviewed concurrent data change.'
        TARGET.write_bytes(content)
    receipt = {'version': '0.49.0', 'implemented': write,
        'new_calibrations': len(inputs['calibrations']), 'total_calibrations': len(output['calibrations']),
        'new_bound_stages': len(output['stages']) - len(old['stages']), 'total_bound_stages': len(output['stages']),
        'new_independent_checks': len(new_errors), 'max_new_independent_error_px': max(new_errors),
        'new_checks_by_stage': {sid: {'count': len(output['calibrations'][sid]['checks']),
            'max_error_px': max(c['error_px'] for c in output['calibrations'][sid]['checks'])}
            for sid in [e['id'] for e in inputs['calibrations']]},
        'tolerance_px': 4, 'prior_34_checks_and_6_calibrations_12_bindings_unchanged': True,
        'prior_file_sha256': digest(PRIOR), 'output_sha256': hashlib.sha256(content).hexdigest(),
        'inputs_sha256': digest(inputs_path), 'sources': source_records,
        'rejected_probes_retained': inputs['rejected_probes'],
        'scope': inputs['scope'], 'game_actions': 0, 'live_battle_captures': 0, 'chat_requests': 0,
        'remaining_stage_count': len(stages) - len(output['stages']),
        'remaining_distinct_bitmap_count': len({s['image']['sha256'] for s in stages.values()}) - len(output['calibrations'])}
    (BASE / 'evidence.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({k: receipt[k] for k in ('implemented', 'new_calibrations', 'new_bound_stages',
        'total_calibrations', 'total_bound_stages', 'new_independent_checks', 'max_new_independent_error_px',
        'remaining_stage_count', 'remaining_distinct_bitmap_count')}))
    return output, receipt


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    build(parser.parse_args().write)
