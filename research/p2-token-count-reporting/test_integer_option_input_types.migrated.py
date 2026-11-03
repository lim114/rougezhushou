"""Integer count/state controls reject raw bool at the actual query seam.

Numbers, manual references, event clocks, checkbox controls and inactive keys
retain their prior contracts. These public cases do not read an active run.
"""
import copy
import json
import re
import unittest

from rouge.catalog import catalog
from rouge.damage import calculate_damage
from rouge.operator_options import OPTIONS
from rouge.relics import mechanics


FIELDS = {'summon_count', 'casts_used', 'slash_kills', 'amiya_slash_kills',
          'incoming_hits', 'shield_contact_ticks', 'cold_state', 'dash_hits',
          'bubble_bursts', 'levitate_triggers', 'snow_entries',
          'drone_warmup_hits', 'note_count', 'bait_triggers', 'enemy_attack_count',
          'palsy_triggers', 'palsy_overflow_hits', 'connected_stones',
          'trap_triggers', 'trap_dot_ticks', 'dragon_arrow_hits', 'ghost_count',
          'ghost_casts'}
CONTROLS = tuple((operator, key, skills) for operator, entries in OPTIONS.items()
                 for key, label, default, maximum, skills in entries if key in FIELDS)


def scenario(operator, skill, mode='frames', **extra):
    return {'operator': operator, 'skill': skill, 'base_attack': 1000,
            'window_seconds': 10, 'timing_mode': mode, **extra}


def outcome(args):
    try:
        return {'accepted': True, 'result': calculate_damage(args)}
    except Exception as error:
        return {'accepted': False, 'error_type': type(error).__name__, 'error': str(error)}


class IntegerOptionInputTypesTests(unittest.TestCase):
    def assert_bool_error(self, args, field):
        before = copy.deepcopy(args)
        with self.assertRaisesRegex(ValueError, '^' + re.escape(
                field + '需要范围内的有限非负整数。') + '$'):
            calculate_damage(args)
        self.assertEqual(args, before)

    def test_all_queried_integer_count_and_state_controls_reject_raw_bools(self):
        self.assertEqual({key for operator, key, skills in CONTROLS}, FIELDS)
        for operator, field, skills in CONTROLS:
            for skill in skills:
                for mode in ('frames', 'continuous'):
                    for value in (False, True):
                        args = scenario(operator, skill, mode, **{field: value})
                        if field == 'ghost_casts':
                            args['ghost_count'] = 1
                        with self.subTest(operator=operator, skill=skill, mode=mode,
                                          field=field, value=value):
                            self.assert_bool_error(args, field)

    def test_empty_enemy_or_observation_does_not_coerce_queried_bool_to_zero(self):
        for operator, field, skills in CONTROLS:
            for mode in ('frames', 'continuous'):
                for empty in ({'window_seconds': 0},
                              {'timing': {'target_disappears_seconds': 0}}):
                    args = scenario(operator, skills[0], mode, **{field: False}, **empty)
                    if field == 'ghost_casts':
                        args['ghost_count'] = 1
                    with self.subTest(operator=operator, field=field, mode=mode, empty=empty):
                        self.assert_bool_error(args, field)

    def test_inactive_fields_and_unqueried_shadow_casts_keep_full_results(self):
        for mode in ('frames', 'continuous'):
            for field in FIELDS:
                plain = scenario('silverash', 3, mode)
                for value in (False, True):
                    with self.subTest(field=field, mode=mode, value=value):
                        self.assertEqual(calculate_damage({**plain, field: value}),
                                         calculate_damage(plain))
            plain = scenario('char_1035_wisdel', 1, mode, ghost_count=0)
            for value in (False, True):
                self.assertEqual(calculate_damage({**plain, 'ghost_casts': value}),
                                 calculate_damage(plain))

    def test_numeric_defaults_and_zero_or_one_values_remain_accepted(self):
        for operator, field, skills in CONTROLS:
            for mode in ('frames', 'continuous'):
                for value in (0, 1, 0.0, 1.0):
                    args = scenario(operator, skills[0], mode, **{field: value})
                    if field == 'ghost_casts':
                        args['ghost_count'] = 1
                    with self.subTest(operator=operator, field=field, mode=mode, value=value):
                        self.assertTrue(outcome(args)['accepted'])

    def test_existing_strings_ranges_and_independent_errors_are_preserved(self):
        for mode in ('frames', 'continuous'):
            args = scenario('char_4202_haruka', 1, mode)
            for value in ('1', '1.0', 1.0):
                self.assertEqual(calculate_damage({**args, 'bubble_bursts': value}),
                                 calculate_damage({**args, 'bubble_bursts': 1}))
            for value in (-1, .5, 10001):
                with self.assertRaisesRegex(ValueError, 'bubble_bursts需要范围内的有限非负整数'):
                    calculate_damage({**args, 'bubble_bursts': value})
            with self.assertRaisesRegex(ValueError, '深度治疗本场已使用两次'):
                calculate_damage(scenario('char_298_susuro', 2, mode, casts_used=2))
            # The report now uses the same validated declared integer count.
            # Legal numeric strings retain the full numeric-count result.
            for number in (1, 2):
                for value in ('0', '0.0', '1', '1.0', '1e0'):
                    self.assertEqual(json.dumps(calculate_damage(scenario('char_110_deepcl', number, mode,
                                                                         summon_count=value)), sort_keys=True),
                                     json.dumps(calculate_damage(scenario('char_110_deepcl', number, mode,
                                                                         summon_count=int(float(value)))), sort_keys=True))
            with self.assertRaisesRegex(ValueError, '手动敌人重量必须是0到100之间的整数'):
                calculate_damage(scenario('char_1015_aglna2', 2, mode, enemy_weight=True))

    def test_real_checkbox_controls_and_noninteger_options_keep_acceptance(self):
        for operator, entries in OPTIONS.items():
            for field, label, default, maximum, skills in entries:
                if type(default) is not bool:
                    continue
                self.assertNotIn(field, FIELDS)
                for skill in skills:
                    for mode in ('frames', 'continuous'):
                        for value in (False, True):
                            with self.subTest(operator=operator, skill=skill, field=field,
                                              mode=mode, value=value):
                                self.assertTrue(outcome(scenario(operator, skill, mode,
                                                                **{field: value}))['accepted'])
        for value in (False, True):
            self.assertTrue(outcome(scenario('char_1044_hsgma2', 1,
                                            current_hp_ratio=value))['accepted'])

    def test_healing_capability_gate_preserves_prior_inactive_count_contract(self):
        for mode in ('frames', 'continuous'):
            for value in (False, True):
                plain = scenario('silverash', 3, mode, healing_targets=int(value))
                actual = calculate_damage({**plain, 'healing_targets': value})
                expected = calculate_damage(plain)
                self.assertEqual({k: v for k, v in actual.items() if k != 'report'},
                                 {k: v for k, v in expected.items() if k != 'report'})
                with self.assertRaisesRegex(ValueError, '治疗目标数需要为 0–100 的整数'):
                    calculate_damage(scenario('char_151_myrtle', 2, mode,
                                              healing_targets=value))

    def test_rejected_counts_preserve_public_caller_and_shared_source_caches(self):
        before_catalog = copy.deepcopy(catalog())
        before_mechanics = copy.deepcopy(mechanics())
        for operator, field, skills in CONTROLS:
            args = scenario(operator, skills[0], **{field: True})
            if field == 'ghost_casts':
                args['ghost_count'] = 1
            self.assert_bool_error(args, field)
        self.assertEqual(catalog(), before_catalog)
        self.assertEqual(mechanics(), before_mechanics)


if __name__ == '__main__':
    unittest.main()
