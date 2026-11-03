"""Regression of floating replay without weakening source/gate constraints."""
import copy
import unittest

from scripts.map_fit_replay import REPLAY_EPSILON, canonical_inverse, verify_fit_replay


def original(error=1.0):
    return {'id': 'literal', 'accepted': error <= 4,
            'matrix': [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0],
            'checks': [{'row': 1, 'col': 2, 'observed_pixel': [10, 20],
                        'projected_pixel': [10.0, 20.0], 'error_px': error}]}


class MapFitReplayTests(unittest.TestCase):
    def test_permitted_leaf_drift_preserves_canonical_and_gate(self):
        frozen = original()
        current = copy.deepcopy(frozen)
        current['matrix'][0] += REPLAY_EPSILON / 2
        current['checks'][0]['projected_pixel'][0] += 5 * REPLAY_EPSILON
        result = verify_fit_replay(current, frozen)
        self.assertEqual(len(result['differing_computed_leaves']), 2)
        self.assertEqual(result['original_pixel_gate'], 4)
        self.assertTrue(result['qualification_and_source_structure_exact'])
        self.assertEqual(frozen, original())

    def test_drift_beyond_numerical_policy_rejected(self):
        for path in ('matrix', 'projection', 'error'):
            frozen = original()
            current = copy.deepcopy(frozen)
            if path == 'matrix':
                current['matrix'][1] = 2 * REPLAY_EPSILON
            elif path == 'projection':
                current['checks'][0]['projected_pixel'][0] += 30 * REPLAY_EPSILON
            else:
                current['checks'][0]['error_px'] += 2 * REPLAY_EPSILON
            with self.subTest(path=path), self.assertRaisesRegex(ValueError, 'exceeds'):
                verify_fit_replay(current, frozen)

    def test_pixel_gate_crossing_rejected_even_within_leaf_budget(self):
        frozen = original(4.0)
        current = copy.deepcopy(frozen)
        current['checks'][0]['error_px'] += REPLAY_EPSILON / 2
        current['accepted'] = False
        with self.assertRaisesRegex(ValueError, 'qualification'):
            verify_fit_replay(current, frozen)
        # Lying about the recomputed gate also fails before comparison.
        current['accepted'] = True
        with self.assertRaisesRegex(ValueError, '4px'):
            verify_fit_replay(current, frozen)

    def test_source_shapes_types_and_original_readings_are_exact(self):
        for mutation in ('source_pixel', 'identity', 'cell', 'type', 'shape', 'key'):
            frozen = original()
            current = copy.deepcopy(frozen)
            if mutation == 'source_pixel': current['checks'][0]['observed_pixel'][0] += 1
            elif mutation == 'identity': current['id'] = 'other'
            elif mutation == 'cell': current['checks'][0]['row'] += 1
            elif mutation == 'type': current['matrix'][0] = 1
            elif mutation == 'shape': current['matrix'].pop()
            else: current['extra'] = 0
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                verify_fit_replay(current, frozen)

    def test_nonfinite_computed_leaves_are_rejected(self):
        for bad in (float('nan'), float('inf'), -float('inf')):
            for path in ('matrix', 'projection', 'error'):
                current = original()
                if path == 'matrix': current['matrix'][0] = bad
                elif path == 'projection': current['checks'][0]['projected_pixel'][0] = bad
                else: current['checks'][0]['error_px'] = bad
                with self.subTest(path=path, bad=bad), self.assertRaises(ValueError):
                    verify_fit_replay(current, original())

    def test_inverse_verifies_then_returns_original_exact_values(self):
        frozen = original()['matrix']
        current = copy.deepcopy(frozen)
        current[0] += REPLAY_EPSILON / 2
        replayed = canonical_inverse(current, frozen)
        self.assertEqual(replayed, frozen)
        self.assertIsNot(replayed, frozen)
        current[0] += REPLAY_EPSILON * 4
        with self.assertRaisesRegex(ValueError, 'exceeds'):
            canonical_inverse(current, frozen)
