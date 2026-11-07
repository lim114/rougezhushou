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

    def test_missing_model_context_is_an_internal_failure(self):
        from rouge import calibration
        payload=model.public_experiment_payload()
        real=calibration.panel_layers;count=0
        def panel(scenario):
            nonlocal count
            count+=1
            result=real(scenario)
            if count==2:result.pop('context')
            return result
        with patch.object(calibration,'panel_layers',side_effect=panel):
            with self.assertRaises(KeyError):model.calibration_experiment(**payload)

    def test_bad_scenario_stays_a_record_error_without_losing_other_records(self):
        payload=model.public_experiment_payload()
        payload['experiment']['records'][0]['data']['scenario']=None
        report=model.calibration_experiment(**payload)
        self.assertIn('record_validation_error',report['records'][0]['blocking_reasons'])
        self.assertEqual(report['records'][1]['state'],'evaluable')

    def test_panel_comparison_internal_errors_are_not_record_errors(self):
        from rouge import calibration
        payload=model.public_experiment_payload()
        for error in (ValueError('comparison defect'),TypeError('comparison defect'),KeyError('comparison defect')):
            with self.subTest(error=type(error).__name__),patch.object(calibration,'_compare_prediction',side_effect=error):
                with self.assertRaises(type(error)):model.calibration_experiment(**payload)

    def test_bad_panel_identity_and_number_remain_record_errors(self):
        payload=model.public_experiment_payload()
        observation=payload['experiment']['records'][0]['data']['observation']
        observation['panel']=[]
        result=model.calibration_experiment(**payload)
        self.assertIn('record_validation_error',result['records'][0]['blocking_reasons'])
        self.assertEqual(result['records'][1]['state'],'evaluable')

    def test_timing_computation_errors_escape_input_handler(self):
        from rouge import bounded_calibration as bounded
        payload=model.public_experiment_payload('mechanist','timing')
        for error in (ValueError('interval defect'),TypeError('interval defect'),KeyError('interval defect'),IndexError('interval defect'),OverflowError('interval defect')):
            with self.subTest(error=type(error).__name__),patch.object(bounded._OrderBounds,'difference',side_effect=error):
                with self.assertRaises(type(error)):model.calibration_experiment(**payload)

    def test_malformed_order_endpoint_stays_record_error(self):
        payload=model.public_experiment_payload('mechanist','timing')
        observation=payload['experiment']['records'][0]['data']['observation']
        observation['ordering_protocol']='explicit_constraints'
        observation['ordering_constraints']=[{'before':[],'after':'deployment','strict':False}]
        report=model.calibration_experiment(**payload)
        self.assertIn('record_validation_error',report['records'][0]['blocking_reasons'])
        self.assertEqual(report['records'][1]['state'],'evaluable')
