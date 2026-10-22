from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import json,subprocess,sys,unittest
from rouge import current_scout as model,node_catalog

def clone(root):
    names={model.MANIFEST,*json.loads((model.ROOT/model.MANIFEST).read_bytes())['files'],model.packet()['data']['icon_reference']['file']}
    for name in names:
        p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((model.ROOT/name).read_bytes())

class CurrentScout342Tests(unittest.TestCase):
    def test_complete_build_and_all_four_source_records_and_followups(self):
        p=subprocess.run([sys.executable,'-B','scripts/build_current_scout_342.py','--check'],cwd=model.ROOT,capture_output=True);self.assertEqual(p.returncode,0,p.stderr)
        r=model.reference();self.assertEqual((len(r['scenes']),len(r['choices'])),(4,4));current=model.version.packet()['current']['details']
        for kind,table in [('scenes','choiceScenes'),('choices','choices'),('items','items')]:
            for key,v in r['data']['originals'][kind].items():self.assertEqual(v,current[table][key])
        self.assertEqual(r['data']['current_game_const'],{k:current['gameConst'][k]for k in r['data']['current_game_const']})
        self.assertEqual([c['role']for c in r['choices'].values()],['inside','origin','confirm','rest'])
    def test_current_const_item_and_old_reference_scopes_remain_separate(self):
        r=model.reference();d=r['data'];self.assertEqual(d['current_game_const']['expedEndingRelic'],'rogue_6_relic_final_3')
        self.assertEqual(next(iter(d['originals']['items'].values()))['name'],'怦然信标');self.assertEqual(len(d['documented_return_references']),3)
        self.assertIn('本区域探索结束后归来',d['current_game_const']['expeditionSelectDescFormat'])
        origin=model.choice_reference(r,'scene_ro6_scout_enter','choice_ro6_scout_3');self.assertEqual(origin['effect_phase_reference'],'on_return');self.assertIsNone(origin['hope_reference'])
    def test_documented_floors_and_ending_prerequisite_not_actual_unlock(self):
        r=model.reference();d=r['data']['documented_conditions'];self.assertEqual(d['documented_regular_floors'],[2,3,4]);self.assertTrue(d['origin_requires_first_ending_reference']);self.assertIsNone(d['actual_account_unlocked']);self.assertFalse(d['complete_server_eligibility_known'])
        for sid in r['scenes']:
            text=model.player_text(r,sid);self.assertIn('第Ⅱ、Ⅲ、Ⅳ层',text);self.assertIn('先完成结局“强制重启”',text);self.assertIn('不代表当前账户已解锁',text)
    def test_inside_never_borrows_origin_reward_rest_is_only_immediate_two(self):
        r=model.reference();inside=r['choices']['choice_ro6_scout_1'];rest=r['choices']['choice_ro6_scout_2'];self.assertIsNone(inside['hope_reference']);self.assertEqual(rest['hope_reference'],2)
        text=model.player_text(r,inside['scene_id'],inside['id']);self.assertIn('完整奖励池、具体数量和培养变化仍未知',text);self.assertIn('不套用探索源头',text)
        text=model.player_text(r,rest['scene_id'],rest['id']);self.assertIn('此分支不派出干员',text);self.assertNotIn('【探索源头：归来参考】',text);self.assertNotIn('【长期科技',text)
    def test_confirmation_only_source_followup_and_explanation_not_fifth_button(self):
        r=model.reference();c=r['choices']['choice_ro6_scout_4'];self.assertEqual(c['scene_id'],'scene_ro6_scout_3');self.assertIsNone(c['next_scene_id']);self.assertEqual(c['stage_ids'],[])
        self.assertEqual(r['scenes']['scene_ro6_scout_3']['choice_ids'],[c['id']]);self.assertEqual(len(r['scenes']['scene_ro6_scout_enter']['choice_ids']),3)
        self.assertFalse(r['data']['return_explanation']['is_actual_button']);text=model.player_text(r,c['scene_id'],c['id']);self.assertIn('不是再次派出、再次休息或立即领奖',text);self.assertIn('不证明会回复生命',text)
        self.assertEqual(r['scenes']['scene_ro6_scout_1']['choice_ids'],[]);self.assertEqual(r['scenes']['scene_ro6_scout_2']['choice_ids'],[])
    def test_origin_return_no_promotion_no_reward_sum_and_beak_unresolved(self):
        r=model.reference();c=r['choices']['choice_ro6_scout_3'];text=model.player_text(r,c['scene_id'],c['id'])
        for word in('不会被进阶','归来时带来2希望','不与“休息”的当场2希望相加','所有敌人的生命+20%','我方单位的生命-40%','不额外加算','实际返回时刻'):
            self.assertIn(word,text)
        for k in('actual_operator','actual_returned','actual_received','actual_advanced','actual_hope','actual_return_clock','actual_selectable','actual_eligible'):self.assertIsNone(r[k])
        self.assertFalse(r['run_updated'])
    def test_all_eight_exact_entry_targets_and_wrong_types_no_fuzzy_match(self):
        r=model.reference();count=0
        for cat in('scenes','choices'):
            for key in r['data']['originals'][cat]:
                t=model.locate(cat,key);self.assertEqual(t['scene_id'],key if cat=='scenes'else r['choices'][key]['scene_id']);self.assertEqual(t['choice_id'],None if cat=='scenes'else key);count+=1
        self.assertEqual(count,8)
        for cat,key in [('choices','尝试探索树的内部'),('scenes','scene_ro6_scout_3x'),('relics','rogue_6_relic_final_3'),(True,1)]:self.assertIsNone(model.locate(cat,key))
        self.assertIsNone(model.reference(True));self.assertIsNone(model.reference('other'));self.assertIsNone(model.choice_reference(r,True,1))
    def test_all_source_files_fail_closed_and_manual_restore_works(self):
        with TemporaryDirectory()as folder:
            root=Path(folder);clone(root)
            with patch.object(model,'ROOT',root):
                for name in(model.MANIFEST,*json.loads((root/model.MANIFEST).read_bytes())['files']):
                    f=root/name;raw=f.read_bytes();self.assertIsNotNone(model.reference());f.write_bytes(raw+b' ');self.assertIsNone(model.reference(),name);f.write_bytes(raw);self.assertIsNotNone(model.reference())
    def test_bad_return_image_keeps_verified_text_and_rest_never_shows_it(self):
        r=model.reference();self.assertIsNotNone(model.icon_bytes());self.assertTrue(model.shows_return_item(r,'scene_ro6_scout_enter','choice_ro6_scout_3'));self.assertTrue(model.shows_return_item(r,'scene_ro6_scout_3','choice_ro6_scout_4'))
        self.assertFalse(model.shows_return_item(r,'scene_ro6_scout_enter','choice_ro6_scout_2'));self.assertFalse(model.shows_return_item(r,'scene_ro6_scout_enter',None))
        with TemporaryDirectory()as folder:
            root=Path(folder);clone(root)
            with patch.object(model,'ROOT',root):
                f=root/r['data']['icon_reference']['file'];f.write_bytes(f.read_bytes()+b'x');self.assertIsNone(model.icon_bytes());self.assertIsNotNone(model.reference())
    def test_full_catalogue_identity_is_required_and_results_are_isolated(self):
        e=deepcopy(node_catalog._event('community_group_024'));b=model.catalogue_binding(e);self.assertEqual(len(b['exact_scene_links']),4);e['scenes'][0]['description']+='x';self.assertIsNone(model.catalogue_binding(e))
        r=model.reference();r['choices'].clear();r['data']['current_game_const'].clear();self.assertEqual(len(model.reference()['choices']),4)
    def test_old297_explanation_and_scope_are_preserved(self):
        from rouge import expedition_results as old
        d=old.source_data();self.assertIsNotNone(d);self.assertFalse(d['current_server_verified']);self.assertFalse(d['return_explanatory_reference']['is_actual_button']);self.assertIsNone(d['rows'][1]['beak_reference']['applies_to_root_branch'])

if __name__=='__main__':unittest.main()
