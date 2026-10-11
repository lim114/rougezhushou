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
    def test_220_walking_blockers_item_direct_and_base_cost_comparison(self):
        g=graph();g['nodes'][2].update(completed_declared=False,occupied_declared=False,other_blocked_declared=False)
        r=p.movement_options(g,'shop',inventory=[{'item_id':'rogue_6_scrap_M_10','remaining_uses':2}],action_points=1)
        self.assertIsNone(r['walking_paths']['no_known_blocker'])
        self.assertEqual(r['walking_paths']['topology']['steps'],2)
        self.assertEqual(r['minimum_base_cost_candidates'],['inventory:1'])
        g['nodes'][2]['completed_declared']=True
        r=p.movement_options(g,'shop',inventory=[{'item_id':'rogue_6_scrap_M_08','remaining_uses':1},
            {'item_id':'rogue_6_scrap_M_10','remaining_uses':2}],action_points=1)
        self.assertEqual(r['walking_paths']['declared_clear']['steps'],2)
        self.assertFalse(r['options'][0]['base_cost_affordable'])
        self.assertEqual(r['minimum_base_ap_cost_reference'],0)
        self.assertEqual(r['minimum_base_cost_candidates'],['inventory:1'])
        self.assertIsNone(r['actual_best_route'])
        g['nodes'][2]['occupied_declared']=True
        self.assertIsNone(p.movement_options(g,'shop')['walking_paths']['no_known_blocker'])

    def test_220_unknown_graph_inventory_instances_reentry_and_validation(self):
        g=graph();old=copy.deepcopy(g)
        r=p.movement_options(g,'shop',inventory=[{'item_id':'rogue_6_scrap_M_10'},
            {'item_id':'rogue_6_scrap_M_10','remaining_uses':0}])
        self.assertEqual(len(r['options']),3);self.assertIsNone(r['options'][0]['known_conditions_match'])
        self.assertIsNone(r['options'][1]['known_conditions_match']);self.assertFalse(r['options'][2]['known_conditions_match'])
        self.assertEqual(g,old)
        r=p.movement_options(g,'s',action_points=0)
        self.assertEqual(r['options'][0]['base_ap_cost'],1)
        self.assertFalse(r['options'][0]['base_cost_affordable'])
        bad=graph();bad['edges']=[['s','missing']]
        with self.assertRaises(ValueError):p.movement_options(bad,'shop')
        bad=graph();bad['nodes'][2]['completed_declared']=1
        with self.assertRaises(ValueError):p.movement_options(bad,'shop')
        with self.assertRaises(ValueError):p.movement_options(g,'shop',inventory=[
            {'item_id':'rogue_6_scrap_M_10','instance_id':'a'},{'item_id':'rogue_6_scrap_M_10','instance_id':'a'}])
        group=graph();group['nodes'][4]['scrap_category']='EVENTS'
        r=p.movement_targets(group,'rogue_6_scrap_M_07')
        self.assertTrue(next(x for x in r['targets'] if x['node_id']=='unknown')['node_type_matches'])

    def test_219_event_estimate_and_unknown_sale_bounds(self):
        r=p.goods_valuation('rogue_6_scrap_G_02',[{'kind':'battle_completed','count':3},
            {'kind':'movement_completed','count':5}])
        self.assertEqual(r['arithmetic_subtotal'],8);self.assertEqual(r['known_description_delta'],6)
        self.assertIsNone(r['actual_sell_value'])
        r=p.goods_valuation('rogue_6_scrap_G_04',[{'kind':'operator_recruited','count':2}],initial_estimate=10)
        self.assertEqual(r['nominal_estimate'],16)
        r=p.goods_valuation('rogue_6_scrap_G_10',[{'kind':'movement_completed','count':20}])
        self.assertEqual(r['arithmetic_subtotal'],-8);self.assertFalse(r['valuation_floor_and_cap_verified'])
        self.assertIsNone(r['actual_sell_value'])
        for args in ({'initial_estimate':True},{'events':[{'kind':'unknown'}]},
                     {'events':[{'kind':'battle_completed','perfect':1}]}):
            with self.assertRaises(ValueError):p.goods_valuation('rogue_6_scrap_G_02',**args)

    def test_219_random_destruction_and_acquisition_cascade(self):
        r=p.goods_valuation('rogue_6_scrap_G_05',[{'kind':'movement_completed'}])
        self.assertIsNone(r['nominal_estimate']);self.assertTrue(r['unknown_effects'])
        events=[{'kind':'battle_completed','perfect':True},
                {'kind':'battle_completed','perfect':False},
                {'kind':'battle_completed','perfect':True}]
        before=copy.deepcopy(events);r=p.goods_valuation('rogue_6_scrap_G_06',events)
        self.assertEqual(r['known_description_delta'],4);self.assertTrue(r['destroyed_in_declared_ledger'])
        self.assertEqual(r['events'][-1]['status'],'after_declared_destruction')
        self.assertEqual(events,before);self.assertIsNone(r['nominal_estimate'])
        r=p.goods_valuation('rogue_6_scrap_G_06',[{'kind':'battle_completed'}])
        self.assertTrue(r['destruction_condition_unknown']);self.assertEqual(len(r['events'][0]['conditional_effects']),2)
        r=p.goods_valuation('rogue_6_scrap_G_07',[{'kind':'item_obtained'}])
        self.assertEqual(r['named_grant_references'][0]['quantity'],3)
        self.assertEqual(r['known_description_delta'],0);self.assertIsNone(r['nominal_estimate'])
        r=p.goods_valuation('rogue_6_scrap_G_09',[{'kind':'parts_obtained','count':2}])
        self.assertEqual(r['arithmetic_subtotal'],16)

    def test_218_all_zones_ids_and_goal_exhaustion_distinct(self):
        rows=p.zone_catalog()['zones'];self.assertEqual(len(rows),26)
        self.assertEqual(sum(x['source_stated_exhaustion_outcome']=='pursuit' for x in rows),7)
        self.assertEqual(sum(x['source_stated_exhaustion_outcome']=='return_original_zone' for x in rows),19)
        self.assertEqual(len({x['zone_id'] for x in rows if x['name']=='未萌生的摇篮'}),19)
        r=p.zone_budget('zone_6',action_points=2,walking_steps=2,goal_completed=False)
        self.assertEqual(r['nominal_ap_after_payment'],0);self.assertTrue(r['payment_zero_boundary'])
        self.assertTrue(r['zone']['goal_requires_battle_victory'])
        self.assertTrue(r['conditional_outcomes'][0]['goal_condition_matches'])
        r=p.zone_budget('zone_portal_normal_6_3',action_points=1,walking_steps=1)
        self.assertEqual(r['conditional_outcomes'][0]['outcome'],'return_original_zone')
        self.assertIsNone(r['conditional_outcomes'][0]['return_zone_id'])

    def test_218_unknown_budget_insufficient_and_refund_boundary(self):
        r=p.zone_budget('zone_1',walking_steps=3)
        self.assertIsNone(r['base_cost_affordable']);self.assertIsNone(r['actual_final_ap'])
        r=p.zone_budget('zone_1',action_points=2,walking_steps=3)
        self.assertFalse(r['base_cost_affordable']);self.assertIsNone(r['nominal_ap_after_payment'])
        r=p.zone_budget('zone_1',action_points=0,item_id='rogue_6_scrap_M_12')
        self.assertEqual(r['nominal_ap_after_stated_grant'],3)
        self.assertTrue(r['payment_zero_boundary']);self.assertIsNone(r['actual_exhaustion_trigger'])
        r=p.zone_budget('zone_5',action_points=5,walking_steps=1,goal_completed=True)
        self.assertFalse(r['conditional_outcomes'][0]['goal_condition_matches'])
        for args in ({'action_points':True},{'walking_steps':-1},{'goal_completed':1},
                     {'walking_steps':1,'item_id':'rogue_6_scrap_M_01'}):
            with self.assertRaises(ValueError):p.zone_budget('zone_1',**args)
        with self.assertRaises(ValueError):p.zone_budget('未萌生的摇篮')

    def test_217_move_grants_and_exact_passive_conditions(self):
        g=graph();old=copy.deepcopy(g)
        r=p.movement_effects(g,'rogue_6_scrap_M_10','shop',remaining_uses=2,
            passive_items=[{'item_id':'rogue_6_scrap_P_03','remaining_activations':1}])
        self.assertEqual(r['movement_grants'][0]['amount'],4)
        self.assertTrue(r['movement_grants'][0]['condition_matches'])
        self.assertTrue(r['passives'][0]['condition_matches'])
        self.assertEqual(r['passives'][0]['effects'],[{'resource':'shield','amount':3}])
        r=p.movement_effects(g,'rogue_6_scrap_M_12','wish',remaining_uses=1,
            passive_items=[{'item_id':'rogue_6_scrap_P_05','remaining_activations':1}])
        self.assertEqual(r['movement_grants'][0]['resource'],'ap')
        self.assertEqual(r['movement_grants'][0]['amount'],3)
        self.assertTrue(r['passives'][0]['condition_matches']);self.assertEqual(g,old)
        self.assertFalse(r['combat_modifiers_applied']);self.assertIsNone(r['actual_new_resources'])

    def test_217_unknown_and_failed_conditions_do_not_become_grants(self):
        g=graph()
        r=p.movement_effects(g,'rogue_6_scrap_M_09','wish',remaining_uses=1)
        self.assertIsNone(r['movement_grants'][0]['condition_matches'])
        g['nodes'][2]['scrap_category']='EVENTS'
        r=p.movement_effects(g,'rogue_6_scrap_M_09','wish',remaining_uses=1,
            passive_items=[{'item_id':'rogue_6_scrap_P_02','remaining_activations':0}])
        self.assertTrue(r['movement_grants'][0]['condition_matches'])
        self.assertFalse(r['passives'][0]['condition_matches'])
        r=p.movement_effects(g,'rogue_6_scrap_M_10','wish',remaining_uses=2)
        self.assertFalse(r['movement_grants'][0]['condition_matches'])
        r=p.movement_effects(g,'rogue_6_scrap_M_07','wish',remaining_uses=1,
            passive_items=[{'item_id':'rogue_6_scrap_P_03','remaining_activations':1}])
        self.assertIsNone(r['random_target_selection_condition']);self.assertIsNone(r['passives'][0]['condition_matches'])
        with self.assertRaises(ValueError):p.movement_effects(g,'rogue_6_scrap_M_01','s')
        with self.assertRaises(ValueError):p.movement_effects(g,'rogue_6_scrap_M_08','wish',passive_items=[
            {'item_id':'rogue_6_scrap_P_03','remaining_activations':2}])

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
