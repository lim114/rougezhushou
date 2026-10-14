"""Ground-only landmarks never bless unrelated imagery or rendered entrances."""
import copy
import hashlib
import json
import math
import unittest
from pathlib import Path

from rouge.battle_preview import battle_data, DATA
from rouge.map_projection import grid_digest, projection_data, projection_for

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / '.cache/research/map-projection-048'
PRIOR = ROOT / '.cache/batch-048-before/rouge/data/battle-map-projections.json'
NEW = ('ro6_n_3_4', 'ro6_e_3_4', 'ro6_n_3_6', 'ro6_e_3_6')


def load(stage, sha=None, size=None):
    image = stage['image']
    return projection_for(stage, image['sha256'] if sha is None else sha,
                          (image['width'], image['height']) if size is None else size)


class GroundLandmarkTests(unittest.TestCase):
    def test_prior_four_calibrations_eight_bindings_twenty_checks_unchanged(self):
        prior = json.loads(PRIOR.read_text(encoding='utf-8'))
        current = projection_data()
        self.assertEqual(len(prior['calibrations']), 4)
        self.assertEqual(len(prior['stages']), 8)
        self.assertEqual(sum(len(c['checks']) for c in prior['calibrations'].values()), 20)
        for key, record in prior['calibrations'].items():
            self.assertEqual(current['calibrations'][key], record)
        for key, record in prior['stages'].items():
            self.assertEqual(current['stages'][key], record)

    def test_new_holdouts_are_ground_metal_centers_never_fit_inputs(self):
        inputs = json.loads((BASE / 'calibration-input.json').read_text(encoding='utf-8'))
        count = 0
        for entry in inputs['calibrations']:
            calibration = projection_data()['calibrations'][entry['id']]
            stage = battle_data()['stages'][entry['id']]
            anchors = {(r, c) for r, c, *_ in entry['anchors']}
            for check in calibration['checks']:
                cell = (check['row'], check['col'])
                self.assertNotIn(cell, anchors)
                tile = stage['tiles'][stage['map'][cell[0]][cell[1]]]
                self.assertEqual((tile['tileKey'], tile['heightType']), ('tile_floor', 'LOWLAND'))
                actual = load(stage).project(check)
                self.assertLessEqual(math.dist(actual, check['observed_pixel']), 4)
                count += 1
        self.assertEqual(count, 14)

    def test_new_check_readings_are_the_original_holdouts(self):
        original = json.loads((BASE / 'ro6_n_3_4-fit.json').read_text(encoding='utf-8'))['input']
        extra = json.loads((BASE / 'ro6_n_3_6-fit.json').read_text(encoding='utf-8'))['input']
        current = json.loads((BASE / 'calibration-input.json').read_text(encoding='utf-8'))['calibrations']
        self.assertEqual(current[0]['anchors'], original['anchors'])
        self.assertEqual(current[0]['checks'], original['checks'][:6])
        self.assertEqual(current[1]['checks'], extra['checks'])
        self.assertEqual(current[1]['anchors'][:6], extra['anchors'])

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

    def test_normal_emergency_share_only_exact_image_and_grid(self):
        for normal, urgent in (NEW[:2], NEW[2:]):
            n, e = (battle_data()['stages'][s] for s in (normal, urgent))
            self.assertEqual(n['image']['sha256'], e['image']['sha256'])
            self.assertEqual(grid_digest(n), grid_digest(e))
            self.assertEqual(load(n), load(e))
            wrong = copy.deepcopy(e)
            wrong['image']['file'] = n['image']['file']
            self.assertIsNone(load(wrong))

    def test_stale_level_image_pixels_and_tile_semantics_do_not_inherit(self):
        for sid in NEW:
            stage = battle_data()['stages'][sid]
            self.assertIsNone(load(stage, sha='f' * 64))
            self.assertIsNone(load(stage, size=(511, 286)))
            wrong = copy.deepcopy(stage)
            wrong['level_source']['sha256'] = 'older-level'
            self.assertIsNone(load(wrong))
            wrong = copy.deepcopy(stage)
            wrong['tiles'][wrong['map'][1][3]]['heightType'] = 'changed'
            self.assertIsNone(load(wrong))
            wrong = copy.deepcopy(stage)
            wrong['id'] = 'unknown-alias'
            self.assertIsNone(load(wrong))

    def test_unaccepted_wood_decorations_and_portal_probes_are_retained(self):
        for sid in ('ro6_n_2_3', 'ro6_n_2_4', 'ro6_t_1', 'ro6_n_3_5'):
            self.assertIsNone(load(battle_data()['stages'][sid]))
            rejected = json.loads((BASE / (sid + '-fit.json')).read_text(encoding='utf-8'))
            self.assertFalse(rejected['accepted'])
            self.assertGreater(max(c['error_px'] for c in rejected['checks']), 4)
        full = json.loads((BASE / 'ro6_n_3_4-fit.json').read_text(encoding='utf-8'))
        self.assertFalse(full['accepted'])
        self.assertGreater(full['checks'][-1]['error_px'], 8)
        verified = projection_data()['calibrations']['ro6_n_3_4']['checks']
        self.assertTrue(all('metal tile center' in p['cue'] for p in verified))
        self.assertIn('spawn offsets', projection_data()['calibrations']['ro6_n_3_4']['scope'])

    def test_all_new_visible_centers_invert_to_the_same_nominal_cell(self):
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
