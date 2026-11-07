from unittest import TestCase
from unittest.mock import patch
from rouge import supplemental_cultivation as model,supplemental_run as run,supplemental_skills as skills
from rouge.catalog import CultivationInputError
from tests.test_supplemental_run_141 import environment


class SupplementalCultivationBoundaryTests(TestCase):
    def test_frozen_baseline_reused_only_for_same_typed_training_and_source(self):
        from rouge.supplemental_run import run_skill_reference
        from copy import deepcopy
        preview = skills.defaults()
        env = environment()
        env['operator_metadata'][preview['operator']] = {'recruitment_kind': 'non_emergency'}
        opened = run_skill_reference(preview, env)
        same = model.cultivation_defaults(preview, env)['proposals'][0]
        choices = {'proposals': [same, {**same, 'name':'来源变化', 'recruitment_kind':'emergency_hire'},
                                 {**same, 'name':'错误潜能', 'potential':True}]}
        with patch.object(model, '_run_inputs', wraps=model._run_inputs) as bind, patch.object(
                model, '_calculate_run_skill', wraps=model._calculate_run_skill) as calculate:
            report = model._compare_cultivation(preview, env, choices, baseline=opened)
        bind.assert_called_once()
        calculate.assert_called_once()
        first, second, bad = report['variants']
        self.assertEqual(first['result'], opened)
        self.assertEqual(second['result'], run_skill_reference(preview, second['environment']))
        self.assertIsNone(bad['result'])
        before = deepcopy(opened)
        first['result']['rows'].clear()
        self.assertEqual(report['baseline'], before)
        self.assertEqual(opened, before)

    def test_strict_training_keeps_exact_integers_and_catalog_keeps_legacy_inputs(self):
        from rouge.catalog import operator_attributes
        class TrainedInt(int):
            pass
        preview = skills.defaults()
        for field in ('elite','level','potential'):
            with self.subTest(field=field), self.assertRaisesRegex(CultivationInputError, field + '需要整数'):
                skills._cultivated_stats({**preview, field:TrainedInt(preview[field])})
        with self.assertRaisesRegex(CultivationInputError, 'level需要整数'):
            skills._cultivated_stats({**preview, 'level':None})
        self.assertEqual(operator_attributes(preview['operator'], TrainedInt(1), None, True),
                         operator_attributes(preview['operator'], 1, None, 1))

    def test_bad_cultivation_is_local_to_proposal(self):
        for field,value in [('elite',False),('level','55'),('level',999),('potential',7),('trust',False),('trust',10**1000)]:
            preview=skills.defaults();choices=model.cultivation_defaults(preview,environment())
            choices['proposals'][1][field]=value
            with self.subTest(field=field,value_type=type(value).__name__):
                result=model.compare_cultivation(preview,environment(),choices)
                self.assertIsNone(result['variants'][1]['result'])
                self.assertTrue(result['variants'][1]['error'])
                self.assertIsNotNone(result['variants'][2]['result'])

    def test_internal_calculation_errors_are_not_invalid_rows(self):
        preview=skills.defaults();choices=model.cultivation_defaults(preview,environment())
        real=model._calculate_run_skill
        for error in (ValueError('internal'),TypeError('internal'),KeyError('internal')):
            count=0
            def calculate(p,e,stats,inputs):
                nonlocal count
                count+=1
                if count==1:return real(p,e,stats,inputs)
                raise error
            with self.subTest(error=type(error).__name__),patch.object(model,'_calculate_run_skill',side_effect=calculate):
                with self.assertRaises(type(error)):model.compare_cultivation(preview,environment(),choices)

    def test_attribute_implementation_error_is_not_relabelled(self):
        with patch.object(skills,'_attribute_values',side_effect=ValueError('attribute implementation')):
            with self.assertRaises(ValueError) as caught:skills._cultivated_stats(skills.defaults())
        self.assertNotIsInstance(caught.exception,CultivationInputError)

    def test_known_hp_deficit_remains_a_proposal_error(self):
        preview=skills.defaults('char_209_ardign');choices=model.cultivation_defaults(preview,environment())
        real=model._calculate_run_skill;count=0
        def calculate(p,e,stats,inputs):
            nonlocal count
            count+=1
            if count==2:raise skills.MissingHpExceedsMaximum('known deficit')
            return real(p,e,stats,inputs)
        with patch.object(model,'_calculate_run_skill',side_effect=calculate):
            result=model.compare_cultivation(preview,environment(),choices)
        self.assertIn('known deficit',result['variants'][0]['error'])
        self.assertIsNotNone(result['variants'][1]['result'])
