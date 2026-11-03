import copy
import unittest

from rouge.catalog import catalog
from rouge.damage import _prepare_damage, calculate_damage
from rouge.operator_engine import Combat, selected_talents

OP = 'char_1015_aglna2'
TALENT = '飘浮大地之上'


def scenario(**extra):
    return {'operator': OP, 'skill': 1, 'elite': 0, 'level': 1,
            'skill_rank': 1, 'base_attack': 1000, 'window_seconds': 10, **extra}


def talent_component(result):
    return next(component for component in result['components'] if component['name'] == TALENT)


class AglnaTalentQualificationTests(unittest.TestCase):
    def test_E0_unlocked_skill_has_no_locked_talent_hits_or_times(self):
        for mode in ('frames', 'continuous'):
            request = scenario(timing_mode=mode)
            self.assertEqual(selected_talents(catalog()['operators'][OP], request)[0], [])
            result = calculate_damage(request)
            component = talent_component(result)
            self.assertEqual((component['hits'], component['per_hit'], component['total']), (0, 0, 0))
            self.assertEqual(component['times_seconds'], [])
            self.assertEqual(result['estimate']['skill']['hit_counts'][TALENT], 0)
            physical = next(c for c in result['components'] if c['name'] == '技能攻击')
            self.assertEqual((physical['hits'], physical['per_hit'], physical['total']), (6, 1600, 9600))
            self.assertEqual(result['total_damage'], 9600)

    def test_E1_E2_exact_source_threshold_and_potential_coefficients_survive(self):
        for elite, potential, light, heavy in ((1, 1, .2, .13), (1, 3, .3, .18),
                                                (2, 1, .35, .25), (2, 3, .45, .3)):
            for mode in ('frames', 'continuous'):
                results = [calculate_damage(scenario(elite=elite, potential=potential,
                               timing_mode=mode, enemy_weight=weight)) for weight in (3, 4)]
                for result in results:
                    component = talent_component(result)
                    self.assertGreater(component['hits'], 0)
                    self.assertEqual(len(component['times_seconds']), component['hits'])
                self.assertAlmostEqual(talent_component(results[0])['per_hit'] /
                                       talent_component(results[1])['per_hit'], light / heavy)

    def test_normal_recharge_plan_uses_the_same_actual_selected_talent_gate(self):
        for mode in ('frames', 'continuous'):
            for elite in (0, 1):
                prepared = _prepare_damage(scenario(elite=elite, timing_mode=mode))
                plan = Combat(prepared[0], prepared[1]).plan(normal=True, window=10)
                component = talent_component(plan)
                if elite == 0:
                    self.assertEqual((component['hits'], component['total'], component['times_seconds']), (0, 0, []))
                else:
                    self.assertGreater(component['hits'], 0)
                self.assertGreater(next(c for c in plan['components'] if c['name'] == '技能攻击')['hits'], 0)

    def test_selected_zero_damage_is_not_mistaken_for_absent_talent(self):
        for mode in ('frames', 'continuous'):
            result = calculate_damage(scenario(elite=1, timing_mode=mode, base_attack=0))
            component = talent_component(result)
            self.assertEqual(component['per_hit'], 0)
            self.assertGreater(component['hits'], 0)
            self.assertGreater(result['estimate']['skill']['hit_counts'][TALENT], 0)
            self.assertTrue(component['times_seconds'])

    def test_zero_window_and_absent_global_enemy_do_not_create_locked_talent_events(self):
        for mode in ('frames', 'continuous'):
            for observation in ({'window_seconds': 0}, {'timing': {'target_disappears_seconds': 0}},
                                {'timing': {'target_windows': []}}):
                result = calculate_damage(scenario(timing_mode=mode, **observation))
                component = talent_component(result)
                self.assertEqual((component['hits'], component['total'], component['times_seconds']), (0, 0, []))
                self.assertEqual(result['estimate']['skill']['hit_counts'][TALENT], 0)

    def test_old_weight_and_training_errors_remain_before_any_event_result(self):
        for value in (True, '4', None, -1, 101, 3.5):
            with self.subTest(weight=value), self.assertRaisesRegex(ValueError, '手动敌人重量'):
                calculate_damage(scenario(enemy_weight=value))
        for options in ({'skill': 2}, {'skill': 3}, {'skill_rank': 10}):
            with self.subTest(options=options), self.assertRaisesRegex(ValueError, '当前精英阶段'):
                calculate_damage(scenario(**options))

    def test_independent_natural_sp_and_selected_enemy_reference_are_retained(self):
        for mode in ('frames', 'continuous'):
            result = calculate_damage(scenario(timing_mode=mode, effects=[{'kind': 'sp_recovery', 'value': .2}],
                enemy_weight=100, target_enemy={'stage_id': 'ro6_n_1_1', 'enemy_id': 'enemy_2133_shdopl', 'level': 0},
                run_config={'difficulty': {'value': 4}}))
            # E0 S1 is deployment-passive; a natural SP rate is inapplicable.
            self.assertIsNone(result['estimate']['skill']['sp_recovery_per_second'])
            self.assertEqual(result['run_resolution']['enemy']['reference_stats']['massLevel'], 0)
            self.assertEqual(talent_component(result)['hits'], 0)
            timed = calculate_damage(scenario(elite=1, skill=2, timing_mode=mode,
                effects=[{'kind': 'sp_recovery', 'value': .2}]))
            self.assertEqual(timed['estimate']['skill']['sp_recovery_per_second'], 1.2)

    def test_retired_combat_relic_stays_reference_while_talent_is_locked(self):
        result = calculate_damage(scenario(relic_ids=['rogue_6_relic_fight_5']))
        record = next(r for r in result['relic_resolution']['records'] if r['id'] == 'rogue_6_relic_fight_5')
        self.assertEqual(record['applied'], [])
        self.assertTrue(record['reference_effects'] or record['reference_pending'])
        self.assertEqual(talent_component(result)['hits'], 0)

    def test_mutating_a_result_does_not_change_source_or_next_public_call(self):
        before = copy.deepcopy(catalog())
        request = scenario()
        original = copy.deepcopy(request)
        result = calculate_damage(request)
        talent_component(result)['hits'] = 999
        talent_component(result)['times_seconds'].append(99)
        self.assertEqual(talent_component(calculate_damage(request))['hits'], 0)
        self.assertEqual(request, original)
        self.assertEqual(catalog(), before)


if __name__ == '__main__':
    unittest.main()
