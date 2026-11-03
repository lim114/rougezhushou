"""Source-qualified environmental subtotals never claim full current panels."""
from copy import deepcopy
from unittest.mock import patch
import unittest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
from rouge import current_battle_reference as model
from rouge.current_enemy_forecast import forecasts,component_numbers
from rouge.current_battle_view import CurrentBattlePanel
from rouge.player_map_reader import make_reader


class CurrentEnemyForecastReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qt=QApplication.instance()or QApplication([])
        cls.stage=model.stage_reference('ro6_n_1_1')

    def config(self,grade=15,zone='zone_1'):
        return {'difficulty':{'value':grade},'zone':{'id':zone}}

    def test_qualified_four_attributes_use_existing_model_and_keep_full_total_unknown(self):
        result=forecasts(self.stage,self.config())
        duck=next(e for e in self.stage['enemies']if e['id']=='enemy_2001_duckmi')
        row=result[duck['key']]
        self.assertEqual(row['environment_component']['maxHp'],28080)
        self.assertAlmostEqual(row['environment_component']['atk'],138)
        self.assertEqual(row['environment_component']['def'],200)
        self.assertIsNone(row['complete_current_total'])
        self.assertFalse(row['actual_gameplay_verified'])
        self.assertIn('完整本局面板：未知',model.enemy_text(duck,row))
        self.assertIn('已证环境分项',model.enemy_text(duck,row))

    def test_low_grades_are_exclusive_and_zone_growth_changes_only_the_subtotal(self):
        duck=next(e for e in self.stage['enemies']if e['id']=='enemy_2001_duckmi')
        for grade,hp,atk in((0,10800,70),(1,14400,80),(2,15300,85),(3,16200,90)):
            with self.subTest(grade=grade):
                values=forecasts(self.stage,self.config(grade))[duck['key']]['environment_component']
                self.assertAlmostEqual(values['maxHp'],hp);self.assertAlmostEqual(values['atk'],atk)
        one=forecasts(self.stage,self.config())[duck['key']]['environment_component']
        two=forecasts(self.stage,self.config(zone='zone_2'))[duck['key']]['environment_component']
        self.assertAlmostEqual(two['maxHp']/one['maxHp'],1.2)
        self.assertAlmostEqual(two['atk']/one['atk'],1.2)

    def test_changed_new_stage_or_core_attribute_cannot_borrow_legacy_numbers(self):
        for mutate in('source','attribute','tier'):
            fresh=deepcopy(self.stage)
            if mutate=='source':fresh['source']['sha256']='changed'
            elif mutate=='attribute':fresh['enemies'][0]['declared_traits']['explicit_core_attributes']['atk']+=1
            else:fresh['enemies'][0]['tier']='NORMAL'
            rows=forecasts(fresh,self.config())
            self.assertIsNone(rows[fresh['enemies'][0]['key']]['environment_component'])
        changed=model.stage_reference('ro6_n_2_6')
        self.assertTrue(all(r['environment_component']is None for r in forecasts(changed,self.config()).values()))

    def test_unknown_grade_new_grade_and_missing_depth_retain_their_uncertainty(self):
        for config in(self.config(17),{'difficulty':{'value':15,'mode':'OTHER'}}):
            rows=forecasts(self.stage,config)
            self.assertTrue(all(r['environment_component']is None and r['pending']for r in rows.values()))
        rows=forecasts(self.stage,{'difficulty':{'value':15}})
        self.assertTrue(any('区域' in line for r in rows.values()for line in r['pending']))
        self.assertTrue(all(r['complete_current_total']is None for r in rows.values()))

    def test_current_unknown_tier_cannot_borrow_old_normal_classification(self):
        stage=model.stage_reference('ro6_b_4_b')
        enemy=next(e for e in stage['enemies']if e['id']=='enemy_1177_dufrbl_2')
        self.assertIsNone(enemy['tier'])
        row=forecasts(stage,self.config())[enemy['key']]
        self.assertIsNone(row['environment_component']);self.assertTrue(row['pending'])

    def test_difficulty_source_change_blocks_reuse_and_inputs_are_not_mutated(self):
        fresh=deepcopy(self.stage);fresh['difficulty_reference']['15']['bossValue']=99
        config=self.config();before=deepcopy((fresh,config))
        rows=forecasts(fresh,config)
        self.assertTrue(all(r['environment_component']is None for r in rows.values()))
        self.assertEqual((fresh,config),before)

    def test_table_numbers_change_without_resetting_branch_fold_or_selected_enemy(self):
        p=CurrentBattlePanel(self.stage['id']);self.addCleanup(p.close)
        p.set_context(self.config());tree=p.enemy_overview.tree
        group=tree.topLevelItem(0);group.setExpanded(False)
        enemy=p.result['enemies'][0];p.enemy_choices.select_value(enemy['key'])
        before=p.enemy_player.toPlainText();p.set_context(self.config(zone='zone_2'))
        self.assertEqual(p.enemy_key,enemy['key']);self.assertNotEqual(before,p.enemy_player.toPlainText())
        self.assertFalse(tree.topLevelItem(0).isExpanded())
        p.enemy_combo.setCurrentIndex(0)
        rows=[tree.topLevelItem(i).child(j)for i in range(tree.topLevelItemCount())for j in range(tree.topLevelItem(i).childCount())]
        item=next(row for row in rows if row.data(0,Qt.ItemDataRole.UserRole)==enemy['key'])
        self.assertNotEqual(item.text(1),'未知')

    def test_source_loss_clears_subtotals_and_recovery_uses_current_conditions(self):
        p=CurrentBattlePanel(self.stage['id']);self.addCleanup(p.close);p.set_context(self.config())
        self.assertTrue(p.enemy_forecasts)
        with patch.object(model,'stage_reference',return_value=None):self.assertFalse(p.refresh_reference())
        self.assertEqual(p.enemy_forecasts,{})
        p.set_context(self.config(zone='zone_2'));self.assertEqual(p.enemy_forecasts,{})
        self.assertTrue(p.refresh_reference());self.assertTrue(p.enemy_forecasts)

    def test_historical_reader_does_not_import_current_run_conditions(self):
        record={'id':self.stage['id'],'title':self.stage['name']}
        current=make_reader('battle',record,None,config=self.config());self.addCleanup(current.close)
        historical=make_reader('battle',record,None,historical=True,config=self.config());self.addCleanup(historical.close)
        self.assertTrue(current.panel.enemy_forecasts)
        self.assertEqual(historical.panel.enemy_forecasts,{})
        self.assertEqual(historical.panel.run_config,{})

    def test_large_numbers_are_plain_and_optional_gallery_is_closed_by_default(self):
        row={'environment_component':{'maxHp':1234567.891,'atk':137.999999999,'def':0,'magicResistance':None}}
        self.assertEqual(component_numbers(row),['1,234,567.89','138','0','未知'])
        p=CurrentBattlePanel(self.stage['id']);self.addCleanup(p.close)
        self.assertFalse(p.enemy_grid_toggle.isChecked())
        self.assertTrue(p.enemy_grid.isHidden());self.assertEqual(p.enemy_grid_toggle.text(),'展开敌人图册')

    def test_internal_script_identifiers_stay_out_of_player_notes(self):
        stage=model.stage_reference('ro6_n_2_1');rows=forecasts(stage,self.config())
        row=next(r for r in rows.values()if any(line.startswith('关卡脚本修正待核验：')for line in r['pending']))
        enemy=next(e for e in stage['enemies']if e['key']==row['reference_key'])
        text=model.enemy_text(enemy,row)
        self.assertIn('关卡特殊规则未计入',text)
        self.assertNotIn('env_system_new',text)
        self.assertTrue(any('env_system_new'in s for s in row['pending']))
