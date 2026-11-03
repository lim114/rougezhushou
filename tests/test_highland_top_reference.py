"""Separate upper-surface identity gates and explicit-selection prototype flow."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import unittest

from rouge.battle_preview import DATA, battle_data
from rouge.fixed_landmark_mapping import landmark_data
from rouge.map_projection import projection_data
from rouge.highland_top_mapping import highland_top_data, highland_top_reference_for
from scripts.build_highland_top_references import BASE, build


class HighlandTopCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.candidate, cls.receipt = build()

    def reference(self, stage, candidate=None):
        image = stage['image']
        return highland_top_reference_for(stage, image['sha256'], (image['width'], image['height']),
                                         self.candidate if candidate is None else candidate)

    def test_only_four_independently_agreed_tops_one_image_and_exact_two_variants(self):
        self.assertEqual(self.receipt['requested_points'], 18)
        self.assertEqual(self.receipt['accepted_unique_image_top_cells'], 4)
        self.assertEqual(self.receipt['rejected_or_unknown_points'], 14)
        self.assertEqual(set(self.candidate['references']), {'ro6_n_4_1'})
        self.assertEqual(set(self.candidate['stages']), {'ro6_n_4_1', 'ro6_e_4_1'})
        for sid in ('ro6_n_2_4', 'ro6_e_2_4'):
            self.assertIsNone(self.reference(battle_data()['stages'][sid]))
        self.assertEqual(self.receipt['complete_map_calibration_added'], 0)
        self.assertEqual(highland_top_data(), self.candidate)
        for key in ('lowland_references_modified', 'ground_projection', 'inverse', 'footpoints', 'spawn_positions', 'checkpoint_connections'):
            self.assertFalse(self.receipt[key])

    def test_all_unobserved_and_fractional_cells_have_no_top_and_no_ground_projection_api(self):
        stage = battle_data()['stages']['ro6_n_4_1']; reference = self.reference(stage)
        known = {(row, col): (x, y) for row, col, x, y in reference.points}
        self.assertEqual(set(known), {(1, 3), (2, 3), (2, 7), (2, 8)})
        for r, line in enumerate(stage['map']):
            for c, _ in enumerate(line):
                self.assertEqual(reference.top_center({'row': r, 'col': c}), known.get((r, c)))
        for row, col in known:
            for value in (row + .1, float(row), True, None):
                self.assertIsNone(reference.top_center({'row': value, 'col': col}))
        self.assertFalse(reference.supports_segment_reference)
        self.assertFalse(reference.supports_inverse_reference)
        self.assertFalse(reference.supports_spawn_reference)
        self.assertFalse(hasattr(reference, 'project'))
        self.assertFalse(hasattr(reference, 'cell_at'))

    def test_bitmap_path_dimensions_level_grid_tile_kind_height_and_surface_schema_are_strict(self):
        for sid in self.candidate['stages']:
            stage = battle_data()['stages'][sid]
            self.assertIsNotNone(self.reference(stage))
            for kind in ('id', 'file', 'level', 'dimensions', 'tile', 'height'):
                bad = copy.deepcopy(stage)
                if kind == 'id': bad['id'] = 'unmeasured-similar-map'
                elif kind == 'file': bad['image']['file'] = 'other-file.png'
                elif kind == 'level': bad['level_source']['sha256'] = 'other-level'
                elif kind == 'dimensions': bad['image']['width'] += 1
                else: bad['tiles'][bad['map'][1][3]]['tileKey' if kind == 'tile' else 'heightType'] = 'tile_floor' if kind == 'tile' else 'LOWLAND'
                self.assertIsNone(self.reference(bad), (sid, kind))
        stage = battle_data()['stages']['ro6_n_4_1']
        for field, value in [('surface_kind', 'ground'), ('tile_kind', 'tile_floor'), ('height_type', 'LOWLAND')]:
            bad = copy.deepcopy(self.candidate); bad['references']['ro6_n_4_1'][field] = value
            self.assertIsNone(self.reference(stage, bad))
        bad = copy.deepcopy(self.candidate); bad['format_version'] = True
        self.assertIsNone(self.reference(stage, bad))
        image = stage['image']
        self.assertIsNone(highland_top_reference_for(stage, 'f' * 64, (512, 286), self.candidate))

    def test_build_preserves_frozen_readings_and_leaves_runtime_lowland_and_planes_unchanged(self):
        source = json.loads((BASE / 'source-receipt.json').read_text())
        for name, digest in source['frozen_sha256'].items():
            self.assertEqual(hashlib.sha256((BASE / name).read_bytes()).hexdigest(), digest)
        paths = [BASE / name for name in source['frozen_sha256']]
        paths += [DATA / 'fixed-landmark-references.json', DATA / 'battle-map-projections.json']
        before = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}
        old_partial, old_planes = copy.deepcopy(landmark_data()), copy.deepcopy(projection_data())
        self.assertEqual(build(), (self.candidate, self.receipt))
        self.assertEqual({path: hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}, before)
        self.assertEqual(landmark_data(), old_partial); self.assertEqual(projection_data(), old_planes)


if __name__ == '__main__':
    unittest.main()
