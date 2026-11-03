"""Complete89 frozen-reader append, without fitting or game/UI operations."""
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
from scripts import extend_direct_landmark_294 as historical_builder


def load_builder():
    explicit = os.environ.get('ROUGE_303_BUILDER_FILE')
    if explicit:
        spec = importlib.util.spec_from_file_location('explicit_direct_builder_303', explicit)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    from scripts import extend_direct_landmark_303
    return extend_direct_landmark_303


def pin(path):
    raw = path.read_bytes()
    return hashlib.sha256(raw).hexdigest(), len(raw)


class DirectGround303Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.builder = load_builder()
        # Replay this303 contract against its exact public107 input. The308
        # tests separately verify the original builder rejects the live append.
        cls.historical_temporary = tempfile.TemporaryDirectory(prefix='rouge303-exact107-')
        cls.addClassCleanup(cls.historical_temporary.cleanup)
        cls.historical_data = Path(cls.historical_temporary.name) / 'data'
        cls.historical_data.mkdir()
        prior = Path(__file__).resolve().parents[1] / 'research/p3-map-direct-ground-308/prior-direct-references.json'
        prior_raw = prior.read_bytes()
        if len(prior_raw) != 58293 or hashlib.sha256(prior_raw).hexdigest() != 'dc43bbbe70eab6f11cc8661c3bfeab994000ea614ea0f8c999a596f5cb2c445a':
            raise AssertionError('Exact original303 public107 bytes are required.')
        for name in ('battle-previews.json', 'battle-map-projections.json'):
            shutil.copyfile(PUBLIC_DATA / name, cls.historical_data / name)
        historical_source = cls.builder.read(cls.builder.BASE / 'source-records.json')
        for image in {row['image']['file'] for row in historical_source['stages'].values()}:
            target = cls.historical_data / image
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(PUBLIC_DATA / image, target)
        (cls.historical_data / 'fixed-landmark-references.json').write_bytes(prior_raw)
        original_data = cls.builder.DATA
        cls.addClassCleanup(setattr, cls.builder, 'DATA', original_data)
        cls.builder.DATA = cls.historical_data
        cls.output, cls.receipt = cls.builder.build(public_data=cls.historical_data)
        cls.source = cls.builder.read(cls.builder.BASE / 'source-records.json')
        cls.stages = cls.builder.read(cls.builder.DATA / 'battle-previews.json')['stages']
        cls.comparisons = cls.receipt['new_agreement_comparisons']
        cls.temporary = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.temporary.cleanup)
        cls.runtime_data = Path(cls.temporary.name) / 'runtime'
        cls.runtime_data.mkdir()
        for name in ('battle-previews.json', 'battle-map-projections.json'):
            shutil.copyfile(cls.builder.DATA / name, cls.runtime_data / name)
        (cls.runtime_data / 'fixed-landmark-references.json').write_bytes(cls.builder.encoded(cls.output))
        images = {row['image']['file'] for row in cls.source['stages'].values()}
        images.update(cls.stages[sid]['image']['file'] for sid in
                      ('ro6_n_3_2', 'ro6_e_3_2', 'ro6_t_5', 'ro6_e_t_5'))
        for image in images:
            target = cls.runtime_data / image
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(PUBLIC_DATA / image, target)

    def setUp(self):
        self.addCleanup(landmarks.landmark_data.cache_clear)
        self.addCleanup(projections.projection_data.cache_clear)
        landmarks.landmark_data.cache_clear()
        projections.projection_data.cache_clear()
        self.enterContext(patch.object(landmarks, 'DATA', self.runtime_data))
        self.enterContext(patch.object(projections, 'DATA', self.runtime_data))

    def reference(self, sid):
        stage = self.stages[sid]
        image = stage['image']
        return projections.projection_for(stage, image['sha256'], (image['width'], image['height']))

    def source_clone(self, directory):
        clone = Path(directory) / 'public'
        manifest = self.builder.source_inputs()
        for name in [*manifest['files'], 'research/p3-map-direct-ground-303/source-manifest.json']:
            source = self.builder.ROOT / name
            target = clone / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
        target = clone / 'rouge/data/fixed-landmark-references.json'
        target.write_bytes(self.builder.encoded(self.output))
        return clone

    def test_01_complete_scope_literal_counts_and_original58_are_preserved(self):
        receipt = self.receipt
        self.assertEqual((receipt['new_requested_points'], receipt['new_accepted_points'],
                          receipt['new_rejected_or_unknown_points']), (89, 49, 40))
        self.assertEqual(receipt['per_image'], [
            {'stage_id': 'ro6_b_6', 'requested': 55, 'accepted': 37, 'unreadable': 12, 'agreement_exceeds_4px': 6},
            {'stage_id': 'ro6_n_2_3', 'requested': 34, 'accepted': 12, 'unreadable': 22, 'agreement_exceeds_4px': 0}])
        self.assertEqual((receipt['total_partial_images'], receipt['total_partial_stage_bindings'],
                          receipt['total_partial_points']), (12, 21, 107))
        prior = self.builder.read(self.builder.BASE / 'prior-direct-references.json')
        self.assertEqual(sum(len(v['points']) for v in prior['references'].values()), 58)
        for group in ('references', 'stages'):
            for name, row in prior[group].items():
                self.assertTrue(self.builder.same_json(self.output[group][name], row))
        self.assertEqual(self.builder.read(self.builder.DATA / 'fixed-landmark-references.json'), self.output)

    def test_02_every89_original_row_and_rejection_survives_without_averaging(self):
        originals = {label: self.builder.read(self.builder.BASE / ('READER_' + label + '_ORIGINAL.json'))
                     for label in ('A', 'B')}
        self.assertEqual(len(self.comparisons), 89)
        self.assertEqual(len({row['request_id'] for row in self.comparisons}), 89)
        for row in self.comparisons:
            for label, pixel_name in (('A', 'observed_pixel'), ('B', 'independent_pixel')):
                link = row['original_reader_rows'][label]
                original = originals[label]['images'][link['image_index']]['readings'][link['reading_index']]
                self.assertEqual(original['request_id'], row['request_id'])
                self.assertEqual(original['pixel'], row[pixel_name])
                self.assertEqual(original['reason'], row['reader_reason'][label])
            a, b = row['observed_pixel'], row['independent_pixel']
            distance = None if a is None or b is None else math.dist(a, b)
            self.assertEqual(row['agreement_px'], distance)
            self.assertIs(row['accepted_for_runtime'], distance is not None and distance <= 4)
            point = next((p for p in self.output['references'][row['reference']]['points']
                          if (p['row'], p['col']) == (row['row'], row['col'])), None)
            if row['accepted_for_runtime']:
                self.assertEqual(point['observed_pixel'], a)
                self.assertEqual(point['independent_pixel'], b)
            else:
                self.assertIsNone(point)
        self.assertEqual(sum(r['rejection'] == 'agreement_exceeds_4px' for r in self.comparisons), 6)
        self.assertEqual(sum(r['rejection'] == 'one_or_both_unreadable' for r in self.comparisons), 34)

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

    def test_05_all_frozen_files_fresh_after_valid_warm_clone_flip_and_missing(self):
        with tempfile.TemporaryDirectory() as directory:
            clone = self.source_clone(directory)
            with patch.object(self.builder, 'ROOT', clone), patch.object(self.builder, 'DATA', clone / 'rouge/data'), \
                 patch.object(self.builder, 'BASE', clone / 'research/p3-map-direct-ground-303'):
                self.assertEqual(self.builder.build(), (self.output, self.receipt))
                names = ['research/p3-map-direct-ground-303/source-manifest.json',
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

    def test_06_all_source_lowland_floor_and_road_requests_are_mandatory(self):
        request = self.builder.read(self.builder.BASE / 'REQUEST_MANIFEST.json')
        groups = self.builder.requests_by_stage(request, self.stages)
        self.assertEqual([len(groups[s]['requests']) for s in self.builder.EXPECTED], [55, 34])
        for mutation in ('drop', 'duplicate', 'wrong_identity', 'wrong_tile'):
            edited = copy.deepcopy(request)
            rows = edited['groups'][0]['requests']
            if mutation == 'drop': rows.pop()
            elif mutation == 'duplicate': rows[1] = copy.deepcopy(rows[0])
            elif mutation == 'wrong_identity': rows[0]['request_id'] += ':other'
            else: rows[0]['tile_metadata']['heightType'] = 'HIGHLAND'
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                self.builder.requests_by_stage(edited, self.stages)

    def test_07_original_reader_pin_list_and_independence_fail_closed(self):
        original = self.builder.read(self.builder.BASE / 'READER_A_ORIGINAL.json')
        manifest = self.builder.source_inputs()
        links = self.source['reader_source_pin_links']['A']
        for mutation in ('duplicatepin', 'wrongbytes', 'independence', 'duplicateimage'):
            edited = copy.deepcopy(original)
            if mutation == 'duplicatepin': edited['source_pins']['files'][1] = edited['source_pins']['files'][0]
            elif mutation == 'wrongbytes': edited['source_pins']['files'][0]['bytes'] += 1
            elif mutation == 'independence': edited['declarations']['other_reader_seen'] = True
            else: edited['images'][1]['stage_id'] = edited['images'][0]['stage_id']
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                self.builder.reader_images(edited, 'A', links, manifest, self.stages)

    def test_08_each_alias_requires_exact_image_level_and_complete_grid(self):
        for sid in self.source['stages']:
            for mutation in ('image', 'level', 'grid', 'dimension'):
                stages = copy.deepcopy(self.stages)
                stage = stages[sid]
                if mutation == 'image': stage['image']['file'] += '.other'
                elif mutation == 'level': stage['level_source']['sha256'] = '0' * 64
                elif mutation == 'grid': stage['tiles'][stage['map'][0][0]]['passableMask'] = -999
                else: stage['map'].pop()
                with self.subTest(sid=sid, mutation=mutation), self.assertRaises(ValueError):
                    self.builder.check_stages(self.source['stages'], stages, self.builder.DATA)

    def test_09_real_resolver_returns_only_frozen_A_centers_for_all_three_stages(self):
        for sid, binding in self.output['stages'].items():
            if sid not in self.source['stages']: continue
            reference = self.reference(sid)
            self.assertIsInstance(reference, landmarks.FixedLandmarkReference)
            self.assertEqual(reference.mapping_mode, 'direct_verified_centers')
            self.assertFalse(reference.supports_segment_reference)
            for point in self.output['references'][binding['reference']]['points']:
                self.assertEqual(reference.project({'row': point['row'], 'col': point['col']}), tuple(point['observed_pixel']))
                self.assertIsNone(reference.cell_at(*point['observed_pixel']))

    def test_10_all_forty_rejected_cells_stay_unmapped_with_aliases(self):
        for row in self.comparisons:
            if row['accepted_for_runtime']: continue
            aliases = self.builder.EXPECTED[row['reference']]['aliases']
            for alias in aliases:
                self.assertIsNone(self.reference(alias).project({'row': row['row'], 'col': row['col']}))

    def test_11_fractional_malformed_highland_and_unlisted_cells_have_no_projection(self):
        for sid in self.source['stages']:
            reference = self.reference(sid)
            for cell in (None, {}, {'row': True, 'col': 1}, {'row': .5, 'col': 1},
                         {'row': 1, 'col': float('nan')}, {'row': -1, 'col': 0}, {'row': 999, 'col': 999}):
                self.assertIsNone(reference.project(cell))
            stage = self.stages[sid]
            listed = {(p['row'], p['col']) for p in self.output['references'][self.output['stages'][sid]['reference']]['points']}
            for row, cells in enumerate(stage['map']):
                for col, _ in enumerate(cells):
                    if (row, col) not in listed:
                        self.assertIsNone(reference.project({'row': row, 'col': col}))

    def test_12_runtime_cannot_borrow_different_tags_or_surface(self):
        for tag in (None, 3, [], 'tile_start', 'tile_wall'):
            current = copy.deepcopy(self.output)
            current['references']['ro6_b_6']['points'][0]['tile_key'] = tag
            with patch.object(landmarks, 'landmark_data', return_value=current):
                self.assertIsNone(self.reference('ro6_b_6'))
        for sid in self.source['stages']:
            stage = copy.deepcopy(self.stages[sid])
            point = self.output['references'][self.output['stages'][sid]['reference']]['points'][0]
            stage['tiles'][stage['map'][point['row']][point['col']]]['heightType'] = 'HIGHLAND'
            image = stage['image']
            self.assertIsNone(projections.projection_for(stage, image['sha256'], (512, 286)))

    def test_13_old_regular_dictionary_and_whole_map_gap_are_unchanged(self):
        prior = self.builder.read(self.builder.BASE / 'prior-regular-projections.json')
        self.assertEqual(self.builder.read(self.builder.DATA / 'battle-map-projections.json'), prior)
        self.assertEqual((len(prior['calibrations']), len(prior['stages'])), (12, 24))
        unbound = [v for sid, v in self.stages.items() if sid not in prior['stages']]
        self.assertEqual((len(unbound), len({v['image']['sha256'] for v in unbound})), (81, 59))
        self.assertEqual(self.receipt['whole_map_gaps_unchanged'], [81, 59])
        self.assertFalse(self.receipt['actual_enemy_position_inverse_or_segment_verified'])

    def test_14_default_cli_is_readonly_and_candidate_output_is_exclusive(self):
        before = pin(self.builder.DATA / 'fixed-landmark-references.json')
        command = [sys.executable, '-B', '-X', 'utf8', str(Path(self.builder.__file__)), '--public-data-dir', str(self.historical_data)]
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(json.loads(result.stdout)['read_only'])
        self.assertEqual(pin(self.builder.DATA / 'fixed-landmark-references.json'), before)
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / 'new'
            first = subprocess.run(command + ['--output-dir', str(target)], capture_output=True, text=True)
            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertEqual(self.builder.read(target / 'fixed-landmark-references.json'), self.output)
            again = subprocess.run(command + ['--output-dir', str(target)], capture_output=True, text=True)
            self.assertNotEqual(again.returncode, 0)
        forbidden = subprocess.run(command + ['--output-dir', str(PUBLIC_DATA / '_forbidden303')], capture_output=True, text=True)
        self.assertNotEqual(forbidden.returncode, 0)
        self.assertFalse((PUBLIC_DATA / '_forbidden303').exists())
        self.assertEqual(pin(self.builder.DATA / 'fixed-landmark-references.json'), before)

    def test_15_current_accepts_only_exact_prior_or_exact_complete_new_dictionary(self):
        with tempfile.TemporaryDirectory() as directory:
            data = Path(directory)
            for name in ('battle-previews.json', 'battle-map-projections.json'):
                shutil.copyfile(self.runtime_data / name, data / name)
            shutil.copytree(self.runtime_data / 'battle-maps', data / 'battle-maps')
            path = data / 'fixed-landmark-references.json'
            path.write_bytes((self.builder.BASE / 'prior-direct-references.json').read_bytes())
            self.assertEqual(self.builder.build(public_data=data), (self.output, self.receipt))
            changed = copy.deepcopy(self.output)
            changed['references']['invented'] = copy.deepcopy(changed['references']['ro6_b_6'])
            path.write_bytes(self.builder.encoded(changed))
            with self.assertRaises(ValueError): self.builder.build(public_data=data)

    def test_16_unchanged_historical294_builder_rejects_current107_not_rewrite_it(self):
        current = self.runtime_data / 'fixed-landmark-references.json'
        before = pin(current)
        with self.assertRaisesRegex(ValueError, 'Current direct data contains unrelated concurrent changes'):
            historical_builder.build(public_data=self.runtime_data)
        self.assertEqual(pin(current), before)
        historical_data = self.runtime_data / 'historical58'
        historical_data.mkdir()
        self.addCleanup(shutil.rmtree, historical_data)
        for name in ('battle-previews.json', 'battle-map-projections.json'):
            shutil.copyfile(self.runtime_data / name, historical_data / name)
        shutil.copytree(self.runtime_data / 'battle-maps', historical_data / 'battle-maps')
        shutil.copyfile(self.builder.BASE / 'prior-direct-references.json', historical_data / 'fixed-landmark-references.json')
        historical, receipt = historical_builder.build(public_data=historical_data)
        self.assertEqual(historical, self.builder.read(self.builder.BASE / 'prior-direct-references.json'))
        self.assertEqual(receipt['total_partial_points'], 58)
        self.assertEqual(pin(current), before)


if __name__ == '__main__':
    unittest.main(verbosity=2)
