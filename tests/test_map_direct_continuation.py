"""New direct map centers retain exact identity and deny uncovered positions."""
import copy
import hashlib
import json
import math
from pathlib import Path
import unittest
from unittest.mock import patch

from rouge.battle_preview import DATA, battle_data
from rouge.fixed_landmark_mapping import direct_reference_for
from rouge.map_projection import projection_data
from scripts.extend_map_direct_continuation import BASE, build


class MapDirectContinuationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.candidate, cls.receipt = build()

    def reference(self, stage):
        image = stage['image']
        with patch('rouge.fixed_landmark_mapping.landmark_data', return_value=self.candidate):
            return direct_reference_for(stage, image['sha256'], (image['width'], image['height']))

    def test_frozen_sources_readings_all_acceptance_and_unknowns_remain_auditable(self):
        self.assertEqual(self.receipt['new_requested_points'], 19)
        self.assertEqual(self.receipt['complete_calibration_added'], 0)
        self.assertFalse(self.receipt['absolute_position_accuracy_verified'])
        source = json.loads((BASE / 'source-receipt.json').read_text())
        for name, digest in source['frozen_sha256'].items():
            self.assertEqual(hashlib.sha256((BASE / name).read_bytes()).hexdigest(), digest)
        for row in self.receipt['new_agreement_comparisons']:
            one, two = row['observed_pixel'], row['independent_pixel']
            distance = math.dist(one, two) if one is not None and two is not None else None
            self.assertEqual(row['agreement_px'], distance)
            self.assertEqual(row['accepted_for_runtime'], distance is not None and distance <= 4)
            reference = self.reference(battle_data()['stages'][row['reference']])
            point = reference.project({'row': row['row'], 'col': row['col']}) if reference else None
            self.assertEqual(point, tuple(one) if row['accepted_for_runtime'] else None)
        self.assertTrue(any(row['observed_pixel'] is None for row in self.receipt['new_agreement_comparisons']))

    def test_prior_partial_and_plane_values_unchanged_and_candidate_build_is_readonly(self):
        prior = json.loads((BASE / 'prior-landmark-references.json').read_text())
        for group in ('references', 'stages'):
            for key, value in prior[group].items():
                self.assertEqual(self.candidate[group][key], value)
        planes = json.loads((BASE / 'prior-regular-projections.json').read_text())
        for group in ('calibrations', 'stages'):
            for key, value in planes[group].items():
                self.assertEqual(projection_data()[group][key], value)
        paths = [path for path in BASE.iterdir() if path.is_file()]
        paths += [DATA / 'fixed-landmark-references.json', DATA / 'battle-map-projections.json']
        before = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}
        self.assertEqual(build(), (self.candidate, self.receipt))
        self.assertEqual({path: hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}, before)

    def test_new_exact_aliases_block_fractional_unobserved_inverse_and_changed_identity(self):
        added = set(self.candidate['stages']) - set(json.loads((BASE / 'prior-landmark-references.json').read_text())['stages'])
        self.assertTrue(added)
        self.assertLessEqual(added, {'ro6_n_2_4', 'ro6_e_2_4', 'ro6_n_4_7', 'ro6_e_4_7'})
        for sid in added:
            stage = battle_data()['stages'][sid]
            reference = self.reference(stage)
            self.assertIsNotNone(reference)
            self.assertFalse(reference.supports_segment_reference)
            known = {(r, c): (x, y) for r, c, x, y in reference.points}
            for r, line in enumerate(stage['map']):
                for c, _ in enumerate(line):
                    self.assertEqual(reference.project({'row': r, 'col': c}), known.get((r, c)))
            for r, c, x, y in reference.points:
                self.assertIsNone(reference.cell_at(x, y))
                self.assertIsNone(reference.project({'row': r + .1, 'col': c}))
                self.assertIsNone(reference.project({'row': True, 'col': c}))
            for field in ('id', 'file', 'level', 'dimensions', 'surface'):
                damaged = copy.deepcopy(stage)
                if field == 'id':
                    damaged['id'] = 'similar-unbound-map'
                elif field == 'file':
                    damaged['image']['file'] = 'similar-image.png'
                elif field == 'level':
                    damaged['level_source']['sha256'] = 'different-original-level'
                elif field == 'dimensions':
                    damaged['image']['width'] += 1
                else:
                    r, c = next(iter(known))
                    damaged['tiles'][damaged['map'][r][c]]['heightType'] = 'HIGHLAND'
                self.assertIsNone(self.reference(damaged), (sid, field))


if __name__ == '__main__':
    unittest.main()
