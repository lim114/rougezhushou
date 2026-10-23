from copy import deepcopy
import unittest
from rouge import current_battle_reference as battle, current_enemy_traits as model


def wrapped(value, defined=True):
    return {'m_defined': defined, 'm_value': value}


class CurrentEnemyTraits351Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reference = battle.packet()

    def record(self, stage, enemy):
        raw = self.reference['version']['current']['details']['stages'][stage]
        level = self.reference['inputs']['levels']['levels/' + raw['levelId'].lower() + '.json']
        return next(e for e in battle.enemy_records(level, self.reference) if e['id'] == enemy)

    def test_all_exact_stage_bindings_retain_original_identity_and_explicit_sources(self):
        seen, independent = 0, 0
        for level in self.reference['inputs']['levels'].values():
            for binding, row in zip(level['enemyDbRefs'], battle.enemy_records(level, self.reference)):
                seen += 1
                independent += not binding['useDb']
                self.assertEqual(row['raw_binding'], binding)
                traits = row['declared_traits']
                self.assertFalse(traits['current_immunity_or_blockability_proven'])
                self.assertFalse(traits['final_life_loss_or_total_count_proven'])
                self.assertEqual(set(traits['values']), set(traits['provenance']))
                if not binding['useDb']:
                    self.assertIsNone(traits['handbook_damage_types'])
                    self.assertTrue(all(v['source'] == '本关明确覆盖' for v in traits['provenance'].values()))
                text = battle.enemy_text(row)
                self.assertIn('不以白值替代', text)
                self.assertNotIn('m_defined', text)
        self.assertGreater(seen, 1000)
        self.assertGreater(independent, 0)

    def test_none_attack_and_zero_life_cost_do_not_erase_special_behaviour(self):
        row = self.record('ro6_b_2', 'enemy_2142_shsggd')
        self.assertEqual(row['declared_traits']['values']['applyWay'], 'NONE')
        self.assertEqual(row['declared_traits']['values']['lifePointReduce'], 0)
        text = battle.enemy_text(row)
        self.assertIn('仍可能有技能或特殊行为', text)
        self.assertIn('扣除0点目标生命', text)
        self.assertIn('不计入总数', text)
        self.assertNotIn('绝不攻击', text)

    def test_independent_undeclared_placeholders_stay_unknown(self):
        # Locate the actual undeclared constructor rather than assuming an ID.
        raw = self.reference['version']['current']['details']['stages']['ro6_n_2_3']
        level = self.reference['inputs']['levels']['levels/' + raw['levelId'].lower() + '.json']
        row = next(e for e in battle.enemy_records(level, self.reference)
                   if not e['use_db'] and not e['raw_binding']['overwrittenData']['motion']['m_defined'])
        values = row['declared_traits']['values']
        self.assertNotIn('motion', values)
        self.assertNotIn('applyWay', values)
        self.assertTrue(all(k not in values for k in model.IMMUNITIES))
        self.assertIn('未取得明确设置', battle.enemy_text(row))

    def test_explicit_false_is_known_but_not_current_control_success(self):
        row = self.record('ro6_b_3_b', 'enemy_2154_shdfb')
        values = row['declared_traits']['values']
        self.assertIs(values['stunImmune'], False)
        text = battle.enemy_text(row)
        self.assertIn('明确未设置这项免疫', text)
        self.assertIn('不等于当前一定能控制', text)
        self.assertIsNone(row['declared_traits']['handbook_damage_types'])

    def test_ground_motion_does_not_override_explicit_unblockable_mechanism(self):
        row = self.record('ro6_b_7', 'enemy_2157_shadvr')
        text = battle.enemy_text(row)
        self.assertEqual(row['declared_traits']['values']['motion'], 'WALK')
        self.assertIn('无法被阻挡', text)
        self.assertIn('不能单凭它判断当前能否阻挡', text)
        self.assertIn('实际扣点仍需核对', text)

    def test_inheritance_overrides_missing_level_and_type_guards(self):
        ref = {'inputs': {'enemy_definitions': {'e': [
            {'level': 0, 'enemyData': {'motion': wrapped('FLY'), 'attributes': {'stunImmune': wrapped(True)}}},
            {'level': 1, 'enemyData': {'motion': wrapped('WALK', False), 'attributes': {'stunImmune': wrapped(False)}}},
        ]}, 'handbook': {'e': {'damageType': ['PHYSIC']}}}}
        binding = {'id': 'e', 'useDb': True, 'level': 1, 'overwrittenData': {'motion': wrapped('WALK')}}
        value = model.declarations(binding, ref)
        self.assertEqual(value['values']['motion'], 'WALK')
        self.assertIs(value['values']['stunImmune'], False)
        binding['level'] = 2
        value = model.declarations(binding, ref)
        self.assertEqual(value['values'], {'motion': 'WALK'})
        self.assertIsNone(value['handbook_damage_types'])
        binding['useDb'] = False
        binding['overwrittenData'] = {'motion': wrapped('WALK', 1), 'lifePointReduce': wrapped(True),
                                     'attributes': {'stunImmune': wrapped(1)}}
        self.assertEqual(model.declarations(binding, ref)['values'], {})

    def test_correct_chinese_terms_unknown_enum_and_mutable_isolation(self):
        self.assertEqual(model.IMMUNITIES['disarmedCombatImmune'], '战栗')
        self.assertEqual(model.IMMUNITIES['attractImmune'], '诱导')
        self.assertEqual(model.IMMUNITIES['groundBoundImmune'], '缚地')
        row = self.record('ro6_b_2', 'enemy_2142_shsggd')
        copy = deepcopy(row['declared_traits'])
        copy['values']['motion'] = 'FUTURE_UNKNOWN'
        text = '\n'.join(model.player_lines(copy))
        self.assertNotIn('FUTURE_UNKNOWN', text)
        self.assertIn('未取得明确设置', text)
        self.assertEqual(row['declared_traits']['values']['motion'], 'WALK')


if __name__ == '__main__':
    unittest.main()
