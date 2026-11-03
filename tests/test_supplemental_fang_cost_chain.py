import unittest
from copy import deepcopy
from itertools import permutations
from rouge.supplemental_run import run_skill_reference,format_run_reference
from rouge.supplemental_skills import defaults
from rouge.supplemental_cost import cost_reference
from rouge.deployment import native_deployment_cost
from tests.test_supplemental_run_141 import environment


class SupplementalFangCostChainTests(unittest.TestCase):
    def test_fang_cost_talent_is_after_rune_round_not_before_it(self):
        p=defaults('char_123_fang')
        r=run_skill_reference(p,environment(['rogue_6_relic_fight_11']))
        # Original cost11, rune0.5 gives ties-to-even6, then talent -1=5.
        # Wrongly subtracting talent before the rune would give5 as well here.
        # Potential6 costs9: round4.5=4 then-1=3; pre-rune8*.5 would4.
        self.assertEqual(r['deployment_reference']['estimated_cost'],5)
        p['potential']=6
        r=run_skill_reference(p,environment(['rogue_6_relic_fight_11']))
        self.assertEqual(r['deployment_reference']['estimated_cost'],3)
        trace=r['deployment_reference']['native_with_talent']
        self.assertEqual((trace['attributes_cost'],trace['deck_base_delta'],trace['deck_base_cost']),(4,-1,3))
        self.assertFalse(r['deployment_reference']['talent_composition_pending'])

    def test_rune_addition_multiplier_and_empty_bed_respect_distinct_layers(self):
        ids=['rogue_6_relic_legacy_141','rogue_6_relic_fight_11','rogue_6_relic_cargo_3']
        for order in permutations(ids):
            e=environment([*order,order[0]]);e['relic_context']['empty_slots']=3
            r=run_skill_reference(defaults('char_123_fang'),e)
            # round((11-1)*.5)=5, then Fang=-1 =>4; empty bed inactive.
            self.assertEqual(r['deployment_reference']['estimated_cost'],4)
            e['relic_context']['empty_slots']=4
            self.assertEqual(run_skill_reference(defaults('char_123_fang'),e)['deployment_reference']['estimated_cost'],0)
        missing=run_skill_reference(defaults('char_123_fang'),environment(ids))
        self.assertIsNone(missing['deployment_reference']['estimated_cost'])

    def test_explicit_native_chain_keeps_deck_delta_before_card_floor(self):
        # Integer-boundary oracles from the identified native pipeline.
        cases=[(dict(cultivation_cost=11,rune_multipliers=(-.5,),deck_base_deltas=(-1,),card_factors=(.25,)),1),
               (dict(cultivation_cost=9,rune_multipliers=(-.5,),deck_base_deltas=(-1,),card_factors=(.25,)),0),
               (dict(cultivation_cost=9,deck_base_deltas=(-1,),redeploy_factor=1.5),12),
               (dict(cultivation_cost=0,deck_base_deltas=(-1,),runtime_deltas=(-6,)),0)]
        for arguments,expected in cases:
            self.assertEqual(native_deployment_cost(**arguments)['estimated_cost'],expected)
        with self.assertRaises(ValueError):native_deployment_cost(11,deck_base_deltas=(.5,))

    def test_elite_and_recipient_selection_do_not_leak_talent(self):
        p=defaults('char_123_fang');e=environment(['rogue_6_relic_fight_11']);before=deepcopy(e)
        p.update(elite=0,level=1,potential=1)
        self.assertIsNone(run_skill_reference(p,e)['deployment_reference']['talent_source'])
        other=run_skill_reference(defaults('char_209_ardign'),e)
        self.assertIsNone(other['deployment_reference']['talent_source'])
        self.assertEqual(e,before)

    def test_unknown_cost_talent_is_not_generalized_from_key(self):
        talents=[{'name':'other','prefabKey':'1','blackboard':[{'key':'cost','value':-1,'valueStr':None}]}]
        rule={'kind':'deployment_cost_pct','relic_id':'rogue_6_relic_fight_11','value':-.5,'_verified_rule':True}
        result=cost_reference({'deployment_cost':11},talents,[rule],[],operator='char_123_fang')
        self.assertTrue(result['talent_composition_pending'])
        self.assertIsNone(result['estimated_cost'])

    def test_report_preserves_source_and_actual_cost_boundaries(self):
        r=run_skill_reference(defaults('char_123_fang'),environment(['rogue_6_relic_fight_11']))
        source=r['deployment_reference']['talent_source']
        self.assertFalse(source['current_hotfix_equivalence_proven'])
        self.assertIsNone(r['deployment_reference']['actual_cost'])
        self.assertIn('符文先取整数，再减1',format_run_reference(r))
