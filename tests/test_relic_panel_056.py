"""Independent, fixed-data rune-vs-battle modifier regression examples."""
import unittest
import struct
from rouge.damage import calculate_damage
from rouge.catalog import operator_attributes, catalog


def rune_integer(base, multiplier):
    """Independent float32 writer oracle for exact selected small rational cases."""
    return round(struct.unpack('<f', struct.pack('<f', base * multiplier))[0])


class RelicPanelTests(unittest.TestCase):
    def test_mechanist_skill_multiplier_follows_rune(self):
        r = calculate_damage({'operator': 'mechanist', 'skill': 3,
            'relic_ids': ['rogue_6_relic_legacy_16']})
        self.assertAlmostEqual(r['attack'], 716 * 3.8)

    def test_kaltsit_skill_multiplier_follows_rune(self):
        r = calculate_damage({'operator': 'kaltsit', 'skill': 2,
            'relic_ids': ['rogue_6_relic_legacy_19']})
        self.assertAlmostEqual(r['attack'], 638 * 2.5)

    def test_kaltsit_hp_talent_follows_rune(self):
        r = calculate_damage({'operator': 'kaltsit', 'skill': 2,
            'relic_ids': ['rogue_6_relic_legacy_90']})
        self.assertAlmostEqual(r['estimate']['base_stats']['hp'], 2120 * 1.5 * 1.25)

    def test_kaltsit_defense_talent_follows_rune(self):
        r = calculate_damage({'operator': 'kaltsit', 'skill': 2,
            'relic_ids': ['rogue_6_relic_legacy_14']})
        self.assertAlmostEqual(r['estimate']['base_stats']['defense'], 306 * 1.5 * 1.25)

    def test_angel_talent_follows_rune(self):
        r = calculate_damage({'operator': 'char_1041_angel2', 'skill': 3,
            'relic_ids': ['rogue_6_relic_legacy_19']})
        self.assertAlmostEqual(r['estimate']['base_stats']['attack'], 972 * 1.18)
        self.assertAlmostEqual(r['attack'], 972 * (1 + .18 + .3))

    def test_two_runes_add_before_skill_not_multiply_each_other(self):
        r = calculate_damage({'operator': 'mechanist', 'skill': 3,
            'relic_ids': ['rogue_6_relic_legacy_16', 'rogue_6_relic_legacy_17']})
        self.assertAlmostEqual(r['attack'], 917 * 3.8)

    def test_wrong_position_does_not_receive_rune(self):
        r = calculate_damage({'operator': 'mechanist', 'skill': 3,
            'relic_ids': ['rogue_6_relic_legacy_19']})
        self.assertAlmostEqual(r['attack'], 573 * 3.8)

    def test_manual_battle_multiplier_is_separate(self):
        r = calculate_damage({'operator': 'mechanist', 'skill': 3,
            'relic_ids': ['rogue_6_relic_legacy_16'],
            'effects': [{'kind': 'attack_pct', 'value': .2}]})
        self.assertAlmostEqual(r['attack'], 716 * (1 + .2 + 2.8))

    def test_random_target_rune_is_before_talent_and_skill(self):
        r = calculate_damage({'operator': 'kaltsit', 'skill': 2,
            'relic_ids': ['rogue_6_relic_legacy_52'],
            'relic_context': {'chitin_recipient': 1}})
        self.assertEqual(r['attack'], 510 * 2 * 2.5)
        self.assertEqual(r['estimate']['base_stats']['hp'], 2120 * 2 * 1.25)

    def test_random_persistent_layer_rune_keeps_recipient_and_cap(self):
        s = {'operator': 'mechanist', 'skill': 3,
             'relic_ids': ['rogue_6_relic_legacy_136']}
        absent = calculate_damage({**s, 'relic_context': {'mercenary_recipient': 0}})
        self.assertAlmostEqual(absent['attack'], 573 * 3.8)
        for count, atk, hp in ((1, 602, 3813), (10, 860, 5446), (11, 860, 5446)):
            r = calculate_damage({**s, 'relic_context': {
                'mercenary_recipient': 1, 'mercenary_stacks': count}})
            self.assertEqual(r['estimate']['base_stats']['attack'], atk)
            self.assertEqual(r['estimate']['base_stats']['hp'], hp)
            self.assertAlmostEqual(r['attack'], atk * 3.8)

    def test_grudge_stacks_are_battle_multiplier_not_final_scaler(self):
        r = calculate_damage({'operator': 'mechanist', 'skill': 3,
            'relic_ids': ['rogue_6_relic_artifact_7'],
            'relic_context': {'grudge_stacks': 100}})
        self.assertAlmostEqual(r['attack'], 584 * (1 + .2 + 2.8))

    def test_grudge_does_not_multiply_stolen_final_addition(self):
        r = calculate_damage({'operator': 'char_4087_ines', 'skill': 1,
            'stolen_enemy_count': 1,
            'relic_ids': ['rogue_6_relic_artifact_7'],
            'relic_context': {'grudge_stacks': 100}})
        self.assertAlmostEqual(r['estimate']['base_stats']['attack'], 652 * 1.2 + 90)

    def test_hp_penalty_precedes_talent(self):
        r = calculate_damage({'operator': 'kaltsit', 'skill': 2,
            'relic_ids': ['rogue_6_relic_final_3']})
        self.assertAlmostEqual(r['estimate']['base_stats']['hp'], 2120 * .6 * 1.25)

    def test_redeploy_rune_precedes_flat_self_talent(self):
        from rouge.relics import mechanics
        rid = next(k for k, v in mechanics()['relics'].items() if any(
            e['kind'] == 'redeploy_delta' and e['value'] == -.5 for e in v['effects']))
        r = calculate_damage({'operator': 'char_1048_orchd2', 'skill': 2,
            'relic_ids': [rid]})
        # Native rune sets respawnTime to 35; 翔虫机动 then subtracts 15.
        self.assertEqual(r['estimate']['base_stats']['redeploy_seconds'], 20)

    def test_two_native_redeploy_runes_multiply_before_self_talent(self):
        r = calculate_damage({'operator': 'char_1029_yato2', 'skill': 1,
            'relic_ids': ['rogue_6_relic_legacy_77', 'rogue_6_relic_artifact_6']})
        # Both selectors match special, unlike warrior 苍苔. 18*.65*.5 -> 6.
        self.assertEqual(r['estimate']['base_stats']['redeploy_seconds'], 6)
        self.assertFalse(any('叠加规则尚未核验' in w for w in r['warnings']))

    def test_cultivation_module_enters_before_rune(self):
        s = {'operator': 'char_1041_angel2', 'skill': 3, 'elite': 2,
             'level': 60, 'trust': 50, 'potential': 3,
             'module_id': 'uniequip_002_angel2', 'module_level': 3}
        # These checks isolate the rune layer; raw cultivation has its own oracle.
        base = calculate_damage(s)
        r = calculate_damage({**s, 'relic_ids': ['rogue_6_relic_legacy_19']})
        cultivated = operator_attributes(s['operator'], s['elite'], s['level'], s['trust'],
            s['potential'], s['module_id'], s['module_level'])['attack']
        self.assertAlmostEqual(r['attack'], rune_integer(cultivated, 1.25) * 1.56)
        self.assertAlmostEqual(r['estimate']['base_stats']['attack'], rune_integer(cultivated, 1.25) * 1.26)

    def test_duplicate_rune_and_order_are_stable(self):
        s = {'operator': 'kaltsit', 'skill': 2}
        r1 = calculate_damage({**s, 'relic_ids': ['rogue_6_relic_legacy_19',
            'rogue_6_relic_legacy_20', 'rogue_6_relic_legacy_19']})
        r2 = calculate_damage({**s, 'relic_ids': ['rogue_6_relic_legacy_20',
            'rogue_6_relic_legacy_19']})
        self.assertAlmostEqual(r1['attack'], 816 * 2.5)
        self.assertEqual(r1['estimate']['base_stats'], r2['estimate']['base_stats'])

    def test_token_rune_precedes_token_skill_multiplier(self):
        s = {'operator': 'char_110_deepcl', 'skill': 1, 'summon_count': 1}
        base = calculate_damage(s)
        r = calculate_damage({**s, 'relic_ids': ['rogue_6_relic_legacy_134']})
        original = next(c for c in base['components'] if c['name'] == '触手')
        buffed = next(c for c in r['components'] if c['name'] == '触手')
        self.assertAlmostEqual(buffed['per_hit'], rune_integer(462, 1.3) * 1.6)
        self.assertEqual(r['estimate']['base_stats'], base['estimate']['base_stats'])

    def test_finite_attack_speed_clock_and_non_attack_sp_are_unchanged(self):
        s = {'operator': 'kaltsit', 'skill': 2,
             'relic_ids': ['rogue_6_relic_legacy_105']}
        base = calculate_damage(s)
        r = calculate_damage({**s, 'relic_ids': s['relic_ids'] + ['rogue_6_relic_legacy_19']})
        self.assertEqual(r['estimate']['skill']['initial_seconds'], base['estimate']['skill']['initial_seconds'])
        self.assertEqual(r['estimate']['skill']['recharge_seconds'], base['estimate']['skill']['recharge_seconds'])
        self.assertEqual(r['estimate']['skill']['duration_seconds'], base['estimate']['skill']['duration_seconds'])

    def test_verified_squad_rune_adds_with_relic_before_talent(self):
        from rouge.run_config import config_data
        squad = next(v for v in config_data()['squads'].values() if any(
            b['key'] == 'char_attribute_mul' and any(x['key'] == 'atk' and x['value'] for x in b['blackboard'])
            for b in v['buffs']))
        value = sum(x['value'] for b in squad['buffs'] if b['key'] == 'char_attribute_mul'
                    for x in b['blackboard'] if x['key'] == 'atk')
        r = calculate_damage({'operator': 'char_1041_angel2', 'skill': 3,
            'relic_ids': ['rogue_6_relic_legacy_19'],
            'run_config': {'squad': {'id': squad['id'], 'name': squad['name'], 'effect_verified': True}}})
        self.assertAlmostEqual(r['estimate']['base_stats']['attack'], rune_integer(778, 1 + value + .25) * 1.18)


if __name__ == '__main__':
    unittest.main()
