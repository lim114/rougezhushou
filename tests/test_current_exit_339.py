from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import json, subprocess, sys, unittest
from rouge import current_exit as model, node_catalog

def clone(root):
    names = {model.MANIFEST, *json.loads((model.ROOT/model.MANIFEST).read_bytes())['files']}
    for name in names:
        p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((model.ROOT/name).read_bytes())

class CurrentExit339Tests(unittest.TestCase):
    def result(self, **kwargs): return model.reference(**kwargs)
    def role(self, r, role): return next(c for c in r['choices'].values() if c['role']==role)
    def test_full_build_is_reproducible_and_preserves_all_document_occurrences(self):
        p=subprocess.run([sys.executable,'-B','scripts/build_current_exit_339.py','--check'],cwd=model.ROOT,capture_output=True)
        self.assertEqual(p.returncode,0,p.stderr);r=self.result()
        self.assertEqual((len(r['scenes']),len(r['choices']),len(r['data']['originals']['scenes']),len(r['data']['originals']['choices'])),(8,8,5,8))
        self.assertTrue(r['data']['document_investigation_notice_retained']);self.assertFalse(r['data']['complete_game_option_pool'])
    def test_root_has_only_four_documented_options_and_no_invented_third(self):
        r=self.result();root=r['scenes'][r['event']['entry_scene_id']]
        self.assertEqual([r['choices'][k]['role']for k in root['choice_ids']],['persuade_part','recruit','leave','help'])
    def test_same_narrative_twice_not_infinite_reward_loop(self):
        r=self.result();c=self.role(r,'persuade_part');first=r['scenes'][c['next_scene_id']];self.assertEqual(len(first['choice_ids']),2)
        repeat=next(r['choices'][cid]for cid in first['choice_ids']if r['choices'][cid]['role']=='persuade_part')
        last=r['scenes'][repeat['next_scene_id']];self.assertEqual(last['raw_scene_id'],first['raw_scene_id']);self.assertNotEqual(last['id'],first['id']);self.assertEqual(last['choice_ids'],[])
    def test_two_no_part_originals_only_have_verified_destination_not_parent(self):
        r=self.result();rows=[c for c in r['choices'].values()if c['role']=='persuade_no_part'];self.assertEqual(len(rows),2)
        for c in rows:
            self.assertFalse(c['document_parent_verified']);self.assertIsNone(r['scenes'][c['scene_id']]['raw_scene_id'])
            self.assertEqual(r['scenes'][c['next_scene_id']]['raw_scene_id'],c['raw_next_scene_id'])
            self.assertIsNone(model.choice_reference(r,c['scene_id'],c['id'])['listed_condition_match'])
    def test_all_eight_complete_originals_match_pinned_current_records(self):
        r=self.result();d=model.version.packet()['current']['details']
        for kind, table in [('choices','choices'),('scenes','choiceScenes'),('items','items')]:
            for key,v in r['data']['originals'][kind].items():self.assertEqual(v,d[table][key])
    def test_difficulty_unknown15_16_do_not_choose_hidden_variant(self):
        for difficulty,expected in [(None,None),(0,1),(15,1),(16,0)]:
            r=self.result(difficulty=difficulty);c=self.role(r,'persuade_part');out=model.choice_reference(r,c['scene_id'],c['id'])
            self.assertEqual(out['base_exit_processed_part_reference'],expected);self.assertIsNone(out['actual_variant_id']);self.assertIsNone(out['actual_received'])
            self.assertEqual(out['listed_condition_match'],False if difficulty==16 else None)
    def test_conversion_only_once_reference_no_final_hope_or_inventory(self):
        for amount in (None,0,7,99999):
            r=self.result(action_points=amount)
            for c in r['choices'].values():
                out=model.choice_reference(r,c['scene_id'],c['id']);self.assertEqual(out['equal_conversion_reference'],amount if c['role']in('persuade_part','persuade_no_part','confirm')else None)
                self.assertIsNone(out['actual_received']);self.assertIsNone(r['actual_transition']);self.assertFalse(r['run_updated'])
    def test_gold9_10_only_matches_help_and_does_not_spend(self):
        for gold,match in [(None,None),(9,False),(10,True)]:
            r=self.result(gold=gold);c=self.role(r,'help');self.assertIs(model.choice_reference(r,c['scene_id'],c['id'])['listed_condition_match'],match);self.assertIsNone(r['actual_consumed'])
    def test_named_help_reward_and_hpmax_hint_not_added_as_quantity_or_stat(self):
        r=self.result();c=self.role(r,'help');text=model.player_text(r,c['scene_id'],c['id'])
        self.assertIn('谒日之祈',text);self.assertIn('10源石锭',text);self.assertIn('没有独立件数',text)
        c=self.role(r,'persuade_part');self.assertEqual(len(c['variant_ids']),2);self.assertIn('不额外加生命上限',model.player_text(r,c['scene_id'],c['id']))
    def test_all14_original_entries_and_ambiguous_document_locations_preserved(self):
        r=self.result();pairs=[(cat,k)for cat in('scenes','choices')for k in r['data']['originals'][cat]]+[('relics','rogue_6_relic_final_7')];self.assertEqual(len(pairs),14)
        for cat,key in pairs:
            target=model.locate(cat,key);self.assertIsNotNone(target);out=self.result(source_request=target['source_request']);self.assertTrue(out['source_targets']);self.assertEqual(out['source_request'],{'category':cat,'key':key})
        self.assertEqual(len(self.result(source_request={'category':'choices','key':'choice_ro6_final1_1'})['source_targets']),2)
        self.assertEqual(len(self.result(source_request={'category':'scenes','key':'scene_ro6_final1_3'})['source_targets']),2)
    def test_bad_inputs_and_foreign_same_names_rejected(self):
        for field,value in [('gold',True),('gold',-1),('action_points',1.5),('difficulty',True),('difficulty',17),('difficulty',-1)]:self.assertIsNone(self.result(**{field:value}))
        for cat,key in [('relics','谒日之祈'),('choices','说服同伴'),('scrap','rogue_6_relic_final_7'),('scenes','scene_ro6_final1_enter_2')]:self.assertIsNone(model.locate(cat,key))
        self.assertIsNone(self.result(source_request={'category':'choices','key':'missing'}));self.assertIsNone(self.result(source_request={'category':'choices','key':'choice_ro6_final1_1','extra':True}))
    def test_all_source_members_fail_closed_and_recover_with_same_query(self):
        with TemporaryDirectory()as folder:
            root=Path(folder);clone(root)
            with patch.object(model,'ROOT',root):
                for name in (model.MANIFEST,*json.loads((root/model.MANIFEST).read_bytes())['files']):
                    p=root/name;raw=p.read_bytes();self.assertIsNotNone(self.result());p.write_bytes(raw+b' ');self.assertIsNone(self.result(),name);p.write_bytes(raw)
    def test_current_difficulty_disagreement_rejects_old_reference(self):
        p=model.version.packet();forged=deepcopy(p);forged['current']['details']['difficulties']=[v for v in forged['current']['details']['difficulties']if v['grade']!=16]
        with patch.object(model.version,'packet',return_value=forged):self.assertIsNone(self.result())
    def test_catalogue_requires_complete_id_and_narrative_not_title_only(self):
        event=deepcopy(node_catalog._event('community_group_033'));self.assertIsNotNone(model.catalogue_binding(event));event['scenes'][0]['description']+='changed';self.assertIsNone(model.catalogue_binding(event))
    def test_isolated_return_and_unproven_fields_remain_unknown(self):
        r=self.result();r['choices'].clear();self.assertEqual(len(self.result()['choices']),8)
        self.assertTrue(all(self.result()[k]is None for k in('actual_received','actual_consumed','actual_transition','actual_recruited','actual_eligible')))
if __name__=='__main__':unittest.main()
