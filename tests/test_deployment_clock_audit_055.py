"""Independent bounded audit of deployment-time relics against native receipts.

Timer facts: p1-native-runtime-054/timer-book-sniper-summary.json.
Therapy facts: rouge/data/native-relic-reference.json. Literal expectations
below are hand-counted schedules; these are not live-client timing oracles.
"""
import copy
import math
import unittest

from rouge.catalog import catalog
from rouge.damage import calculate_damage
from rouge.timing import AttackTimeline, periodic_charge_seconds, wine_events


THERAPY = ['rogue_6_relic_legacy_105', 'rogue_6_relic_legacy_106']
WINES = ['rogue_6_relic_legacy_95', 'rogue_6_relic_legacy_96', 'rogue_6_relic_legacy_97']
WINE_RULES = [
    {'kind': 'periodic_sp', 'value': 1, 'interval': 3, 'clock': 'deployment'},
    {'kind': 'periodic_sp', 'value': 1, 'interval': 2.5, 'clock': 'deployment'},
    {'kind': 'periodic_sp', 'value': 1, 'interval': 1.5, 'clock': 'deployment'},
]
THERAPY_RULES = [
    {'kind': 'deployment_attack_speed', 'value': 40, 'duration': 10},
    {'kind': 'deployment_attack_speed', 'value': 70, 'duration': 10},
]


class DeploymentClockIndependentAudit055(unittest.TestCase):
    def test_two_therapy_instances_add_110_and_expire_at_deployment_10_seconds(self):
        for mode in ('frames', 'continuous'):
            for age, expected in ((0, 210), (9.99, 210), (10, 100), (20, 100)):
                with self.subTest(mode=mode, age=age):
                    result = calculate_damage({'operator': 'mechanist', 'skill': 1,
                        'timing_mode': mode, 'relic_ids': THERAPY,
                        'deployment_elapsed_seconds': age})
                    self.assertEqual(result['estimate']['base_stats']['attack_speed'], expected)
                    self.assertEqual(result['deployment_buff_reference']['permanent_attack_speed'], 100)
                    self.assertFalse(result['deployment_buff_reference']['live_state_verified'])

    def test_first_attack_charging_benefits_before_skill_activation(self):
        # Mechanist's ordinary 1.2s interval is 36 frames. Explicit zero
        # windup isolates cadence: seven releases at 0,36,...216 vs 0,17,...102;
        # attack SP becomes usable on the next reference frame.
        scenario = {'operator': 'mechanist', 'skill': 1,
                    'timing': {'windup_frames': 0, 'recovery_frames': 0}}
        for mode, ordinary, improved in (('frames', 217/30, 103/30),
                                         ('continuous', 8.4, 4)):
            with self.subTest(mode=mode):
                baseline = calculate_damage({**scenario, 'timing_mode': mode})
                result = calculate_damage({**scenario, 'timing_mode': mode, 'relic_ids': THERAPY})
                self.assertAlmostEqual(baseline['estimate']['skill']['initial_seconds'], ordinary)
                self.assertAlmostEqual(result['estimate']['skill']['initial_seconds'], improved)
                self.assertAlmostEqual(result['deployment_clock_reference']['first_skill_start_seconds'], improved)

    def test_skill_start_after_10_seconds_has_no_temporary_speed_or_output_gain(self):
        for mode in ('frames', 'continuous'):
            with self.subTest(mode=mode):
                scenario = {'operator': 'kaltsit', 'skill': 3, 'timing_mode': mode}
                baseline = calculate_damage(scenario)
                result = calculate_damage({**scenario, 'relic_ids': THERAPY})
                a, b = baseline['estimate']['skill'], result['estimate']['skill']
                self.assertEqual(b['initial_seconds'], 15)
                for key in ('skill_attack_speed', 'total_damage', 'total_healing',
                            'cycle_damage', 'cycle_healing', 'recharge_seconds', 'cycle_seconds'):
                    self.assertEqual(a[key], b[key], key)

    def test_recharge_timeline_uses_original_deployment_origin_not_new_10_seconds(self):
        # Initial skill starts at deployment age4. A normal charge phase
        # beginning 12s after that is at age16 and receives neither finite buff.
        for mode in ('frames', 'continuous'):
            with self.subTest(mode=mode):
                scenario = {'operator': 'mechanist', 'skill': 1, 'timing_mode': mode,
                    '_deployment_skill_start_seconds': 4, '_relic_rules': THERAPY_RULES,
                    'timing': {'windup_frames': 0, 'recovery_frames': 0}}
                expired = AttackTimeline(scenario, normal=True, offset=12).attacks(4, 1, 100)
                ordinary = AttackTimeline({**scenario, '_relic_rules': []}, normal=True,
                                          offset=12).attacks(4, 1, 100)
                self.assertEqual(expired['times_seconds'], ordinary['times_seconds'])
                self.assertEqual(expired['start_frames'], ordinary['start_frames'])
                self.assertEqual(expired['interval_frames'], 30)

    def test_real_early_summoner_own_speed_changes_but_tentacles_do_not_inherit_it(self):
        # S2 starts at 8+1/3 s: initial60 + three wine birth SP10, cost80,
        # plus vanilla sarsaparilla natural recovery1.2. A real token path
        # receives no eight-profession-only therapy selector.
        scenario = {'operator': 'char_110_deepcl', 'skill': 2,
                    'relic_ids': WINES + ['rogue_6_relic_legacy_2']}
        for mode in ('frames', 'continuous'):
            with self.subTest(mode=mode):
                baseline = calculate_damage({**scenario, 'timing_mode': mode})
                result = calculate_damage({**scenario, 'timing_mode': mode,
                                           'relic_ids': scenario['relic_ids'] + THERAPY})
                self.assertAlmostEqual(result['estimate']['skill']['initial_seconds'], 25/3)
                components = {c['name']: c for c in baseline['components']}
                boosted = {c['name']: c for c in result['components']}
                self.assertGreater(boosted['本体普攻']['hits'], components['本体普攻']['hits'])
                for key in ('hits', 'per_hit', 'total', 'times_seconds'):
                    self.assertEqual(boosted['触手'][key], components['触手'][key], key)

    def test_three_wines_keep_separate_timers_and_all_birth_sp(self):
        # 3s:5 pulses; 2.5s:6; 1.5s:10 through 15s inclusive.
        scenario = {'operator': 'mechanist', 'skill': 1, '_relic_rules': WINE_RULES}
        events = sorted(wine_events(scenario, 451, initial=True))
        self.assertEqual(len(events), 21)
        self.assertEqual(events[:4], [(45, 1), (75, 1), (90, 1), (90, 1)])
        self.assertEqual(events[-3:], [(450, 1)] * 3)
        result = calculate_damage({'operator': 'mechanist', 'skill': 1,
            'relic_ids': WINES, 'continuous_attacks': False})
        skill = result['estimate']['skill']
        self.assertEqual(skill['initial_sp'], 10)
        self.assertEqual(skill['initial_seconds'], 0)
        # Reference skill ends at frame250. Credits270x2,300,315,360x2,375
        # reach seven at375 (12.5s from deployment), not a restarted phase.
        self.assertAlmostEqual(skill['duration_seconds'], 250/30)
        self.assertAlmostEqual(skill['recharge_seconds'], 125/30)
        self.assertEqual(skill['cycle_seconds'], 12.5)
        self.assertNotIn('initial_seconds_range', skill)

    def test_blocked_wine_timers_advance_and_continuous_mode_keeps_extra_lockout(self):
        # Both reference modes reach seven at deployment15s with this block.
        # Continuous skill ends7.5s; block ends9+1/6. Then10,10.5,12x2,
        # 12.5,13.5,15x3 give >=7. Nothing from the block is banked.
        for mode, duration in (('frames', 25/3), ('continuous', 7.5)):
            with self.subTest(mode=mode):
                result = calculate_damage({'operator': 'mechanist', 'skill': 1,
                    'timing_mode': mode, 'continuous_attacks': False, 'relic_ids': WINES,
                    'timing': {'sp_lockout_extra_seconds': 5/3}})
                skill = result['estimate']['skill']
                self.assertAlmostEqual(skill['duration_seconds'], duration)
                self.assertAlmostEqual(skill['cycle_seconds'], 15)
                self.assertAlmostEqual(skill['recharge_seconds'], 15-duration)

    def test_owner_pulse_at_exact_end_frame_is_discarded_before_basic_skill_end(self):
        scenario = {'operator': 'mechanist', 'skill': 1, '_relic_rules': [WINE_RULES[0]],
                    'continuous_attacks': False}
        # Skill ends at exactly3s: the BuffContainer's pulse still sees blocked
        # SP before BasicSkill ends it. The next permissible pulse is6s.
        self.assertEqual(wine_events(scenario, 100, offset=3), [(90, 1)])
        self.assertAlmostEqual(periodic_charge_seconds(scenario, 1, 0, 1, 100, offset=3), 3)
        # Moving the block end one reference frame earlier makes the3s pulse
        # eligible, so the charge takes just that one frame.
        self.assertAlmostEqual(periodic_charge_seconds(scenario, 1, 0, 1, 100,
                                                       offset=89/30), 1/30)

    def test_phase_continues_through_skill_and_irregular_end_not_period_reset(self):
        scenario = {'operator': 'mechanist', 'skill': 1, '_relic_rules': WINE_RULES,
            '_deployment_skill_start_seconds': 1, 'continuous_attacks': False}
        # End at deployment3.1:4.5,5,6x2,7.5x2,9x2 reach >=7 at9s.
        for mode in ('frames', 'continuous'):
            with self.subTest(mode=mode):
                self.assertAlmostEqual(periodic_charge_seconds({**scenario, 'timing_mode': mode},
                    7, 0, 1, 100, offset=2.1), 5.9)

    def test_all_87_skills_public_interface_both_modes_keep_unknowns_and_input_isolation(self):
        count = 0
        for operator, profile in catalog()['operators'].items():
            for number in range(1, len(profile['skills']) + 1):
                count += 1
                for mode in ('frames', 'continuous'):
                    with self.subTest(operator=operator, skill=number, mode=mode):
                        scenario = {'operator': operator, 'skill': number, 'timing_mode': mode,
                                    'relic_ids': THERAPY + WINES}
                        before = copy.deepcopy(scenario)
                        result = calculate_damage(scenario)
                        self.assertEqual(scenario, before)
                        skill = result['estimate']['skill']
                        first = skill['initial_seconds']
                        if first is not None:
                            self.assertTrue(math.isfinite(first) and first >= 0)
                            self.assertAlmostEqual(result['deployment_clock_reference']['first_skill_start_seconds'], first)
                        for key in ('initial_seconds', 'recharge_seconds', 'cycle_seconds',
                                    'total_damage', 'total_healing', 'cycle_dps', 'cycle_hps'):
                            value = skill[key]
                            if value is not None:
                                self.assertTrue(math.isfinite(value) and value >= 0, key)
                        # Continuous estimate.complete is a formula-scope flag,
                        # not a claim of live animation/hotfix verification.
                        self.assertFalse(result.get('deployment_clock_reference', {}).get('live_state_verified', False))
        self.assertEqual(count, 87)


if __name__ == '__main__':
    unittest.main()
