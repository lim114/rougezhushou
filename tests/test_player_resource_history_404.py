from copy import deepcopy
import unittest
from rouge.player_resource_history import resource_rows,resource_text

def reads(values):return {'history':[{'kind':'resource_updated','at':i,'resource':key,'value':value}for i,(key,value)in enumerate(values)]}

class ResourceHistoryTests(unittest.TestCase):
    def test_first_observation_is_not_from_zero_and_zero_remains_valid(self):
        rows=resource_rows(reads([('gold',10),('gold',0),('gold',3)]))
        self.assertEqual([r['delta']for r in rows],[None,-10,3]);self.assertEqual(rows[1]['value'],0)

    def test_separate_resource_baselines_and_no_reward_attribution(self):
        rows=resource_rows(reads([('gold',10),('parts_count',2),('gold',12),('parts_count',1)]))
        self.assertEqual([r['delta']for r in rows],[None,None,2,-1]);self.assertIn('不能据此确定',resource_text(rows[2]))
        self.assertIn('源石锭',resource_text(rows[2]));self.assertNotIn('resource_updated',resource_text(rows[2]))

    def test_invalid_intermediate_breaks_delta_chain_without_changing_evidence(self):
        for invalid in(True,'20',None,float('inf'),float('nan'),-1):
            state=reads([('gold',2),('gold',invalid),('gold',5)]);before=deepcopy(state);rows=resource_rows(state)
            self.assertIsNone(rows[1]['value']);self.assertIsNone(rows[2]['delta'])
            self.assertEqual(state['history'][0],before['history'][0])

    def test_unknown_resource_does_not_leak_internal_identifier_as_player_name(self):
        row=resource_rows(reads([('internal_field_123',5)]))[0];self.assertEqual(row['name'],'未核对资源')
        self.assertNotIn('internal_field_123',resource_text(row))

if __name__=='__main__':unittest.main()
