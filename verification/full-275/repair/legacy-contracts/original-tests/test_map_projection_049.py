"""Fixed ground references reject stale pixels, grids and unverified landmarks."""
import copy
import hashlib
import json
import math
import unittest
from pathlib import Path

from rouge.battle_preview import battle_data, DATA
from rouge.map_projection import grid_digest, projection_data, projection_for

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / '.cache/research/map-projection-049'
PRIOR = ROOT / '.cache/batch-049-before/rouge/data/battle-map-projections.json'
NEW = ('ro6_n_4_5', 'ro6_e_4_5', 'ro6_n_4_3', 'ro6_e_4_3')


def load(stage, sha=None, size=None):
    image = stage['image']
    return projection_for(stage, image['sha256'] if sha is None else sha,
                          (image['width'], image['height']) if size is None else size)


class GroundReferenceTests(unittest.TestCase):
    def test_prior_six_calibrations_twelve_bindings_thirty_four_checks_unchanged(self):
        prior = json.loads(PRIOR.read_text(encoding='utf-8'))
        current = projection_data()
        self.assertEqual(len(prior['calibrations']), 6)
        self.assertEqual(len(prior['stages']), 12)
        self.assertEqual(sum(len(c['checks']) for c in prior['calibrations'].values()), 34)
        for key, record in prior['calibrations'].items():
            self.assertEqual(current['calibrations'][key], record)
        for key, record in prior['stages'].items():
            self.assertEqual(current['stages'][key], record)

    def test_independent_checks_are_original_ground_centers_and_never_fit_inputs(self):
        inputs = json.loads((BASE / 'calibration-input.json').read_text(encoding='utf-8'))
        count = 0
        for entry in inputs['calibrations']:
            original = json.loads((BASE / (entry['id'] + '-fit.json')).read_text(encoding='utf-8'))['input']
            self.assertEqual(entry['anchors'], original['anchors'])
            self.assertEqual(entry['checks'], original['checks'])
            calibration = projection_data()['calibrations'][entry['id']]
            stage = battle_data()['stages'][entry['id']]
            anchors = {(r, c) for r, c, *_ in entry['anchors']}
            for check in calibration['checks']:
                cell = (check['row'], check['col'])
                self.assertNotIn(cell, anchors)
                tile = stage['tiles'][stage['map'][cell[0]][cell[1]]]
                self.assertEqual((tile['tileKey'], tile['heightType']), ('tile_floor', 'LOWLAND'))
                self.assertLessEqual(math.dist(load(stage).project(check), check['observed_pixel']), 4)
                count += 1
        self.assertEqual(count, 15)

    def test_actual_pinned_images_levels_and_grids_match_every_new_binding(self):
        for sid in NEW:
            stage = battle_data()['stages'][sid]
            c = projection_data()['calibrations'][projection_data()['stages'][sid]['calibration']]
            self.assertEqual(hashlib.sha256((DATA / stage['image']['file']).read_bytes()).hexdigest(), c['bitmap_sha256'])
            self.assertEqual(grid_digest(stage), c['grid_sha256'])
            level = ROOT / '.cache/game-data/levels' / stage['level_source']['url'].split('/gamedata/levels/')[1]
            self.assertEqual(hashlib.sha256(level.read_bytes()).hexdigest(), stage['level_source']['sha256'])
            raw = json.loads(level.read_text(encoding='utf-8'))['mapData']
            self.assertEqual(raw['map'], stage['map'])
            self.assertEqual(raw['tiles'], stage['tiles'])
            self.assertIsNotNone(load(stage))

    def test_normal_emergency_share_only_exact_bitmap_grid_and_level(self):
        for normal, urgent in (NEW[:2], NEW[2:]):
            n, e = (battle_data()['stages'][s] for s in (normal, urgent))
            self.assertEqual(n['image']['sha256'], e['image']['sha256'])
            self.assertEqual(grid_digest(n), grid_digest(e))
            self.assertEqual(load(n), load(e))
            wrong = copy.deepcopy(e)
            wrong['image']['file'] = n['image']['file']
            self.assertIsNone(load(wrong))

    def test_stale_level_image_size_and_tile_semantics_do_not_inherit(self):
        for sid in NEW:
            stage = battle_data()['stages'][sid]
            self.assertIsNone(load(stage, sha='f' * 64))
            self.assertIsNone(load(stage, size=(511, 286)))
            wrong = copy.deepcopy(stage)
            wrong['level_source']['sha256'] = 'stale-level'
            self.assertIsNone(load(wrong))
            wrong = copy.deepcopy(stage)
            wrong['tiles'][wrong['map'][1][5]]['heightType'] = 'changed'
            self.assertIsNone(load(wrong))
            wrong = copy.deepcopy(stage)
            wrong['id'] = 'unverified-alias'
            self.assertIsNone(load(wrong))

    def test_failed_readings_retained_without_relaxed_pixel_gate(self):
        inputs = json.loads((BASE / 'calibration-input.json').read_text(encoding='utf-8'))
        self.assertEqual(inputs['pixel_tolerance'], 4)
        self.assertEqual(len(inputs['rejected_probes']), 2)
        for record in inputs['rejected_probes']:
            path = ROOT / record['file']
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), record['sha256'])
            probe = json.loads(path.read_text(encoding='utf-8'))
            self.assertFalse(record['accepted_for_runtime'])
            self.assertFalse(probe['accepted'])
            self.assertGreater(max(c['error_px'] for c in probe['checks']), 4)
            self.assertIsNone(load(battle_data()['stages'][probe['input']['id']]))

    def test_single_column_ground_holds_do_not_claim_lateral_or_elevated_accuracy(self):
        c = projection_data()['calibrations']['ro6_n_4_3']
        self.assertEqual({p['col'] for p in c['checks']}, {5})
        self.assertIn('lateral extrapolation is not independently measured', c['grid_correspondence'])
        self.assertIn('do not establish whole-map accuracy', c['scope'])
        self.assertIn('elevated surfaces', c['scope'])
        self.assertIn('actual spawn offsets', c['scope'])

    def test_visible_projected_nominal_centers_invert_to_the_same_cell(self):
        for sid in NEW:
            stage = battle_data()['stages'][sid]
            projection = load(stage)
            for row, line in enumerate(stage['map']):
                for col, _ in enumerate(line):
                    cell = {'row': row, 'col': col}
                    x, y = projection.project(cell)
                    if 0 <= x < projection.width and 0 <= y < projection.height:
                        self.assertEqual(projection.cell_at(x, y), cell)


if __name__ == '__main__':
    unittest.main()
