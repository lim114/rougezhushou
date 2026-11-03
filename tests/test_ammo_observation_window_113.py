"""Public API regression proposal; Root must run after binding the actual baseline."""
import copy
import unittest

from rouge.damage import calculate_damage
from rouge.estimate import format_estimate
from rouge.reporting import format_report


FINITE_AMMO = (
    ('char_1041_angel2', 1), ('char_1041_angel2', 2), ('char_1041_angel2', 3),
    ('char_1015_aglna2', 3), ('char_1035_wisdel', 3),
    ('mechanist', 1), ('kaltsit', 2),
)
LIFECYCLE_KEYS = (
    'initial_seconds', 'recharge_seconds', 'cycle_seconds', 'duration_seconds',
    'total_damage', 'total_healing', 'phase_damage', 'phase_healing',
    'cycle_damage', 'cycle_healing', 'cycle_dps', 'cycle_hps',
    'skill_attack', 'skill_attack_speed', 'skill_attack_speed_reference',
)


def scenario(op='char_1041_angel2', skill=1, **extra):
    value = {'operator': op, 'skill': skill, 'elite': 2, 'level': 1,
             'skill_rank': 7, 'trust': 0, 'potential': 1, 'base_attack': 1000,
             'enemy_defense': 0, 'enemy_resistance': 0, 'timing_mode': 'frames',
             'timing': {'windup_frames': 0, 'recovery_frames': 0,
                        'projectile_travel_seconds': 0}}
    if op == 'char_1041_angel2' and skill == 3:
        value['delivery_coordinate'] = False
    value.update(extra)
    return value


def metric(result, section, key):
    group = next(row for row in result['report']['sections'] if row['id'] == section)
    return next(row['value'] for row in group['metrics'] if row['key'] == key)


class AmmoObservationWindowTests113(unittest.TestCase):
    def calculate(self, source):
        before = copy.deepcopy(source)
        result = calculate_damage(source)
        self.assertEqual(source, before)
        return result

    def lifecycle(self, result):
        skill = result['estimate']['skill']
        return {key: skill[key] for key in LIFECYCLE_KEYS}

    def test_public_four_cell_window_travel_matrix_uses_the_requested_domain(self):
        for window in (5, 60):
            for travel in (0, 20):
                with self.subTest(window=window, travel=travel):
                    source = scenario(window_seconds=window,
                        timing={'windup_frames': 0, 'recovery_frames': 0,
                                'projectile_travel_seconds': travel})
                    result = self.calculate(source)
                    skill = result['estimate']['skill']
                    self.assertEqual(skill['window_seconds'], window)
                    self.assertEqual(skill['window_dps'], result['total_damage'] / window)
                    self.assertEqual(metric(result, 'damage', 'window_seconds'), window)
                    self.assertEqual(metric(result, 'damage', 'window_dps'), result['total_damage'] / window)

    def test_short_window_excludes_delayed_impacts_without_erasing_the_cast(self):
        result = self.calculate(scenario(window_seconds=5,
            timing={'windup_frames': 0, 'recovery_frames': 0,
                    'projectile_travel_seconds': 20}))
        self.assertEqual(result['total_damage'], 0)
        self.assertGreater(result['estimate']['skill']['total_damage'], 0)
        self.assertEqual(result['estimate']['skill']['window_dps'], 0)
        self.assertEqual(result['estimate']['skill']['window_seconds'], 5)

    def test_long_window_contains_late_hits_and_retains_the_original_end_clock(self):
        source = scenario(timing={'windup_frames': 0, 'recovery_frames': 0,
                                  'projectile_travel_seconds': 20})
        full = self.calculate(source)
        long = self.calculate({**source, 'window_seconds': 60})
        self.assertGreater(long['total_damage'], 0)
        self.assertEqual(self.lifecycle(long), self.lifecycle(full))
        self.assertLess(long['estimate']['skill']['duration_seconds'], 60)
        self.assertEqual(long['estimate']['skill']['window_dps'], long['total_damage'] / 60)

    def test_all_finite_ammo_families_keep_cast_phase_cycle_and_sp(self):
        for op, number in FINITE_AMMO:
            for mode in ('frames', 'continuous'):
                with self.subTest(op=op, skill=number, mode=mode):
                    source = scenario(op, number, timing_mode=mode)
                    full = self.calculate(source)
                    windowed = self.calculate({**source, 'window_seconds': 60})
                    self.assertEqual(windowed['estimate']['skill']['window_seconds'], 60)
                    self.assertEqual(self.lifecycle(windowed), self.lifecycle(full))
                    self.assertEqual(windowed['estimate']['base_stats'], full['estimate']['base_stats'])
                    self.assertEqual(windowed['estimate'].get('sp_events'), full['estimate'].get('sp_events'))

    def test_finite_ammo_damage_report_uses_actual_window_not_release_duration(self):
        for op, number in FINITE_AMMO:
            with self.subTest(op=op, skill=number):
                result = self.calculate(scenario(op, number, window_seconds=60))
                self.assertEqual(metric(result, 'damage', 'window_seconds'), 60)
                damage = result['estimate']['skill'].get('window_damage', result['total_damage'])
                expected = None if damage is None else damage / 60
                self.assertEqual(metric(result, 'damage', 'window_dps'), expected)

    def test_empty_enemy_keeps_a_positive_observation_and_unknown_end(self):
        result = self.calculate(scenario(window_seconds=60,
            timing={'windup_frames': 0, 'recovery_frames': 0, 'target_windows': []}))
        skill = result['estimate']['skill']
        self.assertEqual(result['total_damage'], 0)
        self.assertEqual(skill['window_seconds'], 60)
        self.assertEqual(skill['window_dps'], 0)
        self.assertIsNone(skill['duration_seconds'])
        self.assertIsNone(skill['cycle_seconds'])

    def test_zero_ammo_observation_has_no_average_or_landed_damage(self):
        for op, number in FINITE_AMMO:
            with self.subTest(op=op, skill=number):
                result = self.calculate(scenario(op, number, window_seconds=0))
                skill = result['estimate']['skill']
                self.assertEqual(skill['window_seconds'], 0)
                self.assertEqual(result['total_damage'], 0)
                self.assertIsNone(skill.get('window_dps'))
                self.assertEqual(metric(result, 'damage', 'window_seconds'), 0)
                self.assertFalse(any(row['key'] == 'window_dps' for group in result['report']['sections']
                                     if group['id'] == 'damage' for row in group['metrics']))

    def test_medical_ammo_friendly_healing_uses_the_same_positive_window(self):
        for mode in ('frames', 'continuous'):
            with self.subTest(mode=mode):
                result = self.calculate(scenario('kaltsit', 2, timing_mode=mode,
                    window_seconds=60, healing_targets=1,
                    timing={'windup_frames': 0, 'recovery_frames': 0, 'target_windows': []}))
                skill = result['estimate']['skill']
                self.assertEqual(result['total_damage'], 0)
                self.assertGreater(skill['window_healing'], 0)
                self.assertEqual(skill['window_seconds'], 60)
                self.assertEqual(metric(result, 'healing', 'window_seconds'), 60)
                self.assertEqual(metric(result, 'healing', 'window_hps'), skill['window_healing'] / 60)

    def test_medical_ammo_no_friendly_target_does_not_invent_a_complete_cast(self):
        result = self.calculate(scenario('kaltsit', 2, window_seconds=60,
            healing_targets=0, timing={'windup_frames': 0, 'recovery_frames': 0,
                                       'target_windows': []}))
        skill = result['estimate']['skill']
        self.assertEqual(result['total_damage'], 0)
        self.assertEqual(skill['window_healing'], 0)
        self.assertEqual(skill['window_seconds'], 60)
        self.assertIsNone(skill['duration_seconds'])
        self.assertIsNone(skill['cycle_seconds'])

    def test_unknown_wisdel_damage_keeps_its_mask_and_coherent_known_subtotal(self):
        result = self.calculate(scenario('char_1035_wisdel', 3, window_seconds=60))
        skill = result['estimate']['skill']
        self.assertIsNone(result['total_damage'])
        self.assertIsNone(skill['window_dps'])
        subtotal = result['known_damage_subtotals']
        self.assertEqual(subtotal['window_dps'], subtotal['window_damage'] / 60)
        self.assertEqual(skill['window_seconds'], 60)
        self.assertFalse(result['complete'])

    def test_unplaced_coordinate_bomb_is_not_promoted_to_complete_damage(self):
        result = self.calculate(scenario('char_1041_angel2', 3,
            window_seconds=60, delivery_coordinate=True))
        self.assertIsNone(result['total_damage'])
        self.assertIsNone(result['estimate']['skill']['window_dps'])
        subtotal = result['known_damage_subtotals']
        self.assertEqual(subtotal['window_dps'], subtotal['window_damage'] / 60)
        self.assertFalse(result['complete'])

    def test_non_ammo_timed_skill_keeps_its_existing_capped_domain(self):
        full = self.calculate(scenario('char_002_amiya', 1))
        result = self.calculate(scenario('char_002_amiya', 1, window_seconds=60))
        self.assertEqual(result['estimate']['skill']['window_seconds'],
                         full['estimate']['skill']['duration_seconds'])
        self.assertEqual(self.lifecycle(result), self.lifecycle(full))

    def test_triggered_token_ammo_is_not_reclassified_as_finite_owner_ammo(self):
        result = self.calculate(scenario('char_2027_wang', 3, window_seconds=60))
        skill = result['estimate']['skill']
        self.assertEqual(skill['mode'], 'triggered_ammo')
        self.assertIsNone(skill['total_damage'])
        self.assertIsNone(skill['duration_seconds'])
        self.assertIsNone(skill['cycle_seconds'])
        self.assertEqual(skill['window_seconds'], 60)

    def test_manual_shield_end_keeps_its_existing_capped_window_and_unknown_break_clock(self):
        result = self.calculate(scenario('mechanist', 2, window_seconds=60,
                                         skill_duration_seconds=5, shield_break_count=0))
        self.assertEqual(result['estimate']['skill']['window_seconds'], 5)
        self.assertIsNone(result['shield_break_reference']['actual_end_seconds'])
        self.assertFalse(result['shield_break_reference']['events_scheduled'])

    def test_three_public_texts_render_the_same_window_and_average(self):
        result = self.calculate(scenario(window_seconds=60))
        texts = (format_estimate(result), format_report(result), format_report(result, technical=True))
        for text in texts:
            self.assertIsInstance(text, str)
            self.assertIn('60', text)
        self.assertEqual(format_estimate(result), format_report(result))
        self.assertEqual(metric(result, 'damage', 'window_seconds'), 60)

    def test_finite_ammo_rejects_invalid_observation_with_existing_value_error(self):
        for value in (-1, float('inf'), float('nan')):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    calculate_damage(scenario(window_seconds=value))
