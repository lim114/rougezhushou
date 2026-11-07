from unittest import TestCase
from unittest.mock import patch
from rouge import supplemental_cultivation as model,supplemental_run as run,supplemental_skills as skills
from rouge.catalog import CultivationInputError
from tests.test_supplemental_run_141 import environment


class SupplementalCultivationBoundaryTests(TestCase):
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
        real=model.run_skill_reference
        for error in (ValueError('internal'),TypeError('internal'),KeyError('internal')):
            count=0
            def calculate(p,e):
                nonlocal count
                count+=1
                if count==1:return real(p,e)
                raise error
            with self.subTest(error=type(error).__name__),patch.object(model,'run_skill_reference',side_effect=calculate):
                with self.assertRaises(type(error)):model.compare_cultivation(preview,environment(),choices)

    def test_attribute_implementation_error_is_not_relabelled(self):
        with patch.object(skills,'operator_attributes',side_effect=ValueError('attribute implementation')):
            with self.assertRaises(ValueError) as caught:skills._cultivated_stats(skills.defaults())
        self.assertNotIsInstance(caught.exception,CultivationInputError)

    def test_known_hp_deficit_remains_a_proposal_error(self):
        preview=skills.defaults('char_209_ardign');choices=model.cultivation_defaults(preview,environment())
        real=model.run_skill_reference;count=0
        def calculate(p,e):
            nonlocal count
            count+=1
            if count==2:raise skills.MissingHpExceedsMaximum('known deficit')
            return real(p,e)
        with patch.object(model,'run_skill_reference',side_effect=calculate):
            result=model.compare_cultivation(preview,environment(),choices)
        self.assertIn('known deficit',result['variants'][0]['error'])
        self.assertIsNotNone(result['variants'][1]['result'])
