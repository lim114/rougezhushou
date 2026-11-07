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
        real=calibration._panel_snapshot;count=0
        def panel(*args):
            nonlocal count
            count+=1
            result=real(*args)
            if count==2:result.pop('context')
            return result
        with patch.object(calibration,'_panel_snapshot',side_effect=panel):
            with self.assertRaises(KeyError):model.calibration_experiment(**payload)

    def test_missing_calculated_panel_field_is_an_internal_failure(self):
        from rouge import calibration
        payload = model.public_experiment_payload()
        calculate = calibration._calculate_prepared
        def missing_field(scenario, prepared):
            result = calculate(scenario, prepared)
            if scenario['level'] == 75:
                del result['estimate']['base_stats']
            return result
        with patch.object(calibration, '_calculate_prepared', side_effect=missing_field):
            with self.assertRaisesRegex(KeyError, 'base_stats'):
                model.calibration_experiment(**payload)

    def test_corrupt_cultivation_source_is_not_a_record_error(self):
        from rouge import calibration
        payload = model.public_experiment_payload()
        original = calibration._cultivated
        for fault in (KeyError, IndexError, ValueError):
            def broken(scenario, **overrides):
                if scenario.get('level') == 75:
                    raise fault('cultivation defect')
                return original(scenario, **overrides)
            with self.subTest(fault=fault), patch.object(calibration, '_cultivated', side_effect=broken):
                with self.assertRaisesRegex(fault, 'cultivation defect'):
                    model.calibration_experiment(**payload)

    def test_skill_selection_separates_bad_input_from_internal_defects(self):
        from rouge import damage
        payload = model.public_experiment_payload()
        selected = damage._damage_selection
        for kind in (ValueError, TypeError, KeyError, IndexError, OverflowError):
            def broken(scenario, cultivated):
                if scenario['level'] == 75:
                    raise kind('skill selection defect')
                return selected(scenario, cultivated)
            with self.subTest(kind=kind), patch.object(damage, '_damage_selection', side_effect=broken):
                with self.assertRaisesRegex(kind, 'skill selection defect'):
                    model.calibration_experiment(**payload)
        payload['experiment']['records'][0]['data']['scenario']['skill'] = False
        report = model.calibration_experiment(**payload)
        self.assertIn('record_validation_error', report['records'][0]['blocking_reasons'])
        self.assertEqual(report['records'][1]['state'], 'evaluable')

    def test_run_resolution_source_defects_escape_but_bad_conditions_only_block_one_row(self):
        from rouge import run_modifiers
        payload = model.public_experiment_payload()
        original = run_modifiers._run_settings
        for fault in (KeyError, IndexError, ValueError, OverflowError):
            def broken(scenario, difficulty_reference):
                if scenario.get('level') == 75:
                    raise fault('missing run source')
                return original(scenario, difficulty_reference)
            with self.subTest(fault=fault), patch.object(run_modifiers, '_run_settings', side_effect=broken):
                with self.assertRaisesRegex(fault, 'missing run source'):
                    model.calibration_experiment(**payload)
        squad = next(iter(run_modifiers.config_data()['squads']))
        for change in ({'run_config': {'squad': []}},
                       {'effects': None, 'run_config': {'squad': {'id': squad, 'effect_verified': True}}},
                       {'target_enemy': {'stage_id': [], 'enemy_id': 'unknown', 'level': 0}}):
            payload['experiment']['records'][0]['data']['scenario'] = {'operator': 'mechanist', **change}
            report = model.calibration_experiment(**payload)
            self.assertIn('record_validation_error', report['records'][0]['blocking_reasons'])
            self.assertEqual(report['records'][1]['state'], 'evaluable')

    def test_enemy_resolution_structure_errors_still_reach_the_caller(self):
        from rouge import enemy_environment
        payload = model.public_experiment_payload()
        payload['experiment']['records'][1]['data']['scenario']['target_enemy'] = {'stage_id': 'ro6_n_1_1'}
        original = enemy_environment._resolve_target
        for fault in (KeyError, IndexError, TypeError, ValueError, OverflowError):
            def broken(scenario, resolution, target, **options):
                if scenario.get('level') == 75:
                    raise fault('invalid enemy source')
                return original(scenario, resolution, target, **options)
            with self.subTest(fault=fault), patch.object(enemy_environment, '_resolve_target', side_effect=broken):
                with self.assertRaisesRegex(fault, 'invalid enemy source'):
                    model.calibration_experiment(**payload)

    def test_damaged_fixed_enemy_panel_is_not_an_invalid_experiment_record(self):
        from rouge import enemy_panel
        payload = model.public_experiment_payload()
        target = {'stage_id':'ro6_n_1_1', 'enemy_id':'enemy_2001_duckmi', 'level':0}
        payload['experiment']['records'][0]['data']['scenario']['target_enemy'] = target
        with patch.object(enemy_panel, 'enemy_panel_reference', side_effect=ValueError('bad fixed panel')) as read:
            with self.assertRaisesRegex(ValueError, 'bad fixed panel'):
                model.calibration_experiment(**payload)
            read.assert_called_once_with(target['stage_id'], target['enemy_id'], target['level'])

    def test_invalid_stage_id_and_orb_mode_only_block_their_record(self):
        from rouge.enemy_environment import EnemyReferenceError
        from rouge.run_modifiers import prepare_run
        for field in ('stage_id', 'orb_mode'):
            for invalid in ([], {}):
                target = {'stage_id': 'ro6_b_5', 'enemy_id': 'enemy_2148_shorbb', 'level': 0, field: invalid}
                with self.subTest(field=field, value=invalid):
                    with self.assertRaises(EnemyReferenceError) as caught:
                        prepare_run({'target_enemy': target})
                    payload = model.public_experiment_payload()
                    payload['experiment']['records'][0]['data']['scenario']['target_enemy'] = target
                    result = model.calibration_experiment(**payload)
                    self.assertEqual(result['records'][0]['validation_error'], str(caught.exception))
                    self.assertEqual(result['records'][1]['state'], 'evaluable')

    def test_bad_trust_blocks_only_its_own_record(self):
        for trust in ('100', None, {}, 10**1000, -1):
            payload = model.public_experiment_payload()
            payload['experiment']['records'][0]['data']['scenario']['trust'] = trust
            report = model.calibration_experiment(**payload)
            self.assertIn('record_validation_error', report['records'][0]['blocking_reasons'])
            self.assertEqual(report['records'][1]['state'], 'evaluable')

    def test_unknown_skill_attack_has_no_numeric_delta(self):
        from rouge import calibration
        scenario = calibration._scenario({'operator': 'mechanist'})
        cult = calibration._cultivated(scenario)
        prepared = calibration._prepare_damage(scenario, cultivated_attributes=cult)
        from copy import deepcopy
        calculation = calibration._calculate_prepared(scenario, deepcopy(prepared))
        calculation['estimate']['skill']['skill_attack'] = None
        snapshot = calibration._panel_snapshot(*calibration._panel_context(scenario), cult, prepared, calculation)
        attack = next(row for row in snapshot['rows'] if row['field'] == 'attack')
        self.assertIsNone(attack['stages'][-1]['value'])
        self.assertIsNone(attack['stages'][-1]['delta_from_previous'])
        self.assertIsNotNone(attack['stages'][-2]['value'])

    def test_invalid_operator_and_unencodable_condition_only_block_their_row(self):
        for change in ({'operator': []}, {'unused': float('nan')}):
            payload = model.public_experiment_payload()
            payload['experiment']['records'][0]['data']['scenario'].update(change)
            result = model.calibration_experiment(**payload)
            self.assertIn('record_validation_error', result['records'][0]['blocking_reasons'])
            self.assertEqual(result['records'][1]['state'], 'evaluable')

    def test_internal_context_or_normalization_failure_is_not_an_invalid_record(self):
        from rouge import calibration
        payload = model.public_experiment_payload()
        for name in ('_scenario', '_panel_context'):
            real = getattr(calibration, name)
            def broken(scenario, **kwargs):
                if scenario.get('level') == 75: raise KeyError('missing source field')
                return real(scenario, **kwargs)
            with self.subTest(name=name), patch.object(calibration, name, side_effect=broken):
                with self.assertRaisesRegex(KeyError, 'missing source field'):
                    model.calibration_experiment(**payload)

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
