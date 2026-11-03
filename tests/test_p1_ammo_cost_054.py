"""Public ammunition behavior justified by the cached Angel skill notes."""
import copy
import math
import unittest
from pathlib import Path
from unittest.mock import patch

from rouge.damage import calculate_damage

BOOK = 'rogue_6_relic_legacy_139'
YA = 'rogue_6_relic_legacy_140'
ANGEL = 'char_1041_angel2'
ROOT = Path(__file__).resolve().parents[1]


def calc(ids, **options):
    return calculate_damage({'operator': ANGEL, 'skill': 3, 'relic_ids': ids, **options})


def component(result, name):
    return next(c for c in result['components'] if c['name'] == name)


class PartialLastAmmoPacket054Tests(unittest.TestCase):
    def test_cached_primary_skill_notes_prove_partial_packet_and_consumption_callback(self):
        text = (ROOT / '.cache/research/p1-ammo-cost-054/angel-page.html').read_text(encoding='utf-8')
        self.assertIn('即使剩余弹药数小于5发仍可', text)
        self.assertIn('不在乎实际剩余弹药数', text)
        self.assertIn('单轮多次轰炸之间间隔0.1s', text)

    def test_all_ranks_and_reference_modes_allow_fourteen_full_five_shot_attacks(self):
        for rank in range(1, 11):
            for mode in ('frames', 'continuous'):
                with self.subTest(rank=rank, mode=mode):
                    result = calc([BOOK], skill_rank=rank, timing_mode=mode)
                    skill = result['estimate']['skill']
                    self.assertTrue(result['relic_resolution']['complete'])
                    self.assertEqual(skill['hit_counts']['技能攻击'], 70)
                    self.assertEqual(skill['hit_counts']['火力电台本体生命回复'], 70)
                    for key in ('duration_seconds', 'cycle_seconds'):
                        self.assertIsNotNone(skill[key])
                        self.assertTrue(math.isfinite(skill[key]))
                    self.assertIsNone(skill['total_damage'])
                    self.assertIsNone(skill['cycle_dps'])
                    self.assertTrue(math.isfinite(result['known_damage_subtotals']['total_damage']))
                    self.assertTrue(math.isfinite(result['known_damage_subtotals']['cycle_dps']))
                    self.assertGreater(skill['duration_seconds'], calc([], skill_rank=rank, timing_mode=mode)['estimate']['skill']['duration_seconds'])

    def test_final_packet_main_damage_and_talent_attempts_are_full_five(self):
        for mode in ('frames', 'continuous'):
            base = calc([], timing_mode=mode)
            result = calc([BOOK], timing_mode=mode)
            for name in ('技能攻击', '火力电台期望轰炸', '火力电台本体生命回复'):
                with self.subTest(mode=mode, name=name):
                    b = component(base, name)
                    c = component(result, name)
                    self.assertAlmostEqual(c['hits'], b['hits'] * 1.4)
                    self.assertAlmostEqual(c['total'], b['total'] * 1.4)
            self.assertIsNone(result['estimate']['skill']['hit_counts']['投递坐标轰炸'])
            self.assertEqual(result['external_event_reference']['conditional_components'][0]['hits'], 1)
            self.assertEqual(result['estimate']['skill']['hit_counts']['火力电台期望轰炸'], 17.5)

    def test_fifty_percent_refill_retains_fifteen_complete_packets(self):
        for mode in ('frames', 'continuous'):
            result = calc([YA], timing_mode=mode)
            self.assertTrue(result['relic_resolution']['complete'])
            self.assertEqual(result['estimate']['skill']['hit_counts']['技能攻击'], 75)

    def test_time_window_cannot_emit_beyond_the_full_cast_packet_count(self):
        full = calc([BOOK])
        for window in (0, 0.1, 1, 5, 100):
            with self.subTest(window=window):
                result = calc([BOOK], window_seconds=window)
                self.assertTrue(result['relic_resolution']['complete'])
                self.assertLessEqual(result['known_damage_subtotals']['window_damage'],
                                     full['known_damage_subtotals']['window_damage'])
                self.assertEqual(result['known_damage_subtotals']['total_damage'],
                                 full['known_damage_subtotals']['total_damage'])
                self.assertIsNone(result['estimate']['skill']['total_damage'])

    def test_polling_race_is_not_unlocked_by_partial_packet_support(self):
        with patch('rouge.ammo_reference.refill_before_empty_is_safe', return_value=False):
            result = calc([BOOK])
        self.assertFalse(result['relic_resolution']['complete'])
        self.assertIsNone(result['estimate']['skill']['total_damage'])
        self.assertIsNone(result['estimate']['skill']['cycle_seconds'])
        self.assertIsNotNone(result['estimate']['skill']['recharge_seconds'])

    def test_absent_acquisition_order_does_not_choose_a_book_by_list_position(self):
        for ids in ([BOOK, YA], [YA, BOOK]):
            result = calc(ids)
            self.assertTrue(result['relic_resolution']['complete'])
            self.assertEqual(result['estimate']['skill']['hit_counts']['技能攻击'],95)
            reference=result['ammo_refill_reference']
            self.assertFalse(reference['order_verified'])
            self.assertTrue(reference['count_order_invariant'])
            self.assertEqual(reference['attack_count_bounds'],[19,19])
            self.assertEqual({tuple(c['order']) for c in reference['cases']},{(BOOK,YA),(YA,BOOK)})

    def test_recalculation_does_not_consume_relic_or_mutate_supplied_scenario(self):
        scenario = {'operator': ANGEL, 'skill': 3, 'relic_ids': [BOOK]}
        before = copy.deepcopy(scenario)
        first = calculate_damage(scenario)
        second = calculate_damage(scenario)
        self.assertEqual(first, second)
        self.assertEqual(scenario, before)


if __name__ == '__main__':
    unittest.main()
