from copy import deepcopy
import unittest
from rouge import public_archive
from rouge.player_exchange_sources import exchange_links,exchange_text

class ExchangeSourceTests(unittest.TestCase):
    def fixture(self):
        data=public_archive.load();version=next(key for key,pools in data['versions'].items()if any(p['name']=='失与得：N藏品输入'and p['collectibles']for p in pools))
        pool=next(p for p in data['versions'][version]if p['name']=='失与得：N藏品输入');return data,version,pool['collectibles'][0]
    def test_only_explicit_source_pair_yields_known_members_not_reward(self):
        data,version,identity=self.fixture();before=deepcopy(data);links=exchange_links(data,version,identity);self.assertTrue(links);self.assertEqual(data,before)
        link=next(row for row in links if row['rarity']=='N'and row['kind']=='藏品');pool=next(p for p in data['versions'][version]if p['id']==link['output_id'])
        self.assertEqual([r['id']for r in link['members']],pool['collectibles']);self.assertIsNone(link['actual_eligible']);self.assertIsNone(link['actual_reward']);self.assertIsNone(link['complete_current_version_pool'])
        self.assertIn('不能据此认定本次',exchange_text(link));self.assertIn('不表示当前DLC的完整奖励池',exchange_text(link))
    def test_missing_explicit_description_does_not_infer_from_same_rarity_or_name(self):
        data,version,identity=self.fixture()
        for pool in data['versions'][version]:
            if pool['name'].startswith('失与得：'):pool['sourceReferences']=[]
        self.assertEqual(exchange_links(data,version,identity),[])
    def test_wrong_node_id_and_wrong_output_label_are_not_silently_equated(self):
        data,version,identity=self.fixture()
        for pool in data['versions'][version]:
            if pool['name'].endswith('输出'):
                for reference in pool.get('sourceReferences',[]):reference['sourceIds']=['OTHER']
        self.assertEqual(exchange_links(data,version,identity),[])
    def test_unlisted_item_or_other_version_does_not_fall_back(self):
        data,version,identity=self.fixture();self.assertEqual(exchange_links(data,'unknown-version',identity),[]);self.assertEqual(exchange_links(data,version,'unlisted-item'),[])
    def test_parts_and_relics_use_their_own_explicit_input_output_sets(self):
        data=public_archive.load();checked=set()
        for version,pools in data['versions'].items():
            for pool in pools:
                if pool['name'].startswith('失与得：')and pool['name'].endswith('输入')and pool['collectibles']:
                    links=exchange_links(data,version,pool['collectibles'][0]);link=next(row for row in links if row['input_id']==pool['id']);checked.add((link['kind'],link['rarity']))
        self.assertEqual(checked,{(kind,rarity)for kind in('藏品','零件')for rarity in('N','R','SR')})

if __name__=='__main__':unittest.main()
