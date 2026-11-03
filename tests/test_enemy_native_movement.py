import copy,math,unittest
from unittest.mock import patch
from rouge.battle_preview import battle_data,enemy_preview,enemy_text
from rouge.enemy_movement_reference import conditional_movement,movement_rules,stage_movement_component
from rouge.spawn_reference import movement_reference
from rouge.damage import calculate_damage

SID='ro6_e_3_6';EID='enemy_10107_mjcdog_2';KEY='conditional_native_movement'

class EnemyNativeMovementTests(unittest.TestCase):
    def test_distinct_rune_writer_and_global_multiplier_layers(self):
        r=conditional_movement(2,1.5,.5)
        self.assertEqual(r['product_fp_raw'],3*(1<<32));self.assertEqual(r['written_move_speed_attribute'],3)
        self.assertEqual(r['conditional_speed_tiles_per_second'],1.5)
        self.assertEqual(r['speed_fp_raw'],int(1.5*(1<<32)))
        self.assertIsNone(r['complete_effective_speed']);self.assertFalse(r['rune_execution_verified'])
    def test_lower_bound_is_before_global_multiplier_and_applies_to_zero(self):
        for base,factor in ((0,1.5),(.01,1.5),(2,0)):
            r=conditional_movement(base,factor,.5)
            self.assertEqual(r['written_move_speed_attribute'],0.10000000149011612)
            self.assertEqual(r['conditional_speed_tiles_per_second'],0.05000000074505806)
        zero=conditional_movement(2,1.5,0)
        self.assertEqual(zero['written_move_speed_attribute'],3);self.assertEqual(zero['conditional_speed_tiles_per_second'],0)
    def test_float_write_then_reread_is_not_a_single_double_product(self):
        r=conditional_movement(.4,1.5,.5)
        self.assertEqual(r['product_fp_raw'],2576980416)
        self.assertEqual(r['written_move_speed_attribute'],.6000000238418579)
        self.assertEqual(r['reread_field_fp_raw'],2576980480)
        self.assertEqual(r['conditional_speed_tiles_per_second'],.30000001192092896)
        self.assertNotEqual(r['conditional_speed_tiles_per_second'],.4*1.5*.5)
    def test_two_source_layers_are_ordered_and_independent(self):
        r=conditional_movement(.04,1.5,.5)
        naive=conditional_movement(.04*.5,1.5,1)
        self.assertEqual(r['conditional_speed_tiles_per_second'],.05000000074505806)
        self.assertEqual(naive['conditional_speed_tiles_per_second'],.10000000149011612)
    def test_native_branch_unwritten_flags_are_not_falsely_proven_by_public_no_upper_rule(self):
        r=conditional_movement(2,1.5,.5)
        self.assertFalse(r['native_unwritten_max_flag_baseline_verified'])
        self.assertFalse(r['native_unwritten_selector_pointer_baseline_verified'])
        self.assertEqual(r['published_standard_range_source']['revision'],440563)
        self.assertGreaterEqual(len(r['conditions']),3)
        self.assertIsNone(r['actual_position_or_arrival_time'])
        self.assertFalse(r['game_clock_speed_multiplier_assumed'])
    def test_invalid_and_out_of_native_range_never_produce_usable_speed(self):
        for index in range(3):
            for bad in (None,True,False,-1,'1.5',float('inf'),float('nan')):
                values=[2,1.5,.5];values[index]=bad;r=conditional_movement(*values)
                self.assertIsNone(r['conditional_speed_tiles_per_second'])
        for values in ((1e308,1.5,.5),(2,1e308,.5),(2,1.5,1e308),(1e9,1e9,.5)):
            self.assertIsNone(conditional_movement(*values)['conditional_speed_tiles_per_second'])
    def test_all_twelve_selected_stage_enemies_have_separate_conditioned_components(self):
        stage=battle_data()['stages'][SID];self.assertEqual(len(stage['enemies']),12)
        for enemy in stage['enemies']:
            with self.subTest(enemy=enemy['id']):
                r=enemy_preview(SID,enemy['id'],enemy['level'],{'difficulty':{'value':4}})
                c=r['movement_reference'][KEY];env=r['environment']
                self.assertTrue(c['native_field_writer_bound']);self.assertFalse(c['rune_execution_verified'])
                self.assertEqual(c,env['movement_source_reference'])
                self.assertEqual(env['stats']['moveSpeed'],r['reference_stats']['moveSpeed'])
                self.assertIsNone(c['complete_effective_speed']);self.assertIsNone(r['movement_reference']['stage_move_speed_rune_reference']['combined_with_stage_multiplier_speed'])
    def test_only_exact_unchanged_stage_source_supplies_factor(self):
        original=copy.deepcopy(battle_data()['stages'][SID]);raw=movement_reference(original,2)['stage_move_speed_rune_reference']
        changes=(('id','ro6_n_3_6'),('difficulty','NORMAL'),('movement_multiplier',1))
        for key,value in changes:
            d=copy.deepcopy(original);d[key]=value;self.assertIsNone(stage_movement_component(d,2,raw))
        d=copy.deepcopy(original);d['level_source']['sha256']='changed';self.assertIsNone(stage_movement_component(d,2,raw))
        for key,value in (('parameter',2),('source_selector','$.runes[1].blackboard[0]')):
            d=copy.deepcopy(raw);d[key]=value;self.assertIsNone(stage_movement_component(original,2,d))
    def test_ordinary_and_unrelated_stages_do_not_acquire_source_component(self):
        for sid,stage in battle_data()['stages'].items():
            if sid==SID:continue
            self.assertNotIn(KEY,movement_reference(stage,2),sid)
    def test_changed_or_ambiguous_blackboard_keeps_parameters_unbound(self):
        stage=copy.deepcopy(battle_data()['stages'][SID])
        stage['runes'][0]['blackboard'].append({'key':'enemy','value':0,'valueStr':EID})
        self.assertNotIn(KEY,movement_reference(stage,2))
        stage=copy.deepcopy(battle_data()['stages'][SID]);stage['runes'][0]['blackboard'][2]['value']=2
        self.assertNotIn(KEY,movement_reference(stage,2))
    def test_complete_speed_and_spawn_times_remain_unknown_with_known_subtotal(self):
        entry=enemy_preview(SID,EID,0);text=enemy_text(entry);tech=enemy_text(entry,True)
        self.assertIn('预计有效移速：未知',text)
        self.assertIn('符文写入移速属性：3',text)
        self.assertIn('无其他属性修正的条件移速：1.5 格/秒',text)
        self.assertIn('实际执行资格/动态修正尚未核验',tech)
        self.assertIn('字段接收、乘法写入及读取层已绑定',tech)
        self.assertIn('实际实例的原生目标、写入及叠加层尚未核验',tech)
        self.assertIn('未写最大范围标志及选择器指针',tech)
        self.assertNotIn('https://',text)
    def test_actual_target_calculation_keeps_original_damage_and_target_float_identity(self):
        scenario={'operator':'mechanist','skill':1,'target_enemy':{'stage_id':SID,'enemy_id':EID,'level':0.0},
            'run_config':{'difficulty':{'value':4}},'enemy_defense':99999,'enemy_resistance':99}
        r=calculate_damage(scenario);env=r['run_resolution']['enemy']
        direct=calculate_damage({'operator':'mechanist','skill':1,'enemy_defense':500,'enemy_resistance':30})
        self.assertEqual(r['total_damage'],direct['total_damage']);self.assertIs(type(env['level']),float)
        self.assertEqual(env['movement_source_reference']['conditional_speed_tiles_per_second'],1.5)
        self.assertEqual(env['stats']['moveSpeed'],2);self.assertEqual(scenario['enemy_defense'],99999)
    def test_unknown_input_keeps_reference_but_no_numeric_component(self):
        r=movement_reference(battle_data()['stages'][SID],None)
        self.assertEqual(r[KEY]['state'],'unavailable_parameters')
        self.assertIsNone(r[KEY]['conditional_speed_tiles_per_second'])
    def test_returned_source_mutation_does_not_pollute_following_queries_or_tables(self):
        before=copy.deepcopy(battle_data()['stages'][SID]);rules=copy.deepcopy(movement_rules())
        first=enemy_preview(SID,EID,0);first['movement_reference'][KEY]['source']['sha256']='wrong'
        first['movement_reference'][KEY]['published_standard_range_source']['revision']=0
        first['environment']['movement_source_reference']['conditions'].clear()
        again=enemy_preview(SID,EID,0)
        self.assertEqual(battle_data()['stages'][SID],before);self.assertEqual(movement_rules(),rules)
        self.assertEqual(again['movement_reference'][KEY]['published_standard_range_source']['revision'],440563)

class EnemyNativeMovementViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from PySide6.QtWidgets import QApplication
        cls.qt=QApplication.instance() or QApplication([])
    def test_source_condition_subtotal_visible_and_selection_survives_refresh(self):
        from rouge.battle_view import BattlePreviewPanel
        panel=BattlePreviewPanel();self.addCleanup(panel.close);panel.show();panel.set_stage(SID);self.qt.processEvents()
        i=next(i for i in range(panel.enemy_combo.count()) if (panel.enemy_combo.itemData(i) or (None,))[0]==EID)
        panel.enemy_combo.setCurrentIndex(i);self.qt.processEvents()
        self.assertIn('无其他属性修正的条件移速：1.5 格/秒',panel.enemy_detail.toPlainText())
        selected=panel.enemy_combo.currentData();panel.set_stage(SID);self.qt.processEvents()
        self.assertEqual(panel.enemy_combo.currentData(),selected)
        panel.technical.setChecked(True);self.qt.processEvents()
        self.assertIn('未写最大范围标志及选择器指针',panel.enemy_detail.toPlainText())
if __name__=='__main__':unittest.main()
