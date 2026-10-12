from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import unittest
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QTextCursor
from rouge.battle_preview import battle_data,display_cell
from rouge.battle_reward_planning import reward_data,stage_reward_sources,reward_source_text
from rouge.battle_view import BattlePreviewPanel
from rouge.node_catalog_view import NodeCatalogPanel


class BattleRewardPlanningTests(unittest.TestCase):
    def test_all_fixed_stages_keep_exact_source_and_unknown_actual_total(self):
        self.assertEqual(set(reward_data()['stages']),set(battle_data()['stages']))
        seen=set()
        for sid,stage in battle_data()['stages'].items():
            result=stage_reward_sources(sid)
            self.assertEqual(result['source']['sha256'],stage['level_source']['sha256'])
            self.assertIsNone(result['actual_reward_total']);self.assertIsNone(result['probability'])
            self.assertFalse(result['complete_settlement_pool_known'])
            for row in result['rows']:
                self.assertIsNone(row['actual_activation']);self.assertIsNone(row['actual_reward'])
                self.assertFalse(row['quantity_is_total']);seen.add(row['entity_id'])
        self.assertEqual(len(battle_data()['stages']),105)
        from rouge.rare_reward_sources import rare_reward_data
        self.assertEqual(seen,set(reward_data()['rules'])|set(rare_reward_data()['fixed_spawn_entity_ids']))

    def test_primary_device_counts_cost_and_same_name_id_distinction(self):
        result=stage_reward_sources('ro6_n_1_1');rows={r['entity_id']:r for r in result['rows']}
        self.assertEqual(rows['trap_321_shnbox']['rule']['outcomes'][0]['quantity'],2)
        self.assertEqual(rows['trap_322_shrbox']['rule']['outcomes'][0]['quantity'],5)
        self.assertEqual(rows['trap_323_shsbox']['rule']['outcomes'][0]['quantity'],10)
        treasure=rows['trap_320_shtlbx']['rule']['outcomes'][0]
        self.assertEqual((treasure['quantity'],treasure['cost_quantity'],treasure['cost_resource']),(1,50,'deployment_points'))
        self.assertFalse(treasure['complete_item_pool_known'])
        self.assertNotEqual(rows['trap_321_shnbox']['name'],rows['enemy_2152_shezlc']['name'])
        self.assertIn('不能把两条来源各算一次10',reward_source_text(result,rows['trap_323_shsbox']))

    def test_exact_branch_override_and_every_empty_random_alternative_remain(self):
        result=stage_reward_sources('ro6_n_1_1')
        boxes=[r for r in result['rows'] if r['entity_id']=='trap_323_shsbox']
        self.assertEqual({r['explicit_branch_id'] for r in boxes},{'shsbox1','shsbox2'})
        self.assertTrue(all(r['branch_configuration_exists'] for r in boxes))
        self.assertTrue(all(r['explicit_branch_reward_actions'] for r in boxes))
        self.assertEqual(len(result['random_groups']),2)
        self.assertTrue(all(any(not m['raw'].get('key') for m in g['members']) for g in result['random_groups']))
        self.assertTrue(all(len(g['members'])==5 for g in result['random_groups']))
        moving=[r for r in result['rows'] if r['entity_id']=='enemy_2152_shezlc']
        self.assertTrue(moving);self.assertTrue(all(r['display_cell'] is None for r in moving))

    def test_original_coordinates_are_flipped_only_for_declarations(self):
        result=stage_reward_sources('ro6_n_1_1');stage=battle_data()['stages']['ro6_n_1_1']
        for row in result['rows']:
            if row['kind']=='predefined_device':
                self.assertEqual(row['display_cell'],display_cell(row['raw']['position'],len(stage['map']),len(stage['map'][0])))
        self.assertIsNone(display_cell({'row':-1,'col':0},7,11))
        self.assertIsNone(display_cell({'row':True,'col':0},7,11))

    def test_unknown_higher_or_multiple_enemy_levels_do_not_inherit_ten(self):
        import rouge.battle_reward_planning as module
        for values in ([1],[2],[0,1],[]):
            fake={'moving_enemy_refs':[{'raw':{'level':v}} for v in values]}
            rule=module._rule('enemy_2152_shezlc',fake)
            self.assertFalse(rule['documented_base_level_matches_reference'])
            self.assertTrue(all(o['quantity'] is None for o in rule['outcomes']))
        zero=module._rule('enemy_2152_shezlc',{'moving_enemy_refs':[{'raw':{'level':0}}]})
        self.assertEqual([o['quantity'] for o in zero['outcomes']],[10,-10])

    def test_public_queries_are_copies_and_invalid_stage_rejected(self):
        before=deepcopy(reward_data());result=stage_reward_sources('ro6_n_1_1')
        result['rows'][0]['rule']['outcomes'][0]['quantity']=999
        result['random_groups'].clear();self.assertEqual(reward_data(),before)
        for value in ('missing-stage','',None,True,[],{}):
            with self.assertRaises(ValueError):stage_reward_sources(value)

    def test_extractor_keeps_branch_activation_alias_conflict_and_db_ref_boundary(self):
        path=Path(__file__).resolve().parents[1]/'scripts/build_battle_reward_reference.py'
        spec=importlib.util.spec_from_file_location('reward_builder',path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        obj={'alias':'same','inst':{'characterKey':'trap_321_shnbox'},'position':{'row':1,'col':2}}
        raw={'predefines':{'tokenInsts':[obj]},'hardPredefines':{'tokenInsts':[deepcopy(obj)]},
            'branches':{'x':{'phases':[{'actions':[{'actionType':'ACTIVATE_PREDEFINED','key':'same','randomSpawnGroupKey':'g'},
                {'actionType':'EMPTY','key':'','randomSpawnGroupKey':'g'}]}]}},
            'enemyDbRefs':[{'id':'enemy_2152_shezlc','level':0}],'enemies':[]}
        result=module.extract_level(raw,{'sha256':'public-test'})
        self.assertEqual(len(result['declarations']),2)
        self.assertEqual(len(result['actions'][0]['definition_ids']),2)
        self.assertEqual(len(result['random_groups'][0]['members']),2)
        self.assertFalse(result['initial_records']);self.assertEqual(len(result['moving_enemy_refs']),1)


class BattleRewardViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance() or QApplication([])

    def test_offscreen_fixed_panel_selection_marks_definition_cell_and_keeps_reading(self):
        panel=BattlePreviewPanel();self.addCleanup(panel.close);panel.resize(1050,760);panel.show();panel.set_stage('ro6_n_1_1');self.qt.processEvents()
        index=next(i for i in range(1,panel.reward_combo.count()) if panel.reward_combo.itemData(i)['entity_id']=='trap_323_shsbox')
        panel.reward_combo.setCurrentIndex(index);self.qt.processEvents();row=panel.reward_combo.currentData()
        self.assertEqual(panel.grid.reference_cell,row['display_cell']);self.assertEqual(panel.original.reference_cell,row['display_cell'])
        self.assertIn('实际奖励总量',panel.spawn_detail.toPlainText());self.assertIn('不同目标',panel.spawn_detail.toPlainText())
        cursor=panel.spawn_detail.textCursor();cursor.setPosition(5);cursor.setPosition(15,QTextCursor.MoveMode.KeepAnchor);panel.spawn_detail.setTextCursor(cursor)
        selection=cursor.selectedText();panel.spawn_detail.verticalScrollBar().setValue(12);scroll=panel.spawn_detail.verticalScrollBar().value();text=panel.spawn_detail.toPlainText()
        panel.render_rows();self.qt.processEvents()
        self.assertEqual(panel.reward_combo.currentData()['id'],row['id']);self.assertEqual(panel.spawn_detail.toPlainText(),text)
        self.assertEqual(panel.spawn_detail.textCursor().selectedText(),selection);self.assertEqual(panel.spawn_detail.verticalScrollBar().value(),scroll)
        panel.set_context({'floor':2});self.assertEqual(panel.reward_combo.currentData()['id'],row['id'])
        panel.technical.setChecked(True);self.assertIn(row['source_selector'],panel.spawn_detail.toPlainText())
        self.assertEqual(panel.grid.reference_cell,row['display_cell'])
        self.assertIsNotNone(panel._shown_enemy)
        self.assertIn(panel._shown_enemy[1],panel.enemy_detail.toPlainText())

    def test_branch_positions_unknown_and_stage_switch_or_spawn_clears_marker(self):
        panel=BattlePreviewPanel();self.addCleanup(panel.close);panel.set_stage('ro6_n_1_1')
        index=next(i for i in range(1,panel.reward_combo.count()) if panel.reward_combo.itemData(i)['kind']=='moving_enemy_action')
        panel.reward_combo.setCurrentIndex(index)
        self.assertIsNone(panel.grid.reference_cell);self.assertIn('位置：未绑定',panel.spawn_detail.toPlainText())
        panel.reward_combo.setCurrentIndex(1);self.assertIsNotNone(panel.grid.reference_cell)
        panel._spawn_selected(panel.spawn_list.currentItem());self.assertEqual(panel.reward_combo.currentIndex(),0);self.assertIsNone(panel.grid.reference_cell)
        panel.set_stage('ro6_n_1_2');self.assertEqual(panel.reward_combo.currentIndex(),0)

    def test_node_directory_battle_has_reward_conditions_and_original_stage_signal(self):
        panel=NodeCatalogPanel();self.addCleanup(panel.close)
        i=next(i for i,e in enumerate(panel.entries) if e['kind']=='battle' and e['record'].get('id')=='ro6_n_1_1')
        panel.list.setCurrentRow(i);text=panel.detail.toPlainText()
        self.assertIn('条件奖励资料',text);self.assertIn('50点部署费用',text);self.assertIn('完整结算池：未知',text)
        calls=[];panel.stageSelected.connect(calls.append);panel.battle_button.click();self.assertEqual(calls,['ro6_n_1_1'])


if __name__=='__main__':unittest.main()
