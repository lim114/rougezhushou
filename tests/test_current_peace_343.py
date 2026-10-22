from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import json,subprocess,sys,unittest
from rouge import current_peace as model,node_catalog

def clone(root):
    names={model.MANIFEST,*json.loads((model.ROOT/model.MANIFEST).read_bytes())['files'],model.packet()['data']['icon_reference']['file']}
    for name in names:
        p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((model.ROOT/name).read_bytes())

class CurrentPeace343Tests(unittest.TestCase):
    def test_complete_build_and_all_source_records_match_current(self):
        p=subprocess.run([sys.executable,'-B','scripts/build_current_peace_343.py','--check'],cwd=model.ROOT,capture_output=True);self.assertEqual(p.returncode,0,p.stderr)
        r=model.reference();self.assertEqual((len(r['scenes']),len(r['choices'])),(3,4));current=model.version.packet()['current']['details']
        for kind,table in [('scenes','choiceScenes'),('choices','choices'),('items','items')]:
            for key,v in r['data']['originals'][kind].items():self.assertEqual(v,current[table][key])
        self.assertEqual([c['role']for c in r['choices'].values()],['join','leave','move','mark'])
    def test_only_joined_context_has_move_and_mark_not_leave(self):
        r=model.reference();join=r['choices']['choice_ro6_task1_1'];leave=r['choices']['choice_ro6_task1_2'];self.assertEqual(r['scenes'][join['next_scene_id']]['choice_ids'],['choice_ro6_task1_3','choice_ro6_task1_4']);self.assertEqual(r['scenes'][leave['next_scene_id']]['choice_ids'],[])
        self.assertEqual(len(r['scenes'][r['event']['entry_scene_id']]['choice_ids']),2)
    def test_three_condition_values_do_not_invert_one_way_exception(self):
        for value in(None,True,False):
            r=model.reference(completed=value);c=model.choice_reference(r,'scene_ro6_task1_1','choice_ro6_task1_3')
            self.assertIs(c['documented_no_move_reference'],True if value is True else None);self.assertIsNone(c['actual_moved']);self.assertIsNone(r['actual_current_floor_completion']);self.assertIsNone(r['actual_target_node'])
            text=model.player_text(r,c['scene_id'],c['id']);self.assertIn('未完成并不保证一定移动',text)
            if value is False:self.assertIn('仍不能据此保证移动或指定目的地',text)
            if value is True:self.assertIn('这不是本局实际状态',text)
        for value in(0,1,'false',[],{}):self.assertIsNone(model.reference(completed=value))
    def test_mark_is_not_move_battle_win_or_second_item(self):
        r=model.reference(completed=True);c=model.choice_reference(r,'scene_ro6_task1_1','choice_ro6_task1_4');text=model.player_text(r,c['scene_id'],c['id']);self.assertIsNone(c['documented_no_move_reference']);self.assertIn('标记不表示已移动、进入作战或取得胜利',text);self.assertIsNone(c['next_scene_id']);self.assertEqual(c['stage_ids'],[]);self.assertIsNone(c['actual_marked'])
    def test_join_receipt_not_win_and_speed10_is_not_ten_percent(self):
        r=model.reference();c=r['choices']['choice_ro6_task1_1'];text=model.player_text(r,c['scene_id'],c['id'])
        for word in('不等于已经前往或获胜','永久攻速奖励还要求作战胜利','+10也不是+10%','累计胜利次数','敌人生命-40%'):self.assertIn(word,text)
        self.assertFalse(r['run_updated']);self.assertTrue(all(r[k]is None for k in('actual_received','actual_moved','actual_marked','actual_battle_won','actual_attack_speed_stacks','actual_eligible')))
    def test_leave_and_overview_do_not_expose_unrelated_relic(self):
        r=model.reference();c=r['choices']['choice_ro6_task1_2'];self.assertFalse(model.shows_reward(r,c['scene_id'],c['id']));self.assertFalse(model.shows_reward(r,c['next_scene_id']));self.assertFalse(model.shows_reward(r,r['event']['entry_scene_id']));self.assertNotIn('【悬赏收藏品】',model.player_text(r,c['scene_id'],c['id']))
        self.assertTrue(model.shows_reward(r,'scene_ro6_task1_1'))
    def test_all_seven_exact_entries_and_unknown_input_rejected(self):
        r=model.reference();count=0
        for cat in('scenes','choices'):
            for key in r['data']['originals'][cat]:
                t=model.locate(cat,key);self.assertEqual(t['scene_id'],key if cat=='scenes'else r['choices'][key]['scene_id']);self.assertEqual(t['choice_id'],None if cat=='scenes'else key);count+=1
        self.assertEqual(count,7)
        for cat,key in [('choices','守卫和平！'),('scenes','scene_ro6_task1_1x'),('relics','rogue_6_relic_cargo_11'),(True,1)]:self.assertIsNone(model.locate(cat,key))
        self.assertIsNone(model.reference(True));self.assertIsNone(model.reference('other'));self.assertIsNone(model.choice_reference(r,True,1))
    def test_all_sources_fail_closed_then_restore(self):
        with TemporaryDirectory()as folder:
            root=Path(folder);clone(root)
            with patch.object(model,'ROOT',root):
                for name in(model.MANIFEST,*json.loads((root/model.MANIFEST).read_bytes())['files']):
                    f=root/name;raw=f.read_bytes();self.assertIsNotNone(model.reference());f.write_bytes(raw+b' ');self.assertIsNone(model.reference(),name);f.write_bytes(raw);self.assertIsNotNone(model.reference())
    def test_bad_icon_only_keeps_text_and_mutable_results_are_isolated(self):
        r=model.reference();self.assertIsNotNone(model.icon_bytes())
        with TemporaryDirectory()as folder:
            root=Path(folder);clone(root)
            with patch.object(model,'ROOT',root):
                f=root/r['data']['icon_reference']['file'];f.write_bytes(f.read_bytes()+b'x');self.assertIsNone(model.icon_bytes());self.assertIsNotNone(model.reference())
        r['choices'].clear();r['data']['movement_exception_reference'].clear();self.assertEqual(len(model.reference()['choices']),4)
    def test_full_catalogue_exact_identity_and_old291_boundary_preserved(self):
        e=deepcopy(node_catalog._event('community_group_019'));self.assertEqual(len(model.catalogue_binding(e)['exact_scene_links']),3);e['scenes'][0]['description']+='x';self.assertIsNone(model.catalogue_binding(e))
        from rouge import peace_guardian_results as old
        d=old.source_data();self.assertFalse(d['source_scene_link_verified']);self.assertFalse(d['complete_movement_result_known']);self.assertTrue(d['completion_exception_reference']['one_way_implication']);self.assertFalse(d['completion_exception_reference']['negation_implies_successful_movement_verified'])

if __name__=='__main__':unittest.main()
