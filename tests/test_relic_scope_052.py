"""Known raw recipient selectors constrain unknown effect reports."""
import unittest
from rouge.catalog import catalog
from rouge.damage import calculate_damage
from rouge.relics import mechanics,prepare

HAND='rogue_6_relic_hand_4'
SELECTOR={'aoesniper','reaperrange','skybreaker'}


class RelicScope052Tests(unittest.TestCase):
    def test_current_roster_does_not_receive_an_unrelated_unknown_mechanism(self):
        for op,profile in catalog()['operators'].items():
            with self.subTest(operator=op):
                self.assertNotIn(profile['subprofession_id'],SELECTOR)
                plain=calculate_damage({'operator':op,'skill':1})
                actual=calculate_damage({'operator':op,'skill':1,'relic_ids':[HAND]})
                self.assertEqual(actual['estimate']['base_stats'],plain['estimate']['base_stats'])
                self.assertEqual(actual['estimate']['skill'],plain['estimate']['skill'])
                self.assertEqual(actual['warnings'],plain['warnings'])
                self.assertTrue(actual['relic_resolution']['complete'])
                row=actual['relic_resolution']['records'][0]
                self.assertEqual(row['status'],'inapplicable')
                self.assertEqual(row['pending'],[])
                self.assertEqual(row['applied'],[])

    def test_selectors_preserve_unknown_for_every_eligible_branch(self):
        # Test only the selector gate with structural fixtures; this does
        # not claim new operators' numerical skill models are implemented.
        base=catalog()['operators']['mechanist']
        for branch in SELECTOR:
            profile={**base,'profession':'sniper','subprofession_id':branch}
            with self.subTest(branch=branch):
                _,resolution=prepare({'operator':'mechanist','skill':1,'relic_ids':[HAND]},profile)
                self.assertFalse(resolution['complete'])
                self.assertEqual(resolution['records'][0]['status'],'incomplete')
                self.assertEqual(resolution['records'][0]['pending'],['global_buff_normal:rogue_6_sniper_book'])
                self.assertFalse(resolution['records'][0]['applied'])

    def test_data_item_remains_pending_and_the_gate_uses_the_raw_selector(self):
        row=mechanics()['relics'][HAND]
        self.assertEqual(row['status'],'pending')
        self.assertEqual(row['pending'],['global_buff_normal:rogue_6_sniper_book'])
        self.assertEqual(row['pending_scopes'][0]['subprofession'],'|'.join(('aoesniper','reaperrange','skybreaker')))
        self.assertFalse(row['effects'])


if __name__=='__main__':unittest.main()
