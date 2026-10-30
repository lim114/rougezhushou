"""Observation comparison is never a transaction or a shop-identity inference."""
from copy import deepcopy
import unittest
from rouge.player_shop_memory import recorded_shops,compare_shops,comparison_text

def observations():
    from rouge.player_shop_hover import ShopNameReader
    from tests.test_player_feature_417 import shop_fixture
    import numpy as np
    reader=ShopNameReader(lambda *a,**k:(shop_fixture(),None))
    image=np.zeros((600,800,3),np.uint8);reader.identify(image,(245,170))
    snapshot=reader.snapshot(image)
    return {**snapshot,'kind':'shop_items_read','at':100.0}

class ShopReadingComparisonTests(unittest.TestCase):
    def test_comparison_preserves_observed_members_without_transactions(self):
        first=observations();second=deepcopy(first);second['items']=first['items'][1:];second['at']=101
        rows=recorded_shops({'history':[first,second]});result=compare_shops(rows,1)
        self.assertEqual(result['unread'],first['items'][:1]);self.assertEqual(result['added'],[])
        self.assertEqual(result['both'],second['items']);text=comparison_text(result)
        self.assertIn('不等于已购买',text);self.assertIn('不同商店',text)
        self.assertNotIn('purchased',result)
    def test_first_and_missing_observations_have_no_fake_previous(self):
        row=observations();rows=recorded_shops({'history':[row]})
        self.assertIsNone(compare_shops(rows,0)['previous']);self.assertIsNone(compare_shops(rows,1))
        self.assertIn('尚无前次',comparison_text(compare_shops(rows,0)))
    def test_unread_set_is_not_inferred_from_partial_public_catalog(self):
        row=observations();reduced=deepcopy(row);reduced['items']=row['items'][:1]
        rows=recorded_shops({'history':[reduced,row]});result=compare_shops(rows,1)
        self.assertEqual(result['added'],row['items'][1:]);self.assertEqual(result['unread'],[])
    def test_invalid_timestamps_and_forged_complete_records_excluded(self):
        row=observations();bad=[]
        for at in(float('nan'),float('inf'),-1,True,'now',None):
            candidate=deepcopy(row);candidate['at']=at;bad.append(candidate)
        candidate=deepcopy(row);candidate['complete']=True;bad.append(candidate)
        state={'history':bad+[row]};before=deepcopy(state)
        result=recorded_shops(state);self.assertEqual([key for key,_ in result],[len(bad)])
        self.assertEqual(len(state['history']),len(before['history']))
    def test_intervening_other_observations_keep_original_history_identity(self):
        row=observations();state={'history':[row,{'kind':'resource_read'},None,deepcopy(row)]}
        rows=recorded_shops(state);self.assertEqual([key for key,_ in rows],[0,3]);self.assertEqual(compare_shops(rows,3)['previous'],0)
    def test_same_item_names_do_not_merge_different_catalog_ids(self):
        row=observations();forged=deepcopy(row);forged['items'][0]['id']='not-a-real-item'
        self.assertEqual(recorded_shops({'history':[forged]}),[])

if __name__=='__main__':unittest.main()
