import unittest
from rouge.catalog import catalog
from rouge.operator_engine import selected_talents
from rouge.mei_module_reference import reference as mei
from rouge.susuro_healing import selected_trait as susuro
from rouge.guardian_healing import selected_trait as guardian


class ReferenceLevelDefaultTests(unittest.TestCase):
    def cases(self):
        for fn, op, mod in ((selected_talents,'char_110_deepcl','uniequip_002_deepcl'),
                            (mei,'char_133_mm','uniequip_002_mm'),
                            (susuro,'char_298_susuro','uniequip_002_susuro'),
                            (guardian,'char_196_sunbr','uniequip_002_sunbr'),
                            (guardian,'char_2025_shu','uniequip_002_shu')):
            yield fn, catalog()['operators'][op], {'operator':op,'elite':2,'module_id':mod,'module_level':3}

    def test_only_missing_and_none_default(self):
        for fn, profile, scenario in self.cases():
            with self.subTest(fn=fn.__name__, operator=profile['id']):
                expected=fn(profile,{**scenario,'level':profile['phases'][2]['max_level']})
                self.assertIsNotNone(expected)
                self.assertEqual(fn(profile,scenario),expected)
                self.assertEqual(fn(profile,{**scenario,'level':None}),expected)

    def test_explicit_invalid_levels_rejected(self):
        for fn, profile, scenario in self.cases():
            for level in (0,False,'',-1,1.5,'60',profile['phases'][2]['max_level']+1):
                with self.subTest(fn=fn.__name__,operator=profile['id'],level=level),self.assertRaises(ValueError):
                    fn(profile,{**scenario,'level':level})
