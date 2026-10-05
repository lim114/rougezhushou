"""Counter behavior checked against native event/slot/config evidence."""
import unittest
from rouge import ammo_counter as counters
from rouge.ammo_reference import refill_parameters
from rouge.relic_events import ammunition_rounds


class AmmoEventsTests(unittest.TestCase):
    def make(self, maximum=8, event=4, cost=1, repeat=False, reset_on_attack=False):
        return counters.AmmoConsumption(counters.AmmoCounter(maximum), event, cost,
            ignore_trigger_once=repeat, reset_when_attack_finished=reset_on_attack)

    def test_s2_charges_at_spell_end_not_spell_start_or_hit(self):
        model = self.make(maximum=35,event=5)
        model.on_cast_start()
        self.assertEqual(model.on_event(4),0)
        self.assertEqual(model.counter.consumed,0)
        self.assertEqual(model.on_event(5),1)
        self.assertEqual(model.on_event(5),0)
        self.assertEqual(model.counter.consumed,1)

    def test_standard_cast_cannot_charge_twice_without_end(self):
        model=self.make()
        for event in (0,2,4,4,5,7):model.on_event(event)
        self.assertEqual(model.counter.consumed,1)
        model.on_event(3)
        self.assertEqual(model.on_event(4),1)

    def test_s1_repeated_spells_consume_each_bullet(self):
        model=self.make(repeat=True)
        for _ in range(3):self.assertEqual(model.on_event(4),1)
        self.assertEqual(model.counter.consumed,3)

    def test_s3_spends_full_packet_without_clamping(self):
        model=self.make(maximum=8,cost=5)
        self.assertEqual(model.ordinary_cast(),5)
        self.assertEqual(model.ordinary_cast(),5)
        self.assertEqual(model.counter.raw_remaining,-2)

    def test_free_cast_still_closes_once_gate(self):
        model=self.make()
        model.not_count_next=True
        self.assertEqual(model.on_event(4),0)
        self.assertTrue(model.triggered)
        model.not_count_next=False
        self.assertEqual(model.on_event(4),0)
        model.on_event(3)
        self.assertEqual(model.on_event(4),1)

    def test_cast_start_resets_ignore_gate_but_not_triggered_gate(self):
        model=self.make(event=5)
        model.ignore_until_cast_end=True
        self.assertEqual(model.on_event(5),0)
        model.on_cast_start()
        self.assertEqual(model.on_event(5),1)
        model.on_cast_start()
        self.assertEqual(model.on_event(5),0)

    def test_detach_clears_flags_without_restoring_ammunition(self):
        model=self.make();model.ordinary_cast()
        model.not_count_next=True;model.ignore_until_cast_end=True;model.triggered=True
        model.on_event(1)
        self.assertFalse(model.not_count_next or model.ignore_until_cast_end or model.triggered)
        self.assertEqual(model.counter.consumed,1)

    def test_attack_finish_reset_is_configured_not_universal(self):
        for reset in (False,True):
            model=self.make(reset_on_attack=reset)
            model.on_event(4);model.on_event(6)
            self.assertEqual(model.on_event(4),int(reset))

    def test_consumption_does_not_invent_ready_or_reset_after_empty(self):
        model=self.make(maximum=1)
        model.ordinary_cast()
        self.assertFalse(model.counter.ready_to_reset)
        self.assertEqual(model.counter.consumed,1)
        model.counter.set_addition('capacity',5)
        self.assertEqual(model.counter.remaining,5)
        self.assertEqual(model.counter.recovered,0)

    def test_refill_respects_actual_consumption_event_and_shared_budget(self):
        model=self.make(maximum=10,event=5)
        model.counter.consume(4)
        params=refill_parameters(10,.5,.5)
        model.on_event(4)
        self.assertIsNone(counters.poll_book(model.counter,params,False))
        model.on_event(5)
        refill=counters.poll_book(model.counter,params,False)
        self.assertEqual(refill['recovered'],5)
        self.assertEqual(model.on_event(5),0)
        self.assertEqual(model.counter.remaining,10)

    def test_binding_uses_actual_event_cost_and_repetition_flags(self):
        expected=[('kaltsit',2,4,1,False),('mechanist',1,4,1,False),
            ('char_1035_wisdel',3,4,1,False),('char_1041_angel2',1,4,1,True),
            ('char_1041_angel2',2,5,1,False),('char_1041_angel2',3,4,5,False)]
        for op,skill,event,cost,repeat in expected:
            with self.subTest(operator=op,skill=skill):
                model=counters.consumption_for(counters.AmmoCounter(40),{'operator':op,'skill':skill},cost)
                self.assertEqual((model.count_event,model.expend_per_trigger,model.ignore_trigger_once),(event,cost,repeat))
                self.assertEqual(model.ordinary_cast(),cost)
        self.assertIsNone(counters.consumption_for(counters.AmmoCounter(8),{'operator':'mechanist','skill':2},1))
        with self.assertRaises(ValueError):
            counters.consumption_for(counters.AmmoCounter(50),{'operator':'char_1041_angel2','skill':3},1)

    def test_bad_event_is_rejected_without_consumption(self):
        model=self.make()
        for value in (True,4.0,-1,'4',None):
            with self.assertRaises(ValueError):model.on_event(value)
        self.assertEqual(model.counter.consumed,0)

    def test_public_round_loop_routes_bound_casts_through_event_counter(self):
        from unittest.mock import patch
        calls=[]
        original=counters.AmmoConsumption.on_event
        def observed(model,event):
            result=original(model,event)
            if result:calls.append((event,result))
            return result
        with patch.object(counters.AmmoConsumption,'on_event',observed):
            rounds=ammunition_rounds(40,1,{'operator':'char_1041_angel2','skill':2})
        self.assertEqual(rounds,40)
        self.assertEqual(calls,[(5,1)]*40)

    def test_midcast_capacity_change_does_not_count_early_or_refund(self):
        model=self.make(maximum=35,event=5)
        model.counter.consume(34)
        model.counter.set_addition('selected_ally',5)
        model.on_event(4)
        self.assertEqual(model.counter.remaining,6)
        model.counter.remove_addition('selected_ally')
        self.assertEqual(model.counter.remaining,1)
        model.on_event(5)
        self.assertEqual(model.counter.remaining,0)
        model.counter.set_addition('selected_ally',5)
        self.assertEqual(model.counter.remaining,5)
        self.assertEqual(model.counter.recovered,0)

    def test_two_modes_have_independent_cast_gates(self):
        main=self.make(maximum=40,event=5)
        extra=self.make(maximum=35,event=5)
        counters_=counters.ExtraModeCounters(main.counter,{2:extra.counter},2)
        main.on_event(5);extra.on_event(5);extra.on_event(5)
        self.assertEqual(counters_.remaining,38)
        extra.on_event(3);extra.on_event(5)
        self.assertEqual(counters_.remaining,37)
        self.assertEqual((main.counter.consumed,extra.counter.consumed),(1,2))


if __name__=='__main__':unittest.main()
