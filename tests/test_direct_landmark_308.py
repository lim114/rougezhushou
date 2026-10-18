"""Complete67 frozen originals, exact107 preservation and runtime direct cells."""
import copy
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from rouge.battle_preview import DATA as PUBLIC_DATA
from rouge import fixed_landmark_mapping as landmarks
from rouge import map_projection as projections
from scripts import extend_direct_landmark_303 as historical_builder

ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'rouge/app.py').is_file())
FIRST_COMPARISON = 'verification/sections/308-preparation/first-frozen-comparison.json'
FIRST_COMPARISON_SHA256 = 'a0141c9bb9fb6c405e23157c62a09eb31861855022e803004bec9d50c85df0f4'
STAGE_IDS = ('ro6_n_5_1', 'ro6_e_5_1', 'ro6_n_5_5', 'ro6_e_5_5')


def load_builder():
    explicit = os.environ.get('ROUGE_308_BUILDER_FILE')
    if explicit:
        spec = importlib.util.spec_from_file_location('explicit_direct_builder_308', explicit)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    from scripts import extend_direct_landmark_308
    return extend_direct_landmark_308


def pin(path):
    raw = path.read_bytes()
    return hashlib.sha256(raw).hexdigest(), len(raw)


class DirectGround308Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.builder = load_builder()
        cls.output, cls.receipt = cls.builder.build()
        cls.source = cls.builder.read(cls.builder.BASE / 'source-records.json')
        cls.stages = cls.builder.read(cls.builder.DATA / 'battle-previews.json')['stages']
        cls.comparisons = cls.receipt['new_agreement_comparisons']
        raw = (ROOT / FIRST_COMPARISON).read_bytes()
        if hashlib.sha256(raw).hexdigest() != FIRST_COMPARISON_SHA256:
            raise AssertionError('Keep the independent root first frozen67 comparison unchanged.')
        cls.first_comparison = json.loads(raw)
        cls.temporary = tempfile.TemporaryDirectory(prefix='rouge308-public-runtime-')
        cls.addClassCleanup(cls.temporary.cleanup)
        cls.runtime_data = Path(cls.temporary.name) / 'runtime'
        cls.runtime_data.mkdir()
        for name in ('battle-previews.json', 'battle-map-projections.json'):
            shutil.copyfile(cls.builder.DATA / name, cls.runtime_data / name)
        (cls.runtime_data / 'fixed-landmark-references.json').write_bytes(cls.builder.encoded(cls.output))
        old_sources = historical_builder.read(historical_builder.BASE / 'source-records.json')
        images = {row['image']['file'] for row in cls.source['stages'].values()}
        images.update(row['image']['file'] for row in old_sources['stages'].values())
        for name in images:
            target = cls.runtime_data / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(PUBLIC_DATA / name, target)

    def setUp(self):
        self.addCleanup(landmarks.landmark_data.cache_clear)
        self.addCleanup(projections.projection_data.cache_clear)
        landmarks.landmark_data.cache_clear()
        projections.projection_data.cache_clear()
        self.enterContext(patch.object(landmarks, 'DATA', self.runtime_data))
        self.enterContext(patch.object(projections, 'DATA', self.runtime_data))

    def reference(self, stage_id):
        stage = self.stages[stage_id]
        image = stage['image']
        return projections.projection_for(stage, image['sha256'], (image['width'], image['height']))

    def source_clone(self, directory):
        clone = Path(directory) / 'public'
        manifest = self.builder.source_inputs()
        for name in [*manifest['files'], 'research/p3-map-direct-ground-308/source-manifest.json']:
            target = clone / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(self.builder.ROOT / name, target)
        # The historical source package pins its exact regular snapshot;
        # this explicit runtime dependency also belongs in a valid clone.
        shutil.copyfile(self.builder.DATA / 'battle-map-projections.json', clone / 'rouge/data/battle-map-projections.json')
        target = clone / 'rouge/data/fixed-landmark-references.json'
        target.write_bytes(self.builder.encoded(self.output))
        return clone

    def test_01_root_first_counts_and_complete_original107_records_are_preserved(self):
        r = self.receipt
        self.assertEqual((r['new_requested_points'], r['new_accepted_points'], r['new_rejected_or_unknown_points']), (67, 16, 51))
        self.assertEqual([(x['stage_id'], x['requested'], x['accepted']) for x in r['per_image']],
                         [('ro6_n_5_1', 30, 5), ('ro6_n_5_5', 37, 11)])
        self.assertEqual((r['total_partial_images'], r['total_partial_stage_bindings'], r['total_partial_points']), (14, 25, 123))
        prior_path = self.builder.BASE / 'prior-direct-references.json'
        self.assertEqual(pin(prior_path), ('dc43bbbe70eab6f11cc8661c3bfeab994000ea614ea0f8c999a596f5cb2c445a', 58293))
        prior = self.builder.read(prior_path)
        self.assertEqual((len(prior['references']), len(prior['stages']), sum(len(v['points']) for v in prior['references'].values())), (12, 21, 107))
        for group in ('references', 'stages'):
            for name, row in prior[group].items():
                self.assertTrue(self.builder.same_json(self.output[group][name], row))
        self.assertEqual(self.builder.read(self.builder.DATA / 'fixed-landmark-references.json'), self.output)

    def test_02_every67_raw_row_cue_pointer_and_rejection_matches_first_comparison(self):
        originals = {label: self.builder.read(self.builder.BASE / ('READER_' + label + '_ORIGINAL.json')) for label in ('A', 'B')}
        first = {row['request_id']: row for row in self.first_comparison['comparisons']}
        self.assertEqual(len(self.comparisons), 67)
        self.assertEqual(len(first), 67)
        self.assertEqual({row['request_id'] for row in self.comparisons}, set(first))
        for row in self.comparisons:
            expected = first[row['request_id']]
            self.assertEqual((row['reference'], row['row'], row['col']), (expected['stage_id'], expected['row'], expected['col']))
            for label, field, pixel_key in (('A', 'observed_pixel', 'observed_pixel'), ('B', 'pixel', 'independent_pixel')):
                link = row['original_reader_rows'][label]
                self.assertEqual((link['file'], link['pixel_field']), ('READER_' + label + '_ORIGINAL.json', field))
                image = originals[label]['images'][link['image_index']]
                raw = image['readings'][link['reading_index']]
                self.assertEqual(image['stage_id'], row['reference'])
                self.assertEqual((raw['request_id'], raw['row'], raw['col'], raw['tile_key']),
                                 (row['request_id'], row['row'], row['col'], row['tile_key']))
                self.assertEqual(raw[field], row[pixel_key])
                self.assertEqual(raw['reason'], row['reader_reason'][label])
                self.assertEqual(row['reader_cue'][label], raw['cue'] if label == 'A' else None)
            a, b = row['observed_pixel'], row['independent_pixel']
            distance = math.dist(a, b) if a is not None and b is not None else None
            self.assertEqual((a, b, distance, row['accepted_for_runtime']),
                             (expected['original_A'], expected['original_B'], expected['unrounded_distance'], expected['accepted']))
            self.assertEqual(row['agreement_px'], distance)
            self.assertIs(row['accepted_for_runtime'], distance is not None and distance <= 4)
            record = self.output['references'][row['reference']]
            point = next((p for p in record['points'] if (p['row'], p['col']) == (row['row'], row['col'])), None)
            if row['accepted_for_runtime']:
                self.assertEqual((point['observed_pixel'], point['independent_pixel']), (a, b))
            else:
                self.assertIsNone(point)

    def test_03_strict_four_pixel_gate_never_rounds_or_repairs_null(self):
        self.assertEqual(self.builder.compare_pixels([10, 10], [14, 10], 512, 286), (4.0, True))
        distance, accepted = self.builder.compare_pixels([10, 10], [math.nextafter(14., math.inf), 10], 512, 286)
        self.assertGreater(distance, 4)
        self.assertFalse(accepted)
        self.assertEqual(self.builder.compare_pixels([10, 10], [14, 11], 512, 286), (math.sqrt(17), False))
        for one, two in ((None, [10, 10]), ([10, 10], None), (None, None)):
            self.assertEqual(self.builder.compare_pixels(one, two, 512, 286), (None, False))

    def test_04_malformed_or_outside_original_pixels_are_rejected(self):
        for bad in ([], [1], [1, 2, 3], [True, 2], [float('nan'), 2], [float('inf'), 1],
                    [-1, 0], [512, 0], [0, 286], {'x': 1, 'y': 2}, '1,2'):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                self.builder.compare_pixels(bad, [10, 10], 512, 286)

    def test_05_all_authorities_fresh_after_valid_warm_clone_flip_and_missing(self):
        with tempfile.TemporaryDirectory() as directory:
            clone = self.source_clone(directory)
            with patch.object(self.builder, 'ROOT', clone), patch.object(self.builder, 'DATA', clone / 'rouge/data'), \
                 patch.object(self.builder, 'BASE', clone / 'research/p3-map-direct-ground-308'):
                self.assertEqual(self.builder.build(), (self.output, self.receipt))
                names = ['research/p3-map-direct-ground-308/source-manifest.json',
                         *self.builder.read(self.builder.BASE / 'source-manifest.json')['files']]
                for name in names:
                    path = clone / name
                    raw = path.read_bytes()
                    try:
                        with self.subTest(name=name, mode='changed'):
                            path.write_bytes(raw + b' ')
                            with self.assertRaises((ValueError, OSError)):
                                self.builder.build()
                        path.write_bytes(raw)
                        with self.subTest(name=name, mode='missing'):
                            path.unlink()
                            with self.assertRaises((ValueError, OSError)):
                                self.builder.build()
                    finally:
                        path.write_bytes(raw)
                self.assertEqual(self.builder.build(), (self.output, self.receipt))

    def test_06_all_67_source_lowland_floor_road_requests_are_mandatory(self):
        request = self.builder.read(self.builder.BASE / 'REQUEST_MANIFEST.json')
        groups = self.builder.requests_by_stage(request, self.stages)
        self.assertEqual([len(groups[s]['all_requests']) for s in self.builder.EXPECTED], [30, 37])
        for mutation in ('drop', 'duplicate', 'wrong_identity', 'wrong_tile', 'wrong_alias'):
            edited = copy.deepcopy(request)
            rows = edited['groups'][0]['all_requests']
            if mutation == 'drop': rows.pop()
            elif mutation == 'duplicate': rows[1] = copy.deepcopy(rows[0])
            elif mutation == 'wrong_identity': rows[0]['request_id'] += ':other'
            elif mutation == 'wrong_tile': rows[0]['tile_metadata']['heightType'] = 'HIGHLAND'
            else: edited['groups'][0]['explicit_alias_records'][1]['image']['file'] = 'other.png'
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                self.builder.requests_by_stage(edited, self.stages)

    def test_07_both_original_raw_shapes_and_independence_fail_closed(self):
        manifest = self.builder.source_inputs()
        for label in ('A', 'B'):
            original = self.builder.read(self.builder.BASE / ('READER_' + label + '_ORIGINAL.json'))
            links = self.source['reader_source_pin_links'][label]
            for mutation in ('pins', 'independence', 'duplicateimage', 'reason'):
                edited = copy.deepcopy(original)
                if mutation == 'pins':
                    if label == 'A': edited['source_pins']['REQUESTS.json']['bytes'] += 1
                    else: edited['source_pins']['files'][1] = edited['source_pins']['files'][0]
                elif mutation == 'independence':
                    if label == 'A': edited['independence']['averaging_or_coordinate_adjustment_against_peer_used'] = True
                    else: edited['declarations']['other_reader_seen'] = True
                elif mutation == 'duplicateimage': edited['images'][1]['stage_id'] = edited['images'][0]['stage_id']
                else: edited['images'][0]['readings'][0]['reason'] = ''
                with self.subTest(label=label, mutation=mutation), self.assertRaises(ValueError):
                    self.builder.reader_images(edited, label, links, manifest, self.stages)
        a = self.builder.read(self.builder.BASE / 'READER_A_ORIGINAL.json')
        a['images'][0]['readings'][0]['readable'] = not a['images'][0]['readings'][0]['readable']
        with self.assertRaises(ValueError):
            self.builder.reader_images(a, 'A', self.source['reader_source_pin_links']['A'], manifest, self.stages)

    def test_08_each_alias_requires_exact_image_level_and_complete_grid(self):
        self.assertEqual(tuple(self.source['stages']), STAGE_IDS)
        for stage_id in STAGE_IDS:
            for mutation in ('image', 'level', 'grid', 'dimension'):
                stages = copy.deepcopy(self.stages)
                stage = stages[stage_id]
                if mutation == 'image': stage['image']['file'] += '.other'
                elif mutation == 'level': stage['level_source']['sha256'] = '0' * 64
                elif mutation == 'grid': stage['tiles'][stage['map'][0][0]]['passableMask'] = -999
                else: stage['map'].pop()
                with self.subTest(stage_id=stage_id, mutation=mutation), self.assertRaises(ValueError):
                    self.builder.check_stages(self.source['stages'], stages, self.builder.DATA)

    def test_09_real_resolver_returns_only_frozen_A_centers_for_four_aliases(self):
        for stage_id in STAGE_IDS:
            reference = self.reference(stage_id)
            self.assertIsInstance(reference, landmarks.FixedLandmarkReference)
            self.assertEqual(reference.mapping_mode, 'direct_verified_centers')
            self.assertFalse(reference.supports_segment_reference)
            binding = self.output['stages'][stage_id]
            for point in self.output['references'][binding['reference']]['points']:
                self.assertEqual(reference.project({'row': point['row'], 'col': point['col']}), tuple(point['observed_pixel']))
                self.assertIsNone(reference.cell_at(*point['observed_pixel']))

    def test_10_all_51_rejected_requests_stay_unmapped_for_each_explicit_alias(self):
        rejected = [row for row in self.comparisons if not row['accepted_for_runtime']]
        self.assertEqual(len(rejected), 51)
        for row in rejected:
            for alias in self.builder.EXPECTED[row['reference']]['aliases']:
                self.assertIsNone(self.reference(alias).project({'row': row['row'], 'col': row['col']}))

    def test_11_fractional_malformed_highland_and_all_unlisted_cells_have_no_projection(self):
        for stage_id in STAGE_IDS:
            reference = self.reference(stage_id)
            for cell in (None, {}, {'row': True, 'col': 1}, {'row': .5, 'col': 1},
                         {'row': 1, 'col': float('nan')}, {'row': -1, 'col': 0}, {'row': 999, 'col': 999}):
                self.assertIsNone(reference.project(cell))
            stage = self.stages[stage_id]
            listed = {(p['row'], p['col']) for p in self.output['references'][self.output['stages'][stage_id]['reference']]['points']}
            for row, cells in enumerate(stage['map']):
                for col, _ in enumerate(cells):
                    if (row, col) not in listed:
                        self.assertIsNone(reference.project({'row': row, 'col': col}))

    def test_12_runtime_cannot_borrow_other_tags_or_raised_surfaces(self):
        for tag in (None, 3, [], 'tile_start', 'tile_wall'):
            current = copy.deepcopy(self.output)
            current['references']['ro6_n_5_1']['points'][0]['tile_key'] = tag
            with patch.object(landmarks, 'landmark_data', return_value=current):
                self.assertIsNone(self.reference('ro6_n_5_1'))
        for stage_id in STAGE_IDS:
            stage = copy.deepcopy(self.stages[stage_id])
            point = self.output['references'][self.output['stages'][stage_id]['reference']]['points'][0]
            stage['tiles'][stage['map'][point['row']][point['col']]]['heightType'] = 'HIGHLAND'
            image = stage['image']
            self.assertIsNone(projections.projection_for(stage, image['sha256'], (512, 286)))

    def test_13_regular_bytes_and_81_stage_59_image_whole_map_gap_are_unchanged(self):
        prior = self.builder.BASE / 'prior-regular-projections.json'
        self.assertEqual((self.builder.DATA / 'battle-map-projections.json').read_bytes(), prior.read_bytes())
        regular = self.builder.read(prior)
        self.assertEqual((len(regular['calibrations']), len(regular['stages'])), (12, 24))
        unbound = [stage for sid, stage in self.stages.items() if sid not in regular['stages']]
        self.assertEqual((len(unbound), len({stage['image']['sha256'] for stage in unbound})), (81, 59))
        self.assertEqual(self.receipt['whole_map_gaps_unchanged'], [81, 59])
        self.assertFalse(self.receipt['actual_enemy_position_inverse_or_segment_verified'])

    def test_14_default_cli_is_readonly_and_exclusive_output_cannot_install_into_runtime(self):
        before = pin(self.builder.DATA / 'fixed-landmark-references.json')
        command = [sys.executable, str(Path(self.builder.__file__))]
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(json.loads(result.stdout)['read_only'])
        self.assertEqual(pin(self.builder.DATA / 'fixed-landmark-references.json'), before)
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / 'new'
            first = subprocess.run(command + ['--output-dir', str(target)], capture_output=True, text=True)
            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertEqual(self.builder.read(target / 'fixed-landmark-references.json'), self.output)
            self.assertNotEqual(subprocess.run(command + ['--output-dir', str(target)], capture_output=True).returncode, 0)
        forbidden = self.builder.DATA / '_forbidden308'
        self.assertNotEqual(subprocess.run(command + ['--output-dir', str(forbidden)], capture_output=True).returncode, 0)
        self.assertFalse(forbidden.exists())
        self.assertEqual(pin(self.builder.DATA / 'fixed-landmark-references.json'), before)

    def test_15_current_must_be_exact_prior107_or_this_complete_append_not_superset(self):
        with tempfile.TemporaryDirectory() as directory:
            data = Path(directory)
            for name in ('battle-previews.json', 'battle-map-projections.json'):
                shutil.copyfile(self.runtime_data / name, data / name)
            shutil.copytree(self.runtime_data / 'battle-maps', data / 'battle-maps')
            path = data / 'fixed-landmark-references.json'
            path.write_bytes((self.builder.BASE / 'prior-direct-references.json').read_bytes())
            self.assertEqual(self.builder.build(public_data=data), (self.output, self.receipt))
            changed = copy.deepcopy(self.output)
            changed['references']['invented'] = copy.deepcopy(changed['references']['ro6_n_5_1'])
            path.write_bytes(self.builder.encoded(changed))
            with self.assertRaises(ValueError):
                self.builder.build(public_data=data)

    def test_16_original303_still_rejects_live_append_and_exact107_replay_succeeds(self):
        self.assertEqual(hashlib.sha256(Path(historical_builder.__file__).read_bytes()).hexdigest(),
                         '1b32f7e3c9cf37fec595436d9054010278ac4b9ab9637715732791a01d9f7d8c')
        before = pin(self.builder.DATA / 'fixed-landmark-references.json')
        with self.assertRaisesRegex(ValueError, 'Current direct data must be the exact frozen prior58'):
            historical_builder.build(public_data=self.runtime_data)
        result = subprocess.run([sys.executable, '-B', '-X', 'utf8', str(Path(historical_builder.__file__))], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Current direct data must be the exact frozen prior58', result.stderr)
        self.assertEqual(pin(self.builder.DATA / 'fixed-landmark-references.json'), before)
        with tempfile.TemporaryDirectory() as directory:
            data = Path(directory)
            for name in ('battle-previews.json', 'battle-map-projections.json'):
                shutil.copyfile(self.runtime_data / name, data / name)
            shutil.copytree(self.runtime_data / 'battle-maps', data / 'battle-maps')
            shutil.copyfile(self.builder.BASE / 'prior-direct-references.json', data / 'fixed-landmark-references.json')
            historical, receipt = historical_builder.build(public_data=data)
            self.assertTrue(self.builder.same_json(historical, self.builder.read(self.builder.BASE / 'prior-direct-references.json')))
            self.assertEqual(receipt['total_partial_points'], 107)
        self.assertEqual(pin(self.builder.DATA / 'fixed-landmark-references.json'), before)


if __name__ == '__main__':
    unittest.main(verbosity=2)
