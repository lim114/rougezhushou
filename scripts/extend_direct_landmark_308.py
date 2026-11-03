"""Append only frozen, independently concordant original LOWLAND centers.

The complete67 source requests are compared, including nulls/rejections. Default
is read-only; --output-dir creates an exclusive candidate directory, never live
runtime data. There is no fit, averaging, interpolation, inverse or path model.
"""
import argparse
import copy
import hashlib
import json
import math
from pathlib import Path, PurePosixPath
import struct

ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'rouge/app.py').is_file())
DATA = ROOT / 'rouge/data'
BASE = ROOT / 'research/p3-map-direct-ground-308'
# Bound only after the root confirms both complete first readings are frozen.
SOURCE_MANIFEST_SHA256 = 'a47baddc0d8201afd63b415602f7ebf572d70efcc09fd6d9e4c0875fbba2ddff'
EXPECTED = {'ro6_n_5_1': {'aliases': ('ro6_n_5_1', 'ro6_e_5_1'), 'requested_count': 30},
            'ro6_n_5_5': {'aliases': ('ro6_n_5_5', 'ro6_e_5_5'), 'requested_count': 37}}


def read(path): return json.loads(path.read_bytes())
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def encoded(value): return (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode('utf8')
def require(condition, message):
    if not condition: raise ValueError(message)


def same_json(value, expected):
    if type(value) is not type(expected): return False
    if type(expected) is dict:
        return value.keys() == expected.keys() and all(type(k) is str and same_json(value[k], expected[k]) for k in value)
    if type(expected) is list:
        return len(value) == len(expected) and all(same_json(a, b) for a, b in zip(value, expected))
    return value == expected


def public_path(relative):
    require(type(relative) is str, 'Public source path must be text.')
    pure = PurePosixPath(relative)
    require(not pure.is_absolute() and '..' not in pure.parts and '\\' not in relative and ':' not in relative,
            'Only exact relative public source paths are allowed.')
    path = ROOT.joinpath(*pure.parts)
    require(path.resolve().is_relative_to(ROOT.resolve()) and not path.is_symlink(), 'Regular source escaped root.')
    return path


def source_inputs():
    manifest_path = BASE / 'source-manifest.json'
    require(type(SOURCE_MANIFEST_SHA256) is str and len(SOURCE_MANIFEST_SHA256) == 64 and sha(manifest_path) == SOURCE_MANIFEST_SHA256,
            'Both original readers and the full source set must first be root-frozen and byte-bound.')
    manifest = read(manifest_path)
    require(manifest['section'] == 308 and manifest['all_source_eligible_requests'] == 67
            and manifest['agreement_tolerance_px'] == 4, 'The complete67/4pixel source contract changed.')
    for relative, pin in manifest['files'].items():
        path = public_path(relative)
        require(type(pin['bytes']) is int and path.stat().st_size == pin['bytes'] and sha(path) == pin['sha256'],
                'A frozen public source changed: ' + relative)
    return manifest


def grid_digest(stage):
    values = [[{key: stage['tiles'][i].get(key) for key in ('tileKey', 'heightType', 'buildableType', 'passableMask')}
               for i in row] for row in stage['map']]
    return hashlib.sha256(json.dumps(values, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def finite_pair(value):
    return type(value) is list and len(value) == 2 and all(type(v) in (int, float) and math.isfinite(v) for v in value)


def compare_pixels(first, second, width, height):
    require(type(width) is int and type(height) is int and width > 0 and height > 0, 'Positive original image dimensions required.')
    for pixel in (first, second):
        if pixel is None: continue
        require(finite_pair(pixel), 'Only null or finite original pixel pairs are allowed.')
        require(0 <= pixel[0] < width and 0 <= pixel[1] < height, 'Original pixel falls outside its source image.')
    distance = math.dist(first, second) if first is not None and second is not None else None
    return distance, distance is not None and distance <= 4


def eligible_cells(stage):
    return {(row, col) for row, cells in enumerate(stage['map']) for col, index in enumerate(cells)
            if stage['tiles'][index]['heightType'] == 'LOWLAND'
            and stage['tiles'][index]['tileKey'] in ('tile_floor', 'tile_road')}


def bitmap(path, image):
    raw = path.read_bytes()
    require(len(raw) == image['bytes'] and hashlib.sha256(raw).hexdigest() == image['sha256'], 'The original image changed.')
    blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
    require(blob == image['source_blob_sha1'], 'The exact resource Git blob changed.')
    require(raw[:8] == b'\x89PNG\r\n\x1a\n' and raw[12:16] == b'IHDR'
            and struct.unpack('>II', raw[16:24]) == (image['width'], image['height']), 'Original PNG dimensions changed.')


def check_stages(records, stages, public_data):
    aliases = {sid for group in EXPECTED.values() for sid in group['aliases']}
    require(set(records) == aliases, 'All four explicit stage aliases must remain source-bound.')
    for identity, record in records.items():
        stage = stages[identity]
        require(stage['id'] == identity and same_json(stage['image'], record['image'])
                and same_json(stage['level_source'], record['level_source']), 'Explicit alias identity changed: ' + identity)
        require(grid_digest(stage) == record['grid_sha256'] and [len(stage['map']), len(stage['map'][0])] == record['grid_size'],
                'Explicit alias complete semantic grid changed: ' + identity)
        bitmap(public_data / stage['image']['file'], stage['image'])
        level = public_path(record['level_file'])
        require(sha(level) == stage['level_source']['sha256'] and level.stat().st_size == stage['level_source']['bytes'],
                'The reused complete original level changed.')
        original = read(level)['mapData']
        require(same_json(original['map'], stage['map']) and same_json(original['tiles'], stage['tiles']),
                'JSON map array is the display map; do not flip it using route source-row rules.')


def indexed(rows, cells, who):
    require(type(rows) is list and len(rows) == len(cells), who + ' dropped or added source-eligible cells.')
    result = {}
    for index, row in enumerate(rows):
        require(type(row) is dict and type(row.get('row')) is int and type(row.get('col')) is int,
                who + ' must retain exact integer display cells.')
        key = row['row'], row['col']
        require(key in cells and key not in result, who + ' duplicates or invents a cell.')
        result[key] = (index, row)
    require(set(result) == cells, who + ' omitted a source-eligible cell.')
    return result


def requests_by_stage(request, stages):
    require(request['schema'] == 'section308-source-only-full-lowland-requests-v1'
            and request['all_eligible_source_requests'] == 67
            and request['pixel_readings_fit_predictions_or_acceptance'] is None,
            'The complete pure67 source request must remain byte-bound and without readings.')
    groups = request['groups']
    require(type(groups) is list and len(groups) == 2, 'Both complete source request groups are required.')
    by_stage = {g['stage_id']: g for g in groups}
    require(len(by_stage) == len(groups) and set(by_stage) == set(EXPECTED), 'Source request stage domain changed.')
    total = 0
    for identity, group in by_stage.items():
        stage = stages[identity]
        cells = eligible_cells(stage)
        require(len(cells) == EXPECTED[identity]['requested_count'], 'The source-eligible ground scope changed.')
        require(type(group['rows']) is int and type(group['cols']) is int
                and group['rows'] == len(stage['map']) and group['cols'] == len(stage['map'][0])
                and group['title'] == stage['name'] and same_json(group['image'], stage['image']),
                'The complete request image, dimensions or title changed.')
        aliases = group['explicit_alias_records']
        require(type(aliases) is list and len(aliases) == len(EXPECTED[identity]['aliases'])
                and tuple(a['stage_id'] for a in aliases) == EXPECTED[identity]['aliases'],
                'Every explicit normal/emergency alias must remain in its original source order.')
        for alias in aliases:
            alias_stage = stages[alias['stage_id']]
            require(same_json(alias['level_source'], alias_stage['level_source'])
                    and same_json(alias['image'], alias_stage['image'])
                    and alias['semantic_grid_sha256'] == grid_digest(alias_stage)
                    and alias['current_projection_reference'] is None,
                    'An explicit source alias identity or its prior-unbound scope changed.')
        grid = read(BASE / ('reader-grid-' + identity + '.json'))
        require(grid['stage_id'] == identity and grid['title'] == stage['name']
                and type(grid['rows']) is int and type(grid['cols']) is int
                and grid['rows'] == len(stage['map']) and grid['cols'] == len(stage['map'][0])
                and grid['array_row_is_display_row'] is True
                and grid['route_source_row_conversion_is_not_applicable'] is True
                and same_json(grid['map'], stage['map']) and same_json(grid['tiles'], stage['tiles'])
                and same_json(grid['level_source'], stage['level_source']),
                'The complete original reader grid must use the actual display-map array.')
        level = public_path(grid['original_level_public_file'])
        require(sha(level) == stage['level_source']['sha256']
                and level.stat().st_size == stage['level_source']['bytes'],
                'The reader grid must remain bound to its complete original public level.')
        rows = indexed(group['all_requests'], cells, 'source request')
        for (row, col), (_, record) in rows.items():
            tile = stage['tiles'][stage['map'][row][col]]
            require(record['request_id'] == identity + ':display:' + str(row) + ':' + str(col)
                    and record['tile_key'] == tile['tileKey'] and record['height_type'] == 'LOWLAND'
                    and same_json(record['tile_metadata'], tile), 'Every complete requested tile must match the raw source.')
        total += len(rows)
    require(total == 67, 'All67 requests must remain, including every later rejection/null.')
    return by_stage


def reader_images(reader, expected_label, pin_links, manifest, stages):
    require(reader['schema'] == 'section308-independent-fixed-image-readings-v1'
            and reader['reader'] == expected_label and expected_label in ('A', 'B'),
            'Original reader schema/identity changed.')
    if expected_label == 'A':
        declarations = reader['independence']
        for key in ('other_reader_coordinate_files_or_results_seen',
                    'existing_projection_matrix_or_landmark_pixels_for_these_two_images_seen',
                    'fit_interpolation_or_extrapolation_used',
                    'averaging_or_coordinate_adjustment_against_peer_used', 'source_PNG_bytes_modified'):
            require(declarations[key] is False, 'Original A target-image independence changed: ' + key)
        require(declarations['formal_first_readings_sealed_before_any_comparison'] is True,
                'The original A first full coordinates must be frozen.')
        require(reader['acceptance_or_actual_positions_verified'] is False,
                'Original A readings are not actual-position or acceptance observations.')
        require(type(reader['source_pins']) is dict and all(type(k) is str for k in reader['source_pins']),
                'The original A short-name pin dictionary must remain intact.')
        pins = reader['source_pins']
        source_pin_manifest = reader['source_pin_manifest']
        require(source_pin_manifest['sha256'] == 'f5b0a26d68aa29b6dd5e5d67dfc96fdfc87e6c662c50f46da598bcb894077d49'
                and type(source_pin_manifest['bytes']) is int and source_pin_manifest['bytes'] == 1687,
                'The exact original pure reader-input manifest identity changed.')
        original_input_path = BASE / 'ORIGINAL_INPUT_PINS.json'
        require(sha(original_input_path) == source_pin_manifest['sha256']
                and original_input_path.stat().st_size == source_pin_manifest['bytes'],
                'The original pure reader-input manifest must be available by exact public bytes.')
        original_inputs = read(original_input_path)
        require(same_json(original_inputs['files'], pins)
                and original_inputs['source_request_count'] == 67
                and original_inputs['has_pixel_readings_or_fit'] is False
                and original_inputs['no_readers_results_or_comparison_present'] is True,
                'Original A five source pins must match the complete frozen pure input manifest.')
    else:
        declarations = reader['declarations']
        for key in ('other_reader_seen', 'old_projection_or_landmarks_seen', 'fit_or_interpolation_used', 'original_images_modified'):
            require(declarations[key] is False, 'An original B target-image independence declaration changed: ' + key)
        require(declarations['coordinates_frozen_in_first_formal_record'] is True,
                'Original B first full coordinates must be frozen.')
        pin_rows = reader['source_pins']['files']
        require(type(pin_rows) is list and len(pin_rows) == 5
                and all(type(pin) is dict and type(pin.get('path')) is str for pin in pin_rows),
                'The original B five full-path source-pin records are required.')
        pins = {pin['path']: pin for pin in pin_rows}
        require(len(pins) == len(pin_rows), 'Original B source pins may not duplicate a path.')
    require(type(pin_links) is dict and len(pins) == 5 and set(pins) == set(pin_links),
            'The original five source-pin keys changed.')
    require(len(pin_links) == 5 and len(set(pin_links.values())) == 5,
            'Both images, both complete grids and complete request must be pinned.')
    for raw_key, relative in pin_links.items():
        pin = pins[raw_key]
        expected = manifest['files'][relative]
        require(type(pin) is dict and type(pin['bytes']) is int and pin['sha256'] == expected['sha256']
                and pin['bytes'] == expected['bytes'], 'Original reader source pin differs from its exact public original.')
    images = reader['images']
    require(type(images) is list and len(images) == 2, 'Both reader image records are required.')
    by_stage = {image['stage_id']: (index, image) for index, image in enumerate(images)}
    require(len(by_stage) == len(images) and set(by_stage) == set(EXPECTED), 'Reader stage domain changed.')
    all_rows = []
    for identity, (_, image) in by_stage.items():
        stage = stages[identity]
        require(type(image['rows']) is int and type(image['cols']) is int
                and type(image['width']) is int and type(image['height']) is int
                and image['rows'] == len(stage['map']) and image['cols'] == len(stage['map'][0])
                and image['width'] == stage['image']['width'] and image['height'] == stage['image']['height']
                and image['image_sha256'] == stage['image']['sha256'], 'Reader original image/grid binding changed.')
        cells = eligible_cells(stage)
        rows = indexed(image['readings'], cells, 'reader ' + expected_label)
        for (row, col), (_, reading) in rows.items():
            tile = stage['tiles'][stage['map'][row][col]]
            require(reading['request_id'] == identity + ':display:' + str(row) + ':' + str(col)
                    and reading['tile_key'] == tile['tileKey']
                    and type(reading['reason']) is str and reading['reason'].strip(),
                    'Every original reader row needs its exact requested identity and retained reason.')
            pixel = reading['observed_pixel'] if expected_label == 'A' else reading['pixel']
            compare_pixels(pixel, None, image['width'], image['height'])
            if expected_label == 'A':
                require(reading['height_type'] == 'LOWLAND' and type(reading['readable']) is bool
                        and reading['readable'] is (pixel is not None) and type(reading['cue']) is str,
                        'Original A readability, exact LOWLAND tag and cue must remain unchanged.')
            all_rows.append(reading)
    if expected_label == 'A':
        require(type(reader['requested']) is int and reader['requested'] == len(all_rows) == 67
                and type(reader['readable']) is int and type(reader['null']) is int
                and reader['readable'] == sum(r['observed_pixel'] is not None for r in all_rows)
                and reader['null'] == sum(r['observed_pixel'] is None for r in all_rows),
                'Original A summary must equal all its unchanged first rows, not acceptance counts.')
    return by_stage


def build(*, public_data=None):
    public_data = Path(public_data) if public_data is not None else DATA
    manifest = source_inputs()
    source = read(BASE / 'source-records.json')
    require(source['section'] == 308 and source['agreement_tolerance_px'] == 4
            and source['both_first_complete_readings_frozen_before_comparison'] is True
            and source['source_pixel_adjustments_after_comparison'] == 0, 'First-frozen/no-adjustment source gate changed.')
    stages = read(public_data / 'battle-previews.json')['stages']
    check_stages(source['stages'], stages, public_data)
    requests = requests_by_stage(read(BASE / 'REQUEST_MANIFEST.json'), stages)
    a, b = read(BASE / 'READER_A_ORIGINAL.json'), read(BASE / 'READER_B_ORIGINAL.json')
    first = reader_images(a, 'A', source['reader_source_pin_links']['A'], manifest, stages)
    second = reader_images(b, 'B', source['reader_source_pin_links']['B'], manifest, stages)
    require(sha(BASE / 'prior-direct-references.json') == 'dc43bbbe70eab6f11cc8661c3bfeab994000ea614ea0f8c999a596f5cb2c445a',
            'Exact original107 file bytes are required.')
    prior = read(BASE / 'prior-direct-references.json')
    require((len(prior['references']), len(prior['stages']), sum(len(r['points']) for r in prior['references'].values())) == (12, 21, 107),
            'The entire old107 reference records must be preserved.')
    regular = read(BASE / 'prior-regular-projections.json')
    require(same_json(read(public_data / 'battle-map-projections.json'), regular)
            and (len(regular['calibrations']), len(regular['stages'])) == (12, 24), 'The entire old regular dictionary changed.')
    output = copy.deepcopy(prior)
    comparisons = []
    added_images, added_stages = 0, 0
    for identity, contract in EXPECTED.items():
        stage = stages[identity]
        cells = eligible_cells(stage)
        requested = indexed(requests[identity]['all_requests'], cells, 'request')
        ai, image_a = first[identity]
        bi, image_b = second[identity]
        one = indexed(image_a['readings'], cells, 'reader A')
        two = indexed(image_b['readings'], cells, 'reader B')
        points = []
        for row, col in sorted(cells):
            _, request = requested[row, col]
            aj, original_a = one[row, col]
            bj, original_b = two[row, col]
            for original in (original_a, original_b):
                require(original['request_id'] == request['request_id'] and original['tile_key'] == request['tile_key']
                        and type(original['reason']) is str and original['reason'].strip(), 'Original request identity and reading reason required.')
            pixel_a, pixel_b = original_a['observed_pixel'], original_b['pixel']
            distance, accepted = compare_pixels(pixel_a, pixel_b, stage['image']['width'], stage['image']['height'])
            links = {'A': {'file': 'READER_A_ORIGINAL.json', 'image_index': ai, 'reading_index': aj, 'pixel_field': 'observed_pixel'},
                     'B': {'file': 'READER_B_ORIGINAL.json', 'image_index': bi, 'reading_index': bj, 'pixel_field': 'pixel'}}
            comparisons.append({'reference': identity, 'row': row, 'col': col, 'tile_key': request['tile_key'],
                                'request_id': request['request_id'], 'observed_pixel': copy.deepcopy(pixel_a),
                                'independent_pixel': copy.deepcopy(pixel_b), 'reader_reason': {'A': original_a['reason'], 'B': original_b['reason']},
                                'original_reader_rows': links, 'reader_cue': {'A': original_a['cue'], 'B': None},
                                'agreement_px': distance, 'accepted_for_runtime': accepted,
                                'rejection': None if accepted else 'one_or_both_unreadable' if distance is None else 'agreement_exceeds_4px'})
            if accepted:
                points.append({'row': row, 'col': col, 'tile_key': request['tile_key'],
                               'observed_pixel': copy.deepcopy(pixel_a), 'independent_pixel': copy.deepcopy(pixel_b),
                               'agreement_px': distance, 'original_reader_rows': links})
        require(identity not in prior['references'] and all(s not in prior['stages'] for s in contract['aliases']),
                'New references must not replace any old record.')
        if points:
            output['references'][identity] = {'rows': len(stage['map']), 'cols': len(stage['map'][0]),
                'width': stage['image']['width'], 'height': stage['image']['height'], 'bitmap_sha256': stage['image']['sha256'],
                'grid_sha256': grid_digest(stage), 'agreement_tolerance_px': 4,
                'scope': 'Only independently concordant original LOWLAND tile_floor/road centers; no plane/inverse/segments or absolute-accuracy proof.',
                'points': points}
            added_images += 1
            for alias in contract['aliases']:
                alias_stage = stages[alias]
                output['stages'][alias] = {'reference': identity, 'image_file': alias_stage['image']['file'],
                                            'level_sha256': alias_stage['level_source']['sha256']}
                added_stages += 1
    require(len(comparisons) == 67 and len({r['request_id'] for r in comparisons}) == 67, 'No source comparison may be dropped.')
    for group in ('references', 'stages'):
        require(all(same_json(output[group][k], v) for k, v in prior[group].items()), 'An original107 record changed.')
    output['source']['additional_source_packs'].append('research/p3-map-direct-ground-308')
    output['source']['direct_ground_308'] = {'source_manifest_sha256': SOURCE_MANIFEST_SHA256,
        'source_pixel_adjustments': 0, 'reader_kind': 'two independent frozen agent readings, not human/gameplay observations',
        'requested_cells': 67, 'full_map_or_all_terrain_calibration_claimed': False}
    current = read(public_data / 'fixed-landmark-references.json')
    require(same_json(current, prior) or same_json(current, output),
            'Current direct data must be the exact frozen prior107 or this exact complete append, not an arbitrary superset.')
    distances = [r['agreement_px'] for r in comparisons if r['agreement_px'] is not None]
    accepted = sum(r['accepted_for_runtime'] for r in comparisons)
    per_image = []
    for identity in EXPECTED:
        rows = [row for row in comparisons if row['reference'] == identity]
        per_image.append({'stage_id': identity, 'requested': len(rows),
            'accepted': sum(row['accepted_for_runtime'] for row in rows),
            'unreadable': sum(row['agreement_px'] is None for row in rows),
            'agreement_exceeds_4px': sum(row['agreement_px'] is not None and not row['accepted_for_runtime'] for row in rows)})
    receipt = {'section': 308, 'kind': 'COMPLETE67_ORIGINAL_READER_COMPARISON_AND_APPEND_NOT_PRODUCT_ACCEPTANCE',
        'new_requested_points': 67, 'new_accepted_points': accepted, 'new_rejected_or_unknown_points': 67-accepted,
        'new_partial_images': added_images, 'new_partial_stage_bindings': added_stages,
        'total_partial_images': len(output['references']), 'total_partial_stage_bindings': len(output['stages']),
        'total_partial_points': 107+accepted, 'new_agreement_comparisons': comparisons, 'per_image': per_image,
        'max_unrounded_agreement_px_all_nonnull': max(distances) if distances else None,
        'original107_records_unchanged': True, 'original_regular_dictionary_unchanged': True,
        'source_pixel_adjustments': 0, 'whole_map_gaps_unchanged': [81,59],
        'actual_enemy_position_inverse_or_segment_verified': False,
        'source_manifest_sha256': SOURCE_MANIFEST_SHA256}
    return output, receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path)
    parser.add_argument('--public-data-dir', type=Path)
    args = parser.parse_args()
    output, receipt = build(public_data=args.public_data_dir)
    if args.output_dir is not None:
        target = args.output_dir.resolve()
        require(not target.exists(), 'Output must be a new exclusive candidate directory.')
        require(not target.is_relative_to(DATA.resolve()) and not target.is_relative_to(BASE.resolve()), 'Output cannot install into runtime or frozen sources.')
        require(not target.is_relative_to(ROOT.resolve()) or target.is_relative_to((ROOT/'.cache').resolve()),
                'Within the repository, candidate output must stay inside .cache, never production.')
        target.mkdir(parents=True, exist_ok=False)
        (target/'fixed-landmark-references.json').write_bytes(encoded(output))
        (target/'build-receipt.json').write_bytes(encoded(receipt))
    print(json.dumps({'section':308,'read_only':args.output_dir is None,
        'new_requested_points':receipt['new_requested_points'],'new_accepted_points':receipt['new_accepted_points'],
        'new_rejected_or_unknown_points':receipt['new_rejected_or_unknown_points'],
        'total_partial_points':receipt['total_partial_points'],'whole_map_gaps_unchanged':[81,59]},ensure_ascii=False))


if __name__=='__main__': main()
