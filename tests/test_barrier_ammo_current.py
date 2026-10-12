import copy
import unittest
from rouge.barrier_ammo import BarrierAmmoProjection, declared_barrier_ammo
from rouge.damage import calculate_damage
from rouge.estimate import format_estimate
from rouge.shield_timeline import compare_shield_windows, format_shield_windows


class SharedBarrierAmmoTests(unittest.TestCase):
    def test_opening_is_free_and_both_recipients_spend_one_pool(self):
        budget=BarrierAmmoProjection(8)
        self.assertEqual(budget.output()['ammunition_consumed_reference'],0)
        for source in ('owner','structure','structure','owner'):
            event=budget.barrier_break(source)
            self.assertTrue(event['barrier_replenished'])
            self.assertEqual(event['ammunition_consumed'],1)
        self.assertEqual(budget.output()['ammunition_remaining_reference'],4)
        self.assertEqual(budget.output()['source_counts'],{'owner':2,'structure':2})
        # Repeated manual events have ignoreTriggerOnce=true. They do not need
        # a normal attack/cast-end event to reset a one-spell gate.
        self.assertTrue(budget.consumption.triggered)

    def test_last_bullet_replenishes_without_manufacturing_an_end_tick(self):
        budget=BarrierAmmoProjection(1)
        event=budget.barrier_break('structure')
        self.assertTrue(event['barrier_replenished'])
        self.assertEqual(event['remaining'],0)
        extra=budget.barrier_break('owner')
        self.assertFalse(extra['barrier_replenished'])
        self.assertEqual(extra['ammunition_consumed'],0)
        out=budget.output()
        self.assertTrue(out['progress_exhausted_reference'])
        self.assertIsNone(out['skill_finished'])
        self.assertIsNone(out['actual_end_seconds'])
        self.assertFalse(out['events_scheduled'])
        self.assertFalse(budget.counter.ready_to_reset)

    def test_inactive_main_buff_does_not_spend_or_replenish(self):
        budget=BarrierAmmoProjection(8)
        self.assertFalse(budget.barrier_break('owner',skill_active=False)['barrier_replenished'])
        self.assertEqual(budget.output()['inactive_breaks'],1)
        self.assertEqual(budget.output()['ammunition_remaining_reference'],8)

    def test_rank_capacity_and_aggregate_count_preserve_damage_declaration(self):
        for rank,maximum in ((1,5),(4,6),(7,7),(10,8)):
            for count in (0,maximum-1,maximum,maximum+2):
                result=calculate_damage({'operator':'mechanist','skill':2,'skill_rank':rank,
                    'base_attack':1000,'shield_break_count':count})
                ref=result['shield_break_reference'];out=ref['ammunition_budget_reference']
                self.assertEqual(out['maximum'],maximum)
                self.assertEqual(out['ammunition_consumed_reference'],min(count,maximum))
                self.assertEqual(out['ammunition_remaining_reference'],max(0,maximum-count))
                self.assertEqual(out['barrier_replenishments_reference'],min(count,maximum))
                self.assertIsNone(out['source_counts'])
                self.assertEqual(ref['hits_requested'],count)
                self.assertEqual(ref['declared_count_damage_reference'],count*ref['per_hit_damage_reference'])
                self.assertIsNone(ref['actual_end_seconds'])

    def test_window_budget_counts_breaks_not_later_hits_and_shared_end_is_unknown(self):
        scenario={'operator':'mechanist','skill':2,'base_attack':1000,'skill_duration_seconds':20}
        events=[{'source':'structure','break_seconds':1,'hit_seconds':2},
                {'source':'owner','break_seconds':1,'hit_seconds':None},
                {'source':'owner','break_seconds':3,'hit_seconds':4}]
        result=compare_shield_windows(scenario,{'events':events,'windows_seconds':[0,1,2,4,5]})
        self.assertEqual([r['ammunition_budget_reference']['ammunition_consumed_reference'] for r in result['rows']],[0,0,2,3,3])
        self.assertEqual([r['owner_hits']+r['structure_hits'] for r in result['rows']],[0,0,0,1,2])
        self.assertEqual(result['rows'][2]['ammunition_budget_reference']['source_counts'],{'owner':1,'structure':1})
        self.assertIsNone(result['actual_ammunition_consumption'])
        self.assertIsNone(result['actual_end_seconds'])
        self.assertIn('共享补盾耗弹参考2、剩余6',format_shield_windows(result))

    def test_declared_time_order_does_not_invent_per_source_refill_allocation(self):
        # Aggregate budgets are invariant to array order, including same-time
        # events whose actual resolution order remains unverified.
        events=[{'source':'structure' if i%2 else 'owner','break_seconds':1,'hit_seconds':2} for i in range(10)]
        s={'operator':'mechanist','skill':2,'base_attack':1000}
        before=copy.deepcopy((s,events))
        one=compare_shield_windows(s,{'events':events,'windows_seconds':[3]})
        two=compare_shield_windows(s,{'events':list(reversed(events)),'windows_seconds':[3]})
        self.assertEqual(one['rows'],two['rows'])
        self.assertEqual(one['rows'][0]['ammunition_budget_reference']['ammunition_consumed_reference'],8)
        self.assertEqual(one['rows'][0]['owner_hits']+one['rows'][0]['structure_hits'],10)
        self.assertEqual((s,events),before)

    def test_report_shows_conditional_ammo_with_actual_clocks_unknown(self):
        r=calculate_damage({'operator':'mechanist','skill':2,'base_attack':1000,'shield_break_count':3})
        text=format_estimate(r)
        self.assertIn('给定破屏无补弹耗弹参考：3',text)
        self.assertIn('给定破屏无补弹剩余参考：5',text)
        self.assertIn('初始屏障不耗弹',text)
        self.assertIn('isAffecting计数门成立',text)
        self.assertIn('不能由主buff存在推导',text)
        self.assertTrue(r['shield_break_reference']['ammunition_budget_reference']['counting_ability_is_affecting_assumed'])
        self.assertIn('实际结束时刻：未知',text)
        self.assertFalse(r['complete'])

    def test_invalid_budgets_and_sources_are_rejected(self):
        for maximum in (True,0,-1,1.0):
            with self.assertRaises(ValueError):BarrierAmmoProjection(maximum)
        for count in (True,-1,2.0):
            with self.assertRaises(ValueError):declared_barrier_ammo(8,count)
        b=BarrierAmmoProjection(8)
        with self.assertRaises(ValueError):b.barrier_break('enemy')
        with self.assertRaises(ValueError):b.barrier_break('owner',skill_active=1)


if __name__=='__main__':unittest.main()
