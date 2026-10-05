"""Independently checked candidates do not rely on production integration."""
import copy
import hashlib
import json
import math
import unittest
from pathlib import Path
from unittest.mock import patch

import cv2
import numpy as np

from rouge.battle_preview import DATA, battle_data
from rouge.map_projection import grid_digest, projection_for
from scripts.build_map_projections_051 import build, fit

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / '.cache/research/map-projection-051'
NEW = ('ro6_n_5_2', 'ro6_e_5_2', 'ro6_n_5_7', 'ro6_e_5_7')


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class FixedGroundCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.candidate = read(BASE / 'battle-map-projections-candidate.json')
        cls.inputs = read(BASE / 'calibration-input.json')
        cls.receipt = read(BASE / 'evidence.json')

    def load(self, stage, sha=None, size=None):
        image = stage['image']
        with patch('rouge.map_projection.projection_data', return_value=self.candidate):
            return projection_for(stage, image['sha256'] if sha is None else sha,
                (image['width'], image['height']) if size is None else size)

    def test_prior_eight_calibrations_sixteen_bindings_forty_nine_checks_unchanged(self):
        prior = read(BASE / 'prior-projections.json')
        self.assertEqual(digest(BASE / 'prior-projections.json'), read(BASE / 'prior-receipt.json')['sha256'])
        self.assertEqual(len(prior['calibrations']), 8)
        self.assertEqual(len(prior['stages']), 16)
        self.assertEqual(sum(len(c['checks']) for c in prior['calibrations'].values()), 49)
        for kind in ('calibrations', 'stages'):
            for key, value in prior[kind].items():
                self.assertEqual(self.candidate[kind][key], value)
        for key, value in prior['source'].items():
            self.assertEqual(self.candidate['source'][key], value)
        self.assertEqual(len(self.candidate['calibrations']), 10)
        self.assertEqual(len(self.candidate['stages']), 20)
        self.assertEqual(sum(len(c['checks']) for c in self.candidate['calibrations'].values()), 78)

    def test_frozen_original_observations_are_not_adjusted_after_fitting(self):
        originals = {}
        for record in self.inputs['frozen_observations']:
            path = ROOT / record['file']
            self.assertEqual(digest(path), record['sha256'])
            for entry in read(path)['calibrations']:
                originals[entry['id']] = entry
        for entry in self.inputs['calibrations']:
            self.assertEqual(entry, originals[entry['id']])
            initial = read(BASE / (entry['id'] + '-initial-fit.json'))
            self.assertEqual(initial['input'], entry)
            self.assertTrue(initial['accepted'])
            calibration = self.candidate['calibrations'][entry['id']]
            self.assertEqual(calibration['anchors'], entry['anchors'])
            self.assertEqual(calibration['checks'], initial['checks'])

    def test_twenty_nine_independent_centers_are_lowland_floor_and_never_fit_inputs(self):
        count = 0
        for entry in self.inputs['calibrations']:
            self.assertGreaterEqual(len(entry['checks']), 5)
            anchors = {(r, c) for r, c, *_ in entry['anchors']}
            stage = battle_data()['stages'][entry['id']]
            projection = self.load(stage)
            self.assertIsNotNone(projection)
            for check in self.candidate['calibrations'][entry['id']]['checks']:
                cell = (check['row'], check['col'])
                self.assertNotIn(cell, anchors)
                tile = stage['tiles'][stage['map'][cell[0]][cell[1]]]
                self.assertEqual((tile['tileKey'], tile['heightType']), ('tile_floor', 'LOWLAND'))
                error = math.dist(projection.project(check), check['observed_pixel'])
                self.assertLessEqual(error, 4)
                self.assertAlmostEqual(error, check['error_px'], places=12)
                count += 1
        self.assertEqual(count, 29)

    def test_the_fit_only_consumes_original_corner_coordinates(self):
        for entry in self.inputs['calibrations']:
            independent, _ = cv2.findHomography(
                np.array([[c, r] for r, c, x, y in entry['anchors']], float),
                np.array([[x, y] for r, c, x, y in entry['anchors']], float), method=0)
            fitted, _ = fit(entry)
            np.testing.assert_array_equal(fitted, independent)
            modified = copy.deepcopy(entry)
            modified['checks'][0][2] += .001
            changed, _ = fit(modified)
            np.testing.assert_array_equal(changed, fitted)
            self.assertEqual(fitted.ravel().tolist(), self.candidate['calibrations'][entry['id']]['matrix'])

    def test_a_failed_holdout_is_rejected_without_relaxing_the_pixel_gate(self):
        for entry in self.inputs['calibrations']:
            wrong = copy.deepcopy(entry)
            wrong['checks'][0][2] += 100
            with self.assertRaises(AssertionError):
                fit(wrong)
        self.assertEqual(self.inputs['pixel_tolerance'], 4)
        self.assertEqual(self.receipt['tolerance_px'], 4)

    def test_actual_pinned_images_level_bytes_and_grids_match_every_binding(self):
        for sid in NEW:
            stage = battle_data()['stages'][sid]
            binding = self.candidate['stages'][sid]
            calibration = self.candidate['calibrations'][binding['calibration']]
            image_file = DATA / stage['image']['file']
            image_bytes = image_file.read_bytes()
            self.assertEqual(digest(image_file), calibration['bitmap_sha256'])
            self.assertEqual(len(image_bytes), stage['image']['bytes'])
            self.assertEqual(hashlib.sha1(b'blob ' + str(len(image_bytes)).encode() + b'\0' + image_bytes).hexdigest(), stage['image']['source_blob_sha1'])
            self.assertEqual(grid_digest(stage), calibration['grid_sha256'])
            level = ROOT / '.cache/game-data/levels' / stage['level_source']['url'].split('/gamedata/levels/')[1]
            self.assertEqual(digest(level), binding['level_sha256'])
            self.assertEqual(level.stat().st_size, stage['level_source']['bytes'])
            raw = read(level)['mapData']
            self.assertEqual(raw['map'], stage['map'])
            self.assertEqual(raw['tiles'], stage['tiles'])
            self.assertIsNotNone(self.load(stage))

    def test_normal_emergency_aliases_share_only_exact_bound_image_and_grid(self):
        for normal, urgent in (NEW[:2], NEW[2:]):
            n, e = (battle_data()['stages'][s] for s in (normal, urgent))
            self.assertEqual(n['image']['sha256'], e['image']['sha256'])
            self.assertEqual(grid_digest(n), grid_digest(e))
            self.assertEqual(self.load(n), self.load(e))
            wrong = copy.deepcopy(e)
            wrong['image']['file'] = n['image']['file']
            self.assertIsNone(self.load(wrong))

    def test_stale_image_level_size_grid_and_unknown_alias_cannot_inherit_projection(self):
        for sid in NEW:
            stage = battle_data()['stages'][sid]
            self.assertIsNone(self.load(stage, sha='f' * 64))
            self.assertIsNone(self.load(stage, size=(511, 286)))
            wrong = copy.deepcopy(stage)
            wrong['level_source']['sha256'] = 'stale'
            self.assertIsNone(self.load(wrong))
            wrong = copy.deepcopy(stage)
            wrong['tiles'][wrong['map'][1][4]]['heightType'] = 'changed'
            self.assertIsNone(self.load(wrong))
            wrong = copy.deepcopy(stage)
            wrong['id'] = 'unverified-alias'
            self.assertIsNone(self.load(wrong))

    def test_three_failed_initial_probes_and_prior_failures_are_retained(self):
        self.assertEqual(len(self.inputs['rejected_probes']), 3)
        for record in self.inputs['rejected_probes']:
            path = ROOT / record['file']
            self.assertEqual(digest(path), record['sha256'])
            probe = read(path)
            self.assertFalse(record['accepted_for_runtime'])
            self.assertFalse(probe['accepted'])
            self.assertEqual(probe['pixel_tolerance'], 4)
            self.assertGreater(max(c['error_px'] for c in probe['checks']), 4)
            self.assertIsNone(self.load(battle_data()['stages'][probe['input']['id']]))
        old_input = read(ROOT / '.cache/research/map-projection-049/calibration-input.json')
        for record in old_input['rejected_probes']:
            self.assertEqual(digest(ROOT / record['file']), record['sha256'])
            sid = read(ROOT / record['file'])['input']['id']
            self.assertNotIn(sid, self.candidate['stages'])

    def test_upper_patch_calibration_does_not_claim_unmeasured_lateral_or_elevated_accuracy(self):
        calibration = self.candidate['calibrations']['ro6_n_5_7']
        self.assertEqual({p['row'] for p in calibration['checks']}, {1, 2, 3})
        self.assertEqual({p['col'] for p in calibration['checks']}, {4, 5, 6, 8, 9})
        self.assertNotIn((2, 6), {(p['row'], p['col']) for p in calibration['checks']})
        self.assertIn('lower and far-right extrapolation is not independently measured', calibration['grid_correspondence'])
        self.assertIn('do not establish whole-map accuracy', calibration['scope'])
        self.assertIn('elevated surfaces', calibration['scope'])
        self.assertIn('actual spawn offsets', calibration['scope'])

    def test_visible_projected_nominal_centers_invert_to_the_same_cell(self):
        for sid in NEW:
            stage = battle_data()['stages'][sid]
            projection = self.load(stage)
            for row, line in enumerate(stage['map']):
                for col, _ in enumerate(line):
                    cell = {'row': row, 'col': col}
                    x, y = projection.project(cell)
                    if 0 <= x < projection.width and 0 <= y < projection.height:
                        self.assertEqual(projection.cell_at(x, y), cell)

    def test_readonly_rebuild_is_deterministic_and_does_not_modify_research_or_production(self):
        paths = [p for p in BASE.iterdir() if p.is_file()]
        paths.append(DATA / 'battle-map-projections.json')
        before = {p: digest(p) for p in paths}
        output, receipt = build(write=False)
        self.assertEqual(output, self.candidate)
        self.assertFalse(receipt['implemented'])
        self.assertFalse(receipt['candidate_written'])
        self.assertEqual(receipt['output_sha256'], digest(BASE / 'battle-map-projections-candidate.json'))
        self.assertEqual(receipt['new_independent_checks'], 29)
        self.assertEqual(receipt['new_checks_by_stage'], self.receipt['new_checks_by_stage'])
        self.assertEqual({p: digest(p) for p in paths}, before)


if __name__ == '__main__':
    unittest.main()
