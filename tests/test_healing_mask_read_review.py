from collections import Counter
from copy import deepcopy
import unittest

from rouge import guardian_healing, susuro_healing
from rouge.catalog import catalog
from rouge.damage import calculate_damage


class HealingMaskReadReviewTests(unittest.TestCase):
    def test_unknown_ratio_reads_each_existing_total_once(self):
        class Skill(dict):
            def __init__(self, values):
                super().__init__(values)
                self.reads=Counter()
            def get(self, key, default=None):
                self.reads[key]+=1
                return super().get(key,default)
        for module,operator,identity in (
            (susuro_healing,'char_298_susuro','uniequip_002_susuro'),
            (guardian_healing,'char_196_sunbr','uniequip_002_sunbr'),
            (guardian_healing,'char_2025_shu','uniequip_002_shu')):
            with self.subTest(operator=operator):
                scenario={'operator':operator,'skill':1,'module_id':identity,'module_level':1}
                result=calculate_damage(scenario)
                skill=Skill(result['estimate']['skill'])
                result['estimate']['skill']=skill
                ref=module.reference(catalog()['operators'][operator],scenario)
                before=deepcopy(ref)
                module.attach_result(result,ref)
                for key in result['known_healing_subtotals']:
                    self.assertEqual(skill.reads[key],1,key)
                self.assertEqual(ref,before)
