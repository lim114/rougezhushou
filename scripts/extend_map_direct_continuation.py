"""Build a candidate from frozen direct observations; never mutate runtime data."""
import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
import struct
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from rouge.battle_preview import DATA, battle_data
from rouge.map_projection import grid_digest

BASE = ROOT / 'research/p3-map-direct-continuation'


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pair(value):
    return (isinstance(value, list) and len(value) == 2 and
            all(type(v) in (int, float) and math.isfinite(v) for v in value))


def bitmap(image):
    raw = (DATA / image['file']).read_bytes()
    if hashlib.sha256(raw).hexdigest() != image['sha256'] or len(raw) != image['bytes']:
        raise ValueError('Original bitmap bytes changed.')
    if hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() != image['source_blob_sha1']:
        raise ValueError('Original resource blob changed.')
    if raw[:8] != b'\x89PNG\r\n\x1a\n' or raw[12:16] != b'IHDR':
        raise ValueError('The declared source is not an original PNG.')
    if struct.unpack('>II', raw[16:24]) != (image['width'], image['height']):
        raise ValueError('Original bitmap dimensions changed.')


def build():
    """Return candidate plus full agreement receipt, without writing either."""
    source = read(BASE / 'source-receipt.json')
    if source.get('independent_reader_pending') is not False:
        raise ValueError('Independent original-bitmap reading is still pending.')
    if (source['agreement_tolerance_px'] != 4 or
            source['source_pixel_adjustments_after_independent_reading'] != 0):
        raise ValueError('Frozen centers and their original gate must not be tuned.')
    for name, digest in source['frozen_sha256'].items():
        if sha(BASE / name) != digest:
            raise ValueError('Frozen original evidence changed: ' + name)
    request = read(BASE / 'independent-reading-request.json')
    author = read(BASE / 'author-readings-frozen.json')
    peer = read(BASE / 'independent-reader-frozen.json')
    if (author['independent_peer_values_or_fits_read'] is not False or
            peer['author_pixel_values_or_fits_read'] is not False):
        raise ValueError('The original readings were not independent.')
    if set(request) != set(author['maps']) or set(request) != set(peer['maps']):
        raise ValueError('Requested original-map identities disagree.')
    prior = read(BASE / 'prior-landmark-references.json')
    output = copy.deepcopy(prior)
    regular_prior = read(BASE / 'prior-regular-projections.json')
    regular = read(DATA / 'battle-map-projections.json')
    for group in ('calibrations', 'stages'):
        for key, value in regular_prior[group].items():
            if regular[group].get(key) != value:
                raise ValueError('A prior regular plane reference changed.')
    comparisons, excluded_aliases = [], []
    for sid, expected in request.items():
        stage = battle_data()['stages'][sid]
        image = stage['image']
        bitmap(image)
        if expected['source_image'] != image or expected['source_level'] != stage['level_source']:
            raise ValueError('The independent request source changed.')
        for observation in (author['maps'][sid], peer['maps'][sid]):
            if observation['source_sha256'] != image['sha256']:
                raise ValueError('A reader observed a different original bitmap.')
        level = BASE / source['sources'][sid]['original_level_file']
        if sha(level) != stage['level_source']['sha256'] or level.stat().st_size != stage['level_source']['bytes']:
            raise ValueError('Original complete level bytes changed.')
        original = read(level)['mapData']
        if original['map'] != stage['map'] or original['tiles'] != stage['tiles']:
            raise ValueError('Logical grid no longer matches original mapData.')
        cells = [tuple(cell) for cell in expected['requested_display_zero_based_cells']]
        first = author['maps'][sid]['points']
        second = peer['maps'][sid]['points']
        if [(row['row'], row['col']) for row in first] != cells:
            raise ValueError('Frozen author requested cells changed.')
        by_cell = {(row['row'], row['col']): row for row in second}
        if len(second) != len(cells) or set(by_cell) != set(cells):
            raise ValueError('Independent requested cells are missing or duplicated.')
        points = []
        for observed in first:
            row, col = observed['row'], observed['col']
            tile = stage['tiles'][stage['map'][row][col]]
            if tile['tileKey'] != 'tile_floor' or tile['heightType'] != 'LOWLAND':
                raise ValueError('A center is outside the declared lowland floor scope.')
            one, two = observed['pixel'], by_cell[(row, col)]['pixel']
            if any(value is not None and not pair(value) for value in (one, two)):
                raise ValueError('Unknown centers must be null; known pixels must be finite pairs.')
            known = pair(one) and pair(two)
            if known and not all(0 <= p[0] < image['width'] and 0 <= p[1] < image['height'] for p in (one, two)):
                raise ValueError('An observed pixel is outside its exact source image.')
            distance = math.dist(one, two) if known else None
            accepted = known and distance <= 4
            result = {'reference': sid, 'row': row, 'col': col,
                      'observed_pixel': copy.deepcopy(one), 'independent_pixel': copy.deepcopy(two),
                      'agreement_px': distance, 'accepted_for_runtime': accepted,
                      'reason': ('independent approximate observations agree' if accepted else
                                 'unknown direct observation' if not known else
                                 'independent observations disagree beyond4px')}
            comparisons.append(result)
            if accepted:
                points.append({k: copy.deepcopy(v) for k, v in result.items()
                               if k not in ('reference', 'accepted_for_runtime', 'reason')})
        if not points:
            continue
        if sid in output['references']:
            raise ValueError('This original bitmap reference was already delivered.')
        output['references'][sid] = {
            'rows': len(stage['map']), 'cols': len(stage['map'][0]),
            'width': image['width'], 'height': image['height'], 'bitmap_sha256': image['sha256'],
            'grid_sha256': grid_digest(stage), 'agreement_tolerance_px': 4,
            'scope': 'Only independently concordant nominal lowland floor centers. Absolute bitmap/actual combat accuracy unverified.',
            'points': points}
        for alias in (sid, sid.replace('ro6_n_', 'ro6_e_', 1)):
            bound = battle_data()['stages'][alias]
            other = bound['image']
            bitmap(other)
            if (any(other[k] != image[k] for k in ('sha256', 'source_blob_sha1', 'bytes', 'width', 'height')) or
                    bound['level_source'] != stage['level_source'] or grid_digest(bound) != grid_digest(stage)):
                excluded_aliases.append({'id': alias, 'accepted_for_runtime': False,
                                        'reason': 'different exact bitmap, original level, or logical grid'})
                continue
            if alias in output['stages']:
                raise ValueError('This stage binding was already delivered.')
            output['stages'][alias] = {'reference': sid, 'image_file': other['file'],
                                      'level_sha256': bound['level_source']['sha256']}
    output['source'].setdefault('additional_source_packs', []).append('research/p3-map-direct-continuation')
    receipt = {'status': 'PARTIAL_DIRECT_CENTER_CANDIDATE',
               'new_requested_points': len(comparisons),
               'new_accepted_points': sum(row['accepted_for_runtime'] for row in comparisons),
               'new_rejected_or_unknown_points': sum(not row['accepted_for_runtime'] for row in comparisons),
               'new_partial_images': len(output['references']) - len(prior['references']),
               'new_partial_stage_bindings': len(output['stages']) - len(prior['stages']),
               'new_agreement_comparisons': comparisons, 'excluded_aliases': excluded_aliases,
               'total_partial_points': sum(len(row['points']) for row in output['references'].values()),
               'total_partial_images': len(output['references']), 'total_partial_stage_bindings': len(output['stages']),
               'regular_images_preserved': len(regular_prior['calibrations']),
               'regular_stage_bindings_preserved': len(regular_prior['stages']),
               'complete_calibration_added': 0, 'absolute_position_accuracy_verified': False,
               'extrapolation': False, 'inverse_cell_assignment': False, 'checkpoint_connections': False,
               'game_actions': 0, 'chat_requests': 0, 'live_samples': 0,
               'output_sha256': hashlib.sha256(json.dumps(output, ensure_ascii=False, indent=2).encode()).hexdigest()}
    return output, receipt


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path)
    args = parser.parse_args()
    candidate, receipt = build()
    if args.output_dir:
        directory = args.output_dir.resolve()
        if directory == DATA.resolve() or directory.is_relative_to(DATA.resolve()):
            raise ValueError('Candidate output must not mutate runtime data.')
        directory.mkdir(parents=True, exist_ok=False)
        for name, value in [('candidate.json', candidate), ('verification.json', receipt)]:
            (directory / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in receipt.items() if k != 'new_agreement_comparisons'}, ensure_ascii=False))
