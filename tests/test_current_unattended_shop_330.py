from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from copy import deepcopy
import json,shutil,unittest
from rouge import current_unattended_shop as model
from scripts import build_current_unattended_shop_330 as builder
ROOT=Path(__file__).resolve().parents[1]
def clone(root):
    m=json.loads((ROOT/model.MANIFEST).read_bytes())
    for name in(model.MANIFEST,*m['files']):
        p=root/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,p)
def by_original(r,n):return next(c for c in r['choices'].values()if 'choice_ro6_wish_'+str(n)in c['variant_ids'])
class CurrentUnattendedShop330Tests(unittest.TestCase):
    def test_whole_table_reproducible_all11_choices4_original_scenes_and_baseline(self):
        d,m=builder.build();self.assertEqual(d,(ROOT/model.DATA).read_bytes());self.assertEqual(m,(ROOT/model.MANIFEST).read_bytes());r=model.reference();data=r['data'];self.assertEqual(data['counts'],{'events':1,'scenes':4,'document_choices':4,'original_choices':11,'held_relic_choices':1,'fixed_gold_choices':1,'same_text_followup_records':2,'items':1})
        current=model.version.packet()['current']['details'];old=model.version.packet()['baseline']['details']
        for g,rows in data['originals'].items():
            table='choiceScenes'if g=='scenes'else g
            for k,v in rows.items():self.assertEqual(v,current[table][k]);self.assertIs(data['complete_selected_record_comparison_to_baseline'][g][k],old[table].get(k)==v)
        self.assertFalse(data['complete_game_option_pool']);self.assertFalse(data['game_parent_script_restored']);self.assertFalse(data['upgrade_order_verified'])
    def test_same_caption_variants_all_retained_groups_not_three_times_rewards(self):
        r=model.reference()
        for n,variants in((1,[1,4,9]),(2,[2,5,10]),(3,[3,8]),(6,[6,7,11])):
            c=by_original(r,n);self.assertEqual(c['variant_ids'],['choice_ro6_wish_'+str(x)for x in variants]);self.assertIsNone(c['actual_variant_id']);self.assertIsNone(c['actual_parent_scene_id']);self.assertIsNone(c['actual_received']);self.assertIn('不能当成多次选择',model.player_text(r,c['scene_id'],c['id']))
        self.assertEqual([c['reward_quantity_reference']for c in r['choices'].values()],[1,1,None,1])
    def test_open_barrel_aliases_no_default_followup_no_repeated_option_or_guessed_tier(self):
        r=model.reference();c=by_original(r,3);self.assertIsNone(c['next_scene_id']);self.assertEqual(c['next_scene_ids'],['scene_ro6_wish_2','scene_ro6_wish_3']);self.assertEqual(r['data']['originals']['scenes']['scene_ro6_wish_2']['description'],r['data']['originals']['scenes']['scene_ro6_wish_3']['description'])
        for sid in c['next_scene_ids']:self.assertEqual(r['scenes'][sid]['choice_ids'],[]);self.assertTrue(model.followup_allowed(r,c['scene_id'],c['id'],sid));self.assertIn('顺序未确认',model.scene_label(r,sid));self.assertIn('不当可重复领取',model.player_text(r,sid))
        self.assertFalse(model.followup_allowed(r,c['scene_id'],c['id'],'scene_ro6_wish_1'));self.assertIsNone(r['actual_upgrade']);self.assertIsNone(r['actual_variant'])
    def test_gold_unknown_0_3_4_only_gates_opening_fossil_state_independent(self):
        for gold in(None,0,3,4):
            for held in(None,False,True):
                r=model.reference(gold=gold,has_fossil=held);cost=by_original(r,3);fossil=by_original(r,6);plain=by_original(r,1);self.assertIs(model.choice_reference(r,cost['scene_id'],cost['id'])['listed_condition_match'],None if gold is None else gold>=4);self.assertIs(model.choice_reference(r,fossil['scene_id'],fossil['id'])['listed_condition_match'],held);self.assertIsNone(model.choice_reference(r,plain['scene_id'],plain['id'])['listed_condition_match']);self.assertIsNone(r['actual_eligible']);self.assertFalse(r['run_updated'])
        with self.assertRaises(ValueError):model.reference(gold=True)
        with self.assertRaises(ValueError):model.reference(has_fossil=1)
        self.assertIsNone(model.reference(requested_original_id='invented'))
    def test_held_is_not_consumed_option_count_not_quantity_upgrade_not_current_reward(self):
        r=model.reference(has_fossil=True);c=by_original(r,6);item=r['data']['originals']['items'][c['required_relic_id']];self.assertEqual((item['type'],item['name']),('RELIC','四叶草化石'));text=model.player_text(r,c['scene_id'],c['id']);self.assertIn('未写交出或消耗',text);self.assertIn('增加可选项不等于增加领取件数',text);self.assertEqual(c['reward_quantity_reference'],1);c=by_original(r,3);self.assertIsNone(c['reward_quantity_reference']);self.assertEqual(c['gold_cost_reference'],4);self.assertIn('不是当场又获得1件',model.player_text(r,c['scene_id'],c['id']));self.assertIsNone(c['complete_reward_pool'])
    def test_all15_original_entries_exact_requested_record_not_real_variant(self):
        r=model.reference()
        for key in r['scenes']:
            t=model.locate('scenes',key);self.assertEqual(t['scene_id'],key);self.assertIsNone(t['original_choice_id'])
        for key in r['data']['originals']['choices']:
            t=model.locate('choices',key);self.assertEqual(t['original_choice_id'],key);self.assertIn(key,r['choices'][t['choice_id']]['variant_ids']);fresh=model.reference(requested_original_id=key);self.assertEqual(fresh['requested_original_id'],key);self.assertIsNone(fresh['actual_variant'])
        self.assertIsNone(model.locate('choices','choice_ro6_wish_12'));self.assertIsNone(model.locate('scenes','scene_ro6_bat5_enter'))
    def test_each_file_damage_and_complete_source_drift_fail_closed(self):
        with TemporaryDirectory()as folder:
            root=Path(folder);clone(root);m=json.loads((root/model.MANIFEST).read_bytes())
            with patch.object(model,'ROOT',root):
                for name in(model.MANIFEST,*m['files']):
                    f=root/name;raw=f.read_bytes();f.write_bytes(raw+b' ');self.assertIsNone(model.packet(),name);f.write_bytes(raw);self.assertIsNotNone(model.packet())
        r=deepcopy(model.version.packet());r['current']['details']['choices']['choice_ro6_wish_8']['nextSceneId']='scene_ro6_wish_2'
        with patch.object(model.version,'packet',return_value=r):self.assertIsNone(model.packet())
    def test_builder_rejects_lost_alias_or_missing_choice_not_silent_merging(self):
        for kind in('alias','choice'):
            with TemporaryDirectory()as folder:
                root=Path(folder);clone(root);f=root/builder.CURRENT;d=json.loads(f.read_bytes())
                if kind=='alias':d['details']['choices']['choice_ro6_wish_8']['nextSceneId']='scene_ro6_wish_2'
                else:del d['details']['choices']['choice_ro6_wish_11']
                f.write_bytes(builder.encoded(d))
                with self.assertRaises(ValueError):builder.build(root)
if __name__=='__main__':unittest.main()
