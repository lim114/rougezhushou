from pathlib import Path
from hashlib import sha256
from urllib.parse import urlsplit
from tempfile import TemporaryDirectory
from unittest.mock import patch
import json,shutil,unittest
from rouge import current_map_position as model
from scripts.build_current_map_position_319 import build,GEOMETRY_KEYS
ROOT=Path(__file__).resolve().parents[1]

class CurrentMapPosition319Tests(unittest.TestCase):
    def clone(self,root):
        manifest=json.loads((ROOT/model.MANIFEST).read_bytes())
        for name in(model.MANIFEST,*manifest['files']):
            p=root/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,p)
    def test_rebuild_and_complete_current_grid_scope(self):
        raw,manifest=build();self.assertEqual(raw,(ROOT/model.DATA).read_bytes());self.assertEqual(manifest,(ROOT/model.MANIFEST).read_bytes());ref=model.packet();self.assertEqual(len(ref['data']['compatible_stages']),33);self.assertEqual(len(ref['data']['unmapped_stage_ids']),151);self.assertEqual(len({x['image']['sha256']for x in ref['data']['compatible_stages'].values()}),13)
        with patch.object(model,'packet',return_value=ref):
            for sid in ref['data']['all_current_stage_ids']:
                r=model.stage_reference(sid);self.assertIsNotNone(r);self.assertEqual(len(r['map']),r['rows']);self.assertTrue(all(len(v)==r['cols']for v in r['map']));self.assertFalse(r['supports_inverse']);self.assertFalse(r['supports_segments']);self.assertFalse(r['run_updated'])
    def test_selected_old_geometries_equal_all13_whole_pinned_public_originals(self):
        source=json.loads((ROOT/model.PACK/'old-selected-complete-geometries.json').read_bytes());self.assertEqual(len(source),13)
        for digest,record in source.items():
            relative=urlsplit(record['source']['url']).path.split('/gamedata/',1)[1];p=ROOT/'.cache/game-data'/relative
            if not p.is_file():self.skipTest('固定完整旧原件不可用；独立全原件核对未计通过。')
            raw=p.read_bytes();self.assertEqual(sha256(raw).hexdigest(),digest);self.assertEqual(len(raw),record['source']['bytes']);whole=json.loads(raw);self.assertEqual(record['geometry'],{k:whole[k]for k in GEOMETRY_KEYS});self.assertEqual(set(record['geometry']['mapData']),set(whole['mapData']))
    def test_265_point_refs_are_observed_lowland_only_not_whole_map(self):
        ref=model.packet();total=0
        with patch.object(model,'packet',return_value=ref):
            for sid,binding in ref['data']['compatible_stages'].items():
                r=model.stage_reference(sid);self.assertEqual(r['image'],binding['image']);total+=len(r['points']);self.assertFalse(r['full_map_projection_verified'])
                for p in r['points']:
                    cell=model.cell_reference(r,p['row'],p['col']);self.assertTrue(cell['mapped_to_original']);self.assertEqual(cell['tile']['heightType'],'LOWLAND');self.assertIn(cell['tile']['tileKey'],('tile_floor','tile_road'));self.assertIsNone(cell['actual_spawn_position']);self.assertFalse(p['absolute_accuracy_verified']);self.assertEqual(p['agreement_limit_px'],4)
        self.assertEqual(total,265)
    def test_new_dlc_identity_can_map_only_by_full_geometry_and_exact_pixels(self):
        r=model.stage_reference('ro6_n_3_2_dlc1');self.assertTrue(r['points']);self.assertTrue(all(d['baseline_stage_id']!='ro6_n_3_2_dlc1'for d in r['mapping_evidence']['donors']));self.assertIn('mapData',r['complete_current_geometry'])
    def test_unmapped_highland_unknown_cells_do_not_borrow_nearby_or_same_name(self):
        r=model.stage_reference('ro6_n_6_2');known={(p['row'],p['col'])for p in r['points']}
        for row in range(r['rows']):
            for col in range(r['cols']):
                cell=model.cell_reference(r,row,col);self.assertEqual(cell['mapped_to_original'],(row,col)in known)
        r=model.stage_reference('ro6_n_1_2');self.assertEqual(r['points'],[]);self.assertIn('没有满足条件',model.summary_text(r));self.assertIsNone(model.cell_reference(r,True,0));self.assertIsNone(model.cell_reference(r,0.5,0));self.assertIsNone(model.cell_reference(r,-1,0));self.assertIsNone(model.cell_reference(r,r['rows'],0))
    def test_complete_map_properties_and_camera_changes_block_transfer(self):
        with TemporaryDirectory()as folder:
            root=Path(folder);self.clone(root);p=root/'research/p3-current-battle-314/source-inputs.json';base=p.read_bytes();data=json.loads(base);source=json.loads((ROOT/model.DATA).read_bytes());key=source['compatible_stages']['ro6_n_6_2']['current_level_key'];expected={sid for sid,row in source['compatible_stages'].items()if row['current_level_key']==key}
            for field in ('cameraPlugin','mapData.tags','mapData.effects','mapData.blockEdges','mapData.layerRects','mapData.tiles.blackboard'):
                fresh=json.loads(base)
                if field.startswith('mapData.tiles'):fresh['levels'][key]['mapData']['tiles'][0]['blackboard']=[{'key':'319_unverified','value':1}]
                elif field.startswith('mapData.'):fresh['levels'][key]['mapData'][field.split('.')[1]]={'319_unverified_change':True}
                else:fresh['levels'][key][field]={'319_unverified_change':True}
                p.write_text(json.dumps(fresh,ensure_ascii=False),encoding='utf8');built=json.loads(build(root)[0]);self.assertTrue(expected.isdisjoint(built['compatible_stages']),field)
            p.write_bytes(base)
    def test_image_identity_change_blocks_even_when_grid_and_id_same(self):
        with TemporaryDirectory()as folder:
            root=Path(folder);self.clone(root);p=root/'research/p3-expansion-313/map-images.json';data=json.loads(p.read_bytes());data['images']['ro6_n_6_2']['sha256']='0'*64;p.write_text(json.dumps(data),encoding='utf8');built=json.loads(build(root)[0]);self.assertNotIn('ro6_n_6_2',built['compatible_stages'])
    def test_actual_source_corruption_and_image_loss_clear_warm_reference(self):
        with TemporaryDirectory()as folder:
            root=Path(folder);self.clone(root);p=root/model.PACK/'old-selected-complete-geometries.json';raw=p.read_bytes()
            with patch.object(model,'ROOT',root):
                self.assertIsNotNone(model.packet());p.write_bytes(raw+b' ');self.assertIsNone(model.packet());p.write_bytes(raw);self.assertIsNotNone(model.packet())
        with patch.object(model.battle.version,'image_bytes',return_value=None):self.assertIsNone(model.stage_reference('ro6_n_6_2'))
    def test_player_words_never_claim_actual_spawn_or_inverse_boundary(self):
        r=model.stage_reference('ro6_n_6_2');self.assertIn('不能点击反推',model.summary_text(r));p=r['points'][0];text=model.cell_text(r,model.cell_reference(r,p['row'],p['col']));self.assertIn('近似中心',text);self.assertIn('没有读取战斗',text);self.assertNotIn('sha256',text)

if __name__=='__main__':unittest.main()
