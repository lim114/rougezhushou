"""Frozen double-read highland top candidate, never runtime data or ground fit."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from rouge.battle_preview import DATA, battle_data
from rouge.map_projection import grid_digest

BASE = ROOT / 'research/p3-highland-top-current'
OUTPUT = ROOT / 'rouge/data/highland-top-references.json'


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bitmap(image):
    raw = (DATA / image['file']).read_bytes()
    if (hashlib.sha256(raw).hexdigest() != image['sha256'] or len(raw) != image['bytes'] or
            hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() != image['source_blob_sha1']):
        raise ValueError('Original bitmap identity changed.')


def pair(value):
    return isinstance(value, list) and len(value) == 2 and all(type(v) in (int, float) and math.isfinite(v) for v in value)


def build():
    source = read(BASE / 'source-receipt.json')
    if source.get('independent_reader_pending') is not False:
        raise ValueError('Independent highland top reading remains pending.')
    if source['agreement_tolerance_px'] != 4 or source['source_pixel_adjustments_after_independent_reading'] != 0:
        raise ValueError('The original centers and4px agreement gate cannot be tuned.')
    for name, digest in source['frozen_sha256'].items():
        if sha(BASE / name) != digest:
            raise ValueError('Frozen source or direct reading changed: ' + name)
    request = read(BASE / 'independent-reading-request.json')
    author = read(BASE / 'author-top-readings-frozen.json')
    reader = read(BASE / 'independent-reader-frozen.json')
    if author['independent_peer_values_or_fits_read'] is not False or reader['author_pixel_values_or_fits_read'] is not False:
        raise ValueError('Top-surface readings were not independent.')
    if set(request) != set(author['maps']) or set(request) != set(reader['maps']):
        raise ValueError('Direct top-surface source identities disagree.')
    output = {'format_version': 1, 'reference_kind': 'highland_nominal_top_center',
              'absolute_position_accuracy_verified': False,
              'source': {'game_commit': source['game_commit'], 'resource_commit': source['resource_commit'],
                         'source_pack': 'research/p3-highland-top-current',
                         'scope': 'Separately read individual tile_wall/HIGHLAND nominal top centers only; no ground, footpoints, spawn positions, projection or inverse.'},
              'references': {}, 'stages': {}}
    comparisons, excluded_aliases = [], []
    for sid, expected in request.items():
        stage = battle_data()['stages'][sid]; image = stage['image']; bitmap(image)
        if expected['source_image'] != image or expected['source_level'] != stage['level_source']:
            raise ValueError('Requested exact original identity changed.')
        level = BASE / source['sources'][sid]['original_level_file']
        if sha(level) != stage['level_source']['sha256'] or level.stat().st_size != stage['level_source']['bytes']:
            raise ValueError('Complete original level bytes changed.')
        original = read(level)['mapData']
        if original['map'] != stage['map'] or original['tiles'] != stage['tiles']:
            raise ValueError('Original highland grid changed.')
        first, second = author['maps'][sid], reader['maps'][sid]
        if first['source_sha256'] != image['sha256'] or second['source_sha256'] != image['sha256']:
            raise ValueError('A reader observed a different original bitmap.')
        cells = [tuple(cell) for cell in expected['requested_display_zero_based_cells']]
        if [(row['row'], row['col']) for row in first['points']] != cells:
            raise ValueError('Author requested top cells changed.')
        peer = {(row['row'], row['col']): row for row in second['points']}
        if len(second['points']) != len(cells) or set(peer) != set(cells):
            raise ValueError('Independent top cells are missing or duplicated.')
        points = []
        for row in first['points']:
            r, c, one = row['row'], row['col'], row['pixel']; two = peer[(r, c)]['pixel']
            tile = stage['tiles'][stage['map'][r][c]]
            if tile['tileKey'] != 'tile_wall' or tile['heightType'] != 'HIGHLAND':
                raise ValueError('Top reading is not the declared tile_wall/HIGHLAND.')
            if any(pixel is not None and not pair(pixel) for pixel in (one, two)):
                raise ValueError('Known top pixels require finite pairs; unknown is null.')
            known = pair(one) and pair(two)
            if known and not all(0 <= p[0] < image['width'] and 0 <= p[1] < image['height'] for p in (one, two)):
                raise ValueError('A direct top pixel lies outside its bitmap.')
            distance = math.dist(one, two) if known else None; accepted = known and distance <= 4
            result = {'reference': sid, 'row': r, 'col': c, 'observed_pixel': one, 'independent_pixel': two,
                      'agreement_px': distance, 'accepted_for_runtime': accepted,
                      'reason': 'independent nominal top readings agree' if accepted else
                                'individual top surface directly unreadable' if not known else
                                'independent nominal top readings disagree beyond4px'}
            comparisons.append(result)
            if accepted:
                points.append({key: value for key, value in result.items() if key not in ('reference', 'accepted_for_runtime', 'reason')})
        if not points:
            continue
        output['references'][sid] = {'rows': len(stage['map']), 'cols': len(stage['map'][0]),
            'width': image['width'], 'height': image['height'], 'bitmap_sha256': image['sha256'],
            'grid_sha256': grid_digest(stage), 'surface_kind': 'highland_nominal_top_center',
            'tile_kind': 'tile_wall', 'height_type': 'HIGHLAND', 'agreement_tolerance_px': 4, 'points': points}
        for alias in (sid, sid.replace('ro6_n_', 'ro6_e_', 1)):
            bound = battle_data()['stages'][alias]; other = bound['image']; bitmap(other)
            if (any(image[key] != other[key] for key in ('sha256', 'source_blob_sha1', 'bytes', 'width', 'height')) or
                    stage['level_source'] != bound['level_source'] or grid_digest(stage) != grid_digest(bound)):
                excluded_aliases.append({'id': alias, 'reason': 'Different exact original bitmap/level/grid; independent top readings absent.'}); continue
            output['stages'][alias] = {'reference': sid, 'image_file': other['file'], 'level_sha256': bound['level_source']['sha256']}
    receipt = {'status': 'SEPARATE_PARTIAL_HIGHLAND_TOP_CANDIDATE', 'requested_points': len(comparisons),
               'accepted_unique_image_top_cells': sum(row['accepted_for_runtime'] for row in comparisons),
               'rejected_or_unknown_points': sum(not row['accepted_for_runtime'] for row in comparisons),
               'partial_images': len(output['references']), 'stage_bindings': len(output['stages']),
               'agreement_comparisons': comparisons, 'excluded_aliases': excluded_aliases,
               'complete_map_calibration_added': 0, 'absolute_position_accuracy_verified': False,
               'lowland_references_modified': False, 'ground_projection': False, 'inverse': False,
               'footpoints': False, 'spawn_positions': False, 'checkpoint_connections': False,
               'game_actions': 0, 'chat_requests': 0}
    return output, receipt


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path)
    parser.add_argument('--write', action='store_true', help='Explicitly write only highland runtime references and this source receipt')
    args = parser.parse_args(); candidate, receipt = build()
    if args.write:
        OUTPUT.write_text(json.dumps(candidate, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        (BASE / 'verification.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    if args.output_dir:
        path = args.output_dir.resolve()
        if path == DATA.resolve() or path.is_relative_to(DATA.resolve()):
            raise ValueError('Future candidate cannot mutate runtime data.')
        path.mkdir(parents=True, exist_ok=False)
        for name, value in [('candidate.json', candidate), ('verification.json', receipt)]:
            (path / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({key: value for key, value in receipt.items() if key != 'agreement_comparisons'}, ensure_ascii=False))
