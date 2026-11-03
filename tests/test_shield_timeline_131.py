import unittest
from copy import deepcopy
from rouge.shield_timeline import compare_shield_windows, format_shield_windows
from rouge.damage import calculate_damage

BASE={'operator':'mechanist','skill':2,'base_attack':1000,'skill_duration_seconds':20}
def event(source,broke,hit):return {'source':source,'break_seconds':broke,'hit_seconds':hit}

class ShieldTimelineTests(unittest.TestCase):
    def test_breaks_collisions_sources_and_boundary(self):
        preview={'events':[event('owner',1,2),event('structure',1,2),event('owner',2,None),event('structure',3,4)],'windows_seconds':[0,2,3,4,5]}
        result=compare_shield_windows(BASE,preview)
        self.assertEqual([r['explosion_damage_reference'] for r in result['rows']],[0,0,10000,10000,15000])
        self.assertEqual(result['rows'][2]['declared_breaks'],3)
        self.assertEqual((result['rows'][2]['owner_hits'],result['rows'][2]['structure_hits']),(1,1))
        self.assertIsNone(result['actual_end_seconds']);self.assertIsNone(result['actual_ammunition_consumption'])

    def test_no_ammo_cap_or_inferred_end(self):
        result=compare_shield_windows(BASE,{'events':[event('owner',i,i) for i in range(10)],'windows_seconds':[30]})
        self.assertEqual(result['rows'][0]['owner_hits'],10)
        self.assertEqual(result['nominal_ammunition_parameter'],8)
        self.assertIsNone(result['full_cast_damage']); self.assertIsNone(result['cycle_damage'])
        self.assertIn('实际结束',format_shield_windows(result))

    def test_preserves_original_ordinary_and_inputs(self):
        scenario={**BASE,'shield_break_count':5};preview={'events':[],'windows_seconds':[5,20]}
        before=deepcopy((scenario,preview));result=compare_shield_windows(scenario,preview)
        for row in result['rows']:
            ordinary=calculate_damage({**scenario,'shield_break_count':0,'window_seconds':row['window_seconds']})['estimate']['skill']['window_damage']
            self.assertEqual(row['ordinary_damage_reference'],ordinary)
        self.assertEqual((scenario,preview),before)

    def test_resistance_applies_to_explosions(self):
        result=compare_shield_windows({**BASE,'enemy_resistance':50}, {'events':[event('owner',0,1)],'windows_seconds':[2]})
        self.assertEqual(result['rows'][0]['explosion_damage_reference'],2500)

    def test_invalid_declarations(self):
        for events in ([event('owner',2,1)],[event('other',0,1)],[event('owner',True,1)],[event('owner',0,float('nan'))],[{}],[event('owner',0,1)]*101):
            with self.assertRaises(ValueError):compare_shield_windows(BASE,{'events':events,'windows_seconds':[10]})
        for windows in ([],[True],[-1],[3601],[1]*13):
            with self.assertRaises(ValueError):compare_shield_windows(BASE,{'events':[],'windows_seconds':windows})
        with self.assertRaises(ValueError):compare_shield_windows({**BASE,'skill':3},{'events':[],'windows_seconds':[10]})
