from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from copy import deepcopy
import json,shutil,unittest
from rouge import current_rest_travel as model
from scripts import build_current_rest_travel_331 as builder
ROOT=Path(__file__).resolve().parents[1]
def clone(root):
    m=json.loads((ROOT/model.MANIFEST).read_bytes())
    for name in(model.MANIFEST,*m['files']):
        p=root/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,p)
def by_original(r,key):return next(c for c in r['choices'].values()if key in c['variant_ids'])
class CurrentRestTravel331Tests(unittest.TestCase):
    def test_whole_tables_reproducible_17_scenes19_choices6_items_and_full_baseline(self):
        d,m=builder.build();self.assertEqual(d,(ROOT/model.DATA).read_bytes());self.assertEqual(m,(ROOT/model.MANIFEST).read_bytes());data=model.packet()['data'];self.assertEqual(data['counts'],{'events':2,'document_scenes':11,'original_scenes':17,'document_choices':10,'original_choices':19,'display_items':6,'travel_accept_variants':6,'travel_exit_variants':3})
        current=model.version.packet()['current']['details'];old=model.version.packet()['baseline']['details']
        for g,rows in data['originals'].items():
            table='choiceScenes'if g=='scenes'else g
            for k,v in rows.items():self.assertEqual(v,current[table][k]);self.assertIs(data['complete_selected_record_comparison_to_baseline'][g][k],old[table].get(k)==v)
        self.assertFalse(data['complete_game_option_pool']);self.assertFalse(data['game_parent_script_restored'])
    def test_rest_seven_documented_options_not_simultaneous_or_proved_seven_choose_three(self):
        r=model.reference('金色凝滞');self.assertEqual(len(r['choices']),7);self.assertEqual(r['event']['documented_random_option_count'],3);self.assertFalse(r['event']['stashed_ticket_shared_random_group_verified']);self.assertIsNone(r['actual_menu']);self.assertIn('不把7项当成本局同时出现',model.player_text(r,r['event']['entry_scene_id']));self.assertTrue(any('随机3个'in c['text']for c in r['event']['document_notes']))
        c=by_original(r,'choice_ro6_rest_7');self.assertEqual(c['processing_type'],'USE_STASHED_TICKET');self.assertIsNone(c['effect_reference']['quantity']);self.assertIn('不是获得新券',model.player_text(r,c['scene_id'],c['id']))
    def test_resource_deltas_distinguish_capacities_and_named_ticket_no_assumed_count(self):
        r=model.reference('金色凝滞');expected={1:(3,'目标生命值上限'),2:(1,'可携带干员数'),3:(3,'希望'),4:(None,'高级物资配给券'),5:(2,'行动力'),6:(1,'零件箱容量'),7:(None,'使用留存招募券')}
        for n,(qty,resource)in expected.items():
            c=by_original(r,'choice_ro6_rest_'+str(n));self.assertEqual(c['effect_reference'],{'quantity':qty,'resource':resource});self.assertIsNone(c['actual_received']);self.assertIsNone(c['actual_consumed'])
        for n,needle in((1,'是否同时回复当前目标生命值不能据此额外断定'),(2,'不等于新招募1名'),(4,'不自动补1张'),(6,'不是获得1件零件')):
            c=by_original(r,'choice_ro6_rest_'+str(n));self.assertIn(needle,model.player_text(r,c['scene_id'],c['id']))
    def test_triple_three_cg_aliases_six_accept_records_and_display_hp_not_extra_reward(self):
        r=model.reference('三重身');self.assertEqual(r['event']['documented_picture_count'],3);self.assertEqual(len(r['event']['backgrounds']),3);self.assertEqual(len(r['scenes']),3)
        for s in r['scenes'].values():self.assertEqual(len(s['original_scene_ids']),3)
        c=by_original(r,'choice_ro6_evacuate_1');self.assertEqual(len(c['variant_ids']),6);self.assertEqual(c['display_item_ids'],['rogue_6_hpmax']);self.assertTrue(c['display_item_includes_none']);self.assertEqual(c['effect_reference'],{'quantity':1,'resource':'加工品','quality':'珍贵','pool':None,'retain_ap_reference':True,'enter_next_region_reference':True});self.assertIn('展示标记不能证明额外生命奖励',model.player_text(r,c['scene_id'],c['id']));self.assertIsNone(r['actual_background']);self.assertIsNone(r['actual_departed'])
    def test_travel_exit_only_document_decline_parent_no_synthetic_next_or_accept_confirmation(self):
        r=model.reference('三重身');accept=by_original(r,'choice_ro6_evacuate_1');decline=by_original(r,'choice_ro6_evacuate_2');exit=by_original(r,'choice_ro6_evacuate_4');self.assertEqual(r['scenes'][accept['next_scene_id']]['choice_ids'],[]);self.assertEqual(r['scenes'][decline['next_scene_id']]['choice_ids'],[exit['id']]);self.assertEqual(exit['processing_type'],'ZONE_END');self.assertIsNone(exit['next_scene_id']);self.assertEqual(exit['original_next_scene_ids'],[None]);self.assertEqual(len(exit['variant_ids']),3);self.assertIsNone(exit['actual_parent_scene_id']);self.assertIn('不假定两分支共用确认',model.player_text(r,exit['scene_id'],exit['id']))
    def test_all36_original_entries_exact_source_lookup_no_actual_record_selection(self):
        d=model.packet()['data'];count=0
        for cat,rows in(('scenes',d['originals']['scenes']),('choices',d['originals']['choices'])):
            for key in rows:
                count+=1;t=model.locate(cat,key);self.assertEqual(t['source_request'],{'category':cat,'key':key});r=model.reference(t['event_id'],t['source_request']);self.assertEqual(r['source_request'],t['source_request']);self.assertIsNone(r['actual_background']);self.assertIsNone(r['actual_menu'])
                if cat=='scenes':self.assertIn(key,r['scenes'][t['scene_id']]['original_scene_ids'])
                else:self.assertIn(key,r['choices'][t['choice_id']]['variant_ids'])
        self.assertEqual(count,36);self.assertIsNone(model.locate('choices','choice_ro6_wish_1'));self.assertIsNone(model.reference('三重身',{'category':'choices','key':'choice_ro6_rest_1'}));self.assertIsNone(model.reference('三重身',{'category':'choices','key':'invented'}))
    def test_each_file_damage_and_full_current_display_drift_fail_closed(self):
        with TemporaryDirectory()as folder:
            root=Path(folder);clone(root);m=json.loads((root/model.MANIFEST).read_bytes())
            with patch.object(model,'ROOT',root):
                for name in(model.MANIFEST,*m['files']):
                    f=root/name;raw=f.read_bytes();f.write_bytes(raw+b' ');self.assertIsNone(model.packet(),name);f.write_bytes(raw);self.assertIsNotNone(model.packet())
        p=deepcopy(model.version.packet());p['current']['details']['choices']['choice_ro6_evacuate_3']['displayData']['itemId']=None
        with patch.object(model.version,'packet',return_value=p):self.assertIsNone(model.packet())
    def test_builder_rejects_missing_alias_or_conflicting_prose_next(self):
        for kind in('alias','next'):
            with TemporaryDirectory()as folder:
                root=Path(folder);clone(root);f=root/builder.CURRENT;d=json.loads(f.read_bytes())
                if kind=='alias':del d['details']['choiceScenes']['scene_ro6_evacuate3_1']
                else:d['details']['choices']['choice_ro6_evacuate_3']['nextSceneId']='scene_ro6_evacuate_2'
                f.write_bytes(builder.encoded(d))
                with self.assertRaises(ValueError):builder.build(root)
if __name__=='__main__':unittest.main()
