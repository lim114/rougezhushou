from collections import defaultdict
from copy import deepcopy
from unittest.mock import patch
import unittest

from rouge import token_module_comparison as comparison
from rouge.catalog import catalog


class TokenComparisonPreparationReviewTests(unittest.TestCase):
    def test_two_token_profile_reuses_conditions_without_sharing_output(self):
        identity='char_1042_phatm2';profile=catalog()['operators'][identity]
        module=profile['modules'][0]['id'];cultivation={'elite':2,'level':profile['phases'][2]['max_level']}
        before=deepcopy(cultivation)
        with patch.object(comparison,'token_attributes',wraps=comparison.token_attributes) as calculate:
            result=comparison.compare_token_module(identity,cultivation,module)
        by_stage=defaultdict(set)
        for call in calculate.call_args_list:by_stage[call.args[1]['module_level']].add(id(call.args[1]))
        self.assertEqual(len(result['tokens']),2)
        self.assertEqual({level:len(ids) for level,ids in by_stage.items()},{0:1,1:1,2:1,3:1})
        second=deepcopy(result['tokens'][1])
        result['tokens'][0]['stages'][0]['values']['hp']=-1
        self.assertEqual(result['tokens'][1],second)
        self.assertEqual(cultivation,before)
