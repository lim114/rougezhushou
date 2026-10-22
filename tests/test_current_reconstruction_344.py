from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import json,subprocess,sys,unittest
from rouge import current_reconstruction as model,node_catalog

def clone(root):
    names={model.MANIFEST,*json.loads((model.ROOT/model.MANIFEST).read_bytes())['files'],model.packet()['data']['icon_reference']['file']}
    for name in names:
        p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((model.ROOT/name).read_bytes())

class CurrentReconstruction344Tests(unittest.TestCase):
    def test_complete_build_preserves_every_current_original_and_document_occurrence(self):
        p=subprocess.run([sys.executable,'-B','scripts/build_current_reconstruction_344.py','--check'],cwd=model.ROOT,capture_output=True);self.assertEqual(p.returncode,0,p.stderr)
        r=model.reference();d=r['data'];self.assertEqual((len(r['scenes']),len(r['choices']),len(d['originals']['scenes']),len(d['originals']['choices'])),(14,13,46,44))
        current=model.version.packet()['current']['details']
        for kind,table in [('scenes','choiceScenes'),('choices','choices'),('items','items')]:
            for key,v in d['originals'][kind].items():self.assertEqual(v,current[table][key])
    def test_36_explicit_destinations_eight_literal_sacrifice_candidates_not_proven_parents(self):
        r=model.reference();a=r['data']['original_choice_association'];self.assertEqual(sum(v=='explicit_destination_scene'for v in a.values()),36);self.assertEqual(sum(v=='full_literal_sacrifice_candidate'for v in a.values()),8)
        for key,kind in a.items():
            v=r['data']['originals']['choices'][key]
            if kind=='full_literal_sacrifice_candidate':self.assertIsNone(v['nextSceneId']);self.assertEqual(v['type'],'SACRIFICE')
        for c in r['choices'].values():
            if c['role'].startswith(('choose_','continue_')):self.assertFalse(c['document_next_is_original_next'])
    def test_full_document_paths_are_distinct_and_do_not_create_infinite_repeats(self):
        r=model.reference()
        for path,end in [([2,4,16,18],'doc:19'),([6,8,22,24],'doc:25'),([2,4,20],'doc:21'),([6,8,26],'doc:27'),([10,12],'doc:13'),([14],'doc:15')]:
            sid='doc:1'
            for row in path:
                c=model.choice_reference(r,sid,'doc-choice:'+str(row));self.assertIsNotNone(c);sid=c['next_scene_id']
            self.assertEqual(sid,end);self.assertEqual(r['scenes'][end]['choice_ids'],[])
        self.assertNotEqual(r['scenes']['doc:5']['id'],r['scenes']['doc:9']['id']);self.assertEqual(r['scenes']['doc:5']['description'],r['scenes']['doc:9']['description'])
    def test_full_candidates_with_explicit_next_always_agree_with_document_narrative(self):
        from scripts.build_documented_event_flows_321 import canonical
        r=model.reference()
        for c in r['choices'].values():
            expected=canonical(r['scenes'][c['next_scene_id']]['description'])
            for key in c['variant_ids']:
                v=r['data']['originals']['choices'][key]
                if v['nextSceneId']:self.assertEqual(canonical(r['data']['originals']['scenes'][v['nextSceneId']]['description']),expected)
    def test_all_ninety_exact_source_entries_keep_original_and_only_explicit_followup(self):
        d=model.reference()['data'];count=0
        for category in('scenes','choices'):
            for key,v in d['originals'][category].items():
                t=model.locate(category,key);r=model.reference(**t);self.assertEqual(r['requested_original'],v);count+=1
                if category=='scenes':self.assertEqual(r['scenes']['source-scene']['choice_ids'],[]);self.assertEqual(r['scenes']['source-scene']['description'],v['description'])
                else:
                    c=model.choice_reference(r,'source-choice','source-choice');self.assertEqual(c['variant_ids'],[key]);self.assertEqual(c['next_scene_id'],'source-next'if v['nextSceneId']else None)
                    if v['nextSceneId']:self.assertEqual(r['scenes']['source-next']['description'],d['originals']['scenes'][v['nextSceneId']]['description']);self.assertEqual(r['scenes']['source-next']['choice_ids'],[])
        self.assertEqual(count,90)
    def test_raw_continue_does_not_choose_relic_type_by_id_or_borrow_document_next(self):
        d=model.reference()['data'];rows=[(k,v)for k,v in d['originals']['choices'].items()if v['title']=='继续赞助它'];self.assertEqual(len(rows),4)
        for key,v in rows:
            r=model.reference(**model.locate('choices',key));c=model.choice_reference(r,'source-choice','source-choice');self.assertEqual(c['role'],'unknown_exchange');self.assertFalse(model.catalogue_allowed(r,'source-choice','source-choice'));self.assertIsNone(c['next_scene_id']);self.assertIn('不按编号指定类型',model.player_text(r,'source-choice','source-choice'))
    def test_only_relic_offering_not_receiving_or_part_exchange_exposes_catalogue(self):
        r=model.reference()
        for c in r['choices'].values():self.assertIs(model.catalogue_allowed(r,c['scene_id'],c['id']),c['role']in('choose_relic','continue_relic'))
        for c in r['choices'].values():
            if c['role']in('claim_relic','claim_part'):
                text=model.player_text(r,c['scene_id'],c['id']);self.assertIn('不按候选记录份数倍增',text);self.assertEqual(c['reward_quantity_reference'],1)
    def test_natural_cost_zero_one_two_boundaries_and_named_receipt_not_double_cost(self):
        for value in(None,0,1,2,100):
            r=model.reference(naturals=value);c=model.choice_reference(r,'doc:1','doc-choice:10');self.assertIs(c['listed_condition_match'],None if value is None else value>=2);self.assertEqual(c['natural_cost_reference'],2)
            c=model.choice_reference(r,'doc:11','doc-choice:12');self.assertIsNone(c['natural_cost_reference']);self.assertIsNone(c['reward_quantity_reference']);self.assertTrue(model.shows_reward(r,'doc:11',c['id']));self.assertIn('不再次消耗2件自然物',model.player_text(r,'doc:11',c['id']))
        for value in(True,False,-1,1.0,'2',[]):self.assertIsNone(model.reference(naturals=value))
    def test_known_technology_and_floor_conditions_not_account_unlock_or_reward_pool(self):
        r=model.reference();text=model.player_text(r,'doc:1');self.assertIn('“声带”允许交换零件',text);self.assertIn('“手掌”',text);self.assertIn('第Ⅰ、Ⅵ层',text);self.assertIn('实际科技、首次类型和剩余次数未知',text)
        for k in('actual_inventory','actual_consumed','actual_received','actual_choice','actual_variant','actual_reward_pool','actual_remaining_exchanges','actual_first_type','actual_eligible'):self.assertIsNone(r[k])
        self.assertFalse(r['run_updated']);self.assertFalse(r['data']['complete_game_option_pool'])
    def test_bad_types_extra_target_fields_and_unknown_ids_rejected(self):
        for q in(True,[],{}, {'category':'choices','key':1},{'category':'items','key':'rogue_6_relic_final_6'},{'category':'scenes','key':'scene_ro6_sacrifice1_enterx'},{'category':'choices','key':'choice_ro6_sacrifice1_1','extra':True}):self.assertIsNone(model.reference(source_request=q))
        self.assertIsNone(model.reference(True));self.assertIsNone(model.locate('choices','复原藏品'));self.assertIsNone(model.locate(True,1))
    def test_all_sources_fail_closed_after_success_then_restore(self):
        with TemporaryDirectory()as folder:
            root=Path(folder);clone(root)
            with patch.object(model,'ROOT',root):
                for name in(model.MANIFEST,*json.loads((root/model.MANIFEST).read_bytes())['files']):
                    f=root/name;raw=f.read_bytes();self.assertIsNotNone(model.reference());f.write_bytes(raw+b' ');self.assertIsNone(model.reference(),name);f.write_bytes(raw);self.assertIsNotNone(model.reference())
    def test_bad_reward_picture_keeps_text_and_results_are_isolated(self):
        r=model.reference();self.assertIsNotNone(model.icon_bytes())
        with TemporaryDirectory()as folder:
            root=Path(folder);clone(root)
            with patch.object(model,'ROOT',root):
                p=root/r['data']['icon_reference']['file'];p.write_bytes(p.read_bytes()+b'x');self.assertIsNone(model.icon_bytes());self.assertIsNotNone(model.reference())
        r['scenes'].clear();r['data']['originals']['choices'].clear();self.assertEqual(len(model.reference()['scenes']),14)
    def test_catalogue_42_exact_links_and_old305_323_boundaries_preserved(self):
        e=deepcopy(node_catalog._event('community_group_025'));self.assertEqual(len(model.catalogue_binding(e)['exact_scene_links']),42);e['scenes'][0]['description']+='x';self.assertIsNone(model.catalogue_binding(e))
        from rouge import relic_exchange_flow as old,current_exchange_reference as current
        d=old.source_data();self.assertFalse(d['original_entry_restored']);self.assertFalse(d['current_server_verified']);self.assertEqual(len(current.packet()['data']['catalogue']),284)

if __name__=='__main__':unittest.main()
