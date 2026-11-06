from unittest import TestCase
from unittest.mock import patch
from rouge import cultivation_comparison as model
from tests.test_cultivation_comparison_140 import proposal


class CultivationResultBoundaryTests(TestCase):
    def test_missing_internal_attribute_is_exposed_for_later_proposal(self):
        original=model._operator_attribute_reference
        calls=[]
        def attributes(*args,**kwargs):
            result,module,applied=original(*args,**kwargs)
            calls.append(result)
            if len(calls)==2:del result['attack']
            return result,module,applied
        with patch.object(model,'_operator_attribute_reference',side_effect=attributes):
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
