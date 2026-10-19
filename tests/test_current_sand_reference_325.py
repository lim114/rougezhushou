from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from copy import deepcopy
import json,shutil,unittest
from rouge import current_sand_reference as model
from scripts import build_current_sand_reference_325 as builder
ROOT=Path(__file__).resolve().parents[1]
def clone(root):
    m=json.loads((ROOT/model.MANIFEST).read_bytes())
    for name in(model.MANIFEST,*m['files']):
        p=root/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,p)
def choice(event,values,cid):
    r=model.reference(event,values);return r,model.choice_reference(r,r['event']['entry_scene_id'],cid)
GOOD={'floor':5,'node_type':'命运所指','cleared_reboot':True,'has_alpha':True,'has_beta':False,'target_marked':False,'gold':50}
class CurrentSandReference325Tests(unittest.TestCase):
    def test_complete_source_reproducible_seven_scenes_five_options_and_exact_rewards(self):
        d,m=builder.build();self.assertEqual(d,(ROOT/model.DATA).read_bytes());self.assertEqual(m,(ROOT/model.MANIFEST).read_bytes());r=model.packet();p=r['data'];self.assertEqual((len(p['events']),len(p['scenes']),len(p['choices'])),(2,7,5));self.assertEqual(len(p['originals']['items']),4);self.assertEqual(p['originals']['stages'],{})
        for k,c in p['choices'].items():self.assertEqual(c['stage_ids'],[]);self.assertEqual(c['next_scene_id'],p['originals']['choices'][k]['nextSceneId'])
        self.assertTrue(all(x for rows in p['complete_selected_record_comparison_to_baseline'].values()for x in rows.values()));self.assertFalse(p['complete_game_option_pool']);self.assertIsNone(p['choices']['choice_ro6_bomb1_1']['reward']['quantity']);self.assertEqual(p['choices']['choice_ro6_bomb1_2']['reward']['kind'],'加工品');self.assertEqual(p['choices']['choice_ro6_end1_2']['reward']['quantity'],1);self.assertIsNone(p['choices']['choice_ro6_end1_2']['reward']['pool'])
    def test_explicit_parent_groups_not_a_flat_all_events_menu(self):
        for event,expected in(('informer',3),('curiosity',2)):
            r=model.reference(event);entry=r['event']['entry_scene_id'];self.assertEqual(len(r['scenes'][entry]['choice_ids']),expected)
            for sid,s in r['scenes'].items():
                if sid!=entry:self.assertEqual(s['choice_ids'],[])
                for cid in s['choice_ids']:self.assertIsNotNone(model.choice_reference(r,sid,cid))
            self.assertIsNone(model.choice_reference(r,entry,'choice_ro6_end2_1'))
    def test_gold_49_50_51_unknown_and_marker_gate_do_not_turn_marking_into_reward(self):
        for gold,expected in((49,False),(50,True),(51,True),(None,None)):
            r,c=choice('curiosity',{**GOOD,'gold':gold},'choice_ro6_end1_1');self.assertIs(c['listed_condition_match'],expected);self.assertIsNone(c['reward']);self.assertEqual(c['cost_gold'],50);self.assertIsNone(c['actual_eligible']);text=model.player_text(r,c['scene_id'],c['id']);self.assertIn('不是再获得一件收藏品',text)
        for marked,expected in((True,False),(False,True),(None,None)):
            _,c=choice('curiosity',{**GOOD,'target_marked':marked},'choice_ro6_end1_1');self.assertIs(c['listed_condition_match'],expected)
        _,reward=choice('curiosity',{**GOOD,'gold':0,'target_marked':True},'choice_ro6_end1_2');self.assertIs(reward['listed_condition_match'],True)
    def test_three_valued_sand_either_one_known_and_neither_not_unknown(self):
        for a,b,expected in((True,None,True),(None,True,True),(False,False,False),(False,None,None),(None,None,None)):
            _,c=choice('curiosity',{**GOOD,'has_alpha':a,'has_beta':b},'choice_ro6_end1_2');self.assertIs(c['listed_condition_match'],expected)
        for change in({'floor':4},{'node_type':'不期而遇'},{'cleared_reboot':False}):
            _,c=choice('curiosity',{**GOOD,**change},'choice_ro6_end1_2');self.assertIs(c['listed_condition_match'],False)
    def test_unlock_only_applies_related_informer_reward_not_all_other_options(self):
        v={'floor':2,'node_type':'不期而遇','cleared_reboot':False}
        _,c=choice('informer',v,'choice_ro6_bomb1_1');self.assertIs(c['listed_condition_match'],False)
        for cid in('choice_ro6_bomb1_2','choice_ro6_bomb1_3'):
            _,c=choice('informer',v,cid);self.assertIs(c['listed_condition_match'],True)
        for f in(1,5,6):
            _,c=choice('informer',{**v,'floor':f},'choice_ro6_bomb1_2');self.assertIs(c['listed_condition_match'],False)
    def test_history_and_inconsistent_marker_never_erase_or_rewrite_facts(self):
        r,c=choice('curiosity',{**GOOD,'floor':1,'gold':0,'has_alpha':False,'scope':'history'},'choice_ro6_end1_1');self.assertIsNone(c['listed_condition_match']);self.assertIn('不用于否定过去',model.player_text(r,c['scene_id'],c['id']));self.assertEqual(r['context']['gold'],0)
        r,c=choice('curiosity',{**GOOD,'has_beta':True},'choice_ro6_end1_1');self.assertTrue(c['contradictory_marker_declaration']);self.assertIsNone(c['listed_condition_match']);self.assertIn('不一致',model.player_text(r,c['scene_id'],c['id']));self.assertFalse(r['context']['target_marked']);self.assertFalse(r['run_updated'])
    def test_exact_entry_and_relic_selection_is_not_possession(self):
        d=model.packet()['data']
        for key in d['choices']:self.assertEqual(model.locate('choices',key)['choice_id'],key)
        for key in d['scenes']:self.assertEqual(model.locate('scenes',key)['scene_id'],key)
        a=model.locate('relics','rogue_6_relic_final_1');b=model.locate('relics','rogue_6_relic_final_2');self.assertEqual(a['choice_id'],'choice_ro6_bomb1_1');self.assertIsNone(b['choice_id']);self.assertEqual(b['event_id'],'curiosity');self.assertIsNone(model.reference(b['event_id'])['context']['has_beta'])
        for cat,key in(('scenes','scene_ro6_end2_enter'),('choices','choice_ro6_bomb1_999'),('relics','rogue_6_relic_final_3'),('stages','ro6_b_5')):self.assertIsNone(model.locate(cat,key))
    def test_conflicting_marker_does_not_override_known_insufficient_payment(self):
        _,c=choice('curiosity',{**GOOD,'has_beta':True,'gold':49},'choice_ro6_end1_1');self.assertTrue(c['contradictory_marker_declaration']);self.assertIs(c['listed_condition_match'],False)
        _,c=choice('informer',{'floor':2,'node_type':'不期而遇','has_alpha':True,'has_beta':True,'target_marked':False},'choice_ro6_bomb1_2');self.assertFalse(c['contradictory_marker_declaration']);self.assertIs(c['listed_condition_match'],True)
    def test_invalid_context_types_rejected_before_partial_condition_pass(self):
        for v in({'gold':True},{'gold':-1},{'has_alpha':1},{'floor':True},{'floor':7},{'scope':'future'},{'node_type':'作战'},{'other':True}):
            with self.assertRaises(ValueError):model.context(v)
    def test_every_actual_public_source_corruption_and_complete_record_drift_closed(self):
        with TemporaryDirectory()as folder:
            root=Path(folder);clone(root);m=json.loads((root/model.MANIFEST).read_bytes())
            with patch.object(model,'ROOT',root):
                for name in(model.MANIFEST,*m['files']):
                    p=root/name;raw=p.read_bytes();p.write_bytes(raw+b' ');self.assertIsNone(model.packet(),name);p.write_bytes(raw);self.assertIsNotNone(model.packet())
        p=deepcopy(model.version.packet());p['current']['details']['choices']['choice_ro6_end1_1']['description']='消耗49源石锭'
        with patch.object(model.version,'packet',return_value=p):self.assertIsNone(model.packet())
    def test_builder_rejects_ambiguous_caption_and_wrong_next(self):
        for mode in('duplicate','next'):
            with TemporaryDirectory()as folder:
                root=Path(folder);clone(root);p=root/builder.CURRENT;v=json.loads(p.read_bytes())
                if mode=='duplicate':v['details']['choices']['duplicate']=deepcopy(v['details']['choices']['choice_ro6_end1_1'])
                else:v['details']['choices']['choice_ro6_end1_1']['nextSceneId']='scene_ro6_end1_2'
                p.write_bytes(builder.encoded(v))
                with self.assertRaises(ValueError):builder.build(root)

if __name__=='__main__':unittest.main()
