from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from copy import deepcopy
import json,shutil,unittest
from rouge import current_lake as model
from scripts import build_current_lake_328 as builder
ROOT=Path(__file__).resolve().parents[1]
def clone(root):
    m=json.loads((ROOT/model.MANIFEST).read_bytes())
    for name in(model.MANIFEST,*m['files']):
        p=root/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,p)
def cid(n):return 'choice_ro6_bat5_'+str(n)
def sid(n):return 'scene_ro6_bat5_'+str(n)
class CurrentLake328Tests(unittest.TestCase):
    def test_whole_table_reproducible_full_records_and_independent_baseline_comparison(self):
        d,m=builder.build();self.assertEqual(d,(ROOT/model.DATA).read_bytes());self.assertEqual(m,(ROOT/model.MANIFEST).read_bytes());data=model.packet()['data'];self.assertEqual(data['counts'],{'scenes':10,'original_choices':10,'caption_cells':13,'scene_choice_references':14,'random_outcomes':2,'pay_actions':3,'named_battle_choices':2})
        current=model.version.packet()['current']['details'];old=model.version.packet()['baseline']['details']
        for g,rows in data['originals'].items():
            table='choiceScenes'if g=='scenes'else g
            for k,v in rows.items():self.assertEqual(v,current[table][k]);self.assertIs(data['complete_selected_record_comparison_to_baseline'][g][k],old[table].get(k)==v)
        self.assertFalse(data['complete_game_option_pool']);self.assertFalse(data['game_parent_script_restored'])
    def test_all_ten_scenes_and_choices_shared_context_never_defaults_initial(self):
        r=model.reference()
        for key in r['scenes']:self.assertEqual(model.locate('scenes',key),{'event_id':'lake','scene_id':key,'choice_id':None,'phase_needed':False})
        for key,c in r['choices'].items():
            t=model.locate('choices',key);self.assertEqual(t['phase_needed'],len(c['scene_ids'])>1)
            if t['phase_needed']:self.assertIsNone(t['scene_id']);self.assertEqual(c['scene_ids'],[sid(1),sid(5),sid(6)])
            for s in c['scene_ids']:self.assertEqual(model.choice_reference(r,s,key)['scene_id'],s)
        self.assertIsNone(model.locate('choices',cid(99)));self.assertIsNone(model.locate('choices','choice_ro6_bat4_4'));self.assertIsNone(model.choice_reference(r,sid(9),cid(1)))
    def test_repeated_note_targets_quoted_watch_separately_and_random_stays_unselected(self):
        r=model.reference();c=r['choices'][cid(7)];self.assertEqual(c['scene_ids'],[sid(5)]);self.assertEqual(c['next_scene_id'],sid(6));self.assertEqual(c['mapping_basis'],'explicit_repeat_note_plus_unique_current_nextSceneId');self.assertIn('若在第一轮环节',c['source_cells'][0]['text']);c=r['choices'][cid(8)];self.assertEqual(c['scene_ids'],[sid(6)]);self.assertIsNone(c['next_scene_id']);self.assertEqual(r['data']['originals']['choices'][cid(8)]['type'],'NEXT_PROB');self.assertEqual({x['scene_id']for x in c['documented_outcomes']},{sid(7),sid(8)})
        for row in c['documented_outcomes']:self.assertIsNone(row['probability']);self.assertIsNone(row['actual_result'])
        self.assertIsNone(r['actual_outcome']);self.assertIsNone(r['actual_probability']);self.assertFalse(r['run_updated']);self.assertIn('不会同时发生',model.player_text(r,sid(6),cid(8)))
    def test_cost_is_each_action_only_reward_explicit_one_precious_no_guessed_pool(self):
        r=model.reference()
        for n in(3,7,8):
            c=r['choices'][cid(n)];self.assertEqual(c['gold_cost_reference'],1);self.assertIsNone(c['actual_consumed']);self.assertIn('不自动累计本局投入',model.player_text(r,c['scene_ids'][0],cid(n)))
        c=r['choices'][cid(10)];self.assertEqual(c['reward_reference'],{'quantity':1,'quality':'珍贵','kind':'收藏品','pool':None});self.assertIsNone(c['actual_received']);self.assertIn('1件珍贵收藏品',model.player_text(r,sid(8),cid(10)))
    def test_only_exact_normal_and_urgent_battle_links_optional_reader(self):
        r=model.reference()
        for n,s in((5,3),(9,7)):self.assertEqual(model.battle_target(r,sid(s),cid(n))['choice_id'],cid(n))
        self.assertIsNone(model.battle_target(r,sid(6),cid(8)))
        with patch('rouge.current_event_battles.locate',return_value=None):self.assertIsNotNone(model.reference());self.assertIsNone(model.battle_target(r,sid(3),cid(5)))
    def test_each_file_damage_and_full_current_record_drift_fail_closed(self):
        with TemporaryDirectory()as folder:
            root=Path(folder);clone(root);m=json.loads((root/model.MANIFEST).read_bytes())
            with patch.object(model,'ROOT',root):
                for name in(model.MANIFEST,*m['files']):
                    f=root/name;raw=f.read_bytes();f.write_bytes(raw+b' ');self.assertIsNone(model.packet(),name);f.write_bytes(raw);self.assertIsNotNone(model.packet())
        p=deepcopy(model.version.packet());p['current']['details']['choices'][cid(8)]['nextSceneId']=sid(7)
        with patch.object(model.version,'packet',return_value=p):self.assertIsNone(model.packet())
    def test_builder_rejects_duplicate_narrative_or_invented_random_next(self):
        for kind in('scene','next'):
            with TemporaryDirectory()as folder:
                root=Path(folder);clone(root);f=root/builder.CURRENT;d=json.loads(f.read_bytes())
                if kind=='scene':d['details']['choiceScenes']['invented']=deepcopy(d['details']['choiceScenes'][sid(6)])
                else:d['details']['choices'][cid(8)]['nextSceneId']=sid(7)
                f.write_bytes(builder.encoded(d))
                with self.assertRaises(ValueError):builder.build(root)
if __name__=='__main__':unittest.main()
