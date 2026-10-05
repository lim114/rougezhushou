"""Recipient confirmation is distinct from holding a relic or live recognition."""
import copy
import hashlib
import json
from pathlib import Path
import unittest

from rouge.damage import calculate_damage
from rouge.relics import mechanics


ROOT = Path(__file__).resolve().parents[1]
# Independently enumerate the seven supported parent/recipient relationships.
CASES = (
    (5, 'char_133_mm', 1),
    (7, 'char_1029_yato2', 2),
    (9, 'mechanist', 3),
    (10, 'mechanist', 3),
    (12, 'mechanist', 3),
    (13, 'mechanist', 3),
    (15, 'mechanist', 3),
)


def parent(number):
    return 'rogue_6_relic_assign_' + str(number)


def recipient(number):
    return 'rogue_6_from_relic_' + str(number)


def scenario(operator='mechanist', skill=3, **values):
    return {'operator': operator, 'skill': skill, 'enemy_defense': 100,
            'timing': {'windup_frames': 6, 'recovery_frames': 9}, **values}


def record(result, identity):
    return next(row for row in result['relic_resolution']['records']
                if row['id'] == identity)


class RecipientBinding050Tests(unittest.TestCase):
    def assert_forecast_equal(self, actual, expected):
        self.assertEqual(actual['estimate']['base_stats'], expected['estimate']['base_stats'])
        self.assertEqual(actual['estimate']['skill'], expected['estimate']['skill'])
        self.assertEqual(actual['total_damage'], expected['total_damage'])
        self.assertEqual(actual.get('total_healing'), expected.get('total_healing'))
        self.assertEqual(actual['deployment_cost'], expected['deployment_cost'])

    def test_exact_seven_parent_bindings_and_recipient_effects_preserved(self):
        backup_file = ROOT / '.cache/batch-050-before/rouge/data/relic-mechanics.json'
        manifest = json.loads((ROOT / '.cache/batch-050-before/manifest.json').read_text(encoding='utf-8'))
        saved = backup_file.read_bytes()
        self.assertEqual(hashlib.sha256(saved).hexdigest(), manifest['rouge/data/relic-mechanics.json'])
        before = json.loads(saved.decode('utf-8'))
        data = mechanics()
        self.assertEqual({rid for rid, row in data['relics'].items() if row.get('recipient_binding')},
                         {parent(number) for number, _, _ in CASES})
        projected = copy.deepcopy(data['char_buffs'])
        # Raw recipient records and numerical parameters remain exact. Only
        # independently proven origin/layer metadata extends the old contract.
        added = {'source_buff_key', 'source_buff_index', 'attribute_layer',
                 'formula_item', 'native_count_scale'}
        for identity, entry in projected.items():
            for effect in entry['effects']:
                source = entry['raw']['buffs'][effect['source_buff_index']]
                self.assertEqual(effect['source_buff_key'], source['key'])
                if effect.get('attribute_layer') == 'relic_rune':
                    self.assertEqual(effect['formula_item'], {
                        'char_attribute_add': 'ADDITION', 'char_attribute_mul': 'MULTIPLIER',
                        'char_attribute_final_scaler': 'FINAL_SCALER'}[source['key']])
                if source['key'] == 'char_attribute_final_scaler' and effect['kind'] == 'redeploy_delta':
                    self.assertEqual(effect['stacking'], 'independent_rune_scalers')
                    effect['stacking'] = 'unverified' # old seal; native product proof resolves this field
                for key in added:
                    effect.pop(key, None)
        self.assertEqual(projected, before['char_buffs'])
        for number, _, _ in CASES:
            with self.subTest(number=number):
                binding = data['relics'][parent(number)]['recipient_binding']
                self.assertEqual(binding['char_buff_ids'], [recipient(number)])
                self.assertEqual(binding['scope'], 'current_operator_only')
                self.assertEqual(binding['effect_path'], 'char_buff_only')

    def test_holding_each_parent_without_confirmation_keeps_recipient_unknown(self):
        for number, operator, skill in CASES:
            with self.subTest(number=number):
                plain = calculate_damage(scenario(operator, skill))
                actual = calculate_damage(scenario(operator, skill, relic_ids=[parent(number)]))
                self.assert_forecast_equal(actual, plain)
                item = record(actual, parent(number))
                self.assertEqual(item['recipient_binding']['state'], 'unknown')
                self.assertEqual(item['recipient_binding']['char_buff_ids'], [])
                self.assertEqual(item['status'], 'incomplete')
                self.assertTrue(item['missing_conditions'])
                self.assertFalse(item['applied'])
                self.assertFalse(actual['relic_resolution']['complete'])

    def test_explicit_incomplete_empty_list_does_not_mean_no_recipient(self):
        actual = calculate_damage(scenario(relic_ids=[parent(9)], char_buff_ids=[], char_buffs_complete=False))
        self.assertEqual(record(actual, parent(9))['recipient_binding']['state'], 'unknown')
        self.assertFalse(actual['relic_resolution']['complete'])

    def test_complete_current_operator_list_confirms_all_seven_absent(self):
        for number, operator, skill in CASES:
            with self.subTest(number=number):
                plain = calculate_damage(scenario(operator, skill))
                actual = calculate_damage(scenario(operator, skill, relic_ids=[parent(number)],
                                                  char_buff_ids=[], char_buffs_complete=True))
                self.assert_forecast_equal(actual, plain)
                item = record(actual, parent(number))
                self.assertEqual(item['recipient_binding']['state'], 'absent')
                self.assertEqual(item['status'], 'inapplicable')
                self.assertFalse(item['missing_conditions'])
                self.assertFalse(item['applied'])
                self.assertTrue(actual['relic_resolution']['complete'])

    def test_profession_inapplicable_parents_need_no_recipient_confirmation(self):
        plain = calculate_damage(scenario())
        actual = calculate_damage(scenario(relic_ids=[parent(5), parent(7)]))
        self.assert_forecast_equal(actual, plain)
        for number in (5, 7):
            with self.subTest(number=number):
                item = record(actual, parent(number))
                self.assertEqual(item['recipient_binding']['state'], 'absent')
                self.assertEqual(item['status'], 'inapplicable')
                self.assertFalse(item['missing_conditions'])
        self.assertTrue(actual['relic_resolution']['complete'])

    def test_confirmed_parent_and_recipient_do_not_double_count(self):
        for number, operator, skill in CASES:
            if number == 10:
                continue
            with self.subTest(number=number):
                bound = calculate_damage(scenario(operator, skill, char_buff_ids=[recipient(number)]))
                actual = calculate_damage(scenario(operator, skill, relic_ids=[parent(number)],
                                                  char_buff_ids=[recipient(number)], char_buffs_complete=False))
                self.assert_forecast_equal(actual, bound)
                item = record(actual, parent(number))
                self.assertEqual(item['recipient_binding']['state'], 'confirmed')
                self.assertEqual(item['recipient_binding']['char_buff_ids'], [recipient(number)])
                self.assertEqual(item['status'], 'bound')
                self.assertFalse(item['missing_conditions'])
                self.assertFalse(item['applied'])
                self.assertEqual(record(actual, recipient(number))['recipient'], operator)
                self.assertTrue(actual['relic_resolution']['complete'])

    def test_confirmed_forbidden_recipient_rejects_skill_even_with_parent(self):
        for ids in ([], [parent(10)]):
            with self.subTest(parent_held=bool(ids)):
                with self.assertRaisesRegex(ValueError, '指中狼.*禁止开启技能'):
                    calculate_damage(scenario(relic_ids=ids, char_buff_ids=[recipient(10)]))

    def test_recipient_effects_survive_parent_consumption_with_numeric_oracles(self):
        sniper = scenario('char_133_mm', 1, base_attack=1000)
        plain = calculate_damage(sniper)
        enhanced = calculate_damage({**sniper, 'char_buff_ids': [recipient(5)]})
        self.assertEqual(enhanced['components'][0]['per_hit'] - plain['components'][0]['per_hit'], 50)
        specialist = scenario('char_1029_yato2', 2)
        plain = calculate_damage(specialist)
        enhanced = calculate_damage({**specialist, 'char_buff_ids': [recipient(7)]})
        self.assertEqual(enhanced['estimate']['base_stats']['redeploy_seconds'],
                         plain['estimate']['base_stats']['redeploy_seconds'] * .5)
        plain = calculate_damage(scenario())
        gift = calculate_damage(scenario(char_buff_ids=[recipient(9)]))
        self.assertEqual(gift['estimate']['base_stats']['attack_speed'], 150)
        foam = calculate_damage(scenario(char_buff_ids=[recipient(12)]))
        self.assertEqual(foam['estimate']['base_stats']['attack_speed'], 50)
        self.assertEqual(foam['estimate']['base_stats']['attack'],1261) # round-even(573*2.2)
        snack = calculate_damage(scenario(char_buff_ids=[recipient(13)]))
        self.assertEqual(snack['estimate']['skill']['sp_cost'], plain['estimate']['skill']['sp_cost'] * .8)
        cookie = calculate_damage(scenario(char_buff_ids=[recipient(15)]))
        self.assertEqual(cookie['estimate']['skill']['sp_recovery_per_second'], 1.8)
        for number, operator, skill in CASES:
            if number == 10:
                continue
            with self.subTest(number=number):
                actual = calculate_damage(scenario(operator, skill, char_buff_ids=[recipient(number)]))
                self.assertEqual(len(actual['relic_resolution']['records']), 1)
                self.assertEqual(record(actual, recipient(number))['source_relic_id'], parent(number))
                self.assertTrue(record(actual, recipient(number))['applied'])

    def test_duplicate_parent_and_recipient_ids_are_applied_once(self):
        for number, operator, skill in CASES:
            if number == 10:
                continue
            with self.subTest(number=number):
                once = calculate_damage(scenario(operator, skill, relic_ids=[parent(number)],
                                                char_buff_ids=[recipient(number)]))
                duplicate = calculate_damage(scenario(operator, skill, relic_ids=[parent(number)] * 3,
                                                     char_buff_ids=[recipient(number)] * 3))
                self.assert_forecast_equal(duplicate, once)
                self.assertEqual(duplicate['relic_resolution'], once['relic_resolution'])
        with self.assertRaisesRegex(ValueError, '禁止开启技能'):
            calculate_damage(scenario(char_buff_ids=[recipient(10)] * 3))

    def test_complete_list_scope_does_not_suppress_another_confirmed_buff(self):
        expected = calculate_damage(scenario(char_buff_ids=[recipient(12)]))
        actual = calculate_damage(scenario(relic_ids=[parent(9)], char_buff_ids=[recipient(12)],
                                          char_buffs_complete=True))
        self.assert_forecast_equal(actual, expected)
        self.assertEqual(record(actual, parent(9))['recipient_binding']['state'], 'absent')
        self.assertTrue(record(actual, recipient(12))['applied'])

    def test_wrong_profession_recipient_is_rejected_with_or_without_parent(self):
        for number in (5, 7):
            for ids in ([], [parent(number)]):
                with self.subTest(number=number, parent_held=bool(ids)):
                    with self.assertRaisesRegex(ValueError, '职业不符'):
                        calculate_damage(scenario(relic_ids=ids, char_buff_ids=[recipient(number)]))

    def test_completeness_requires_actual_boolean_not_truthy_values(self):
        for value in (None, 0, 1, 'true', [], {}):
            with self.subTest(value=value):
                args = scenario(relic_ids=[parent(9)], char_buff_ids=[], char_buffs_complete=value)
                before = copy.deepcopy(args)
                with self.assertRaisesRegex(ValueError, '完整性.*布尔'):
                    calculate_damage(args)
                self.assertEqual(args, before)

    def test_recalculation_leaves_inputs_and_shared_mechanics_unchanged(self):
        data_before = copy.deepcopy(mechanics())
        for extra in (
                {'relic_ids': [parent(9)], 'char_buff_ids': []},
                {'relic_ids': [parent(9)], 'char_buff_ids': [], 'char_buffs_complete': True},
                {'relic_ids': [parent(9)] * 2, 'char_buff_ids': [recipient(9)] * 2, 'char_buffs_complete': False}):
            with self.subTest(extra=extra):
                args = scenario(**extra)
                before = copy.deepcopy(args)
                one = calculate_damage(args)
                two = calculate_damage(args)
                self.assertEqual(one, two)
                self.assertEqual(args, before)
        self.assertEqual(mechanics(), data_before)


if __name__ == '__main__':
    unittest.main()
