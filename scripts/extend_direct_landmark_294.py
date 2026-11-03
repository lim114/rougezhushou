"""Append only independently concordant fixed-image cell centers.

Source reconstruction is read-only. Only --output-dir writes a new candidate
directory; this tool never installs runtime data. It uses only the standard
library, the frozen originals, and public stage/image data. No fitting,
interpolation, inverse mapping, gameplay or actual enemy positions are inferred.
"""
import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
import struct

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'rouge/data'
BASE = ROOT / 'research/p3-map-direct-checkpoints-294'
SOURCE_MANIFEST_SHA256 = '52e447bc1c616db021da9cad9c2cbc68a0a63849138cd7f9297b4ccc1b32c097'
EXPECTED = {
    'ro6_n_3_2': {'aliases': ('ro6_n_3_2', 'ro6_e_3_2'),
        'cells': ((3, 2), (3, 3), (3, 4), (3, 5), (3, 6), (4, 3), (4, 4), (4, 5), (4, 6), (4, 9))},
    'ro6_t_5': {'aliases': ('ro6_t_5', 'ro6_e_t_5'),
        'cells': ((1, 4), (2, 3), (2, 5), (3, 2), (3, 6), (4, 3), (4, 5), (5, 4))},
}


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def grid_digest(stage):
    """Semantic source digest, identical to the public parser's digest format."""
    semantic = [[{key: stage['tiles'][i].get(key) for key in
                 ('tileKey', 'heightType', 'buildableType', 'passableMask')}
                 for i in row] for row in stage['map']]
    return hashlib.sha256(json.dumps(semantic, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def source_inputs():
    """Check every pin again, including after a previous successful call."""
    path = BASE / 'source-manifest.json'
    require(sha(path) == SOURCE_MANIFEST_SHA256, 'The sealed source manifest changed.')
    manifest = read(path)
    require(manifest['section'] == 294 and len(manifest['files']) == 10, 'The source set changed.')
    for name, expected in manifest['files'].items():
        require(type(name) is str and Path(name).name == name, 'Source filenames must be flat and exact.')
        path = BASE / name
        require(sha(path) == expected['sha256'] and path.stat().st_size == expected['bytes'],
                'A sealed source changed: ' + name)
    return manifest


def finite_pair(value):
    return (type(value) is list and len(value) == 2
            and all(type(v) in (int, float) and math.isfinite(v) for v in value))


def compare_pixels(author, peer, width, height):
    """Nulls stay unknown; the unrounded Euclidean distance alone gates <=4."""
    for value in (author, peer):
        if value is None:
            continue
        require(finite_pair(value), 'Only null or finite original pixel pairs are allowed.')
        require(0 <= value[0] < width and 0 <= value[1] < height, 'An observed pixel is outside its bitmap.')
    distance = math.dist(author, peer) if author is not None and peer is not None else None
    return distance, distance is not None and distance <= 4


def bitmap(path, image):
    raw = path.read_bytes()
    require(len(raw) == image['bytes'] and hashlib.sha256(raw).hexdigest() == image['sha256'],
            'Original PNG bytes changed: ' + str(path))
    require(hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() == image['source_blob_sha1'],
            'Original resource Git blob changed.')
    require(raw[:8] == b'\x89PNG\r\n\x1a\n' and raw[12:16] == b'IHDR', 'Expected original PNG/IHDR.')
    require(struct.unpack('>II', raw[16:24]) == (image['width'], image['height']), 'PNG dimensions changed.')


def check_stage(stage_id, expected, stages, public_data):
    stage = stages[stage_id]
    require(stage['id'] == stage_id and stage['image'] == expected['image']
            and stage['level_source'] == expected['level_source'], 'Explicit alias source changed: ' + stage_id)
    require(grid_digest(stage) == expected['grid_sha256'], 'Explicit alias semantic grid changed: ' + stage_id)
    require((len(stage['map']), len(stage['map'][0])) == (expected['rows'], expected['cols']), 'Grid size changed.')
    bitmap(public_data / stage['image']['file'], stage['image'])
    bitmap(BASE / expected['bitmap_file'], stage['image'])
    level = BASE / expected['level_file']
    require(sha(level) == stage['level_source']['sha256'] and level.stat().st_size == stage['level_source']['bytes'],
            'The full original level changed.')
    original = read(level)['mapData']
    # Original JSON rows already are display rows. Route row is only metadata.
    require(original['map'] == stage['map'] and original['tiles'] == stage['tiles'],
            'Original display map/tiles changed.')
    return stage


def indexed(rows, cells, row_key, column_key, who):
    require(type(rows) is list and len(rows) == len(cells), who + ' dropped or added requested cells.')
    result = {}
    for item in rows:
        require(type(item) is dict and type(item.get(row_key)) is int and type(item.get(column_key)) is int,
                who + ' needs exact integer display cells.')
        cell = item[row_key], item[column_key]
        require(cell in cells and cell not in result, who + ' has a duplicate or unrequested cell.')
        result[cell] = item
    require(set(result) == set(cells), who + ' omitted requested cells.')
    return result


def reader_sources(author, blind, source, stages):
    require(author['schema'] == 'section-294-independent-map-author-readings-v1', 'Author schema changed.')
    require(blind['schema'] == 'p3-map-294-independent-blind-readings-v1' and blind['frozen'] is True,
            'Blind source/freeze changed.')
    independence = author['independence_declaration']
    for field in ('read_other_reader_coordinates', 'read_other_reader_outputs', 'read_prior_049_or_051_fits',
                  'read_any_projection_results', 'used_fit_or_interpolation', 'modified_original_images'):
        require(independence[field] is False, 'Author independence declaration changed: ' + field)
    for field in ('author_output_seen', 'other_readings_seen', 'old_049_051_fits_seen',
                  'projection_or_landmark_reference_seen', 'coordinate_exchange', 'fit_or_interpolation_used'):
        require(blind['declarations'][field] is False, 'Blind independence declaration changed: ' + field)
    require(blind['declarations']['coordinates_frozen_after_this_first_formal_record'] is True,
            'Blind coordinates are not declared frozen.')
    first_images = {row['map_id']: row for row in author['images']}
    peer_images = {row['stage_id']: row for row in blind['images']}
    require(len(first_images) == len(author['images']) == len(EXPECTED)
            and len(peer_images) == len(blind['images']) == len(EXPECTED)
            and set(first_images) == set(peer_images) == set(EXPECTED), 'Reader image identities changed.')
    for sid in EXPECTED:
        stage = stages[sid]
        image, level = stage['image'], stage['level_source']
        first, peer = first_images[sid], peer_images[sid]
        require((first['sha256'], first['bytes'], first['width'], first['height'], first['level_sha256']) ==
                (image['sha256'], image['bytes'], image['width'], image['height'], level['sha256']),
                'Author image/level identity changed.')
        require((peer['image_sha256'], peer['image_byte_size'], peer['image_size'], peer['level_sha256']) ==
                (image['sha256'], image['bytes'], [image['width'], image['height']], level['sha256']),
                'Blind image/level identity changed.')
        dimensions = len(stage['map']), len(stage['map'][0])
        require((first['map_rows'], first['map_columns']) == dimensions
                and (peer['rows'], peer['columns']) == dimensions, 'Reader logical dimensions changed.')
    return first_images, peer_images


def build(*, public_data=None):
    """Return candidate and evidence without modifying any source or runtime data."""
    public_data = Path(public_data) if public_data is not None else DATA
    source_inputs()
    source = read(BASE / 'source-records.json')
    require(source['section'] == 294 and source['agreement_tolerance_px'] == 4
            and source['source_pixel_adjustments_after_comparison'] == 0
            and source['both_readers_frozen_before_comparison'] is True, 'Source gate changed.')
    stages = read(public_data / 'battle-previews.json')['stages']
    source_stages = source['stages']
    require(set(source_stages) == {sid for row in EXPECTED.values() for sid in row['aliases']},
            'The four explicitly bound aliases changed.')
    for sid, expected in source_stages.items():
        check_stage(sid, expected, stages, public_data)
    author = read(BASE / 'AUTHOR_READINGS.json')
    blind = read(BASE / 'BLIND_READINGS.json')
    request = read(BASE / 'REQUEST_MANIFEST.json')
    require(request['request_count'] == 18 and len(request['requests']) == 18
            and author['request_count'] == 18 and len(author['readings']) == 18
            and blind['summary']['requested_count'] == blind['summary']['preserved_request_count'] == 18,
            'The complete eighteen requests must be preserved.')
    require({row['map_id'] for row in request['requests']} == set(EXPECTED)
            and {row['map_id'] for row in author['readings']} == set(EXPECTED), 'Reader/request domain changed.')
    _, peer_images = reader_sources(author, blind, source, stages)
    prior = read(BASE / 'prior-direct-references.json')
    output = copy.deepcopy(prior)
    require((len(prior['references']), len(prior['stages']), sum(len(v['points']) for v in prior['references'].values()))
            == (8, 14, 40), 'The prior published direct scope changed.')
    regular = read(BASE / 'prior-regular-projections.json')
    require(read(public_data / 'battle-map-projections.json') == regular, 'The complete regular dictionaries changed.')
    require((len(regular['calibrations']), len(regular['stages'])) == (12, 24), 'The regular baseline changed.')
    comparisons = []
    for sid, contract in EXPECTED.items():
        stage, cells = stages[sid], contract['cells']
        rows, cols = len(stage['map']), len(stage['map'][0])
        requested = indexed([r for r in request['requests'] if r['map_id'] == sid], cells,
                            'display_row', 'display_column', 'request')
        first = indexed([r for r in author['readings'] if r['map_id'] == sid], cells,
                        'display_row', 'display_column', 'author')
        second = indexed(peer_images[sid]['readings'], cells, 'display_row', 'column', 'blind')
        points = []
        for row, col in cells:
            origin, one, two = requested[row, col], first[row, col], second[row, col]
            route_row = rows - 1 - row
            require(origin['map_array_row'] == one['map_array_row'] == two['json_array_row'] == row,
                    'Display row must index the original array directly.')
            require(origin['source_row'] == one['source_row'] == one['engine_row'] == two['source_row'] == route_row,
                    'The distinct route/source row changed.')
            require(one['source_tile_index'] == route_row * cols + col, 'Reader route-index metadata changed.')
            tile = stage['tiles'][stage['map'][row][col]]
            require(tile['heightType'] == 'LOWLAND' and tile['tileKey'] in ('tile_floor', 'tile_road'),
                    'A requested surface is outside the existing parser contract.')
            require(one['source_tile_key'] == two['tile_key'] == tile['tileKey']
                    and one['source_height_type'] == two['height_type'] == tile['heightType'],
                    'A frozen reader used another logical tile identity.')
            require('observed_pixel' in one and 'independent_pixel' in two, 'Unreadable points must remain explicit null.')
            author_pixel, peer_pixel = one['observed_pixel'], two['independent_pixel']
            distance, accepted = compare_pixels(author_pixel, peer_pixel, stage['image']['width'], stage['image']['height'])
            comparison = {'reference': sid, 'row': row, 'col': col, 'map_array_row': row,
                'source_route_row': route_row, 'tile_key': tile['tileKey'],
                'observed_pixel': copy.deepcopy(author_pixel), 'independent_pixel': copy.deepcopy(peer_pixel),
                'agreement_px': distance, 'accepted_for_runtime': accepted,
                'reason': ('independent direct observations agree within four pixels' if accepted else
                           'at least one direct observation is unknown' if distance is None else
                           'independent direct observations disagree beyond four pixels')}
            comparisons.append(comparison)
            if accepted:
                points.append({key: copy.deepcopy(comparison[key]) for key in
                    ('row', 'col', 'tile_key', 'observed_pixel', 'independent_pixel', 'agreement_px')})
        # Source equality is explicit, not inferred from similar stage names.
        for alias_id in contract['aliases']:
            alias = stages[alias_id]
            require(alias['image']['sha256'] == stage['image']['sha256']
                    and alias['level_source'] == stage['level_source'] and grid_digest(alias) == grid_digest(stage),
                    'An alias cannot borrow centers from a different grid or image.')
        if not points:
            continue
        require(sid not in output['references'], 'An existing image reference cannot be replaced.')
        output['references'][sid] = {'rows': rows, 'cols': cols, 'width': stage['image']['width'],
            'height': stage['image']['height'], 'bitmap_sha256': stage['image']['sha256'],
            'grid_sha256': grid_digest(stage), 'agreement_tolerance_px': 4,
            'scope': 'Only listed independently concordant LOWLAND floor/road centers. '
                     'No plane, inverse, interpolation, segments or actual-position accuracy claim.',
            'points': points}
        for alias_id in contract['aliases']:
            require(alias_id not in output['stages'], 'An existing stage binding cannot be replaced.')
            output['stages'][alias_id] = {'reference': sid, 'image_file': stages[alias_id]['image']['file'],
                'level_sha256': stages[alias_id]['level_source']['sha256']}
    require(len(comparisons) == 18, 'One or more original requests disappeared.')
    actual_author_nonnull = sum(row['observed_pixel'] is not None for row in comparisons)
    actual_blind_nonnull = sum(row['independent_pixel'] is not None for row in comparisons)
    require(author['non_null_count'] == actual_author_nonnull
            and blind['summary']['non_null_count'] == actual_blind_nonnull
            and blind['summary']['null_count'] == 18 - actual_blind_nonnull, 'Reader count declarations disagree.')
    for group in ('references', 'stages'):
        require(all(output[group][key] == value for key, value in prior[group].items()), 'An old direct value changed.')
    accepted = sum(row['accepted_for_runtime'] for row in comparisons)
    if accepted:
        output['source'].setdefault('additional_source_packs', []).append('research/p3-map-direct-checkpoints-294')
        output['source']['direct_checkpoint_294'] = {'source_manifest_sha256': SOURCE_MANIFEST_SHA256,
            'source_pixel_adjustments': 0, 'reader_kind': 'two isolated-context agents; not human gameplay observations'}
    current = read(public_data / 'fixed-landmark-references.json')
    require(current == prior or current == output, 'Current direct data contains unrelated concurrent changes.')
    unbound = {sid: stage for sid, stage in stages.items() if sid not in regular['stages']}
    require((len(unbound), len({row['image']['sha256'] for row in unbound.values()})) == (81, 59),
            'The regular calibration gap changed.')
    receipt = {'status': 'PARTIAL_DIRECT_CENTER_CANDIDATE' if accepted else 'NO_NEW_ACCEPTED_DIRECT_CENTERS',
        'reader_kind': 'two isolated-context agents, not humans or live-game observers',
        'new_requested_points': len(comparisons), 'author_non_null_points': actual_author_nonnull,
        'independent_non_null_points': actual_blind_nonnull,
        'new_accepted_points': accepted, 'new_rejected_or_unknown_points': len(comparisons) - accepted,
        'new_agreement_comparisons': comparisons, 'max_unrounded_agreement_px':
            max((row['agreement_px'] for row in comparisons if row['agreement_px'] is not None), default=None),
        'prior_partial_points': 40, 'new_partial_images': len(output['references']) - len(prior['references']),
        'new_partial_stage_bindings': len(output['stages']) - len(prior['stages']),
        'total_partial_images': len(output['references']), 'total_partial_stage_bindings': len(output['stages']),
        'total_partial_points': sum(len(row['points']) for row in output['references'].values()),
        'regular_images_preserved': 12, 'regular_stage_bindings_preserved': 24, 'complete_calibration_added': 0,
        'remaining_regular_unbound_stages': 81, 'remaining_regular_distinct_bitmaps': 59,
        'prior_direct_values_unchanged': True, 'regular_dictionaries_unchanged': True,
        'source_pixel_adjustments_after_comparison': 0, 'absolute_position_accuracy_verified': False,
        'extrapolation': False, 'inverse_cell_assignment': False, 'checkpoint_connections': False,
        'game_actions': 0, 'chat_requests': 0, 'live_samples': 0,
        'source_manifest_sha256': SOURCE_MANIFEST_SHA256,
        'output_sha256': hashlib.sha256(encoded(output)).hexdigest()}
    return output, receipt


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--public-data-dir', type=Path, default=DATA,
                        help='Existing public stage data; always read-only.')
    parser.add_argument('--output-dir', type=Path,
                        help='New exclusive candidate directory; never installs runtime data.')
    args = parser.parse_args()
    output, receipt = build(public_data=args.public_data_dir)
    if args.output_dir:
        directory = args.output_dir.resolve()
        require(not directory.is_relative_to(args.public_data_dir.resolve()), 'Candidate output cannot enter public runtime data.')
        directory.mkdir(parents=True, exist_ok=False)
        (directory / 'candidate.json').write_bytes(encoded(output))
        (directory / 'verification.json').write_bytes(encoded(receipt))
    print(json.dumps({key: value for key, value in receipt.items() if key != 'new_agreement_comparisons'}, ensure_ascii=False))
