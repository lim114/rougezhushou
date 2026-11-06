import unittest
from copy import deepcopy
from rouge import susuro_healing,guardian_healing

FIELDS=('total_healing','phase_healing','window_healing','cycle_healing','cycle_hps','window_hps')


class HealingResultContractTests(unittest.TestCase):
    def test_missing_generated_fields_raise(self):
        for module in (susuro_healing,guardian_healing):
            for field in (*FIELDS,'top_total'):
                result={'estimate':{'notes':[],'skill':dict.fromkeys(FIELDS,0),'complete':True},'total_healing':0,'complete':True}
                if field=='top_total':del result['total_healing']
                else:del result['estimate']['skill'][field]
                with self.subTest(module=module.__name__,field=field):
                    with self.assertRaises(KeyError):
                        module.attach_result(result,{'qualified':None,'comparison':'LT','operator_name':'古米'})

    def test_unknown_and_zero_retained_positive_subtotals_preserved(self):
        values=dict(zip(FIELDS,(100,0,None,200,5,None)))
        for module in (susuro_healing,guardian_healing):
            result={'estimate':{'notes':[],'skill':deepcopy(values),'complete':True},'total_healing':100,'complete':True}
            module.attach_result(result,{'qualified':None,'comparison':'LT','operator_name':'古米'})
            self.assertEqual(result['known_healing_subtotals'],values)
            self.assertEqual(result['estimate']['skill'],dict(zip(FIELDS,(None,0,None,None,None,None))))
            self.assertIsNone(result['total_healing'])
            self.assertFalse(result['complete'])
            self.assertFalse(result['estimate']['complete'])
