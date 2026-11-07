from unittest import TestCase
from unittest.mock import patch
from rouge import cultivation_comparison as model
from tests.test_cultivation_comparison_140 import proposal


class CultivationResultBoundaryTests(TestCase):
    def test_supplemental_preparation_defect_is_not_a_skill_condition(self):
        with patch.object(model, '_cultivated_stats', side_effect=ValueError('skill preparation defect')):
            with self.assertRaisesRegex(ValueError, 'skill preparation defect'):
                model.compare_cultivation({'operator':'char_208_melan','skill_rank':7},
                                          {'proposals':[proposal('基础')]})

    def test_missing_internal_attribute_is_exposed_for_later_proposal(self):
        original=model._attribute_values
        calls=[]
        def attributes(*args,**kwargs):
            result,module,applied=original(*args,**kwargs)
            calls.append(result)
            if len(calls)==2:del result['attack']
            return result,module,applied
        with patch.object(model,'_attribute_values',side_effect=attributes):
            with self.assertRaisesRegex(KeyError,'attack'):
                model.compare_cultivation({'operator':'char_208_melan','skill_rank':7},
                    {'proposals':[proposal('基准'),proposal('另一方案')]})
        self.assertEqual(len(calls),2)

    def test_invalid_cultivation_remains_a_row_error(self):
        result=model.compare_cultivation({'operator':'char_208_melan','skill_rank':7},
            {'proposals':[proposal('基准'),proposal('无效等级',level=10000)]})
        self.assertIsNotNone(result['rows'][0]['attributes'])
        self.assertEqual(result['rows'][1]['status'],'不可测算')
        self.assertIsNone(result['rows'][1]['attributes'])

    def test_internal_attribute_errors_are_not_proposal_errors(self):
        original=model._attribute_values
        for error_type in (KeyError,TypeError,ValueError):
            with self.subTest(error_type=error_type):
                count=0
                def attributes(*args,**kwargs):
                    nonlocal count
                    count+=1
                    if count==2:raise error_type('internal defect')
                    return original(*args,**kwargs)
                with patch.object(model,'_attribute_values',side_effect=attributes):
                    with self.assertRaisesRegex(error_type,'internal defect'):
                        model.compare_cultivation({'operator':'char_208_melan','skill_rank':7},
                            {'proposals':[proposal('基准'),proposal('其它')]})

    def test_declared_cultivation_errors_still_have_row_messages(self):
        invalid=({'elite':True},{'level':0},{'trust':True},{'potential':0},
                 {'module_id':'missing','module_level':1},{'module_level':1})
        result=model.compare_cultivation({'operator':'char_208_melan','skill_rank':7},
            {'proposals':[proposal('基准')]+[proposal(str(i),**values) for i,values in enumerate(invalid)]})
        for row in result['rows'][1:]:
            self.assertEqual(row['status'],'不可测算')
            self.assertTrue(row['error'])
