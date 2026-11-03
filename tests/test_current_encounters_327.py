from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from copy import deepcopy
import json,shutil,unittest
from rouge import current_encounters as model
from scripts import build_current_encounters_327 as builder
ROOT=Path(__file__).resolve().parents[1]
def clone(root):
    m=json.loads((ROOT/model.MANIFEST).read_bytes())
    for name in(model.MANIFEST,*m['files']):
        p=root/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,p)
def by_original(result,key):return next(c for c in result['choices'].values()if key in c['variant_ids'])
class CurrentEncounters327Tests(unittest.TestCase):
    def test_seven_complete_tables_reproducible_all_choices_and_full_current_records(self):
        d,m=builder.build();self.assertEqual(d,(ROOT/model.DATA).read_bytes());self.assertEqual(m,(ROOT/model.MANIFEST).read_bytes());r=model.packet();data=r['data'];self.assertEqual(data['counts'],{'events':7,'scenes':23,'document_choices':25,'original_choice_variants':28,'named_battle_choices':9,'required_item_choices':1,'items':2})
        current=model.version.packet()['current']['details'];old=model.version.packet()['baseline']['details']
        for g,rows in data['originals'].items():
            table='choiceScenes'if g=='scenes'else g
            for k,v in rows.items():self.assertEqual(v,current[table][k]);self.assertIs(data['complete_selected_record_comparison_to_baseline'][g][k],old[table].get(k)==v)
        self.assertTrue(data['complete_document_tables']);self.assertFalse(data['complete_game_option_pool']);self.assertFalse(data['game_parent_script_restored'])
    def test_root_labels_four_not_guessed_ids_and_no_battle_on_setup_choice(self):
        r=model.reference('鸭托邦');entry=r['event']['entry_scene_id'];ids=[r['choices'][k]['variant_ids']for k in r['scenes'][entry]['choice_ids']];self.assertEqual(ids,[['choice_ro6_bat3_1'],['choice_ro6_bat3_2'],['choice_ro6_bat3_4']])
        setup=by_original(r,'choice_ro6_bat3_2');confirm=by_original(r,'choice_ro6_bat3_5');self.assertFalse(setup['has_documented_battle_link']);self.assertIsNone(model.battle_target(r,setup['scene_id'],setup['id']));self.assertNotEqual(setup['scene_id'],confirm['scene_id']);self.assertEqual(setup['next_scene_id'],confirm['scene_id']);self.assertEqual(model.battle_target(r,confirm['scene_id'],confirm['id'])['choice_id'],'choice_ro6_bat3_5')
    def test_all_23_scene_links_and_28_original_choices_map_to_document_groups(self):
        d=model.packet()['data']
        for sid,s in d['scenes'].items():self.assertEqual(model.locate('scenes',sid),{'event_id':s['event_id'],'scene_id':sid,'choice_id':None})
        for cid in d['originals']['choices']:
            target=model.locate('choices',cid);c=d['choices'][target['choice_id']];self.assertIn(cid,c['variant_ids']);self.assertEqual(target['scene_id'],c['scene_id']);self.assertIsNone(c['actual_variant_id'])
        self.assertIsNone(model.locate('choices','choice_ro6_bat1_999'));self.assertIsNone(model.locate('scenes','scene_ro6_end4_enter'))
    def test_four_escape_variants_preserved_in_one_group_common_next_without_choice(self):
        r=model.reference('黑诞');c=by_original(r,'choice_ro6_normal2_3');self.assertEqual(c['variant_ids'],['choice_ro6_normal2_'+str(n)for n in(3,4,5,6)]);self.assertEqual(c['next_scene_id'],'scene_ro6_normal2_2');self.assertEqual(len(r['choices']),3);self.assertIsNone(c['actual_variant_id']);self.assertEqual({r['data']['originals']['choices'][v]['type']for v in c['variant_ids']},{'NEXT','TRADE'});text=model.player_text(r,c['scene_id'],c['id']);self.assertIn('不当作4次选择或4次扣除',text);self.assertIn('至少保留1点',text);self.assertNotIn('choice_ro6_',text)
    def test_controller_three_states_only_gate_named_reward_not_battle_or_escape(self):
        for declared in(None,False,True):
            r=model.reference('黑诞',declared);c=by_original(r,'choice_ro6_normal2_1');item=r['data']['originals']['items'][c['required_item_id']];self.assertEqual((item['name'],item['type']),('笼控器','SCRAP'));self.assertIs(model.choice_reference(r,c['scene_id'],c['id'])['listed_condition_match'],declared);text=model.player_text(r,c['scene_id'],c['id']);self.assertIn('不自动扣除笼控器',text);self.assertIn('猎印',text)
            for key in('choice_ro6_normal2_2','choice_ro6_normal2_3'):
                c=by_original(r,key);self.assertIsNone(model.choice_reference(r,c['scene_id'],c['id'])['listed_condition_match'])
        with self.assertRaises(ValueError):model.reference('鸭托邦',True)
        with self.assertRaises(ValueError):model.reference('黑诞',1)
    def test_half_gold_no_integer_guess_and_all_nine_battle_references_optional(self):
        r=model.reference('传奇团伙');c=by_original(r,'choice_ro6_bat4_4');self.assertIn('奇数时怎样取整',model.player_text(r,c['scene_id'],c['id']));self.assertFalse(r['data']['half_gold_integer_rule_verified']);count=0
        for event in r['data']['events']:
            fresh=model.reference(event)
            for row in fresh['choices'].values():
                if row['has_documented_battle_link']:
                    count+=1;target=model.battle_target(fresh,row['scene_id'],row['id']);self.assertIsNotNone(target);self.assertIn(target['choice_id'],row['variant_ids'])
        self.assertEqual(count,9)
        with patch('rouge.current_event_battles.locate',return_value=None):self.assertIsNotNone(model.reference('传奇团伙'));c=by_original(r,'choice_ro6_bat4_3');self.assertIsNone(model.battle_target(r,c['scene_id'],c['id']))
    def test_each_file_damage_and_complete_primary_drift_fail_closed(self):
        with TemporaryDirectory()as folder:
            root=Path(folder);clone(root);m=json.loads((root/model.MANIFEST).read_bytes())
            with patch.object(model,'ROOT',root):
                for name in(model.MANIFEST,*m['files']):
                    f=root/name;raw=f.read_bytes();f.write_bytes(raw+b' ');self.assertIsNone(model.packet(),name);f.write_bytes(raw);self.assertIsNotNone(model.packet())
        p=deepcopy(model.version.packet());p['current']['details']['choices']['choice_ro6_normal2_6']['type']='unverified'
        with patch.object(model.version,'packet',return_value=p):self.assertIsNone(model.packet())
    def test_builder_does_not_merge_variant_with_different_destination(self):
        with TemporaryDirectory()as folder:
            root=Path(folder);clone(root);f=root/builder.CURRENT;d=json.loads(f.read_bytes());d['details']['choices']['choice_ro6_normal2_6']['nextSceneId']='scene_ro6_normal2_1';f.write_bytes(builder.encoded(d))
            with self.assertRaises(ValueError):builder.build(root)

if __name__=='__main__':unittest.main()
