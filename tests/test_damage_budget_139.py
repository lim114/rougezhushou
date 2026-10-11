import unittest
from copy import deepcopy
from rouge.damage_budget import damage_sources,damage_budget,format_damage_budget
from rouge.damage import calculate_damage


class DamageBudget139Tests(unittest.TestCase):
    scenario={'operator':'mechanist','skill':3,'base_attack':1000}
    def proposal(self):
        return {'targets':[{'id':'甲','hp':1000,'defense':0,'resistance':0},
                           {'id':'乙','hp':10000,'defense':500,'resistance':50}],
                'events':[{'at_seconds':0,'target':'甲','source':'damage_0'},
                          {'at_seconds':0,'target':'甲','source':'damage_1'},
                          {'at_seconds':1,'target':'乙','source':'damage_0'}]}

    def test_each_target_recomputed_and_overkill(self):
        p=self.proposal();s=deepcopy(self.scenario);before=deepcopy(p);r=damage_budget(s,p)
        first=r['rows'][0];self.assertEqual(first['effective_damage'],1000);self.assertGreater(first['overkill'],0)
        self.assertEqual(r['rows'][1]['effective_damage'],0)
        expected=calculate_damage({**s,'enemy_resistance':50,'enemy_defense':500})['components'][0]['per_hit']
        self.assertEqual(r['rows'][2]['per_hit'],expected);self.assertEqual(r['targets'][0]['budget_exhausted_at'],0)
        self.assertIsNone(r['actual_kill_time']);self.assertEqual(s,self.scenario);self.assertEqual(p,before)
        self.assertIn('不是实际击杀',format_damage_budget(r))

    def test_order_and_empty_events(self):
        p=self.proposal();p['events'].reverse();r=damage_budget(self.scenario,p)
        self.assertEqual([x['input_order'] for x in r['rows']],[1,2,0])
        p['events']=[];r=damage_budget(self.scenario,p)
        self.assertEqual(r['rows'],[]);self.assertIsNone(r['targets'][0]['budget_exhausted_at'])
        self.assertEqual(r['targets'][0]['hp'],1000)

    def test_target_binding_replaced_without_mutation(self):
        s={**self.scenario,'target_enemy':{'stage_id':'bad'}}
        r=damage_budget(s,self.proposal());self.assertNotIn('target_enemy',r['references']['甲']['scenario'])
        self.assertIn('target_enemy',s)

    def test_healing_and_unknown_not_damage(self):
        self.assertEqual(damage_sources({'components':[{'name':'治疗','damage_type':'healing','per_hit':500},
            {'name':'未知','damage_type':'physical','per_hit':None}]}),[])
        with self.assertRaises(ValueError):damage_budget({'operator':'char_2025_shu','skill':1},self.proposal())

    def test_invalid_inputs(self):
        for path,value in [('hp',0),('hp',True),('defense',-1),('resistance',101),('id','')]:
            p=self.proposal();p['targets'][0][path]=value
            with self.subTest(path=path),self.assertRaises(ValueError):damage_budget(self.scenario,p)
        for key,value in [('at_seconds',True),('source','unknown'),('target','unknown')]:
            p=self.proposal();p['events'][0][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):damage_budget(self.scenario,p)
        p=self.proposal();p['targets'].append(deepcopy(p['targets'][0]))
        with self.assertRaises(ValueError):damage_budget(self.scenario,p)
