"""Explicit offline count transitions; no inferred skill callback timeline."""
import unittest

from rouge.ammo_counter import AmmoCounter, ExtraModeCounters, poll_book
from rouge.ammo_reference import refill_parameters


class AmmoCapacity062Tests(unittest.TestCase):
    def test_partial_packet_records_full_expenditure(self):
        counter = AmmoCounter(50, consumed=48)
        counter.consume(5)
        self.assertEqual((counter.consumed, counter.raw_remaining, counter.remaining), (53, -3, 0))
        self.assertIsNone(poll_book(counter, refill_parameters(50, .3, .5), False))

    def test_capacity_loss_never_reduces_past_consumption(self):
        counter = AmmoCounter(35, consumed=39, recovered=2, additions={'target': 5})
        counter.remove_addition('target')
        counter.consume(1)
        self.assertEqual((counter.consumed, counter.raw_remaining, counter.recovered), (40, -5, 2))
        counter.set_addition('target', 5)
        self.assertEqual(counter.remaining, 0)

    def test_raw_expenditure_is_retained_across_recovery_and_capacity_changes(self):
        counter = AmmoCounter(10, consumed=9)
        counter.consume(5)
        self.assertEqual(counter.recover(3), 3)
        self.assertEqual((counter.consumed, counter.recovered, counter.raw_remaining), (11, 3, -1))
        counter.set_addition('capacity', 5)
        self.assertEqual(counter.remaining, 4)

    def test_extra_counter_overconsumption_survives_later_main_capacity_increase(self):
        main = AmmoCounter(35)
        extra = AmmoCounter(35, consumed=34)
        group = ExtraModeCounters(main, {2: extra}, 2)
        extra.consume(5)
        self.assertEqual(group.remaining, 0)
        main.set_addition('target', 5)
        self.assertEqual(group.remaining, 1)

    def test_grown_capacity_rejects_stale_threshold_before_mutation(self):
        counter = AmmoCounter(35, consumed=29)
        old = refill_parameters(35, .3, .5)
        counter.set_addition('target', 5)
        with self.assertRaisesRegex(ValueError, '当前最大弹药'):
            poll_book(counter, old, False)
        self.assertEqual((counter.consumed, counter.recovered), (29, 0))
        # Current maximum 40: floor(40*.3)=12, ceil(40*.5)=20.
        self.assertEqual(poll_book(counter, refill_parameters(40, .3, .5), False),
                         {'requested': 20, 'recovered': 20, 'remaining_after': 31, 'finished': True})

    def test_shrunk_capacity_recomputes_recovery_request(self):
        counter = AmmoCounter(35, consumed=30, additions={'target': 5})
        old = refill_parameters(40, .3, .5)
        counter.remove_addition('target')
        with self.assertRaisesRegex(ValueError, '当前最大弹药'):
            poll_book(counter, old, False)
        event = poll_book(counter, refill_parameters(35, .3, .5), False)
        self.assertEqual((event['requested'], event['recovered'], counter.remaining), (18, 18, 23))

    def test_skill_capacity_and_active_recovery_budget_stay_separate(self):
        main = AmmoCounter(35, consumed=20, additions={'target': 5})
        extra = AmmoCounter(35, consumed=10, recovered=34)
        group = ExtraModeCounters(main, {2: extra}, 2)
        event = poll_book(group, refill_parameters(40, .3, .5), False)
        self.assertEqual(event, {'requested': 20, 'recovered': 1, 'remaining_after': 11, 'finished': True})
        self.assertEqual((main.recovered, extra.recovered), (0, 35))

    def test_finished_book_is_not_reopened_by_capacity_change(self):
        counter = AmmoCounter(35, consumed=30, additions={'target': 5})
        self.assertIsNone(poll_book(counter, refill_parameters(35, .3, .5), True))
        self.assertEqual(counter.recovered, 0)


if __name__ == '__main__':
    unittest.main()
