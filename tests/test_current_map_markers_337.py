from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import json,shutil,unittest
from rouge import current_map_markers as symbols,current_map_position as positions,current_battle_reference as battle,current_action_positions as actions
from scripts import build_current_map_markers_337 as builder
ROOT=Path(__file__).resolve().parents[1]
def clone(root):
    manifest=json.loads((ROOT/symbols.MANIFEST).read_bytes())
    for n in(symbols.MANIFEST,*manifest['files']):
        p=root/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/n,p)

class CurrentMapMarkers337Tests(unittest.TestCase):
    def test_reproducible_two_complete_configurations_eight_observed_symbols_not_cell_centers(self):
        raw,m=builder.build();self.assertEqual(raw,(ROOT/symbols.DATA).read_bytes());self.assertEqual(m,(ROOT/symbols.MANIFEST).read_bytes());r=symbols.packet();self.assertEqual(list(r['data']['bindings']),list(symbols.STAGES));current=battle.packet()
        for sid in symbols.STAGES:
            row=symbols.mapping_for(sid,current)['mapping'];self.assertEqual(len(row['points']),8);self.assertEqual(sum(p['tile_key']=='tile_start'for p in row['points']),7)
            self.assertEqual(row['full_selected_geometry'],{k:current['inputs']['levels'][row['current_level_key']][k]for k in builder.GEOMETRY})
            for p in row['points']:
                self.assertEqual(p['kind'],'visible_map_symbol');self.assertFalse(p['tile_center_measured']);self.assertFalse(p['absolute_accuracy_verified']);self.assertIsNone(p['actual_spawn_position']);x0,y0,x1,y1=p['marker_bbox'];self.assertTrue(x0<=p['pixel'][0]<x1 and y0<=p['pixel'][1]<y1)
        self.assertFalse(r['data']['new_external_ground_truth_claimed']);self.assertTrue(r['data']['observation']['two_pixel_estimators_not_independent_external_ground_truth'])
    def test_all16_point_pairs_and_every_other_cell_unknown_old_ground_scope_preserved(self):
        old=positions.packet()['data'];self.assertEqual(len(old['compatible_stages']),33)
        for sid in symbols.STAGES:
            r=positions.stage_reference(sid);known={(p['row'],p['col'])for p in r['points']};self.assertEqual(len(known),8);self.assertFalse(r['full_map_projection_verified']);self.assertFalse(r['supports_inverse']);self.assertFalse(r['supports_segments']);self.assertFalse(r['run_updated'])
            for row in range(r['rows']):
                for col in range(r['cols']):
                    c=positions.cell_reference(r,row,col);self.assertEqual(c['mapped_to_original'],(row,col)in known);self.assertIsNone(c['actual_spawn_position'])
            self.assertIn('标志',positions.summary_text(r));self.assertIn('精确误差尚未测量',positions.cell_text(r,positions.cell_reference(r,7,6)))
        previous=positions.stage_reference('ro6_n_6_2');self.assertEqual(previous['points'],old['compatible_stages']['ro6_n_6_2']['points']);self.assertIsNone(positions.cell_reference(previous,True,0))
    def test_complete_geometry_camera_image_and_same_name_are_not_substitutes(self):
        current=battle.packet();self.assertIsNone(symbols.mapping_for('ro6_b_6',current));self.assertIsNone(symbols.mapping_for(True,current))
        for sid in symbols.STAGES:
            row=symbols.packet()['data']['bindings'][sid]
            for field in builder.GEOMETRY:
                changed=deepcopy(current);changed['inputs']['levels'][row['current_level_key']][field]={'unverified_new_value':True};self.assertIsNone(symbols.mapping_for(sid,changed),field)
            changed=deepcopy(current);changed['version']['images']['images'][sid]['sha256']='0'*64;self.assertIsNone(symbols.mapping_for(sid,changed));changed=deepcopy(current);changed['version']['current']['details']['stages'][sid]['description']='same-name changed source';self.assertIsNone(symbols.mapping_for(sid,changed))
    def test_each_member_damage_and_image_deletion_clear_new_scope_only(self):
        with TemporaryDirectory()as folder:
            root=Path(folder);clone(root);m=json.loads((ROOT/symbols.MANIFEST).read_bytes())
            with patch.object(symbols,'ROOT',root):
                for n in(symbols.MANIFEST,*m['files']):
                    p=root/n;raw=p.read_bytes();p.write_bytes(raw+b' ');self.assertIsNone(symbols.packet(),n);self.assertIsNone(positions.stage_reference('ro6_b_7'));self.assertIsNotNone(positions.stage_reference('ro6_n_6_2'));p.write_bytes(raw);self.assertIsNotNone(symbols.packet())
                image=root/symbols.packet()['data']['observation']['image_file'];raw=image.read_bytes();image.unlink();self.assertIsNone(positions.stage_reference('ro6_b_7_b'));image.write_bytes(raw);self.assertIsNotNone(positions.stage_reference('ro6_b_7_b'))
    def test_builder_rejects_bad_marker_topology_channel_and_boolean_cells(self):
        with TemporaryDirectory()as folder:
            root=Path(folder);clone(root);p=root/symbols.PACK/'observations.json';raw=p.read_bytes()
            for field,value in[('row',True),('col',99),('channel_rule','anything'),('marker_bbox',[-1,0,20,30])]:
                d=json.loads(raw);d['points'][0][field]=value;p.write_bytes(builder.encoded(d))
                with self.assertRaises(ValueError):builder.build(root)
            p.write_bytes(raw)
    def test_current_action_only_exact_nominal_cell_links_symbol_without_actual_foot_or_path(self):
        for sid in symbols.STAGES:
            r=actions.reference(sid,'0');e=next(e for e in r['entries']if e['label']=='终点参考格');self.assertEqual(e['cell'],{'row':7,'col':6});self.assertEqual(e['center']['kind'],'visible_map_symbol');self.assertIn('原图可见标志位置',actions.player_text(r,e));self.assertIn('精确误差尚未测量',actions.player_text(r,e));self.assertIsNone(r['actual_path']);self.assertIsNone(r['absolute_time']);self.assertIsNone(r['actual_occurrence']);self.assertFalse(r['run_updated'])
if __name__=='__main__':unittest.main()
