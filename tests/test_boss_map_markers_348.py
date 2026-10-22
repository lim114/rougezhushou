from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from copy import deepcopy
import json,unittest
from rouge import boss_map_markers as model,current_map_position as positions,current_battle_reference as battle,current_map_markers as old_symbols,current_action_positions as actions
from scripts import build_boss_map_markers_348 as builder
ROOT=Path(__file__).resolve().parents[1]
def clone(root):
    for n in(model.MANIFEST,*json.loads((ROOT/model.MANIFEST).read_bytes())['files']):
        p=root/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((ROOT/n).read_bytes())
class BossMapMarkers348Tests(unittest.TestCase):
    def test_build_all16_exact_configurations_ten_images46_observations75_pairs(self):
        d,m=builder.build();self.assertEqual(d,(ROOT/model.DATA).read_bytes());self.assertEqual(m,(ROOT/model.MANIFEST).read_bytes());r=model.packet();self.assertEqual(tuple(r['data']['bindings']),model.STAGES);self.assertEqual(len(r['data']['observations']['groups']),10);self.assertEqual(sum(len(g['points'])for g in r['data']['observations']['groups']),46);self.assertEqual(sum(len(g['points'])for g in r['data']['bindings'].values()),75)
    def test_all75_pairs_and_every_other_cell_unknown_no_inverse_or_segments(self):
        for sid in model.STAGES:
            r=positions.stage_reference(sid);points={(p['row'],p['col'])for p in r['points']};self.assertFalse(r['full_map_projection_verified']);self.assertFalse(r['supports_inverse']);self.assertFalse(r['supports_segments']);self.assertFalse(r['run_updated']);self.assertFalse(r['actual_combat_positions_verified'])
            for row in range(r['rows']):
                for col in range(r['cols']):self.assertIs(positions.cell_reference(r,row,col)['mapped_to_original'],(row,col)in points)
            self.assertIn('可见标志',positions.summary_text(r));self.assertIn('每份配置各自核对',positions.summary_text(r))
    def test_exact_geometry_image_and_stage_identity_each_checked_not_shared_title(self):
        current=battle.packet();self.assertIsNone(model.mapping_for('ro6_b_7',current));self.assertIsNone(model.mapping_for(True,current))
        for sid in model.STAGES:
            row=model.packet()['data']['bindings'][sid]
            for field in builder.GEOMETRY:
                changed=deepcopy(current);changed['inputs']['levels'][row['current_level_key']][field]={'unverified':True};self.assertIsNone(model.mapping_for(sid,changed),sid+field)
            changed=deepcopy(current);changed['version']['images']['images'][sid]['sha256']='0'*64;self.assertIsNone(model.mapping_for(sid,changed));changed=deepcopy(current);changed['version']['current']['details']['stages'][sid]['description']='same title but changed';self.assertIsNone(model.mapping_for(sid,changed))
    def test_each_mark_is_visible_symbol_inside_box_not_measured_terrain_or_foot(self):
        for row in model.packet()['data']['bindings'].values():
            for point in row['points']:
                self.assertEqual(point['kind'],'visible_map_symbol');self.assertFalse(point['tile_center_measured']);self.assertFalse(point['absolute_accuracy_verified']);self.assertIsNone(point['actual_spawn_position']);x0,y0,x1,y1=point['marker_bbox'];self.assertTrue(x0<=point['pixel'][0]<x1 and y0<=point['pixel'][1]<y1);self.assertGreater(point['color_pixel_count'],0)
        p=next(p for p in model.packet()['data']['bindings']['ro6_b_4']['points']if p['row']==6);self.assertEqual(p['manual_symbol_estimate'],[69,173]);self.assertEqual(p['minimum_red_channel'],90);self.assertEqual(p['color_pixel_count'],64);self.assertAlmostEqual(p['color_centroid'][1],172.34375);self.assertFalse(model.packet()['data']['new_external_ground_truth_claimed'])
    def test_every_manifest_member_damage_fails_new_scope_only_and_recovers(self):
        with TemporaryDirectory()as f:
            root=Path(f);clone(root)
            with patch.object(model,'ROOT',root):
                for name in(model.MANIFEST,*json.loads((root/model.MANIFEST).read_bytes())['files']):
                    p=root/name;raw=p.read_bytes();p.write_bytes(raw+b' ');self.assertIsNone(model.packet(),name);self.assertIsNone(positions.stage_reference('ro6_b_1'));self.assertIsNotNone(positions.stage_reference('ro6_b_7'));self.assertIsNotNone(positions.stage_reference('ro6_n_6_2'));p.write_bytes(raw);self.assertIsNotNone(model.packet())
    def test_builder_rejects_moved_cells_wrong_channels_bounds_boolean_and_unsupported_contrast(self):
        with TemporaryDirectory()as f:
            root=Path(f);clone(root);p=root/model.PACK/'observations.json';raw=p.read_bytes()
            for field,value in [('row',True),('col',99),('tile_key','tile_floor'),('channel_rule','blue'),('marker_bbox',[-1,0,20,20]),('minimum_red_channel',True),('minimum_red_channel',0),('manual_symbol_estimate',[400,250])]:
                d=json.loads(raw);d['groups'][0]['points'][0][field]=value;p.write_bytes(builder.encoded(d))
                with self.assertRaises(ValueError):builder.build(root)
            d=json.loads(raw);d['groups'][0]['stage_ids'].append('ro6_b_7');p.write_bytes(builder.encoded(d))
            with self.assertRaises(ValueError):builder.build(root)
    def test_old33_geometry_bindings_two_entropy_symbols_and_remaining133_preserved(self):
        old=positions.packet()['data'];self.assertEqual(len(old['compatible_stages']),33);self.assertEqual(len(old_symbols.STAGES),2);self.assertEqual(len(set(old['all_current_stage_ids'])-set(old['compatible_stages'])-set(old_symbols.STAGES)-set(model.STAGES)),133)
        for sid in old_symbols.STAGES:self.assertEqual(len(positions.stage_reference(sid)['points']),8)
        self.assertEqual(positions.stage_reference('ro6_n_6_2')['points'],old['compatible_stages']['ro6_n_6_2']['points']);self.assertEqual(positions.stage_reference('ro6_n_1_2')['points'],[])
    def test_nominal_action_cells_gain_only_matching_symbols_no_actual_path_or_clock(self):
        first_without_marker=set();checked=0
        for sid in model.STAGES:
            current=battle.stage_reference(sid);grid=positions.stage_reference(sid);known={(p['row'],p['col']):p for p in grid['points']};main=[a for a in current['actions']if a['raw']['actionType']=='SPAWN'and a['queue']['kind']=='main']
            for index,action in enumerate(main):
                r=actions._reference(current,grid,action['key']);self.assertIsNone(r['actual_path']);self.assertIsNone(r['absolute_time']);self.assertIsNone(r['actual_occurrence']);self.assertFalse(r['run_updated'])
                for entry in r['entries']:
                    cell=entry['cell'];expected=known.get((cell['row'],cell['col']))if cell else None;self.assertEqual(entry['center'],expected);checked+=1
                    if entry['center']:self.assertEqual(entry['center']['kind'],'visible_map_symbol');self.assertIn('原图可见标志位置',actions.player_text(r,entry))
                    if index==0 and entry['label']=='终点参考格'and entry['center']is None:
                        first_without_marker.add(sid);self.assertEqual(action['key'],'0');self.assertEqual(entry['raw_position'],{'row':5,'col':6});self.assertEqual(entry['cell'],{'row':3,'col':6});self.assertIn('尚未核对，不猜位置',actions.player_text(r,entry))
        self.assertGreater(checked,75);self.assertEqual(first_without_marker,{'ro6_b_5','ro6_b_5_b'})
    def test_return_mutation_and_bad_cell_types_cannot_leak(self):
        r=positions.stage_reference('ro6_b_1');self.assertIsNone(positions.cell_reference(r,True,0));r['points'].clear();self.assertEqual(len(positions.stage_reference('ro6_b_1')['points']),6)
if __name__=='__main__':unittest.main()
