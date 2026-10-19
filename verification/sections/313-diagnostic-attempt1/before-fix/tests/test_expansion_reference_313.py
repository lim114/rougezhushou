"""Complete version selections, explicit next-scene links and exact map bytes."""
from pathlib import Path
from hashlib import sha256
from tempfile import TemporaryDirectory
from unittest.mock import patch
from copy import deepcopy
import json,shutil,unittest
from rouge import expansion_reference as model
from scripts.build_expansion_reference_313 import build
ROOT=Path(__file__).resolve().parents[1]

class ExpansionReference313Tests(unittest.TestCase):
    def test_whole_original_topic_selections_or_explicit_missing_source(self):
        paths={'baseline':ROOT/'.cache/game-data/roguelike_topic_table.json','current':ROOT/'.cache/p3-313-dlc2-research/roguelike-topic.json'}
        if any(not p.is_file()for p in paths.values()):self.skipTest('完整固定原表不可用，原件选片核对未执行，不可计通过。')
        ref=model.packet();self.assertIsNotNone(ref)
        for record in ref['source']['records']:
            role=record['role']
            if role not in paths:continue
            raw=paths[role].read_bytes();self.assertEqual(sha256(raw).hexdigest(),record['sha256']);self.assertEqual(len(raw),record['bytes'])
            full=json.loads(raw)
            self.assertEqual({k:full[k]['rogue_6']for k in('topics','details','modules','customizeData')},ref[role])

    def test_every_category_complete_identity_not_collapsed_and_delta_exact(self):
        ref=model.packet();expected={'stages':184,'scenes':355,'choices':418,'relics':395,'scrap':44,'squads':27,'difficulty':18,'regions':27,'endings':4,'initial':21}
        for cat,count in expected.items():
            rows=model.rows(cat,changes_only=False,reference=ref)
            self.assertEqual(len(rows),count,cat);self.assertEqual(len({r['id']for r in rows}),count)
            self.assertEqual(len({r['label']for r in rows}),count,cat)
            delta=model.rows(cat,reference=ref)
            self.assertEqual(delta,[r for r in rows if r['change']!='unchanged'])
        self.assertEqual(len(model.rows('stages',reference=ref)),80)
        self.assertEqual(sum(r['change']=='added'for r in model.rows('stages',reference=ref)),79)
        self.assertEqual([r['id']for r in model.rows('stages',reference=ref)if r['change']=='changed'],['ro6_e_3_3'])
        self.assertEqual(len(model.rows('scenes',reference=ref)),17);self.assertEqual(len(model.rows('choices',reference=ref)),22)

    def test_distinct_initial_month_records_and_normal16_are_retained(self):
        rows=model.rows('initial',changes_only=False)
        months=[r for r in rows if r['value']['modeId']=='MONTH_TEAM']
        self.assertEqual(len(months),4);self.assertEqual({r['value']['predefinedId']for r in months},{'month_team_'+str(i)for i in range(1,5)})
        rule=model.detail('difficulty','NORMAL|16');self.assertIn('险路尽头不再获得加工品',rule['player_text'])
        self.assertIn('尚未',rule['player_text']);self.assertFalse(rule['mutations_applied'])

    def test_all80_exact_map_refs_and_reproducible_manifest(self):
        ref=model.packet();images=ref['images']['images']
        self.assertEqual(set(images),{r['id']for r in model.rows('stages',changes_only=False,reference=ref)})
        changed={r['id']for r in model.rows('stages',reference=ref)}
        self.assertEqual(len({images[sid]['git_blob_sha1']for sid in changed}),41)
        self.assertTrue(all(model.image_bytes(info)is not None for info in images.values()))
        self.assertEqual(build(ROOT),(ROOT/model.MANIFEST).read_bytes())
        self.assertTrue(all(v['level_geometry_or_position_calibration_verified']is False for v in images.values()))

    def test_same_name_stages_are_distinct_without_borrowed_previews(self):
        a=model.detail('stages','ro6_n_4_1');b=model.detail('stages','ro6_n_4_1_dlc1')
        self.assertEqual(a['row']['name'],b['row']['name']);self.assertNotEqual(a['row']['id'],b['row']['id'])
        self.assertIn('不能借用',b['player_text']);self.assertIn('尚未校准',b['player_text'])
        self.assertEqual(b['row']['value']['levelId'],'Obt/Roguelike/RO6/DLC1/level_rogue6_4-1_dlc1')

    def test_explicit_choice_destination_and_named_reward_are_not_invented_parent_or_grant(self):
        r=model.detail('choices','choice_ro6_final1_8')
        self.assertEqual(r['next_scene'],{'id':'scene_ro6_final1_4','title':'险路尽头'})
        self.assertEqual(r['item_hint']['name'],'谒日之祈')
        self.assertIn('消耗10源石锭',r['player_text']);self.assertIn('来自哪个前置场景',r['player_text'])
        self.assertIsNone(r['actual_reward']);self.assertIsNone(r['actual_eligibility'])
        text=model.detail('scenes','scene_ro6_final1_4')['player_text']
        self.assertIn('帮助倒下的探险家同伴',text);self.assertIn('不是本场景内的选项',text)
        battle=model.detail('choices','choice_ro6_end4_3');self.assertIsNone(battle['next_scene']);self.assertIn('尚未取得明确关卡绑定',battle['player_text'])

    def test_scene_and_choice_ids_cannot_be_matched_by_name_or_prefix(self):
        for category,key in [('choices','scene_ro6_end4_1'),('scenes','choice_ro6_end4_1'),('choices','choice_ro6_end4_1x'),('stages','ro6_b_7_b_missing')]:
            self.assertIsNone(model.detail(category,key))
        self.assertEqual(model.detail('choices','choice_ro6_end4_1')['next_scene']['id'],'scene_ro6_end4_1')

    def test_game_angle_names_survive_format_removal_and_technical_is_complete(self):
        value='<@ro6.get>1件</><color=#123456>自然物</color>与<城防路障>、<旅行绒>\\n下一行'
        self.assertEqual(model._plain(value),'1件自然物与<城防路障>、<旅行绒>\n下一行')
        raw=model.detail('relics','rogue_6_relic_final_7')
        self.assertTrue(raw['row']['value']['effect']['buffs'])
        self.assertIn('熄日余径',raw['player_text']);self.assertFalse(raw['mutations_applied'])

    def test_warm_source_damage_clears_packet_and_restores_from_actual_exact_bytes(self):
        manifest=json.loads((ROOT/model.MANIFEST).read_bytes())
        with TemporaryDirectory()as folder:
            root=Path(folder)
            for name in(model.MANIFEST,*manifest['files']):
                p=root/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,p)
            with patch.object(model,'ROOT',root):
                self.assertIsNotNone(model.packet())
                for name in(model.MANIFEST,*manifest['files']):
                    p=root/name;raw=p.read_bytes()
                    try:p.write_bytes(raw+b' ');self.assertIsNone(model.packet(),name);self.assertIsNone(model.detail('choices','choice_ro6_final1_8'))
                    finally:p.write_bytes(raw)
                    self.assertIsNotNone(model.packet())

    def test_image_guard_refuses_private_outside_and_wrong_content(self):
        with patch.object(model,'_file',side_effect=AssertionError('Must not open unsafe input')):
            self.assertIsNone(model.image_bytes({'file':'.local/run-state.json'}));self.assertIsNone(model.image_bytes({'file':'local-settings.json'}))
        info=deepcopy(next(iter(model.packet()['images']['images'].values())));info['sha256']='0'*64
        self.assertIsNone(model.image_bytes(info))
        for name in('../private','C:/private','a\\b','a/../b'):
            with self.assertRaises(ValueError):model._file(name)

    def test_official_label_and_legacy_limits_are_explicit_not_DLC2_or_current_calibration(self):
        ref=model.packet();self.assertFalse(ref['source']['DLC2_as_official_name_verified']);self.assertFalse(ref['baseline_calculation_migrated']);self.assertFalse(ref['position_mapping_verified'])
        self.assertIn('内容拓展·一',model.NOTICE);self.assertIn('尚未整体迁移',model.NOTICE)
        copy=model.packet();copy['current']['details']['stages'].clear();self.assertEqual(len(model.packet()['current']['details']['stages']),184)

if __name__=='__main__':unittest.main()
