import unittest
from rouge.supplemental_run import run_skill_reference,format_run_reference
from rouge.supplemental_skills import defaults,_cultivated_stats
from tests.test_supplemental_run_141 import environment


class SupplementalCost143Tests(unittest.TestCase):
    def test_six_operators_use_pinned_cost_chain(self):
        for identity in ('char_208_melan','char_124_kroos','char_210_stward','char_209_ardign','char_122_beagle','char_120_hibisc'):
            p=defaults(identity);e=environment(['rogue_6_relic_legacy_141','rogue_6_relic_fight_11'])
            r=run_skill_reference(p,e);base=_cultivated_stats(p)['deployment_cost']
            self.assertEqual(r['deployment_reference']['estimated_cost'],round((base-1)*.5))
            self.assertIsNone(r['deployment_reference']['actual_cost'])
            self.assertEqual(r['attribute_resolution']['unsupported'],[])

    def test_first_tank_card_separates_rune_round_and_card_floor(self):
        p=defaults('char_209_ardign');p.update(elite=0,level=1,potential=2)
        self.assertEqual(_cultivated_stats(p)['deployment_cost'],15)
        r=run_skill_reference(p,environment(['rogue_6_relic_fight_11','rogue_6_relic_book_3']))
        trace=r['deployment_reference']['native_without_talent']
        self.assertEqual(trace['attributes_cost'],8)
        self.assertEqual(trace['estimated_cost'],2)
        self.assertTrue(r['deployment_reference']['first_card_only'])
        self.assertIn('仅首次有效',format_run_reference(r))

    def test_empty_bed_missing_zero_active_and_clamp(self):
        p=defaults('char_124_kroos');e=environment(['rogue_6_relic_cargo_3','rogue_6_relic_legacy_141'])
        r=run_skill_reference(p,e);self.assertIsNone(r['deployment_reference']['estimated_cost'])
        e['relic_context']['empty_slots']=3
        self.assertEqual(run_skill_reference(p,e)['deployment_reference']['estimated_cost'],10)
        e['relic_context']['empty_slots']=4
        self.assertEqual(run_skill_reference(p,e)['deployment_reference']['estimated_cost'],4)
        e['relic_ids']+=['rogue_6_relic_fight_11']
        self.assertEqual(run_skill_reference(p,e)['deployment_reference']['estimated_cost'],0)

    def test_fang_talent_unchanged_alone_unknown_with_discount(self):
        p=defaults('char_123_fang')
        self.assertEqual(run_skill_reference(p,environment())['deployment_reference']['estimated_cost'],10)
        r=run_skill_reference(p,environment(['rogue_6_relic_hand_1']))
        self.assertIsNone(r['deployment_reference']['estimated_cost'])
        self.assertTrue(r['deployment_reference']['talent_composition_pending'])
        self.assertIsNone(r['rows'][1]['delta'])
        p.update(elite=0,level=1)
        self.assertEqual(run_skill_reference(p,environment(['rogue_6_relic_hand_1']))['deployment_reference']['estimated_cost'],3)

    def test_pioneer_start_dp_is_counted_once_and_not_on_other_panels(self):
        p=defaults('char_123_fang');p['count']=3
        e=environment(['rogue_6_relic_book_1','rogue_6_relic_book_1'])
        r=run_skill_reference(p,e)
        self.assertEqual(r['rows'][0]['value'],9);self.assertEqual(r['rows'][0]['declared_total'],27)
        self.assertEqual(r['deployment_reference']['estimated_cost'],10)
        other=run_skill_reference(defaults(),e)
        self.assertEqual(other['deployment_reference']['skill_start_dp'],0)

    def test_selectors_and_potential_are_recomputed(self):
        p=defaults('char_124_kroos');p['potential']=6
        r=run_skill_reference(p,environment(['rogue_6_relic_legacy_70','rogue_6_relic_legacy_72']))
        self.assertEqual(r['deployment_reference']['estimated_cost'],7)
        self.assertEqual(len(r['attribute_resolution']['costs']),1)
