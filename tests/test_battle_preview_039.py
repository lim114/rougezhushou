import copy,hashlib,json,unittest
from pathlib import Path
from rouge.battle_preview import (battle_data,display_cell,route_reference,spawn_rows,
    hidden_group_reference,enemy_preview,enemy_text,spawn_text)
from rouge.catalog import catalog,stage_previews

ROOT=Path(__file__).resolve().parents[1]
SID='ro6_n_1_2'
EID='enemy_1093_ccsbr'

class BattlePreviewTests(unittest.TestCase):
    def test_known_entry_and_protect_point(self):
        stage=battle_data()['stages'][SID]
        row=next(r for r in spawn_rows(SID) if r['action']['key']==EID)
        route=row['route'];self.assertEqual(route['start'],{'row':1,'col':8})
        self.assertEqual(route['end'],{'row':3,'col':0})
        self.assertEqual(stage['tiles'][stage['map'][1][8]]['tileKey'],'tile_start')
        self.assertEqual(stage['tiles'][stage['map'][3][0]]['tileKey'],'tile_end')

    def test_row_direction(self):
        self.assertEqual(display_cell({'row':0,'col':2},7,9),{'row':6,'col':2})
        self.assertEqual(display_cell({'row':6,'col':8},7,9),{'row':0,'col':8})

    def test_outside_positions_are_not_clamped(self):
        for point in ({'row':-1,'col':0},{'row':7,'col':0},{'row':0,'col':9},
                      {'row':True,'col':1},{'row':.5,'col':1},None,{}):
            self.assertIsNone(display_cell(point,7,9))

    def test_waits_are_not_space_points(self):
        stage=copy.deepcopy(battle_data()['stages'][SID]);route=stage['routes'][0]
        route['motionMode']='WALK'
        route['checkpoints']=[{'type':'WAIT_FOR_SECONDS','position':{'row':0,'col':0},'time':99},
            {'type':'WAIT_CURRENT_FRAGMENT_TIME','position':{'row':6,'col':8},'time':13}]
        ref=route_reference(stage,0)
        self.assertTrue(all(c['cell'] is None for c in ref['checkpoints']))
        self.assertTrue(all(p['kind'] in ('start','end') for p in ref['points']))

    def test_reappearance_is_not_continuous_path(self):
        stage=copy.deepcopy(battle_data()['stages'][SID]);route=stage['routes'][0]
        route['motionMode']='WALK'
        route['checkpoints']=[{'type':'DISAPPEAR','time':1,'position':{'row':0,'col':0}},
            {'type':'APPEAR_AT_POS','time':2,'position':{'row':4,'col':2}}]
        ref=route_reference(stage,0)
        self.assertFalse(ref['continuous_reference']);self.assertFalse(ref['path_is_actual'])
        self.assertEqual(ref['checkpoints'][1]['cell'],{'row':2,'col':2})

    def test_bad_route_never_borrows_first(self):
        stage=battle_data()['stages'][SID]
        for index in (-1,99999,None,True,'0'):
            self.assertIsNone(route_reference(stage,index)['start'])

    def test_default_enum_placeholder_not_mapped(self):
        stage=copy.deepcopy(battle_data()['stages'][SID]);stage['routes'][0]['motionMode']='E_NUM'
        self.assertIsNone(route_reference(stage,0)['start'])

    def test_offsets_remain_nominal(self):
        stage=copy.deepcopy(battle_data()['stages'][SID]);stage['routes'][0]['motionMode']='WALK'
        stage['routes'][0]['spawnOffset']['x']=.25
        route=route_reference(stage,0)
        self.assertEqual(route['offset']['x'],.25);self.assertTrue(route['pending'])

    def test_branches_not_projected_on_base_routes(self):
        branches=[r for r in spawn_rows(SID) if r['branch']]
        self.assertEqual(len(branches),2)
        self.assertTrue(all(r['route']['start'] is None and not r['route_scope_verified'] for r in branches))

    def test_wave_filters_exclude_branches(self):
        for wave in (1,2,3):
            rows=spawn_rows(SID,wave=wave)
            # A wave can contain only non-SPAWN actions; don't manufacture rows.
            self.assertTrue(all(r['wave']==wave and r['branch'] is None for r in rows))

    def test_enemy_filter(self):
        rows=spawn_rows(SID,enemy_id=EID)
        self.assertTrue(rows);self.assertTrue(all(r['action']['key']==EID for r in rows))
        self.assertEqual(spawn_rows('no-stage'),[])
        self.assertEqual(spawn_rows(SID,enemy_id='no-enemy'),[])

    def test_absolute_times_and_probabilities_not_invented(self):
        for sid in battle_data()['stages']:
            for row in spawn_rows(sid):
                self.assertIsNone(row['absolute_time']);self.assertIsNone(row['probability'])
        text=spawn_text(spawn_rows(SID)[0],SID)
        self.assertIn('绝对出场时刻：未知',text)
        self.assertIn('不直接相加为全局时间',text)

    def test_hidden_group_differs_by_variant(self):
        stages=battle_data()['stages'];urgent=next(sid for sid,s in stages.items()
            if s['name']==stages[SID]['name'] and s['difficulty']=='FOUR_STAR')
        self.assertFalse(hidden_group_reference(stages[SID],'raid')['enabled_by_stage_rune'])
        self.assertTrue(hidden_group_reference(stages[urgent],'raid')['enabled_by_stage_rune'])
        self.assertEqual(hidden_group_reference(stages[SID],'raid')['status'],'activation_unknown')

    def test_raw_random_weights_are_preserved_not_normalized(self):
        row=next(r for r in spawn_rows(SID) if r['action'].get('randomSpawnGroupKey'))
        self.assertIn('原始权重',spawn_text(row,SID));self.assertIn('非概率',spawn_text(row,SID))
        self.assertIsNone(row['probability'])

    def test_enemy_base_matches_existing_calculation(self):
        for sid,stage in battle_data()['stages'].items():
            old={(e['id'],e['level']):e for e in stage_previews()[sid]['possible_enemies']}
            for e in stage['enemies']:
                self.assertEqual({k:e['reference_stats'][k] for k in old[e['id'],e['level']]['reference_stats']},
                    old[e['id'],e['level']]['reference_stats'])

    def test_context_correction_recomputes(self):
        low=enemy_preview(SID,EID,0,{'difficulty':{'value':0},'zone':{'id':'zone_3'}})
        high=enemy_preview(SID,EID,0,{'difficulty':{'value':15},'zone':{'id':'zone_3'}})
        unknown=enemy_preview(SID,EID,0,{})
        self.assertLess(low['environment']['stats']['maxHp'],high['environment']['stats']['maxHp'])
        self.assertEqual(unknown['environment']['stats']['maxHp'],2600)
        self.assertIn('本局保密等级尚未确认',enemy_text(unknown))

    def test_invalid_config_does_not_keep_previous_numbers(self):
        preview=enemy_preview(SID,EID,0,{'difficulty':{'value':16}})
        self.assertIsNone(preview['environment']);self.assertIn('环境无法确认',enemy_text(preview))

    def test_missing_immunity_is_not_false(self):
        e=enemy_preview(SID,EID,0)
        self.assertIsNone(e['immunity_reference']['stunImmune'])
        self.assertTrue(e['immunity_reference']['silenceImmune'])
        self.assertIn('眩晕：未知',enemy_text(e));self.assertIn('沉默：是',enemy_text(e))

    def test_handbook_and_stable_extensions(self):
        e=enemy_preview(SID,EID,0)
        self.assertEqual(e['reference_stats']['attackSpeed'],100)
        self.assertEqual(e['reference_stats']['moveSpeed'],.8)
        self.assertEqual(e['reference_stats']['baseAttackTime'],1.8)
        self.assertIn('被阻挡时防御提升',e['abilities'])
        self.assertIn('含藏品的目标预测结果请在伤害测试页查看',enemy_text(e))

    def test_identity_requires_exact_level(self):
        with self.assertRaises(ValueError):enemy_preview(SID,EID,999)
        with self.assertRaises(ValueError):enemy_preview(SID,'missing',0)

    def test_context_and_catalog_are_not_mutated(self):
        config={'difficulty':{'value':15},'zone':{'id':'zone_3'}};before=copy.deepcopy(config)
        e=enemy_preview(SID,EID,0,config);e['reference_stats']['atk']=-99
        self.assertEqual(before,config)
        self.assertEqual(enemy_preview(SID,EID,0,config)['reference_stats']['atk'],290)
        rows=spawn_rows(SID);rows[0]['action']['count']=-999
        self.assertNotEqual(spawn_rows(SID)[0]['action']['count'],-999)

    def test_all_images_match_pinned_receipt(self):
        receipt=json.loads((ROOT/'.cache/research/battle-039/image-receipt.json').read_text(encoding='utf-8'))
        self.assertEqual(set(receipt['images']),set(battle_data()['stages']))
        for sid,image in receipt['images'].items():
            path=ROOT/'rouge/data'/image['file']
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),image['sha256'])
            self.assertEqual(battle_data()['stages'][sid]['image'],image)

    def test_all_level_variants_and_cells_present(self):
        stages=battle_data()['stages'];self.assertEqual(len(stages),105)
        self.assertEqual(set(stages),set(stage_previews()))
        for sid,s in stages.items():
            self.assertEqual(s['difficulty'],catalog()['stages'][sid]['difficulty'])
            self.assertEqual(s['map'],stage_previews()[sid]['terrain']['map'])
            for line in s['map']:
                self.assertEqual(len(line),len(s['map'][0]))
                self.assertTrue(all(0<=cell<len(s['tiles']) for cell in line))

    def test_every_main_spawn_and_branch_retained(self):
        rows=[r for sid in battle_data()['stages'] for r in spawn_rows(sid)]
        self.assertEqual(sum(r['wave'] is not None for r in rows),3639)
        self.assertEqual(sum(bool(r['branch']) for r in rows),299)
        self.assertTrue(all(r['route']['start'] is not None for r in rows if r['wave']))

if __name__=='__main__':unittest.main()
