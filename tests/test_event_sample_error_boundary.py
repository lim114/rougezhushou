import unittest
from unittest.mock import patch
from rouge import public_event_samples as model


class EventSampleBoundaryTests(unittest.TestCase):
    def test_input_errors_remain_unavailable(self):
        with patch.object(model, 'map_conditions', return_value={'floor': 1, 'special_region': False}):
            for error in (OSError, ValueError):
                with self.subTest(error=error), patch.object(model, 'samples', side_effect=error('bad source')):
                    self.assertEqual(model.references({}), {})

    def test_internal_type_and_key_errors_surface(self):
        with patch.object(model, 'map_conditions', return_value={'floor': 1, 'special_region': False}):
            for error in (TypeError, KeyError):
                with self.subTest(error=error), patch.object(model, 'samples', side_effect=error('internal')):
                    with self.assertRaises(error):
                        model.references({})

    def test_cohort_lookup_is_outside_input_catch(self):
        class BrokenCohorts:
            def get(self, *args):
                raise ValueError('internal lookup')
        with patch.object(model, 'map_conditions', return_value={'floor': 1, 'special_region': False}), patch.object(model, 'samples', return_value=({}, BrokenCohorts())):
            with self.assertRaisesRegex(ValueError, 'internal lookup'):
                model.references({})
