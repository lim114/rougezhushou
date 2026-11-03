import copy
import hashlib
import json
from pathlib import Path
import unittest
from unittest.mock import patch
from rouge.battle_preview import battle_data, route_reference, enemy_preview, enemy_text
from rouge.rare_reward_sources import rare_reward_data, rare_stage_reward_sources, documented_reward_rule, enemy_reward_reference
from rouge.battle_reward_planning import stage_reward_sources, reward_source_text, reward_data
from scripts.build_rare_reward_sources import build, extract_level, BASE

IDS = ('enemy_2001_duckmi','enemy_2002_bearmi','enemy_2034_sythef','enemy_2085_skzjxd')


def ref(entity, level, use_db=True):
    return {'source_selector': '$.enemyDbRefs[0]',
        'raw': {'id': entity, 'level': level, 'useDb': use_db, 'overwrittenData': None}}


class RareRewardSourcesTests(unittest.TestCase):
    def test_source_bound_rebuild_has_all_five_original_ids_but_only_four_fixed_spawn_types(self):
        data = rare_reward_data()
        self.assertEqual(build(), data)
        self.assertEqual(len(data['stages']), 105)
        self.assertEqual(len(data['levels']), 68)
        self.assertEqual(set(data['mimic_ids']), set(IDS) | {'enemy_2125_dylnpp'})
        self.assertEqual(set(data['fixed_spawn_entity_ids']), set(IDS))
        self.assertEqual(data['unreferenced_mimic_ids'], ['enemy_2125_dylnpp'])
        self.assertEqual(sum(len(row['actions']) for row in data['levels'].values()), 149)
        self.assertEqual(sum(len(row['random_groups']) for row in data['levels'].values()), 44)

    def test_all_fixed_sources_preserve_unknown_actual_total_and_stage_level_binding(self):
        data = rare_reward_data()
        total = 0
        nonempty = 0
        grades = set()
        for sid, stage in battle_data()['stages'].items():
            result = rare_stage_reward_sources(sid)
            self.assertEqual(result['source']['sha256'], stage['level_source']['sha256'])
            self.assertIsNone(result['actual_reward_total'])
            self.assertIsNone(result['probability'])
            self.assertFalse(result['database_reference_is_spawn_proof'])
            self.assertFalse(result['complete_settlement_pool_known'])
            nonempty += bool(result['rows'])
            for row in result['rows']:
                total += 1
                self.assertEqual(row['kind'], 'rare_enemy_action')
                self.assertEqual(row['raw']['actionType'], 'SPAWN')
                self.assertEqual(row['raw']['key'], row['entity_id'])
                self.assertIsNone(row['actual_activation'])
                self.assertIsNone(row['actual_reward'])
                self.assertIsNone(row['actual_defeated_count'])
                self.assertIsNone(row['actual_spawn_level'])
                self.assertFalse(row['quantity_is_total'])
                self.assertFalse(row['rule']['current_rogue6_server_script_verified'])
                self.assertFalse(row['rule']['complete_relic_pool_known'])
                grades.update(row['rule']['referenced_levels'])
                self.assertEqual(row['rule']['outcomes'][0]['resource'], 'random_relic')
                self.assertEqual(row['rule']['outcomes'][0]['quantity'], 1)
                self.assertIsNone(row['rule']['outcomes'][0]['actual_quantity'])
        self.assertEqual((total, nonempty, grades), (279, 70, {0,1,2}))

    def test_four_same_group_enemies_and_empty_member_are_not_added_as_four_actual_rewards(self):
        result = rare_stage_reward_sources('ro6_n_1_1')
        self.assertEqual(len(result['rows']), 4)
        self.assertEqual(len(result['random_groups']), 1)
        group = result['random_groups'][0]
        self.assertEqual(len(group['members']), 5)
        self.assertEqual({m['raw']['key'] for m in group['members'] if not m['is_empty_key']}, set(IDS))
        self.assertTrue(any(m['raw']['actionType'] == 'EMPTY' and m['is_empty_key'] for m in group['members']))
        self.assertIsNone(group['actual_choice'])
        self.assertIsNone(group['probabilities'])
        self.assertIsNone(result['actual_reward_total'])
        self.assertTrue(all(r['candidate_group_reference'] == group for r in result['rows']))

    def test_base_database_grade_documentation_does_not_cover_missing_default_or_unsupported_grade(self):
        for entity in IDS:
            for grade in (0,1,2):
                row = documented_reward_rule(entity, [ref(entity, grade)])
                self.assertEqual(row['outcomes'][0]['quantity'], 1)
                self.assertTrue(row['all_fixed_level_candidates_documented'])
            mixed = documented_reward_rule(entity, [ref(entity,0), ref(entity,1)])
            self.assertEqual(mixed['outcomes'][0]['quantity'], 1)
            self.assertFalse(mixed['action_level_binding_unique'])
            for refs in ([], [ref(entity,3)], [ref(entity,True)], [ref(entity,-1)],
                    [ref(entity,0),ref(entity,3)], [ref(entity,0,False)], [ref('another-ID',0)]):
                result = documented_reward_rule(entity, refs)
                self.assertIsNone(result['outcomes'][0]['quantity'])
                self.assertFalse(result['all_fixed_level_candidates_documented'])
                self.assertIsNone(result['actual_reward'])
        missing = documented_reward_rule('enemy_2125_dylnpp', [ref('enemy_2125_dylnpp',0)])
        self.assertIsNone(missing['outcomes'][0]['quantity'])

    def test_main_positions_use_exact_base_route_and_no_branch_scope_is_borrowed(self):
        stage = battle_data()['stages']['ro6_n_1_1']
        result = rare_stage_reward_sources(stage['id'])
        for row in result['rows']:
            self.assertEqual(row['display_cell'], route_reference(stage,row['raw']['routeIndex'])['start'])
            self.assertEqual(row['position_source_selector'], f"$.routes[{row['raw']['routeIndex']}].startPosition")
        fake = copy.deepcopy(rare_reward_data())
        key = fake['stages'][stage['id']]['level_key']
        fake['levels'][key]['actions'][0]['branch'] = True
        fake['levels'][key]['actions'][0]['raw']['routeIndex'] = 0
        with patch('rouge.rare_reward_sources.rare_reward_data', return_value=fake):
            row = rare_stage_reward_sources(stage['id'])['rows'][0]
            self.assertIsNone(row['display_cell'])
            self.assertIsNone(row['nominal_route_reference'])
            self.assertIsNone(row['position_source_selector'])

    def test_changed_stage_name_difficulty_level_hash_and_unknown_id_are_rejected(self):
        for key in ('name','difficulty','level_source'):
            data = copy.deepcopy(battle_data())
            row = data['stages']['ro6_n_1_1']
            if key == 'level_source':
                row[key]['sha256'] = 'changed'
            else:
                row[key] = 'changed'
            with patch('rouge.rare_reward_sources.battle_data', return_value=data), self.assertRaises(ValueError):
                rare_stage_reward_sources('ro6_n_1_1')
        for value in (None,'',True,[],'unknown-same-name-stage'):
            with self.assertRaises(ValueError):
                rare_stage_reward_sources(value)

    def test_extractor_checks_only_spawn_type_and_keeps_all_group_members_per_queue(self):
        identities = {k:{'name':k} for k in IDS}
        actions = [
            {'actionType':'SPAWN','key':IDS[0],'randomSpawnGroupKey':'g','count':1},
            {'actionType':'EMPTY','key':'','randomSpawnGroupKey':'g','count':0},
            {'actionType':'SPAWN','key':'other','randomSpawnGroupKey':'g','count':2},
            {'actionType':'DISPLAY_ENEMY_INFO','key':IDS[0],'count':1}]
        raw = {'source':{'sha256':'public'}, 'queues_with_rare_spawns':[
            {'source_selector':'$.waves[0].fragments[0]','raw_actions':actions},
            {'source_selector':'$.branches["b"].phases[0]','raw_actions':actions}],
            'enemy_db_refs':[ref(IDS[0],0)], 'initial_enemy_records':[]}
        result = extract_level(raw, identities)
        self.assertEqual(len(result['actions']), 2)
        self.assertEqual(len(result['random_groups']), 2)
        self.assertEqual([r['branch'] for r in result['actions']], [False,True])
        self.assertTrue(all(len(g['members']) == 3 for g in result['random_groups']))
        self.assertFalse(result['initial_enemy_records'])
        self.assertFalse(result['database_reference_is_spawn_proof'])

    def test_copies_and_legacy_reward_mechanisms_are_preserved(self):
        before = copy.deepcopy(rare_reward_data())
        result = rare_stage_reward_sources('ro6_n_1_1')
        result['rows'][0]['rule']['outcomes'][0]['quantity'] = 999
        result['rows'][0]['candidate_group_reference']['members'].clear()
        self.assertEqual(rare_reward_data(), before)
        combined = stage_reward_sources('ro6_n_1_1')
        old = {r['entity_id']:r for r in combined['rows'] if r['kind'] != 'rare_enemy_action'}
        self.assertEqual(set(old), set(reward_data()['rules']))
        self.assertEqual(old['trap_321_shnbox']['rule']['outcomes'][0]['quantity'],2)
        self.assertEqual(old['trap_322_shrbox']['rule']['outcomes'][0]['quantity'],5)
        self.assertEqual(old['trap_323_shsbox']['rule']['outcomes'][0]['quantity'],10)
        self.assertEqual(old['trap_320_shtlbx']['rule']['outcomes'][0]['cost_quantity'],50)
        self.assertEqual(len(combined['random_groups']),2)
        self.assertEqual(len(combined['rare_random_groups']),1)
        self.assertIsNone(combined['actual_reward_total'])

    def test_source_text_has_grade_quantity_pool_boundary_and_full_empty_alternatives(self):
        result = stage_reward_sources('ro6_n_1_1')
        row = next(r for r in result['rows'] if r['kind'] == 'rare_enemy_action')
        text = reward_source_text(result,row,technical=True)
        for expected in ('+1收藏品','空候选','不能相加','固定敌人级别候选','实际生成级别','服务器','原路线名义起点',row['source_selector'],row['rule']['quantity_source']['url']):
            self.assertIn(expected, text)
        self.assertNotIn('+4收藏品', text)
        self.assertIn('完整结算池：未知', text)
        self.assertIn('基础战斗结算分项', text)

    def test_enemy_mechanism_panel_gets_same_conditional_reward_without_polluting_ordinary_enemies(self):
        stage = battle_data()['stages']['ro6_n_1_1']
        for entity in IDS:
            entry = next(e for e in stage['enemies'] if e['id'] == entity)
            result = enemy_reward_reference(stage['id'],entity,entry['level'])
            self.assertEqual(result['rule']['outcomes'][0]['quantity'],1)
            self.assertEqual(result['fixed_spawn_reference_count'],1)
            self.assertIsNone(result['actual_quantity'])
            preview = enemy_preview(stage['id'],entity,entry['level'])
            self.assertEqual(preview['conditional_reward_reference'],result)
            text = enemy_text(preview)
            self.assertIn('【宝藏条件参考】',text)
            self.assertIn('1件收藏品',text)
            self.assertIn('已领取数量：未知',text)
        ordinary = next(e for e in stage['enemies'] if e['id'] not in rare_reward_data()['mimic_ids'])
        preview = enemy_preview(stage['id'],ordinary['id'],ordinary['level'])
        self.assertIsNone(preview.get('conditional_reward_reference'))
        self.assertNotIn('宝藏条件参考',enemy_text(preview))
        with self.assertRaises(ValueError):
            enemy_reward_reference(stage['id'],IDS[0],99)


class RareRewardViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from PySide6.QtWidgets import QApplication
        cls.app = QApplication.instance() or QApplication([])

    def test_fixed_battle_selector_places_rare_reference_and_preserves_reading(self):
        from PySide6.QtGui import QTextCursor
        from rouge.battle_view import BattlePreviewPanel
        panel = BattlePreviewPanel()
        self.addCleanup(panel.close)
        panel.resize(1200,850)
        panel.show()
        panel.set_stage('ro6_n_1_1')
        self.app.processEvents()
        indexes = [i for i in range(1,panel.reward_combo.count()) if panel.reward_combo.itemData(i)['kind'] == 'rare_enemy_action']
        self.assertEqual(len(indexes),4)
        for index in indexes:
            panel.reward_combo.setCurrentIndex(index)
            self.app.processEvents()
            row = panel.reward_combo.currentData()
            self.assertEqual(panel.grid.reference_cell,row['display_cell'])
            self.assertEqual(panel.original.reference_cell,row['display_cell'])
            self.assertIsNotNone(panel.original.cell_center(row['display_cell']))
            self.assertIn('+1收藏品',panel.spawn_detail.toPlainText())
            self.assertEqual(panel._shown_enemy[1],row['entity_id'])
            self.assertIn('【宝藏条件参考】',panel.enemy_detail.toPlainText())
        cursor = panel.spawn_detail.textCursor()
        cursor.setPosition(5)
        cursor.setPosition(15,QTextCursor.MoveMode.KeepAnchor)
        panel.spawn_detail.setTextCursor(cursor)
        selected = cursor.selectedText()
        row_id = panel.reward_combo.currentData()['id']
        panel.render_rows()
        panel.set_context({'floor':1})
        self.app.processEvents()
        self.assertEqual(panel.reward_combo.currentData()['id'],row_id)
        self.assertEqual(panel.spawn_detail.textCursor().selectedText(),selected)
        panel.technical.setChecked(True)
        self.assertIn('原件位置：',panel.spawn_detail.toPlainText())
        panel.set_stage('ro6_n_2_1')
        self.assertEqual(panel.reward_combo.currentIndex(),0)
        self.assertIsNone(panel.grid.reference_cell)

    def test_node_catalog_includes_conditional_relic_reference_and_keeps_exact_stage_link(self):
        from rouge.node_catalog_view import NodeCatalogPanel
        panel = NodeCatalogPanel()
        self.addCleanup(panel.close)
        index = next(i for i,e in enumerate(panel.entries) if e['kind'] == 'battle' and e['record'].get('id') == 'ro6_n_1_1')
        panel.list.setCurrentRow(index)
        text = panel.detail.toPlainText()
        self.assertIn('鸭爵',text)
        self.assertIn('+1收藏品',text)
        self.assertIn('不能相加',text)
        calls = []
        panel.stageSelected.connect(calls.append)
        panel.battle_button.click()
        self.assertEqual(calls,['ro6_n_1_1'])


if __name__ == '__main__':
    unittest.main()
