"""Explicit empty hostile acquisition, without inventing a continuous clock.

Positive continuous ranges retain the existing reference. Permanent attacks,
independently supplied token scopes, friendly healing and unplaced conditional
sources are tested separately; owner absence is not global event absence.
"""
from copy import deepcopy
import unittest

from rouge.damage import calculate_damage
from rouge.estimate import format_estimate
from rouge.reporting import format_report
from rouge.timing import AttackTimeline, charge_seconds


MODES = ('frames', 'continuous')
TOKEN = 'token_10001_deepcl_tentac'
WINE = 'rogue_6_relic_legacy_97'
FINITE_SPEED = 'rogue_6_relic_legacy_105'
MEDICAL = 'char_1037_amiya3'
SNOW = 'char_1046_sbell2'


def request(op='mechanist', skill=1, mode='continuous', **extra):
    return {'operator': op, 'skill': skill, 'base_attack': 1000,
            'enemy_defense': 0, 'enemy_resistance': 0,
            'timing_mode': mode, **extra}


def evaluate(op='mechanist', skill=1, mode='continuous', **extra):
    return calculate_damage(request(op, skill, mode, **extra))


def components(result):
    return {row['name']: row for row in result.get('components', [])}


class EmptyOwnerAcquisition109Tests(unittest.TestCase):
    def test_exact_empty_ordinary_timeline_has_no_hostile_attack_events(self):
        for mode in MODES:
            for normal in (False, True):
                with self.subTest(mode=mode, normal=normal):
                    scenario = request('char_002_amiya', timing={'target_windows': []}, mode=mode)
                    stream = AttackTimeline(scenario, normal=normal).attacks(10, 1)
                    for key in ('start_frames', 'release_frames', 'impact_frames', 'times_seconds'):
                        self.assertEqual(stream[key], [])

    def test_positive_continuous_ranges_keep_reference_instead_of_scheduling_gaps(self):
        scenario = request('char_002_amiya')
        baseline = AttackTimeline(scenario).attacks(10, 1)
        positive = AttackTimeline({**scenario, 'timing': {
            'target_windows': [[2, 3]], 'movement_windows': [[0, 9]],
            'interrupt_windows': [[1, 8]]}}).attacks(10, 1)
        self.assertGreater(len(baseline['times_seconds']), 0)
        self.assertEqual(positive, baseline)

    def test_owner_empty_does_not_cancel_independently_supplied_token(self):
        for mode in MODES:
            with self.subTest(mode=mode):
                baseline = evaluate('char_110_deepcl', mode=mode, summon_count=1, window_seconds=10)
                empty_owner = evaluate('char_110_deepcl', mode=mode, summon_count=1,
                                       window_seconds=10, timing={'target_windows': []})
                self.assertGreater(baseline['total_damage'], 0)
                self.assertEqual(components(empty_owner)['触手'], components(baseline)['触手'])
                self.assertEqual(components(empty_owner)['本体普攻']['total'], 0)
                self.assertGreater(empty_owner['total_damage'], 0)

    def test_token_own_explicit_empty_scope_cancels_only_its_own_events(self):
        for mode in MODES:
            with self.subTest(mode=mode):
                scenario = request('char_110_deepcl', mode=mode)
                baseline = AttackTimeline(scenario).attacks(10, 1, unit=TOKEN)
                empty = AttackTimeline({**scenario, 'timing': {
                    'units': {TOKEN: {'target_windows': []}}}}).attacks(10, 1, unit=TOKEN)
                self.assertGreater(len(baseline['times_seconds']), 0)
                self.assertEqual(empty['times_seconds'], [])
                result = evaluate('char_110_deepcl', mode=mode, summon_count=1, window_seconds=10,
                                  timing={'units': {TOKEN: {'target_windows': []}}})
                self.assertEqual(components(result)['触手']['total'], 0)
                self.assertGreater(components(result)['本体普攻']['total'], 0)
                self.assertGreater(result['total_damage'], 0)

    def test_friendly_healing_keeps_potential_events_when_enemy_scope_is_empty(self):
        for mode in MODES:
            for op, skill in (('kaltsit', 1), ('char_298_susuro', 1), ('char_2025_shu', 2)):
                with self.subTest(mode=mode, op=op):
                    baseline = evaluate(op, skill, mode, window_seconds=10)
                    empty = evaluate(op, skill, mode, window_seconds=10, timing={'target_windows': []})
                    self.assertEqual(empty['total_healing'], baseline['total_healing'])
                    self.assertGreater(empty['total_healing'], 0)
                    self.assertEqual(empty['total_damage'], 0)

    def test_medical_ammo_with_friend_matches_existing_zero_enemy_lifetime_fallback(self):
        for mode in MODES:
            for window in ({}, {'window_seconds': 10}):
                with self.subTest(mode=mode, window=window):
                    empty = evaluate('kaltsit', 2, mode, healing_targets=1,
                                     timing={'target_windows': []}, **window)
                    lifetime = evaluate('kaltsit', 2, mode, healing_targets=1,
                                        timing={'target_disappears_seconds': 0}, **window)
                    self.assertEqual(empty['total_damage'], 0)
                    self.assertEqual(empty.get('healing_hits'), lifetime.get('healing_hits'))
                    for key in ('total_healing', 'window_healing', 'duration_seconds', 'cycle_healing'):
                        self.assertEqual(empty['estimate']['skill'][key], lifetime['estimate']['skill'][key])
                    self.assertGreater(empty['estimate']['skill']['total_healing'], 0)

    def test_medical_ammo_without_recipient_has_no_hit_or_known_ammo_end(self):
        for mode in MODES:
            for window in ({}, {'window_seconds': 10}):
                with self.subTest(mode=mode, window=window):
                    result = evaluate('kaltsit', 2, mode, healing_targets=0,
                                      timing={'target_windows': []}, **window)
                    self.assertEqual(result['hits'], 0)
                    self.assertEqual(result['total_damage'], 0)
                    self.assertIsNone(result['execution_seconds'])
                    self.assertEqual(result['estimate']['skill']['total_healing'], 0)
                    self.assertIsNone(result['estimate']['skill']['duration_seconds'])

    def test_active_healing_recipient_validation_is_retained(self):
        for mode in MODES:
            for count in (-1, 101, .5, True, False):
                with self.subTest(mode=mode, count=count), self.assertRaises(ValueError):
                    evaluate('kaltsit', 2, mode, healing_targets=count,
                             timing={'target_windows': []})

    def test_complete_ammo_count_cannot_overwrite_an_empty_hostile_stream(self):
        for mode in MODES:
            for window in ({}, {'window_seconds': 10}):
                with self.subTest(mode=mode, window=window):
                    baseline = evaluate(mode=mode, **window)
                    result = evaluate(mode=mode, timing={'target_windows': []}, **window)
                    self.assertGreater(baseline['hits'], 0)
                    self.assertEqual((result['hits'], result['total_damage']), (0, 0))
                    self.assertIsNone(result['execution_seconds'])
                    self.assertEqual(result['estimate']['skill']['total_damage'], 0)
                    self.assertIsNone(result['estimate']['skill']['recharge_seconds'])

    def test_finite_deployment_speed_does_not_recreate_empty_ammo_events(self):
        for mode in MODES:
            with self.subTest(mode=mode):
                baseline = evaluate(mode=mode, relic_ids=[FINITE_SPEED])
                empty = evaluate(mode=mode, relic_ids=[FINITE_SPEED], timing={'target_windows': []})
                self.assertGreater(baseline['hits'], 0)
                self.assertEqual((empty['hits'], empty['total_damage']), (0, 0))
                self.assertIsNone(empty['execution_seconds'])
                self.assertEqual(empty['estimate']['skill']['initial_seconds'],
                                 baseline['estimate']['skill']['initial_seconds'])

    def test_initial_and_post_skill_attack_sp_use_separate_empty_supply_inputs(self):
        for mode in MODES:
            with self.subTest(mode=mode):
                scenario = request(mode=mode, timing={'target_windows': []})
                initial = charge_seconds(scenario, 3, 1, 1, 100, initial=True)
                post = charge_seconds(scenario, 3, 1, 1, 100)
                self.assertGreater(initial, 0)
                self.assertIsNone(post)
                scenario['timing'] = {'initial_target_windows': []}
                self.assertIsNone(charge_seconds(scenario, 3, 1, 1, 100, initial=True))
                self.assertGreater(charge_seconds(scenario, 3, 1, 1, 100), 0)

    def test_discrete_wine_initial_credits_survive_without_claiming_empty_ammo_end(self):
        for mode in MODES:
            with self.subTest(mode=mode):
                result = evaluate(mode=mode, relic_ids=[WINE], timing={
                    'target_windows': [], 'initial_target_windows': []})
                self.assertEqual(result['total_damage'], 0)
                self.assertGreater(result['estimate']['skill']['initial_seconds'], 0)
                self.assertIsNone(result['execution_seconds'])
                self.assertIsNone(result['estimate']['skill']['duration_seconds'])
                self.assertIsNone(result['estimate']['skill']['cycle_seconds'])
                self.assertFalse(result['deployment_clock_reference']['live_state_verified'])

    def test_natural_recovery_survives_ordinary_empty_enemy_acquisition(self):
        for mode in MODES:
            with self.subTest(mode=mode):
                # Gnosis S2 uses natural SP, without Amiya's attack-SP talent.
                baseline = evaluate('char_206_gnosis', 2, mode=mode)
                empty = evaluate('char_206_gnosis', 2, mode=mode, timing={
                    'target_windows': [], 'initial_target_windows': []})
                self.assertEqual(empty['total_damage'], 0)
                for key in ('initial_seconds', 'recharge_seconds', 'cycle_seconds'):
                    self.assertEqual(empty['estimate']['skill'][key], baseline['estimate']['skill'][key])

    def test_manual_duration_ordinary_estimate_uses_empty_owner_stream(self):
        for mode in MODES:
            with self.subTest(mode=mode):
                baseline = evaluate(skill=2, mode=mode, skill_duration_seconds=20, shield_break_count=0)
                empty = evaluate(skill=2, mode=mode, skill_duration_seconds=20, shield_break_count=0,
                                 timing={'target_windows': []})
                self.assertGreater(baseline['estimate']['skill']['total_damage'], 0)
                for key in ('total_damage', 'phase_damage', 'cycle_damage', 'window_damage'):
                    self.assertEqual(empty['estimate']['skill'][key], 0)
                self.assertEqual(empty['estimate']['skill']['duration_seconds'], 20)
                self.assertIsNone(empty['shield_break_reference']['actual_end_seconds'])

    def test_owner_empty_does_not_bind_or_cancel_declared_shield_explosion(self):
        for mode in MODES:
            with self.subTest(mode=mode):
                result = evaluate(skill=2, mode=mode, skill_duration_seconds=20,
                                  shield_break_count=2, window_seconds=10,
                                  timing={'target_windows': []})
                reference = result['shield_break_reference']
                self.assertTrue(reference['source_possible']['window'])
                self.assertGreater(reference['declared_count_damage_reference'], 0)
                self.assertIsNone(reference['actual_collision_times_seconds'])
                self.assertIsNone(reference['actual_end_seconds'])
                self.assertIsNone(result['total_damage'])
                for key in ('total_damage', 'phase_damage', 'cycle_damage', 'window_damage'):
                    self.assertEqual(result['known_damage_subtotals'][key], 0)

    def test_invalid_manual_duration_and_hostile_ranges_still_raise(self):
        for mode in MODES:
            for duration in (0, -1, float('nan')):
                with self.subTest(mode=mode, duration=duration), self.assertRaises(ValueError):
                    evaluate(skill=2, mode=mode, skill_duration_seconds=duration,
                             timing={'target_windows': []})
            for windows in (True, False, None, {}, [[True, 1]], [[0, False]], [[1, 1]], [[0]]):
                with self.subTest(mode=mode, windows=windows), self.assertRaises(ValueError):
                    evaluate(mode=mode, timing={'target_windows': windows})

    def test_two_generic_instant_callers_respect_empty_and_preserve_positive_reference(self):
        for mode in MODES:
            for op, skill, name in ((MEDICAL, 2, '慈悲愿景开启伤害'), (SNOW, 1, '施放伤害')):
                with self.subTest(mode=mode, op=op):
                    baseline = evaluate(op, skill, mode, window_seconds=10)
                    empty = evaluate(op, skill, mode, window_seconds=10, timing={'target_windows': []})
                    positive = evaluate(op, skill, mode, window_seconds=10,
                                        timing={'target_windows': [[0, 5], [8, 20]]})
                    self.assertGreater(components(baseline)[name]['total'], 0)
                    self.assertEqual(components(empty)[name]['hits'], 0)
                    self.assertEqual(components(empty)[name]['total'], 0)
                    self.assertEqual(components(positive)[name], components(baseline)[name])

    def test_medical_opening_dependent_healing_is_zero_without_binding_regeneration(self):
        for mode in MODES:
            for count in (0, 1):
                with self.subTest(mode=mode, recipients=count):
                    result = evaluate(MEDICAL, 2, mode, healing_targets=count,
                                      window_seconds=10, timing={'target_windows': []})
                    reference = result['amiya_phase_reference']['window_reference']
                    self.assertEqual(reference['opening_damage_reference'], 0)
                    self.assertEqual(reference['opening_healing_reference'], 0)
                    self.assertEqual(result['known_damage_subtotals']['window_damage'], 0)
                    regeneration = components(result)['诚挚期许本体生命回复']
                    self.assertGreater(regeneration['total'], 0)
                    self.assertIsNone(regeneration['actual_total'])
                    self.assertIsNone(result['amiya_phase_reference']['actual_skill_end_seconds'])

    def test_snow_opening_absence_does_not_cancel_independent_entry_reference(self):
        for mode in MODES:
            with self.subTest(mode=mode):
                result = evaluate(SNOW, 1, mode, snow_entries=2, window_seconds=10,
                                  timing={'target_windows': []})
                self.assertEqual(components(result)['施放伤害']['total'], 0)
                self.assertIsNone(result['total_damage'])
                self.assertTrue(result['external_event_reference']['source_possible'])
                self.assertGreater(result['external_event_reference']['conditional_components'][0]['total'], 0)
                self.assertIsNone(result['external_event_reference']['actual_event_times_seconds'])
                self.assertEqual(result['known_damage_subtotals']['window_damage'], 0)

    def test_gnosis_separate_instant_gate_respects_empty_and_zero_observation(self):
        for mode in MODES:
            with self.subTest(mode=mode):
                baseline = evaluate('char_206_gnosis', 2, mode, window_seconds=10)
                self.assertGreater(baseline['total_damage'], 0)
                for extra in ({'timing': {'target_windows': []}}, {'window_seconds': 0},
                              {'timing': {'target_disappears_seconds': 0}}):
                    result = evaluate('char_206_gnosis', 2, mode, **extra)
                    self.assertEqual(result['total_damage'], 0)

    def test_permanent_attack_and_sp_reference_remain_excluded_from_ordinary_fix(self):
        # Full original/candidate native replay covers all 40 permanent controls.
        # This deliberately asserts the narrower existing continuous contract;
        # release/impact separation belongs to a later independently proved fix.
        for skill in (1, 3):
            for relic_ids in ([], ['rogue_6_relic_legacy_67'], [FINITE_SPEED]):
                with self.subTest(skill=skill, relic_ids=relic_ids):
                    baseline = evaluate('char_4182_oblvns', skill, relic_ids=relic_ids, window_seconds=10)
                    empty = evaluate('char_4182_oblvns', skill, relic_ids=relic_ids, window_seconds=10,
                                     timing={'target_windows': [], 'initial_target_windows': []})
                    self.assertEqual(empty['components'], baseline['components'])
                    self.assertEqual(empty['estimate']['skill'], baseline['estimate']['skill'])

    def test_public_callers_and_both_formatters_remain_read_only(self):
        for scenario in (request(timing={'target_windows': []}),
                         request('kaltsit', 2, timing={'target_windows': []}, healing_targets=1),
                         request(MEDICAL, 2, timing={'target_windows': []}, window_seconds=10),
                         request(SNOW, 1, timing={'target_windows': []}, snow_entries=2)):
            before = deepcopy(scenario)
            result = calculate_damage(scenario)
            self.assertEqual(scenario, before)
            result_before = deepcopy(result)
            for formatter in (format_estimate, format_report):
                self.assertIsInstance(formatter(result), str)
                self.assertEqual(result, result_before)


if __name__ == '__main__':
    unittest.main()
