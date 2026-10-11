import copy,json,unittest
from pathlib import Path
from rouge import exploration_planning as p

ROOT=Path(__file__).resolve().parents[1]

def graph():
    return {'current_node':'s','zone_id':'zone_1','nodes':[
        {'id':'s','row':2,'col':2,'node_type_raw':'EMPTY'},
        {'id':'shop','row':2,'col':4,'node_type_raw':'BATTLE_SHOP'},
        {'id':'wish','row':3,'col':3,'node_type_raw':'WISH'},
        {'id':'combat','row':4,'col':2,'node_type_raw':'BATTLE_NORMAL','scrap_category':'BATTLES'},
        {'id':'unknown','row':1,'col':1},
        {'id':'far','row':5,'col':5,'node_type_raw':'SCRAP_SHOP'}],
        'edges':[['s','wish'],['wish','shop'],['s','combat'],['s','unknown'],['shop','far']]}

class ExplorationPlanningTests(unittest.TestCase):
    def test_216_original_item_and_range_parameters(self):
        data=p.reference_data();self.assertEqual(len(p.item_catalog()['items']),30)
        self.assertEqual({k:len(p.item_catalog(k)['items']) for k in ('MOVE','GOODS','PASSIVE')},
                         {'MOVE':12,'GOODS':12,'PASSIVE':6})
        self.assertEqual({(v['row'],v['col']) for v in data['ranges']['r-6']['grids']},
                         {(0,i) for i in range(-2,3)}|{(i,0) for i in range(-2,3)})
        for item in p.item_catalog('MOVE')['items']:
            self.assertIn('$.modules.rogue_6.scrap.moveScrapData.',item['source_selector'])

    def test_216_straight_diagonal_all_map_and_exact_shop(self):
        before=copy.deepcopy(graph())
        r=p.movement_targets(before,'rogue_6_scrap_M_01',remaining_uses=1)
        self.assertEqual({n['node_id'] for n in r['targets']},{'shop','combat'})
        r=p.movement_targets(before,'rogue_6_scrap_M_02')
        self.assertEqual({n['node_id'] for n in r['targets']},{'wish','unknown'})
        r=p.movement_targets(before,'rogue_6_scrap_M_10')
        self.assertEqual({n['node_id'] for n in r['targets']},{'shop','far','unknown'})
        self.assertEqual(before,graph());self.assertFalse(r['inventory_updated'])

    def test_216_unknown_groups_random_and_expired_are_explicit(self):
        r=p.movement_targets(graph(),'rogue_6_scrap_M_07')
        self.assertIn('unknown',{x['node_id'] for x in r['targets']})
        self.assertNotIn('combat',{x['node_id'] for x in r['targets']})
        self.assertTrue(all(x['probability'] is None for x in r['targets']))
        self.assertTrue(all(x['is_random_destination'] for x in r['targets']))
        self.assertFalse(p.movement_targets(graph(),'rogue_6_scrap_M_03',remaining_uses=0)['targets'])
        for args in ({'remaining_uses':True},{'remaining_uses':4},{'start':'missing'}):
            with self.assertRaises(ValueError):p.movement_targets(graph(),'rogue_6_scrap_M_03',**args)
        bad=graph();bad['nodes'][1]['row']=True
        with self.assertRaises(ValueError):p.movement_targets(bad,'rogue_6_scrap_M_01')
        bad=graph();bad['nodes'].append(copy.deepcopy(bad['nodes'][0]))
        with self.assertRaises(ValueError):p.movement_targets(bad,'rogue_6_scrap_M_01')

if __name__=='__main__':unittest.main()
