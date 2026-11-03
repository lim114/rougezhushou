"""294 fixed-image centers: original readings, append-only scope and real parser."""
import copy
import hashlib
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from rouge.battle_preview import DATA, battle_data
from rouge.fixed_landmark_mapping import landmark_data
from rouge.map_projection import grid_digest, projection_data, projection_for
from scripts import extend_direct_landmark_294 as builder

STAGES = ('ro6_n_3_2', 'ro6_e_3_2', 'ro6_t_5', 'ro6_e_t_5')


def projected(stage):
    image = stage['image']
    return projection_for(stage, image['sha256'], (image['width'], image['height']))


class DirectCheckpoints294Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Replay the unchanged historical294 builder against its exact public58
        # input. Actual current appended values remain checked via landmark_data
        # below and the separate303 suite; no runtime source is replaced.
        snapshot = builder.ROOT / 'research/p3-map-direct-ground-303/prior-direct-references.json'
        raw = snapshot.read_bytes()
        if hashlib.sha256(raw).hexdigest() != '63ec9488f8f905d2ced1a4e349413e9c92d78125b9f1c94c00293cafa4d348f5':
            raise ValueError('Historical294 public58 input changed.')
        temporary = tempfile.TemporaryDirectory(prefix='rouge-public294-replay-')
        cls.addClassCleanup(temporary.cleanup)
        history = Path(temporary.name)
        original = DATA
        names = ['battle-previews.json', 'battle-map-projections.json']
        records = builder.read(builder.BASE / 'source-records.json')['stages']
        names += sorted({row['image']['file'] for row in records.values()})
        for name in names:
            target = history / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(original / name, target)
        (history / 'fixed-landmark-references.json').write_bytes(raw)
        for owner in (builder, sys.modules[__name__]):
            fixture = patch.object(owner, 'DATA', history)
            fixture.start()
            cls.addClassCleanup(fixture.stop)
        cls.output, cls.receipt = builder.build()

    def test_01_append_eighteen_centers_and_preserve_all_forty_prior_values(self):
        prior = builder.read(builder.BASE / 'prior-direct-references.json')
        current = landmark_data()
        for group in ('references', 'stages'):
            for key, value in prior[group].items():
                self.assertEqual(self.output[group][key], value)
            for key, value in self.output[group].items():
                self.assertEqual(current[group][key], value)
        self.assertEqual(set(self.output['stages']) - set(prior['stages']), set(STAGES))
        r = self.receipt
        self.assertEqual((r['new_requested_points'], r['new_accepted_points'], r['new_rejected_or_unknown_points']), (18, 18, 0))
        self.assertEqual((r['new_partial_images'], r['new_partial_stage_bindings']), (2, 4))
        self.assertEqual((r['total_partial_images'], r['total_partial_stage_bindings'], r['total_partial_points']), (10, 18, 58))

    def test_02_all_original_pairs_and_null_placeholders_survive_unrounded_comparison(self):
        author = builder.read(builder.BASE / 'AUTHOR_READINGS.json')
        blind = builder.read(builder.BASE / 'BLIND_READINGS.json')
        first = {(r['map_id'], r['display_row'], r['display_column']): r['observed_pixel'] for r in author['readings']}
        second = {(image['stage_id'], r['display_row'], r['column']): r['independent_pixel']
                  for image in blind['images'] for r in image['readings']}
        self.assertEqual(len(first), 18)
        self.assertEqual(set(first), set(second))
        comparisons = self.receipt['new_agreement_comparisons']
        self.assertEqual({(r['reference'], r['row'], r['col']) for r in comparisons}, set(first))
        for row in comparisons:
            key = row['reference'], row['row'], row['col']
            self.assertEqual(row['observed_pixel'], first[key])
            self.assertEqual(row['independent_pixel'], second[key])
            a, b = first[key], second[key]
            expected = math.hypot(a[0] - b[0], a[1] - b[1]) if a is not None and b is not None else None
            self.assertEqual(row['agreement_px'], expected)
            self.assertIs(row['accepted_for_runtime'], expected is not None and expected <= 4)
            points = self.output['references'][row['reference']]['points']
            point = next((p for p in points if (p['row'], p['col']) == key[1:]), None)
            if row['accepted_for_runtime']:
                self.assertEqual(point['observed_pixel'], a)
                self.assertEqual(point['independent_pixel'], b)
            else:
                self.assertIsNone(point)
        self.assertEqual(self.receipt['max_unrounded_agreement_px'], math.sqrt(10))
        self.assertEqual(self.output['references']['ro6_n_3_2']['points'][0]['observed_pixel'], [118, 129])
        self.assertNotEqual([118, 129], [(118 + 115) / 2, (129 + 128) / 2])

    def test_03_four_pixel_gate_uses_exact_distance_and_never_rounds_acceptance(self):
        self.assertEqual(builder.compare_pixels([10, 10], [14, 10], 512, 286), (4.0, True))
        self.assertEqual(builder.compare_pixels([10, 10], [14, 11], 512, 286), (math.sqrt(17), False))
        distance, accepted = builder.compare_pixels([10, 10], [math.nextafter(14.0, math.inf), 10], 512, 286)
        self.assertGreater(distance, 4)
        self.assertFalse(accepted)

    def test_04_unreadable_and_invalid_pixels_are_not_repaired_or_promoted(self):
        for one, two in ((None, [10, 10]), ([10, 10], None), (None, None)):
            self.assertEqual(builder.compare_pixels(one, two, 512, 286), (None, False))
        for value in ([], [1], [1, 2, 3], [True, 1], [float('nan'), 1], [float('inf'), 1],
                      [-1, 0], [512, 0], [0, 286], {'x': 1, 'y': 2}, '10,10'):
            with self.subTest(value=value), self.assertRaises(ValueError):
                builder.compare_pixels(value, [10, 10], 512, 286)

    def test_05_warm_source_tamper_and_missing_original_each_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            clone = Path(directory) / 'public'
            shutil.copytree(builder.BASE, clone)
            with patch.object(builder, 'BASE', clone):
                self.assertEqual(builder.build(), (self.output, self.receipt))
                names = ['source-manifest.json', *builder.read(clone / 'source-manifest.json')['files']]
                for name in names:
                    path = clone / name
                    raw = path.read_bytes()
                    with self.subTest(name=name, kind='changed'):
                        path.write_bytes(bytes([raw[0] ^ 1]) + raw[1:])
                        with self.assertRaises((ValueError, OSError)):
                            builder.build()
                        path.write_bytes(raw)
                    with self.subTest(name=name, kind='missing'):
                        path.unlink()
                        with self.assertRaises((ValueError, OSError)):
                            builder.build()
                        path.write_bytes(raw)
                self.assertEqual(builder.build(), (self.output, self.receipt))

    def test_06_source_reconstruction_is_deterministic_and_does_not_write(self):
        files = [p for p in builder.BASE.iterdir() if p.is_file()]
        files += [DATA / name for name in ('fixed-landmark-references.json', 'battle-map-projections.json', 'battle-previews.json')]
        before = {p: builder.sha(p) for p in files}
        self.assertEqual(builder.build(), (self.output, self.receipt))
        self.assertEqual(before, {p: builder.sha(p) for p in files})
        self.assertEqual(self.receipt['output_sha256'], hashlib.sha256(builder.encoded(self.output)).hexdigest())
        for field in ('game_actions', 'chat_requests', 'live_samples', 'source_pixel_adjustments_after_comparison'):
            self.assertEqual(self.receipt[field], 0)

    def test_07_every_alias_has_its_own_image_filename_level_grid_and_size_binding(self):
        records = builder.read(builder.BASE / 'source-records.json')['stages']
        self.assertEqual(set(records), set(STAGES))
        for sid in STAGES:
            stage = battle_data()['stages'][sid]
            binding = self.output['stages'][sid]
            self.assertEqual(binding['image_file'], stage['image']['file'])
            self.assertEqual(binding['level_sha256'], stage['level_source']['sha256'])
            self.assertEqual(records[sid]['grid_sha256'], grid_digest(stage))
            self.assertNotIn(sid, projection_data()['stages'])
            self.assertIsNotNone(projected(stage))

    def test_08_runtime_maps_exact_listed_integer_cells_without_inverse_or_segments(self):
        for sid in STAGES:
            stage = battle_data()['stages'][sid]
            reference = projected(stage)
            self.assertIsNotNone(reference, sid)
            points = self.output['references'][self.output['stages'][sid]['reference']]['points']
            expected = {(p['row'], p['col']): tuple(p['observed_pixel']) for p in points}
            self.assertEqual(reference.mapping_mode, 'direct_verified_centers')
            self.assertFalse(reference.supports_segment_reference)
            for r, row in enumerate(stage['map']):
                for c, _ in enumerate(row):
                    self.assertEqual(reference.project({'row': r, 'col': c}), expected.get((r, c)))
            for r, c in expected:
                self.assertIsNone(reference.project({'row': r + .1, 'col': c}))
                self.assertIsNone(reference.project({'row': True, 'col': c}))
                self.assertIsNone(reference.cell_at(*expected[r, c]))
            for invalid in ({'row': -1, 'col': 2}, {'row': float('nan'), 'col': 2}, None, {}):
                self.assertIsNone(reference.project(invalid))
            self.assertIsNone(reference.cell_at(0, 0))

    def test_09_stale_alias_bitmap_level_geometry_and_size_cannot_borrow_centers(self):
        for sid in STAGES:
            original = battle_data()['stages'][sid]
            for kind in ('id', 'level', 'filename', 'sha', 'dimensions', 'grid'):
                stage = copy.deepcopy(original)
                if kind == 'id':
                    stage['id'] = 'unbound-same-display-name'
                elif kind == 'level':
                    stage['level_source']['sha256'] = 'changed'
                elif kind == 'filename':
                    stage['image']['file'] = 'other.png'
                elif kind == 'sha':
                    stage['image']['sha256'] = '0' * 64
                elif kind == 'dimensions':
                    stage['image']['width'] += 1
                else:
                    # These are source-verified LOWLAND cells; [0][0] is already
                    # HIGHLAND/forbidden on both maps and would be a no-op.
                    point = self.output['references'][self.output['stages'][sid]['reference']]['points'][0]
                    stage['tiles'][stage['map'][point['row']][point['col']]]['heightType'] = 'HIGHLAND'
                self.assertIsNone(projected(stage), (sid, kind))
            self.assertIsNone(projection_for(original, '0' * 64, (512, 286)))
            self.assertIsNone(projection_for(original, original['image']['sha256'], (511, 286)))

    def test_10_road_centers_require_explicit_matching_tags_and_old_floors_survive(self):
        stage = battle_data()['stages']['ro6_n_3_2']
        for value in (None, False, 1, [], {}, 'tile_floor', 'tile_wall'):
            data = copy.deepcopy(self.output)
            data['references']['ro6_n_3_2']['points'][0]['tile_key'] = value
            with self.subTest(value=value), patch('rouge.fixed_landmark_mapping.landmark_data', return_value=data):
                self.assertIsNone(projected(stage))
        data = copy.deepcopy(self.output)
        data['references']['ro6_n_3_2']['points'][0].pop('tile_key')
        with patch('rouge.fixed_landmark_mapping.landmark_data', return_value=data):
            self.assertIsNone(projected(stage))
        prior = builder.read(builder.BASE / 'prior-direct-references.json')
        for sid in prior['stages']:
            self.assertIsNotNone(projected(battle_data()['stages'][sid]))

    def test_11_wrong_tile_height_or_surface_still_fails_after_digest_rebinding(self):
        for sid in ('ro6_n_3_2', 'ro6_t_5'):
            for height, key in (('HIGHLAND', 'tile_road'), ('LOWLAND', 'tile_wall'), ('LOWLAND', 'tile_forbidden')):
                stage = copy.deepcopy(battle_data()['stages'][sid])
                data = copy.deepcopy(self.output)
                point = data['references'][sid]['points'][0]
                tile = stage['tiles'][stage['map'][point['row']][point['col']]]
                tile['heightType'], tile['tileKey'] = height, key
                data['references'][sid]['grid_sha256'] = grid_digest(stage)
                with self.subTest(sid=sid, height=height, key=key), patch('rouge.fixed_landmark_mapping.landmark_data', return_value=data):
                    self.assertIsNone(projected(stage))

    def test_12_regular_planes_and_unresolved_regular_gap_are_not_counted_as_fixed(self):
        self.assertEqual(projection_data(), builder.read(builder.BASE / 'prior-regular-projections.json'))
        self.assertEqual((len(projection_data()['calibrations']), len(projection_data()['stages'])), (12, 24))
        self.assertEqual((self.receipt['remaining_regular_unbound_stages'], self.receipt['remaining_regular_distinct_bitmaps']), (81, 59))
        self.assertEqual(self.receipt['complete_calibration_added'], 0)
        for flag in ('absolute_position_accuracy_verified', 'extrapolation', 'inverse_cell_assignment', 'checkpoint_connections'):
            self.assertIs(self.receipt[flag], False)
        for record in self.output['references'].values():
            self.assertNotIn('matrix', record)
            self.assertNotIn('inverse', record)

    def test_13_explicit_candidate_write_is_exclusive_and_cannot_install_runtime_data(self):
        script = builder.ROOT / 'scripts/extend_direct_landmark_294.py'
        before = builder.sha(DATA / 'fixed-landmark-references.json')
        command = [sys.executable, '-B', '-X', 'utf8', str(script), '--public-data-dir', str(DATA)]
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / 'candidate'
            first = subprocess.run(command + ['--output-dir', str(target)], capture_output=True, text=True, encoding='utf-8')
            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertEqual(builder.read(target / 'candidate.json'), self.output)
            self.assertEqual(builder.read(target / 'verification.json'), self.receipt)
            second = subprocess.run(command + ['--output-dir', str(target)], capture_output=True, text=True, encoding='utf-8')
            self.assertNotEqual(second.returncode, 0)
            blocked = DATA / 'forbidden-294-candidate-write'
            self.assertFalse(blocked.exists())
            third = subprocess.run(command + ['--output-dir', str(blocked)], capture_output=True, text=True, encoding='utf-8')
            self.assertNotEqual(third.returncode, 0)
            self.assertFalse(blocked.exists())
        self.assertEqual(builder.sha(DATA / 'fixed-landmark-references.json'), before)

    def test_14_request_index_rejects_lost_extra_duplicate_and_bool_cells(self):
        cells = ((3, 2), (3, 3))
        good = [{'row': 3, 'col': 2}, {'row': 3, 'col': 3}]
        self.assertEqual(set(builder.indexed(good, cells, 'row', 'col', 'fixture')), set(cells))
        for rows in (good[:1], good + [good[0]], [good[0], good[0]],
                     [good[0], {'row': True, 'col': 3}], [good[0], {'row': 4, 'col': 3}]):
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                builder.indexed(rows, cells, 'row', 'col', 'fixture')

    def test_15_original_json_display_rows_are_not_inverted_into_route_rows(self):
        source = builder.read(builder.BASE / 'source-records.json')['stages']
        for comparison in self.receipt['new_agreement_comparisons']:
            sid, row, col = comparison['reference'], comparison['row'], comparison['col']
            stage = battle_data()['stages'][sid]
            raw = builder.read(builder.BASE / source[sid]['level_file'])['mapData']
            self.assertEqual(raw['map'], stage['map'])
            tile = raw['tiles'][raw['map'][row][col]]
            self.assertEqual(tile['tileKey'], comparison['tile_key'])
            self.assertEqual(comparison['map_array_row'], row)
            self.assertEqual(comparison['source_route_row'], len(raw['map']) - 1 - row)
        point = next(p for p in self.output['references']['ro6_n_3_2']['points'] if (p['row'], p['col']) == (4, 9))
        self.assertEqual(point['observed_pixel'], [406, 164])
        self.assertEqual(projected(battle_data()['stages']['ro6_n_3_2']).project({'row': 4, 'col': 9}), (406, 164))
        self.assertIsNone(projected(battle_data()['stages']['ro6_n_3_2']).project({'row': 2, 'col': 9}))

    def test_16_frozen_readings_are_agents_not_a_human_or_game_accuracy_claim(self):
        manifest = builder.source_inputs()
        self.assertEqual(manifest['files']['AUTHOR_READINGS.json']['sha256'],
                         '6632a056c955fa03c351d888e07e817b4b7fcfca41579c7f3d9ef05c0610203c')
        self.assertEqual(manifest['files']['BLIND_READINGS.json']['sha256'],
                         '82d3edee8560181e9f9cc08220f5cf616918984d37ffd7ff5c2412fa94b2b463')
        records = builder.read(builder.BASE / 'source-records.json')
        self.assertIn('isolated-context agents', records['readers'])
        self.assertIn('not a third', records['root_image_review_role'])
        self.assertIn('not humans', self.receipt['reader_kind'])
        self.assertFalse(self.receipt['absolute_position_accuracy_verified'])

    def test_17_return_values_are_independent_and_mutation_cannot_change_source(self):
        output, receipt = builder.build()
        output['references']['ro6_t_5']['points'][0]['observed_pixel'][0] = -999
        receipt['new_agreement_comparisons'][0]['observed_pixel'][0] = -888
        self.assertEqual(builder.build(), (self.output, self.receipt))
        self.assertEqual(self.output['references']['ro6_t_5']['points'][0]['observed_pixel'], [237, 63])

    def test_18_runtime_recomputes_peer_distance_instead_of_trusting_the_stored_number(self):
        stage = battle_data()['stages']['ro6_n_3_2']
        for dx, dy, accepted in ((4, 0, True), (4, 1, False)):
            data = copy.deepcopy(self.output)
            point = data['references']['ro6_n_3_2']['points'][0]
            x, y = point['observed_pixel']
            point['independent_pixel'] = [x + dx, y + dy]
            point['agreement_px'] = 0
            with self.subTest(dx=dx, dy=dy), patch('rouge.fixed_landmark_mapping.landmark_data', return_value=data):
                self.assertIs(projected(stage) is not None, accepted)


if __name__ == '__main__':
    unittest.main()
