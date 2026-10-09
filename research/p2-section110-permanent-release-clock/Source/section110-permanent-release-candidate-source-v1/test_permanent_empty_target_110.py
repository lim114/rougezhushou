"""Permanent release/SP reference survives explicit empty hostile impact supply.

This does not bind independent note collisions or create positive continuous
range scheduling. Complete old/candidate public records are compared by Root.
"""
from copy import deepcopy
import unittest

from rouge.catalog import catalog
from rouge.damage import calculate_damage
from rouge.estimate import format_estimate
from rouge.reporting import format_report
from rouge.relics import prepare
from rouge.sp_events import charge as event_charge
from rouge.timing import AttackTimeline, FPS, charge_seconds, mixed_charge_seconds


OP = 'char_4182_oblvns'
MODES = ('frames', 'continuous')
ATTACK_SP = 'rogue_6_relic_legacy_67'
FINITE_SPEED = 'rogue_6_relic_legacy_105'
WINE = 'rogue_6_relic_legacy_97'
HORN = 'rogue_6_relic_fight_5'
CLOCK_KEYS = ('initial_seconds', 'recharge_seconds', 'cycle_seconds', 'duration_seconds')
SUPPLIES = ({}, {'target_windows': []}, {'initial_target_windows': []},
            {'target_windows': [], 'initial_target_windows': []})


def request(skill=3, mode='continuous', **extra):
    return {'operator': OP, 'skill': skill, 'elite': 2, 'level': 90,
            'skill_rank': 10, 'trust': 100, 'potential': 1, 'base_attack': 1000,
            'enemy_defense': 0, 'enemy_resistance': 0,
            'timing_mode': mode, **extra}


def evaluate(skill=3, mode='continuous', **extra):
    return calculate_damage(request(skill, mode, **extra))


def prepared(skill=3, mode='continuous', **extra):
    return prepare(request(skill, mode, **extra), catalog()['operators'][OP])[0]


def float_bits(values):
    return [value.hex() for value in values]


def timing_report(result):
    return next(section for section in result['report']['sections']
                if section['id'] == 'timing')


class PermanentEmptyTarget110Tests(unittest.TestCase):
    def assertSameSP(self, empty, baseline):
        for key in CLOCK_KEYS:
            self.assertEqual(empty['estimate']['skill'][key], baseline['estimate']['skill'][key])
        self.assertEqual(empty['estimate'].get('sp_events'), baseline['estimate'].get('sp_events'))
        self.assertEqual(timing_report(empty), timing_report(baseline))

    def test_continuous_empty_keeps_release_and_clears_only_impact(self):
        for skill in (1, 3):
            with self.subTest(skill=skill):
                scenario = request(skill)
                baseline = AttackTimeline(scenario).attacks(10, .73)
                empty = AttackTimeline({**scenario, 'timing': {'target_windows': []}}).attacks(10, .73)
                self.assertGreater(len(baseline['times_seconds']), 0)
                self.assertEqual(empty['start_frames'], baseline['start_frames'])
                self.assertEqual(empty['release_frames'], baseline['release_frames'])
                self.assertEqual(float_bits(empty['release_times_seconds']), float_bits(baseline['times_seconds']))
                self.assertEqual(empty['resume_frame'], baseline['resume_frame'])
                self.assertEqual((empty['impact_frames'], empty['times_seconds']), ([], []))
                self.assertNotIn('release_times_seconds', baseline)

    def test_release_float_clock_is_not_reconstructed_from_quantized_frames(self):
        scenario = request(timing={'target_windows': []})
        stream = AttackTimeline(scenario).attacks(10, .73)
        self.assertNotEqual(float_bits(stream['release_times_seconds']),
                            float_bits([frame / FPS for frame in stream['release_frames']]))

    def test_finite_deployment_speed_preserves_exact_release_steps_and_origin(self):
        scenario = prepared(relic_ids=[FINITE_SPEED])
        baseline = AttackTimeline(scenario).attacks(20, .73, 100, attribute_speed=100)
        empty = AttackTimeline({**scenario, 'timing': {'target_windows': []}}).attacks(
            20, .73, 100, attribute_speed=100)
        self.assertEqual(float_bits(empty['release_times_seconds']), float_bits(baseline['times_seconds']))
        for key in ('start_frames', 'release_frames', 'interval_frames_by_attack',
                    'deployment_origin_seconds', 'resume_frame'):
            self.assertEqual(empty[key], baseline[key])
        self.assertEqual(empty['times_seconds'], [])
        self.assertEqual(empty['impact_frames'], [])

    def test_frames_keep_existing_permanent_releases_and_no_continuous_float_field(self):
        for skill in (1, 3):
            with self.subTest(skill=skill):
                scenario = request(skill, 'frames', timing={'windup_frames': 6, 'recovery_frames': 9})
                baseline = AttackTimeline(scenario).attacks(10, 1)
                empty = AttackTimeline({**scenario, 'timing': {
                    **scenario['timing'], 'target_windows': []}}).attacks(10, 1)
                self.assertGreater(len(baseline['release_frames']), 0)
                for key in ('start_frames', 'release_frames', 'resume_frame'):
                    self.assertEqual(empty[key], baseline[key])
                self.assertEqual(empty['times_seconds'], [])
                self.assertNotIn('release_times_seconds', empty)

    def test_missing_and_positive_continuous_ranges_keep_original_stream_shape(self):
        scenario = request()
        baseline = AttackTimeline(scenario).attacks(10, .73)
        positive = AttackTimeline({**scenario, 'timing': {
            'target_windows': [[2, 3]], 'movement_windows': [[0, 9]],
            'interrupt_windows': [[1, 8]]}}).attacks(10, .73)
        self.assertEqual(positive, baseline)
        self.assertNotIn('release_times_seconds', positive)

    def test_global_zero_enemy_lifetime_keeps_original_no_release_contract(self):
        for mode in MODES:
            with self.subTest(mode=mode):
                stream = AttackTimeline(request(mode=mode, timing={
                    'target_windows': [], 'target_disappears_seconds': 0})).attacks(10, 1)
                for key in ('times_seconds', 'impact_frames'):
                    self.assertEqual(stream[key], [])
                if mode == 'continuous':
                    self.assertEqual(stream['release_frames'], [])
                else:
                    # Existing framed permanent releases ignore acquisition;
                    # zero lifetime filters impacts, not the release clock.
                    baseline = AttackTimeline(request(mode=mode)).attacks(10, 1)
                    self.assertEqual(stream['release_frames'], baseline['release_frames'])
                self.assertNotIn('release_times_seconds', stream)
                result = evaluate(mode=mode, timing={'target_disappears_seconds': 0})
                self.assertEqual(result['total_damage'], 0)

    def test_friendly_scope_is_not_filtered_as_a_hostile_permanent_impact(self):
        for mode in MODES:
            with self.subTest(mode=mode):
                baseline = AttackTimeline(request(mode=mode), target_scope='friendly').attacks(10, 1)
                empty = AttackTimeline(request(mode=mode, timing={'target_windows': []}),
                                       target_scope='friendly').attacks(10, 1)
                self.assertEqual(empty['times_seconds'], baseline['times_seconds'])
                self.assertEqual(empty['release_frames'], baseline['release_frames'])
                self.assertNotIn('release_times_seconds', empty)

    def test_independent_unit_scope_does_not_inherit_owner_permanent_exemption(self):
        unit = 'token_10001_deepcl_tentac'
        for mode in MODES:
            with self.subTest(mode=mode):
                owner = request(mode=mode, timing={'target_windows': []})
                inherited = AttackTimeline(owner).attacks(10, 1, unit=unit)
                explicit = AttackTimeline({**owner, 'timing': {
                    'target_windows': [], 'units': {unit: {'target_windows': []}}}}).attacks(10, 1, unit=unit)
                self.assertGreater(len(inherited['times_seconds']), 0)
                self.assertEqual(explicit['release_frames'], [])
                self.assertEqual(explicit['times_seconds'], [])
                self.assertNotIn('release_times_seconds', explicit)

    def test_attack_charge_uses_original_releases_in_initial_and_post_skill_scopes(self):
        for mode in MODES:
            for initial in (False, True):
                for relic_ids in ([], [ATTACK_SP], [FINITE_SPEED], [ATTACK_SP, FINITE_SPEED]):
                    with self.subTest(mode=mode, initial=initial, relic_ids=relic_ids):
                        baseline = prepared(mode=mode, relic_ids=relic_ids)
                        empty = prepared(mode=mode, relic_ids=relic_ids,
                                         timing={'target_windows': [], 'initial_target_windows': []})
                        original = charge_seconds(baseline, 13, 1, .73, 100, initial=initial,
                                                  attribute_speed=100)
                        observed = charge_seconds(empty, 13, 1, .73, 100, initial=initial,
                                                  attribute_speed=100)
                        self.assertGreater(original, 0)
                        self.assertEqual(observed.hex(), original.hex())

    def test_mixed_charge_preserves_original_release_precision_and_blocking(self):
        for mode in MODES:
            for initial in (False, True):
                for relic_ids in ([], [ATTACK_SP], [FINITE_SPEED]):
                    with self.subTest(mode=mode, initial=initial, relic_ids=relic_ids):
                        plain = prepared(mode=mode, relic_ids=relic_ids)
                        empty = prepared(mode=mode, relic_ids=relic_ids,
                                         timing={'target_windows': [], 'initial_target_windows': []})
                        params = dict(initial=initial, blocked_seconds=.2, attribute_speed=100)
                        baseline = mixed_charge_seconds(plain, 13, .7, 2, .73, 100, **params)
                        observed = mixed_charge_seconds(empty, 13, .7, 2, .73, 100, **params)
                        self.assertGreater(baseline, 0)
                        self.assertEqual(observed.hex(), baseline.hex())

    def test_classified_event_sp_consumes_release_clock_without_fabricating_callbacks(self):
        skill = catalog()['operators'][OP]['skills'][2]['levels'][9]
        for mode in MODES:
            for initial in (False, True):
                for wait_next_attack in (False, True):
                    with self.subTest(mode=mode, initial=initial, wait_next_attack=wait_next_attack):
                        phases = {'initial': [], 'cycle': []}
                        plain = prepared(mode=mode, relic_ids=[HORN, ATTACK_SP],
                                         timing={'sp_events': phases})
                        empty = prepared(mode=mode, relic_ids=[HORN, ATTACK_SP], timing={
                            'sp_events': phases, 'target_windows': [], 'initial_target_windows': []})
                        params = dict(initial=initial, wait_next_attack=wait_next_attack,
                                      attribute_speed=100)
                        baseline = event_charge(plain, skill, 13, 0, .73, 100, **params)
                        observed = event_charge(empty, skill, 13, 0, .73, 100, **params)
                        self.assertIsNotNone(baseline['seconds'])
                        self.assertEqual(observed, baseline)
                        self.assertEqual(observed['credited_callback_events'], 0)

    def test_public_initial_post_and_both_empty_keep_all_sp_fields_and_report(self):
        for mode in MODES:
            for skill in (1, 3):
                for relic_ids in ([], [ATTACK_SP], [FINITE_SPEED], [ATTACK_SP, FINITE_SPEED]):
                    with self.subTest(mode=mode, skill=skill, relic_ids=relic_ids):
                        baseline = evaluate(skill, mode, relic_ids=relic_ids, window_seconds=10)
                        for timing in SUPPLIES[1:]:
                            empty = evaluate(skill, mode, relic_ids=relic_ids,
                                             window_seconds=10, timing=timing)
                            self.assertSameSP(empty, baseline)

    def test_initial_only_empty_keeps_skill_hits_and_complete_component_values(self):
        for mode in MODES:
            for relic_ids in ([], [ATTACK_SP], [FINITE_SPEED]):
                with self.subTest(mode=mode, relic_ids=relic_ids):
                    baseline = evaluate(mode=mode, relic_ids=relic_ids, window_seconds=10)
                    initial = evaluate(mode=mode, relic_ids=relic_ids, window_seconds=10,
                                       timing={'initial_target_windows': []})
                    self.assertGreater(baseline['total_damage'], 0)
                    self.assertEqual(initial['components'], baseline['components'])
                    self.assertEqual(initial['total_damage'], baseline['total_damage'])
                    self.assertEqual(initial['estimate']['skill'], baseline['estimate']['skill'])

    def test_known_s3_skill_and_normal_cycle_damage_are_zero_without_hostile_impacts(self):
        for mode in MODES:
            for relic_ids in ([], [ATTACK_SP], [FINITE_SPEED]):
                with self.subTest(mode=mode, relic_ids=relic_ids):
                    baseline = evaluate(mode=mode, relic_ids=relic_ids, window_seconds=10)
                    empty = evaluate(mode=mode, relic_ids=relic_ids, window_seconds=10,
                                     timing={'target_windows': []})
                    self.assertGreater(baseline['total_damage'], 0)
                    self.assertSameSP(empty, baseline)
                    self.assertEqual(empty['total_damage'], 0)
                    for key in ('total_damage', 'phase_damage', 'cycle_damage'):
                        self.assertEqual(empty['estimate']['skill'][key], 0)
                    for before, after in zip(baseline['components'], empty['components'], strict=True):
                        self.assertEqual(after['per_hit'], before['per_hit'])
                        self.assertEqual((after['hits'], after['total'], after['times_seconds']), (0, 0, []))

    def test_s1_independent_note_parameters_and_unknown_actual_clocks_survive(self):
        for mode in MODES:
            for relic_ids in ([], [ATTACK_SP], [FINITE_SPEED]):
                with self.subTest(mode=mode, relic_ids=relic_ids):
                    baseline = evaluate(1, mode, relic_ids=relic_ids, window_seconds=10)
                    empty = evaluate(1, mode, relic_ids=relic_ids, window_seconds=10,
                                     timing={'target_windows': [], 'initial_target_windows': []})
                    self.assertSameSP(empty, baseline)
                    self.assertEqual(empty['components'], baseline['components'])
                    self.assertEqual(empty['unbound_cast_reference'], baseline['unbound_cast_reference'])
                    self.assertIsNone(empty['total_damage'])
                    self.assertIsNone(empty['unbound_cast_reference']['actual_hit_times_seconds'])
                    self.assertIsNone(empty['unbound_cast_reference']['actual_end_seconds'])
                    self.assertFalse(empty['complete'])
                    self.assertFalse(empty['timing']['resource_and_damage_shared_clock'])

    def test_s2_piano_and_organ_modes_clear_known_impacts_and_keep_initial_sp(self):
        for mode in MODES:
            for organ_mode in (False, True):
                for fever in (False, True):
                    with self.subTest(mode=mode, organ_mode=organ_mode, fever=fever):
                        options = dict(organ_mode=organ_mode, fever=fever, window_seconds=10)
                        baseline = evaluate(2, mode, **options)
                        empty = evaluate(2, mode, timing={'target_windows': []}, **options)
                        self.assertGreater(baseline['total_damage'], 0)
                        self.assertSameSP(empty, baseline)
                        self.assertEqual(empty['total_damage'], 0)
                        self.assertTrue(all(row['hits'] == 0 and row['times_seconds'] == []
                                            for row in empty['components']))

    def test_s2_switch_end_and_repeatable_cycle_stay_unknown(self):
        for mode in MODES:
            for organ_mode in (False, True):
                with self.subTest(mode=mode, organ_mode=organ_mode):
                    result = evaluate(2, mode, organ_mode=organ_mode, window_seconds=10,
                                      timing={'target_windows': [], 'initial_target_windows': []})
                    for key in ('duration_seconds', 'cycle_seconds'):
                        self.assertIsNone(result['estimate']['skill'][key])
                    self.assertEqual(result['estimate']['skill']['window_seconds'], 10)

    def test_declared_no_continuous_attacks_does_not_gain_attack_sp_from_preserved_releases(self):
        for mode in MODES:
            with self.subTest(mode=mode):
                baseline = evaluate(mode=mode, continuous_attacks=False, window_seconds=10)
                empty = evaluate(mode=mode, continuous_attacks=False, window_seconds=10,
                                 timing={'target_windows': []})
                self.assertSameSP(empty, baseline)
                self.assertIsNone(empty['estimate']['skill']['initial_seconds'])
                self.assertIsNone(empty['estimate']['skill']['recharge_seconds'])
                self.assertEqual(empty['total_damage'], 0)

    def test_periodic_wine_keeps_public_sp_clock_with_plain_or_finite_speed(self):
        for mode in MODES:
            for skill in (1, 3):
                for relic_ids in ([WINE], [WINE, ATTACK_SP], [WINE, FINITE_SPEED]):
                    with self.subTest(mode=mode, skill=skill, relic_ids=relic_ids):
                        baseline = evaluate(skill, mode, relic_ids=relic_ids, window_seconds=10)
                        empty = evaluate(skill, mode, relic_ids=relic_ids, window_seconds=10,
                                         timing={'target_windows': [], 'initial_target_windows': []})
                        self.assertSameSP(empty, baseline)
                        self.assertEqual(empty.get('deployment_clock_reference'),
                                         baseline.get('deployment_clock_reference'))
                        if skill == 3:
                            self.assertEqual(empty['total_damage'], 0)
                        else:
                            self.assertIsNone(empty['total_damage'])

    def test_public_classified_callback_receipts_keep_sp_values_and_complete_evidence(self):
        for mode in MODES:
            for skill in (1, 3):
                with self.subTest(mode=mode, skill=skill):
                    phases = {'initial': [{'at_seconds': 1, 'type': 'kill'}],
                              'cycle': [{'at_seconds': 26, 'type': 'kill'}]}
                    baseline = evaluate(skill, mode, relic_ids=[HORN, ATTACK_SP],
                                        window_seconds=10, timing={'sp_events': phases})
                    empty = evaluate(skill, mode, relic_ids=[HORN, ATTACK_SP], window_seconds=10,
                                     timing={'sp_events': phases, 'target_windows': [],
                                             'initial_target_windows': []})
                    self.assertSameSP(empty, baseline)
                    self.assertEqual(empty['estimate']['sp_events'], baseline['estimate']['sp_events'])

    def test_missing_classified_callbacks_stay_unknown_without_synthetic_empty_events(self):
        for mode in MODES:
            with self.subTest(mode=mode):
                result = evaluate(mode=mode, relic_ids=[HORN], window_seconds=10,
                                  timing={'target_windows': []})
                self.assertIsNone(result['estimate']['skill']['initial_seconds'])
                self.assertEqual(result['estimate']['sp_events']['initial']['status'], 'missing')
                self.assertEqual(result['total_damage'], 0)

    def test_explicit_zero_observation_does_not_erase_independent_note_parameters(self):
        for mode in MODES:
            with self.subTest(mode=mode):
                baseline = evaluate(1, mode, window_seconds=0)
                empty = evaluate(1, mode, window_seconds=0, timing={'target_windows': []})
                self.assertEqual(empty['total_damage'], 0)
                self.assertEqual(empty['unbound_cast_reference']['conditional_components'],
                                 baseline['unbound_cast_reference']['conditional_components'])
                self.assertIsNone(empty['unbound_cast_reference']['actual_end_seconds'])

    def test_public_calculations_and_formatters_do_not_mutate_caller_or_returned_graph(self):
        for mode in MODES:
            for skill in (1, 3):
                with self.subTest(mode=mode, skill=skill):
                    caller = request(skill, mode, relic_ids=[ATTACK_SP, FINITE_SPEED],
                                     window_seconds=10, timing={'target_windows': [],
                                                               'initial_target_windows': []})
                    before = deepcopy(caller)
                    result = calculate_damage(caller)
                    self.assertEqual(caller, before)
                    result_before = deepcopy(result)
                    for formatter in (format_estimate, format_report):
                        self.assertIsInstance(formatter(result), str)
                        self.assertEqual(result, result_before)


if __name__ == '__main__':
    unittest.main()
