from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import json,subprocess,sys,unittest
from rouge import current_resting as model,node_catalog

def clone(root):
    names={model.MANIFEST,*json.loads((model.ROOT/model.MANIFEST).read_bytes())['files'],model.packet()['data']['icon_reference']['file']}
    for name in names:
        p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((model.ROOT/name).read_bytes())

PATHS=[(['dog','dog-orchard'],'doc:20'),(['dog','dog-race'],'doc:24'),(['net','observe'],'doc:26'),(['net','net-mud'],'doc:30'),(['squirrel','squirrel-orchard'],'doc:34'),(['squirrel','squirrel-race'],'doc:38'),(['squirrel','legacy-squirrel-mud'],'legacy:end')]
def path_keys(first,last):
    common=['option:enter','option:look','result:first-'+first,'reward:'+first]
    if last=='observe':return common+['reward:observe']
    return common+['option:touch-'+first,'result:'+last,'reward:legacy-gold99'if last.startswith('legacy')else'reward:gold99'if last=='net-mud'else'reward:'+last]

class CurrentResting345Tests(unittest.TestCase):
    def test_complete_build_preserves_all_current_originals_and_document_occurrences(self):
        p=subprocess.run([sys.executable,'-B','scripts/build_current_resting_345.py','--check'],cwd=model.ROOT,capture_output=True);self.assertEqual(p.returncode,0,p.stderr)
        r=model.reference();d=r['data'];self.assertEqual((len(r['scenes']),len(r['choices']),len(d['originals']['scenes']),len(d['originals']['choices'])),(25,24,12,12));current=model.version.packet()['current']['details']
        for kind,table in [('scenes','choiceScenes'),('choices','choices'),('items','items')]:
            for key,v in d['originals'][kind].items():self.assertEqual(v,current[table][key])
    def test_all_seven_document_paths_remain_in_case_and_end_without_invented_loops(self):
        r=model.reference()
        for (first,last),end in PATHS:
            sid='doc:1'
            for key in path_keys(first,last):
                c=model.choice_reference(r,sid,key);self.assertIsNotNone(c,key);sid=c['next_scene_id']
            self.assertEqual(sid,end);self.assertEqual(r['scenes'][sid]['choice_ids'],[])
    def test_outcomes_are_reference_cards_not_actual_game_buttons_or_pool(self):
        r=model.reference()
        for key in('outcomes:first','outcomes:dog','outcomes:net','outcomes:squirrel'):
            for cid in r['scenes'][key]['choice_ids']:
                c=model.choice_reference(r,key,cid);self.assertEqual(c['presentation'],'outcome_reference');self.assertIs(c['actual_game_button'],False)
            self.assertIn('结果参考，非游戏菜单',model.player_text(r,key))
        self.assertEqual(len(r['scenes']['outcomes:first']['choice_ids']),3);self.assertEqual(len(r['scenes']['outcomes:dog']['choice_ids']),2)
        self.assertFalse(r['data']['complete_game_option_pool']);self.assertIsNone(r['actual_pool'])
    def test_both_old_count_conflicts_and_bwiki_difference_are_explicit_not_resolved(self):
        r=model.reference();cards=r['data']['historical_result_cards'];self.assertEqual([(c['documented_count'],c['listed_branch_count'],c['count_matches'])for c in cards],[(3,3,True),(2,2,True),(2,1,False),(2,3,False)])
        self.assertEqual(len(r['scenes']['outcomes:net']['choice_ids']),1);rows=[r['choices'][c]for c in r['scenes']['outcomes:squirrel']['choice_ids']];self.assertEqual(sum(c['scope']=='bwiki'for c in rows),2);self.assertEqual(sum(c['scope']=='legacy_unresolved'for c in rows),1)
        self.assertIn('不能据此认定只有1项或补出第2项',model.player_text(r,'outcomes:net'));self.assertIn('归属未证候选',model.player_text(r,'outcomes:squirrel'));self.assertIn('当前归属未证',model.player_text(r,'legacy:mud'))
    def test_reward_scalars_match_whole_descriptions_not_other_cases_or_sums(self):
        r=model.reference();expected={'reward:dog':(20,'hope'),'reward:net':(15,'shield'),'reward:squirrel':(1,'precious_processed_part'),'reward:observe':(20,'hope'),'reward:gold99':(99,'gold'),'reward:dog-orchard':(15,'shield')}
        for key,(quantity,kind)in expected.items():
            c=r['choices'][key];self.assertEqual(c['reward_reference'],{'quantity':quantity,'kind':kind});self.assertIn('只解释这一按钮',model.player_text(r,c['scene_id'],key))
        self.assertIsNone(r['actual_gold_total']);self.assertFalse(r['run_updated']);self.assertTrue(all(r[k]is None for k in('actual_inventory','actual_received','actual_result','actual_choice','actual_transition','actual_eligible','actual_pool','actual_left')))
    def test_99_original_bed_destination_conflicts_with_document_leave_both_preserved(self):
        r=model.reference();c=r['choices']['reward:gold99'];self.assertTrue(c['explicit_next_conflict']);self.assertEqual(c['next_scene_id'],'doc:30');t=model.conflicting_original_target(r,'doc:28',c['id']);self.assertEqual(t,{'source_request':{'category':'choices','key':'choice_ro6_surprise_12'}})
        q=model.reference(**t);self.assertEqual(q['requested_original']['nextSceneId'],'scene_ro6_surprise_1');self.assertEqual(q['scenes']['source-next']['source_scene_ids'],['scene_ro6_surprise_1']);self.assertEqual(q['scenes']['source-next']['choice_ids'],[]);self.assertIsNone(model.conflicting_original_target(q,'source-choice','source-choice'))
        self.assertIn('不能认定哪一边就是实际结束方式',model.player_text(r,'doc:28',c['id']))
    def test_key_is_unique_named_catalogue_reference_not_nonexistent_original_pointer(self):
        r=model.reference();binding=r['data']['named_item_binding'];self.assertEqual(binding['basis'],'full_literal_unique_current_RELIC_name');self.assertIsNone(binding['original_item_pointer']);self.assertIsNone(r['data']['originals']['choices']['choice_ro6_surprise_1']['displayData']['itemId'])
        item=next(iter(r['data']['originals']['items'].values()));self.assertEqual(item['name'],'源私钥');self.assertEqual(item['type'],'RELIC');self.assertIn('99源石锭',item['usage']);text=model.player_text(r,'doc:1','option:enter');self.assertIn('没有给出物品编号',text);self.assertIn('不能相加成198',text)
        self.assertIn('不能相加成198',model.player_text(r,'doc:28','reward:gold99'))
    def test_all24_exact_original_entries_eight_explicit_four_no_next_candidates(self):
        d=model.reference()['data'];count=0;explicit=0;candidate=0
        for category in('scenes','choices'):
            for key,v in d['originals'][category].items():
                r=model.reference(**model.locate(category,key));self.assertEqual(r['requested_original'],v);count+=1
                if category=='scenes':self.assertEqual(r['scenes']['source-scene']['choice_ids'],[])
                else:
                    c=model.choice_reference(r,'source-choice','source-choice');self.assertEqual(c['variant_ids'],[key]);self.assertEqual(c['next_scene_id'],'source-next'if v['nextSceneId']else None)
                    if v['nextSceneId']:explicit+=1;self.assertEqual(r['scenes']['source-next']['description'],d['originals']['scenes'][v['nextSceneId']]['description'])
                    else:candidate+=1;self.assertEqual(v['type'],'NEXT_PROB');self.assertEqual(r['requested_choice_association'],'full_literal_random_candidate')
        self.assertEqual((count,explicit,candidate),(24,8,4))
    def test_bad_targets_unknown_ids_and_extra_fields_rejected(self):
        for target in(True,[],{}, {'category':'choices','key':1},{'category':'items','key':'rogue_6_relic_cargo_13'},{'category':'scenes','key':'scene_ro6_surprise_1x'},{'category':'choices','key':'choice_ro6_surprise_1','extra':True}):self.assertIsNone(model.reference(source_request=target))
        self.assertIsNone(model.reference(True));self.assertIsNone(model.locate('choices','四处看看'));self.assertIsNone(model.locate(True,1))
    def test_all_source_members_fail_closed_after_success_and_restore(self):
        with TemporaryDirectory()as folder:
            root=Path(folder);clone(root)
            with patch.object(model,'ROOT',root):
                for name in(model.MANIFEST,*json.loads((root/model.MANIFEST).read_bytes())['files']):
                    f=root/name;raw=f.read_bytes();self.assertIsNotNone(model.reference());f.write_bytes(raw+b' ');self.assertIsNone(model.reference(),name);f.write_bytes(raw);self.assertIsNotNone(model.reference())
    def test_picture_failure_only_fallback_and_mutable_results_isolated(self):
        r=model.reference();self.assertIsNotNone(model.icon_bytes())
        with TemporaryDirectory()as folder:
            root=Path(folder);clone(root)
            with patch.object(model,'ROOT',root):
                f=root/r['data']['icon_reference']['file'];f.write_bytes(f.read_bytes()+b'x');self.assertIsNone(model.icon_bytes());self.assertIsNotNone(model.reference())
        r['data']['choices'].clear();r['scenes'].clear();self.assertEqual(len(model.reference()['scenes']),25)
    def test_full_legacy_context_identity_and_old293_conflicts_preserved(self):
        e=deepcopy(node_catalog._event('community_group_023'));b=model.catalogue_binding(e);self.assertEqual(len(b['exact_scene_links']),18);self.assertEqual(len({x['current_original_scene_id']for x in b['exact_scene_links']}),12);e['scenes'][0]['description']+='x';self.assertIsNone(model.catalogue_binding(e))
        from rouge import resting_corner_results as old
        d=old.source_data();self.assertFalse(d['current_server_verified']);self.assertFalse(d['full_actual_pool_known']);self.assertEqual(sum(not c['count_matches']for c in d['cards']),2)

if __name__=='__main__':unittest.main()
