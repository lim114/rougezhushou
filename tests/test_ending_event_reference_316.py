from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import json,shutil,unittest
from rouge import ending_event_reference as model
from scripts.build_ending_events_reference_316 import build
ROOT=Path(__file__).resolve().parents[1]

class EndingEventReference316Tests(unittest.TestCase):
    def test_rebuild_exact_pinned_current_objects(self):
        data,manifest=build();self.assertEqual(data,(ROOT/model.DATA).read_bytes());self.assertEqual(manifest,(ROOT/model.MANIFEST).read_bytes());r=model.packet();self.assertIsNotNone(r)
        self.assertEqual(len(r['data']['records']),7);self.assertEqual(len(r['data']['selected_originals']['choices']),12);self.assertEqual(len(r['data']['selected_originals']['stages']),7)
        self.assertFalse(r['data']['original_scene_choice_script_restored']);self.assertIsNone(r['actual_eligible'])
    def test_entry_cost_does_not_exclude_event(self):
        c={'floor':1,'node_type':'险路尽头','gold':9,'post_update_clear':True};r=model.evaluate('entry',c);self.assertEqual(r['listed_conditions_status'],'listed_matched');self.assertEqual(r['choice_conditions_status']['choice_ro6_final1_8'],'not_matched')
        c['gold']=10;self.assertEqual(model.evaluate('entry',c)['choice_conditions_status']['choice_ro6_final1_8'],'listed_matched')
        c['floor']=3;self.assertEqual(model.evaluate('entry',c)['listed_conditions_status'],'not_matched')
    def test_button_npc_only_gates_advancing_option(self):
        r=model.evaluate('button',{'region':'熄日余径','node_type':'命运所指','adventurer_alive':False});self.assertEqual(r['listed_conditions_status'],'listed_matched');self.assertEqual(r['choice_conditions_status']['choice_ro6_end4_1'],'not_matched');self.assertNotIn('choice_ro6_end4_2',r['choice_checks']);self.assertIsNone(r['actual_choice_eligible'])
    def test_future_generation_does_not_remove_existing_or_history(self):
        c={'scope':'future','region':'main','floor':3,'has_prayer':True,'has_covenant':False};self.assertEqual(model.evaluate('side_path',c)['listed_conditions_status'],'listed_matched')
        c['has_covenant']=True;self.assertEqual(model.evaluate('side_path',c)['listed_conditions_status'],'not_matched');c['scope']='current';r=model.evaluate('side_path',c);self.assertEqual(r['event_checks'],[]);self.assertEqual(r['listed_conditions_status'],'unknown')
        c['scope']='history';self.assertEqual(model.evaluate('side_path',c)['listed_conditions_status'],'reference_only')
    def test_only_normal_path_battle_has_documented_extra_relic(self):
        for region,node,expected in [('熄日余径','普通作战','listed_matched'),('熄日余径','紧急作战','not_matched'),('main','普通作战','not_matched')]:self.assertEqual(model.evaluate('path_bonus',{'region':region,'node_type':node})['listed_conditions_status'],expected)
        self.assertIsNone(model.evaluate('path_bonus')['actual_reward'])
    def test_rescue_once_and_unmarked_next_conditions(self):
        c={'node_type':'不期而遇','next_unmarked_after_first_down':True,'rescue_used':False};self.assertEqual(model.evaluate('revive',c)['listed_conditions_status'],'listed_matched');c['rescue_used']=True;self.assertEqual(model.evaluate('revive',c)['listed_conditions_status'],'not_matched');c['rescue_used']=None;self.assertEqual(model.evaluate('revive',c)['listed_conditions_status'],'unknown')
    def test_unknown_blueprint_node_not_assigned_to_every_type(self):
        for node in ('命运所指','不期而遇','普通作战'):
            r=model.evaluate('blueprint',{'node_type':node});self.assertEqual(r['listed_conditions_status'],'unknown');self.assertEqual(r['event_checks'],[]);self.assertIn('未明确',model.player_text(r))
    def test_exact_graypit_and_two_boss_configs_no_suffix_inference(self):
        r=model.evaluate('button');self.assertEqual(r['record']['stage_ids'],['ro6_s_1']);self.assertEqual(r['battle_choices'][0]['name'],'灰坑');h=model.evaluate('hidden_region');self.assertEqual(len(h['battle_choices']),6);self.assertEqual([h['originals']['stages'][k]['name']for k in('ro6_b_7','ro6_b_7_b')],['熄日','熄日']);self.assertEqual(h['originals']['zone']['name'],'盲目者所见')
    def test_invalid_and_contradictory_context_not_silently_repaired(self):
        for values in ({'floor':True},{'gold':False},{'gold':-1},{'floor':7},{'has_prayer':1},{'unrecognised':1}):
            with self.assertRaises(ValueError):model.context(values)
        r=model.evaluate('entry',{'floor':1,'node_type':'险路尽头','post_update_clear':False,'has_prayer':True});self.assertTrue(r['contradictions']);self.assertFalse(r['context']['post_update_clear']);self.assertTrue(r['context']['has_prayer']);self.assertEqual(r['listed_conditions_status'],'unknown')
    def test_all_records_chinese_unknown_and_no_actual_state_or_probability(self):
        for record in model.packet()['data']['records']:
            r=model.evaluate(record['id']);text=model.player_text(r);self.assertIn(record['title'],text);self.assertIn('未知',text);self.assertIsNone(r['probability']);self.assertIsNone(r['actual_event_eligible']);self.assertFalse(r['memory_updated'])
    def test_actual_excerpt_corruption_invalidates_packet(self):
        manifest=json.loads((ROOT/model.MANIFEST).read_bytes())
        with TemporaryDirectory()as folder:
            root=Path(folder)
            for name in(model.MANIFEST,*manifest['files']):
                p=root/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,p)
            with patch.object(model,'ROOT',root):
                self.assertIsNotNone(model.packet());p=root/model.PACK/'topic-441984-excerpt.md';raw=p.read_bytes();p.write_bytes(raw+b' ');self.assertIsNone(model.packet());p.write_bytes(raw);self.assertIsNotNone(model.packet())

if __name__=='__main__':unittest.main()
