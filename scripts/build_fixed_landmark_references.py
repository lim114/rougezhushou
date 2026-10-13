"""Build exact, double-read center references without fitting or extrapolation."""
import argparse
import copy
import hashlib
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from rouge.battle_preview import battle_data, DATA
from rouge.map_projection import grid_digest
from scripts.extend_fixed_map_projections import fit
from scripts.map_fit_replay import verify_fit_replay

BASE = ROOT / 'research/p3-direct-ground-current'
OUTPUT = DATA / 'fixed-landmark-references.json'


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build(write=False):
    source = read(BASE / 'source-receipt.json')
    request = read(BASE / 'independent-reading-request.json')
    author = read(BASE / 'author-direct-readings-frozen.json')
    reader = read(BASE / 'independent-reader-frozen.json')
    if sha(BASE / 'author-direct-readings-frozen.json') != source['author_reading_sha256']:
        raise ValueError('Frozen author observations changed.')
    if sha(BASE / 'independent-reader-frozen.json') != source['independent_reader_sha256']:
        raise ValueError('Frozen independent observations changed.')
    if reader['author_pixel_values_or_fits_read'] is not False:
        raise ValueError('The second reader did not independently observe the original.')
    if source['original_tolerance_retained_px'] != 4 or source['source_pixel_adjustments_after_independent_reading'] != 0:
        raise ValueError('Agreement must not be obtained by adjusting points or tolerance.')
    for name, digest in source['frozen_sha256'].items():
        if sha(BASE / name) != digest:
            raise ValueError('A frozen public source changed: ' + name)
    failed = []
    for number in (1, 2, 3):
        frozen = read(BASE / f'frozen-observation-{number}.json')['calibrations'][0]
        first = read(BASE / f'initial-fit-{number}.json')[0]
        verify_fit_replay(fit(frozen), first)
        if first['accepted']:
            raise ValueError('A rejected original plane fit changed or was promoted.')
        failed.append({'id': first['id'], 'observation': number,
            'max_error_px': max(c['error_px'] for c in first['checks']), 'accepted_for_runtime': False})
    output = {'source': {'scope': 'Only agreed observed LOWLAND tile_floor centers; no plane, extrapolation, inverse, or path.',
        'agreement_tolerance_px': 4, 'absolute_position_accuracy_verified': False,
        'game_commit': battle_data()['source']['game_commit'],
        'resource_commit': battle_data()['source']['resource_commit']}, 'references': {}, 'stages': {}}
    agreements = []
    for sid, expected in request.items():
        stage = battle_data()['stages'][sid]; image = stage['image']
        path = DATA / image['file']; raw = path.read_bytes()
        if sha(path) != image['sha256'] or len(raw) != image['bytes']:
            raise ValueError('The pinned original bitmap changed.')
        if hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() != image['source_blob_sha1']:
            raise ValueError('The original resource blob changed.')
        if expected['source_image'] != image or expected['source_level'] != stage['level_source']:
            raise ValueError('The request source identity changed.')
        level = BASE / ('level_rogue6_' + sid.removeprefix('ro6_n_').replace('_', '-') + '.json')
        if sha(level) != stage['level_source']['sha256'] or level.stat().st_size != stage['level_source']['bytes']:
            raise ValueError('The full pinned level bytes changed.')
        primary = read(level)['mapData']
        if primary['map'] != stage['map'] or primary['tiles'] != stage['tiles']:
            raise ValueError('The logical cells differ from the original level grid.')
        if reader['maps'][sid]['source_sha256'] != image['sha256']:
            raise ValueError('The reader did not read this exact source image.')
        peer = {(p['row'], p['col']): p for p in reader['maps'][sid]['points']}
        expected_cells = [tuple(v) for v in expected['requested_display_zero_based_cells']]
        if len(peer) != len(expected_cells) or set(peer) != set(expected_cells):
            raise ValueError('The independently read set changed.')
        if [(p['row'], p['col']) for p in author[sid]] != expected_cells:
            raise ValueError('The frozen author set changed.')
        accepted = []
        for point in author[sid]:
            row, col = point['row'], point['col']; pixel = point['pixel']
            observation = read(BASE / f"frozen-observation-{point['source_observation']}.json")['calibrations'][0]
            if [row, col, *pixel] not in [p[:4] for p in observation['anchors'] + observation['checks']]:
                raise ValueError('The direct observation was not frozen before the peer read.')
            tile = stage['tiles'][stage['map'][row][col]]
            if tile['tileKey'] != 'tile_floor' or tile['heightType'] != 'LOWLAND':
                raise ValueError('An unverified height or non-floor was added.')
            independent = peer[(row, col)]['pixel']; distance = math.dist(pixel, independent)
            result = {'reference': sid, 'row': row, 'col': col, 'observed_pixel': copy.deepcopy(pixel),
                'independent_pixel': copy.deepcopy(independent), 'agreement_px': distance,
                'accepted_for_runtime': distance <= 4}
            agreements.append(result)
            if distance <= 4:
                accepted.append({k: copy.deepcopy(v) for k, v in result.items() if k not in ('reference', 'accepted_for_runtime')})
        if not accepted:
            continue
        output['references'][sid] = {'rows': len(stage['map']), 'cols': len(stage['map'][0]),
            'width': image['width'], 'height': image['height'], 'bitmap_sha256': image['sha256'],
            'grid_sha256': grid_digest(stage), 'agreement_tolerance_px': 4,
            'scope': 'Only these independently concordant nominal floor centers. Absolute bitmap/actual combat accuracy unverified.',
            'points': accepted}
        for alias in (sid, sid.replace('ro6_n_', 'ro6_e_', 1)):
            bound = battle_data()['stages'][alias]
            alias_image = bound['image']; alias_path = DATA / alias_image['file']; alias_raw = alias_path.read_bytes()
            if any(alias_image[k] != image[k] for k in ('sha256', 'source_blob_sha1', 'bytes', 'width', 'height')):
                raise ValueError('An alias does not have the same pinned bitmap identity.')
            if sha(alias_path) != alias_image['sha256'] or len(alias_raw) != alias_image['bytes']:
                raise ValueError('An alias original file differs from its bound bitmap.')
            if hashlib.sha1(b'blob ' + str(len(alias_raw)).encode() + b'\0' + alias_raw).hexdigest() != alias_image['source_blob_sha1']:
                raise ValueError('An alias resource blob changed.')
            if bound['level_source'] != stage['level_source'] or grid_digest(bound) != grid_digest(stage):
                raise ValueError('An alias does not have the same pinned original level and grid.')
            output['stages'][alias] = {'reference': sid, 'image_file': bound['image']['file'],
                'level_sha256': bound['level_source']['sha256']}
    prior = read(BASE / 'prior-regular-projections.json')
    regular = read(DATA / 'battle-map-projections.json')
    for group in ('calibrations', 'stages'):
        for key, value in prior[group].items():
            if regular[group].get(key) != value:
                raise ValueError('An existing regular plane reference changed.')
    receipt = {'status': 'PASS_PARTIAL_DIRECT_CENTER_AGREEMENT_ONLY', 'requested_points': len(agreements),
        'accepted_points': sum(p['accepted_for_runtime'] for p in agreements),
        'rejected_points': sum(not p['accepted_for_runtime'] for p in agreements),
        'partial_images': len(output['references']), 'partial_stage_bindings': len(output['stages']),
        'agreement_comparisons': agreements, 'rejected_plane_fits': failed,
        'regular_calibrations_at_baseline': len(prior['calibrations']), 'regular_stage_bindings_at_baseline': len(prior['stages']),
        'complete_calibration_added': 0, 'remaining_regular_unbound_stages': 81,
        'remaining_regular_distinct_bitmaps': 59, 'absolute_position_accuracy_verified': False,
        'extrapolation': False, 'inverse_cell_assignment': False, 'bitmap_checkpoint_connections': False,
        'game_actions': 0, 'chat_requests': 0, 'live_samples': 0,
        'output_sha256': hashlib.sha256(json.dumps(output, ensure_ascii=False, indent=2).encode('utf-8')).hexdigest()}
    if write:
        OUTPUT.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding='utf-8', newline='\n')
        (BASE / 'verification.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    return output, receipt


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--write', action='store_true')
    args = parser.parse_args(); _, receipt = build(write=args.write)
    print(json.dumps({k: v for k, v in receipt.items() if k not in ('agreement_comparisons', 'rejected_plane_fits')}, ensure_ascii=False))
