"""Append reviewed ground observations, rejecting failed fits without tuning them.

Original public source bytes, seam anchors and holdout centers are hash-bound.
The existing four-source-pixel gate is unchanged. No observations enter the fit
after its result is inspected, and rejected observations remain excluded.
"""
import copy
import hashlib
import json
import math
import sys
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from rouge.battle_preview import battle_data, DATA
from rouge.map_projection import grid_digest

BASE = ROOT / 'research/p3-map-ground-current'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def fit(entry):
    anchors = entry['anchors']
    checks = entry['checks']
    if len(anchors) < 4 or len(checks) < 5:
        raise ValueError('Need independent seam anchors and at least five holdouts.')
    if {(r, c) for r, c, *_ in anchors} & {(r, c) for r, c, *_ in checks}:
        raise ValueError('A holdout coordinate entered the fit.')
    matrix, _ = cv2.findHomography(
        np.array([[c, r] for r, c, x, y in anchors], float),
        np.array([[x, y] for r, c, x, y in anchors], float), method=0)
    if matrix is None or not np.isfinite(matrix).all():
        raise ValueError('Ground correspondence is not a finite homography.')
    observed = []
    for r, c, x, y, cue in checks:
        vector = matrix @ np.array([c, r, 1.0])
        point = vector[:2] / vector[2]
        observed.append({'row': r, 'col': c, 'observed_pixel': [x, y],
            'projected_pixel': point.tolist(), 'error_px': math.dist(point, [x, y]),
            'cue': cue})
    return {'id': entry['id'], 'matrix': matrix.ravel().tolist(),
        'checks': observed, 'accepted': max(c['error_px'] for c in observed) <= 4}


def source_check(sid, receipt):
    stage = battle_data()['stages'][sid]
    source = receipt['sources'][sid]
    if stage['image'] != source['image'] or stage['level_source'] != source['level_source']:
        raise ValueError('Bound bitmap or original level metadata changed.')
    image = DATA / stage['image']['file']
    if digest(image) != stage['image']['sha256'] or image.stat().st_size != stage['image']['bytes']:
        raise ValueError('The original bitmap changed.')
    raw = image.read_bytes()
    if hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() != stage['image']['source_blob_sha1']:
        raise ValueError('The bitmap does not match its pinned resource blob.')
    level = ROOT / source['level_local_file']
    if digest(level) != stage['level_source']['sha256'] or level.stat().st_size != stage['level_source']['bytes']:
        raise ValueError('The original level bytes changed.')
    raw_map = read(level)['mapData']
    if raw_map['map'] != stage['map'] or raw_map['tiles'] != stage['tiles']:
        raise ValueError('The rendered grid is not the pinned original grid.')
    return stage


def build(write=False):
    receipt = read(BASE / 'source-receipt.json')
    if receipt['pixel_tolerance'] != 4:
        raise ValueError('The source-pixel gate cannot be relaxed.')
    prior_path = BASE / 'prior-projections.json'
    if digest(prior_path) != receipt['prior_sha256']:
        raise ValueError('The frozen prior projection data changed.')
    prior = read(prior_path)
    if len(prior['calibrations']) != 10 or len(prior['stages']) != 20:
        raise ValueError('Review the prior calibration scope before rebasing.')
    for name, sha in receipt['frozen_sha256'].items():
        if digest(BASE / name) != sha:
            raise ValueError('A pre-fit observation or initial fit changed: ' + name)
    output = copy.deepcopy(prior)
    accepted, rejected = [], []
    for number in [*receipt['included_observations'], *receipt['rejected_observations']]:
        entry = read(BASE / f'frozen-observation-{number}.json')['calibrations'][0]
        original = read(BASE / f'initial-fit-{number}.json')[0]
        result = fit(entry)
        if result != original:
            raise ValueError('The original observation cannot reproduce its first fit.')
        stage = source_check(entry['id'], receipt)
        expected = number in receipt['included_observations']
        if result['accepted'] is not expected:
            raise ValueError('A failed observation cannot be promoted to a production binding.')
        if not expected:
            rejected.append({'id': entry['id'], 'observation': number,
                'max_error_px': max(c['error_px'] for c in result['checks']),
                'accepted_for_runtime': False})
            continue
        for point in result['checks']:
            tile = stage['tiles'][stage['map'][point['row']][point['col']]]
            if tile['heightType'] != 'LOWLAND' or tile['tileKey'] not in ('tile_floor', 'tile_road'):
                raise ValueError('A center observation cannot certify an elevated or unspecified surface.')
        matrix = np.array(result['matrix']).reshape(3, 3)
        cid = entry['id']
        if cid in output['calibrations']:
            raise ValueError('Existing production calibration cannot be overwritten.')
        image = stage['image']
        output['calibrations'][cid] = {'anchors': copy.deepcopy(entry['anchors']),
            'checks': result['checks'], 'matrix': result['matrix'],
            'inverse': np.linalg.inv(matrix).ravel().tolist(), 'tolerance_px': 4,
            'bitmap_sha256': image['sha256'], 'grid_sha256': grid_digest(stage),
            'width': image['width'], 'height': image['height'],
            'rows': len(stage['map']), 'cols': len(stage['map'][0]),
            'base_stage_id': cid, 'landmarks_sha256': receipt['frozen_sha256'][f'frozen-observation-{number}.json'],
            'scope': receipt['scope'], 'grid_correspondence': entry['grid_correspondence'],
            'independent_coverage': receipt['calibration_coverage'][cid]}
        for sid in [cid, *entry['aliases']]:
            alias = battle_data()['stages'][sid]
            if (grid_digest(alias) != grid_digest(stage) or alias['image']['sha256'] != image['sha256']
                    or alias['level_source'] != stage['level_source']):
                raise ValueError('A named alias alone cannot inherit a bitmap transform.')
            if sid in output['stages']:
                raise ValueError('An existing production stage binding cannot be overwritten.')
            output['stages'][sid] = {'calibration': cid,
                'level_sha256': alias['level_source']['sha256'], 'image_file': alias['image']['file']}
        accepted.append({'id': cid, 'observation': number, 'aliases': entry['aliases'],
            'checks': len(result['checks']), 'max_error_px': max(c['error_px'] for c in result['checks'])})
    output['version'] = '0.51.0+wood-ground-reference'
    output['source']['added_wood_road_ground'] = {
        'file': 'research/p3-map-ground-current/source-receipt.json',
        'sha256': digest(BASE / 'source-receipt.json')}
    content = json.dumps(output, ensure_ascii=False, indent=2).encode('utf-8')
    result = {'scope': receipt['scope'], 'accepted': accepted, 'rejected': rejected,
        'total_calibrations': len(output['calibrations']), 'total_bound_stages': len(output['stages']),
        'new_independent_checks': sum(row['checks'] for row in accepted),
        'pixel_tolerance': 4, 'prior_unchanged': True,
        'remaining_unbound_stages': len(battle_data()['stages']) - len(output['stages']),
        'remaining_distinct_bitmaps': len({s['image']['sha256'] for s in battle_data()['stages'].values()}) - len(output['calibrations']),
        'output_sha256': hashlib.sha256(content).hexdigest(),
        'game_actions': 0, 'chat_requests': 0, 'live_samples': 0}
    if write:
        (DATA / 'battle-map-projections.json').write_bytes(content)
        (BASE / 'build-receipt.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    return output, result


if __name__ == '__main__':
    print(json.dumps(build(write=True)[1], ensure_ascii=False))
