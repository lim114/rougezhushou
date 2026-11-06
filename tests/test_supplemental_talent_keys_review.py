from copy import deepcopy
from unittest.mock import patch
import unittest

from rouge import supplemental_skills as subject


class SupplementalTalentKeysReviewTests(unittest.TestCase):
    def test_each_candidate_unlock_phase_is_parsed_once(self):
        data=deepcopy(subject.supplemental_profiles())
        reads=[]

        class Phase(str):
            def split(self,*args,**kwargs):
                reads.append(str(self))
                return super().split(*args,**kwargs)

        profile=data['operators']['char_124_kroos']
        count=0
        for slot in profile['talents']:
            for candidate in slot['candidates']:
                candidate['unlockCondition']['phase']=Phase(candidate['unlockCondition']['phase'])
                count+=1
        preview=subject.defaults('char_124_kroos');preview['potential']=5
        with patch.object(subject,'supplemental_profiles',return_value=data):
            result=subject.skill_reference(preview)
        self.assertEqual(len(reads),count)
        self.assertEqual(len(result['talents']),1)
        self.assertEqual(result['talents'][0]['blackboard'][1]['value'],1.6)

    def test_equal_rank_candidates_keep_first_source_order_and_return_independent_copy(self):
        data=deepcopy(subject.supplemental_profiles())
        profile=data['operators']['char_124_kroos']
        candidate=deepcopy(profile['talents'][0]['candidates'][-1])
        duplicate=deepcopy(candidate);duplicate['name']='second candidate'
        profile['talents'][0]['candidates']=[candidate,duplicate]
        preview=subject.defaults('char_124_kroos');preview['potential']=6
        original=deepcopy(data)
        with patch.object(subject,'supplemental_profiles',return_value=data):
            result=subject.skill_reference(preview)
        self.assertEqual(result['talents'][0]['name'],candidate['name'])
        result['talents'][0]['name']='changed result'
        self.assertEqual(data,original)
