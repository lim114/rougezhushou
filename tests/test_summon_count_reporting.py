"""Declared token counts use the already validated value in report references."""
import copy
import json
import unittest
from unittest.mock import patch

from rouge.catalog import catalog
from rouge.damage import calculate_damage
from rouge.summons import module_rules, token_concurrent_limit

OP = 'char_110_deepcl'
TOKEN = 'token_10001_deepcl_tentac'
MOD = 'uniequip_002_deepcl'
PERFUME = 'rogue_6_relic_legacy_91'


def scenario(skill=1, mode='frames', **extra):
    return {'operator': OP, 'skill': skill, 'elite': 2, 'level': 70,
            'module_id': MOD, 'module_level': 3, 'window_seconds': 10,
            'timing_mode': mode, **extra}


def metrics(result, section):
    block = next(block for block in result['report']['sections'] if block['id'] == section)
    return {row['key']: row['value'] for row in block['metrics']}


class SummonCountReportingTests(unittest.TestCase):
    def test_legal_string_forms_have_full_numeric_count_results(self):
        training = ({'elite': 0, 'level': 45, 'skill_rank': 4, 'module_id': None, 'module_level': 0},
                    {'elite': 1, 'level': 60, 'skill_rank': 7, 'module_id': MOD, 'module_level': 3},
                    {'level': 39}, {'level': 40}, {'module_id': None, 'module_level': 0},
                    {'module_level': 1}, {'module_level': 2}, {'module_level': 3})
        profile = catalog()['operators'][OP]
        for fields in training:
            for skill in (1, 2):
                if fields.get('elite') == 0 and skill == 2:
                    continue
                for mode in ('frames', 'continuous'):
                    base = scenario(skill, mode, **fields)
                    cap = token_concurrent_limit(profile, base, TOKEN)
                    for count in (0, 1, cap):
                        numeric = calculate_damage({**base, 'summon_count': count})
                        for value in (str(count), str(float(count)), f'{count}e0'):
                            with self.subTest(fields=fields, skill=skill, mode=mode, count=value):
                                self.assertEqual(json.dumps(calculate_damage({**base, 'summon_count': value}), sort_keys=True),
                                                 json.dumps(numeric, sort_keys=True))

    def test_string_count_metrics_use_integers_numeric_dtypes_and_default_remain_unchanged(self):
        for skill in (1, 2):
            for mode in ('frames', 'continuous'):
                base = scenario(skill, mode)
                self.assertEqual(calculate_damage(base), calculate_damage({**base, 'summon_count': 1}))
                result = calculate_damage({**base, 'summon_count': '1.0'})
                self.assertIs(type(metrics(result, 'summons')['summon_count']), int)
                self.assertIs(type(metrics(result, 'relic_token_' + TOKEN)['model_count']), int)
                self.assertEqual(metrics(result, 'summons')['concurrent_limit'], 7)
                self.assertEqual(metrics(result, 'relic_token_' + TOKEN)['held_limit'], 7)
                for value in (0, 1, 0.0, 1.0):
                    numeric = calculate_damage({**base, 'summon_count': value})
                    self.assertIs(type(metrics(numeric, 'summons')['summon_count']), type(value))
                    self.assertIs(type(metrics(numeric, 'relic_token_' + TOKEN)['model_count']), type(value))
                    self.assertEqual(metrics(numeric, 'summons')['summon_count'], value)

    def test_fixed_s1_rate_is_declared_reference_with_empty_enemy_or_observation(self):
        for mode in ('frames', 'continuous'):
            for extra in ({'window_seconds': 0}, {'timing': {'target_disappears_seconds': 0}},
                          {'timing': {'target_windows': []}}):
                for count in (0, 1, 2):
                    result = calculate_damage(scenario(mode=mode, summon_count=str(float(count)), **extra))
                    rates = metrics(result, 'regeneration')
                    self.assertEqual(rates['per_token_rate'], 70)
                    self.assertEqual(rates['all_tokens_rate'], 70 * count)
                    self.assertIn('局外假设', str(result['report']))
                    self.assertIn('关卡可用部署位', str(result['report']))

    def test_original_qualification_caps_and_other_invalid_inputs_are_not_expanded(self):
        profile = catalog()['operators'][OP]
        for fields in ({'elite': 0, 'level': 45, 'skill_rank': 4, 'module_id': None, 'module_level': 0},
                       {'elite': 1, 'level': 60, 'skill_rank': 7}, {'level': 39}, {'level': 40}):
            for mode in ('frames', 'continuous'):
                base = scenario(mode=mode, **fields)
                cap = token_concurrent_limit(profile, base, TOKEN)
                for value in (-1, .5, cap + 1, float('inf'), float('nan')):
                    with self.assertRaisesRegex(ValueError, 'summon_count需要范围内的有限非负整数'):
                        calculate_damage({**base, 'summon_count': value})
                for value in (None, [], {}):
                    with self.assertRaises(TypeError):
                        calculate_damage({**base, 'summon_count': value})

    def test_section61_active_bool_rejection_is_retained(self):
        for skill in (1, 2):
            for mode in ('frames', 'continuous'):
                for value in (False, True):
                    with self.assertRaisesRegex(ValueError, '^summon_count需要范围内的有限非负整数。$'):
                        calculate_damage(scenario(skill, mode, summon_count=value))

    def test_inactive_count_inputs_keep_full_results(self):
        for op in ('mechanist', 'char_151_myrtle', 'char_1037_amiya3'):
            for mode in ('frames', 'continuous'):
                base = {'operator': op, 'skill': 1, 'window_seconds': 10, 'timing_mode': mode}
                plain = calculate_damage(base)
                for value in (False, True, '1.0', None, [], {}, -1, .5, float('nan')):
                    self.assertEqual(calculate_damage({**base, 'summon_count': value}), plain)

    def test_synthetic_unknown_hp_composition_guard_preserves_fixed_skill_reference(self):
        rules = copy.deepcopy(module_rules())
        rules[MOD]['hp_composition_verified'] = False
        for stage in (1, 2, 3):
            for mode in ('frames', 'continuous'):
                base = scenario(mode=mode, module_level=stage, summon_count='2.0', relic_ids=[PERFUME],
                                effects=[{'kind': 'hp_pct', 'value': .5, 'target_scope': 'all_units'}])
                with patch('rouge.summons.module_rules', return_value=rules):
                    result = calculate_damage(base)
                token = next(t for t in result['relic_token_stats'] if t['id'] == TOKEN)
                if stage == 1:
                    self.assertIsNotNone(token['hp'])
                    self.assertIsNotNone(token['regeneration_rate'])
                    self.assertFalse(token['module_reference']['hp_composition_pending'])
                else:
                    self.assertIsNone(token['hp'])
                    self.assertIsNone(token['regeneration_rate'])
                    self.assertTrue(token['module_reference']['hp_composition_pending'])
                    self.assertFalse(result['complete'])
                self.assertEqual(metrics(result, 'regeneration')['all_tokens_rate'], 140)

    def test_report_copy_preserves_raw_caller_and_shared_catalog(self):
        cached_catalog = copy.deepcopy(catalog())
        cached_rules = copy.deepcopy(module_rules())
        args = scenario(summon_count='1.0', timing={'target_disappears_seconds': 0})
        original = copy.deepcopy(args)
        result = calculate_damage(args)
        self.assertEqual(args, original)
        self.assertEqual(catalog(), cached_catalog)
        self.assertEqual(module_rules(), cached_rules)
        self.assertEqual(metrics(result, 'summons')['summon_count'], 1)


if __name__ == '__main__':
    unittest.main()
