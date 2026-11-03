"""Four-Sui periodic credits cannot establish a uniform or bound SP clock."""
from copy import deepcopy
import unittest
from rouge.catalog import catalog
from rouge.damage import calculate_damage
from rouge.estimate import format_estimate

SHU = 'char_2025_shu'
GENERAL = ['rogue_6_relic_legacy_' + str(n) for n in (2, 3, 4)]
CYCLE = ('recharge_seconds', 'cycle_seconds', 'cycle_damage', 'cycle_healing', 'cycle_dps', 'cycle_hps')


def evaluate(skill=3, **kwargs):
    return calculate_damage({'operator': SHU, 'skill': skill, 'four_sui': True, **kwargs})


class ShuPeriodicSpReferenceTests(unittest.TestCase):
    def test_unverified_periodic_credit_leaves_resource_and_cycle_unknown(self):
        for mode in ('frames', 'continuous'):
            for skill in (1, 2, 3):
                with self.subTest(mode=mode, skill=skill):
                    r = evaluate(skill, timing_mode=mode)
                    s = r['estimate']['skill']
                    self.assertIsNone(s['initial_seconds'])
                    for key in CYCLE:
                        self.assertIsNone(s[key], key)
                    self.assertEqual(r['timing']['recharge_streams'], [])
                    self.assertFalse(r['timing']['resource_and_damage_shared_clock'])
                    self.assertFalse(r['complete'])
                    self.assertFalse(r['estimate']['complete'])

    def test_original_parameters_do_not_supply_tick_reset_or_lockout_rule(self):
        for potential in (1, 6):
            r = evaluate(potential=potential)
            ref = r['shu_periodic_sp_reference']
            self.assertEqual(ref['interval_seconds_parameter'], 4)
            self.assertEqual(ref['sp_per_pulse_parameter'], 1)
            self.assertEqual(ref['attack_bonus_parameter'], .12)
            for key in ('first_tick_seconds', 'actual_tick_times_seconds', 'clock_origin', 'reset_rule', 'blocked_credit_rule'):
                self.assertIsNone(ref[key], key)
            self.assertFalse(ref['events_scheduled'])
            self.assertFalse(ref['clock_verified'])
            self.assertFalse(ref['native_attachment_verified'])

    def test_qualified_static_attack_and_skill_relative_amounts_survive(self):
        for mode in ('frames', 'continuous'):
            for skill in (1, 2, 3):
                args = {'operator': SHU, 'skill': skill, 'timing_mode': mode, 'window_seconds': 10,
                        'three_professions': True, 'three_same_profession': True}
                r = calculate_damage({**args, 'four_sui': True})
                static = calculate_damage({**args, 'four_sui': False, 'effects': [{'kind': 'attack_pct', 'value': .12}]})
                self.assertEqual(r['estimate']['base_stats'], static['estimate']['base_stats'])
                self.assertEqual(r['attack'], static['attack'])
                self.assertEqual(r['components'], static['components'])
                for key in ('duration_seconds', 'total_damage', 'total_healing', 'phase_damage', 'phase_healing',
                            'window_seconds', 'window_healing', 'window_dps', 'window_hps'):
                    self.assertEqual(r['estimate']['skill'][key], static['estimate']['skill'][key], key)
                self.assertEqual(r['total_damage'], static['total_damage'])
                self.assertEqual(r['total_healing'], static['total_healing'])

    def test_ineligible_elite_and_false_flag_have_no_reference_or_output_change(self):
        for elite, rank, skills in ((0, 1, (1,)), (1, 7, (1, 2))):
            for skill in skills:
                args = {'operator': SHU, 'skill': skill, 'elite': elite, 'skill_rank': rank}
                absent = calculate_damage(args)
                for flag in (True, False):
                    self.assertEqual(calculate_damage({**args, 'four_sui': flag}), absent)
        for skill in (1, 2, 3):
            self.assertEqual(evaluate(skill, four_sui=False), calculate_damage({'operator': SHU, 'skill': skill}))

    def test_inactive_flag_does_not_loan_shu_talent_to_another_operator(self):
        for op in ('kaltsit', 'mechanist', 'char_002_amiya', 'char_298_susuro'):
            p = catalog()['operators'][op]
            for skill in range(1, len(p['skills']) + 1):
                args = {'operator': op, 'skill': skill}
                self.assertEqual(calculate_damage({**args, 'four_sui': True}), calculate_damage(args))

    def test_full_initial_sp_retains_zero_without_claiming_postcast_clock(self):
        for mode in ('frames', 'continuous'):
            for skill in (1, 2, 3):
                r = evaluate(skill, timing_mode=mode, relic_ids=['rogue_6_relic_legacy_99'])
                self.assertEqual(r['estimate']['skill']['initial_seconds'], 0)
                for key in CYCLE:
                    self.assertIsNone(r['estimate']['skill'][key], key)
                self.assertFalse(r['shu_periodic_sp_reference']['clock_verified'])

    def test_enemy_absence_and_zero_window_do_not_erase_independent_friend_sp(self):
        for mode in ('frames', 'continuous'):
            for skill in (1, 2, 3):
                for scenario in ({'window_seconds': 0}, {'timing': {'target_windows': []}},
                                 {'timing': {'target_disappears_seconds': 0}}):
                    r = evaluate(skill, timing_mode=mode, **scenario)
                    self.assertIn('shu_periodic_sp_reference', r)
                    self.assertIsNone(r['estimate']['skill']['initial_seconds'])
                    self.assertIsNone(r['estimate']['skill']['recharge_seconds'])
                    self.assertIsNone(r['estimate']['skill']['cycle_seconds'])
                    if scenario.get('window_seconds') == 0:
                        self.assertEqual(r['total_damage'], 0)
                        self.assertEqual(r['total_healing'], 0)

    def test_independent_natural_and_attack_sp_sources_remain_separate(self):
        for mode in ('frames', 'continuous'):
            r = evaluate(2, timing_mode=mode, relic_ids=[*GENERAL, 'rogue_6_relic_legacy_67'],
                         effects=[{'kind': 'sp_recovery', 'value': .3}])
            self.assertAlmostEqual(r['estimate']['skill']['sp_recovery_per_second'], 2.35)
            record = next(item for item in r['relic_resolution']['records'] if item['id'] == 'rogue_6_relic_legacy_67')
            self.assertEqual(record['status'], 'inapplicable')
            self.assertEqual(record['applied'], [])
            self.assertEqual(record['reference_effects'], [])
            self.assertIsNone(r['estimate']['skill']['initial_seconds'])
            self.assertIsNone(r['estimate']['skill']['recharge_seconds'])
            self.assertAlmostEqual(r['shu_periodic_sp_reference']['independent_sp_clock_reference']['initial_seconds'],
                                   calculate_damage({'operator': SHU, 'skill': 2, 'timing_mode': mode,
                                                     'relic_ids': [*GENERAL, 'rogue_6_relic_legacy_67'],
                                                     'effects': [{'kind': 'sp_recovery', 'value': .3}]})['estimate']['skill']['initial_seconds'])

    def test_retired_callback_sources_remain_references_with_supplied_table(self):
        for mode in ('frames', 'continuous'):
            for identity in ('rogue_6_relic_legacy_118', 'rogue_6_relic_fight_5'):
                args = {'operator': SHU, 'skill': 2, 'timing_mode': mode, 'relic_ids': [identity],
                        'timing': {'sp_events': {'initial': [], 'cycle': []}}}
                r = calculate_damage({**args, 'four_sui': True})
                baseline = calculate_damage({**args, 'four_sui': False})
                self.assertEqual(r['relic_resolution'], baseline['relic_resolution'])
                self.assertEqual(r['relic_resolution']['records'][0]['status'], 'reference_only')
                self.assertNotIn('sp_events', r['estimate'])
                self.assertIsNone(r['estimate']['skill']['initial_seconds'])
                self.assertIsNone(r['estimate']['skill']['cycle_seconds'])

    def test_missing_retired_callback_table_does_not_create_new_missing_conditions(self):
        r = evaluate(2, relic_ids=['rogue_6_relic_legacy_118'])
        self.assertEqual(r['relic_resolution'], evaluate(2, four_sui=False, relic_ids=['rogue_6_relic_legacy_118'])['relic_resolution'])
        self.assertTrue(r['relic_resolution']['complete'])
        self.assertNotIn('sp_events', r['estimate'])
        self.assertIsNone(r['estimate']['skill']['initial_seconds'])
        self.assertIsNone(r['estimate']['skill']['cycle_seconds'])

    def test_module_gate_and_potential_do_not_supply_periodic_clock(self):
        for level, stage in ((59, 3), (60, 1), (60, 3)):
            for potential in (1, 6):
                r = evaluate(level=level, module_id='uniequip_002_shu', module_level=stage, potential=potential)
                self.assertEqual(r['shu_periodic_sp_reference']['interval_seconds_parameter'], 4)
                self.assertIsNone(r['estimate']['skill']['initial_seconds'])
                self.assertIsNone(r['estimate']['skill']['cycle_healing'])

    def test_readonly_report_exposes_periodic_unknown_and_true_natural_rate(self):
        for mode in ('frames', 'continuous'):
            r = evaluate(2, timing_mode=mode)
            section = next(s for s in r['report']['sections'] if s['id'] == 'shu_periodic_sp')
            values = {m['key']: m['value'] for m in section['metrics']}
            self.assertEqual(values['natural_rate'], 1)
            self.assertIsNone(values['first_tick'])
            text = format_estimate(r)
            self.assertIn('天有四时 · 周期技力待核验', text)
            self.assertIn('实际周期首跳：未知', text)
            self.assertIn('不能当作每秒自然回复+0.25', text)
            self.assertIn('结束后充能：未知', text)
            self.assertIn('预计初动：未知', text)
            self.assertNotIn('初动/回转已按模拟帧处理', text)

    def test_input_and_catalog_remain_isolated_between_requests(self):
        request = {'operator': SHU, 'skill': 2, 'four_sui': True, 'timing': {'target_windows': [[0, 10]]}}
        original = deepcopy(request); public = deepcopy(catalog())
        first = calculate_damage(request)
        first['shu_periodic_sp_reference']['interval_seconds_parameter'] = 999
        second = calculate_damage(request)
        self.assertEqual(second['shu_periodic_sp_reference']['interval_seconds_parameter'], 4)
        self.assertEqual(request, original)
        self.assertEqual(catalog(), public)


if __name__ == '__main__':
    unittest.main()
