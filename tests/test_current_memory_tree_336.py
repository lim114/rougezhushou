from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import json,shutil,unittest
from rouge import current_memory_tree as model,current_node_readers as bridge,node_catalog
from scripts import build_current_memory_tree_336 as builder
ROOT=Path(__file__).resolve().parents[1]
def clone(root):
    m=json.loads((ROOT/model.MANIFEST).read_bytes())
    for name in(model.MANIFEST,*m['files']):
        p=root/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,p)

class CurrentMemoryTree336Tests(unittest.TestCase):
    def test_complete_notice_five_options_six_narratives_four_items_and_reproducible_sources(self):
        d,m=builder.build();self.assertEqual(d,(ROOT/model.DATA).read_bytes());self.assertEqual(m,(ROOT/model.MANIFEST).read_bytes());r=model.reference();self.assertEqual((len(r['scenes']),len(r['choices']),len(r['data']['originals']['items'])),(6,5,4));self.assertTrue(r['data']['document_investigation_notice_retained']);v=model.version.packet()
        for group,rows in r['data']['originals'].items():
            table='choiceScenes'if group=='scenes'else group
            for k,value in rows.items():self.assertEqual(v['current']['details'][table][k],value);self.assertIs(r['data']['complete_selected_record_comparison_to_baseline'][group][k],v['baseline']['details'][table].get(k)==value)
        self.assertFalse(r['data']['complete_game_option_pool']);self.assertFalse(r['data']['game_parent_script_restored'])
    def test_each_resource_boundary_independent_and_unknowns_never_actual_eligibility(self):
        sid='scene_ro6_normal5_enter'
        for ap,parts,key,controller,expected in[(None,None,None,None,[None,None,None,None,True]),(2,1,False,False,[False,False,False,False,True]),(3,2,True,True,[True]*5),(0,2,False,True,[False,True,False,True,True]),(3,0,True,False,[True,False,True,False,True])]:
            r=model.reference('memorytree',ap,parts,key,controller)
            self.assertEqual([model.choice_reference(r,sid,c)['listed_condition_match']for c in r['event']['choice_ids']],expected);self.assertIsNone(r['actual_eligible']);self.assertFalse(r['run_updated']);self.assertIsNone(r['actual_consumed']);self.assertIsNone(r['actual_new_region'])
        for value in(True,-1,0.5,'3'):
            self.assertIsNone(model.reference(action_points=value));self.assertIsNone(model.reference(processed_parts=value))
        for value in(0,1,'yes',[]):self.assertIsNone(model.reference(source_key=value));self.assertIsNone(model.reference(controller=value))
    def test_all11_exact_entries_and_every_choice_has_own_terminal_narrative(self):
        r=model.reference();destinations=[]
        for key in r['scenes']:self.assertEqual(model.locate('scenes',key),{'event_id':'memorytree','scene_id':key,'choice_id':None})
        for key,c in r['choices'].items():
            self.assertEqual(model.locate('choices',key),{'event_id':'memorytree','scene_id':c['scene_id'],'choice_id':key});self.assertIsNotNone(model.choice_reference(r,c['scene_id'],key));self.assertEqual(r['scenes'][c['next_scene_id']]['choice_ids'],[]);self.assertIsNone(model.choice_reference(r,c['next_scene_id'],key));destinations.append(c['next_scene_id'])
        self.assertEqual(len(set(destinations)),5);self.assertIsNone(model.locate('choices','choice_ro6_scout_1'))
    def test_three_alternative_costs_no_fake_quantity_or_second_key_income_and_controller_held(self):
        r=model.reference();sid=r['event']['entry_scene_id'];cs=r['choices']
        self.assertEqual(cs['choice_ro6_normal5_1']['action_point_cost'],3);self.assertEqual(cs['choice_ro6_normal5_2']['random_processed_parts_cost'],2);self.assertTrue(cs['choice_ro6_normal5_3']['key_consumed_reference']);self.assertIsNone(cs['choice_ro6_normal5_3']['key_quantity']);self.assertTrue(cs['choice_ro6_normal5_4']['controller_held_reference']);self.assertIsNone(cs['choice_ro6_normal5_4']['controller_consumed']);self.assertEqual([cs[k]['action_point_gain']for k in ('choice_ro6_normal5_4','choice_ro6_normal5_5')],[5,1])
        for i in range(1,4):
            c=cs['choice_ro6_normal5_'+str(i)];self.assertEqual(c['reward_item_id'],'rogue_6_relic_artifact_5');self.assertIsNone(c['reward_quantity']);self.assertIn('不补成1件',model.player_text(r,sid,c['id']))
        self.assertIn('不是本事件消费它后再发放',model.player_text(r,sid,'choice_ro6_normal5_3'));self.assertIn('不是消耗笼控器',model.player_text(r,sid,'choice_ro6_normal5_4'));self.assertIn('进入误入奇境不会触发',model.player_text(r,sid,'choice_ro6_normal5_1'));self.assertIn('不能据此认定本事件所有其它选项',model.player_text(r,sid,'choice_ro6_normal5_1'))
    def test_catalogue_full_guard_three_exact_three_explicit_ellipsis_and_no_fuzzy_match(self):
        row=next(x for x in node_catalog.all_events(include_indirect=True)['rows']if x['id']=='community_group_011');b=bridge.binding_for(row);self.assertEqual(b['reader'],'memory336');self.assertEqual(len(b['exact_scene_links']),6);self.assertEqual([x['match_kind']for x in b['exact_scene_links']].count('document_ellipsis_only'),3);self.assertIsNotNone(bridge.recheck(b));warm=deepcopy(node_catalog._event(row['id']));warm['scenes'][1]['description']+='changed'
        with patch.object(node_catalog,'_event',return_value=warm):self.assertIsNone(bridge.binding_for(row))
        with TemporaryDirectory()as folder:
            root=Path(folder);clone(root);p=root/builder.LEGACY;l=json.loads(p.read_bytes());next(x for x in l['events']if x['id']==row['id'])['scenes'][1]['description']+='different';p.write_bytes(builder.encoded(l))
            with self.assertRaises(ValueError):builder.build(root)
    def test_each_runtime_member_and_complete_current_record_damage_is_rejected_and_recovers(self):
        with TemporaryDirectory()as folder:
            root=Path(folder);clone(root);m=json.loads((ROOT/model.MANIFEST).read_bytes())
            with patch.object(model,'ROOT',root):
                for name in(model.MANIFEST,*m['files']):
                    p=root/name;raw=p.read_bytes();p.write_bytes(raw+b' ');self.assertIsNone(model.packet(),name);p.write_bytes(raw);self.assertIsNotNone(model.packet())
        r=deepcopy(model.version.packet());r['current']['details']['choices']['choice_ro6_normal5_4']['description']='消耗笼控器'
        with patch.object(model.version,'packet',return_value=r):self.assertIsNone(model.packet())
if __name__=='__main__':unittest.main()
