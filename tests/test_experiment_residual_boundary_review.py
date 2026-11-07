from unittest import TestCase
from unittest.mock import patch
from rouge import calibration_experiment as model


class ExperimentResidualBoundaryTests(TestCase):
    def test_internal_residual_errors_escape_record_input_handler(self):
        payload=model.public_experiment_payload()
        for error in (ValueError('residual defect'),TypeError('residual defect'),KeyError('residual defect'),IndexError('residual defect'),OverflowError('residual defect')):
            with self.subTest(error=type(error).__name__),patch.object(model,'_residual',side_effect=error):
                with self.assertRaises(type(error)):
                    model.calibration_experiment(**payload)

    def test_bad_reading_stays_blocked_and_never_reaches_residual(self):
        payload=model.public_experiment_payload()
        for record in payload['experiment']['records']:
            record['data']['observation']['values']['attack']=[2,1]
        with patch.object(model,'_residual') as residual:
            result=model.calibration_experiment(**payload)
        residual.assert_not_called()
        self.assertEqual(result['training_state'],'blocked')
        for row in result['records']:
            self.assertIn('record_validation_error',row['blocking_reasons'])
            self.assertIsNone(row['residual_interval'])
