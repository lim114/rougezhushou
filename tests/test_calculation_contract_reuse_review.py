from unittest import TestCase
from rouge import panel_native_bridge as bridge
from rouge.calibration_experiment import calibration_experiment, public_experiment_payload


class CalculationContractReuseTests(TestCase):
    def test_explicit_unknown_basis_remains_unknown(self):
        row = bridge._record('normal', 'attack', None, bridge._term(None))
        self.assertIsNone(row['basis_single_bits'])
        self.assertIsNone(row['model_value'])

    def test_missing_or_empty_internal_term_is_not_synthesized(self):
        with self.assertRaises(TypeError):
            bridge._record('normal', 'attack', 1)
        with self.assertRaises(KeyError):
            bridge._record('normal', 'attack', 1, {})

    def test_public_experiment_rejects_bad_record_structure_and_values(self):
        for data in (None, {}, {'scenario': {}, 'observation': None}):
            payload = public_experiment_payload()
            payload['experiment']['records'][0]['data'] = data
            result = calibration_experiment(**payload)
            self.assertEqual(result['records'][0]['state'], 'blocked')
        for values in (None, {}, []):
            payload = public_experiment_payload()
            payload['experiment']['records'][0]['data']['observation']['values'] = values
            result = calibration_experiment(**payload)
            self.assertEqual(result['records'][0]['state'], 'blocked')
