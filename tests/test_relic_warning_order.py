"""Public warnings follow existing candidate order without applying unknown stacks."""
import copy
import json
import os
import subprocess
import sys
import unittest
from itertools import permutations
from unittest.mock import patch
from pathlib import Path

from rouge.catalog import catalog
from rouge.damage import calculate_damage
from rouge.relics import prepare, mechanics as source_mechanics
from rouge.relic_healing_factors import healing_factor, regeneration_factor

SOURCE_IDS = ('rogue_6_relic_legacy_81', 'rogue_6_relic_legacy_82', 'rogue_6_relic_legacy_83')
ROSE = 'unproved_healing_order_source_a'
CROWN = 'unproved_healing_order_source_b'
MEAL = 'unproved_healing_order_source_c'
GROUPS = ('heal_scale', 'received_regeneration')

def unverified_order_mechanics():
    """Single-source fixtures with explicitly absent native composition proof.

    Section 198 closed the real rose/crown/meal combination. Keep exercising
    the generic unknown-combination order contract using three different test
    IDs, with no claim that those IDs or their stacking exist in game data.
    """
    data = copy.deepcopy(source_mechanics())
    for identity, original in zip((ROSE, CROWN, MEAL), SOURCE_IDS):
        entry = copy.deepcopy(data['relics'][original])
        entry['name'] = '未证组合源测试fixture ' + identity[-1].upper()
        entry['verification'] = {'fixture_only': True, 'native_composition_evidence': None}
        for effect in entry['effects']:
            effect['stacking'] = 'unverified'
            for key in ('composition_evidence', 'healing_composition', 'regeneration_composition'):
                effect.pop(key, None)
        data['relics'][identity] = entry
    return data


def warning(group):
    return '组合 ' + group + ' 的叠加规则尚未核验，未套用该组合。'

def scenario(**values):
    return {'operator': 'char_1037_amiya3', 'skill': 1, 'base_attack': 1000,
            'window_seconds': 10, **values}

def combinations(result):
    return [w for w in result['warnings'] if w.startswith('组合 ')]

class RelicWarningOrderTests(unittest.TestCase):
    def setUp(self):
        fixture = patch('rouge.relics.mechanics', return_value=unverified_order_mechanics())
        fixture.start()
        self.addCleanup(fixture.stop)

    def test_conflicts_follow_first_candidate_and_keep_pending_text(self):
        result = calculate_damage(scenario(relic_ids=[ROSE, CROWN]))
        expected = [warning(group) for group in GROUPS]
        self.assertEqual(combinations(result), expected)
        for record in result['relic_resolution']['records']:
            self.assertEqual(record['pending'], ['组合叠加规则待核验:' + group for group in GROUPS])
            self.assertEqual(record['applied'], [])
            self.assertEqual(record['status'], 'incomplete')
        self.assertFalse(result['relic_resolution']['complete'])

    def test_duplicate_ids_do_not_duplicate_warnings_or_records(self):
        plain = calculate_damage(scenario(relic_ids=[ROSE, CROWN]))
        self.assertEqual(calculate_damage(scenario(relic_ids=[ROSE, CROWN, ROSE, CROWN])), plain)

    def test_reversed_input_preserves_record_order_and_candidate_group_order(self):
        result = calculate_damage(scenario(relic_ids=[CROWN, ROSE]))
        self.assertEqual([r['id'] for r in result['relic_resolution']['records']], [CROWN, ROSE])
        self.assertEqual(combinations(result), [warning(group) for group in GROUPS])

    def test_three_unproved_source_fixtures_leave_stacking_unknown(self):
        result = calculate_damage(scenario(relic_ids=[ROSE, CROWN, MEAL]))
        self.assertEqual(combinations(result), [warning(group) for group in GROUPS])
        self.assertEqual([r['id'] for r in result['relic_resolution']['records']], [ROSE, CROWN, MEAL])
        self.assertFalse(result['complete'])
        self.assertFalse(any(r['kind'] in ('healing_factor', 'regeneration_factor')
                             for r in result['relic_resolution']['rules']))

    def test_unrelated_warning_position_and_unknown_zero_scope_are_preserved(self):
        args = scenario(relic_ids=['unknown_relic_for_order_test', ROSE, CROWN], window_seconds=0)
        original = copy.deepcopy(args)
        result = calculate_damage(args)
        warnings = result['relic_resolution']['warnings']
        self.assertEqual(warnings, ['未知藏品 unknown_relic_for_order_test，效果未计算。'] +
                         [warning(group) for group in GROUPS])
        self.assertFalse(result['complete'])
        self.assertEqual(args, original)
        self.assertEqual(result['total_damage'], 0)
        self.assertEqual(result['total_healing'], 0)

    def test_rules_effects_and_token_effects_keep_their_source_order(self):
        args = scenario(operator='char_110_deepcl', skill=2,
                        relic_ids=[ROSE, CROWN, 'rogue_6_relic_legacy_5'])
        prepared, resolution = prepare(args, catalog()['operators'][args['operator']])
        self.assertEqual(resolution['warnings'], [warning(group) for group in GROUPS])
        self.assertEqual([e['relic_id'] for e in prepared['effects']], ['rogue_6_relic_legacy_5'])
        self.assertEqual([e['relic_id'] for e in prepared['_token_relic_effects']], ['rogue_6_relic_legacy_5'])
        self.assertEqual(prepared['_token_relic_effects'][0]['token_ids'], ['token_10001_deepcl_tentac'])
        self.assertEqual(resolution['rules'], [])

    def test_empty_single_and_inapplicable_groups_have_no_conflict_warning(self):
        for args in (scenario(relic_ids=[]), scenario(relic_ids=[ROSE]),
                     scenario(operator='char_110_deepcl', skill=2, relic_ids=['rogue_6_relic_legacy_80'])):
            with self.subTest(args=args):
                self.assertEqual(combinations(calculate_damage(args)), [])

    def test_real_three_sources_have_proved_rules_in_input_order_without_duplicates(self):
        for order in permutations(SOURCE_IDS):
            result = calculate_damage(scenario(relic_ids=[*order, order[0], order[1]]))
            resolution = result['relic_resolution']
            self.assertEqual(combinations(result), [])
            self.assertEqual([r['id'] for r in resolution['records']], list(order))
            self.assertTrue(resolution['complete'])
            self.assertEqual([r['relic_id'] for r in resolution['rules']],
                             [identity for identity in order for _ in range(3)])
            self.assertEqual([r['kind'] for r in resolution['rules']],
                             ['healing_factor', 'regeneration_factor', 'regeneration_factor'] * 3)
            self.assertAlmostEqual(healing_factor([r for r in resolution['rules']
                if r['kind'] == 'healing_factor']), 2.184)
            self.assertAlmostEqual(regeneration_factor([r for r in resolution['rules']
                if r['kind'] == 'regeneration_factor']), 1.9)
            self.assertTrue(all(not r['pending'] and len(r['applied']) == 3
                                for r in resolution['records']))

    def test_complete_public_result_and_three_texts_are_hash_seed_independent(self):
        root = Path(__file__).resolve().parents[1]
        code = '''import json
from rouge.damage import calculate_damage
from rouge.estimate import format_estimate
from rouge.reporting import format_report
from tests.test_relic_warning_order import unverified_order_mechanics
from unittest.mock import patch
args = json.loads(__import__('sys').argv[1])
with patch('rouge.relics.mechanics', return_value=unverified_order_mechanics()):
    r = calculate_damage(args)
print(json.dumps([r, format_estimate(r), format_report(r), format_report(r, technical=True)], ensure_ascii=False, sort_keys=True))
'''
        args = scenario(operator='mechanist', skill=3,
                        relic_ids=['rogue_6_relic_legacy_61', 'rogue_6_relic_legacy_62', ROSE, CROWN])
        outputs = []
        for seed in ('0', '1', '42', '314159'):
            env = {**os.environ, 'PYTHONHASHSEED': seed, 'PYTHONPATH': str(root),
                   'PYTHONIOENCODING': 'utf-8'}
            outputs.append(subprocess.check_output([sys.executable, '-c', code, json.dumps(args)],
                                                   cwd=root, env=env, text=True, encoding='utf-8'))
        self.assertEqual(len(set(outputs)), 1)

if __name__ == '__main__':
    unittest.main()
