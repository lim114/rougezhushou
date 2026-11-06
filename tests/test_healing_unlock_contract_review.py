import unittest
from copy import deepcopy
from rouge.catalog import catalog
from rouge import susuro_healing,guardian_healing

CASES=((susuro_healing,'char_298_susuro','uniequip_002_susuro'),
       (guardian_healing,'char_196_sunbr','uniequip_002_sunbr'),
       (guardian_healing,'char_2025_shu','uniequip_002_shu'))


class HealingUnlockContractTests(unittest.TestCase):
    def test_all_three_sources_and_stages_have_unlock_conditions(self):
        for module,operator,equipment in CASES:
            for stage in (1,2,3):
                with self.subTest(operator=operator,stage=stage):
                    result=module.selected_trait(catalog()['operators'][operator],
                        {'operator':operator,'module_id':equipment,'module_level':stage})
                    self.assertIsNotNone(result)
                    self.assertEqual(result['module_level'],stage)

    def test_missing_or_null_unlock_condition_is_not_phase_zero(self):
        for module,operator,equipment in CASES:
            for missing in (True,False):
                profile=deepcopy(catalog()['operators'][operator])
                equipped=next(m for m in profile['modules']if m['id']==equipment)
                count=0
                for part in equipped['levels'][0]['parts']:
                    if part.get('target')!='TRAIT':continue
                    for candidate in part['overrideTraitDataBundle']['candidates']:
                        count+=1
                        if missing:del candidate['unlockCondition']
                        else:candidate['unlockCondition']=None
                self.assertGreater(count,0)
                with self.subTest(operator=operator,missing=missing):
                    with self.assertRaises(KeyError if missing else TypeError):
                        module.selected_trait(profile,{'operator':operator,'module_id':equipment,'module_level':1})
