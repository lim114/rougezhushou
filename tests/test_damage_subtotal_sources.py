"""Subtotal warnings identify the actual pending sources, including combinations."""
from copy import deepcopy
import unittest

from rouge.damage import calculate_damage
from rouge.estimate import format_estimate

OP = 'char_1042_phatm2'
RIVER = 'rogue_6_relic_fight_22'


def evaluate(skill=1, **extra):
    args = {'operator': OP, 'skill': skill, 'base_attack': 1000,
            'relic_ids': [], **extra}
    before = deepcopy(args)
    result = calculate_damage(args)
    assert args == before
    return result


def subtotal(result):
    return next(s for s in result['report']['sections']
                if s['id'] == 'known_damage_subtotals')


class DamageSubtotalSourceTests(unittest.TestCase):
    def test_unselected_river_is_not_named_as_binding_or_incoming_source(self):
        for mode in ('frames', 'continuous'):
            for skill, extra, cause in (
                (1, {}, '束缚倍率首次生效与刷新'),
                (2, {'enemy_attack_count': 20}, '目标普通攻击次数没有事件时刻')):
                with self.subTest(mode=mode, skill=skill):
                    r = evaluate(skill, timing_mode=mode, **extra)
                    notes = '\n'.join(subtotal(r)['notes'])
                    self.assertIn(cause, notes)
                    self.assertIn('不能当作完整', notes)
                    self.assertNotIn('河谷', notes)
                    self.assertNotIn('河谷祭祈', format_estimate(r))
                    self.assertIsNone(r['total_damage'])
                    self.assertFalse(r['complete'])
                    if skill == 1:
                        self.assertEqual(r['known_damage_subtotals']['total_damage'], 3000)
                        self.assertIsNone(r['estimate']['skill']['recharge_seconds'])
                        self.assertIsNone(r['estimate']['skill']['cycle_seconds'])
                    else:
                        self.assertEqual(r['estimate']['skill']['recharge_seconds'], 25)
                        self.assertIsNone(r['estimate']['skill']['cycle_seconds'])

    def test_binding_incoming_and_river_causes_are_all_visible_without_duplicate_subtotal(self):
        for ids in ([], [RIVER]):
            r = evaluate(enemy_attack_count=20, relic_ids=ids)
            notes = '\n'.join(subtotal(r)['notes'])
            self.assertIn('暗夜回声', notes)
            self.assertIn('堕梦', notes)
            self.assertEqual('河谷祭祈' in notes, bool(ids))
            self.assertEqual(r['known_damage_subtotals']['total_damage'], 3000)
            self.assertIsNone(r['total_damage'])
            self.assertEqual(sum(s['id'] == 'known_damage_subtotals'
                                 for s in r['report']['sections']), 1)
            if ids:
                self.assertIn('river_neural', {s['id'] for s in r['report']['sections']})
                self.assertIsNone(r['neural_relic_reference']['window_burst_times'])

    def test_s3_primary_limit_is_preserved_alongside_incoming_and_real_river(self):
        plain = subtotal(evaluate(3))['notes'][0]
        for ids in ([], [RIVER]):
            r = evaluate(3, enemy_attack_count=20, relic_ids=ids)
            notes = subtotal(r)['notes']
            self.assertEqual(notes[0], plain)
            self.assertIn('持续损伤', plain)
            self.assertIn('堕梦', '\n'.join(notes))
            self.assertEqual('河谷祭祈' in '\n'.join(notes), bool(ids))
            self.assertIsNone(r['total_damage'])
            self.assertFalse(r['neural_skill_reference']['secondary_events_scheduled'])

    def test_bait_primary_limit_is_preserved_alongside_incoming_and_real_river(self):
        plain = subtotal(evaluate(2, bait_triggers=1))['notes'][0]
        for ids in ([], [RIVER]):
            r = evaluate(2, bait_triggers=1, enemy_attack_count=20, relic_ids=ids)
            notes = subtotal(r)['notes']
            self.assertEqual(notes[0], plain)
            self.assertIn('诱饵持续效果', plain)
            self.assertIn('堕梦', '\n'.join(notes))
            self.assertEqual('河谷祭祈' in '\n'.join(notes), bool(ids))
            self.assertIsNone(r['total_damage'])
            self.assertIsNone(r['neural_bait_reference']['snapshot_attack'])

    def test_real_river_alone_keeps_its_existing_subtotal_warning_and_numbers(self):
        river_note = '这些数值不包含河谷祭祈未排程的额外持续伤害，不能当作完整总伤或完整 DPS。'
        wine = evaluate(2, relic_ids=[RIVER], initial_neural_buildup=999)
        self.assertEqual(subtotal(wine)['notes'], [river_note])
        r = calculate_damage({'operator': 'char_4204_mantra', 'skill': 2,
            'relic_ids': [RIVER], 'initial_neural_buildup': 999, 'window_seconds': 1})
        self.assertEqual(subtotal(r)['notes'][0],
            '这些数值只包含已保留的本体来源参考，不含未核验的次生事件，不能当作完整输出。')
        self.assertEqual(subtotal(r)['notes'][1:], [river_note])
        self.assertEqual(r['known_damage_subtotals']['window_damage'], 14000.75)
        self.assertIsNone(r['total_damage'])

    def test_absent_sources_and_known_zero_do_not_acquire_pending_source_labels(self):
        r = evaluate(2, enemy_attack_count=0)
        self.assertNotIn('known_damage_subtotals', r)
        self.assertNotIn('neural_incoming_reference', r)
        for timing in ({'target_windows': []}, {'target_disappears_seconds': 0}):
            r = evaluate(timing=timing)
            self.assertEqual(r['total_damage'], 0)
            self.assertNotIn('neural_s1_reference', r)
            self.assertNotIn('河谷祭祈', format_estimate(r))
        r = evaluate(window_seconds=0)
        self.assertEqual(r['total_damage'], 0)
        self.assertEqual(r['known_damage_subtotals']['window_damage'], 0)
        self.assertIsNone(r['estimate']['skill']['total_damage'])
        self.assertIn('暗夜回声', '\n'.join(subtotal(r)['notes']))

    def test_held_river_does_not_take_credit_for_an_unrelated_shield_source(self):
        for mode in ('frames', 'continuous'):
            with self.subTest(mode=mode):
                r = calculate_damage({'operator': 'mechanist', 'skill': 2,
                    'base_attack': 1000, 'shield_break_count': 2,
                    'timing_mode': mode, 'relic_ids': [RIVER]})
                self.assertNotIn('neural_relic_reference', r)
                self.assertNotIn('河谷', '\n'.join(subtotal(r)['notes']))
                self.assertIn('不能当作完整', '\n'.join(subtotal(r)['notes']))
                self.assertIn('河谷祭祈 · 神经机制资料', format_estimate(r))
                self.assertIsNone(r['total_damage'])
                self.assertIsNone(r['estimate']['skill']['total_damage'])
                self.assertIsNone(r['shield_break_reference']['actual_break_times_seconds'])
                self.assertIsNone(r['shield_break_reference']['actual_end_seconds'])
                self.assertEqual(r['shield_break_reference']['declared_count_damage_reference'], 10000)


if __name__ == '__main__':
    unittest.main()
