"""Public conditional settlements, source boundaries and actual Qt entry points."""
from copy import deepcopy
import json,time,unittest
from pathlib import Path
from PySide6.QtCore import QUrl
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication
from rouge import base_settlement_planning as p
from rouge.battle_reward_planning import stage_reward_sources,reward_source_text
from rouge.offline_tools_view import (OfflineToolsPanel,QUERIES,public_payload,exploration_presets,
    run_offline_query,render_offline_result)
from rouge.node_catalog_view import NodeCatalogPanel
from rouge.battle_view import BattlePreviewPanel

ROOT=Path(__file__).resolve().parents[1]

def declaration(stage='ro6_n_1_1',floor=1,entry='map_battle',special=False,victory=True):
    return {'stage_id':stage,'battle_floor':floor,'entry_context':entry,'special_region':special,'victory_declared':victory}

class BaseSettlementTests(unittest.TestCase):
    def test_source_reconstruction_all_tables_and_exact_stage_pages(self):
        from scripts.build_base_settlement_reference import build
        data=p.reference_data();self.assertEqual(build(ROOT),data)
        self.assertEqual(len(data['stages']),105);self.assertEqual(len(data['main_floor_table']),6)
        self.assertEqual(len(data['special_battle_table']),18)
        self.assertEqual(len({key for rule in data['special_battle_table'] for key in rule['stage_ids']}),27)
        self.assertTrue(all(len(row)==4 for row in data['main_floor_table'].values()))
        self.assertEqual(data['portal_rule']['inherited_column_kinds'],['normal','emergency'])
        self.assertEqual(data['portal_rule']['undocumented_column_kinds'],['boss','boss_pursuit'])
        self.assertTrue(all(p.stage_base_rewards(key)['rows'] for key in data['stages']))

    def test_main_floor_base_and_full_technology_columns_not_concatenated_or_auto_applied(self):
        for stage,floor,xp,gold,full in (('ro6_n_1_1',1,10,1,13),('ro6_e_1_1',1,12,2,15),
                ('ro6_b_1',3,32,5,42),('ro6_b_4',5,50,8,66)):
            r=p.stage_base_rewards(stage,floor,'map_battle',False)
            matched=[row for row in r['rows'] if row['status']=='matched'];self.assertEqual(len(matched),1)
            row=matched[0];self.assertEqual(row['base_experience_reference'],xp)
            self.assertEqual(row['base_gold_reference'],{'minimum':gold,'maximum':gold})
            self.assertEqual(row['full_technology_experience_reference'],full);self.assertFalse(row['full_technology_auto_applied'])
            self.assertIsNone(r['actual_reward_total']);self.assertFalse(r['actual_victory_verified'])

    def test_sixth_floor_uses_exact_public_zero_area_proof_without_changing_old_metadata(self):
        data=p.reference_data();ids={k for k,row in data['stages'].items() if row['floor_zero_binding']}
        self.assertEqual(ids,{'ro6_n_6_1','ro6_n_6_2','ro6_e_6_1','ro6_e_6_2','ro6_b_6'})
        for identity in ids:
            r=p.stage_base_rewards(identity,6,'map_battle',False)
            self.assertIsNone(r['documented_origin_floors']);self.assertEqual(r['settlement_origin_floors'],[6])
            self.assertEqual(r['floor_zero_binding']['original_name'],'源流交汇处')
            self.assertEqual(sum(row['status']=='matched' for row in r['rows']),1)
        boss=next(row for row in p.stage_base_rewards('ro6_b_6',6,'map_battle',False)['rows'] if row['status']=='matched')
        self.assertEqual(boss['base_experience_reference'],70)
        self.assertIn('旧目录层数未归类',p.stage_reward_text(p.stage_base_rewards('ro6_b_6')))
        self.assertIn('地图模板与连线仍未知',p.stage_reward_text(p.stage_base_rewards('ro6_b_6')))

    def test_six_event_pursuit_aliases_retain_different_contexts_without_prefix_choice(self):
        for identity in ('ro6_t_13','ro6_c_5','ro6_t_14','ro6_c_6','ro6_t_15','ro6_c_7'):
            unknown=p.stage_base_rewards(identity)
            self.assertEqual({row['base_experience_reference'] for row in unknown['rows']},{0,30})
            self.assertTrue(all(row['status']=='unknown' for row in unknown['rows']))
            for context,expected in (('event_battle',30),('pursuit',0)):
                rows=[row for row in p.stage_base_rewards(identity,4,context,False)['rows'] if row['status']=='matched']
                self.assertEqual(len(rows),1);self.assertEqual(rows[0]['base_experience_reference'],expected)

    def test_boss_pursuit_has_normal_reward_reference_and_ordinary_pursuit_has_zero_components(self):
        for identity,floor,xp in (('ro6_b_1_b',3,32),('ro6_b_4_b',5,50)):
            rows=[row for row in p.stage_base_rewards(identity,floor,'pursuit',False)['rows'] if row['status']=='matched']
            self.assertEqual(rows[0]['base_experience_reference'],xp)
        row=next(row for row in p.stage_base_rewards('ro6_c_1',1,'pursuit',False)['rows'] if row['status']=='matched')
        self.assertEqual(row['base_experience_reference'],0);self.assertEqual(row['base_gold_reference']['maximum'],0)
        self.assertFalse(row['native_settlement_script_verified'])

    def test_special_normal_emergency_overrides_and_all_resident_variants(self):
        for identity,xp,gold in (('ro6_t_3',13,2),('ro6_e_t_3',24,3),('ro6_t_5',25,4),('ro6_e_t_5',36,8)):
            rows=[r for r in p.stage_base_rewards(identity,None,'event_battle',True)['rows'] if r['status']=='matched']
            self.assertEqual(rows[0]['base_experience_reference'],xp);self.assertEqual(rows[0]['base_gold_reference']['minimum'],gold)
        for identity in ('ro6_t_8','ro6_t_8_b','ro6_t_8_c'):
            row=next(r for r in p.stage_base_rewards(identity,None,'map_battle',False)['rows'] if r['status']=='matched')
            self.assertEqual(row['base_experience_reference'],15);self.assertFalse(row['native_settlement_script_verified'])

    def test_special_gold_range_and_unknown_preserved_as_independent_components(self):
        result=p.settlements(steps=[declaration('ro6_t_1',None,'event_battle'),declaration('ro6_t_2',None,'event_battle')])
        self.assertEqual(result['conditional_base_total'],{'experience':22,'gold':{'minimum':4,'maximum':5}})
        result=p.settlements(steps=[declaration('ro6_t_12',None)])
        self.assertEqual(result['known_base_subtotal']['experience'],36);self.assertIsNone(result['conditional_base_total'])
        self.assertIsNone(result['rows'][0]['conditional_base_gold'])
        self.assertIn('base_gold_not_documented',result['rows'][0]['unknown_components'])

    def test_portal_battle_origin_floor_unknown_stays_unknown_despite_zone_suffix(self):
        graph={'zone_id':'zone_portal_normal_5_3','nodes':[{'id':'a','row':0,'col':0}]}
        step=declaration();step.pop('battle_floor');step.pop('special_region');step['target']='a'
        r=p.settlements(steps=[step],graph=graph)
        self.assertIsNone(r['conditional_base_total']);self.assertTrue(r['rows'][0]['battle_references'][0]['special_region_declared'])
        step['battle_floor']=1;r=p.settlements(steps=[step],graph=graph)
        self.assertEqual(r['conditional_base_total']['experience'],10)
        step['battle_floor']=5;r=p.settlements(steps=[step],graph=graph)
        self.assertIsNone(r['conditional_base_total'])
        self.assertFalse(r['actual_victory_verified'])

    def test_unknown_region_keeps_main_and_portal_source_rows(self):
        r=p.stage_base_rewards('ro6_n_1_1',1,'map_battle')
        self.assertEqual(len(r['rows']),2);self.assertTrue(all(row['status']=='unknown' for row in r['rows']))

    def test_portal_boss_and_boss_pursuit_blank_source_never_reuse_main_reward(self):
        for identity,context in (('ro6_b_1','map_battle'),('ro6_b_1_b','pursuit')):
            step=declaration(identity,3,context,True)
            r=p.settlements(steps=[step]);self.assertFalse(r['complete_conditional_base_reference'])
            self.assertIsNone(r['conditional_base_total']);self.assertEqual(r['known_base_subtotal']['experience'],0)
            row=next(row for row in r['rows'][0]['battle_references'][0]['rows'] if row['status']=='matched')
            self.assertEqual(row['region_scope'],'portal');self.assertIsNone(row['base_experience_reference'])
            self.assertIsNone(row['base_gold_reference']);self.assertTrue(row['blank_source_does_not_exclude_entry'])
            self.assertIn('不套主层数值',p.stage_reward_text(p.stage_base_rewards(identity,3,context,True)))
            step['special_region']=False
            self.assertEqual(p.settlements(steps=[step])['conditional_base_total']['experience'],32)

    def test_ambiguous_identity_not_resolved_to_richer_stage_or_probability(self):
        step=declaration();step.pop('stage_id');step['stage_ids']=['ro6_n_1_1','ro6_e_1_1']
        r=p.settlements(steps=[step]);self.assertIsNone(r['conditional_base_total'])
        self.assertEqual(r['rows'][0]['stage_candidates'],step['stage_ids']);self.assertIsNone(r['probability'])
        self.assertEqual(len(r['rows'][0]['battle_references']),2)

    def test_victory_unknown_never_becomes_observed_reward_or_ledger_update(self):
        r=p.settlements(steps=[declaration(victory=None)])
        self.assertEqual(r['rows'][0]['conditional_base_experience'],10);self.assertIsNone(r['conditional_base_total'])
        self.assertFalse(r['rows'][0]['admitted_to_known_base_subtotal']);self.assertFalse(r['inventory_updated'])
        self.assertIsNone(r['actual_reward_total']);self.assertFalse(r['complete_settlement_pool_known'])
        self.assertFalse(r['actual_victory_verified'])

    def test_current_graph_content_only_and_exact_title_not_history_or_surname(self):
        graph={'zone_id':'zone_1','nodes':[{'id':'a','row':0,'col':0,'observed_type':'作战',
            'remembered_content':{'kind':'battle','title':'猎犬病原','variant_id':'ro6_n_1_1'}},
            {'id':'b','row':0,'col':1,'content':{'kind':'battle','title':'陌生旅伴','variant_id':'ro6_n_1_1'}}]}
        before=deepcopy(graph);r=p.settlements(graph=graph)
        self.assertEqual(len(r['rows']),2);self.assertTrue(all(not row['stage_candidates'] for row in r['rows']))
        self.assertEqual(r['rows'][1]['unresolved_stage_ids'],['ro6_n_1_1']);self.assertEqual(graph,before)
        self.assertIsNone(p.settlements()['conditional_base_total'])

    def test_invalid_declarations_are_rejected_without_filling_context(self):
        for kwargs in ({'stage_id':'猎犬病原'},{'stage_id':{}},{'stage_id':'ro6_n_1_1','battle_floor':0},
                {'stage_id':'ro6_n_1_1','battle_floor':True},{'stage_id':'ro6_n_1_1','special_region':1}):
            with self.subTest(kwargs=kwargs),self.assertRaises(ValueError):p.stage_base_rewards(**kwargs)
        for steps in ([{'stage_id':'ro6_n_1_1','stage_ids':['ro6_n_1_1']}],[{'stage_ids':[]}],
                [{'stage_id':'ro6_n_1_1','victory_declared':1}],[{'target':'absent'}],
                [{'stage_id':'ro6_n_1_1','gold_multiplier':2}]):
            with self.subTest(steps=steps),self.assertRaises(ValueError):p.settlements(steps=steps)
        for graph in ({'nodes':[{'id':'a','row':0,'col':0,'content':[]}]},
                {'nodes':[{'id':'a','row':0,'col':0},{'id':'a','row':1,'col':0}]}):
            with self.assertRaises(ValueError):p.settlements(graph=graph)

    def test_incomplete_current_variants_are_rejected_instead_of_resolved_to_known_candidate(self):
        for content in ({'variants':[{'id':'ro6_n_1_1'},{'id':None}]},
                {'variants':[{'id':'ro6_n_1_1'},None]},{'variants':{}},
                {'variant_id':[]},{'variant_id':'ro6_n_1_1','variants':[{}]}):
            graph={'nodes':[{'id':'a','row':0,'col':0,'content':
                {'kind':'battle','title':'猎犬病原',**content}}]}
            with self.subTest(content=content),self.assertRaises(ValueError):
                p.settlements(steps=[{'target':'a','battle_floor':1,'entry_context':'map_battle',
                    'special_region':False,'victory_declared':True}],graph=graph)

    def test_existing_device_reward_scope_and_base_reference_stay_independent(self):
        r=stage_reward_sources('ro6_n_1_1');self.assertIsNone(r['actual_reward_total'])
        text=reward_source_text(r)
        self.assertIn('条件奖励资料',text);self.assertIn('基础战斗结算分项',text)
        self.assertIn('未混入基础分项',text);self.assertIn('完整结算池：未知',text)
        self.assertTrue(all(row['actual_reward'] is None for row in r['rows']))

class BaseSettlementViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance() or QApplication([])
    def setUp(self):
        self.panel=OfflineToolsPanel();self.panel.resize(1000,750);self.panel.show();self.qt.processEvents()
        self.addCleanup(self.panel.close)
    def run_query(self):
        self.panel.run_button.click();end=time.monotonic()+8
        while self.panel._workers and time.monotonic()<end:self.qt.processEvents();time.sleep(.005)
        self.qt.processEvents();self.assertFalse(self.panel._workers)
        self.assertIsNotNone(self.panel.result_snapshot(),self.panel.status.text())
    def graph(self):return next(r['payload']['graph'] for r in exploration_presets('settlements') if r['id']=='base-graph-reference')

    def test_new_query_all_eight_public_scenarios_run_and_render_in_qt(self):
        # Keep the original coverage and the four subsequent mechanical queries;
        # historical exploration catalog still includes all13 original entries.
        self.assertEqual(len(QUERIES['calibration'])+len(QUERIES['battle']),28)
        self.assertIn(('relic-panels','藏品组合与面板差值诊断'),QUERIES['calibration'])
        for command in ('barrier-ledger','shield-grants','shield-inventory','explosion-values','modifier-values','regen-clock','regen-attributes'):
            self.assertIn(command,dict(QUERIES['calibration']))
        self.assertEqual(len(QUERIES['exploration']),13)
        self.panel.select_query('exploration','settlements');presets=exploration_presets('settlements')
        self.assertEqual(len(presets),8)
        for preset in presets:
            self.panel.preset.setCurrentIndex(self.panel.preset.findData(preset['id']));self.panel.load_example.click()
            before=self.panel.editor.toPlainText();self.run_query()
            self.assertEqual(self.panel.editor.toPlainText(),before)
            text=self.panel.result_view.toPlainText();self.assertIn('战斗基础奖励与路线分项',text)
            self.assertIn('实际完整奖励总量：未知',text);self.assertFalse(self.panel._result_links)
            self.assertFalse(self.panel.result_snapshot()['inventory_updated'])
            if preset['id']=='base-graph-reference':self.assertIn('节点数组次序不表示路线',text)

    def test_import_fixed_stage_appends_reference_without_victory_or_overwriting_steps(self):
        self.panel.select_query('exploration','settlements');before=json.loads(self.panel.editor.toPlainText())
        self.panel.set_stage('ro6_t_1');self.assertTrue(self.panel.import_stage.isEnabled());self.panel.import_stage.click()
        after=json.loads(self.panel.editor.toPlainText());self.assertEqual(after['steps'][:-1],before['steps'])
        self.assertEqual(after['steps'][-1],{'stage_id':'ro6_t_1'});self.run_query()
        self.assertIsNone(self.panel.result_snapshot()['conditional_base_total'])
        self.assertIn('固定关卡选择的显式参考',self.panel.result_view.toPlainText())

    def test_imported_graph_append_node_reference_and_epoch_guard(self):
        graph=self.graph();self.panel.select_query('exploration','settlements')
        self.panel.editor.setPlainText(json.dumps({'steps':None}));self.panel.set_graph(graph,epoch='public-run',historical=False)
        self.panel.import_graph.click();self.panel.graph_node.setCurrentIndex(self.panel.graph_node.findData('a'))
        self.panel.fill_node.click();payload=json.loads(self.panel.editor.toPlainText())
        self.assertEqual(payload['steps'],[{'target':'a'}]);self.run_query()
        self.assertEqual(set(self.panel._result_links),{'a'});text=self.panel.result_view.toPlainText()
        self.assertIn('第1行、第1列',text);self.assertIn('猎犬病原',text)
        calls=[];self.panel.mapNodeSelected.connect(lambda key,binding:calls.append((key,binding)))
        url=QUrl('rouge-map-node:a');self.panel.result_view.anchorClicked.emit(url)
        self.assertEqual(calls[0][0],'a');self.assertEqual(calls[0][1]['epoch'],'public-run')
        self.panel.set_graph(graph,epoch='other-run');self.panel.result_view.anchorClicked.emit(url)
        self.assertEqual(len(calls),1);self.assertIn('过期',self.panel.status.text())

    def test_refresh_and_family_switch_preserve_complete_input_result_and_reading(self):
        self.panel.select_query('exploration','settlements');self.run_query();self.panel.technical.setChecked(True)
        cursor=self.panel.editor.textCursor();cursor.setPosition(5);cursor.setPosition(15,QTextCursor.MoveMode.KeepAnchor)
        self.panel.editor.setTextCursor(cursor);self.panel.result_view.verticalScrollBar().setValue(30)
        snapshot=(self.panel.editor.toPlainText(),self.panel.editor.textCursor().selectedText(),
            self.panel.result_snapshot(),self.panel.result_view.toHtml(),self.panel.result_view.verticalScrollBar().value())
        for sequence in (False,True):
            self.panel.set_graph(self.graph(),epoch=1,historical=sequence);self.panel.set_stage('ro6_b_6')
            self.panel.select_query('calibration','panel');self.panel.select_query('exploration','settlements');self.qt.processEvents()
            self.assertEqual((self.panel.editor.toPlainText(),self.panel.editor.textCursor().selectedText(),
                self.panel.result_snapshot(),self.panel.result_view.toHtml(),self.panel.result_view.verticalScrollBar().value()),snapshot)

    def test_actual_fixed_battle_and_catalog_details_include_base_reference(self):
        battle=BattlePreviewPanel();self.addCleanup(battle.close);battle.set_stage('ro6_e_t_3');battle.reward_summary.click();self.qt.processEvents()
        self.assertIn('基础战斗结算分项',battle.spawn_detail.toPlainText())
        self.assertIn('基础指挥经验 24',battle.spawn_detail.toPlainText())
        panel=NodeCatalogPanel();self.addCleanup(panel.close)
        panel.kind.setCurrentIndex(panel.kind.findData('battle'))
        panel.list.setCurrentRow(next(i for i,row in enumerate(panel.entries) if row['record'].get('id')=='ro6_t_12'))
        self.assertIn('基础战斗结算分项',panel.detail.toPlainText());self.assertIn('源石锭 未知',panel.detail.toPlainText())
        self.assertIn('实际胜利、领取',panel.detail.toPlainText())

    def test_fixed_summary_is_available_without_devices_and_refresh_keeps_reading(self):
        battle=BattlePreviewPanel();self.addCleanup(battle.close);battle.resize(1000,750);battle.show()
        battle.set_stage('ro6_t_12');self.assertTrue(battle.reward_summary.isEnabled());battle.reward_summary.click();self.qt.processEvents()
        cursor=battle.spawn_detail.textCursor();cursor.setPosition(2);cursor.setPosition(12,QTextCursor.MoveMode.KeepAnchor)
        battle.spawn_detail.setTextCursor(cursor);battle.spawn_detail.verticalScrollBar().setValue(30)
        before=(battle.spawn_detail.toPlainText(),battle.spawn_detail.textCursor().selectedText(),battle.spawn_detail.verticalScrollBar().value())
        battle.render_rows();self.qt.processEvents()
        self.assertEqual((battle.spawn_detail.toPlainText(),battle.spawn_detail.textCursor().selectedText(),battle.spawn_detail.verticalScrollBar().value()),before)
        self.assertIsNone(battle.grid.reference_cell);self.assertIsNone(battle.original.reference_cell)
        battle.set_stage(None);self.assertFalse(battle.reward_summary.isEnabled())

if __name__=='__main__':unittest.main()
