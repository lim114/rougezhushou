import copy
import unittest

from rouge.battle_preview import battle_data, enemy_preview, enemy_text
from rouge.damage import calculate_damage
from rouge.spawn_reference import movement_reference


SID = 'ro6_e_3_6'
NORMAL = 'ro6_n_3_6'
EID = 'enemy_10107_mjcdog_2'
KEY = 'stage_move_speed_rune_reference'
RAW_SHA = '2d2e89306c3d3c4a2a6c21f71b3828f66cb7a7996ab149faaad043d4867e8296'


class StageMoveSpeedReferenceTests(unittest.TestCase):
    def test_exact_selected_stage_parameter_and_scope_for_all_actual_enemy_references(self):
        stage = battle_data()['stages'][SID]
        for enemy in stage['enemies']:
            with self.subTest(enemy=enemy['id'], level=enemy['level']):
                move = enemy_preview(SID, enemy['id'], enemy['level'])['movement_reference']
                ref = move[KEY]
                self.assertEqual(ref['parameter'], 1.5)
                self.assertEqual(ref['source_selector'], '$.runes[0].blackboard[2]')
                self.assertEqual(ref['source'], stage['level_source'])
                self.assertEqual(ref['source']['sha256'], RAW_SHA)
                self.assertEqual((ref['rune_key'], ref['blackboard_key']),
                                 ('enemy_attribute_mul', 'move_speed'))
                self.assertEqual((ref['difficulty_mask_parameter'],
                                  ref['profession_mask_parameter'], ref['buildable_mask_parameter']),
                                 ('FOUR_STAR', 1023, 'ALL'))
                self.assertFalse(ref['native_target_writer_layer_verified'])
                self.assertFalse(ref['complete_effective_speed_verified'])
                self.assertIsNone(ref['combined_with_stage_multiplier_speed'])

    def test_normal_and_unrelated_stages_do_not_acquire_this_parameter(self):
        ordinary = enemy_preview(NORMAL, EID, 0)['movement_reference']
        self.assertEqual(ordinary, {'base_attribute': 2.0, 'stage_multiplier': .5,
                                   'base_times_stage_speed': 1.0,
                                   'complete_effective_speed_verified': False})
        for sid, stage in battle_data()['stages'].items():
            if sid == SID:
                continue
            self.assertNotIn(KEY, movement_reference(stage, 2.0), sid)

    def test_original_subtotal_and_missing_or_zero_base_never_become_combined_speed(self):
        stage = copy.deepcopy(battle_data()['stages'][SID])
        for base, expected in ((2.0, 1.0), (.4, .2), (0, 0), (None, None)):
            with self.subTest(base=base):
                move = movement_reference(stage, base)
                self.assertEqual(move['base_times_stage_speed'], expected)
                self.assertFalse(move['complete_effective_speed_verified'])
                self.assertEqual(move[KEY]['parameter'], 1.5)
                self.assertIsNone(move[KEY]['combined_with_stage_multiplier_speed'])
        stage['movement_multiplier'] = None
        move = movement_reference(stage, 2.0)
        self.assertIsNone(move['base_times_stage_speed'])
        self.assertIsNone(move[KEY]['combined_with_stage_multiplier_speed'])

    def test_unverified_scope_is_not_borrowed_from_the_selected_literal_record(self):
        changes = (('id', 'ro6_e_5_1'), ('difficulty', 'NORMAL'),
                   ('difficultyMask', 'ALL'), ('professionMask', 511),
                   ('buildableMask', 'MELEE'), ('key', 'enemy_attackradius_mul'))
        for field, value in changes:
            stage = copy.deepcopy(battle_data()['stages'][SID])
            target = stage if field in ('id', 'difficulty') else stage['runes'][0]
            target[field] = value
            with self.subTest(field=field, value=value):
                move = movement_reference(stage, 2.0)
                self.assertNotIn(KEY, move)
                self.assertEqual(move['base_times_stage_speed'], 1.0)
                self.assertFalse(move['complete_effective_speed_verified'])

    def test_missing_malformed_and_enemy_selected_parameters_stay_unbound(self):
        cases = []
        for value in (None, True, -1, '1.5', float('inf'), float('nan')):
            stage = copy.deepcopy(battle_data()['stages'][SID])
            stage['runes'][0]['blackboard'][2]['value'] = value
            cases.append(stage)
        for change in ('missing', 'duplicate', 'text', 'enemy_selector', 'alias', 'not_list', 'not_dict'):
            stage = copy.deepcopy(battle_data()['stages'][SID])
            rune = stage['runes'][0]
            if change == 'missing':
                rune['blackboard'].pop(2)
            elif change == 'duplicate':
                rune['blackboard'].append(copy.deepcopy(rune['blackboard'][2]))
            elif change == 'text':
                rune['blackboard'][2]['valueStr'] = '1.5'
            elif change in ('enemy_selector', 'alias'):
                rune['blackboard'].append({'key': 'enemy' if change == 'enemy_selector' else 'rune_alias',
                                          'value': 0, 'valueStr': EID})
            elif change == 'not_list':
                rune['blackboard'] = None
            else:
                rune['blackboard'].append(None)
            cases.append(stage)
        for index, stage in enumerate(cases):
            with self.subTest(case=index):
                move = movement_reference(stage, 2.0)
                self.assertNotIn(KEY, move)
                self.assertEqual(move['base_times_stage_speed'], 1.0)

    def test_new_reference_source_is_a_copy_and_callers_and_static_stage_are_preserved(self):
        stage = battle_data()['stages'][SID]
        original = copy.deepcopy(stage)
        config = {'difficulty': {'value': 4}, 'zone': {'id': 'zone_3'}}
        prior = copy.deepcopy(config)
        first = enemy_preview(SID, EID, 0, config)
        first['movement_reference'][KEY]['source']['url'] = 'changed'
        first['movement_reference'][KEY]['parameter'] = -999
        second = enemy_preview(SID, EID, 0, config)
        self.assertEqual(second['movement_reference'][KEY]['source'], original['level_source'])
        self.assertEqual(second['movement_reference'][KEY]['parameter'], 1.5)
        self.assertEqual(stage, original)
        self.assertEqual(config, prior)

    def test_default_text_retains_unknown_effective_speed_and_technical_text_labels_parameter(self):
        entry = enemy_preview(SID, EID, 0)
        ordinary = enemy_text(entry)
        technical = enemy_text(entry, technical=True)
        self.assertIn('预计有效移速：未知', ordinary)
        self.assertNotIn('关卡移速符文参数参考', ordinary)
        self.assertNotIn('基础移速×关卡倍率小计', ordinary)
        self.assertIn('关卡移速符文参数参考：1.5', technical)
        self.assertIn('基础移速×关卡倍率小计：1', technical)
        self.assertIn('符文与关卡倍率合成的移速：未知', technical)
        self.assertIn('原生目标、写入及叠加层尚未核验', technical)
        self.assertIn(entry['movement_reference'][KEY]['source']['url'], technical)
        self.assertNotIn('关卡移速符文参数参考', enemy_text(enemy_preview(NORMAL, EID, 0), True))

    def test_existing_enemy_attribute_math_and_independent_shu_periodic_unknowns_survive(self):
        entry = enemy_preview(SID, EID, 0, {'difficulty': {'value': 4}})
        self.assertEqual(entry['environment']['stats']['maxHp'], 30000)
        self.assertEqual(entry['environment']['stats']['atk'], 198)
        self.assertNotIn('moveSpeed', entry['environment']['stats'])
        self.assertIn('关卡存在未覆盖的属性修正字段。', entry['context_pending'])
        for mode in ('frames', 'continuous'):
            for window in (0, 10):
                result = calculate_damage({'operator': 'char_2025_shu', 'skill': 2,
                    'four_sui': True, 'timing_mode': mode, 'window_seconds': window,
                    'target_enemy': {'stage_id': SID, 'enemy_id': EID, 'level': 0},
                    'run_config': {'difficulty': {'value': 4}}})
                skill = result['estimate']['skill']
                for field in ('initial_seconds', 'recharge_seconds', 'cycle_seconds',
                              'cycle_damage', 'cycle_healing', 'cycle_dps', 'cycle_hps'):
                    self.assertIsNone(skill[field], (mode, window, field))
                self.assertEqual(skill['sp_recovery_per_second'], 1.0)
                self.assertEqual(result['run_resolution']['enemy']['stats']['atk'], 198)


if __name__ == '__main__':
    unittest.main()
