"""Native default attribute bounds; synthetic modifiers isolate the two layers.

These fixtures are not assertions that an invented relic exists in the game.
"""
import unittest
from rouge.damage import _prepare_damage, _evaluate_damage
from rouge.relic_attributes import apply_attribute_runes
from rouge.timing import AttackTimeline, charge_seconds, mixed_charge_seconds, periodic_charge_seconds


def prepared(operator='kaltsit', skill=2, ordinary=-100, rune=None, mode='continuous', temporary=False):
    result = _prepare_damage({'operator': operator, 'skill': skill, 'timing_mode': mode})
    scenario, attributes, _, _ = result
    if rune is not None:
        attributes.update(apply_attribute_runes(attributes, [
            {'kind': 'attack_speed', 'value': rune, 'attribute_layer': 'relic_rune', 'formula_item': 'ADDITION'}]))
        scenario['_attribute_attack_speed'] = attributes['attack_speed']
    scenario['effects'].append({'kind': 'attack_speed', 'value': ordinary, '_verified_rule': True})
    if temporary:
        scenario['_relic_rules'].append({'kind': 'deployment_attack_speed', 'value': 40,
            'duration': 10, 'relic_id': 'rogue_6_relic_legacy_105'})
    return result


class AttackSpeedBounds(unittest.TestCase):
    def test_rune_floor_precedes_ordinary_addition(self):
        r = _evaluate_damage(prepared(rune=-200, ordinary=30))
        self.assertEqual(r['estimate']['base_stats']['attack_speed_reference'], 50)
        self.assertEqual(r['base_attack_speed'], 50)

    def test_default_raw_attribute_is_bounded_even_without_runes(self):
        self.assertEqual(apply_attribute_runes({'attack_speed': 0}, [])['attack_speed'], 20)

    def test_default_ordinary_floor_in_both_engines(self):
        for operator, skill in [('kaltsit', 2), ('silverash', 3), ('mechanist', 1), ('char_1041_angel2', 3)]:
            with self.subTest(operator=operator):
                r = _evaluate_damage(prepared(operator, skill, ordinary=-1000))
                self.assertEqual(r['base_attack_speed'], 20)
                self.assertEqual(r['base_attack_speed_reference'], 20)
                self.assertEqual(r['estimate']['base_stats']['attack_speed_reference'], 20)
                self.assertEqual(r['estimate']['skill']['skill_attack_speed_reference'], 20)

    def test_finite_bonus_adds_before_ordinary_floor(self):
        for mode in ('continuous', 'frames'):
            with self.subTest(mode=mode):
                r = _evaluate_damage(prepared(ordinary=-100, mode=mode, temporary=True))
                stats = r['estimate']['base_stats']
                self.assertEqual(stats['attack_speed'], 40)
                self.assertEqual(stats['attack_speed_reference'], 40)
                self.assertEqual(r['deployment_buff_reference']['permanent_attack_speed'], 20)

    def test_skill_bonus_is_added_before_attribute_floor(self):
        # Kaltsit S1 contributes +50. A -40 ordinary sum gives 20, not 70.
        for ordinary, expected in [(-140, 20), (-100, 50), (-90, 60)]:
            with self.subTest(ordinary=ordinary):
                r = _evaluate_damage(prepared(skill=1, ordinary=ordinary))
                self.assertEqual(r['attack_speed'], expected)
                self.assertEqual(r['estimate']['skill']['skill_attack_speed_reference'], expected)

    def test_operator_floor_does_not_change_independent_summon_stream(self):
        baseline = _evaluate_damage(prepared('char_110_deepcl', 1, ordinary=0))
        slower = _evaluate_damage(prepared('char_110_deepcl', 1, ordinary=-1000))
        get_token = lambda r: next(c for c in r['components'] if c['name'] == '触手')
        self.assertEqual(get_token(baseline), get_token(slower))
        self.assertEqual(slower['base_attack_speed'], 20)

    def test_event_sp_native_attack_path_uses_raw_sum(self):
        from rouge.sp_events import charge
        scenario = prepared(mode='frames', temporary=True)[0]
        scenario['timing'] = {'sp_events': {'initial': []}}
        skill = {'sp_type':'INCREASE_WHEN_ATTACK','sp_increment':1}
        result = charge(scenario, skill, 3, 0, 5, 20, initial=True, attribute_speed=0)
        self.assertAlmostEqual(result['seconds'], 226 / 30)

    def test_temporary_attack_stream_preserves_unclamped_sum(self):
        # Raw ordinary sum 0; permanent effective speed 20. +40 gives 40, not 60.
        for mode in ('continuous', 'frames'):
            scenario = prepared(mode=mode, temporary=True)[0]
            timeline = AttackTimeline(scenario)
            stream = timeline.attacks(25, 5, 20, attribute_speed=0)
            self.assertEqual(stream['interval_frames_by_attack'][:4], [75] * 4)
            self.assertEqual(stream['interval_frames_by_attack'][4:], [150] * (len(stream['interval_frames_by_attack']) - 4))

    def test_attack_sp_initial_and_cycle_use_same_raw_sum(self):
        scenario = prepared(mode='continuous', temporary=True)[0]
        for initial, offset, expected in [(True, 0, 7.5), (False, 10, 15)]:
            with self.subTest(initial=initial):
                self.assertEqual(charge_seconds(scenario, 3, 1, 5, 20, initial=initial,
                    offset=offset, attribute_speed=0), expected)
                self.assertEqual(mixed_charge_seconds(scenario, 3, 0, 1, 5, 20, initial=initial,
                    offset=offset, attribute_speed=0), expected)

    def test_periodic_sp_attack_merge_uses_raw_sum(self):
        scenario = prepared(mode='frames', temporary=True)[0]
        scenario['_relic_rules'].append({'kind':'periodic_sp','interval':20,'value':1,'clock':'deployment'})
        self.assertAlmostEqual(periodic_charge_seconds(scenario, 3, 1, 5, 20,
            initial=True, attribute_speed=0), 226 / 30)

    def test_attribute_upper_bound_remains_distinct_from_timing_cap(self):
        r = _evaluate_damage(prepared(ordinary=1000))
        self.assertEqual(r['base_attack_speed_reference'], 1100)
        self.assertEqual(r['base_attack_speed'], 600)

    def test_unverified_negative_manual_effect_still_rejected(self):
        from rouge.damage import calculate_damage
        with self.assertRaises(ValueError):
            calculate_damage({'operator':'kaltsit','skill':2,'effects':[{'kind':'attack_speed','value':-100}]})


if __name__ == '__main__': unittest.main()
