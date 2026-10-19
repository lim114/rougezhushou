from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from copy import deepcopy
import json,shutil,unittest
from rouge import current_resource_events as model
from scripts import build_current_resource_events_329 as builder
ROOT=Path(__file__).resolve().parents[1]
def clone(root):
    m=json.loads((ROOT/model.MANIFEST).read_bytes())
    for name in(model.MANIFEST,*m['files']):
        p=root/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,p)
def by_original(r,key):return next(c for c in r['choices'].values()if key in c['variant_ids'])
class CurrentResourceEvents329Tests(unittest.TestCase):
    def test_eight_complete_tables_reproducible32_scenes24_choices11_items(self):
        d,m=builder.build();self.assertEqual(d,(ROOT/model.DATA).read_bytes());self.assertEqual(m,(ROOT/model.MANIFEST).read_bytes());r=model.packet();data=r['data'];self.assertEqual(data['counts'],{'events':8,'scenes':32,'document_choices':24,'original_choice_variants':24,'named_battle_choices':0,'required_item_choices':0,'items':11})
        current=model.version.packet()['current']['details'];old=model.version.packet()['baseline']['details']
        for g,rows in data['originals'].items():
            table='choiceScenes'if g=='scenes'else g
            for k,v in rows.items():self.assertEqual(v,current[table][k]);self.assertIs(data['complete_selected_record_comparison_to_baseline'][g][k],old[table].get(k)==v)
        self.assertFalse(data['complete_game_option_pool']);self.assertFalse(data['game_parent_script_restored'])
    def test_all56_original_entries_exact_context_and_cross_event_generic_leave_not_merged(self):
        d=model.packet()['data']
        for sid,s in d['scenes'].items():self.assertEqual(model.locate('scenes',sid),{'event_id':s['event_id'],'scene_id':sid,'choice_id':None})
        for key in d['originals']['choices']:
            t=model.locate('choices',key);r=model.reference(t['event_id']);c=model.choice_reference(r,t['scene_id'],t['choice_id']);self.assertEqual(c['variant_ids'],[key]);self.assertEqual(r['data']['originals']['scenes'][c['next_scene_id']]['title'],t['event_id'])
        for title in('沉重的契约','擒与缚'):
            r=model.reference(title);c=next(c for c in r['choices'].values()if c['title']=='不关我的事');self.assertEqual(r['data']['originals']['scenes'][c['next_scene_id']]['title'],title)
        self.assertIsNone(model.locate('choices','choice_ro6_bat5_1'))
    def test_fixed_cost_boundaries_unknown3_4_9_10_leave_independent_and_not_actual_eligibility(self):
        for gold in(None,0,3,4,9,10):
            r=model.reference('敲动杠杆',gold)
            for key,cost in(('choice_ro6_res5_1',4),('choice_ro6_res5_2',10)):
                c=by_original(r,key);row=model.choice_reference(r,c['scene_id'],c['id']);self.assertEqual(row['gold_cost_reference'],cost);self.assertIs(row['listed_condition_match'],None if gold is None else gold>=cost);self.assertIsNone(row['actual_eligible']);self.assertIsNone(row['actual_consumed'])
            c=by_original(r,'choice_ro6_res5_3');self.assertIsNone(model.choice_reference(r,c['scene_id'],c['id'])['listed_condition_match']);self.assertFalse(r['run_updated']);self.assertIsNone(r['actual_eligible'])
        for value in(-1,False,1.5,'4'):
            with self.assertRaises(ValueError):model.reference('敲动杠杆',value)
        with self.assertRaises(ValueError):model.reference('桑尼的邀请',4)
    def test_three_random_part_categories_not_relic_pool_and_one_vs_three_quantities(self):
        r=model.reference('货从口出')
        for i,kind in enumerate(('加工品','概念体','自然物'),1):
            c=by_original(r,'choice_ro6_res3_'+str(i));self.assertEqual(c['gold_cost_reference'],4);self.assertEqual(c['random_reward_reference'],{'quantity':1,'kind':kind,'pool':None});self.assertIsNone(c['named_reward_item_id'])
        r=model.reference('敲动杠杆')
        for n,qty in((1,1),(2,3)):
            c=by_original(r,'choice_ro6_res5_'+str(n));self.assertEqual(c['random_reward_reference'],{'quantity':qty,'kind':'收藏品','pool':None});self.assertIn('不把多选项奖励相加',model.player_text(r,c['scene_id'],c['id']))
    def test_hpmax_shield_action_and_hope_separate_six_named_items_no_guessed_quantity(self):
        all_rows=model.packet()['data']['choices'];named=[c for c in all_rows.values()if c['named_reward_item_id']];self.assertEqual(len(named),6)
        for c in named:
            r=model.reference(c['event_id']);item=r['data']['originals']['items'][c['named_reward_item_id']];self.assertEqual(item['type'],'RELIC');self.assertIsNone(c['named_reward_quantity']);self.assertIsNone(c['actual_received']);self.assertIn(item['name'],model.player_text(r,c['scene_id'],c['id']));self.assertIn('不补成1件',model.player_text(r,c['scene_id'],c['id']))
        for title in('桑尼的邀请','血衣之下','泪之聚落'):
            r=model.reference(title)
            for c in r['choices'].values():self.assertNotIn('本页填写的源石锭',model.player_text(r,c['scene_id'],c['id']))
        resources=[c['resource_reward_reference']for c in all_rows.values()if c['resource_reward_reference']];self.assertEqual(len(resources),7);self.assertIn({'quantity':3,'resource':'目标生命值上限'},resources);self.assertIn({'quantity':5,'resource':'护盾'},resources);self.assertIn({'quantity':5,'resource':'行动力'},resources);self.assertIn({'quantity':3,'resource':'希望'},resources)
    def test_half_life_no_copied_one_hp_floor_all_gold_not_fixed_or_zero_eligibility(self):
        r=model.reference('沉重的契约');c=by_original(r,'choice_ro6_res4_2');text=model.player_text(r,c['scene_id'],c['id']);self.assertTrue(c['half_life_cost_reference']);self.assertIsNone(c['gold_cost_reference']);self.assertIn('不能从其它事件搬用保留1点',text);self.assertIn('奇数时的取整',text)
        r=model.reference('泪之聚落');c=by_original(r,'choice_ro6_chimera2_1');self.assertTrue(c['all_gold_cost_reference']);self.assertIsNone(c['gold_cost_reference']);self.assertIn('零源石锭时是否出现或可选',model.player_text(r,c['scene_id'],c['id']))
    def test_each_manifest_file_damage_and_complete_current_drift_fail_closed(self):
        with TemporaryDirectory()as folder:
            root=Path(folder);clone(root);m=json.loads((root/model.MANIFEST).read_bytes())
            with patch.object(model,'ROOT',root):
                for name in(model.MANIFEST,*m['files']):
                    f=root/name;raw=f.read_bytes();f.write_bytes(raw+b' ');self.assertIsNone(model.packet(),name);f.write_bytes(raw);self.assertIsNotNone(model.packet())
        r=deepcopy(model.version.packet());r['current']['details']['choices']['choice_ro6_res5_2']['description']='unverified'
        with patch.object(model.version,'packet',return_value=r):self.assertIsNone(model.packet())
    def test_builder_rejects_conflicting_next_and_duplicate_narrative(self):
        for kind in('next','scene'):
            with TemporaryDirectory()as folder:
                root=Path(folder);clone(root);f=root/builder.CURRENT;d=json.loads(f.read_bytes())
                if kind=='next':d['details']['choices']['choice_ro6_res5_2']['nextSceneId']='scene_ro6_res5_1'
                else:d['details']['choiceScenes']['invented']=deepcopy(d['details']['choiceScenes']['scene_ro6_res5_2'])
                f.write_bytes(builder.encoded(d))
                with self.assertRaises(ValueError):builder.build(root)
if __name__=='__main__':unittest.main()
