"""Native-derived cases include shared limits and S2's distinct counters."""
import copy
import unittest

from rouge.ammo_counter import AmmoCounter,ExtraModeCounters,poll_book
from rouge.ammo_reference import refill_parameters
from rouge.damage import calculate_damage
from rouge.relic_events import ammunition_rounds

BOOK='rogue_6_relic_legacy_139'
YA='rogue_6_relic_legacy_140'


class NativeAmmoCounter055Tests(unittest.TestCase):
    def test_shared_recovery_budget_caps_request_and_zero_still_finishes_book(self):
        p=refill_parameters(10,.3,.5)
        c=AmmoCounter(10,consumed=9,recovered=9)
        self.assertEqual(poll_book(c,p,False),{'requested':5,'recovered':1,'remaining_after':2,'finished':True})
        self.assertEqual(poll_book(c,p,False)['recovered'],0)

    def test_ready_to_reset_cannot_be_revived(self):
        c=AmmoCounter(10,consumed=9,ready_to_reset=True)
        self.assertEqual(poll_book(c,refill_parameters(10,.3,.5),False)['recovered'],0)
        self.assertEqual(c.remaining,1)

    def test_actual_overridden_recovery_limit_is_not_forced_to_maximum(self):
        c=AmmoCounter(10,consumed=9,recover_limit_override=2)
        self.assertEqual(c.recover(5),2)
        self.assertEqual(c.recover(5),0)

    def test_uid_replacement_and_removal_preserve_consumption_and_recovery(self):
        c=AmmoCounter(10,consumed=9,recovered=7)
        c.set_addition('a',5);c.set_addition('a',7);c.set_addition('b',5)
        self.assertEqual((c.maximum,c.remaining,c.recovered),(22,13,7))
        c.remove_addition('a')
        self.assertEqual((c.maximum,c.remaining,c.consumed,c.recovered),(15,6,9,7))

    def test_dynamic_main_capacity_does_not_modify_extra_counter(self):
        main=AmmoCounter(30,consumed=10);extra=AmmoCounter(30,consumed=12)
        s=ExtraModeCounters(main,{2:extra},2)
        main.set_addition('steal',5)
        self.assertEqual((s.maximum,extra.maximum,s.remaining),(35,30,13))

    def test_mixed_mode_global_remaining_does_not_prove_recoverable_consumption(self):
        s=ExtraModeCounters(AmmoCounter(35,consumed=25),{2:AmmoCounter(35)},2)
        event=poll_book(s,refill_parameters(35,.3,.3),False)
        self.assertEqual((event['requested'],event['recovered'],s.remaining),(11,0,10))

    def test_active_extra_counter_has_its_own_recovery_budget(self):
        main=AmmoCounter(35,consumed=20);extra=AmmoCounter(35,consumed=10,recovered=34)
        s=ExtraModeCounters(main,{2:extra},2)
        event=poll_book(s,refill_parameters(35,.3,.5),False)
        self.assertEqual((event['requested'],event['recovered'],s.remaining),(18,1,6))
        self.assertEqual((main.recovered,extra.recovered),(0,35))

    def test_all_legal_book_orders_keep_counts_but_do_not_choose_trigger_order(self):
        rules=[]
        for rid,ratio in ((BOOK,.3),(YA,.5)):
            params=refill_parameters(10,.3,ratio);params['attack_cost_reference']=1
            rules.append({'kind':'ammo_refill','relic_id':rid,'ammo_parameters':params})
        scenario={'_relic_rules':rules}
        self.assertEqual(ammunition_rounds(10,1,scenario,minimum_interval=1),18)
        cases=scenario['_ammo_refill_reference']['cases']
        self.assertEqual([c['recovered_total'] for c in cases],[8,8])
        self.assertNotEqual(cases[0]['events'],cases[1]['events'])

    def test_two_book_full_cast_counts_cover_both_reference_modes_and_ranks(self):
        for rank in range(1,11):
            for mode in ('continuous','frames'):
                with self.subTest(rank=rank,mode=mode):
                    result=calculate_damage({'operator':'char_1041_angel2','skill':3,
                        'skill_rank':rank,'timing_mode':mode,'relic_ids':[YA,BOOK]})
                    self.assertEqual(result['estimate']['skill']['hit_counts']['技能攻击'],95)
                    self.assertEqual(result['ammo_refill_reference']['attack_count_bounds'],[19,19])
                    self.assertTrue(result['relic_resolution']['complete'])

    def test_repeat_calculation_does_not_consume_supplied_inventory_or_counter(self):
        scenario={'operator':'kaltsit','skill':2,'relic_ids':[BOOK,YA]}
        before=copy.deepcopy(scenario)
        self.assertEqual(calculate_damage(scenario),calculate_damage(scenario))
        self.assertEqual(scenario,before)

    def test_counter_rejects_boolean_and_fractional_capacity(self):
        for maximum in (True,3.5):
            with self.assertRaises(ValueError):AmmoCounter(maximum)

    def test_removing_capacity_preserves_negative_native_raw_remaining(self):
        c=AmmoCounter(10,consumed=12,recovered=1)
        self.assertEqual(c.raw_remaining,-2)
        self.assertEqual(c.remaining,0)
        self.assertIsNone(poll_book(c,refill_parameters(10,.3,.5),False))

    def test_maximum_supported_input_has_room_for_two_recovery_budgets(self):
        rules=[]
        for rid,ratio in ((BOOK,.3),(YA,.5)):
            params=refill_parameters(10000,.3,ratio);params['attack_cost_reference']=1
            rules.append({'kind':'ammo_refill','relic_id':rid,'ammo_parameters':params})
        scenario={'_relic_rules':rules}
        expected=10000+sum(r['ammo_parameters']['refill_count'] for r in rules)
        self.assertEqual(ammunition_rounds(10000,1,scenario,minimum_interval=1),expected)


if __name__=='__main__':unittest.main()
